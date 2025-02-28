import os
import nibabel as nib
import dicom2nifti
import nibabel.processing
from utils.common import verbose_print
from typing import Tuple
import numpy as np

def load_nifti_files(ct_scan_path: str, segmentation_folder: str, verbose: bool = False) -> Tuple[nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image, nib.Nifti1Image]:
    """
    Loads NIfTI files for the CT scan and segmentation masks.
    """
    try:
        verbose_print("Loading NIfTI files...", verbose)
        ct_scan = nib.load(ct_scan_path, mmap=True)
        hyoid_mask = nib.load(os.path.join(segmentation_folder, "hyoid.nii.gz"), mmap=True)
        cricoid_mask = nib.load(os.path.join(segmentation_folder, "cricoid_cartilage.nii.gz"), mmap=True)
        body_mask = nib.load(os.path.join(segmentation_folder, "body.nii.gz"), mmap=True)
        head_mask = nib.load(os.path.join(segmentation_folder, "body_extremities.nii.gz"), mmap=True)
        verbose_print("NIfTI files loaded successfully.", verbose)
        return ct_scan, hyoid_mask, cricoid_mask, body_mask, head_mask
    except Exception as e:
        print(f"Failed to load NIfTI files: {e}")
        raise

def get_image_arrays(ct_scan: nib.Nifti1Image, hyoid_mask: nib.Nifti1Image, cricoid_mask: nib.Nifti1Image, body_mask: nib.Nifti1Image, head_mask: nib.Nifti1Image, verbose: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Extracts image arrays from the loaded NIfTI files.
    """
    try:
        verbose_print("Extracting image arrays from NIfTI files...", verbose)
        ct_data = ct_scan.get_fdata()
        hyoid_data = hyoid_mask.get_fdata()
        cricoid_data = cricoid_mask.get_fdata()
        head_data = head_mask.get_fdata()
        body_data = nibabel.processing.resample_from_to(body_mask, ct_scan, order=1).get_fdata()
        verbose_print("Image arrays extracted.", verbose)
        return ct_data, hyoid_data, cricoid_data, head_data, body_data
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

