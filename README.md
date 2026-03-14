# RouteConnect Backend

Backend service for the Automated Bus Scheduling & Route Management System.

## Features

- REST API (FastAPI)
- JWT authentication
- PostgreSQL / SQLite compatible via SQLAlchemy
- Modules for crew, buses, routes, schedules
- AI scheduling integration point (stubbed)

## Setup

1. Create and activate a Python venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Configure environment variables (create a `.env` file)

```text
# Set to "production" when hosting live.
ENV=development

# API host and port.
HOST=0.0.0.0
PORT=8000

# Allowed CORS origins, comma separated.
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database config (use Postgres in production)
DATABASE_URL=sqlite:///./routeconnect.db

# JWT configuration
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

4. Run the server (development)

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Running in Production (Recommended)

### Option 1: Docker (recommended for hosting)

```powershell
# build + start
docker compose up --build -d
```

Then visit http://localhost:8000 (or the host/IP where you deployed).

### Option 2: Gunicorn + Uvicorn workers

```powershell
gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000 --workers 4
```

---

## API Base URL

When running locally, the base URL is:

```
http://localhost:8000
```

When deployed, the base URL is whatever host/port you expose (e.g. `https://api.yourdomain.com`).

API endpoints are under `/api`, for example:

- `POST /api/register` (create user)
- `POST /api/login` (get JWT token)
- `POST /api/crew` (create crew member)
- `GET /api/crew` (list crew members)
- `POST /api/bus` (register bus)
- `GET /api/bus` (list buses)
- `POST /api/routes` (save route)
- `GET /api/routes` (list routes)
- `POST /api/schedule/generate` (generate schedule)

## API Docs

Interactive API docs are available at:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

- `POST /api/login` - authenticate and receive JWT
- `POST /api/crew` - create crew member
- `GET /api/crew` - list crew members
- `POST /api/bus` - register bus
- `GET /api/bus` - list buses
- `POST /api/routes` - save route
- `GET /api/routes` - list routes
- `POST /api/schedule/generate` - trigger AI schedule generation (stub)

