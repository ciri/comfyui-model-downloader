import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

from tests.helpers import PACKAGE_NAME, load_package


class DownloadedCheckpointLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_package()
        cls.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.checkpoint_loader"
        )

    def test_loader_resolves_filename_and_loads_checkpoint(self):
        fake_model = object()
        fake_clip = object()
        fake_vae = object()
        comfy_module = types.ModuleType("comfy")
        comfy_sd_module = types.ModuleType("comfy.sd")
        comfy_sd_module.load_checkpoint_guess_config = Mock(
            return_value=(fake_model, fake_clip, fake_vae, object())
        )
        comfy_module.sd = comfy_sd_module

        with patch.dict(sys.modules, {"comfy": comfy_module, "comfy.sd": comfy_sd_module}), \
                patch.object(self.module.folder_paths, "get_full_path_or_raise", return_value="/models/checkpoints/tiny.safetensors", create=True), \
                patch.object(self.module.folder_paths, "get_folder_paths", return_value=["/models/embeddings"]):
            result = self.module.DownloadedCheckpointLoader().load_checkpoint(
                "tiny.safetensors"
            )

        self.assertEqual((fake_model, fake_clip, fake_vae), result)
        comfy_sd_module.load_checkpoint_guess_config.assert_called_once_with(
            "/models/checkpoints/tiny.safetensors",
            output_vae=True,
            output_clip=True,
            embedding_directory=["/models/embeddings"],
        )
