
from .nodes.hf_download import HFDownloader
from .nodes.cai_download import CivitAIDownloader

NODE_CLASS_MAPPINGS = { 
    "HF Downloader" : HFDownloader,
    "CivitAI Downloader":CivitAIDownloader,
}
NODE_DISPLAY_NAME_MAPPINGS = { 
    "HF Downloader" : "HF Downloader", 
    "CivitAI Downloader" : "CivitAI Downloader",
}


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']