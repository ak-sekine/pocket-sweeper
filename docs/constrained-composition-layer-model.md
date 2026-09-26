# 制約付き作曲レイヤーモデル

対象WBS: `WBS-001-01576`

## 1. 目的と設計原則

melody、motif、rhythm、harmony、bass、accompaniment、noise/percussionを独立した論理layerとして管理し、共通時間軸、Game Boyのphysical channel、JSON/UGE/hUGEDriver、loop、SFXによる一時欠損を段階的に検証できる表現を定義する。

最重要原則は`logical layer != physical channel`である。CH1=melody、CH2=accompaniment、CH3=bass、CH4=noiseは候補allocationであり、hardwareや一般理論から必然的に導出しない。

本書はmodel、reference、constraint、validation stageを定義する。最終key、scale、tempo、meter、progression、motif、phrase長、channel allocation、default weight、generator algorithm、JSON Version 3は決めない。

## 2. 3段階モデル

### A. Composition model

曲全体の音楽的意味を持つ状態。`key`、`scale`、`meter`、`tempo`、`form`、`loop region`、harmony、motif、phrase、layerの意図を持つ。未決定値を`null`にできる。

### B. Logical timeline / layer model

共通musical time grid上のevent。layer、start、duration、pitch/relation、rest、accent候補、motif/harmony/rhythm参照、`rule_refs`、degradation metadataを持つ。まだCH番号やUGE patternを持たない。

### C. Physical allocation

logical voiceをGame Boy channel、Instrument、hUGE/JSON表現へ割り当てる段階。channel capability、1channel 1発音、4ch上限、tool値域、SFX占有をここで検査する。

```text
composition context
  → logical timeline / layers
  → harmony realization / logical voices
  → constrained allocation
  → JSON / UGE / hUGEDriver
```

## 3. 共通musical time grid

一般音楽時間とhUGE row/pattern/orderを分離する。少なくともmeasure、beat、subdivision、absolute position、durationを表す整数gridを持つ。

候補は`ticks_per_beat`を曲contextで定義し、eventが`start_tick`と`duration_tick`を持つ形式である。`measure`や`beat`は表示・検証用に導出できる。

```yaml
time_grid:
  ticks_per_beat: null
  meter: null
  subdivision: null
  events_use_integer_ticks: true
```

`1 beat = 1 hUGE row`とは定義しない。quantization後にhUGE rowへ写像し、64-row patternとorderへ分割する。浮動小数点を正本の時間値にせず、必要な分解能を整数gridで選択するが、`ticks_per_beat`の最終値は未決定とする。

## 4. Global musical context

曲ごとに次を共有contextとして持ち、各noteへ重複保存しない。

```yaml
context:
  key: null
  scale: null
  meter: null
  tempo: null
  time_grid_ref: null
  form: null
  loop_ref: null
```

key/scaleが未決定でもtimelineを保持できる。eventは必要に応じてscale degree、relative interval、absolute pitch候補を持つ。最終pitchへのresolveはallocation/export前の責務候補であり、唯一の実装方式として固定しない。

## 5. Harmony timeline

harmonyはphysical channelではなく時間軸上のcontextである。

```yaml
harmony:
  - id: harmony-001
    start_tick: 0
    duration_tick: 16
    root: null
    chord_tones: []
    inversion: null
    function: null
    rule_refs: []
```

melody、bass、accompanimentは`harmony_ref`で参照する。`root`と`bass_note`は別概念であり、inversion、passing、pedalを表現できる。harmony境界とloop boundaryはtimeline上で検証するが、特定progressionやfunctionをdefault化しない。

## 6. Motif definition / instance

motifは絶対note列やphysical channelではなく、次の関係の組合せとして定義候補を持つ。

- relative pitch / scale degree
- interval
- rhythm、duration、rest
- accent
- transformation metadata

```yaml
motifs:
  - id: motif-001
    pitch_relation: []
    rhythm_relation: []
    duration_relation: []
    rest_relation: []
    accent_relation: []
motif_instances:
  - id: motif-instance-001
    motif_ref: motif-001
    start_tick: 0
    transformation: null
    rule_refs: []
```

instanceはtranspose、rhythmic variation、pitch variation、register variation、layer variationを記録できる。高度なtransformation engineや具体motifは実装・確定しない。

## 7. Melody layer

