import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, validator


def load_dotenv(dotenv_path: str = ".env") -> None:
    """Basic dotenv loader that sets env vars if not already set."""
    env_path = Path(dotenv_path)
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


# Load env vars from .env when present (dev/local use)
load_dotenv()


class Settings(BaseModel):
    APP_NAME: str = "RouteConnect Backend"
    ENV: str = "development"  # set to 'production' in live deployments
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    DATABASE_URL: str = ""
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FIREBASE_DATABASE_URL: str = ""
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    REQUIRE_AUTH_FOR_READS: bool = True

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


# Build settings from the current environment (including values loaded from .env)
settings = Settings(
    APP_NAME=os.getenv("APP_NAME", "RouteConnect Backend"),
    ENV=os.getenv("ENV", "development"),
    DEBUG=str(os.getenv("DEBUG", "False")).lower() in ("1", "true", "yes"),
    HOST=os.getenv("HOST", "0.0.0.0"),
    PORT=int(os.getenv("PORT", 8000)),
    BACKEND_CORS_ORIGINS=os.getenv("BACKEND_CORS_ORIGINS", "*"),
    DATABASE_URL=os.getenv("DATABASE_URL"),
    JWT_SECRET=os.getenv("JWT_SECRET"),
    JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    FIREBASE_DATABASE_URL=os.getenv("FIREBASE_DATABASE_URL", ""),
    RATE_LIMIT_REQUESTS=int(os.getenv("RATE_LIMIT_REQUESTS", 120)),
    RATE_LIMIT_WINDOW_SECONDS=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60)),
    REQUIRE_AUTH_FOR_READS=str(os.getenv("REQUIRE_AUTH_FOR_READS", "true")).lower() in ("1", "true", "yes"),
)
