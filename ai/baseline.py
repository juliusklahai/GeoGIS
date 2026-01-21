import rasterio
import numpy as np

def detect_change_baseline(t1_ndvi_path, t2_ndvi_path, output_path, threshold=0.2):
    """
    Detect change based on NDVI difference.
    """
    with rasterio.open(t1_ndvi_path) as src1, rasterio.open(t2_ndvi_path) as src2:
        ndvi1 = src1.read(1)
        ndvi2 = src2.read(1)
        
        diff = ndvi2 - ndvi1
        
        # Classify
        # 0: Stable, 1: Loss (NDVI drop), 2: Gain (NDVI increase)
        change_map = np.zeros_like(diff, dtype=np.uint8)
        
        change_map[diff < -threshold] = 1 # Loss
        change_map[diff > threshold] = 2  # Gain
        
        meta = src1.meta.copy()
        meta.update(dtype=rasterio.uint8, count=1)
        
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(change_map, 1)
