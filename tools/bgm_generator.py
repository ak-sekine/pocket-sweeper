"""Deterministic random foundation for later BGM generators.

This module deliberately does not generate musical material.  It provides an
explicit-seed context and a small probe used by tests and later WBS tasks.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from numbers import Real
from typing import Sequence, TypeVar


GENERATOR_VERSION = "0.1.0"
T = TypeVar("T")


class GenerationInputError(ValueError):
    """Raised when a generation input cannot be deterministic or is invalid."""


@dataclass(frozen=True)
class GenerationMetadata:
    seed: int
    generator_version: str

    def as_dict(self) -> dict[str, object]:
        return {"seed": self.seed, "generator_version": self.generator_version}


class GenerationContext:
    """Own an independent deterministic PRNG for one generation run."""

    def __init__(self, seed: int, generator_version: str = GENERATOR_VERSION) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise GenerationInputError("seed must be an integer")
        if not isinstance(generator_version, str) or not generator_version:
            raise GenerationInputError("generator_version must be a non-empty string")
        self.seed = seed
        self.generator_version = generator_version
        self.rng = random.Random(seed)

    @property
    def metadata(self) -> GenerationMetadata:
        return GenerationMetadata(self.seed, self.generator_version)

    def choice(self, candidates: Sequence[T]) -> T:
        values = _ordered_values(candidates)
        if not values:
            raise GenerationInputError("choice requires at least one candidate")
        return self.rng.choice(values)

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        try:
            if stop is None:
                return self.rng.randrange(start)
            return self.rng.randrange(start, stop, step)
        except (TypeError, ValueError) as exc:
            raise GenerationInputError(str(exc)) from exc

    def weighted_choice(self, candidates: Sequence[T], weights: Sequence[Real]) -> T:
        values = _ordered_values(candidates)
        if not values:
            raise GenerationInputError("weighted_choice requires candidates")
        if len(values) != len(weights):
            raise GenerationInputError("candidates and weights must have equal length")
        normalized: list[float] = []
        for weight in weights:
            if isinstance(weight, bool) or not isinstance(weight, Real) or weight < 0:
                raise GenerationInputError("weights must be non-negative real numbers")
            normalized.append(float(weight))
        total = sum(normalized)
        if total <= 0:
            raise GenerationInputError("at least one weight must be positive")
        threshold = self.rng.random() * total
        cumulative = 0.0
        for value, weight in zip(values, normalized):
            cumulative += weight
            if threshold < cumulative:
                return value
        return values[-1]

    def shuffled(self, candidates: Sequence[T]) -> list[T]:
        values = _ordered_values(candidates)
        self.rng.shuffle(values)
        return values


def _ordered_values(candidates: Sequence[T]) -> list[T]:
    if isinstance(candidates, (str, bytes)):
        raise GenerationInputError("candidates must be an ordered collection, not text")
    if isinstance(candidates, (set, frozenset)):
        raise GenerationInputError("candidate ordering must be explicit")
    try:
        return list(candidates)
    except TypeError as exc:
        raise GenerationInputError("candidates must be an ordered collection") from exc


def deterministic_probe(seed: int) -> dict[str, object]:
    """Return a small non-musical deterministic probe for integration tests."""
    context = GenerationContext(seed)
    values = ["a", "b", "c", "d"]
    return {
        "metadata": context.metadata.as_dict(),
        "choice": context.choice(values),
        "range": context.randrange(0, 100),
        "weighted": context.weighted_choice(values, [1, 2, 3, 4]),
        "shuffle": context.shuffled(values),
    }
