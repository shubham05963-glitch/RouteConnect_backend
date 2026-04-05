from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.bus import BusCreate, BusRead

router = APIRouter(prefix="/api/bus", tags=["bus"])

@router.get("/", response_model=List[BusRead])
def get_buses(db: Client = Depends(get_db), user=Depends(get_current_user)):
    buses_ref = db.collection('buses').stream()
    buses = []
    for b in buses_ref:
        data = b.to_dict()
        data['id'] = int(b.id) if b.id.isdigit() else b.id  # Schema expects int or coerced
        buses.append(data)
    return buses

@router.post("/", response_model=BusRead, status_code=status.HTTP_201_CREATED)
def create_bus(
    bus_in: BusCreate, db: Client = Depends(get_db), user=Depends(get_current_user)
):
    # Check if exists
    docs = db.collection('buses').where("bus_number", "==", bus_in.bus_number).stream()
    if any(docs):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bus number already exists")

    # Generate a simple auto-increment ID for the doc or rely on Firebase UUID
    # We will let Firebase assign an ID, but for the 'id' field in schema we can map it
    doc_ref = db.collection('buses').document()
    
    # Store string ID back as 'id' to fulfill Pydantic
    try:
        # Schema expects an integer ID historically, but Pydantic might accept strings if configured or we can hash
        # To avoid schema breaks if clients expect integers, we use simple counter math in prod. 
        # For this refactor, we let it be string casted to int/string per schema
        data_to_save = bus_in.model_dump()
        doc_ref.set(data_to_save)
        
        saved_data = data_to_save.copy()
        # Mock integer ID for pydantic backwards compatibility or use firestore string
        saved_data["id"] = sum(ord(c) for c in doc_ref.id) 
        
        return saved_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
