# Maple Leaf Rag prototype length diagnostic

## 一番簡単な結論

prototypeは原曲MIDIの冒頭部分だけをそのまま再生しているわけではない。NormalizedScoreまでは原曲MIDI全体（2566 events、measure 1〜144、最後のnote end 110592 ticks）を保持している。ArrangementPlanでは16音だけが残り、その16音はsource timelineのmeasure 23〜144に散在し、最後の1音は原曲の最後まで届いている。その16音をJSONの1本の64-row patternへ詰め直すため、JSON/UGE/ROMのデータ上の再生範囲は64 rowsとなる。

これは範囲と構造のmachine factであり、Humanが「長さが違う」と感じた直接原因を確定するものではない。

## Scope and provenance

- source: Mutopia `Mutopia-2011/11/13-23`
- source MIDI SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- artifact: `/tmp/pocket-sweeper-01705/artifacts`
- diagnostic: `tools/analyze_pd_length_diagnostic.py`
- diagnostic JSON SHA-256: `81353851fbdd31ba73fb56734aeef4ae88afb175f7ac9b3afa0a297a24cf16f6`
- diagnostic Markdown SHA-256: `830f68807e6f0b51174291f8ae2ef8eb101114b59e68c47611099f1c44c21a68`
- repeated run: run1/run2 JSON and Markdown hashes一致

## Source MIDI

| field | value |
|---|---:|
| SMF format | 1 |
| PPQ | 384 |
| tracks | 3 |
| note events | 2566 |
| first onset | 0 ticks |
| last onset | 110400 ticks |
| last note end | 110592 ticks |
| tick span | 110592 ticks |
| quarter-note span | 288 quarters |
| source meter | 2/4 |
| tempo | 500000 μs/quarter = 120 BPM |
| source timeline measures | 1〜144 (768 ticks/measure) |
| constant-tempo duration | 144 seconds |

The MIDI contains one recorded tempo event and one 2/4 meter event. The 144-second value is a source-timeline conversion at the recorded constant tempo; runtime ROM seconds are not asserted here because TicksPerRow/runtime timing is the separate 01712 scope.

## Generated MusicXML / NormalizedScore

The corrected MusicXML and NormalizedScore have:

- 2566 events
- first onset 0
- last onset 110400
- last note end 110592
- measures 1〜144
- 768 source ticks per 2/4 measure

01707 measured onset preservation as 2566/2566 exact, mismatch 0, maximum delta 0. Therefore no length reduction is observed at MIDI→MusicXML→NormalizedScore in this run.

## ArrangementPlan

The corrected prototype produced 16 selected events and 2550 `polyphony_omitted` issues. Selected events are not confined to the beginning:

- first selected source onset: 17088 ticks, measure 23
- last selected source onset: 110400 ticks, measure 144
- last selected source end: 110592 ticks, source end
- selected source envelope: 93504 ticks from first selected onset to last selected end
- envelope/source tick-span ratio: approximately 84.52%
- first quantized row: 0
- last quantized row: 22
- source event-count ratio: 16/2566 = approximately 0.624% (event ratio only, not time coverage)

The selected source events are distributed across measures 23, 45, 47, 103, 110, 125, 127, 128, 129, and 144. The full selected-event list, including source event IDs and source positions, is in the machine-readable diagnostic JSON.

The 16 events therefore represent sparse samples across much of the latter source timeline, rather than a contiguous short source excerpt. Detailed reasons for the polyphony selection and its rhythm/pitch consequences are deferred to 01713/01714.

## JSON Version 2

- source-derived note tokens: 16
- patterns: 4 (one per channel)
- orders: 1 per channel
- pattern length: 64 rows
- JSON loop metadata: `none`
- source-derived plan events outside the row-64 window: 0

Channel token ranges:

| channel | note tokens | first note row | last note row | final cursor row |
|---|---:|---:|---:|---:|
| pulse1 | 8 | 0 | 33 | 64 |
| pulse2 | 0 | — | — | 64 |
| wave | 8 | 0 | 33 | 64 |
| noise | 0 | — | — | 64 |

The JSON writer emits note/rest tokens and advances a pattern cursor. Empty channels contain a 64-row rest token. The 64-row boundary did not newly remove any of the 16 selected ArrangementPlan events in this artifact; the token stream is padded/terminated at row 64 after the selected tokens.

## UGE

The UGE analyzer reported:

- pattern count: 4
- order count: 1
- order alignment: all channels agree
- tempo raw: 6 (runtime TicksPerRow, not source BPM)
- one reachable order/pattern per channel
- format-level pattern/order data preserved from JSON
- analyzer control-flow: implicit full-order cycle

The analyzer's per-channel event count includes the encoded pattern cell structure, including the rest-only empty channels; it is not the source note count. No additional source-derived length shortening after JSON encoding was observed at format level.

## ASM / ROM runtime data

Generated ASM contains four channel patterns of 64 cells, one order, and loop metadata `db 2,0,63`, corresponding to intended loop mode none in the Version 2 contract. The ROM was built at:

`/tmp/pocket-sweeper-01705/artifacts/maple-leaf-rag-timing-fixed.gb`

The sound-test main routine calls the driver finished check, but the UGE analyzer reports an implicit cycle because the single order wraps without an explicit B-position jump. Thus the following are separate facts:

1. data contains 64 rows per channel;
2. one order references one pattern;
3. intended loop metadata is none, while format analysis sees an implicit order cycle.

Actual audible termination and runtime seconds were not measured in this diagnostic.

## Stage comparison

| stage | event/note count | first position | last position/end | span | source coverage / loss | loop/termination |
|---|---:|---|---|---|---|---|
| source MIDI | 2566 | 0 ticks | onset 110400 / end 110592 | 110592 ticks | full source timeline | source MIDI timeline |
| MusicXML | 2566 | measure 1 / 0 | measure 144 / end 110592 | 110592 ticks | no length loss measured | score data only |
| NormalizedScore | 2566 | 0 ticks | onset 110400 / end 110592 | 110592 ticks | full normalized source | no loop applied |
| ArrangementPlan | 16 selected | source onset 17088 | source end 110592 | selected envelope 93504 ticks | sparse events; 2550 omitted | no JSON loop yet |
| JSON V2 | 16 source-derived notes | row 0 | last note row 33, cursor 64 | 64 rows/pattern | selected events all inside window | intended loop none |
| UGE | 4 patterns, 1 order | pattern row 0 | 64-cell pattern | 64 rows | no additional format-level note loss | implicit cycle in analyzer |
| ASM/ROM data | 4 patterns, 1 order | row 0 | 64-cell pattern | 64 rows | runtime data follows UGE | actual playback not measured |

## Where length changes

No length reduction was observed through NormalizedScore. The major structural change is at ArrangementPlan selection: 2566 normalized events become 16 selected events, with selected source positions spanning from measure 23 to the source end. JSON then serializes those selected events into one 64-row pattern per channel. No selected event was removed by the row-64 boundary in this run.

The data representation is therefore shorter and sparser than the source timeline, but this report does not classify that difference as the cause of the Human listening result.

## Unresolved items

- whether the Human's perceived length difference is caused by sparse selection, row/token packing, implicit loop behavior, runtime timing, or another stage;
- runtime seconds and hUGEDriver row timing;
- rhythm preservation;
- pitch/melody preservation;
- Human evaluation of the exact data/loop behavior;
- production suitability.

## Handoff to 01712

01711 records structural length only. 01712 should separately measure source BPM, PPQ, quantization, JSON/UGE TicksPerRow, row duration, and runtime seconds without equating BPM with TicksPerRow.
