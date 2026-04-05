# RouteConnect Backend

Backend service for the Automated Bus Scheduling & Route Management System.

## Features

- REST API (FastAPI)
- JWT + Firebase ID-token authentication
- Firestore-backed modules for crew, buses, routes, schedules
- Chat API for driver/passenger dispatch messaging
- Notifications API with role-based publishing
- Global rate limiting + security headers + structured JSON logs

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
FIREBASE_DATABASE_URL=https://<your-project-id>-default-rtdb.firebaseio.com

# API hardening
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
REQUIRE_AUTH_FOR_READS=true
```

4. Run the server (development)

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Running in Production (Recommended)

### Option 1: Render (Cloud Hosting)

1. **Push your code to GitHub** (if not already done).

2. **Connect to Render:**
   - Go to [render.com](https://render.com) and sign up/login.
   - Click "New +" → "Web Service".
   - Connect your GitHub repo (`RouteConnect_backend`).
   - Choose "Docker" as the runtime (uses your `Dockerfile`).

3. **Configure Environment Variables:**
   In Render dashboard, set these env vars:
   - `ENV=production`
   - `HOST=0.0.0.0`
   - `PORT=10000` (Render assigns this automatically)
   - `BACKEND_CORS_ORIGINS=https://your-frontend-domain.com` (replace with your frontend URL)
   - `DATABASE_URL=postgresql://...` (from Render's managed Postgres)
   - `JWT_SECRET=<your-secret>` (generate a new one for production)
   - `JWT_ALGORITHM=HS256`
   - `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60`

4. **Add a Database:**
   - In Render, create a "PostgreSQL" service.
   - Copy the `DATABASE_URL` from the Postgres service and paste it into your web service env vars.

5. **Deploy:**
   - Render will build from your `Dockerfile` and start the service.
   - Your API will be live at `https://your-service-name.onrender.com`.

### Option 2: Docker (recommended for hosting)

```powershell
# build + start
docker compose up --build -d
```

Then visit http://localhost:8000 (or the host/IP where you deployed).

### Option 3: Gunicorn + Uvicorn workers

```powershell
gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000 --workers 4
```

Make sure `ENV=production` in `.env` and `JWT_SECRET` is strong.

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
- `GET /api/chat/messages` (fetch chat messages)
- `POST /api/chat/messages` (send chat message)
- `GET /api/notifications` (fetch notifications)
- `POST /api/notifications` (create notification: admin/manager/dispatcher)
- `PATCH /api/notifications/{id}/read` (mark as read)
- `POST /api/handover` (submit driver handover report)

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
- `GET /api/chat/messages` - list chat messages by channel
- `POST /api/chat/messages` - create chat message
- `GET /api/notifications` - list notifications for current role
- `POST /api/notifications` - create notification (role-protected)
- `PATCH /api/notifications/{id}/read` - mark notification as read
- `POST /api/handover` - submit handover report

