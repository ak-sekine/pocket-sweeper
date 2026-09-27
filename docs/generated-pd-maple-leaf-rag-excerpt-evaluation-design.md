# Maple Leaf Rag evaluation excerpt design

## Human scope decision

The Human decision is recorded verbatim:

> 曲全体ではなく、何小節かだけ抜き出すようにしてください。

This changes only the evaluation scope. It does not delete or invalidate the
full-song emitter, does not change JSON Version 2 or ArrangementPlan rules,
does not decide production ROM architecture, and does not introduce MBC or a
bank-aware hUGEDriver.

## Candidate comparison

Candidates were extracted from the existing structure-aware plan without
changing its role, pitch, polyphony, octave, or range rules. Source plan event
counts include selected and omitted events in the measure range; ArrangementPlan
counts are selected events.

| source measures | bars | source events | plan events | melody / harmony / bass / rhythm | rebased rows | JSON patterns / orders | ASM section | headroom |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1–4 | 4 | 68 | 56 | 20 / 20 / 16 / 0 | 0–96 | 7 / 2 | `0x0699` | `0x3967` |
| 1–8 | 8 | 110 | 98 | 34 / 32 / 32 / 0 | 0–202 | 13 / 4 | `0x0B29` | `0x34D7` |
| 1–12 | 12 | 193 | 155 | 57 / 51 / 47 / 0 | 0–301 | 16 / 5 | `0x0D71` | `0x328F` |
| 1–16 | 16 | 275 | 211 | 78 / 71 / 62 / 0 | 0–403 | 22 / 7 | `0x1201` | `0x2DFF` |

All candidates built successfully. The first six source measures contain all
three melodic roles in every measure; measures 7–8 add continuation material
but have no selected harmony events in those individual measures. The 8-bar
candidate supplies more than the minimum 4-bar comparison while remaining a
small, clearly bounded excerpt with substantial section headroom. This is a
machine-structure choice, not a claim that it is the best musical phrase.

## Selected excerpt

The selected evaluation interval is source measures **1–8**, inclusive. The
existing plan contains 110 events in that range and selects 98 events:
34 melody, 32 harmony, 32 bass, and no rhythm/noise events. The source plan's
measure numbers and event IDs are retained in the sidecar. No source note is
added.

Timeline rebasing subtracts the first selected quantized row (`0` here), so
the runtime excerpt starts at row 0. Each sidecar record retains original
absolute onset, original quantized row, rebased row, measure, role, channel,
pitch, duration, and `source_event_id`.

## Pipeline evidence

The selected excerpt was processed using the existing pipeline:

`structure-aware plan → excerpt plan → JSON V2 → UGE → hUGEDriver ASM → ROM`

- JSON non-rest note cells: 86
- UGE non-empty pattern cells: 86
- pattern definitions: 13
- synchronized orders: 4
- JSON loop: `none`; no loop was added
- ASM section: `0x0B29` bytes, below `0x4000`
- ROM header: cartridge type `0x00` (ROM ONLY), ROM size code `0x00`
- estimated duration: approximately 32.8 seconds at the existing 60 Hz
  sound-test cadence, including final pattern padding

The four-order mapping preserves rebased row order and channel alignment. The
full-song artifacts and bank-layout evidence remain unchanged.

## Human evaluation handoff

Codex has not judged the sound. Human should compare this ROM with the prior
64-row prototype and assess Maple Leaf Rag recognition, song coherence,
melody, harmony, bass, tempo, rhythm, and pitch.

