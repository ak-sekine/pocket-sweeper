import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from openpyxl import load_workbook
import yaml
from tools.generate_wbs_excel import extract_section, generate_wbs_excel

class GenerateWbsExcelTest(unittest.TestCase):
    ROOT = Path(__file__).parents[1]

    @classmethod
    def load_wbs_metadata(cls):
        metadata = {}
        for path in sorted((cls.ROOT / "wbs" / "tasks").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            _, front_matter, _ = text.split("---", 2)
            item = yaml.safe_load(front_matter)
            metadata[item["id"]] = item
        return metadata

    @staticmethod
    def sheet_ids(sheet):
        return [row[0].value for row in sheet.iter_rows(min_row=2) if row[0].value]

    def test_read_only_recommended_xml_and_regeneration(self):
        output = Path(__file__).parents[1] / "reports" / "wbs.xlsx"
        generate_wbs_excel(output=output)
        generate_wbs_excel(output=output)
        with zipfile.ZipFile(output) as archive:
            root = ET.fromstring(archive.read("xl/workbook.xml"))
            namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            sharing = root.findall("main:fileSharing", namespace)
            self.assertEqual(1, len(sharing)); self.assertIn(sharing[0].get("readOnlyRecommended"), {"1", "true"})
            names = [node.tag.rsplit("}", 1)[-1] for node in root]
            self.assertLess(names.index("fileSharing"), names.index("workbookPr"))
            self.assertLess(names.index("fileSharing"), names.index("bookViews"))
            self.assertLess(names.index("fileSharing"), names.index("sheets"))
        self.assertIn("WBS一覧", load_workbook(output).sheetnames)

    def test_section_extraction_and_empty_section(self):
        text = "# 完了条件\n\n条件1\n条件2\n# 証跡\n\n証跡1\n# その他\n\n除外"
        self.assertEqual("条件1\n条件2", extract_section(text, "完了条件")); self.assertEqual("証跡1", extract_section(text, "証跡")); self.assertEqual("未登録", extract_section("# 完了条件\n\n# 証跡\n\n", "完了条件"))

    def test_workbook_structure_and_wbs_consistency(self):
        expected = self.load_wbs_metadata()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "wbs.xlsx"
            generate_wbs_excel(output=output)
            book = load_workbook(output)

        self.assertEqual({"WBS一覧", "未完了一覧", "進捗集計", "検証結果", "移行対応"}, set(book.sheetnames))
        ws = book["WBS一覧"]
        self.assertEqual(19, ws.max_column)
        self.assertEqual(
            [
                "WBS ID", "プロジェクト番号", "プロジェクト内番号", "親WBS ID", "階層",
                "種別", "WBS名", "担当", "状態", "依存先", "流用元WBS", "仕様書",
                "関連ファイル", "成果物", "ブロック理由", "完了条件要約", "証跡要約",
                "更新日", "詳細ファイル",
            ],
            [cell.value for cell in ws[1]],
        )
        actual_ids = self.sheet_ids(ws)
        expected_ids = set(expected)
        self.assertEqual(len(expected_ids), len(actual_ids))
        self.assertEqual(expected_ids, set(actual_ids))
        self.assertEqual(len(actual_ids), len(set(actual_ids)))
        self.assertEqual("WBS-001-01000", ws["A2"].value)
        self.assertEqual("001", ws["B2"].value)
        self.assertEqual("01000", ws["C2"].value)
        self.assertIsInstance(ws["A2"].value, str)

        incomplete_task_ids = {
            ident for ident, item in expected.items()
            if item["type"] == "task" and item["status"] == "incomplete"
        }
        incomplete_ids = self.sheet_ids(book["未完了一覧"])
        self.assertEqual(incomplete_task_ids, set(incomplete_ids))
        self.assertEqual(len(incomplete_ids), len(set(incomplete_ids)))
        self.assertTrue(set(incomplete_ids).issubset(expected_ids))
        self.assertTrue(all(expected[ident]["status"] == "incomplete" for ident in incomplete_ids))

        summary = [row[0].value for row in book["進捗集計"].iter_rows()]; self.assertIn("最上位group別集計", summary)
        self.assertTrue(any("既存項目を完了し証跡を記録する" not in str(cell.value) for row in ws.iter_rows(min_row=2, max_row=3) for cell in row))
        self.assertIn(" > ", book["移行対応"]["A3"].value); self.assertIn("PROJECT.md削除後", book["移行対応"]["G2"].value)

    def test_small_wbs_can_be_generated_to_temporary_output(self):
        with tempfile.TemporaryDirectory() as d:
            tasks = Path(d) / "tasks"; tasks.mkdir(); p = tasks / "WBS-001-01000.md"
            p.write_text('''---\nid: WBS-001-01000\ntitle: 小規模\ntype: task\nstatus: incomplete\nactor: codex\nparent: null\ndepends_on: []\nspecs: []\nrelated_files: []\noutputs: []\nblocked_by: []\nsource_wbs: []\nevidence_required: true\nupdated: '2026-08-01'\n---\n# 目的\n\n目的\n# 作業内容\n\n作業\n# 入力\n\n入力\n# 成果物\n\n成果物\n# 完了条件\n\n小規模条件\n# 完了にしてはいけない条件\n\n禁止\n# 確認結果\n\n確認\n# 証跡\n\n小規模証跡\n''', encoding="utf-8")
            output = Path(d) / "out.xlsx"; generate_wbs_excel(tasks, output); ws = load_workbook(output)["WBS一覧"]
            self.assertEqual("小規模条件", ws["P2"].value); self.assertEqual("小規模証跡", ws["Q2"].value)

if __name__ == "__main__": unittest.main()
