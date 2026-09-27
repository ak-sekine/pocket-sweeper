import json
import tempfile
import unittest
from pathlib import Path

from tools.emit_measure_excerpt import extract


class MeasureExcerptTest(unittest.TestCase):
    def test_contiguous_range_rebases_and_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "plan.json"
            plan = {"schema": "test", "events": [
                {"measure": 1, "row": 4, "absolute_onset": 120, "status": "selected", "role": "melody", "channel": "pulse1", "pitch": 60, "duration": 30, "source_event_id": "a"},
                {"measure": 2, "row": 28, "absolute_onset": 840, "status": "selected", "role": "bass", "channel": "wave", "pitch": 40, "duration": 30, "source_event_id": "b"},
                {"measure": 3, "row": 52, "absolute_onset": 1560, "status": "selected", "role": "harmony", "channel": "pulse2", "pitch": 55, "duration": 30, "source_event_id": "c"},
            ]}
            source.write_text(json.dumps(plan), encoding="utf-8")
            output, sidecar = root / "excerpt.json", root / "excerpt.sidecar.json"
            extract(source, 1, 2, output, sidecar)
            result = json.loads(output.read_text(encoding="utf-8"))
            mapping = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual([e["row"] for e in result["events"]], [0, 24])
            self.assertEqual([e["source_event_id"] for e in mapping["events"]], ["a", "b"])
            self.assertEqual(mapping["events"][1]["original_absolute_onset"], 840)


if __name__ == "__main__":
    unittest.main()
