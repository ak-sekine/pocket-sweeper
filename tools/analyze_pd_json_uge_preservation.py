#!/usr/bin/env python3
"""Compare selected ArrangementPlan events with JSON V2 and UGE cells."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

SCHEMA="maple-pd-json-uge-diagnostic/v1"
CHANNELS=("pulse1","pulse2","wave","noise")
CH_TO_UGE={"pulse1":"ch1","pulse2":"ch2","wave":"ch3","noise":"ch4"}
NAMES={"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def note_pitch(note):
    if note=="rest": return None
    m=re.fullmatch(r"([A-G])(#?)([0-9]+)",note)
    if not m: return None
    return (int(m.group(3))+1)*12+NAMES[m.group(1)]+(1 if m.group(2) else 0)
def json_events(data):
    result=[]
    for channel in CHANNELS:
        pattern_name=next(iter(data["patterns"][channel]))
        row=0
        for index,cell in enumerate(data["patterns"][channel][pattern_name]):
            result.append({"channel":channel,"pattern":pattern_name,"index":index,"row":row,"length":cell["length"],"note":cell["note"],"pitch":note_pitch(cell["note"]),"instrument":cell["instrument"],"synthetic":cell["note"]=="rest"})
            row+=cell["length"]
    return result
def analyze(reduction_path,json_path,uge_analysis,output):
    reduction=json.loads(reduction_path.read_text()); data=json.loads(json_path.read_text()); uge=json.loads(uge_analysis.read_text())[0]
    selected_ids={c["selected"] for c in reduction["collision_groups"]}
    selected=[r for r in reduction["records"] if r["source_event_id"] in selected_ids]
    je=json_events(data); notes=[x for x in je if not x["synthetic"]]
    mappings=[]
    selected_by_channel={c:sorted([r for r in selected if r["channel"]==c],key=lambda r:(r["quantized_onset"],r["source_event_id"])) for c in CHANNELS}
    json_notes_by_channel={c:sorted([x for x in notes if x["channel"]==c],key=lambda x:x["index"]) for c in CHANNELS}
    ordinal={c:0 for c in CHANNELS}
    for r in selected:
        local=r["quantized_onset"]
        in_window=0<=local<64
        j=None
        if in_window:
            inside=[x for x in selected_by_channel[r["channel"]] if 0<=x["quantized_onset"]<64]
            pos=inside.index(r)
            if pos < len(json_notes_by_channel[r["channel"]]): j=json_notes_by_channel[r["channel"]][pos]
        mappings.append({"source_event_id":r["source_event_id"],"role":r["role"],"physical_channel":r["channel"],"arrangement_row":local,"window_status":"inside" if in_window and j else "prototype_window_overflow" if in_window and not j else "outside","json":j,"status":"mapped" if j else "prototype_window"})
    j_by_ch={c:[x for x in notes if x["channel"]==c] for c in CHANNELS}
    uge_notes={}
    for c in CHANNELS:
        u=uge["channels"][CH_TO_UGE[c]]
        # analyze_uge stores pattern cells keyed by numeric pattern key.
        cells=uge["pattern_cells"][str(u["order_pattern_keys"][0])]
        uge_notes[c]=[{"row":i,"note":cell[0],"instrument":cell[1]} for i,cell in enumerate(cells) if cell[0]!=90]
    json_uge=[]
    for c in CHANNELS:
        for x in j_by_ch[c]:
            u=[z for z in uge_notes[c] if z["row"]==x["row"]]
            json_uge.append({"channel":c,"json":x,"uge":u[0] if u else None,"status":"exact" if u and u[0]["note"]==x["pitch"]-48 and u[0]["instrument"]==x["instrument"] else "unmapped"})
    pattern_summary={c:{"pattern_count":len(data["patterns"][c]),"rows_total":sum(x["length"] for x in data["patterns"][c][next(iter(data["patterns"][c]))]),"note_count":len(j_by_ch[c]),"rest_cells":sum(x["synthetic"] for x in je if x["channel"]==c)} for c in CHANNELS}
    diag={"schema":SCHEMA,"tool":{"name":"analyze_pd_json_uge_preservation.py","version":"1"},"source":reduction["source"],"upstream":{"reduction_sha256":digest(reduction_path),"role_diagnostic_sha256":reduction["upstream"]["role_diagnostic_sha256"],"preservation_diagnostic_sha256":reduction["upstream"]["preservation_diagnostic_sha256"]},"configuration":{"window_start":0,"window_end_inclusive":63,"window_stage":"JSON pattern emission","json_channels":CHANNELS,"uge_channels":CH_TO_UGE},"arrangement_baseline":{"input_events":len(reduction["records"]),"selected_events":len(selected),"by_role":{role:sum(r["role"]==role for r in selected) for role in ("melody","harmony","bass","rhythm")}},"arrangement_to_json":{"mappings":mappings,"summary":{"input":len(selected),"encoded":sum(x["status"]=="mapped" for x in mappings),"window_omitted":sum(x["status"]=="prototype_window" for x in mappings),"unmapped":sum(x["status"]=="unmapped" for x in mappings),"pitch_exact":sum(x["json"] is not None and x["json"]["pitch"]==next(r["post_shift_pitch"] for r in selected if r["source_event_id"]==x["source_event_id"]) for x in mappings),"row_exact":sum(x["json"] is not None and x["json"]["row"]==x["arrangement_row"] for x in mappings)}},"json_structure":pattern_summary,"json_to_uge":{"mappings":json_uge,"summary":{"json_notes":len(json_uge),"uge_notes":sum(len(x) for x in uge_notes.values()),"exact":sum(x["status"]=="exact" for x in json_uge),"unmapped":sum(x["status"]!="exact" for x in json_uge)}},"tempo":{"source_microseconds_per_quarter":500000,"source_bpm":120,"json_ticks_per_row":data["tempo"],"uge_tempo_raw":uge["tempo_raw"]},"loop":{"intended":"none","json":data["loop"],"uge_analyzer":uge["loop"]},"empty_channels":{"pulse2_notes":len(j_by_ch["pulse2"]),"noise_notes":len(j_by_ch["noise"]),"representation":"rest-only pattern with default instrument"},"runtime_unknowns":["hUGEDriver real-time timing","APU writes","audible duration","SameBoy playback","Human musical equivalence"]}
    output.mkdir(parents=True,exist_ok=True); j=output/"maple_leaf_rag.json-uge-diagnostic.json"; j.write_text(json.dumps(diag,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    md=output/"maple_leaf_rag.json-uge-diagnostic.md"; md.write_text("# Maple Leaf Rag JSON/UGE preservation diagnostic\n\n"+json.dumps({k:diag[k] for k in ("source","upstream","configuration","arrangement_baseline","arrangement_to_json","json_structure","json_to_uge","tempo","loop","empty_channels","runtime_unknowns")},indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    return j,md
def main():
    p=argparse.ArgumentParser();p.add_argument("reduction",type=Path);p.add_argument("json",type=Path);p.add_argument("uge_analysis",type=Path);p.add_argument("output",type=Path);a=p.parse_args();[print(x) for x in analyze(a.reduction,a.json,a.uge_analysis,a.output)]
if __name__=="__main__":main()
