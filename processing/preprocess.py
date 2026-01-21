import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import Resampling as ResamplingEnums
import numpy as np
import os
from scipy.ndimage import median_filter

def reproject_resample(input_path, output_path, dst_crs='EPSG:3857', resolution=10):
    """
    Reproject and resample a raster to a target CRS and resolution.
    """
    with rasterio.open(input_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=resolution)
        
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=ResamplingEnums.bilinear)

def calculate_ndvi(red_path, nir_path, output_path):
    """
    Calculate NDVI from Red and NIR bands.
    """
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        red = red_src.read(1).astype(float)
        nir = nir_src.read(1).astype(float)
        
        # Avoid division by zero
        ndvi = (nir - red) / (nir + red + 1e-10)
        
        meta = red_src.meta.copy()
        meta.update(dtype=rasterio.float32, count=1)
        
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(ndvi.astype(rasterio.float32), 1)

def filter_speckle(input_path, output_path, size=3):
    """
    Apply a simple median filter for speckle reduction in SAR data.
    """
    with rasterio.open(input_path) as src:
        data = src.read(1)
        filtered = median_filter(data, size=size)
        
        meta = src.meta.copy()
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(filtered, 1)

def create_median_composite(scene_paths, output_path):
    """
    Create a median composite from a list of scene paths (same band).
    Assumes all inputs are already reprojected/aligned.
    """
    if not scene_paths:
        return
    
    # Read first to get meta
    with rasterio.open(scene_paths[0]) as src:
        meta = src.meta.copy()
        shape = src.shape
        
    stack = np.zeros((len(scene_paths), shape[0], shape[1]), dtype=rasterio.float32)
    
    for idx, path in enumerate(scene_paths):
        with rasterio.open(path) as src:
            # Handle different sizes if alignment isn't perfect (crop/pad) - simplified here
            data = src.read(1)
            if data.shape == shape:
                stack[idx] = data
            else:
                # In real world, use reproject/warp to match reference
                pass 

    # Calculate median ignoring NaNs/NoData
    composite = np.nanmedian(stack, axis=0)
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(composite.astype(meta['dtype']), 1)
