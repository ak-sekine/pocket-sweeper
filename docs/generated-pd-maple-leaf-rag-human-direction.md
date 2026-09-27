# Maple Leaf Rag Human判断記録

## Scope

WBS-001-01703で、01697〜01702のdiagnostic結果を確認したHumanが、次に調査する改善・追加調査方針を選択した。本記録は判断の記録のみを対象とし、原因調査や実装変更は行わない。

## Human判断

Human原文を改変せず記録する。

> まず、MIDI→MusicXMLで発生している音符のタイミングのズレを調べる。

## 選択した対象範囲

次に調査する対象は、承認済みMutopia Maple Leaf Ragのsource MIDIからgenerated MusicXMLへの音符開始時刻（onset）の差分である。01698で確認された、source MIDI onsetとgenerated MusicXML onsetの差分を詳しく調査する。

## 現在確認済みの事実

01698のcanonical evidenceでは、次のmachine factsが記録されている。

| 項目 | 値 |
|---|---:|
| total note events | 2566 |
| onset exact | 981 |
| onset mismatch | 1585 |
| maximum absolute onset delta | 1152 source ticks |

この数値は差分の存在を示すが、差分の発生箇所や理由を確定するものではない。

## この判断の意味

Humanは、まずMIDI→MusicXML onset差分を調査する次工程を選択した。次工程では、source MIDI onset、parsed MIDI event、MusicXMLのmeasure-local表現、generated MusicXMLのabsolute onset復元、NormalizedScore onsetを段階別に比較する。

## まだ確定していないこと

以下は本判断から確定しない。

- onset mismatchがMusicXML writerで発生したのか
- diagnostic側のabsolute onset復元で差分として観測されたのか
- converter defectが存在するのか
- diagnostic defectが存在するのか
- sourceとMusicXMLの表現差であるのか
- onset mismatchがHuman試聴結果の原因であるのか
- timing修正で音楽的結果が改善するのか
- MusicXML方式を変更・廃止すべきか
- production BGMとして採用できるか

## 未選択事項

role assignment、polyphony reduction、quantization、octave/range transformation、JSON/UGE、runtime、Human再試聴、production採用について、今回新たな選択は記録していない。

## 次工程

WBS-001-01704「MIDI→MusicXML onset差分の発生箇所・理由を特定する」を登録した。次工程では少なくとも、source_event_id、MIDI PPQ、MusicXML divisions、measure長、measure-local onset、absolute onset、2/4 meter、rest、chord、cursor advancementを比較し、差分の規則性と発生stageを確認する。01703ではこの調査を開始しない。

## WBS状態

Human判断を原文・対象範囲・次工程として記録したため、WBS-001-01703はcompleteとする。01704は未実施のためincompleteであり、WBS-001-01696および上位のWBS-001-01684はgroup aggregation ruleに従いincompleteのままとする。
