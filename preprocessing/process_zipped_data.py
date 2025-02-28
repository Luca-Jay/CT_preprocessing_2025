import os
import zipfile
import shutil
from utils.common import verbose_print
from utils.file_utils import convert_dicom_to_nifti
from typing import List


def find_parent_of_target(zip_ref: zipfile.ZipFile, target_folders: List[str]) -> str:
    """
    Finds the parent directory inside the ZIP that contains any of the target folders.
    """
    for file in zip_ref.namelist():
        for folder in target_folders:
            if f"/{folder}/" in file:
                return "/".join(file.split("/")[:-2])
    return None

        
def process_zipped_data(data_zipped_folder: str, data_folder: str, high_res_ct: str, low_res_ct: str, verbose: bool = False) -> None:
    """
    Extracts relevant folders from ZIP files, converts DICOM scans to NIfTI,
    and cleans up temporary folders.
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
                target_folders = [high_res_ct, low_res_ct]
                os.makedirs(case_destination, exist_ok=True)

                for file in zip_ref.namelist():
                    if any(f"/{folder}/" in file for folder in target_folders):
                        extracted_path = os.path.join(data_folder, file)
                        zip_ref.extract(file, data_folder)
                        # Move the extracted files to the case destination
                        target_folder_name = file.split('/')[1]
                        target_folder_path = os.path.join(data_folder, target_folder_name)
                        if os.path.exists(target_folder_path):
                            for item in os.listdir(target_folder_path):
                                shutil.move(os.path.join(target_folder_path, item), case_destination)
                            shutil.rmtree(target_folder_path, ignore_errors=True)

                for folder in target_folders:
                    extracted_folder = os.path.join(case_destination, folder)
                    if os.path.exists(extracted_folder):
                        nifti_output = os.path.join(case_destination, f"{folder}.nii.gz")
                        convert_dicom_to_nifti(extracted_folder, nifti_output, verbose=verbose)
                        shutil.rmtree(extracted_folder, ignore_errors=True)

            # Delete the initially zipped folder
            os.remove(zip_path)

    verbose_print(f"Processing complete. Extracted cases and NIfTI files are in: {data_folder}", verbose)
