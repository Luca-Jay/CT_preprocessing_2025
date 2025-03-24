import torch
import scipy.ndimage
from utils.common import verbose_print
import numpy as np
from typing import Tuple
import torchio as tio  # Add torchio import

def downsample_ct(scan_tensor: torch.Tensor, target_shape: Tuple[int, int, int], order: int = 3, verbose=True) -> torch.Tensor:
    verbose_print(f"Original shape: {scan_tensor.shape}", verbose=True)
    verbose_print(f"Target shape: {target_shape}", verbose=True)

    # Perform downsampling using torchio
    transform = tio.transforms.Resize(target_shape)
    downsampled_scan = transform(scan_tensor)

    verbose_print("Downsampling complete.", verbose=True)

    return downsampled_scan
