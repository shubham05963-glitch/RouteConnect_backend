from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
from ortools.sat.python import cp_model
from geopy.distance import geodesic
import numpy as np

def parse_crew_shift(shift_str: str, base_date: datetime):
    \"\"\"Parse string shift into datetime objects.\"\"\"
    shift_str = shift_str.lower()
    if "morning" in shift_str:
        return base_date.replace(hour=6, minute=0), base_date.replace(hour=14, minute=0)
    elif "evening" in shift_str or "afternoon" in shift_str:
        return base_date.replace(hour=14, minute=0), base_date.replace(hour=22, minute=0)
    elif "night" in shift_str:
        return base_date.replace(hour=22, minute=0), base_date.replace(hour=6, minute=0) + timedelta(days=1)
    else:
        return base_date.replace(hour=9, minute=0), base_date.replace(hour=17, minute=0)


def _driver_priority_rank(crew_member: Dict[str, Any], default_rank: int) -> int:
    \"\"\"Lower rank value means higher scheduling priority.\"\"\"
    for key in ("priority_order", "driver_order", "order", "seniority_rank"):
        val = crew_member.get(key)
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.strip().isdigit():
            return int(val.strip())
    return default_rank


def generate_schedule(
    crew: List[Dict[str, Any]],
    buses: List[Dict[str, Any]],
    routes: List[Dict[str, Any]],
    trips: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    \"\"\"Production OR-Tools CP-SAT solver for optimal assignment.
    
    Maximizes total assignments with constraints:
    - One driver/bus per trip
    - Shift windows
    - No overlaps
    - Max hours/rest periods
    - Priority weighting
    \"""
    now = datetime.now(timezone.utc)
    base_date = now.replace(second=0, microsecond=0)
    
    # Auto-generate trips if missing
    if not trips:
        trips = []
        trip_counter = 1
        for route in routes:
            for i in range(6):  # 6 trips/day
                start_hour = 6 + (i * 3)
                if start_hour >= 24:
                    continue
                start_time = base_date.replace(hour=start_hour, minute=0)
                end_time = start_time + timedelta(hours=2, minutes=30)
                trips.append({
                    "id": trip_counter,
                    "route_id": route.get("id"),
                    "route_name": route.get("route_name", route.get("name", str(route.get("id")))),
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_hours": 2.5
                })
                trip_counter += 1

    trips.sort(key=lambda t: t["start_time"])

    num_trips = len(trips)
    num_crew = len(crew)
    num_buses = len(buses)

    if num_trips == 0:
        return {"assignments": [], "metadata": {"message": "No trips to schedule"}}

    # OR-Tools model
    model = cp_model.CpModel()

    # Variables: x[crew_idx, trip_idx, bus_idx] = 1 if assigned
    x = {}
    for c in range(num_crew):
        for t in range(num_trips):
            for b in range(num_buses):
                x[c, t, b] = model.NewBoolVar(f'x_c{c}_t{t}_b{b}')

    # Objective: Maximize assignments + priority bonus
    objective_terms = []
    for c in range(num_crew):
        priority_bonus = 10 / (1 + _driver_priority_rank(crew[c], 999))
        for t in range(num_trips):
            for b in range(num_buses):
                objective_terms.append(priority_bonus * x[c, t, b])
    model.Maximize(sum(objective_terms))

    # Constraint 1: Each trip assigned to at most one driver/bus
    for t in range(num_trips):
        model.Add(sum(x[c, t, b] for c in range(num_crew) for b in range(num_buses)) <= 1)

    # Constraint 2: Driver shift windows + hours + rest
    for c in range(num_crew):
        shift_start, shift_end = parse_crew_shift(crew[c].get('shift', 'morning'), base_date)
        max_hours = crew[c].get('max_work_hours', 8.0)
        
        # Total hours for driver
        driver_trips = []
        for t in range(num_trips):
            for b in range(num_buses):
                if x[c, t, b]:
                    duration = trips[t]['duration_hours']
                    driver_trips.append(duration * x[c, t, b])
        model.Add(sum(driver_trips) <= max_hours)

        # Time window: only trips within shift
        for t in range(num_trips):
            trip_start = trips[t]['start_time']
            trip_end = trips[t]['end_time']
            if trip_end <= shift_start or trip_start >= shift_end:
                for b in range(num_buses):
                    model.Add(x[c, t, b] == 0)

        # Rest period between consecutive trips (min 30min)
        for t1 in range(num_trips):
            for t2 in range(t1 + 1, num_trips):
                if trips[t2]['start_time'] - trips[t1]['end_time'] < timedelta(minutes=30):
                    for b1 in range(num_buses):
                        for b2 in range(num_buses):
                            model.Add(x[c, t1, b1] + x[c, t2, b2] <= 1)

    # Constraint 3: Bus non-overlap
    for b in range(num_buses):
        for t1 in range(num_trips):
            for t2 in range(t1 + 1, num_trips):
                if trips[t2]['start_time'] < trips[t1]['end_time']:
                    for c1 in range(num_crew):
                        for c2 in range(num_crew):
                            model.Add(x[c1, t1, b] + x[c2, t2, b] <= 1)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0  # Production timeout
    status = solver.Solve(model)

    assignments = []
    metadata = {
        "total_trips": num_trips,
        "assigned_trips": 0,
        "optimization_status": solver.StatusName(status),
        "objective_value": solver.ObjectiveValue() if status == cp_model.OPTIMAL else 0,
        "solve_time_seconds": solver.WallTime(),
        "generated_at": now.isoformat(),
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for c in range(num_crew):
            for t in range(num_trips):
                for b in range(num_buses):
                    if solver.Value(x[c, t, b]) == 1:
                        assignments.append({
                            "trip_id": trips[t]["id"],
                            "route_id": trips[t]["route_id"],
                            "route_name": trips[t]["route_name"],
                            "bus_id": buses[b].get("id"),
                            "bus_number": buses[b].get("bus_number", buses[b].get("id")),
                            "crew_id": crew[c].get("id"),
                            "crew_name": crew[c].get("name"),
                            "start_time": trips[t]["start_time"].isoformat(),
                            "end_time": trips[t]["end_time"].isoformat(),
                            "priority_score": _driver_priority_rank(crew[c], 999)
                        })
                        metadata["assigned_trips"] += 1
    else:
        metadata["missed_trips"] = num_trips
        metadata["error"] = f"No feasible solution (status: {solver.StatusName(status)})"

    return {
        "assignments": sorted(assignments, key=lambda a: a["start_time"]),
        "metadata": metadata
    }


def calculate_eta(bus_location: Dict[str, float], stop_location: Dict[str, float], avg_speed_kmh: float = 25.0) -> float:
    \"\"\"Calculate ETA in minutes using geodesic distance.\"\"\"
    distance_km = geodesic(
        (bus_location['latitude'], bus_location['longitude']), 
        (stop_location['latitude'], stop_location['longitude'])
    ).kilometers
    
    time_hours = distance_km / avg_speed_kmh
    return round(time_hours * 60, 1)  # Minutes
