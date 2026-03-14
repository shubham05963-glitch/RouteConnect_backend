from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.route import Route
from app.schemas.route import RouteCreate, RouteRead

router = APIRouter(prefix="/api", tags=["routes"])


@router.post("/routes", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(
    route_in: RouteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
) -> RouteRead:
    # For simplicity, we store the geometry as JSON.
    route = Route(**route_in.dict())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.get("/routes", response_model=list[RouteRead])
def list_routes(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[RouteRead]:
    return db.query(Route).all()
