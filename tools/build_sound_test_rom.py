#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OBJ_DIR = PROJECT_ROOT / "obj"
HUGE_DRIVER = PROJECT_ROOT / "src" / "hUGEDriver.asm"
SOUND_MANAGER = PROJECT_ROOT / "src" / "sound.asm"
SFX_ASSET = PROJECT_ROOT / "assets" / "se_cursor.json"
SFX_CONVERTER = PROJECT_ROOT / "tools" / "json_to_sfx_asm.py"
BG_MAP_WIDTH = 32
VISIBLE_TILE_WIDTH = 20
SOUND_TEST_DISPLAY_ROWS = 3


def fail(message: str) -> None:
    raise ValueError(message)


def asm_string(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def tool_name(name: str) -> str:
    return os.environ.get(name.upper(), name)


def parse_song_label(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_.$#]*)::\s*$", line.strip())
        if match:
            return match.group(1)
    fail(f"{path}: song descriptor label ending with '::' was not found")


def parse_song_version(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    if "_loop_metadata" in text:
        return 2
    return 1


def parse_loop_mode(path: Path) -> int | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"_loop_metadata:\s*db\s+([0-9]+)\s*,", text)
    return int(match.group(1)) if match else None


def _screen_data(*lines: str) -> list[int]:
    cells = [ord(" ")] * (BG_MAP_WIDTH * SOUND_TEST_DISPLAY_ROWS)
    for y, line in enumerate(lines[:SOUND_TEST_DISPLAY_ROWS]):
        if len(line) > VISIBLE_TILE_WIDTH:
            fail(f"screen line {y}: text exceeds {VISIBLE_TILE_WIDTH} visible tiles")
        for x, char in enumerate(line):
            cells[y * BG_MAP_WIDTH + x] = ord(char)
    return cells


def _db_lines(values: list[int]) -> str:
    return "\n".join(
        "    db " + ", ".join(f"${value:02X}" for value in values[offset : offset + BG_MAP_WIDTH])
        for offset in range(0, len(values), BG_MAP_WIDTH)
    )


FONT_5X7 = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    ":": ("00000", "00100", "00100", "00000", "00100", "00100", "00000"),
}


def _font_tile_data() -> list[int]:
    tiles = [0] * (91 * 16)
    for char, rows in FONT_5X7.items():
        base = ord(char) * 16
        for y, row in enumerate(rows):
            pixels = int(row, 2) << 2
            tiles[base + (y * 2)] = pixels
            tiles[base + (y * 2) + 1] = pixels
    return tiles


def generate_main_asm(
    input_asm: Path,
    song_label: str,
    song_version: int,
    loop_mode: int | None = None,
    sfx_asm: Path | None = None,
    ch2_mute_toggle: bool = False,
) -> str:
    include_path = input_asm.resolve()
    init_routine = "hUGE_init_v2" if song_version == 2 else "hUGE_init"
    if ch2_mute_toggle:
        return generate_ch2_mute_main_asm(include_path, song_label, init_routine)
    if song_version == 2 and loop_mode == 2:
        if sfx_asm is None:
            sfx_asm = OBJ_DIR / "sound_test_sfx.asm"
        return generate_none_sfx_main_asm(include_path, song_label, sfx_asm.resolve())
    return f"""INCLUDE "hardware.inc"
INCLUDE "{asm_string(include_path)}"

SECTION "Sound Test ROM Header", ROM0[$0100]

EntryPoint::
    nop
    jp SoundTest_Main
    ds $0150 - @, 0

SECTION "Sound Test Main", ROM0[$0150]

SoundTest_Main::
    di
    ld sp, $DFFF
    call SoundTest_InitAudio
    ld hl, {song_label}
    call {init_routine}

.loop:
    call SoundTest_WaitVBlank
    call hUGE_dosound
    call hUGE_bgm_finished
    and a
    jr nz, .finished
    jr .loop

.finished:
    xor a
    ldh [rAUDENA], a
.finished_loop:
    halt
    jr .finished_loop

SoundTest_InitAudio:
    ld a, %10000000
    ldh [rAUDENA], a
    ld a, %01110111
    ldh [rAUDVOL], a
    ld a, %11111111
    ldh [rAUDTERM], a
    ret

SoundTest_WaitVBlank:
.waitVisible:
    ldh a, [rLY]
    cp 144
    jr nc, .waitVisible
.waitVBlank:
    ldh a, [rLY]
    cp 144
    jr c, .waitVBlank
    ret
"""


def generate_ch2_mute_main_asm(input_asm: Path, song_label: str, init_routine: str) -> str:
    font_tiles = _db_lines(_font_tile_data())
    all_screen = _db_lines(_screen_data("ALL CHANNELS"))
    muted_screen = _db_lines(_screen_data("CH2 MUTED"))
    return f'''INCLUDE "hardware.inc"
INCLUDE "{asm_string(input_asm)}"
SECTION "Sound Test ROM Header", ROM0[$0100]
EntryPoint::
    nop
    jp SoundTest_Main
    ds $0150 - @, 0
SECTION "Sound Test Main", ROM0[$0150]
SoundTest_Main::
    di
    ld sp, $DFFF
    call SoundTest_InitAudio
    call SoundTest_InitDisplay
    ld hl, {song_label}
    call {init_routine}
    xor a
    ld [wSoundTestPreviousButtons], a
    ld hl, SoundTestScreenAll
    call SoundTest_ShowScreen
.loop:
    call SoundTest_WaitVBlank
    call hUGE_dosound
    call SoundTest_ReadButtons
    jr .loop
SoundTest_ReadButtons:
    ld a, P1F_GET_BUTTONS
    ldh [rP1], a
    ldh a, [rP1]
    cpl
    and $0F
    ld b, a
    ld a, [wSoundTestPreviousButtons]
    cpl
    and b
    ld c, a
    ld a, b
    ld [wSoundTestPreviousButtons], a
    ld a, c
    bit 0, a
    jr nz, .mute
    bit 1, a
    ret z
    ld b, 1
    ld c, 0
    call hUGE_mute_channel
    ld hl, SoundTestScreenAll
    jp SoundTest_ShowScreen
.mute:
    ld b, 1
    ld c, 1
    call hUGE_mute_channel
    ld hl, SoundTestScreenCh2Muted
    jp SoundTest_ShowScreen
SoundTest_InitAudio:
    ld a, %10000000
    ldh [rAUDENA], a
    ld a, %01110111
    ldh [rAUDVOL], a
    ld a, %11111111
    ldh [rAUDTERM], a
    ret
SoundTest_InitDisplay:
    xor a
    ldh [rLCDC], a
    ldh [rSCX], a
    ldh [rSCY], a
    ld a, %11100100
    ldh [rBGP], a
    ld hl, SoundTestFontTiles
    ld de, $8000
    ld bc, 91 * 16
.copyTiles:
    ld a, [hl+]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copyTiles
    call SoundTest_ClearBg
    ret
SoundTest_ClearBg:
    xor a
    ld hl, $9800
    ld bc, 32 * 32
.clear:
    ld [hl+], a
    dec bc
    ld a, b
    or c
    jr nz, .clear
    ret
SoundTest_ShowScreen:
    push hl
    xor a
    ldh [rLCDC], a
    ld de, $9800
    ld bc, 32 * 2
.copy:
    ld a, [hl+]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copy
    ld a, %10010001
    ldh [rLCDC], a
    pop hl
    ret
SoundTest_WaitVBlank:
.waitVisible:
    ldh a, [rLY]
    cp 144
    jr nc, .waitVisible
.waitVBlank:
    ldh a, [rLY]
    cp 144
    jr c, .waitVBlank
    ret
SECTION "Sound Test Screen Data", ROM0
SoundTestFontTiles:
{font_tiles}
SoundTestScreenAll:
{all_screen}
SoundTestScreenCh2Muted:
{muted_screen}
SECTION "Sound Test WRAM", WRAM0
wSoundTestPreviousButtons: ds 1
'''


def generate_none_sfx_main_asm(input_asm: Path, song_label: str, sfx_asm: Path) -> str:
    playing = _db_lines(_screen_data("BGM PLAYING"))
    ready = _db_lines(_screen_data("BGM FINISHED", "A: PLAY SFX", "READY"))
    sfx_playing = _db_lines(_screen_data("SFX PLAYING"))
    sfx_finished = _db_lines(_screen_data("SFX FINISHED", "UNMUTE COMPLETE"))
    font_tiles = _db_lines(_font_tile_data())
    return f"""INCLUDE "{asm_string(input_asm)}"
INCLUDE "{asm_string(sfx_asm)}"
DEF SOUND_NO_TEST_BGM EQU 1
INCLUDE "{asm_string(SOUND_MANAGER.resolve())}"

SECTION "Sound Test WRAM", WRAM0
wSoundTestState: ds 1
wSoundTestDisplayTimer: ds 1
wSoundTestAWasReleased: ds 1

SECTION "Sound Test ROM Header", ROM0[$0100]
EntryPoint::
    nop
    jp SoundTest_Main
    ds $0150 - @, 0

SECTION "Sound Test Main", ROM0[$0150]
SoundTest_Main::
    di
    ld sp, $DFFF
    call SoundTest_InitDisplay
    call Sound_Init
    ld hl, {song_label}
    call Sound_PlayBgmV2
    ld hl, SoundTestScreenBgmPlaying
    call SoundTest_ShowScreen
    xor a
    ld [wSoundTestState], a
    ld [wSoundTestDisplayTimer], a
    ld [wSoundTestAWasReleased], a

.loop:
    call SoundTest_WaitVBlank
    call Sound_Update
    ld a, [wSoundTestState]
    and a
    jr z, .waitForBgmEnd
    cp 1
    jr z, .ready
    cp 2
    jr z, .sfxPlaying

    ld hl, wSoundTestDisplayTimer
    dec [hl]
    jr nz, .loop
    ld hl, SoundTestScreenReady
    call SoundTest_ShowScreen
    ld a, 1
    ld [wSoundTestState], a
    jr .loop

.waitForBgmEnd:
    ld a, [wSoundPlaybackActive]
    and a
    jr nz, .loop
    ld hl, SoundTestScreenReady
    call SoundTest_ShowScreen
    ld a, 1
    ld [wSoundTestState], a
    jr .loop

.ready:
    call SoundTest_AButtonPressed
    and a
    jr z, .loop
    xor a
    call Sound_PlaySfx
    ld hl, SoundTestScreenSfxPlaying
    call SoundTest_ShowScreen
    ld a, 2
    ld [wSoundTestState], a
    jr .loop

.sfxPlaying:
    ld a, [wSoundSfxActive]
    and a
    jr nz, .loop
    ld hl, SoundTestScreenSfxFinished
    call SoundTest_ShowScreen
    ld a, 60
    ld [wSoundTestDisplayTimer], a
    ld a, 3
    ld [wSoundTestState], a
    jr .loop

SoundTest_AButtonPressed:
    ld a, $10
    ldh [rP1], a
    ldh a, [rP1]
    ldh a, [rP1]
    cpl
    and 1
    jr nz, .pressed
    ld a, 1
    ld [wSoundTestAWasReleased], a
    xor a
    ret
.pressed:
    ld a, [wSoundTestAWasReleased]
    and a
    ret z
    xor a
    ld [wSoundTestAWasReleased], a
    inc a
    ret

SoundTest_InitDisplay:
    xor a
    ldh [rLCDC], a
    ld hl, SoundTestFontTiles
    ld de, $8000
    ld bc, 91 * 16
.copyTiles:
    ld a, [hl+]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copyTiles
    ld a, %11100100
    ldh [rBGP], a
    ret

SoundTest_ShowScreen:
    push hl
    xor a
    ldh [rLCDC], a
    ld de, $9800
    ld bc, 32 * 3
.copy:
    ld a, [hl+]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copy
    ld a, %10010001
    ldh [rLCDC], a
    pop hl
    ret

SoundTest_WaitVBlank:
.waitVisible:
    ldh a, [rLY]
    cp 144
    jr nc, .waitVisible
.waitVBlank:
    ldh a, [rLY]
    cp 144
    jr c, .waitVBlank
    ret

SECTION "Sound Test Screen Data", ROM0
SoundTestFontTiles:
{font_tiles}
SoundTestScreenBgmPlaying:
{playing}
SoundTestScreenReady:
{ready}
SoundTestScreenSfxPlaying:
{sfx_playing}
SoundTestScreenSfxFinished:
{sfx_finished}
"""


def run_command(command: list[str]) -> None:
    try:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    except FileNotFoundError:
        fail(f"{command[0]} was not found")
    except subprocess.CalledProcessError as exc:
        fail(f"{' '.join(command)} failed with exit code {exc.returncode}")


def build_rom(input_asm: Path, output_rom: Path, ch2_mute_toggle: bool = False) -> tuple[Path, Path, Path, Path, Path]:
    if not input_asm.exists():
        fail(f"{input_asm}: input ASM does not exist")
    if not HUGE_DRIVER.exists():
        fail(f"{HUGE_DRIVER}: hUGEDriver source does not exist")

    OBJ_DIR.mkdir(parents=True, exist_ok=True)
    output_rom.parent.mkdir(parents=True, exist_ok=True)

    song_label = parse_song_label(input_asm)
    song_version = parse_song_version(input_asm)
    loop_mode = parse_loop_mode(input_asm)
    stem = output_rom.stem
    main_asm = OBJ_DIR / f"{stem}_sound_test.asm"
    main_obj = OBJ_DIR / f"{stem}_sound_test.o"
    driver_obj = OBJ_DIR / f"{stem}_hUGEDriver.o"
    map_file = OBJ_DIR / f"{stem}.map"
    sym_file = OBJ_DIR / f"{stem}.sym"

    sfx_asm = OBJ_DIR / f"{stem}_sound_test_sfx.asm"
    if song_version == 2 and loop_mode == 2:
        run_command([sys.executable, str(SFX_CONVERTER), str(SFX_ASSET), str(sfx_asm)])
    main_asm.write_text(
        generate_main_asm(input_asm, song_label, song_version, loop_mode, sfx_asm, ch2_mute_toggle),
        encoding="utf-8",
        newline="\n",
    )

    rgbasm = tool_name("rgbasm")
    rgblink = tool_name("rgblink")
    rgbfix = tool_name("rgbfix")

    include_flags = ["-I", "include/", "-I", "."]
    run_command([rgbasm, *include_flags, "-o", str(main_obj), str(main_asm)])
    run_command([rgbasm, *include_flags, "-o", str(driver_obj), str(HUGE_DRIVER)])
    run_command([rgblink, "-m", str(map_file), "-n", str(sym_file), "-o", str(output_rom), str(main_obj), str(driver_obj)])
    run_command([rgbfix, "-v", "-p", "0xFF", "-t", "SOUND TEST", "-m", "ROM", "-r", "0x00", str(output_rom)])

    return main_asm, main_obj, driver_obj, map_file, sym_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a minimal Game Boy sound test ROM from hUGEDriver RGBDS ASM."
    )
    parser.add_argument("input_asm", type=Path, help="Input hUGEDriver song ASM")
    parser.add_argument("output_rom", type=Path, help="Output Game Boy ROM")
    parser.add_argument("--ch2-mute-toggle", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        input_asm = args.input_asm.resolve()
        output_rom = args.output_rom.resolve()
        main_asm, main_obj, driver_obj, map_file, sym_file = build_rom(input_asm, output_rom, args.ch2_mute_toggle)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"input: {input_asm}")
    print(f"main asm: {main_asm}")
    print(f"objects: {main_obj}, {driver_obj}")
    print(f"rom: {output_rom}")
    print(f"map: {map_file}")
    print(f"sym: {sym_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
