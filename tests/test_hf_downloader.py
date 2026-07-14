import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tests.helpers import PACKAGE_NAME, load_package


class HFDownloaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_package()
        cls.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.hf.hf_download"
        )

    def test_token_input_is_optional_and_masked(self):
        with patch.object(self.module, "get_model_dirs", return_value=["checkpoints"]):
            token_input = self.module.HFDownloader.INPUT_TYPES()["optional"]["hf_token"]

        self.assertEqual("STRING", token_input[0])
        self.assertEqual("", token_input[1]["default"])
        self.assertTrue(token_input[1]["password"])

    def test_download_sends_token_as_bearer_header(self):
        downloader = self.module.HFDownloader()

        with patch.object(downloader, "prepare_download_path", return_value="/models/checkpoints"), \
                patch.object(downloader, "handle_download", return_value=("flux1-dev.safetensors",)) as handle_download:
            result = downloader.download(
                repo_id="black-forest-labs/FLUX.1-dev",
                filename="flux1-dev.safetensors",
                local_path="checkpoints",
                node_id="node-1",
                hf_token="secret-token",
            )

        self.assertEqual(("flux1-dev.safetensors", None, None, None), result)
        self.assertEqual(
            {"Authorization": "Bearer secret-token"},
            handle_download.call_args.kwargs["headers"],
        )

    def test_download_omits_authorization_without_token(self):
        downloader = self.module.HFDownloader()

        with patch.object(downloader, "prepare_download_path", return_value="/models/checkpoints"), \
                patch.object(downloader, "handle_download", return_value=("model.safetensors",)) as handle_download:
            downloader.download(
                repo_id="public/repository",
                filename="model.safetensors",
                local_path="checkpoints",
                node_id="node-2",
            )

        self.assertIsNone(handle_download.call_args.kwargs["headers"])

    def test_downloader_exposes_filename_output(self):
        self.assertEqual(
            ("STRING", "MODEL", "CLIP", "VAE"),
            self.module.HFDownloader.RETURN_TYPES,
        )
        self.assertEqual(
            ("filename", "model", "clip", "vae"),
            self.module.HFDownloader.RETURN_NAMES,
        )

    def test_completed_download_returns_saved_filename(self):
        downloader = self.module.HFDownloader()

        with tempfile.TemporaryDirectory() as directory:
            downloaded_path = Path(directory) / "model.safetensors"
            with patch.object(
                self.module.DownloadManager,
                "download_with_progress",
                return_value=str(downloaded_path),
            ):
                result = downloader.handle_download(
                    self.module.DownloadManager.download_with_progress,
                    save_path=directory,
                    filename="requested.safetensors",
                )

        self.assertEqual(("model.safetensors",), result)

    def test_downloader_loads_checkpoint_when_requested(self):
        downloader = self.module.HFDownloader()
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
                patch.object(downloader, "prepare_download_path", return_value="/models/checkpoints"), \
                patch.object(downloader, "handle_download", return_value=("tiny.safetensors",)), \
                patch.object(self.module.folder_paths, "get_full_path_or_raise", return_value="/models/checkpoints/tiny.safetensors", create=True), \
                patch.object(self.module.folder_paths, "get_folder_paths", return_value=["/models/embeddings"]):
            result = downloader.download(
                repo_id="owner/tiny",
                filename="tiny.safetensors",
                local_path="checkpoints",
                node_id="node-1",
                load_checkpoint=True,
            )

        self.assertEqual(("tiny.safetensors", fake_model, fake_clip, fake_vae), result)
        comfy_sd_module.load_checkpoint_guess_config.assert_called_once_with(
            "/models/checkpoints/tiny.safetensors",
            output_vae=True,
            output_clip=True,
            embedding_directory=["/models/embeddings"],
        )


class DownloadManagerHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_package()
        cls.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.download_utils"
        )

    def test_request_receives_headers_and_download_completes(self):
        response = Mock()
        response.headers = {"content-length": "4"}
        response.iter_content.return_value = [b"test"]
        response.raise_for_status.return_value = None

        with tempfile.TemporaryDirectory() as directory, \
                patch.object(self.module.requests, "get", return_value=response) as request:
            result = self.module.DownloadManager.download_with_progress(
                url="https://huggingface.co/org/repo/resolve/main/model.bin",
                save_path=directory,
                headers={"Authorization": "Bearer secret-token"},
            )

            self.assertEqual(b"test", Path(result).read_bytes())

        request.assert_called_once_with(
            "https://huggingface.co/org/repo/resolve/main/model.bin",
            stream=True,
            params=None,
            headers={"Authorization": "Bearer secret-token"},
        )


if __name__ == "__main__":
    unittest.main()