melody eventは最低限、start、duration、pitchまたはscale-degree relation、rest、motif_ref/instance_ref、harmony_ref、accent/weight候補、`rule_refs`を持つ。

```yaml
layers:
  - id: melody-001
    type: melody
    structural_role: primary_candidate
    optional: null
    events:
      - id: melody-event-001
        start_tick: 0
        duration_tick: 2
        pitch: null
        scale_degree: null
        rest: false
        motif_instance_ref: null
        harmony_ref: harmony-001
        rule_refs: []
```

step/leap、contour、range、repetitionはSoft rule/parameterであり、固定禁止ではない。

## 8. Rhythm layer

rhythmはmelody eventの副作用にせず、独立patternとして管理する。onset、duration、rest、accent、subdivision、syncopation候補、densityを持ち、melody、bass、accompaniment、noiseが同じrhythm_refを共有または別patternを参照できる。

`rhythm_ref`とeventのstart/durationの整合、restの重複、loop範囲、phrase boundaryを検証する。具体的density、accent、syncopationのdefaultは決めない。

## 9. Bass layer

bassは抽象layerで、`harmony_ref`、root/chord-tone/passing/pedal/ostinato relation、absolute/relative pitch、`rhythm_ref`、register候補を持つ。`bass = CH3`や`bass note = chord root`を固定しない。

allocation時にはCH3 wave、CH1/CH2 pulse等を候補として検査できるが、最終channelは決定しない。bassの聞き取りやすさ、register、waveform、densityはHuman evaluation対象である。

## 10. Accompaniment layer

accompanimentは、sustained tone、chord tone、arpeggiation、broken chord、counter-line、rhythmic supportを`realization`候補として表現する。抽象chordと実際の単音イベントを分離する。

```text
abstract chord → accompaniment realization → logical voices → allocation
```

CH2固定にはしない。melodyへのmasking、欠落時の調性・phrase維持、SFX復帰時の自然さはHuman evaluationへ送る。

## 11. Noise / percussion layer

noise layerはrhythmic role、onset、duration、accent、density、noise character candidateを管理する。CH4のJSON noteは通常pitchではなくNoise pitch indexであり、melodyのpitch modelをそのまま適用しない。

CH4のwidth、clock shift、divisor、envelope等はhardware/tool layerで扱い、kick/snare/hatという聴感ラベルとは分離する。CH4を使わないlayerも表現可能とし、noiseだけへbeat、motif、loop boundaryの必須情報を置かない候補を検証できるようにする。

## 12. Optional layer / priority / skeleton

各layerに`required`、`optional`、`omittable_under_pressure`等のmetadataを持たせる候補を定義する。ただしmelodyを絶対必須とはしない。

```yaml
layer_policy:
  optional: null
  structural_role: null
  allocation_priority: null
  drop_degrade_policy: null
```

`structural_role`は、melody、tonal_context、beat、phrase_progression、loop_position等の論理的な保持対象を表す。`allocation_priority`の数値やdefaultは決めない。

sound-specの骨格概念（melody、tonality/chord progression、beat、phrase progression、loop position）をlogical layerで参照できるようにするが、特定channelへ固定しない。

## 13. Physical channel capability

01572のRule IDを参照してallocationを検査する。

|channel|capability|allocation上の禁止・注意|rule_ref|
|---|---|---|---|
|CH1|pulse、sweep capability|sweep要求はCH1以外へ割り当てない|`GB-HW-005`、`GB-HARD-001`|
|CH2|pulse、CH1相当sweepなし|CH1 sweepを要求するvoiceを割り当てない|`GB-HW-005`|
|CH3|wave、Wave table/output level|pulse/Noise envelopeを適用しない|`GB-HW-006`、`GB-HW-007`|
|CH4|LFSR noise|通常pitched melodyをそのまま割り当てない|`GB-HW-008`、`GB-TOOL-004`|

CH1ならmelody、CH3ならbassという逆方向の推論は禁止する。

## 14. Allocation constraint

allocation recordはlogical layer、logical voice、physical channel、Instrument、tool representation、`rule_refs`を分離する。

```yaml
allocation:
  assignments:
    - logical_layer: melody-001
      logical_voice: voice-001
      physical_channel: null
      instrument_ref: null
      representation: null
      rule_refs: []
```

最低限、次を検査する。

