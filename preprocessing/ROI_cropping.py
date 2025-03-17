import numpy as np
import nibabel as nib
from utils.common import verbose_print, find_bounding_box, transform_coordinates
from typing import Tuple, List

def compute_bounding_boxes(mask_data: dict, roi_bounds: dict, verbose: bool = False) -> dict:
    """
    Computes the bounding boxes for the masks based on the config bounds.
    """
    verbose_print("Computing bounding boxes for masks...", verbose)
    bounding_boxes = {}

    # Compute bounding boxes for each label
    for label, data in mask_data.items():
        min_bounds, max_bounds = find_bounding_box(data)
        bounding_boxes[label] = {"min": min_bounds, "max": max_bounds}

    # Extract the required bounds from the computed bounding boxes
    for bound, settings in roi_bounds.items():
        if bound != "outside":
            label = settings["label"]
            bound_type = settings["type"]
            bounding_boxes[bound] = bounding_boxes[label][bound_type][{"left": 0, "right": 0, "up": 2, "down": 2, "front": 1, "back": 1}[bound]]

    verbose_print("Bounding boxes computed.", verbose)
    return bounding_boxes

def crop_ct_scan(ct_data: np.ndarray, x_min: int, x_max: int, y_min: int, y_max: int, z_min: int, z_max: int, verbose: bool = False) -> np.ndarray:
    """
    Crops the CT scan data to the specified bounding box.
    """
    verbose_print("Cropping CT scan...", verbose)
    cropped_ct_data = ct_data[x_min:x_max, y_min:y_max, z_min:z_max]
    verbose_print("CT scan cropped.", verbose)
    return cropped_ct_data