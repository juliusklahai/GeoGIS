import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import pandas as pd
import numpy as np

def vectorize_change(raster_path, output_path):
    """
    Convert change raster to vector (GeoPackage).
    """
    with rasterio.open(raster_path) as src:
        image = src.read(1)
        mask = image > 0 # Ignore 0 (Stable/NoData)
        
        results = (
            {'properties': {'class_id': int(v)}, 'geometry': s}
            for i, (s, v) in enumerate(
                shapes(image, mask=mask, transform=src.transform))
        )
        
        geoms = list(results)
        
        if not geoms:
            print("No changes detected.")
            return

        gdf = gpd.GeoDataFrame.from_features(geoms)
        gdf.crs = src.crs
        
        # Save
        gdf.to_file(output_path, driver="GPKG")
        return gdf

def calculate_area(gdf):
    """
    Calculate area in hectares for each polygon.
    Assumes CRS is projected (meters). If geographic, need to reproject first.
    """
    # Check if CRS is projected
    if not gdf.crs.is_projected:
        # Reproject to an equal area projection (e.g., Albers or UTM)
        # For simplicity, let's use World Mercator or a local UTM if known.
        # Here we'll just warn or use a generic equal area.
        gdf = gdf.to_crs(epsg=3857) # Web Mercator is NOT equal area, but commonly used. Better: 6933 (Cylindrical Equal Area)
    
    gdf['area_ha'] = gdf.geometry.area / 10000.0
    return gdf

def zonal_statistics(change_gdf, admin_gdf):
    """
    Calculate change statistics per admin boundary.
    """
    # Spatial Join
    joined = gpd.sjoin(change_gdf, admin_gdf, how="inner", predicate="intersects")
    
    # Group by Admin ID and Class ID
    stats = joined.groupby(['admin_id', 'class_id'])['area_ha'].sum().reset_index()
    
    return stats
