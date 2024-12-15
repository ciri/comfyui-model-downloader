import asyncio
from .workflow_scanner import scan_workflow
from .model_search import search_for_model
from .utils import get_model_path, check_model_exists
from server import PromptServer
from ..base_downloader import BaseModelDownloader
import os
import json
import hashlib

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
                "prompt": "PROMPT",
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
        self.initialized = False
        self.last_workflow_hash = None
        print("[AutoModelDownloader] Initialized")

    def process(self, select_model, prompt, node_id, log=""):
        # Check if workflow has changed
        current_hash = self._get_workflow_hash(prompt)
        workflow_changed = current_hash != self.last_workflow_hash

        # Handle missing or default values, or if workflow changed
        if not select_model or select_model == "Scan First" or workflow_changed:
            self.log = ""

            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run scan_workflow synchronously
            try:
                self.missing_models = loop.run_until_complete(scan_workflow(prompt))
                
                # Remove duplicates
                seen = set()
                unique_models = [model for model in self.missing_models if not (identifier := (model['filename'], model['local_path'])) in seen and not seen.add(identifier)]
                self.missing_models = unique_models

                valid_models = []
                # Search for each model
                async def search_all_models():
                    if not self.missing_models:  # Check if list is empty
                        return
                    
                    for model in self.missing_models:
                        result = await search_for_model(model['filename'])
                        if result and result.get('repo_id'):  # Only add if we have a valid repo_id
                            model['repo_id'] = result['repo_id']
                            valid_models.append(model)

                            print(f"[Downloader] {model['filename']} → {model['repo_id']}")
                        else:
                            print(f"[Downloader] {model['filename']} → not found")

                loop.run_until_complete(search_all_models())
            finally:
                loop.close()

            self.missing_models = valid_models            
                    
            # Update widget with found models
            if not self.missing_models:  # Check if list is empty
                return ("No valid models found", "", "")
            
            self._update_model_list(self.missing_models)

            # Send update to frontend with models and select first one
            PromptServer.instance.send_sync("scan_complete", {
                "node": node_id,
                "models": self.missing_models
            })

            self.last_workflow_hash = current_hash

            # return first valid model
            return (
                valid_models[0]['repo_id'],
                valid_models[0]['filename'],
                valid_models[0]['local_path']
            )

        # Handle missing or default values
        if not select_model or select_model == "Scan First":
            print("[process] No model selected. Skipping...")
            raise Exception("Select a model")

        # Find selected model        
        selected_model = next((m for m in self.missing_models if m['filename'] == select_model), None)
        print(f"[process] select_model={select_model}")
        print(f"[process] Current missing_models: {self.missing_models}")

        if not selected_model:
            print(f"[process] No model found for {select_model}")
            raise Exception("Model not found")
        
        repo_id = selected_model.get('repo_id', '')
        if not repo_id:
            print(f"[process] No repo_id found for {select_model}")
            raise Exception("No repository found")
        
        print(f"[process] Returning model info: repo_id={repo_id}, filename={selected_model['filename']}, local_path={selected_model['local_path']}")
        return (repo_id, selected_model['filename'], selected_model['local_path'])
    
    def _get_workflow_hash(self, prompt):
        # Convert prompt to dict if it's a string
        if isinstance(prompt, str):
            prompt = json.loads(prompt)
            
        # Create a new dict excluding Auto Model Downloader nodes
        filtered_prompt = {
            k: v for k, v in prompt.items() 
            if v.get('class_type') != 'Auto Model Downloader'
        }
        
        # Convert to stable string representation and hash
        prompt_str = json.dumps(filtered_prompt, sort_keys=True)
        return hashlib.md5(prompt_str.encode()).hexdigest()

    def _update_model_list(self, models):
        print(f"[update_model_list] Updating with models: {models}")
        for model in models:
            # Update existing or add new model
            for existing_model in self.missing_models:
                if model['filename'] == existing_model['filename']:
                    existing_model['repo_id'] = model.get('repo_id')
                    print(f"[DEBUG] Updated model: {existing_model}")
                    break
            else:
                # Add new model if not already in missing_models
                self.missing_models.append(model)
                print(f"[DEBUG] Added new model: {model}")

        # Filter valid models for widget options
        filenames = [m['filename'] for m in self.missing_models if m.get('repo_id')]
        if not filenames:
            filenames = ["No models found"]

        result = {
            "widget_name": "select_model",
            "options": filenames,
            "value": filenames[0] if filenames else "No models found"
        }
        print(f"[update_model_list] Returning widget update: {result}")
        return result

    def serialize(self):
        print("[serialize] Serializing missing_models:", self.missing_models)

        return {
            "missing_models": self.missing_models,
            "initialized": self.initialized,
            "last_workflow_hash": self.last_workflow_hash
        }
    
    def deserialize(self, data):
        print(f"[deserialize] Data: {data}")
        self.missing_models = data.get("missing_models", [])
        self.initialized = data.get("initialized", False)
        self.last_workflow_hash = data.get("last_workflow_hash", None)
