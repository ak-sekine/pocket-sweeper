import unittest
from tools.compare_huge_asm import bytes_from, canonical, comparable, detect_prefix, sections


class CompareHugeAsmTest(unittest.TestCase):
    def test_prefix_and_routine_labels(self):
        self.assertEqual(canonical("song_P0", "song_"), "P0")
        self.assertEqual(canonical("song__hUGE_Routine_0", "song_"), "__hUGE_Routine_0")

    def test_instrument_prefix_is_spelling_only_input(self):
        self.assertEqual(canonical("range_itSquareinst1", "range_"), "itSquareinst1")

    def test_waves_can_be_one_or_many_db_lines(self):
        self.assertEqual(bytes_from(["db $01,$02", "db $03"]), [1, 2, 3])
        self.assertTrue(comparable(["db $01,$02,$03"], ["db 1,2", "db 3"], "wave table"))

    def test_version2_metadata_is_separate(self):
        self.assertIn("loop_metadata", "song_loop_metadata")

    def test_pattern_data_mismatch_is_not_spelling(self):
        self.assertFalse(comparable(["dn C_4,1,$000"], ["dn D_4,1,$000"], "pattern"))


if __name__ == "__main__":
    unittest.main()
