import unittest
from pathlib import Path
import tempfile
from tools.validate_wbs import validate

class ValidateWbsTest(unittest.TestCase):
    def test_current_wbs_is_valid(self):
        data, issues = validate()
        self.assertTrue(data)
        self.assertFalse([x for x in issues if x[0] == 'error'])

    def test_short_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'01003.md'; p.write_text('---\nid: "01003"\ntitle: x\ntype: task\nstatus: incomplete\nactor: codex\nparent: null\ndepends_on: []\nspecs: []\nrelated_files: []\noutputs: []\nblocked_by: []\nsource_wbs: []\nevidence_required: true\nupdated: "2026-08-01"\n---\n\n'+'\n'.join('# '+x+'\n' for x in ['目的','作業内容','入力','成果物','完了条件','完了にしてはいけない条件','確認結果','証跡']))
            _, issues=validate(d)
            self.assertTrue(any('ID形式不正' in x[3] for x in issues))

if __name__ == '__main__': unittest.main()
