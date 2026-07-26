import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from tools import json_to_huge_asm, json_to_uge


JSON_PATH = ROOT / "assets/bgm_pulse_chase.json"
ASM_PATH = ROOT / "assets/bgm_pulse_chase.asm"
ORDER = ["section0_a", "section0_b", "section1_a", "section1_b", "section2_a", "section2_b"]
CHANNELS = ("pulse1", "pulse2", "wave", "noise")


def note_to_asm(note: str) -> str:
    if note == "rest":
        return "___"
    match = re.fullmatch(r"([A-G]#?)([0-9])", note)
    assert match
    name, octave = match.groups()
    return f"{name}{octave}" if "#" in name else f"{name}_{octave}"


def expanded_json_cells(data: dict, channel: str) -> list[list[tuple[str, int, int]]]:
    result = []
    for pattern_name in ORDER:
        cells = []
        for item in data["patterns"][channel][pattern_name]:
            effect = 0 if item["note"] == "rest" or "volume" not in item else 0xC00 | item["volume"]
            instrument = 0 if item["note"] == "rest" else item["instrument"]
            cells.append((note_to_asm(item["note"]), instrument, effect))
            cells.extend(("___", 0, 0) for _ in range(item["length"] - 1))
        result.append(cells)
    return result


def parse_asm_patterns(asm: str) -> dict[int, list[tuple[str, int, int]]]:
    pattern_matches = list(re.finditer(r"^bgm_pulse_chase_P(\d+):\n(.*?)(?=^bgm_pulse_chase_P\d+:|^bgm_pulse_chase_duty_instruments:)", asm, re.M | re.S))
    patterns = {}
    for match in pattern_matches:
        cells = re.findall(r"^ dn ([A-G]#?\d|[A-G]_\d|___),(\d+),\$([0-9A-F]{3})$", match.group(2), re.M)
        patterns[int(match.group(1))] = [(note, int(instrument), int(effect, 16)) for note, instrument, effect in cells]
    return patterns


class PulseChaseAsmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.asm = ASM_PATH.read_text(encoding="utf-8")
        cls.patterns = parse_asm_patterns(cls.asm)

    def test_tracked_asm_is_deterministic_build_output(self):
        generated = json_to_huge_asm.build_asm(self.data, "bgm_pulse_chase")
        self.assertEqual(generated, self.asm)

    def test_orders_and_patterns_preserve_four_channel_structure(self):
        orders = re.findall(r"^bgm_pulse_chase_order[1-4]: dw (.+)$", self.asm, re.M)
        self.assertEqual(len(orders), 4)
        self.assertTrue(all(len(order.split(",")) == 6 for order in orders))
        self.assertEqual(len(self.patterns), 24)
        self.assertEqual(re.search(r"bgm_pulse_chase_order_cnt: db (\d+)", self.asm).group(1), "12")
        self.assertEqual(re.search(r"bgm_pulse_chase_loop_metadata: db ([^\n]+)", self.asm).group(1), "0,5,63")

    def test_json_cells_match_asm_cells_for_all_channels(self):
        for channel_index, channel in enumerate(CHANNELS):
            expected = expanded_json_cells(self.data, channel)
            for pattern_index, cells in enumerate(expected):
                self.assertEqual(len(cells), 64)
                self.assertEqual(self.patterns[pattern_index + channel_index * 6], cells)

    def test_known_cross_stage_events_and_gsharp_are_preserved(self):
        gsharp = [cell for cell in self.patterns[6].copy() if cell[0] == "G#3"]
        gsharp += [cell for index in range(7, 12) for cell in self.patterns[index] if cell[0] == "G#3"]
        self.assertEqual(len(gsharp), 6)
        self.assertEqual(len([cell for index in range(18, 24) for cell in self.patterns[index] if cell[0] == "C_3" and cell[1] == 1]), 48)
        self.assertEqual(len([cell for index in range(18, 24) for cell in self.patterns[index] if cell[0] == "C_5" and cell[1] == 2]), 48)
        self.assertEqual(len([cell for index in range(18, 24) for cell in self.patterns[index] if cell[0] == "C_7" and cell[1] == 3]), 48)

    def test_instrument_banks_and_wave_table_match_packing(self):
        self.assertIn("bgm_pulse_chase_itSquareinst1:", self.asm)
        self.assertIn("bgm_pulse_chase_itSquareinst2:", self.asm)
        self.assertIn("bgm_pulse_chase_itWaveinst1:", self.asm)
        self.assertEqual(len(re.findall(r"^bgm_pulse_chase_itNoiseinst\d+:$", self.asm, re.M)), 3)
        self.assertIn("db 8\ndb 128\ndb 192\ndw 0\ndb 128", self.asm)
        self.assertIn("db 8\ndb 64\ndb 112\ndw 0\ndb 128", self.asm)
        self.assertIn("db 0\ndb 32\ndb 0\ndw 0\ndb 128", self.asm)
        noise_values = re.findall(r"^bgm_pulse_chase_itNoiseinst\d+:\ndb (\d+)\ndw 0\ndb (\d+)$", self.asm, re.M)
        self.assertEqual(noise_values, [("96", "0"), ("80", "128"), ("64", "128")])
        packed = json_to_uge.pack_wave_samples(self.data["wave_tables"][0]["samples"])
        wave_line = re.search(r"^bgm_pulse_chase_waves:\n(db [^\n]+)", self.asm, re.M).group(1)
        self.assertEqual(wave_line, "db " + ",".join(f"${value:02X}" for value in packed))

    def test_descriptor_and_representative_phrase_structure(self):
        self.assertRegex(self.asm, r"bgm_pulse_chase::\ndb 6\n")
        self.assertRegex(self.asm, r"bgm_pulse_chase_P0:\n dn G_5,1,\$C0[0-9A-F]")
        section1 = "\n".join("\n".join(f"{note},{instrument}" for note, instrument, _ in self.patterns[index]) for index in range(2, 4))
        section2 = "\n".join("\n".join(f"{note},{instrument}" for note, instrument, _ in self.patterns[index]) for index in range(4, 6))
        self.assertIn("G_6,1", section1)
        self.assertLess(section2.count(",1"), section1.count(",1"))
        final_wave = [note for note, instrument, _ in self.patterns[17] if instrument == 1 and note != "___"][-4:]
        self.assertEqual(final_wave, ["D_3", "F#3", "A_3", "G_3"])


if __name__ == "__main__":
    unittest.main()
