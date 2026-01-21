from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    stac_id = Column(String, unique=True, index=True)
    sensor = Column(String, index=True)  # Sentinel-2, Landsat-8, etc.
    acquisition_date = Column(Date, index=True)
    cloud_cover = Column(Float)
    geometry = Column(Geometry("POLYGON", srid=4326))
    storage_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Composite(Base):
    __tablename__ = "composites"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    sensor = Column(String)
    storage_path = Column(String)  # Path to COG
    geometry = Column(Geometry("POLYGON", srid=4326))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChangeDetection(Base):
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    baseline_composite_id = Column(Integer, ForeignKey("composites.id"))
    target_composite_id = Column(Integer, ForeignKey("composites.id"))
    change_type = Column(String)  # Loss, Gain, Degradation, Stable
    confidence = Column(Float)
    geometry = Column(Geometry("POLYGON", srid=4326))
    area_ha = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
