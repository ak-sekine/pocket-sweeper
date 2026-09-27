#!/usr/bin/env python3
"""Locate onset differences across the prototype MIDI/MusicXML stages."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype


TOOL_VERSION = "1"
SCHEMA = "maple-pd-onset-diagnostic/v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded_xml_events(path: Path, ppq: int) -> list[dict[str, object]]:
    """Read the actual implicit MusicXML cursor, including chord semantics."""
    root = ET.parse(path).getroot()
    result: list[dict[str, object]] = []
    for part in root.findall("part"):
        part_id = part.attrib["id"]
        for measure in part.findall("measure"):
            number = int(measure.attrib["number"])
            cursor = 0
            last_onset = 0
            for index, note in enumerate(measure.findall("note")):
                duration = int(note.findtext("duration", "1"))
                is_chord = note.find("chord") is not None
                pitch = note.find("pitch")
                local_onset = last_onset if is_chord else cursor
                if pitch is not None:
                    step = pitch.findtext("step", "C")
                    alter = int(pitch.findtext("alter", "0"))
                    octave = int(pitch.findtext("octave", "4"))
                    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
                    value = (octave + 1) * 12 + semitones[step] + alter
                    result.append({
                        "part": part_id,
                        "measure": number,
                        "note_index": index,
                        "local_onset": local_onset,
                        "duration": duration,
                        "pitch": value,
                        "chord": is_chord,
                    })
                if not is_chord:
                    cursor += duration
                last_onset = local_onset
    return result


def classify(first: str, source_onset: int, encoded_onset: int, restored_onset: int) -> str:
    if encoded_onset != source_onset:
        return "generated_musicxml_representation"
    if restored_onset != source_onset:
        return "diagnostic_absolute_reconstruction"
    return first


def compare(midi: Path, output: Path) -> tuple[Path, Path]:
    source_hash = digest(midi)
    if source_hash != prototype.EXPECTED_SOURCE_SHA256:
        raise ValueError(f"source SHA-256 mismatch: expected {prototype.EXPECTED_SOURCE_SHA256}, got {source_hash}")
    output.mkdir(parents=True, exist_ok=True)
    ppq, tracks, meta = prototype.read_midi(midi)
    xml_path = output / "maple_leaf_rag.generated.musicxml"
    prototype.write_musicxml(xml_path, ppq, tracks, meta)
    parsed_xml, xml_meta = prototype.parse_musicxml(xml_path)
    encoded = encoded_xml_events(xml_path, ppq)
    if len(encoded) != sum(len(t.notes) for t in tracks) or len(parsed_xml) != len(encoded):
        raise ValueError("MusicXML event count differs between raw XML and prototype parser")

    mappings: list[dict[str, object]] = []
    first_stage = Counter()
    delta_by_measure: defaultdict[int, Counter[int]] = defaultdict(Counter)
    delta_by_track: defaultdict[int, Counter[int]] = defaultdict(Counter)
    exact = 0
    max_delta = 0
    measures = ppq * 4  # actual writer boundary; intentionally compared with source 2/4 metadata
    source_notes = [note for track in tracks for note in track.notes]
    xml_by_part: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in parsed_xml:
        xml_by_part[event["part"]].append(event)
    for track in tracks:
        xml_part = xml_by_part[f"P{track.index + 1}"]
        raw_part = [e for e in encoded if e["part"] == f"P{track.index + 1}"]
        for source, xml, raw in zip(track.notes, xml_part, raw_part):
            writer_measure = source.start // measures + 1
            expected_local = source.start % measures
            encoded_local = int(raw["local_onset"])
            encoded_absolute = (int(raw["measure"]) - 1) * measures + encoded_local
            parsed_onset = (int(xml["measure"]) - 1) * measures + int(xml["start"])
            diagnostic_onset = parsed_onset
            source_onset = source.start
            delta = diagnostic_onset - source_onset
            encoded_delta = encoded_absolute - source_onset
            parser_delta = parsed_onset - encoded_absolute
            if encoded_delta:
                stage = "generated_musicxml_representation"
            elif parser_delta:
                stage = "musicxml_parser"
            elif delta:
                stage = "diagnostic_absolute_reconstruction"
            else:
                stage = "none"
            first_stage[stage] += 1
            delta_by_measure[int(raw["measure"])][delta] += 1
            delta_by_track[track.index][delta] += 1
            exact += delta == 0
            max_delta = max(max_delta, abs(delta))
            mappings.append({
                "source_event_id": source.event_id,
                "track": track.index,
                "part": raw["part"],
                "pitch": source.pitch,
                "source_midi_onset": source_onset,
                "parsed_midi_onset": source_onset,
                "writer_input_onset": source_onset,
                "writer_measure": writer_measure,
                "writer_expected_local_onset": expected_local,
                "musicxml_measure": raw["measure"],
                "musicxml_measure_local_onset": encoded_local,
                "musicxml_encoded_absolute_onset": encoded_absolute,
                "musicxml_parser_onset": parsed_onset,
                "normalized_score_onset": parsed_onset,
                "diagnostic_absolute_onset": diagnostic_onset,
                "source_delta": delta,
                "encoded_delta": encoded_delta,
                "parser_delta": parser_delta,
                "first_mismatch_stage": stage,
                "musicxml_divisions": ppq,
                "midi_ppq": ppq,
                "duration": int(raw["duration"]),
                "chord": raw["chord"],
            })

    diagnostics = {
        "schema": SCHEMA,
        "tool": {"name": "analyze_pd_onset_diagnostic.py", "version": TOOL_VERSION, "prototype": "maple_leaf_rag_prototype.py", "prototype_version": "1"},
        "source": {"identity": prototype.SOURCE_ID, "url": prototype.SOURCE_URL, "sha256": source_hash, "format": meta["format"], "ppq": ppq, "track_count": len(tracks)},
        "configuration": {"scope": "full source MIDI and generated MusicXML; no arrangement/window", "writer_measure_ticks": measures, "source_meter": meta["meters"], "musicxml_divisions": ppq, "absolute_reconstruction": "(measure - 1) * writer_measure_ticks + measure_local_cursor", "rest_encoding": "writer emits no rest/forward for gaps", "chord_encoding": "chord notes do not advance cursor"},
        "stages": ["source_midi", "parsed_midi", "writer_input", "generated_musicxml", "musicxml_parser", "normalized_score", "diagnostic_absolute_onset"],
        "artifacts": {"musicxml_sha256": digest(xml_path)},
        "summary": {"total_events": len(mappings), "onset_exact": exact, "onset_mismatch": len(mappings) - exact, "max_abs_delta": max_delta, "first_mismatch_stage": dict(first_stage), "delta_distribution": dict(sorted(Counter(m["source_delta"] for m in mappings).items())), "measure_delta_distribution": {str(k): dict(sorted(v.items())) for k, v in sorted(delta_by_measure.items())}, "track_delta_distribution": {str(k): dict(sorted(v.items())) for k, v in sorted(delta_by_track.items())}},
        "metadata": {"tempo": meta["tempo"], "source_meter": meta["meters"], "musicxml_meter": xml_meta["time"], "voice": "RECONSTRUCTED", "staff": "RECONSTRUCTED", "spelling": "RECONSTRUCTED", "repeats": "NOT_APPLICABLE"},
        "event_mappings": mappings,
    }
    json_path = output / "maple_leaf_rag.onset-diagnostic.json"
    json_path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = output / "maple_leaf_rag.onset-diagnostic.md"
    summary = diagnostics["summary"]
    report_path.write_text(
        "# Maple Leaf Rag onset diagnostic\n\n"
        "Machine structural comparison only; this report does not infer Human musical causality.\n\n"
        f"- source SHA-256: `{source_hash}`\n- MusicXML SHA-256: `{diagnostics['artifacts']['musicxml_sha256']}`\n"
        f"- events: {summary['total_events']}\n- exact: {summary['onset_exact']}\n- mismatch: {summary['onset_mismatch']}\n- maximum absolute delta: {summary['max_abs_delta']} source ticks\n\n"
        "## First mismatch stage\n\n"
        + json.dumps(summary["first_mismatch_stage"], ensure_ascii=False, indent=2, sort_keys=True)
        + "\n\n## Interpretation\n\n"
        "The writer groups measures using `PPQ * 4`, while the source meter is 2/4. It also emits no rest/forward for gaps, so the actual MusicXML cursor is not an independent absolute onset field. The event-level JSON records this observation; it does not by itself classify the behavior as a defect.\n",
        encoding="utf-8",
    )
    return json_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    paths = compare(args.midi, args.output)
    print(paths[0])
    print(paths[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
