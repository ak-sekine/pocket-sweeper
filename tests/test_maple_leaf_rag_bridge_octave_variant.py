import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import json_to_uge  # noqa: E402
import analyze_uge  # noqa: E402


BRIDGE = {
    375: ("G#4", "G#5"),
    383: ("G#4", "G#5"),
    390: ("B4", "B5"),
    398: ("G#5", "G#6"),
    405: ("G#4", "G#5"),
    413: ("G#5", "G#6"),
    420: ("B5", "B6"),
    428: ("G#5", "G#6"),
    435: ("G#4", "G#5"),
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expanded_channel(data):
    rows = []
    starts = []
    row = 0
    for pattern_name in data["order"]["pulse1"]:
        pattern = json_to_uge.build_channel_pattern(
            data["patterns"]["pulse1"][pattern_name],
            f"patterns.pulse1.{pattern_name}",
            version=2,
            channel="pulse1",
        )
        for cell in pattern:
            if cell.note != json_to_uge.NO_NOTE:
                starts.append((row, cell.note))
            rows.append(cell)
            row += 1
    return rows, starts


class MapleLeafRagBridgeOctaveVariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load_json(
            ROOT / "assets/maple_leaf_rag_16bars_melody.json"
        )
        cls.variant = load_json(
            ROOT / "assets/maple_leaf_rag_16bars_melody_bridge_octave_up.json"
        )
        cls.original_rows, cls.original_starts = expanded_channel(cls.original)
        cls.variant_rows, cls.variant_starts = expanded_channel(cls.variant)

    def test_only_bridge_pitch_labels_change_by_one_octave(self):
        self.assertEqual(len(self.original_starts), 87)
        self.assertEqual(len(self.variant_starts), 87)
        self.assertEqual(len(self.original_rows), 960)
        self.assertEqual(len(self.variant_rows), 960)
        self.assertEqual(self.original["order"], self.variant["order"])
        self.assertEqual(self.original["tempo"], self.variant["tempo"])
        self.assertEqual(self.original["loop"], self.variant["loop"])
        self.assertEqual(self.original["instruments"], self.variant["instruments"])

        original_sequence = dict(self.original_starts)
        variant_sequence = dict(self.variant_starts)
        self.assertEqual(original_sequence.keys(), variant_sequence.keys())
        for row, original_note in original_sequence.items():
            if row in BRIDGE:
                expected_original, expected_variant = BRIDGE[row]
                self.assertEqual(original_note, json_to_uge.parse_note(expected_original, "test"))
                self.assertEqual(
                    variant_sequence[row],
                    json_to_uge.parse_note(expected_variant, "test"),
                )
            else:
                self.assertEqual(variant_sequence[row], original_note)

        for row, (before, after) in BRIDGE.items():
            self.assertEqual(
                json_to_uge.parse_note(after, "test")
                - json_to_uge.parse_note(before, "test"),
                12,
            )

    def test_order_timing_cuts_rests_and_repeat_articulation_are_preserved(self):
        self.assertEqual(self.variant_rows, [
            cell if row not in BRIDGE else json_to_uge.Cell(
                note=json_to_uge.parse_note(BRIDGE[row][1], "test"),
                instrument=cell.instrument,
                volume=cell.volume,
                effect_code=cell.effect_code,
                effect_param=cell.effect_param,
            )
            for row, cell in enumerate(self.original_rows)
        ])
        cut_rows = [
            row for row, cell in enumerate(self.variant_rows)
            if cell.effect_code == 0xE and cell.effect_param == 0
        ]
        self.assertEqual(len(cut_rows), 22)
        self.assertTrue({382, 442, 494, 509, 524, 539, 547, 749, 764, 779, 787}.issubset(cut_rows))
        self.assertEqual(len(self.variant_starts), 87)

    def test_bridge_apu_frequencies_match_the_standard_midi_pitches_in_variant(self):
        labels = {
            match.group(1).replace("_", ""): int(match.group(2))
            for match in re.finditer(
                r"^DEF ([A-G](?:#|_)?\d) EQU (\d+)$",
                (ROOT / "include/hUGE.inc").read_text(encoding="utf-8"),
                re.MULTILINE,
            )
        }
        periods = [
            int(match.group(1))
            for match in re.finditer(
                r"^dw (\d+)$",
                (ROOT / "include/hUGE_note_table.inc").read_text(encoding="utf-8"),
                re.MULTILINE,
            )
        ]

        def pulse_frequency(note):
            period = periods[labels[note]]
            return 131072 / (2048 - period)

        midi = {"G#4": 415.3047, "B4": 493.8833, "G#5": 830.6094, "B5": 987.7666}
        for before, after in BRIDGE.values():
            target = midi[before]
            self.assertAlmostEqual(pulse_frequency(before) * 2, target, delta=2.5)
            self.assertAlmostEqual(pulse_frequency(after), target, delta=2.5)

    def test_saved_uge_changes_only_bridge_pitch_cells(self):
        original = analyze_uge.read_file(
            ROOT / "assets/maple_leaf_rag_16bars_melody.uge"
        )
        variant = analyze_uge.read_file(
            ROOT / "assets/maple_leaf_rag_16bars_melody_bridge_octave_up.uge"
        )
        self.assertEqual(original["tempo_raw"], variant["tempo_raw"])

        for channel_index, channel in enumerate(analyze_uge.CHANNELS):
            original_orders = original["channels"][channel]["order_pattern_keys"]
            variant_orders = variant["channels"][channel]["order_pattern_keys"]
            self.assertEqual(original_orders, variant_orders)
            for row in range(960):
                order_index, local_row = divmod(row, 64)
                original_pattern = original_orders[order_index]
                variant_pattern = variant_orders[order_index]
                before = original["pattern_cells"][str(original_pattern)][local_row]
                after = variant["pattern_cells"][str(variant_pattern)][local_row]
                if channel_index == 0 and row in BRIDGE:
                    self.assertEqual(after[0] - before[0], 12)
                    self.assertEqual(after[1:], before[1:])
                else:
                    self.assertEqual(after, before, (channel, row))


if __name__ == "__main__":
    unittest.main()
