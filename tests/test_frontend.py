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


if __name__ == "__main__":
    unittest.main()
