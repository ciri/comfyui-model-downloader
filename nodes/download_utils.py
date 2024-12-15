import requests
from tqdm import tqdm
import os
import re
import shutil

class DownloadManager:
    @staticmethod
    def download_with_progress(url, save_path, progress_callback=None, params=None, chunk_size=1024*1024):
        response = requests.get(url, stream=True, params=params)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        filename = DownloadManager._get_filename(response, url)
        full_path = os.path.join(save_path, filename)
        temp_path = full_path + '.tmp'
        
        downloaded = 0
        try:
            with open(temp_path, 'wb') as file:
                with tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename) as pbar:
                    for data in response.iter_content(chunk_size=chunk_size):
                        size = file.write(data)
                        downloaded += size
                        pbar.update(size)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100.0
                            progress_callback.set_progress(progress)
            
            # Only move the file if the download completed successfully
            shutil.move(temp_path, full_path)
            return full_path
            
        except Exception as e:
            # Clean up the temp file if something goes wrong
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    @staticmethod
    def _get_filename(response, url):
        cd = response.headers.get('content-disposition')
        if cd:
            filenames = re.findall('filename="(.+)"', cd)
            if filenames:
                return filenames[0]
        return url.split("/")[-1] 