from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    license_number = Column(String, unique=True, nullable=False, index=True)
    shift = Column(String, nullable=False)
