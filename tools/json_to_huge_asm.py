#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path

import json_to_uge


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def fail(message: str) -> None:
    raise ValueError(message)


def asm_symbol_from_path(path: Path) -> str:
    symbol = re.sub(r"[^A-Za-z0-9_]", "_", path.stem)
    symbol = re.sub(r"_+", "_", symbol).strip("_")
    if not symbol:
        fail(f"{path}: cannot derive ASM symbol from output filename")
    if symbol[0].isdigit():
        symbol = "_" + symbol
    return symbol


def note_to_asm(note: int) -> str:
    if note == json_to_uge.NO_NOTE:
        return "___"
    if note < 0 or note > 71:
        fail(f"internal error: unsupported note number {note}")
    octave = note // 12 + 3
    name = NOTE_NAMES[note % 12]
    if "#" in name:
        return f"{name}{octave}"
    return f"{name}_{octave}"


def render_cell(cell: json_to_uge.Cell) -> str:
    effect = (cell.effect_code << 8) | cell.effect_param
    return f" dn {note_to_asm(cell.note)},{cell.instrument},${effect:03X}"


def render_order(label: str, order_matrix: list[list[int]]) -> list[str]:
    lines = [f"{label}_order_cnt: db {len(order_matrix[0]) * 2}"]
    for index, orders in enumerate(order_matrix, start=1):
        joined = ",".join(f"{label}_P{pattern}" for pattern in orders)
        lines.append(f"{label}_order{index}: dw {joined}")
    lines.append("")
    return lines


def render_patterns(label: str, patterns: dict[int, list[json_to_uge.Cell]]) -> list[str]:
    lines: list[str] = []
    for key in sorted(patterns):
        lines.append(f"{label}_P{key}:")
        lines.extend(render_cell(cell) for cell in patterns[key])
        lines.append("")
    return lines


def square_instrument_bytes(
    instrument_id: int,
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
) -> tuple[int, int, int, int]:
    _, duty, vol_sweep_amount = json_to_uge.default_duty_values(instrument_id)
    initial_volume = 15
    vol_sweep_direction = json_to_uge.ST_DOWN

    spec = instruments["duty"].get(instrument_id)
    if spec:
        duty = spec.duty
        initial_volume = spec.initial_volume
        vol_sweep_direction = spec.vol_sweep_direction
        vol_sweep_amount = spec.vol_sweep_amount

    direction_bit = 1 if vol_sweep_direction == json_to_uge.ST_UP else 0
    if spec and spec.json_version == 2:
        sweep_direction_bit = 1 if spec.sweep_direction == json_to_uge.ST_DOWN else 0
        nr10 = (spec.sweep_time << 4) | (sweep_direction_bit << 3) | spec.sweep_shift
        nr11 = (duty << 6) | spec.length
        nr14 = (0x40 if spec.length_enable else 0) | 0x80
    else:
        # Preserve the Version 1 ASM representation: no NR10 sweep settings,
        # no sound-length value, and trigger enabled without length counter.
        nr10 = 8
        nr11 = duty << 6
        nr14 = 0x80
    nr12 = (initial_volume << 4) | (direction_bit << 3) | vol_sweep_amount
    return nr10, nr11, nr12, nr14


def highest_used_instrument(patterns: dict[int, list[json_to_uge.Cell]], order_matrix: list[list[int]]) -> int:
    return highest_used_instrument_for_channels(patterns, order_matrix, (0, 1))


def highest_used_instrument_for_channels(
    patterns: dict[int, list[json_to_uge.Cell]],
    order_matrix: list[list[int]],
    channel_indices: tuple[int, ...],
) -> int:
    highest = 0
    for channel_index in channel_indices:
        channel_orders = order_matrix[channel_index]
        for pattern_key in channel_orders:
            for cell in patterns[pattern_key]:
                if cell.instrument > highest:
                    highest = cell.instrument
    return highest


def render_duty_instruments(
    label: str,
    patterns: dict[int, list[json_to_uge.Cell]],
    order_matrix: list[list[int]],
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
) -> list[str]:
    lines = [f"{label}_duty_instruments:"]
    for instrument_id in range(1, highest_used_instrument(patterns, order_matrix) + 1):
        nr10, nr11, nr12, nr14 = square_instrument_bytes(instrument_id, instruments)
        lines.extend(
            [
                f"{label}_itSquareinst{instrument_id}:",
                f"db {nr10}",
                f"db {nr11}",
                f"db {nr12}",
                "dw 0",
                f"db {nr14}",
                "",
            ]
        )
    return lines


def wave_instrument_bytes(
    instrument_id: int,
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
) -> tuple[int, int, int, int, int, int]:
    spec = instruments["wave"].get(instrument_id)
    _, length, length_enabled, output_level, waveform_index = (
        json_to_uge.wave_instrument_packing_values(instrument_id, spec)
    )
    return (
        length,
        output_level << 5,
        waveform_index,
        0,
        0,
        0x80 if not length_enabled else 0xC0,
    )


def render_wave_instruments(
    label: str,
    patterns: dict[int, list[json_to_uge.Cell]],
    order_matrix: list[list[int]],
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
    json_version: int,
) -> list[str]:
    if json_version != 2:
        return render_empty_instrument_bank(label, "wave_instruments")

    lines = [f"{label}_wave_instruments:"]

    highest = highest_used_instrument_for_channels(patterns, order_matrix, (2,))
    for instrument_id in range(1, highest + 1):
        length, output_level, waveform_index, pointer_low, pointer_high, highmask = (
            wave_instrument_bytes(instrument_id, instruments)
        )
        lines.extend(
            [
                f"{label}_itWaveinst{instrument_id}:",
                f"db {length}",
                f"db {output_level}",
                f"db {waveform_index}",
                f"dw {(pointer_high << 8) | pointer_low}",
                f"db {highmask}",
                "",
            ]
        )
    return lines


