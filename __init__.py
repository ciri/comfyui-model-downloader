from .nodes.hf_download import HFDownloader
from .nodes.auto_download import AutoModelDownloader
from .nodes.cai_download import CivitAIDownloader
import os

# Node mappings
NODE_CLASS_MAPPINGS = { 
    "HF Downloader": HFDownloader,
    "Auto Model Downloader": AutoModelDownloader,
    "CivitAI Downloader": CivitAIDownloader,
}

# Display names
NODE_DISPLAY_NAME_MAPPINGS = { 
    "HF Downloader": "HF Downloader",
    "Auto Model Downloader": "Auto Model Downloader",
    "CivitAI Downloader": "CivitAI Downloader",
}

# Web directory for JavaScript files
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
]