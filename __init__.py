from .nodes.hf_download import HFDownloader, HFAuthDownloader
from .nodes.cai_download import CivitAIDownloader
import os

# Node mappings - using the exact display name as the key
NODE_CLASS_MAPPINGS = { 
    "HF Downloader": HFDownloader,
    "HF Auth Downloader": HFAuthDownloader,
    "CivitAI Downloader": CivitAIDownloader,
}

# Display names (can be omitted since they're the same)
NODE_DISPLAY_NAME_MAPPINGS = { 
    "HF Downloader": "HF Downloader",
    "HF Auth Downloader": "HF Auth Downloader",
    "CivitAI Downloader": "CivitAI Downloader",
}

# Web directory for JavaScript files
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

# Export all required symbols
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
]