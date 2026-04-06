from fastapi import APIRouter, Depends
from google.cloud.firestore import Client
from firebase_admin import db as firebase_db

from app.db.session import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["tracking"])


@router.get("/bus-location")
def get_bus_locations(db: Client = Depends(get_db), user=Depends(get_current_user)):
    # Primary source: Firebase Realtime DB (driver app writes here every few seconds)
    try:
        snapshot = firebase_db.reference("bus_locations").get()
        if isinstance(snapshot, dict):
            items = []
            for bus_id, data in snapshot.items():
                if not isinstance(data, dict):
                    continue
                items.append(
                    {
                        "bus_id": data.get("bus_id", bus_id),
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "speed": data.get("speed"),
                        "timestamp": data.get("timestamp"),
                    }
                )
            return items
    except Exception:
        pass

    # Fallback source: Firestore collection
    docs = db.collection("bus_locations").stream()
    items = []
    for doc in docs:
        data = doc.to_dict() or {}
        items.append(
            {
                "bus_id": data.get("bus_id", doc.id),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "speed": data.get("speed"),
                "timestamp": data.get("timestamp"),
            }
        )
    return items


from app.services.ai_scheduler import calculate_eta
from app.services.delhi_map_data import DELHI_STOPS

@router.get("/eta/{bus_id}/{stop_id}")
def get_bus_eta(bus_id: str, stop_id: str, db: Client = Depends(get_db), user=Depends(get_current_user)):
    # Get latest bus location
    bus_locations = get_bus_locations(db, user)
    bus_loc = next((loc for loc in bus_locations if loc['bus_id'] == bus_id), None)
    
    if not bus_loc:
        raise HTTPException(status_code=404, detail="Bus location not found")
    
    # Find stop
    stop = next((s for s in DELHI_STOPS if s['stop_id'] == stop_id), None)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    eta_minutes = calculate_eta(bus_loc, stop)
    
    return {
        "bus_id": bus_id,
        "stop_id": stop_id,
        "eta_minutes": eta_minutes,
        "distance_km": geodesic(
            (bus_loc['latitude'], bus_loc['longitude']), 
            (stop['latitude'], stop['longitude'])
        ).kilometers,
        "current_speed_kmh": bus_loc.get('speed', 25.0)
    }
