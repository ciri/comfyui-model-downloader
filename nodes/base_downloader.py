from server import PromptServer
import os

def get_base_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    models_dir = os.path.join(base_dir, 'models')
    return models_dir

def get_model_dirs():
    models_dir = get_base_dir()
    model_dirs = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    return model_dirs

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
        # Just create the base directory, don't include the filename
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