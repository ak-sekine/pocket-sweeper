# 生成楽曲からGame Boy楽曲データへの変換契約

## 目的と範囲

01587は、01579〜01585のlogical compositionを、MIDIを経由せず既存のJSON Version 2へ変換する決定的なadapterである。ASM、UGE、ROM生成は01588以降の責務とする。JSON Version 3は追加しない。

入力はCompositionStructure、logical layer、明示的なLayerAllocation、pitch/instrument/noiseのresolution contextである。layerの種類からCH1〜CH4を暗黙に決めない。

## 物理割当と検証

01585のallocation validatorを先に実行し、machine violationがあれば変換を拒否する。変換先は明示的に `CH1=pulse1`、`CH2=pulse2`、`CH3=wave`、`CH4=noise` と対応するが、どのlogical layerを割り当てるかはcallerの入力である。logical objectへphysical channelを書き戻さない。

CH1/CH4のSFX占有、CH2のfuture SFX、CH3のcurrent policyはallocation validationの結果とhuman-review metadataとして扱う。変換成功はSFX時の聴感品質を保証しない。

## 時間・pattern・order

callerが指定する整数 `ticks_per_row` によりtickをVersion 2 rowへ写像する。start、duration、section durationが正確に割り切れない場合は丸めず拒否する。初版は各sectionを1 pattern、section順をchannel orderとし、patternは1〜64 rowに収める。これは変換adapterの制約であり、phraseが常にpatternであるという音楽理論上の規則ではない。

Version 2のloop表現へ次のように写像する。

- `none` → `{"mode":"none"}`
- `full` → `{"mode":"full"}`
- `range` → section/order境界に開始点があり、終端が曲末の場合だけ `start_order` と `end_order` へ変換

logical loopとUGEのB effectは同一概念ではない。Version 2で表現できないloop intentはsilent fallbackしない。

## pitch、harmony、instrument、noise

pitched channelは初版ではcallerが `absolute_pitch` を解決済みで、整数値からnote名への `absolute_pitch_map` がある場合だけ変換する。relative interval、scale degree、未解決のharmony_refからC major等を推測しない。

instrument IDとchannelの対応はcaller-supplied `instrument_by_channel` と既存instrument定義で検証する。duty、wave table、output level、envelope等を推測しない。

Noise channelは通常pitchとして扱わず、`character_ref` をcaller-supplied `noise_character_map`で既存JSONのnoise note表現へ解決する。LFSR、NR43、hUGE instrumentの具体値はこのWBSの対象外である。

## 決定性と未解決入力

変換自体は乱数を使用しない。同じlogical input、allocation、resolution context、conversion parametersで同じdictを返す。生成version `0.2.0`は生成アルゴリズムを変更していないため維持する。converterの入力契約が変更される場合は別途識別する。

必要なkey/scale、harmony、register、instrument、wave、noise mapping、quantizationが不足する場合、fallbackせず `GenerationInputError` とする。これらは01577のworkflowで調査またはcaller policyへ戻す。

## 根拠とコーパス

JSON Version 2と既存converterを形式上の正本として再利用する。01572/01576/01585のhardware・allocation制約を適用し、01573の理論から具体的なkeyやprogressionを新規推測しない。21曲UGEは品質、default、allocation、pitch resolution、quantizationの根拠に使用しない。

## 後続WBSとHuman evaluation

01588以降がJSONからhUGEDriver ASM、UGE、ROM、実行確認を担当する。変換テストは構造・値域・参照整合性を検証するだけで、曲の自然さ、instrumentの適切さ、SFX欠損時の聴感は判定しない。CH1 Pulse1 SFXとmelody候補の競合、3ch/4ch方針、SFX復帰時の聴感は未解決事項として保持する。
