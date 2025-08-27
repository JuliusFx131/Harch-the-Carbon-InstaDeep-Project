import os
import torch
import rasterio
import warnings
import numpy as np
import argparse
from tqdm import tqdm
from glob import glob
import segmentation_models_pytorch as smp
from torch.utils.data import Dataset, DataLoader

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ---------- Helper: vegetation indices ----------
def compute_indices(chip):
    indices = []
    for t in range(3):
        b = chip[t*6 + 0].astype(np.float32)
        g = chip[t*6 + 1].astype(np.float32)
        r = chip[t*6 + 2].astype(np.float32)
        nir = chip[t*6 + 3].astype(np.float32)
        swir1 = chip[t*6 + 4].astype(np.float32)
        swir2 = chip[t*6 + 5].astype(np.float32)

        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir - r) / (nir + r + 1e-6)
            ndwi = (g - nir) / (g + nir + 1e-6)
            evi = 2.5 * (nir - r) / (nir + 6*r - 7.5*b + 1)
            nbr = (nir - swir2) / (nir + swir2 + 1e-6)
        indices.extend([ndvi, ndwi, evi, nbr])
    return np.stack(indices, axis=0)

# ---------- Dataset for TEST ----------
class BiomassTestDataset(Dataset):
    def __init__(self, chips_dir):
        self.chips_dir = chips_dir
        self.files = sorted([f for f in os.listdir(chips_dir) if f.endswith(".tif")])
        print(f"Found {len(self.files)} test chips in '{chips_dir}'")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        chip_file = os.path.join(self.chips_dir, self.files[idx])
        
        with rasterio.open(chip_file) as src:
            chip = src.read().astype(np.float32) / 10000.0
        
        vi = compute_indices(chip)
        x = np.concatenate([chip, vi], axis=0)
        x = torch.tensor(x, dtype=torch.float32)

        return x, self.files[idx]

def main(args):
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory: '{args.output_dir}'")

    # Prepare DataLoader
    test_ds = BiomassTestDataset(args.chips_dir)
    test_loader = DataLoader(
        test_ds,
        batch_size=1,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )

    # Load model
    print("Loading model...")
    model = smp.Unet(
        encoder_name="efficientnet-b3",
        encoder_weights=None,
        in_channels=30,
        classes=1
    )
    model.load_state_dict(torch.load(args.model_weights, map_location=device))
    model.to(device)
    model.eval()
    print("Model loaded successfully!")

    # Run inference
    print("Starting inference...")
    with torch.no_grad():
        for x, fnames in tqdm(test_loader, desc="Predicting"):
            x = x.to(device)
            for i in range(x.size(0)):
                pred = model(x[i:i+1])
                mask = pred.squeeze().cpu().numpy().astype(np.float32)
                
                fname = fnames[i]
                out_name = os.path.splitext(fname)[0].replace("chip_", "prediction_") + ".tif"
                out_path = os.path.join(args.output_dir, out_name)

                # Save prediction as GeoTIFF
                with rasterio.open(
                    out_path,
                    "w",
                    driver="GTiff",
                    height=mask.shape[0],
                    width=mask.shape[1],
                    count=1,
                    dtype=mask.dtype
                ) as dst:
                    dst.write(mask, 1)
    print("Inference complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run biomass estimation inference on a directory of chips.')
    parser.add_argument('--chips_dir', type=str, required=True,
                       help='Path to the directory containing input .tif chips')
    parser.add_argument('--model_weights', type=str, required=True,
                       help='Path to the trained model weights file (e.g., unet_weights.pth)')
    parser.add_argument('--output_dir', type=str, default='./predictions',
                       help='Path to the directory where prediction .tif files will be saved (default: ./predictions)')
    
    args = parser.parse_args()
    main(args)