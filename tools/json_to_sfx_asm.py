#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import json_to_uge


SFX_CH_PULSE1 = 0
SFX_CH_NOISE = 3

NOTE_PERIODS = (
    44, 156, 262, 363, 457, 547, 631, 710, 786, 854, 923, 986,
    1046, 1102, 1155, 1205, 1253, 1297, 1339, 1379, 1417, 1452, 1486, 1517,
    1546, 1575, 1602, 1627, 1650, 1673, 1694, 1714, 1732, 1750, 1767, 1783,
    1798, 1812, 1825, 1837, 1849, 1860, 1871, 1881, 1890, 1899, 1907, 1915,
    1923, 1930, 1936, 1943, 1949, 1954, 1959, 1964, 1969, 1974, 1978, 1982,
    1985, 1988, 1992, 1995, 1998, 2001, 2004, 2006, 2009, 2011, 2013, 2015,
)


def fail(message: str) -> None:
    raise ValueError(message)


def asm_symbol_from_path(path: Path) -> str:
    symbol = re.sub(r"[^A-Za-z0-9_]", "_", path.stem)
    symbol = re.sub(r"_+", "_", symbol).strip("_")
    if symbol.endswith("_sfx"):
        symbol = symbol[:-4]
    if symbol.startswith("se_"):
        symbol = symbol[3:]
    if not symbol:
        fail(f"{path}: cannot derive ASM symbol from output filename")
    if symbol[0].isdigit():
        symbol = "_" + symbol
    return symbol


def pascal_symbol(value: str) -> str:
    parts = [part for part in value.split("_") if part]
    if not parts:
        fail("cannot derive PascalCase ASM label")
    return "".join(part[:1].upper() + part[1:] for part in parts)


def sfx_constant_name(value: str) -> str:
    return "SFX_" + value.upper()


def expect_priority(data: dict[str, Any]) -> int:
    if "priority" not in data:
        fail("priority: required for type 'sfx'")
    priority = json_to_uge.expect_int(data.get("priority"), "priority")
    if priority < 1 or priority > 5:
        fail("priority: expected 1-5")
    return priority


def validate_header(data: dict[str, Any]) -> int:
    json_to_uge.validate_header(data)
    song_type = json_to_uge.expect_string(data.get("type"), "type")
    if song_type != "sfx":
        fail("type: expected 'sfx'")
    return expect_priority(data)


def event_has_sound(event: Any) -> bool:
    if not isinstance(event, dict):
        return True
    return event.get("note") != "rest"


def active_channel(data: dict[str, Any]) -> str:
    order = json_to_uge.expect_list(data.get("order"), "order")
    patterns = json_to_uge.expect_dict(data.get("patterns"), "patterns")
    active: set[str] = set()

    for order_index, pattern_name_value in enumerate(order):
        pattern_name = json_to_uge.expect_string(pattern_name_value, f"order[{order_index}]")
        pattern = json_to_uge.expect_dict(patterns.get(pattern_name), f"patterns.{pattern_name}")
        channels = json_to_uge.expect_dict(pattern.get("channels"), f"patterns.{pattern_name}.channels")
        for channel in json_to_uge.CHANNELS:
            events = json_to_uge.expect_list(
                channels.get(channel, []),
                f"patterns.{pattern_name}.channels.{channel}",
            )
            if any(event_has_sound(event) for event in events):
                active.add(channel)

    if not active:
        fail("patterns: no sound events found")
    if len(active) > 1:
        fail("patterns: multiple simultaneous SFX channels are not supported")
    channel = next(iter(active))
    if channel not in ("pulse1", "noise"):
        fail(f"patterns: channel '{channel}' is not supported for SFX; use pulse1 or noise")
    return channel


