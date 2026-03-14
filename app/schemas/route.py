from typing import Any, Dict, Optional

from pydantic import BaseModel


class RouteBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry: Dict[str, Any]


class RouteCreate(RouteBase):
    pass


class RouteRead(RouteBase):
    id: int

    class Config:
        orm_mode = True
