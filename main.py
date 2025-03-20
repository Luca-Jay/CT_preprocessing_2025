import os
import time
import gc  # Import garbage collection module
import pandas as pd  # Import pandas for DataFrame
from preprocessing import (
    downsampling, 
    normalization, 
    removing_excess, 
    ROI_cropping,
    process_zipped_data
)
from utils import file_utils
from utils.common import verbose_print, transform_coordinates
from config import config
from typing import Tuple
import numpy as np
import nibabel as nib
from preprocessing.segmentation import run_segmentation  # Import the segmentation function
import torch

# Initialize a DataFrame to store errors
error_log = []

def preprocess_ct_scan(case_path: str, ct_scan_path: str, segmentation_ct_path: str, config: dict, verbose: bool = False) -> None:
    """
    Preprocesses a CT scan by loading NIfTI files, applying various preprocessing steps,
    and saving the preprocessed scan to an output file.
    """
    global error_log
    try:
        case_name = os.path.basename(case_path)
        output_file = os.path.join(config["output_folder"], f"{case_name}_NORMAL.nii.gz")
        
        if os.path.exists(output_file):
            verbose_print(f"Preprocessed scan already exists for {case_path}.", verbose)
            return
        
        segmentation_path = os.path.join(case_path, "segmentation")
        if not os.path.exists(segmentation_path):
            os.makedirs(segmentation_path)
            if not run_segmentation(segmentation_ct_path, segmentation_path, config["roi_bounds"], verbose=verbose):
                error_log.append([case_name, "Segmentation failed or missing files"])
                return

        try:
            # Load NIfTI files dynamically based on the labels in the config
            nifti_files = file_utils.load_nifti_files_dynamic(ct_scan_path, segmentation_path, config["roi_bounds"], verbose=verbose)
            ct_scan = nifti_files.pop("ct_scan")
            ct_data = ct_scan.get_fdata()
            mask_data = {label: nifti_files[label].get_fdata() for label in nifti_files}
        except Exception as e:
            error_log.append([case_name, str(e)])
            return
        
        # Convert to PyTorch tensor and move to appropriate device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        ct_tensor = torch.tensor(ct_data, dtype=torch.float32).to(device)
        mask_tensors = {label: torch.tensor(mask_data[label], dtype=torch.float32).to(device) for label in mask_data}

        # Setting values outside the body to -1000 HU
        body_mask = nifti_files.get("body")
        if body_mask and (body_mask.affine != ct_scan.affine).any():
            body_data_transformed = nib.processing.resample_from_to(body_mask, ct_scan, order=1).get_fdata()
        else:
            body_data_transformed = mask_data.get("body")
        if body_data_transformed is not None:
            body_tensor = torch.tensor(body_data_transformed, dtype=torch.float32).to(device)
            body_data_with_padding = removing_excess.expand_mask(body_tensor, config["roi_bounds"]["outside"]["padding"], verbose=verbose)
            ct_tensor = removing_excess.set_values_outside_body(ct_tensor, body_data_with_padding, verbose=verbose)

        # Compute bounding boxes for masks
        bounding_boxes = ROI_cropping.compute_bounding_boxes(mask_tensors, config["roi_bounds"], verbose=verbose)

        # Define cropping limits using the bounding boxes and config bounds
        z_min, z_max = bounding_boxes["down"], bounding_boxes["up"]
        y_min, y_max = bounding_boxes["back"], bounding_boxes["front"]
        x_min, x_max = bounding_boxes["left"], bounding_boxes["right"]

        # Transform coordinates from segmentation scan to high res scan        
        coords = [
            [0, 0, z_min-config["roi_bounds"]["down"]["padding"]],
            [0, 0, z_max+config["roi_bounds"]["up"]["padding"]],
            [0, y_min-config["roi_bounds"]["back"]["padding"], 0],
            [0, y_max+config["roi_bounds"]["front"]["padding"], 0],
            [x_min-config["roi_bounds"]["left"]["padding"], 0, 0],
            [x_max+config["roi_bounds"]["right"]["padding"], 0, 0]
        ]
        z_min_transformed, z_max_transformed, y_min_transformed, y_max_transformed, x_min_transformed, x_max_transformed = transform_coordinates(
            coords, 
            torch.tensor(body_mask.affine if body_mask else ct_scan.affine, dtype=torch.float32), 
            torch.tensor(ct_scan.affine, dtype=torch.float32), 
            verbose=verbose
        )
        
        # Crop CT scan using ROI bounds
        ct_tensor = ROI_cropping.crop_ct_scan(ct_tensor, x_min_transformed, x_max_transformed, y_min_transformed, y_max_transformed, z_min_transformed, z_max_transformed, verbose=verbose)

        # Downsample and normalize the CT scan        
        ct_tensor = downsampling.downsample_ct(ct_tensor, config["target_shape"], verbose=verbose)
        ct_tensor = normalization.normalize_hu(ct_tensor, config["min_hu"], config["max_hu"], verbose=verbose)
        
        # Center the image and resample to 1mm voxels
        center = torch.tensor(ct_tensor.shape, dtype=torch.float32) / 2.0
        final_affine = ct_scan.affine
        final_affine[:3, :3] = torch.eye(3)
        final_affine[:3, 3] = -center
        print(ct_tensor.shape)
        file_utils.save_nifti(ct_tensor.cpu().numpy(), final_affine, output_file, verbose=verbose)

        verbose_print(f"Preprocessing complete for: {case_name}", verbose)
    except Exception as e:
        error_log = error_log.append([case_name, str(e)])
        print(f"An error occurred while preprocessing {case_path}: {e}")
        return

def main() -> None:
    """
    Main function to start the preprocessing pipeline. It processes zipped data,
    iterates through each case folder, and preprocesses the CT scans.
    """
    global error_log
    print("Starting preprocessing pipeline...")
    start_time = time.time()
    try:
        process_zipped_data.process_zipped_data(
            config["data_zipped_folder"], 
            config["data_folder"], 
            config["scan_choice"],
            verbose=True
        )

        # Clear memory after unzipping
        gc.collect()

        for case_folder in os.listdir(config["data_folder"]):
            case_path = os.path.join(config["data_folder"], case_folder)
            if os.path.isdir(case_path):
                ct_scan_path = os.path.join(case_path, "CT_scan.nii.gz")
                segmentation_ct_path = os.path.join(case_path, "CT_scan_segmentation.nii.gz")
                preprocess_ct_scan(case_path, ct_scan_path, segmentation_ct_path, config, verbose=True)

        print("Preprocessing pipeline complete.")
    except Exception as e:
        print(f"An error occurred: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")
    # Save error log to CSV
    error_log_df = pd.DataFrame(error_log, columns=["Case", "Error"])
    error_log_df.to_csv("error_log.csv", index=False)

if __name__ == "__main__": 
    main()
