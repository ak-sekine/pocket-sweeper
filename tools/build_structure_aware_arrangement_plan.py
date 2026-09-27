#!/usr/bin/env python3
"""Structure-aware deterministic role and reduction diagnostic."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as p

def build(midi:Path, xml:Path, out:Path)->Path:
    if p.sha256(midi)!=p.EXPECTED_SOURCE_SHA256: raise ValueError("source SHA-256 mismatch")
    _,tracks,_=p.read_midi(midi); events,_=p.parse_musicxml(xml); by=collections.defaultdict(list)
    for e in events: by[e["part"]].append(e)
    source={}
    for t in tracks:
        for n,e in zip(t.notes,by[f"P{t.index+1}"]): source[e["event_id"]]=n
    by={k:v for k,v in by.items() if v}; roles={}; groups=collections.defaultdict(list)
    for e in events:
        n=source[e["event_id"]]; abs_tick=(e["measure"]-1)*768+e["start"]; groups[abs_tick].append(e)
    for onset, members in groups.items():
        for part in set(e["part"] for e in members):
            pm=[e for e in members if e["part"]==part]; ordered=sorted(pm,key=lambda e:(-e["pitch"],e["event_id"]))
            for i,e in enumerate(ordered):
                if part=="P2": roles[e["event_id"]]="melody" if i==0 else "harmony"
                elif part=="P3": roles[e["event_id"]]="bass" if i==len(ordered)-1 else "harmony"
                else: roles[e["event_id"]]="harmony"
    channels={"melody":"pulse1","harmony":"pulse2","bass":"wave","rhythm":"noise"}; selected=[]; omitted=[]; collision=collections.defaultdict(list)
    for e in events:
        n=source[e["event_id"]]; role=roles[e["event_id"]]; ch=channels[role]; abs_tick=(e["measure"]-1)*768+e["start"]; row=round(abs_tick/30); r={"source_event_id":n.event_id,"xml_event_id":e["event_id"],"part":e["part"],"measure":e["measure"],"absolute_onset":n.start,"pitch":n.pitch,"duration":n.end-n.start,"role":role,"channel":ch,"row":row}; collision[(role,ch,row)].append(r)
    for key, members in collision.items():
        members.sort(key=lambda r:(-r["duration"],-r["pitch"],r["source_event_id"]))
        for i,r in enumerate(members):
            r["collision_group"]="|".join(map(str,key)); r["status"]="selected" if i==0 else "omitted"; r["reason"]="structure_aware_representative" if i==0 else ("duplicate_pitch_omitted" if any(x["pitch"]==r["pitch"] for x in members[:i]) else "channel_capacity_omitted")
            (selected if i==0 else omitted).append(r)
    result={"schema":"structure-aware-arrangement-plan/v1","source":{"identity":p.SOURCE_ID,"sha256":p.sha256(midi),"events":len(events)},"rule":"P2 upper voice=melody, P3 lower voice=bass, remaining simultaneous source notes=harmony; per role/channel/absolute row choose longest duration, then pitch, then source_event_id","events":sorted(selected+omitted,key=lambda r:(r["absolute_onset"],r["source_event_id"])),"summary":{"input":len(events),"selected":len(selected),"omitted":len(omitted),"roles":{r:{"selected":sum(x["role"]==r for x in selected),"omitted":sum(x["role"]==r for x in omitted)} for r in channels},"collision_groups":len(collision),"harmony_selected":sum(x["role"]=="harmony" for x in selected)}}
    out.mkdir(parents=True,exist_ok=True); path=out/"arrangement-plan.structure-aware.json"; path.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); return path

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("midi",type=Path); a.add_argument("xml",type=Path); a.add_argument("output",type=Path); x=a.parse_args(); print(build(x.midi,x.xml,x.output))