- 最大4 physical channel
- 1 physical channelは同時に1発音状態
- 1 logical voiceの同時割当先が不正に複数でない
- channel capability、pitch/range、Instrument/channel整合
- optional layerの省略可否
- SFX reservation/preemptionとの衝突
- JSON/UGE/hUGEDriverの表現可能範囲

同時harmonyが3音でも、必ず3channelを消費させない。realizationでsustained tone、arpeggio、broken chord、note omission、reduced voicingを選択できる。

## 15. Constraint分類とRule reference

constraintは次の分類で管理する。

- `musical`
- `temporal`
- `allocation`
- `hardware_reference`
- `tool_format_reference`
- `pocket_sweeper_policy`
- `degradation`
- `validation`

```yaml
constraints:
  - id: ALLOC-001
    kind: allocation
    statement: "sweepを要求するvoiceはCH1以外へ割り当てない"
    rule_refs:
      - GB-HW-005
      - GB-HARD-001
    machine_checkability: true
    implementation_status: planned
```

01575のRule IDを`rule_refs`で参照する。新しいIDが必要な場合は既存prefixと衝突しない暫定IDを使い、根拠記録を付与する。

## 16. Hard / Soft / Parameter

### Hard constraint候補

- 選択mode内部のkey/scale/chord relation整合
- event start/durationのgrid整合
- loop boundaryと全layer timelineの同期
- 4ch上限、1channel 1発音
- physical channel capability、pitch/range、Instrument整合
- JSON/UGE/hUGEDriverの形式・値域整合
- SFX preemption対象とdegradation metadataの整合

### Soft rule候補

- melody contour、step/leap、voice-leading
- motif reuse/variation
- harmonyとbass/chord-tone relation
- rhythm density、accent、syncopation
- accompanimentのmasking、noiseのforeground化
- layer欠落時の骨格維持の優先度

### Parameter候補

key、scale、tempo、meter、ticks_per_beat、phrase/motif length、layer optionality、allocation priority、bass relation、accompaniment realization、noise density、variation amount、loop region、SFX degradation policy。

Soft rule違反はinvalid songとしない。具体値と最終allocationは後続設計・Human evaluationへ残す。

## 17. SFX reservation / preemption

現行仕様・実装として、Pulse1 SFXはCH1、Noise SFX/カーソルSFXはCH4を一時占有し、`hUGE_mute_channel`でBGMをmuteする。BGMのorder/row位置は進行し、終了時に対象channelをunmuteする。

```yaml
channel_availability:
  ch1:
    bgm_available: true
    may_be_preempted_by: [pulse1_sfx]
  ch4:
    bgm_available: true
    may_be_preempted_by: [noise_sfx, cursor_sfx]
```

このblockは現行仕様の記録であり、将来のSFX割当変更を決定しない。SFX reservationとlogical layer roleを別に管理する。

## 18. Graceful degradationと未解決conflict

```yaml
degradation:
  may_drop: true
  max_loss_scope: null
  preserve:
    - melody
    - tonal_context
    - beat
    - phrase_progression
    - loop_position
  preemption_refs: []
  rule_refs: [PS-SOUND-001]
```

sound-specには、CH2/CH4が一時muteされてもCH1+CH3で骨格を保つ方針がある。一方、現行SFX実装はCH1/CH4を占有する。CH1占有時のmelody欠損と、CH2/CH4欠損耐性の記述を「CH2へSFXを変更する」「CH1 melody方針を廃止する」と推測で解決しない。

|項目|現行確認|01576の扱い|
|---|---|---|
|Pulse1 SFX|CH1を占有|current occupancyとして記録|
|Noise SFX|CH4を占有|current occupancyとして記録|
|BGM欠損方針|CH2/CH4欠損耐性の記述あり|intended policy候補|
|CH1欠損時の骨格|適用範囲が未確定|`conflicts`/`open_issues`へ保留|

## 19. Loop

logical loopは全layerで共通の`loop_ref`を参照し、loop start/endがgrid上、phrase boundary、harmony boundary、motif instance boundaryと整合するかを検証候補にする。physical order mappingは後段に保持する。

JSON Version 2の`none`、`full`、`range`と、UGE上のimplicit cycle/B effectは同一概念ではない。JSONの意図をUGEのB effectだけから復元しない。loop semantic、logical boundary、UGE mappingを別フィールドにする。

## 20. Pattern / order mapping

