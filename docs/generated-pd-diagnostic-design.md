# PD曲自動編曲 diagnostic design

## Scope

WBS-001-01697では、Maple Leaf Rag prototypeの各変換境界を後続WBSで
比較できる契約を設計する。これは診断方式の設計であり、全曲の実測比較、
原因の特定、音楽品質評価、JSON Version 2の変更は行わない。

## Diagnostic goals / non-goals

診断の目的は、source eventが各stageで保存・変換・省略・再構成された事実を
再現可能に比較することである。machine structural equivalenceと、
「Maple Leaf Ragらしい」「曲として成立する」というHuman musical
equivalenceは別証拠として扱う。後者をCodexが算出・代行しない。

## Pipeline stages

| id | stage | input/output | machine comparison |
|---|---|---|---|
| A | source_midi | approved MIDI bytes | source hash, SMF metadata |
| B | parsed_midi | `MidiNote`/track representation | raw pitch/tick/duration/event identity |
| C | generated_musicxml | MIDI-derived MusicXML | pitch, divisions, measure/location, reconstructed fields |
| D | normalized_score | parser-neutral events | musical tick, pitch, duration, source reference |
| E | arrangement_plan | roles/channels/events | selection, transformation, omission, channel |
| F | json_v2 | rows/instruments/order | row/note/instrument/loop metadata |
| G | uge | hUGE binary structures | pattern cell/order/tempo/instrument |
| H | asm | hUGEDriver ASM | descriptor/order/instrument/loop metadata |
| I | rom/runtime | RGBDS ROM | build bytes; note equivalence ends at encoded runtime data, playback needs Human/runtime evidence |

ASM and ROM can be structurally inspected, but audio playback, timbre,
phrase perception, and musical equivalence are not inferred from them.

## Event identity

The canonical key is `source_event_id`. It is assigned by the source parser and
retained in sidecar records, not added to JSON V2 or UGE. The existing MIDI IDs
such as `midi:t0:e12` are valid source references; MusicXML/NormalizedScore
records add deterministic stage IDs while retaining `source_event_id`.

Recommended mapping record:

```json
{
  "source_event_id": "midi:t0:e12",
  "events": [
    {"stage": "parsed_midi", "stage_event_id": "midi:t0:e12", "status": "PRESERVED"},
    {"stage": "generated_musicxml", "stage_event_id": "xml:P1:m1:n3", "status": "RECONSTRUCTED"},
    {"stage": "normalized_score", "stage_event_id": "norm:P1:m1:n3", "status": "PRESERVED"},
    {"stage": "arrangement_plan", "stage_event_id": "plan:melody:42", "status": "TRANSFORMED"},
    {"stage": "json_v2", "stage_event_id": "json:ch1:r7", "status": "TRANSFORMED"}
  ]
}
```

One source event may map to zero, one, or multiple output events. Omitted or
rejected mappings remain in the sidecar with a reason rather than disappearing.

## Common event fields

Each comparable event record uses these fields where available:

- identity: `source_event_id`, `stage`, `stage_event_id`, source track/part,
  source measure/location
- pitch: `original_pitch`, `current_pitch`, `transformed_pitch`,
  `octave_shift`, `range_rejection`, `pitch_reason`
- timing: `original_onset_tick`, `current_onset_tick`, `quantized_onset_tick`,
  `original_duration_tick`, `current_duration_tick`, `quantized_duration_tick`
- grouping: `simultaneous_group_id`, `part`, `track`, `logical_role`,
  `physical_channel`
- result: `status`, `reason`, `selected_event_id`, `warnings`

Missing values are `null` with `UNKNOWN` or `NOT_APPLICABLE`; they are not
silently filled from musical assumptions.

## Stage-specific fields

- MIDI: SMF format, PPQ, track, channel, velocity, raw tick boundaries.
- MusicXML: part/measure, divisions, pitch spelling, voice/staff fields,
  serialization hash, and whether the field was reconstructed.
- NormalizedScore: parser-neutral onset/duration in source ticks, meter/key/tempo
  references, and source event identity.
- ArrangementPlan: role, selected/omitted event, channel, range transform,
  quantization, instrument, loop/section treatment.
- JSON: pattern, row, note token, instrument, `tempo`/TicksPerRow, order, loop.
- UGE/ASM: pattern/order/instrument addresses and encoded row metadata.
- ROM: input hashes, RGBDS version, binary hash; no inferred musical semantics.

## Timing normalization

The canonical comparison unit is source MIDI tick, with PPQ recorded in the
manifest. MusicXML divisions are mapped back to source ticks using its divisions
and PPQ. NormalizedScore remains in musical/source-tick coordinates. Arrangement
quantization records both original and quantized ticks; the prototype grid is 30
source ticks. JSON row is a separate coordinate (`quantized_tick / grid`).

Source tempo is stored as microseconds per quarter/BPM metadata. JSON/UGE
TicksPerRow is runtime timing and is not BPM; both values must appear separately
in every diagnostic scope. A rounding rule and versioned conversion function must
be recorded before 01698 measurements.

## Pitch representation

Use MIDI integer pitch as the canonical comparison value. MusicXML step/alter/
octave is normalized to that value, while original spelling is retained as an
optional field. Arrangement records octave shift and reason; range rejection is
distinct from clamping. JSON note names are decoded back to MIDI pitch for
comparison. Unsupported/ambiguous spelling is `RECONSTRUCTED` or `UNKNOWN`, not
silently equivalent.

