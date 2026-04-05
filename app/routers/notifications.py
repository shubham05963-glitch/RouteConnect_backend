from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.cloud.firestore import Client

from app.db.session import get_db
from app.dependencies import get_current_user, require_roles
from app.schemas.notification import NotificationCreate, NotificationRead

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    db: Client = Depends(get_db),
    user=Depends(get_current_user),
):
    role = str(user.get("role", "passenger")).lower()
    docs = db.collection("notifications").order_by("created_at", direction="DESCENDING").limit(limit).stream()
    response: list[dict] = []
    for doc in docs:
        data = doc.to_dict()
        target = str(data.get("target_role", "all")).lower()
        if target not in {"all", role}:
            continue
        created_at = data.get("created_at")
        if not hasattr(created_at, "isoformat"):
            created_at = datetime.now(timezone.utc)
        read_by = data.get("read_by", [])
        user_id = str(user.get("doc_id", ""))
        response.append(
            {
                "id": doc.id,
                "title": data.get("title", ""),
                "body": data.get("body", ""),
                "target_role": target,
                "severity": data.get("severity", "info"),
                "created_by": data.get("created_by", ""),
                "created_at": created_at,
                "is_read": user_id in read_by,
            }
        )
    return response


@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    db: Client = Depends(get_db),
    user=Depends(require_roles("admin", "manager", "dispatcher")),
):
    data = {
        "title": payload.title.strip(),
        "body": payload.body.strip(),
        "target_role": payload.target_role.strip().lower(),
        "severity": payload.severity.strip().lower(),
        "created_by": str(user.get("email", "")),
        "created_at": datetime.now(timezone.utc),
        "read_by": [],
    }
    ref = db.collection("notifications").document()
    ref.set(data)
    return {"id": ref.id, **data, "is_read": False}


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_as_read(
    notification_id: str,
    db: Client = Depends(get_db),
    user=Depends(get_current_user),
):
    doc_ref = db.collection("notifications").document(notification_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Notification not found")

    data = doc.to_dict() or {}
    read_by = data.get("read_by", [])
    user_id = str(user.get("doc_id", ""))
    if user_id and user_id not in read_by:
        read_by.append(user_id)
        doc_ref.update({"read_by": read_by})
    return {"ok": True}
