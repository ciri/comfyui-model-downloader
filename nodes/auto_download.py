import os
import json
from server import PromptServer
from aiohttp import web
from .base_downloader import BaseModelDownloader, get_model_dirs
import sys
import aiohttp
import re
import asyncio


# Global dictionary to store node instances
node_instances = {}


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
        print("[AutoModelDownloader] Initialized")

    def process(self, select_model, prompt, node_id):
        print(f"[process] Called with select_model={select_model}, prompt={prompt}, node_id={node_id}")
        
        if not self.initialized:
            self.missing_models = self._scan_workflow(prompt)
            print(f"[process] Found missing models: {self.missing_models}")
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Search for each model
            async def search_all_models():
                for model in self.missing_models:
                    result = await search_for_model(model['filename'])
                    if result:
                        model['repo_id'] = result['repo_id']
                        print(f"Found repo: {result['repo_id']} for {model['filename']}")            
            try:
                loop.run_until_complete(search_all_models())
            finally:
                loop.close()
            
            self.initialized = True

                        
            # Update widget with found models
            filenames = [m['filename'] for m in self.missing_models]
            if not filenames:
                filenames = ["No models found"]
                return ("No models found", "")
            
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
                    valid_models[0]['filename']
                )
            
            raise Exception("No valid models found to download")

        # Handle missing or default values
        if not select_model or select_model == "Scan First":
            print("[process] No model selected. Skipping...")
            raise Exception("Select a model")

        # Find selected model
        selected_model = next((m for m in self.missing_models if m['filename'] == select_model), None)
        if not selected_model:
            print(f"[process] No model found for {select_model}")
            raise Exception("Model not found")
        
        repo_id = selected_model.get('repo_id', '')
        if not repo_id:
            print(f"[process] No repo_id found for {select_model}")
            raise Exception("No repository found")
        
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

import aiohttp
import re

async def search_for_model(filename):
    """
    Search for a model file on Hugging Face based on its filename components.
    """
    def extract_model_components(filename):
        name_without_extension = re.sub(r'\.[^/.]+$', '', filename)
        parts = re.split(r'[-_]', name_without_extension)
        
        core_name = []
        version = None
        tags = []
        
        for part in parts:
            if re.match(r'v?\d+(-\d+)?', part):
                version = part
            elif re.match(r'[a-zA-Z]+', part):
                if not core_name:
                    core_name.append(part)
                else:
                    tags.append(part)
            elif core_name:
                tags.append(part)
        
        core_name = "_".join(core_name) if core_name else None
        return {"core_name": core_name, "version": version, "tags": tags}
    
    print(f"Searching for model: {filename}")
    components = extract_model_components(filename)
    print(f"Extracted components: {components}")
    
    base_url = "https://huggingface.co/api/models"
    search_queries = []
    
    # Construct search queries
    if components["core_name"]:
        if components["version"]:
            search_queries.append(f"{components['core_name']}_{components['version']}")
        search_queries.append(components["core_name"])
    search_queries.append("_".join([components["core_name"], *components["tags"]]))

    print(f"Search queries: {search_queries}")

    headers = {}
    # Add HF token support if needed
    # if hf_token:
    #     headers["Authorization"] = f"Bearer {hf_token}"

    matching_result = None
    async with aiohttp.ClientSession() as session:
        # Search repositories
        for query in search_queries:
            print(f"Searching for repository: {query}")
            async with session.get(f"{base_url}?full=true&search={query}", headers=headers) as response:
                if response.status == 200:
                    repos = await response.json()
                    if repos:
                        for repo in repos:
                            # Check repository siblings for the exact file match
                            # print(f"Checking repository: {repo['modelId']}")
                            if "siblings" in repo:
                                match = next(
                                    (sibling for sibling in repo["siblings"] if sibling["rfilename"] == filename),
                                    None
                                )
                                if match:
                                    matching_result = {
                                        "repo_id": repo["modelId"],
                                        "file": match
                                    }
                                    break
                        if matching_result:
                            break
                else:
                    print(f"Failed to search for repository {query}: {response.status}")
            if matching_result:
                break

    if matching_result:
        print(f"Match found: {matching_result['repo_id']}")
        return {
            "repo_id": matching_result["repo_id"],
            "filename": filename
        }
    else:
        print(f"No exact match found for {filename}")
        return None
