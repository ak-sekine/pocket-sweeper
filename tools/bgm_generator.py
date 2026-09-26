"""Deterministic random foundation for later BGM generators.

This module deliberately does not generate musical material.  It provides an
explicit-seed context and a small probe used by tests and later WBS tasks.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from numbers import Real
from typing import Mapping, Sequence, TypeVar


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


@dataclass(frozen=True)
class LogicalGenerationPlan:
    """Caller-owned inputs for a complete deterministic logical generation run."""

    structure_parameters: "StructureParameters"
    structure_options: "StructureGenerationOptions"
    melody_parameters: "MelodyParameters"
    melody_options: "MelodyGenerationOptions"
    accompaniment_parameters: "AccompanimentParameters"
    accompaniment_options: "AccompanimentGenerationOptions"
    bass_parameters: "BassParameters"
    bass_options: "BassGenerationOptions"
    noise_parameters: "NoiseParameters"
    noise_options: "NoiseGenerationOptions"


@dataclass(frozen=True)
class LogicalGenerationResult:
    seed: int
    generator_version: str
    structure: "CompositionStructure"
    melody: "MelodyLayer"
    accompaniment: "AccompanimentLayer"
    bass: "BassLayer"
    noise: "NoiseLayer"

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": {"seed": self.seed, "generator_version": self.generator_version},
            "structure": self.structure.as_dict(),
            "melody": self.melody.as_dict(),
            "accompaniment": self.accompaniment.as_dict(),
            "bass": self.bass.as_dict(),
            "noise": self.noise.as_dict(),
        }


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


@dataclass(frozen=True)
class MotifStep:
    duration_tick: int
    rest: bool = False
    relative_interval: int | None = None
    scale_degree: int | None = None
    absolute_pitch: int | None = None
    accent: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "relative_interval": self.relative_interval,
            "scale_degree": self.scale_degree,
            "absolute_pitch": self.absolute_pitch,
            "accent": self.accent,
        }


@dataclass(frozen=True)
class MotifDefinition:
    id: str
    steps: tuple[MotifStep, ...]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "steps": [step.as_dict() for step in self.steps], "rule_refs": list(self.rule_refs)}


@dataclass(frozen=True)
class MotifInstance:
    id: str
    motif_ref: str
    phrase_ref: str
    start_tick: int
    transformation: dict[str, object]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "motif_ref": self.motif_ref,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "transformation": dict(self.transformation),
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class MelodyEvent:
    id: str
    phrase_ref: str
    start_tick: int
    duration_tick: int
    rest: bool
    pitch_kind: str | None
    pitch_value: int | None
    motif_instance_ref: str
    accent: str | None = None
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "pitch_kind": self.pitch_kind,
            "pitch_value": self.pitch_value,
            "motif_instance_ref": self.motif_instance_ref,
            "accent": self.accent,
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class MelodyLayer:
    metadata: GenerationMetadata
    id: str
    motif_definitions: tuple[MotifDefinition, ...]
    motif_instances: tuple[MotifInstance, ...]
    events: tuple[MelodyEvent, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": self.metadata.as_dict(),
            "layer": {"id": self.id, "type": "melody", "physical_channel": None},
            "motif_definitions": [motif.as_dict() for motif in self.motif_definitions],
            "motif_instances": [instance.as_dict() for instance in self.motif_instances],
            "events": [event.as_dict() for event in self.events],
        }


@dataclass(frozen=True)
class MelodyParameters:
    motif_by_phrase: tuple[str, ...] | None = None
    variation_by_phrase: tuple[str, ...] | None = None
    variation_offsets_by_phrase: tuple[int, ...] | None = None


@dataclass(frozen=True)
class MelodyGenerationOptions:
    motif_definitions: tuple[MotifDefinition, ...] = ()
    motif_candidates_by_phrase: tuple[tuple[str, ...], ...] = ()
    variation_candidates: tuple[str, ...] = ()


def generate_melody(
    context: GenerationContext,
    structure: CompositionStructure,
    parameters: MelodyParameters | None = None,
    options: MelodyGenerationOptions | None = None,
) -> MelodyLayer:
    """Generate a logical, non-channel-bound melody from caller-owned motifs."""
    parameters = parameters or MelodyParameters()
    options = options or MelodyGenerationOptions()
    motifs = {motif.id: motif for motif in options.motif_definitions}
    if len(motifs) != len(options.motif_definitions) or not motifs:
        raise GenerationInputError("motif definitions must be non-empty and uniquely identified")
    phrases = structure.phrases
    motif_ids = parameters.motif_by_phrase
    if motif_ids is None:
        if len(options.motif_candidates_by_phrase) != len(phrases):
            raise GenerationInputError("motif candidates must cover every phrase")
        motif_ids = tuple(context.choice(candidates) for candidates in options.motif_candidates_by_phrase)
    if len(motif_ids) != len(phrases) or any(motif_id not in motifs for motif_id in motif_ids):
        raise GenerationInputError("motif_by_phrase must reference one motif per phrase")
    variations = parameters.variation_by_phrase
    if variations is None:
        if not options.variation_candidates:
            raise GenerationInputError("variation candidates are required when variations are not fixed")
        variations = tuple(context.choice(options.variation_candidates) for _ in phrases)
    if len(variations) != len(phrases) or any(variation not in ("exact", "relative_interval_offset") for variation in variations):
        raise GenerationInputError("unsupported or incomplete melody variation")

    instances: list[MotifInstance] = []
    events: list[MelodyEvent] = []
    for phrase, motif_id, variation in zip(phrases, motif_ids, variations):
        motif = motifs[motif_id]
        _validate_motif(motif)
        motif_duration = sum(step.duration_tick for step in motif.steps)
        if motif_duration > phrase.duration_tick:
            raise GenerationInputError("motif does not fit inside its phrase")
        instance_id = f"motif-instance-{len(instances) + 1:03d}"
        offset = 0
        transformation: dict[str, object] = {"type": variation}
        if variation == "relative_interval_offset":
            offsets = parameters.variation_offsets_by_phrase
            if offsets is None or len(offsets) != len(phrases):
                raise GenerationInputError("relative variation requires one offset per phrase")
            transformation["offset"] = offsets[len(instances)]
        instance = MotifInstance(instance_id, motif_id, phrase.id, phrase.start_tick, transformation)
        instances.append(instance)
        for step in motif.steps:
            if step.rest:
                kind = value = None
            elif step.relative_interval is not None:
                kind, value = "relative_interval", step.relative_interval + int(transformation.get("offset", 0))
            elif step.scale_degree is not None:
                kind, value = "scale_degree", step.scale_degree
            else:
                kind, value = "absolute_pitch", step.absolute_pitch
            events.append(MelodyEvent(
                f"melody-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                step.duration_tick, step.rest, kind, value, instance_id, step.accent,
            ))
            offset += step.duration_tick
        if offset < phrase.duration_tick:
            events.append(MelodyEvent(
                f"melody-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                phrase.duration_tick - offset, True, None, None, instance_id,
            ))
    layer = MelodyLayer(context.metadata, "melody-001", tuple(options.motif_definitions), tuple(instances), tuple(events))
    validate_melody(layer, structure)
    return layer


def _validate_motif(motif: MotifDefinition) -> None:
    if not motif.id or not motif.steps:
        raise GenerationInputError("motif must have an id and steps")
    for step in motif.steps:
        _positive_int(step.duration_tick, "motif step duration")
        values = [step.relative_interval, step.scale_degree, step.absolute_pitch]
        if step.rest and any(value is not None for value in values):
            raise GenerationInputError("rest step must not have pitch relation")
        if not step.rest and sum(value is not None for value in values) != 1:
            raise GenerationInputError("non-rest step must have exactly one pitch relation")


def validate_melody(layer: MelodyLayer, structure: CompositionStructure) -> None:
    motifs = {motif.id: motif for motif in layer.motif_definitions}
    instances = {instance.id: instance for instance in layer.motif_instances}
    phrases = {phrase.id: phrase for phrase in structure.phrases}
    if len(motifs) != len(layer.motif_definitions) or len(instances) != len(layer.motif_instances):
        raise GenerationInputError("melody IDs must be unique")
    event_ids: set[str] = set()
    previous_end: dict[str, int] = {}
    for instance in layer.motif_instances:
        if instance.motif_ref not in motifs or instance.phrase_ref not in phrases:
            raise GenerationInputError("motif instance reference is broken")
    for event in layer.events:
        if event.id in event_ids:
            raise GenerationInputError("melody event IDs must be unique")
        event_ids.add(event.id)
        if event.phrase_ref not in phrases or event.motif_instance_ref not in instances:
            raise GenerationInputError("melody event reference is broken")
        phrase = phrases[event.phrase_ref]
        if event.duration_tick <= 0 or event.start_tick < phrase.start_tick or event.start_tick + event.duration_tick > phrase.end_tick:
            raise GenerationInputError("melody event is outside its phrase")
        if event.rest and (event.pitch_kind is not None or event.pitch_value is not None):
            raise GenerationInputError("rest event must not have pitch relation")
        if not event.rest and (event.pitch_kind not in ("relative_interval", "scale_degree", "absolute_pitch") or event.pitch_value is None):
            raise GenerationInputError("pitched event must have one pitch relation")
        if event.phrase_ref in previous_end and event.start_tick < previous_end[event.phrase_ref]:
            raise GenerationInputError("melody events must not overlap within a phrase")
        previous_end[event.phrase_ref] = event.start_tick + event.duration_tick


ACCOMPANIMENT_REALIZATIONS = ("sustained_tone", "repeated_tone", "rhythmic_support")
ACCOMPANIMENT_VARIATIONS = ("exact", "relative_interval_offset")


@dataclass(frozen=True)
class AccompanimentPatternStep:
    duration_tick: int
    rest: bool = False
    relative_interval: int | None = None
    scale_degree: int | None = None
    absolute_pitch: int | None = None
    harmony_ref: str | None = None
    accent: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "relative_interval": self.relative_interval,
            "scale_degree": self.scale_degree,
            "absolute_pitch": self.absolute_pitch,
            "harmony_ref": self.harmony_ref,
            "accent": self.accent,
        }


@dataclass(frozen=True)
class AccompanimentPatternDefinition:
    id: str
    realization: str
    steps: tuple[AccompanimentPatternStep, ...]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "realization": self.realization, "steps": [step.as_dict() for step in self.steps], "rule_refs": list(self.rule_refs)}


@dataclass(frozen=True)
class AccompanimentPatternInstance:
    id: str
    pattern_ref: str
    phrase_ref: str
    start_tick: int
    transformation: dict[str, object]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "pattern_ref": self.pattern_ref,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "transformation": dict(self.transformation),
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class AccompanimentEvent:
    id: str
    phrase_ref: str
    start_tick: int
    duration_tick: int
    rest: bool
    pitch_kind: str | None
    pitch_value: int | None
    harmony_ref: str | None
    pattern_instance_ref: str
    accent: str | None = None
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "pitch_kind": self.pitch_kind,
            "pitch_value": self.pitch_value,
            "harmony_ref": self.harmony_ref,
            "pattern_instance_ref": self.pattern_instance_ref,
            "accent": self.accent,
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class AccompanimentLayer:
    metadata: GenerationMetadata
    id: str
    pattern_definitions: tuple[AccompanimentPatternDefinition, ...]
    pattern_instances: tuple[AccompanimentPatternInstance, ...]
    events: tuple[AccompanimentEvent, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": self.metadata.as_dict(),
            "layer": {"id": self.id, "type": "accompaniment", "physical_channel": None},
            "pattern_definitions": [pattern.as_dict() for pattern in self.pattern_definitions],
            "pattern_instances": [instance.as_dict() for instance in self.pattern_instances],
            "events": [event.as_dict() for event in self.events],
        }


@dataclass(frozen=True)
class AccompanimentParameters:
    pattern_by_phrase: tuple[str, ...] | None = None
    variation_by_phrase: tuple[str, ...] | None = None
    variation_offsets_by_phrase: tuple[int, ...] | None = None


@dataclass(frozen=True)
class AccompanimentGenerationOptions:
    pattern_definitions: tuple[AccompanimentPatternDefinition, ...] = ()
    pattern_candidates_by_phrase: tuple[tuple[str, ...], ...] = ()
    variation_candidates: tuple[str, ...] = ()
    harmony_refs: tuple[str, ...] = ()


def generate_accompaniment(
    context: GenerationContext,
    structure: CompositionStructure,
    parameters: AccompanimentParameters | None = None,
    options: AccompanimentGenerationOptions | None = None,
) -> AccompanimentLayer:
    """Generate a logical accompaniment voice without assigning a channel."""
    parameters = parameters or AccompanimentParameters()
    options = options or AccompanimentGenerationOptions()
    patterns = {pattern.id: pattern for pattern in options.pattern_definitions}
    if len(patterns) != len(options.pattern_definitions) or not patterns:
        raise GenerationInputError("pattern definitions must be non-empty and uniquely identified")
    phrases = structure.phrases
    pattern_ids = parameters.pattern_by_phrase
    if pattern_ids is None:
        if len(options.pattern_candidates_by_phrase) != len(phrases):
            raise GenerationInputError("pattern candidates must cover every phrase")
        pattern_ids = tuple(context.choice(candidates) for candidates in options.pattern_candidates_by_phrase)
    if len(pattern_ids) != len(phrases) or any(pattern_id not in patterns for pattern_id in pattern_ids):
        raise GenerationInputError("pattern_by_phrase must reference one pattern per phrase")
    variations = parameters.variation_by_phrase
    if variations is None:
        if not options.variation_candidates:
            raise GenerationInputError("variation candidates are required when variations are not fixed")
        variations = tuple(context.choice(options.variation_candidates) for _ in phrases)
    if len(variations) != len(phrases) or any(variation not in ACCOMPANIMENT_VARIATIONS for variation in variations):
        raise GenerationInputError("unsupported or incomplete accompaniment variation")

    instances: list[AccompanimentPatternInstance] = []
    events: list[AccompanimentEvent] = []
    for phrase, pattern_id, variation in zip(phrases, pattern_ids, variations):
        pattern = patterns[pattern_id]
        _validate_accompaniment_pattern(pattern, options.harmony_refs)
        pattern_duration = sum(step.duration_tick for step in pattern.steps)
        if pattern_duration > phrase.duration_tick:
            raise GenerationInputError("accompaniment pattern does not fit inside its phrase")
        instance_id = f"accompaniment-instance-{len(instances) + 1:03d}"
        transformation: dict[str, object] = {"type": variation}
        if variation == "relative_interval_offset":
            offsets = parameters.variation_offsets_by_phrase
            if offsets is None or len(offsets) != len(phrases):
                raise GenerationInputError("relative variation requires one offset per phrase")
            transformation["offset"] = offsets[len(instances)]
        instances.append(AccompanimentPatternInstance(instance_id, pattern_id, phrase.id, phrase.start_tick, transformation))
        offset = 0
        for step in pattern.steps:
            if step.rest:
                kind = value = None
            elif step.relative_interval is not None:
                kind, value = "relative_interval", step.relative_interval + int(transformation.get("offset", 0))
            elif step.scale_degree is not None:
                kind, value = "scale_degree", step.scale_degree
            else:
                kind, value = "absolute_pitch", step.absolute_pitch
            events.append(AccompanimentEvent(
                f"accompaniment-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                step.duration_tick, step.rest, kind, value, step.harmony_ref, instance_id, step.accent,
            ))
            offset += step.duration_tick
        if offset < phrase.duration_tick:
            events.append(AccompanimentEvent(
                f"accompaniment-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                phrase.duration_tick - offset, True, None, None, None, instance_id,
            ))
    layer = AccompanimentLayer(context.metadata, "accompaniment-001", tuple(options.pattern_definitions), tuple(instances), tuple(events))
    validate_accompaniment(layer, structure, options.harmony_refs)
    return layer


def _validate_accompaniment_pattern(pattern: AccompanimentPatternDefinition, harmony_refs: tuple[str, ...]) -> None:
    if not pattern.id or pattern.realization not in ACCOMPANIMENT_REALIZATIONS or not pattern.steps:
        raise GenerationInputError("unsupported or incomplete accompaniment pattern")
    for step in pattern.steps:
        _positive_int(step.duration_tick, "accompaniment step duration")
        values = [step.relative_interval, step.scale_degree, step.absolute_pitch]
        if step.rest and (any(value is not None for value in values) or step.harmony_ref is not None):
            raise GenerationInputError("rest accompaniment step must not have pitch relation")
        if not step.rest and sum(value is not None for value in values) != 1:
            raise GenerationInputError("accompaniment step must have exactly one pitch relation")
        if step.harmony_ref is not None and step.harmony_ref not in harmony_refs:
            raise GenerationInputError("accompaniment harmony_ref is not available")


def validate_accompaniment(layer: AccompanimentLayer, structure: CompositionStructure, harmony_refs: tuple[str, ...] = ()) -> None:
    patterns = {pattern.id: pattern for pattern in layer.pattern_definitions}
    instances = {instance.id: instance for instance in layer.pattern_instances}
    phrases = {phrase.id: phrase for phrase in structure.phrases}
    if len(patterns) != len(layer.pattern_definitions) or len(instances) != len(layer.pattern_instances):
        raise GenerationInputError("accompaniment IDs must be unique")
    for instance in layer.pattern_instances:
        if instance.pattern_ref not in patterns or instance.phrase_ref not in phrases:
            raise GenerationInputError("accompaniment instance reference is broken")
    event_ids: set[str] = set()
    previous_end: dict[str, int] = {}
    for event in layer.events:
        if event.id in event_ids:
            raise GenerationInputError("accompaniment event IDs must be unique")
        event_ids.add(event.id)
        if event.phrase_ref not in phrases or event.pattern_instance_ref not in instances:
            raise GenerationInputError("accompaniment event reference is broken")
        instance = instances[event.pattern_instance_ref]
        if instance.phrase_ref != event.phrase_ref:
            raise GenerationInputError("accompaniment event and instance phrase differ")
        phrase = phrases[event.phrase_ref]
        if event.duration_tick <= 0 or event.start_tick < phrase.start_tick or event.start_tick + event.duration_tick > phrase.end_tick:
            raise GenerationInputError("accompaniment event is outside its phrase")
        if event.harmony_ref is not None and event.harmony_ref not in harmony_refs:
            raise GenerationInputError("accompaniment event harmony_ref is not available")
        if event.rest and (event.pitch_kind is not None or event.pitch_value is not None or event.harmony_ref is not None):
            raise GenerationInputError("rest accompaniment event must not have pitch relation")
        if not event.rest and (event.pitch_kind not in ("relative_interval", "scale_degree", "absolute_pitch") or event.pitch_value is None):
            raise GenerationInputError("pitched accompaniment event must have one pitch relation")
        if event.phrase_ref in previous_end and event.start_tick < previous_end[event.phrase_ref]:
            raise GenerationInputError("accompaniment events must not overlap within a phrase")
        previous_end[event.phrase_ref] = event.start_tick + event.duration_tick


BASS_RELATIONS = ("root", "chord_tone", "passing", "pedal", "ostinato")


@dataclass(frozen=True)
class BassPatternStep:
    duration_tick: int
    rest: bool = False
    bass_relation: str | None = None
    relative_interval: int | None = None
    scale_degree: int | None = None
    absolute_pitch: int | None = None
    harmony_ref: str | None = None
    accent: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "bass_relation": self.bass_relation,
            "relative_interval": self.relative_interval,
            "scale_degree": self.scale_degree,
            "absolute_pitch": self.absolute_pitch,
            "harmony_ref": self.harmony_ref,
            "accent": self.accent,
        }


@dataclass(frozen=True)
class BassPatternDefinition:
    id: str
    steps: tuple[BassPatternStep, ...]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "steps": [step.as_dict() for step in self.steps], "rule_refs": list(self.rule_refs)}


@dataclass(frozen=True)
class BassPatternInstance:
    id: str
    pattern_ref: str
    phrase_ref: str
    start_tick: int
    transformation: dict[str, object]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "pattern_ref": self.pattern_ref,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "transformation": dict(self.transformation),
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class BassEvent:
    id: str
    phrase_ref: str
    start_tick: int
    duration_tick: int
    rest: bool
    bass_relation: str | None
    pitch_kind: str | None
    pitch_value: int | None
    harmony_ref: str | None
    pattern_instance_ref: str
    accent: str | None = None
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "bass_relation": self.bass_relation,
            "pitch_kind": self.pitch_kind,
            "pitch_value": self.pitch_value,
            "harmony_ref": self.harmony_ref,
            "pattern_instance_ref": self.pattern_instance_ref,
            "accent": self.accent,
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class BassLayer:
    metadata: GenerationMetadata
    id: str
    pattern_definitions: tuple[BassPatternDefinition, ...]
    pattern_instances: tuple[BassPatternInstance, ...]
    events: tuple[BassEvent, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": self.metadata.as_dict(),
            "layer": {"id": self.id, "type": "bass", "physical_channel": None},
            "pattern_definitions": [pattern.as_dict() for pattern in self.pattern_definitions],
            "pattern_instances": [instance.as_dict() for instance in self.pattern_instances],
            "events": [event.as_dict() for event in self.events],
        }


@dataclass(frozen=True)
class BassParameters:
    pattern_by_phrase: tuple[str, ...] | None = None
    variation_by_phrase: tuple[str, ...] | None = None
    variation_offsets_by_phrase: tuple[int, ...] | None = None


@dataclass(frozen=True)
class BassGenerationOptions:
    pattern_definitions: tuple[BassPatternDefinition, ...] = ()
    pattern_candidates_by_phrase: tuple[tuple[str, ...], ...] = ()
    variation_candidates: tuple[str, ...] = ()
    harmony_refs: tuple[str, ...] = ()


def generate_bass(
    context: GenerationContext,
    structure: CompositionStructure,
    parameters: BassParameters | None = None,
    options: BassGenerationOptions | None = None,
) -> BassLayer:
    """Generate a logical bass voice without assigning a Game Boy channel."""
    parameters = parameters or BassParameters()
    options = options or BassGenerationOptions()
    patterns = {pattern.id: pattern for pattern in options.pattern_definitions}
    if len(patterns) != len(options.pattern_definitions) or not patterns:
        raise GenerationInputError("bass pattern definitions must be non-empty and unique")
    phrases = structure.phrases
    pattern_ids = parameters.pattern_by_phrase
    if pattern_ids is None:
        if len(options.pattern_candidates_by_phrase) != len(phrases):
            raise GenerationInputError("bass pattern candidates must cover every phrase")
        pattern_ids = tuple(context.choice(candidates) for candidates in options.pattern_candidates_by_phrase)
    if len(pattern_ids) != len(phrases) or any(pattern_id not in patterns for pattern_id in pattern_ids):
        raise GenerationInputError("bass pattern_by_phrase has an invalid reference")
    variations = parameters.variation_by_phrase
    if variations is None:
        if not options.variation_candidates:
            raise GenerationInputError("bass variation candidates are required")
        variations = tuple(context.choice(options.variation_candidates) for _ in phrases)
    if len(variations) != len(phrases) or any(variation not in ACCOMPANIMENT_VARIATIONS for variation in variations):
        raise GenerationInputError("unsupported or incomplete bass variation")

    instances: list[BassPatternInstance] = []
    events: list[BassEvent] = []
    for phrase, pattern_id, variation in zip(phrases, pattern_ids, variations):
        pattern = patterns[pattern_id]
        _validate_bass_pattern(pattern, options.harmony_refs)
        pattern_duration = sum(step.duration_tick for step in pattern.steps)
        if pattern_duration > phrase.duration_tick:
            raise GenerationInputError("bass pattern does not fit inside its phrase")
        instance_id = f"bass-instance-{len(instances) + 1:03d}"
        transformation: dict[str, object] = {"type": variation}
        if variation == "relative_interval_offset":
            offsets = parameters.variation_offsets_by_phrase
            if offsets is None or len(offsets) != len(phrases):
                raise GenerationInputError("relative bass variation requires one offset per phrase")
            transformation["offset"] = offsets[len(instances)]
        instances.append(BassPatternInstance(instance_id, pattern_id, phrase.id, phrase.start_tick, transformation))
        offset = 0
        for step in pattern.steps:
            if step.rest:
                kind = value = relation = None
            elif step.relative_interval is not None:
                kind, value, relation = "relative_interval", step.relative_interval + int(transformation.get("offset", 0)), step.bass_relation
            elif step.scale_degree is not None:
                kind, value, relation = "scale_degree", step.scale_degree, step.bass_relation
            else:
                kind, value, relation = "absolute_pitch", step.absolute_pitch, step.bass_relation
            events.append(BassEvent(
                f"bass-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                step.duration_tick, step.rest, relation, kind, value, step.harmony_ref, instance_id, step.accent,
            ))
            offset += step.duration_tick
        if offset < phrase.duration_tick:
            events.append(BassEvent(
                f"bass-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                phrase.duration_tick - offset, True, None, None, None, None, instance_id,
            ))
    layer = BassLayer(context.metadata, "bass-001", tuple(options.pattern_definitions), tuple(instances), tuple(events))
    validate_bass(layer, structure, options.harmony_refs)
    return layer


def _validate_bass_pattern(pattern: BassPatternDefinition, harmony_refs: tuple[str, ...]) -> None:
    if not pattern.id or not pattern.steps:
        raise GenerationInputError("bass pattern must have an id and steps")
    for step in pattern.steps:
        _positive_int(step.duration_tick, "bass step duration")
        values = [step.relative_interval, step.scale_degree, step.absolute_pitch]
        if step.rest:
            if any(value is not None for value in values) or step.bass_relation is not None or step.harmony_ref is not None:
                raise GenerationInputError("rest bass step must not have relation or pitch")
        else:
            if sum(value is not None for value in values) != 1:
                raise GenerationInputError("bass step must have exactly one pitch relation")
            if step.bass_relation is not None and step.bass_relation not in BASS_RELATIONS:
                raise GenerationInputError("unsupported bass relation")
            if step.harmony_ref is not None and step.harmony_ref not in harmony_refs:
                raise GenerationInputError("bass harmony_ref is not available")


def validate_bass(layer: BassLayer, structure: CompositionStructure, harmony_refs: tuple[str, ...] = ()) -> None:
    patterns = {pattern.id: pattern for pattern in layer.pattern_definitions}
    instances = {instance.id: instance for instance in layer.pattern_instances}
    phrases = {phrase.id: phrase for phrase in structure.phrases}
    if len(patterns) != len(layer.pattern_definitions) or len(instances) != len(layer.pattern_instances):
        raise GenerationInputError("bass IDs must be unique")
    for instance in layer.pattern_instances:
        if instance.pattern_ref not in patterns or instance.phrase_ref not in phrases:
            raise GenerationInputError("bass instance reference is broken")
    event_ids: set[str] = set()
    previous_end: dict[str, int] = {}
    for event in layer.events:
        if event.id in event_ids:
            raise GenerationInputError("bass event IDs must be unique")
        event_ids.add(event.id)
        if event.phrase_ref not in phrases or event.pattern_instance_ref not in instances:
            raise GenerationInputError("bass event reference is broken")
        instance = instances[event.pattern_instance_ref]
        if instance.phrase_ref != event.phrase_ref:
            raise GenerationInputError("bass event and instance phrase differ")
        phrase = phrases[event.phrase_ref]
        if event.duration_tick <= 0 or event.start_tick < phrase.start_tick or event.start_tick + event.duration_tick > phrase.end_tick:
            raise GenerationInputError("bass event is outside its phrase")
        if event.harmony_ref is not None and event.harmony_ref not in harmony_refs:
            raise GenerationInputError("bass event harmony_ref is not available")
        if event.rest and any(value is not None for value in (event.bass_relation, event.pitch_kind, event.pitch_value, event.harmony_ref)):
            raise GenerationInputError("rest bass event must not have relation or pitch")
        if not event.rest:
            if event.bass_relation is not None and event.bass_relation not in BASS_RELATIONS:
                raise GenerationInputError("unsupported bass relation")
            if event.pitch_kind not in ("relative_interval", "scale_degree", "absolute_pitch") or event.pitch_value is None:
                raise GenerationInputError("pitched bass event must have one pitch relation")
        if event.phrase_ref in previous_end and event.start_tick < previous_end[event.phrase_ref]:
            raise GenerationInputError("bass events must not overlap within a phrase")
        previous_end[event.phrase_ref] = event.start_tick + event.duration_tick


NOISE_VARIATIONS = ("exact",)


@dataclass(frozen=True)
class NoisePatternStep:
    duration_tick: int
    rest: bool = False
    role: str | None = None
    character_ref: str | None = None
    accent: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "role": self.role,
            "character_ref": self.character_ref,
            "accent": self.accent,
        }


@dataclass(frozen=True)
class NoisePatternDefinition:
    id: str
    steps: tuple[NoisePatternStep, ...]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "steps": [step.as_dict() for step in self.steps], "rule_refs": list(self.rule_refs)}


@dataclass(frozen=True)
class NoisePatternInstance:
    id: str
    pattern_ref: str
    phrase_ref: str
    start_tick: int
    transformation: dict[str, object]
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "pattern_ref": self.pattern_ref,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "transformation": dict(self.transformation),
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class NoiseEvent:
    id: str
    phrase_ref: str
    start_tick: int
    duration_tick: int
    rest: bool
    role: str | None
    character_ref: str | None
    pattern_instance_ref: str
    accent: str | None = None
    rule_refs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "phrase_ref": self.phrase_ref,
            "start_tick": self.start_tick,
            "duration_tick": self.duration_tick,
            "rest": self.rest,
            "role": self.role,
            "character_ref": self.character_ref,
            "pattern_instance_ref": self.pattern_instance_ref,
            "accent": self.accent,
            "rule_refs": list(self.rule_refs),
        }


@dataclass(frozen=True)
class NoiseLayer:
    metadata: GenerationMetadata
    id: str
    pattern_definitions: tuple[NoisePatternDefinition, ...]
    pattern_instances: tuple[NoisePatternInstance, ...]
    events: tuple[NoiseEvent, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "metadata": self.metadata.as_dict(),
            "layer": {"id": self.id, "type": "noise_percussion", "physical_channel": None},
            "pattern_definitions": [pattern.as_dict() for pattern in self.pattern_definitions],
            "pattern_instances": [instance.as_dict() for instance in self.pattern_instances],
            "events": [event.as_dict() for event in self.events],
        }


@dataclass(frozen=True)
class NoiseParameters:
    pattern_by_phrase: tuple[str, ...] | None = None
    variation_by_phrase: tuple[str, ...] | None = None


@dataclass(frozen=True)
class NoiseGenerationOptions:
    pattern_definitions: tuple[NoisePatternDefinition, ...] = ()
    pattern_candidates_by_phrase: tuple[tuple[str, ...], ...] = ()
    variation_candidates: tuple[str, ...] = ()


def generate_noise(
    context: GenerationContext,
    structure: CompositionStructure,
    parameters: NoiseParameters | None = None,
    options: NoiseGenerationOptions | None = None,
) -> NoiseLayer:
    """Generate logical rhythm/noise events without CH4 or NR43 semantics."""
    parameters = parameters or NoiseParameters()
    options = options or NoiseGenerationOptions()
    patterns = {pattern.id: pattern for pattern in options.pattern_definitions}
    if len(patterns) != len(options.pattern_definitions) or not patterns:
        raise GenerationInputError("noise pattern definitions must be non-empty and unique")
    phrases = structure.phrases
    pattern_ids = parameters.pattern_by_phrase
    if pattern_ids is None:
        if len(options.pattern_candidates_by_phrase) != len(phrases):
            raise GenerationInputError("noise pattern candidates must cover every phrase")
        pattern_ids = tuple(context.choice(candidates) for candidates in options.pattern_candidates_by_phrase)
    if len(pattern_ids) != len(phrases) or any(pattern_id not in patterns for pattern_id in pattern_ids):
        raise GenerationInputError("noise pattern_by_phrase has an invalid reference")
    variations = parameters.variation_by_phrase
    if variations is None:
        if not options.variation_candidates:
            raise GenerationInputError("noise variation candidates are required")
        variations = tuple(context.choice(options.variation_candidates) for _ in phrases)
    if len(variations) != len(phrases) or any(variation not in NOISE_VARIATIONS for variation in variations):
        raise GenerationInputError("unsupported or incomplete noise variation")

    instances: list[NoisePatternInstance] = []
    events: list[NoiseEvent] = []
    for phrase, pattern_id, variation in zip(phrases, pattern_ids, variations):
        pattern = patterns[pattern_id]
        _validate_noise_pattern(pattern)
        pattern_duration = sum(step.duration_tick for step in pattern.steps)
        if pattern_duration > phrase.duration_tick:
            raise GenerationInputError("noise pattern does not fit inside its phrase")
        instance_id = f"noise-instance-{len(instances) + 1:03d}"
        instances.append(NoisePatternInstance(instance_id, pattern_id, phrase.id, phrase.start_tick, {"type": variation}))
        offset = 0
        for step in pattern.steps:
            if step.rest:
                role = character = accent = None
            else:
                role, character, accent = step.role, step.character_ref, step.accent
            events.append(NoiseEvent(
                f"noise-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                step.duration_tick, step.rest, role, character, instance_id, accent,
            ))
            offset += step.duration_tick
        if offset < phrase.duration_tick:
            events.append(NoiseEvent(
                f"noise-event-{len(events) + 1:03d}", phrase.id, phrase.start_tick + offset,
                phrase.duration_tick - offset, True, None, None, instance_id,
            ))
    layer = NoiseLayer(context.metadata, "noise-percussion-001", tuple(options.pattern_definitions), tuple(instances), tuple(events))
    validate_noise(layer, structure)
    return layer


def _validate_noise_pattern(pattern: NoisePatternDefinition) -> None:
    if not pattern.id or not pattern.steps:
        raise GenerationInputError("noise pattern must have an id and steps")
    for step in pattern.steps:
        _positive_int(step.duration_tick, "noise step duration")
        if step.rest and any(value is not None for value in (step.role, step.character_ref, step.accent)):
            raise GenerationInputError("rest noise step must not have role, character, or accent")
        if not step.rest and not step.role:
            raise GenerationInputError("noise hit must have a logical role")


def validate_noise(layer: NoiseLayer, structure: CompositionStructure) -> None:
    patterns = {pattern.id: pattern for pattern in layer.pattern_definitions}
    instances = {instance.id: instance for instance in layer.pattern_instances}
    phrases = {phrase.id: phrase for phrase in structure.phrases}
    if len(patterns) != len(layer.pattern_definitions) or len(instances) != len(layer.pattern_instances):
        raise GenerationInputError("noise IDs must be unique")
    for instance in layer.pattern_instances:
        if instance.pattern_ref not in patterns or instance.phrase_ref not in phrases:
            raise GenerationInputError("noise instance reference is broken")
    event_ids: set[str] = set()
    previous_end: dict[str, int] = {}
    for event in layer.events:
        if event.id in event_ids:
            raise GenerationInputError("noise event IDs must be unique")
        event_ids.add(event.id)
        if event.phrase_ref not in phrases or event.pattern_instance_ref not in instances:
            raise GenerationInputError("noise event reference is broken")
        instance = instances[event.pattern_instance_ref]
        if instance.phrase_ref != event.phrase_ref:
            raise GenerationInputError("noise event and instance phrase differ")
        phrase = phrases[event.phrase_ref]
        if event.duration_tick <= 0 or event.start_tick < phrase.start_tick or event.start_tick + event.duration_tick > phrase.end_tick:
            raise GenerationInputError("noise event is outside its phrase")
        if event.rest and any(value is not None for value in (event.role, event.character_ref, event.accent)):
            raise GenerationInputError("rest noise event must not have role, character, or accent")
        if not event.rest and not event.role:
            raise GenerationInputError("noise hit must have a logical role")
        if event.phrase_ref in previous_end and event.start_tick < previous_end[event.phrase_ref]:
            raise GenerationInputError("noise events must not overlap within a phrase")
        previous_end[event.phrase_ref] = event.start_tick + event.duration_tick


PHYSICAL_CHANNELS = ("CH1", "CH2", "CH3", "CH4")
CHANNEL_CAPABILITIES = {
    "CH1": frozenset(("pulse", "sweep")),
    "CH2": frozenset(("pulse",)),
    "CH3": frozenset(("wave",)),
    "CH4": frozenset(("noise",)),
}
DEGRADATION_POLICIES = ("required", "temporarily_degradable", "optional")


@dataclass(frozen=True)
class LayerAllocation:
    logical_layer_ref: str
    physical_channel: str
    required_capabilities: tuple[str, ...] = ()
    degradation_policy: str = "required"
    structural_role: str | None = None
    rule_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class SfxOccupancy:
    sfx_id: str
    physical_channel: str
    temporary: bool = True
    mute_bgm_channel: bool = True
    implemented: bool = True
    recovery: str = "resume_current_position"


@dataclass(frozen=True)
class AllocationValidation:
    valid: bool
    machine_violations: tuple[str, ...] = ()
    human_review_items: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "machine_violations": list(self.machine_violations),
            "human_review_items": list(self.human_review_items),
            "notes": list(self.notes),
        }


def validate_game_boy_allocation(
    logical_layers: Sequence[object],
    allocations: Sequence[LayerAllocation],
    sfx_occupancies: Sequence[SfxOccupancy] = (),
    timeline_continues_during_sfx: bool = True,
) -> AllocationValidation:
    """Check allocation and known SFX preemption without judging sound quality."""
    layer_ids = [getattr(layer, "id", None) for layer in logical_layers]
    violations: list[str] = []
    review: list[str] = []
    notes: list[str] = []
    if any(not layer_id for layer_id in layer_ids) or len(set(layer_ids)) != len(layer_ids):
        violations.append("logical layer IDs must be present and unique")
    known_layers = set(layer_ids)
    if len(allocations) > len(PHYSICAL_CHANNELS):
        violations.append("physical allocation exceeds four channels")
    seen_layers: set[str] = set()
    seen_channels: set[str] = set()
    for allocation in allocations:
        if allocation.logical_layer_ref not in known_layers:
            violations.append(f"unknown logical layer: {allocation.logical_layer_ref}")
        if allocation.logical_layer_ref in seen_layers:
            violations.append(f"logical layer allocated more than once: {allocation.logical_layer_ref}")
        seen_layers.add(allocation.logical_layer_ref)
        if allocation.physical_channel not in CHANNEL_CAPABILITIES:
            violations.append(f"unknown physical channel: {allocation.physical_channel}")
            continue
        if allocation.physical_channel in seen_channels:
            violations.append(f"exclusive physical channel conflict: {allocation.physical_channel}")
        seen_channels.add(allocation.physical_channel)
        if allocation.degradation_policy not in DEGRADATION_POLICIES:
            violations.append(f"invalid degradation policy: {allocation.degradation_policy}")
        missing = set(allocation.required_capabilities) - CHANNEL_CAPABILITIES[allocation.physical_channel]
        if missing:
            violations.append(f"channel {allocation.physical_channel} lacks capabilities: {sorted(missing)}")

    occupied = {occupancy.physical_channel for occupancy in sfx_occupancies if occupancy.implemented}
    for occupancy in sfx_occupancies:
        if occupancy.physical_channel not in CHANNEL_CAPABILITIES:
            violations.append(f"unknown SFX physical channel: {occupancy.physical_channel}")
        if occupancy.recovery != "resume_current_position":
            notes.append(f"recovery policy is not the current implementation contract: {occupancy.sfx_id}")
        if not occupancy.implemented:
            notes.append(f"SFX is a future/unimplemented occupancy: {occupancy.sfx_id}")
    for allocation in allocations:
        if allocation.physical_channel not in occupied:
            continue
        if allocation.degradation_policy == "required":
            violations.append(f"required layer preempted by SFX: {allocation.logical_layer_ref}")
        else:
            review.append(f"temporary SFX loss requires listening review: {allocation.logical_layer_ref}")
    if not timeline_continues_during_sfx:
        violations.append("BGM timeline must continue during SFX occupancy")
    if occupied:
        notes.append("SFX mute affects the channel while the BGM timeline continues")
    notes.append("machine-valid allocation does not establish musical quality")
    return AllocationValidation(not violations, tuple(violations), tuple(review), tuple(notes))


@dataclass(frozen=True)
class GameBoyConversionInput:
    structure: CompositionStructure
    logical_layers: tuple[object, ...]
    allocations: tuple[LayerAllocation, ...]
    title: str
    tempo: int
    ticks_per_row: int
    instrument_by_channel: Mapping[str, int]
    instruments: tuple[dict[str, object], ...]
    absolute_pitch_map: Mapping[int, str]
    noise_character_map: Mapping[str, str]
    sfx_occupancies: tuple[SfxOccupancy, ...] = ()
    timeline_continues_during_sfx: bool = True


def convert_to_json_v2(input_data: GameBoyConversionInput) -> dict[str, object]:
    """Adapt resolved logical layers to the existing Version 2 JSON contract."""
    if not input_data.title or not isinstance(input_data.title, str):
        raise GenerationInputError("title must be a non-empty string")
    _positive_int(input_data.tempo, "tempo")
    _positive_int(input_data.ticks_per_row, "ticks_per_row")
    validation = validate_game_boy_allocation(
        input_data.logical_layers,
        input_data.allocations,
        input_data.sfx_occupancies,
        input_data.timeline_continues_during_sfx,
    )
    if not validation.valid:
        raise GenerationInputError("allocation validation failed: " + "; ".join(validation.machine_violations))
    if not input_data.instruments:
        raise GenerationInputError("caller-supplied instruments are required")
    if set(input_data.instrument_by_channel) - set(PHYSICAL_CHANNELS):
        raise GenerationInputError("instrument mapping contains an unknown channel")
    instrument_channels = {
        item.get("id"): item.get("channel")
        for item in input_data.instruments
        if isinstance(item, dict)
    }

    layer_by_id = {getattr(layer, "id", None): layer for layer in input_data.logical_layers}
    allocation_by_channel = {allocation.physical_channel: allocation for allocation in input_data.allocations}
    channel_names = {"CH1": "pulse1", "CH2": "pulse2", "CH3": "wave", "CH4": "noise"}
    sections = input_data.structure.sections
    patterns: dict[str, dict[str, list[dict[str, object]]]] = {}
    orders: dict[str, list[str]] = {}
    for physical_channel, allocation in allocation_by_channel.items():
        if physical_channel not in input_data.instrument_by_channel:
            raise GenerationInputError(f"missing instrument mapping for {physical_channel}")
        channel = channel_names[physical_channel]
        layer = layer_by_id.get(allocation.logical_layer_ref)
        if layer is None or not hasattr(layer, "events"):
            raise GenerationInputError(f"allocation layer is not convertible: {allocation.logical_layer_ref}")
        instrument_id = input_data.instrument_by_channel[physical_channel]
        if not isinstance(instrument_id, int) or isinstance(instrument_id, bool) or instrument_id <= 0:
            raise GenerationInputError("instrument IDs must be positive integers")
        if instrument_channels.get(instrument_id) != channel:
            raise GenerationInputError(f"instrument {instrument_id} is not defined for {channel}")
        channel_patterns: dict[str, list[dict[str, object]]] = {}
        for section in sections:
            section_ticks = section.duration_tick
            if section_ticks % input_data.ticks_per_row:
                raise GenerationInputError("section duration is not exactly representable in rows")
            row_count = section_ticks // input_data.ticks_per_row
            if row_count <= 0 or row_count > 64:
                raise GenerationInputError("each output pattern must contain 1..64 rows")
            events = [event for event in layer.events if getattr(event, "phrase_ref", None) in section.phrase_refs]
            events.sort(key=lambda event: event.start_tick)
            channel_patterns[section.id] = _events_to_json_notes(
                events, section.start_tick, section.end_tick, input_data.ticks_per_row,
                instrument_id, input_data.absolute_pitch_map, input_data.noise_character_map,
                channel,
            )
        patterns[channel] = channel_patterns
        orders[channel] = [section.id for section in sections]

    if not orders:
        raise GenerationInputError("at least one allocated channel is required")
    loop = _logical_loop_to_json(input_data.structure, sections)
    result: dict[str, object] = {
        "version": 2,
        "title": input_data.title,
        "type": "bgm",
        "tempo": input_data.tempo,
        "loop": loop,
        "instruments": list(input_data.instruments),
        "order": orders,
        "patterns": patterns,
    }
    return result


def _events_to_json_notes(
    events: Sequence[object],
    section_start: int,
    section_end: int,
    ticks_per_row: int,
    instrument_id: int,
    absolute_pitch_map: Mapping[int, str],
    noise_character_map: Mapping[str, str],
    channel: str,
) -> list[dict[str, object]]:
    notes: list[dict[str, object]] = []
    cursor = section_start
    for event in events:
        start = getattr(event, "start_tick", None)
        duration = getattr(event, "duration_tick", None)
        if not isinstance(start, int) or not isinstance(duration, int) or start < cursor or start + duration > section_end:
            raise GenerationInputError("event is outside section or overlaps another event")
        if start % ticks_per_row or duration % ticks_per_row:
            raise GenerationInputError("event timing is not exactly representable in rows")
        if start > cursor:
            notes.append({"note": "rest", "length": (start - cursor) // ticks_per_row, "instrument": instrument_id})
        length = duration // ticks_per_row
        if length <= 0:
            raise GenerationInputError("event duration must produce at least one row")
        if getattr(event, "rest", False):
            note = "rest"
        elif channel == "noise":
            character = getattr(event, "character_ref", None)
            if character not in noise_character_map:
                raise GenerationInputError("Noise character requires caller-supplied note mapping")
            note = noise_character_map[character]
        else:
            if getattr(event, "pitch_kind", None) != "absolute_pitch":
                raise GenerationInputError("unresolved pitch relation cannot be converted")
            pitch = getattr(event, "pitch_value", None)
            if pitch not in absolute_pitch_map:
                raise GenerationInputError("absolute pitch requires caller-supplied note mapping")
            note = absolute_pitch_map[pitch]
        notes.append({"note": note, "length": length, "instrument": instrument_id})
        cursor = start + duration
    if cursor < section_end:
        notes.append({"note": "rest", "length": (section_end - cursor) // ticks_per_row, "instrument": instrument_id})
    return notes


def _logical_loop_to_json(structure: CompositionStructure, sections: Sequence[Section]) -> dict[str, object]:
    mode = structure.loop_mode
    if mode == "none":
        return {"mode": "none"}
    if mode == "full":
        return {"mode": "full"}
    if structure.loop_start_tick is None or structure.loop_end_tick != structure.total_duration_tick:
        raise GenerationInputError("Version 2 range loop requires a loop ending at song end")
    starts = [section.start_tick for section in sections]
    if structure.loop_start_tick not in starts:
        raise GenerationInputError("range loop start must align to an order boundary")
    return {"mode": "range", "start_order": starts.index(structure.loop_start_tick), "end_order": len(sections)}


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


def generate_logical_composition(seed: int, plan: LogicalGenerationPlan) -> LogicalGenerationResult:
    """Generate all logical layers from one master seed and one shared stream."""
    context = GenerationContext(seed)
    structure = generate_structure(context, plan.structure_parameters, plan.structure_options)
    melody = generate_melody(context, structure, plan.melody_parameters, plan.melody_options)
    accompaniment = generate_accompaniment(
        context, structure, plan.accompaniment_parameters, plan.accompaniment_options
    )
    bass = generate_bass(context, structure, plan.bass_parameters, plan.bass_options)
    noise = generate_noise(context, structure, plan.noise_parameters, plan.noise_options)
    return LogicalGenerationResult(seed, GENERATOR_VERSION, structure, melody, accompaniment, bass, noise)
