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
                "token_id": ("STRING", {"multiline": False, "default": "API_token_here"}),
                "save_dir": (get_model_dirs(),),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }
        
    FUNCTION = "download"

    def get_download_filename_url(self, model_id, token_id):
        """ Find the model filename and URL from the CivitAI API
            This Assumes that the first file.name in the latest version is correct.
        """
        model_details_url = f'{self.base_url}/v1/models/{model_id}'
        response = requests.get(model_details_url, headers={"Authorization": f"Bearer {token_id}"})
        model_details = response.json()
        possible_files = []
        model_versions = model_details.get('modelVersions', [])
        for model_version in model_versions:
            for file in model_version.get("files", []):
                possible_files.append((model_version['createdAt'], file['name'], file['downloadUrl']))

        possible_files.sort(reverse=True)
        if possible_files:
            create_at_date, filename, url = possible_files[0]
        else:
            filename = f'civitai-model-{model_id}'
            url = f'{self.base_url}/download/models/{model_id}'
        return filename, url

    def download(self, model_id, token_id, save_dir, node_id):
        self.node_id = node_id

        filename, url = self.get_download_filename_url(model_id, token_id)
        save_path = self.prepare_download_path(save_dir, filename)

        return self.handle_download(
            DownloadManager.download_with_progress,
            url=url,
            save_path=save_path,
            filename=filename,
            progress_callback=self,
            params={'token': token_id}
        )
