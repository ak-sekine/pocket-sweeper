# PD曲Game Boy自動編曲の要件と処理境界

対象: WBS-001-01685

## Scope

パブリックドメイン曲を元にした自動編曲について、原曲/sourceから既存JSON Version 2とJSON→UGE→ASM→ROM pipelineへ渡すまでの責務境界を整理する。入力形式、prototype曲、具体的な編曲rule、JSON拡張は決定しない。

今回のsourceは、既に曲として成立した音楽構造を含む前提で扱う。旧rule-based generatorのように無からmelody/harmony/phrase/sectionを作ることは中心責務ではない。

## Confirmed decisions

- 次の方式はHumanが選択した「パブリックドメイン曲を元にした自動編曲」である。
- JSON Version 2→UGE→hUGEDriver ASM→ROMは基本的に維持する。
- 具体的な表現不足や変換問題が確認された場合は、根拠を記録して変更を検討できる。
- 現時点で入力形式・曲・編曲rule・JSON拡張は未決定である。

## End-to-end responsibility model

`composition/source → source representation → normalization/analysis → Game Boy arrangement → JSON Version 2 → UGE → ASM → ROM/runtime`

|段階|責務|入力|出力|今回の境界|
|---|---|---|---|---|
|Composition/source|曲のmelody、harmony、rhythm、phrase、section、repeat等を保持|原曲と権利情報|曲の意味・source identity|特定形式・曲は未決定|
|Source representation|machine-readable入力として保存|MIDI、MusicXML、公開楽譜等の候補|parserが扱えるsource|01686で調査、01687でHuman選択|
|Normalization/analysis|形式固有情報を正規化・解析|選択されたsource|notes、timing、voices、measure、tempo等|必要項目を後続で確定|
|Arrangement|Game Boy 4chへ縮約・mapping|正規化された曲情報|編曲済みchannel/pattern/order/loop|01688で設計|
|JSON boundary|編曲済み結果をJSON Version 2で表現|編曲結果、instrument、wave/noise等|検証可能なJSON|01689で適合性確認|
|Downstream|既存converter/runtimeで変換・再生|JSON Version 2|UGE、ASM、ROM、runtime|01680で再利用候補を確認済み|

## Composition vs source representation

composition自体（曲の旋律・和声・構造）と、具体的なMIDI/MusicXML/楽譜ファイル（edition、採譜、録音、編曲を含み得るsource）は別物としてidentity・license・provenanceを管理する。形式の選択は01686、Humanによる選択は01687、具体的な曲/sourceの権利調査は01690、曲選択は01691で扱う。

## Source normalization boundary

normalization/analysisは入力形式を解釈し、編曲判断に必要な内部表現へ変換する責務を持つ。候補情報と扱いは次のとおり。

- notes: pitch、duration、start timing
- voices/parts: melody、伴奏、bass、percussion候補の識別
- measure/beat、tempo、time signature: timingとphrase境界の解釈
- key、harmony/chord: 編曲で利用できる場合の構造情報
- repeat/section: order・loop候補
- dynamics、instrument/part identity: 4ch mappingの入力候補

どの項目がsourceに必須か、parserが失う情報をwarning/reject/Human decisionのどれにするかは未確定で、01686/01688へ引き継ぐ。normalize時に無根拠なC major、default tempo、instrument、loopへsilent fallbackしない要件を置く。

## Arrangement boundary

Arrangementは既存曲をGame Boy制約へ縮約する責務であり、作曲ruleとは区別する。01688で次の設計判断を行う。

- CH1/CH2 pulse、CH3 wave、CH4 noiseへのallocation
- melody priority、polyphony reduction、harmony/accompaniment reduction
- bass extraction、percussion/noise conversion
- octave/range conversion、quantization、tempo/TicksPerRow変換
- phrase/section、repeat/loopの変換
- instrument、wave、noise mapping
- unsupported source情報とchannel conflictの扱い

ここでは具体的なpriority、最低note数、4ch必須、tempo default等を確定しない。sourceに存在する情報をどの程度保持・喪失するかを明示し、lossy conversionなら記録可能にする要件を置く。

## JSON Version 2 boundary

既存`docs/json-format.md`に基づき、JSON Version 2は編曲済みのchannel-local order/pattern、note/length、instrument、volume/effect、tempo、loop、wave/noise等を表現する後段データ契約として扱う。JSON自体が原曲解析や4ch編曲判断を行う境界とはしない。

編曲前に解決または明示する候補は、pitch、timing/grid、channel、instrument、wave/noise、loop、tempo/TicksPerRow、必要なprovenance参照である。表現できない情報は、adapterで吸収できるか、JSON拡張が必要か、未確定かを01689で分類する。今回はJSONやconverterを変更しない。

## Existing downstream pipeline boundary

- JSON Version 2: 編曲済み結果の検証可能な境界。新方式が契約を満たせば再利用候補。
- JSON→UGE: order/pattern、tempo、instrument、wave/noise、loopをSong Version 6へ変換。作曲方式非依存だが、入力契約への適合が必要。
- JSON→ASM: descriptor tempo、order/pattern、instrument、wave data、loop metadataを生成。作曲方式非依存。
- ASM→ROM: RGBDS、`hUGE_init_v2`、VBlank、`hUGE_dosound`、`hUGE_bgm_finished`を用いる既存test ROM。作曲方式非依存。
- hUGEDriver runtime: ticks_per_row、row/tick進行、4ch、loop、mute API等。SFX共存の聴感品質は未確認。
- validation: JSON validation、UGE Version/order alignment、ASM生成、RGBDS build、manifest/hash、same-run追跡。技術成立を確認し、音楽品質は判定しない。

