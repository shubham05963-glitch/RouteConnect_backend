from datetime import datetime
from pydantic import BaseModel, Field


class HandoverCreate(BaseModel):
    crew_id: str = Field(min_length=1, max_length=128)
    bus_id: str = Field(min_length=1, max_length=128)
    notes: str = Field(default="", max_length=2000)


class HandoverRead(BaseModel):
    id: str
    crew_id: str
    bus_id: str
    notes: str
    created_at: datetime
    submitted_by: str
