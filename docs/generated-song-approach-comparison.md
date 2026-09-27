# 自動作曲アプローチのGame Boy用途比較

対象: WBS-001-01682

## Scope

01681で調査したA〜Fを、Pocket Sweeper/Game Boy BGM用途の同じ観点で記述的に比較する。点数、順位、推奨、採用決定は行わない。比較は既存仕様、01680の技術基盤、過去Human評価に基づく。方式が曲として成立することはこの比較から保証しない。

## Comparison criteria

- Game Boy 4chへの接続とpolyphony/channel allocation
- JSON Version 2および既存JSON→UGE→ASM→ROM基盤の再利用境界
- phrase/section/repetition/variation/harmony/rhythm/bass/accompaniment/cadence/loopの扱い方
- deterministic input、seed、model version、prompt、Human input、source/tool version、artifact hash
- Humanが修正できる段階
- copyright/license/provenanceの確認点
- converter、quantization、loop、service/model、workflow等の未確定事項

## Comparison table

| 観点 | A 原曲・PD曲の編曲 | B MIDI/MusicXML中間表現 | C 明示的音楽構造モデル | D corpus構造抽出 | E AI/LLM/生成モデル | F Human + automation |
|---|---|---|---|---|---|---|
| 性質 | 既存曲を基礎にした自動編曲 | 楽曲イベント/楽譜を介した変換・生成 | 構造を先に定義する生成 | 既存corpusからtemplate/統計/モデルを抽出 | symbolic生成または構造生成 | Humanの音楽入力と自動処理の分担 |
| 4ch接続 | reduction・編曲・mappingが必要 | polyphony reduction、quantization、mappingが必要 | layerからCH1/2/3/4への明示変換が必要 | 抽出patternを4chへ割り当てる必要 | 生成結果を4ch制約へ検証・変換する必要 | Human指定と自動reductionの境界を定義 |
| 既存pipeline | JSON Version 2へ落とせれば後段再利用 | adapterでJSONへ変換する候補 | JSONへ直接変換またはadapter | 抽出結果をJSONへ変換する候補 | structured output/adapterが必要 | 自動処理の出力をJSONへ接続する候補 |
| 曲構造 | 原曲側の構造を入力として利用 | part/measure等から抽出可能だが解釈が必要 | phrase/harmony/cadence等を明示対象にできる | corpusから構造を抽出する対象にできる | model/outputの構造表現は方式依存 | Humanが構造を指定できる |
| 再現性 | source file、解析tool、編曲設定、hash | source、parser、quantization、mapping、tool version | plan、rule version、seed等を記録 | corpus version、抽出設定、model/seed | model version、prompt、parameters、service、seed | Human input、tool version、source、artifact hash |
| Human修正 | 原曲選択・編曲方針・最終修正 | MIDI/MusicXML、reduction、mapping | 構造・rule・生成結果 | template/corpus選択・抽出結果 | prompt、出力、構造、最終JSON | melody/chord/structureまたは4ch結果 |
| 権利・provenance | 原曲、採譜、録音、編曲を個別確認 | MIDI/MusicXMLの作成者・licenseを確認 | rule/sourceの出典を確認 | corpusと学習/抽出許可を確認 | model/data/service/output条件を確認 | Human入力と自動処理sourceを記録 |
| 未確定 | public domain判定、編曲権、入力形式 | parser、quantization、loop、4ch reduction | rule設計、品質評価、入力範囲 | corpus license、抽出手法、再現性 | structured output、依存、license | Human作業範囲、再現性、運用フロー |

表中の「候補」は実装済みを意味しない。「必要」「方式依存」は、方式を選択した場合に契約設計が必要という意味である。

## Approach-by-approach trade-offs

### A

原曲にphraseや構造が存在するため、入力から構造を扱える。一方、自動作曲というより自動編曲となり、原曲・採譜・録音・編曲の権利とprovenanceを分けて管理する必要がある。4ch縮約で原曲の情報を失う可能性は未評価。

### B

MIDIはnote/event交換、MusicXMLはデジタル楽譜交換の中間表現として扱える。一方、Game Boy 4ch、instrument、loop、quantizationは別の変換規則が必要で、形式を使うだけでは曲構造や品質は保証されない。既存方式で未採用だった理由の再確認が必要。

### C

key/scale、chord、harmonic rhythm、phrase、cadence、melody、bass等を明示的な生成対象にできる。一方、どの理論・rule・defaultを採用するかは新規のevidenceとHuman判断が必要で、旧方式のruleをそのまま確定できない。

### D

実在corpusのphrase・rhythm・pattern・structureを抽出する対象にできる。一方、単純抽出、template、確率モデル、学習モデルで意味が異なり、corpusのlicense・provenance・出力との関係を管理する必要がある。

### E

structured symbolic outputやHuman修正を組み込める可能性がある。一方、AI利用だけでは品質を保証せず、model version、prompt、service依存、再現性、training data/model/outputの利用条件を確認する必要がある。Magenta等の個別repository状態・licenseは方式ごとに再確認する。

### F

Humanがmelody/chord/structure等を入力し、自動処理が4ch reduction・伴奏・bass・rhythm・変換を担当する境界を設計できる。一方、Human作業量、入力形式、再現性、どこまでを「自動作曲」と呼ぶかは未決定である。

## Combination possibilities

方式は排他的とは限らない。例えばA+B（原曲をMIDI/MusicXMLへ取り込み編曲）、C+F（Humanが構造指定し構造モデルが生成）、E+F（AI出力をHumanが修正してJSON化）、D+B（corpus抽出結果をMIDI等へ変換）は組み合わせとして記述できる。ただし、どの組み合わせを採用するか、その権利・再現性・変換境界はHuman選択後に定義する。

## Common unresolved items

- 既存JSON Version 2を共通出力境界にするか
- 4ch reduction、CH1/2 pulse、CH3 wave、CH4 noiseへのmapping責務
- timing/quantization、tempo/TicksPerRow、loop境界
- Human inputと完全自動処理の境界
- source/corpus/model/outputのprovenanceとlicense
- deterministic build、seed、model/tool/promptの記録
- 音楽品質・長時間loop・SFX共存のHuman評価方法

## Questions for Human decision

- 完全自動生成を目標にするか。
- 原曲・パブリックドメイン曲の自動編曲を許容するか。
- Humanがmelody/chord/structureを入力する方式を許容するか。
- MIDI/MusicXMLを中間表現として再採用候補にするか。
- corpusを利用する方式を許容するか。
- 外部AI/model/serviceの利用を許容するか。
- provenance・license管理にどの程度の運用コストを許容するか。
- JSON Version 2を維持することを要求するか、別中間表現を許容するか。
- 次に試す方式を一つにするか、組み合わせるか、検討を停止するか。

## Handoff to WBS-001-01683

01683では本比較表とtrade-offを入力として、Humanが方式、組み合わせ、または検討停止を選択する。Codexは最良方式・推奨方式・採用方式を決定していない。
