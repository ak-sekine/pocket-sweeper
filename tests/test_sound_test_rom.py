import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_sound_test_rom  # noqa: E402
import json_to_huge_asm  # noqa: E402
import json_to_uge  # noqa: E402


class SoundTestRomTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((ROOT / "assets" / name).read_text(encoding="utf-8"))

    def test_v2_none_main_uses_sound_manager_and_remains_interactive(self) -> None:
        source = ROOT / "obj" / "bgm_v2_loop_none_manual_test.asm"
        main = build_sound_test_rom.generate_main_asm(
            source,
            build_sound_test_rom.parse_song_label(source),
            2,
            2,
            ROOT / "obj" / "se_cursor_sfx.asm",
        )
        self.assertIn("call Sound_PlayBgmV2", main)
        self.assertIn("call Sound_Update", main)
        self.assertIn("call Sound_PlaySfx", main)
        self.assertIn("SoundTest_AButtonPressed:", main)
        self.assertIn("SoundTestScreenSfxFinished:", main)
        self.assertNotIn("ldh [rAUDENA], a\n.finished_loop:", main)

    def test_manual_test_patterns_are_64_rows(self) -> None:
        for filename in (
            "bgm_v2_loop_full_manual_test.json",
            "bgm_v2_loop_range_manual_test.json",
            "bgm_v2_loop_none_manual_test.json",
        ):
            data = self.load(filename)
            asm = json_to_huge_asm.build_asm(data, "song")
            lines = asm.splitlines()
            pattern_labels = [line for line in lines if line.startswith("song_P") and line.endswith(":")]
            self.assertGreaterEqual(len(pattern_labels), 3)
            for index, label in enumerate(pattern_labels):
                start = lines.index(label) + 1
                end = lines.index(pattern_labels[index + 1]) if index + 1 < len(pattern_labels) else lines.index("song_duty_instruments:")
                self.assertEqual(len([line for line in lines[start:end] if line.startswith(" dn ")]), 64)

    def test_manual_test_metadata_modes(self) -> None:
        expected = {
            "bgm_v2_loop_full_manual_test.json": "song_loop_metadata: db 0,2,63",
            "bgm_v2_loop_range_manual_test.json": "song_loop_metadata: db 1,2,63",
            "bgm_v2_loop_none_manual_test.json": "song_loop_metadata: db 2,2,63",
        }
        for filename, metadata in expected.items():
            asm = json_to_huge_asm.build_asm(self.load(filename), "song")
            self.assertIn(metadata, asm)


if __name__ == "__main__":
    unittest.main()
