from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.crew import Crew
from app.schemas.crew import CrewCreate, CrewRead

router = APIRouter(prefix="/api", tags=["crew"])


@router.post("/crew", response_model=CrewRead, status_code=status.HTTP_201_CREATED)
def create_crew(
    crew_in: CrewCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
) -> CrewRead:
    existing = db.query(Crew).filter(Crew.license_number == crew_in.license_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Crew member already exists")

    crew = Crew(**crew_in.dict())
    db.add(crew)
    db.commit()
    db.refresh(crew)
    return crew


@router.get("/crew", response_model=list[CrewRead])
def list_crew(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[CrewRead]:
    return db.query(Crew).all()
