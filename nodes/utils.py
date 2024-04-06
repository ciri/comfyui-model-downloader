import os

    
def get_base_dir():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate 3 levels up from the current directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    # Append the 'models' directory to the path
    models_dir = os.path.join(base_dir, 'models')
    return models_dir

def get_model_dirs():
    models_dir = get_base_dir()
    model_dirs = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    return model_dirs
