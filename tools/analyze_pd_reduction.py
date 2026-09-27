#!/usr/bin/env python3
"""Diagnose quantization, collision reduction, and pitch range transforms."""
from __future__ import annotations
import argparse, hashlib, json, statistics, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as prototype
from analyze_pd_role_extraction import assign_roles

SCHEMA = "maple-pd-reduction-diagnostic/v1"
GRID = 30
RANGES = {"pulse1": (48, 96), "pulse2": (48, 84), "wave": (48, 72), "noise": (0, 0)}
CHANNELS = {"melody": "pulse1", "harmony": "pulse2", "bass": "wave", "rhythm": "noise"}

def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def quantize(value: int, grid: int = GRID) -> int: return round(value / grid)
def shift_pitch(pitch: int, channel: str) -> tuple[int, int, bool]:
    original = pitch
    low, high = RANGES[channel]
    while pitch < low: pitch += 12
    while pitch > high: pitch -= 12
    return pitch, pitch - original, low <= pitch <= high
def collision_class(members: list[dict]) -> str:
    starts = {x["normalized_onset"] for x in members}
    return "PREEXISTING_SIMULTANEOUS" if len(starts) == 1 else "QUANTIZATION_INDUCED"
def contour(events: list[dict]) -> dict:
    ordered = sorted(events, key=lambda x: (x["onset"], x["pitch"], x["id"]))
    dirs=[]; intervals=[]
    for a,b in zip(ordered, ordered[1:]):
        d=b["pitch"]-a["pitch"]; intervals.append(d); dirs.append("UP" if d>0 else "DOWN" if d<0 else "SAME")
    return {"event_count":len(ordered),"counts":dict(Counter(dirs)),"intervals":intervals,"directions":dirs}

