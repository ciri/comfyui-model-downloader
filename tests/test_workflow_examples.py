import json
import unittest
from pathlib import Path


WORKFLOWS_DIRECTORY = Path(__file__).parents[1] / "examples" / "workflows"


class WorkflowExampleTests(unittest.TestCase):
    def load_workflow(self, filename):
        return json.loads((WORKFLOWS_DIRECTORY / filename).read_text())

    def test_civitai_demo_downloads_and_previews_an_image(self):
        workflow = self.load_workflow("civitai-demo.json")
        nodes = {node["id"]: node for node in workflow["nodes"]}

        self.assertEqual("CivitAI Downloader", nodes[1]["type"])
        self.assertEqual(["71", "80", ""], nodes[1]["widgets_values"][:3])
        self.assertEqual("Downloaded Checkpoint Loader", nodes[8]["type"])
        self.assertEqual("PreviewImage", nodes[7]["type"])
        self.assertEqual(
            [433342518721672, "randomize", 20, 20.0, "euler", "exponential", 1.0],
            nodes[5]["widgets_values"],
        )

    def test_auto_model_finder_workflow_is_scan_only(self):
        workflow = self.load_workflow("auto-model-finder-scan.json")
        nodes = {node["id"]: node for node in workflow["nodes"]}

        self.assertEqual("CheckpointLoaderSimple", nodes[1]["type"])
        self.assertEqual(["model.safetensors"], nodes[1]["widgets_values"])
        self.assertEqual("Auto Model Downloader", nodes[2]["type"])
        self.assertEqual("PreviewAny", nodes[3]["type"])
        self.assertEqual("PreviewAny", nodes[4]["type"])
        self.assertEqual("PreviewAny", nodes[5]["type"])
        self.assertEqual(
            [
                [1, 2, 0, 3, 0, "STRING"],
                [2, 2, 1, 4, 0, "STRING"],
                [3, 2, 2, 5, 0, "STRING"],
            ],
            workflow["links"],
        )

    def test_huggingface_demo_downloads_and_previews_an_image(self):
        workflow = self.load_workflow("hf-demo.json")
        nodes = {node["id"]: node for node in workflow["nodes"]}

        self.assertEqual("HF Downloader", nodes[1]["type"])
        self.assertEqual("Downloaded Checkpoint Loader", nodes[8]["type"])
        self.assertEqual("KSampler", nodes[5]["type"])
        self.assertEqual(
            [433342518721672, "randomize", 20, 20.0, "euler", "exponential", 1.0],
            nodes[5]["widgets_values"],
        )
        self.assertEqual([512, 512, 1], nodes[4]["widgets_values"])
        self.assertEqual("PreviewImage", nodes[7]["type"])
        self.assertIn([1, 1, 0, 8, 0, "STRING"], workflow["links"])
        self.assertIn([10, 6, 0, 7, 0, "IMAGE"], workflow["links"])
