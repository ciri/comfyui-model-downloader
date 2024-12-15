from .utils import get_model_path
from .constants import EXTENSION_MAP
import os

async def scan_workflow(prompt):
    print(f"[Scannner] Scanning workflow.")
    if not prompt:
        print("No workflow found")
        return []

    missing_models = []

    for node_id, node in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs = node.get("inputs", {})
        for key, input_path in inputs.items():
            if not isinstance(input_path, str):
                continue

            # Split into directory and filename
            if '/' in input_path:
                # For paths like "custom_dir/model.safetensors"
                local_path = os.path.dirname(input_path)
                filename = os.path.basename(input_path)
            else:
                # For regular files like "model.safetensors"
                filename = input_path
                file_extension = os.path.splitext(filename)[1].lower()

                # Skip inputs without a valid extension
                if not file_extension:                    
                    continue

                # Map to a valid model directory - THIS IS THE DIRECTORY
                local_path = EXTENSION_MAP.get(file_extension)
                if not local_path:
                    continue

            missing_models.append({
                "filename": filename,  # JUST the filename
                "repo_id": None,
                "local_path": local_path  # JUST the directory
            })
            print(f"[Scanner] Missing model: {filename}, Directory: {local_path}")

    print(f"[Scanner] {len(missing_models)} missing models")
    return missing_models
