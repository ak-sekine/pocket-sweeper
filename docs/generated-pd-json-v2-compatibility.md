# PD自動編曲結果のJSON Version 2適合性確認

対象: WBS-001-01689
確認日: 2026-09-27

## Scope

01688のArrangementPlanを現行JSON Version 2へ渡す境界を確認した。JSONはMusicXMLの保存形式ではなく、編曲済みの再生データを既存JSON→UGE/ASM→ROMへ渡す契約として扱う。今回は仕様・converter・validator・テストを確認したが、JSONやconverterは変更していない。

## Confirmed JSON Version 2 contract

`docs/json-format.md`と`tools/json_to_uge.py`から、Version 2は`version`、`title`、`type`、`tempo`、`instruments`、channel別`order`/`patterns`、`loop`を扱う。channel名は`pulse1`、`pulse2`、`wave`、`noise`で、使用channelのorder数は一致し、pattern展開は64行以内である必要がある。noteは`note`（または`rest`）、`length`、`instrument`、任意の`volume`、`effect`、`effect_param`を持つ。

Version 2の`loop`は必須で、`full`、`range`、`none`を持つ。rangeは`start_order`と`end_order`を要求し、実装はendを全order数に制限する。`tempo`はBPMではなくSong Version 6/hUGEDriverのTicksPerRowとして正の整数で扱われる。Wave tableはVersion 2では対象外で、Version 1側の契約を含むため、実際のchannel/instrument仕様を混在させない。

## Existing converter behavior

### JSON to UGE

`tools/json_to_uge.py`はheader、JSON version、instruments、wave tables、channel order/pattern、loop、tempoを検証し、4channel OrderMatrix、pattern cell、instrument bank、wave/noise dataを生成する。Version 2のrange loopは最終orderのCH1 row 63へjump effectを付与する。order matrixは4channelで、使用channel order数が揃っている必要がある。source part名、MusicXML measure、原chord、loss report、provenanceは読まない。

### JSON to ASM

`tools/json_to_huge_asm.py`は同じJSON validator/build処理を使い、descriptorへtempo、4 order、duty/wave/noise instrument、routine、wave、Version 2 loop metadataを出力し、pattern cellを`dn note,instrument,effect`へ変換する。したがってArrangementPlanはphysical channel、row、Game Boy instrument、order/pattern、loop、TicksPerRowまで解決してJSON化する必要がある。

## Classification rule

- **A**: 現行JSONと既存converterが直接扱い、runtimeに必要な形。
- **B**: 前段adapter、manifest、sidecar、transformation reportで解決・保存でき、JSON変更不要。
- **C**: runtime生成に必要だが前段解決やsidecarでは代替できず、現行JSONで表現不能な場合だけ付ける。
- **D**: concrete source、prototype、実験、Human判断がないと確定できない。

## ArrangementPlan compatibility matrix

|ArrangementPlan情報|JSON V2表現|分類|根拠|adapter/manifest|downstream影響|unresolved|
|---|---|---|---|---|---|---|
|source/provenance identity|不要|B|converterは読まない|sidecar/manifest|なし|保存schema|
|source hash|不要|B|runtime入力ではない|manifest|なし|source未選択|
|normalized score reference|不要|B|編曲前の内部情報|report|なし|正規化形式|
|logical layers|physical channelへ解決|B|converterはlogical roleを読まない|mapping report|なし|allocation方法|
|source event対応|不要|B|変換追跡情報|sidecar|なし|loss記録|
|physical channel allocation|4 channel order/pattern|A|JSON channel契約、converterがOrderMatrix化|不要|UGE/ASM/ROMに直結|具体mapping|
|quantized note/rest rows|note/rest、length|A|pattern cellへ変換|不要|64行制約|grid|
|note pitch|`note`|A|converterがpitchを解析|不要|note tableへ変換|range policy|
|note length|`length`|A|row展開|不要|pattern row|duration丸め|
|Game Boy instrument mapping|`instrument`/instrument bank|A|channel bankをconverterが使用|不要|APU descriptor|mapping|
|volume/effect|`volume`/`effect`/`effect_param`|A|Version 2 note commandをconverterが使用|不要|cell effect|source dynamics変換|
|source tempo|直接保存しない|B/D|JSON tempoはTicksPerRow|normalization report|誤変換防止|tempo policy|
|TicksPerRow|top-level `tempo`|A|converterがdescriptorへ書く|不要|runtime timing|値決定|
|order/pattern|`order`/`patterns`|A|converterの主入力|不要|UGE/ASM order|分割|
|repeat展開結果|order/pattern|A|展開済み結果だけ必要|元repeatはreport|loop意味|展開方式|
|BGM loop metadata|`loop`|A|Version 2必須、converter/runtimeが使用|不要|loop effect/descriptor|loop選択|
|warning/loss|不要|B|runtime dataではない|report/manifest|なし|policy|
|transformation history|不要|B|再現性・review用|manifest|なし|schema|

現時点でCと確認された項目はない。Dはsource tempo change、loop policy、range/loss、具体的instrument mapping等であり、prototype実験後に再評価する。

## Channel / note compatibility

ArrangementPlanで4 physical channelへ割り当て済みなら、`pulse1`/`pulse2`/`wave`/`noise`のchannel別order/patternへ落とせる。logical role（melody、bass、harmony等）はruntimeが参照しないためBである。polyphony、chord、inner voiceは前段でreductionし、出力note/restへする。削除元や理由はJSON外reportへ保存する。

## Instrument / wave / noise compatibility

source instrument名はBであり、Game Boy pulse/wave/noise instrumentへ変換したIDはAである。converterはchannelに対応するinstrument bank、Version 2のwave/noise instrument、wave/noise parameterを検証・出力する。未対応mappingは暗黙fallbackせず、明示設定、warning、rejectのいずれかをprototypeで決める。具体的source instrumentとの対応はDである。

