# 生成Composition構造

対象WBS: `WBS-001-01580`

## Scope

`tools/bgm_generator.py` の構造生成は、seed付きで曲全体のtime grid、section、phrase、form、logical loopを生成する。音符、motif、chord、各layerの内容、Instrument、physical channel、UGE pattern/order、SFX共存は後続WBSの責務である。logical layerとphysical channelを固定対応させない。

## 入力と候補

`StructureParameters` は `ticks_per_beat`、`beats_per_measure`、必要ならphrase長・section phrase数・loop modeを固定値として受け取る。未指定値は `StructureGenerationOptions` の呼び出し側が明示した候補から `GenerationContext` で選ぶ。候補が空の場合はエラーとし、4/4、4小節、full loop等を暗黙のPocket Sweeper defaultにしない。

## Time gridとtimeline

正本の時間値は整数tickで、`ticks_per_measure = ticks_per_beat * beats_per_measure`から導出する。start、duration、endを検証し、初版の構造modelはsectionとphraseが隙間なく連続し、phraseがsectionを覆うtimelineに限定する。これは音楽理論上の必須条件ではなく、後続layerが共通境界を参照しやすくする生成model上の制約である。

sectionは一意ID、順序、時間範囲、phrase参照を持つ。phraseは一意ID、section参照、順序、時間範囲を持つ。`as_dict()` はJSON化しやすい決定的な辞書を返すが、現行公開JSON Version 2やJSON Version 3ではない。

## Logical loop

`none` は境界なし、`full` は0からtotal duration、`range` は指定されたphrase境界の範囲である。これはlogical loopであり、UGEのB effectやJSONのorder mappingとは同一視しない。phrase境界へのrange限定は初版実装の表現制約であり、最終的な音楽方針として確定していない。

## 再現性とversion

同じgenerator version、入力parameters/options、seedで同じ構造とserializationを生成する。構造生成を追加したためgenerator versionは`0.2.0`へ更新した。乱数は01579のshared single streamを消費し、layer別sub-streamは後続で判断する。

## Rule/evidenceと未確定事項

構造は後続layerが参照する骨格であり、具体的なphrase長・form・loop長を21曲UGEの多数派から決めない。Game-BGM調査はloop境界や反復疲労を評価対象にする根拠であって、数値defaultを導出する根拠ではない。最終meter、tempo、grid分解能、phrase/form/loop default、phrase途中loopの許否、hUGE row/order mapping、layer別random streamは未確定である。

01581〜01584はこの構造を参照して各logical layerを生成し、01585がphysical/tool/runtime制約を扱う。
