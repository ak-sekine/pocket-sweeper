import copy
from dataclasses import replace
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


def noise_data(version: int = 2, **fields: object) -> dict:
    instrument = {
        "id": 1,
        "name": "noise test",
        "channel": "noise",
    }
    instrument.update(fields)
    return {"version": version, "instruments": [instrument]}


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


def read_wave_instrument(blob: bytes, instrument_id: int) -> dict[str, int | bool | str]:
    record_size = len(json_to_uge.pack_instrument(json_to_uge.IT_WAVE, ""))
    offset = (json_to_uge.INSTRUMENT_COUNT + instrument_id - 1) * record_size
    record = blob[offset : offset + record_size]
    if len(record) != record_size:
        raise AssertionError(f"missing Wave instrument {instrument_id}")

    name_length = record[4]
    return {
        "type": struct.unpack_from("<i", record, 0)[0],
        "name": record[5 : 5 + name_length].decode("utf-8"),
        "length": struct.unpack_from("<i", record, 260)[0],
        "length_enable": bool(record[264]),
        "output_level": struct.unpack_from("<i", record, 284)[0],
        "waveform": struct.unpack_from("<i", record, 288)[0],
    }


def read_noise_instrument(blob: bytes, instrument_id: int) -> dict[str, int | bool | str]:
    record_size = len(json_to_uge.pack_instrument(json_to_uge.IT_NOISE, ""))
    offset = (2 * json_to_uge.INSTRUMENT_COUNT + instrument_id - 1) * record_size
    record = blob[offset : offset + record_size]
    if len(record) != record_size:
        raise AssertionError(f"missing Noise instrument {instrument_id}")

    name_length = record[4]
    return {
        "type": struct.unpack_from("<i", record, 0)[0],
        "name": record[5 : 5 + name_length].decode("utf-8"),
        "length": struct.unpack_from("<i", record, 260)[0],
        "length_enable": bool(record[264]),
        "initial_volume": record[265],
        "vol_sweep_direction": struct.unpack_from("<i", record, 266)[0],
        "vol_sweep_amount": record[270],
        "counter_step": struct.unpack_from("<i", record, 292)[0],
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


class NoiseInstrumentValidationTests(unittest.TestCase):
    def validate(self, data: dict) -> json_to_uge.InstrumentSpec:
        return json_to_uge.validate_instruments(data)["noise"][1]

    def test_version_2_noise_accepts_all_fields(self) -> None:
        spec = self.validate(
            noise_data(
                length=63,
                length_enable=True,
                initial_volume=0,
                envelope_direction="up",
                envelope_sweep=7,
                width_mode="7bit",
            )
        )
        self.assertEqual(spec.length, 63)
        self.assertTrue(spec.length_enable)
        self.assertEqual(spec.initial_volume, 0)
        self.assertEqual(spec.vol_sweep_direction, json_to_uge.ST_UP)
        self.assertEqual(spec.vol_sweep_amount, 7)
        self.assertEqual(spec.width_mode, json_to_uge.NOISE_WIDTH_7BIT)
        self.assertEqual(spec.json_version, 2)
        self.assertEqual(spec.bank, "noise")

    def test_version_2_noise_defaults(self) -> None:
        spec = self.validate(noise_data())
        self.assertEqual(spec.length, 0)
        self.assertFalse(spec.length_enable)
        self.assertEqual(spec.initial_volume, 15)
        self.assertEqual(spec.vol_sweep_direction, json_to_uge.ST_DOWN)
        self.assertEqual(spec.vol_sweep_amount, 0)
        self.assertEqual(spec.width_mode, json_to_uge.NOISE_WIDTH_15BIT)

    def test_version_2_noise_accepts_boundaries_and_width_modes(self) -> None:
        for width_mode in ("15bit", "7bit"):
            with self.subTest(width_mode=width_mode):
                spec = self.validate(
                    noise_data(
                        length=0,
                        initial_volume=15,
                        envelope_sweep=0,
                        width_mode=width_mode,
                    )
                )
                self.assertEqual(
                    spec.width_mode,
                    json_to_uge.NOISE_WIDTH_15BIT if width_mode == "15bit" else json_to_uge.NOISE_WIDTH_7BIT,
                )

    def test_version_2_noise_rejects_forbidden_fields(self) -> None:
        cases = (
            ("noise_length", 0),
            ("clock_shift", 0),
            ("divisor_code", 0),
            *[(field, 0) for field in json_to_uge.NOISE_PULSE_ONLY_FIELDS],
            ("waveform", "wave"),
            ("output_level", "100%"),
            ("trigger", 0),
            ("frequency", 0),
        )
        for field, value in cases:
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}"):
                    self.validate(noise_data(**{field: value}))

    def test_version_2_noise_rejects_unknown_fields_with_path(self) -> None:
        for value in (123, "value", True, None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    r"instruments\[0\]\.unknown_field: unknown Noise Instrument field",
                ):
                    self.validate(noise_data(unknown_field=value))

    def test_version_2_noise_reports_first_unknown_field_when_multiple_exist(self) -> None:
        data = noise_data(first_unknown=1, second_unknown=2)
        with self.assertRaisesRegex(
            ValueError,
            r"instruments\[0\]\.first_unknown: unknown Noise Instrument field",
        ):
            self.validate(data)

    def test_version_2_noise_forbidden_fields_keep_dedicated_errors(self) -> None:
        fields = (
            *json_to_uge.NOISE_VERSION_2_FORBIDDEN_FIELDS,
            *json_to_uge.NOISE_PULSE_ONLY_FIELDS,
            *json_to_uge.NOISE_WAVE_ONLY_FIELDS,
            *json_to_uge.NOISE_UNSUPPORTED_FIELDS,
        )
        for field in fields:
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as raised:
                    self.validate(noise_data(**{field: 0}))
                message = str(raised.exception)
                self.assertIn(f"instruments[0].{field}", message)
                self.assertNotIn("unknown Noise Instrument field", message)

    def test_version_2_noise_rejects_invalid_values(self) -> None:
        cases = (
            ("length", -1),
            ("length", 64),
            ("length", True),
            ("length", "1"),
            ("length", 1.5),
            ("length_enable", 1),
            ("initial_volume", -1),
            ("initial_volume", 16),
            ("initial_volume", True),
            ("envelope_sweep", -1),
            ("envelope_sweep", 8),
            ("envelope_sweep", False),
            ("envelope_direction", "sideways"),
            ("width_mode", "4bit"),
            ("width_mode", True),
            ("width_mode", 7),
            ("width_mode", None),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(ValueError, rf"instruments\[0\]\.{field}"):
                    self.validate(noise_data(**{field: value}))

    def test_version_2_noise_null_length_uses_default(self) -> None:
        self.assertEqual(self.validate(noise_data(length=None)).length, 0)

    def test_version_1_noise_preserves_existing_noise_fields(self) -> None:
        spec = self.validate(
            noise_data(
                version=1,
                noise_length=12,
                initial_volume=5,
                envelope_direction="down",
                envelope_sweep=2,
                clock_shift=1,
                width_mode="7bit",
                divisor_code=0,
                length_enable=True,
            )
        )
        self.assertEqual(spec.length, 12)
        self.assertTrue(spec.length_enable)
        self.assertEqual(spec.initial_volume, 5)
        self.assertEqual(spec.vol_sweep_amount, 2)

    def test_version_1_noise_rejects_version_2_length(self) -> None:
        with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.length"):
            self.validate(noise_data(version=1, length=0))


class Ch4NoiseNoteTests(unittest.TestCase):
    def instruments(self, items: list[dict]) -> dict[str, dict[int, json_to_uge.InstrumentSpec]]:
        data = {"version": 2, "instruments": items}
        if any(item.get("channel") == "wave" for item in items):
            data["wave_tables"] = [{"name": "wave", "samples": [0] * 32}]
            for item in items:
                if item.get("channel") == "wave":
                    item.setdefault("waveform", "wave")
        return json_to_uge.validate_instruments(data)

    def build(self, events: list[dict], instruments: dict | None = None) -> list[json_to_uge.Cell]:
        if instruments is None:
            instruments = self.instruments(
                [{"id": 1, "name": "noise", "channel": "noise"}]
            )
        return json_to_uge.build_channel_pattern(
            events,
            "patterns.noise.drums",
            version=2,
            channel="noise",
            instruments=instruments,
        )

    def test_noise_note_names_use_common_note_numbers(self) -> None:
        expected = {
            "C3": 0,
            "C#3": 1,
            "B3": 11,
            "C4": 12,
            "B8": 71,
            "rest": json_to_uge.NO_NOTE,
        }
        for note, note_number in expected.items():
            with self.subTest(note=note):
                cells = self.build([{"note": note, "length": 1, "instrument": 1}])
                self.assertEqual(cells[0].note, note_number)

    def test_rest_requires_noise_instrument_and_clears_cell_instrument(self) -> None:
        cells = self.build([{"note": "rest", "length": 2, "instrument": 1}])
        self.assertEqual(cells[0], json_to_uge.Cell(note=json_to_uge.NO_NOTE, instrument=0))
        self.assertEqual(cells[1], json_to_uge.Cell())

        for instrument in (0, 16, "1", True):
            with self.subTest(instrument=instrument):
                with self.assertRaisesRegex(ValueError, r"patterns\.noise\.drums\[0\]\.instrument"):
                    self.build([{"note": "rest", "length": 1, "instrument": instrument}])

    def test_noise_note_rejects_forbidden_note_forms(self) -> None:
        for note in ("c4", "g#4", "C-4", "C_4", "Db4", "kick", "snare", "hat", "B2", "C9", 57, True, {"clock_shift": 4}):
            with self.subTest(note=note):
                with self.assertRaisesRegex(ValueError, r"patterns\.noise\.drums\[0\]\.note"):
                    self.build([{"note": note, "length": 1, "instrument": 1}])

    def test_noise_note_rejects_direct_noise_fields_and_unknown_fields(self) -> None:
        for field in ("noise_note", "clock_shift", "divisor_code", "nr43"):
            with self.subTest(field=field):
                event = {"note": "C4", "length": 1, "instrument": 1, field: 0}
                with self.assertRaisesRegex(ValueError, rf"patterns\.noise\.drums\[0\]\.{field}"):
                    self.build([event])

    def test_noise_note_allows_common_optional_fields_without_output_conversion(self) -> None:
        cells = self.build(
            [{
                "note": "C4",
                "length": 1,
                "instrument": 1,
                "volume": 0,
                "effect": None,
                "effect_param": None,
            }]
        )
        self.assertEqual(cells[0].note, 12)
        self.assertEqual(cells[0].instrument, 1)

    def test_noise_note_requires_noise_bank_instrument(self) -> None:
        for channel in ("pulse1", "pulse2", "wave"):
            with self.subTest(channel=channel):
                instruments = self.instruments([{"id": 1, "name": "other", "channel": channel}])
                with self.assertRaisesRegex(ValueError, r"instrument: Noise Instrument 1 is not defined"):
                    self.build([{"note": "C4", "length": 1, "instrument": 1}], instruments)

        instruments = self.instruments([
            {"id": 1, "name": "pulse", "channel": "pulse1"},
            {"id": 1, "name": "noise", "channel": "noise"},
        ])
        self.assertEqual(self.build([{"note": "C4", "length": 1, "instrument": 1}], instruments)[0].instrument, 1)

        for instrument in (15,):
            instruments = self.instruments([{"id": instrument, "name": "noise", "channel": "noise"}])
            self.assertEqual(
                self.build([{"note": "B8", "length": 1, "instrument": instrument}], instruments)[0].instrument,
                instrument,
            )

        with self.assertRaisesRegex(ValueError, r"Noise Instrument 2 is not defined"):
            self.build([{"note": "C4", "length": 1, "instrument": 2}])

    def test_noise_note_rejects_unknown_note_fields(self) -> None:
        for value in (1, "x", True, None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, r"unknown Noise note field"):
                    self.build([{"note": "C4", "length": 1, "instrument": 1, "unknown": value}])

    def test_version_1_noise_note_does_not_apply_version_2_bank_check(self) -> None:
        cells = json_to_uge.build_channel_pattern(
            [{"note": "C4", "length": 1, "instrument": 1}],
            "patterns.noise.legacy",
            version=1,
            channel="noise",
        )
        self.assertEqual(cells[0].note, 12)
        self.assertEqual(cells[0].instrument, 1)


class NoisePolyTests(unittest.TestCase):
    def reference(self, note_number: int) -> tuple[int, int | None, int | None]:
        x = (~((note_number + 192) & 0xFF)) & 0xFF
        if x < 7:
            return x, None, None
        clock_shift = ((x - 4) // 4) & 0x0F
        divisor_code = (x % 4) + 4
        return (clock_shift << 4) | divisor_code, clock_shift, divisor_code

    def test_representative_noise_note_values(self) -> None:
        for note_number in (0, 1, 12, 24, 48, 56, 57, 58, 63, 64, 71):
            with self.subTest(note_number=note_number):
                poly = json_to_uge.noise_note_to_poly(note_number)
                self.assertEqual(
                    (poly.value, poly.clock_shift, poly.divisor_code),
                    self.reference(note_number),
                )

    def test_all_valid_noise_notes_match_reference(self) -> None:
        for note_number in range(72):
            with self.subTest(note_number=note_number):
                poly = json_to_uge.noise_note_to_poly(note_number)
                self.assertEqual(
                    (poly.value, poly.clock_shift, poly.divisor_code),
                    self.reference(note_number),
                )
                self.assertEqual(poly.value & 0x08, 0)

    def test_special_branch_57_through_63_returns_raw_poly(self) -> None:
        for note_number, expected in zip(range(57, 64), range(6, -1, -1)):
            with self.subTest(note_number=note_number):
                poly = json_to_uge.noise_note_to_poly(note_number)
                self.assertEqual(poly.value, expected)
                self.assertIsNone(poly.clock_shift)
                self.assertIsNone(poly.divisor_code)

    def test_invalid_noise_note_numbers_are_rejected(self) -> None:
        for value in (-1, 72, 89, 90, 91, 256, True, False, "12", 12.0, None, {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, r"note_number.*0-71"):
                    json_to_uge.noise_note_to_poly(value)


class PackedNoiseInstrumentTests(unittest.TestCase):
    def pack(self, data: dict) -> bytes:
        return json_to_uge.pack_instruments(json_to_uge.validate_instruments(data))

    def test_version_2_noise_fields_are_written_to_uge_record(self) -> None:
        record = read_noise_instrument(
            self.pack(
                noise_data(
                    name="noise custom",
                    length=37,
                    length_enable=True,
                    initial_volume=9,
                    envelope_direction="up",
                    envelope_sweep=5,
                    width_mode="7bit",
                )
            ),
            1,
        )
        self.assertEqual(
            record,
            {
                "type": json_to_uge.IT_NOISE,
                "name": "noise custom",
                "length": 37,
                "length_enable": True,
                "initial_volume": 9,
                "vol_sweep_direction": json_to_uge.ST_UP,
                "vol_sweep_amount": 5,
                "counter_step": json_to_uge.SW_SEVEN,
            },
        )

    def test_version_2_noise_defaults_are_written(self) -> None:
        record = read_noise_instrument(self.pack(noise_data()), 1)
        self.assertEqual(record["length"], 0)
        self.assertFalse(record["length_enable"])
        self.assertEqual(record["initial_volume"], 15)
        self.assertEqual(record["vol_sweep_direction"], json_to_uge.ST_DOWN)
        self.assertEqual(record["vol_sweep_amount"], 0)
        self.assertEqual(record["counter_step"], json_to_uge.SW_FIFTEEN)

    def test_noise_width_modes_only_change_counter_step(self) -> None:
        common = {
            "length": 37,
            "length_enable": True,
            "initial_volume": 9,
            "envelope_direction": "up",
            "envelope_sweep": 5,
        }
        record_15 = read_noise_instrument(self.pack(noise_data(**common, width_mode="15bit")), 1)
        record_7 = read_noise_instrument(self.pack(noise_data(**common, width_mode="7bit")), 1)
        self.assertEqual(record_15["counter_step"], json_to_uge.SW_FIFTEEN)
        self.assertEqual(record_7["counter_step"], json_to_uge.SW_SEVEN)
        self.assertEqual(
            {key: value for key, value in record_15.items() if key != "counter_step"},
            {key: value for key, value in record_7.items() if key != "counter_step"},
        )

    def test_undefined_noise_instruments_keep_default_records(self) -> None:
        blob = self.pack(noise_data())
        record_size = len(json_to_uge.pack_instrument(json_to_uge.IT_NOISE, ""))
        self.assertEqual(len(blob), 3 * json_to_uge.INSTRUMENT_COUNT * record_size)
        record = read_noise_instrument(blob, 2)
        self.assertEqual(record["type"], json_to_uge.IT_NOISE)
        self.assertEqual(record["name"], "")
        self.assertEqual(record["length"], 0)
        self.assertFalse(record["length_enable"])
        self.assertEqual(record["initial_volume"], 15)
        self.assertEqual(record["vol_sweep_direction"], json_to_uge.ST_DOWN)
        self.assertEqual(record["vol_sweep_amount"], 0)
        self.assertEqual(record["counter_step"], json_to_uge.SW_FIFTEEN)

    def test_version_1_noise_fields_are_not_reflected_in_uge(self) -> None:
        record = read_noise_instrument(
            self.pack(
                noise_data(
                    version=1,
                    noise_length=37,
                    length_enable=True,
                    initial_volume=9,
                    envelope_direction="up",
                    envelope_sweep=5,
                    width_mode="7bit",
                )
            ),
            1,
        )
        self.assertEqual(record["name"], "noise test")
        self.assertEqual(record["length"], 0)
        self.assertFalse(record["length_enable"])
        self.assertEqual(record["initial_volume"], 15)
        self.assertEqual(record["vol_sweep_direction"], json_to_uge.ST_DOWN)
        self.assertEqual(record["vol_sweep_amount"], 0)
        self.assertEqual(record["counter_step"], json_to_uge.SW_FIFTEEN)

    def test_invalid_internal_width_mode_is_rejected(self) -> None:
        specs = json_to_uge.validate_instruments(noise_data())
        specs["noise"][1] = replace(specs["noise"][1], width_mode="invalid")
        with self.assertRaisesRegex(ValueError, r"Noise Instrument 1.*width_mode"):
            json_to_uge.pack_instruments(specs)


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
    data = {"version": version, "instruments": [instrument]}
    if version == 2:
        waveform = fields.get("waveform")
        table_name = waveform if isinstance(waveform, str) and waveform and waveform == waveform.strip() and waveform.islower() else "bass"
        data["wave_tables"] = [{"name": table_name, "samples": [0] * 32}]
    return data


def wave_data_with_tables(names: list[str], waveform: str | None = None, instruments: list[dict] | None = None) -> dict:
    data = {
        "version": 2,
        "instruments": instruments if instruments is not None else [
            {
                "id": 1,
                "name": "wave test",
                "channel": "wave",
                "waveform": waveform if waveform is not None else names[0],
            }
        ],
        "wave_tables": [
            {"name": name, "samples": [0] * 32}
            for name in names
        ],
    }
    return data


def uge_wave_fixture(wave_tables: list[dict] | None = None) -> dict:
    data = {
        "version": 2,
        "title": "Wave bank test",
        "type": "bgm",
        "tempo": 6,
        "instruments": [],
        "order": ["main"],
        "patterns": {
            "main": {
                "channels": {
                    "pulse1": [],
                    "pulse2": [],
                    "wave": [],
                    "noise": [],
                }
            }
        },
    }
    if wave_tables is not None:
        data["wave_tables"] = wave_tables
    return data


def read_uge_wave_banks(uge: bytes) -> tuple[bytes, ...]:
    header_size = 4 + (3 * len(json_to_uge.pack_short_string("", "test")))
    instrument_size = len(json_to_uge.pack_instrument(json_to_uge.IT_SQUARE, ""))
    wave_offset = header_size + (3 * json_to_uge.INSTRUMENT_COUNT * instrument_size)
    return tuple(
        uge[wave_offset + index * json_to_uge.WAVE_BYTES : wave_offset + (index + 1) * json_to_uge.WAVE_BYTES]
        for index in range(json_to_uge.WAVE_COUNT)
    )


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

    def test_wave_table_array_order_resolves_to_zero_based_indices(self) -> None:
        names = ["bass_wave", "lead_wave"]
        result = json_to_uge.validate_instruments(wave_data_with_tables(names))
        first = result["wave"][1]
        self.assertEqual(first.waveform, "bass_wave")
        self.assertEqual(first.waveform_index, 0)

        result = json_to_uge.validate_instruments(wave_data_with_tables(names, "lead_wave"))
        self.assertEqual(result["wave"][1].waveform_index, 1)

    def test_wave_table_array_order_not_name_order(self) -> None:
        data = wave_data_with_tables(["z_wave", "a_wave"], "z_wave")
        result = json_to_uge.validate_instruments(data)
        self.assertEqual(result["wave"][1].waveform_index, 0)

        data["instruments"][0]["waveform"] = "a_wave"
        result = json_to_uge.validate_instruments(data)
        self.assertEqual(result["wave"][1].waveform_index, 1)

    def test_sixteen_wave_tables_resolve_last_entry_to_index_15(self) -> None:
        names = [f"wave_{index}" for index in range(16)]
        result = json_to_uge.validate_instruments(wave_data_with_tables(names, names[-1]))
        self.assertEqual(result["wave"][1].waveform_index, 15)

    def test_multiple_wave_instruments_can_share_or_use_different_tables(self) -> None:
        data = wave_data_with_tables(
            ["bass_wave", "lead_wave"],
            instruments=[
                {"id": 1, "name": "bass", "channel": "wave", "waveform": "bass_wave"},
                {"id": 2, "name": "lead", "channel": "wave", "waveform": "lead_wave"},
                {"id": 3, "name": "bass copy", "channel": "wave", "waveform": "bass_wave"},
            ],
        )
        result = json_to_uge.validate_instruments(data)
        self.assertEqual(result["wave"][1].waveform_index, 0)
        self.assertEqual(result["wave"][2].waveform_index, 1)
        self.assertEqual(result["wave"][3].waveform_index, 0)

    def test_wave_tables_are_optional_without_wave_instruments(self) -> None:
        self.assertEqual(json_to_uge.validate_instruments({"version": 2, "instruments": []}), {"duty": {}, "wave": {}, "noise": {}})
        data = {"version": 2, "instruments": [], "wave_tables": []}
        self.assertEqual(json_to_uge.validate_instruments(data), {"duty": {}, "wave": {}, "noise": {}})

    def test_version_1_ignores_wave_tables(self) -> None:
        data = {
            "version": 1,
            "instruments": [],
            "wave_tables": "not interpreted in Version 1",
        }
        self.assertEqual(json_to_uge.validate_instruments(data), {"duty": {}, "wave": {}, "noise": {}})

    def test_unreferenced_wave_tables_are_allowed(self) -> None:
        data = wave_data_with_tables(["used_wave", "unused_wave"], "used_wave")
        data["wave_tables"][0]["samples"] = [0] * 32
        data["wave_tables"][1]["samples"] = [15] * 32
        result = json_to_uge.validate_instruments(data)
        self.assertEqual(result["wave"][1].waveform_index, 0)

    def test_wave_table_spec_keeps_name_index_and_sample_order(self) -> None:
        samples = list(range(16)) + list(range(15, -1, -1))
        data = {"version": 2, "instruments": [], "wave_tables": [{"name": "bass_wave", "samples": samples}]}
        specs = json_to_uge.validate_wave_tables(data, 2)
        self.assertIsNotNone(specs)
        self.assertEqual(specs, (json_to_uge.WaveTableSpec("bass_wave", 0, tuple(samples)),))
        self.assertEqual(json_to_uge.build_waveform_index(specs), {"bass_wave": 0})

    def test_wave_table_all_zero_and_all_max_samples_are_valid(self) -> None:
        data = {
            "version": 2,
            "instruments": [],
            "wave_tables": [
                {"name": "zero_wave", "samples": [0] * 32},
                {"name": "max_wave", "samples": [15] * 32},
            ],
        }
        specs = json_to_uge.validate_wave_tables(data, 2)
        self.assertEqual(specs[0].samples, (0,) * 32)
        self.assertEqual(specs[1].samples, (15,) * 32)

    def test_sixteen_wave_tables_and_valid_trailing_underscore_name_are_allowed(self) -> None:
        names = ["wave_"] + [f"wave_{index}" for index in range(1, 16)]
        data = {"version": 2, "instruments": [], "wave_tables": [
            {"name": name, "samples": [index % 16] * 32}
            for index, name in enumerate(names)
        ]}
        specs = json_to_uge.validate_wave_tables(data, 2)
        self.assertEqual(len(specs), 16)
        self.assertEqual(specs[0].index, 0)
        self.assertEqual(specs[-1].index, 15)

    def test_wave_table_object_requires_name_and_samples(self) -> None:
        cases = (
            ({"samples": [0] * 32}, r"wave_tables\[0\]\.name"),
            ({"name": "bass"}, r"wave_tables\[0\]\.samples"),
        )
        for table, path in cases:
            with self.subTest(table=table):
                with self.assertRaisesRegex(ValueError, path):
                    json_to_uge.validate_wave_tables(
                        {"version": 2, "instruments": [], "wave_tables": [table]},
                        2,
                    )

    def test_wave_table_unknown_keys_are_rejected(self) -> None:
        valid = {"name": "bass", "samples": [0] * 32}
        for extra in ({"metadata": 1}, {"foo": 1, "bar": 2}):
            with self.subTest(extra=extra):
                table = {**valid, **extra}
                with self.assertRaisesRegex(ValueError, r"wave_tables\[0\]\.(?:metadata|foo|bar).*unknown"):
                    json_to_uge.validate_wave_tables(
                        {"version": 2, "instruments": [], "wave_tables": [table]},
                        2,
                    )

    def test_wave_table_samples_length_and_types_are_rejected(self) -> None:
        cases = (
            ([], r"wave_tables\[0\]\.samples"),
            ([0] * 31, r"wave_tables\[0\]\.samples"),
            ([0] * 33, r"wave_tables\[0\]\.samples"),
            ("samples", r"wave_tables\[0\]\.samples.*array"),
            (None, r"wave_tables\[0\]\.samples.*array"),
            ({}, r"wave_tables\[0\]\.samples.*array"),
        )
        for samples, path in cases:
            with self.subTest(samples=samples):
                with self.assertRaisesRegex(ValueError, path):
                    json_to_uge.validate_wave_tables(
                        {"version": 2, "instruments": [], "wave_tables": [{"name": "bass", "samples": samples}]},
                        2,
                    )

    def test_wave_table_sample_values_reject_invalid_positions(self) -> None:
        cases = (
            (-1, 0),
            (16, 15),
            (1.5, 0),
            ("1", 15),
            (True, 0),
            (None, 31),
            ([], 12),
            ({}, 31),
        )
        for value, index in cases:
            with self.subTest(value=value, index=index):
                samples = [0] * 32
                samples[index] = value
                with self.assertRaisesRegex(ValueError, rf"wave_tables\[0\]\.samples\[{index}\]"):
                    json_to_uge.validate_wave_tables(
                        {"version": 2, "instruments": [], "wave_tables": [{"name": "bass", "samples": samples}]},
                        2,
                    )

    def test_wave_instrument_requires_wave_tables(self) -> None:
        data = wave_data(waveform="bass")
        del data["wave_tables"]
        with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.waveform.*does not exist"):
            json_to_uge.validate_instruments(data)

        data = wave_data(waveform="bass")
        data["wave_tables"] = []
        with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.waveform.*does not exist"):
            json_to_uge.validate_instruments(data)

    def test_wave_tables_basic_shape_and_name_rules_are_checked(self) -> None:
        valid_samples = [0] * 32
        cases = (
            ("wave_tables", {}, "array expected"),
            ("wave_tables", [None], "object expected"),
            ("wave_tables", [{}], "name.*string expected"),
            ("wave_tables", [{"name": 1, "samples": valid_samples}], "name.*string expected"),
            ("wave_tables", [{"name": "", "samples": valid_samples}], "name"),
            ("wave_tables", [{"name": "   ", "samples": valid_samples}], "name"),
            ("wave_tables", [{"name": " bass", "samples": valid_samples}], "name"),
            ("wave_tables", [{"name": "Bass", "samples": valid_samples}], "name"),
            ("wave_tables", [{"name": "bad-name", "samples": valid_samples}], "name"),
            ("wave_tables", [{"name": "wave", "samples": valid_samples}] * 17, "at most 16"),
        )
        for field, value, message in cases:
            with self.subTest(value=value):
                data = {"version": 2, "instruments": []}
                data[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    json_to_uge.validate_instruments(data)

    def test_duplicate_wave_table_names_are_rejected_case_sensitively(self) -> None:
        data = wave_data_with_tables(["bass", "bass"], "bass")
        with self.assertRaisesRegex(ValueError, "duplicate Wave table name 'bass'"):
            json_to_uge.validate_instruments(data)

        data = wave_data_with_tables(["bass", "lead"], "Bass")
        with self.assertRaisesRegex(ValueError, r"instruments\[0\]\.waveform.*does not exist"):
            json_to_uge.validate_instruments(data)

    def test_waveform_reference_requires_exact_existing_name(self) -> None:
        for waveform in ("missing", "bass ", "0", 0):
            with self.subTest(waveform=repr(waveform)):
                data = wave_data_with_tables(["bass"], waveform)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    json_to_uge.validate_instruments(data)

    def test_duty_and_wave_ids_can_match_with_resolved_waveform(self) -> None:
        data = wave_data_with_tables(
            ["bass"],
            instruments=[
                {"id": 1, "name": "wave", "channel": "wave", "waveform": "bass"},
                {"id": 1, "name": "pulse", "channel": "pulse1"},
            ],
        )
        result = json_to_uge.validate_instruments(data)
        self.assertEqual(result["wave"][1].waveform_index, 0)


class WaveSamplePackingTests(unittest.TestCase):
    def test_all_zero_and_all_max_samples_pack_to_fixed_length(self) -> None:
        self.assertEqual(json_to_uge.pack_wave_samples([0] * 32), bytes([0x00] * 16))
        self.assertEqual(json_to_uge.pack_wave_samples([15] * 32), bytes([0xFF] * 16))

    def test_sequential_samples_pack_in_order(self) -> None:
        samples = list(range(16)) * 2
        expected = bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF] * 2)
        packed = json_to_uge.pack_wave_samples(samples)
        self.assertEqual(packed, expected)
        self.assertEqual(len(packed), 16)

    def test_upper_and_lower_nibbles_are_not_reversed(self) -> None:
        self.assertEqual(json_to_uge.pack_wave_samples([15, 0] * 16), bytes([0xF0] * 16))
        self.assertEqual(json_to_uge.pack_wave_samples([0, 15] * 16), bytes([0x0F] * 16))
        samples = [0] * 32
        samples[0:4] = [1, 2, 10, 15]
        self.assertEqual(json_to_uge.pack_wave_samples(samples)[0:2], bytes([0x12, 0xAF]))

    def test_packing_does_not_mutate_input_and_is_deterministic(self) -> None:
        samples = list(range(16)) * 2
        original = samples.copy()
        first = json_to_uge.pack_wave_samples(samples)
        second = json_to_uge.pack_wave_samples(samples)
        self.assertEqual(samples, original)
        self.assertEqual(first, second)

    def test_wave_table_spec_packs_samples_without_changing_metadata(self) -> None:
        samples = tuple(range(16)) * 2
        wave_table = json_to_uge.WaveTableSpec("bass_wave", 3, samples)
        self.assertEqual(json_to_uge.pack_wave_table(wave_table), bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF] * 2))
        self.assertEqual(wave_table.name, "bass_wave")
        self.assertEqual(wave_table.index, 3)
        self.assertEqual(wave_table.samples, samples)

    def test_multiple_wave_tables_are_packed_independently(self) -> None:
        first = json_to_uge.WaveTableSpec("first", 0, tuple([1, 2] * 16))
        second = json_to_uge.WaveTableSpec("second", 1, tuple([3, 4] * 16))
        self.assertEqual(json_to_uge.pack_wave_table(first), bytes([0x12] * 16))
        self.assertEqual(json_to_uge.pack_wave_table(second), bytes([0x34] * 16))

    def test_default_wave_can_be_packed(self) -> None:
        samples = json_to_uge.DEFAULT_WAVES[0]
        expected = bytes(
            (samples[index] << 4) | samples[index + 1]
            for index in range(0, len(samples), 2)
        )
        packed = json_to_uge.pack_wave_samples(samples)
        self.assertEqual(len(packed), 16)
        self.assertEqual(packed, expected)

    def test_invalid_sample_lengths_are_rejected(self) -> None:
        for samples in ([], [0] * 31, [0] * 33):
            with self.subTest(length=len(samples)):
                with self.assertRaisesRegex(ValueError, "exactly 32"):
                    json_to_uge.pack_wave_samples(samples)

    def test_invalid_sample_types_and_ranges_are_rejected_at_multiple_positions(self) -> None:
        cases = (
            (0, -1),
            (15, 16),
            (1, 1.5),
            (2, "1"),
            (3, True),
            (16, None),
            (12, []),
            (31, {}),
        )
        for index, value in cases:
            with self.subTest(index=index, value=value):
                samples = [0] * 32
                samples[index] = value
                with self.assertRaisesRegex(ValueError, rf"samples\[{index}\]"):
                    json_to_uge.pack_wave_samples(samples)

    def test_non_array_input_is_rejected(self) -> None:
        for samples in (None, "samples", {}, 0):
            with self.subTest(samples=samples):
                with self.assertRaisesRegex(ValueError, "array expected"):
                    json_to_uge.pack_wave_samples(samples)


