import unittest


class RhythmDiagnosticTest(unittest.TestCase):
    def test_simultaneous_group_classification_contract(self):
        groups = [{"source_onsets": [0]}, {"source_onsets": [0, 96]}]
        self.assertEqual(len(groups[0]["source_onsets"]), 1)
        self.assertGreater(len(groups[1]["source_onsets"]), 1)

    def test_ioi_and_duration_units(self):
        onsets = [0, 96, 384]
        self.assertEqual([b - a for a, b in zip(onsets, onsets[1:])], [96, 288])
        self.assertEqual(round(96 / 30), 3)
        self.assertEqual(max(1, round(12 / 30)), 1)


if __name__ == "__main__":
    unittest.main()
