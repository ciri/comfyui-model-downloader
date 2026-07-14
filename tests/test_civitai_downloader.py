import importlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tests.helpers import PACKAGE_NAME, load_package


def make_folder_paths(models_dir):
    module = types.ModuleType("folder_paths")
    checkpoints = str(Path(models_dir) / "checkpoints")
    module.models_dir = models_dir
    module.folder_names_and_paths = {
        "checkpoints": ([checkpoints], {".safetensors"}),
    }
    module.get_folder_paths = lambda folder_name: list(
        module.folder_names_and_paths[folder_name][0]
    )
    return module


class CivitAIDownloaderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        folder_paths = make_folder_paths(self.temporary_directory.name)
        load_package(folder_paths)
        self.base_module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.base_downloader"
        )
        self.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.cai.cai_download"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_prepare_download_path_accepts_legacy_call_without_filename(self):
        downloader = self.base_module.BaseModelDownloader()

        result = downloader.prepare_download_path("checkpoints")

        self.assertEqual(
            str(Path(self.temporary_directory.name) / "checkpoints"),
            result,
        )

    def test_api_key_input_is_optional_and_masked(self):
        with patch.object(self.module, "get_model_dirs", return_value=["checkpoints"]):
            api_key_input = self.module.CivitAIDownloader.INPUT_TYPES()["required"]["api_key"]

        self.assertEqual("STRING", api_key_input[0])
        self.assertEqual("", api_key_input[1]["default"])
        self.assertTrue(api_key_input[1]["password"])

    def test_latest_version_filename_and_url_are_discovered(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "modelVersions": [
                {
                    "id": 100,
                    "createdAt": "2025-01-01T00:00:00Z",
                    "files": [{"name": "old.safetensors", "downloadUrl": "https://old"}],
                },
                {
                    "id": 200,
                    "createdAt": "2025-02-01T00:00:00Z",
                    "files": [{"name": "new.safetensors", "downloadUrl": "https://new"}],
                },
            ]
        }

        with patch.object(self.module.requests, "get", return_value=response) as request:
            result = self.module.CivitAIDownloader().get_download_filename_url(
                "123",
                "",
                "token",
            )

        self.assertEqual(("new.safetensors", "https://new"), result)
        request.assert_called_once_with(
            "https://civitai.com/api/v1/models/123",
            headers={"Authorization": "Bearer token"},
        )

    def test_requested_version_is_selected(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "modelVersions": [
                {
                    "id": 100,
                    "createdAt": "2025-01-01T00:00:00Z",
                    "files": [{"name": "selected.bin", "downloadUrl": "https://selected"}],
                },
                {
                    "id": 200,
                    "createdAt": "2025-02-01T00:00:00Z",
                    "files": [{"name": "other.bin", "downloadUrl": "https://other"}],
                },
            ]
        }

        with patch.object(self.module.requests, "get", return_value=response):
            result = self.module.CivitAIDownloader().get_download_filename_url(
                "123",
                "100",
                "token",
            )

        self.assertEqual(("selected.bin", "https://selected"), result)

    def test_safetensors_is_preferred_over_an_archive(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "modelVersions": [
                {
                    "id": 100,
                    "files": [
                        {"name": "styles.zip", "downloadUrl": "https://archive"},
                        {"name": "model.safetensors", "downloadUrl": "https://model"},
                    ],
                }
            ]
        }

        with patch.object(self.module.requests, "get", return_value=response):
            result = self.module.CivitAIDownloader().get_download_filename_url(
                "123",
                "100",
                "",
            )

        self.assertEqual(("model.safetensors", "https://model"), result)

    def test_public_metadata_request_omits_authorization(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "modelVersions": [{"id": 100, "createdAt": "2025-01-01T00:00:00Z", "files": [{"name": "model.bin", "downloadUrl": "https://download"}]}]
        }

        with patch.object(self.module.requests, "get", return_value=response) as request:
            self.module.CivitAIDownloader().get_download_filename_url("123", "", "")

        request.assert_called_once_with(
            "https://civitai.com/api/v1/models/123",
            headers=None,
        )

    def test_download_uses_discovered_filename(self):
        downloader = self.module.CivitAIDownloader()

        with patch.object(
            downloader,
            "get_download_filename_url",
            return_value=("model.safetensors", "https://download"),
        ), patch.object(
            downloader,
            "prepare_download_path",
            return_value="/models/checkpoints",
        ) as prepare_path, patch.object(
            downloader,
            "handle_download",
            return_value={},
        ) as handle_download:
            result = downloader.download("123", "", "token", "checkpoints", "node-1")

        self.assertEqual({}, result)
        prepare_path.assert_called_once_with("checkpoints", "model.safetensors")
        self.assertEqual(
            "model.safetensors",
            handle_download.call_args.kwargs["filename"],
        )
        self.assertEqual("https://download", handle_download.call_args.kwargs["url"])
        self.assertEqual({"token": "token"}, handle_download.call_args.kwargs["params"])

    def test_download_omits_token_parameter_without_api_key(self):
        downloader = self.module.CivitAIDownloader()

        with patch.object(
            downloader,
            "get_download_filename_url",
            return_value=("model.safetensors", "https://download"),
        ), patch.object(
            downloader,
            "prepare_download_path",
            return_value="/models/checkpoints",
        ), patch.object(downloader, "handle_download", return_value={} ) as handle_download:
            downloader.download("123", "", "", "checkpoints", "node-1")

        self.assertIsNone(handle_download.call_args.kwargs["params"])

    def test_missing_versions_raise_clear_error(self):
        response = Mock(status_code=200)
        response.json.return_value = {"modelVersions": []}

        with patch.object(self.module.requests, "get", return_value=response):
            with self.assertRaisesRegex(Exception, "No versions found for model ID 123"):
                self.module.CivitAIDownloader().get_download_filename_url(
                    "123",
                    "",
                    "token",
                )


if __name__ == "__main__":
    unittest.main()
