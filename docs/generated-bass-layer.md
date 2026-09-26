# 生成logical bass layer

対象WBS: `WBS-001-01583`

## Scope

`generate_bass()` は01580の`CompositionStructure`上にbass pattern definition/instanceとeventを生成する。結果はlogical layerで、physical channelは未割当（`null`）である。CH3、Wave table、output level、Instrument、UGE mapping、melody・伴奏・noiseとの最終編成、SFX共存は扱わない。

## Relationとpitchの分離

`BassEvent`は音楽的な`bass_relation`とpitch表現を別々に保持する。relation候補は`root`、`chord_tone`、`passing`、`pedal`、`ostinato`であり、pitchはrelative interval、scale degree、absolute pitchのいずれかである。root relationを選んでもbass noteが常にchord rootになるというHard/default規則にはしない。

`harmony_ref`はcaller-suppliedな参照を保持できるが、harmony progressionやHarmony timelineは本WBSで生成しない。参照IDの存在だけを検証し、そのharmonyが時刻をcoverするかは未実装のHarmony modelに委譲する。

## Patternと検証

`BassPatternDefinition`と`BassPatternInstance`を分離し、instanceはpattern、phrase、開始tick、transformationを参照する。restはrelation/pitch/harmony referenceを持たず、非restはpitch relationを1種類だけ持つ。初版variationは`exact`と`relative_interval_offset`、単一logical bass voiceのoverlap禁止、phrase末尾の明示rest補完を採用する。これらは初版generator model constraintであり、音楽理論上の普遍的規則やCH3制約ではない。

## 再現性・未確定事項

01579のsingle shared `GenerationContext`を使う。同じcontext呼び出し順、structure、parameters/options、seedなら同じserializationを得る。key/scale、harmony progression、root/chord-tone解決、passing/pedal/ostinatoの具体化、register、density、default pattern、physical allocation、CH3/Wave、UGE mapping、SFX欠損時の聴感は未確定またはHuman evaluation対象である。

21曲UGEからrelation比率、rhythm、register、CH3 allocation、wave table、volume等を導出していない。自動検証は構造・参照・値域を対象とし、「良いbass」やmelodyとの分離は判定しない。
