# Maple Leaf Rag prototype Human試聴評価

## 試聴対象

- WBS: WBS-001-01694
- 対象: WBS-001-01693で生成したMaple Leaf Rag prototype ROM
- source: Mutopia Project `Maple Leaf Rag (Mutopia-2011/11/13-23)`
- 再生環境: SameBoy
- machine validation: 01693の記録を参照
- 評価者: Human

## Human原文

以下はHumanから得た原文であり、改変していない。

> Maple Leaf Ragとは全く違う曲になっていました。

追加確認への回答:

> 曲としても成立はしていませんが、自動作曲よりは進歩しているように感じます。

## 記録できる評価

- 原曲認識: Maple Leaf Ragとして認識できない。Human表現では「全く違う曲」。
- 曲として成立しているか: Human判断では成立していない。
- 過去の自動作曲方式との比較: 「自動作曲よりは進歩しているように感じる」と評価された。
- production BGM: 現prototypeをそのままPocket Sweeperの本番BGMとして採用できるというHuman判断は得られていない。

「以前より進歩している」という評価を、実用可能、本番採用可能、またはMaple Leaf Ragの編曲として成功したという意味には拡張しない。

## 未評価項目

Humanから以下の個別評価は得ていない。Codexは推測で補完しない。

- melody
- bass / accompaniment / rhythm
- tempo
- loop
- Game Boy BGMとしての個別の聴感

## 原因と今後の切り分け

今回確認できたのは、現在のprototype ROMに対するHuman試聴結果だけである。原因は確定していない。

今後は、MIDI → MusicXML → NormalizedScore → ArrangementPlan → quantization/polyphony reduction → JSON → UGE/ASM/ROMの各境界を切り分ける必要がある。候補にはMIDI由来MusicXML、reconstructed voices/staff/spelling、lost/unknown repeat/endings/articulation/dynamics、role extraction、polyphony reduction、pitch octave transformation、30-tick quantization、64-row windowがあるが、今回の試聴結果だけから原因とは断定しない。

Maple Leaf Rag方式の失敗、PD曲自動編曲方式の不可能、またはMIDI→MusicXML方式の廃止という結論は本記録には含めない。

## Handoff

WBS-001-01694のHuman試聴結果記録は完了した。WBS-001-01695では、このHuman evidenceと01692/01693のmachine evidenceを分離して実用性を評価する。production BGMの正式採用は未決定である。
