# MusicXMLからGame Boy 4chへの自動編曲設計

対象: WBS-001-01688
設計日: 2026-09-27

## Scope

Humanが選択したMusicXMLを、正規化された音楽情報を経由してGame Boy 4ch向け編曲結果へ変換し、JSON Version 2へ渡す責務と契約を設計する。これは既存曲の編曲であり、旧rule-based generatorのように曲を無から作曲する設計ではない。parser実装、source選択、具体的production default、JSON変更、prototype生成は後続へ残す。

## Confirmed inputs and constraints

- prototypeの入力形式はMusicXMLをベースに検討する。ただし永久的・不可逆な採用ではない。
- 具体的source、parser/library、曲、license/provenanceは未決定である。
- JSON Version 2は現時点で変更しない。編曲結果を既存契約へ接続できるかは01689で確認する。
- JSONの4チャンネルは`pulse1`、`pulse2`、`wave`、`noise`で、`tempo`はSong Version 6のTicksPerRow契約である。
- `sound-spec.md`ではCH1を主旋律、CH3を土台、CH2/CH4を一時欠落を許容する補助とする方針がある。これは既存仕様として考慮するが、MusicXMLの情報を暗黙に固定channelへ落とす規則ではない。
- SFXはCH1/CH4等を占有し得る。編曲はSFX共存を考慮するが、SFX方式自体は変更しない。

## MusicXML normalization boundary

parser固有のオブジェクトを直接編曲器へ渡さず、次の正規化境界を置く。

`MusicXML source → NormalizedScore → ArrangementPlan → JSON Version 2`

NormalizedScoreは少なくともsource hash、parts、measures、voices、staves、note/rest、pitch、duration、位置、tie、chord、meter、key、tempo/direction、dynamics、repeat/ending、instrument/part identityを保持できる構造とする。実装時の型名・APIはparser選択後に決める。

|情報|prototypeでの扱い|分類|理由/後続|
|---|---|---|---|
|part/voice/staff|保持し、mapping入力の候補にする|利用|polyphonyと役割を区別するため|
|measure/位置/duration/divisions|正規化する|利用|quantizationとorder/rowの入力|
|note/rest/pitch/tie/chord|正規化する|利用|発音イベントと重なりを追跡|
|time/key|保持し、編曲判断の入力候補|条件付き利用|転調・拍の扱いは未確定|
|tempo/direction|source情報として保持|条件付き利用|runtime tempoとは別概念|
|dynamics/articulation|保持または明示的にloss記録|保存/条件付き|JSONで表現できない可能性|
|repeat/ending|構造情報として保持|利用候補|BGM loopとは別に解決|
|instrument/part identity|保持|利用候補|source role推定の手掛かり|

未使用フィールドを黙って捨てず、未対応・lossy変換・保存のみを変換レポートへ記録する。

## Logical musical representation

MusicXML固有のpartと物理channelの間に論理層を置く。例として、NormalizedScoreのイベントを`melody`、`harmony`、`accompaniment`、`bass`、`percussion`等のArrangementLayerへ割り当てる。logical roleはsource part/voice、明示設定、解析結果のいずれから得たかを記録する。

ArrangementPlanは、各layerのイベント列、priority、source reference、変換警告、transpose/range処理、quantization結果、logical-to-physical allocation、loop/order情報を保持する。roleの自動推定が不確かな場合は暗黙に決めず、explicit mapping、Human選択、warning、rejectのいずれかを設定で選べる設計にする。

## Game Boy channel capabilities

|物理channel|hardware role|編曲上の扱い|
|---|---|---|
|CH1 / Pulse1|pulse melody等|重要な旋律を置く候補。CH1固定はsource解析後のallocationで決める|
|CH2 / Pulse2|pulse補助|harmony、対旋律、arpeggio、装飾等の候補。SFXで欠落し得る|
|CH3 / Wave|wave土台|bass、root、持続音等の候補。source roleから明示的に割り当てる|
|CH4 / Noise|noise percussion|percussion/rhythm候補。pitch音符をそのままnoiseへ変換しない|

logical roleとphysical channelは別のデータとして保持する。source instrument名からGame Boy instrumentを1対1で決めない。

## Logical role vs physical channel

基本処理は`source part/voice → logical role → physical channel → Game Boy instrument`とする。allocationにはsource reference、channel、priority、lossy conversionの有無を含める。CH1/CH3に曲の骨格を配置しCH2/CH4の一時欠落に耐えるという既存sound-specの検証は後続prototypeで行うが、MusicXMLの全曲に適用する固定ruleとはしない。

## Melody selection

melody候補はpart、voice、staff、pitch/range、density、source instrument、明示設定から評価可能にする。複数候補が同等、または主旋律が明確でない場合は、heuristicで黙って選択せず、Human mappingまたは明示configurationを要求する。確定できない候補はwarning/reportまたはrejectとし、具体的な優先順位・閾値はprototype実験または根拠確認後に決める。

