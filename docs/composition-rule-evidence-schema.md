# 作曲ルールの根拠・出典・確度記録形式

対象WBS: `WBS-001-01575`

## 1. 目的と設計原則

自動作曲ルールごとに、根拠、適用範囲、状態、許可用途、禁止推論、検証状態、人の評価、未解決事項を追跡するMarkdown正本schemaを定義する。現時点ではYAML/JSON parserやvalidatorを追加しない。

`source`、`evidence`、`rule`、`applicability`、`status`、`allowed_use`を1対1に固定しない。異なる根拠を単一confidence数値へ圧縮せず、capabilityとconstraint、theoryとpolicy、corpus observationとhuman evaluationを分離する。

## 2. Source type

|値|意味|例|
|---|---|---|
|`music_theory`|一般音楽理論|scale degree、chord、cadence|
|`game_bgm`|ゲームBGM固有の知見|long loop、variation、attention|
|`game_boy_hardware`|Game Boy APU仕様|CH1 sweep、4ch|
|`tool_driver`|hUGE/UGE/hUGEDriver/JSON仕様|effect、Instrument、note|
|`pocket_sweeper_spec`|本プロジェクトの方針|SFX mute、JSON Version 2|
|`implementation`|リポジトリ内コードの検査|driver、converter|
|`corpus_observation`|実在UGEの形式観測|`used`、`event_count`、loop.kind|
|`human_evaluation`|GUI、試聴、実機・エミュレータ評価|表示照合、聴感結果|

`corpus_observation`は品質・default・推奨役割・style・naturalnessの根拠ではない。`human_evaluation`も一次仕様へ自動昇格させない。

## 3. Evidence type

`source_type`は出所、`evidence_type`は確認方法である。`definition`、`specification`、`implementation`、`automated_test`、`format_test`、`parser_regression`、`structural_observation`、`human_gui`、`human_listening`を使用する。1 sourceから複数rule、1 ruleから複数source/evidenceを参照できる。

## 4. Rule kind

|値|意味|例|
|---|---|---|
|`capability`|可能な能力|CH1はsweep可能|
|`hard_constraint`|選択scope内で必ず守る条件|CH2/3/4へsweepを生成しない|
|`soft_rule`|候補重み・優先順位|stepwise motionを候補化|
|`parameter`|選択・調整する値|key、scale、tempo、density|
|`policy`|Pocket Sweeper固有方針|SFX channel一時mute|
|`hypothesis`|未確認の仮説|CH1をmain melodyにする候補|
|`human_evaluation_item`|人の評価対象|melodyが自然か|

capabilityと、そこから導出したhard constraintは別ruleとする。

## 5. Status / confidence

`status`は`confirmed`、`conditional`、`provisional`、`hypothesis`、`needs_human_evaluation`、`unresolved`、`rejected`、`superseded`のいずれかとする。confidenceを0〜100へ圧縮しない。

- `source_authority`: `primary` / `secondary` / `internal` / `observed`
- `verification_status`: `not_checked` / `documented` / `implementation_checked` / `automated_checked` / `human_checked`
- `applicability_status`: `explicit` / `conditional` / `unknown`
- `human_evaluation_status`: `not_required` / `not_started` / `planned` / `completed` / `conflict_found`

CPU Manual=100、21曲多数派=80、人が好き=90のような比較は禁止する。

## 6. Applicability

各ruleに`target`、`conditions`、`exclusions`を記録する。

```yaml
applicability:
  target: generated_song
  conditions:
    - platform: dmg
    - channel: ch1
    - generator_mode: scale_only
  exclusions:
    - generator_mode: chromatic_allowed
```

## 7. Allowed use / Prohibited inference

`allowed_use`には`generation_constraint`、`candidate_weighting`、`parameter_selection`、`format_validation`、`parser_regression`、`structural_comparison`、`human_review`、`documentation`を複数指定できる。

