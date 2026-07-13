from ..base_downloader import BaseModelDownloader, get_model_dirs
from ..download_utils import DownloadManager

class HFDownloader(BaseModelDownloader):     
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {       
                "repo_id": ("STRING", {"multiline": False, "default": "runwayml/stable-diffusion-v1-5"}),
                "filename": ("STRING", {"multiline": False, "default": "v1-5-pruned-emaonly.ckpt"}),
                "local_path": (get_model_dirs(),),
                
            },
            "optional": {
                "overwrite": ("BOOLEAN", {"default": True}),
                "local_path_override": ("STRING", {"default": ""}),
                "hf_token": ("STRING", {"default": "", "password": True}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }
        
    FUNCTION = "download"

    def download(
        self,
        repo_id,
        filename,
        local_path,
        node_id,
        overwrite=False,
        local_path_override="",
        hf_token="",
    ):
        if not repo_id or not filename:
            print(f"Missing required values: repo_id='{repo_id}', filename='{filename}'")
            return {}
        
        final_path = local_path_override if local_path_override else local_path
        
        print(f'downloading model {repo_id} {filename} {final_path} {node_id} {overwrite}')
        self.node_id = node_id
        save_path = self.prepare_download_path(final_path, filename)
        url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
        headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else None
        
        return self.handle_download(
            DownloadManager.download_with_progress,
            save_path=save_path,
            filename=filename,
            overwrite=overwrite,
            url=url,
            progress_callback=self,
            headers=headers,
        )
