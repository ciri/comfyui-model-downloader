import importlib
import tempfile
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
                patch.object(downloader, "handle_download", return_value={}) as handle_download:
            result = downloader.download(
                repo_id="black-forest-labs/FLUX.1-dev",
                filename="flux1-dev.safetensors",
                local_path="checkpoints",
                node_id="node-1",
                hf_token="secret-token",
            )

        self.assertEqual({}, result)
        self.assertEqual(
            {"Authorization": "Bearer secret-token"},
            handle_download.call_args.kwargs["headers"],
        )

    def test_download_omits_authorization_without_token(self):
        downloader = self.module.HFDownloader()

        with patch.object(downloader, "prepare_download_path", return_value="/models/checkpoints"), \
                patch.object(downloader, "handle_download", return_value={}) as handle_download:
            downloader.download(
                repo_id="public/repository",
                filename="model.safetensors",
                local_path="checkpoints",
                node_id="node-2",
            )

        self.assertIsNone(handle_download.call_args.kwargs["headers"])


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
