import torch
from scipy.ndimage import binary_dilation
from utils.common import verbose_print
import numpy as np
import torchio as tio  # Add torchio import
from scipy.ndimage import binary_dilation


def remove_excess(ct_scan: tio.ScalarImage, body_mask: tio.LabelMap, padding: int, verbose: bool = False) -> torch.Tensor:
    """
    Sets the values outside the body mask to -1000.
    """
    verbose_print("Setting values outside the body to -1000...", verbose)

    # Expand the body mask with padding
    body_mask.data = binary_dilation(body_mask.data.numpy(), iterations=padding).astype(bool)

    # Resample using torchio if the affines are different
    if (body_mask.affine != ct_scan.affine).any():
        body_mask = tio.Resample(ct_scan)(body_mask)
    
    # Set values outside the body to -1000 using PyTorch
    ct_scan.data[~body_mask.data.bool()] = -1000

    verbose_print("Values outside the body have been set.", verbose)
    return ct_scan.data