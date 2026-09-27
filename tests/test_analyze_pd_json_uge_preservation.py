import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import analyze_pd_json_uge_preservation as diagnostic
class JsonUgeDiagnosticTest(unittest.TestCase):
    def test_pitch_and_window_helpers(self):
        self.assertEqual(diagnostic.note_pitch("D4"),62)
        self.assertEqual(diagnostic.note_pitch("rest"),None)
        self.assertIn("pulse1",diagnostic.CH_TO_UGE)
    def test_json_event_rows(self):
        data={"patterns":{c:{"p":[{"note":"C3","length":2,"instrument":1},{"note":"rest","length":3,"instrument":1}]} for c in diagnostic.CHANNELS}}
        events=diagnostic.json_events(data)
        self.assertEqual(events[0]["row"],0); self.assertEqual(events[1]["row"],2); self.assertTrue(events[1]["synthetic"])
if __name__=="__main__":unittest.main()
