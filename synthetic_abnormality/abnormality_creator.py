import nibabel as nib
import numpy as np
import random

def inject_cube_anomaly(input_nifti_path, output_nifti_path, cube_size=10, cube_hu=2000):
    import nibabel as nib
    import numpy as np

    # Load the original NIfTI file
    nifti_img = nib.load(input_nifti_path)
    img_data = nifti_img.get_fdata()

    # Image dimensions
    dims = img_data.shape

    # Choose random location ensuring cube fits inside, around the middle
    x = np.random.randint(dims[0]//4, 3*dims[0]//4 - cube_size)
    y = np.random.randint(dims[1]//4, 3*dims[1]//4 - cube_size)
    z = np.random.randint(dims[2]//4, 3*dims[2]//4 - cube_size)

    # Inject cube with high HU (normalized so max = 1)
    anomaly_hu = 1
    img_data[x:x+cube_size, y:y+cube_size, z:z+cube_size] = anomaly_hu

    # Save the modified image as a new NIfTI file
    anomaly_img = nib.Nifti1Image(img_data, affine=nifti_img.affine, header=nifti_img.header)
    nib.save(anomaly_img, output_nifti_path)

    print(f"Anomaly injected at location: ({x},{y},{z})")
