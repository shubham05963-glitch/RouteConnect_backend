from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials

from app.core.config import settings
from app.core.logging import setup_logging
# Removed SQLAlchemy models/database engine
from app.routers import auth, bus, crew, routes, schedule, upload

# Initialize Firebase Admin using Application Default Credentials or explicit path
# Note: For production on Render, set GOOGLE_APPLICATION_CREDENTIALS in env config.
try:
    firebase_admin.initialize_app()
    print("Firebase Admin initialized successfully using default credentials.")
except ValueError:
    print("Firebase Admin already initialized or invalid configuration.")

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url="/redoc" if settings.ENV != "production" else None,
    openapi_url="/openapi.json" if settings.ENV != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(crew.router)
app.include_router(bus.router)
app.include_router(routes.router)
app.include_router(schedule.router)
app.include_router(upload.router)  # New Cloudinary upload router

@app.get("/")
def root() -> dict:
    return {"status": "live", "message": "RouteConnect Backend (Firebase + Cloudinary) is running"}

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "db": "firebase"}
