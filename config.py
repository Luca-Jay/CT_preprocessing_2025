import json

config = {
    
    # Target shape for downsampling the CT scan
    "target_shape": (128, 128, 128),
    
    # Hounsfield Units (HU) range for normalization
    "min_hu": 100,
    "max_hu": 900,
    
    # Target Z-coordinate for vertical alignment
    "target_z": 64,
    
    # Output folder for saving preprocessed scans
    "output_folder": "./PREPROCESSED_CT_SCANS",
    
    # Folder containing zipped data
    "data_zipped_folder": "data_zipped",
    
    # Folder for unzipped data
    "data_folder": "data_unzipped",
    
    # Bounds for ROI cropping
    "roi_bounds": {
        "left": {"label": "vertebrae_C4", "task": "total", "type": "min", "padding": 15},
        "right": {"label": "vertebrae_C4", "task": "total", "type": "max", "padding": 15},
        "up": {"label": "vertebrae_C3", "task":"total", "type": "max", "padding": 2},
        "down": {"label": "cricoid_cartilage", "task":"headneck_bones_vessels", "type": "min", "padding": 2},
        "front": {"label": "skull", "task":"total", "type": "max", "padding": 0},
        "back": {"label": "vertebrae_C7", "task":"total", "type": "min", "padding": 5},
        "outside": {"label": "body", "task":"body", "padding": 5},
    }
}

# Load scan choices from a separate JSON file
with open('scan_choices.json', 'r') as f:
    config["scan_choice"] = json.load(f)
