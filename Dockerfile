FROM python:3.12-slim

# Install system deps for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose a default port (Render / other hosting platforms will provide the real port via $PORT).
EXPOSE 8000

# Use $PORT when available (e.g. Render). Fall back to 8000 when running locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
