import torch
import numpy as np
from utils.common import verbose_print
import torchio as tio  # Add torchio import

def normalize_hu(scan_tensor: torch.Tensor, min_hu: int, max_hu: int, verbose: bool = False) -> torch.Tensor:
    """
    Normalizes the Hounsfield Units (HU) of the scan array to the specified range.
    """
    verbose_print(f"Normalizing Hounsfield Units to range [{min_hu}, {max_hu}]...", verbose)

    # Perform normalization using torchio
    transform = tio.transforms.RescaleIntensity(out_min_max=(0, 1), in_min_max=(min_hu, max_hu))
    scan_tensor = transform(scan_tensor)

    verbose_print("Normalization complete.", verbose)
    return scan_tensor