```text
musical timeline
  → quantization
  → channel events
  → 64-row patterns
  → order
  → UGE / hUGEDriver
```

logical eventを直接hUGE rowへ固定しない。既存JSON/converterで仕様化済みの、64-row pattern、note lengthのrow展開、rest/effect、channel order同期を優先して参照する。

pattern境界を跨ぐeventのsplit、continuation、rest expansion、note retriggerの選択は変換責務候補として記録するが、本WBSで新規規則を推測して確定しない。

## 21. Machine validation matrix

|段階|検証候補|machine checkability|実装状態|
|---|---|---|---|
|Composition|layer/harmony/motif/rule referenceの存在・relation整合|partial|planned|
|Timeline|start/duration、grid、同期、loop boundary|true/partial|planned|
|Allocation|channel存在、4ch、1channel 1発音、capability、Instrument|true|既存toolの範囲＋planned|
|Tool-format|JSON/UGE、64-row、order、pitch/range、Wave/Noise|true/partial|既存converter/analyzerの範囲|
|Runtime coexistence|SFX reservation、preemption、degradation metadata|partial|planned|
|Human listening|自然さ、単調さ、欠損時の聴感|false|not_started|

具体的検証項目は、event start/duration > 0、layer/motif/harmony参照、harmony coverage、loop整合、allocation先、sweep CH1限定、Wave/Noise制約、pitch/range、instrument/channel整合、quantize可能性、64-row/order mapping、SFX識別である。

## 22. Validation stages

1. **Stage 1 Composition validation**: 音楽的reference、mode、layer relation。
2. **Stage 2 Timeline validation**: integer grid、同期、loop、phrase/harmony境界。
3. **Stage 3 Allocation validation**: 4ch、capability、同時発音、optional layer。
4. **Stage 4 Tool-format validation**: JSON、UGE、hUGEDriver、64-row/order。
5. **Stage 5 Runtime coexistence validation**: SFX mute/preemption、degradation metadata。
6. **Stage 6 Human listening**: 自然さ、単調さ、欠損、noise density、loop fatigue。

Stage 6をStage 1〜5の自動検証結果で代替しない。

## 23. Structured example（架空）

```yaml
composition:
  context:
    key: null
    scale: null
    meter: null
    tempo: null
    time_grid_ref: grid-001
    loop_ref: loop-001
  harmony:
    - id: harmony-001
      start_tick: 0
      duration_tick: 16
      root: null
      chord_tones: []
      inversion: null
      function: null
      rule_refs: []
  motifs:
    - id: motif-001
      pitch_relation: []
      rhythm_relation: []
      transformation: null
  layers:
    - id: melody-001
      type: melody
      structural_role: primary_candidate
      optional: null
      events: []
    - id: bass-001
      type: bass
      structural_role: support_candidate
      optional: true
      events: []
allocation:
  assignments: []
```

これはschema例であり、Pocket Sweeperのkey、tempo、channel allocationを確定するデータではない。

## 24. 21曲UGEの扱い

既存21曲からlayer schema、channel role、priority、motif/rhythm template、progression、density、allocation probabilityを決めない。01574どおり、format compatibility、regression、structural diversityの検証にのみ利用する。固定patternのコピーも前提にしない。

## 25. Human evaluation

layer priority、graceful degradation、melody自然さ、accompanimentの干渉、noise density、loop fatigue、SFX muteからの復帰はHuman evaluation対象である。本WBSでは試聴、GUI、SameBoy、実機確認を行わず、`human_evaluation_status: not_started`相当として残す。

## 26. 未確定事項

- ticks_per_beat、meter、tempo、key、scaleの最終値。
- motif/phraseの具体schemaとtransformation engine。
- layer priority、required/optionalの最終policy。
- harmony realization、4ch allocation algorithm、channel sharing。
- pattern境界を跨ぐeventのsplit/continuation/retrigger規則。
- CH1 SFX占有時のBGM骨格、CH2/CH4欠損方針の適用範囲。
- loop semanticとUGE mappingの最終contract。
- Human evaluationの対象曲、環境、判定基準。

## 27. 01577への引き継ぎ

01577では、本書のlogical layer、rule_refs、constraint、status、conflict、open issueを使い、根拠不足やSFX conflictを勝手に新規ruleへ昇格させず、理論・Game-BGM・hardware/tool・implementation・Human evaluationの適切な調査へ戻す運用を定義する。
