from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import auth, bus as bus_router, crew as crew_router, routes, schedule as schedule_router, upload

# Initialize Firebase Admin using Application Default Credentials.
# On Render, set GOOGLE_APPLICATION_CREDENTIALS as an environment variable.
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
app.include_router(crew_router.router)
app.include_router(bus_router.router)
app.include_router(routes.router)
app.include_router(schedule_router.router)
app.include_router(upload.router)


@app.get("/")
def root() -> dict:
    return {"status": "live", "message": "RouteConnect Backend is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "db": "postgresql"}
