#!/usr/bin/env python3
"""Compare source rhythm with the prototype's role/row/token representation."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype
from analyze_pd_length_diagnostic import digest, token_metrics


SCHEMA = "maple-pd-rhythm-diagnostic/v1"
VERSION = "1"
MEASURE_TICKS = 768


def direction_intervals(values: list[int]) -> list[int]:
    return [b - a for a, b in zip(values, values[1:])]


def compare(midi: Path, artifact_dir: Path, output: Path) -> tuple[Path, Path]:
    if digest(midi) != prototype.EXPECTED_SOURCE_SHA256:
        raise ValueError("source SHA-256 mismatch")
    ppq, tracks, meta = prototype.read_midi(midi)
    xml_path = artifact_dir / "maple_leaf_rag.generated.musicxml"
    events, _ = prototype.parse_musicxml(xml_path)
    source_by_xml: dict[str, object] = {}
    by_part: dict[str, list[dict]] = {}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    for track in tracks:
        for source, xml in zip(track.notes, by_part.get(f"P{track.index + 1}", [])):
            source_by_xml[xml["event_id"]] = source
    manifest = json.loads((artifact_dir / "maple_leaf_rag.manifest.json").read_text(encoding="utf-8"))
    config = manifest["arrangement_configuration"]
    plan, issues = prototype.group_patterns(events, config)
    parts: dict[str, list[dict]] = {}
    for event in events:
        parts.setdefault(event["part"], []).append(event)
    ranked = sorted(parts, key=lambda key: (-sum(e["pitch"] for e in parts[key]) / len(parts[key]), key))
    roles = {ranked[0]: "melody", ranked[-1]: "bass"}
    channels = {"melody": "pulse1", "harmony": "pulse2", "bass": "wave", "rhythm": "noise"}
    records = []
    groups: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
    for event in events:
        source = source_by_xml[event["event_id"]]
        role = roles.get(event["part"], "harmony")
        local_onset = int(event["start"])
        absolute_onset = (int(event["measure"]) - 1) * MEASURE_TICKS + local_onset
        quant_row = round(local_onset / prototype.GRID_TICKS)
        record = {"source_event_id": source.event_id, "part": event["part"], "role": role, "channel": channels[role], "measure": event["measure"], "source_onset": source.start, "source_duration": source.end - source.start, "absolute_normalized_onset": absolute_onset, "normalized_measure_local_onset": local_onset, "quantized_row": quant_row, "quantization_delta_local_ticks": quant_row * prototype.GRID_TICKS - local_onset, "quantized_duration_rows": max(1, round((source.end - source.start) / prototype.GRID_TICKS)), "xml_event_id": event["event_id"]}
        records.append(record)
        groups[(role, quant_row)].append(record)
    selected_ids = {event["source_event"]: event for values in plan["channels"].values() for event in values}
    for record in records:
        selected = selected_ids.get(record["xml_event_id"])
        record["selection"] = "selected" if selected else "polyphony_omitted"
        if selected:
            record["selected_pitch"] = selected["pitch"]
            record["selected_row"] = selected["row"]
            record["json_source"] = True
    group_records = []
    for (role, row), members in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1])):
        source_onsets = sorted({m["source_onset"] for m in members})
        measures = sorted({m["measure"] for m in members})
        if len(source_onsets) == 1:
            classification = "PREEXISTING_SIMULTANEOUS"
        elif len(measures) > 1:
            classification = "CROSS_MEASURE_LOCAL_CURSOR_AGGREGATION"
        else:
            classification = "QUANTIZATION_INDUCED"
        selected = next((m for m in members if m["selection"] == "selected"), None)
        group_records.append({"role": role, "channel": channels[role], "quantized_row": row, "member_count": len(members), "source_onsets": source_onsets, "source_measures": measures, "classification": classification, "selected_event": selected["source_event_id"] if selected else None, "omitted_event_ids": [m["source_event_id"] for m in members if m["selection"] != "selected"]})
    source_notes = [n for t in tracks for n in t.notes]
    source_onsets = sorted({n.start for n in source_notes})
    source_simultaneous = collections.Counter(n.start for n in source_notes)
    durations = collections.Counter(n.end - n.start for n in source_notes)
    source_ioi = direction_intervals(source_onsets)
    selected = [r for r in records if r["selection"] == "selected"]
    selected_source = sorted(selected, key=lambda r: (r["source_onset"], r["source_event_id"]))
    json_data = json.loads((artifact_dir / "maple_leaf_rag.prototype.json").read_text(encoding="utf-8"))
    json_channel_metrics = {}
    json_selected = []
    for channel, patterns in json_data["patterns"].items():
        tokens = token_metrics(next(iter(patterns.values())))
        json_channel_metrics[channel] = {k: v for k, v in tokens.items() if k != "notes"}
        plan_events = sorted(plan["channels"].get(channel, []), key=lambda e: (e["row"], e["source_event"]))
        for event, token in zip(plan_events, tokens["notes"]):
            source = source_by_xml[event["source_event"]]
            json_selected.append({"source_event_id": source.event_id, "channel": channel, "source_onset": source.start, "json_row": token["row_start"], "json_length": token["length"], "source_duration": source.end - source.start})
    json_selected.sort(key=lambda x: (x["json_row"], x["source_event_id"]))
    result = {"schema": SCHEMA, "tool": {"name": "analyze_pd_rhythm_diagnostic.py", "version": VERSION}, "source": {"identity": prototype.SOURCE_ID, "sha256": digest(midi), "note_count": len(source_notes), "unique_onsets": len(source_onsets), "simultaneous_onset_groups": sum(count > 1 for count in source_simultaneous.values()), "simultaneous_group_size_distribution": dict(collections.Counter(source_simultaneous.values())), "duration_distribution_ticks": dict(sorted(durations.items())), "ioi_distribution_ticks": dict(sorted(collections.Counter(source_ioi).items())), "first_onset": min(source_onsets), "last_end": max(n.end for n in source_notes)}, "normalized_score": {"event_count": len(records), "onset_exact_vs_source": len(records), "duration_exact_vs_source": sum(r["source_duration"] == next(e["duration"] for e in events if e["event_id"] == r["xml_event_id"]) for r in records), "unique_absolute_onsets": len({r["absolute_normalized_onset"] for r in records}), "unique_measure_local_onsets": len({r["normalized_measure_local_onset"] for r in records})}, "quantization": {"grid_ticks": prototype.GRID_TICKS, "onset_exact_local": sum(r["quantization_delta_local_ticks"] == 0 for r in records), "onset_changed_local": sum(r["quantization_delta_local_ticks"] != 0 for r in records), "max_abs_delta_local": max(abs(r["quantization_delta_local_ticks"]) for r in records), "duration_exact_rows": sum(r["source_duration"] == r["quantized_duration_rows"] * prototype.GRID_TICKS for r in records), "duration_changed_rows": sum(r["source_duration"] != r["quantized_duration_rows"] * prototype.GRID_TICKS for r in records), "max_abs_duration_delta": max(abs(r["source_duration"] - r["quantized_duration_rows"] * prototype.GRID_TICKS) for r in records)}, "collision": {"group_count": len(group_records), "multi_event_groups": sum(g["member_count"] > 1 for g in group_records), "max_group_size": max(g["member_count"] for g in group_records), "selected": len(selected), "omitted": len(records) - len(selected), "classification_counts": dict(collections.Counter(g["classification"] for g in group_records)), "groups": group_records}, "selected_events": selected_source, "json": {"note_count": sum(x["note_count"] for x in json_channel_metrics.values()), "channels": json_channel_metrics, "selected_events": json_selected, "loop": json_data["loop"], "pattern_rows": 64}, "artifacts": {"source_sha256": digest(midi), "musicxml_sha256": digest(xml_path), "json_sha256": digest(artifact_dir / "maple_leaf_rag.prototype.json"), "uge_sha256": digest(artifact_dir / "maple_leaf_rag-timing-fixed.uge")}, "notes": ["Machine structural comparison only; no Human musical causality claim.", "ArrangementPlan uses measure-local normalized start for row calculation; cross-measure local cursor aggregation is reported explicitly."]}
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "maple_leaf_rag.rhythm-diagnostic.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = output / "maple_leaf_rag.rhythm-diagnostic.md"
    report_path.write_text("# Maple Leaf Rag rhythm diagnostic\n\n" + json.dumps({k: result[k] for k in ("source", "normalized_score", "quantization", "collision", "json", "artifacts", "notes")}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return json_path, report_path


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
