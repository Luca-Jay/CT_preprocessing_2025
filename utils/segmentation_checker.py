import os

def check_segmentation_files(segmentation_path: str) -> bool:
    """
    Checks if all required segmentation files are present in the given path.
    """
    required_files = [
        "vertebrae_C3.nii.gz",
        "vertebrae_C7.nii.gz",
        "body.nii.gz",
        "skull.nii.gz"
    ]
    
    for file in required_files:
        if not os.path.exists(os.path.join(segmentation_path, file)):
            return False
    return True
