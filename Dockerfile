FROM python:3.10-slim

# Install system dependencies for spatial libraries
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (from the backend folder)
COPY backend/requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY backend/ .
COPY frontend/ ./frontend/

# Railway uses the PORT env var
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
