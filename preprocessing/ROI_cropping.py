import torch
import numpy as np
import nibabel as nib
from utils.common import verbose_print, find_bounding_box, transform_coordinates
from typing import Tuple, List
import torchio as tio 

def compute_bounding_boxes(mask_data: dict, roi_bounds: dict, verbose: bool = False) -> dict:
    """
    Computes the bounding boxes for the masks based on the config bounds.
    """
    verbose_print("Computing bounding boxes for masks...", verbose)
    bounding_boxes = {}

    # Compute bounding boxes for each label
    for label, mask in mask_data.items():
        min_bounds, max_bounds = find_bounding_box(mask.data)
        bounding_boxes[label] = {"min": min_bounds, "max": max_bounds}

    # Extract the required bounds from the computed bounding boxes
    for bound, settings in roi_bounds.items():
        if bound != "outside":
            label = settings["label"]
            bound_type = settings["type"]
            bounding_boxes[bound] = bounding_boxes[label][bound_type][{"left": 1, "right": 1, "up": 3, "down": 3, "front": 2, "back": 2}[bound]]

    verbose_print("Bounding boxes computed.", verbose)
    return bounding_boxes

def get_transformed_bounding_boxes(mask_data: dict, roi_bounds: dict, ct_scan: tio.ScalarImage, verbose: bool = False) -> Tuple[int, int, int, int, int, int]:
    """
    Computes and transforms the bounding boxes for the masks based on the config bounds.
    """
    bounding_boxes = compute_bounding_boxes(mask_data, roi_bounds, verbose=verbose)

    # Transform coordinates from segmentation scan to high res scan        
    coords = [
        [bounding_boxes["left"]-roi_bounds["left"]["padding"], 0, 0],
        [bounding_boxes["right"]+roi_bounds["right"]["padding"], 0, 0],
        [0, bounding_boxes["back"]-roi_bounds["back"]["padding"], 0],
        [0, bounding_boxes["front"]+roi_bounds["front"]["padding"], 0],
        [0, 0, bounding_boxes["down"]-roi_bounds["down"]["padding"]],
        [0, 0, bounding_boxes["up"]+roi_bounds["up"]["padding"]]
    ]
    x_min_transformed, x_max_transformed, y_min_transformed, y_max_transformed, z_min_transformed, z_max_transformed = transform_coordinates(
        coords, 
        mask_data["body"].affine,
        ct_scan.affine,
        verbose=verbose
    )

    return x_min_transformed[0], x_max_transformed[0], y_min_transformed[1], y_max_transformed[1], z_min_transformed[2], z_max_transformed[2]

def crop_ct_scan(ct_image: tio.ScalarImage, x_min: int, x_max: int, y_min: int, y_max: int, z_min: int, z_max: int, verbose: bool = False) -> tio.ScalarImage:
    """
    Crops a TorchIO ScalarImage using the given voxel indices.
    Input bounds are assumed to be in voxel coordinates (x=W, y=H, z=D).
    """
    verbose_print("Cropping CT scan using TorchIO...", verbose)

    cropped_ct_tensor = ct_image.data[:, x_min:x_max, y_min:y_max, z_min:z_max]

    verbose_print("CT scan cropped.", verbose)
    return cropped_ct_tensor