import unittest
from tools.build_structure_aware_arrangement_plan import build
class StructureAwareTest(unittest.TestCase):
    def test_function_exists_and_rejects_bad_source(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad"; p.write_bytes(b"x")
            with self.assertRaises(ValueError): build(p,p,Path(d)/"o")
if __name__=="__main__": unittest.main()
