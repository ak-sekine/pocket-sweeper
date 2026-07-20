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
        self.assertIn("ld bc, 32 * 3", main)
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

    def test_ch4_audibility_fixture_has_loud_noise_and_nonrest_notes(self) -> None:
        data = self.load("bgm_v2_ch4_mute_audibility_test.json")
        noise_instrument = json_to_uge.validate_instruments(data)["noise"][4]
        self.assertEqual(noise_instrument.initial_volume, 15)
        noise_patterns = data["patterns"]["noise"]
        notes = [event["note"] for pattern in noise_patterns.values() for event in pattern]
        self.assertIn("C4", notes)
        self.assertIn("G4", notes)
        self.assertIn("rest", notes)
        self.assertTrue(any(note != "rest" for note in notes))

        for note in ("C4", "G4"):
            note_number = json_to_uge.parse_note(note, f"test.{note}")
            nr43 = json_to_uge.noise_note_to_nr43(note_number, noise_instrument)
            self.assertNotEqual(nr43, 0)
            self.assertEqual(nr43 & 0x08, 0)

        asm = json_to_huge_asm.build_asm(data, "ch4_audibility")
        self.assertIn("ch4_audibility_P6:", asm)
        self.assertIn("dn C_4,4,$000", asm)
        self.assertIn("dn G_4,4,$000", asm)
        self.assertIn("ch4_audibility_itNoiseinst4:\ndb 240", asm)


if __name__ == "__main__":
    unittest.main()
