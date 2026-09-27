# 根本的に異なる自動作曲アプローチ候補の調査

対象: WBS-001-01681
調査日: 2026-09-27

## Scope

現在のmotif/random中心のルールベース方式のparameter tuningではない方式候補を並列に調査した。ここでは比較、順位付け、採用、実装を行わない。既存のJSON Version 2→UGE→ASM→ROM基盤を使うことも、別中間表現を使うことも未決定である。

## Existing constraints

既存技術基盤の再利用境界は`docs/generated-song-technical-foundation.md`に整理した。候補は最終的にGame Boy 4ch、tempo/TicksPerRow、loop、instrument、wave/noise、既存JSONまたは別の変換境界を明示する必要がある。既存pipelineの成功は音楽品質を保証しない。旧quality profileのHuman評価「全部、音を並べただけで曲になっていません。」から、原因や新ruleは確定していない。

## Investigated approaches

### Approach A: 既存曲・パブリックドメイン曲を基礎にした編曲

入力は、権利状態とprovenanceを確認した楽曲の旋律・和声・構造、またはMIDI/MusicXML等の表現。原曲のphrase/section/旋律を解析し、Game Boy 4chへ縮約・編曲してJSON Version 2または別のsymbolic intermediateへ渡す。自動化候補は構造抽出、4ch reduction、instrument/channel mapping、loop化で、Humanは原曲選択・編曲方針・最終修正を担当し得る。

原曲の作曲著作権、編曲著作権、録音・データの権利は別に確認が必要である。「パブリックドメイン」の判定、入力ファイルのlicense、編曲結果の権利は未確認。自動作曲というより自動編曲・変換に近く、JSON Version 2へ落とせる範囲は既存契約で表現可能なnote/timing/channelに依存する。

### Approach B: MIDI/MusicXML等を中間表現にする方式

入力をMIDIまたはMusicXMLとし、note、duration、part、meter、tempo、score構造などを抽出する。中間表現から4ch reduction、quantization、instrument mapping、loop境界を明示し、JSON Version 2または直接UGE/別形式へ変換する。Humanはreductionと表現解釈を修正し得る。

MIDIは音楽イベント交換の仕様であり、MIDI 1.0仕様はnote等のメッセージとデータ形式を定義するが、Game Boy 4chへの編曲方針や「曲として成立する」ことは定義しない。MusicXMLはデジタル楽譜交換用の標準オープン形式だが、同様にGB allocationは別工程である。quantization、polyphony reduction、loop、instrument resolutionが既存JSONとの境界になる。入力MIDI/MusicXMLの権利と、過去にMIDIを採用しなかった設計判断の再評価は未実施。

### Approach C: 明示的な音楽構造・理論モデルから生成する方式

入力または生成対象をkey/scale、chord progression、harmonic rhythm、phrase/cadence、melody、bass、accompaniment、rhythm、loop構造などの明示的なsymbolic planとする。構造を先に作り、その後Game Boy 4chへ編曲してJSON Version 2へ接続する境界を検討する。

現在方式のmotif候補を増やすこととは異なり、和声・時間・phrase関係を明示する点が根本的な差になり得る。ただし、どの理論モデル・rule・defaultを採用するか、Humanがどの入力を担うか、品質をどう評価するかは未確定であり、今回production ruleにはしない。

### Approach D: corpusから構造・patternを抽出する方式

入力corpusからphrase、interval、rhythm、chord、accompaniment pattern、song structure等を抽出し、template、統計モデル、Markov系、または学習モデルで再構成する。出力はsymbolic eventまたはJSON Version 2へ変換する候補になる。

単純なfeature/template抽出、確率遷移、machine learningは別方式として扱う必要がある。corpus license、解析・学習許可、provenance、出力との関係、seed/モデルversionによる再現性は未確認。既存21曲UGEを品質defaultや多数決ruleの根拠には使用しない。

### Approach E: AI・LLM・生成モデルを利用する方式

入力を自然言語、構造化制約、参照曲、MIDI、またはsymbolic promptとし、AI/LLM/音楽生成モデルからsymbolic musicやJSON候補を得る。Human修正を挟んでJSON Version 2へ変換し、既存pipelineへ接続する構成も候補になる。

確認すべき点はstructured outputの保証、temperature/model version、seed、外部サービス依存、Game Boy制約を適用する段階、Human修正、model/output licenseである。AIを使えば品質が上がるとは扱わない。LLMの自由文出力を直接JSONへ信頼することも未確認。

Magenta repositoryは音楽・アート生成を研究する公開projectとして説明され、モデル・toolsをopen sourceで提供している一方、現在はarchived/read-onlyと表示される。個別モデル・データ・出力の利用条件は候補ごとに確認が必要であり、採用判断はしていない。

### Approach F: Human + automation

Humanがmelody、chord progression、structure、reference song、または高水準の制約を指定し、自動処理がaccompaniment、bass、rhythm、4ch reduction、instrument allocation、JSON化、UGE/ASM/ROM化を担当する方式。完全自動ではないが、Humanの音楽的判断と既存技術基盤を分担できる候補である。

Human入力の最小範囲、再現性、入力データのprovenance、どこまで自動化すれば目的に合うかは未確定。Human-assistedを採用方式と決めていない。

## External evidence

外部資料は方式の存在・仕様・公開状態を確認するために使用し、優劣や採用理由には使用していない。

| URL | 資料名 / 提供元 | 確認した事実 |
|---|---|---|
| https://midi.org/midi-1-0-detailed-specification | MIDI 1.0 Detailed Specification / The MIDI Association | MIDI 1.0のデータ形式・channel voice等の仕様資料で、音楽イベント交換の技術基盤である。 |
| https://www.w3.org/2021/06/musicxml40/ | MusicXML 4.0 / W3C Music Notation Community Group | MusicXMLはデジタル楽譜交換用の標準オープン形式。W3C Community Final Reportであり、Game Boy allocationは別工程。 |
| https://github.com/magenta/magenta | Magenta repository / Google等のcontributors | 音楽・アート生成の研究project、公開tools/models、Apache-2.0表示、現在archived/read-onlyであることを確認。個別model/data/output条件は未確認。 |

調査日はいずれも2026-09-27。外部資料からライセンス込みの採用可否を決定していない。

## Licensing / provenance considerations

- 入力曲、MIDI、MusicXML、corpus、参照音源の権利とlicenseを個別に記録する必要がある。
- パブリックドメインの原曲でも、特定録音・採譜データ・編曲は別の権利を持ち得る。
- corpus学習・抽出は、利用許諾、provenance、出力との関係を確認する必要がある。
- AI/model/serviceは、コードlicenseだけでなくmodel、training data、生成output、外部APIの利用条件を確認する必要がある。

## Unresolved items

- どの方式を比較対象として残すか
- 既存JSON Version 2を共通境界にするか、別中間表現を設けるか
- 4ch reduction、quantization、loop、instrument mappingの責務
- Human入力と自動処理の境界
- 再現性とprovenanceの保存形式
- 入力corpus・原曲・model・serviceのlicense
- Game BoyでのHuman品質評価方法

## Handoff to WBS-001-01682

01682では、A〜Fを候補例として、必要なら追加候補を含めて比較できる。比較時はGame Boy 4ch接続、既存JSON/UGE/ASM/ROM基盤の再利用可能性、曲構造の扱い、再現性、Human調整、license/provenance、実装・運用上の未確定事項を同じ枠で扱う。01681では方式の順位付け、最良方式の決定、採用方式の実装は行っていない。
