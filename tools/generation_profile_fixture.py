"""Explicit evaluation fixture; not a Pocket Sweeper musical default."""

from bgm_generator import *  # noqa: F403


def build_profile(seed):
    motif = MotifDefinition("motif-a", (MotifStep(2, absolute_pitch=0), MotifStep(2, rest=True)))
    plan = LogicalGenerationPlan(
        StructureParameters(4, 4, phrase_measures=1, section_phrase_counts=(2,), loop_mode="full"),
        StructureGenerationOptions(),
        MelodyParameters(motif_by_phrase=("motif-a", "motif-a"), variation_by_phrase=("exact", "exact")),
        MelodyGenerationOptions(motif_definitions=(motif,)),
        AccompanimentParameters(pattern_by_phrase=("support-a", "support-a"), variation_by_phrase=("exact", "exact")),
        AccompanimentGenerationOptions(pattern_definitions=(
            AccompanimentPatternDefinition("support-a", "rhythmic_support", (
                AccompanimentPatternStep(2, absolute_pitch=0), AccompanimentPatternStep(2, rest=True),
            )),
        )),
        BassParameters(pattern_by_phrase=("bass-a", "bass-a"), variation_by_phrase=("exact", "exact")),
        BassGenerationOptions(pattern_definitions=(
            BassPatternDefinition("bass-a", (
                BassPatternStep(2, bass_relation="root", absolute_pitch=0), BassPatternStep(2, rest=True),
            )),
        )),
        NoiseParameters(pattern_by_phrase=("noise-a", "noise-a"), variation_by_phrase=("exact", "exact")),
        NoiseGenerationOptions(pattern_definitions=(
            NoisePatternDefinition("noise-a", (
                NoisePatternStep(2, role="beat_support", character_ref="low"), NoisePatternStep(2, rest=True),
            )),
        )),
    )
    return {
        "plan": plan,
        "logical_layers": lambda result: (result.melody,),
        "allocations": (LayerAllocation("melody-001", "CH1", ("pulse",)),),
        "title": "Generated Evaluation Fixture",
        "tempo": 120,
        "ticks_per_row": 1,
        "instrument_by_channel": {"CH1": 1},
        "instruments": ({"id": 1, "name": "fixture-pulse", "channel": "pulse1"},),
        "absolute_pitch_map": {0: "C4"},
        "noise_character_map": {"low": "C3"},
    }
