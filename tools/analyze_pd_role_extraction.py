#!/usr/bin/env python3
"""Measure NormalizedScore -> ArrangementPlan role extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype


SCHEMA = "maple-pd-role-diagnostic/v1"
VERSION = "1"
CHANNELS = {"melody": "pulse1", "harmony": "pulse2", "bass": "wave", "rhythm": "noise"}
ROLES = ("melody", "bass", "harmony", "rhythm")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contour(events: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(events, key=lambda e: (e["start"], e["pitch"], e["event_id"]))
    directions: list[str] = []
    intervals: list[int] = []
    for previous, current in zip(ordered, ordered[1:]):
        delta = current["pitch"] - previous["pitch"]
        intervals.append(delta)
        directions.append("UP" if delta > 0 else "DOWN" if delta < 0 else "SAME")
    return {"event_count": len(ordered), "intervals": intervals, "directions": directions, "counts": dict(Counter(directions))}


def part_stats(events: list[dict[str, Any]], role_by_part: dict[str, str]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        grouped.setdefault(event["part"], []).append(event)
    result = []
    for part in sorted(grouped):
        values = grouped[part]
        result.append({"part": part, "event_count": len(values), "min_pitch": min(e["pitch"] for e in values), "max_pitch": max(e["pitch"] for e in values), "average_pitch": sum(e["pitch"] for e in values) / len(values), "median_pitch": statistics.median(e["pitch"] for e in values), "onset_min": min(e["start"] for e in values), "onset_max": max(e["start"] for e in values), "duration_min": min(e["duration"] for e in values), "duration_max": max(e["duration"] for e in values), "simultaneous_group_count": len({(e["start"], e["part"]) for e in values}), "assigned_role": role_by_part[part]})
    return result


def assign_roles(events: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    by_part: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    ranked = sorted(by_part, key=lambda key: (-sum(e["pitch"] for e in by_part[key]) / len(by_part[key]), key))
    roles: dict[str, list[dict[str, Any]]] = {role: [] for role in ROLES}
    if ranked:
        roles["melody"] = by_part[ranked[0]]
        if len(ranked) > 1:
            roles["bass"] = by_part[ranked[-1]]
            roles["harmony"] = [e for key in ranked[1:-1] for e in by_part[key]]
        else:
            roles["bass"] = [e for e in by_part[ranked[0]] if e["pitch"] <= 60]
            roles["harmony"] = [e for e in by_part[ranked[0]] if e["pitch"] > 60]
    return roles, ranked


def analyze(midi: Path, upstream: Path, output: Path) -> tuple[Path, Path]:
    source_hash = digest(midi)
    if source_hash != prototype.EXPECTED_SOURCE_SHA256:
        raise ValueError(f"source SHA-256 mismatch: expected {prototype.EXPECTED_SOURCE_SHA256}, got {source_hash}")
    upstream_data = json.loads(upstream.read_text(encoding="utf-8"))
    if upstream_data["source"]["sha256"] != source_hash:
        raise ValueError("upstream diagnostic source hash mismatch")
    ppq, tracks, midi_meta = prototype.read_midi(midi)
    output.mkdir(parents=True, exist_ok=True)
    xml = output / "maple_leaf_rag.generated.musicxml"
    prototype.write_musicxml(xml, ppq, tracks, midi_meta)
    events, xml_meta = prototype.parse_musicxml(xml)
    by_part: dict[str, list[dict[str, Any]]] = {}
    source_by_event: dict[str, str] = {}
    source_events: dict[str, dict[str, Any]] = {}
    for track in tracks:
        source_notes = list(track.notes)
        xml_notes = [e for e in events if e["part"] == f"P{track.index + 1}"]
        if len(source_notes) != len(xml_notes):
            raise ValueError("source/XML note count mismatch")
        for source, xml_event in zip(source_notes, xml_notes):
            source_by_event[xml_event["event_id"]] = source.event_id
            source_events[source.event_id] = {"source_event_id": source.event_id, "part": xml_event["part"], "track": source.track, "pitch": xml_event["pitch"], "onset": xml_event["start"], "duration": xml_event["duration"], "source_onset": source.start, "source_duration": source.end - source.start}
    for event in events:
        by_part.setdefault(event["part"], []).append(event)
    roles, ranked = assign_roles(events)
    role_by_part = {}
    for role, role_events in roles.items():
        for event in role_events:
            role_by_part[event["part"]] = role
    config = {"quantization_grid_ticks": prototype.GRID_TICKS, "pitch_range": {"pulse1": [48, 96], "pulse2": [48, 84], "wave": [48, 72], "noise": [0, 0]}, "mapping": CHANNELS, "role_algorithm": "highest average pitch melody; lowest average pitch bass; middle parts harmony; one-part fallback pitch <=60 bass and >60 harmony", "tie_break": "part ID ascending after descending average pitch"}
    plan, losses = prototype.group_patterns(events, {**config, "ticks_per_row": prototype.TICKS_PER_ROW, "ch4_policy": "unused", "repeat_policy": "do_not_infer", "loop_policy": "none", "prototype_range": "full normalized source; JSON window is later"})
    plan_by_xml = {event["source_event"]: event for channel in plan["channels"].values() for event in channel}
    loss_by_xml = {loss["event_id"]: loss for loss in losses if "event_id" in loss}
    mapping = []
    for event in events:
        source_id = source_by_event[event["event_id"]]
        role = next(role for role, values in roles.items() if event in values)
        emitted = event["event_id"] in plan_by_xml
        loss = loss_by_xml.get(event["event_id"])
        status = "TRANSFORMED" if emitted and plan_by_xml[event["event_id"]]["pitch"] != event["pitch"] else "PRESERVED" if emitted else "OMITTED"
        mapping.append({"source_event_id": source_id, "normalized_event_id": event["event_id"], "logical_role": role, "physical_channel": CHANNELS[role], "role_assignment": "selected", "arrangement_status": status, "reason": loss.get("reason") if loss else None, "source_onset": source_events[source_id]["source_onset"], "normalized_onset": event["start"], "arrangement_row": plan_by_xml[event["event_id"]]["row"] if emitted else None, "source_pitch": event["pitch"], "arrangement_pitch": plan_by_xml[event["event_id"]]["pitch"] if emitted else None})
    role_summary = {}
    for role in ROLES:
        values = [m for m in mapping if m["logical_role"] == role]
        role_summary[role] = {"input_event_count": len(values), "selected_count": sum(m["arrangement_status"] != "OMITTED" for m in values), "omitted_count": sum(m["arrangement_status"] == "OMITTED" for m in values), "transformed_count": sum(m["arrangement_status"] == "TRANSFORMED" for m in values), "rejected_count": sum(m["reason"] == "range_reject" for m in values), "output_event_count": sum(m["arrangement_status"] != "OMITTED" for m in values), "source_pitch_range": [min((m["source_pitch"] for m in values), default=None), max((m["source_pitch"] for m in values), default=None)], "arrangement_pitch_range": [min((m["arrangement_pitch"] for m in values if m["arrangement_pitch"] is not None), default=None), max((m["arrangement_pitch"] for m in values if m["arrangement_pitch"] is not None), default=None)], "contour": contour([e for e in events if e["event_id"] in {m["normalized_event_id"] for m in values}])}
    role_diag = {"schema": SCHEMA, "tool": {"name": "analyze_pd_role_extraction.py", "version": VERSION}, "source": {"identity": prototype.SOURCE_ID, "url": prototype.SOURCE_URL, "sha256": source_hash, "ppq": ppq}, "upstream": {"diagnostic_sha256": digest(upstream), "scope": upstream_data["configuration"]["scope"], "onset_mismatch": upstream_data["summary_metrics"]["onset_mismatch"]}, "configuration": config, "part_statistics": part_stats(events, role_by_part), "average_pitch_ranking": [{"rank": i + 1, "part": part, "average_pitch": sum(e["pitch"] for e in by_part[part]) / len(by_part[part]), "assigned_role": role_by_part[part]} for i, part in enumerate(ranked)], "role_summary": role_summary, "channel_allocation": CHANNELS, "event_mappings": mapping, "losses": losses, "summary_metrics": {"normalized_total": len(events), "role_assigned": len(mapping), "unassigned": 0, "arrangement_emitted": sum(m["arrangement_status"] != "OMITTED" for m in mapping), "omitted": sum(m["arrangement_status"] == "OMITTED" for m in mapping), "transformed": sum(m["arrangement_status"] == "TRANSFORMED" for m in mapping), "rejected": sum(m["reason"] == "range_reject" for m in mapping), "rhythm_input": 0, "ch4_used": False, "full_source_scope": True, "json_window_applied": False}}
    json_path = output / "maple_leaf_rag.role-diagnostic.json"
    json_path.write_text(json.dumps(role_diag, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    md_path = output / "maple_leaf_rag.role-diagnostic.md"
    md_path.write_text("# Maple Leaf Rag role extraction diagnostic\n\n" + json.dumps({"schema": SCHEMA, "source": role_diag["source"], "average_pitch_ranking": role_diag["average_pitch_ranking"], "role_summary": role_summary, "summary_metrics": role_diag["summary_metrics"], "note": "Machine role/coverage evidence only; no musical correctness claim."}, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", type=Path)
    parser.add_argument("upstream_diagnostic", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    paths = analyze(args.midi, args.upstream_diagnostic, args.output)
    for path in paths: print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
