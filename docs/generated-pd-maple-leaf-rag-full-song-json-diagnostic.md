# Structure-aware ArrangementPlan → full-song JSON診断

## 目的

現行の1 pattern/64-row/1 orderによるArrangementPlan→JSON lossを、JSON V2のmulti-pattern/orderで分離して確認した。ArrangementPlan自体は変更していない。

## Mapping

`pattern_index = absolute_row // 64`、`local_row = absolute_row % 64`を使用し、4 channelで同じorder長を生成した。source repeat/loopは推測せず、JSON loopはnoneとした。

- max absolute row: 3680
- required pattern/order count: 58
- channel patterns: pulse1/pulse2/wave/noise 各58（empty patternを含む）
- source-derived ArrangementPlan events: 2035
- current single-window JSON notes: 30
- full-song JSON note tokens: 2035 candidatesをpatternへmapping（token/cursor境界の詳細はsidecarで追跡）

## Format validation

full-song JSONは既存JSON V2のchannel別order/pattern構造に従い、UGE生成に成功した。UGE sizeは317990 bytesで、multi-pattern/order表現自体はconverterへ入力可能だった。

## ROM boundary

既存`build_sound_test_rom.py`でASM生成までは進んだが、RGBDS assemblerが次で失敗した。

`Section "full_song Song Data" grew too big (max size = 0x4000 bytes, reached 0xB119)`

したがってfull-song ROMは生成できていない。原因はfull-song dataが既存sound-test ROMの単一section上限を超えたことであり、Human試聴へ進む前にROM builder/バンク配置/runtime contractの設計判断が必要である。今回、JSON V2やROM builderを無断変更していない。

## Current vs full-song

| metric | current single window | full-song emitter |
|---|---:|---:|
| ArrangementPlan events | 2035 | 2035 |
| JSON source-derived notes/tokens | 30 | 2035 candidates |
| patterns/order | 4/1 | 58/channel, 58 synchronized orders |
| UGE | 68KB | 317990 bytes |
| ROM | existing prototype possible | blocked by 0x4000 section |

Machine format validationは成功したが、full-song音楽品質・Human聴感は未評価である。
