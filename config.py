import json

config = {
    # Padding values for expanding the body mask
    "padding": 7,

    # Padding values for cropping the CT scan
    "padding_Z_lower": 2,
    "padding_Z_upper": 2,
    "padding_Y_lower": 2,
    "padding_Y_upper": 2,
    "padding_X_lower": 2,
    "padding_X_upper": 2,
    
    # Target shape for downsampling the CT scan
    "target_shape": (128, 128, 128),
    
    # Hounsfield Units (HU) range for normalization
    "min_hu": -1000,
    "max_hu": 1000,
    
    # Output folder for saving preprocessed scans
    "output_folder": ".\PREPROCESSED_CT_SCANS",
    
    # Folder containing zipped data
    "data_zipped_folder": ".\data_zipped",
    
    # Folder for unzipped data
    "data_folder": ".\data_unzipped",
}

# Load scan choices from a separate JSON file
with open('scan_choices.json', 'r') as f:
    config["scan_choice"] = json.load(f)
