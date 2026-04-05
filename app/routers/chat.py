from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Query, status
from google.cloud.firestore import Client

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.chat import ChatMessageCreate, ChatMessageRead

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/messages", response_model=List[ChatMessageRead])
def list_messages(
    channel: str = Query(default="dispatch", min_length=2, max_length=64),
    limit: int = Query(default=50, ge=1, le=200),
    db: Client = Depends(get_db),
    user=Depends(get_current_user),
):
    role = str(user.get("role", "passenger")).lower()
    normalized_channel = channel.strip().lower()
    if role == "passenger" and normalized_channel != "passenger":
        normalized_channel = "passenger"

    docs = (
        db.collection("chat_messages")
        .where("channel", "==", normalized_channel)
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        created_at = data.get("created_at")
        if hasattr(created_at, "isoformat"):
            created_at = created_at
        else:
            created_at = datetime.now(timezone.utc)
        result.append(
            {
                "id": doc.id,
                "channel": data.get("channel", normalized_channel),
                "sender_email": data.get("sender_email", ""),
                "sender_role": data.get("sender_role", "unknown"),
                "text": data.get("text", ""),
                "created_at": created_at,
            }
        )
    return list(reversed(result))


@router.post("/messages", response_model=ChatMessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: ChatMessageCreate,
    db: Client = Depends(get_db),
    user=Depends(get_current_user),
):
    role = str(user.get("role", "passenger")).lower()
    allowed_channels = {"dispatch", "passenger", "driver"}
    channel = payload.channel.strip().lower()
    if channel not in allowed_channels:
        channel = "dispatch"
    if role == "passenger":
        channel = "passenger"

    data = {
        "channel": channel,
        "sender_email": str(user.get("email", "")),
        "sender_role": role,
        "text": payload.text.strip(),
        "created_at": datetime.now(timezone.utc),
    }
    ref = db.collection("chat_messages").document()
    ref.set(data)
    return {
        "id": ref.id,
        **data,
    }
