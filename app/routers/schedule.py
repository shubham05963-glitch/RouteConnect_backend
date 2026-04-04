from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.schedule import ScheduleRead
from app.services.ai_scheduler import generate_schedule

router = APIRouter(prefix="/api", tags=["schedule"])

@router.post("/schedule/generate", response_model=ScheduleRead)
def generate_schedule_endpoint(db: Client = Depends(get_db)):
    # Fetch lists from Firestore
    crew_docs = list(db.collection('crew').stream())
    bus_docs = list(db.collection('buses').stream())
    route_docs = list(db.collection('routes').stream())

    # Safely convert to dicts containing string 'id', which AI scheduler code natively accepts
    crew = [{"id": c.id, **c.to_dict()} for c in crew_docs]
    buses = [{"id": b.id, **b.to_dict()} for b in bus_docs]
    routes = [{"id": r.id, **r.to_dict()} for r in route_docs]

    if not crew or not buses or not routes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one crew member, bus, and route are required to generate a schedule.",
        )

    # Let AI execute the optimization routines
    schedule_data = generate_schedule(crew=crew, buses=buses, routes=routes)
    
    schedule_payload = {
        "name": f"Schedule {datetime.now(timezone.utc).isoformat()}",
        "data": schedule_data,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    doc_ref = db.collection('schedules').document()
    doc_ref.set(schedule_payload)
    
    saved_data = schedule_payload.copy()
    saved_data["id"] = sum(ord(ch) for ch in doc_ref.id) # Schema backward compatibility

    return saved_data


@router.get("/schedule", response_model=list[ScheduleRead])
def list_schedules(db: Client = Depends(get_db)) -> list[ScheduleRead]:
    # Query schedules collection
    sched_ref = db.collection('schedules').order_by('generated_at', direction="DESCENDING").stream()
    sched_list = []
    for s in sched_ref:
        data = s.to_dict()
        data['id'] = sum(ord(ch) for ch in s.id)
        if 'generated_at' in data and type(data['generated_at']) == str:
            # Pydantic handles ISO strings or datetime objects automatically
            pass 
        sched_list.append(data)
    return sched_list
