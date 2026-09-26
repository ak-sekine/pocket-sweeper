# 根拠不足時の作曲ルール調査復帰workflow

対象WBS: `WBS-001-01577`

## 1. 目的

rule不足、rule競合、machine validation failure、Human evaluationの問題、Pocket Sweeper policy未確定、Game Boy/tool/implementation不整合が見つかったとき、都合のよい新規ruleやdefault値を追加せず、適切な根拠確認へ戻す運用を定義する。

```text
問題発見
  → 既存Rule ID / evidence / applicabilityを確認
  → 既存ruleで説明できるか判定
  → 根拠不足の種類を分類
  → 適切な調査・実装確認・Human evaluationへ戻る
  → evidenceとdecisionを記録
  → rule新設・変更をgateで再判定
```

禁止する流れは、既存21曲UGEを見て多数派patternを採用し、confirmed ruleやdefaultへ昇格することである。

## 2. Rule不足判定

新規ruleを作る前に、次を順に確認する。

1. 既存Rule IDに該当ruleがないか。
2. 別分類に同じ意味のruleがないか。
3. `applicability`の条件違いではないか。
4. `conditional` ruleを無条件ruleとして誤用していないか。
5. `soft_rule`を`hard_constraint`として扱っていないか。
6. capabilityとconstraintを混同していないか。
7. Pocket Sweeper policyと一般理論を混同していないか。
8. logical layerとphysical channelを混同していないか。
9. implementation未実装をrule不足と誤認していないか。
10. Human evaluation未実施を仕様不足と誤認していないか。

既存ruleのscopeを正しく適用すれば解決する場合、新規ruleは作らず既存ruleを参照する。上記を通過して初めて`missing_evidence`を持つ根拠不足候補として記録する。

## 3. Problem type

|problem_type|例|戻り先|
|---|---|---|
|`theory_gap`|interval、harmony、cadence、bass、voice leadingの概念不足|一般音楽理論、01560/01573系|
|`game_bgm_gap`|loop fatigue、variation、attention、gameplay共存|01558/01561、追加Game-BGM資料|
|`hardware_gap`|channel capability、sweep、Wave、Noise、同時発音|一次/準一次hardware資料、01559/01572|
|`tool_driver_gap`|hUGE、UGE、JSON、effect、Instrumentの表現不足|tool仕様、実装、automated test、必要ならGUI|
|`pocket_sweeper_policy_gap`|channel role、SFX共存、priority、degradation、default|sound-spec、json-format、プロジェクト設計判断|
|`implementation_gap`|仕様・ruleはあるがgenerator/validator/converter/game codeが未実装|implementation task、既存コード確認|
|`format_validation_gap`|JSON→UGE変換不能、参照・値域・row不整合|format/tool仕様、converter/analyzer|
|`human_evaluation_gap`|melodyの自然さ、noise、loop疲労、SFX欠損の聴感|Human listening evaluation|
|`evidence_conflict`|仕様と実装、仕様同士、Human findingとの不一致|conflict resolution|
|`applicability_gap`|platform、channel、mode、toolchain、layer scopeが不明|適用条件の追加調査・仕様確認|

## 4. Evidence selection / Return-to matrix

evidence authorityを単純ランキングにしない。question typeに適したsource/evidence typeを選ぶ。

|問題|必要なevidence|戻り先|
|---|---|---|
|理論概念|`music_theory` + definition/specification|01560/01573、一般理論資料|
|Game-BGM|`game_bgm` + definition/research|01558/01561、追加資料|
|APU capability|`game_boy_hardware` + specification/implementation|01559/01572、hardware資料|
|hUGE/UGE/effect/Instrument|`tool_driver` + implementation/format test|01565、repository、automated test、必要ならGUI|
|Pocket Sweeper方針|`pocket_sweeper_spec` + specification/decision|sound-spec、json-format、設計判断|
|仕様とコード差|`implementation` + implementation/automated test|実装確認・fix task|
|形式変換失敗|`tool_driver`/`implementation` + format_test/parser_regression|converter、analyzer、format仕様|
|聴感問題|`human_evaluation` + human_listening|Human evaluation|
|資料競合|複数source + conflict record|authority、scope、実装差を比較|
|適用範囲不明|複数source + applicability evidence|platform/channel/mode/toolchainの確認|

## 5. Evidence conflict

01575の`conflicts`形式を使用し、最低限以下を記録する。

```yaml
conflicts:
  - id: CONFLICT-SFX-001
    affected_rule: PS-SOUND-001
    competing_evidence: [EVID-SOUND-SPEC, EVID-IMPLEMENTATION]
    conflict: "仕様上のBGM欠損方針と現行SFX占有channelの適用範囲が一致しない"
    applicability_difference: "CH1/CH4占有とCH2/CH4欠損記述"
    source_authority: [internal, internal]
    implementation_difference: true
    resolution_owner: "Pocket Sweeper sound design"
    resolution_type: "specification + human_listening"
    status: unresolved
```

