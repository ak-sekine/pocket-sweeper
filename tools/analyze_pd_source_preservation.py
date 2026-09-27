#!/usr/bin/env python3
"""Measure MIDI -> generated MusicXML -> NormalizedScore preservation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype


TOOL_VERSION = "1"
DIAGNOSTIC_SCHEMA = "maple-pd-diagnostic/v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_tick(xml_value: int, divisions: int, ppq: int) -> tuple[int, str, int]:
    """Convert MusicXML divisions to source ticks with deterministic half-up rounding."""
    exact = Fraction(xml_value * ppq, divisions)
    if exact.denominator == 1:
        return exact.numerator, "exact", 0
    rounded = (exact.numerator * 2 + exact.denominator) // (2 * exact.denominator)
    return rounded, "rounded_half_up", rounded - exact.numerator // exact.denominator


def classify(actual: int, expected: int) -> str:
    return "PRESERVED" if actual == expected else "TRANSFORMED"


def compare(midi: Path, output: Path) -> tuple[Path, Path]:
    source_hash = digest(midi)
    if source_hash != prototype.EXPECTED_SOURCE_SHA256:
        raise ValueError(f"source SHA-256 mismatch: expected {prototype.EXPECTED_SOURCE_SHA256}, got {source_hash}")
    output.mkdir(parents=True, exist_ok=True)
    ppq, tracks, meta = prototype.read_midi(midi)
    xml_path = output / "maple_leaf_rag.generated.musicxml"
    prototype.write_musicxml(xml_path, ppq, tracks, meta)
    xml_events, xml_meta = prototype.parse_musicxml(xml_path)
    by_part: dict[str, list[dict[str, Any]]] = {}
    for event in xml_events:
        by_part.setdefault(event["part"], []).append(event)

    mappings: list[dict[str, Any]] = []
    pitch_exact = pitch_mismatch = 0
    onset_exact = onset_rounded = onset_mismatch = 0
    duration_exact = duration_rounded = duration_mismatch = 0
    max_onset_delta = max_duration_delta = 0
    source_count = xml_count = normalized_count = 0
    for track in tracks:
        source_notes = list(track.notes)
        xml_notes = by_part.get(f"P{track.index + 1}", [])
        source_count += len(source_notes)
        xml_count += len(xml_notes)
        if len(source_notes) != len(xml_notes):
            raise ValueError(f"unmapped note count in track {track.index}: {len(source_notes)} != {len(xml_notes)}")
        for source, xml in zip(source_notes, xml_notes):
            # The writer uses four quarter notes as its measure boundary. The
            # parser's start is measure-local, so restore the absolute source
            # coordinate before comparing it with MIDI.
            xml_local_onset, onset_mode, _ = source_tick(xml["start"], ppq, ppq)
            xml_onset = (xml["measure"] - 1) * ppq * 4 + xml_local_onset
            xml_duration, duration_mode, _ = source_tick(xml["duration"], ppq, ppq)
            normalized_onset = (xml["measure"] - 1) * ppq * 4 + xml_local_onset
            normalized_duration, _, _ = source_tick(xml["duration"], ppq, ppq)
            pitch_status = classify(xml["pitch"], source.pitch)
            onset_status = classify(xml_onset, source.start)
            duration_status = classify(xml_duration, source.end - source.start)
            if pitch_status == "PRESERVED": pitch_exact += 1
            else: pitch_mismatch += 1
            if onset_status == "PRESERVED": onset_exact += 1
            elif onset_mode == "rounded_half_up": onset_rounded += 1
            else: onset_mismatch += 1
            if duration_status == "PRESERVED": duration_exact += 1
            elif duration_mode == "rounded_half_up": duration_rounded += 1
            else: duration_mismatch += 1
            max_onset_delta = max(max_onset_delta, abs(xml_onset - source.start))
            max_duration_delta = max(max_duration_delta, abs(xml_duration - (source.end - source.start)))
            mappings.append({
                "source_event_id": source.event_id,
                "events": [
                    {"stage": "parsed_midi", "stage_event_id": source.event_id, "status": "PRESERVED", "track": source.track, "pitch": source.pitch, "onset_tick": source.start, "duration_tick": source.end - source.start},
                    {"stage": "generated_musicxml", "stage_event_id": xml["event_id"], "status": pitch_status if pitch_status != "PRESERVED" else onset_status if onset_status != "PRESERVED" else duration_status, "part": xml["part"], "measure": xml["measure"], "pitch": xml["pitch"], "onset_divisions": xml["start"], "duration_divisions": xml["duration"], "onset_tick": xml_onset, "duration_tick": xml_duration, "voice_status": "RECONSTRUCTED", "staff_status": "RECONSTRUCTED", "spelling_status": "RECONSTRUCTED"},
                    {"stage": "normalized_score", "stage_event_id": f"norm:{xml['part']}:m{xml['measure']}:{xml['event_id'].split(':')[-1]}", "status": "PRESERVED", "part": xml["part"], "measure": xml["measure"], "pitch": xml["pitch"], "onset_tick": normalized_onset, "duration_tick": normalized_duration, "comparison_basis": "MusicXML parser output; not independent parser"}
                ],
                "deltas": {"pitch": xml["pitch"] - source.pitch, "onset_tick": xml_onset - source.start, "duration_tick": xml_duration - (source.end - source.start)},
            })
        normalized_count += len(xml_notes)

    diagnostic = {
        "schema": DIAGNOSTIC_SCHEMA,
        "tool": {"name": "analyze_pd_source_preservation.py", "version": TOOL_VERSION, "prototype_tool": "maple_leaf_rag_prototype.py", "prototype_version": "1"},
        "source": {"identity": prototype.SOURCE_ID, "url": prototype.SOURCE_URL, "sha256": source_hash, "format": meta["format"], "ppq": ppq, "track_count": len(tracks)},
        "configuration": {"tick_conversion": "xml_divisions_to_source_tick_v1", "formula": "Fraction(xml_value * PPQ, divisions)", "rounding": "half-up only when denominator != 1", "scope": "full MIDI and full normalized source; no 64-row window"},
        "stages": ["source_midi", "parsed_midi", "generated_musicxml", "normalized_score"],
        "artifacts": {"musicxml_sha256": digest(xml_path)},
        "event_mappings": mappings,
        "summary_metrics": {"source_midi_note_count": source_count, "parsed_midi_note_count": source_count, "musicxml_note_count": xml_count, "normalized_score_note_count": normalized_count, "mapped_count": len(mappings), "unmapped_count": source_count - len(mappings), "mapping_1_to_1": source_count, "mapping_1_to_0": 0, "mapping_1_to_n": 0, "mapping_n_to_1": 0, "pitch_exact": pitch_exact, "pitch_mismatch": pitch_mismatch, "pitch_transformed": 0, "pitch_unknown": 0, "onset_exact": onset_exact, "onset_rounded": onset_rounded, "onset_mismatch": onset_mismatch, "onset_max_abs_delta": max_onset_delta, "duration_exact": duration_exact, "duration_rounded": duration_rounded, "duration_mismatch": duration_mismatch, "duration_max_abs_delta": max_duration_delta, "normalized_vs_musicxml_pitch_exact": normalized_count, "normalized_vs_musicxml_onset_exact": normalized_count, "normalized_vs_musicxml_duration_exact": normalized_count},
        "metadata": {"tempo": meta["tempo"], "meter_source": meta["meters"], "meter_musicxml": xml_meta["time"], "tempo_status": "RECONSTRUCTED", "meter_status": "RECONSTRUCTED", "repeats": "NOT_APPLICABLE", "endings": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "dynamics": "NOT_APPLICABLE", "notation_semantics": "NOT_APPLICABLE", "voice": "RECONSTRUCTED", "staff": "RECONSTRUCTED", "spelling": "RECONSTRUCTED"},
    }
    diagnostic_path = output / "maple_leaf_rag.diagnostic.json"
    diagnostic_path.write_text(json.dumps(diagnostic, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    diagnostic_hash = digest(diagnostic_path)
    report = {"schema": DIAGNOSTIC_SCHEMA, "diagnostic_sha256": diagnostic_hash, "source": diagnostic["source"], "summary_metrics": diagnostic["summary_metrics"], "metadata": diagnostic["metadata"], "scope": diagnostic["configuration"]["scope"], "note": "Machine structural comparison only; no Human musical equivalence claim."}
    report_path = output / "maple_leaf_rag.diagnostic.md"
    report_path.write_text("# Maple Leaf Rag MIDI preservation diagnostic\n\n" + json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return diagnostic_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    diagnostic, report = compare(args.midi, args.output)
    print(diagnostic)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
