#!/usr/bin/env python3
"""Emit JSON V2 multi-pattern data from absolute-row plan events."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as p

def emit(plan_path:Path,out:Path,tempo:int|None=None)->Path:
    x=json.loads(plan_path.read_text()); selected=[e for e in x["events"] if e["status"]=="selected"]
    max_row=max((e["row"] for e in selected),default=0); count=max_row//64+1
    channels={"pulse1":"melody","pulse2":"harmony","wave":"bass","noise":"rhythm"}; inst={"pulse1":1,"pulse2":3,"wave":2,"noise":4}; patterns={}; order={}
    for ch,role in channels.items():
        order[ch]=[]; patterns[ch]={}; fingerprints={}
        for i in range(count):
            row=0; tokens=[]
            es=sorted([e for e in selected if e["channel"]==ch and e["row"]//64==i],key=lambda e:(e["row"],e["source_event_id"]))
            for e in es:
                target=e["row"]%64
                if target<row: continue
                if target>row: tokens.append({"note":"rest","length":target-row,"instrument":inst[ch]}); row=target
                length=min(max(1,round(e["duration"]/p.GRID_TICKS)),64-row)
                if length<=0: continue
                pitch=e["pitch"]
                while ch in ("pulse1","pulse2","wave") and pitch<{"pulse1":48,"pulse2":48,"wave":48}[ch]: pitch+=12
                while ch in ("pulse1","pulse2","wave") and pitch>{"pulse1":96,"pulse2":84,"wave":72}[ch]: pitch-=12
                tokens.append({"note":p.json_note_name(pitch),"length":length,"instrument":inst[ch],"source_event_id":e["source_event_id"]}); row+=length
            if row<64: tokens.append({"note":"rest","length":64-row,"instrument":inst[ch]})
            # Provenance identifies source events, but does not change the
            # playable pattern.  Exclude it from deduplication so identical
            # musical patterns can be shared while the first token retains
            # its traceability metadata.
            canonical_tokens=[{k:v for k,v in token.items() if k != "source_event_id"} for token in tokens]
            fingerprint=json.dumps(canonical_tokens,sort_keys=True,separators=(",",":"))
            name=fingerprints.get(fingerprint)
            if name is None:
                name=f"structure_{ch}_{len(patterns[ch]):03d}"; patterns[ch][name]=tokens; fingerprints[fingerprint]=name
            order[ch].append(name)
    if tempo is None:
        tempo=p.TICKS_PER_ROW
    if not isinstance(tempo,int) or tempo < 1 or tempo > 255:
        raise ValueError("tempo must be an integer from 1 to 255")
    result={"version":2,"title":"Maple Leaf Rag Full Song Prototype","type":"bgm","tempo":tempo,"loop":{"mode":"none"},"instruments":[{"id":1,"name":"maple_lead","channel":"pulse1","duty":2,"length":0,"length_enable":False,"initial_volume":12,"envelope_direction":"down","envelope_sweep":0,"sweep_time":0,"sweep_direction":"down","sweep_shift":0},{"id":2,"name":"maple_bass","channel":"wave","waveform":"maple_triangle","output_level":"100%","length":0,"length_enable":False},{"id":3,"name":"maple_harmony","channel":"pulse2","duty":1,"length":0,"length_enable":False,"initial_volume":8,"envelope_direction":"down","envelope_sweep":0},{"id":4,"name":"unused_noise","channel":"noise","width_mode":"15bit","initial_volume":0,"envelope_direction":"down","envelope_sweep":0,"length":0,"length_enable":False}],"order":order,"patterns":patterns}
    result["wave_tables"]=[{"name":"maple_triangle","samples":[*range(16),*range(15,-1,-1)]}]
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n"); return out
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("plan",type=Path); a.add_argument("output",type=Path); a.add_argument("--tempo",type=int,default=None); x=a.parse_args(); print(emit(x.plan,x.output,x.tempo))
