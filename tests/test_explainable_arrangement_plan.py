import tempfile, unittest
from pathlib import Path
from tools.build_explainable_arrangement_plan import build

class ExplainablePlanTest(unittest.TestCase):
    def test_source_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.mid"; p.write_bytes(b"bad")
            with self.assertRaises(ValueError): build(p,p,Path(d)/"out")

if __name__ == "__main__": unittest.main()
