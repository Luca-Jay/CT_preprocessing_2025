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

def rotate_ct_scan_to_align_vertebrae(ct_scan: tio.ScalarImage, vertebrae_c3: tio.LabelMap, vertebrae_c7: tio.LabelMap, verbose: bool = False) -> tio.ScalarImage:

    verbose_print("Rotating CT scan to align vertebrae C3 and C7...", verbose)

    # Compute CoM of vertebrae in voxel space (remove channel dim)
    com_c3_voxel = np.array(center_of_mass(vertebrae_c3.data.numpy()[0]))
    com_c7_voxel = np.array(center_of_mass(vertebrae_c7.data.numpy()[0]))
    neck_center_voxel = (com_c3_voxel + com_c7_voxel) / 2

    # Convert voxel center to world (physical) coordinates
    neck_center_world = ct_scan.affine[:3, :3] @ neck_center_voxel + ct_scan.affine[:3, 3]

    # Compute rotation matrix from C3->C7 direction to z-axis
    direction = com_c7_voxel - com_c3_voxel
    direction /= np.linalg.norm(direction)
    target = np.array([0, 0, 1])  # z-axis

    if np.allclose(direction, target):
        rot = np.eye(3)
    else:
        rotation_vector = np.cross(direction, target)
        angle = np.arccos(np.clip(np.dot(direction, target), -1.0, 1.0))
        if np.linalg.norm(rotation_vector) < 1e-6:
            rot = np.eye(3)
        else:
            rotation_vector = rotation_vector / np.linalg.norm(rotation_vector)
            rot = R.from_rotvec(rotation_vector * angle).as_matrix()

    # Step 1: Translate to origin
    T1 = np.eye(4)
    T1[:3, 3] = -neck_center_world

    # Step 2: Apply rotation
    R_affine = np.eye(4)
    R_affine[:3, :3] = rot

    # Step 3: Translate back
    T2 = np.eye(4)
    T2[:3, 3] = neck_center_world

    # Combine: T2 * R * T1
    final_affine = T2 @ R_affine @ T1
    new_affine = final_affine @ ct_scan.affine

    # Create new reference image with rotated affine
    reference = tio.ScalarImage(tensor=ct_scan.data.clone(), affine=new_affine)

    # Apply transform
    rotated = tio.Resample(reference)(ct_scan)

    verbose_print("Rotation applied around neck center.", verbose)
    return rotated


