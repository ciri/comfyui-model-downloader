#import install
from .cai_utils import download_cai
from .hf_utils import download_hf
from .utils import get_model_dirs

class CivitAIDownloader:     
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {       
                "save_dir": (get_model_dirs(),),
            },
            "optional" : {
                "ignore": ("BOOLEAN", { "default": False}),
                "model_id":  ("STRING", {"multiline": False, "default": "360292"}),
                "token_id": ("STRING", {"multiline": False, "default": ""}),
                "full_url": ("STRING", {"multiline": False, "default": ""})
            }
        }
        
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    FUNCTION     = "download"
    OUTPUT_NODE  = True
    CATEGORY     = "loaders"

    # inputs match input types
    def download(self, model_id, token_id, save_dir, ignore, full_url):  
        print("Dowloading")
        print(f"\tModel: {model_id}")
        print(f"\tToken: {token_id}")
        print(f"\tFull URL: {full_url}")
        print(f"\tSaving to: {save_dir}")
        
        # https://civitai.com/models/321320/wildcardx-xl-lightning
        if(not ignore):
            download_cai(model_id, token_id, save_dir, full_url)
        return {}
