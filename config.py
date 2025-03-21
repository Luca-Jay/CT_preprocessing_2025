import json

config = {
    
    # Target shape for downsampling the CT scan
    "target_shape": (128, 128, 128),
    
    # Hounsfield Units (HU) range for normalization
    "min_hu": -1000,
    "max_hu": 1000,
    
    # Output folder for saving preprocessed scans
    "output_folder": "/workspace/project-data/PREPROCESSED_CT_SCANS",
    
    # Folder containing zipped data
    "data_zipped_folder": "/workspace/project-data/data-zipped",
    
    # Folder for unzipped data
    "data_folder": "/workspace/project-data/data_unzipped",
    
    # Bounds for ROI cropping
    "roi_bounds": {
        "left": {"label": "thyroid_cartilage", "task": "headneck_bones_vessels", "type": "min", "padding": 15},
        "right": {"label": "thyroid_cartilage", "task": "headneck_bones_vessels", "type": "max", "padding": 15},
        "up": {"label": "hyoid", "task":"headneck_bones_vessels", "type": "max", "padding": 5},
        "down": {"label": "cricoid_cartilage", "task":"headneck_bones_vessels", "type": "min", "padding": 5},
        "front": {"label": "thyroid_cartilage", "task":"headneck_bones_vessels", "type": "max", "padding": 7},
        "back": {"label": "larynx_air", "task":"headneck_bones_vessels", "type": "min", "padding": 7},
        "outside": {"label": "body", "task":"body", "padding": 5},

    }
}

# Load scan choices from a separate JSON file
with open('/workspace/project-data/CT_preprocessing_2025/scan_choice.json', 'r') as f:
    config["scan_choice"] = json.load(f)
