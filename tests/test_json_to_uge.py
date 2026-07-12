import copy
import json
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import json_to_uge  # noqa: E402
import json_to_huge_asm  # noqa: E402


def pulse_data(version: int = 2, channel: str = "pulse1") -> dict:
    return {
        "version": version,
        "instruments": [
            {
                "id": 1,
                "name": "test",
                "channel": channel,
            }
        ],
    }


def read_duty_instrument(blob: bytes, instrument_id: int) -> dict[str, int | bool]:
    """Read one TInstrumentV3 record from the packed Duty bank."""
    record_size = len(json_to_uge.pack_instrument(json_to_uge.IT_SQUARE, ""))
    offset = (instrument_id - 1) * record_size
    record = blob[offset : offset + record_size]
    if len(record) != record_size:
        raise AssertionError(f"missing Duty instrument {instrument_id}")

    return {
        "length": struct.unpack_from("<i", record, 260)[0],
        "length_enable": bool(record[264]),
        "initial_volume": record[265],
        "vol_sweep_direction": struct.unpack_from("<i", record, 266)[0],
        "vol_sweep_amount": record[270],
        "sweep_time": struct.unpack_from("<i", record, 271)[0],
        "sweep_direction": struct.unpack_from("<i", record, 275)[0],
        "sweep_shift": struct.unpack_from("<i", record, 279)[0],
        "duty": record[283],
    }


