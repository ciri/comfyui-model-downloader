
from .nodes.hf_download import HFDownloader

NODE_CLASS_MAPPINGS = { 
    "HF Downloader" : HFDownloader 
}
NODE_DISPLAY_NAME_MAPPINGS = { 
    "HF Downloader" : "HF Downloader" 
}


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']