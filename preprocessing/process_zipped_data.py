import os
import zipfile
import shutil
from utils.common import verbose_print
from utils.file_utils import convert_dicom_to_nifti
from typing import List

def find_target_folder(zip_ref, target_folder):
    """
    Finds the full path of the target folder inside a ZIP file.
    """
    for file in zip_ref.namelist():
        if file.endswith('/') and target_folder in file:
            return file
    return None

def process_zipped_data(data_zipped_folder: str, data_folder: str, scan_choice: dict, verbose: bool = False) -> None:
    """
    Extracts relevant folders from ZIP files, converts DICOM scans to NIfTI,
    and cleans up temporary folders. Ensures correct placement inside case folders.
    """
    os.makedirs(data_folder, exist_ok=True)

    for zip_filename in os.listdir(data_zipped_folder):
        if zip_filename.endswith(".zip"):
            case_name = os.path.splitext(zip_filename)[0]
            case_destination = os.path.join(data_folder, case_name)

            if os.path.exists(case_destination):
                verbose_print(f"Skipping {case_name}: already exists in {data_folder}", verbose)
                continue

            zip_path = os.path.join(data_zipped_folder, zip_filename)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                os.makedirs(case_destination, exist_ok=True)

                # Find target folders inside the ZIP
                segment_folder = scan_choice.get(f"{case_name}-SEGMENT")
                scan_folder = scan_choice.get(f"{case_name}-SCAN")
                if not segment_folder or not scan_folder:
                    verbose_print(f"No target folders specified for {case_name} in config.", verbose)
                    continue

                matched_segment_folder = find_target_folder(zip_ref, segment_folder)
                matched_scan_folder = find_target_folder(zip_ref, scan_folder)
                if not matched_segment_folder or not matched_scan_folder:
                    verbose_print(f"No matching folders found in {zip_filename} for targets {segment_folder} and {scan_folder}", verbose)
                    continue

                # Extract only the relevant folders
                temp_extract_path = os.path.join(data_folder, "temp_extract")
                os.makedirs(temp_extract_path, exist_ok=True)

                for file in zip_ref.namelist():
                    if file.startswith(matched_segment_folder) or file.startswith(matched_scan_folder):
                        zip_ref.extract(file, temp_extract_path)

                # Move extracted files to the correct case destination
                extracted_segment_folder = os.path.join(temp_extract_path, matched_segment_folder)
                extracted_scan_folder = os.path.join(temp_extract_path, matched_scan_folder)
                
                if os.path.exists(extracted_segment_folder):
                    # Convert extracted DICOM folders to NIfTI
                    nifti_output_segment = os.path.join(case_destination, "CT_scan_segmentation.nii.gz")
                    convert_dicom_to_nifti(extracted_segment_folder, nifti_output_segment, verbose=verbose)

                if os.path.exists(extracted_scan_folder) :
                    # Convert extracted DICOM folders to NIfTI
                    nifti_output_scan = os.path.join(case_destination, "CT_scan.nii.gz")
                    convert_dicom_to_nifti(extracted_scan_folder, nifti_output_scan, verbose=verbose)

                shutil.rmtree(temp_extract_path, ignore_errors=True)  # Cleanup temp folder

            # Delete the initially zipped folder
            #os.remove(zip_path)

    verbose_print(f"Processing complete. Extracted cases and NIfTI files are in: {data_folder}", verbose)
