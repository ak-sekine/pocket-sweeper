import json, tempfile, unittest
from pathlib import Path
from tools.emit_explainable_plan_json import emit

class EmitPlanTest(unittest.TestCase):
    def test_emits_version_two(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"plan.json"; out=Path(d)/"song.json"
            source.write_text(json.dumps({"events":[{"status":"selected","role":"melody","quantized_absolute_row":0,"pitch":60,"duration":30,"source_event_id":"x"}]}))
            self.assertEqual(emit(source,out).read_text()[:1], "{")
            self.assertEqual(json.loads(out.read_text())["version"], 2)

if __name__ == "__main__": unittest.main()
