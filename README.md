# CT Preprocessing Pipeline

This project provides a preprocessing pipeline for CT scans, including DICOM to NIfTI conversion, loading NIfTI files, extracting image arrays, expanding masks, setting values outside the body, computing bounding boxes, cropping, downsampling, and normalizing the CT scan data.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Functions](#functions)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/CT_preprocessing.git
    ```

2. Navigate to the project directory:
    ```sh
    cd CT_preprocessing
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

The configuration settings are stored in the `config.py` file. Update the paths and parameters as needed:

```python
config = {
    "padding": 7,
    "padding_Z_lower": 2,
    "padding_Z_upper": 5,
    "padding_Y_lower": 5,
    "padding_Y_upper": 5,
    "padding_X_lower": 2,
    "padding_X_upper": 2,
    "target_shape": (256, 256, 256),
    "min_hu": -1000,
    "max_hu": 1000,
    "output_folder": ".\output",
    "data_zipped_folder": ".\data_zipped",
    "data_folder": ".\data_unzipped",
    "high_res_ct": "THIN_S.T._HEAD",
    "low_res_ct": "COR_ST_HEAD-NECK"
}