class UgeWaveBankTests(unittest.TestCase):
    def tables(self, count: int) -> list[dict]:
        return [
            {"name": f"wave_{index}", "samples": [index % 16] * 32}
            for index in range(count)
        ]

    def test_version_2_wave_banks_are_always_16_banks_and_512_bytes(self) -> None:
        for count in (1, 3, 11, 12, 16):
            with self.subTest(count=count):
                banks = read_uge_wave_banks(json_to_uge.build_uge(uge_wave_fixture(self.tables(count))))
                self.assertEqual(len(banks), 16)
                self.assertEqual(sum(len(bank) for bank in banks), 512)
                for index, bank in enumerate(banks):
                    if index < count:
                        self.assertEqual(bank, bytes([index % 16] * 32))
                    elif index <= 10:
                        self.assertEqual(bank, bytes(json_to_uge.DEFAULT_WAVES[index]))
                    else:
                        self.assertEqual(bank, bytes(32))

    def test_version_2_defined_wave_table_is_not_packed_for_uge(self) -> None:
        samples = [1, 2, 10, 15] + [0] * 28
        banks = read_uge_wave_banks(
            json_to_uge.build_uge(
                uge_wave_fixture([{"name": "bass", "samples": samples}])
            )
        )
        self.assertEqual(banks[0][:4], bytes([1, 2, 10, 15]))
        self.assertNotEqual(banks[0][:2], bytes([0x12, 0xAF]))

    def test_version_2_without_wave_tables_uses_standard_banks(self) -> None:
        for data in (uge_wave_fixture(), uge_wave_fixture([])):
            with self.subTest(has_wave_tables="wave_tables" in data):
                banks = read_uge_wave_banks(json_to_uge.build_uge(data))
                self.assertEqual(banks[:11], tuple(bytes(wave) for wave in json_to_uge.DEFAULT_WAVES))
                self.assertEqual(banks[11:], tuple(bytes(32) for _ in range(5)))

    def test_unreferenced_wave_tables_are_still_output_in_array_order(self) -> None:
        tables = [
            {"name": "used", "samples": [1] * 32},
            {"name": "unused", "samples": [2] * 32},
        ]
        banks = read_uge_wave_banks(json_to_uge.build_uge(uge_wave_fixture(tables)))
        self.assertEqual(banks[0], bytes([1] * 32))
        self.assertEqual(banks[1], bytes([2] * 32))

    def test_wave_instrument_index_matches_uge_wave_bank_position(self) -> None:
        tables = self.tables(3)
        tables[2]["samples"] = list(range(16)) * 2
        data = uge_wave_fixture(tables)
        data["instruments"] = [{
            "id": 1,
            "name": "bass",
            "channel": "wave",
            "waveform": "wave_2",
        }]
        banks = read_uge_wave_banks(json_to_uge.build_uge(data))
        specs = json_to_uge.validate_instruments(data)
        self.assertEqual(specs["wave"][1].waveform_index, 2)
        self.assertEqual(banks[2], bytes(tables[2]["samples"]))

    def test_direct_wave_bank_builder_rejects_invalid_internal_state(self) -> None:
        valid = json_to_uge.WaveTableSpec("wave", 0, (0,) * 32)
        invalid_specs = (
            (json_to_uge.WaveTableSpec("wave", True, (0,) * 32), "integer"),
            (json_to_uge.WaveTableSpec("wave", 1, (0,) * 32), "expected 0"),
            (json_to_uge.WaveTableSpec("wave", 0, (0,) * 31), "exactly 32"),
            (json_to_uge.WaveTableSpec("wave", 0, (-1,) + (0,) * 31), r"samples\[0\]"),
        )
        for spec, message in invalid_specs:
            with self.subTest(spec=spec):
                with self.assertRaisesRegex(ValueError, message):
                    json_to_uge.build_uge_wave_banks((spec,))
        self.assertEqual(len(json_to_uge.build_uge_wave_banks((valid,))), 16)


