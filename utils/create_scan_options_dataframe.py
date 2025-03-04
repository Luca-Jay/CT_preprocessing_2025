import os
import zipfile
import pandas as pd

def get_dicom_parent_folders(zip_path: str) -> list:
    """
    Extracts the parent folders of all DICOM files in the ZIP file.
    """
    dicom_folders = set()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.lower().endswith('.dcm'):
                parent_folder = os.path.basename(os.path.dirname(file))
                dicom_folders.add(parent_folder)
    return list(dicom_folders)

def create_scan_options_dataframe(data_zipped_folder: str) -> pd.DataFrame:
    """
    Creates a pandas DataFrame containing the different options for the scans
    for each zipped folder name.
    """
    data = []
    for zip_filename in os.listdir(data_zipped_folder):
        if zip_filename.endswith(".zip"):
            zip_path = os.path.join(data_zipped_folder, zip_filename)
            dicom_folders = get_dicom_parent_folders(zip_path)
            data.append({
                "zip_filename": zip_filename,
                "dicom_folders": dicom_folders
            })
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    data_zipped_folder = "./data_zipped"  # Update this path as needed
    df = create_scan_options_dataframe(data_zipped_folder)
    output_csv ="scan_options.csv"
    df.to_csv(output_csv, index=False)
    print(f"Scan options DataFrame saved to {output_csv}")
