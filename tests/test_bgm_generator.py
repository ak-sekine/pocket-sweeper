import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from bgm_generator import (  # noqa: E402
    GENERATOR_VERSION,
    GenerationContext,
    LogicalGenerationPlan,
    GenerationInputError,
    StructureGenerationOptions,
    StructureParameters,
    MelodyGenerationOptions,
    MelodyParameters,
    MotifDefinition,
    MotifStep,
    AccompanimentGenerationOptions,
    AccompanimentParameters,
    AccompanimentPatternDefinition,
    AccompanimentPatternStep,
    BassGenerationOptions,
    BassParameters,
    BassPatternDefinition,
    BassPatternStep,
    NoiseGenerationOptions,
    NoiseParameters,
    NoisePatternDefinition,
    NoisePatternStep,
    deterministic_probe,
    generate_accompaniment,
    generate_bass,
    generate_noise,
    LayerAllocation,
    GameBoyConversionInput,
    SfxOccupancy,
    validate_game_boy_allocation,
    generate_melody,
    generate_structure,
    generate_logical_composition,
    convert_to_json_v2,
)
import json_to_uge  # noqa: E402
import json_to_huge_asm  # noqa: E402
import build_sound_test_rom  # noqa: E402


class GenerationContextTests(unittest.TestCase):
    def test_same_seed_has_same_probe_and_metadata(self):
        self.assertEqual(deterministic_probe(42), deterministic_probe(42))
        self.assertEqual(deterministic_probe(42)["metadata"], {"seed": 42, "generator_version": GENERATOR_VERSION})

    def test_contexts_are_independent_of_global_random_state(self):
        random.seed(1)
        expected = deterministic_probe(1234)
        random.seed(999999)
        self.assertEqual(deterministic_probe(1234), expected)

    def test_negative_and_arbitrarily_large_integer_seeds_are_allowed(self):
        self.assertEqual(deterministic_probe(-1), deterministic_probe(-1))
        huge = 2**4096
        self.assertEqual(deterministic_probe(huge), deterministic_probe(huge))

    def test_invalid_seed_is_rejected(self):
        for seed in (None, "42", 1.5, True):
            with self.subTest(seed=seed):
                with self.assertRaises(GenerationInputError):
                    GenerationContext(seed)

    def test_candidate_ordering_and_weight_errors(self):
        context = GenerationContext(1)
        with self.assertRaises(GenerationInputError):
            context.choice(set("abc"))
        with self.assertRaises(GenerationInputError):
            context.choice([])
        with self.assertRaises(GenerationInputError):
            context.weighted_choice(["a"], [0])
        with self.assertRaises(GenerationInputError):
            context.weighted_choice(["a"], [-1])
        with self.assertRaises(GenerationInputError):
            context.weighted_choice(["a"], [1, 2])

    def test_subprocess_reproduces_probe(self):
        code = (
            "import json, sys; sys.path.insert(0, sys.argv[1]); "
            "from bgm_generator import deterministic_probe; "
            "print(json.dumps(deterministic_probe(987654321), sort_keys=True))"
        )
        env = os.environ.copy()
        first = subprocess.run(
            [sys.executable, "-c", code, str(ROOT / "tools")],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        second = subprocess.run(
            [sys.executable, "-c", code, str(ROOT / "tools")],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(json.loads(first.stdout), json.loads(second.stdout))


class CompleteLogicalGenerationTests(unittest.TestCase):
    def plan(self):
        motif = MotifDefinition("motif-a", (MotifStep(2, absolute_pitch=0), MotifStep(2, rest=True)))
        accompaniment = AccompanimentPatternDefinition(
            "support-a", "rhythmic_support", (AccompanimentPatternStep(2, absolute_pitch=0), AccompanimentPatternStep(2, rest=True))
        )
        bass = BassPatternDefinition(
            "bass-a", (BassPatternStep(2, bass_relation="root", absolute_pitch=0), BassPatternStep(2, rest=True))
        )
        noise = NoisePatternDefinition(
            "noise-a", (NoisePatternStep(2, role="beat_support", character_ref="low"), NoisePatternStep(2, rest=True))
        )
        return LogicalGenerationPlan(
            StructureParameters(4, 4, phrase_measures=1, section_phrase_counts=(2,), loop_mode="full"),
            StructureGenerationOptions(),
            MelodyParameters(motif_by_phrase=("motif-a", "motif-a"), variation_by_phrase=("exact", "exact")),
            MelodyGenerationOptions(motif_definitions=(motif,)),
            AccompanimentParameters(pattern_by_phrase=("support-a", "support-a"), variation_by_phrase=("exact", "exact")),
            AccompanimentGenerationOptions(pattern_definitions=(accompaniment,)),
            BassParameters(pattern_by_phrase=("bass-a", "bass-a"), variation_by_phrase=("exact", "exact")),
            BassGenerationOptions(pattern_definitions=(bass,)),
            NoiseParameters(pattern_by_phrase=("noise-a", "noise-a"), variation_by_phrase=("exact", "exact")),
            NoiseGenerationOptions(pattern_definitions=(noise,)),
        )

    def test_master_seed_reproduces_complete_logical_composition(self):
        for seed in (0, 1, 42, -1, 2**256):
            first = generate_logical_composition(seed, self.plan())
            second = generate_logical_composition(seed, self.plan())
            self.assertEqual(first.as_dict(), second.as_dict())
            self.assertEqual(first.as_dict()["metadata"], {"seed": seed, "generator_version": GENERATOR_VERSION})

    def test_complete_generation_does_not_use_global_random_state(self):
        random.seed(1)
        first = generate_logical_composition(42, self.plan()).as_dict()
        random.seed(999)
        self.assertEqual(first, generate_logical_composition(42, self.plan()).as_dict())

    def test_end_to_end_cli_writes_manifest_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "generated"
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "generate_bgm_test_rom.py"),
                 "--seed", "42", "--profile", str(ROOT / "tools" / "generation_profile_fixture.py"),
                 "--output-dir", str(output), "--name", "generated_seed_42"],
                check=True, capture_output=True, text=True,
            )
            for suffix in ("json", "uge", "asm", "gb", "manifest.json"):
                self.assertTrue((output / f"generated_seed_42.{suffix}").exists())

    def test_candidate_profile_uses_driver_ticks_per_row_as_tempo(self):
        profile_path = ROOT / "tools" / "generation_profile_candidates.py"
        namespace = {}
        exec(profile_path.read_text(encoding="utf-8"), namespace)
        profile = namespace["build_profile"](1)
        self.assertEqual(profile["tempo"], profile["ticks_per_row"])


