#import install
from .cai_utils import download_cai
from .hf_utils import download_hf
from .utils import get_model_dirs

class HFDownloader:     
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {       
                "repo_id":  ("STRING", {"multiline": False, "default": "ByteDance/SDXL-Lightning"}),
                "filename": ("STRING", {"multiline": False, "default": "sdxl_lightning_2step_lora.safetensors"}),
                "save_dir": (get_model_dirs(),),
            },
            "optional" : {
                "overwrite": ("BOOLEAN", { "default": False})
            }
        }
        
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    FUNCTION     = "download"
    OUTPUT_NODE  = True
    CATEGORY     = "loaders"

    # inputs match input types
    def download(self, repo_id, filename,save_dir, overwrite):  
        print("Dowloading")
        print(f"\t{repo_id}")
        print(f"\t{filename}")
        print(f"\t{save_dir}")
        download_hf(repo_id, filename,save_dir,overwrite)
        return {}


class CivitAIDownloader:     
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {       
                "model_id":  ("STRING", {"multiline": False, "default": "360292"}),
                "token_id": ("STRING", {"multiline": False, "default": "bb2a86388b3e178eacfa9d44f76a915d"}),
                "save_dir": (get_model_dirs(),),
            },
            "optional" : {
                "overwrite": ("BOOLEAN", { "default": False})
            }
        }
        
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    FUNCTION     = "download"
    OUTPUT_NODE  = True
    CATEGORY     = "loaders"

    # inputs match input types
    def download(self, repo_id, token_id, save_dir, overwrite):  
        print("Dowloading")
        print(f"\tModel: {repo_id}")
        print(f"\tToken: {token_id}")
        print(f"\tSaving to: {save_dir}")
        
        # https://civitai.com/models/321320/wildcardx-xl-lightning

        download_cai(repo_id, token_id, save_dir,overwrite)
        return {}
