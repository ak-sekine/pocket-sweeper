import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import analyze_pd_role_extraction as diagnostic


class RoleDiagnosticTest(unittest.TestCase):
    def test_average_pitch_assigns_high_middle_low(self):
        events = [
            {"part": "high", "pitch": 80, "start": 0, "event_id": "h", "duration": 1},
            {"part": "middle", "pitch": 60, "start": 0, "event_id": "m", "duration": 1},
            {"part": "low", "pitch": 40, "start": 0, "event_id": "l", "duration": 1},
        ]
        roles, ranked = diagnostic.assign_roles(events)
        self.assertEqual(ranked, ["high", "middle", "low"])
        self.assertEqual(roles["melody"][0]["part"], "high")
        self.assertEqual(roles["harmony"][0]["part"], "middle")
        self.assertEqual(roles["bass"][0]["part"], "low")

    def test_contour_is_structural_only(self):
        result = diagnostic.contour([
            {"start": 0, "pitch": 60, "event_id": "a"},
            {"start": 1, "pitch": 60, "event_id": "b"},
            {"start": 2, "pitch": 62, "event_id": "c"},
        ])
        self.assertEqual(result["counts"], {"SAME": 1, "UP": 1})

    def test_role_and_channel_are_separate(self):
        self.assertEqual(diagnostic.CHANNELS["melody"], "pulse1")
        self.assertEqual(diagnostic.CHANNELS["bass"], "wave")
        self.assertEqual(diagnostic.CHANNELS["rhythm"], "noise")


if __name__ == "__main__":
    unittest.main()
