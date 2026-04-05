from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import uuid
import logging
import firebase_admin
from firebase_admin import credentials

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import (
    auth,
    bus as bus_router,
    chat,
    crew as crew_router,
    handover,
    map_data,
    notifications,
    routes,
    schedule as schedule_router,
    tracking,
    upload,
)

# Initialize Firebase Admin using Service Account or Default Credentials
try:
    cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-credentials.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        options = {"databaseURL": settings.FIREBASE_DATABASE_URL} if settings.FIREBASE_DATABASE_URL else None
        firebase_admin.initialize_app(cred, options)
    else:
        options = {"databaseURL": settings.FIREBASE_DATABASE_URL} if settings.FIREBASE_DATABASE_URL else None
        firebase_admin.initialize_app(options=options)
except ValueError:
    print("Firebase Admin already initialized or invalid configuration.")

setup_logging()
logger = logging.getLogger("routeconnect.api")

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
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(handover.router)
app.include_router(map_data.router)
app.include_router(tracking.router)

_RATE_BUCKET: dict[str, list[float]] = {}


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.time()
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"

    if not path.startswith("/docs") and not path.startswith("/openapi"):
        key = f"{client_ip}:{path}"
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS
        entries = [ts for ts in _RATE_BUCKET.get(key, []) if ts >= window_start]
        if len(entries) >= settings.RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "request_id": request_id},
            )
        entries.append(now)
        _RATE_BUCKET[key] = entries

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled request error", extra={"request_id": request_id, "path": path})
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
        )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    elapsed_ms = int((time.time() - started) * 1000)
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": elapsed_ms,
            "client_ip": client_ip,
        },
    )
    return response


@app.get("/")
def root() -> dict:
    return {"status": "live", "message": "RouteConnect Backend is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "db": "postgresql"}
