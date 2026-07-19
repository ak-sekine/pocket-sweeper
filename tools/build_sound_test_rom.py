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


def generate_main_asm(input_asm: Path, song_label: str, song_version: int) -> str:
    include_path = input_asm.resolve()
    init_routine = "hUGE_init_v2" if song_version == 2 else "hUGE_init"
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


def run_command(command: list[str]) -> None:
    try:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    except FileNotFoundError:
        fail(f"{command[0]} was not found")
    except subprocess.CalledProcessError as exc:
        fail(f"{' '.join(command)} failed with exit code {exc.returncode}")


def build_rom(input_asm: Path, output_rom: Path) -> tuple[Path, Path, Path, Path, Path]:
    if not input_asm.exists():
        fail(f"{input_asm}: input ASM does not exist")
    if not HUGE_DRIVER.exists():
        fail(f"{HUGE_DRIVER}: hUGEDriver source does not exist")

    OBJ_DIR.mkdir(parents=True, exist_ok=True)
    output_rom.parent.mkdir(parents=True, exist_ok=True)

    song_label = parse_song_label(input_asm)
    song_version = parse_song_version(input_asm)
    stem = output_rom.stem
    main_asm = OBJ_DIR / f"{stem}_sound_test.asm"
    main_obj = OBJ_DIR / f"{stem}_sound_test.o"
    driver_obj = OBJ_DIR / f"{stem}_hUGEDriver.o"
    map_file = OBJ_DIR / f"{stem}.map"
    sym_file = OBJ_DIR / f"{stem}.sym"

    main_asm.write_text(generate_main_asm(input_asm, song_label, song_version), encoding="utf-8", newline="\n")

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        input_asm = args.input_asm.resolve()
        output_rom = args.output_rom.resolve()
        main_asm, main_obj, driver_obj, map_file, sym_file = build_rom(input_asm, output_rom)
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
