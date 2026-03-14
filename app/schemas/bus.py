from pydantic import BaseModel


class BusBase(BaseModel):
    bus_number: str
    capacity: int
    status: str


class BusCreate(BusBase):
    pass


class BusRead(BusBase):
    id: int

    class Config:
        orm_mode = True
