import os
from tqdm import tqdm
import requests


def download_hf(repo_id, filename, save_path, overwrite=False, progress_callback=None):
    URL = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    
    # Get file size first
    response = requests.get(URL, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    # Create the full file path
    full_file_path = os.path.join(save_path, filename)
    
    chunk_size = 1024 * 1024  # 1MB chunks
    downloaded = 0

    with open(full_file_path, 'wb') as file:
        with tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename, leave=True) as pbar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                downloaded += size
                pbar.update(size)
                
                if progress_callback and total_size > 0:
                    progress = (downloaded / total_size) * 100.0
                    progress_callback.set_progress(progress)

    return True