class PackedWaveInstrumentTests(unittest.TestCase):
    def pack(self, data: dict) -> bytes:
        return json_to_uge.pack_instruments(json_to_uge.validate_instruments(data))

    def test_version_2_wave_fields_are_written_to_uge(self) -> None:
        data = wave_data_with_tables(
            ["bass_wave", "lead_wave", "pad_wave"],
            "pad_wave",
            [
                {
                    "id": 3,
                    "name": "Wave Bass",
                    "channel": "wave",
                    "waveform": "pad_wave",
                    "output_level": "50%",
                    "length": 173,
                    "length_enable": True,
                }
            ],
        )
        record = read_wave_instrument(self.pack(data), 3)
        self.assertEqual(
            record,
            {
                "type": json_to_uge.IT_WAVE,
                "name": "Wave Bass",
                "length": 173,
                "length_enable": True,
                "output_level": 2,
                "waveform": 2,
            },
        )

    def test_waveform_index_zero_is_written_as_zero(self) -> None:
        data = wave_data_with_tables(
            ["bass_wave"],
            "bass_wave",
            [{"id": 3, "name": "first", "channel": "wave", "waveform": "bass_wave"}],
        )
        record = read_wave_instrument(self.pack(data), 3)
        self.assertEqual(record["waveform"], 0)

    def test_all_output_levels_are_written_unchanged(self) -> None:
        names = ["mute_wave", "full_wave", "half_wave", "quarter_wave"]
        output_levels = ("mute", "100%", "50%", "25%")
        instruments = [
            {
                "id": index + 1,
                "name": f"wave {index}",
                "channel": "wave",
                "waveform": names[index],
                "output_level": output_levels[index],
            }
            for index in range(4)
        ]
        data = wave_data_with_tables(names, instruments=instruments)
        packed = self.pack(data)
        for index, expected in enumerate(range(4), start=1):
            with self.subTest(instrument_id=index):
                self.assertEqual(read_wave_instrument(packed, index)["output_level"], expected)

    def test_wave_length_boundaries_and_length_enable_are_written(self) -> None:
        data = wave_data_with_tables(
            ["zero_wave", "max_wave"],
            instruments=[
                {
                    "id": 1,
                    "name": "zero",
                    "channel": "wave",
                    "waveform": "zero_wave",
                    "length": 0,
                    "length_enable": False,
                },
                {
                    "id": 2,
                    "name": "max",
                    "channel": "wave",
                    "waveform": "max_wave",
                    "length": 255,
                    "length_enable": True,
                },
            ],
        )
        packed = self.pack(data)
        self.assertEqual(read_wave_instrument(packed, 1)["length"], 0)
        self.assertFalse(read_wave_instrument(packed, 1)["length_enable"])
        self.assertEqual(read_wave_instrument(packed, 2)["length"], 255)
        self.assertTrue(read_wave_instrument(packed, 2)["length_enable"])

    def test_multiple_wave_instruments_keep_independent_values(self) -> None:
        names = [f"wave_{index}" for index in range(4)]
        data = wave_data_with_tables(
            names,
            instruments=[
                {"id": 2, "name": "two", "channel": "wave", "waveform": names[0], "output_level": "100%"},
                {"id": 7, "name": "seven", "channel": "wave", "waveform": names[3], "output_level": "25%"},
            ],
        )
        packed = self.pack(data)
        self.assertEqual(read_wave_instrument(packed, 2)["waveform"], 0)
        self.assertEqual(read_wave_instrument(packed, 2)["output_level"], 1)
        self.assertEqual(read_wave_instrument(packed, 7)["waveform"], 3)
        self.assertEqual(read_wave_instrument(packed, 7)["output_level"], 3)

    def test_undefined_version_2_wave_instruments_keep_standard_values(self) -> None:
        data = wave_data_with_tables(
            ["defined_wave"],
            instruments=[
                {"id": 3, "name": "defined", "channel": "wave", "waveform": "defined_wave"},
            ],
        )
        record = read_wave_instrument(self.pack(data), 4)
        self.assertEqual(record["type"], json_to_uge.IT_WAVE)
        self.assertEqual(record["name"], json_to_uge.DEFAULT_WAVE_NAMES[4])
        self.assertEqual(record["waveform"], 3)
        self.assertEqual(record["output_level"], 1)
        self.assertEqual(record["length"], 0)
        self.assertFalse(record["length_enable"])

    def test_unresolved_waveform_index_is_an_error(self) -> None:
        data = wave_data_with_tables(
            ["defined_wave"],
            instruments=[{"id": 1, "name": "defined", "channel": "wave", "waveform": "defined_wave"}],
        )
        specs = json_to_uge.validate_instruments(data)
        for invalid in (None, -1, 16):
            with self.subTest(waveform_index=invalid):
                overrides = {
                    "duty": specs["duty"],
                    "wave": {1: replace(specs["wave"][1], waveform_index=invalid)},
                    "noise": specs["noise"],
                }
                with self.assertRaisesRegex(ValueError, r"Wave Instrument 1.*waveform_index"):
                    json_to_uge.pack_instruments(overrides)


