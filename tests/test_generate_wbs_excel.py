import unittest
from pathlib import Path
from openpyxl import load_workbook

class GenerateWbsExcelTest(unittest.TestCase):
    def test_workbook_shape_and_string_ids(self):
        book=load_workbook(Path(__file__).parents[1]/'reports/wbs.xlsx')
        self.assertEqual({'WBS一覧','未完了一覧','進捗集計','検証結果','移行対応'}, set(book.sheetnames))
        ws=book['WBS一覧']; self.assertGreater(ws.max_row, 600)
        self.assertEqual('WBS-001-01000', ws['A2'].value)
        self.assertIsInstance(ws['A2'].value, str)
        self.assertEqual('001', ws['B2'].value)
        self.assertEqual('01000', ws['C2'].value)
        self.assertEqual('WBS ID', ws['A1'].value)

if __name__ == '__main__': unittest.main()
