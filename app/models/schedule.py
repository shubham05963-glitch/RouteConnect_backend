from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.models.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSON, nullable=False)
