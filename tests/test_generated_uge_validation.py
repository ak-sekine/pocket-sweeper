import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_uge  # noqa: E402
import json_to_uge  # noqa: E402


class GeneratedUgeValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "assets" / "bgm_v2_workflow_check.json").read_text(encoding="utf-8")
        )

    def build_and_analyze(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.uge"
            path.write_bytes(json_to_uge.build_uge(data))
            return analyze_uge.read_file(path)

    @staticmethod
    def cell(result, key, row):
        return result["pattern_cells"][str(key)][row]

    def test_generated_version_2_structure_matches_expected_input(self):
        result = self.build_and_analyze(self.data)

        self.assertEqual(result["song_version"], {"raw": 6, "interpreted": "6", "supported": True})
        self.assertEqual(result["order_counts"], [6, 6, 6, 6])
        self.assertEqual(result["order_alignment"], "一致")

        # Version 2 resolves channel-local pattern names in channel/order
        # order, yielding six keys per channel in the Song Version 6 output.
        expected_orders = {
            channel: list(range(index * 6, (index + 1) * 6))
            for index, channel in enumerate(analyze_uge.CHANNELS)
        }
        for channel, expected in expected_orders.items():
            report = result["channels"][channel]
            self.assertEqual(report["order_pattern_keys"], expected)
            self.assertTrue(report["used"])
            json_channel = {"ch1": "pulse1", "ch2": "pulse2", "ch3": "wave", "ch4": "noise"}[channel]
            self.assertEqual(report["order_count"], len(self.data["order"][json_channel]))

        self.assertEqual(result["loop"]["kind"], "explicit_simple_loop")
        self.assertEqual(result["loop"]["start_order"], 2)
        self.assertEqual(result["loop"]["end_order_inclusive"], 5)
        self.assertEqual(result["loop"]["loop_order_count"], 4)
        self.assertEqual(result["loop"]["unreachable_orders"], [])

        self.assertEqual(len(result["pattern_cells"]), result["pattern_count"])
        for cells in result["pattern_cells"].values():
            self.assertEqual(len(cells), 64)
            self.assertTrue(all(len(cell) == 5 and all(isinstance(value, int) for value in cell) for cell in cells))

        # Cxy is generated from note volume; E00 is generated from rest.
        self.assertEqual(self.cell(result, 0, 0), [24, 1, 0, 0x0C, 0x0C])
        self.assertEqual(self.cell(result, 0, 4), [analyze_uge.NO_NOTE, 0, 0, 0x0E, 0])
        self.assertEqual(self.cell(result, 6, 4), [12, 2, 0, 0x0C, 0x07])
        self.assertEqual(self.cell(result, 18, 0), [0, 1, 0, 0x0C, 0x06])

        # The range loop is emitted as a one-based B target on the final row.
        self.assertEqual(self.cell(result, 5, 63)[3:], [0x0B, 3])
        jump = result["channels"]["ch1"]["position_jumps"][0]
        self.assertEqual(jump["source_order"], 5)
        self.assertEqual(jump["raw_target_order"], 3)
        self.assertEqual(jump["target_order"], 2)

    def test_generated_unused_channel_is_reported_false(self):
        data = copy.deepcopy(self.data)
        del data["order"]["noise"]
        del data["patterns"]["noise"]
        result = self.build_and_analyze(data)
        self.assertEqual(result["order_counts"], [6, 6, 6, 6])
        self.assertTrue(result["channels"]["ch1"]["used"])
        self.assertTrue(result["channels"]["ch2"]["used"])
        self.assertTrue(result["channels"]["ch3"]["used"])
        self.assertFalse(result["channels"]["ch4"]["used"])
        self.assertEqual(result["channels"]["ch4"]["event_count"], 0)

    def test_full_loop_is_implicit_and_none_is_not_inferred(self):
        data = copy.deepcopy(self.data)
        data["loop"] = {"mode": "full"}
        result = self.build_and_analyze(data)
        self.assertEqual(result["loop"]["kind"], "implicit_full_order_cycle")
        self.assertEqual(result["loop"]["position_jumps"], [])

        data["loop"] = {"mode": "none"}
        result = self.build_and_analyze(data)
        self.assertEqual(result["loop"]["kind"], "implicit_full_order_cycle")


if __name__ == "__main__":
    unittest.main()
