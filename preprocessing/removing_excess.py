import torch
from scipy.ndimage import binary_dilation
from utils.common import verbose_print
import numpy as np

def expand_mask(body_tensor: torch.Tensor, padding: int, verbose: bool = False) -> torch.Tensor:
    """
    Expands the body mask with the specified padding.
    """
    verbose_print(f"Expanding body mask with padding of {padding}...", verbose)

    # Perform mask expansion using PyTorch
    body_data_with_padding = binary_dilation(body_tensor.cpu().numpy(), iterations=padding).astype(bool)
    body_data_with_padding = torch.tensor(body_data_with_padding, dtype=torch.bool).to(body_tensor.device)

    verbose_print("Mask expansion complete.", verbose)
    return body_data_with_padding

def set_values_outside_body(ct_tensor: torch.Tensor, body_data_with_padding: torch.Tensor, verbose: bool = False) -> torch.Tensor:
    """
    Sets the values outside the body mask to -1000.
    """
    verbose_print("Setting values outside the body to -1000...", verbose)

    # Set values outside the body to -1000 using PyTorch
    ct_tensor[~body_data_with_padding] = -1000

    verbose_print("Values outside the body have been set.", verbose)
    return ct_tensor