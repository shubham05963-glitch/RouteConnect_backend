from pydantic import BaseModel


class CrewBase(BaseModel):
    name: str
    license_number: str
    shift: str


class CrewCreate(CrewBase):
    pass


class CrewRead(CrewBase):
    id: int

    class Config:
        orm_mode = True
