import torch
import numpy as np
from utils.common import verbose_print

def normalize_hu(scan_tensor: torch.Tensor, min_hu: int, max_hu: int, verbose: bool = False) -> torch.Tensor:
    """
    Normalizes the Hounsfield Units (HU) of the scan array to the specified range.
    """
    verbose_print(f"Normalizing Hounsfield Units to range [{min_hu}, {max_hu}]...", verbose)

    # Perform normalization using PyTorch
    scan_tensor = torch.clamp(scan_tensor, min=min_hu, max=max_hu)
    scan_tensor = (scan_tensor - min_hu) / (max_hu - min_hu)

    verbose_print("Normalization complete.", verbose)
    return scan_tensor