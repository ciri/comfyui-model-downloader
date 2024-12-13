# Not used at the moment
import subprocess
import sys

def is_installed(package_name):
    """Check if a package is installed."""
    installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().lower()
    return f'{package_name.lower()}==' in installed_packages

def install_package(package_name):
    """Install a package using pip."""
    if not is_installed(package_name):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])

# Install joblib if it's not already installed
# install_package('joblib')
# install_package('huggingface_hub')
# install_package('tqdm')