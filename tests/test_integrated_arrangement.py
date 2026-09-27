import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tools.maple_leaf_rag_prototype import group_patterns

class IntegratedArrangementTest(unittest.TestCase):
    def test_absolute_measure_position_does_not_collide(self):
        events = [
            {"event_id":"a","part":"P1","measure":1,"start":0,"duration":30,"pitch":70},
            {"event_id":"b","part":"P1","measure":2,"start":0,"duration":30,"pitch":71},
        ]
        config={"quantization_grid_ticks":30,"ticks_per_row":6,"measure_ticks":768,
                "timeline_mode":"absolute","pitch_range":{"pulse1":[48,96],"pulse2":[48,84],"wave":[48,72],"noise":[0,0]}}
        plan, issues=group_patterns(events,config)
        self.assertEqual(len(plan["channels"]["pulse1"]),2)
        self.assertFalse(any(i.get("reason")=="polyphony_omitted" for i in issues))

if __name__ == "__main__": unittest.main()
