import unittest
from tools.analyze_pd_pitch_melody_diagnostic import note_name

class PitchDiagnosticTest(unittest.TestCase):
    def test_note_name_and_intervals(self):
        self.assertEqual(note_name(60), "C4")
        self.assertEqual(note_name(61), "C#4")
        self.assertEqual(64 - 60, 4)

if __name__ == "__main__": unittest.main()
