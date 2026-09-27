# Maple Leaf Rag timing-fixed prototype Human評価

## 対象

- 評価日: 2026-09-27
- 対象ROM: `/tmp/pocket-sweeper-01705/artifacts/maple-leaf-rag-timing-fixed.gb`
- 比較対象: WBS-001-01693/01694で評価した旧Maple Leaf Rag prototype ROM
- timing machine evidence: WBS-001-01707

修正版は、source MIDI→MusicXML→NormalizedScoreのonsetが2566/2566 exact、mismatch 0、最大delta 0になった後に生成されたROMである。

## Human原文

> 全然Maple Leaf Ragとは違います。
曲としても成立していません。
曲の長さ、テンポ、リズム、音程がすべて違っています。

原文の意味を変更せず記録した。

## Human evidenceとして確認できること

- Maple Leaf Ragとして認識できなかった。
- 曲として成立しているとは評価されなかった。
- Humanは曲の長さが原曲と違うと感じた。
- Humanはテンポが原曲と違うと感じた。
- Humanはリズムが原曲と違うと感じた。
- Humanは音程が原曲と違うと感じた。
- onset保存性を修正した後のROMでも、Human評価として改善は確認されなかった。

## Machine evidenceとの区別

01707ではMIDI→MusicXML→NormalizedScoreのonsetは全2566件一致した。しかしこれは音符開始時刻のformat-level保存性だけを示す。今回のHuman評価は、その後のrole assignment、polyphony reduction、pitch/range transform、quantization、JSON 64-row representation、UGE/ROM等を含むprototype全体への評価である。

## 未確認の因果関係

今回のHuman原文だけから、2566→16の縮約、polyphony reduction、tempo、pitch、JSON Version 2、hUGEDriver、Game Boy 4ch制約、MusicXML方式のいずれかを原因と確定しない。また、Maple Leaf RagのGame Boy適性、PD自動編曲方式の可否、production BGM採用可否も確定しない。

## 次のmachine diagnostic

WBS-001-01710を追加し、次の4項目をsource MIDIからruntime用データまで段階比較する。

- 長さ: source全体、prototype範囲、ArrangementPlan、JSON 64-row、UGE order/pattern、ROM終了・loop。
- テンポ: source 120 BPM、PPQ、quantization、JSON/UGE TicksPerRow 6、row進行と実時間換算。
- リズム: onset、duration、inter-onset interval、同時発音、omission、rest、row advancement。
- 音程: source pitch、role、selected/omitted event、octave/range、ArrangementPlan、JSON、UGE。

診断結果をHumanが確認してから、改善方針を選択する。今回の評価では修正方針を選択していない。
