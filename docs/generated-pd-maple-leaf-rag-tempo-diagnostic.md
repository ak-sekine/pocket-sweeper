# Maple Leaf Rag prototype tempo diagnostic

## 一番簡単な結論

原曲は120 BPMで、1拍は0.5秒です。prototype runtimeは60 Hzで6回更新するごとに1 row進むため、1 rowは0.1秒です。したがって現在のruntime row自体は、sourceの30-tick quantization row（0.0390625秒）より2.56倍長い設計です。

ただし、prototypeはsource上で22.25秒から144秒まで離れている16音を、JSON上の0〜33 rowへ詰め直しています。そのためselected eventの時間範囲はsourceの121.75秒からruntimeの3.9秒へ圧縮されています。これはruntime row速度の問題とtimeline再配置を分けて観測した結果であり、Human評価の単独原因とは断定しません。

## Scope and provenance

- source: Mutopia `Mutopia-2011/11/13-23`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- artifact: `/tmp/pocket-sweeper-01705/artifacts`
- tool: `tools/analyze_pd_tempo_diagnostic.py`
- diagnostic JSON SHA-256: `8e82008ad114ebfd5471f260bbce74e2b11c21664c75f9b04e52a4439942d011`
- diagnostic Markdown SHA-256: `92127c8cfa179eaf132d73e8ba6b49618349a5639d9ab8e730ee175f4909b544`

## Source time units

The source contains one tempo event, with no tempo change:

- 500000 microseconds per quarter note
- 120 BPM
- PPQ 384
- quarter note: 0.5 seconds
- eighth note: 0.25 seconds
- sixteenth note: 0.125 seconds
- one MIDI tick: 0.0013020833 seconds
- source total timeline: 144 seconds at the constant source tempo

## Arrangement quantization

The prototype configuration is `GRID_TICKS = 30` and uses `round(source_onset / 30)` for the ArrangementPlan row. Duration uses nearest integer `round(source_duration / 30)`, with minimum duration 1 row.

- one source grid row: 30 ticks
- source-equivalent row: `30 / 384 * 0.5 = 0.0390625` seconds
- 64 source-equivalent grid rows: 2.5 seconds

This source-equivalent row is not the same as runtime JSON row duration.

## JSON and hUGEDriver timing

The JSON field `tempo` is defined by `docs/json-format.md` as Song Version 6 `TicksPerRow`, not BPM. The artifact has `tempo = 6`; the UGE analyzer reports `tempo_raw = 6`.

The runtime path calls `hUGE_dosound` once per VBlank through `Sound_Update`. The project sound specification defines the update as fixed 60 Hz. hUGEDriver increments its tick on each call and advances one row when the tick reaches `ticks_per_row`. Therefore:

- hUGE calls: 60 per second
- TicksPerRow: 6
- runtime row: `6 / 60 = 0.1` seconds
- one 64-row pattern: 6.4 seconds

The 6.4-second value is the data pattern duration before considering loop/control flow. It is not the 144-second source timeline.

## Selected event mapping

The 16 selected events are mapped source-side to runtime-side rows in the machine-readable JSON. Representative aggregate values:

| item | source | runtime |
|---|---:|---:|
| first selected onset | 22.25 s | 0.0 s |
| last selected note end | 144.0 s | 3.9 s |
| selected envelope | 121.75 s | 3.9 s |
| runtime/source envelope ratio | — | 0.03203285 |

The source events are not played at their original absolute timeline positions. For example, an event at source 102.0 seconds is emitted at runtime row 0, while the final source event at 143.75 seconds is emitted at runtime row 27 (2.7 seconds). This is timeline repacking, separate from the per-row clock.

Selected note durations are also changed by representation: source durations of 0.125 or 0.25 seconds become JSON lengths of 3 or 6 rows, i.e. 0.3 or 0.6 runtime seconds. The machine JSON contains all 16 event mappings and duration values.

## JSON → UGE → ASM → runtime

- JSON `tempo`: 6
- UGE `tempo_raw`: 6
- generated ASM descriptor tempo: 6
- hUGEDriver receives the descriptor tempo as `ticks_per_row`
- no additional tempo conversion was observed in JSON→UGE→ASM

The JSON intended loop is `none`. The UGE analyzer reports an implicit full-order cycle for the one-order structure because the order advances and wraps. Loop behavior is separate from the duration of one row.

## Comparison table

| item | Source | Prototype/runtime |
|---|---:|---:|
| quarter note | 0.5 s | not a runtime unit |
| source tick | 0.0013020833 s | not directly emitted |
| source-equivalent grid row | 0.0390625 s | — |
| runtime row | — | 0.1 s |
| 64 rows | source-equivalent 2.5 s | runtime 6.4 s |
| selected first→last envelope | 121.75 s | 3.9 s |

## Confirmed time changes

### Runtime row speed

Confirmed: runtime row is 0.1 seconds at the repository's fixed 60 Hz and TicksPerRow 6. This is 2.56 times the duration of the 30-tick source grid row.

### Timeline compression

Confirmed: selected source events spanning 121.75 seconds are repacked into a 3.9-second runtime envelope. The selected source absolute gaps are not preserved as JSON row gaps.

### JSON → UGE

Confirmed: tempo/timing parameter value 6 is preserved format-level. No additional tempo change was observed.

### Runtime

Format-level row timing is calculable from the 60 Hz contract. Actual emulator/APU audible timing was not measured in this WBS.

## Not concluded

- that runtime row speed alone caused the Human evaluation;
- that timeline compression alone caused it;
- that the source/prototype duration difference is the whole explanation;
- rhythm or pitch causality;
- production suitability.

Those remain separate WBS-001-01713/01714 and Human evaluation concerns.

## Handoff

WBS-001-01713 should measure onset, duration, inter-onset intervals, simultaneous notes, omission, rest, and row advancement. It should keep the confirmed 0.1-second runtime row and the separate timeline repacking evidence distinct.
