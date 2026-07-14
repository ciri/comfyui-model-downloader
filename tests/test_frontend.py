import unittest
from pathlib import Path


class DownloaderFrontendTests(unittest.TestCase):
    def test_progress_renderer_uses_current_comfyui_title_bar_api(self):
        source = (Path(__file__).parents[1] / "js" / "hfdownloader.js").read_text()

        self.assertIn("CivitAI Downloader", source)
        self.assertIn("function(ctx, titleHeight, size, scale, foregroundColor)", source)
        self.assertIn("ctx.rect(0, -titleHeight, titleWidth, titleHeight)", source)
        self.assertIn("ctx.fillRect(0, -titleHeight, titleWidth * progress, titleHeight)", source)
        self.assertIn("Math.min(1, Math.max(0, value / maximum))", source)
        self.assertNotIn("ctx.fillText(this.title", source)

    def test_auto_model_finder_restores_output_links_after_loading(self):
        source = (Path(__file__).parents[1] / "js" / "autodownloader.js").read_text()

        self.assertIn("const synchronizeOutputLinks", source)
        self.assertIn("output.links = []", source)
        self.assertIn("output.links.push(linkId)", source)
        self.assertIn("setTimeout(() => synchronizeOutputLinks(this), 0)", source)

    def test_auto_model_finder_uses_current_selection_keys(self):
        source = (Path(__file__).parents[1] / "js" / "autodownloader.js").read_text()

        self.assertIn("model.selection", source)
        self.assertIn("!selections.includes(selectWidget.value)", source)
        self.assertNotIn("this.triggerSlot(0)", source)
        self.assertNotIn("getExtraProperties", source)

    def test_auto_model_finder_has_an_explicit_rescan_button(self):
        source = (Path(__file__).parents[1] / "js" / "autodownloader.js").read_text()

        self.assertIn('"Rescan models"', source)
        self.assertIn('api.fetchApi("/model-downloader/scan"', source)
        self.assertIn("await app.graphToPrompt()", source)


if __name__ == "__main__":
    unittest.main()
