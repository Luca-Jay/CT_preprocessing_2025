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
from utils.common import verbose_print, transform_coordinates
from config import config
from totalsegmentator.python_api import totalsegmentator
from typing import Tuple

def preprocess_ct_scan(case_path: str, low_res_ct_path: str, high_res_ct_path: str, config: dict, verbose: bool = False) -> None:
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
            totalsegmentator(low_res_ct_path, segmentation_path, task='headneck_bones_vessels')
            totalsegmentator(low_res_ct_path, segmentation_path, task='body', fast=True)

        ct_scan, hyoid_mask, cricoid_mask, body_mask, head_mask = file_utils.load_nifti_files(high_res_ct_path, segmentation_path, verbose=verbose)
        ct_data, hyoid_data, cricoid_data, head_data, body_data = file_utils.get_image_arrays(ct_scan, hyoid_mask, cricoid_mask, body_mask, head_mask, verbose=verbose)
        
        body_data_with_padding = removing_excess.expand_mask(body_data, config["padding"], verbose=verbose)
        ct_data = removing_excess.set_values_outside_body(ct_data, body_data_with_padding, verbose=verbose)

        _, hyoid_max, cricoid_min, _, skin_min, skin_max = ROI_cropping.compute_bounding_boxes(hyoid_data, cricoid_data, head_data, verbose=verbose)
        coords = [
            [0, 0, cricoid_min[2] + config["padding_Z_lower"]],
            [0, 0, hyoid_max[2] + config["padding_Z_upper"]],
            [0, skin_min[1] + config["padding_Y_lower"], 0],
            [0, skin_max[1] + config["padding_Y_upper"], 0],
            [skin_min[0] - config["padding_X_lower"], 0, 0],
            [skin_max[0] + config["padding_X_upper"], 0, 0]
        ]
        z_min_transformed, z_max_transformed, y_min_transformed, y_max_transformed, x_min_transformed, x_max_transformed = transform_coordinates(coords, hyoid_mask.affine, ct_scan.affine, verbose=verbose)
        ct_data = ROI_cropping.crop_ct_scan(ct_data, x_min_transformed, x_max_transformed, y_min_transformed, y_max_transformed, z_min_transformed, z_max_transformed, verbose=verbose)
        
        ct_data = downsampling.downsample_ct(ct_data, config["target_shape"], verbose=verbose)
        ct_data = normalization.normalize_hu(ct_data, config["min_hu"], config["max_hu"], verbose=verbose)
        
        file_utils.save_nifti(ct_data, ct_scan.affine, output_file, verbose=verbose)

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
            config["high_res_ct"],
            config["low_res_ct"],
            verbose=True
        )

        # Clear memory after unzipping
        gc.collect()

        for case_folder in os.listdir(config["data_folder"]):
            case_path = os.path.join(config["data_folder"], case_folder)
            if os.path.isdir(case_path):
                low_res_ct_path = os.path.join(case_path, "low_res.nii.gz")
                high_res_ct_path = os.path.join(case_path, "high_res.nii.gz")
                if os.path.exists(low_res_ct_path) and os.path.exists(high_res_ct_path):
                    preprocess_ct_scan(case_path, low_res_ct_path, high_res_ct_path, config, verbose=False)

        print("Preprocessing pipeline complete.")
    except Exception as e:
        print(f"An error occurred: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__": 
    main()
