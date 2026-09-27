# Maple Leaf Rag NormalizedScore → ArrangementPlan role extraction

## Scope

WBS-001-01699のmachine diagnostic。対象はNormalizedScoreからrole assignment、
channel allocation、ArrangementPlan selectionまでである。01700で扱う
polyphony/octave/quantizationの詳細評価、JSON/UGE/ASM/ROM、Human試聴は行わない。

## Source / upstream evidence

- source: Mutopia `Maple Leaf Rag (Mutopia-2011/11/13-23)`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- upstream: 01698 `maple-pd-diagnostic/v1`
- upstream onset mismatch: 1585
- upstream scope: full normalized source

The upstream onset mismatch is retained as a warning field. This report measures
NormalizedScore→ArrangementPlan and does not repair or reclassify that upstream
difference.

## Role extraction algorithm

The current `tools/maple_leaf_rag_prototype.py` implementation groups events by
MusicXML part and sorts parts by descending average MIDI pitch, with part ID as
the tie-break after the average-pitch comparison. The highest part is `melody`,
the lowest is `bass`, and intermediate parts are `harmony`. For a single part,
events at pitch ≤60 are `bass` and events above 60 are `harmony`. This is the
implemented prototype heuristic, not a musical correctness claim.

Physical allocation is separate:

| logical role | physical channel |
|---|---|
| melody | pulse1 / CH1 |
| harmony | pulse2 / CH2 |
| bass | wave / CH3 |
| rhythm | noise / CH4 |

The source has no generated rhythm role; CH4 is unused.

## Part statistics and ranking

| part | events | pitch range | average | median | onset range | assigned role |
|---|---:|---:|---:|---:|---:|---|
| P2 | 1193 | 60–92 | 73.471920 | 73 | 0–1632 | melody |
| P3 | 1373 | 32–73 | 54.663511 | 56 | 0–1536 | bass |

The input contains no pitched events in P1. Ranking was P2 then P3. No average
pitch tie occurred in this source; the implementation tie-break is part ID
ascending. There is no evidence here that the selected roles are musically
correct.

## Event coverage and role mapping

The event-level JSON sidecar is `/tmp/pocket-sweeper-01699/run1/maple_leaf_rag.role-diagnostic.json`
and retains source_event_id, normalized event ID, logical role, physical channel,
source/normalized onset, arrangement row, pitch, status, and loss reason.

| role | input | selected/output | omitted | transformed | rejected |
|---|---:|---:|---:|---:|---:|
| melody | 1193 | 18 | 1175 | 0 | 0 |
| bass | 1373 | 13 | 1360 | 11 | 0 |
| harmony/accompaniment | 0 | 0 | 0 | 0 | 0 |
| rhythm/noise | 0 | 0 | 0 | 0 | 0 |

Overall: NormalizedScore 2566, role-assigned 2566, unassigned 0,
ArrangementPlan emitted 31, omitted 2535, transformed 11, rejected 0.
Omissions reported by this stage carry the implementation reason
`polyphony_omitted`; range rejection was zero. The detailed impact of those
operations remains 01700 scope.

## Melody / bass / accompaniment

Melody input pitch range was 60–92, output range 60–77, with 18 output events.
Its structural contour counts were DOWN 17, SAME 971, UP 204.

Bass input pitch range was 32–73, output range 49–59, with 13 output events.
Its structural contour counts were DOWN 12, SAME 1182, UP 178.

Harmony/accompaniment received no input part in this source because only two
pitched parts were parsed: the implementation assigns the highest to melody and
lowest to bass, leaving no middle part. This is a machine fact, not a judgment
that accompaniment was musically unnecessary.

Contour is the 01697 structural definition: events sorted by onset, pitch, and
event ID; adjacent pitch interval classified UP/SAME/DOWN. It is not a musical
quality score. Arrangement output is sparse after later selection, so contour
comparison is reported as structural counts rather than a claim of one-to-one
musical phrase preservation.

## Full source / 64-row scope

Role assignment and ArrangementPlan construction were measured over all 2566
NormalizedScore events. The diagnostic records `full_source_scope=true` and
`json_window_applied=false`. The 64-row window belongs to later JSON emission;
events were not mislabeled as role omissions because of that window.

## Determinism / hashes

Commands:

```text
python3 tools/analyze_pd_source_preservation.py <maple.mid> <upstream>
python3 tools/analyze_pd_role_extraction.py <maple.mid> <upstream>/maple_leaf_rag.diagnostic.json <output>
```

Two runs produced identical hashes:

- source MIDI: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- upstream diagnostic: `a25edd84e5d83dcf25bbe92d32cce4486cd999581d5e799caa73c756d816c087`
- role diagnostic JSON: `032256e6735d00c2eec5f9276048dc5de41a9600a99c701e4ffe24cdd91391fd`
- role diagnostic Markdown: `ae87ef69d503a6e9fd30f5d4b7410d83b53930c083eb5ab5b145df4645c551cd`

## Machine conclusions

The prototype role algorithm assigned every normalized event to a logical role,
mapped melody/bass to pulse1/wave, emitted 31 ArrangementPlan events, and
reported each omitted/transformed event by source_event_id and reason. It did
not assign a harmony or rhythm role for this input, and CH4 remained unused.

## Explicit non-conclusions

These results do not establish that melody or bass is musically correct, that
accompaniment is appropriate, that role extraction caused the Human listening
result, or that the upstream onset mismatch caused it. They do not assess
Maple Leaf Rag recognizability, Game Boy BGM suitability, or production use.

## Handoff to 01700

01700 should separately quantify polyphony collision, octave/range transformation,
and quantization effects using this source_event_id mapping. It should preserve
the distinction between role assignment and later omission/transformation.
