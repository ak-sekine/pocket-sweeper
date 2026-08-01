from pathlib import Path
import re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "wbs/tasks"
ID_RE = re.compile(r"^WBS-[0-9]{3}-[0-9]{5}$")
REQUIRED = ["id","title","type","status","actor","parent","depends_on","specs","related_files","outputs","blocked_by","source_wbs","evidence_required","updated"]
SECTIONS = {"task": ["目的","作業内容","入力","成果物","完了条件","完了にしてはいけない条件","確認結果","証跡"], "group": ["概要","配下の作業"]}

def load(directory=TASKS):
    out=[]; issues=[]
    for path in sorted(Path(directory).glob("*.md")):
        text=path.read_text()
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            issues.append(("error",None,str(path),"YAML front matterを読み取れません")); continue
        end=text.find("\n---\n",4)
        try: meta=yaml.safe_load(text[4:end]) or {}
        except Exception as e: issues.append(("error",None,str(path),f"YAML解析失敗: {e}")); continue
        out.append((path,meta,text[end+5:]))
    return out,issues

def validate(directory=TASKS):
    items, issues=load(directory); byid={}; valid_types={"group","task"}; valid_status={"complete","incomplete"}; valid_actor={"codex","human","none"}
    for path,m,text in items:
        ident=m.get("id")
        for k in REQUIRED:
            if k not in m: issues.append(("error",ident,str(path),f"必須項目不足: {k}"))
        if not isinstance(ident,str) or not ID_RE.fullmatch(ident or ""): issues.append(("error",ident,str(path),"ID形式不正"))
        elif not ident.startswith("WBS-001-"): issues.append(("error",ident,str(path),"現行プロジェクト外のID"))
        if path.stem != ident: issues.append(("error",ident,str(path),"ファイル名とIDが不一致"))
        if ident in byid: issues.append(("error",ident,str(path),"ID重複"))
        byid[ident]=(path,m,text)
        if m.get("type") not in valid_types: issues.append(("error",ident,str(path),"type不正"))
        if m.get("status") not in valid_status: issues.append(("error",ident,str(path),"status不正"))
        if m.get("actor") not in valid_actor: issues.append(("error",ident,str(path),"actor不正"))
        if m.get("type")=="group" and m.get("actor")!="none": issues.append(("error",ident,str(path),"groupのactorはnone"))
        if m.get("type")=="task" and m.get("actor")=="none": issues.append(("error",ident,str(path),"taskのactorはnone不可"))
        for s in SECTIONS.get(m.get("type"),[]):
            if not re.search(rf"^# {re.escape(s)}\s*$",text,re.M): issues.append(("error",ident,str(path),f"必須セクション不足: {s}"))
        for field in ("parent","depends_on"):
            vals=[] if field=="depends_on" else ([m.get(field)] if m.get(field) else [])
            vals = vals if field=="parent" else (m.get(field) or [])
            for ref in vals:
                if not isinstance(ref,str) or not ID_RE.fullmatch(ref): issues.append(("error",ident,str(path),f"{field}のID形式不正: {ref}"))
                elif not ref.startswith("WBS-001-"): issues.append(("error",ident,str(path),f"{field}が別プロジェクト"))
        for ref in m.get("source_wbs") or []:
            if not isinstance(ref,str) or not ID_RE.fullmatch(ref): issues.append(("error",ident,str(path),"source_wbsのID形式不正"))
        if m.get("actor_review_required"): issues.append(("warning",ident,str(path),"担当未確定・要確認"))
    for ident,(path,m,text) in byid.items():
        p=m.get("parent")
        if p and p not in byid: issues.append(("error",ident,str(path),"親が存在しない"))
        for d in m.get("depends_on") or []:
            if d not in byid: issues.append(("error",ident,str(path),"依存先が存在しない"))
            elif m.get("status")=="complete" and byid[d][1].get("status")!="complete": issues.append(("error",ident,str(path),"完了タスクが未完了タスクへ依存"))
        seen=set(); cur=ident
        while cur:
            if cur in seen: issues.append(("error",ident,str(path),"親循環")); break
            seen.add(cur); cur=byid.get(cur,(None,{}))[1].get("parent")
    for ident,(path,m,text) in byid.items():
        if m.get("type")=="group" and m.get("status")=="complete":
            for cid,(cp,cm,_) in byid.items():
                cur=cm.get("parent")
                while cur:
                    if cur==ident and cm.get("status")!="complete": issues.append(("warning",ident,str(path),"完了した親に未完了子孫（移行前からの矛盾）")); break
                    cur=byid.get(cur,(None,{}))[1].get("parent")
        if m.get("parent") and m.get("parent") in (m.get("depends_on") or []): issues.append(("error",ident,str(path),"親を依存先に指定"))
    return byid,issues

if __name__ == "__main__":
    _, issues=validate();
    for kind,ident,path,msg in issues: print(f"{kind}: {ident or '-'}: {path}: {msg}")
    print(f"errors={sum(x[0]=='error' for x in issues)} warnings={sum(x[0]=='warning' for x in issues)}")
    sys.exit(1 if any(x[0]=='error' for x in issues) else 0)
