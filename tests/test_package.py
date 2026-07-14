import unittest

from tests.helpers import load_package


class PackageSmokeTests(unittest.TestCase):
    def test_package_registers_all_nodes(self):
        package = load_package(execute=True)

        self.assertEqual(
            {
                "HF Downloader",
                "Downloaded Checkpoint Loader",
                "Auto Model Downloader",
                "CivitAI Downloader",
            },
            set(package.NODE_CLASS_MAPPINGS),
        )
        self.assertEqual("./js", package.WEB_DIRECTORY)


if __name__ == "__main__":
    unittest.main()
