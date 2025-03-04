import os
import zipfile
import shutil
from utils.common import verbose_print
from utils.file_utils import convert_dicom_to_nifti
from typing import List

def find_target_folder(zip_ref, high_res_keywords, low_res_keywords):
    """
    Finds the full path of the deepest folder that matches all target keywords inside a ZIP file.
    Allows partial matching instead of exact folder names.
    """
    matched_folders = {}

    for file in zip_ref.namelist():
        if file.endswith('/'):  # Ensure it's a folder
            folder_parts = file.split("/")[:-1]  # Get the folder structure
            folder_name = folder_parts[-1] if folder_parts else ""

            if all(keyword in folder_name for keyword in high_res_keywords):
                parent_folder = "/".join(folder_parts)  # Get the full parent folder path
                matched_folders[folder_name] = (parent_folder, "high_res.nii.gz")
            elif all(keyword in folder_name for keyword in low_res_keywords):
                parent_folder = "/".join(folder_parts)  # Get the full parent folder path
                matched_folders[folder_name] = (parent_folder, "low_res.nii.gz")

    return matched_folders

def process_zipped_data(data_zipped_folder: str, data_folder: str, high_res_ct: List[str], low_res_ct: List[str], verbose: bool = False) -> None:
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

                # Find parent directory inside the ZIP
                matched_folders = find_target_folder(zip_ref, high_res_ct, low_res_ct)

                if not matched_folders:
                    verbose_print(f"No matching folders found in {zip_filename}", verbose)
                    continue

                # Extract only relevant folders
                temp_extract_path = os.path.join(data_folder, "temp_extract")
                os.makedirs(temp_extract_path, exist_ok=True)

                for file in zip_ref.namelist():
                    if any(f"/{folder}/" in file for folder in matched_folders.keys()):
                        zip_ref.extract(file, temp_extract_path)

                # Move extracted files to the correct case destination
                for folder_name, (full_folder_path, output_filename) in matched_folders.items():
                    extracted_folder = os.path.join(temp_extract_path, full_folder_path)
                    
                    if os.path.exists(extracted_folder):
                        correct_destination = os.path.join(case_destination, folder_name)
                        shutil.move(extracted_folder, correct_destination)

                        # Convert extracted DICOM folders to NIfTI
                        nifti_output = os.path.join(case_destination, output_filename)
                        convert_dicom_to_nifti(correct_destination, nifti_output, verbose=verbose)
                        shutil.rmtree(correct_destination, ignore_errors=True)  # Cleanup

                shutil.rmtree(temp_extract_path, ignore_errors=True)  # Cleanup temp folder

            # Delete the initially zipped folder
            #os.remove(zip_path)

    verbose_print(f"Processing complete. Extracted cases and NIfTI files are in: {data_folder}", verbose)
