from ..base_downloader import BaseModelDownloader, get_model_dirs
from ..download_utils import DownloadManager
import requests

class CivitAIDownloader(BaseModelDownloader):
    base_url = 'https://civitai.com/api'
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {       
                "model_id": ("STRING", {"multiline": False, "default": "360292"}),
                "version_id": ("STRING", {"multiline": False, "default": "", "placeholder": "Leave empty for latest version"}),
                "token_id": ("STRING", {"multiline": False, "default": "API_token_here"}),
                "save_dir": (get_model_dirs(),),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }
        
    FUNCTION = "download"
    
    def get_download_filename_url(self, model_id, version_id, token_id):
        """ Find the model filename and URL from the CivitAI API
            If version_id is provided, download that specific version
            Otherwise, download the latest version
        """
        model_details_url = f'{self.base_url}/v1/models/{model_id}'
        response = requests.get(model_details_url, headers={"Authorization": f"Bearer {token_id}"})
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch model details. Status code: {response.status_code}")
            
        model_details = response.json()
        model_versions = model_details.get('modelVersions', [])
        
        if not model_versions:
            raise Exception(f"No versions found for model ID {model_id}")
        
        # If version_id is provided, find that specific version
        if version_id:
            for model_version in model_versions:
                if str(model_version['id']) == version_id:
                    files = model_version.get('files', [])
                    if not files:
                        raise Exception(f"No files found for version {version_id}")
                    
                    # Get the primary file (usually the first one)
                    filename = files[0]['name']
                    url = files[0]['downloadUrl']
                    return filename, url
                    
            # If we reach here, the specified version was not found
            raise Exception(f"Version {version_id} not found for model ID {model_id}")
        
        # If no version_id is provided, use the latest version (first in the list)
        else:
            # Sort versions by creation date (newest first)
            model_versions.sort(key=lambda x: x['createdAt'], reverse=True)
            latest_version = model_versions[0]
            files = latest_version.get('files', [])
            
            if not files:
                raise Exception(f"No files found for latest version of model ID {model_id}")
                
            filename = files[0]['name']
            url = files[0]['downloadUrl']
            return filename, url
    
    def download(self, model_id, version_id, token_id, save_dir, node_id):
        self.node_id = node_id
        filename, url = self.get_download_filename_url(model_id, version_id, token_id)
        save_path = self.prepare_download_path(save_dir, filename)
        
        return self.handle_download(
            DownloadManager.download_with_progress,
            url=url,
            save_path=save_path,
            filename=filename,
            progress_callback=self,
            params={'token': token_id}
        )
