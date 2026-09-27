# PD曲入力形式とsource/provenance方式の調査

対象: WBS-001-01686
調査日: 2026-09-27

## Scope

PD曲をGame Boy向けに自動編曲するためのmachine-readable入力候補を調査する。MIDI、MusicXML、公開されるmachine-readable楽譜source、その他symbolic representationを比較するが、入力形式・parser・曲・sourceの採用はWBS-001-01687/01691でHumanが判断する。MP3/WAV等のaudioはsymbolic inputとは別系統で、audio transcriptionが必要になる。

## Requirements inherited from WBS-001-01685

入力からnotes、pitch、duration、timing、voices/parts、measure、tempo、time signature、key、repeat、dynamics、instrument/part identity等を正規化できることが候補の確認対象である。4ch arrangement、quantization、loop、instrument mapping、JSON Version 2適合性は後続WBSで扱い、ここでは決定しない。

## Standard MIDI File

MIDI 1.0は演奏イベント交換の仕様で、Standard MIDI Fileではtrack、channel、note on/off、delta-time/ticks、tempo event、time signature、key signature、program change等を扱う入力として検討できる。format type（0/1/2）、ticks per quarter note、同時発音イベント、複数track/channelの対応はparserで明示的に読む必要がある。

MIDIは楽譜の意味を完全に保持する形式とは限らない。phrase、harmony、voice function、cadence、section、repeat意図はイベント・meta event・track名等から取得できる場合があるが、解析やHuman interpretationが必要になる。program/channelはsource instrumentの手掛かりだが、Game Boy CH1〜CH4 mappingではない。percussion conventionもMIDI channel 10等の慣例を別途解釈する必要がある。

既存JSON Version 2へは、note/timing/trackをnormalizationしてからvoicesを4ch arrangementへ渡し、編曲済み結果をJSONへ出力する接続が候補である。polyphony reduction、quantization、repeat/loop、tempo/TicksPerRow、instrument mappingで情報損失が生じ得る。MIDIを採用決定していない。

## MusicXML

MusicXML 4.0はデジタル楽譜交換用の形式で、score-partwise/score-timewise、part、measure、note、voice、staff、duration、divisions、time、key、direction/tempo、dynamics、repeat/ending等を構造として扱う。score structureやpart/voiceの情報を保持しやすい一方、Game Boy 4ch reduction、instrument mapping、loopのruntime semanticsは別工程である。

MusicXMLのnote/rest、measure、voice、staff、time/key、directionをnormalizationし、編曲済みchannel/patternへ変換してJSON Version 2へ接続する候補である。複数voice/polyphony、装飾・articulation、dynamics、repeat/endingの解釈やlossy conversionは別途設計が必要で、MusicXMLを採用決定していない。

## Other symbolic/public score representations

公開楽譜データは形式と入手sourceを分けて扱う。MusicXML、MIDI、ABC、Humdrum等のsymbolic representationがあり得るが、今回のrepositoryで新規parser導入やsource downloadは行っていない。形式が同じでもedition、採譜者、encoder、license、配布条件が異なるため、公開source単位のprovenance確認が必要である。

ABC/Humdrum等を候補にする場合は、parserの公式仕様、polyphony/voice、meter/key、repeat、license、JSON接続を個別確認する。現時点で追加候補を採用・推奨していない。

## Parser/library candidates

実装・installは行わず、候補の存在と公式情報のみ確認した。

- Mido: PythonでMIDI 1.0 ports/messages/filesを扱うlibraryとして公式documentationに記載される。MIDI parsing候補だが、score-level harmony/phrase解析やGame Boy arrangementは別責務。Midoのコード・依存・version固定・license確認は導入時に必要。
- music21: MIDI、MusicXML等を読み書きし、計算音楽学・解析用のPython toolkitとして公式documentation/repositoryに記載される。codeはBSD 3-Clauseだが、corpusのencoded musicは個別license/permissionがあり、library licenseとdata licenseを分離する必要がある。大きな依存・Python version・deterministic outputは導入時に確認する。
- XML標準library: MusicXMLはXML/XSDとして扱えるため、Python標準XML parserを使う実装可能性はあるが、MusicXMLの音楽意味の正規化・解釈を自動で解決するものではない。

