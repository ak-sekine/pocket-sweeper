#!/usr/bin/env python3

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SONG_VERSION = 6
JSON_VERSION = 1
SUPPORTED_JSON_VERSIONS = (1, 2)
CHANNELS = ("pulse1", "pulse2", "wave", "noise")
NO_NOTE = 90
PATTERN_ROWS = 64
INSTRUMENT_COUNT = 15
WAVE_COUNT = 16
WAVE_BYTES = 32

IT_SQUARE = 0
IT_WAVE = 1
IT_NOISE = 2

ST_UP = 0
ST_DOWN = 1
SW_FIFTEEN = 0

DEFAULT_DUTY_NAMES = {
    1: ("Duty 12.5%", 0, 0),
    2: ("Duty 25%", 1, 0),
    3: ("Duty 50%", 2, 0),
    4: ("Duty 75%", 3, 0),
    5: ("Duty 12.5% plink", 0, 1),
    6: ("Duty 25% plink", 1, 1),
    7: ("Duty 50% plink", 2, 1),
    8: ("Duty 75% plink", 3, 1),
}

DEFAULT_WAVE_NAMES = {
    1: "Square wave 12.5%",
    2: "Square wave 25%",
    3: "Square wave 50%",
    4: "Square wave 75%",
    5: "Sawtooth wave",
    6: "Triangle wave",
    7: "Sine wave",
    8: "Toothy",
    9: "Triangle Toothy",
    10: "Pointy",
    11: "Strange",
}

WAVE_OUTPUT_LEVELS = {
    "mute": 0,
    "100%": 1,
    "50%": 2,
    "25%": 3,
}

WAVE_VERSION_2_FIELDS = ("waveform", "output_level", "length", "length_enable")
WAVE_PULSE_ONLY_FIELDS = (
    "duty",
    "initial_volume",
    "envelope_direction",
    "envelope_sweep",
    "sweep_time",
    "sweep_direction",
    "sweep_shift",
)
WAVE_NOISE_ONLY_FIELDS = ("noise_length", "clock_shift", "width_mode", "divisor_code")
WAVE_UNSUPPORTED_FIELDS = ("trigger", "frequency")

