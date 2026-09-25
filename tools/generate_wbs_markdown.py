#!/usr/bin/env python3
"""Generate the deterministic, human-readable WBS index."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_wbs import ROOT, TASKS, validate

OUT = ROOT / "reports/wbs.md"


def _tree(data):
    children = {ident: [] for ident in data}
    for ident, (_, meta, _) in data.items():
        if meta.get("parent") in children:
            children[meta["parent"]].append(ident)
    order = []

    def visit(ident, level):
        order.append((ident, level))
        for child in children[ident]:
            visit(child, level + 1)

    for ident, (_, meta, _) in data.items():
        if not meta.get("parent"):
            visit(ident, 0)
    return order


def generate_wbs_markdown(tasks_dir=TASKS, output=OUT):
    tasks_dir = Path(tasks_dir)
    root = tasks_dir.resolve().parents[1]
    data, issues = validate(tasks_dir, root)
    if any(issue[0] == "error" for issue in issues):
        raise ValueError("WBS validation failed; Markdown was not generated")
    lines = ["# WBS一覧", ""]
    for ident, level in _tree(data):
        meta = data[ident][1]
        checkbox = "x" if meta["status"] == "complete" else " "
        title = " ".join(str(meta["title"]).split())
        lines.append(f'{"  " * level}- [{checkbox}] {ident} {title}')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return output


if __name__ == "__main__":
    print(generate_wbs_markdown())
