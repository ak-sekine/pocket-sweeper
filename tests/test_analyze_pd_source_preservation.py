import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import analyze_pd_source_preservation as diagnostic


class DiagnosticTest(unittest.TestCase):
    def test_tick_conversion_is_exact_and_deterministic(self):
        self.assertEqual(diagnostic.source_tick(384, 384, 384), (384, "exact", 0))
        self.assertEqual(diagnostic.source_tick(1, 2, 3), (2, "rounded_half_up", 1))
        self.assertEqual(diagnostic.source_tick(1, 2, 3), diagnostic.source_tick(1, 2, 3))

    def test_classification(self):
        self.assertEqual(diagnostic.classify(60, 60), "PRESERVED")
        self.assertEqual(diagnostic.classify(61, 60), "TRANSFORMED")

    def test_source_hash_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.mid"
            path.write_bytes(b"not the approved source")
            with self.assertRaises(ValueError):
                diagnostic.compare(path, Path(directory) / "out")


if __name__ == "__main__":
    unittest.main()