解消前は`unresolved`、`provisional`、`needs_human_evaluation`等を維持し、都合のよいsourceだけで`confirmed`にしない。

## 6. SFX conflictの運用例

現行の確認事項は、Pulse1 SFX→CH1、Noise/Cursor SFX→CH4、`hUGE_mute_channel`による一時mute、BGM位置の継続である。一方、BGM role/mute耐性方針にはCH2/CH4欠損を想定した記述があり、CH1欠損時の骨格維持範囲は未確定である。

これは`pocket_sweeper_policy_gap`、`implementation_gap`または`evidence_conflict`、`human_evaluation_gap`として記録する。既存21曲でCH1 melodyが多いことを根拠にCH2へSFXを移す、またはCH1 melody方針を廃止する決定はしない。sound-specの整理、current implementation確認、必要な試聴へ戻し、SFX仕様自体は本WBSで変更しない。

## 7. Human evaluation loop

machine validationが成功しても、melodyの単調さ、loop fatigue、noiseの耳障りさ、SFX mute時の骨格崩れはHuman findingになり得る。

```text
Human finding
  → 問題をmotif repetition / variation / rhythm / range / accompaniment / loop等へ分解
  → 既存Theory / Game-BGM ruleを確認
  → 根拠不足なら該当調査へ戻る
  → candidate ruleをprovisional/hypothesisで記録
  → scopeを限定して再生成
  → 再評価
```

「melodyが単調」から「4小節ごとに必ずvariation」のようなHard/default ruleを直接作らない。Human resultは対象環境、criteria、result、未解決事項とともに記録する。

## 8. Machine validation failure

|failure|扱い|新規ruleの要否|
|---|---|---|
|Hard constraint failure|既存rule違反としてgenerator/allocation/dataを修正|不要|
|Reference failure|motif/harmony/layer参照、schema、implementationを修正|通常不要|
|Format failure|JSON→UGE、value range、64-row/order、converter/analyzerを確認|tool/implementation調査|
|Soft-rule score低下|invalidにせずcandidate weightingやHuman evaluationへ戻す|通常不要|
|Human quality failure|Human evaluation loopへ戻す|根拠追加後に再判定|

01576のStage 1〜6と、problem type・戻り先を混同しない。allocation failureでTheory ruleを追加せず、format failureで音楽理論を変更しない。

## 9. New rule creation gate

新規ruleを`confirmed`または`conditional`で追加するには、次をすべて確認する。

1. 問題statementが具体的。
2. 既存ruleで説明できない。
3. source/evidenceが存在する。
4. source_type/evidence_typeが適切。
5. applicabilityが明確。
6. allowed_useが明確。
7. prohibited_inferenceが明確。
8. conflictが解消済み、または未解消状態が明示されている。
9. machine-checkabilityが整理されている。
10. implementation statusが分離されている。
11. Human evaluationが必要なら、完了済みか`needs_human_evaluation`のまま扱う。
12. 01575の必須schema項目を満たす。

条件を満たさない場合は`hypothesis`、`provisional`、`unresolved`、`needs_human_evaluation`のいずれかで保留する。

## 10. Rule modification gate

既存ruleの変更も同じgateを通す。特に、applicability拡大、Soft→Hard、hypothesis→confirmed、parameter candidate→default、Human finding→policyは変更理由、source/evidence、影響scope、conflict、supersessionを記録する。

## 11. Hypothesis / Provisional

仮説は作成できるが、generator defaultやHard constraintにはしない。根拠不足、調査先、実験scope、Human evaluation要否を明示する。

暫定値は次のようにscopeを限定する。

```yaml
status: provisional
allowed_use:
  - documentation
  - human_review
prohibited_inference:
  - composition_quality
  - default_parameter
applicability:
  conditions: [{purpose: experiment_or_test_fixture}]
open_issues: ["追加evidenceが必要"]
```

`conditional`は根拠不足ではなく、適用条件が限定されたruleを意味する。

## 12. Default value gate

21曲の平均・多数派、単一曲、「よくありそう」、AI推測、1回のHuman listeningからdefault値を作らない。defaultが必要な場合は、source、purpose、applicability、expected effect、alternatives、evaluation、uncertaintyを記録する。根拠と評価が不足する場合はdefaultを設定せず、parameterまたは明示入力とする。

## 13. Corpus observation

01574を強制する。corpus observationの許可用途はparser compatibility、format diversity、regression、edge-case discovery、structural comparisonに限る。composition quality、preferred channel role、default parameter、style generalization、musical naturalnessは禁止推論である。

コーパスから作曲ruleを提案したくなった場合、その提案自体をhypothesisとして記録し、theory、Game-BGM、hardware/tool、implementation、Human evaluationの適切な調査へ戻す。

## 14. Decision record

問題1件ごとに次を記録する。`rule status`と`decision resolution_status`は別物である。

