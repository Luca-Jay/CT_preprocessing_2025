import os
import nibabel as nib
import dicom2nifti
import nibabel.processing
from utils.common import verbose_print
from typing import Tuple, Dict
import numpy as np

def load_nifti_files(ct_scan_path: str, segmentation_folder: str, verbose: bool = False) -> Tuple[nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image]:
    """
    Loads NIfTI files for the CT scan and segmentation masks.
    """
    try:
        verbose_print("Loading NIfTI files...", verbose)
        ct_scan = nib.load(ct_scan_path, mmap=True)
        vertebrae_C3_mask = nib.load(os.path.join(segmentation_folder, "vertebrae_C3.nii.gz"), mmap=True)
        vertebrae_C7_mask = nib.load(os.path.join(segmentation_folder, "vertebrae_C7.nii.gz"), mmap=True)
        body_mask = nib.load(os.path.join(segmentation_folder, "body.nii.gz"), mmap=True)
        skull_mask = nib.load(os.path.join(segmentation_folder, "skull.nii.gz"), mmap=True)
        verbose_print("NIfTI files loaded successfully.", verbose)
        return ct_scan, vertebrae_C3_mask, vertebrae_C7_mask, body_mask, skull_mask
    except Exception as e:
        print(f"Failed to load NIfTI files: {e}")
        raise

def load_nifti_files_dynamic(ct_scan_path: str, segmentation_folder: str, roi_bounds: dict, verbose: bool = False) -> Dict[str, nib.Nifti1Image]:
    """
    Dynamically loads NIfTI files for the CT scan and segmentation masks based on the provided roi_bounds.
    """
    try:
        verbose_print("Loading NIfTI files...", verbose)
        nifti_files = {"ct_scan": nib.load(ct_scan_path, mmap=True)}
        for bound in roi_bounds.values():
            label = bound["label"]
            if label not in nifti_files:
                nifti_files[label] = nib.load(os.path.join(segmentation_folder, f"{label}.nii.gz"), mmap=True)
        verbose_print("NIfTI files loaded successfully.", verbose)
        return nifti_files
    except Exception as e:
        print(f"Failed to load NIfTI files: {e}")
        raise

def get_image_arrays(ct_scan: nib.Nifti1Image, nifti_files: Dict[str, nib.Nifti1Image], verbose: bool = False) -> Dict[str, np.ndarray]:
    """
    Extracts image arrays from the loaded NIfTI files.
    """
    try:
        verbose_print("Extracting image arrays from NIfTI files...", verbose)
        ct_data = ct_scan.get_fdata()
        mask_data = {label: nifti_file.get_fdata() for label, nifti_file in nifti_files.items() if label != "ct_scan"}
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
        preprocessed_scan = nib.Nifti1Image(scan_array, affine)
        nib.save(preprocessed_scan, output_file)
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

