import os
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Scene, Composite
from preprocess import reproject_resample, calculate_ndvi, create_median_composite, filter_speckle

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/geogis")
DATA_DIR = os.getenv("DATA_DIR", "data")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_monthly_pipeline(year, month, sensor="Sentinel-2"):
    """
    Run the full pipeline for a specific month.
    """
    db = next(get_db())
    
    # 1. Query scenes for the month
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
        
    scenes = db.query(Scene).filter(
        Scene.sensor == sensor,
        Scene.acquisition_date >= start_date,
        Scene.acquisition_date < end_date
    ).all()
    
    if not scenes:
        logger.info(f"No scenes found for {year}-{month}")
        return

    logger.info(f"Processing {len(scenes)} scenes for {year}-{month}")
    
    # 2. Preprocess each scene (Reproject/Resample)
    processed_files = {"red": [], "nir": []} # Track paths for compositing
    
    for scene in scenes:
        # Example: Process Red and NIR bands
        bands = ["red", "nir"]
        for band in bands:
            # Find the file
            # In a real system, we'd have a better way to map band names to files
            # Here we assume a naming convention from ingest
            input_path = None
            for f in os.listdir(scene.storage_path):
                if band in f:
                    input_path = os.path.join(scene.storage_path, f)
                    break
            
            if input_path:
                output_dir = os.path.join(DATA_DIR, "processed", str(year), str(month), scene.stac_id)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{band}.tif")
                
                if not os.path.exists(output_path):
                    reproject_resample(input_path, output_path)
                
                processed_files[band].append(output_path)

    # 3. Create Composites
    composite_dir = os.path.join(DATA_DIR, "composites", str(year), str(month))
    os.makedirs(composite_dir, exist_ok=True)
    
    for band, paths in processed_files.items():
        if paths:
            output_path = os.path.join(composite_dir, f"{band}_composite.tif")
            create_median_composite(paths, output_path)
            logger.info(f"Created {band} composite")

    # 4. Calculate NDVI Composite
    red_comp = os.path.join(composite_dir, "red_composite.tif")
    nir_comp = os.path.join(composite_dir, "nir_composite.tif")
    
    if os.path.exists(red_comp) and os.path.exists(nir_comp):
        ndvi_path = os.path.join(composite_dir, "ndvi.tif")
        calculate_ndvi(red_comp, nir_comp, ndvi_path)
        logger.info("Created NDVI composite")
        
        # Save Composite Metadata
        comp = Composite(
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            sensor=sensor,
            storage_path=composite_dir,
            # geometry=... (union of scene geometries)
        )
        db.add(comp)
        db.commit()

if __name__ == "__main__":
    # Example run
    run_monthly_pipeline(2023, 1)