## Timing / quantization compatibility

MusicXMLのdivisions、duration、BPMはJSONへ直接コピーしない。normalized musical timeからquantization grid、64-row pattern、note lengthを作り、runtime契約用のTicksPerRowを別途決める。JSONのrow/length/TicksPerRowはA、source timingと丸め・変換履歴はB、tempo changeを単一tempoへどう近似するかはDである。source BPMをJSON `tempo`へ書く設計は不適合である。

## Tempo / TicksPerRow compatibility

`tools/json_to_uge.py`と`tools/json_to_huge_asm.py`はいずれも`data["tempo"]`を正整数として読み、UGE/ASM descriptorへ渡す。これはhUGEDriverのTicksPerRowであり、BPMを意味しない。source musical tempo、normalized tempo、JSON tempo、実時間を変換レポートで分離する。曲中tempo変更は現行JSONの単一tempo契約にそのまま入らないため、adapterで制約・近似するか、Dとして実験後に判断する。現時点でCとはしない。

## Repeat / loop compatibility

MusicXML repeat/endingは前段で解決し、生成されたorder/patternとVersion 2 `loop`へ変換する。元repeatをJSONに保存する必要はなくBである。`full`、`range`、`none`はAだが、rangeの実装制約（end orderが全order数）を満たす必要がある。repeat解釈とBGM loop選択は別であり、具体策はDである。

## Dynamics / articulation compatibility

Game Boy向けvolume/effectへ変換できるものはA、sourceの表現・変換前後・失われた情報はBである。JSONをMusicXML archiveとして完全保存する必要はない。現行JSONで表現できないornament/articulation/dynamicsをruntimeで必須とする根拠はなく、Cとはしない。変換できない場合はloss/warning/reportへ記録する。

## Provenance boundary

composition identity、source identity/URL/format/license、edition、arranger、transcriber、encoder、retrieval date、source hash、parser version、transformation history、generated artifact hashは原則Bでmanifest/sidecarへ保持できる。既存converterはこれらを読まない。具体的sourceとlicenseは01690、prototypeで必須とする詳細は後続で確認する。

## Loss / warning / transformation history boundary

loss、warning、削除note、voice選択、range shift、quantization誤差、repeat展開履歴はruntimeには不要であり、Bとしてtransformation report/manifestへ分離する。reportを保存しないとsilent lossになるため、adapterの出力契約に含める。Human reviewが必要なwarningはprototypeの入力を止める可能性があり、Dである。

## Minimal conversion example

著作物に依存しない抽象例:

```
NormalizedScore:
  melody: C4, quarter
  bass: C3, half

ArrangementPlan:
  melody -> pulse1, 2 rows, instrument 1
  bass   -> wave,   4 rows, instrument 1

JSON Version 2:
  order.pulse1 -> ["p0"]
  order.wave   -> ["p0"]
  patterns.pulse1.p0 -> [{note: "C4", length: 2, instrument: 1}]
  patterns.wave.p0   -> [{note: "C3", length: 4, instrument: 1}]
  tempo -> explicit TicksPerRow value
  loop -> {mode: "full"}
```

実際には使用channelのorder数を揃え、未使用channelをVersion 2契約に従って補完し、全patternを64行へ展開する。source BPMやlogical roleはJSONへ直接入れない。

## Existing pipeline reuse conditions

MusicXML → ArrangementPlan → JSON V2 → existing pipelineを成立させる条件は、(1) polyphony/reduction済み、(2)4 physical channel allocation済み、(3)note/rest/lengthが64-row制約内、(4)Game Boy instrument IDとwave/noise dataが検証済み、(5)source tempoとは別にTicksPerRowを決定、(6)order数を4 channelで整合、(7)repeatをorderへ解決、(8)loopを`full/range/none`へ解決、(9)unsupported/lossをreport、(10)JSON Version 2 validatorを通過することである。これらを満たせばjson_to_uge/json_to_huge_asmは方式非依存の後段として再利用候補になる。

## JSON extension candidates

現時点で、ROM/UGE/ASM生成に必要で、前段またはsidecarで解決不能なためJSON拡張が必要と確認された項目はない。source provenance、logical role、元polyphony、loss/history、source BPM、MusicXML repeatはJSON外で保持または編曲前に解決できる。将来、曲中tempo changeや追加instrument表現をruntimeで保持する要件が確定し、adapter・segment化・既存effectで表現できない場合だけ、別WBSでJSON拡張を検討する。

## Downstream impact

JSONを変更しない場合は、adapter/manifestを追加し、既存converter・UGE/ASM/ROM・runtime検証を再利用できる。JSONを将来変更する場合は、`json_to_uge.py`、`json_to_huge_asm.py`、validator、tests、UGE/ASM descriptor、ROM runtime、fixtures、docsの契約更新が必要になるため、別WBSへ分離する。今回は変更しない。

## Unresolved items

- concrete MusicXML source、parser、prototype曲
- melody/voice/part、polyphony、instrument mapping
- tempo change、quantization、range、repeat/loop policy
- JSON外manifest/reportの具体schema
- 未対応MusicXML情報のreject/warning policy
- 01690のlicense/provenance確認

## Handoff to WBS-001-01690 / 01692

01690では具体的MusicXML sourceのcomposition、edition、arrangement、transcription、encoding、license、商用ROM/GitHub公開、repository保存可否を確認する。01692以降のprototypeでは、選択sourceと設定からArrangementPlan、JSON V2、UGE、ASM、ROMまでを実測し、D項目とloss/report契約を確定する。
