FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .
# Copy frontend code so FastAPI can serve it
COPY frontend/ ./frontend/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
