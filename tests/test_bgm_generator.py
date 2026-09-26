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
    deterministic_probe,
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


if __name__ == "__main__":
    unittest.main()
