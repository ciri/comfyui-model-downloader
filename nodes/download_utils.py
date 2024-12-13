import requests
from tqdm import tqdm
import os
import re

class DownloadManager:
    @staticmethod
    def download_with_progress(url, save_path, progress_callback=None, params=None, chunk_size=1024*1024):
        response = requests.get(url, stream=True, params=params)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        filename = DownloadManager._get_filename(response, url)
        full_path = os.path.join(save_path, filename)
        
        downloaded = 0
        with open(full_path, 'wb') as file:
            with tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename) as pbar:
                for data in response.iter_content(chunk_size=chunk_size):
                    size = file.write(data)
                    downloaded += size
                    pbar.update(size)
                    
                    if progress_callback and total_size > 0:
                        progress = (downloaded / total_size) * 100.0
                        progress_callback.set_progress(progress)
        
        return full_path

    @staticmethod
    def _get_filename(response, url):
        cd = response.headers.get('content-disposition')
        if cd:
            filenames = re.findall('filename="(.+)"', cd)
            if filenames:
                return filenames[0]
        return url.split("/")[-1] 