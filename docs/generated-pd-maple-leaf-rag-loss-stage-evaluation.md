# Maple Leaf Rag原曲性喪失 stage evaluation

## Scope / Evidence sources

01698〜01701のmachine diagnosticと01694のHuman evidenceを統合する。
目的は変化が確認されたstageと未確認の因果候補を整理することであり、原因の
順位付け、algorithm改善、production採用判断は行わない。

参照canonical evidence:

- `docs/generated-pd-maple-leaf-rag-human-evaluation.md`
- `docs/generated-pd-maple-leaf-rag-preservation.md`
- `docs/generated-pd-maple-leaf-rag-role-extraction.md`
- `docs/generated-pd-maple-leaf-rag-reduction.md`
- `docs/generated-pd-maple-leaf-rag-json-uge-preservation.md`
- `docs/generated-pd-diagnostic-design.md`

## Human evidence

Human原文:

> Maple Leaf Ragとは全く違う曲になっていました。

> 曲としても成立していませんが、自動作曲よりは進歩しているように感じます。

確認できる範囲は、原曲として認識されなかった、曲として成立していないと
評価された、以前の自動作曲より進歩したと感じられた、ということだけである。
production BGM採用の判断は得られていない。中間stageを個別に聴いた結果ではない。

## Diagnostic chain and event-count funnel

```text
MIDI → MusicXML → NormalizedScore → role assignment
     → quantization/collision/polyphony → octave/range
     → ArrangementPlan → JSON V2 → UGE → runtime → Human
```

| stage | event count / result |
|---|---|
| MIDI / MusicXML / NormalizedScore | 2566 / 2566 / 2566 |
| role assigned | 2566; melody 1193, bass 1373, harmony/rhythm 0 |
| reduction | selected 31, omitted 2535 |
| JSON | 26 note cells, 5 prototype-window overflow |
| UGE | 26 notes, JSON→UGE exact 26 |

これはevent-count funnelであり、音楽情報量や品質scoreではない。

## Stage-by-stage summary

| stage | confirmed preservation | confirmed transformation/loss | Human causality |
|---|---|---|---|
| MIDI→MusicXML | 2566 events、pitch 2566、duration 2566、1→1 mapping | onset exact 981、mismatch 1585、max 1152 ticks；notation fields reconstructed | not confirmed |
| MusicXML→NormalizedScore | internal parser comparisonでpitch/onset/duration 2566 exact | independent parser検証ではない | not confirmed |
| role assignment | 全2566 assigned | P2→melody、P3→bass、harmony/rhythm 0 | not confirmed |
| quantization | explicit 30-tick rule | onset changed 2009、duration changed 2552 | not confirmed |
| polyphony reduction | collision selectionをsource IDで追跡 | 31 preexisting groups、selected 31、omitted 2535 | not confirmed |
| octave/range | range ruleを記録 | shift 276、rejection 0 | not confirmed |
| ArrangementPlan→JSON | 26 note cellsへmapping | 5 window overflow、pitch/row representation difference | not confirmed |
| JSON→UGE | 26/26 note/instrument exact、追加lossなし | runtime semanticsは未確認 | not confirmed |
| UGE→runtime | ROM生成・format解析の証跡 | real-time/APU/audible timing未確認 | not confirmed |
| runtime→Human | SameBoyでHumanが実際に試聴 | Human評価は最終ROMのみ | Human evidence confirmed、原因は未確認 |

## MIDI → MusicXML → NormalizedScore

SMF format 1、PPQ 384、3 tracks、tempo 500000 microseconds/quarter（120 BPM）、
meter 2/4だった。MIDI/MusicXML/NormalizedScoreは各2566 events、source-to-XMLは
全件1→1、pitch exact 2566、duration exact 2566だった。onsetは981 exact、1585
mismatch、最大delta 1152 ticks。MusicXML→NormalizedScoreは既存parser内部で一致
したが独立parser検証ではない。voices/staff/spellingはreconstructedである。

これは確認済み差分であり、Human評価の確認済み原因ではない。

## Role assignment

average-pitch heuristicはP2（1193、平均73.471920）をmelody、P3（1373、平均
54.663511）をbassへ割り当てた。harmony/rhythmは0。確認済みなのはこの機械的
assignmentだけで、主旋律・bassの音楽的正しさやharmony欠如の影響は未確認である。

## Quantization / polyphony / octave

