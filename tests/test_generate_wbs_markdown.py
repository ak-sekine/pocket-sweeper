import tempfile
import unittest
import re
from pathlib import Path

import yaml

from tools.generate_wbs_markdown import generate_wbs_markdown


class GenerateWbsMarkdownTest(unittest.TestCase):
    ROOT = Path(__file__).parents[1]

    def test_current_report_matches_wbs_source(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "wbs.md"
            generate_wbs_markdown(output=output)
            self.assertEqual(output.read_bytes(), (self.ROOT / "reports/wbs.md").read_bytes())

    def test_all_ids_status_titles_and_hierarchy_are_generated(self):
        with tempfile.TemporaryDirectory() as directory:
            tasks = Path(directory) / "tasks"
            tasks.mkdir()
            items = [
                ("WBS-001-01000", "root", "group", "complete", None),
                ("WBS-001-01001", "child", "task", "incomplete", "WBS-001-01000"),
                ("WBS-001-01002", "grandchild", "task", "complete", "WBS-001-01001"),
            ]
            for ident, title, kind, status, parent in items:
                actor = "none" if kind == "group" else "codex"
                parent_yaml = "null" if parent is None else parent
                sections = "# 概要\n\n概要\n# 配下の作業\n\n作業" if kind == "group" else "# 目的\n\n目的\n# 作業内容\n\n作業\n# 入力\n\n入力\n# 成果物\n\n成果物\n# 完了条件\n\n条件\n# 完了にしてはいけない条件\n\n禁止\n# 確認結果\n\n確認\n# 証跡\n\n証跡"
                (tasks / f"{ident}.md").write_text(f"""---
id: {ident}
title: {title}
type: {kind}
status: {"incomplete" if ident == "WBS-001-01000" else status}
actor: {actor}
parent: {parent_yaml}
depends_on: []
specs: []
related_files: []
outputs: []
blocked_by: []
source_wbs: []
evidence_required: true
updated: '2026-09-25'
---
{sections}
""", encoding="utf-8")
            first = Path(directory) / "first.md"
            second = Path(directory) / "second.md"
            generate_wbs_markdown(tasks, first)
            generate_wbs_markdown(tasks, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_text(encoding="utf-8").splitlines(), [
                "# WBS一覧", "", "- [ ] WBS-001-01000 root",
                "  - [ ] WBS-001-01001 child",
                "    - [x] WBS-001-01002 grandchild",
            ])

    def test_report_contains_each_source_id_once(self):
        source_ids = []
        for path in sorted((self.ROOT / "wbs" / "tasks").glob("*.md")):
            _, front_matter, _ = path.read_text(encoding="utf-8").split("---", 2)
            source_ids.append(yaml.safe_load(front_matter)["id"])
        report = (self.ROOT / "reports/wbs.md").read_text(encoding="utf-8")
        report_ids = [match.group(1) for line in report.splitlines() if (match := re.match(r"^\s*-\s+\[[ x]\]\s+(WBS-[0-9]{3}-[0-9]{5})\b", line))]
        self.assertEqual(set(source_ids), set(report_ids))
        self.assertEqual(len(source_ids), len(report_ids))
        self.assertEqual(len(report_ids), len(set(report_ids)))


if __name__ == "__main__":
    unittest.main()
