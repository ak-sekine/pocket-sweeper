import unittest, tempfile, json
from pathlib import Path
from tools.emit_full_song_json import emit
class FullSongJsonTest(unittest.TestCase):
    def test_boundary_patterns(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"p.json"; o=Path(d)/"o.json"
            p.write_text(json.dumps({"events":[{"status":"selected","channel":"pulse1","role":"melody","row":63,"pitch":60,"duration":30,"source_event_id":"a"},{"status":"selected","channel":"pulse1","role":"melody","row":64,"pitch":62,"duration":30,"source_event_id":"b"}]}))
            x=json.loads(emit(p,o).read_text()); self.assertEqual(len(x["order"]["pulse1"]),2); first=x["patterns"]["pulse1"][x["order"]["pulse1"][0]]; self.assertEqual(sum(n["length"] for n in first),64); self.assertTrue(any(n["note"] != "rest" for n in first))
    def test_tempo_override_changes_only_descriptor_tempo(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"p.json"; a=Path(d)/"a.json"; b=Path(d)/"b.json"
            event={"status":"selected","channel":"pulse1","role":"melody","row":0,"pitch":60,"duration":30,"source_event_id":"a"}
            p.write_text(json.dumps({"events":[event]}))
            emit(p,a); emit(p,b,tempo=2)
            old=json.loads(a.read_text()); new=json.loads(b.read_text())
            self.assertEqual(old["tempo"], 6); self.assertEqual(new["tempo"], 2)
            self.assertEqual({k:v for k,v in old.items() if k != "tempo"}, {k:v for k,v in new.items() if k != "tempo"})
if __name__=="__main__": unittest.main()