## Simultaneous notes and polyphony

Events sharing `(stage, part/track, onset_tick)` form a deterministic
`simultaneous_group_id`, with pitches sorted numerically then by event ID.
Reports include source count, pre-reduction count, selected event(s), omitted
events, physical channel, and omission reason. Thus same-quantized-row
polyphony reduction can be measured without treating omission as preservation.

## Role/channel mapping

Logical roles and physical channels are separate fields. For the current
prototype, the configured mapping is melody→pulse1, harmony→pulse2,
bass→wave, rhythm→noise; CH4 is unused. The diagnostic records the role
selection rule (including average-pitch ranking) and does not call a role a
musical fact. A role may be `UNKNOWN` until selected by the algorithm.

## Loss/transformation classification

The controlled vocabulary is:

- `PRESERVED`: comparable value retained under the declared coordinate mapping
- `TRANSFORMED`: deliberately changed with input/output and reason recorded
- `OMITTED`: source event not emitted by a reduction/window policy
- `REJECTED`: source event excluded by an explicit validity/range rule
- `RECONSTRUCTED`: representation recreated without original semantic data
- `UNKNOWN`: source or destination cannot establish the relationship
- `NOT_APPLICABLE`: field does not exist at that stage

`TRANSFORMED` is not the same as `OMITTED`; `RECONSTRUCTED` is not evidence of
original notation preservation.

## Contour definition

For a declared role and scope, sort selected events by `(onset_tick, pitch,
stage_event_id)`. For adjacent pitch-bearing events, record integer interval
`current_pitch - previous_pitch` and direction `UP`, `SAME`, or `DOWN`; equal
onsets are grouped before sequencing and ties are not interpreted as phrases.
The report includes sequence IDs, scope, role, pitch coordinate, and whether
events were transformed or omitted. Melody/bass contour is a structural metric,
not a Human judgment that the tune is preserved.

## Event-level comparison and summary metrics

The reusable report compares mappings by source event and records deltas for
pitch, onset, duration, and role/channel. Each stage/scope summary contains only
metrics needed for diagnosis:

- total input/output events
- preserved, transformed, omitted, rejected, reconstructed, unknown counts
- unique pitch count
- onset and duration difference counts
- simultaneous-group count and collision count
- role/channel counts
- contour event count and interval differences

Metrics are always scoped by source full-song, normalized full-song,
ArrangementPlan scope, or emitted 64-row window. They are not quality scores.

## Report format

The proposed sidecars are:

- `maple_leaf_rag.diagnostic.json`: canonical machine-readable schema
  `maple-pd-diagnostic/v1`, sorted arrays, explicit nulls, no timestamps
- `maple_leaf_rag.diagnostic.md`: deterministic human summary generated from
  the JSON, including scope, tables, losses, and unresolved comparisons

The JSON top level contains `schema`, `source`, `tool`, `configuration`,
`scopes`, `stages`, `event_mappings`, `transformations`, `losses`, and
`summary_metrics`. JSON V2 remains unchanged; diagnostic provenance is sidecar
data.

## Determinism and provenance

The report records source URL/identity/hash, every stage artifact hash, tool and
parser versions, configuration hash, comparison algorithm/version, coordinate
conversion settings, and report hash. Arrays and object keys are serialized in
stable order; generated time is excluded. The later implementation must run the
same source/config twice and compare canonical JSON and report hashes.

## 64-row scope handling

The diagnostic must distinguish:

1. source MIDI full event scope;
2. full normalized/ArrangementPlan scope;
3. JSON/UGE/ASM/ROM emitted scope, currently one 64-row window.

Events outside the emitted window are `OMITTED` with reason `prototype_window`,
not evidence of arrangement loss. No section name such as first strain is
assigned without source evidence.

## Known transformation mapping

| known behavior | observed stage/field |
|---|---|
| voices/staff/spelling reconstructed | MusicXML fields, status `RECONSTRUCTED` |
| repeats/endings/articulation/dynamics/notation unknown | MusicXML/NormalizedScore semantic fields, `UNKNOWN` |
| average-pitch part ranking | ArrangementPlan role selection/reason |
| polyphony reduction | simultaneous groups, selected/omitted mappings |
| same quantized-row omission | JSON row collision, `OMITTED` reason |
| octave shift | ArrangementPlan pitch fields, `TRANSFORMED` |
| range rejection | ArrangementPlan mapping, `REJECTED` |
| 30-tick grid | timing original/quantized fields |
| 64-row window | scope and `prototype_window` omission |
| CH4 unused | role/channel `NOT_APPLICABLE` or explicit unused policy |

This mapping identifies where to observe behavior, not which behavior caused the
Human result.

## Machine vs Human evidence boundary

Machine diagnostic can establish event/pitch/onset/duration preservation,
contour, selection, omission, role/channel mapping, encoded pattern data,
provenance, and deterministic hashes. It cannot establish recognizability,
musical form, playability, timbre balance, natural ending, or production BGM
suitability. Those remain Human/runtime evidence.

## Handoff to 01698–01702

01698 should instantiate A–D comparisons for note/timing. 01699 should measure
role extraction. 01700 should measure reduction, octave, and quantization.
01701 should compare ArrangementPlan, JSON, and UGE coordinates. 01702 should
combine reports without assigning an unproven single cause. 01703 remains the
Human choice of improvement direction.
