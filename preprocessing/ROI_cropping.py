import numpy as np
import nibabel as nib
from utils.common import verbose_print, find_bounding_box, transform_coordinates
from typing import Tuple, List

def compute_bounding_boxes(hyoid_data: np.ndarray, cricoid_data: np.ndarray, head_data: np.ndarray, verbose: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes the bounding boxes for the hyoid, cricoid, and head masks.
    """
    verbose_print("Computing bounding boxes for masks...", verbose)
    hyoid_min, hyoid_max = find_bounding_box(hyoid_data)
    cricoid_min, cricoid_max = find_bounding_box(cricoid_data)
    skin_min, skin_max = find_bounding_box(head_data[:, :, :hyoid_min[2]])
    verbose_print("Bounding boxes computed.", verbose)
    return hyoid_min, hyoid_max, cricoid_min, cricoid_max, skin_min, skin_max

def crop_ct_scan(ct_data: np.ndarray, x_min: int, x_max: int, y_min: int, y_max: int, z_min: int, z_max: int, verbose: bool = False) -> np.ndarray:
    """
    Crops the CT scan data to the specified bounding box.
    """
    verbose_print("Cropping CT scan...", verbose)
    cropped_ct_data = ct_data[x_min:x_max, y_min:y_max, z_min:z_max]
    verbose_print("CT scan cropped.", verbose)
    return cropped_ct_data