import os
from config import config

def check_segmentation_files(segmentation_path: str) -> set:
    """
    Checks if all required segmentation files are present in the given path.
    """
    required_segmenations = [bound["label"] for bound in config["roi_bounds"].values()]
    
    missing_segmenations = set()
    for label in required_segmenations:
        if not os.path.exists(os.path.join(segmentation_path, label+".nii.gz")):
            missing_segmenations.add(label)

    return missing_segmenations
