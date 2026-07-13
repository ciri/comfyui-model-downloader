import importlib.util
import sys
import types
from pathlib import Path


PACKAGE_NAME = "comfyui_model_downloader"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PromptServer:
    instance = types.SimpleNamespace(send_sync=lambda *args, **kwargs: None)


def load_package(folder_paths=None, execute=False):
    for module_name in list(sys.modules):
        if module_name == PACKAGE_NAME or module_name.startswith(f"{PACKAGE_NAME}."):
            del sys.modules[module_name]

    server_module = types.ModuleType("server")
    server_module.PromptServer = PromptServer
    sys.modules["server"] = server_module

    tqdm_module = types.ModuleType("tqdm")
    tqdm_module.tqdm = DummyProgressBar
    sys.modules["tqdm"] = tqdm_module

    if folder_paths is None:
        folder_paths = types.ModuleType("folder_paths")
        folder_paths.models_dir = str(PROJECT_ROOT / "models")
        folder_paths.folder_names_and_paths = {
            "checkpoints": ([str(PROJECT_ROOT / "models" / "checkpoints")], set())
        }
        folder_paths.get_folder_paths = lambda folder_name: list(
            folder_paths.folder_names_and_paths[folder_name][0]
        )
    sys.modules["folder_paths"] = folder_paths

    if execute:
        spec = importlib.util.spec_from_file_location(
            PACKAGE_NAME,
            PROJECT_ROOT / "__init__.py",
            submodule_search_locations=[str(PROJECT_ROOT)],
        )
        package = importlib.util.module_from_spec(spec)
    else:
        package = types.ModuleType(PACKAGE_NAME)
        package.__path__ = [str(PROJECT_ROOT)]
        package.__package__ = PACKAGE_NAME
    sys.modules[PACKAGE_NAME] = package
    if execute:
        spec.loader.exec_module(package)
    return package


class DummyProgressBar:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def update(self, size):
        pass