class StructureGenerationTests(unittest.TestCase):
    def setUp(self):
        self.parameters = StructureParameters(
            ticks_per_beat=4,
            beats_per_measure=4,
            phrase_measures=2,
            section_phrase_counts=(1, 2),
        )

    def test_structure_is_reproducible_and_serializable(self):
        first = generate_structure(GenerationContext(7), self.parameters, StructureGenerationOptions(loop_modes=("full",)))
        second = generate_structure(GenerationContext(7), self.parameters, StructureGenerationOptions(loop_modes=("full",)))
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertEqual(first.total_duration_tick, 96)
        self.assertEqual(first.loop_start_tick, 0)
        self.assertEqual(first.loop_end_tick, 96)

    def test_structure_has_contiguous_sections_and_phrases(self):
        structure = generate_structure(GenerationContext(1), self.parameters, StructureGenerationOptions(loop_modes=("none",)))
        self.assertEqual([section.start_tick for section in structure.sections], [0, 32])
        self.assertEqual([phrase.start_tick for phrase in structure.phrases], [0, 32, 64])
        self.assertEqual(structure.as_dict()["time_grid"]["ticks_per_measure"], 16)
        self.assertIsNone(structure.loop_start_tick)

    def test_range_loop_uses_phrase_boundaries(self):
        parameters = StructureParameters(**{**self.parameters.__dict__, "loop_mode": "range", "loop_start_phrase": 1, "loop_end_phrase": 3})
        structure = generate_structure(GenerationContext(2), parameters)
        self.assertEqual((structure.loop_start_tick, structure.loop_end_tick), (32, 96))

    def test_candidates_are_selected_by_context_and_empty_candidates_fail(self):
        parameters = StructureParameters(ticks_per_beat=4, beats_per_measure=4)
        options = StructureGenerationOptions(phrase_measures=(1, 2), section_phrase_counts=((1,), (2,)), loop_modes=("none", "full"))
        first = generate_structure(GenerationContext(10), parameters, options)
        second = generate_structure(GenerationContext(10), parameters, options)
        self.assertEqual(first.as_dict(), second.as_dict())
        with self.assertRaises(GenerationInputError):
            generate_structure(GenerationContext(1), parameters, StructureGenerationOptions())

    def test_invalid_grid_and_loop_are_rejected(self):
        with self.assertRaises(GenerationInputError):
            generate_structure(GenerationContext(1), StructureParameters(0, 4, 1, (1,), "full"))
        with self.assertRaises(GenerationInputError):
            generate_structure(GenerationContext(1), StructureParameters(4, 4, 1, (1,), "range"))
        with self.assertRaises(GenerationInputError):
            generate_structure(GenerationContext(1), StructureParameters(4, 4, 1, (1,), "range", 1, 1))


