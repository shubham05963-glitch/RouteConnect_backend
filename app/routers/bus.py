from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.bus import Bus
from app.schemas.bus import BusCreate, BusRead

router = APIRouter(prefix="/api", tags=["bus"])


@router.post("/bus", response_model=BusRead, status_code=status.HTTP_201_CREATED)
def create_bus(
    bus_in: BusCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
) -> BusRead:
    existing = db.query(Bus).filter(Bus.bus_number == bus_in.bus_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bus number already exists")

    bus = Bus(**bus_in.dict())
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return bus


@router.get("/bus", response_model=list[BusRead])
def list_buses(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[BusRead]:
    return db.query(Bus).all()
