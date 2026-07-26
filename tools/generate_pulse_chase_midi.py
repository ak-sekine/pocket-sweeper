#!/usr/bin/env python3
"""Generate and validate the completed Pulse Chase comparison MIDI.

The file deliberately uses only the Python standard library so the asset can
be regenerated in a clean checkout without installing a MIDI package.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

PPQ = 480
EIGHTH = PPQ // 2
BAR = PPQ * 4
TEMPO_US = 441_176  # 136 BPM, rounded to the nearest microsecond
BARS = 24


def vlq(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def track(name: str, channel: int, program: int, notes: list[tuple[int, int, int, int]], drum=False) -> bytes:
    events: list[tuple[int, int, bytes]] = [(0, 0, b"\xff\x03" + bytes([len(name)]) + name.encode())]
    if not drum:
        events.append((0, 1, bytes([0xC0 | channel, program])))
    for start, pitch, duration, velocity in notes:
        events.append((start, 2, bytes([0x90 | channel, pitch, velocity])))
        events.append((start + duration, 1, bytes([0x80 | channel, pitch, 0])))
    events.sort(key=lambda item: (item[0], item[1]))
    data = bytearray()
    previous = 0
    for tick, _, message in events:
        data += vlq(tick - previous) + message
        previous = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def make_notes() -> dict[str, list[tuple[int, int, int, int]]]:
    # Each eight-bar section keeps the original 2–4 note cell but changes its
    # direction, register, rests, and cadence. Chords are Em-D-C-Bm per bar.
    roots = [40, 38, 36, 35]  # E2, D2, C2, B1
    melody_cells = [
        ([76, 79, 83, 79], [0, 1, 2, 3], 0),
        ([79, 83, 81, 79], [0, 1, 3, 5], 1),
        ([83, 81, 79, 76], [0, 2, 3, 5], 0),
        ([79, 76, 74, 71], [0, 1, 3, 5], 2),
        ([76, 79, 83, 86], [0, 1, 2, 4], 0),
        ([86, 83, 81, 79], [0, 2, 3, 5], 1),
        ([83, 79, 76, 74], [0, 1, 3, 4], 0),
        ([79, 76, 74, 71], [0, 2, 3, 5], 3),
    ]
    melody: list[tuple[int, int, int, int]] = []
    bass: list[tuple[int, int, int, int]] = []
    support: list[tuple[int, int, int, int]] = []
    rhythm: list[tuple[int, int, int, int]] = []
    for bar in range(BARS):
        section = bar % 8
        cell, positions, variant = melody_cells[section]
        base = bar * BAR
        for i, position in enumerate(positions):
            pitch = cell[i] + (12 if bar // 8 == 1 and i == 0 else 0)
            melody.append((base + position * EIGHTH, pitch, 150 if i != 3 else 220, 88 if variant else 96))
        root = roots[bar % 4]
        for offset, pitch in [(0, root), (2, root + 7), (4, root + 12), (6, root + 7)]:
            bass.append((base + offset * EIGHTH, pitch, 190, 78 if offset else 88))
        # Weak-beat answers; never duplicate the melody's contour.
        for offset, pitch in ((3, root + 19), (7, root + 16)):
            if not (bar % 8 == 7 and offset == 7):
                support.append((base + offset * EIGHTH, pitch, 110, 54))
        for offset in (0, 2, 4, 6):
            rhythm.append((base + offset * EIGHTH, 36 if offset in (0, 4) else 42, 80, 48 if offset else 60))
        for offset in (2, 6):
            rhythm.append((base + offset * EIGHTH, 38, 80, 52))
    return {"melody": melody, "bass": bass, "support": support, "rhythm": rhythm}


def make_midi() -> bytes:
    tracks = [
        b"MTrk" + struct.pack(">I", 19) + b"\x00\xff\x51\x03" + TEMPO_US.to_bytes(3, "big") + b"\x00\xff\x58\x04\x04\x02\x18\x08\x00\xff\x2f\x00",
    ]
    channels = [("melody", 0, 80), ("bass", 1, 38), ("support", 2, 81), ("rhythm", 9, 0)]
    notes = make_notes()
    tracks += [track(name, channel, program, notes[name], channel == 9) for name, channel, program in channels]
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    return header + b"".join(tracks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_bytes(make_midi())
    print(f"wrote {args.output} ({BARS} bars, 136 BPM, loop bars 1-{BARS})")


if __name__ == "__main__":
    main()
