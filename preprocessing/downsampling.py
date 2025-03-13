import scipy.ndimage
from utils.common import verbose_print
import numpy as np
from typing import Tuple

def downsample_ct(scan_array: np.ndarray, target_shape: Tuple[int, int, int], order:int = 3, verbose=True) -> np.ndarray:
    verbose_print(f"Original shape: {scan_array.shape}", verbose=True)
    verbose_print(f"Target shape: {target_shape}", verbose=True)

    zoom_factors = np.array(target_shape) / np.array(scan_array.shape)
    verbose_print(f"Zoom factors: {zoom_factors}", verbose=True)

    downsampled_scan = scipy.ndimage.zoom(scan_array, zoom_factors, order=3)
    verbose_print("Downsampling (cubic interpolation) complete.", verbose=True)

    return downsampled_scan
