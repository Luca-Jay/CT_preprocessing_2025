config = {
    # Padding values for expanding the body mask
    "padding": 7,

    # Padding values for cropping the CT scan
    "padding_Z_lower": 2,
    "padding_Z_upper": 5,
    "padding_Y_lower": 5,
    "padding_Y_upper": 5,
    "padding_X_lower": 2,
    "padding_X_upper": 2,
    
    # Target shape for downsampling the CT scan
    "target_shape": (256, 256, 256),
    
    # Hounsfield Units (HU) range for normalization
    "min_hu": -1000,
    "max_hu": 1000,
    
    # Output folder for saving preprocessed scans
    "output_folder": ".\output",
    
    # Folder containing zipped data
    "data_zipped_folder": ".\data_zipped",
    
    # Folder for unzipped data
    "data_folder": ".\data_unzipped",
    
    # Names of the high and low resolution CT scan folders
    "high_res_ct": "THIN_S.T._HEAD",
    "low_res_ct": "COR_ST_HEAD-NECK"
}
