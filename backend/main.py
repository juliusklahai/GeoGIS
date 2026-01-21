from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2 import Geometry
import os
import subprocess
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ForestWatch API")

# Serve Frontend
if os.path.exists("frontend"):
    app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="frontend")
elif os.path.exists("backend/frontend"): # Handling local run vs docker
    app.mount("/dashboard", StaticFiles(directory="backend/frontend", html=True), name="frontend")

# Use DATABASE_URL from .env (Supabase Connection String)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to local if not provided
    DATABASE_URL = "postgresql://user:password@localhost:5432/geogis"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models (Simplified for API)
class Scene(Base):
    __tablename__ = "scenes"
    id = Column(Integer, primary_key=True, index=True)
    stac_id = Column(String)
    sensor = Column(String)
    acquisition_date = Column(Date)
    cloud_cover = Column(Float)

# Schemas
class IngestRequest(BaseModel):
    bbox: List[float]
    start_date: date
    end_date: date
    sensor: str = "Sentinel-2"

class ProcessRequest(BaseModel):
    year: int
    month: int
    sensor: str = "Sentinel-2"

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background Tasks
def run_ingestion(bbox, start_date, end_date, sensor):
    # In a real app, import the function. Here we call the script.
    # We need to pass args to the script, but the script currently has hardcoded args in __main__
    # For this demo, we'll just print.
    print(f"Starting ingestion for {sensor} from {start_date} to {end_date}")
    # subprocess.run(["python", "processing/ingest_s2.py", ...])

def run_pipeline(year, month, sensor):
    print(f"Starting pipeline for {sensor} {year}-{month}")
    # subprocess.run(["python", "processing/pipeline.py", ...])

@app.post("/jobs/ingest")
def trigger_ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion, request.bbox, request.start_date, request.end_date, request.sensor)
    return {"message": "Ingestion job started"}

@app.post("/jobs/process")
def trigger_process(request: ProcessRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline, request.year, request.month, request.sensor)
    return {"message": "Processing job started"}

@app.get("/scenes", response_model=List[dict])
def list_scenes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scenes = db.query(Scene).offset(skip).limit(limit).all()
    return [{"id": s.id, "sensor": s.sensor, "date": s.acquisition_date} for s in scenes]

@app.get("/health")
def health_check():
    return {"status": "ok"}

