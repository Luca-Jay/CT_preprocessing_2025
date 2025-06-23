import json

config = {
    
    # Target shape for downsampling the CT scan
    "target_shape": (128, 128, 128),
    
    # Output folder for saving preprocessed scans
    "output_folder": "preprocessed_scans",
    
    # Folder containing zipped data
    "data_zipped_folder": "data_zipped",

    # Folder for unzipped data
    "data_folder": "data_unzipped",
    
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
    # # Example bounds for ROI cropping for lungs
    # "roi_bounds": {
    #     "left": {"label": "lung_upper_lobe_right", "task": "total", "type": "min", "padding": 10},
    #     "right": {"label": "lung_upper_lobe_left", "task": "total", "type": "max", "padding": 10},
    #     "up": {"label": "lung_upper_lobe_left", "task":"total", "type": "max", "padding": 10},
    #     "down": {"label": "lung_lower_lobe_left", "task":"total", "type": "min", "padding": 2},
    #     "front": {"label": "lung_upper_lobe_left", "task":"total", "type": "max", "padding": 5},
    #     "back": {"label": "lung_upper_lobe_left", "task":"total", "type": "min", "padding": 5},
    #     "outside": {"label": "body", "task":"body", "padding": 5},
    #     "skull": {"label": "skull", "task": "total", "padding": 4}
    # }
}

# Load scan choices from a separate JSON file
with open('scan_choices.json', 'r') as f:
    config["scan_choice"] = json.load(f)
