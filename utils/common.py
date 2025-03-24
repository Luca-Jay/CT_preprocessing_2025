import nibabel as nib
import numpy as np
import torch
from typing import List, Tuple
from nibabel.affines import apply_affine

def verbose_print(message: str, verbose: bool) -> None:
    """
    Prints a message if verbose is True.
    """
    if verbose:
        print(message)

def find_bounding_box(mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Finds the bounding box of a given mask.
    """
    indices = torch.nonzero(mask > 0, as_tuple=False)
    min_bounds = indices.min(axis=0).values
    max_bounds = indices.max(axis=0).values
    return min_bounds, max_bounds

def transform_coordinates(coords, source_affine, target_affine, verbose=False):
    verbose_print("Transforming coordinates...", verbose)
    world_coords = apply_affine(source_affine, coords)
    target_coords = apply_affine(np.linalg.inv(target_affine), world_coords)
    return np.round(target_coords).astype(int).tolist()