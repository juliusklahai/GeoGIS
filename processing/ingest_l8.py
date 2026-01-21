import os
import logging
from pystac_client import Client
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from models import Scene

# Configuration
STAC_API_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "landsat-c2-l2" # Check exact collection name for Earth Search or use USGS
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/geogis")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Setup DB
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

def search_scenes(bbox, date_range, max_cloud_cover=20):
    client = Client.open(STAC_API_URL)
    search = client.search(
        collections=[COLLECTION],
        bbox=bbox,
        datetime=date_range,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}}
    )
    items = list(search.items())
    logger.info(f"Found {len(items)} scenes")
    return items

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def process_scene(item):
    scene_id = item.id
    scene_dir = os.path.join(DATA_DIR, "raw", "landsat", scene_id)
    os.makedirs(scene_dir, exist_ok=True)
    
    # Landsat bands (Red, Green, Blue, NIR) - check asset keys
    bands = ["red", "green", "blue", "nir08"]
    
    downloaded = False
    for band in bands:
        if band in item.assets:
            url = item.assets[band].href
            ext = os.path.splitext(url)[1]
            output_path = os.path.join(scene_dir, f"{band}{ext}")
            
            if not os.path.exists(output_path):
                logger.info(f"Downloading {band} for {scene_id}")
                if download_file(url, output_path):
                    downloaded = True
            else:
                downloaded = True

    if downloaded:
        db = next(get_db())
        existing = db.query(Scene).filter(Scene.stac_id == scene_id).first()
        
        if not existing:
            geom = shape(item.geometry)
            scene = Scene(
                stac_id=scene_id,
                sensor="Landsat",
                acquisition_date=item.datetime.date(),
                cloud_cover=item.properties.get("eo:cloud_cover", 0),
                geometry=from_shape(geom, srid=4326),
                storage_path=scene_dir
            )
            db.add(scene)
            db.commit()
            logger.info(f"Saved metadata for {scene_id}")

if __name__ == "__main__":
    import time
    time.sleep(5)
    bbox = (28.8, -2.9, 30.9, -1.0)
    dates = "2023-01-01/2023-01-10"
    items = search_scenes(bbox, dates)
    for item in items:
        process_scene(item)
