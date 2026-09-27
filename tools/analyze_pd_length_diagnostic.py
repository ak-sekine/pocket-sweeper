#!/usr/bin/env python3
"""Compare source timeline length with the Maple Leaf Rag prototype output."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype


SCHEMA = "maple-pd-length-diagnostic/v1"
VERSION = "1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_map(midi_path: Path, musicxml_path: Path):
    ppq, tracks, meta = prototype.read_midi(midi_path)
    events, xml_meta = prototype.parse_musicxml(musicxml_path)
    by_part = {}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    source_by_xml = {}
    for track in tracks:
        xml_events = by_part.get(f"P{track.index + 1}", [])
        for source, xml in zip(track.notes, xml_events):
            source_by_xml[xml["event_id"]] = source
    return ppq, tracks, meta, events, xml_meta, source_by_xml


def token_metrics(pattern: list[dict]) -> dict:
    row = 0
    notes = []
    rests = []
    for index, token in enumerate(pattern):
        length = int(token["length"])
        entry = {"token_index": index, "row_start": row, "row_end_exclusive": row + length, "note": token["note"], "length": length}
        if token["note"] == "rest":
            rests.append(entry)
        else:
            notes.append(entry)
        row += length
    return {"token_count": len(pattern), "note_count": len(notes), "rest_count": len(rests), "first_note_row": notes[0]["row_start"] if notes else None, "last_note_row": notes[-1]["row_start"] if notes else None, "last_token_end_row": row, "notes": notes}


def compare(midi: Path, artifact_dir: Path, output: Path) -> tuple[Path, Path]:
    if digest(midi) != prototype.EXPECTED_SOURCE_SHA256:
        raise ValueError("source SHA-256 mismatch")
    musicxml = artifact_dir / "maple_leaf_rag.generated.musicxml"
    json_path = artifact_dir / "maple_leaf_rag.prototype.json"
    manifest_path = artifact_dir / "maple_leaf_rag.manifest.json"
    uge_analysis = artifact_dir / "uge-analysis-current.json"
    ppq, tracks, meta, events, xml_meta, source_by_xml = event_map(midi, musicxml)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = manifest["arrangement_configuration"]
    plan, issues = prototype.group_patterns(events, config)
    source_notes = [note for track in tracks for note in track.notes]
    measure_ticks = ppq * (meta["meters"][0]["beats"] if meta["meters"] else 2) * 4 // (meta["meters"][0]["beat_type"] if meta["meters"] else 4)
    normalized = []
    for event in events:
        onset = (int(event["measure"]) - 1) * measure_ticks + int(event["start"])
        normalized.append((onset, onset + int(event["duration"]), event))
    selected = []
    for channel, channel_events in plan["channels"].items():
        for event in channel_events:
            source = source_by_xml.get(event["source_event"])
            selected.append({"channel": channel, "row": event["row"], "pitch": event["pitch"], "source_event_id": source.event_id if source else None, "source_onset": source.start if source else None, "source_end": source.end if source else None, "xml_event_id": event["source_event"]})
    json_data = json.loads(json_path.read_text(encoding="utf-8"))
    json_metrics = {channel: token_metrics(next(iter(patterns.values()))) for channel, patterns in json_data["patterns"].items()}
    analysis = json.loads(uge_analysis.read_text(encoding="utf-8"))[0] if uge_analysis.exists() else None
    result = {
        "schema": SCHEMA,
        "tool": {"name": "analyze_pd_length_diagnostic.py", "version": VERSION},
        "source": {"identity": prototype.SOURCE_ID, "sha256": digest(midi), "ppq": ppq, "format": meta["format"], "tempo": meta["tempo"], "meter": meta["meters"], "note_count": len(source_notes), "first_onset": min(n.start for n in source_notes), "last_onset": max(n.start for n in source_notes), "last_note_end": max(n.end for n in source_notes), "tick_span": max(n.end for n in source_notes) - min(n.start for n in source_notes), "quarter_span": (max(n.end for n in source_notes) - min(n.start for n in source_notes)) / ppq, "source_seconds_at_constant_tempo": 144.0},
        "normalized_score": {"event_count": len(normalized), "first_onset": min(x[0] for x in normalized), "last_onset": max(x[0] for x in normalized), "last_note_end": max(x[1] for x in normalized), "tick_span": max(x[1] for x in normalized) - min(x[0] for x in normalized), "measure_ticks": measure_ticks, "last_measure": max(int(e["measure"]) for e in events)},
        "arrangement_plan": {"selected_count": len(selected), "first_source_onset": min(x["source_onset"] for x in selected), "last_source_onset": max(x["source_onset"] for x in selected), "last_source_end": max(x["source_end"] for x in selected), "first_row": min(x["row"] for x in selected), "last_row": max(x["row"] for x in selected), "selected_events": sorted(selected, key=lambda x: (x["source_onset"], x["source_event_id"])), "omitted_polyphony": sum(issue.get("reason") == "polyphony_omitted" for issue in issues)},
        "json": {"note_count": sum(x["note_count"] for x in json_metrics.values()), "pattern_count": sum(len(p) for p in json_data["patterns"].values()), "order_count": len(next(iter(json_data["order"].values()))), "pattern_rows": 64, "channels": json_metrics, "loop": json_data["loop"], "tempo_ticks_per_row": json_data["tempo"], "source_derived_plan_events_outside_window": sum(x["row"] >= 64 for x in selected)},
        "uge": {"analysis": analysis},
        "artifacts": {"source_sha256": digest(midi), "musicxml_sha256": digest(musicxml), "json_sha256": digest(json_path), "manifest_sha256": digest(manifest_path)},
    }
    output.mkdir(parents=True, exist_ok=True)
    json_out = output / "maple_leaf_rag.length-diagnostic.json"
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_out = output / "maple_leaf_rag.length-diagnostic.md"
    report_out.write_text("# Maple Leaf Rag length diagnostic\n\n" + json.dumps({"schema": SCHEMA, "source": result["source"], "normalized_score": result["normalized_score"], "arrangement_plan": {k: v for k, v in result["arrangement_plan"].items() if k != "selected_events"}, "json": result["json"], "note": "Structural length comparison only; no Human musical causality claim."}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return json_out, report_out


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
