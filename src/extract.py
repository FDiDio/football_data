import os
import requests
import zipfile
import io

def download_and_extract_zip(url, folder_name, specific_file=None):
    # Step 1: Download the ZIP file
    print(f"Downloading data from {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        print("ZIP file downloaded successfully.")
        
        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)
        
        # Step 2: Extract the ZIP file content to the folder
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(folder_name)

        # Step 3: List the extracted files
        extracted_files = os.listdir(folder_name)

        
        # If specific file is provided, check if it exists
        if specific_file:
            # Enrich file path with folder name and .csv extension
            file_name = f"{specific_file}.csv"  # Format like '24_25\\I1.csv'

            if file_name.replace("\\", "/") in [file.replace("\\", "/") for file in extracted_files]:
                print(f"File {file_name} found. Proceeding to process it.")
                return [file_name]
            else:
                print(f"Error: {file_name} not found in the extracted files.")
                return []  # Return empty list if file not found
        else:
            # Return all extracted files with correct paths
            return [os.path.join(folder_name, file) for file in extracted_files]
    else:
        print(f"Failed to download ZIP file. Status code: {response.status_code}")
        exit()  # Exit if download fails
