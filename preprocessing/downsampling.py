import scipy.ndimage
from utils.common import verbose_print
import numpy as np
from typing import Tuple

def downsample_ct(scan_array: np.ndarray, target_shape: Tuple[int, int, int], verbose: bool = False) -> np.ndarray:
    """
    Downsamples the CT scan array to the specified target shape.
    """
    verbose_print(f"Downsampling CT scan to target shape {target_shape}...", verbose)
    zoom_factors = [t / s for t, s in zip(target_shape, scan_array.shape)]
    downsampled_scan = scipy.ndimage.zoom(scan_array, zoom_factors, order=1)
    verbose_print("Downsampling complete.", verbose)
    return downsampled_scan
