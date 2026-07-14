from .nodes.auto.downloader import AutoModelDownloader
from .nodes.cai.cai_download import CivitAIDownloader
from .nodes.checkpoint_loader import DownloadedCheckpointLoader
from .nodes.hf.hf_download import HFDownloader

NODE_CLASS_MAPPINGS = {
    "HF Downloader": HFDownloader,
    "Downloaded Checkpoint Loader": DownloadedCheckpointLoader,
    "Auto Model Downloader": AutoModelDownloader,
    "CivitAI Downloader": CivitAIDownloader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HF Downloader": "HF Download",
    "Downloaded Checkpoint Loader": "Load Downloaded Checkpoint",
    "Auto Model Downloader": "Auto Model Finder (Experimental)",
    "CivitAI Downloader": "CivitAI Download",
}

# Relative path required by ComfyUI's frontend extension loader.
# See: https://docs.comfy.org/custom-nodes/js/javascript_overview
WEB_DIRECTORY = "./js"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
