# Maple Leaf Rag quantization / polyphony / octave reduction

## Scope

WBS-001-01700のmachine diagnostic。NormalizedScore/role-assigned eventsから
ArrangementPlan相当の選択までをfull source scopeで比較した。JSON 64-row
window、JSON/UGE/ASM/ROM、Human試聴、algorithm改善は実施していない。

## Source / upstream evidence

- source: Mutopia `Maple Leaf Rag (Mutopia-2011/11/13-23)`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- 01698 diagnostic: `a25edd84e5d83dcf25bbe92d32cce4486cd999581d5e799caa73c756d816c087`
- 01699 role diagnostic: `032256e6735d00c2eec5f9276048dc5de41a9600a99c701e4ffe24cdd91391fd`
- upstream onset mismatch: 1585, retained separately

## Actual transformation order

Code inspection and diagnostic confirm this order:

1. role assignment
2. onset quantization
3. collision lookup by row
4. first-event selection and `polyphony_omitted`
5. octave shift and range check
6. ArrangementPlan emission

The production algorithm was not changed.

## Quantization

- grid: 30 source ticks
- onset: `round(start / 30)` using Python `round` (banker's rounding)
- duration: `max(1, round(duration / 30))`
- collision tie order: `(normalized onset, pitch, event_id)` ascending

| metric | result |
|---|---:|
| onset exact | 557 |
| onset changed | 2009 |
| max absolute onset delta | 12 ticks |
| mean absolute onset delta | 7.017147 ticks |
| median absolute onset delta | 6 ticks |
| duration exact | 14 |
| duration changed | 2552 |

These deltas are NormalizedScore→quantized deltas, separate from the 01698
source MIDI→NormalizedScore onset mismatch.

## Collision / polyphony

Collision key: `(logical_role, physical_channel, quantized_row)`. The first event
after the implementation sort is selected; later members are omitted with
`polyphony_omitted`.

| statistic | result |
|---|---:|
| multi-event collision groups | 31 |
| maximum group size | 199 |
| preexisting simultaneous groups | 31 |
| quantization-induced groups | 0 |
| mixed groups | 0 |
| selected | 31 |
| omitted | 2535 |

All multi-event groups had equal NormalizedScore onset. Group sizes were 5 (5
groups), 72 (2), 65 (2), and one each of 16, 47, 49, 54, 59, 60, 64, 68, 71,
75, 85, 93, 95, 109, 112, 148, 154, 169, 172, 176, 192, and 199.

## Role-by-role reduction

| role | input | unique quantized positions | collision groups | selected | omitted |
|---|---:|---:|---:|---:|---:|
| melody | 1193 | 18 | 18 | 18 | 1175 |
| bass | 1373 | 13 | 13 | 13 | 1360 |
| harmony | 0 | 0 | 0 | 0 | 0 |
| rhythm | 0 | 0 | 0 | 0 | 0 |

All 2566 event records retain source_event_id, role, channel, normalized and
quantized timing, pitch before/after shift, collision group, status, reason, and
transformation history in the diagnostic JSON. The 31 selected and 2535 omitted
events are therefore traceable individually.

## Octave shift / range

Configured ranges are pulse1 48–96, pulse2 48–84, wave 48–72, noise 0–0.
The implementation repeatedly adds/subtracts 12 until the range is reached,
then rejects if still outside.

| role / shift | count |
|---|---:|
| bass +12 | 265 |
| bass +24 | 8 |
| bass -12 | 3 |
| all other shifts | 0 |
| total shifted | 276 |
| range rejected | 0 |

Maximum absolute shift was 24 semitones. No rejection examples exist.

## Contour / timing sequence

Contour uses the 01697 structural UP/SAME/DOWN definition.

| role | stage | UP | SAME | DOWN | intervals |
|---|---|---:|---:|---:|---:|
| melody | before | 204 | 971 | 17 | 1192 |
| melody | selected after | 7 | 1 | 9 | 17 |
| bass | before | 178 | 1182 | 12 | 1372 |
| bass | selected after | 3 | 6 | 3 | 12 |

There were 31 unique role/channel quantized positions and 18 unique quantized
onsets across selected events. The sparse post-selection contour is a machine
metric, not a musical quality score.

## Full source / 64-row scope

The diagnostic used all 2566 NormalizedScore/ArrangementPlan events and records
`json_window_applied=false`. The later 64-row JSON window did not cause the
2535 omissions measured here.

## Determinism / hashes

Two runs produced identical hashes:

- source: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- reduction JSON: `7ed9939805ac2fa9550888d7a08db53839c0033008c2652e96b33a7abed547b6`
- reduction Markdown: `ef6713d37e95fd03b4252b63151adc54dea33a26067ac2ee7c8630514012b876`

## Machine conclusions

The implementation quantized 2009 onsets, changed 2552 output durations, formed
31 preexisting collision groups, selected 31 events, omitted 2535, shifted 276
pitches, and rejected none. The diagnostic artifact records all transformations
by source_event_id.

## Explicit non-conclusions

These measurements do not establish that omission, quantization, octave shift,
01698 onset mismatch, or role assignment caused the Human listening result.
They do not judge melody/bass correctness, Game Boy BGM suitability, production
readiness, or whether parameter changes would improve it.

## Handoff to 01701

01701 should compare selected ArrangementPlan events against JSON Version 2 and
UGE, preserving the distinction between this reduction stage and downstream
encoding/runtime behavior.
