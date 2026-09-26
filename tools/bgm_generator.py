"""Deterministic random foundation for later BGM generators.

This module deliberately does not generate musical material.  It provides an
explicit-seed context and a small probe used by tests and later WBS tasks.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from numbers import Real
from typing import Sequence, TypeVar


GENERATOR_VERSION = "0.2.0"
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


LOOP_MODES = ("none", "full", "range")


@dataclass(frozen=True)
class StructureParameters:
    """Fixed grid values and optional explicit structural choices."""

    ticks_per_beat: int
    beats_per_measure: int
    phrase_measures: int | None = None
    section_phrase_counts: tuple[int, ...] | None = None
    loop_mode: str | None = None
    loop_start_phrase: int | None = None
    loop_end_phrase: int | None = None


@dataclass(frozen=True)
class StructureGenerationOptions:
    """Caller-owned candidates; this module provides no musical defaults."""

    phrase_measures: tuple[int, ...] = ()
    section_phrase_counts: tuple[tuple[int, ...], ...] = ()
    loop_modes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Phrase:
    id: str
    section_ref: str
    index: int
    start_tick: int
    duration_tick: int
    rule_refs: tuple[str, ...] = ()

    @property
    def end_tick(self) -> int:
        return self.start_tick + self.duration_tick

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "section_ref": self.section_ref,
            "index": self.index,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "end_tick": self.end_tick,
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class Section:
    id: str
    index: int
    start_tick: int
    duration_tick: int
    phrase_refs: tuple[str, ...]
    kind: str | None = None
    rule_refs: tuple[str, ...] = ()

    @property
    def end_tick(self) -> int:
        return self.start_tick + self.duration_tick

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "index": self.index,
            "kind": self.kind,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "end_tick": self.end_tick,
            "phrase_refs": list(self.phrase_refs),
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class CompositionStructure:
    metadata: GenerationMetadata
    ticks_per_beat: int
    beats_per_measure: int
    total_duration_tick: int
    section_refs: tuple[str, ...]
    sections: tuple[Section, ...]
    phrases: tuple[Phrase, ...]
    loop_mode: str
    loop_start_tick: int | None
    loop_end_tick: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": self.metadata.as_dict(),
            "time_grid": {
                "ticks_per_beat": self.ticks_per_beat,
                "beats_per_measure": self.beats_per_measure,
                "ticks_per_measure": self.ticks_per_beat * self.beats_per_measure,
            },
            "form": {"section_refs": list(self.section_refs)},
            "sections": [section.as_dict() for section in self.sections],
            "phrases": [phrase.as_dict() for phrase in self.phrases],
            "loop": {
                "mode": self.loop_mode,
                "start_tick": self.loop_start_tick,
                "end_tick": self.loop_end_tick,
            },
        }


def generate_structure(
    context: GenerationContext,
    parameters: StructureParameters,
    options: StructureGenerationOptions | None = None,
) -> CompositionStructure:
    """Generate only the shared composition/timeline skeleton."""
    options = options or StructureGenerationOptions()
    _positive_int(parameters.ticks_per_beat, "ticks_per_beat")
    _positive_int(parameters.beats_per_measure, "beats_per_measure")
    phrase_measures = parameters.phrase_measures
    if phrase_measures is None:
        phrase_measures = context.choice(options.phrase_measures)
    _positive_int(phrase_measures, "phrase_measures")
    counts = parameters.section_phrase_counts
    if counts is None:
        counts = context.choice(options.section_phrase_counts)
    if not counts:
        raise GenerationInputError("section_phrase_counts must not be empty")
    for count in counts:
        _positive_int(count, "section phrase count")
    loop_mode = parameters.loop_mode
    if loop_mode is None:
        loop_mode = context.choice(options.loop_modes)
    if loop_mode not in LOOP_MODES:
        raise GenerationInputError("loop_mode must be none, full, or range")

    ticks_per_measure = parameters.ticks_per_beat * parameters.beats_per_measure
    phrase_duration = phrase_measures * ticks_per_measure
    sections: list[Section] = []
    phrases: list[Phrase] = []
    cursor = 0
    for section_index, phrase_count in enumerate(counts):
        section_id = f"section-{section_index + 1:03d}"
        phrase_refs: list[str] = []
        section_start = cursor
        for phrase_index in range(phrase_count):
            phrase_id = f"phrase-{len(phrases) + 1:03d}"
            phrase = Phrase(phrase_id, section_id, phrase_index, cursor, phrase_duration)
            phrases.append(phrase)
            phrase_refs.append(phrase_id)
            cursor += phrase_duration
        sections.append(Section(section_id, section_index, section_start, cursor - section_start, tuple(phrase_refs)))

    total = cursor
    if loop_mode == "none":
        loop_start = loop_end = None
    elif loop_mode == "full":
        loop_start, loop_end = 0, total
    else:
        start_index = parameters.loop_start_phrase
        end_index = parameters.loop_end_phrase
        if start_index is None or end_index is None:
            raise GenerationInputError("range loop requires loop phrase boundaries")
        if not 0 <= start_index < end_index <= len(phrases):
            raise GenerationInputError("range loop phrase boundaries are outside the song")
        loop_start = phrases[start_index].start_tick
        loop_end = phrases[end_index - 1].end_tick

    result = CompositionStructure(
        context.metadata,
        parameters.ticks_per_beat,
        parameters.beats_per_measure,
        total,
        tuple(section.id for section in sections),
        tuple(sections),
        tuple(phrases),
        loop_mode,
        loop_start,
        loop_end,
    )
    validate_structure(result)
    return result


def validate_structure(structure: CompositionStructure) -> None:
    """Validate the contiguous logical timeline, references, and loop."""
    _positive_int(structure.ticks_per_beat, "ticks_per_beat")
    _positive_int(structure.beats_per_measure, "beats_per_measure")
    if structure.loop_mode not in LOOP_MODES:
        raise GenerationInputError("invalid loop mode")
    if not structure.sections or not structure.phrases:
        raise GenerationInputError("structure must contain sections and phrases")
    if len({item.id for item in structure.sections + structure.phrases}) != len(structure.sections) + len(structure.phrases):
        raise GenerationInputError("section and phrase IDs must be unique")
    cursor = 0
    phrase_ids = {phrase.id for phrase in structure.phrases}
    for section in structure.sections:
        if section.start_tick != cursor or section.duration_tick <= 0 or section.end_tick > structure.total_duration_tick:
            raise GenerationInputError("sections must form a contiguous positive timeline")
        if any(ref not in phrase_ids for ref in section.phrase_refs):
            raise GenerationInputError("section references an unknown phrase")
        section_phrases = [phrase for phrase in structure.phrases if phrase.section_ref == section.id]
        if tuple(phrase.id for phrase in section_phrases) != section.phrase_refs:
            raise GenerationInputError("phrase references must match section order")
        phrase_cursor = section.start_tick
        for phrase in section_phrases:
            if phrase.start_tick != phrase_cursor or phrase.duration_tick <= 0 or phrase.end_tick > section.end_tick:
                raise GenerationInputError("phrases must be contiguous inside a section")
            phrase_cursor = phrase.end_tick
        if phrase_cursor != section.end_tick:
            raise GenerationInputError("phrases must cover each section")
        cursor = section.end_tick
    if cursor != structure.total_duration_tick:
        raise GenerationInputError("last section must end at total duration")
    if structure.loop_mode == "none":
        if structure.loop_start_tick is not None or structure.loop_end_tick is not None:
            raise GenerationInputError("none loop must not have boundaries")
    else:
        start, end = structure.loop_start_tick, structure.loop_end_tick
        if start is None or end is None or not 0 <= start < end <= structure.total_duration_tick:
            raise GenerationInputError("loop boundaries are outside the song")
        if structure.loop_mode == "full" and (start != 0 or end != structure.total_duration_tick):
            raise GenerationInputError("full loop must cover the complete structure")


def _positive_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise GenerationInputError(f"{name} must be a positive integer")


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
