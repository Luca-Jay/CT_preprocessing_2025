import ants
from utils.common import verbose_print

def non_linear_registration(fixed_image_path: str, moving_image_path: str, output_image_path: str, verbose: bool = False) -> None:
    """
    Performs non-linear registration of the moving image to the fixed image.
    """
    try:
        verbose_print("Starting non-linear registration...", verbose)
        fixed = ants.image_read(fixed_image_path)
        moving = ants.image_read(moving_image_path)
        registration = ants.registration(fixed=fixed, moving=moving, type_of_transform='SyN')
        ants.image_write(registration['warpedmovout'], output_image_path)
        verbose_print("Non-linear registration complete.", verbose)
    except Exception as e:
        print(f"Failed to perform non-linear registration: {e}")
        raise
