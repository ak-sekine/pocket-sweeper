"""Explicit candidate-generation profile for WBS-001-01593 evaluation.

This is an evaluation profile, not a Pocket Sweeper production default.
"""

from bgm_generator import (
    AccompanimentGenerationOptions, AccompanimentParameters, AccompanimentPatternDefinition,
    AccompanimentPatternStep, BassGenerationOptions, BassParameters, BassPatternDefinition,
    BassPatternStep, LayerAllocation, LogicalGenerationPlan, MelodyGenerationOptions,
    MelodyParameters, MotifDefinition, MotifStep, NoiseGenerationOptions, NoiseParameters,
    NoisePatternDefinition, NoisePatternStep, StructureGenerationOptions, StructureParameters,
)


def build_profile(seed):
    motifs = (
        MotifDefinition("motif-a", (MotifStep(2, absolute_pitch=0), MotifStep(2, rest=True))),
        MotifDefinition("motif-b", (MotifStep(2, absolute_pitch=1), MotifStep(2, rest=True))),
        MotifDefinition("motif-c", (MotifStep(2, absolute_pitch=2), MotifStep(2, rest=True))),
    )
    support = AccompanimentPatternDefinition(
        "support-a", "rhythmic_support", (AccompanimentPatternStep(2, absolute_pitch=0), AccompanimentPatternStep(2, rest=True))
    )
    bass = BassPatternDefinition(
        "bass-a", (BassPatternStep(2, bass_relation="root", absolute_pitch=0), BassPatternStep(2, rest=True))
    )
    noise = NoisePatternDefinition(
        "noise-a", (NoisePatternStep(2, role="beat_support", character_ref="low"), NoisePatternStep(2, rest=True))
    )
    plan = LogicalGenerationPlan(
        StructureParameters(4, 4, phrase_measures=1, section_phrase_counts=(2,), loop_mode="full"),
        StructureGenerationOptions(),
        MelodyParameters(),
        MelodyGenerationOptions(
            motif_definitions=motifs,
            motif_candidates_by_phrase=(("motif-a", "motif-b", "motif-c"), ("motif-a", "motif-b", "motif-c")),
            variation_candidates=("exact",),
        ),
        AccompanimentParameters(pattern_by_phrase=("support-a", "support-a"), variation_by_phrase=("exact", "exact")),
        AccompanimentGenerationOptions(pattern_definitions=(support,)),
        BassParameters(pattern_by_phrase=("bass-a", "bass-a"), variation_by_phrase=("exact", "exact")),
        BassGenerationOptions(pattern_definitions=(bass,)),
        NoiseParameters(pattern_by_phrase=("noise-a", "noise-a"), variation_by_phrase=("exact", "exact")),
        NoiseGenerationOptions(pattern_definitions=(noise,)),
    )
    return {
        "plan": plan,
        "logical_layers": lambda result: (result.melody,),
        "allocations": (LayerAllocation("melody-001", "CH1", ("pulse",)),),
        "title": "Generated Candidate Evaluation",
        "tempo": 120,
        "ticks_per_row": 1,
        "instrument_by_channel": {"CH1": 1},
        "instruments": ({"id": 1, "name": "candidate-pulse", "channel": "pulse1"},),
        "absolute_pitch_map": {0: "C4", 1: "D4", 2: "E4"},
        "noise_character_map": {"low": "C3"},
    }
