from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    channel: str = Field(default="dispatch", min_length=2, max_length=64)
    text: str = Field(min_length=1, max_length=1000)


class ChatMessageRead(BaseModel):
    id: str
    channel: str
    sender_email: str
    sender_role: str
    text: str
    created_at: datetime
