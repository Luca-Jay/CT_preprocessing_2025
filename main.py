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
from utils.common import verbose_print
from config import config
import torchio as tio

from preprocessing.segmentation import run_segmentation  # Import the segmentation function
from preprocessing.removing_excess import rotate_ct_scan_to_align_vertebrae

# Initialize a DataFrame to store errors
error_log = []

def preprocess_ct_scan(case_path: str, config: dict, verbose: bool = False) -> None:
    """
    Preprocesses a CT scan by loading NIfTI files, applying various preprocessing steps,
    and saving the preprocessed scan to an output file.
    """
    global error_log
    try:
        ct_scan_path = os.path.join(case_path, "CT_scan_bone.nii.gz")
        segmentation_ct_path = os.path.join(case_path, "CT_scan_segmentation.nii.gz")
        case_name = os.path.basename(case_path)
        # output_folder = os.path.join(config["output_folder"],f"CLIPPED({config['min_hu']}-{config['max_hu']})", "TIGHT")
        os.makedirs(config["output_folder"], exist_ok=True)
        output_file = os.path.join(config["output_folder"], f"{case_name}.nii.gz")
        
        if os.path.exists(output_file):
            verbose_print(f"Preprocessed scan already exists for {case_path}.", verbose)
            return
        print(f"Preprocessing started for: {case_name}")
        
        segmentation_path = os.path.join(case_path, "segmentation")
        if not run_segmentation(segmentation_ct_path, segmentation_path, config["roi_bounds"], verbose=verbose):
            error_log.append([case_name, "Segmentation failed or missing files"])
            return

        # Load NIfTI files dynamically based on the labels in the config
        ct_scan, mask_tensors = file_utils.load_nifti_files(ct_scan_path, segmentation_path, config["roi_bounds"], verbose=verbose)

        # Set values outside the body to -1000 HU
        ct_scan.set_data(removing_excess.remove_excess(ct_scan, mask_tensors, config, verbose=verbose))

        # Compute bounding boxes for masks and transform coordinates
        x_min_transformed, x_max_transformed, y_min_transformed, y_max_transformed, z_min_transformed, z_max_transformed = ROI_cropping.get_transformed_bounding_boxes(
            mask_tensors, 
            config["roi_bounds"], 
            ct_scan, 
            verbose=verbose
        )
        print(x_min_transformed, x_max_transformed)
        
        # Crop CT scan using ROI bounds
        ct_scan.set_data(ROI_cropping.crop_ct_scan(ct_scan, x_min_transformed, x_max_transformed, y_min_transformed, y_max_transformed, z_min_transformed, z_max_transformed, verbose=verbose))

        # Downsample the CT scan        
        ct_scan.set_data(downsampling.downsample_ct(ct_scan.data, config["target_shape"], verbose=verbose))

        # Normalize the Hounsfield units
        #ct_scan.set_data(normalization.normalize_hu(ct_scan.data, config["min_hu"], config["max_hu"], verbose=verbose))

        # Convert to NIfTI and save
        file_utils.save_nifti(ct_scan.data, output_file, verbose=True)

        print(f"Preprocessing complete for: {case_name}")
    
    except Exception as e:
        error_log.append([case_name, str(e)])
        print(f"An error occurred while preprocessing {case_path}: {e}")

def main() -> None:
    """
    Main function to start the preprocessing pipeline. It processes zipped data,
    iterates through each case folder, and preprocesses the CT scans.
    """
    global error_log
    print("Starting preprocessing pipeline...")
    start_time = time.time()
    try:
        # process_zipped_data.process_zipped_data(
        #     config["data_zipped_folder"], 
        #     config["data_folder"], 
        #     config["scan_choice"],
        #     verbose=True
        # )

        # Clear memory after unzipping
        gc.collect()
        number_of_scans = 1000
        scan = 0
        for case_folder in os.listdir(config["data_folder"]):
            case_path = os.path.join(config["data_folder"], case_folder)
            if os.path.isdir(case_path):
                preprocess_ct_scan(case_path, config, verbose=False)
                if scan > number_of_scans:
                    return
                else:
                    scan+=1

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
