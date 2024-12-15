import asyncio
from .workflow_scanner import scan_workflow
from .model_search import search_for_model
from .utils import get_model_path, check_model_exists
from server import PromptServer
from ..base_downloader import BaseModelDownloader
import os

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
        return True  # Skip validation
    
    def __init__(self):
        super().__init__()
        self.missing_models = []
        self.initialized = False
        print("[AutoModelDownloader] Initialized")

    def process(self, select_model, prompt, node_id):        
        if not self.initialized:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run scan_workflow synchronously
            try:
                self.missing_models = loop.run_until_complete(scan_workflow(prompt))
                print(f"[process] Found missing models: {self.missing_models}")
                
                # Search for each model
                async def search_all_models():
                    if not self.missing_models:  # Check if list is empty
                        return
                    
                    for model in self.missing_models:
                        result = await search_for_model(model['filename'])
                        if result:
                            model['repo_id'] = result['repo_id']
                            print(f"→Found repo: {result['repo_id']} for {model['filename']}")            
                
                loop.run_until_complete(search_all_models())
            finally:
                loop.close()
            
            self.initialized = True
                    
            # Update widget with found models
            if not self.missing_models:  # Check if list is empty
                return ("No models found", "", "")
            
            self.update_model_list(self.missing_models)

            # Send update to frontend with models and select first one
            PromptServer.instance.send_sync("scan_complete", {
                "node": node_id,
                "models": self.missing_models
            })

            # Check if we have any valid models (with repo_id)
            valid_models = [m for m in self.missing_models if m.get('repo_id')]
            if valid_models:
                return (
                    valid_models[0]['repo_id'],
                    valid_models[0]['filename'],
                    valid_models[0]['local_path']
                )
            
            raise Exception("No valid models found to download")

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
    
    # TODO: filter out models without repo_id here, maybe keep a second list for valid ones?
    def update_model_list(self, models):
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

        # Save the missing_models list and initialized state
        return {
            "missing_models": self.missing_models,
            "initialized": self.initialized
        }
    
    def deserialize(self, data):
        print(f"[deserialize] Data: {data}")
        self.missing_models = data.get("missing_models", [])
        self.initialized = data.get("initialized", False)
        # Restore other relevant state variables