DEFAULT_WAVES = [
    [0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
    [0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15],
    [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15],
    [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15],
    [7, 10, 12, 13, 13, 11, 7, 5, 2, 1, 1, 3, 6, 8, 11, 13, 13, 12, 9, 7, 4, 1, 0, 1, 4, 7, 9, 12, 13, 13, 11, 8],
    [0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15, 0, 15],
    [15, 14, 15, 12, 15, 10, 15, 8, 15, 6, 15, 4, 15, 2, 15, 0, 15, 2, 15, 4, 15, 6, 15, 8, 15, 10, 15, 12, 15, 14, 15, 15],
    [15, 14, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 8, 8, 7, 7, 8, 10, 11, 13, 15, 1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 14],
    [8, 4, 1, 1, 6, 1, 14, 13, 5, 7, 4, 7, 5, 10, 10, 13, 12, 14, 10, 3, 1, 7, 7, 9, 13, 13, 2, 0, 0, 3, 4, 7],
]


@dataclass(frozen=True)
class Cell:
    note: int = NO_NOTE
    instrument: int = 0
    volume: int = 0
    effect_code: int = 0
    effect_param: int = 0


@dataclass(frozen=True)
class WaveTableSpec:
    name: str
    index: int
    samples: tuple[int, ...]


@dataclass(frozen=True)
class InstrumentSpec:
    id: int
    name: str
    channel: str
    bank: str
    duty: int
    initial_volume: int
    vol_sweep_direction: int
    vol_sweep_amount: int
    length: int = 0
    length_enable: bool = False
    sweep_time: int = 0
    sweep_direction: int = ST_DOWN
    sweep_shift: int = 0
    json_version: int = JSON_VERSION
    waveform: str | None = None
    waveform_index: int | None = None
    output_level: int = 1


def fail(message: str) -> None:
    raise ValueError(message)


def expect_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{path}: object expected")
    return value


def expect_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{path}: array expected")
    return value


def expect_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        fail(f"{path}: string expected")
    return value


def expect_int(value: Any, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        fail(f"{path}: integer expected")
    return value


def expect_optional_int(value: Any, path: str, default: int) -> int:
    if value is None:
        return default
    return expect_int(value, path)


def expect_optional_bool(value: Any, path: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        fail(f"{path}: boolean expected")
    return value


def pack_int(value: int) -> bytes:
    return struct.pack("<i", value)


def pack_bool(value: bool) -> bytes:
    return b"\x01" if value else b"\x00"


def pack_short_string(value: str, path: str) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) > 255:
        fail(f"{path}: string is too long for hUGETracker ShortString ({len(encoded)} bytes)")
    return bytes([len(encoded)]) + encoded + bytes(255 - len(encoded))


def pack_ansi_string(value: str, path: str) -> bytes:
    encoded = value.encode("utf-8")
    return pack_int(len(encoded)) + encoded


def pack_cell(cell: Cell) -> bytes:
    return b"".join(
        [
            pack_int(cell.note),
            pack_int(cell.instrument),
            pack_int(cell.volume),
            pack_int(cell.effect_code),
            bytes([cell.effect_param]),
        ]
    )


def blank_pattern() -> list[Cell]:
    return [Cell() for _ in range(PATTERN_ROWS)]


def pack_pattern(pattern: list[Cell]) -> bytes:
    if len(pattern) != PATTERN_ROWS:
        fail(f"internal error: pattern must have {PATTERN_ROWS} rows")
    return b"".join(pack_cell(cell) for cell in pattern)


def parse_note(note: Any, path: str) -> int:
    value = expect_string(note, path)
    if value == "rest":
        return NO_NOTE

    if len(value) not in (2, 3):
        fail(f"{path}: invalid note '{value}'")

    if len(value) == 2:
        name = value[0]
        octave_text = value[1]
        accidental = ""
    else:
        name = value[0]
        accidental = value[1]
        octave_text = value[2]

    semitones = {
        "C": 0,
        "D": 2,
        "E": 4,
        "F": 5,
        "G": 7,
        "A": 9,
        "B": 11,
    }
    if name not in semitones:
        fail(f"{path}: invalid note name '{value}'")
    if accidental not in ("", "#"):
        fail(f"{path}: only sharp notes with # are supported, got '{value}'")
    if not octave_text.isdigit():
        fail(f"{path}: invalid octave in note '{value}'")

    octave = int(octave_text)
    semitone = semitones[name] + (1 if accidental == "#" else 0)
    note_number = (octave - 3) * 12 + semitone
    if note_number < 0 or note_number > 71:
        fail(f"{path}: note '{value}' is out of supported range C3-B8")
    return note_number


def validate_instrument_id(value: Any, path: str) -> int:
    instrument = expect_int(value, path)
    if instrument < 1 or instrument > INSTRUMENT_COUNT:
        fail(f"{path}: instrument id must be 1-15; 0 is reserved for no instrument")
    return instrument


def instrument_bank_for_channel(channel: str) -> str:
    if channel in ("pulse1", "pulse2"):
        return "duty"
    if channel == "wave":
        return "wave"
    if channel == "noise":
        return "noise"
    fail(f"unsupported channel '{channel}'")


def validate_range(value: int, path: str, minimum: int, maximum: int) -> int:
    if value < minimum or value > maximum:
        fail(f"{path}: expected {minimum}-{maximum}, got {value}")
    return value


def parse_envelope_direction(value: Any, path: str, default: int) -> int:
    if value is None:
        return default
    direction = expect_string(value, path)
    if direction == "up":
        return ST_UP
    if direction == "down":
        return ST_DOWN
    fail(f"{path}: expected 'up' or 'down'")


def default_duty_values(instrument_id: int) -> tuple[str, int, int]:
    return DEFAULT_DUTY_NAMES.get(instrument_id, ("", 2, 0))


def validate_json_version(data: dict[str, Any]) -> int:
    version = expect_int(data.get("version"), "version")
    if version not in SUPPORTED_JSON_VERSIONS:
        supported = ", ".join(str(item) for item in SUPPORTED_JSON_VERSIONS)
        fail(f"version: expected one of {supported}, got {version}")
    return version


PULSE_VERSION_2_FIELDS = (
    "length",
    "length_enable",
    "sweep_time",
    "sweep_direction",
    "sweep_shift",
)


def reject_version_2_instrument_fields(
    instrument: dict[str, Any],
    path: str,
) -> None:
    for field in PULSE_VERSION_2_FIELDS:
        if field in instrument:
            fail(f"{path}.{field}: Version 2専用項目はVersion 1では使用できません")


def reject_wave_instrument_fields(
    instrument: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    description: str,
) -> None:
    for field in fields:
        if field in instrument:
            fail(f"{path}.{field}: Wave Instrumentでは使用できません（{description}）")


def validate_wave_tables(
    data: dict[str, Any],
    version: int,
) -> tuple[WaveTableSpec, ...] | None:
    if version == JSON_VERSION:
        return None

    if "wave_tables" not in data:
        return None

    wave_tables = expect_list(data["wave_tables"], "wave_tables")
    if len(wave_tables) > WAVE_COUNT:
        fail(f"wave_tables: at most {WAVE_COUNT} tables are allowed")

    wave_tables_specs: list[WaveTableSpec] = []
    known_fields = {"name", "samples"}
    name_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    for index, item in enumerate(wave_tables):
        path = f"wave_tables[{index}]"
        table = expect_dict(item, path)
        for key in table:
            if key not in known_fields:
                fail(f"{path}.{key}: unknown Wave table field")
        name = expect_string(table.get("name"), f"{path}.name")
        if not name or not name.strip():
            fail(f"{path}.name: must not be empty or whitespace")
        if name != name.strip():
            fail(f"{path}.name: leading or trailing whitespace is not allowed")
        if not name_pattern.fullmatch(name):
            fail(f"{path}.name: must match ^[a-z][a-z0-9_]*$")
        if any(spec.name == name for spec in wave_tables_specs):
            fail(f"{path}.name: duplicate Wave table name '{name}'")
        samples = expect_list(table.get("samples"), f"{path}.samples")
        if len(samples) != WAVE_BYTES:
            fail(f"{path}.samples: expected exactly {WAVE_BYTES} samples")
        validated_samples = tuple(
            validate_range(
                expect_int(sample, f"{path}.samples[{sample_index}]"),
                f"{path}.samples[{sample_index}]",
                0,
                15,
            )
            for sample_index, sample in enumerate(samples)
        )
        wave_tables_specs.append(
            WaveTableSpec(name=name, index=index, samples=validated_samples)
        )

    return tuple(wave_tables_specs)


def build_waveform_index(
    wave_tables: tuple[WaveTableSpec, ...] | None,
) -> dict[str, int] | None:
    if wave_tables is None:
        return None
    return {wave_table.name: wave_table.index for wave_table in wave_tables}


def validate_wave_instrument(
    instrument: dict[str, Any],
    path: str,
    version: int,
    waveform_index: dict[str, int] | None,
) -> tuple[str | None, int | None, int, int, bool]:
    if version == JSON_VERSION:
        reject_wave_instrument_fields(
            instrument,
            path,
            WAVE_VERSION_2_FIELDS,
            "Version 2専用項目のためVersion 1では使用できません",
        )
        return None, None, 1, 0, False

    reject_wave_instrument_fields(instrument, path, WAVE_PULSE_ONLY_FIELDS, "Pulse専用項目")
    reject_wave_instrument_fields(instrument, path, WAVE_NOISE_ONLY_FIELDS, "Noise専用項目")
    reject_wave_instrument_fields(instrument, path, WAVE_UNSUPPORTED_FIELDS, "Wave Instrumentでは公開しない項目")

    waveform = expect_string(instrument.get("waveform"), f"{path}.waveform")
    if not waveform:
        fail(f"{path}.waveform: must not be empty")
    if waveform != waveform.strip():
        fail(f"{path}.waveform: leading or trailing whitespace is not allowed")
    if waveform_index is None or not waveform_index:
        fail(f"{path}.waveform: referenced Wave table '{waveform}' does not exist")
    if waveform not in waveform_index:
        fail(f"{path}.waveform: referenced Wave table '{waveform}' does not exist")

    output_level_name = instrument.get("output_level", "100%")
    output_level_name = expect_string(output_level_name, f"{path}.output_level")
    if output_level_name not in WAVE_OUTPUT_LEVELS:
        allowed = ", ".join(WAVE_OUTPUT_LEVELS)
        fail(f"{path}.output_level: expected one of {allowed}")

    length = validate_range(
        expect_optional_int(instrument.get("length"), f"{path}.length", 0),
        f"{path}.length",
        0,
        255,
    )
    length_enable = expect_optional_bool(
        instrument.get("length_enable"),
        f"{path}.length_enable",
        False,
    )
    return waveform, waveform_index[waveform], WAVE_OUTPUT_LEVELS[output_level_name], length, length_enable


def validate_instruments(data: dict[str, Any]) -> dict[str, dict[int, InstrumentSpec]]:
    version = validate_json_version(data)
    wave_tables = validate_wave_tables(data, version)
    waveform_index = build_waveform_index(wave_tables)
    result: dict[str, dict[int, InstrumentSpec]] = {"duty": {}, "wave": {}, "noise": {}}
    instruments = expect_list(data.get("instruments"), "instruments")
    for index, item in enumerate(instruments):
        path = f"instruments[{index}]"
        instrument = expect_dict(item, path)
        instrument_id = validate_instrument_id(instrument.get("id"), f"{path}.id")
        name = expect_string(instrument.get("name"), f"{path}.name")
        channel = expect_string(instrument.get("channel"), f"{path}.channel")
        if channel not in CHANNELS:
            fail(f"{path}.channel: expected one of {', '.join(CHANNELS)}")
        bank = instrument_bank_for_channel(channel)
        if instrument_id in result[bank]:
            fail(f"{path}.id: duplicate instrument id {instrument_id} in {bank} bank")

        if channel == "wave":
            waveform, resolved_waveform_index, output_level, length, length_enable = validate_wave_instrument(
                instrument,
                path,
                version,
                waveform_index,
            )
            result[bank][instrument_id] = InstrumentSpec(
                id=instrument_id,
                name=name,
                channel=channel,
                bank=bank,
                duty=0,
                initial_volume=15,
                vol_sweep_direction=ST_DOWN,
                vol_sweep_amount=0,
                length=length,
                length_enable=length_enable,
                json_version=version,
                waveform=waveform,
                waveform_index=resolved_waveform_index,
                output_level=output_level,
            )
            continue

        if version == JSON_VERSION and channel in ("pulse1", "pulse2"):
            reject_version_2_instrument_fields(instrument, path)

        default_name, default_duty, default_sweep = default_duty_values(instrument_id)
        duty = validate_range(
            expect_optional_int(instrument.get("duty"), f"{path}.duty", default_duty),
            f"{path}.duty",
            0,
            3,
        )
        initial_volume = validate_range(
            expect_optional_int(instrument.get("initial_volume"), f"{path}.initial_volume", 15),
            f"{path}.initial_volume",
            0,
            15,
        )
        vol_sweep_direction = parse_envelope_direction(
            instrument.get("envelope_direction"),
            f"{path}.envelope_direction",
            ST_DOWN,
        )
        vol_sweep_amount = validate_range(
            expect_optional_int(instrument.get("envelope_sweep"), f"{path}.envelope_sweep", default_sweep),
            f"{path}.envelope_sweep",
            0,
            7,
        )

        length = 0
        length_enable = False
        sweep_time = 0
        sweep_direction = ST_DOWN
        sweep_shift = 0

        if version == 2 and channel in ("pulse1", "pulse2"):
            length = validate_range(
                expect_optional_int(instrument.get("length"), f"{path}.length", 0),
                f"{path}.length",
                0,
                63,
            )
            length_enable = expect_optional_bool(
                instrument.get("length_enable"),
                f"{path}.length_enable",
                False,
            )

            if channel == "pulse1":
                sweep_time = validate_range(
                    expect_optional_int(instrument.get("sweep_time"), f"{path}.sweep_time", 0),
                    f"{path}.sweep_time",
                    0,
                    7,
                )
                sweep_direction = parse_envelope_direction(
                    instrument.get("sweep_direction"),
                    f"{path}.sweep_direction",
                    ST_DOWN,
                )
                sweep_shift = validate_range(
                    expect_optional_int(instrument.get("sweep_shift"), f"{path}.sweep_shift", 0),
                    f"{path}.sweep_shift",
                    0,
                    7,
                )
            else:
                for field in ("sweep_time", "sweep_direction", "sweep_shift"):
                    if field in instrument:
                        fail(f"{path}.{field}: pulse1でのみ使用可能です（pulse2では指定禁止）")

        has_duty_detail = "duty" in instrument
        if bank != "duty" and has_duty_detail:
            fail(f"{path}: duty is only supported for pulse1/pulse2")

        result[bank][instrument_id] = InstrumentSpec(
            id=instrument_id,
            name=name or default_name,
            channel=channel,
            bank=bank,
            duty=duty,
            initial_volume=initial_volume,
            vol_sweep_direction=vol_sweep_direction,
            vol_sweep_amount=vol_sweep_amount,
            length=length,
            length_enable=length_enable,
            sweep_time=sweep_time,
            sweep_direction=sweep_direction,
            sweep_shift=sweep_shift,
            json_version=version,
        )
    return result


def validate_header(data: dict[str, Any]) -> None:
    validate_json_version(data)
    expect_string(data.get("title"), "title")
    song_type = expect_string(data.get("type"), "type")
    if song_type not in ("bgm", "sfx"):
        fail("type: expected 'bgm' or 'sfx'")
    tempo = expect_int(data.get("tempo"), "tempo")
    if tempo <= 0:
        fail("tempo: must be a positive integer")
    expect_list(data.get("order"), "order")
    expect_dict(data.get("patterns"), "patterns")


def validate_event_effect(event: dict[str, Any], path: str) -> None:
    if event.get("effect") is not None:
        fail(f"{path}.effect: only null is supported in the initial version")
    if event.get("effect_param") is not None:
        fail(f"{path}.effect_param: only null is supported in the initial version")


def build_channel_pattern(events: list[Any], path: str) -> list[Cell]:
    rows: list[Cell] = []
    for index, item in enumerate(events):
        event_path = f"{path}[{index}]"
        event = expect_dict(item, event_path)
        note = parse_note(event.get("note"), f"{event_path}.note")
        length = expect_int(event.get("length"), f"{event_path}.length")
        if length < 1:
            fail(f"{event_path}.length: must be 1 or greater")
        instrument = validate_instrument_id(event.get("instrument"), f"{event_path}.instrument")
        validate_event_effect(event, event_path)

        first_instrument = 0 if note == NO_NOTE else instrument
        rows.append(Cell(note=note, instrument=first_instrument))
        for _ in range(length - 1):
            rows.append(Cell())
        if len(rows) > PATTERN_ROWS:
            fail(f"{path}: expanded pattern exceeds {PATTERN_ROWS} rows")

    rows.extend(Cell() for _ in range(PATTERN_ROWS - len(rows)))
    return rows


def build_patterns(data: dict[str, Any]) -> tuple[dict[int, list[Cell]], list[list[int]]]:
    order = expect_list(data.get("order"), "order")
    patterns_json = expect_dict(data.get("patterns"), "patterns")
    if not order:
        fail("order: at least one pattern name is required")

    patterns: dict[int, list[Cell]] = {}
    order_matrix: list[list[int]] = [[] for _ in CHANNELS]

    for order_index, pattern_name_value in enumerate(order):
        pattern_name = expect_string(pattern_name_value, f"order[{order_index}]")
        if pattern_name not in patterns_json:
            fail(f"order[{order_index}]: pattern '{pattern_name}' is not defined")
        pattern_obj = expect_dict(patterns_json[pattern_name], f"patterns.{pattern_name}")
        channels_obj = expect_dict(pattern_obj.get("channels"), f"patterns.{pattern_name}.channels")

        for channel_index, channel in enumerate(CHANNELS):
            pattern_key = order_index * len(CHANNELS) + channel_index
            events = expect_list(
                channels_obj.get(channel, []),
                f"patterns.{pattern_name}.channels.{channel}",
            )
            if events:
                patterns[pattern_key] = build_channel_pattern(
                    events,
                    f"patterns.{pattern_name}.channels.{channel}",
                )
            else:
                patterns[pattern_key] = blank_pattern()
            order_matrix[channel_index].append(pattern_key)

    return patterns, order_matrix


def pack_instrument(
    type_: int,
    name: str,
    *,
    length: int = 0,
    length_enabled: bool = False,
    initial_volume: int = 0,
    vol_sweep_direction: int = ST_DOWN,
    vol_sweep_amount: int = 0,
    sweep_time: int = 0,
    sweep_inc_dec: int = ST_DOWN,
    sweep_shift: int = 0,
    duty: int = 0,
    output_level: int = 0,
    waveform: int = 0,
    counter_step: int = SW_FIFTEEN,
    subpattern_enabled: bool = False,
) -> bytes:
    parts = [
        pack_int(type_),
        pack_short_string(name, "instrument.name"),
        pack_int(length),
        pack_bool(length_enabled),
        bytes([initial_volume]),
        pack_int(vol_sweep_direction),
        bytes([vol_sweep_amount]),
        pack_int(sweep_time),
        pack_int(sweep_inc_dec),
        pack_int(sweep_shift),
        bytes([duty]),
        pack_int(output_level),
        pack_int(waveform),
        pack_int(counter_step),
        pack_bool(subpattern_enabled),
        pack_pattern(blank_pattern()),
    ]
    return b"".join(parts)


def wave_instrument_packing_values(
    instrument_id: int,
    spec: InstrumentSpec | None,
) -> tuple[str, int, bool, int, int]:
    default_name = DEFAULT_WAVE_NAMES.get(instrument_id, "")
    if spec is None or spec.json_version != 2:
        return default_name, 0, False, 1, instrument_id - 1

    waveform_index = spec.waveform_index
    if waveform_index is None:
        raise ValueError(
            f"Wave Instrument {instrument_id}: waveform_index is unresolved"
        )
    if type(waveform_index) is not int or not 0 <= waveform_index < WAVE_COUNT:
        raise ValueError(
            f"Wave Instrument {instrument_id}: waveform_index must be an integer 0-{WAVE_COUNT - 1}"
        )
    return (
        spec.name,
        spec.length,
        spec.length_enable,
        spec.output_level,
        waveform_index,
    )


def pack_instruments(overrides: dict[str, dict[int, InstrumentSpec]]) -> bytes:
    parts: list[bytes] = []

    for instrument_id in range(1, INSTRUMENT_COUNT + 1):
        default_name, duty, vol_sweep_amount = DEFAULT_DUTY_NAMES.get(
            instrument_id,
            ("", 2, 0),
        )
        spec = overrides["duty"].get(instrument_id)
        name = spec.name if spec else default_name
        initial_volume = spec.initial_volume if spec else 15
        vol_sweep_direction = spec.vol_sweep_direction if spec else ST_DOWN
        vol_sweep_amount = spec.vol_sweep_amount if spec else vol_sweep_amount
        duty = spec.duty if spec else duty
        if spec and spec.json_version == 2:
            length = spec.length
            length_enabled = spec.length_enable
            sweep_time = spec.sweep_time
            sweep_inc_dec = spec.sweep_direction
            sweep_shift = spec.sweep_shift
        else:
            # Keep the Version 1 packing behavior, where the existing envelope
            # direction also supplied the legacy SweepIncDec field.
            length = 0
            length_enabled = False
            sweep_time = 0
            sweep_inc_dec = vol_sweep_direction
            sweep_shift = 0
        parts.append(
            pack_instrument(
                IT_SQUARE,
                name,
                length=length,
                length_enabled=length_enabled,
                initial_volume=initial_volume,
                vol_sweep_direction=vol_sweep_direction,
                vol_sweep_amount=vol_sweep_amount,
                sweep_time=sweep_time,
                sweep_inc_dec=sweep_inc_dec,
                sweep_shift=sweep_shift,
                duty=duty,
                output_level=1,
            )
        )

    for instrument_id in range(1, INSTRUMENT_COUNT + 1):
        spec = overrides["wave"].get(instrument_id)
        name, length, length_enabled, output_level, waveform = wave_instrument_packing_values(
            instrument_id,
            spec,
        )
        parts.append(
            pack_instrument(
                IT_WAVE,
                name,
                length=length,
                length_enabled=length_enabled,
                output_level=output_level,
                waveform=waveform,
            )
        )

    for instrument_id in range(1, INSTRUMENT_COUNT + 1):
        spec = overrides["noise"].get(instrument_id)
        name = spec.name if spec else ""
        parts.append(
            pack_instrument(
                IT_NOISE,
                name,
                initial_volume=15,
                vol_sweep_direction=ST_DOWN,
                counter_step=SW_FIFTEEN,
            )
        )

    return b"".join(parts)


def pack_waves() -> bytes:
    waves = [bytes(wave) for wave in DEFAULT_WAVES]
    while len(waves) < WAVE_COUNT:
        waves.append(bytes(WAVE_BYTES))
    return b"".join(waves)


def build_uge(data: dict[str, Any]) -> bytes:
    validate_header(data)
    instruments = validate_instruments(data)
    patterns, order_matrix = build_patterns(data)

    output = bytearray()
    output += pack_int(SONG_VERSION)
    output += pack_short_string(expect_string(data["title"], "title"), "title")
    output += pack_short_string("", "artist")
    output += pack_short_string("", "comment")
    output += pack_instruments(instruments)
    output += pack_waves()
    output += pack_int(expect_int(data["tempo"], "tempo"))
    output += pack_bool(False)
    output += pack_int(0)

    output += pack_int(len(patterns))
    for key in sorted(patterns):
        output += pack_int(key)
        output += pack_pattern(patterns[key])

    for channel_orders in order_matrix:
        stored_orders = channel_orders + [0]
        output += pack_int(len(stored_orders))
        for pattern_key in stored_orders:
            output += pack_int(pattern_key)

    for index in range(16):
        output += pack_ansi_string("", f"routines[{index}]")

    return bytes(output)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}")
    return expect_dict(data, str(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Pocket Sweeper music definition JSON into hUGETracker .uge Version 6."
    )
    parser.add_argument("input_json", type=Path, help="Input music definition JSON")
    parser.add_argument("output_uge", type=Path, help="Output .uge file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        data = load_json(args.input_json)
        uge = build_uge(data)
        args.output_uge.parent.mkdir(parents=True, exist_ok=True)
        args.output_uge.write_bytes(uge)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"input: {args.input_json}")
    print(f"output: {args.output_uge}")
    print(f"bytes: {len(uge)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