def analyze(midi: Path, upstream: Path, role_diag: Path, output: Path) -> tuple[Path, Path]:
    source_hash=digest(midi)
    if source_hash != prototype.EXPECTED_SOURCE_SHA256: raise ValueError("source SHA-256 mismatch")
    upstream_data=json.loads(upstream.read_text()); role_data=json.loads(role_diag.read_text())
    if upstream_data["source"]["sha256"] != source_hash or role_data["source"]["sha256"] != source_hash: raise ValueError("upstream source hash mismatch")
    ppq, tracks, meta=prototype.read_midi(midi); output.mkdir(parents=True,exist_ok=True)
    xml=output/"maple_leaf_rag.generated.musicxml"; prototype.write_musicxml(xml,ppq,tracks,meta); events,_=prototype.parse_musicxml(xml)
    source_ids={}; source_values={}
    for track in tracks:
        xs=[e for e in events if e["part"]==f"P{track.index+1}"]
        for s,x in zip(track.notes,xs): source_ids[x["event_id"]]=s.event_id; source_values[s.event_id]=s
    roles, ranked=assign_roles(events); event_role={e["event_id"]:role for role,es in roles.items() for e in es}
    records=[]; groups={}; role_counts={role:{"input":0,"unique_quantized_positions":set(),"collision_groups":0,"selected":0,"omitted":0} for role in CHANNELS}
    for e in events:
        sid=source_ids[e["event_id"]]; role=event_role[e["event_id"]]; channel=CHANNELS[role]; q=quantize(e["start"]); qp,delta,valid=shift_pitch(e["pitch"],channel)
        rec={"source_event_id":sid,"normalized_event_id":e["event_id"],"role":role,"channel":channel,"normalized_onset":e["start"],"quantized_onset":q,"quantization_delta":q*GRID-e["start"],"normalized_duration":e["duration"],"quantized_duration":max(1,round(e["duration"]/GRID)),"duration_delta":max(1,round(e["duration"]/GRID))*GRID-e["duration"],"original_pitch":e["pitch"],"post_shift_pitch":qp,"pitch_delta":delta,"range":RANGES[channel],"range_valid":valid,"history":["role_assigned","onset_quantized"]}
        records.append(rec); groups.setdefault((role,channel,q),[]).append(rec); role_counts[role]["input"]+=1; role_counts[role]["unique_quantized_positions"].add(q)
    collisions=[]; selected_ids=set()
    for key,members in sorted(groups.items(),key=lambda x:x[0]):
        cls=collision_class(members); selected=members[0]; selected_ids.add(selected["source_event_id"])
        for m in members:
            m["collision_group_id"]=f"{key[0]}:{key[1]}:row{key[2]}"; m["collision_class"]=cls
            if m is selected: m["selection"]="selected_first_sorted_event"
            else: m["selection"]="omitted"; m["omission_reason"]="polyphony_omitted"; m["history"].append("collision_omitted")
        if len(members)>1: collisions.append({"id":f"{key[0]}:{key[1]}:row{key[2]}","role":key[0],"channel":key[1],"row":key[2],"classification":cls,"members":[m["source_event_id"] for m in members],"pitches":[m["original_pitch"] for m in members],"selected":selected["source_event_id"],"omitted":[m["source_event_id"] for m in members[1:]],"selection_rule":"first event after sort (normalized onset, pitch, event_id)"})
    for r in records:
        role_counts[r["role"]]["selected" if r["source_event_id"] in selected_ids else "omitted"]+=1
        if r["pitch_delta"]: r["history"].append("octave_shift")
    for role in role_counts: role_counts[role]["unique_quantized_positions"]=len(role_counts[role]["unique_quantized_positions"]); role_counts[role]["collision_groups"]=sum(c["role"]==role for c in collisions)
    absq=[abs(r["quantization_delta"]) for r in records]; absd=[abs(r["duration_delta"]) for r in records]
    multi=[c for c in collisions if len(c["members"])>1]
    selected_records=[r for r in records if r["source_event_id"] in selected_ids]
    diag={"schema":SCHEMA,"tool":{"name":"analyze_pd_reduction.py","version":"1"},"source":{"identity":prototype.SOURCE_ID,"url":prototype.SOURCE_URL,"sha256":source_hash,"ppq":ppq},"upstream":{"preservation_diagnostic_sha256":digest(upstream),"role_diagnostic_sha256":digest(role_diag),"onset_mismatch":upstream_data["summary_metrics"]["onset_mismatch"]},"configuration":{"grid_ticks":GRID,"quantization":"round(start / 30) using Python round (banker's rounding); duration max(1, round(duration / 30))","collision_key":"logical_role + physical_channel + quantized_row","selection_rule":"first after (normalized onset, pitch, event_id) sort","actual_order":["role_assignment","onset_quantization","collision_grouping","first-event selection/polyphony omission","octave shift/range check","ArrangementPlan emission"],"scope":"full NormalizedScore/ArrangementPlan; JSON 64-row window not applied"},"records":records,"collision_groups":collisions,"role_summary":role_counts,"summary":{"input_events":len(records),"unique_quantized_positions":len({(r['role'],r['channel'],r['quantized_onset']) for r in records}),"collision_groups":len(multi),"preexisting_simultaneous_groups":sum(c["classification"]=="PREEXISTING_SIMULTANEOUS" for c in multi),"quantization_induced_groups":sum(c["classification"]=="QUANTIZATION_INDUCED" for c in multi),"mixed_groups":0,"max_group_size":max((len(c["members"]) for c in multi),default=0),"selected":len(selected_records),"omitted":len(records)-len(selected_records),"octave_shifted":sum(bool(r["pitch_delta"]) for r in records),"range_rejected":sum(not r["range_valid"] for r in records),"quantization_exact_onset":sum(r["quantization_delta"]==0 for r in records),"quantization_changed_onset":sum(r["quantization_delta"]!=0 for r in records),"max_abs_onset_delta":max(absq),"mean_abs_onset_delta":sum(absq)/len(absq),"median_abs_onset_delta":statistics.median(absq),"duration_exact":sum(x==0 for x in absd),"duration_changed":sum(x!=0 for x in absd),"emitted_onsets":len({r["quantized_onset"] for r in selected_records})},"contours":{"before":{role:contour([{"id":r["source_event_id"],"onset":r["normalized_onset"],"pitch":r["original_pitch"]} for r in records if r["role"]==role]) for role in ("melody","bass")},"after":{role:contour([{"id":r["source_event_id"],"onset":r["quantized_onset"],"pitch":r["post_shift_pitch"]} for r in selected_records if r["role"]==role]) for role in ("melody","bass")}}}
    j=output/"maple_leaf_rag.reduction-diagnostic.json"; j.write_text(json.dumps(diag,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    summary={k:diag[k] for k in ("source","upstream","configuration","role_summary","summary","contours")}; summary["diagnostic_sha256"]=digest(j); summary["note"]="Machine transformation evidence only; no Human musical-cause claim."
    md=output/"maple_leaf_rag.reduction-diagnostic.md"; md.write_text("# Maple Leaf Rag reduction diagnostic\n\n"+json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    return j,md
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("midi",type=Path); p.add_argument("upstream",type=Path); p.add_argument("role",type=Path); p.add_argument("output",type=Path); a=p.parse_args(); [print(x) for x in analyze(a.midi,a.upstream,a.role,a.output)]; return 0
if __name__=="__main__": raise SystemExit(main())