```yaml
decision:
  id: DECISION-001
  problem_statement: "具体的な問題"
  problem_type: theory_gap
  stage: composition
  affected_rule_refs: []
  affected_layer_refs: []
  existing_evidence: []
  missing_evidence: []
  conflicts: []
  return_to:
    - source_type: music_theory
      work_item: "01560/01573系調査"
  hypothesis: null
  provisional_change: null
  human_evaluation_required: false
  machine_validation_required: true
  resolution_status: open
  resulting_rule_refs: []
  notes: "ruleをconfirmedにしない"
```

`resolution_status`は`open`、`researching`、`awaiting_implementation_check`、`awaiting_human_evaluation`、`resolved`、`rejected`、`superseded`を使用する。

## 15. Stop condition

調査しても根拠が得られない場合、confirmedにしない。次のいずれかで停止する。

- hypothesisのまま保留
- feature・layerを使用しない
- optional layerを省略
- 根拠とscopeを記録したconservative fallbackを使用
- Human evaluationへ送る
- 別WBSとして調査を追加

conservative fallback自体も、適用範囲、理由、代替案、open issueを持たせる。根拠のない「たぶんこれでよい」は採用しない。

## 16. Escalation

既存WBSで扱えるなら重複WBSを作らない。

|不足の性質|追加先|
|---|---|
|資料・概念の不足|新規theory/Game-BGM/hardware/tool調査WBS|
|仕様判断・default・policy|specification decision WBS|
|コードが未実装|implementation WBS|
|聴感・自然さ・疲労|Human evaluation WBS|
|既存WBSのscope外で複数分類にまたがる|統合decision/research WBS|

## 17. Supersession

根拠が変わったとき旧ruleを黙って書き換えず、01575の`supersedes`、`superseded_by`、`reason`を記録する。既存生成物・テストが参照する旧IDは削除・再利用しない。

## 18. 01576 layer / validation stageとの対応

|01576 stage|主な問題|戻り先の例|
|---|---|---|
|Stage 1 Composition|theory、reference、mode|01560/01573、rule evidence|
|Stage 2 Timeline|grid、loop、同期|01558/01561、timeline implementation|
|Stage 3 Allocation|4ch、capability、同時発音|01572、allocation implementation|
|Stage 4 Tool-format|JSON、UGE、hUGEDriver|01565、converter/analyzer|
|Stage 5 Runtime coexistence|SFX mute、preemption、degradation|sound-spec、implementation、Human evaluation|
|Stage 6 Human listening|自然さ、単調さ、fatigue|Human evaluation、theory/Game-BGM再調査|

layer modelの`composition`、`timeline`、`realization`、`allocation`、`tool_format`、`runtime_coexistence`、`human_listening`を`affected_layer_refs`へ記録できる。

## 19. Case A〜F

|case|判断|
|---|---|
|A: CH2へsweep voice|`GB-HARD-001`の既存Hard constraint違反。新rule不要。allocation/generatorを修正。|
|B: melodyが単調|Human findingをmotif、variation、rhythm、range、accompaniment、loopへ分解。4小節ごとのHard/defaultを即追加せず、theory/Game-BGM/Human loopへ戻す。|
|C: 既存21曲でCH3使用率が高い|`corpus_observation`として形式・回帰にのみ保持。`bass=CH3`は作らない。|
|D: CH1 SFXで骨格崩れ|Pocket Sweeper policy gap + implementation/evidence conflict + human evaluation gap。CH2/CH4方針との競合を記録し、sound-spec整理・実装確認・試聴へ戻す。|
|E: JSON→UGE変換不能|tool/formatまたはconverterを確認。音楽理論ruleを追加しない。|
|F: cadenceが不自然|Human findingを選択harmony mode、theory、Game-BGM loop context、再評価へ戻す。普遍cadence ruleにしない。|

## 20. Review checklist

1. 問題は具体的か。
2. 既存ruleで説明できないか。
3. 発生stageはどこか。
4. problem typeは何か。
5. questionに適切なevidence typeか。
6. source/evidenceは存在するか。
7. applicabilityは明確か。
8. corpus observationを品質根拠にしていないか。
9. Human findingを普遍化していないか。
10. capability/constraintを混同していないか。
11. Soft/Hardを混同していないか。
12. implementation不足をrule不足にしていないか。
13. conflictは解決または明示されているか。
14. statusは根拠に合っているか。
15. allowed/prohibited useがあるか。
16. machine/Human validationの要否が明確か。
17. supersessionが必要か。
18. 新規WBSが本当に必要か。

## 21. 未確定事項と実装範囲

decision recordの実データをどのWBSで管理するか、default gateの承認者、Human evaluation WBSの共通環境、SFX conflictのresolution owner、conservative fallbackの個別定義は未確定である。

本WBSではworkflow文書とWBSのみを変更し、generator、analyzer、converter、game code、自動rule engine、decision engineは実装しない。
