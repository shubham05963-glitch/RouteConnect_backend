from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String, unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="active")
