#import install
from .cai_utils import download_cai
from .hf_utils import download_hf
from .utils import get_model_dirs

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
                "ignore": ("BOOLEAN", { "default": False})
            }
        }
        
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    FUNCTION     = "download"
    OUTPUT_NODE  = True
    CATEGORY     = "loaders"

    # inputs match input types
    def download(self, model_id, token_id, save_dir, ignore):  
        print("Dowloading")
        print(f"\tModel: {model_id}")
        print(f"\tToken: {token_id}")
        print(f"\tSaving to: {save_dir}")
        
        # https://civitai.com/models/321320/wildcardx-xl-lightning
        if(not ignore):
            download_cai(model_id, token_id, save_dir)
        return {}
