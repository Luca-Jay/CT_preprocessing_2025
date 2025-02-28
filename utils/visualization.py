import matplotlib.pyplot as plt
import numpy as np

def show_slices(ct_data, z_min, z_max, x_min, x_max):
    mid_z = (z_max - z_min) // 2
    plt.figure(figsize=(5, 5))
    plt.imshow(ct_data[:, :, mid_z], cmap="gray")
    plt.axis("off")
    plt.title("Cropped Head & Neck CT Scan")
    plt.show()

    mid_x = (x_max - x_min) // 2
    plt.figure(figsize=(5, 5))
    plt.imshow(ct_data[mid_x, :, :], cmap="gray")
    plt.axis("off")
    plt.title("Cropped Head & Neck CT Scan")
    plt.show()
