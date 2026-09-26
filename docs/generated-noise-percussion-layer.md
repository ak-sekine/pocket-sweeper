# 生成logical Noise/percussion layer

対象WBS: `WBS-001-01584`

## Scope

`generate_noise()` は01580の`CompositionStructure`上にNoise pattern definition/instanceとeventを生成する。結果はlogical noise/percussion layerで、physical channelは未割当（`null`）である。CH4、NR41〜NR44、LFSR、width、clock shift、divisor、envelope、hUGE Instrument、UGE Noise note index、SFX共存は扱わない。

## Event / role / character

Noise eventは通常pitchを持たず、duration、rest、rhythmic `role`、caller-defined symbolic `character_ref`、accentを持つ。roleとcharacterは別概念であり、kick/snare/hat等を使う場合もlogical labelに留める。logical characterからCH4 hardware parameterへのmappingは行わない。

初版variationは`exact`だけとし、fill、ghost note、syncopation、density change等の自動生成はしない。patternがphraseより短い場合は明示restで末尾を補完し、単一logical noise voice内のoverlapを禁止する。いずれも音楽理論やhardwareの普遍的規則ではなく、初版generatorのmodel constraintである。

## 再現性・境界

01579のsingle shared `GenerationContext`を利用する。同じcontext呼び出し順、structure、parameters/options、seedなら同じserializationを得る。noise layer単独で生成でき、melody・伴奏・bassは入力必須ではない。

CH4がLFSR noise channelであることはhardware capabilityとして後段で参照できるが、logical NoiseをCH4へ固定しない。SFXによるCH4占有、mute、復帰、degradationは01585へ委譲する。

## 未確定事項

role vocabulary、character vocabulary、rhythm pattern、density、accent、syncopation、fill、複数percussion voice、他layerとのバランス、physical allocation、LFSR/NR43 mapping、Instrument、SFX欠損時の聴感、Human evaluationは未確定である。

21曲UGEからrhythm、density、character、CH4 allocation、Noise pitch、hardware値、default weightを導出していない。自動検証は構造・参照・範囲を対象とし、「良いリズム」や「良いNoise音色」は判定しない。