class PulseInstrumentValidationTests(unittest.TestCase):
    def validate(self, data: dict) -> json_to_uge.InstrumentSpec:
        return json_to_uge.validate_instruments(data)["duty"][1]

    def test_version_2_pulse1_accepts_common_and_sweep_fields(self) -> None:
        data = pulse_data()
        data["instruments"][0].update(
            {
                "duty": 3,
                "length": 63,
                "length_enable": True,
                "initial_volume": 0,
                "envelope_direction": "up",
                "envelope_sweep": 7,
                "sweep_time": 7,
                "sweep_direction": "up",
                "sweep_shift": 7,
            }
        )
        spec = self.validate(data)
        self.assertEqual(spec.duty, 3)
        self.assertEqual(spec.length, 63)
        self.assertTrue(spec.length_enable)
        self.assertEqual(spec.initial_volume, 0)
        self.assertEqual(spec.vol_sweep_direction, json_to_uge.ST_UP)
        self.assertEqual(spec.vol_sweep_amount, 7)
        self.assertEqual(spec.sweep_time, 7)
        self.assertEqual(spec.sweep_direction, json_to_uge.ST_UP)
        self.assertEqual(spec.sweep_shift, 7)

    def test_version_2_pulse2_accepts_length_without_sweep(self) -> None:
        data = pulse_data(channel="pulse2")
        data["instruments"][0].update({"length": 12, "length_enable": True})
        spec = self.validate(data)
        self.assertEqual(spec.length, 12)
        self.assertTrue(spec.length_enable)
        self.assertEqual(spec.sweep_time, 0)
        self.assertEqual(spec.sweep_direction, json_to_uge.ST_DOWN)
        self.assertEqual(spec.sweep_shift, 0)

    def test_version_2_defaults_preserve_duty_defaults(self) -> None:
        pulse1 = self.validate(pulse_data())
        pulse2 = self.validate(pulse_data(channel="pulse2"))
        self.assertEqual(pulse1.duty, 0)
        self.assertEqual(pulse1.vol_sweep_amount, 0)
        self.assertEqual(pulse1.length, 0)
        self.assertFalse(pulse1.length_enable)
        self.assertEqual(pulse1.initial_volume, 15)
        self.assertEqual(pulse1.vol_sweep_direction, json_to_uge.ST_DOWN)
        self.assertEqual(pulse2.duty, 0)
        self.assertEqual(pulse2.vol_sweep_amount, 0)

    def test_version_1_existing_assets_remain_valid(self) -> None:
        for path in sorted((ROOT / "assets").glob("*.json")):
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                json_to_uge.validate_header(data)
                json_to_uge.validate_instruments(data)

    def test_version_2_pulse2_rejects_each_sweep_field(self) -> None:
        for field, value in (
            ("sweep_time", 0),
            ("sweep_direction", "down"),
            ("sweep_shift", 0),
        ):
            with self.subTest(field=field):
                data = pulse_data(channel="pulse2")
                data["instruments"][0][field] = value
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}.*pulse1でのみ使用可能"):
                    self.validate(data)

    def test_version_2_pulse2_rejects_multiple_sweep_fields(self) -> None:
        data = pulse_data(channel="pulse2")
        data["instruments"][0].update(
            {"sweep_time": 0, "sweep_direction": "down", "sweep_shift": 0}
        )
        with self.assertRaisesRegex(ValueError, "pulse1でのみ使用可能"):
            self.validate(data)

    def test_version_2_integer_ranges_and_boolean_rejection(self) -> None:
        cases = (
            ("duty", -1),
            ("duty", 4),
            ("duty", True),
            ("length", -1),
            ("length", 64),
            ("length", True),
            ("length_enable", 1),
            ("initial_volume", -1),
            ("initial_volume", 16),
            ("initial_volume", True),
            ("envelope_sweep", -1),
            ("envelope_sweep", 8),
            ("envelope_sweep", False),
            ("sweep_time", -1),
            ("sweep_time", 8),
            ("sweep_time", True),
            ("sweep_shift", -1),
            ("sweep_shift", 8),
            ("sweep_shift", False),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                data = pulse_data()
                data["instruments"][0][field] = value
                with self.assertRaises(ValueError):
                    self.validate(data)

    def test_version_2_rejects_invalid_sweep_direction(self) -> None:
        data = pulse_data()
        data["instruments"][0]["sweep_direction"] = "sideways"
        with self.assertRaisesRegex(ValueError, "sweep_direction"):
            self.validate(data)

    def test_version_1_rejects_version_2_only_fields(self) -> None:
        for field, value in (
            ("length", 0),
            ("length_enable", False),
            ("sweep_time", 0),
            ("sweep_direction", "down"),
            ("sweep_shift", 0),
        ):
            with self.subTest(field=field):
                data = pulse_data(version=1)
                data["instruments"][0][field] = value
                with self.assertRaisesRegex(ValueError, "Version 2専用"):
                    self.validate(data)

    def test_supported_version_is_identified(self) -> None:
        data = pulse_data(version=2)
        self.assertEqual(json_to_uge.validate_json_version(data), 2)
        unsupported = copy.deepcopy(data)
        unsupported["version"] = 3
        with self.assertRaises(ValueError):
            json_to_uge.validate_json_version(unsupported)


class PackedPulseInstrumentTests(unittest.TestCase):
    def pack(self, instruments: list[dict]) -> bytes:
        return json_to_uge.pack_instruments(
            json_to_uge.validate_instruments({"version": 2, "instruments": instruments})
        )

    def test_version_2_pulse1_fields_are_written_to_uge_instrument_record(self) -> None:
        blob = self.pack(
            [
                {
                    "id": 1,
                    "name": "pulse1 custom",
                    "channel": "pulse1",
                    "duty": 1,
                    "length": 37,
                    "length_enable": True,
                    "initial_volume": 9,
                    "envelope_direction": "down",
                    "envelope_sweep": 5,
                    "sweep_time": 6,
                    "sweep_direction": "up",
                    "sweep_shift": 3,
                }
            ]
        )
        self.assertEqual(
            read_duty_instrument(blob, 1),
            {
                "length": 37,
                "length_enable": True,
                "initial_volume": 9,
                "vol_sweep_direction": json_to_uge.ST_DOWN,
                "vol_sweep_amount": 5,
                "sweep_time": 6,
                "sweep_direction": json_to_uge.ST_UP,
                "sweep_shift": 3,
                "duty": 1,
            },
        )

    def test_version_2_pulse2_common_fields_are_written_to_shared_duty_bank(self) -> None:
        blob = self.pack(
            [
                {
                    "id": 2,
                    "name": "pulse2 custom",
                    "channel": "pulse2",
                    "duty": 3,
                    "length": 22,
                    "length_enable": True,
                    "initial_volume": 7,
                    "envelope_direction": "up",
                    "envelope_sweep": 3,
                }
            ]
        )
        record = read_duty_instrument(blob, 2)
        self.assertEqual(record["length"], 22)
        self.assertTrue(record["length_enable"])
        self.assertEqual(record["initial_volume"], 7)
        self.assertEqual(record["vol_sweep_direction"], json_to_uge.ST_UP)
        self.assertEqual(record["vol_sweep_amount"], 3)
        self.assertEqual(record["duty"], 3)
        self.assertEqual(record["sweep_time"], 0)
        self.assertEqual(record["sweep_direction"], json_to_uge.ST_DOWN)
        self.assertEqual(record["sweep_shift"], 0)

    def test_version_2_pulse_defaults_are_written(self) -> None:
        blob = self.pack([{"id": 3, "name": "defaults", "channel": "pulse1"}])
        self.assertEqual(
            read_duty_instrument(blob, 3),
            {
                "length": 0,
                "length_enable": False,
                "initial_volume": 15,
                "vol_sweep_direction": json_to_uge.ST_DOWN,
                "vol_sweep_amount": 0,
                "sweep_time": 0,
                "sweep_direction": json_to_uge.ST_DOWN,
                "sweep_shift": 0,
                "duty": 2,
            },
        )

    def test_version_1_pulse_packing_keeps_legacy_values(self) -> None:
        data = pulse_data(version=1)
        data["instruments"][0].update(
            {
                "duty": 3,
                "initial_volume": 9,
                "envelope_direction": "up",
                "envelope_sweep": 5,
            }
        )
        blob = json_to_uge.pack_instruments(json_to_uge.validate_instruments(data))
        self.assertEqual(
            read_duty_instrument(blob, 1),
            {
                "length": 0,
                "length_enable": False,
                "initial_volume": 9,
                "vol_sweep_direction": json_to_uge.ST_UP,
                "vol_sweep_amount": 5,
                "sweep_time": 0,
                "sweep_direction": json_to_uge.ST_UP,
                "sweep_shift": 0,
                "duty": 3,
            },
        )

    def test_pulse1_and_pulse2_share_duty_bank_and_duplicate_ids_error(self) -> None:
        data = {
            "version": 2,
            "instruments": [
                {"id": 1, "name": "p1", "channel": "pulse1"},
                {"id": 1, "name": "p2", "channel": "pulse2"},
            ],
        }
        with self.assertRaisesRegex(ValueError, "duplicate instrument id 1 in duty bank"):
            json_to_uge.validate_instruments(data)


class PulseAsmInstrumentTests(unittest.TestCase):
    def instruments(self, items: list[dict]) -> dict[str, dict[int, json_to_uge.InstrumentSpec]]:
        return json_to_uge.validate_instruments({"version": 2, "instruments": items})

    def test_version_2_pulse1_register_bytes_include_all_fields(self) -> None:
        instruments = self.instruments(
            [
                {
                    "id": 1,
                    "name": "pulse1 asm",
                    "channel": "pulse1",
                    "duty": 3,
                    "length": 37,
                    "length_enable": True,
                    "initial_volume": 9,
                    "envelope_direction": "up",
                    "envelope_sweep": 5,
                    "sweep_time": 6,
                    "sweep_direction": "up",
                    "sweep_shift": 3,
                }
            ]
        )
        self.assertEqual(
            json_to_huge_asm.square_instrument_bytes(1, instruments),
            (
                (6 << 4) | 3,
                (3 << 6) | 37,
                (9 << 4) | (1 << 3) | 5,
                0xC0,
            ),
        )

    def test_envelope_and_frequency_sweep_directions_use_separate_registers(self) -> None:
        instruments = self.instruments(
            [
                {
                    "id": 1,
                    "name": "direction check",
                    "channel": "pulse1",
                    "envelope_direction": "up",
                    "sweep_direction": "down",
                }
            ]
        )
        nr10, nr11, nr12, nr14 = json_to_huge_asm.square_instrument_bytes(1, instruments)
        self.assertEqual(nr10, 0x08)
        self.assertEqual(nr12, 0xF8)
        self.assertEqual(nr11, 0)
        self.assertEqual(nr14, 0x80)

    def test_version_2_pulse2_common_fields_reach_asm(self) -> None:
        instruments = self.instruments(
            [
                {
                    "id": 2,
                    "name": "pulse2 asm",
                    "channel": "pulse2",
                    "duty": 1,
                    "length": 22,
                    "length_enable": True,
                    "initial_volume": 7,
                    "envelope_direction": "down",
                    "envelope_sweep": 3,
                }
            ]
        )
        self.assertEqual(
            json_to_huge_asm.square_instrument_bytes(2, instruments),
            ((0 << 4) | 0x08, (1 << 6) | 22, 7 << 4 | 3, 0xC0),
        )

    def test_version_2_defaults_and_register_boundaries(self) -> None:
        instruments = self.instruments(
            [
                {"id": 1, "name": "defaults", "channel": "pulse1"},
                {
                    "id": 2,
                    "name": "boundaries",
                    "channel": "pulse1",
                    "duty": 3,
                    "length": 63,
                    "length_enable": True,
                    "initial_volume": 0,
                    "envelope_direction": "up",
                    "envelope_sweep": 7,
                    "sweep_time": 7,
                    "sweep_direction": "down",
                    "sweep_shift": 7,
                },
            ]
        )
        self.assertEqual(json_to_huge_asm.square_instrument_bytes(1, instruments), (8, 0, 0xF0, 0x80))
        self.assertEqual(json_to_huge_asm.square_instrument_bytes(2, instruments), (0x7F, 0xFF, 0x0F, 0xC0))

    def test_version_1_register_bytes_are_unchanged(self) -> None:
        data = pulse_data(version=1)
        data["instruments"][0].update(
            {
                "duty": 3,
                "initial_volume": 9,
                "envelope_direction": "up",
                "envelope_sweep": 5,
            }
        )
        instruments = json_to_uge.validate_instruments(data)
        self.assertEqual(
            json_to_huge_asm.square_instrument_bytes(1, instruments),
            (8, 3 << 6, (9 << 4) | (1 << 3) | 5, 0x80),
        )


def wave_data(version: int = 2, **fields: object) -> dict:
    instrument = {
        "id": 1,
        "name": "wave test",
        "channel": "wave",
    }
    instrument.update(fields)
    return {"version": version, "instruments": [instrument]}


class WaveInstrumentValidationTests(unittest.TestCase):
    def validate(self, data: dict) -> json_to_uge.InstrumentSpec:
        return json_to_uge.validate_instruments(data)["wave"][1]

    def test_version_2_wave_accepts_all_fields_and_keeps_waveform_name(self) -> None:
        spec = self.validate(
            wave_data(
                waveform="bass_wave",
                output_level="50%",
                length=255,
                length_enable=True,
            )
        )
        self.assertEqual(spec.waveform, "bass_wave")
        self.assertIsInstance(spec.waveform, str)
        self.assertEqual(spec.output_level, 2)
        self.assertEqual(spec.length, 255)
        self.assertTrue(spec.length_enable)
        self.assertEqual(spec.json_version, 2)
        self.assertEqual(spec.bank, "wave")

    def test_version_2_wave_output_level_mapping(self) -> None:
        for name, value in json_to_uge.WAVE_OUTPUT_LEVELS.items():
            with self.subTest(output_level=name):
                self.assertEqual(self.validate(wave_data(waveform="bass", output_level=name)).output_level, value)

    def test_version_2_wave_defaults(self) -> None:
        spec = self.validate(wave_data(waveform="bass"))
        self.assertEqual(spec.waveform, "bass")
        self.assertEqual(spec.output_level, 1)
        self.assertEqual(spec.length, 0)
        self.assertFalse(spec.length_enable)

    def test_version_2_wave_rejects_empty_or_whitespace_waveform(self) -> None:
        for waveform in ("", "   ", " bass", "bass "):
            with self.subTest(waveform=repr(waveform)):
                with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.waveform"):
                    self.validate(wave_data(waveform=waveform))

    def test_version_2_waveform_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.waveform"):
            self.validate(wave_data())

    def test_version_2_wave_rejects_invalid_types_and_ranges(self) -> None:
        cases = (
            ("waveform", 1),
            ("output_level", 1),
            ("output_level", "75%"),
            ("length", -1),
            ("length", 256),
            ("length", True),
            ("length_enable", 1),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    self.validate(wave_data(**{field: value}))

    def test_version_2_wave_rejects_pulse_and_noise_only_fields(self) -> None:
        for field in (
            *json_to_uge.WAVE_PULSE_ONLY_FIELDS,
            *json_to_uge.WAVE_NOISE_ONLY_FIELDS,
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}.*Wave Instrument.*(?:Pulse|Noise)専用"):
                    self.validate(wave_data(waveform="bass", **{field: 0}))

    def test_version_2_wave_rejects_trigger_and_frequency(self) -> None:
        for field in json_to_uge.WAVE_UNSUPPORTED_FIELDS:
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}.*Wave Instrument"):
                    self.validate(wave_data(waveform="bass", **{field: 0}))

    def test_version_2_wave_duplicate_id_is_rejected(self) -> None:
        data = wave_data(waveform="bass")
        data["instruments"].append(
            {"id": 1, "name": "other", "channel": "wave", "waveform": "lead"}
        )
        with self.assertRaisesRegex(ValueError, "duplicate instrument id 1 in wave bank"):
            json_to_uge.validate_instruments(data)

    def test_duty_and_wave_banks_can_share_instrument_id(self) -> None:
        data = wave_data(waveform="bass")
        data["instruments"].append(
            {"id": 1, "name": "pulse", "channel": "pulse1"}
        )
        result = json_to_uge.validate_instruments(data)
        self.assertIn(1, result["wave"])
        self.assertIn(1, result["duty"])

    def test_version_1_wave_version_2_fields_are_rejected(self) -> None:
        for field, value in (
            ("waveform", "bass"),
            ("output_level", "100%"),
            ("length", 0),
            ("length_enable", False),
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}.*Version 2専用"):
                    self.validate(wave_data(version=1, **{field: value}))


if __name__ == "__main__":
    unittest.main()
