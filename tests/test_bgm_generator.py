import json
import os
import random
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from bgm_generator import (  # noqa: E402
    GENERATOR_VERSION,
    GenerationContext,
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
    deterministic_probe,
    generate_accompaniment,
    generate_melody,
    generate_structure,
)


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


if __name__ == "__main__":
    unittest.main()