def collect_events(data: dict[str, Any], channel: str) -> list[dict[str, Any]]:
    order = json_to_uge.expect_list(data.get("order"), "order")
    patterns = json_to_uge.expect_dict(data.get("patterns"), "patterns")
    result: list[dict[str, Any]] = []

    for order_index, pattern_name_value in enumerate(order):
        pattern_name = json_to_uge.expect_string(pattern_name_value, f"order[{order_index}]")
        pattern = json_to_uge.expect_dict(patterns.get(pattern_name), f"patterns.{pattern_name}")
        channels = json_to_uge.expect_dict(pattern.get("channels"), f"patterns.{pattern_name}.channels")
        events = json_to_uge.expect_list(
            channels.get(channel, []),
            f"patterns.{pattern_name}.channels.{channel}",
        )
        for event_index, event_value in enumerate(events):
            event = json_to_uge.expect_dict(
                event_value,
                f"patterns.{pattern_name}.channels.{channel}[{event_index}]",
            )
            validate_event(event, f"patterns.{pattern_name}.channels.{channel}[{event_index}]")
            result.append(event)

    if not result:
        fail(f"patterns: channel '{channel}' has no events")
    return result


def validate_event(event: dict[str, Any], path: str) -> None:
    length = json_to_uge.expect_int(event.get("length"), f"{path}.length")
    if length <= 0:
        fail(f"{path}.length: must be 1 or greater")
    if event.get("effect") is not None:
        fail(f"{path}.effect: only null is supported")
    if event.get("effect_param") is not None:
        fail(f"{path}.effect_param: only null is supported")
    json_to_uge.validate_instrument_id(event.get("instrument"), f"{path}.instrument")


def instrument_for_channel(
    instruments: dict[str, dict[int, json_to_uge.InstrumentSpec]],
    channel: str,
    instrument_id: int,
) -> json_to_uge.InstrumentSpec:
    bank = "duty" if channel == "pulse1" else "noise"
    spec = instruments[bank].get(instrument_id)
    if spec is None:
        fail(f"instruments: instrument id {instrument_id} is not defined for {channel}")
    return spec


def direction_bit(direction: int) -> int:
    return 1 if direction == json_to_uge.ST_UP else 0


def pulse_step(event: dict[str, Any], spec: json_to_uge.InstrumentSpec) -> list[int] | None:
    note = json_to_uge.parse_note(event.get("note"), "event.note")
    wait_frames = json_to_uge.expect_int(event.get("length"), "event.length")
    if note == json_to_uge.NO_NOTE:
        return None

    period = NOTE_PERIODS[note]
    nr10 = 0
    nr11 = spec.duty << 6
    nr12 = (spec.initial_volume << 4) | (direction_bit(spec.vol_sweep_direction) << 3) | spec.vol_sweep_amount
    nr13 = period & 0xFF
    nr14 = 0x80 | ((period >> 8) & 0x07)
    return [wait_frames, nr10, nr11, nr12, nr13, nr14]


def optional_int(instrument: dict[str, Any], key: str, default: int, minimum: int, maximum: int, path: str) -> int:
    value = instrument.get(key, default)
    parsed = json_to_uge.expect_int(value, f"{path}.{key}")
    if parsed < minimum or parsed > maximum:
        fail(f"{path}.{key}: expected {minimum}-{maximum}")
    return parsed


def optional_bool(instrument: dict[str, Any], key: str, default: bool, path: str) -> bool:
    value = instrument.get(key, default)
    if not isinstance(value, bool):
        fail(f"{path}.{key}: boolean expected")
    return value


