#!/usr/bin/env python3
"""Deterministic MIDI -> MusicXML -> normalized score -> GB JSON prototype.

This is deliberately a small, dependency-free adapter for the selected Mutopia
SMF. It is not a general MIDI notation engraver: repeat/ending semantics and
human engraving are reported as lost/unknown rather than guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json_to_uge


SOURCE_URL = "https://www.mutopiaproject.org/ftp/JoplinS/maple/maple.mid"
SOURCE_ID = "Mutopia-2011/11/13-23"
EXPECTED_SOURCE_SHA256 = "3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66"
TICKS_PER_ROW = 6
GRID_TICKS = 30
PATTERN_ROWS = 64


@dataclass(frozen=True)
class MidiNote:
    track: int
    event_id: str
    start: int
    end: int
    pitch: int
    velocity: int


@dataclass(frozen=True)
class MidiTrack:
    index: int
    name: str
    notes: tuple[MidiNote, ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def varlen(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos


def read_midi(path: Path) -> tuple[int, list[MidiTrack], dict[str, Any]]:
    data = path.read_bytes()
    if data[:4] != b"MThd":
        raise ValueError("source is not a Standard MIDI File")
    header_len, fmt, count, division = struct.unpack(">IHHH", data[4:14])
    if header_len != 6 or division & 0x8000:
        raise ValueError("only SMF PPQ timing is supported")
    pos = 14
    tracks: list[MidiTrack] = []
    tempo: list[dict[str, int]] = []
    meters: list[dict[str, int]] = []
    active: dict[tuple[int, int], tuple[int, int, str]] = {}
    for track_index in range(count):
        if data[pos:pos + 4] != b"MTrk":
            raise ValueError(f"missing MTrk at track {track_index}")
        length = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 8 + length
        cursor = 0
        tick = 0
        running = None
        name = f"track_{track_index}"
        notes: list[MidiNote] = []
        event_counter = 0
        while cursor < len(chunk):
            delta, cursor = varlen(chunk, cursor)
            tick += delta
            status = chunk[cursor]
            if status < 0x80:
                if running is None:
                    raise ValueError("running status without previous status")
                status = running
            else:
                cursor += 1
                if status < 0xF0:
                    running = status
            if status == 0xFF:
                kind = chunk[cursor]
                cursor += 1
                size, cursor = varlen(chunk, cursor)
                payload = chunk[cursor:cursor + size]
                cursor += size
                if kind == 0x03:
                    name = payload.decode("latin-1", errors="replace") or name
                elif kind == 0x51 and size == 3:
                    tempo.append({"track": track_index, "tick": tick, "microseconds_per_quarter": int.from_bytes(payload, "big")})
                elif kind == 0x58 and size >= 2:
                    meters.append({"track": track_index, "tick": tick, "beats": payload[0], "beat_type": 2 ** payload[1]})
                continue
            if status in (0xF0, 0xF7):
                size, cursor = varlen(chunk, cursor)
                cursor += size
                continue
            channel = status & 0x0F
            kind = status & 0xF0
            width = 1 if kind in (0xC0, 0xD0) else 2
            first = chunk[cursor]
            cursor += 1
            second = None
            if width == 2:
                second = chunk[cursor]
                cursor += 1
            if kind == 0x90 and second and second > 0:
                event_id = f"midi:t{track_index}:e{event_counter}"
                active[(channel, first)] = (tick, second, event_id)
                event_counter += 1
            elif kind in (0x80, 0x90):
                started = active.pop((channel, first), None)
                if started:
                    start, velocity, event_id = started
                    notes.append(MidiNote(track_index, event_id, start, max(start + 1, tick), first, velocity))
        for (channel, pitch), (start, velocity, event_id) in sorted(active.items()):
            if any(note.track == track_index and note.event_id == event_id for note in notes):
                continue
            notes.append(MidiNote(track_index, event_id, start, max(start + 1, tick), pitch, velocity))
        tracks.append(MidiTrack(track_index, name, tuple(sorted(notes, key=lambda n: (n.start, n.pitch, n.event_id)))))
    return division, tracks, {"format": fmt, "tempo": sorted(tempo, key=lambda x: (x["tick"], x["track"])), "meters": sorted(meters, key=lambda x: (x["tick"], x["track"]))}


def pitch_name(pitch: int) -> tuple[str, int]:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return names[pitch % 12], pitch // 12 - 1


def json_note_name(pitch: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[pitch % 12]}{pitch // 12 - 1}"


def write_musicxml(path: Path, ppq: int, tracks: list[MidiTrack], meta: dict[str, Any]) -> None:
    root = ET.Element("score-partwise", version="4.0")
    ET.SubElement(root, "work").append(ET.Element("work-title"))
    root.find("work/work-title").text = "Maple Leaf Rag (MIDI-derived prototype encoding)"
    identification = ET.SubElement(root, "identification")
    ET.SubElement(identification, "creator", type="composer").text = "Scott Joplin"
    ET.SubElement(identification, "encoding").append(ET.Element("software"))
    root.find("identification/encoding/software").text = "pocket-sweeper maple_leaf_rag_prototype"
    part_list = ET.SubElement(root, "part-list")
    for track in tracks:
        score_part = ET.SubElement(part_list, "score-part", id=f"P{track.index + 1}")
        ET.SubElement(score_part, "part-name").text = track.name
    max_tick = max((note.end for track in tracks for note in track.notes), default=0)
    beats = meta["meters"][0]["beats"] if meta["meters"] else 2
    beat_type = meta["meters"][0]["beat_type"] if meta["meters"] else 4
    # MusicXML divisions are ticks per quarter note.  A 2/4 measure is
    # therefore two quarter notes, not four.  The source starts with a
    # pickup-like offset on one part; an explicit forward preserves it.
    measure_ticks = ppq * beats * 4 // beat_type
    for track in tracks:
        part = ET.SubElement(root, "part", id=f"P{track.index + 1}")
        notes_by_start: dict[int, list[MidiNote]] = {}
        for note in track.notes:
            notes_by_start.setdefault(note.start, []).append(note)
        for number, measure_start in enumerate(range(0, max_tick + measure_ticks, measure_ticks), 1):
            measure = ET.SubElement(part, "measure", number=str(number))
            if number == 1:
                attrs = ET.SubElement(measure, "attributes")
                ET.SubElement(attrs, "divisions").text = str(ppq)
                time = ET.SubElement(attrs, "time")
                ET.SubElement(time, "beats").text = str(meta["meters"][0]["beats"] if meta["meters"] else 2)
                ET.SubElement(time, "beat-type").text = str(meta["meters"][0]["beat_type"] if meta["meters"] else 4)
                key = ET.SubElement(attrs, "key")
                ET.SubElement(key, "fifths").text = "-4"
                ET.SubElement(attrs, "staves").text = "1"
                if meta["tempo"]:
                    direction = ET.SubElement(measure, "direction", placement="above")
                    direction_type = ET.SubElement(direction, "direction-type")
                    metronome = ET.SubElement(direction_type, "metronome")
                    ET.SubElement(metronome, "beat-unit").text = "quarter"
                    ET.SubElement(metronome, "per-minute").text = str(round(60_000_000 / meta["tempo"][0]["microseconds_per_quarter"]))
            cursor = 0
            for start, notes in sorted(notes_by_start.items()):
                if not measure_start <= start < measure_start + measure_ticks:
                    continue
                local_start = start - measure_start
                saved_cursor = cursor
                if local_start > cursor:
                    forward = ET.SubElement(measure, "forward")
                    ET.SubElement(forward, "duration").text = str(local_start - cursor)
                    cursor = local_start
                elif local_start < cursor:
                    backup = ET.SubElement(measure, "backup")
                    ET.SubElement(backup, "duration").text = str(cursor - local_start)
                    cursor = local_start
                for index, note in enumerate(sorted(notes, key=lambda n: n.pitch)):
                    xml_note = ET.SubElement(measure, "note")
                    if index:
                        ET.SubElement(xml_note, "chord")
                    step, octave = pitch_name(note.pitch)
                    pitch = ET.SubElement(xml_note, "pitch")
                    ET.SubElement(pitch, "step").text = step[0]
                    if len(step) > 1:
                        ET.SubElement(pitch, "alter").text = "1"
                    ET.SubElement(pitch, "octave").text = str(octave)
                    ET.SubElement(xml_note, "duration").text = str(max(1, note.end - note.start))
                    ET.SubElement(xml_note, "voice").text = "1"
                    ET.SubElement(xml_note, "type").text = "quarter"
                    ET.SubElement(xml_note, "lyric")
                note_end = local_start + max(note.end - note.start for note in notes)
                if local_start < saved_cursor and note_end < saved_cursor:
                    forward = ET.SubElement(measure, "forward")
                    ET.SubElement(forward, "duration").text = str(saved_cursor - note_end)
                    cursor = saved_cursor
                else:
                    cursor = max(saved_cursor, note_end)
            if number == (max_tick // measure_ticks) + 1:
                ET.SubElement(measure, "barline", location="right").append(ET.Element("bar-style"))
                measure.find("barline/bar-style").text = "light-heavy"
    ET.indent(root, space="  ")
    path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def parse_musicxml(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = ET.parse(path).getroot()
    events: list[dict[str, Any]] = []
    parts = root.findall("part")
    for part_index, part in enumerate(parts):
        part_id = part.attrib.get("id", f"P{part_index + 1}")
        divisions = 1
        time = "unknown"
        key = "unknown"
        for measure in part.findall("measure"):
            attrs = measure.find("attributes")
            if attrs is not None:
                divisions = int(attrs.findtext("divisions", str(divisions)))
                time = f"{attrs.findtext('time/beats', '?')}/{attrs.findtext('time/beat-type', '?')}"
                key = attrs.findtext("key/fifths", key)
            measure_no = int(measure.attrib.get("number", "0")) if measure.attrib.get("number", "0").isdigit() else measure.attrib.get("number", "0")
            cursor = 0
            last_onset = 0
            note_index = 0
            for child in list(measure):
                if child.tag == "forward":
                    cursor += int(child.findtext("duration", "0"))
                    continue
                if child.tag == "backup":
                    cursor -= int(child.findtext("duration", "0"))
                    continue
                if child.tag != "note":
                    continue
                duration = int(child.findtext("duration", "1"))
                is_chord = child.find("chord") is not None
                onset = last_onset if is_chord else cursor
                pitch = child.find("pitch")
                if pitch is None:
                    if not is_chord:
                        cursor += duration
                    last_onset = onset
                    continue
                step = pitch.findtext("step", "C")
                alter = int(pitch.findtext("alter", "0"))
                octave = int(pitch.findtext("octave", "4"))
                semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
                value = (octave + 1) * 12 + semitones[step] + alter
                event_id = f"xml:{part_id}:m{measure_no}:n{note_index}"
                events.append({"event_id": event_id, "part": part_id, "measure": measure_no, "start": onset, "duration": duration, "pitch": value, "time": time, "key": key})
                if not is_chord:
                    cursor += duration
                last_onset = onset
                note_index += 1
    return events, {"parts": len(parts), "time": time, "key": key}


def group_patterns(events: list[dict[str, Any]], config: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    role_events: dict[str, list[dict[str, Any]]] = {role: [] for role in ("melody", "harmony", "bass")}
    by_part: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    ranked = sorted(by_part, key=lambda key: (-sum(e["pitch"] for e in by_part[key]) / max(1, len(by_part[key])), key))
    if not ranked:
        raise ValueError("MusicXML contains no pitched notes")
    role_events["melody"] = by_part[ranked[0]]
    if len(ranked) > 1:
        role_events["bass"] = by_part[ranked[-1]]
        role_events["harmony"] = [e for key in ranked[1:-1] for e in by_part[key]]
    else:
        role_events["bass"] = [e for e in by_part[ranked[0]] if e["pitch"] <= 60]
        role_events["harmony"] = [e for e in by_part[ranked[0]] if e["pitch"] > 60]
    channels = {"melody": "pulse1", "harmony": "pulse2", "bass": "wave"}
    instruments = {"pulse1": 1, "pulse2": 3, "wave": 2}
    patterns: dict[str, list[dict[str, Any]]] = {channel: [] for channel in json_to_uge.CHANNELS}
    losses: list[dict[str, Any]] = []
    max_tick = max((e["start"] + e["duration"] for e in events), default=0)
    range_config = config["pitch_range"]
    for role, role_notes in role_events.items():
        channel = channels[role]
        selected: dict[int, dict[str, Any]] = {}
        for event in sorted(role_notes, key=lambda e: (e["start"], e["pitch"], e["event_id"])):
            if config.get("timeline_mode") == "absolute":
                measure_ticks = config.get("measure_ticks", 768)
                timeline_tick = (int(event["measure"]) - 1) * measure_ticks + int(event["start"])
            else:
                timeline_tick = int(event["start"])
            row = round(timeline_tick / config["quantization_grid_ticks"])
            pitch = event["pitch"]
            original = pitch
            while pitch < range_config[channel][0]:
                pitch += 12
            while pitch > range_config[channel][1]:
                pitch -= 12
            if not range_config[channel][0] <= pitch <= range_config[channel][1]:
                losses.append({"event_id": event["event_id"], "reason": "range_reject", "original_pitch": original})
                continue
            if row in selected:
                losses.append({"event_id": event["event_id"], "reason": "polyphony_omitted", "selected_event": selected[row]["source_event"]})
                continue
            selected[row] = {"row": row, "pitch": pitch, "length": max(1, round(event["duration"] / config["quantization_grid_ticks"])), "source_event": event["event_id"], "original_pitch": original, "instrument": instruments[channel]}
        patterns[channel] = sorted(selected.values(), key=lambda e: e["row"])
    warnings = [{"kind": "repeat_structure", "status": "lost", "detail": "MIDI event stream has no trusted repeat/ending semantics"}, {"kind": "ch4", "status": "unused", "detail": "piano source has no source percussion; no implicit noise conversion"}]
    return {"channels": patterns, "max_tick": max_tick}, losses + warnings


def make_json(plan: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    channel_names = json_to_uge.CHANNELS
    names = {channel: f"maple_{channel}" for channel in channel_names}
    order = {channel: [names[channel]] for channel in channel_names}
    patterns: dict[str, dict[str, list[dict[str, Any]]]] = {channel: {names[channel]: []} for channel in channel_names}
    for channel in channel_names:
        row = 0
        for event in plan["channels"].get(channel, []):
            while row < event["row"]:
                rest = {"note": "rest", "length": min(event["row"] - row, PATTERN_ROWS - row)}
                rest["instrument"] = {"pulse1": 1, "pulse2": 3, "wave": 2, "noise": 4}[channel]
                patterns[channel][names[channel]].append(rest)
                row += patterns[channel][names[channel]][-1]["length"]
            if row >= PATTERN_ROWS:
                break
            length = min(event["length"], PATTERN_ROWS - row)
            note = json_note_name(event["pitch"])
            patterns[channel][names[channel]].append({"note": note, "length": length, "instrument": event["instrument"]})
            row += length
        while row < PATTERN_ROWS:
            rest = {"note": "rest", "length": PATTERN_ROWS - row}
            rest["instrument"] = {"pulse1": 1, "pulse2": 3, "wave": 2, "noise": 4}[channel]
            patterns[channel][names[channel]].append(rest)
            row = PATTERN_ROWS
    return {"version": 2, "title": "Maple Leaf Rag Prototype", "type": "bgm", "tempo": config["ticks_per_row"], "loop": {"mode": "none"}, "wave_tables": [{"name": "maple_triangle", "samples": [*range(16), *range(15, -1, -1)]}], "instruments": [{"id": 1, "name": "maple_lead", "channel": "pulse1", "duty": 2, "length": 0, "length_enable": False, "initial_volume": 12, "envelope_direction": "down", "envelope_sweep": 0, "sweep_time": 0, "sweep_direction": "down", "sweep_shift": 0}, {"id": 2, "name": "maple_bass", "channel": "wave", "waveform": "maple_triangle", "output_level": "100%", "length": 0, "length_enable": False}, {"id": 3, "name": "maple_harmony", "channel": "pulse2", "duty": 1, "length": 0, "length_enable": False, "initial_volume": 8, "envelope_direction": "down", "envelope_sweep": 0}, {"id": 4, "name": "unused_noise", "channel": "noise", "width_mode": "15bit", "initial_volume": 0, "envelope_direction": "down", "envelope_sweep": 0, "length": 0, "length_enable": False}], "order": order, "patterns": patterns}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", type=Path)
    parser.add_argument("output", type=Path, help="output directory for MusicXML, JSON, manifest and report")
    args = parser.parse_args()
    source_hash = sha256(args.midi)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source SHA-256 mismatch: expected {EXPECTED_SOURCE_SHA256}, got {source_hash}")
    ppq, tracks, midi_meta = read_midi(args.midi)
    args.output.mkdir(parents=True, exist_ok=True)
    musicxml = args.output / "maple_leaf_rag.generated.musicxml"
    write_musicxml(musicxml, ppq, tracks, midi_meta)
    events, xml_meta = parse_musicxml(musicxml)
    measure_ticks = ppq * (midi_meta["meters"][0]["beats"] if midi_meta["meters"] else 2) * 4 // (midi_meta["meters"][0]["beat_type"] if midi_meta["meters"] else 4)
    config = {"quantization_grid_ticks": GRID_TICKS, "ticks_per_row": TICKS_PER_ROW, "measure_ticks": measure_ticks, "timeline_mode": "absolute", "pitch_range": {"pulse1": [48, 96], "pulse2": [48, 84], "wave": [48, 72], "noise": [0, 0]}, "mapping": {"melody": "pulse1", "harmony": "pulse2", "bass": "wave", "rhythm": "noise"}, "ch4_policy": "unused", "repeat_policy": "do_not_infer", "loop_policy": "none", "prototype_range": "all parsed MIDI events; one 64-row JSON pattern window"}
    plan, issues = group_patterns(events, config)
    output_json = make_json(plan, config)
    json_path = args.output / "maple_leaf_rag.prototype.json"
    json_path.write_text(json.dumps(output_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json_to_uge.build_uge(output_json)
    manifest = {"composition": "Maple Leaf Rag", "composer": "Scott Joplin", "source_provider": "Mutopia Project", "source_identity": SOURCE_ID, "source_url": SOURCE_URL, "source_format": "Standard MIDI File", "source_sha256": source_hash, "source_license": "Mutopia Public Domain contribution; see https://www.mutopiaproject.org/legal.html", "conversion_tool": "maple_leaf_rag_prototype.py deterministic SMF/MusicXML adapter", "conversion_tool_version": "2", "conversion_settings": {"ppq": ppq, "midi_format": midi_meta["format"], "musicxml_version": "4.0", "measure_ticks": ppq * (midi_meta["meters"][0]["beats"] if midi_meta["meters"] else 2) * 4 // (midi_meta["meters"][0]["beat_type"] if midi_meta["meters"] else 4), "gap_encoding": "forward", "overlap_encoding": "backup_forward", "chord_encoding": "chord"}, "musicxml_sha256": sha256(musicxml), "parser": "xml.etree.ElementTree + built-in SMF parser", "parser_version": "Python standard library", "arrangement_configuration": config, "source_tempo": midi_meta["tempo"], "source_meter": midi_meta["meters"], "ticks_per_row": TICKS_PER_ROW, "warnings": issues, "losses": [issue for issue in issues if issue.get("reason") or issue.get("status") == "lost"], "transformation_history": ["SMF parse", "deterministic MusicXML generation with forward/backup", "MusicXML parse with note/chord/rest/forward/backup semantics", "MusicXML parse to NormalizedScore", "role mapping to ArrangementPlan", "quantization and explicit range transform", "JSON Version 2 emission"], "json_sha256": sha256(json_path)}
    (args.output / "maple_leaf_rag.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output / "maple_leaf_rag.report.json").write_text(json.dumps({"normalized_score": {"event_count": len(events), "musicxml": xml_meta, "source_timing": {"ppq": ppq, "tempo": midi_meta["tempo"], "meters": midi_meta["meters"]}}, "arrangement_plan": plan, "issues": issues}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
