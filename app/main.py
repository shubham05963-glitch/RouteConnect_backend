from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.models.base import Base
from app.routers import auth, bus, crew, routes, schedule


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


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


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
