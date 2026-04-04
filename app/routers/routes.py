from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.route import RouteCreate, RouteRead

router = APIRouter(prefix="/api/routes", tags=["routes"])

@router.get("/", response_model=List[RouteRead])
def get_routes(db: Client = Depends(get_db)):
    route_ref = db.collection('routes').stream()
    routes_list = []
    for r in route_ref:
        data = r.to_dict()
        data['id'] = sum(ord(ch) for ch in r.id)
        routes_list.append(data)
    return routes_list

@router.post("/", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(
    route_in: RouteCreate, db: Client = Depends(get_db), user=Depends(get_current_user)
):
    doc_ref = db.collection('routes').document()
    data_to_save = route_in.model_dump()
    doc_ref.set(data_to_save)
    
    saved_data = data_to_save.copy()
    saved_data["id"] = sum(ord(ch) for ch in doc_ref.id)
    return saved_data