既存pipelineで不足する情報が見つかった場合は、最初にadapter・別境界・JSON拡張の必要性を01689で整理し、先回りして仕様変更しない。

## Music information requirements

|情報|source/normalization|arrangement|JSON boundary|downstream|分類・後続|
|---|---|---|---|---|---|
|melody|notes/voiceとして必要候補|priority・rangeを変換|channel pattern/note|CH1/CH2等|条件付き、01686/01688|
|harmony/chord|sourceにあれば抽出候補|reduction/accompanimentへ利用候補|直接fieldではなくnotes/patternで表現候補|pattern|未確定、01686/01688/01689|
|rhythm|timing/percussionを解析候補|CH4/伴奏へ変換候補|noise/note/length|pattern|条件付き、01686/01688|
|bass|part/低音voiceを識別候補|CH3等へallocation候補|wave pattern|CH3|条件付き、01688|
|accompaniment|part/polyphonyを抽出候補|reduction・allocation|pulse pattern|CH2等|条件付き、01688|
|phrase/section|measure/repeatから解析候補|pattern/order/structureへ変換|order/pattern|order|条件付き、01686/01688|
|repeat|source semanticsを保持候補|loop境界へ変換|loop metadata|hUGEDriver loop|未確定、01686/01688/01689|
|tempo|source metadataを抽出候補|TicksPerRowへ明示変換|tempo|runtime ticks|条件付き、01688/01689|
|meter/time signature|measure/timing解釈に必要候補|quantizationへ利用|直接保持は未確認|row timing|条件付き、01686/01688|
|key|source metadata/解析候補|pitch/harmony解釈へ利用候補|直接保持は未確認|note|未確定、01686/01688/01689|
|dynamics|source metadata候補|volume/instrumentへ縮約候補|volume等|channel command|条件付き、01686/01688|
|instrument/part|part identityを抽出候補|GB instrument mapping|instrument ID/data|driver instrument|条件付き、01686/01688/01689|
|percussion|part/roleを抽出候補|CH4 noise mapping|noise note/instrument|CH4|条件付き、01686/01688|
|loop|repeat/sectionから候補|full/range/noneへ変換候補|loop|driver metadata|未確定、01688/01689|
|provenance|source identity/metadataを保持|変換履歴へ伝搬|既存field外の保存方法は未確認|manifest/document|条件付き、01686/01690|

## Human vs automation responsibilities

既存WBSでHumanが担当することは、01687の入力形式選択、01691のprototype曲/source選択、01694のSameBoy試聴である。source parse、normalization、4ch reduction、quantization、mapping、JSON生成、downstream buildはautomation候補だが、すべて完全自動にすると決定していない。編曲前のsource解釈、lossy conversion、unsupported情報、最終修正にHuman interventionが必要になる可能性を未確定として残す。

## Provenance requirements

後続処理で追跡できるよう、最低限候補として次を保持する。

- composition identity、composer/traditional
- source identity、URL/location、format
- source license、edition、arranger/transcriber
- retrieval date、source hash
- transformation history、parser/tool version、生成artifact hash

これらを必須metadataとして確定するのは01686/01690の調査後とする。composition自体がPDであることと、具体的source file・採譜・MIDI/MusicXML・録音・編曲が再利用可能であることを同一視しない。

## Unsupported / lossy conversion handling

unsupported polyphony、timing、instrument、repeat semantics、JSONで表現できない情報、4ch縮約による情報損失を検出可能にする。将来の実装ではreject、warning、explicit lossy conversion、Human decision requiredの分類が必要だが、具体的policyや閾値は01688/01689で根拠を確認して決める。silent fallbackは要件上避け、失われた情報と変換履歴を追跡可能にする。

## Unresolved items

- MIDI/MusicXML/公開楽譜等の入力形式とparser
- source/license/provenanceの具体的なmetadata schema
- melody/harmony/rhythm/伴奏/bassの抽出可能性
- 4ch reduction、priority、allocation、quantization
- BPM等からTicksPerRowへの変換
- repeat/loop semantics
- dynamics/instrument/wave/noise mapping
- JSON Version 2で表現できない情報とadapter/拡張
- Human interventionの範囲

## Handoff to WBS-001-01686

01686では、入力形式を採用決定せず、候補形式のpolyphony、timing、parts、repeat、parser、license、provenance、determinism、JSON接続を調査する。compositionと具体的source fileを分離して調査する。

## Handoff to WBS-001-01688

01688では、01687でHumanが選択した入力に基づき、4ch reduction、melody/harmony/bass/rhythm、quantization、tempo、loop、instrument、conflictの具体設計を行う。旧generatorの作曲ruleをそのまま移植せず、編曲責務として根拠と未確定事項を記録する。

## Handoff to WBS-001-01689

01689では、編曲済み結果をJSON Version 2でA:そのまま、B:adapter、C:拡張、D:未確定に分類する。JSONやdownstream converterはこの要件整理だけを理由に変更しない。
