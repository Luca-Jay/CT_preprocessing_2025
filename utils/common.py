import nibabel as nib
import numpy as np
from typing import List, Tuple

def verbose_print(message: str, verbose: bool) -> None:
    """
    Prints a message if verbose is True.
    """
    if verbose:
        print(message)

def find_bounding_box(mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Finds the bounding box of a given mask.
    """
    indices = np.argwhere(mask > 0)
    min_bounds = indices.min(axis=0)
    max_bounds = indices.max(axis=0)
    return min_bounds, max_bounds

def transform_coordinates(coords: List[List[int]], source_affine: np.ndarray, target_affine: np.ndarray, verbose: bool = False) -> List[int]:
    """
    Transforms coordinates from the source affine to the target affine.
    """
    verbose_print("Transforming coordinates...", verbose)
    transformed_coords = []
    for coord in coords:
        coord_world = nib.affines.apply_affine(source_affine, coord)
        coord_transformed = nib.affines.apply_affine(np.linalg.inv(target_affine), coord_world)
        transformed_coords.append(round(coord_transformed[coord.index(max(coord))]))
    verbose_print("Coordinates transformed.", verbose)
    return transformed_coords
