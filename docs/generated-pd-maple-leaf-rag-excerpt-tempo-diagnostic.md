# Maple Leaf Rag 8-measure excerpt tempo diagnostic

## Scope

This diagnostic isolates source/runtime timing. It does not change melody,
harmony, bass, role allocation, pitch, octave, or polyphony rules.

Source artifact: `/tmp/pocket-sweeper-01705/maple.mid`.
Plan artifact: `/tmp/pocket-sweeper-01734/structure/arrangement-plan.structure-aware.json`.
Excerpt: source measures 1–8.

## Source timing

- PPQ: `384`
- tempo events: one event at source tick `0`, `500000` microseconds/quarter
- BPM: `120`
- meter: `2/4`
- quarter note: `384` ticks = `0.5` seconds
- eighth note: `192` ticks = `0.25` seconds
- sixteenth note: `96` ticks = `0.125` seconds
- measure starts: `0, 768, 1536, 2304, 3072, 3840, 4608, 5376`
- measure 1–8 end: tick `6144`, exactly `8.0` seconds
- source note events in the range: `110`
- source note onset range: `0..6048`
- source onset IOI: `96/192/288` ticks; min/median/max `0.125/0.125/0.375` seconds
- source note duration: min/median/max `96/192/480` ticks

The structure-aware plan retains the selected event absolute onset and source
IDs. In the selected range it has 98 events, absolute onset `0..6048`, plan
onset IOI `96..288` ticks, and quantized rows `0..202`.

## Quantization and runtime

The existing plan uses `GRID_TICKS = 30`. One source-equivalent grid row is
`30 / 384 * 0.5 = 0.0390625` seconds. The existing JSON field is hUGE
Song Version 6 `TicksPerRow`, not BPM. The sound-test loop waits for the next
VBlank and calls `hUGE_dosound` once per frame; the project runtime is 60 Hz.
Thus runtime row duration is `tempo / 60` seconds.

| musical unit | source | source-equivalent rows | old runtime tempo 6 | corrected tempo 2 |
| --- | ---: | ---: | ---: | ---: |
| quarter | 0.5 s | 12.8 rows | 1.2 s | 0.4 s |
| eighth | 0.25 s | 6.4 rows | 0.6 s | 0.2 s |
| sixteenth | 0.125 s | 3.2 rows | 0.3 s | 0.1 s |
| one grid row | 0.0390625 s | 1 | 0.1 s | 0.0333333 s |

With integer `TicksPerRow`, tempo 2 is closer to the source-equivalent grid
row than tempo 3: `0.0333333 / 0.0390625 = 0.8533333`, while tempo 3 gives
`1.28`. This is a quantized approximation; exact 30-tick row timing is not
representable by the current integer hUGEDriver field at 60 Hz.

## Direct source/runtime comparison

The selected plan emits the same 205 maximum runtime rows in both ROMs. The
old ROM uses `tempo=6`, the correction uses `tempo=2`.

| item | source | old runtime | ratio | corrected runtime | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| max sounding timeline | 8.0 s | 20.5 s | 2.5625 | 6.833333 s | 0.854167 |
| 4 orders × 64 rows completion | 8.0 s target | 25.6 s | 3.2 | 8.533333 s | 1.066667 |

The old tempo is therefore a confirmed runtime timing mismatch. The correction
does not claim the Human musical result is fixed; it only moves the integer
runtime clock closer to source timing.

## 32.8-second correction

The prior design estimate of 32.8 seconds was incorrect. The actual old
completion duration is `4 × 64 × 6 / 60 = 25.6` seconds. The old maximum
sounding event end is row 205, or `20.5` seconds. The remaining `5.1` seconds
are final-order/row padding before `hUGE_bgm_finished` reaches order 3, row 63.
With tempo 2 these values become `6.833333` seconds sounding and `8.533333`
seconds completion; padding is `1.7` seconds.

## Cause classification

Confirmed: **D/E**, JSON `tempo`/hUGEDriver `TicksPerRow` was `6` while the
source-equivalent 30-tick grid requires approximately `2.34375` 60-Hz calls
per row. The integer nearest timing choice is `tempo=2`.

Not established by this diagnostic: source BPM conversion error, ArrangementPlan
role selection, pitch, harmony/bass content, or note-loss as causes of the
Human recognition/coherence result.

