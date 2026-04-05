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
