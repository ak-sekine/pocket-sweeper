import unittest

from tools.analyze_pd_tempo_diagnostic import bpm_from_us_per_quarter, runtime_row_seconds, tick_seconds


class TempoDiagnosticTest(unittest.TestCase):
    def test_source_time_units(self):
        self.assertEqual(bpm_from_us_per_quarter(500000), 120)
        self.assertAlmostEqual(tick_seconds(384, 384, 500000), 0.5)
        self.assertAlmostEqual(runtime_row_seconds(6), 0.1)

    def test_source_grid_and_pattern_duration(self):
        source_grid = 30 * 500000 / 1_000_000 / 384
        self.assertAlmostEqual(source_grid, 0.0390625)
        self.assertAlmostEqual(64 * runtime_row_seconds(6), 6.4)


if __name__ == "__main__":
    unittest.main()
