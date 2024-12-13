from .hf_download import HFDownloader
from .cai_download import CivitAIDownloader

NODE_CLASS_MAPPINGS = { 
    "HFDownloader": HFDownloader,
    "CivitAIDownloader": CivitAIDownloader,
}

NODE_DISPLAY_NAME_MAPPINGS = { 
    "HFDownloader": "HF Downloader", 
    "CivitAIDownloader": "CivitAI Downloader",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 