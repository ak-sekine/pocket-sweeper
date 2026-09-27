#!/usr/bin/env python3
"""Report source pitch/role selection and downstream pitch preservation."""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import maple_leaf_rag_prototype as p
from analyze_pd_length_diagnostic import digest, token_metrics

SCHEMA = "maple-pd-pitch-melody-diagnostic/v1"
MEASURE_TICKS = 768

def note_name(n: int) -> str:
    return p.json_note_name(n)

def compare(midi: Path, artifact: Path, out: Path) -> tuple[Path, Path]:
    if digest(midi) != p.EXPECTED_SOURCE_SHA256: raise ValueError("source SHA-256 mismatch")
    ppq, tracks, _ = p.read_midi(midi)
    xml_events, _ = p.parse_musicxml(artifact / "maple_leaf_rag.generated.musicxml")
    by_part = collections.defaultdict(list)
    for e in xml_events: by_part[e["part"]].append(e)
    source_by_xml = {}
    for t in tracks:
        for n, e in zip(t.notes, by_part[f"P{t.index+1}"]): source_by_xml[e["event_id"]] = n
    manifest = json.loads((artifact / "maple_leaf_rag.manifest.json").read_text())
    plan, issues = p.group_patterns(xml_events, manifest["arrangement_configuration"])
    parts = collections.defaultdict(list)
    for e in xml_events: parts[e["part"]].append(e)
    averages = {k: sum(e["pitch"] for e in v)/len(v) for k,v in parts.items()}
    ranked = sorted(parts, key=lambda k: (-averages[k], k))
    roles = {ranked[0]: "melody"}
    if len(ranked)>1: roles[ranked[-1]]="bass"
    if len(ranked)>2:
        for k in ranked[1:-1]: roles[k]="harmony"
    channels={"melody":"pulse1","harmony":"pulse2","bass":"wave","rhythm":"noise"}
    selected = {e["source_event"]: (ch,e) for ch,es in plan["channels"].items() for e in es}
    groups=collections.defaultdict(list)
    all_records=[]
    for e in xml_events:
        n=source_by_xml[e["event_id"]]; role=roles[e["part"]]; ch=channels[role]
        row=round(e["start"]/p.GRID_TICKS); key=(role,row)
        rec={"source_event_id":n.event_id,"part":e["part"],"role":role,"channel":ch,"measure":e["measure"],"source_onset":n.start,"source_duration":n.end-n.start,"source_pitch":n.pitch,"source_note":note_name(n.pitch),"normalized_pitch":e["pitch"],"quantized_row":row,"group_key":[role,row]}
        if e["event_id"] in selected:
            out_ch, pe=selected[e["event_id"]]; rec.update({"status":"selected","arrangement_pitch":pe["pitch"],"octave_delta":pe["pitch"]-e["pitch"],"arrangement_row":pe["row"],"arrangement_event_id":e["event_id"],"selection_rule":"first in sorted (start,pitch,event_id) per role/local row"})
        else: rec.update({"status":"omitted","reason":"polyphony_omitted"})
        groups[key].append(rec); all_records.append(rec)
    for key, members in groups.items():
        for i,r in enumerate(members): r["collision_group_size"]=len(members); r["collision_member_index"]=i
    json_data=json.loads((artifact/"maple_leaf_rag.prototype.json").read_text())
    json_rows=[]
    for ch, patterns in json_data["patterns"].items():
        toks=token_metrics(next(iter(patterns.values())))["notes"]
        pes=sorted(plan["channels"].get(ch,[]),key=lambda e:(e["row"],e["source_event"]))
        for e,t in zip(pes,toks):
            n=source_by_xml[e["source_event"]]; jp=t["note"]
            json_rows.append({"source_event_id":n.event_id,"channel":ch,"json_row":t["row_start"],"json_note":jp,"arrangement_pitch":e["pitch"],"json_pitch":next((q for q in range(128) if note_name(q)==jp),None),"exact":note_name(e["pitch"])==jp})
    json_by_id={x["source_event_id"]:x for x in json_rows}
    for r in all_records:
        if r["status"]=="selected": r.update(json_by_id.get(r["source_event_id"],{"json_mapping":"window_or_token_omitted"}))
    source_notes=[n for t in tracks for n in t.notes]
    part_stats={}
    for k,v in parts.items():
        pitches=[e["pitch"] for e in v]; part_stats[k]={"event_count":len(v),"pitch_min":min(pitches),"pitch_max":max(pitches),"average_pitch":averages[k],"unique_pitches":len(set(pitches)),"role":roles[k]}
    role_counts={role:collections.Counter(r["status"] for r in all_records if r["role"]==role) for role in channels}
    result={"schema":SCHEMA,"source":{"identity":p.SOURCE_ID,"sha256":digest(midi),"ppq":ppq,"event_count":len(source_notes),"pitch_min":min(n.pitch for n in source_notes),"pitch_max":max(n.pitch for n in source_notes),"unique_pitches":len({n.pitch for n in source_notes})},"parts":part_stats,"role_counts":{k:dict(v) for k,v in role_counts.items()},"selection_rule":"sorted role events by (measure-local start, pitch, event_id); first event per (role, round(start/30)) wins","selected_events":sorted([r for r in all_records if r["status"]=="selected"],key=lambda r:(r["source_onset"],r["source_event_id"])),"omitted_pitch_summary":{role:collections.Counter(r["source_pitch"] for r in all_records if r["role"]==role and r["status"]=="omitted") for role in channels},"json":{"note_count":len(json_rows),"exact_pitch":sum(x["exact"] for x in json_rows),"rows":json_rows,"channels":{ch:sum(1 for x in json_rows if x["channel"]==ch) for ch in ("pulse1","pulse2","wave","noise")}},"uge":{"note_count":16,"format_level":"JSON/UGE note comparison from 01701: 16 exact, 0 mismatch"},"artifacts":{"source_sha256":digest(midi),"musicxml_sha256":digest(artifact/"maple_leaf_rag.generated.musicxml"),"json_sha256":digest(artifact/"maple_leaf_rag.prototype.json"),"uge_sha256":digest(artifact/"maple_leaf_rag-timing-fixed.uge")},"notes":["Machine structural evidence only; no Human melody correctness claim."]}
    out.mkdir(parents=True,exist_ok=True); jp=out/"maple_leaf_rag.pitch-melody-diagnostic.json"; mp=out/"maple_leaf_rag.pitch-melody-diagnostic.md"
    jp.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    mp.write_text("# Maple Leaf Rag pitch/melody diagnostic\n\n"+json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    return jp,mp

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("midi",type=Path); a.add_argument("artifact",type=Path); a.add_argument("output",type=Path); x=a.parse_args()
    for q in compare(x.midi,x.artifact,x.output): print(q)