parserのactive maintenance、依存version、外部サービス依存、license適合性は今回の採用判断では未確定である。

## JSON Version 2 connection

候補形式はいずれも、直接JSONへ変換するのではなく、次のnormalization/arrangement境界を通す想定である。

`source → normalized symbolic events/structure → Game Boy arrangement → JSON Version 2`

MIDIはevent/ticks/track/channelを取得しやすいが、score semanticsの推定が必要。MusicXMLはmeasure/voice/part/time/key/repeat等を取得しやすいが、polyphony reductionとruntime loopへの解釈が必要。公開楽譜sourceは形式とデータlicenseを別々に確認する必要がある。JSON Version 2の変更要否は01689の責務であり、今回は変更しない。

## Copyright/license/provenance separation

次を別identityとして管理する必要がある。

1. composition: 作曲そのもの、composer/traditional、publication/date
2. edition: 校訂・版・出版社等
3. arrangement: 編曲者と編曲結果
4. transcription: 採譜者・採譜方法
5. symbolic encoding: MIDI/MusicXML等への入力・変換データ、encoder
6. recording: 演奏・録音

作曲がPDでも、具体的なMIDI/MusicXML/楽譜ファイル、採譜、edition、編曲、録音が自由利用できるとは判断しない。sourceごとにlicense、利用範囲、商用ROM/GitHub公開可否を個別確認する。具体的sourceとprototype曲の確認は01690/01691で行う。

## Provenance metadata candidates

|項目|分類候補|用途|
|---|---|---|
|composition identity / composer/traditional|prototype必須候補|原曲の同一性|
|source identity / URL/location / format|prototype必須候補|入力source追跡|
|source license|prototype必須候補、個別確認|利用範囲確認|
|edition / arranger / transcriber / encoder|条件付き・source依存|権利と変換履歴|
|retrieval date|prototype必須候補|source更新追跡|
|source hash|prototype必須候補|同一入力識別|
|parser/library name/version|変換artifactで記録候補|再現性|
|transformation history|prototype必須候補|normalization/arrangement追跡|
|generated artifact hash|後段artifactで記録|同一run確認|

この表は候補schemaであり、production schemaとして確定していない。

## Determinism and reproducibility

- MIDI: source bytes/hash、format、parser/version、ticks解釈、tempo/quantization設定、mapping、toolchainを固定する必要がある。seedは必須ではない。
- MusicXML: source bytes/hash、schema/version、parser/version、divisions/time/repeat解釈、normalization設定、mappingを固定する必要がある。edition/source更新の影響を追跡する。
- 公開score source: URLだけでなく取得日時、bytes hash、edition、license、変換者を保持する必要がある。
- 外部service/modelを使う場合: service/model version、prompt/config、応答、利用条件、取得日時を保存し、非決定性を別途確認する。

同一source hash・parser/library version・設定・変換コード・toolchainからnormalizationとartifactを再生成できることを、選択後のprototype要件候補とする。

## Comparison table

