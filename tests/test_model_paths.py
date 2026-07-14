import importlib
import tempfile
import types
import unittest
from pathlib import Path

from tests.helpers import PACKAGE_NAME, load_package


def make_folder_paths(models_dir, default_checkpoints):
    module = types.ModuleType("folder_paths")
    module.models_dir = models_dir
    module.folder_names_and_paths = {
        "checkpoints": ([default_checkpoints, str(Path(models_dir) / "checkpoints")], {".safetensors"}),
        "loras": ([str(Path(models_dir) / "loras")], {".safetensors"}),
        "custom_nodes": ([str(Path(models_dir).parent / "custom_nodes")], set()),
    }
    module.get_folder_paths = lambda folder_name: list(
        module.folder_names_and_paths[folder_name][0]
    )
    return module


class ModelPathTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.models_dir = Path(self.temporary_directory.name) / "models"
        self.default_checkpoints = Path(self.temporary_directory.name) / "shared" / "checkpoints"
        folder_paths = make_folder_paths(
            str(self.models_dir),
            str(self.default_checkpoints),
        )
        load_package(folder_paths)
        self.base_module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.base_downloader"
        )
        self.auto_utils = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.auto.utils"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_model_directory_choices_come_from_comfyui(self):
        self.assertEqual(["checkpoints", "loras"], self.base_module.get_model_dirs())

    def test_configured_default_directory_is_used_for_downloads(self):
        downloader = self.base_module.BaseModelDownloader()

        result = downloader.prepare_download_path("checkpoints", "model.safetensors")

        self.assertEqual(str(self.default_checkpoints), result)
        self.assertTrue(self.default_checkpoints.is_dir())

    def test_relative_override_remains_under_models_directory(self):
        downloader = self.base_module.BaseModelDownloader()

        result = downloader.prepare_download_path("custom/subfolder", "model.bin")

        self.assertEqual(str(self.models_dir / "custom" / "subfolder"), result)

    def test_absolute_override_is_preserved(self):
        downloader = self.base_module.BaseModelDownloader()
        absolute_path = Path(self.temporary_directory.name) / "absolute"

        result = downloader.prepare_download_path(str(absolute_path), "model.bin")

        self.assertEqual(str(absolute_path), result)

    def test_auto_downloader_uses_configured_default_directory(self):
        self.assertEqual(
            str(self.default_checkpoints),
            self.auto_utils.get_model_path("checkpoints"),
        )


if __name__ == "__main__":
    unittest.main()
