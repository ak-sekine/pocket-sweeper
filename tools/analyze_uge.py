#!/usr/bin/env python3
"""Read the structural fields needed from a hUGETracker Song Version 6 UGE."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

SONG_VERSION = 6
CHANNELS = ("ch1", "ch2", "ch3", "ch4")
NO_NOTE = 90
PATTERN_ROWS = 64
INSTRUMENTS_PER_BANK = 15
INSTRUMENT_SIZE = 1385
WAVE_BANK_SIZE = 16 * 32
HEADER_SIZE_AFTER_VERSION = 3 * 256
CELL_SIZE = 17


class UgeError(ValueError):
    """Raised when a UGE is truncated or has an unsupported structure."""


class Reader:
    def __init__(self, data: bytes, path: Path) -> None:
        self.data = data
        self.path = path
        self.offset = 0

    def take(self, size: int) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise UgeError(f"{self.path}: truncated at offset {self.offset}")
        result = self.data[self.offset:end]
        self.offset = end
        return result

    def int32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def byte(self) -> int:
        return self.take(1)[0]

    def short_string(self) -> str:
        raw = self.take(256)
        length = raw[0]
        return raw[1 : 1 + length].decode("utf-8", "replace")


def cell_is_non_empty(cell: tuple[int, int, int, int, int]) -> bool:
    note, instrument, volume, effect, effect_param = cell
    return note != NO_NOTE or any((instrument, volume, effect, effect_param))


def classify_loop(position_jumps: list[dict[str, int | str]], order_count: int) -> dict[str, Any]:
    """Classify B-effect control flow without guessing a complex loop range."""
    targets = sorted({int(jump["target_order"]) for jump in position_jumps})
    sources = sorted({int(jump["source_order"]) for jump in position_jumps})
    channels = sorted({str(jump["channel"]) for jump in position_jumps})
    invalid = [
        jump
        for jump in position_jumps
        if int(jump["raw_target_order"]) > order_count
        or int(jump["raw_target_order"]) < 0
        or int(jump["source_order"]) >= order_count
        or int(jump["source_order"]) < 0
        or int(jump["target_order"]) > int(jump["source_order"])
    ]
    sources_agree = len(sources) <= 1
    targets_agree = len(targets) <= 1
    channels_agree = len(channels) <= 1 or (sources_agree and targets_agree)
    simple = bool(position_jumps) and not invalid and sources_agree and targets_agree
    common = {
        "position_jumps": position_jumps,
        "channels_agree": channels_agree,
        "sources_agree": sources_agree,
        "targets_agree": targets_agree,
    }
    if invalid:
        return {
            **common,
            "present": False,
            "kind": "invalid_position_jump",
            "simple_loop": False,
            "reason": "position jump target/source is out of range or jumps forward",
            "start_order": None,
            "end_order_inclusive": None,
            "intro_order_count": None,
            "loop_order_count": None,
            "reachable_order_range": None,
            "unreachable_orders": None,
            "unreachable_order_count": None,
        }
    if simple:
        start_order = targets[0]
        end_order = sources[0]
        unreachable = list(range(end_order + 1, order_count))
        return {
            **common,
            "present": True,
            "kind": "explicit_simple_loop",
            "simple_loop": True,
            "reason": "all position jumps share one target and source order",
            "start_order": start_order,
            "end_order_inclusive": end_order,
            "intro_order_count": start_order,
            "loop_order_count": end_order - start_order + 1,
            "reachable_order_range": [0, end_order],
            "unreachable_orders": unreachable,
            "unreachable_order_count": len(unreachable),
        }
    if position_jumps:
        return {
            **common,
            "present": False,
            "kind": "complex_position_jumps",
            "simple_loop": False,
            "reason": "multiple source/target orders or channel control paths",
            "start_order": None,
            "end_order_inclusive": None,
            "intro_order_count": None,
            "loop_order_count": None,
            "reachable_order_range": None,
            "unreachable_orders": None,
            "unreachable_order_count": None,
        }
    end_order = max(0, order_count - 1)
    return {
        **common,
        "present": True,
        "kind": "implicit_full_order_cycle",
        "simple_loop": True,
        "position_jumps": [],
        "reason": "no B position jump; hUGEDriver advances to the next order and wraps",
        "start_order": 0,
        "end_order_inclusive": end_order,
        "intro_order_count": 0,
        "loop_order_count": order_count,
        "reachable_order_range": [0, end_order],
        "unreachable_orders": [],
        "unreachable_order_count": 0,
    }


def read_file(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    reader = Reader(data, path)
    version = reader.int32()
    title = reader.short_string()
    artist = reader.short_string()
    comment = reader.short_string()
    if version != SONG_VERSION:
        raise UgeError(f"{path}: unsupported Song Version {version}; expected {SONG_VERSION}")

    reader.take(INSTRUMENTS_PER_BANK * 3 * INSTRUMENT_SIZE)
    reader.take(WAVE_BANK_SIZE)
    tempo = reader.int32()
    reader.byte()  # preview flag
    reader.int32()  # restart position, unused by this report

    pattern_count = reader.int32()
    if pattern_count < 0:
        raise UgeError(f"{path}: negative pattern count")
    patterns: dict[int, list[tuple[int, int, int, int, int]]] = {}
    for _ in range(pattern_count):
        key = reader.int32()
        patterns[key] = [
            struct.unpack("<4iB", reader.take(CELL_SIZE))
            for _ in range(PATTERN_ROWS)
        ]

    orders: list[list[int]] = []
    for _ in CHANNELS:
        stored_count = reader.int32()
        if stored_count < 1:
            raise UgeError(f"{path}: invalid order count {stored_count}")
        values = [reader.int32() for _ in range(stored_count)]
        if values[-1] != 0:
            raise UgeError(f"{path}: order list has no zero terminator")
        orders.append(values[:-1])

    for channel, channel_orders in zip(CHANNELS, orders):
        for order_index, pattern_key in enumerate(channel_orders):
            if pattern_key not in patterns:
                raise UgeError(
                    f"{path}: {channel} order {order_index} references missing pattern {pattern_key}"
                )

    # The generated Song Version 6 files have 16 ANSI routine records.
    routines: list[str] = []
    for _ in range(16):
        length = reader.int32()
        if length < 0:
            raise UgeError(f"{path}: negative routine length")
        routines.append(reader.take(length).decode("utf-8", "replace"))

    if reader.offset != len(data):
        raise UgeError(f"{path}: {len(data) - reader.offset} trailing bytes")

    channel_reports: dict[str, dict[str, Any]] = {}
    position_jumps: list[dict[str, int | str]] = []
    for channel, channel_orders in zip(CHANNELS, orders):
        references = list(dict.fromkeys(channel_orders))
        non_empty_patterns = [
            key for key in references if any(cell_is_non_empty(cell) for cell in patterns[key])
        ]
        loop_patterns: list[int] = []
        event_count = 0
        for order_index, pattern_key in enumerate(channel_orders):
            for row_index, cell in enumerate(patterns[pattern_key]):
                if cell_is_non_empty(cell):
                    event_count += 1
                if cell[3] == 0x0B:
                    # hUGEDriver's B effect stores the target order as a
                    # one-based value; zero is the special full-cycle target.
                    position_jumps.append(
                        {
                            "channel": channel,
                            "channel_index": CHANNELS.index(channel),
                            "source_order": order_index,
                            "source_row": row_index,
                            # Legacy aliases retained for the existing JSON shape.
                            "order": order_index,
                            "row": row_index,
                            "raw_target_order": cell[4],
                            "target_order": max(0, cell[4] - 1),
                        }
                    )
                    loop_patterns.append(pattern_key)
        channel_reports[channel] = {
            "order_count": len(channel_orders),
            "order_pattern_keys": channel_orders,
            "unique_patterns": len(references),
            "unique_pattern_keys": references,
            "non_empty_patterns": len(non_empty_patterns),
            "non_empty_pattern_keys": non_empty_patterns,
            "loop_pattern_keys": sorted(set(loop_patterns)),
            "position_jumps": [],
            "event_count": event_count,
            "used": bool(non_empty_patterns),
        }

    order_counts = [len(values) for values in orders]
    if len(set(order_counts)) != 1:
        order_alignment = "不一致"
    else:
        order_alignment = "一致"
    order_count = order_counts[0] if order_counts else 0
    for jump in position_jumps:
        channel_reports[str(jump["channel"])]["position_jumps"].append(jump)

    loop = classify_loop(position_jumps, order_count)

    loop_start = loop["start_order"]
    loop_end = loop["end_order_inclusive"]
    for channel, channel_orders in zip(CHANNELS, orders):
        channel_report = channel_reports[channel]
        if loop_start is None or loop_end is None:
            channel_report["loop_order_pattern_keys"] = None
            channel_report["loop_unique_patterns"] = None
            channel_report["loop_non_empty_patterns"] = None
            channel_report["loop_non_empty_pattern_keys"] = None
            channel_report["loop_event_count"] = None
            channel_report["pattern_reuse_in_orders"] = None
            channel_report["unreachable_order_pattern_keys"] = None
            continue
        loop_order_keys = channel_orders[loop_start : loop_end + 1]
        loop_unique = list(dict.fromkeys(loop_order_keys))
        loop_non_empty = [
            key for key in loop_unique if any(cell_is_non_empty(cell) for cell in patterns[key])
        ]
        counts = {key: loop_order_keys.count(key) for key in loop_unique}
        channel_report["loop_order_pattern_keys"] = loop_order_keys
        channel_report["loop_unique_patterns"] = len(loop_unique)
        channel_report["loop_non_empty_patterns"] = len(loop_non_empty)
        channel_report["loop_non_empty_pattern_keys"] = loop_non_empty
        channel_report["loop_event_count"] = sum(
            1
            for key in loop_order_keys
            for cell in patterns[key]
            if cell_is_non_empty(cell)
        )
        channel_report["pattern_reuse_in_orders"] = sorted(
            key for key, count in counts.items() if count > 1
        )
        unreachable = loop.get("unreachable_orders") or []
        channel_report["unreachable_order_pattern_keys"] = [
            {"order": index, "pattern_key": channel_orders[index]}
            for index in unreachable
        ]

    return {
        "file": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "song_version": {"raw": version, "interpreted": str(version), "supported": True},
        "internal_song_name": title,
        "artist": artist,
        "comment": comment,
        "tempo_raw": tempo,
        "pattern_count": pattern_count,
        "channels": channel_reports,
        "order_count": order_count,
        "order_counts": order_counts,
        "order_alignment": order_alignment,
        "loop": loop,
        "routine_count": len(routines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Song Version 6 UGE files")
    parser.add_argument("--output", type=Path, help="Write deterministic JSON instead of stdout")
    args = parser.parse_args()
    reports = [read_file(path) for path in sorted(args.files)]
    output = json.dumps(reports, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
