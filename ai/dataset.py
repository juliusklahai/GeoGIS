import torch
from torch.utils.data import Dataset
import rasterio
import numpy as np
import os

class ChangeDetectionDataset(Dataset):
    def __init__(self, t1_paths, t2_paths, labels_paths=None, transform=None):
        """
        t1_paths: List of paths to T1 images (stacked bands)
        t2_paths: List of paths to T2 images (stacked bands)
        labels_paths: List of paths to label masks (optional)
        """
        self.t1_paths = t1_paths
        self.t2_paths = t2_paths
        self.labels_paths = labels_paths
        self.transform = transform

    def __len__(self):
        return len(self.t1_paths)

    def __getitem__(self, idx):
        with rasterio.open(self.t1_paths[idx]) as src:
            t1 = src.read().astype(np.float32)
            
        with rasterio.open(self.t2_paths[idx]) as src:
            t2 = src.read().astype(np.float32)
            
        # Normalize (simple min-max or standardization)
        t1 = t1 / 10000.0 # Sentinel-2 scaling
        t2 = t2 / 10000.0
        
        sample = {'t1': torch.from_numpy(t1), 't2': torch.from_numpy(t2)}

        if self.labels_paths:
            with rasterio.open(self.labels_paths[idx]) as src:
                label = src.read(1).astype(np.long)
            sample['label'] = torch.from_numpy(label)

        if self.transform:
            sample = self.transform(sample)

        return sample