`prohibited_inference`には`composition_quality`、`default_parameter`、`preferred_channel_role`、`style_generalization`、`musical_naturalness`、`hardware_capability`、`human_preference_generalization`を必要に応じて指定する。corpus observationは少なくとも品質・default・preferred role・style・naturalnessを禁止する。

## 8. Source reference

```yaml
source:
  id: SRC-GB-HW-001
  source_type: game_boy_hardware
  title: Game Boy CPU Manual
  location: https://example.invalid/manual.pdf
  locator: "pp. 39-50; NR10-NR14"
  access_date: 2026-09-26
  authority: primary
  revision_or_commit: "version 1.01"
  note: "01559の一次資料対応を再利用"
```

内部文書はpath、section heading、WBS ID、確認commit SHAを記録し、line numberは補助扱いとする。外部資料はURLだけでなくtitle、該当section/page、access dateを記録する。

## 9. Rule record template

```yaml
id: MT-HARD-EXAMPLE-001
title: "選択scale内にnoteを限定する"
rule_kind: hard_constraint
statement: "scale_only modeでは生成noteのpitch classを選択scaleに限定する"
source_type: [music_theory]
evidence:
  - id: EVID-MT-001
    evidence_type: definition
    source_refs: [SRC-MT-001]
    observation: "scaleは音高集合として扱える"
    supports: "scale membershipを条件化できる"
applicability:
  target: generated_event
  conditions: [{generator_mode: scale_only}]
  exclusions: [{generator_mode: chromatic_allowed}]
status: conditional
source_authority: secondary
verification_status: documented
applicability_status: conditional
allowed_use: [generation_constraint, format_validation]
prohibited_inference: [default_parameter, musical_naturalness]
machine_checkability:
  level: true
  expected_condition: "pitch_class in selected_scale_pitch_classes"
  failure_meaning: "選択modeの入力整合性違反"
  validator: "planned"
implementation_status:
  rule_documented: true
  generator: not_implemented
  validator: planned
  automated_test: planned
human_evaluation_status: not_required
dependencies: {rule_refs: []}
conflicts: []
supersedes: []
superseded_by: []
open_issues: ["default scaleは未決定"]
```

必須フィールドは`id`、`title`、`rule_kind`、`statement`、`source_type`、`evidence`、`applicability`、`status`、`allowed_use`、`prohibited_inference`、`machine_checkability`、`implementation_status`、`human_evaluation_status`、`open_issues`とする。

## 10. Machine validation / Implementation status

`machine_checkability.level`は`true`、`false`、`partial`を取る。`expected_condition`、`failure_meaning`、`validator`も記録する。「形式化できる」と「現在validator実装済み」は別である。

`implementation_status`には`rule_documented`、`generator`、`validator`、`automated_test`、`human_evaluation`を個別に記録する。ruleが`confirmed`でもgenerator/validatorが`planned`であり得る。melodyの自然さは`level: false`でHuman evaluationへ送る。

## 11. Conflict / Open issue

```yaml
conflicts:
  - id: CONFLICT-001
    affected_rule: GB-EXAMPLE-001
    competing_evidence: [EVID-SPEC-001, EVID-IMPL-001]
    conflict: "specificationとimplementationが一致しない"
    status: unresolved
    resolution_required: "対象platform・toolchainを明示して再確認する"
```

競合がある場合、都合のよい根拠だけで`confirmed`にしない。`unresolved`または`needs_human_evaluation`とし、追加調査・実装確認・人の評価の必要性を`open_issues`へ残す。

## 12. Human evaluation

```yaml
human_evaluation:
  - id: HE-001
    evaluator: human
    target: "generated song / phrase boundary"
    environment: "SameBoy version; playback condition"
    date: 2026-09-26
    criteria: ["自然さ", "loop境界", "反復疲労"]
    result: "not performed: template example only"
    unresolved_issue: "実際の試聴結果が必要"
```