|観点|MIDI|MusicXML|その他公開symbolic score|
|---|---|---|---|
|音符/timing|note on/off、delta-time/ticks、tempo event|note/rest、duration/divisions、measure|形式ごとに異なるため個別確認|
|polyphony|track/channelと同時event|voice/staff/partで表現|個別確認|
|score structure|track/meta eventから解析候補、意味は別解析|part/measure/time/key/repeat等を構造として保持|個別確認|
|parts/voices|track/channel/program|part/voice/staff/instrument|個別確認|
|repeat|event/metaまたは慣例から解析|repeat/ending等を表現可能|個別確認|
|tempo|tempo event|direction/tempo|個別確認|
|instrument|program/channel、percussion convention|part/instrument情報|個別確認|
|parser|Mido等の候補、未導入|XML parser/music21等の候補、未導入|公式parserの有無を個別確認|
|provenance|source file/encoder/licenseを別管理|edition/encoder/licenseを別管理|公開source単位で管理|
|license確認|sourceごとに必要|sourceごとに必要|sourceごとに必要|
|normalization負荷|score semantics推定、quantization|構造解釈、polyphony/repeat解釈|形式依存|
|Game Boy arrangement接続|4ch reduction/mappingが別工程|4ch reduction/mappingが別工程|別工程|
|JSON V2接続|normalization→arrangement後に候補|normalization→arrangement後に候補|個別adapter候補|
|reproducibility|source hash/parser/version/config|source hash/parser/version/config|source取得・版・parserを固定|
|主な未確定|harmony/phrase推定、loop、mapping|lossy reduction、repeat semantics、mapping|parser・license・表現力|

## Unresolved items

- 入力形式とparserのHuman選択
- source入手先と具体的PD曲
- source file license、edition、採譜、encoder、録音の権利
- harmony/phrase/section/repeatの解析範囲
- polyphony reduction、quantization、tempo/TicksPerRow、loop、4ch mapping
- parser/libraryのversion・依存・license・maintenance
- JSON Version 2での表現不足とadapter/拡張
- sourceをrepositoryへ保存するか、hash/URLのみ保持するか

## Questions for Human decision

- 演奏イベント中心のMIDI入力でよいか。
- 楽譜構造をできるだけ保持するMusicXML等を重視するか。
- 公開sourceの入手性と権利確認コストをどの程度重視するか。
- Humanによるsource前処理・normalizationを許容するか。
- parser/libraryを追加導入するか。
- source fileをrepositoryへ保存するか、metadata/hashで追跡するか。
- provenanceをどの粒度まで保持するか。

## Handoff to WBS-001-01687

01687では本調査の比較表、parser候補、provenance要件、未確定事項を確認し、prototypeで使用する入力形式をHumanが選択する。CodexはMIDI/MusicXML等を採用決定していない。

## Handoff to WBS-001-01690

01690では具体的PD曲/sourceについて、composition、edition、arrangement、transcription、symbolic encoding、recordingを分離し、source license、利用範囲、商用ROM/GitHub公開可否、hash、retrieval dateを個別確認する。compositionがPDであることだけからsource fileの自由利用を推測しない。

## External evidence

- URL: https://midi.org/midi-1-0-detailed-specification
  - 資料: MIDI 1.0 Detailed Specification
  - 提供元: The MIDI Association
  - 確認事実: MIDI 1.0のdata format、channel voice/system message、transport等の公式仕様案内。調査日: 2026-09-27。
- URL: https://www.w3.org/2021/06/musicxml40/
  - 資料: MusicXML 4.0
  - 提供元: W3C Music Notation Community Group
  - 確認事実: score-partwise/timewise等の楽譜交換形式、measure/note/voice/time/key/repeat等の仕様参照。調査日: 2026-09-27。
- URL: https://mido.readthedocs.io/_/downloads/en/latest/pdf/
  - 資料: Mido documentation
  - 提供元: Mido project
  - 確認事実: PythonでMIDI 1.0 ports/messages/filesを扱うlibraryとして説明。調査日: 2026-09-27。
- URL: https://github.com/cuthbertLab/music21
  - 資料: music21 repository / README
  - 提供元: cuthbertLab
  - 確認事実: MIDI/MusicXML等を扱うPython toolkit、code licenseはBSD 3-Clause、corpus dataは個別license/permissionがある。調査日: 2026-09-27。
- URL: https://music21.org/music21docs/about/about.html
  - 資料: music21 licensing and corpus documentation
  - 提供元: music21
  - 確認事実: code licenseとencoded corpusのlicenseを分離し、個別作品に制限があり得る。調査日: 2026-09-27。
