from sqlalchemy import Column, Integer, JSON, String

from app.models.base import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    geometry = Column(JSON, nullable=False)
