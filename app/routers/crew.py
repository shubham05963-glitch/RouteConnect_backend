from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.crew import CrewCreate, CrewRead

router = APIRouter(prefix="/api/crew", tags=["crew"])

@router.get("/", response_model=List[CrewRead])
def get_crew(db: Client = Depends(get_db)):
    crew_ref = db.collection('crew').stream()
    crew_list = []
    for c in crew_ref:
        data = c.to_dict()
        data['id'] = sum(ord(ch) for ch in c.id) # simple schema integer map
        crew_list.append(data)
    return crew_list

@router.post("/", response_model=CrewRead, status_code=status.HTTP_201_CREATED)
def create_crew(
    crew_in: CrewCreate, db: Client = Depends(get_db), user=Depends(get_current_user)
):
    docs = db.collection('crew').where("license_number", "==", crew_in.license_number).stream()
    if any(docs):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Crew member already exists")

    doc_ref = db.collection('crew').document()
    data_to_save = crew_in.model_dump()
    doc_ref.set(data_to_save)
    
    saved_data = data_to_save.copy()
    saved_data["id"] = sum(ord(ch) for ch in doc_ref.id)
    return saved_data
