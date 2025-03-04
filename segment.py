import pydicom

# Load the DICOM file
dicom_file = "data_unzipped\Test Case 3\Test Case\Subfolder\subsubfolder\COR_ST_HEAD-NECK\CT.1.2.840.113704.7.1.1.6260.1295389096.156.dcm"
ds = pydicom.dcmread(dicom_file)

# Print all DICOM headers
print(ds)

# Load the DICOM file
dicom_file = "data_unzipped\Test Case 3\Test Case\Subfolder\subsubfolder\THIN_S.T._HEAD\CT.1.2.840.113704.1.111.2200.1295360035.252.dcm"
ds = pydicom.dcmread(dicom_file)

# Print all DICOM headers
print(ds)

# Load the DICOM file
dicom_file = "data_unzipped\Test Case 3\Test Case\Subfolder\subsubfolder\COR_ST_HEAD-NECK\CT.1.2.840.113704.7.1.1.6260.1295389096.156.dcm"
ds = pydicom.dcmread(dicom_file)

# Print all DICOM headers
print(ds)

# Load the DICOM file
dicom_file = "CT.1.2.840.113704.1.111.6316.1306858313.44334.dcm"
ds = pydicom.dcmread(dicom_file)

# Print all DICOM headers
print(ds)

