# Maple Leaf Rag 統合方式 残存変換診断（01726〜01732）

## Scope

対象は、統合方式のsource MIDI 2566 eventsから、ArrangementPlan、JSON V2、UGEまで。Humanの「見直しが必要」という判断を受けた診断であり、修正方式の選択ではない。

## 01726: full-song / window

統合ArrangementPlanはpulse1 762、wave 575、合計1337 events。quantized absolute rowは10〜3680（pulse1）、0〜3680（wave）。現行JSONは各channel 1 pattern、64 rows、1 orderで、source-derived notesはpulse1 11、wave 10、合計21。plan eventsのうちrow<64はpulse1 11、wave 10であり、残り1326 eventsはpattern window外またはtoken cursor境界でJSONへ入らない。JSON追加lossはpolyphonyとは別に`prototype_window`/cursor境界として扱うべきで、現artifactのproduction reportは全window外eventのsidecar理由を十分に持たない。この診断上、1337→21の主な確認済み差分は64-row単一pattern境界である。full-song複数pattern/orderへのmappingは未実装・未確認。

## 01727: melody / role

現在の明示ruleは平均pitch rankingでP2→melody、P3→bass。P2 1193 events、P3 1373 events、harmony/noise 0。統合planではpulse1 762、wave 575だが、JSON melodyは11 notes。P2が音楽的主旋律か、phraseが保持されているかはmachine factではない。selected sequence、measure progression、intervalを診断可能にする必要があり、現時点ではrole heuristicとsource structureの音楽的同等性は未確認。

## 01728: polyphony / 4ch

absolute timeline化によりcross-measure local-row false collisionは0。ただし同一role/channel内のtrue simultaneousまたはquantized collisionによるpolyphony omissionは残り、reportのloss reasonは`polyphony_omitted` 1229件。これは64-row window外の1326件とは別である。pulse1/waveのみ使用、pulse2/noiseは0。harmony 0は2-part role rule、noise 0はsource percussionをnoiseへ推測変換しないpolicyによる。削除が音楽的に適切かは未確認。

## 01729: timing / rhythm

sourceは120 BPM、PPQ 384。gridは30 source ticks、runtime `TicksPerRow=6`。既存runtime contractでは1 row約0.1秒。source tick→absolute rowの変換は保持されるが、64-row patternへ入るeventはlocal patternへ再配置されるため、source IOIとJSON IOIは同一timelineではない。source duration、quantized duration、JSON token length、runtime durationは別fieldで比較する必要がある。window scalingとrow speedは別変換であり、Humanのテンポ/リズム原因は未確定。

## 01730: pitch / interval

統合方式のJSON/UGE format-level pitch追加mismatchは確認されていない。source→planではrange内octave shiftがあり得るが、pitch class保持とabsolute pitch保持は別である。melody 11 notesがsourceの連続旋律を表すかは未確認。pitch contour/intervalのmachine比較をHumanの音程評価へ拡張しない。

## 01731: source representation

| field | state |
|---|---|
| MIDI pitch/onset/duration | MusicXML/NormalizedScoreでmachine一致を確認 |
| track/part/meter/tempo | parser・MusicXML metadataとして保持/再構成 |
| voice/staff/spelling | reconstructed、原譜保存とは主張しない |
| chord | MusicXML semanticsを扱うが、編曲上の意味は未確認 |
| repeats/endings/articulation/dynamics | lost/unknownまたはsource MIDIで不在。音楽的原譜意味は未確認 |
| section/phrase identity | 未確認 |

onset/duration一致は、編曲に必要なvoice・phrase・repeat構造の完全保持を意味しない。

## 01732: integrated assessment

### Event funnel

`2566 source → 2566 NormalizedScore → 1337 ArrangementPlan → 21 JSON source-derived → 21 UGE-format notes`。2566→1337はrole/true polyphony/reduction、1337→21は64-row single-pattern/windowとcursor境界が確認対象。JSON→UGEの追加note mismatchは未確認。

### Time funnel

source timelineは144秒。absolute plan rowsは最大3680。JSONは64 rows/1 patternへ再配置され、runtime rowは約0.1秒。source durationとruntime durationの同一性は未確認で、event countと時間範囲は混同しない。

### Melody funnel

P2 1193 candidate → role melody → plan pulse1 762 → JSON pulse1 11 → UGE 11 format-level。source上の連続性・phrase同等性は未確認。

### Confirmed facts

- cross-measure false collisionは0
- ArrangementPlan 1337 events、JSON source-derived 21 notes
- 64-row/1-pattern/1-order境界が存在
- roleはP2/P3の平均pitch rule
- JSON/UGE形式変換で追加pitch mismatchは確認されていない

### Candidates / unknowns

full-song pattern/order、melody continuity、true polyphony/chord reduction、source-to-runtime timing、pitch sequence、voice/staff/phrase reconstructionはいずれも追加検証候補。Human聴感への因果は特定されていない。

## 01733への選択肢

| 方向 | 対象evidence | 未確認 | pipeline影響 |
|---|---|---|---|
| full-song pattern/order | 1337→21、64-row境界 | 全曲化で聴感が改善するか | JSON/order設計の追加検証 |
| melody/voice extraction | P2 heuristic、11 notes | 主旋律同等性 | role/sidecar中心、JSON基盤は維持可能性あり |
| polyphony/chord reduction | 1229 omissions、4ch | 音楽的優先順位 | ArrangementPlan変更の影響 |
| timing/rhythm | source→row/token | runtime聴感 | timing設定・pattern設計 |
| pitch/interval | octave/sequence | Human音程評価との因果 | role/pitch transform |
| source representation | reconstructed/lost fields | 原譜意味の必要性 | parser/writerまたはsidecar |
| 複数領域の統合再設計 | 上記全体 | どの組合せが有効か | pipeline全体の再検証 |

順位・推奨は付けない。01733ではHumanが次に診断・見直す範囲を選択する。
