from pydantic import BaseModel


class CrewBase(BaseModel):
    name: str
    license_number: str
    shift: str
    driver_id: str | None = None
    phone: str | None = None
    assigned_bus: str | None = None
    status: str = "active"
    priority_order: int = 999


class CrewCreate(CrewBase):
    pass


class CrewRead(CrewBase):
    id: int

    class Config:
        orm_mode = True
