import asyncio
import importlib
import unittest
from unittest.mock import Mock, patch

from tests.helpers import PACKAGE_NAME, load_package


class ModelSearchTests(unittest.TestCase):
    def setUp(self):
        load_package()
        self.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.auto.model_search"
        )
        self.module._model_cache.clear()

    def test_model_search_is_synchronous(self):
        response = Mock(status_code=200)
        response.json.return_value = [
            {
                "modelId": "owner/repository",
                "siblings": [{"rfilename": "example-v1.safetensors"}],
            }
        ]

        with patch.object(self.module.requests, "get", return_value=response) as request:
            result = self.module.search_for_model("example-v1.safetensors")

        self.assertEqual(
            {
                "repo_id": "owner/repository",
                "filename": "example-v1.safetensors",
            },
            result,
        )
        request.assert_called_with(
            "https://huggingface.co/api/models",
            params={"full": "true", "search": "example_v1"},
        )

    def test_cached_result_avoids_second_request(self):
        response = Mock(status_code=200)
        response.json.return_value = [
            {
                "modelId": "owner/repository",
                "siblings": [{"rfilename": "model.safetensors"}],
            }
        ]

        with patch.object(self.module.requests, "get", return_value=response) as request:
            first = self.module.search_for_model("model.safetensors")
            second = self.module.search_for_model("model.safetensors")

        self.assertEqual(first, second)
        self.assertEqual(1, request.call_count)

    def test_sd_checkpoint_filename_uses_stable_diffusion_search(self):
        no_match = Mock(status_code=200)
        no_match.json.return_value = []
        matching_response = Mock(status_code=200)
        matching_response.json.return_value = [
            {
                "modelId": "owner/stable-diffusion-tiny",
                "siblings": [{"rfilename": "sd-v1-5-tiny.safetensors"}],
            }
        ]

        with patch.object(
            self.module.requests,
            "get",
            side_effect=[no_match, matching_response],
        ) as request:
            result = self.module.search_for_model("sd-v1-5-tiny.safetensors")

        self.assertEqual(
            {
                "repo_id": "owner/stable-diffusion-tiny",
                "filename": "sd-v1-5-tiny.safetensors",
            },
            result,
        )
        self.assertEqual(
            [
                {"full": "true", "search": "sd_5"},
                {"full": "true", "search": "stable-diffusion-tiny"},
            ],
            [call.kwargs["params"] for call in request.call_args_list],
        )


class AutoDownloaderEventLoopTests(unittest.TestCase):
    def setUp(self):
        load_package()
        self.module = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.auto.downloader"
        )

    def test_process_runs_when_event_loop_is_already_running(self):
        downloader = self.module.AutoModelDownloader()
        prompt = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "model.safetensors"},
            }
        }
        missing_models = [
            {
                "filename": "model.safetensors",
                "repo_id": None,
                "local_path": "checkpoints",
            }
        ]

        async def run_process():
            with patch.object(
                self.module,
                "scan_workflow",
                return_value=missing_models,
            ), patch.object(
                self.module,
                "search_for_model",
                return_value={"repo_id": "owner/repository"},
            ):
                return downloader.process("Scan First", prompt, "node-1")

        result = asyncio.run(run_process())

        self.assertEqual(
            ("owner/repository", "model.safetensors", "checkpoints"),
            result,
        )

    def test_process_selects_a_second_discovered_model(self):
        downloader = self.module.AutoModelDownloader()
        prompt = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "first.safetensors"},
            },
            "2": {
                "class_type": "CLIPLoader",
                "inputs": {"clip_name": "second.bin"},
            },
        }
        missing_models = [
            {
                "filename": "first.safetensors",
                "repo_id": None,
                "local_path": "checkpoints",
            },
            {
                "filename": "second.bin",
                "repo_id": None,
                "local_path": "clip_models",
            },
        ]

        with patch.object(self.module, "scan_workflow", return_value=missing_models), \
                patch.object(
                    self.module,
                    "search_for_model",
                    side_effect=[
                        {"repo_id": "owner/first"},
                        {"repo_id": "owner/second"},
                    ],
                ):
            downloader.process("Scan First", prompt, "node-1")

        result = downloader.process("second.bin", prompt, "node-1")

        self.assertEqual(("owner/second", "second.bin", "clip_models"), result)

    def test_workflow_scanner_is_synchronous(self):
        scanner = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.auto.workflow_scanner"
        )

        result = scanner.scan_workflow(
            {
                "1": {
                    "inputs": {"ckpt_name": "model.safetensors"},
                }
            }
        )

        self.assertEqual(
            [
                {
                    "filename": "model.safetensors",
                    "repo_id": None,
                    "local_path": "checkpoints",
                }
            ],
            result,
        )

    def test_workflow_scanner_skips_models_that_exist(self):
        scanner = importlib.import_module(
            f"{PACKAGE_NAME}.nodes.auto.workflow_scanner"
        )

        with patch.object(scanner, "check_model_exists", return_value=True):
            result = scanner.scan_workflow(
                {
                    "1": {
                        "inputs": {"ckpt_name": "model.safetensors"},
                    }
                }
            )

        self.assertEqual([], result)


if __name__ == "__main__":
    unittest.main()
