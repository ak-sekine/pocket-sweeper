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


if __name__ == "__main__":
    unittest.main()
