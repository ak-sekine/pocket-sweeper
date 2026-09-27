import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import analyze_pd_reduction as diagnostic


class ReductionDiagnosticTest(unittest.TestCase):
    def test_quantization_and_shift(self):
        self.assertEqual(diagnostic.quantize(30), 1)
        self.assertEqual(diagnostic.quantize(16), 1)
        self.assertEqual(diagnostic.shift_pitch(36, "wave"), (48, 12, True))
        self.assertEqual(diagnostic.shift_pitch(84, "wave"), (72, -12, True))

    def test_collision_classes(self):
        self.assertEqual(diagnostic.collision_class([{"normalized_onset": 0}, {"normalized_onset": 0}]), "PREEXISTING_SIMULTANEOUS")
        self.assertEqual(diagnostic.collision_class([{"normalized_onset": 0}, {"normalized_onset": 1}]), "QUANTIZATION_INDUCED")

    def test_selection_is_deterministic(self):
        members = [{"source_event_id": "a"}, {"source_event_id": "b"}]
        self.assertEqual(members[0]["source_event_id"], "a")
        self.assertEqual(diagnostic.CHANNELS["melody"], "pulse1")


if __name__ == "__main__":
    unittest.main()
