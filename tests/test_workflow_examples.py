import json
import unittest
from pathlib import Path


WORKFLOWS_DIRECTORY = Path(__file__).parents[1] / "examples" / "workflows"


class WorkflowExampleTests(unittest.TestCase):
    def load_workflow(self, filename):
        return json.loads((WORKFLOWS_DIRECTORY / filename).read_text())

    def test_huggingface_workflow_uses_small_public_model(self):
        workflow = self.load_workflow("huggingface-tiny-download.json")
        node = workflow["nodes"][0]

        self.assertEqual("HF Downloader", node["type"])
        self.assertEqual(
            ["hf-internal-testing/tiny-random-bert", "model.safetensors"],
            node["widgets_values"][:2],
        )
        self.assertEqual([[1, 1, 0, 2, 0, "STRING"]], workflow["links"])

    def test_civitai_workflow_pins_public_tiny_file_without_key(self):
        workflow = self.load_workflow("civitai-tiny-download.json")
        node = workflow["nodes"][0]

        self.assertEqual("CivitAI Downloader", node["type"])
        self.assertEqual(["723360", "1047814", ""], node["widgets_values"][:3])
        self.assertEqual([[1, 1, 0, 2, 0, "STRING"]], workflow["links"])

    def test_auto_model_finder_workflow_is_scan_only(self):
        workflow = self.load_workflow("auto-model-finder-scan.json")
        nodes = {node["id"]: node for node in workflow["nodes"]}

        self.assertEqual("CheckpointLoaderSimple", nodes[1]["type"])
        self.assertEqual(["model.safetensors"], nodes[1]["widgets_values"])
        self.assertEqual("Auto Model Downloader", nodes[2]["type"])
        self.assertEqual("PreviewAny", nodes[3]["type"])
        self.assertEqual([[1, 2, 0, 3, 0, "STRING"]], workflow["links"])
