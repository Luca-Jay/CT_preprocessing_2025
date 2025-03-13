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

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

The configuration settings are stored in the `config.py` file. Update the paths and parameters as needed.

## Scan options

The scan choices should be stored in scan_choices.json. Scan for segmenting and scan for processing should be stored as follows:
```json
{
    "FolderName-SEGMENT": "BONE_H-N-UXT_3X3",
    "FolderName-SCAN": "THIN_BONE_HD-UXT"
}
```

