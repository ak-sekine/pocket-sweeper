# Structure-aware ArrangementPlan → full-song JSON診断

## 目的

現行の1 pattern/64-row/1 orderによるArrangementPlan→JSON lossを、JSON V2のmulti-pattern/orderで分離して確認した。ArrangementPlan自体は変更していない。

## Mapping

`pattern_index = absolute_row // 64`、`local_row = absolute_row % 64`を使用し、4 channelで同じorder長を生成した。source repeat/loopは推測せず、JSON loopはnoneとした。

- max absolute row: 3680
- required pattern/order count: 58
- channel patterns: dedup前は各58、dedup後は pulse1=58 / pulse2=57 / wave=57 / noise=1
- source-derived ArrangementPlan events: 2035
- current single-window JSON notes: 30
- full-song JSON note tokens: 2035 candidatesをpatternへmapping（token/cursor境界の詳細はsidecarで追跡）

## Format validation

full-song JSONは既存JSON V2のchannel別order/pattern構造に従い、UGE生成に成功した。UGE sizeは317990 bytesで、multi-pattern/order表現自体はconverterへ入力可能だった。

## ROM boundary

既存`build_sound_test_rom.py`でASM生成までは進んだが、RGBDS assemblerが次で失敗した。

初回は `Section "full_song Song Data" grew too big (max size = 0x4000 bytes, reached 0xB119)` だった。pattern fingerprintから`source_event_id`を除外して同一演奏patternを共有しても、再試行は `reached 0x84D9` となり、なお上限を超えた。

したがってfull-song ROMは生成できていない。hUGEDriverのsong descriptor/order/pattern参照は16-bit addressで、bank番号を保持せず、`load_patterns`にもbank切替がない。sound-test ROMは`rgbfix -m ROM -r 0x00`でMBCなしである。よって、単純にpatternを別ROM bankへ置く方式は現行runtimeでは再生可能と確認できない。dedupだけでは解決せず、bank-aware runtimeまたは別の容量削減方式の設計が必要である。

## Size breakdown

生成ASMでは1 patternがhUGEDriverの64行固定データ（`dn` 3バイト×64）として出力される。dedup後も4 channel合計173 pattern定義があり、pattern dataがsectionの主要因である。order pointer tablesは各channel 58参照、descriptor/instrument/wave metadataはpattern dataより小さい。UGEファイルサイズ317990 bytesは圧縮前のcontainerサイズであり、sectionの`0x84D9`と同一視しない。

## Current vs full-song

| metric | current single window | full-song emitter |
|---|---:|---:|
| ArrangementPlan events | 2035 | 2035 |
| JSON source-derived notes/tokens | 30 | 2035 candidates |
| patterns/order | 4/1 | 58/channel, 58 synchronized orders |
| UGE | 68KB | 317990 bytes |
| ROM | existing prototype possible | blocked by 0x4000 section |

Machine format validationは成功したが、full-song音楽品質・Human聴感は未評価である。
