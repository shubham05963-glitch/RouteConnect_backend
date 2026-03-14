from typing import Any, Dict

from pydantic import BaseModel


class ScheduleBase(BaseModel):
    name: str
    data: Dict[str, Any]


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleRead(ScheduleBase):
    id: int

    class Config:
        orm_mode = True
