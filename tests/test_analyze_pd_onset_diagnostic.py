import tempfile
import unittest
from pathlib import Path

from tools.analyze_pd_onset_diagnostic import encoded_xml_events


class OnsetDiagnosticTest(unittest.TestCase):
    def test_musicxml_cursor_preserves_chord_onset_and_advances_rest(self):
        xml = """<?xml version='1.0'?><score-partwise><part id='P1'><measure number='1'>
        <attributes><divisions>384</divisions><time><beats>2</beats><beat-type>4</beat-type></time></attributes>
        <note><pitch><step>C</step><octave>4</octave></pitch><duration>96</duration></note>
        <note><chord/><pitch><step>E</step><octave>4</octave></pitch><duration>96</duration></note>
        <note><duration>192</duration></note>
        <note><pitch><step>G</step><octave>4</octave></pitch><duration>96</duration></note>
        </measure></part></score-partwise>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.musicxml"
            path.write_text(xml, encoding="utf-8")
            events = encoded_xml_events(path, 384)
        self.assertEqual([event["local_onset"] for event in events], [0, 0, 288])
        self.assertEqual([event["chord"] for event in events], [False, True, False])


if __name__ == "__main__":
    unittest.main()
