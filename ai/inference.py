import torch
import rasterio
import numpy as np
import os
from model import ChangeNet

def run_inference(t1_path, t2_path, output_path, model_path=None):
    """
    Run change detection inference on a pair of images.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load Model
    model = ChangeNet(in_channels=4, n_classes=4) # 4 classes: Stable, Loss, Gain, Deg
    if model_path and os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
    else:
        print("Warning: No model weights found, using random initialization for demo.")
    
    model.to(device)
    model.eval()
    
    # Read Data
    with rasterio.open(t1_path) as src:
        t1 = src.read().astype(np.float32) / 10000.0
        meta = src.meta.copy()
        
    with rasterio.open(t2_path) as src:
        t2 = src.read().astype(np.float32) / 10000.0
        
    # Prepare Input
    t1_tensor = torch.from_numpy(t1).unsqueeze(0).to(device)
    t2_tensor = torch.from_numpy(t2).unsqueeze(0).to(device)
    
    # Inference
    with torch.no_grad():
        output = model(t1_tensor, t2_tensor)
        probs = torch.softmax(output, dim=1)
        preds = torch.argmax(probs, dim=1).squeeze(0).cpu().numpy()
        
    # Save Result
    meta.update(count=1, dtype=rasterio.uint8)
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(preds.astype(rasterio.uint8), 1)

if __name__ == "__main__":
    # Demo
    pass
