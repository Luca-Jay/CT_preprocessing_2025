import torch
from scipy.ndimage import binary_dilation, center_of_mass
from utils.common import verbose_print
import numpy as np
import torchio as tio  # Add torchio import


def remove_excess(ct_scan: tio.ScalarImage, body_mask: tio.LabelMap, padding: int, verbose: bool = False) -> torch.Tensor:
    """
    Sets the values outside the body mask to -1000.
    """
    verbose_print("Setting values outside the body to -1000...", verbose)

    # Expand the body mask with padding
    body_mask.data = binary_dilation(body_mask.data.numpy(), iterations=padding).astype(bool)
    
    # Set values outside the body to -1000 using PyTorch
    ct_scan.data[~body_mask.data.bool()] = -1000

    verbose_print("Values outside the body have been set.", verbose)
    return ct_scan.data


def rotate_ct_scan_to_align_vertebrae(ct_scan: tio.ScalarImage, vertebrae_c3: tio.LabelMap, vertebrae_c7: tio.LabelMap, verbose: bool = False) -> tio.ScalarImage:
    """
    Rotates the CT scan to align the middle of vertebrae C3 and C7 in the X and Y axes.
    """
    verbose_print("Rotating CT scan to align vertebrae C3 and C7...", verbose)

    # Compute the center of mass for both vertebrae
    com_c3 = center_of_mass(vertebrae_c3.data.numpy())
    com_c7 = center_of_mass(vertebrae_c7.data.numpy())

    # Compute the midpoint of the vertebrae in X and Y
    midpoint_x = (com_c3[0] + com_c7[0]) / 2
    midpoint_y = (com_c3[1] + com_c7[1]) / 2

    # Compute the translation required to align the midpoint to the center of the CT scan
    _, W, H, _ = ct_scan.shape
    center_x, center_y = W / 2, H / 2
    x_shift = int(center_x - midpoint_x)
    y_shift = int(center_y - midpoint_y)

    # Apply the translation to the CT scan
    ct_scan.data = torch.roll(ct_scan.data, shifts=(x_shift, y_shift), dims=(1, 2))

    verbose_print(f"CT scan rotated. X shift: {x_shift}, Y shift: {y_shift}.", verbose)
    return ct_scan