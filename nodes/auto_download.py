import os
import json
from server import PromptServer
from aiohttp import web
from .base_downloader import BaseModelDownloader, get_model_dirs
import sys
import logging


# Global dictionary to store node instances
node_instances = {}

@PromptServer.instance.routes.post("/customnode/comfyui-model-downloader/update_model_list")
async def update_model_list_endpoint(request):
    print(f"[update_model_list_endpoint] Received request")
    try:
        json_data = await request.json()
        print(f"[update_model_list_endpoint] Received data: {json_data}")
        
        node_id = str(json_data.get("id"))
        models  = json_data.get("models", [])
        
        node = node_instances.get(node_id)
        print(f"[update_model_list_endpoint] Found node instances: {node_instances}")
        print(f"[update_model_list_endpoint] Found node: {node}")
        
        if node and isinstance(node, AutoModelDownloader):
            result = node.update_model_list(models)
            print(f"[update_model_list_endpoint] Update result: {result}")
            return web.json_response({"success": True, "result": result})
        else:
            print(f"[update_model_list_endpoint] Node not found or wrong type. ID: {node_id}, Type: {type(node)}")
            return web.json_response({"success": False, "error": f"Node not found: {node_id}"})

        
    except Exception as e:
        print(f"[update_model_list_endpoint] Error: {str(e)}", exc_info=True)
        return web.json_response({"success": False, "error": str(e)})


class AutoModelDownloader(BaseModelDownloader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Define as COMBO special type
                "select_model": (["SCAN FIRST"], {
                    "choices": ["Scan First"],
                    "default": "Scan First"
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "node_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("repo_id", "filename")
    FUNCTION = "process"
    CATEGORY = "loaders"
    
    @classmethod
    def VALIDATE_INPUTS(cls, *args, **kwargs):
        return True  # Skip validation

    def __init__(self):
        super().__init__()
        self.missing_models = []
        self.initialized = False
        self.widget_updated = False
        self.node_id = None
        print("[AutoModelDownloader] Initialized")

    def process(self, select_model, prompt, node_id):
        print(f"[process] Called with select_model={select_model}, prompt={prompt}, node_id={node_id}")
        
        node_instances[node_id] = self
        
        if not self.initialized:
            self.node_id = node_id
            self.missing_models = self._scan_workflow(prompt)
            print(f"[process] First run, found missing models: {self.missing_models}")
            
            PromptServer.instance.send_sync("scan_complete", {
                "node": node_id,
                "models": self.missing_models
            })
            self.initialized = True
            #return ("", "")
            return ("", "")


        # Handle missing or default values
        if not select_model:
            print("[process] No model selected. Skipping...")
            return ("", "")

        # Find selected model
        selected_model = next((m for m in self.missing_models if m['filename'] == select_model), None)
        if not selected_model:
            print(f"[process] No model found for {select_model}")
            return ("", "")
        
        repo_id = selected_model.get('repo_id', '')
        if not repo_id:
            print(f"[process] No repo_id found for {select_model}")
            return ("", "")
        
        print(f"[process] Returning model info: repo_id={repo_id}, filename={selected_model['filename']}")
        return (repo_id, selected_model['filename'])

    def _scan_workflow(self, prompt):
        print(f"Scanning workflow with prompt: {prompt}")
        if not prompt:
            print("No workflow found")
            return []

        print("\n=== Starting Workflow Scan ===")
        missing_models = []
        
        for node_id, node in prompt.items():
            if not isinstance(node, dict):
                continue
                
            inputs = node.get("inputs", {})
            
            if "ckpt_name" in inputs:
                filename = inputs["ckpt_name"]
                if not self.check_model_exists(filename, "checkpoints"):
                    missing_models.append({
                        "filename": filename,
                        "repo_id": None
                    })
            
            if "lora_name" in inputs:
                filename = inputs["lora_name"]
                if not self.check_model_exists(filename, "loras"):
                    missing_models.append({
                        "filename": filename,
                        "repo_id": None
                    })

        print(f"Found {len(missing_models)} missing models")
        return missing_models

    def check_model_exists(self, filename, model_type):
        print(f"Checking model {filename} in {model_type}")

        base_path = self.get_model_path(model_type)
        full_path = os.path.join(base_path, filename)
        exists = os.path.exists(full_path)
        print(f"Checking {full_path}: {'Found' if exists else 'Missing'}")
        return exists

    def get_model_path(self, model_type):
        print(f"Getting model path for {model_type}")
        base_dir = get_model_dirs()[0]
        return os.path.join(base_dir, model_type)

    def update_model_list(self, models):
        print(f"[update_model_list] Updating with models: {models}")
        self.missing_models = []
        
        for model in models:
            if model.get('filename') and model.get('repo_id'):
                self.missing_models.append({
                    'filename': model['filename'],
                    'repo_id': model['repo_id']
                })
                print(f"[update_model_list] Added model: {model}")
        
        self.widget_updated = True
        
        filenames = [m['filename'] for m in self.missing_models]
        if not filenames:
            filenames = ["No models found"]
        
        # Changed to update SELECT widget
        result = {
            "widget_name": "select_model", 
            "options": filenames,  # The available options
            "value": filenames[0] if filenames else "No models found"  # Default selected value
        }
        print(f"[update_model_list] Returning widget update: {result}")
        return result

    def onWidgetChanged(self, widget_name, value):
        print(f"[onWidgetChanged] Called with widget_name={widget_name}, value={value}")
        if widget_name == "select_model":
            # Handle the change in selected model
            self.selected_model = value

        return True
