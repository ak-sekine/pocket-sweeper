import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import json_to_sfx_asm  # noqa: E402


class Version1CursorNoiseSfxCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.asset_path = ROOT / "assets" / "se_cursor.json"
        self.data = json.loads(self.asset_path.read_text(encoding="utf-8"))

    def test_asset_remains_version_1_noise_sfx(self) -> None:
        self.assertEqual(self.data["version"], 1)
        self.assertEqual(self.data["type"], "sfx")
        self.assertEqual(self.data["priority"], 1)
        self.assertEqual(self.data["order"], ["main"])

        instrument = self.data["instruments"]
        self.assertEqual(
            instrument,
            [
                {
                    "id": 5,
                    "name": "cursor_tick",
                    "channel": "noise",
                    "noise_length": 12,
                    "initial_volume": 5,
                    "envelope_direction": "down",
                    "envelope_sweep": 2,
                    "clock_shift": 1,
                    "width_mode": "7bit",
                    "divisor_code": 0,
                    "length_enable": True,
                }
            ],
        )

        channels = self.data["patterns"]["main"]["channels"]
        self.assertEqual(channels["pulse1"], [])
        self.assertEqual(channels["pulse2"], [])
        self.assertEqual(channels["wave"], [])
        self.assertEqual(
            channels["noise"],
            [
                {
                    "note": "C3",
                    "length": 1,
                    "instrument": 5,
                    "effect": None,
                    "effect_param": None,
                }
            ],
        )

    def test_generated_asm_preserves_version_1_noise_register_bytes(self) -> None:
        asm = json_to_sfx_asm.render_asm(self.data, "cursor")
        self.assertIn("DEF SFX_CH_NOISE EQU 3", asm)
        self.assertIn("    db 3, 1, 1, 1", asm)
        self.assertIn("    db 1, $0C, $52, $18, $C0", asm)


if __name__ == "__main__":
    unittest.main()
