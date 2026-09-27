"""Evaluation-only profile for Human BGM quality review.

This is not a Pocket Sweeper production composition rule or default, and it is
not the minimum pipeline fixture.  Its explicit layer coverage and parameter
values exist only to give WBS-001-01677 observable material.
"""

from bgm_generator import (
    AccompanimentGenerationOptions, AccompanimentParameters, AccompanimentPatternDefinition,
    AccompanimentPatternStep, BassGenerationOptions, BassParameters, BassPatternDefinition,
    BassPatternStep, LayerAllocation, LogicalGenerationPlan, MelodyGenerationOptions,
    MelodyParameters, MotifDefinition, MotifStep, NoiseGenerationOptions, NoiseParameters,
    NoisePatternDefinition, NoisePatternStep, StructureGenerationOptions, StructureParameters,
)


PROFILE_PURPOSE = "human_bgm_quality_evaluation"
PROFILE_SCOPE = "evaluation_only_not_production_default_or_pipeline_fixture"


def build_profile(seed):
    """Return explicit evaluation inputs; values are not production defaults."""
    motifs = (
        MotifDefinition("motif-a", (MotifStep(2, absolute_pitch=0), MotifStep(2, rest=True))),
        MotifDefinition("motif-b", (MotifStep(2, absolute_pitch=1), MotifStep(2, rest=True))),
        MotifDefinition("motif-c", (MotifStep(2, absolute_pitch=2), MotifStep(2, rest=True))),
    )
    support = AccompanimentPatternDefinition(
        "support-a", "rhythmic_support",
        (AccompanimentPatternStep(2, absolute_pitch=0), AccompanimentPatternStep(2, rest=True)),
    )
    bass = BassPatternDefinition(
        "bass-a", (BassPatternStep(2, bass_relation="root", absolute_pitch=0), BassPatternStep(2, rest=True))
    )
    noise = NoisePatternDefinition(
        "noise-a", (NoisePatternStep(2, role="beat_support", character_ref="low"), NoisePatternStep(2, rest=True))
    )
    plan = LogicalGenerationPlan(
        StructureParameters(4, 4, phrase_measures=1, section_phrase_counts=(2, 2), loop_mode="full"),
        StructureGenerationOptions(),
        MelodyParameters(),
        MelodyGenerationOptions(
            motif_definitions=motifs,
            motif_candidates_by_phrase=(
                ("motif-a", "motif-b", "motif-c"),
                ("motif-a", "motif-b", "motif-c"),
                ("motif-a", "motif-b", "motif-c"),
                ("motif-a", "motif-b", "motif-c"),
            ),
            variation_candidates=("exact",),
        ),
        AccompanimentParameters(
            pattern_by_phrase=("support-a",) * 4,
            variation_by_phrase=("exact",) * 4,
        ),
        AccompanimentGenerationOptions(pattern_definitions=(support,)),
        BassParameters(
            pattern_by_phrase=("bass-a",) * 4,
            variation_by_phrase=("exact",) * 4,
        ),
        BassGenerationOptions(pattern_definitions=(bass,)),
        NoiseParameters(
            pattern_by_phrase=("noise-a",) * 4,
            variation_by_phrase=("exact",) * 4,
        ),
        NoiseGenerationOptions(pattern_definitions=(noise,)),
    )
    return {
        "profile_purpose": PROFILE_PURPOSE,
        "profile_scope": PROFILE_SCOPE,
        "plan": plan,
        # Coverage selection for Human evaluation; not a production 4-layer rule.
        "logical_layers": lambda result: (result.melody, result.accompaniment, result.bass, result.noise),
        # Explicit evaluation allocation; logical objects remain unmodified.
        "allocations": (
            LayerAllocation("melody-001", "CH1", ("pulse",)),
            LayerAllocation("accompaniment-001", "CH2", ("pulse",)),
            LayerAllocation("bass-001", "CH3", ("wave",)),
            LayerAllocation("noise-percussion-001", "CH4", ("noise",)),
        ),
        "title": "Generated BGM Quality Evaluation",
        # JSON Version 2 / Song Version 6 TicksPerRow, not BPM.
        # This is an evaluation parameter and matches the row resolution.
        "tempo": 1,
        "ticks_per_row": 1,
        "instrument_by_channel": {"CH1": 1, "CH2": 2, "CH3": 3, "CH4": 4},
        "instruments": (
            {"id": 1, "name": "evaluation-pulse1", "channel": "pulse1"},
            {"id": 2, "name": "evaluation-pulse2", "channel": "pulse2"},
            {"id": 3, "name": "evaluation-wave", "channel": "wave", "waveform": "evaluation_wave"},
            {"id": 4, "name": "evaluation-noise", "channel": "noise", "initial_volume": 15,
             "envelope_direction": "down", "envelope_sweep": 0, "width_mode": "15bit"},
        ),
        "wave_tables": ({
            "name": "evaluation_wave",
            "samples": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                         15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
        },),
        "absolute_pitch_map": {0: "C4", 1: "D4", 2: "E4"},
        "noise_character_map": {"low": "C3"},
    }
