#!/usr/bin/env python3
"""Compare source tempo, quantized rows, and fixed-rate runtime rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype
from analyze_pd_length_diagnostic import compare as length_compare, digest, token_metrics


SCHEMA = "maple-pd-tempo-diagnostic/v1"
VERSION = "1"
FRAME_HZ = 60


def bpm_from_us_per_quarter(value: int) -> float:
    return 60_000_000 / value


def tick_seconds(tick: int, ppq: int, us_per_quarter: int) -> float:
    return tick * us_per_quarter / 1_000_000 / ppq


def runtime_row_seconds(ticks_per_row: int, frame_hz: int = FRAME_HZ) -> float:
    return ticks_per_row / frame_hz


def compare(midi: Path, artifact_dir: Path, output: Path) -> tuple[Path, Path]:
    length_dir = output / "length-input"
    length_compare(midi, artifact_dir, length_dir)
    length = json.loads((length_dir / "maple_leaf_rag.length-diagnostic.json").read_text(encoding="utf-8"))
    data = json.loads((artifact_dir / "maple_leaf_rag.prototype.json").read_text(encoding="utf-8"))
    manifest = json.loads((artifact_dir / "maple_leaf_rag.manifest.json").read_text(encoding="utf-8"))
    ppq, tracks, meta = prototype.read_midi(midi)
    tempo_event = meta["tempo"][0]
    us_per_quarter = tempo_event["microseconds_per_quarter"]
    source_by_id = {note.event_id: note for track in tracks for note in track.notes}
    # Reconstruct the same selected plan used by the prototype, without changing it.
    events, _ = prototype.parse_musicxml(artifact_dir / "maple_leaf_rag.generated.musicxml")
    config = manifest["arrangement_configuration"]
    plan, _ = prototype.group_patterns(events, config)
    xml_to_source = {}
    by_part = {}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    for track in tracks:
        for source, xml in zip(track.notes, by_part.get(f"P{track.index + 1}", [])):
            xml_to_source[xml["event_id"]] = source
    ticks_per_row_source = prototype.GRID_TICKS
    ticks_per_row_runtime = data["tempo"]
    row_seconds = runtime_row_seconds(ticks_per_row_runtime)
    mappings = []
    for channel, selected in plan["channels"].items():
        selected = sorted(selected, key=lambda event: (event["row"], event["source_event"]))
        tokens = token_metrics(next(iter(data["patterns"][channel].values())))['notes']
        for event, token in zip(selected, tokens):
            source = xml_to_source[event["source_event"]]
            mappings.append({
                "source_event_id": source.event_id,
                "channel": channel,
                "source_onset_ticks": source.start,
                "source_onset_seconds": tick_seconds(source.start, ppq, us_per_quarter),
                "source_duration_ticks": source.end - source.start,
                "source_duration_seconds": tick_seconds(source.end - source.start, ppq, us_per_quarter),
                "arrangement_row": event["row"],
                "source_grid_row_seconds": event["row"] * (ticks_per_row_source / ppq * us_per_quarter / 1_000_000),
                "json_runtime_row": token["row_start"],
                "runtime_onset_seconds": token["row_start"] * row_seconds,
                "quantized_duration_rows": event["length"],
                "json_note_length_rows": token["length"],
                "runtime_duration_seconds": token["length"] * row_seconds,
            })
    selected_first = min(x["source_onset_seconds"] for x in mappings)
    selected_last_end = max(x["source_onset_seconds"] + x["source_duration_seconds"] for x in mappings)
    runtime_first = min(x["runtime_onset_seconds"] for x in mappings)
    runtime_last_end = max(x["runtime_onset_seconds"] + x["runtime_duration_seconds"] for x in mappings)
    result = {
        "schema": SCHEMA,
        "tool": {"name": "analyze_pd_tempo_diagnostic.py", "version": VERSION},
        "source": {"sha256": digest(midi), "identity": prototype.SOURCE_ID, "ppq": ppq, "tempo_events": meta["tempo"], "tempo_event_count": len(meta["tempo"]), "microseconds_per_quarter": us_per_quarter, "bpm": bpm_from_us_per_quarter(us_per_quarter), "quarter_seconds": us_per_quarter / 1_000_000, "eighth_seconds": us_per_quarter / 2_000_000, "sixteenth_seconds": us_per_quarter / 4_000_000, "tick_seconds": us_per_quarter / 1_000_000 / ppq, "total_seconds": length["source"]["source_seconds_at_constant_tempo"]},
        "quantization": {"grid_ticks": ticks_per_row_source, "source_grid_seconds": ticks_per_row_source * us_per_quarter / 1_000_000 / ppq, "formula": "round(source_onset / GRID_TICKS)", "duration_formula": "round(source_duration / GRID_TICKS)"},
        "runtime": {"json_ticks_per_row": ticks_per_row_runtime, "uge_tempo_raw": ticks_per_row_runtime, "frame_hz": FRAME_HZ, "hugodriver_calls_per_second": FRAME_HZ, "hugodriver_ticks_per_row": ticks_per_row_runtime, "row_seconds": row_seconds, "pattern_rows": 64, "pattern_seconds": 64 * row_seconds, "selected_first_to_last_seconds": runtime_last_end - runtime_first, "loop": data["loop"]},
        "source_selected": {"first_to_last_seconds": selected_last_end - selected_first, "first_source_seconds": selected_first, "last_source_end_seconds": selected_last_end},
        "timeline_compression": {"selected_source_envelope_seconds": selected_last_end - selected_first, "selected_runtime_envelope_seconds": runtime_last_end - runtime_first, "runtime_over_source_envelope": (runtime_last_end - runtime_first) / (selected_last_end - selected_first)},
        "selected_event_mappings": sorted(mappings, key=lambda x: (x["source_onset_ticks"], x["source_event_id"])),
        "artifacts": {"source_sha256": digest(midi), "json_sha256": digest(artifact_dir / "maple_leaf_rag.prototype.json"), "manifest_sha256": digest(artifact_dir / "maple_leaf_rag.manifest.json"), "uge_sha256": digest(artifact_dir / "maple_leaf_rag-timing-fixed.uge")},
    }
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "maple_leaf_rag.tempo-diagnostic.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path = output / "maple_leaf_rag.tempo-diagnostic.md"
    md_path.write_text("# Maple Leaf Rag tempo diagnostic\n\n" + json.dumps({k: result[k] for k in ("source", "quantization", "runtime", "source_selected", "timeline_compression", "artifacts")}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("midi", type=Path)
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for path in compare(args.midi, args.artifact_dir, args.output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
