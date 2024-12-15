import os

def get_base_dir():
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    models_dir = os.path.join(base_dir, 'models')
    return models_dir

def get_model_dirs():
    models_dir = get_base_dir()
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return ["models"]  # Return default if directory doesn't exist
    model_dirs = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    return model_dirs if model_dirs else ["models"]  # Return default if no subdirectories found

def get_model_path(model_type):
    base_dir = get_base_dir()
    return os.path.join(base_dir, model_type)

def check_model_exists(filename, model_type):
    local_path = get_model_path(model_type)
    full_path = os.path.join(local_path, filename)
    return os.path.exists(full_path)
