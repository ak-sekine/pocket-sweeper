import json
import re
import unittest
from pathlib import Path

from tools import json_to_uge
from tools.generate_pulse_chase_midi import BAR, make_notes


ROOT = Path(__file__).parents[1]
JSON_PATH = ROOT / "assets/bgm_pulse_chase.json"
ORDER = ["section0_a", "section0_b", "section1_a", "section1_b", "section2_a", "section2_b"]
CHANNELS = ("pulse1", "pulse2", "wave", "noise")
MIDI_PARTS = {"pulse1": "melody", "pulse2": "support", "wave": "bass", "noise": "rhythm"}
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def midi_name(pitch: int) -> str:
    return NOTE_NAMES[pitch % 12] + str(pitch // 12 - 1)


def json_events(data: dict, channel: str) -> list[tuple[int, str, int, int]]:
    events = []
    for order_index, pattern_name in enumerate(ORDER):
        row = order_index * 64
        for item in data["patterns"][channel][pattern_name]:
            if item["note"] != "rest":
                events.append((row, item["note"], item["length"], item["instrument"]))
            row += item["length"]
    return events


def expected_events(part: str) -> list[tuple[int, str, int, int]]:
    events = []
    for start, pitch, duration, velocity in make_notes()[part]:
        row = round(start / 120)
        length = max(1, round(duration / 120))
        if part == "bass":
            pitch += 12
        if part == "rhythm":
            note_and_instrument = {36: ("C3", 1), 38: ("C5", 2), 42: ("C7", 3)}
            note, instrument = note_and_instrument[pitch]
        else:
            note = midi_name(pitch)
            instrument = {"melody": 1, "support": 2, "bass": 1}[part]
        events.append((row, note, length, instrument))
    if part == "rhythm":
        # CH4 has one cell per row. Preserve kick/snare on their source row;
        # evacuate a colliding hat by at most one row within its pattern.
        selected = {}
        for event in sorted(events):
            if event[3] in (1, 2):
                selected[event[0]] = min(selected.get(event[0], event), event, key=lambda item: item[3])
        for event in sorted(events):
            if event[3] != 3:
                continue
            row = event[0]
            if row not in selected:
                selected[row] = event
            elif row + 1 < (row // 64 + 1) * 64 and row + 1 not in selected:
                selected[row + 1] = (row + 1, event[1], event[2], event[3])
        events = list(selected.values())
    return sorted(events)


class PulseChaseJsonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    def test_header_and_existing_version2_validator(self):
        self.assertEqual({key: self.data[key] for key in ("version", "title", "type", "tempo")}, {"version": 2, "title": "Pulse Chase", "type": "bgm", "tempo": 6})
        self.assertEqual(self.data["loop"], {"mode": "full"})
        # build_uge exercises the existing Version 2 schema/instrument,
        # pattern, wave-table, note, and loop validation without writing UGE.
        json_to_uge.build_uge(self.data)

    def test_orders_patterns_and_64row_sections(self):
        for channel in CHANNELS:
            self.assertEqual(self.data["order"][channel], ORDER)
            self.assertEqual(set(self.data["patterns"][channel]), set(ORDER))
            for pattern in self.data["patterns"][channel].values():
                self.assertEqual(sum(note["length"] for note in pattern), 64)
        self.assertEqual(sum(sum(note["length"] for note in pattern) for pattern in self.data["patterns"]["pulse1"].values()), 384)

    def test_instruments_and_triangle_wave_table(self):
        instruments = {(item["channel"], item["id"]): item for item in self.data["instruments"]}
        self.assertEqual(instruments[("pulse1", 1)]["duty"], 2)
        self.assertEqual(instruments[("pulse1", 1)]["initial_volume"], 12)
        self.assertEqual(instruments[("pulse1", 1)]["envelope_direction"], "down")
        self.assertEqual(instruments[("pulse1", 1)]["envelope_sweep"], 0)
        self.assertEqual(instruments[("pulse1", 1)]["sweep_time"], 0)
        self.assertEqual(instruments[("pulse2", 2)]["duty"], 1)
        self.assertEqual(instruments[("pulse2", 2)]["initial_volume"], 7)
        wave = instruments[("wave", 1)]
        self.assertEqual((wave["waveform"], wave["output_level"]), ("workflow_triangle", "100%"))
        wave_table = next(table for table in self.data["wave_tables"] if table["name"] == "workflow_triangle")
        self.assertEqual(len(wave_table["samples"]), 32)
        self.assertTrue(all(0 <= sample <= 15 for sample in wave_table["samples"]))
        self.assertEqual(wave["waveform"], wave_table["name"])
        for number, name, volume, width in ((1, "kick", 6, "15bit"), (2, "snare", 5, "7bit"), (3, "hat", 4, "7bit")):
            noise = instruments[("noise", number)]
            self.assertIn(name, noise["name"])
            self.assertEqual((noise["initial_volume"], noise["width_mode"], noise["envelope_direction"], noise["envelope_sweep"]), (volume, width, "down", 0))

    def test_note_fields_and_noise_rest_volume_rule(self):
        for channel in CHANNELS:
            valid_instruments = {
                item["id"] for item in self.data["instruments"]
                if item["channel"] in (("pulse1", "pulse2") if channel in ("pulse1", "pulse2") else (channel,))
            }
            for pattern in self.data["patterns"][channel].values():
                for item in pattern:
                    self.assertIsInstance(item["length"], int)
                    self.assertGreater(item["length"], 0)
                    json_to_uge.parse_note(item["note"], "pulse_chase")
                    self.assertIn(item["instrument"], valid_instruments)
                    if "volume" in item:
                        self.assertIn(item["volume"], range(16))
                    self.assertIsNone(item.get("effect"))
                    self.assertIsNone(item.get("effect_param"))
                    if channel == "noise" and item["note"] == "rest":
                        self.assertNotIn("volume", item)

    def test_melody_matches_quantized_midi_and_support_is_gb_safe(self):
        actual = [(row, note, length, instrument) for row, note, length, instrument in json_events(self.data, "pulse1")]
        self.assertEqual(actual, expected_events("melody"))
        support = json_events(self.data, "pulse2")
        self.assertEqual(len(support), 45)
        self.assertTrue(all(note in {"D4", "B3", "A3", "F#3", "G3", "E3"} for _, note, _, _ in support))
        self.assertNotIn("G#3", [note for _, note, _, _ in support])
        melody_notes = [event[1] for event in json_events(self.data, "pulse1")]
        support_notes = [event[1] for event in json_events(self.data, "pulse2")]
        self.assertNotEqual(melody_notes, support_notes)

    def test_melody_sections_have_distinct_structure(self):
        sections = []
        events = json_events(self.data, "pulse1")
        for start in (0, 128, 256):
            section = [(row - start, note) for row, note, _, _ in events if start <= row < start + 128]
            sections.append(section)
        self.assertNotEqual(sections[0], sections[1])
        self.assertNotEqual(sections[1], sections[2])
        self.assertNotEqual(sections[0], sections[2])
        self.assertGreater(sum(self._pitch(note) for _, note in sections[1]) / len(sections[1]), sum(self._pitch(note) for _, note in sections[0]) / len(sections[0]))
        self.assertLess(len(sections[2]), len(sections[0]))

    def test_bass_octave_and_loop_cadence_match_midi(self):
        self.assertEqual(json_events(self.data, "wave"), expected_events("bass"))
        final = [(row - 320, note) for row, note, _, _ in json_events(self.data, "wave") if row >= 320]
        self.assertEqual([note for _, note in final[-4:]], ["D3", "F#3", "A3", "G3"])
        self.assertLessEqual(max(row + length for row, _, length, _ in json_events(self.data, "wave")), 384)

    def test_known_gsharp_issue_matches_midi_without_approving_harmony(self):
        midi_gsharp = [pitch for _, pitch, _, _ in make_notes()["support"] if pitch == 56]
        json_gsharp = [note for _, note, _, _ in json_events(self.data, "pulse2") if note == "G#3"]
        self.assertEqual(len(midi_gsharp), 6)
        self.assertEqual(len(json_gsharp), 0)
        # The approved MIDI retains the known issue; the GB arrangement resolves it.
        self.assertNotIn("G#3", [note for _, note, _, _ in json_events(self.data, "pulse2")])

    def test_noise_is_a_sparse_gb_arrangement_of_midi_rhythm(self):
        actual = json_events(self.data, "noise")
        self.assertEqual(len(actual), 51)
        self.assertEqual(sum(instrument == 1 for _, _, _, instrument in actual), 24)
        self.assertEqual(sum(instrument == 2 for _, _, _, instrument in actual), 24)
        self.assertEqual(sum(instrument == 3 for _, _, _, instrument in actual), 3)
        self.assertEqual([row for row, _, _, _ in actual if row % 16 == 0], list(range(0, 384, 16)))
        self.assertTrue(all(note == "C3" for _, note, _, instrument in actual if instrument == 1))
        self.assertTrue(all(note == "C5" for _, note, _, instrument in actual if instrument == 2))
        self.assertTrue(all(note == "C7" for _, note, _, instrument in actual if instrument == 3))
        self.assertLess(len(actual), 144)

    def test_noise_hats_are_retained_in_each_eight_bar_section(self):
        hats = [(row, note, instrument) for row, note, _, instrument in json_events(self.data, "noise") if instrument == 3]
        self.assertGreater(len(hats), 0)
        self.assertTrue(all(note == "C7" for _, note, _ in hats))
        self.assertTrue(all(any(start <= row < start + 128 for row, _, _ in hats) for start in (0, 128, 256)))
        source_rows = [round(start / 120) for start, pitch, _, _ in make_notes()["rhythm"] if pitch == 42]
        self.assertEqual(len(hats), 3)
        actual_rows = sorted(row for row, _, _ in hats)
        self.assertEqual(actual_rows, [5, 133, 261])
        self.assertTrue(all(actual - source in (0, 1) for actual, source in zip(actual_rows, [4, 132, 260])))

    def test_noise_kick_and_snare_rows_remain_on_midi_rows(self):
        actual = json_events(self.data, "noise")
        for pitch, instrument, modulo in ((36, 1, 0), (38, 2, 12)):
            expected_rows = [row for row in range(0, 384) if row % 16 == modulo]
            actual_rows = sorted(row for row, _, _, inst in actual if inst == instrument)
            self.assertEqual(actual_rows, expected_rows)

    @staticmethod
    def _pitch(note: str) -> int:
        match = re.match(r"([A-G]#?)(\d)", note)
        return int(match.group(2)) * 12 + NOTE_NAMES.index(match.group(1))


if __name__ == "__main__":
    unittest.main()