gridは30 ticks。onset changed 2009、exact 557、duration changed 2552、exact 14、
最大onset delta 12 ticks。quantization-induced collisionは0だった。

collision keyはrole/channel/quantized row。31 groupsは全てNormalizedScoreで既に
同一onset、最大group size 199。従って2535 omissionは確認済みpolyphony reduction
だが、quantizationが新たに作ったcollisionとは確認されていない。

octave shiftは276件（bass +12: 265、+24: 8、-12: 3）、最大24 semitones、range
rejection 0。これは全入力event集合に対するtransform countであり、31 selected
eventsの件数ではない。

## ArrangementPlan → JSON → UGE

ArrangementPlan 31件のうちJSONは26件、5件はpattern cursorが64-row boundaryへ
到達した`prototype_window_overflow`。nominal arrangement rowの範囲とは別に、
sequential note/length tokenによるcursor進行で発生したdownstream lossである。
pitch exactは6/26、row exactは3/26だが、JSONはsource-event-indexed arrayではなく
sequential token streamであり、durationはlength/cursor advancementで表現される。
sidecarのdeterministic per-channel mappingによるrepresentation comparisonで、
単純なpitch error/timing error件数とは解釈しない。

JSON 26 note cellsはUGE 26 note cellsへ、note/instrument/pattern/orderともformat
levelでexactだった。CH2/CH4はrest-only pattern。JSON tempo/UGE tempo_rawは6で、
source BPM 120とは別のTicksPerRowである。intended loopはnone、analyzerは
implicit_full_order_cycleを報告したが、両者は別概念である。

## Causal candidates

以下はmachine changeが確認され、今後因果を検証できる候補である。順位付けはしない。

- MIDI→MusicXML onset reconstruction: 1585差分。A/B timing representationと中間stage比較が必要。
- role assignment / harmony absence: P2/P3のみassignment。別role ruleまたは中間音源の比較が必要。
- preexisting simultaneous structure / polyphony reduction: 31 groups、2535 omission。reduction前後の聴取・構造比較が必要。
- quantization: 2009 onset changesだがinduced collision 0。grid有無比較が必要。
- octave/range: 276 shifts、rejection 0。shift前後の比較が必要。
- JSON cursor/length representation: 31→26、5 overflow。window/cursor表現のA/B比較が必要。
- runtime: format-level以降のreal-time/APU/audible behavior未確認。測定または別Human試聴が必要。

各候補は「変化が存在する」ことが確認されたのみで、Human原因は証明されていない。

## Confirmed causes

Humanの「全く違う曲」「曲としても成立していない」という評価に対する、直接確認済み
の単一原因はまだ特定されていない。

## Unknown / unverified

- 中間stageごとのHuman聴感
- onset mismatchが最終聴感へ与えた影響
- role assignmentの音楽的正しさ
- polyphony omission後の旋律・和声保持
- quantization/octave shiftの聴感影響
- JSON cursor representationのruntime影響
- hUGEDriver real-time timing、APU writes、audible duration

## Negative evidence

今回確認したJSON→UGE format-level conversionでは、26 note/instrument cellsの
追加loss・mismatchは確認されなかった。これはJSON→UGEが絶対に原因でないことや、
runtimeが正しいことの証明ではない。

## Options for Human decision (01703)

Humanが選択できる追加検証方向を、順位・scoreなしで提示する。

- upstream timing representationの追加検証/A-B prototype
- role extractionとharmony absenceの比較
- polyphony reduction前後の構造・試聴比較
- quantization gridの比較検証
- octave/range handlingの比較検証
- ArrangementPlan→JSON cursor/length representationの追加検証
- runtime timingのmachine測定
- 複数stageを固定して比較する最小A/B prototype

Codexは選択・推奨・production採用を決定していない。

## Explicit non-conclusions

MIDI→MusicXML onset mismatch、polyphony reduction、role assignment、harmony欠如、
quantization、octave shift、JSON overflow、JSON→UGE、Maple Leaf Rag自体、MusicXML
方式、PD自動編曲方式のいずれについても、今回の証拠だけで失敗原因・不適切・廃止・
改善効果を確定しない。production BGM採用も判断しない。

## Handoff to 01703

01703では本書のconfirmed facts、候補、unknownを確認し、Humanが次の改善または追加
検証範囲を選択する。Humanの明示判断が記録されるまで、01703はcompleteにしない。
