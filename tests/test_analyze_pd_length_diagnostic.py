import unittest

from tools.analyze_pd_length_diagnostic import token_metrics


class LengthDiagnosticTest(unittest.TestCase):
    def test_token_range_and_pattern_boundary(self):
        result = token_metrics([
            {"note": "C4", "length": 6},
            {"note": "rest", "length": 58},
        ])
        self.assertEqual(result["note_count"], 1)
        self.assertEqual(result["first_note_row"], 0)
        self.assertEqual(result["last_token_end_row"], 64)

    def test_empty_pattern(self):
        result = token_metrics([{"note": "rest", "length": 64}])
        self.assertEqual(result["note_count"], 0)
        self.assertIsNone(result["first_note_row"])


if __name__ == "__main__":
    unittest.main()
