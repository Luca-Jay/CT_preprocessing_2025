from scipy.ndimage import binary_dilation
from utils.common import verbose_print
import numpy as np

def expand_mask(body_data: np.ndarray, padding: int, verbose: bool = False) -> np.ndarray:
    """
    Expands the body mask with the specified padding.
    """
    verbose_print(f"Expanding body mask with padding of {padding}...", verbose)
    body_data_with_padding = binary_dilation(body_data, iterations=padding).astype(bool)
    verbose_print("Mask expansion complete.", verbose)
    return body_data_with_padding

def set_values_outside_body(ct_data: np.ndarray, body_data_with_padding: np.ndarray, verbose: bool = False) -> np.ndarray:
    """
    Sets the values outside the body mask to -1000.
    """
    verbose_print("Setting values outside the body to -1000...", verbose)
    ct_data[~body_data_with_padding] = -1000
    verbose_print("Values outside the body have been set.", verbose)
    return ct_data