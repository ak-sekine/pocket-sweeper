import struct
import unittest
from pathlib import Path

from tools.generate_pulse_chase_midi import BAR, BARS, PPQ, make_midi, make_notes


class PulseChaseMidiTest(unittest.TestCase):
    @staticmethod
    def _event_statuses(data):
        pos = 14
        while pos < len(data):
            length = int.from_bytes(data[pos + 4:pos + 8], "big")
            track = data[pos + 8:pos + 8 + length]
            pos += 8 + length
            i = 0
            running = None
            while i < len(track):
                while True:
                    byte = track[i]
                    i += 1
                    if byte < 128:
                        break
                status = track[i]
                if status < 128:
                    status = running
                else:
                    i += 1
                    running = status
                yield status
                if status == 0xFF:
                    i += 1
                    i += track[i] + 1
                elif status & 0xF0 in (0xC0, 0xD0):
                    i += 1
                else:
                    i += 2

    def test_three_melody_sections_and_turnaround(self):
        notes = make_notes()["melody"]
        sections = [
            [n for n in notes if start <= n[0] < start + 8 * BAR]
            for start in (0, 8 * BAR, 16 * BAR)
        ]
        self.assertNotEqual([(n[0], n[1]) for n in sections[0]], [(n[0], n[1]) for n in sections[1]])
        self.assertNotEqual([(n[0], n[1]) for n in sections[1]], [(n[0], n[1]) for n in sections[2]])
        self.assertNotEqual([(n[0], n[1]) for n in sections[0]], [(n[0], n[1]) for n in sections[2]])
        self.assertLess(sum(n[1] for n in sections[2]) / len(sections[2]), sum(n[1] for n in sections[1]) / len(sections[1]))
        self.assertLess(len(sections[2]), len(sections[0]))
        self.assertEqual(sections[2][-1][1], 79)  # final G returns toward loop head

    def test_bass_has_explicit_loop_return(self):
        bass = make_notes()["bass"]
        final = [n for n in bass if 23 * BAR <= n[0] < BARS * BAR]
        self.assertEqual([(n[1], n[0] - 23 * BAR) for n in final], [(38, 0), (42, 2 * 240), (45, 4 * 240), (43, 6 * 240)])
        self.assertLessEqual(max(n[0] + n[2] for n in bass), BARS * BAR)

    def test_bright_major_center_is_present_in_melody_and_bass(self):
        notes = make_notes()
        melody_pitches = {pitch % 12 for _, pitch, _, _ in notes["melody"]}
        bass_pitches = {pitch % 12 for _, pitch, _, _ in notes["bass"]}
        self.assertTrue({7, 11, 2}.issubset(melody_pitches))  # G, B, D
        self.assertTrue({7, 11, 2}.issubset(bass_pitches))

    def test_note_ranges_are_monophonic_and_within_loop(self):
        parts = make_notes()
        for name, events in parts.items():
            if name == "rhythm":
                continue  # kick/snare may share a drum beat on CH4.
            for left, right in zip(sorted(events), sorted(events)[1:]):
                self.assertLessEqual(left[0] + left[2], right[0])
            self.assertLessEqual(max(start + duration for start, _, duration, _ in events), BARS * BAR)
        boundaries = sorted({0, *[start for events in parts.values() for start, _, _, _ in events], BARS * BAR})
        maximum = 0
        for start, end in zip(boundaries, boundaries[1:]):
            active = sum(any(note_start <= start < note_start + duration for note_start, _, duration, _ in events) for events in parts.values())
            maximum = max(maximum, active)
        self.assertLessEqual(maximum, 4)

    def test_midi_header_tracks_and_restrictions(self):
        data = make_midi()
        self.assertEqual(data[:4], b"MThd")
        self.assertEqual(struct.unpack(">IHHH", data[4:14]), (6, 1, 5, PPQ))
        self.assertEqual(data.count(b"\xff\x51\x03"), 1)
        self.assertEqual(data.count(b"\xff\x58\x04"), 1)
        statuses = list(self._event_statuses(data))
        self.assertFalse(any(status & 0xF0 in (0xA0, 0xD0, 0xE0) for status in statuses))
        self.assertFalse(any(status == 0xB0 for status in statuses))

    def test_generated_asset_matches_generator(self):
        asset = Path(__file__).parents[1] / "assets/pulse_chase.mid"
        self.assertEqual(asset.read_bytes(), make_midi())


if __name__ == "__main__":
    unittest.main()
