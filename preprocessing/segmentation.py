from totalsegmentator.python_api import totalsegmentator
from totalsegmentator.map_to_binary import class_map
from utils.segmentation_checker import check_segmentation_files
from utils.common import verbose_print

def run_segmentation(segmentation_ct_path: str, segmentation_path: str, roi_bounds: dict, verbose: bool = False) -> bool:
    """
    Runs the necessary totalsegmentator tasks based on the roi_bounds.
    """
    try:
        missing_segmentations = check_segmentation_files(segmentation_path)
        if len(missing_segmentations)!=0:
            tasks = set([bound["task"] for bound in roi_bounds.values() if bound["label"] in missing_segmentations])
            if "total_v1" in tasks:
                tasks.remove("total_v1")
            for task in tasks:
                roi_subset = [bound["label"] for bound in roi_bounds.values() if bound["task"] == "total"]
                verbose_print(f"Running segmentation task: {task}...", verbose)
                if task == "body":
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, fast=True, quiet=not(verbose))
                elif task =="total":
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, fastest=True, roi_subset=roi_subset, quiet=not(verbose))
                else:
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, quiet=not(verbose))
        return True
    except Exception as e:
        verbose_print(f"Segmentation error: {e}", verbose)
        return False
