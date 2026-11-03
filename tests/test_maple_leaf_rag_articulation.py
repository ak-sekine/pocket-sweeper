import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import json_to_uge  # noqa: E402


class MapleLeafRagRepeatedNoteArticulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "assets" / "maple_leaf_rag_16bars_melody.json").read_text(
                encoding="utf-8"
            )
        )
        cls.rows = []
        cls.note_starts = []
        cls.cuts = []
        for pattern_name in cls.data["order"]["pulse1"]:
            pattern = json_to_uge.build_channel_pattern(
                cls.data["patterns"]["pulse1"][pattern_name],
                f"patterns.pulse1.{pattern_name}",
                version=2,
                channel="pulse1",
            )
            for cell in pattern:
                absolute_row = len(cls.rows)
                cls.rows.append(cell)
                if cell.note != json_to_uge.NO_NOTE:
                    cls.note_starts.append((absolute_row, cell.note))
                if cell.effect_code == 0xE and cell.effect_param == 0:
                    cls.cuts.append(absolute_row)

    def test_all_87_pitch_onsets_remain_and_repeated_notes_have_one_row_cuts(self):
        repeated_note_pairs = [
            (375, 383, "G#4"),
            (435, 443, "G#4"),
            (488, 495, "G#6"),
            (495, 510, "G#6"),
            (510, 525, "G#6"),
            (525, 540, "G#6"),
            (540, 548, "G#6"),
            (728, 750, "G#5"),
            (750, 765, "G#5"),
            (765, 780, "G#5"),
            (780, 788, "G#5"),
        ]
        self.assertEqual(len(self.note_starts), 87)

        for first_row, next_row, pitch in repeated_note_pairs:
            with self.subTest(first_row=first_row, next_row=next_row, pitch=pitch):
                expected_note = json_to_uge.parse_note(pitch, "test.note")
                self.assertIn((first_row, expected_note), self.note_starts)
                self.assertIn((next_row, expected_note), self.note_starts)
                self.assertIn(next_row - 1, self.cuts)

    def test_full_pitch_order_and_onset_sequence_matches_the_original_json(self):
        sequence = []
        for order_index, pattern_name in enumerate(self.data["order"]["pulse1"]):
            row = 0
            for event in self.data["patterns"]["pulse1"][pattern_name]:
                if event["note"] not in {"rest", "hold"}:
                    sequence.append([order_index * 64 + row, event["note"]])
                row += event["length"]
        digest = hashlib.sha256(
            json.dumps(sequence, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(len(sequence), 87)
        self.assertEqual(
            digest,
            "cbfb19a04425e0af3071c55d40db88835a40c9e6a4cbfcbd471af58c592a5088",
        )

    def test_cuts_are_on_the_correct_side_of_pattern_order_boundaries(self):
        # The notes starting at rows 510 and 765 continue across order edges.
        # Their cuts must be in the following patterns at rows 524 and 779.
        self.assertEqual(self.rows[524].effect_code, 0xE)
        self.assertEqual(self.rows[779].effect_code, 0xE)
        self.assertEqual(len(self.cuts), 22)  # 10 MIDI rests + lead-in + 11 articulations
        self.assertEqual(len(self.rows), 960)
        self.assertEqual((self.rows[0].effect_code, self.rows[0].effect_param), (0xE, 0))

    def test_bridge_nine_notes_remain_at_their_original_rows_and_pitches(self):
        bridge = [
            (375, "G#4"),
            (383, "G#4"),
            (390, "B4"),
            (398, "G#5"),
            (405, "G#4"),
            (413, "G#5"),
            (420, "B5"),
            (428, "G#5"),
            (435, "G#4"),
        ]
        expected = [
            (row, json_to_uge.parse_note(note, "test.note"))
            for row, note in bridge
        ]
        self.assertTrue(all(event in self.note_starts for event in expected))


if __name__ == "__main__":
    unittest.main()
