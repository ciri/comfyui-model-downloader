import uuid

from .workflow_scanner import scan_workflow
from .model_search import search_for_model
from server import PromptServer
from ..base_downloader import BaseModelDownloader

class AutoModelDownloader(BaseModelDownloader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "select_model": (["Scan First"], {
                    "choices": ["Scan First"],
                    "default": "Scan First"
                }),
            },
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "node_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("repo_id", "filename", "local_path")
    FUNCTION = "process"
    CATEGORY = "loaders"
    
    @classmethod
    def VALIDATE_INPUTS(cls, *args, **kwargs):
        return True 
    
    def __init__(self):
        super().__init__()
        self.missing_models = []
        print("[AutoModelDownloader] Initialized")

    def process(self, select_model, dynprompt, node_id, log=""):
        self.log = ""
        seen = set()
        missing_models = []
        prompt = self._original_prompt(dynprompt)
        for model in scan_workflow(prompt):
            identifier = (model["filename"], model["local_path"])
            if identifier in seen:
                continue
            seen.add(identifier)

            result = search_for_model(model["filename"])
            if result and result.get("repo_id"):
                model["repo_id"] = result["repo_id"]
                model["selection"] = self._selection_for(model)
                missing_models.append(model)
                print(f"[Downloader] {model['filename']} → {model['repo_id']}")
            else:
                print(f"[Downloader] {model['filename']} → not found")

        self.missing_models = missing_models
        if not missing_models:
            PromptServer.instance.send_sync("scan_complete", {
                "node": node_id,
                "models": [],
            })
            return ("No valid models found", "", "")

        self._update_model_list(missing_models)
        PromptServer.instance.send_sync("scan_complete", {
            "node": node_id,
            "models": missing_models,
        })

        selected_model = next(
            (model for model in missing_models if model["selection"] == select_model),
            None,
        )
        if selected_model is None:
            selected_model = next(
                (model for model in missing_models if model["filename"] == select_model),
                missing_models[0],
            )

        return (
            selected_model["repo_id"],
            selected_model["filename"],
            selected_model["local_path"],
        )
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return uuid.uuid4().hex

    @staticmethod
    def _selection_for(model):
        return f"{model['local_path']}/{model['filename']}"

    @staticmethod
    def _original_prompt(dynprompt):
        if hasattr(dynprompt, "get_original_prompt"):
            return dynprompt.get_original_prompt()
        return dynprompt

    def _update_model_list(self, models):
        result = {
            "widget_name": "select_model",
            "options": [model["selection"] for model in models],
            "value": models[0]["selection"],
        }
        print(f"[update_model_list] Returning widget update: {result}")
        return result
