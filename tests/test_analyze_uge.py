import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_uge  # noqa: E402
import json_to_uge  # noqa: E402


class AnalyzeUgeTests(unittest.TestCase):
    def test_reads_generated_version_2_structure(self):
        source = ROOT / "assets" / "bgm_v2_workflow_check.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflow.uge"
            path.write_bytes(json_to_uge.build_uge(data))
            result = analyze_uge.read_file(path)

        self.assertEqual(result["song_version"], {"raw": 6, "interpreted": "6", "supported": True})
        self.assertEqual(result["order_counts"], [6, 6, 6, 6])
        self.assertEqual(result["order_alignment"], "一致")
        self.assertEqual(result["loop"]["kind"], "explicit_position_jump")
        self.assertEqual(result["loop"]["start_order"], 2)
        self.assertTrue(all(result["channels"][channel]["used"] for channel in analyze_uge.CHANNELS))


if __name__ == "__main__":
    unittest.main()
