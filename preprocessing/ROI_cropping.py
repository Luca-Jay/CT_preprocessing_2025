import numpy as np
import nibabel as nib
from utils.common import verbose_print, find_bounding_box, transform_coordinates
from typing import Tuple, List

def compute_bounding_boxes(vertebrae_C3_data: np.ndarray, vertebrae_C7_data: np.ndarray, body_data: np.ndarray, verbose: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes the bounding boxes for the vertebrae_C3, vertebrae_C7, and body masks.
    """
    verbose_print("Computing bounding boxes for masks...", verbose)
    vertebrae_C3_min, vertebrae_C3_max = find_bounding_box(vertebrae_C3_data)
    vertebrae_C7_min, vertebrae_C7_max = find_bounding_box(vertebrae_C7_data)
    body_min, body_max = find_bounding_box(body_data[:, :, vertebrae_C7_max[2]:vertebrae_C3_max[2]])
    verbose_print("Bounding boxes computed.", verbose)
    return vertebrae_C3_min, vertebrae_C3_max, vertebrae_C7_min, vertebrae_C7_max, body_min, body_max

def crop_ct_scan(ct_data: np.ndarray, x_min: int, x_max: int, y_min: int, y_max: int, z_min: int, z_max: int, verbose: bool = False) -> np.ndarray:
    """
    Crops the CT scan data to the specified bounding box.
    """
    verbose_print("Cropping CT scan...", verbose)
    cropped_ct_data = ct_data[x_min:x_max, y_min:y_max, z_min:z_max]
    verbose_print("CT scan cropped.", verbose)
    return cropped_ct_data