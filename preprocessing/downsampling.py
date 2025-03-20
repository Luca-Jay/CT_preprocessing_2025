import torch
import scipy.ndimage
from utils.common import verbose_print
import numpy as np
from typing import Tuple

def downsample_ct(scan_tensor: torch.Tensor, target_shape: Tuple[int, int, int], order: int = 3, verbose=True) -> torch.Tensor:
    verbose_print(f"Original shape: {scan_tensor.shape}", verbose=True)
    verbose_print(f"Target shape: {target_shape}", verbose=True)

    zoom_factors = torch.tensor(target_shape, dtype=torch.float32) / torch.tensor(scan_tensor.shape, dtype=torch.float32)
    verbose_print(f"Zoom factors: {zoom_factors}", verbose=True)

    # Perform downsampling using PyTorch
    downsampled_scan = torch.nn.functional.interpolate(scan_tensor.unsqueeze(0).unsqueeze(0), size=target_shape, mode='trilinear', align_corners=False)
    downsampled_scan = downsampled_scan.squeeze()

    verbose_print("Downsampling (trilinear interpolation) complete.", verbose=True)

    return downsampled_scan
