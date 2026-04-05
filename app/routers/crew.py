from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.crew import CrewCreate, CrewRead

router = APIRouter(prefix="/api/crew", tags=["crew"])

@router.get("/", response_model=List[CrewRead])
def get_crew(db: Client = Depends(get_db), user=Depends(get_current_user)):
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
    by_license = db.collection('crew').where("license_number", "==", crew_in.license_number).stream()
    by_driver = (
        db.collection('crew').where("driver_id", "==", crew_in.driver_id).stream()
        if crew_in.driver_id
        else []
    )
    if any(by_license) or any(by_driver):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Crew member already exists")

    doc_ref = db.collection('crew').document()
    data_to_save = crew_in.model_dump()
    doc_ref.set(data_to_save)
    
    saved_data = data_to_save.copy()
    saved_data["id"] = sum(ord(ch) for ch in doc_ref.id)
    return saved_data


@router.delete("/by-driver/{driver_id}", status_code=status.HTTP_200_OK)
def delete_crew_by_driver_id(
    driver_id: str, db: Client = Depends(get_db), user=Depends(get_current_user)
):
    docs = list(db.collection("crew").where("driver_id", "==", driver_id).stream())
    if not docs:
        return {"deleted": 0}
    for d in docs:
        d.reference.delete()
    return {"deleted": len(docs)}