## Polyphony reduction

MusicXMLの同時発音、chord、inner voice、overlapは、4ch制約に合わせてdeterministicな変換段階で処理する。候補処理はmelody preservation、重複note統合、chord toneの選択、arpeggio、rhythmic accompaniment、omission、layer redistributionであるが、今回は一つをproduction defaultにしない。

削除、短縮、voice統合、range変換があれば、入力イベント、出力イベント、理由、設定、loss量を変換レポートとtransformation historyへ記録する。未解決のpolyphonyをsilent lossにしない。明示設定がない場合はwarning、Human decision、またはrejectのポリシーを後続実装で選ぶ。

## Harmony and accompaniment

chord/harmonyはそのまま同時発音できない場合がある。代表chord tone、arpeggio、rhythmic accompaniment、別channelへのredistribution、omissionを比較可能な候補として保持する。原曲に明示的harmonyがない場合に新しい和声を作曲することは今回の中心責務ではなく、必要なら未確定として扱う。

## Bass handling

bassは、(a) source bass part、(b) lowest-note extraction、(c) harmonyからの派生、(d) Human mappingを区別する。source bassがない場合に自動生成するかは未確定で、sourceに存在しない情報を暗黙に発明しない。CH3へのallocationはArrangementPlanで明示する。

## Percussion / CH4 handling

percussion partがある場合はinstrument identity、hit timing、duration、複数instrumentを保持し、CH4 noiseへのmapping候補へ渡す。percussionがない場合はCH4を未使用、別layerのrhythm、またはHuman指定とする可能性を残す。pitch instrumentをnoise percussionへ自動変換しない。unsupported percussion、複数hitの同時発生、noise instrument mappingはwarning/reportまたはHuman decisionが必要である。

## Pitch range and octave handling

Game Boyで表現できないpitchは、octave shift、transpose、clamp、reject、Human decisionの候補として分類する。処理前後のpitch、役割、contourへの影響を記録する。clampを黙って行わず、melody contourやbass roleが壊れる場合はlossy warningまたはrejectとする。具体的range/defaultは後続で検証する。

## Quantization model

source tempo、音楽上のduration、quantization grid、JSON pattern row、runtime ticksを別概念として保持する。MusicXMLのdivisionsとmeasure/beatからnormalized musical timeを作り、選択したgridへquantizeし、その結果を64-row pattern/orderへ分割する。

JSON Version 2の`tempo`はBPMではなくSong Version 6のTicksPerRowであり、sourceのtempoをそのまま書き込まない。変換計画にはsource tempo、normalized tempo、grid、row duration、TicksPerRow、丸め誤差を明示する。過去のtempo/TicksPerRow不一致を避けるため、これらの値と単位をmanifest・変換レポートに残し、具体的defaultは01689/実験で確認する。

## Tempo / TicksPerRow model

`source musical tempo → normalized timing model → tracker/runtime timing`を分ける。JSONへ渡す際は、Version 2の単一`tempo`契約とhUGEDriverのTicksPerRowを明示的に生成し、source BPM、tempo変更、曲中変化を失う場合は記録する。現行JSONは曲全体単一tempoであり、曲中tempo eventを直接表現する契約ではないため、tempo changeは保持、近似、分割、rejectの選択を後続で決める。

## Phrase / section handling

MusicXMLから直接得られるmeasure、part、repeat、ending、direction等と、解析から構築するphrase/section、Human指定を分ける。旧generatorのsection生成ruleを流用しない。phrase boundaryが明示されない場合はmeasure/repeatから候補を生成し、推定であることを記録する。section名・variation・cadenceの自動生成は未確定とする。

## Repeat and BGM loop handling

次を別段階として扱う。

1. 楽譜のrepeat/endingの解釈・展開
2. 編曲されたsong order/patternの構築
3. Game Boy BGMとしてのloop point選択
4. JSON `loop` metadataとruntime loop

楽譜repeatをそのままBGM loopへ変換しない。repeat展開の有無、endingの処理、loop開始/終了、全channel order alignment、full/range/noneとの対応をmanifestで確認する。loop pointが明示できない場合はHuman decisionまたはwarning/rejectとし、runtime metadataを推測しない。

## Instrument mapping

source instrument/part identityはlogical roleの手掛かりであり、Game Boy instrumentそのものではない。`source instrument → logical role → physical channel → pulse/wave/noise instrument`の各変換を記録し、未対応instrumentやarticulation/dynamicsのlossを明示する。Wave table、pulse duty、noise parametersの具体値は既存JSON/instrument契約とprototype検証に基づいて後続決定する。

## Channel allocation

