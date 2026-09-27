#!/usr/bin/env python3
"""Adapt the explainable plan's selected events to existing JSON V2."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as p

def emit(plan_path: Path, out: Path) -> Path:
    data=json.loads(plan_path.read_text())
    channels={"pulse1":[],"pulse2":[],"wave":[],"noise":[]}
    role_channel={"melody":"pulse1","harmony":"pulse2","bass":"wave","rhythm":"noise"}
    instrument={"pulse1":1,"pulse2":3,"wave":2,"noise":4}
    for e in data["events"]:
        if e["status"]!="selected": continue
        ch=role_channel[e["role"]]
        pitch=e["pitch"]
        while ch in ("pulse1","pulse2","wave") and pitch < {"pulse1":48,"pulse2":48,"wave":48}[ch]: pitch+=12
        while ch in ("pulse1","pulse2","wave") and pitch > {"pulse1":96,"pulse2":84,"wave":72}[ch]: pitch-=12
        channels[ch].append({"row":e["quantized_absolute_row"],"pitch":pitch,"length":max(1,round(e["duration"]/p.GRID_TICKS)),"source_event":e["source_event_id"],"original_pitch":e["pitch"],"instrument":instrument[ch]})
    plan={"channels":{k:sorted(v,key=lambda x:(x["row"],x["source_event"])) for k,v in channels.items()}}
    config={"ticks_per_row":p.TICKS_PER_ROW}
    result=p.make_json(plan,config); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n"); return out

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("plan",type=Path); a.add_argument("output",type=Path); x=a.parse_args(); print(emit(x.plan,x.output))
