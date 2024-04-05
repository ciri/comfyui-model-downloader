import requests
import os

def get_base_dir():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate two levels up from the current directory
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    # Append the 'models' directory to the path
    models_dir = os.path.join(base_dir, 'models')
    return models_dir


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
    LOCAL_FILE_PATH =  os.path.join(LOCAL_PATH, FILENAME)

    # Check if the file already exists
    if (overwrite or not os.path.exists(LOCAL_FILE_PATH)):
        if download_file_from_url(URL, LOCAL_FILE_PATH):
            print("File downloaded successfully.")
        else:
            print("Failed to download the file.")
    else:
        print("File already exists, not overwriting it.")