必要項目はevaluator、target、environment、date、criteria、result、unresolved issueである。templateの`not performed`を実績にしない。評価結果でSoft ruleを変更しても、既存21曲の多数派で補強しない。

## 13. Rule dependency / Supersession

WBSの`depends_on`と区別するため、rule recordでは`dependencies.rule_refs`を使用する。これはrule間の概念・検証依存を表し、WBS taskの完了順を表さない。

旧ruleは削除せず、`supersedes`、`superseded_by`、`reason`で置換関係を記録する。ID再利用は禁止する。既存の`GB-HW-*`、`GB-TOOL-*`、`PS-SOUND-*`、`MT-*`は暫定IDとして維持し、大量renameを行わない。

## 14. 記入例A〜G

|例|ID|要点|
|---|---|---|
|A Hardware|`GB-HW-005`|CH1だけがsweep capability。`capability`であり、CH1をmelodyにする根拠ではない。|
|B Derived hard constraint|`GB-HARD-001`|CH2/CH3/CH4へsweepを生成しない。Aとは別ruleで、format validation可能。|
|C Theory conditional|`MT-HARD-001`|`scale_only` modeだけnoteをscale内へ限定。全曲共通のscale外音禁止ではない。|
|D Soft rule|`MT-SOFT-001`|stepwise motionを候補weightへ使う。具体weightは未確定でhard invalidではない。|
|E Corpus observation|`CORPUS-OBS-001`|UGEの`channels.ch3.used=true`。format/regressionには使えるが、CH3=bass・推奨role・qualityへ推論しない。|
|F Policy unresolved|`PS-SOUND-001`|SFX channel欠損耐性。sound-specと実装を根拠にするが、CH1/CH2/CH4の適用範囲は未確定。|
|G Human template|`HE-EXAMPLE-001`|melody自然さの試聴記録テンプレート。未実施でありHuman evaluation済みではない。|

## 15. 21曲UGEの扱い

01574の36候補、25実ファイル、A判定21曲の区別を維持する。21曲の平均・多数派・SHA-256をtheory、hardware、tool evidenceと同格にしない。SHA-256は入力同一性確認でありconfidence scoreではない。

`corpus_observation`の記入例には、`allowed_use: [format_validation, parser_regression, structural_comparison]`等と、`prohibited_inference: [composition_quality, default_parameter, preferred_channel_role, style_generalization, musical_naturalness]`を明示する。

## 16. Review checklist

1. Rule IDが一意で再利用されていない。
2. statementが検証可能な粒度である。
3. source/evidenceと安定したsource referenceがある。
4. source typeとevidence typeを混同していない。
5. applicable scope、条件、除外条件が明確である。
6. capabilityとconstraintを分離している。
7. theoryとPocket Sweeper policyを分離している。
8. corpus observationを品質根拠にしていない。
9. Human evaluationを仕様事実にしていない。
10. machine-checkableとimplementedを混同していない。
11. conflict/open issueを隠していない。
12. superseded ruleを無断削除していない。

## 17. 01576 / 01577への引き継ぎ

01576ではmelody、motif、rhythm、harmony、bass、noiseのconstraint/referenceへ`rule_ref`として本書のRule IDを付与できるようにする。ただし、01576の最終schemaや4ch allocation algorithmは先取りしない。

01577では`status`、`evidence`、`conflicts`、`open_issues`、`human_evaluation_status`、`source_type`を使い、根拠不足のruleを`confirmed`にせず、theory、Game-BGM、hardware/tool、implementation、human evaluationの適切な調査へ戻す運用を定義する。

## 18. 未確定事項と実装範囲

将来YAML/JSONへ移行する時期、既存Rule IDへのsource record付与単位、共通Human evaluation環境、supersessionの複雑なscope変更は未確定である。

本WBSではschema/templateと例だけを追加し、generator、analyzer、converter、game code、WBS validator、rule databaseは変更しない。
