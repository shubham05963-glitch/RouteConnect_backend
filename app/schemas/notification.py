from datetime import datetime
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=2, max_length=1000)
    target_role: str = Field(default="all", min_length=2, max_length=24)
    severity: str = Field(default="info", min_length=2, max_length=16)


class NotificationRead(BaseModel):
    id: str
    title: str
    body: str
    target_role: str
    severity: str
    created_by: str
    created_at: datetime
    is_read: bool = False
