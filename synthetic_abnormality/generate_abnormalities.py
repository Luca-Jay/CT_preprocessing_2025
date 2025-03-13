import os
import random
import nibabel as nib
import numpy as np
from abnormality_creator import inject_cube_anomaly

def generate_abnormalities(input_folder, output_folder, num_scans, cube_sizes):
    """
    Generates synthetic abnormalities in a specified number of CT scans.
    
    Parameters:
    - input_folder: Folder containing the original CT scans.
    - output_folder: Folder to save the modified CT scans.
    - num_scans: Number of CT scans to modify.
    - cube_sizes: List of cube sizes for the abnormalities.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of all CT scans in the input folder
    ct_scans = [f for f in os.listdir(input_folder) if f.endswith('.nii.gz')]
    
    # Randomly select the specified number of CT scans
    selected_scans = random.sample(ct_scans, num_scans)
    
    for scan in selected_scans:
        input_path = os.path.join(input_folder, scan)
        
        for cube_size in cube_sizes:
            # Remove .nii extension before adding anomaly suffix
            scan_name = str.split(os.path.splitext(os.path.splitext(scan)[0])[0], '_')[0]
            output_filename = f"{scan_name}_ANOMALY_CUBE{cube_size}.nii.gz"
            output_path = os.path.join(output_folder, output_filename)
            
            # Inject anomaly and save the modified scan
            inject_cube_anomaly(input_path, output_path, cube_size)
            print(f"Generated {output_filename}")


if __name__ == "__main__":
    input_folder = 'PREPROCESSED_CT_SCANS'
    output_folder = 'PREPROCESSED_CT_SCANS/synthetic_abnormalities'
    num_scans = 2
    cube_sizes = [5, 10, 15]

    generate_abnormalities(input_folder, output_folder, num_scans, cube_sizes)