class WaveAsmInstrumentTests(unittest.TestCase):
    def instruments(self, items: list[dict]) -> dict[str, dict[int, json_to_uge.InstrumentSpec]]:
        return json_to_uge.validate_instruments(
            wave_data_with_tables(
                [f"wave_{index}" for index in range(16)],
                instruments=items,
            )
        )

    def test_wave_entry_has_six_bytes_in_hugedriver_order(self) -> None:
        instruments = self.instruments(
            [
                {
                    "id": 3,
                    "name": "Wave Bass",
                    "channel": "wave",
                    "waveform": "wave_5",
                    "output_level": "50%",
                    "length": 173,
                    "length_enable": True,
                }
            ]
        )
        self.assertEqual(
            json_to_huge_asm.wave_instrument_bytes(3, instruments),
            (173, 0x40, 5, 0, 0, 0xC0),
        )

    def test_wave_instrument_rendering_preserves_field_order_and_boundaries(self) -> None:
        instruments = self.instruments(
            [
                {"id": 3, "name": "bass", "channel": "wave", "waveform": "wave_2", "length": 10},
                {"id": 7, "name": "lead", "channel": "wave", "waveform": "wave_5", "output_level": "25%", "length_enable": True},
            ]
        )
        patterns = {
            0: [json_to_uge.Cell(instrument=3)],
            1: [json_to_uge.Cell(instrument=7)],
        }
        order_matrix = [[], [], [0, 1], []]
        lines = json_to_huge_asm.render_wave_instruments(
            "song",
            patterns,
            order_matrix,
            instruments,
            2,
        )
        self.assertEqual(lines[0], "song_wave_instruments:")
        self.assertEqual(lines[-1], "")

        id3 = lines.index("song_itWaveinst3:")
        self.assertEqual(lines[id3 + 1 : id3 + 7], ["db 10", "db 32", "db 2", "dw 0", "db 128", ""])
        id7 = lines.index("song_itWaveinst7:")
        self.assertEqual(lines[id7 + 1 : id7 + 7], ["db 0", "db 96", "db 5", "dw 0", "db 192", ""])
        self.assertEqual(id7 - id3, 4 * 7)

    def test_waveform_index_zero_and_fifteen_are_not_recalculated_from_id(self) -> None:
        instruments = self.instruments(
            [
                {"id": 3, "name": "first", "channel": "wave", "waveform": "wave_0"},
                {"id": 7, "name": "last", "channel": "wave", "waveform": "wave_15"},
            ]
        )
        self.assertEqual(json_to_huge_asm.wave_instrument_bytes(3, instruments)[2], 0)
        self.assertEqual(json_to_huge_asm.wave_instrument_bytes(7, instruments)[2], 15)

    def test_wave_instrument_invalid_internal_indices_are_rejected(self) -> None:
        data = wave_data_with_tables(
            ["wave_0"],
            instruments=[{"id": 1, "name": "wave", "channel": "wave", "waveform": "wave_0"}],
        )
        specs = json_to_uge.validate_instruments(data)
        for invalid in (None, -1, 16, True):
            with self.subTest(waveform_index=invalid):
                invalid_specs = {
                    "duty": specs["duty"],
                    "wave": {1: replace(specs["wave"][1], waveform_index=invalid)},
                    "noise": specs["noise"],
                }
                with self.assertRaisesRegex(ValueError, r"Wave Instrument 1.*waveform_index"):
                    json_to_huge_asm.wave_instrument_bytes(1, invalid_specs)

    def test_wave_bank_is_empty_when_no_wave_instrument_is_used(self) -> None:
        lines = json_to_huge_asm.render_wave_instruments(
            "song",
            {},
            [[], [], [], []],
            {"duty": {}, "wave": {}, "noise": {}},
            2,
        )
        self.assertEqual(lines, ["song_wave_instruments:"])

    def test_version_1_wave_bank_remains_empty(self) -> None:
        instruments = self.instruments(
            [{"id": 1, "name": "legacy", "channel": "wave", "waveform": "wave_0"}]
        )
        lines = json_to_huge_asm.render_wave_instruments(
            "song",
            {0: [json_to_uge.Cell(instrument=1)]},
            [[], [], [0], []],
            instruments,
            1,
        )
        self.assertEqual(lines, ["song_wave_instruments:", ""])