def noise_instrument_bytes(
    instrument_id: int,
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
) -> tuple[int, int, int, int, int, int]:
    spec = instruments["noise"].get(instrument_id)
    if spec is None or spec.json_version != 2:
        initial_volume = 15
        vol_sweep_direction = json_to_uge.ST_DOWN
        vol_sweep_amount = 0
        length = 0
        length_enable = False
        width_mode = json_to_uge.NOISE_WIDTH_15BIT
    else:
        initial_volume = spec.initial_volume
        vol_sweep_direction = spec.vol_sweep_direction
        vol_sweep_amount = spec.vol_sweep_amount
        length = spec.length
        length_enable = spec.length_enable
        width_mode = spec.width_mode

    direction_bit = 1 if vol_sweep_direction == json_to_uge.ST_UP else 0
    nr42 = (initial_volume << 4) | (direction_bit << 3) | vol_sweep_amount
    if width_mode == json_to_uge.NOISE_WIDTH_15BIT:
        width_bit = 0
    elif width_mode == json_to_uge.NOISE_WIDTH_7BIT:
        width_bit = 0x80
    else:
        raise ValueError(
            f"Noise Instrument {instrument_id}: unsupported width_mode {width_mode!r}"
        )
    highmask = width_bit | (0x40 if length_enable else 0) | length
    return nr42, 0, 0, highmask, 0, 0


def render_noise_instruments(
    label: str,
    patterns: dict[int, list[json_to_uge.Cell]],
    order_matrix: list[list[int]],
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
    json_version: int,
) -> list[str]:
    if json_version != 2:
        return render_empty_instrument_bank(label, "noise_instruments")

    lines = [f"{label}_noise_instruments:"]
    highest = highest_used_instrument_for_channels(patterns, order_matrix, (3,))
    for instrument_id in range(1, highest + 1):
        nr42, pointer_low, pointer_high, highmask, padding_low, padding_high = (
            noise_instrument_bytes(instrument_id, instruments)
        )
        lines.extend(
            [
                f"{label}_itNoiseinst{instrument_id}:",
                f"db {nr42}",
                f"dw {(pointer_high << 8) | pointer_low}",
                f"db {highmask}",
                f"dw {(padding_high << 8) | padding_low}",
                "",
            ]
        )
    return lines


def render_empty_instrument_bank(label: str, name: str) -> list[str]:
    return [f"{label}_{name}:", ""]


def render_routines(label: str) -> list[str]:
    lines = [f"{label}_routines:"]
    for index in range(16):
        lines.extend(
            [
                f"{label}__hUGE_Routine_{index}:",
                f"{label}__end_hUGE_Routine_{index}:",
                "ret",
                "",
            ]
        )
    return lines


def render_waves(
    label: str,
    wave_tables: tuple[json_to_uge.WaveTableSpec, ...] | None,
    json_version: int,
) -> list[str]:
    if json_version != 2:
        return [f"{label}_waves:"]

    lines = [f"{label}_waves:"]
    for bank in json_to_uge.build_uge_wave_banks(wave_tables):
        packed = json_to_uge.pack_wave_samples(bank)
        lines.append("db " + ",".join(f"${value:02X}" for value in packed))
    return lines


def build_asm(data: dict, label: str) -> str:
    json_to_uge.validate_header(data)
    json_version = json_to_uge.validate_json_version(data)
    wave_tables = json_to_uge.validate_wave_tables(data, json_version)
    instruments = json_to_uge.validate_instruments(data, wave_tables=wave_tables)
    patterns, order_matrix = json_to_uge.build_patterns(data, instruments)
    loop = json_to_uge.validate_loop(data, json_version, len(order_matrix[0]))
    if json_version == 2:
        patterns, order_matrix = json_to_uge.assign_version_2_pattern_numbers(
            patterns, order_matrix
        )
    tempo = json_to_uge.expect_int(data["tempo"], "tempo")

    lines = [
        'include "hUGE.inc"',
        "",
        f'SECTION "{label} Song Data", ROMX',
        "",
        f"{label}::",
        f"db {tempo}",
        f"dw {label}_order_cnt",
        f"dw {label}_order1, {label}_order2, {label}_order3, {label}_order4",
        f"dw {label}_duty_instruments, {label}_wave_instruments, {label}_noise_instruments",
        f"dw {label}_routines",
        f"dw {label}_waves",
        "",
    ]
    lines.extend(render_order(label, order_matrix))
    lines.extend(render_patterns(label, patterns))
    lines.extend(render_duty_instruments(label, patterns, order_matrix, instruments))
    lines.extend(render_wave_instruments(label, patterns, order_matrix, instruments, json_version))
    lines.extend(render_noise_instruments(label, patterns, order_matrix, instruments, json_version))
    lines.extend(render_routines(label))
    lines.extend(render_waves(label, wave_tables, json_version))
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Pocket Sweeper music definition JSON into hUGEDriver RGBDS ASM."
    )
    parser.add_argument("input_json", type=Path, help="Input music definition JSON")
    parser.add_argument("output_asm", type=Path, help="Output RGBDS ASM file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        label = asm_symbol_from_path(args.output_asm)
        data = json_to_uge.load_json(args.input_json)
        asm = build_asm(data, label)
        args.output_asm.parent.mkdir(parents=True, exist_ok=True)
        args.output_asm.write_text(asm, encoding="utf-8", newline="\n")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"input: {args.input_json}")
    print(f"output: {args.output_asm}")
    print(f"label: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
