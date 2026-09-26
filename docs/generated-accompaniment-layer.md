# 生成logical accompaniment layer

対象WBS: `WBS-001-01582`

## Scope

`generate_accompaniment()` は01580の`CompositionStructure`を共通時間軸として、伴奏pattern definition/instanceとeventを生成する。結果はlogical layerであり、physical channelは未割当（`null`）である。CH2、pulse設定、Instrument、UGE mapping、bass、noise、SFX共存は扱わない。

## Harmony境界

本WBSではharmony progressionやC major/I-IV-V-I等を生成しない。pattern step/eventはcaller-suppliedな`harmony_ref`を保持でき、利用する場合は`AccompanimentGenerationOptions.harmony_refs`に存在する参照だけを許可する。harmony contextなしで使える初版realizationは`rhythmic_support`、`sustained_tone`、`repeated_tone`とし、chord-tone/arpeggiation/broken-chordは未実装として拒否する。

chord root、bass note、伴奏pitchは別概念であり、rootを常時鳴らす規則やbassとの同一視は行わない。抽象harmonyからrealization、logical event、physical allocationへ進む層分離を維持する。

## Patternとevent

`AccompanimentPatternDefinition`と`AccompanimentPatternInstance`を分離し、instanceはpattern、phrase、開始tick、transformationを参照する。step/eventはduration、rest、relative interval、scale degree、absolute pitch、harmony reference、accentを保持する。非restのpitch relationは1種類だけ、restはpitch/harmony referenceを持たない。

固定parametersと候補optionsを分け、pattern・variation・offsetは呼び出し側が決める。初版variationは`exact`と`relative_interval_offset`で、同一logical voice内のoverlapは禁止するmodel constraintである。phrase末尾は明示rest eventで補完する。

## 再現性・検証・未確定事項

01579のsingle shared `GenerationContext`を利用する。同じcontext呼び出し順、structure、parameters/options、seedなら同じserializationを得る。key/scale、harmony progression、chord-tone realization、register、density、repetition/variation default、melody masking、複数logical voice、CH2を含むallocation、UGE mapping、SFX欠損時の聴感は未確定またはHuman evaluation対象である。

21曲UGEからpattern、rhythm、density、register、CH2 allocation等を導出していない。自動検証は形式・参照・範囲の成立性を対象とし、「良い伴奏」やmelodyを邪魔しないことは判定しない。
