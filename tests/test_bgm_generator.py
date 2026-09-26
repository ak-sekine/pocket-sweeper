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
    deterministic_probe,
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


if __name__ == "__main__":
    unittest.main()
