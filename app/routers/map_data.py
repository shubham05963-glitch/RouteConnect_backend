from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.services.delhi_map_data import DELHI_ROUTES, DELHI_STOPS

router = APIRouter(prefix="/api/map/delhi", tags=["map"])


@router.get("/routes")
def get_delhi_routes(user=Depends(get_current_user)):
    return DELHI_ROUTES


@router.get("/stops")
def get_delhi_stops(user=Depends(get_current_user)):
    return DELHI_STOPS
