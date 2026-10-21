# test_plot_histogram.py - runs on the PC
# Runs plot_histogram.py on a small known log.txt in a temp folder and
# checks that histogram.png is written.
import os
import runpy
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent


class TestPlotHistogram(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def test_histogram_written(self):
        # Small known log: four trials
        with open("log.txt", "w") as f:
            f.write("14\n15\n15\n16\n")
        runpy.run_path(str(LAB_DIR / "plot_histogram.py"))
        self.assertTrue(os.path.exists("histogram.png"))
        self.assertGreater(os.path.getsize("histogram.png"), 0)


if __name__ == "__main__":
    unittest.main()
