from totalsegmentator.python_api import totalsegmentator
from totalsegmentator.map_to_binary import class_map
from utils.segmentation_checker import check_segmentation_files
from utils.common import verbose_print


def run_segmentation(segmentation_ct_path: str, segmentation_path: str, roi_bounds: dict, verbose: bool = False) -> bool:
    """
    Runs the necessary totalsegmentator tasks based on the roi_bounds.
    """
    try:
        if not(check_segmentation_files(segmentation_path)):
            tasks = set([bound["task"] for bound in roi_bounds.values()])
            if "total_v1" in tasks:
                tasks.remove("total_v1")
            for task in tasks:
                fast = task == "body"
                fastest = task =="total"
                roi_subset = [bound["label"] if bound["task"]=="total" else None for bound in roi_bounds.values()] if task == "total" else None
                verbose_print(f"Running segmentation task: {task}...", verbose)
                if fast:
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, roi_subset=roi_subset, fast=True, quiet=not(verbose))
                elif fastest:
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, roi_subset=roi_subset, fastest=True, quiet=not(verbose))
                else:
                    totalsegmentator(segmentation_ct_path, segmentation_path, task=task, roi_subset=roi_subset, quiet=not(verbose))
        return check_segmentation_files(segmentation_path)
    except Exception as e:
        verbose_print(f"Segmentation error: {e}", verbose)
        return False
