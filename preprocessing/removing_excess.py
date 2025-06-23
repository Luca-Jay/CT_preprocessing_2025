import torch
from scipy.ndimage import binary_dilation, center_of_mass
from utils.common import verbose_print
import numpy as np
import torchio as tio  # Add torchio import
from scipy.spatial.transform import Rotation as R



def remove_excess(ct_scan: tio.ScalarImage, masks: dict[str, tio.ScalarImage], config, verbose: bool = False) -> torch.Tensor:
    """
    Sets the values outside the body mask to -1000.
    """
    verbose_print("Setting values outside the body to -1000...", verbose)

    # Expand the body mask with padding
    body_mask = masks["body"]
    body_mask.data = binary_dilation(body_mask.data.numpy(), iterations=config["roi_bounds"]["outside"]["padding"], ).astype(bool)

    # Resample using torchio if the affines are different
    if (body_mask.affine != ct_scan.affine).any():
        body_mask = tio.Resample(ct_scan)(body_mask)
    
    ct_scan.data[~body_mask.data.bool()] = -1000

    # Expand the body mask with padding
    skull_mask = masks["skull"]
    skull_mask.data = binary_dilation(skull_mask.data.numpy(), iterations=config["roi_bounds"]["skull"]["padding"], ).astype(bool)

    # Resample using torchio if the affines are different
    if (skull_mask.affine != ct_scan.affine).any():
        skull_mask = tio.Resample(ct_scan)(skull_mask)
    

    ct_scan.data[skull_mask.data.bool()] = 0

    

    verbose_print("Values outside the body have been set.", verbose)
    return ct_scan.data



