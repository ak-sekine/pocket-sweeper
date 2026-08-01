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
    @staticmethod
    def jump(channel: str, source: int, target: int, row: int = 63) -> dict:
        return {
            "channel": channel,
            "channel_index": analyze_uge.CHANNELS.index(channel),
            "source_order": source,
            "source_row": row,
            "raw_target_order": target + 1,
            "target_order": target,
        }

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
        self.assertEqual(result["loop"]["kind"], "explicit_simple_loop")
        self.assertEqual(result["loop"]["start_order"], 2)
        self.assertEqual(result["loop"]["end_order_inclusive"], 5)
        self.assertEqual(result["loop"]["loop_order_count"], 4)
        self.assertEqual(result["loop"]["unreachable_orders"], [])
        self.assertTrue(all(result["channels"][channel]["used"] for channel in analyze_uge.CHANNELS))

    def test_simple_loop_ends_at_jump_source_before_final_order(self):
        result = analyze_uge.classify_loop([self.jump("ch1", 3, 1)], 6)
        self.assertEqual(result["kind"], "explicit_simple_loop")
        self.assertEqual(result["start_order"], 1)
        self.assertEqual(result["end_order_inclusive"], 3)
        self.assertEqual(result["unreachable_orders"], [4, 5])

    def test_same_jump_across_channels_is_simple(self):
        result = analyze_uge.classify_loop(
            [self.jump("ch1", 3, 1), self.jump("ch2", 3, 1)], 6
        )
        self.assertTrue(result["simple_loop"])
        self.assertTrue(result["channels_agree"])

    def test_different_sources_are_complex(self):
        result = analyze_uge.classify_loop(
            [self.jump("ch1", 3, 1), self.jump("ch2", 4, 1)], 6
        )
        self.assertEqual(result["kind"], "complex_position_jumps")
        self.assertIsNone(result["start_order"])

    def test_different_targets_are_complex(self):
        result = analyze_uge.classify_loop(
            [self.jump("ch1", 3, 1), self.jump("ch1", 3, 2)], 6
        )
        self.assertEqual(result["kind"], "complex_position_jumps")

    def test_forward_and_out_of_range_jumps_are_invalid(self):
        forward = analyze_uge.classify_loop([self.jump("ch1", 1, 2)], 6)
        out_of_range = self.jump("ch1", 3, 6)
        out_of_range["raw_target_order"] = 99
        self.assertEqual(forward["kind"], "invalid_position_jump")
        self.assertEqual(out_of_range["target_order"], 6)
        self.assertEqual(
            analyze_uge.classify_loop([out_of_range], 6)["kind"],
            "invalid_position_jump",
        )

    def test_repeated_same_jump_is_simple_and_no_jump_is_implicit(self):
        jumps = [self.jump("ch1", 3, 1), self.jump("ch1", 3, 1)]
        self.assertEqual(analyze_uge.classify_loop(jumps, 6)["kind"], "explicit_simple_loop")
        implicit = analyze_uge.classify_loop([], 1)
        self.assertEqual(implicit["kind"], "implicit_full_order_cycle")
        self.assertEqual(implicit["loop_order_count"], 1)

    def test_missing_pattern_reference_is_contextual_error(self):
        source = ROOT / "assets" / "bgm_v2_workflow_check.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        raw = bytearray(json_to_uge.build_uge(data))
        pattern_count_offset = 4 + 3 * 256 + 45 * 1385 + 512 + 4 + 1 + 4
        pattern_count = int.from_bytes(raw[pattern_count_offset:pattern_count_offset + 4], "little", signed=True)
        order_offset = pattern_count_offset + 4 + pattern_count * (4 + 64 * 17)
        raw[order_offset + 4:order_offset + 8] = (999999).to_bytes(4, "little", signed=True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.uge"
            path.write_bytes(raw)
            with self.assertRaisesRegex(analyze_uge.UgeError, r"ch1 order 0.*missing pattern 999999"):
                analyze_uge.read_file(path)

    def test_unknown_version_and_truncated_file_fail(self):
        source = ROOT / "assets" / "bgm_v2_workflow_check.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        raw = json_to_uge.build_uge(data)
        with tempfile.TemporaryDirectory() as directory:
            unknown = Path(directory) / "unknown.uge"
            unknown.write_bytes((7).to_bytes(4, "little", signed=True) + raw[4:])
            with self.assertRaisesRegex(analyze_uge.UgeError, "unsupported Song Version 7"):
                analyze_uge.read_file(unknown)
            truncated = Path(directory) / "truncated.uge"
            truncated.write_bytes(raw[:-1])
            with self.assertRaises(analyze_uge.UgeError):
                analyze_uge.read_file(truncated)


if __name__ == "__main__":
    unittest.main()
