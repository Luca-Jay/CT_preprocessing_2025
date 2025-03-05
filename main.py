import os
import time
import gc  # Import garbage collection module
from preprocessing import (
    downsampling, 
    normalization, 
    removing_excess, 
    ROI_cropping,
    process_zipped_data
)
from utils import file_utils
from utils.common import verbose_print
from config import config
from totalsegmentator.python_api import totalsegmentator
from typing import Tuple
import numpy as np

def preprocess_ct_scan(case_path: str, ct_scan_path: str, config: dict, verbose: bool = False) -> None:
    """
    Preprocesses a CT scan by loading NIfTI files, applying various preprocessing steps,
    and saving the preprocessed scan to an output file.
    """
    try:
        case_name = os.path.basename(case_path)
        output_file = os.path.join(config["output_folder"], f"{case_name}_preprocessed.nii.gz")
        
        if os.path.exists(output_file):
            verbose_print(f"Preprocessed scan already exists for {case_path}.", verbose)
            return
        
        segmentation_path = os.path.join(case_path, "segmentation")
        if not os.path.exists(segmentation_path):
            os.makedirs(segmentation_path)
            totalsegmentator(ct_scan_path, segmentation_path, task='total', fastest=True, roi_subset=['vertebrae_C7', 'vertebrae_C3', 'skull'], quiet=not(verbose))
            totalsegmentator(ct_scan_path, segmentation_path, task='body', fast=True, quiet=not(verbose))


        ct_scan, vertebrae_C3_mask, vertebrae_C7_mask, body_mask, skull_mask = file_utils.load_nifti_files(ct_scan_path, segmentation_path, verbose=verbose)
        ct_data, vertebrae_C3_data, vertebrae_C7_data, body_data, skull_data = file_utils.get_image_arrays(ct_scan, vertebrae_C3_mask, vertebrae_C7_mask, body_mask, skull_mask, verbose=verbose)
        
        body_data_with_padding = removing_excess.expand_mask(body_data, config["padding"], verbose=verbose)
        ct_data = removing_excess.set_values_outside_body(ct_data, body_data_with_padding, verbose=verbose)

        vertebrae_C3_min, vertebrae_C3_max, vertebrae_C7_min, vertebrae_C7_max, body_min, body_max, skull_min, skull_max = ROI_cropping.compute_bounding_boxes(vertebrae_C3_data, vertebrae_C7_data, body_data, skull_data, verbose=verbose)

        # Define cropping limits
        z_min, z_max =  vertebrae_C7_min[2] - config['padding_Z_lower'],    vertebrae_C3_max[2] + config['padding_Z_upper'] # Crop Z from underside of vertebrae_C3 to upperside of C7
        y_min, y_max =  vertebrae_C7_min[1] - config['padding_Y_lower'],    body_max[1] + config['padding_Y_upper']  # Crop Y from back of C7 to front part of skin
        x_min, x_max =  skull_min[0] - config['padding_X_lower'],    skull_max[0] + config['padding_X_upper'] # Crop X from left side of skull to right side of skull
                
        ct_data = ROI_cropping.crop_ct_scan(ct_data, x_min, x_max, y_min, y_max, z_min, z_max, verbose=verbose)
        
        ct_data = downsampling.downsample_ct(ct_data, config["target_shape"], verbose=verbose)
        ct_data = normalization.normalize_hu(ct_data, config["min_hu"], config["max_hu"], verbose=verbose)
        
        # Center the image and resample to 1mm voxels
        center = np.array(ct_data.shape) / 2.0
        final_affine = np.copy(ct_scan.affine)
        final_affine[:3, :3] = np.eye(3)
        final_affine[:3, 3] = -center
        
        file_utils.save_nifti(ct_data, final_affine, output_file, verbose=verbose)

        verbose_print(f"Preprocessing complete for: {case_name}", verbose)
    except Exception as e:
        print(f"An error occurred while preprocessing {case_path}: {e}")

def main() -> None:
    """
    Main function to start the preprocessing pipeline. It processes zipped data,
    iterates through each case folder, and preprocesses the CT scans.
    """
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
                ct_scan_path = os.path.join(case_path, "ct_scan.nii.gz")
                if os.path.exists(ct_scan_path):
                    preprocess_ct_scan(case_path, ct_scan_path, config, verbose=False)

        print("Preprocessing pipeline complete.")
    except Exception as e:
        print(f"An error occurred: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__": 
    main()
