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
import torch
import torchio as tio  # Add torchio import
from preprocessing.segmentation import run_segmentation  # Import the segmentation function

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
        output_file = os.path.join(config["output_folder"], f"{case_name}.nii.gz")
        
        if os.path.exists(output_file):
            verbose_print(f"Preprocessed scan already exists for {case_path}.", verbose)
            return
        
        segmentation_path = os.path.join(case_path, "segmentation")
        if not run_segmentation(segmentation_ct_path, segmentation_path, config["roi_bounds"], verbose=verbose):
            error_log.append([case_name, "Segmentation failed or missing files"])
            return

        try:
            # Load NIfTI files dynamically based on the labels in the config
            nifti_files = file_utils.load_nifti_files(ct_scan_path, segmentation_path, config["roi_bounds"], verbose=verbose)
            # Convert to PyTorch tensor and move to appropriate device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            ct_scan = nifti_files.pop("ct_scan")
            body_mask = nifti_files.get("body")
            ct_tensor = ct_scan.data.to(device)
            mask_tensors = {label: nifti_files[label].data.to(device) for label in nifti_files}
            nifti_files = None  # Clear memory
        except Exception as e:
            error_log.append([case_name, str(e)])
            return

        # Setting values outside the body to -1000 HU
        if body_mask is not None and (body_mask.affine != ct_scan.affine).any():
            # Resample using torch
            body_tensor = file_utils.resample_mask_torch(
                mask_tensors["body"],
                ct_tensor.shape
            )
            body_tensor = removing_excess.expand_mask(body_tensor, config["roi_bounds"]["outside"]["padding"], verbose=verbose)
            ct_tensor = removing_excess.set_values_outside_body(ct_tensor, body_tensor, verbose=verbose)

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
            torch.tensor(body_mask.affine, dtype=torch.float32).to(device), 
            torch.tensor(ct_scan.affine, dtype=torch.float32).to(device), 
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