class NoiseAsmInstrumentTests(unittest.TestCase):
    def instruments(self, items: list[dict]) -> dict[str, dict[int, json_to_uge.InstrumentSpec]]:
        return json_to_uge.validate_instruments(
            {"version": 2, "instruments": items}
        )

    def test_noise_entry_contains_nr42_and_length_width_byte(self) -> None:
        instruments = self.instruments(
            [
                {
                    "id": 1,
                    "name": "noise custom",
                    "channel": "noise",
                    "length": 23,
                    "length_enable": True,
                    "initial_volume": 10,
                    "envelope_direction": "up",
                    "envelope_sweep": 5,
                    "width_mode": "7bit",
                }
            ]
        )
        self.assertEqual(
            json_to_huge_asm.noise_instrument_bytes(1, instruments),
            (0xAD, 0, 0, 0xD7, 0, 0),
        )

    def test_noise_entry_defaults(self) -> None:
        instruments = self.instruments(
            [{"id": 1, "name": "defaults", "channel": "noise"}]
        )
        self.assertEqual(
            json_to_huge_asm.noise_instrument_bytes(1, instruments),
            (0xF0, 0, 0, 0, 0, 0),
        )

    def test_noise_width_mode_only_changes_width_bit(self) -> None:
        common = {
            "id": 1,
            "name": "noise",
            "channel": "noise",
            "length": 23,
            "length_enable": True,
            "initial_volume": 10,
            "envelope_direction": "up",
            "envelope_sweep": 5,
        }
        instruments_15 = self.instruments([{**common, "width_mode": "15bit"}])
        instruments_7 = self.instruments([{**common, "width_mode": "7bit"}])
        entry_15 = json_to_huge_asm.noise_instrument_bytes(1, instruments_15)
        entry_7 = json_to_huge_asm.noise_instrument_bytes(1, instruments_7)
        self.assertEqual(entry_15[0:3], entry_7[0:3])
        self.assertEqual(entry_15[4:], entry_7[4:])
        self.assertEqual(entry_15[3] ^ entry_7[3], 0x80)

    def test_noise_length_enable_only_changes_length_enable_bit(self) -> None:
        common = {"id": 1, "name": "noise", "channel": "noise", "length": 23}
        disabled = self.instruments([{**common, "length_enable": False}])
        enabled = self.instruments([{**common, "length_enable": True}])
        entry_disabled = json_to_huge_asm.noise_instrument_bytes(1, disabled)
        entry_enabled = json_to_huge_asm.noise_instrument_bytes(1, enabled)
        self.assertEqual(entry_disabled[3], 23)
        self.assertEqual(entry_enabled[3], 0x40 | 23)
        self.assertEqual(entry_disabled[3] ^ entry_enabled[3], 0x40)

    def test_noise_bank_uses_ch4_maximum_and_does_not_mix_other_channels(self) -> None:
        instruments = self.instruments(
            [
                {"id": 1, "name": "noise one", "channel": "noise"},
                {"id": 2, "name": "noise two", "channel": "noise", "width_mode": "7bit"},
                {"id": 3, "name": "pulse three", "channel": "pulse1"},
            ]
        )
        patterns = {
            0: [json_to_uge.Cell(instrument=2)],
            1: [json_to_uge.Cell(instrument=1)],
        }
        order_matrix = [[], [], [], [0, 1]]
        lines = json_to_huge_asm.render_noise_instruments(
            "song", patterns, order_matrix, instruments, 2
        )
        self.assertEqual(lines[0], "song_noise_instruments:")
        self.assertIn("song_itNoiseinst1:", lines)
        self.assertIn("song_itNoiseinst2:", lines)
        self.assertNotIn("song_itNoiseinst3:", lines)
        id2 = lines.index("song_itNoiseinst2:")
        self.assertEqual(lines[id2 + 1 : id2 + 6], ["db 240", "dw 0", "db 128", "dw 0", ""])

    def test_version_1_noise_bank_remains_empty(self) -> None:
        instruments = json_to_uge.validate_instruments(
            noise_data(version=1, noise_length=12, width_mode="7bit")
        )
        lines = json_to_huge_asm.render_noise_instruments(
            "song",
            {0: [json_to_uge.Cell(instrument=1)]},
            [[], [], [], [0]],
            instruments,
            1,
        )
        self.assertEqual(lines, ["song_noise_instruments:", ""])

    def test_noise_invalid_internal_width_mode_is_rejected(self) -> None:
        instruments = self.instruments(
            [{"id": 1, "name": "noise", "channel": "noise"}]
        )
        instruments["noise"][1] = replace(instruments["noise"][1], width_mode="invalid")
        with self.assertRaisesRegex(ValueError, r"Noise Instrument 1.*width_mode"):
            json_to_huge_asm.noise_instrument_bytes(1, instruments)