class MelodyGenerationTests(unittest.TestCase):
    def setUp(self):
        self.structure = generate_structure(
            GenerationContext(3),
            StructureParameters(4, 4, 1, (2,)),
            StructureGenerationOptions(loop_modes=("full",)),
        )
        self.motif = MotifDefinition(
            "motif-a",
            (MotifStep(2, relative_interval=0), MotifStep(2, relative_interval=1), MotifStep(2, rest=True)),
        )

    def _generate(self, seed=3):
        return generate_melody(
            GenerationContext(seed),
            self.structure,
            MelodyParameters(motif_by_phrase=("motif-a", "motif-a"), variation_by_phrase=("exact", "relative_interval_offset"), variation_offsets_by_phrase=(0, 1)),
            MelodyGenerationOptions(motif_definitions=(self.motif,), variation_candidates=("exact",)),
        )

    def test_melody_is_reproducible_and_not_channel_bound(self):
        first = self._generate()
        second = self._generate()
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertIsNone(first.as_dict()["layer"]["physical_channel"])
        self.assertEqual(first.events[1].pitch_value, 1)

    def test_motif_instance_and_phrase_references_are_preserved(self):
        layer = self._generate()
        self.assertEqual([instance.phrase_ref for instance in layer.motif_instances], ["phrase-001", "phrase-002"])
        self.assertTrue(all(event.phrase_ref in {"phrase-001", "phrase-002"} for event in layer.events))
        self.assertEqual(layer.as_dict(), self._generate().as_dict())

    def test_invalid_motif_and_candidate_inputs_are_rejected(self):
        invalid = MotifDefinition("bad", (MotifStep(1, rest=True, relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_melody(GenerationContext(1), self.structure, MelodyParameters(motif_by_phrase=("bad", "bad"), variation_by_phrase=("exact", "exact")), MelodyGenerationOptions(motif_definitions=(invalid,)))
        with self.assertRaises(GenerationInputError):
            generate_melody(GenerationContext(1), self.structure, MelodyParameters(motif_by_phrase=("motif-a", "motif-a"), variation_by_phrase=("unsupported", "exact")), MelodyGenerationOptions(motif_definitions=(self.motif,)))
        with self.assertRaises(GenerationInputError):
            generate_melody(GenerationContext(1), self.structure, MelodyParameters(motif_by_phrase=("motif-a",), variation_by_phrase=("exact", "exact")), MelodyGenerationOptions(motif_definitions=(self.motif,)))

    def test_motif_must_fit_and_duplicate_events_are_rejected_by_validation(self):
        long_motif = MotifDefinition("long", (MotifStep(100, relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_melody(GenerationContext(1), self.structure, MelodyParameters(motif_by_phrase=("long", "long"), variation_by_phrase=("exact", "exact")), MelodyGenerationOptions(motif_definitions=(long_motif,)))


class AccompanimentGenerationTests(unittest.TestCase):
    def setUp(self):
        self.structure = generate_structure(
            GenerationContext(4),
            StructureParameters(4, 4, 1, (2,)),
            StructureGenerationOptions(loop_modes=("full",)),
        )
        self.pattern = AccompanimentPatternDefinition(
            "support-a", "rhythmic_support",
            (AccompanimentPatternStep(2, relative_interval=0), AccompanimentPatternStep(2, rest=True)),
        )

    def _generate(self, seed=4):
        return generate_accompaniment(
            GenerationContext(seed), self.structure,
            AccompanimentParameters(pattern_by_phrase=("support-a", "support-a"), variation_by_phrase=("exact", "relative_interval_offset"), variation_offsets_by_phrase=(0, 1)),
            AccompanimentGenerationOptions(pattern_definitions=(self.pattern,)),
        )

    def test_accompaniment_is_reproducible_and_not_channel_bound(self):
        first = self._generate()
        self.assertEqual(first.as_dict(), self._generate().as_dict())
        self.assertIsNone(first.as_dict()["layer"]["physical_channel"])
        self.assertEqual(first.events[3].pitch_value, 1)

    def test_pattern_instance_and_event_phrase_references_are_checked(self):
        layer = self._generate()
        self.assertTrue(all(event.pattern_instance_ref for event in layer.events))
        self.assertTrue(all(event.phrase_ref in {"phrase-001", "phrase-002"} for event in layer.events))

    def test_harmony_ref_requires_caller_supplied_context(self):
        pattern = AccompanimentPatternDefinition(
            "harmony-support", "sustained_tone",
            (AccompanimentPatternStep(2, relative_interval=0, harmony_ref="h-1"),),
        )
        params = AccompanimentParameters(pattern_by_phrase=("harmony-support", "harmony-support"), variation_by_phrase=("exact", "exact"))
        with self.assertRaises(GenerationInputError):
            generate_accompaniment(GenerationContext(1), self.structure, params, AccompanimentGenerationOptions(pattern_definitions=(pattern,)))
        layer = generate_accompaniment(GenerationContext(1), self.structure, params, AccompanimentGenerationOptions(pattern_definitions=(pattern,), harmony_refs=("h-1",)))
        self.assertEqual(layer.events[0].harmony_ref, "h-1")

    def test_invalid_realization_pitch_overlap_and_fit_are_rejected(self):
        bad_realization = AccompanimentPatternDefinition("bad", "arpeggiation", (AccompanimentPatternStep(1, relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_accompaniment(GenerationContext(1), self.structure, AccompanimentParameters(pattern_by_phrase=("bad", "bad"), variation_by_phrase=("exact", "exact")), AccompanimentGenerationOptions(pattern_definitions=(bad_realization,)))
        bad_pitch = AccompanimentPatternDefinition("bad-pitch", "sustained_tone", (AccompanimentPatternStep(1, relative_interval=0, scale_degree=1),))
        with self.assertRaises(GenerationInputError):
            generate_accompaniment(GenerationContext(1), self.structure, AccompanimentParameters(pattern_by_phrase=("bad-pitch", "bad-pitch"), variation_by_phrase=("exact", "exact")), AccompanimentGenerationOptions(pattern_definitions=(bad_pitch,)))
        long_pattern = AccompanimentPatternDefinition("long", "sustained_tone", (AccompanimentPatternStep(100, relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_accompaniment(GenerationContext(1), self.structure, AccompanimentParameters(pattern_by_phrase=("long", "long"), variation_by_phrase=("exact", "exact")), AccompanimentGenerationOptions(pattern_definitions=(long_pattern,)))


class BassGenerationTests(unittest.TestCase):
    def setUp(self):
        self.structure = generate_structure(
            GenerationContext(5),
            StructureParameters(4, 4, 1, (2,)),
            StructureGenerationOptions(loop_modes=("full",)),
        )
        self.pattern = BassPatternDefinition(
            "bass-a",
            (BassPatternStep(2, bass_relation="root", relative_interval=0), BassPatternStep(2, rest=True)),
        )

    def _generate(self, seed=5):
        return generate_bass(
            GenerationContext(seed), self.structure,
            BassParameters(pattern_by_phrase=("bass-a", "bass-a"), variation_by_phrase=("exact", "relative_interval_offset"), variation_offsets_by_phrase=(0, -1)),
            BassGenerationOptions(pattern_definitions=(self.pattern,)),
        )

    def test_bass_is_reproducible_and_not_channel_bound(self):
        first = self._generate()
        self.assertEqual(first.as_dict(), self._generate().as_dict())
        self.assertIsNone(first.as_dict()["layer"]["physical_channel"])
        self.assertEqual(first.events[3].pitch_value, -1)
        self.assertEqual(first.events[0].bass_relation, "root")

    def test_bass_relation_and_harmony_reference_are_separate(self):
        pattern = BassPatternDefinition(
            "harmony-bass", (BassPatternStep(2, bass_relation="chord_tone", relative_interval=0, harmony_ref="h-1"),),
        )
        params = BassParameters(pattern_by_phrase=("harmony-bass", "harmony-bass"), variation_by_phrase=("exact", "exact"))
        with self.assertRaises(GenerationInputError):
            generate_bass(GenerationContext(1), self.structure, params, BassGenerationOptions(pattern_definitions=(pattern,)))
        layer = generate_bass(GenerationContext(1), self.structure, params, BassGenerationOptions(pattern_definitions=(pattern,), harmony_refs=("h-1",)))
        self.assertEqual(layer.events[0].bass_relation, "chord_tone")
        self.assertEqual(layer.events[0].harmony_ref, "h-1")

    def test_invalid_relation_pitch_and_pattern_fit_are_rejected(self):
        bad_relation = BassPatternDefinition("bad", (BassPatternStep(1, bass_relation="walking", relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_bass(GenerationContext(1), self.structure, BassParameters(pattern_by_phrase=("bad", "bad"), variation_by_phrase=("exact", "exact")), BassGenerationOptions(pattern_definitions=(bad_relation,)))
        bad_pitch = BassPatternDefinition("bad-pitch", (BassPatternStep(1, bass_relation="pedal", relative_interval=0, scale_degree=1),))
        with self.assertRaises(GenerationInputError):
            generate_bass(GenerationContext(1), self.structure, BassParameters(pattern_by_phrase=("bad-pitch", "bad-pitch"), variation_by_phrase=("exact", "exact")), BassGenerationOptions(pattern_definitions=(bad_pitch,)))
        long_pattern = BassPatternDefinition("long", (BassPatternStep(100, relative_interval=0),))
        with self.assertRaises(GenerationInputError):
            generate_bass(GenerationContext(1), self.structure, BassParameters(pattern_by_phrase=("long", "long"), variation_by_phrase=("exact", "exact")), BassGenerationOptions(pattern_definitions=(long_pattern,)))


class NoiseGenerationTests(unittest.TestCase):
    def setUp(self):
        self.structure = generate_structure(
            GenerationContext(6),
            StructureParameters(4, 4, 1, (2,)),
            StructureGenerationOptions(loop_modes=("full",)),
        )
        self.pattern = NoisePatternDefinition(
            "noise-a",
            (NoisePatternStep(2, role="beat_support", character_ref="caller-hit", accent="strong"), NoisePatternStep(2, rest=True)),
        )

    def _generate(self, seed=6):
        return generate_noise(
            GenerationContext(seed), self.structure,
            NoiseParameters(pattern_by_phrase=("noise-a", "noise-a"), variation_by_phrase=("exact", "exact")),
            NoiseGenerationOptions(pattern_definitions=(self.pattern,)),
        )

    def test_noise_is_reproducible_and_not_ch4_bound(self):
        first = self._generate()
        self.assertEqual(first.as_dict(), self._generate().as_dict())
        self.assertIsNone(first.as_dict()["layer"]["physical_channel"])
        self.assertEqual(first.events[0].role, "beat_support")
        self.assertEqual(first.events[0].character_ref, "caller-hit")

    def test_noise_events_have_no_pitch_fields(self):
        event = self._generate().as_dict()["events"][0]
        self.assertNotIn("pitch_kind", event)
        self.assertNotIn("pitch_value", event)
        self.assertNotIn("nr43", event)

    def test_rest_metadata_role_and_fit_are_validated(self):
        bad_rest = NoisePatternDefinition("bad-rest", (NoisePatternStep(1, rest=True, role="pulse"),))
        with self.assertRaises(GenerationInputError):
            generate_noise(GenerationContext(1), self.structure, NoiseParameters(pattern_by_phrase=("bad-rest", "bad-rest"), variation_by_phrase=("exact", "exact")), NoiseGenerationOptions(pattern_definitions=(bad_rest,)))
        no_role = NoisePatternDefinition("no-role", (NoisePatternStep(1),))
        with self.assertRaises(GenerationInputError):
            generate_noise(GenerationContext(1), self.structure, NoiseParameters(pattern_by_phrase=("no-role", "no-role"), variation_by_phrase=("exact", "exact")), NoiseGenerationOptions(pattern_definitions=(no_role,)))
        long_pattern = NoisePatternDefinition("long", (NoisePatternStep(100, role="accent"),))
        with self.assertRaises(GenerationInputError):
            generate_noise(GenerationContext(1), self.structure, NoiseParameters(pattern_by_phrase=("long", "long"), variation_by_phrase=("exact", "exact")), NoiseGenerationOptions(pattern_definitions=(long_pattern,)))

    def test_only_exact_variation_is_supported(self):
        with self.assertRaises(GenerationInputError):
            generate_noise(GenerationContext(1), self.structure, NoiseParameters(pattern_by_phrase=("noise-a", "noise-a"), variation_by_phrase=("fill", "exact")), NoiseGenerationOptions(pattern_definitions=(self.pattern,)))


class AllocationValidationTests(unittest.TestCase):
    def setUp(self):
        self.layers = [SimpleNamespace(id=name) for name in ("melody-001", "accompaniment-001", "bass-001", "noise-percussion-001")]

    def test_channel_capabilities_and_four_channel_exclusivity(self):
        result = validate_game_boy_allocation(
            self.layers,
            (
                LayerAllocation("melody-001", "CH1", ("pulse", "sweep")),
                LayerAllocation("accompaniment-001", "CH2", ("pulse",)),
                LayerAllocation("bass-001", "CH3", ("wave",)),
                LayerAllocation("noise-percussion-001", "CH4", ("noise",)),
            ),
        )
        self.assertTrue(result.valid)
        duplicate = validate_game_boy_allocation(self.layers, (LayerAllocation("melody-001", "CH1"), LayerAllocation("bass-001", "CH1")))
        self.assertFalse(duplicate.valid)
        self.assertTrue(any("exclusive" in item for item in duplicate.machine_violations))

    def test_invalid_capability_and_unknown_layer(self):
        result = validate_game_boy_allocation(self.layers, (LayerAllocation("unknown", "CH4", ("pulse",)),))
        self.assertFalse(result.valid)
        self.assertTrue(any("unknown logical" in item for item in result.machine_violations))
        self.assertTrue(any("lacks capabilities" in item for item in result.machine_violations))

    def test_sfx_preemption_distinguishes_required_and_degradable(self):
        pulse_sfx = SfxOccupancy("pulse1_sfx", "CH1")
        required = validate_game_boy_allocation(self.layers, (LayerAllocation("melody-001", "CH1", ("pulse",), "required"),), (pulse_sfx,))
        self.assertFalse(required.valid)
        self.assertTrue(any("required layer" in item for item in required.machine_violations))
        degradable = validate_game_boy_allocation(self.layers, (LayerAllocation("melody-001", "CH1", ("pulse",), "temporarily_degradable"),), (pulse_sfx,))
        self.assertTrue(degradable.valid)
        self.assertTrue(degradable.human_review_items)

    def test_noise_sfx_can_preempt_degradable_noise_and_ch2_future_sfx_is_not_current(self):
        noise_sfx = SfxOccupancy("cursor", "CH4")
        result = validate_game_boy_allocation(self.layers, (LayerAllocation("noise-percussion-001", "CH4", ("noise",), "optional"),), (noise_sfx,))
        self.assertTrue(result.valid)
        self.assertTrue(result.human_review_items)
        future_ch2 = SfxOccupancy("pulse2_future", "CH2", implemented=False)
        result = validate_game_boy_allocation(self.layers, (LayerAllocation("accompaniment-001", "CH2", ("pulse",), "required"),), (future_ch2,))
        self.assertTrue(result.valid)
        self.assertTrue(any("future" in item for item in result.notes))

    def test_timeline_stop_is_rejected_and_current_recovery_is_recorded(self):
        result = validate_game_boy_allocation(self.layers, (), (SfxOccupancy("cursor", "CH4"),), timeline_continues_during_sfx=False)
        self.assertFalse(result.valid)
        self.assertTrue(any("timeline" in item for item in result.machine_violations))


class GameBoyConversionTests(unittest.TestCase):
    def setUp(self):
        self.structure = generate_structure(
            GenerationContext(7),
            StructureParameters(1, 1, phrase_measures=1, section_phrase_counts=(1, 1), loop_mode="full"),
        )
        self.layer = SimpleNamespace(
            id="melody-001",
            events=(SimpleNamespace(id="event-001", phrase_ref="phrase-001", start_tick=0,
                                    duration_tick=1, rest=False, pitch_kind="absolute_pitch", pitch_value=0),),
        )
        self.instrument = {"id": 1, "name": "caller-pulse", "channel": "pulse1"}

    def conversion(self, **kwargs):
        values = dict(
            structure=self.structure, logical_layers=(self.layer,),
            allocations=(LayerAllocation("melody-001", "CH1", ("pulse",)),),
            title="generated", tempo=120, ticks_per_row=1,
            instrument_by_channel={"CH1": 1}, instruments=(self.instrument,),
            absolute_pitch_map={0: "C4"}, noise_character_map={},
        )
        values.update(kwargs)
        return GameBoyConversionInput(**values)

    def test_explicit_allocation_and_existing_v2_converter(self):
        result = convert_to_json_v2(self.conversion())
        self.assertEqual(result["version"], 2)
        self.assertEqual(result["order"], {"pulse1": ["section-001", "section-002"]})
        self.assertTrue(json_to_uge.build_uge(result))
        asm = json_to_huge_asm.build_asm(result, "generated_song")
        self.assertIn('include "hUGE.inc"', asm)
        self.assertIn("generated_song_loop_metadata", asm)
        self.assertFalse(hasattr(self.layer, "physical_channel"))

    def test_conversion_is_deterministic_and_full_loop_is_preserved(self):
        first = convert_to_json_v2(self.conversion())
        second = convert_to_json_v2(self.conversion())
        self.assertEqual(first, second)
        self.assertEqual(json_to_huge_asm.build_asm(first, "generated_song"), json_to_huge_asm.build_asm(second, "generated_song"))
        self.assertEqual(first["loop"], {"mode": "full"})

    def test_unresolved_pitch_and_non_exact_grid_are_rejected(self):
        unresolved = SimpleNamespace(**{**self.layer.__dict__, "events": (
            SimpleNamespace(id="event-001", phrase_ref="phrase-001", start_tick=0,
                            duration_tick=1, rest=False, pitch_kind="relative_interval", pitch_value=0),)})
        with self.assertRaises(GenerationInputError):
            convert_to_json_v2(self.conversion(logical_layers=(unresolved,)))
        with self.assertRaises(GenerationInputError):
            convert_to_json_v2(self.conversion(ticks_per_row=2))

    def test_invalid_allocation_and_missing_instrument_are_rejected(self):
        with self.assertRaises(GenerationInputError):
            convert_to_json_v2(self.conversion(allocations=(LayerAllocation("melody-001", "CH4", ("pulse",)),)))
        with self.assertRaises(GenerationInputError):
            convert_to_json_v2(self.conversion(instrument_by_channel={}))

    def test_range_loop_requires_explicit_order_boundary(self):
        structure = generate_structure(
            GenerationContext(8),
            StructureParameters(1, 1, phrase_measures=1, section_phrase_counts=(1, 1),
                                loop_mode="range", loop_start_phrase=1, loop_end_phrase=2),
        )
        result = convert_to_json_v2(self.conversion(structure=structure))
        self.assertEqual(result["loop"], {"mode": "range", "start_order": 1, "end_order": 2})
        self.assertIn("generated_song_loop_metadata", json_to_huge_asm.build_asm(result, "generated_song"))

    def test_generated_asm_builds_version_two_test_rom(self):
        data = convert_to_json_v2(self.conversion())
        asm = json_to_huge_asm.build_asm(data, "generated_song")
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = Path(temp_dir) / "generated_song.asm"
            rom_path = Path(temp_dir) / "generated_song.gb"
            asm_path.write_text(asm, encoding="utf-8")
            build_sound_test_rom.build_rom(asm_path, rom_path)
            self.assertEqual(rom_path.stat().st_size, 32768)


if __name__ == "__main__":
    unittest.main()
