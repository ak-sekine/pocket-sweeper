import tempfile
import unittest
from pathlib import Path
import yaml
from tools.validate_wbs import validate

SECTIONS = "目的 作業内容 入力 成果物 完了条件 完了にしてはいけない条件 確認結果 証跡".split()

def write_task(root, ident="WBS-001-01000", **overrides):
    meta = {"id": ident, "title": "テスト", "type": "task", "status": "incomplete", "actor": "codex", "parent": None, "depends_on": [], "specs": [], "related_files": [], "outputs": [], "blocked_by": [], "source_wbs": [], "evidence_required": True, "updated": "2026-08-01"}
    meta.update(overrides); body = "\n\n".join(f"# {section}\n\n本文" for section in SECTIONS)
    path = Path(root) / f"{ident}.md"; path.write_text(f"---\n{yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)}---\n\n{body}\n", encoding="utf-8"); return path

class ValidateWbsTest(unittest.TestCase):
    def check_error(self, **overrides):
        with tempfile.TemporaryDirectory() as d:
            write_task(d, **overrides); _, issues = validate(d, Path(d)); self.assertTrue(any(x[0] == "error" for x in issues), overrides)
    def test_current_wbs_is_valid(self):
        data, issues = validate(); self.assertEqual(673, len(data)); self.assertFalse([x for x in issues if x[0] == "error"])
    def test_short_id_and_bad_filename(self): self.check_error(ident="01003")
    def test_duplicate_id(self):
        with tempfile.TemporaryDirectory() as d:
            write_task(d); Path(d, "duplicate.md").write_text(Path(d, "WBS-001-01000.md").read_text()); _, issues=validate(d, Path(d)); self.assertTrue(any("ID重複" in x[3] for x in issues))
    def test_missing_parent_self_parent_and_missing_dependency(self):
        self.check_error(parent="WBS-001-09999"); self.check_error(parent="WBS-001-01000"); self.check_error(depends_on=["WBS-001-09999"])
    def test_dependency_self_and_cycle(self):
        self.check_error(depends_on=["WBS-001-01000"])
        with tempfile.TemporaryDirectory() as d:
            write_task(d, depends_on=["WBS-001-01001"]); write_task(d, ident="WBS-001-01001", depends_on=["WBS-001-01000"]); _, issues=validate(d, Path(d)); self.assertTrue(any("依存循環" in x[3] for x in issues))
    def test_invalid_fields_and_sections(self):
        self.check_error(status="bad"); self.check_error(actor="bad"); self.check_error(type="bad"); self.check_error(depends_on="bad"); self.check_error(evidence_required="yes"); self.check_error(updated="2026/08/01")
        with tempfile.TemporaryDirectory() as d:
            p=write_task(d); p.write_text(p.read_text().replace("# 証跡", "# 欠落")); _, issues=validate(d, Path(d)); self.assertTrue(any("必須セクション不足" in x[3] for x in issues))
    def test_paths_and_source_separation(self):
        self.check_error(specs=["missing.md"]); self.check_error(related_files=["missing.md"]); self.check_error(source_wbs=["WBS-002-01000"], parent="WBS-002-01000"); self.check_error(source_wbs=["WBS-002-01000"], depends_on=["WBS-002-01000"])
    def test_same_parent_warning_and_different_parent_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            write_task(d); write_task(d, ident="WBS-001-01001"); _, issues=validate(d, Path(d)); self.assertTrue(any("同一親配下" in x[3] for x in issues))
        with tempfile.TemporaryDirectory() as d:
            write_task(d, ident="WBS-001-01000", title="親A"); write_task(d, ident="WBS-001-01001", title="親B"); write_task(d, ident="WBS-001-01002", title="同名", parent="WBS-001-01000"); write_task(d, ident="WBS-001-01003", title="同名", parent="WBS-001-01001"); _, issues=validate(d, Path(d)); self.assertFalse(any(x[0] == "error" for x in issues))
    def test_complete_group_with_incomplete_descendant_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            write_task(d, ident="WBS-001-01000", type="group", actor="none", status="complete"); write_task(d, ident="WBS-001-01001", parent="WBS-001-01000"); _, issues=validate(d, Path(d)); self.assertTrue(any(x[0] == "warning" for x in issues))

if __name__ == "__main__": unittest.main()