class WaveTableAsmTests(unittest.TestCase):
    def wave_lines(self, tables: list[dict]) -> list[str]:
        asm = json_to_huge_asm.build_asm(
            uge_wave_fixture(tables),
            "song",
        )
        lines = asm.splitlines()
        start = lines.index("song_waves:")
        return lines[start + 1 : start + 17]

    def parse_line(self, line: str) -> bytes:
        self.assertTrue(line.startswith("db "))
        return bytes(int(token[1:], 16) for token in line[3:].split(","))

    def test_one_wave_table_is_packed_in_asm_order(self) -> None:
        samples = [1, 2, 10, 15] + [0] * 28
        lines = self.wave_lines([{"name": "bass", "samples": samples}])
        self.assertEqual(self.parse_line(lines[0])[:2], bytes([0x12, 0xAF]))
        self.assertEqual(len(self.parse_line(lines[0])), 16)

    def test_multiple_wave_tables_keep_definition_order_and_boundaries(self) -> None:
        tables = [
            {"name": "first", "samples": [1, 2] * 16},
            {"name": "second", "samples": [3, 4] * 16},
        ]
        lines = self.wave_lines(tables)
        self.assertEqual(len(lines), 16)
        self.assertEqual(self.parse_line(lines[0]), bytes([0x12] * 16))
        self.assertEqual(self.parse_line(lines[1]), bytes([0x34] * 16))
        self.assertEqual(len(self.parse_line(lines[0])), 16)

    def test_asm_wave_boundaries_and_complement_values(self) -> None:
        tables = [{"name": "zero", "samples": [0] * 32}]
        lines = self.wave_lines(tables)
        self.assertEqual(self.parse_line(lines[0]), bytes([0x00] * 16))
        self.assertEqual(self.parse_line(lines[1]), bytes(
            (samples[index] << 4) | samples[index + 1]
            for index in range(0, 32, 2)
            for samples in [json_to_uge.DEFAULT_WAVES[1]]
        ))
        self.assertEqual(self.parse_line(lines[11]), bytes([0x00] * 16))
        self.assertEqual(len(lines), 16)

    def test_asm_wave_all_max_and_alternating_samples(self) -> None:
        tables = [
            {"name": "max", "samples": [15] * 32},
            {"name": "alternating", "samples": [0, 15] * 16},
        ]
        lines = self.wave_lines(tables)
        self.assertEqual(self.parse_line(lines[0]), bytes([0xFF] * 16))
        self.assertEqual(self.parse_line(lines[1]), bytes([0x0F] * 16))

    def test_sixteen_wave_tables_are_emitted_without_extra_data(self) -> None:
        tables = [
            {"name": f"wave_{index}", "samples": [index % 16] * 32}
            for index in range(16)
        ]
        lines = self.wave_lines(tables)
        self.assertEqual(len(lines), 16)
        self.assertEqual(self.parse_line(lines[15]), bytes([0xFF] * 16))

    def test_version_2_without_wave_tables_emits_standard_sixteen_banks(self) -> None:
        asm = json_to_huge_asm.build_asm(uge_wave_fixture(), "song")
        lines = asm.splitlines()
        start = lines.index("song_waves:")
        wave_lines = lines[start + 1 : start + 17]
        self.assertEqual(len(wave_lines), 16)
        self.assertEqual(
            self.parse_line(wave_lines[0]),
            json_to_uge.pack_wave_samples(json_to_uge.DEFAULT_WAVES[0]),
        )

    def test_version_1_wave_table_output_remains_label_only(self) -> None:
        data = json.loads((ROOT / "assets" / "bgm_title.json").read_text(encoding="utf-8"))
        asm = json_to_huge_asm.build_asm(data, "bgm_title")
        lines = asm.splitlines()
        start = lines.index("bgm_title_waves:")
        self.assertEqual(lines[start + 1 :], [])


if __name__ == "__main__":
    unittest.main()
