from server import PromptServer
import folder_paths
import os

def get_base_dir():
    return folder_paths.models_dir

def get_model_dirs():
    return sorted(
        folder_name
        for folder_name, (paths, _) in folder_paths.folder_names_and_paths.items()
        if paths and folder_name != "custom_nodes"
    )

class BaseModelDownloader:
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = "loaders"

    def __init__(self):
        self.status = "Idle"
        self.progress = 0.0
        self.node_id = None

    def set_progress(self, percentage):
        self.update_status(f"Downloading... {percentage:.1f}%", percentage)

    def update_status(self, status_text, progress=None):
        if progress is not None and hasattr(self, 'node_id'):
            PromptServer.instance.send_sync("progress", {
                "node": self.node_id,
                "value": progress,
                "max": 100
            })


    def prepare_download_path(self, local_path, filename):
        if os.path.isabs(local_path):
            full_path = local_path
        elif local_path in folder_paths.folder_names_and_paths:
            full_path = folder_paths.get_folder_paths(local_path)[0]
        else:
            full_path = os.path.join(get_base_dir(), local_path)

        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
        return full_path

    def handle_download(self, download_func, save_path, filename, overwrite=False, **kwargs):
        try:
            file_path = os.path.join(save_path, filename)
            if os.path.exists(file_path) and not overwrite:
                print(f"File already exists and overwrite is False: {file_path}")
                return {}

            kwargs['save_path'] = save_path
            download_func(**kwargs)
            self.update_status("Complete!", 100)
            return {}
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise e
