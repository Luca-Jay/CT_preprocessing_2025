import json

config = {
    
    # Target shape for downsampling the CT scan
    "target_shape": (128, 128, 128),
    
    # Hounsfield Units (HU) range for normalization
    "min_hu": -1000,
    "max_hu": 1000,
    
    # Output folder for saving preprocessed scans
    "output_folder": "/workspace/project-data/PREPROCESSED_CT_SCANS/TIGHTRQ3",
    
    # Folder containing zipped data
    "data_zipped_folder": "/workspace/project-data/data-zipped-RQ3",
    
    # Folder for unzipped data
    "data_folder": "/workspace/project-data/data_unzipped_RQ3",
    
    # Bounds for ROI cropping
    "roi_bounds": {
        "left": {"label": "thyroid_cartilage", "task": "headneck_bones_vessels", "type": "min", "padding": 20},
        "right": {"label": "thyroid_cartilage", "task": "headneck_bones_vessels", "type": "max", "padding": 20},
        "up": {"label": "hyoid", "task":"headneck_bones_vessels", "type": "max", "padding": 2},
        "down": {"label": "cricoid_cartilage", "task":"headneck_bones_vessels", "type": "min", "padding": 5},
        "front": {"label": "hyoid", "task":"headneck_bones_vessels", "type": "max", "padding": 20},
        "back": {"label": "cricoid_cartilage", "task":"headneck_bones_vessels", "type": "min", "padding": 10},
        "outside": {"label": "body", "task":"body", "padding": 5},
        "skull": {"label": "skull", "task": "total", "padding": 4}
    }
    # Bounds for ROI cropping
    # "roi_bounds": {
    #     "left": {"label": "vertebrae_C4", "task": "total", "type": "min", "padding": 15},
    #     "right": {"label": "vertebrae_C4", "task": "total", "type": "max", "padding": 15},
    #     "up": {"label": "vertebrae_C3", "task":"total", "type": "max", "padding": 2},
    #     "down": {"label": "vertebrae_C7", "task":"total", "type": "min", "padding": 2},
    #     "front": {"label": "skull", "task":"total", "type": "max", "padding": 0},
    #     "back": {"label": "vertebrae_C7", "task":"total", "type": "min", "padding": 5},
    #     "outside": {"label": "body", "task":"body", "padding": 5},
    #     "skull": {"label": "skull", "task": "body", "padding": 4}
    # }
}

# Load scan choices from a separate JSON file
with open('/workspace/project-data/CT_preprocessing_2025/scan_choices_RQ3.json', 'r') as f:
    config["scan_choice"] = json.load(f)
