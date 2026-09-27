# Structure-aware ArrangementPlan 診断・再設計

## 対象

NormalizedScore → ArrangementPlan。JSON 64-row問題は別段階として扱った。

## 新しいheuristic

sourceに存在する音だけを使い、同一absolute onset内で次の明示ruleを適用した。

- P2: 上声をmelody、残余をharmony候補
- P3: 下声をbass、残余をharmony候補
- その他part: harmony候補
- 同一role/channel/quantized absolute row内は、duration長、pitch高、source_event_id順で代表eventを選択
- CH4/noiseはsource根拠がないため生成しない

これは主旋律の音楽的確定ではなく、再現可能なstructure-aware heuristicである。

## Old / new machine comparison

| metric | old explainable plan | structure-aware plan |
|---|---:|---:|
| input events | 2566 | 2566 |
| selected | 1337 | 2035 |
| omitted | 1229 | 531 |
| melody selected | 762 | 762 |
| bass selected | 575 | 575 |
| harmony selected | 0 | 698 |
| rhythm selected | 0 | 0 |
| collision groups | 1337 | 2035 |
| cross-measure false collision | 0 | 0 |

新方式では、P2/P3の同時発音残余をharmonyとして保持可能なsource-eventに割り当てた。selected数増加は音楽品質の証明ではない。

## 後段反映

structure-aware planを現行JSON V2へ適応した結果、source-derived notesはpulse1 11、pulse2 9、wave 10、noise 0。ArrangementPlanの2035 eventsが全てJSONへ入ったわけではなく、64-row window/cursor問題は残る。従ってHuman試聴で新ArrangementPlan全体の効果を評価できるかは限定的であり、次ROMは「structure-aware planが現行windowに反映された比較用」として扱う。

生成artifact:

- JSON: `/tmp/pocket-sweeper-01734/new-artifacts/structure-aware.json` SHA-256 `73cb86071b1e68d0a7dd5acea780fbbdebb7c200329cce3ba4dc85b8c79848f3`
- UGE: `/tmp/pocket-sweeper-01734/new-artifacts/structure-aware.uge` SHA-256 `2cd6647f7e72db1d430b2c8d7b78ce2ef220b931e7552226b7ae47918c13b8d0`
- ASM: `/tmp/pocket-sweeper-01734/new-artifacts/structure-aware.asm` SHA-256 `d0c86b0a7efa0548f9fccff1270efc4ee0058976ceaa80fd819f1ae1f02e1a95`
- ROM: `/tmp/pocket-sweeper-01734/new-artifacts/structure-aware.gb` SHA-256 `b245dc0d0633d5de6ae517351f7cf6e16b1ad4c389ad6820b54f48f2bcc61b10`

## 未確認

Humanがmelody/harmony構造を改善と感じるか、原曲認識が改善するかは未確認。machine metricsだけで方式の採用やproduction BGM化は判断しない。
