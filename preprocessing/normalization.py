import numpy as np
from utils.common import verbose_print

def normalize_hu(scan_array: np.ndarray, min_hu: int, max_hu: int, verbose: bool = False) -> np.ndarray:
    """
    Normalizes the Hounsfield Units (HU) of the scan array to the specified range.
    """
    verbose_print(f"Normalizing Hounsfield Units to range [{min_hu}, {max_hu}]...", verbose)
    scan_array = np.clip(scan_array, min_hu, max_hu)
    scan_array = (scan_array - min_hu) / (max_hu - min_hu)
    verbose_print("Normalization complete.", verbose)
    return scan_array