# National Spatial Monitoring System

A stand-alone system for monthly forest and land-cover change detection using Sentinel-2, Landsat, and Sentinel-1 data.

## Features
- **Automated Ingestion**: Downloads data from public STAC APIs (Earth Search).
- **Preprocessing**: Cloud masking, speckle filtering, and monthly compositing.
- **AI Change Detection**: Siamese U-Net model for detecting forest loss/gain.
- **Analysis**: Vectorization and area statistics.
- **API**: FastAPI backend for job management and data access.
- **Dashboard**: Simple web interface for visualization.

## Prerequisites
- Docker and Docker Compose
- 16GB+ RAM recommended
- GPU recommended for AI training/inference

## Setup

1.  **Clone the repository**
    ```bash
    git clone <repo-url>
    cd GeoGis
    ```

2.  **Start Services**
    ```bash
    docker compose up --build
    ```
    This will start:
    - PostGIS database (port 5432)
    - Backend API (port 8000)
    - Processing service (background)

3.  **Access the Dashboard**
    Open `frontend/index.html` in your browser.

## Usage API

- **Trigger Ingestion**:
    ```bash
    curl -X POST "http://localhost:8000/jobs/ingest" \
         -H "Content-Type: application/json" \
         -d '{"bbox": [29.0, -2.0, 30.0, -1.0], "start_date": "2023-01-01", "end_date": "2023-01-31"}'
    ```

- **Trigger Processing**:
    ```bash
    curl -X POST "http://localhost:8000/jobs/process" \
         -H "Content-Type: application/json" \
         -d '{"year": 2023, "month": 1}'
    ```

## Project Structure
- `backend/`: FastAPI application
- `processing/`: Ingestion and image processing scripts
- `ai/`: PyTorch models and inference
- `database/`: Database models and init scripts
- `frontend/`: Web dashboard
