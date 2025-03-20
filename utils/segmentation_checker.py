import os
from config import config

def check_segmentation_files(segmentation_path: str) -> bool:
    """
    Checks if all required segmentation files are present in the given path.
    """
    required_files = [f"{label}.nii.gz" for label in config["roi_bounds"].keys()]
    
    for file in required_files:
        if not os.path.exists(os.path.join(segmentation_path, file)):
            return False
    return True
