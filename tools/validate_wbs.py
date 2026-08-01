from pathlib import Path
import datetime
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "wbs/tasks"
ID_RE = re.compile(r"^WBS-[0-9]{3}-[0-9]{5}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED = ("id", "title", "type", "status", "actor", "parent", "depends_on", "specs", "related_files", "outputs", "blocked_by", "source_wbs", "evidence_required", "updated")
LIST_FIELDS = ("depends_on", "specs", "related_files", "outputs", "blocked_by", "source_wbs")
SECTIONS = {"task": ("目的", "作業内容", "入力", "成果物", "完了条件", "完了にしてはいけない条件", "確認結果", "証跡"), "group": ("概要", "配下の作業")}

def load(directory=TASKS):
    items, issues = [], []
    for path in sorted(Path(directory).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            issues.append(("error", None, str(path), "YAML front matterを読み取れません")); continue
        end = text.find("\n---\n", 4)
        try: meta = yaml.safe_load(text[4:end]) or {}
        except Exception as exc:
            issues.append(("error", None, str(path), f"YAML解析失敗: {exc}")); continue
        if not isinstance(meta, dict):
            issues.append(("error", None, str(path), "front matterはmappingでなければなりません")); continue
        items.append((path, meta, text[end + 5:]))
    return items, issues

def _error(issues, ident, path, message):
    issues.append(("error", ident, str(path), message))

def _refs(value):
    return value if isinstance(value, list) else []

def _cycle(graph):
    state, stack, found = {}, [], []
    def visit(node):
        state[node] = 1; stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                found.append(stack[stack.index(nxt):] + [nxt])
            elif not state.get(nxt): visit(nxt)
        stack.pop(); state[node] = 2
    for node in graph:
        if not state.get(node): visit(node)
    return found

def validate(directory=TASKS, root=ROOT):
    items, issues = load(directory); byid = {}
    for path, meta, text in items:
        ident = meta.get("id")
        for field in REQUIRED:
            if field not in meta: _error(issues, ident, path, f"必須項目不足: {field}")
        type_ok = isinstance(meta.get("type"), str)
        if not isinstance(ident, str): _error(issues, ident, path, "idは文字列でなければなりません")
        elif not ID_RE.fullmatch(ident): _error(issues, ident, path, "ID形式不正")
        elif not ident.startswith("WBS-001-"): _error(issues, ident, path, "現行プロジェクト外のID")
        if path.stem != ident: _error(issues, ident, path, "ファイル名とIDが不一致")
        if ident in byid: _error(issues, ident, path, "ID重複")
        byid[ident] = (path, meta, text)
        for field in ("title", "type", "status", "actor"):
            if not isinstance(meta.get(field), str) or (field == "title" and not meta.get(field).strip()): _error(issues, ident, path, f"{field}は空でない文字列でなければなりません")
        if meta.get("type") not in {"group", "task"}: _error(issues, ident, path, "type不正")
        if meta.get("status") not in {"complete", "incomplete"}: _error(issues, ident, path, "status不正")
        if meta.get("actor") not in {"codex", "human", "none"}: _error(issues, ident, path, "actor不正")
        if meta.get("type") == "group" and meta.get("actor") != "none": _error(issues, ident, path, "groupのactorはnone")
        if meta.get("type") == "task" and meta.get("actor") == "none": _error(issues, ident, path, "taskのactorはnone不可")
        if meta.get("parent") is not None and not isinstance(meta.get("parent"), str): _error(issues, ident, path, "parentはnullまたは文字列")
        for field in LIST_FIELDS:
            if not isinstance(meta.get(field), list) or not all(isinstance(x, str) for x in _refs(meta.get(field))): _error(issues, ident, path, f"{field}は文字列配列")
        if not isinstance(meta.get("evidence_required"), bool): _error(issues, ident, path, "evidence_requiredは真偽値")
        if not isinstance(meta.get("updated"), str) or not DATE_RE.fullmatch(meta.get("updated", "")):
            _error(issues, ident, path, "updatedはYYYY-MM-DD形式の文字列")
        for section in SECTIONS.get(meta.get("type"), ()):
            if not re.search(rf"^# {re.escape(section)}\s*$", text, re.M): _error(issues, ident, path, f"必須セクション不足: {section}")
        for ref in _refs(meta.get("source_wbs")):
            if not ID_RE.fullmatch(ref): _error(issues, ident, path, f"source_wbsのID形式不正: {ref}")
            if ref == meta.get("parent") or ref in _refs(meta.get("depends_on")): _error(issues, ident, path, "source_wbsをparent/depends_onと混用")
        for field in ("specs", "related_files"):
            for ref in _refs(meta.get(field)):
                matches = list((root / ref).parent.glob((root / ref).name)) if any(c in ref for c in "*?[") else [(root / ref) if (root / ref).exists() else None]
                if not any(x is not None and x.exists() for x in matches): _error(issues, ident, path, f"{field}のパスが存在しません: {ref}")
        if meta.get("actor_review_required"): issues.append(("warning", ident, str(path), "担当未確定・要確認"))
    parent_graph, dep_graph = {}, {}
    for ident, (path, meta, _) in byid.items():
        parent = meta.get("parent")
        parent_graph[ident] = [parent] if isinstance(parent, str) else []
        dep_graph[ident] = _refs(meta.get("depends_on"))
        if parent == ident: _error(issues, ident, path, "自分自身をparentに指定")
        if parent and parent not in byid: _error(issues, ident, path, "親が存在しない")
        for dep in _refs(meta.get("depends_on")):
            if dep == ident: _error(issues, ident, path, "自分自身へ依存")
            elif dep not in byid: _error(issues, ident, path, "依存先が存在しない")
            elif meta.get("status") == "complete" and byid[dep][1].get("status") != "complete": _error(issues, ident, path, "完了タスクが未完了タスクへ依存")
    for label, graph in (("親", parent_graph), ("依存", dep_graph)):
        for cycle in _cycle(graph): issues.append(("error", cycle[0], str(byid[cycle[0]][0]), f"{label}循環: {' -> '.join(cycle)}"))
    seen_titles = {}
    for ident, (path, meta, _) in byid.items():
        key = meta.get("parent")
        if (key, meta.get("title")) in seen_titles: issues.append(("warning", ident, str(path), "同一親配下に同名項目"))
        seen_titles[(key, meta.get("title"))] = ident
        if meta.get("type") == "group" and meta.get("status") == "complete":
            for child, (_, cm, _) in byid.items():
                cur = cm.get("parent")
                while cur:
                    if cur == ident and cm.get("status") != "complete":
                        issues.append(("warning", ident, str(path), "完了した親に未完了子孫（移行前からの矛盾）")); break
                    cur = byid.get(cur, (None, {}, ""))[1].get("parent")
    return byid, issues

if __name__ == "__main__":
    _, issues = validate()
    for kind, ident, path, message in issues: print(f"{kind}: {ident or '-'}: {path}: {message}")
    print(f"errors={sum(x[0] == 'error' for x in issues)} warnings={sum(x[0] == 'warning' for x in issues)}")
    sys.exit(1 if any(x[0] == "error" for x in issues) else 0)
