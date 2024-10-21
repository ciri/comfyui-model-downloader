import requests
from requests.exceptions import HTTPError
import os
import re

from .utils import get_base_dir

def download_file_with_token(url, params=None, save_path='.'):
    try:
        # Send a GET request to the URL
        with requests.get(url, params=params, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            print(f"Downloading model successfully from {response.url}")

            # Get filename from the content-disposition header if available
            cd = response.headers.get('content-disposition')
            filename = None
            if cd:
                filenames = re.findall('filename="(.+)"', cd)
                if len(filenames) > 0:
                    filename = filenames[0]

            # Default filename if not specified in headers
            if not filename:
                filename = url.split("/")[-1]

            # Write response content to a file
            file_path = os.path.join(save_path, filename)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192): 
                    file.write(chunk)
            
            print(f"File downloaded successfully: {file_path}")
            return True

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')

            
def download_cai(MODEL_ID, TOKEN, LOCAL_PATH, FULL_URL):
    # Directory path where the file will be saved
    directory_path = os.path.join(get_base_dir(), LOCAL_PATH)

    # Ensure the directory exists
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

    # URL and parameters for the request
    if not FULL_URL and not MODEL_ID:
        print("Should have at least full_url or model_id for model download.")
    
    if FULL_URL:
        url = f'{FULL_URL}'
    else:
        url = f'https://civitai.com/api/download/models/{MODEL_ID}'
    params = {'token': TOKEN } if TOKEN else {}

    # Call the download function without checking for file existence
    download_success = download_file_with_token(url, params, directory_path)
    if download_success:
        print("File downloaded successfully.")
    else:
        print("Failed to download the file.")