import os
import dicom2nifti
from utils.common import verbose_print
from typing import Tuple, Dict
import numpy as np
import torch
import torchio as tio  # Add torchio import

def load_nifti_files(ct_scan_path: str, segmentation_folder: str, roi_bounds: dict, verbose: bool = False) -> Dict[str, tio.ScalarImage]:
    """
    Dynamically loads NIfTI files for the CT scan and segmentation masks based on the provided roi_bounds.
    """
    try:
        verbose_print("Loading NIfTI files...", verbose)
        nifti_files = {"ct_scan": tio.ScalarImage(ct_scan_path)}
        for bound in roi_bounds.values():
            label = bound["label"]
            if label not in nifti_files:
                nifti_files[label] = tio.ScalarImage(os.path.join(segmentation_folder, f"{label}.nii.gz"))
        verbose_print("NIfTI files loaded successfully.", verbose)
        return nifti_files
    except Exception as e:
        print(f"Failed to load NIfTI files: {e}")
        raise

def get_image_arrays(ct_scan: tio.ScalarImage, nifti_files: Dict[str, tio.ScalarImage], verbose: bool = False) -> Dict[str, np.ndarray]:
    """
    Extracts image arrays from the loaded NIfTI files.
    """
    try:
        verbose_print("Extracting image arrays from NIfTI files...", verbose)
        ct_data = ct_scan.data.numpy()
        mask_data = {label: nifti_file.data.numpy() for label, nifti_file in nifti_files.items() if label != "ct_scan"}
        verbose_print("Image arrays extracted.", verbose)
        return {"ct_data": ct_data, **mask_data}
    except Exception as e:
        print(f"Failed to extract image arrays: {e}")
        raise

def save_nifti(scan_array: np.ndarray, affine: np.ndarray, output_file: str, verbose: bool = False) -> None:
    """
    Saves the preprocessed scan array as a NIfTI file.
    """
    try:
        verbose_print(f"Saving preprocessed scan to {output_file}...", verbose)
        preprocessed_scan = tio.ScalarImage(tensor=scan_array, affine=affine)
        preprocessed_scan.save(output_file)
        verbose_print(f"Preprocessed scan saved as {output_file}.", verbose)
    except Exception as e:
        print(f"Failed to save NIfTI file: {e}")

def convert_dicom_to_nifti(dicom_directory: str, output_file: str, verbose: bool = False) -> None:
    """
    Converts a DICOM series to NIfTI format.
    """
    try:
        dicom2nifti.dicom_series_to_nifti(dicom_directory, output_file)
        verbose_print(f"Converted DICOM to NIfTI: {output_file}", verbose)
    except Exception as e:
        print(f"Error converting {dicom_directory} to NIfTI: {e}")

def resample_mask_torch(src_image, target_shape):
    """
    Resample a 3D tensor from source space to target space using torchIO.
    src_tensor: shape (1, 1, D, H, W)
    """
    # Define the target shape
    target_shape = tuple(target_shape)

    # Create a torchIO CropOrPad transform
    resample_transform = tio.CropOrPad(target_shape)

    # Apply the resample transform
    resampled_image = resample_transform(src_image)

    # Extract the resampled tensor
    resampled_tensor = resampled_image.data

    return resampled_tensor