# Generated song rule evidence review

対象: WBS-001-01597

## Scope

01594〜01596で得られた候補評価を、01575のevidence schemaと01577のreturn workflowでレビューした。今回はルールの追加・変更、実装修正、候補再生成、追加試聴を行っていない。

## Evidence

### Human evidence

`human_evaluation` / `human_listening` として、candidate-01 (seed 1)、candidate-02 (seed 5)、candidate-03 (seed 7)をHumanがSameBoyで試聴し、3件すべて「1音しかならず曲になっていません。」と報告した。適用範囲は今回の3候補と評価profileに限定し、音楽品質の一般則、note数・rest率・channel数のdefault、原因の証明には使わない。

### Machine evidence

`implementation` / `automated_test` / `structural_observation` として、logical generationは4 logical layerを生成したが、candidate profileはmelodyのみを変換し、melody-001をCH1へ割り当てた。各候補のmelodyには6 event、2つの有音eventがあり、JSON/UGE/ASMにも2つの有音noteが残り、UGEはSong Version 6、order alignment一致、RGBDS ROM生成成功だった。これは形式・構造・変換の証拠であり、runtime発音や音楽品質の証拠ではない。

01596でruntime症状の原因は未特定のまま維持する。

## Rule gate review

| proposed change | classification | evidence / applicability | status and decision |
|---|---|---|---|
| runtimeで2つのnoteが実際に発音されることを検証する | `implementation_gap` / `tool_driver_gap`候補 | Human listeningと、2 noteが生成物に存在するというimplementation evidenceの不一致。対象はcandidate runtime pipeline | `unresolved`。composition ruleではなく実装調査・runtime validationへ戻す。原因や修正は確定しない |
| 評価profileを複数logical layer・より長い構造へ拡張する | evaluation methodology / profile変更候補 | `human_evaluation`、`implementation`、`structural_observation`。対象は評価fixtureでproduction defaultではない | `provisional`。`human_review` と `documentation` に限定し、composition ruleや具体的note数・layer数defaultへ昇格しない |
| 4chを必ず使う | `hard_constraint`候補 | hardware capabilityや既存policyは4ch必須の作曲ruleを支持しない | `rejected` as confirmed rule。4ch allocation、品質、preferred roleを推論しない |
| melodyの最低note数を定める | `parameter` / `hard_constraint`候補 | 3候補のHuman結果だけでは具体値を導けない | `unresolved`。数値default・generation constraintにしない |
| rest率の上限を定める | `parameter` / `soft_rule`候補 | Human結果はrest率の閾値を測定していない | `unresolved`。具体値・品質判定へ使わない |
| accompaniment、bass、noiseを必須にする | `hard_constraint` / `policy`候補 | 4 logical layerの存在と評価profileのmelody-only変換は確認済みだが、必須性の根拠はない | `rejected` as confirmed rule。profile構成とproduction ruleを分離する |
| motif長、pitch variation、densityを変更する | `parameter` / `soft_rule`候補 | 小規模profileの構造は確認できるが、望ましい値の根拠はない | `hypothesis` / `unresolved`。01577 workflowの調査・Human evaluationへ戻す |

## Gate result

今回、`confirmed` または `conditional` として新規追加・変更できるcomposition ruleはない。既存のlogical layerとphysical channelの分離、hardware capability、形式検証のruleを拡張していない。Human結果は対象候補のreview evidenceとして記録し、一般化しない。

## 21-song UGE corpus

21曲UGEは今回のrule、default、channel role、density、note数、rest率、motif長、harmonyの根拠に使用していない。許可されたformat/parser/regression/structural comparison用途を超える推論は行わない。

## Open issues and handoff

- 2つの生成noteがruntimeで1音に聞こえた原因は未確定。converter、ASM、driver、ROM、SameBoy等を原因と断定しない。
- 評価profileを拡張する場合の目的・入力・範囲は、production composition ruleと分けて後続で判断する。
- note数、rest率、4ch、accompaniment/bass/noise必須性の具体ruleは根拠不足。
- SFX共存、Pocket Sweeper用途、loop聴感は今回のevidenceから確定しない。
- 01598でHumanが継続・見直し・中止を判断する。01597ではその判断を代行しない。
