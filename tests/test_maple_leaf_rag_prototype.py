import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import json_to_uge  # noqa: E402
import maple_leaf_rag_prototype as prototype  # noqa: E402


def midi_fixture() -> bytes:
    # Format 0, PPQ 96: C4 and E4 overlap, followed by a G3 bass event.
    events = bytes([
        0x00, 0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20,
        0x00, 0xFF, 0x58, 0x04, 0x02, 0x02, 0x18, 0x08,
        0x00, 0x90, 0x3C, 0x64,
        0x00, 0x90, 0x40, 0x50,
        0x60, 0x80, 0x3C, 0x00,
        0x00, 0x80, 0x40, 0x00,
        0x00, 0x90, 0x37, 0x64,
        0x60, 0x80, 0x37, 0x00,
        0x00, 0xFF, 0x2F, 0x00,
    ])
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 96) + b"MTrk" + struct.pack(">I", len(events)) + events


class MapleLeafRagPrototypeTests(unittest.TestCase):
    def test_midi_musicxml_normalization_and_loss_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            midi = root / "fixture.mid"
            midi.write_bytes(midi_fixture())
            ppq, tracks, metadata = prototype.read_midi(midi)
            self.assertEqual(ppq, 96)
            self.assertEqual(len(tracks), 1)
            self.assertEqual(metadata["tempo"][0]["microseconds_per_quarter"], 500000)
            xml = root / "fixture.musicxml"
            prototype.write_musicxml(xml, ppq, tracks, metadata)
            events, xml_metadata = prototype.parse_musicxml(xml)
            self.assertGreaterEqual(len(events), 3)
            self.assertEqual(xml_metadata["parts"], 1)
            config = {"quantization_grid_ticks": 24, "ticks_per_row": 6, "pitch_range": {"pulse1": [48, 96], "pulse2": [48, 84], "wave": [48, 72], "noise": [0, 0]}}
            plan, issues = prototype.group_patterns(events, config)
            self.assertIn("pulse1", plan["channels"])
            self.assertTrue(any(issue.get("reason") == "polyphony_omitted" for issue in issues))

    def test_json_v2_contract_and_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            midi = root / "fixture.mid"
            midi.write_bytes(midi_fixture())
            ppq, tracks, metadata = prototype.read_midi(midi)
            xml = root / "fixture.musicxml"
            prototype.write_musicxml(xml, ppq, tracks, metadata)
            events, _ = prototype.parse_musicxml(xml)
            config = {"quantization_grid_ticks": 24, "ticks_per_row": 6, "pitch_range": {"pulse1": [48, 96], "pulse2": [48, 84], "wave": [48, 72], "noise": [0, 0]}}
            plan_a, _ = prototype.group_patterns(events, config)
            plan_b, _ = prototype.group_patterns(events, config)
            self.assertEqual(plan_a, plan_b)
            data = prototype.make_json(plan_a, config)
            self.assertEqual(data["version"], 2)
            self.assertEqual(set(data["patterns"]), set(json_to_uge.CHANNELS))
            self.assertTrue(json_to_uge.build_uge(data))
            first = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            second = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            self.assertEqual(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())


if __name__ == "__main__":
    unittest.main()
