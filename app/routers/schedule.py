from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.crew import Crew
from app.models.bus import Bus
from app.models.route import Route
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleRead
from app.services.ai_scheduler import generate_schedule

router = APIRouter(prefix="/api", tags=["schedule"])


@router.post("/schedule/generate", response_model=ScheduleRead)
def generate_schedule_endpoint(db: Session = Depends(get_db), user=Depends(get_current_user)) -> ScheduleRead:
    # Serialize only fields needed for scheduling
    crew = [
        {"id": c.id, "name": c.name, "license_number": c.license_number, "shift": c.shift}
        for c in db.query(Crew).all()
    ]
    buses = [
        {"id": b.id, "bus_number": b.bus_number, "capacity": b.capacity, "status": b.status}
        for b in db.query(Bus).all()
    ]
    routes = [
        {"id": r.id, "name": r.name, "description": r.description, "geometry": r.geometry}
        for r in db.query(Route).all()
    ]

    if not crew or not buses or not routes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one crew member, bus, and route are required to generate a schedule.",
        )

    schedule_data = generate_schedule(crew=crew, buses=buses, routes=routes)
    schedule = Schedule(
        name=f"Schedule {datetime.utcnow().isoformat()}",
        data=schedule_data,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.get("/schedule", response_model=list[ScheduleRead])
def list_schedules(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[ScheduleRead]:
    return db.query(Schedule).order_by(Schedule.generated_at.desc()).all()