allocationはcaller-supplied configurationまたは明示された変換結果として保持し、logical objectへ埋め込まない。CH1〜CH4のcapability、SFX占有可能性、同時発音制限、未使用channelをvalidationする。全channelを必須とするproduction ruleは設定しない。allocation conflictはdeterministicに検出し、warning、再配置、Human decision、rejectのいずれかを明示する。

## SFX coexistence boundary

既存sound-specではSFXがCH1/CH4等を一時占有し、CH2/CH4の欠落に耐え、CH1/CH3で骨格を維持する方針がある。ArrangementPlanではSFX occupancy、BGM channel、mute tolerance、復帰時のtimeline continuationを検証対象にする。ただしSFXの実装方式、Human聴感評価、全allocationの実機確認はこのWBSで完了しない。

## Unsupported / lossy conversion policy

|対象|初期分類|必要な扱い|
|---|---|---|
|過剰polyphony|supported with loss候補|削除・再配置と理由を記録|
|unsupported duration/timing|warningまたはreject|quantization誤差を記録|
|pitch/range外|warning、Human decision、reject候補|shift/clampを明示|
|unsupported percussion|warningまたはreject|CH4 mappingを推測しない|
|ornament/articulation/dynamics|保存のみまたはlossy|JSON非表現を記録|
|ambiguous melody/voice/part|explicit configuration/Human decision|暗黙heuristic禁止|
|complex repeat/ending|Human decisionまたはreject候補|loopと分離|
|tempo changes|保存・近似・分割・reject候補|BPMとTicksPerRowを分離|

これは実装時の分類候補であり、具体的policyは未確定である。全変換はreportとtransformation historyを出力し、未対応情報をsilent fallbackしない。

## Determinism / reproducibility

同じsource bytes、source hash、normalization configuration、arrangement configuration、mapping、parser/tool versionから同じArrangementPlanとJSONを生成する設計とする。source、設定、変換履歴、warning、出力artifact hashをmanifestへ保存する。randomnessは不要で、将来導入する場合だけseedと生成条件を追加する。MusicXML parserのversionとschema解釈が変わる場合は再生成差分を検出する。

## Configuration points

自動推定を強制せず、少なくとも次を明示設定可能な境界候補とする。

- melody source part/voice/staff
- bass sourceまたは抽出方式
- harmony/accompaniment方式
- percussion sourceとCH4 mapping
- source-to-logical-role mapping
- channel preference/allocation
- transpose/octave/range handling
- quantization grid
- source tempo/tempo-change handling
- repeat expansion
- BGM loop range
- unsupported/loss policy

これはproduction config schemaの確定ではなく、01689/prototypeへ渡す設計入力である。

## Arrangement output contract

編曲器の出力は、少なくとも以下を含む中間成果物とする。

- source/provenance identityとhash
- normalized score reference
- logical layersとsource event対応
- physical channel allocation
- quantized note/rest rows
- instrument mapping
- tempo/TicksPerRowと単位
- order/pattern構造
- repeat展開とBGM loop metadata
- warning/loss/transformation history
- JSON Version 2へ渡す入力

JSON V2生成後は、既存validatorでchannel名、order/pattern、64-row制約、instrument reference、loop、tempoを確認し、UGE/ASM/ROMは既存pipelineで検証する。これは音楽品質を保証しない。

## JSON Version 2 handoff

現行JSONで表現できそうなのは、4channel別note/rest、length、instrument、volume/effect、order/pattern、単一tempo、loop metadataである。01689では、MusicXMLのpolyphony、voice、repeat/ending、tempo changes、dynamics、articulation、source provenance、loss reportをJSON本体へ入れる必要があるか、adapter/manifest側で保持できるかを確認する。JSON Version 2やconverterは本作業で変更していない。

## Unresolved items

- MusicXML parser/libraryと具体source
- melody/voice/partの選択方法
- polyphony、harmony、bass、percussionの具体的reduction
- range、quantization、tempo change、loop policy
- source provenanceをJSON外manifestで保持する範囲
- MusicXML情報のloss policyとHuman review
- SFX占有時の全channel聴感検証
- 現行JSONで不足する情報の有無

## Handoff to WBS-001-01689

01689では、このArrangementPlan出力を現在のJSON Version 2へ表現できるかを、note/timing、4channel allocation、order/pattern、instrument、loop、tempo/TicksPerRow、loss/provenanceの境界ごとに確認する。不足があっても直ちにJSON仕様を変更せず、adapter、manifest、または別WBSの必要性を記録する。

## Handoff to prototype implementation

prototype実装では、parser APIに依存しないNormalizedScore入力、明示configuration、deterministic transformation report、loss/warning、source hash、JSON validationを先に用意する。具体的なsource、parser、4ch rule、instrument mapping、JSON適合性が確定するまで実装を開始しない。
