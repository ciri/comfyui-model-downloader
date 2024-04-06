import requests
import os

from .utils import get_base_dir

def download_file_from_url(url, local_file_path):
    """Download a file from a URL to a local file path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        with open(local_file_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download file: {response.status_code}")
        return False

def download_hf(REPO_ID, FILENAME, LOCAL_PATH,overwrite):
    URL = f"https://huggingface.co/{REPO_ID}/resolve/main/{FILENAME}"
    LOCAL_FILE_PATH =  os.path.join(get_base_dir(), LOCAL_PATH, FILENAME)

    # Check if the file already exists
    if (overwrite or not os.path.exists(LOCAL_FILE_PATH)):
        if download_file_from_url(URL, LOCAL_FILE_PATH):
            print("File downloaded successfully.")
        else:
            print("Failed to download the file.")
    else:
        print("File already exists, not overwriting it.")
            
