import nibabel as nib
import numpy as np
import torch
from typing import List, Tuple

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

def transform_coordinates(coords: List[List[int]], source_affine: torch.Tensor, target_affine: torch.Tensor, verbose: bool = False) -> List[int]:
    """
    Transforms coordinates from the source affine to the target affine.
    """
    verbose_print("Transforming coordinates...", verbose)
    transformed_coords = []
    for coord in coords:
        coord_world = torch.matmul(source_affine, torch.tensor(coord + [1.0])).tolist()
        coord_transformed = torch.matmul(torch.inverse(target_affine), torch.tensor(coord_world)).tolist()
        transformed_coords.append(round(coord_transformed[coord.index(max(coord))]))
    verbose_print("Coordinates transformed.", verbose)
    return transformed_coords