def noise_details(data: dict[str, Any], instrument_id: int) -> dict[str, Any]:
    instruments = json_to_uge.expect_list(data.get("instruments"), "instruments")
    for index, item in enumerate(instruments):
        path = f"instruments[{index}]"
        instrument = json_to_uge.expect_dict(item, path)
        if json_to_uge.expect_int(instrument.get("id"), f"{path}.id") != instrument_id:
            continue
        channel = json_to_uge.expect_string(instrument.get("channel"), f"{path}.channel")
        if channel != "noise":
            fail(f"{path}.channel: expected 'noise'")
        width_mode = instrument.get("width_mode", "15bit")
        if width_mode not in ("15bit", "7bit"):
            fail(f"{path}.width_mode: expected '15bit' or '7bit'")
        return {
            "noise_length": optional_int(instrument, "noise_length", 0, 0, 63, path),
            "initial_volume": optional_int(instrument, "initial_volume", 15, 0, 15, path),
            "envelope_direction": json_to_uge.parse_envelope_direction(
                instrument.get("envelope_direction"),
                f"{path}.envelope_direction",
                json_to_uge.ST_DOWN,
            ),
            "envelope_sweep": optional_int(instrument, "envelope_sweep", 0, 0, 7, path),
            "clock_shift": optional_int(instrument, "clock_shift", 4, 0, 15, path),
            "width_mode": width_mode,
            "divisor_code": optional_int(instrument, "divisor_code", 0, 0, 7, path),
            "length_enable": optional_bool(instrument, "length_enable", False, path),
        }
    fail(f"instruments: instrument id {instrument_id} is not defined")


def noise_step(event: dict[str, Any], details: dict[str, Any]) -> list[int] | None:
    wait_frames = json_to_uge.expect_int(event.get("length"), "event.length")
    if event.get("note") == "rest":
        return None

    nr41 = details["noise_length"] & 0x3F
    nr42 = (
        (details["initial_volume"] << 4)
        | (direction_bit(details["envelope_direction"]) << 3)
        | details["envelope_sweep"]
    )
    width_bit = 1 if details["width_mode"] == "7bit" else 0
    nr43 = (details["clock_shift"] << 4) | (width_bit << 3) | details["divisor_code"]
    nr44 = (0x40 if details["length_enable"] else 0) | 0x80
    return [wait_frames, nr41, nr42, nr43, nr44]


def build_steps(data: dict[str, Any], channel: str) -> list[list[int]]:
    instruments = json_to_uge.validate_instruments(data)
    events = collect_events(data, channel)
    steps: list[list[int]] = []

    for event in events:
        instrument_id = json_to_uge.validate_instrument_id(event.get("instrument"), "event.instrument")
        if channel == "pulse1":
            spec = instrument_for_channel(instruments, channel, instrument_id)
            step = pulse_step(event, spec)
        else:
            step = noise_step(event, noise_details(data, instrument_id))
        if step is not None:
            steps.append(step)

    if not steps:
        fail("patterns: SFX must contain at least one non-rest event")
    if len(steps) > 255:
        fail("patterns: SFX step count must fit in one byte")
    return steps


def render_asm(data: dict[str, Any], label_base: str) -> str:
    priority = validate_header(data)
    channel = active_channel(data)
    steps = build_steps(data, channel)
    channel_kind = SFX_CH_PULSE1 if channel == "pulse1" else SFX_CH_NOISE
    const_name = sfx_constant_name(label_base)
    label = "Sfx" + pascal_symbol(label_base)
    total_frames = sum(step[0] for step in steps)
    if total_frames > 255:
        fail("patterns: total SFX frames must fit in one byte")

    lines = [
        f"{const_name} EQU 0",
        "SFX_CH_PULSE1 EQU 0",
        "SFX_CH_NOISE EQU 3",
        "",
        "SfxTable:",
        f"    dw {label}",
        "",
        f"{label}:",
        f"    db {channel_kind}, {priority}, {len(steps)}, {total_frames}",
    ]
    for step in steps:
        joined = ", ".join(f"${value:02X}" for value in step[1:])
        lines.append(f"    db {step[0]}, {joined}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Pocket Sweeper SFX JSON into APU register RGBDS ASM."
    )
    parser.add_argument("input_json", type=Path, help="Input SFX JSON")
    parser.add_argument("output_asm", type=Path, help="Output SFX ASM")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        label_base = asm_symbol_from_path(args.output_asm)
        data = json_to_uge.load_json(args.input_json)
        asm = render_asm(data, label_base)
        args.output_asm.parent.mkdir(parents=True, exist_ok=True)
        args.output_asm.write_text(asm, encoding="utf-8", newline="\n")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"input: {args.input_json}")
    print(f"output: {args.output_asm}")
    print(f"label: {label_base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
