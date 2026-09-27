#!/usr/bin/env python3
"""Extract a contiguous measure range from a structure-aware plan.

The output keeps all plan events in the range for provenance, rebases selected
runtime rows to the first selected row, and writes a separate source mapping
sidecar. It does not alter arrangement-role or pitch-selection rules.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def extract(plan_path: Path, start: int, end: int, out_plan: Path, out_sidecar: Path) -> None:
    if start < 1 or end < start:
        raise ValueError("measure range must be positive and contiguous")
    source = json.loads(plan_path.read_text(encoding="utf-8"))
    events = source["events"]
    in_range = [e for e in events if start <= e["measure"] <= end]
    selected = [e for e in in_range if e["status"] == "selected"]
    if not selected:
        raise ValueError("measure range contains no selected events")
    base_row = min(e["row"] for e in selected)
    rebased = []
    sidecar = []
    for event in in_range:
        item = dict(event)
        item["original_row"] = event["row"]
        item["row"] = event["row"] - base_row
        rebased.append(item)
        sidecar.append({
            "source_event_id": event["source_event_id"],
            "measure": event["measure"],
            "original_absolute_onset": event["absolute_onset"],
            "original_quantized_row": event["row"],
            "rebased_row": item["row"],
            "status": event["status"],
            "role": event["role"],
            "channel": event["channel"],
            "pitch": event["pitch"],
            "duration": event["duration"],
        })
    result = dict(source)
    result["events"] = rebased
    result["source"] = dict(source.get("source", {}))
    result["source"]["measure_range"] = [start, end]
    result["source"]["timeline_rebase_row"] = base_row
    result["summary"] = {
        "input_events_in_range": len(in_range),
        "selected_events_in_range": len(selected),
        "measure_range": [start, end],
        "timeline_rebase_row": base_row,
    }
    out_plan.parent.mkdir(parents=True, exist_ok=True)
    out_sidecar.parent.mkdir(parents=True, exist_ok=True)
    out_plan.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_sidecar.write_text(json.dumps({"measure_range": [start, end], "events": sidecar}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("output_plan", type=Path)
    parser.add_argument("output_sidecar", type=Path)
    args = parser.parse_args()
    extract(args.plan, args.start, args.end, args.output_plan, args.output_sidecar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
