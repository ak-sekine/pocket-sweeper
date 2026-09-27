#!/usr/bin/env python3
"""Build a deterministic, source-traceable ArrangementPlan sidecar.

This diagnostic plan deliberately keeps JSON windowing out of the stage. It
records every normalized event and makes any channel collision explicit.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as p

MEASURE_TICKS = 768
POLICY = "prefer_longer_duration_then_higher_pitch_then_source_event_id"

def build(midi: Path, musicxml: Path, out: Path) -> Path:
    if p.sha256(midi) != p.EXPECTED_SOURCE_SHA256: raise ValueError("source SHA-256 mismatch")
    _, tracks, _ = p.read_midi(midi); events, _ = p.parse_musicxml(musicxml)
    by_part=collections.defaultdict(list)
    for e in events: by_part[e["part"]].append(e)
    source={}
    for t in tracks:
        for n,e in zip(t.notes,by_part[f"P{t.index+1}"]): source[e["event_id"]]=n
    by_part={k:v for k,v in by_part.items() if v}
    ranked=sorted(by_part,key=lambda k:(-sum(e["pitch"] for e in by_part[k])/len(by_part[k]),k))
    roles={ranked[0]:"melody"}
    if len(ranked)>1: roles[ranked[-1]]="bass"
    for k in ranked[1:-1]: roles[k]="harmony"
    channels={"melody":"pulse1","harmony":"pulse2","bass":"wave","rhythm":"noise"}
    ranges={"pulse1":(48,96),"pulse2":(48,84),"wave":(48,72),"noise":(0,0)}
    records=[]; groups=collections.defaultdict(list)
    for e in events:
        n=source[e["event_id"]]; role=roles[e["part"]]; ch=channels[role]
        absolute=(int(e["measure"])-1)*MEASURE_TICKS+int(e["start"]); row=round(absolute/p.GRID_TICKS)
        r={"source_event_id":n.event_id,"xml_event_id":e["event_id"],"part":e["part"],"measure":e["measure"],"absolute_onset":n.start,"measure_local_onset":e["start"],"duration":n.end-n.start,"pitch":n.pitch,"role":role,"channel":ch,"quantized_absolute_row":row,"status":"unclassified"}
        records.append(r); groups[(role,ch,row)].append(r)
    for key,members in groups.items():
        members.sort(key=lambda r:(-r["duration"],-r["pitch"],r["source_event_id"]))
        for i,r in enumerate(members):
            r["collision_group"]="|".join(map(str,key)); r["collision_group_size"]=len(members); r["collision_member_index"]=i
            if i==0:
                r["status"]="selected"; r["selection_reason"]=POLICY
            else:
                r["status"]="omitted"; r["omission_reason"]="same_role_channel_quantized_absolute_row"
    result={"schema":"explainable-arrangement-plan/v1","source":{"identity":p.SOURCE_ID,"sha256":p.sha256(midi),"event_count":len(records)},"policy":POLICY,"role_rule":"highest average pitch part=melody; lowest= bass; intermediate=harmony","channels":channels,"events":sorted(records,key=lambda r:(r["absolute_onset"],r["source_event_id"])),"summary":{"input":len(records),"selected":sum(r["status"]=="selected" for r in records),"omitted":sum(r["status"]=="omitted" for r in records),"by_role":{role:{"input":sum(r["role"]==role for r in records),"selected":sum(r["role"]==role and r["status"]=="selected" for r in records),"omitted":sum(r["role"]==role and r["status"]=="omitted" for r in records)} for role in ("melody","harmony","bass","rhythm")},"collision_groups":len(groups),"multi_event_groups":sum(len(v)>1 for v in groups.values()),"cross_measure_local_false_collision":0}}
    out.mkdir(parents=True,exist_ok=True); path=out/"arrangement-plan.explainable.json"; path.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); return path

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("midi",type=Path); a.add_argument("musicxml",type=Path); a.add_argument("output",type=Path); x=a.parse_args(); print(build(x.midi,x.musicxml,x.output))
