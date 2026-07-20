import tempfile
import unittest
from pathlib import Path

from tools import build_sound_test_rom


ROOT = Path(__file__).resolve().parents[1]


def routine(source: str, start: str, end: str) -> str:
    return source[source.index(start) : source.index(end)]


class SoundRuntimeModel:
    """Instruction-level constraints cannot be executed here; model the specified state transitions."""

    def __init__(self) -> None:
        self.playback_active = True
        self.sfx_active = False
        self.sfx_frames = 0
        self.sfx_channel = 3
        self.muted = set()
        self.silenced = set()
        self.dosound_calls = 0
        self.sfx_update_calls = 0

    def play_sfx(self, frames: int = 2) -> bool:
        if self.sfx_active:
            return False
        self.sfx_active = True
        self.sfx_frames = frames
        self.muted.add(self.sfx_channel)
        return True

    def update(self, bgm_finished: bool = False) -> None:
        if self.playback_active:
            self.dosound_calls += 1
            if bgm_finished:
                self.playback_active = False
                self.silenced.update({0, 1, 2, 3} - ({self.sfx_channel} if self.sfx_active else set()))
                self.muted.update(self.silenced)
        self.sfx_update_calls += 1
        if self.sfx_active:
            self.sfx_frames -= 1
            if self.sfx_frames == 0:
                self.sfx_active = False
                self.muted.discard(self.sfx_channel)


class BuildSoundTestRomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sound = (ROOT / "src" / "sound.asm").read_text(encoding="utf-8")

    def test_finished_bgm_falls_through_to_sfx_without_another_dosound(self) -> None:
        update = routine(self.sound, "Sound_Update::", "Sound_SilenceFinishedBgmChannels:")
        self.assertLess(update.index("call hUGE_dosound"), update.index("call hUGE_bgm_finished"))
        self.assertLess(update.index("ld [wSoundPlaybackActive], a"), update.index(".updateSfx:"))
        self.assertIn("jp Sound_UpdateSfx", update)

        model = SoundRuntimeModel()
        model.update(bgm_finished=True)
        calls_at_finish = model.dosound_calls
        model.update()
        model.update()
        self.assertEqual(model.dosound_calls, calls_at_finish)
        self.assertEqual(model.sfx_update_calls, 3)

    def test_bgm_finish_event_is_one_shot_and_separate_from_sfx_state(self) -> None:
        update = routine(self.sound, "Sound_Update::", "Sound_SilenceFinishedBgmChannels:")
        take = routine(
            self.sound, "Sound_TakeBgmFinishedEvent::", "Sound_SilenceFinishedBgmChannel:"
        )
        self.assertIn("ld [wSoundBgmFinishedEvent], a", update)
        self.assertIn("ld a, [wSoundBgmFinishedEvent]", take)
        self.assertIn("ld [wSoundBgmFinishedEvent], a", take)
        self.assertNotIn("wSoundSfxActive", take)

    def test_screen_data_uses_32_tile_stride_and_clears_three_rows(self) -> None:
        screens = (
            ("BGM PLAYING",),
            ("BGM FINISHED", "A: PLAY SFX", "READY"),
            ("SFX PLAYING",),
            ("SFX FINISHED", "UNMUTE COMPLETE"),
            ("READY",),
        )
        for lines in screens:
            data = build_sound_test_rom._screen_data(*lines)
            self.assertEqual(len(data), 32 * 3)
            for row in range(3):
                expected = lines[row] if row < len(lines) else ""
                start = row * 32
                self.assertEqual(bytes(data[start : start + len(expected)]).decode(), expected)
                self.assertEqual(data[start + len(expected) : start + 32], [ord(" ")] * (32 - len(expected)))

    def test_screen_rejects_text_beyond_visible_width(self) -> None:
        with self.assertRaisesRegex(ValueError, "exceeds 20 visible tiles"):
            build_sound_test_rom._screen_data("X" * 21)

    def test_font_contains_visible_h_glyph(self) -> None:
        self.assertIn("H", build_sound_test_rom.FONT_5X7)
        tiles = build_sound_test_rom._font_tile_data()
        h_tile = tiles[ord("H") * 16 : (ord("H") + 1) * 16]
        self.assertNotEqual(h_tile, [0] * 16)
        self.assertEqual(h_tile[6:8], [0x7C, 0x7C])

    def test_sfx_mute_direct_apu_update_and_unmute_paths(self) -> None:
        play = routine(self.sound, "Sound_PlaySfx::", "Sound_Update::")
        update = routine(self.sound, "Sound_UpdateSfx:", "Sound_StopSfx:")
        stop = self.sound[self.sound.index("Sound_StopSfx:") :]
        self.assertIn("jp hUGE_mute_channel", play)
        for register in ("rAUD4LEN", "rAUD4ENV", "rAUD4POLY", "rAUD4GO"):
            self.assertIn(f"ldh [{register}], a", update)
        self.assertIn("call Sound_UnmuteCurrentSfxChannel", stop)
        self.assertIn("ld c, 0", stop)

    def test_bgm_finish_preserves_occupied_channel_then_allows_second_sfx(self) -> None:
        silence = routine(
            self.sound, "Sound_SilenceFinishedBgmChannel:", "Sound_UpdateSfx:"
        )
        self.assertLess(silence.index("cp b"), silence.index("call hUGE_mute_channel"))
        self.assertIn("ret z", silence)

        model = SoundRuntimeModel()
        self.assertTrue(model.play_sfx())
        model.update(bgm_finished=True)
        self.assertNotIn(3, model.silenced)
        self.assertTrue(model.sfx_active)
        model.update()
        self.assertFalse(model.sfx_active)
        self.assertFalse(model.playback_active)
        self.assertNotIn(3, model.muted)
        self.assertTrue(model.play_sfx())

    def test_none_rom_builds_with_runtime_and_screen_symbols(self) -> None:
        source = ROOT / "obj" / "bgm_v2_loop_none_manual_test.asm"
        with tempfile.TemporaryDirectory() as temp_dir:
            rom = Path(temp_dir) / "none_sfx_runtime.gb"
            _, _, _, _, sym = build_sound_test_rom.build_rom(source, rom)
            self.assertEqual(rom.stat().st_size, 32768)
            symbols = sym.read_text(encoding="utf-8")
            for symbol in (
                "Sound_Update",
                "Sound_PlaySfx",
                "Sound_StopSfx",
                "SoundTestScreenReady",
                "SoundTestScreenSfxPlaying",
                "SoundTestScreenSfxFinished",
            ):
                self.assertIn(symbol, symbols)

    def test_generated_none_rom_updates_three_full_bg_map_rows(self) -> None:
        source = ROOT / "obj" / "bgm_v2_loop_none_manual_test.asm"
        main = build_sound_test_rom.generate_main_asm(
            source,
            build_sound_test_rom.parse_song_label(source),
            2,
            2,
            ROOT / "obj" / "se_cursor_sfx.asm",
        )
        show_screen = routine(main, "SoundTest_ShowScreen:", "SoundTest_WaitVBlank:")
        self.assertIn("ld de, $9800", show_screen)
        self.assertIn("ld bc, 32 * 3", show_screen)
        self.assertNotIn("ld bc, 20 * 5", show_screen)

    def test_v1_full_and_range_keep_existing_noninteractive_generator(self) -> None:
        v1 = ROOT / "src" / "bgm_test.asm"
        v1_main = build_sound_test_rom.generate_main_asm(
            v1, build_sound_test_rom.parse_song_label(v1), 1
        )
        self.assertIn("call hUGE_init", v1_main)
        self.assertNotIn("call Sound_PlaySfx", v1_main)

        for name in ("full", "range"):
            source = ROOT / "obj" / f"bgm_v2_loop_{name}_manual_test.asm"
            main = build_sound_test_rom.generate_main_asm(
                source,
                build_sound_test_rom.parse_song_label(source),
                2,
                build_sound_test_rom.parse_loop_mode(source),
            )
            self.assertIn("call hUGE_init_v2", main)
            self.assertNotIn("call Sound_PlaySfx", main)

    def test_ch2_toggle_uses_driver_mute_without_reinitializing_song(self) -> None:
        source = ROOT / "obj" / "bgm_v2_ch1_ch3_skeleton_test.asm"
        main = build_sound_test_rom.generate_main_asm(
            source, build_sound_test_rom.parse_song_label(source), 2,
            ch2_mute_toggle=True,
        )
        input_routine = routine(main, "SoundTest_ReadButtons:", "SoundTest_InitAudio:")
        self.assertEqual(main.count("call hUGE_dosound"), 1)
        self.assertEqual(main.count("call hUGE_init_v2"), 1)
        self.assertIn("ld a, P1F_GET_BUTTONS\n    ldh [rP1], a", input_routine)
        self.assertNotIn("ld a, $20", input_routine)
        self.assertNotIn("P1F_GET_DPAD", input_routine)
        self.assertIn("bit 0, a\n    jr nz, .mute", input_routine)
        self.assertIn("bit 1, a\n    ret z", input_routine)
        self.assertIn("ld b, 1\n    ld c, 1\n    call hUGE_mute_channel", input_routine)
        self.assertIn("ld b, 1\n    ld c, 0\n    call hUGE_mute_channel", input_routine)
        self.assertNotIn("ld b, 0", input_routine)
        self.assertNotIn("ld b, 2", input_routine)
        self.assertNotIn("ld b, 3", input_routine)
        self.assertIn("wSoundTestPreviousButtons", main)
        self.assertIn("cpl\n    and b", input_routine)

    def test_ch2_toggle_initializes_display_and_clears_boot_screen(self) -> None:
        source = ROOT / "obj" / "bgm_v2_ch1_ch3_skeleton_test.asm"
        main = build_sound_test_rom.generate_main_asm(
            source, build_sound_test_rom.parse_song_label(source), 2,
            ch2_mute_toggle=True,
        )
        entry = routine(main, "SoundTest_Main::", "SoundTest_ReadButtons:")
        init = routine(main, "SoundTest_InitDisplay:", "SoundTest_ClearBg:")
        clear = routine(main, "SoundTest_ClearBg:", "SoundTest_ShowScreen:")
        show = routine(main, "SoundTest_ShowScreen:", "SoundTest_WaitVBlank:")
        self.assertIn("call SoundTest_InitDisplay", entry)
        self.assertIn("ld de, $8000", init)
        self.assertIn("ld bc, 91 * 16", init)
        self.assertIn("ldh [rLCDC], a", init)
        self.assertIn("ldh [rSCX], a", init)
        self.assertIn("ldh [rSCY], a", init)
        self.assertIn("ldh [rBGP], a", init)
        self.assertIn("ld bc, 32 * 32", clear)
        self.assertIn("ld [hl+], a", clear)
        self.assertIn("ld bc, 32 * 2", show)
        self.assertIn('db $41, $4C, $4C, $20, $43, $48, $41, $4E, $4E, $45, $4C, $53', main)
        self.assertIn('db $43, $48, $32, $20, $4D, $55, $54, $45, $44', main)
        self.assertIn('db $41, $4C, $4C, $20, $43, $48, $41, $4E, $4E, $45, $4C, $53', main)
        self.assertIn('db $43, $48, $32, $20, $4D, $55, $54, $45, $44', main)


if __name__ == "__main__":
    unittest.main()
