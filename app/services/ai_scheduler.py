from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

def parse_crew_shift(shift_str: str, base_date: datetime):
    """Parse string shift into datetime objects."""
    shift_str = shift_str.lower()
    if "morning" in shift_str:
        return base_date.replace(hour=6, minute=0), base_date.replace(hour=14, minute=0)
    elif "evening" in shift_str or "afternoon" in shift_str:
        return base_date.replace(hour=14, minute=0), base_date.replace(hour=22, minute=0)
    elif "night" in shift_str:
        return base_date.replace(hour=22, minute=0), base_date.replace(hour=6, minute=0) + timedelta(days=1)
    else:
        # Default 9 to 5
        return base_date.replace(hour=9, minute=0), base_date.replace(hour=17, minute=0)


def _driver_priority_rank(crew_member: Dict[str, Any], default_rank: int) -> int:
    """Lower rank value means higher scheduling priority."""
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
    """Real AI scheduling algorithm ported from RouteConnect_ai.

    Checks crew max hours, rest periods, bus availability overlaps,
    and dynamically produces trips.
    """
    now = datetime.now(timezone.utc)
    base_date = now.replace(second=0, microsecond=0)
    
    # --- 1. PREPARE DYNAMIC TRIPS IF NONE PROVIDED ---
    # Since the DB currently lacks a Trips table, we'll auto-generate trips 
    # ensuring every route operates repeatedly throughout the day.
    if not trips:
        trips = []
        trip_counter = 1
        for route in routes:
            # Generate 4 trips per day per route (starting 8 AM, every 3 hours)
            for i in range(4):
                start_hour = 8 + (i * 3)
                if start_hour >= 24:
                    continue
                start_time = base_date.replace(hour=start_hour, minute=0)
                # Assume each trip takes 2 hours (estimated)
                end_time = start_time + timedelta(hours=2)
                trips.append({
                    "id": trip_counter,
                    "route_id": route.get("id"),
                    "route_name": route.get("route_name") or route.get("name") or str(route.get("id", "Unknown Route")),
                    "start_time": start_time,
                    "end_time": end_time
                })
                trip_counter += 1

    # Sort trips by start_time
    trips.sort(key=lambda t: t["start_time"])

    # --- 2. PREPARE STATE TRACKERS ---
    for b in buses:
        b["assigned_intervals"] = []  # List of tuples: (start, end)
        
    for index, c in enumerate(crew):
        shift_str = c.get("shift", "morning")
        st, et = parse_crew_shift(shift_str, base_date)
        c["shift_start"] = st
        c["shift_end"] = et
        c["worked_hours"] = 0.0
        c["assigned_count"] = 0
        c["last_end_time"] = None
        c["max_work_hours"] = 8.0 # Default max hours
        c["rest_time"] = 1.0      # Mandatory rest time between shifts in hours
        c["priority_rank"] = _driver_priority_rank(c, index + 1)

    assignments = []
    metadata = {
        "crew_count": len(crew),
        "bus_count": len(buses),
        "route_count": len(routes),
        "total_trips": len(trips),
        "successful_assignments": 0,
        "missed_trips": 0,
        "generated_at": now.isoformat(),
    }

    # --- 3. RUN ASSIGNMENT OPTIMIZATION ---
    for trip in trips:
        start_t = trip["start_time"]
        end_t = trip["end_time"]
        trip_duration = (end_t - start_t).total_seconds() / 3600.0

        # Find available bus wrapper
        selected_bus = None
        for b in buses:
            if b.get("status", "").lower() in ["maintenance", "out of service"]:
                continue
            
            conflict = False
            for assigned_start, assigned_end in b["assigned_intervals"]:
                # Check overlap
                if not (end_t <= assigned_start or start_t >= assigned_end):
                    conflict = True
                    break
            
            if not conflict:
                selected_bus = b
                break

        # Find available crew wrappers
        eligible_crew = []
        for c in crew:
            # Rule 1: Shift must cover the trip
            if start_t < c["shift_start"] or end_t > c["shift_end"]:
                continue
            
            # Rule 2: Fatigue / Rest checking
            if c["last_end_time"]:
                rest_needed = timedelta(hours=c["rest_time"])
                if start_t - c["last_end_time"] < rest_needed:
                    continue
            
            # Rule 3: Max Hours
            if c["worked_hours"] + trip_duration > c["max_work_hours"]:
                continue

            eligible_crew.append(c)

        # Professional scheduling policy:
        # 1) respect configured driver order/priority
        # 2) keep fairness with lower assignment count and worked hours
        selected_crew = None
        if eligible_crew:
            eligible_crew.sort(
                key=lambda c: (
                    c["priority_rank"],
                    c["assigned_count"],
                    c["worked_hours"],
                    c["last_end_time"] or datetime.min.replace(tzinfo=timezone.utc),
                )
            )
            selected_crew = eligible_crew[0]

        # Make the assignment if both available
        if selected_bus and selected_crew:
            assignments.append({
                "trip_id": trip["id"],
                "route_id": trip["route_id"],
                "route_name": trip["route_name"],
                "bus_id": selected_bus["id"],
                "bus_number": selected_bus["bus_number"],
                "crew_id": selected_crew["id"],
                "crew_name": selected_crew["name"],
                "start_time": start_t.isoformat(),
                "end_time": end_t.isoformat(),
            })
            
            # Update Trackers
            selected_bus["assigned_intervals"].append((start_t, end_t))
            selected_crew["worked_hours"] += trip_duration
            selected_crew["assigned_count"] += 1
            selected_crew["last_end_time"] = end_t
            metadata["successful_assignments"] += 1
        else:
            metadata["missed_trips"] += 1

    metadata["driver_ordering_policy"] = (
        "priority_order -> assigned_count -> worked_hours -> last_end_time"
    )

    return {
        "assignments": assignments,
        "metadata": metadata
    }
