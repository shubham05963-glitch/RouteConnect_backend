from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from google.cloud.firestore import Client

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.handover import HandoverCreate, HandoverRead

router = APIRouter(prefix="/api/handover", tags=["handover"])


@router.post("", response_model=HandoverRead, status_code=status.HTTP_201_CREATED)
def submit_handover(
    payload: HandoverCreate,
    db: Client = Depends(get_db),
    user=Depends(get_current_user),
):
    data = {
        "crew_id": payload.crew_id.strip(),
        "bus_id": payload.bus_id.strip(),
        "notes": payload.notes.strip(),
        "created_at": datetime.now(timezone.utc),
        "submitted_by": str(user.get("email", "")),
    }
    ref = db.collection("handover_reports").document()
    ref.set(data)
    return {"id": ref.id, **data}
