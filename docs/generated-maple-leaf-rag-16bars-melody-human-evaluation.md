# Maple Leaf Rag 16秒・87音単旋律ROMのHuman試聴記録

## 試聴済みのROM

- ROM: `assets/maple_leaf_rag_16bars_melody.json`から生成した16秒CH1/Pulse1 ROM
- SHA-256: `82773f4ac58a4f676110feb72eeb29e0208c0795a4c46ca213be1ce2f14bfd3f`
- GitHub Actions run: `41580017338`（success）
- Artifact: `maple-leaf-rag-16bars-melody-rom`（artifact ID `13204364519`）
- 試聴方法: SameBoy

## Human試聴結果

| 項目 | 結果 |
|---|---|
| 8〜9秒付近のG♯6がそれぞれ独立した音として聞こえる | OK |
| 12〜13秒付近のG♯5がそれぞれ独立した音として聞こえる | OK |
| 6〜7秒付近の橋渡しフレーズが正常に聞こえる | NG |
| 同音連打にクリック音や不自然な音切れがない | OK |
| 約16秒のループが自然につながり、テンポも問題ない | OK |

変換前の16秒MIDIはHumanが試聴し、問題なしと判断している。従ってHumanの評価では、現在のROMへの変換後にだけ橋渡し区間の問題が観測されている。ただし、MIDIとROMの聴感差の原因をこの結果だけで特定してはいない。

## 追加比較ROMと試聴結果

以下の2 ROMを同じSameBoy環境で比較した。現行ROMは対照、`bridge_octave_up`は6.25〜7.375秒のevent 30〜38のJSON音名だけを各+12半音した候補である。発音row、音長、rest、instrument、loopは同一。採否はHumanの聴感で判断した。

| ROM | SHA-256 | 橋渡しのJSON音名 |
|---|---|---|
| 現行版（対照） | `82773f4ac58a4f676110feb72eeb29e0208c0795a4c46ca213be1ce2f14bfd3f` | G#4, G#4, B4, G#5, G#4, G#5, B5, G#5, G#4 |
| +12半音候補 | `08564ccf6793d35e3bd7f3fcdaf5c6ab7fc654f6b4b7c4481fa69db9925ea5fb` | G#5, G#5, B5, G#6, G#5, G#6, B6, G#6, G#5 |

比較時の確認項目:

1. 6.25〜7.375秒の9音がフレーズとして自然か。
2. 8〜9秒のG♯6連打と12〜13秒のG♯5連打が、両ROMで個別の発音として聞こえるか。
3. 同音連打にクリック音や不自然な音切れがないか。
4. 他区間、休符、16秒ループ、テンポが崩れていないか。
5. 2案とも不自然なら、問題の聞こえ方と希望する方向（旋律らしさ、音域、原曲らしさ）を記録し、次の候補選定に使う。

比較用ArtifactはGitHub Actions [run `41586140138`](https://github.com/ak-sekine/pocket-sweeper/actions/runs/41586140138)から取得できる。runはsuccess、artifact IDは`13207473800`、名前は`maple-leaf-rag-bridge-comparison-roms`、期限は2026-12-03。iPhoneではrepository → Actions → “Maple Leaf Rag melody ROM” → run `41586140138` → Artifacts → `maple-leaf-rag-bridge-comparison-roms` を開く。

## Humanによる比較結果（2026-11-03）

- 採用済み87音MIDI: 違和感なし。
- 現行ROM: 6〜7秒の橋渡しに違和感がある。
- bridge +12半音候補ROM: 現行ROMより違和感が大きい。
- +12半音候補は不採用。現行の楽曲データを維持する。
- 橋渡しフレーズの原因は未特定。

この比較結果は聴感評価のみを記録し、原因診断や自動変換の正しさを意味しない。詳細なMIDI→JSON→UGE→ASM→APU経路と未確定の技術的原因は`docs/generated-maple-leaf-rag-bridge-diagnosis.md`に記録する。`docs/generated-pd-maple-leaf-rag-bridge-evaluation.md`はこの比較試聴記録と役割が重なるため作成せず、Human評価は本ファイルへ集約する。

## 状態

比較ROMの試聴は実施済みだが、現行案にも+12半音案にも違和感が残るため、橋渡しフレーズは未解決である。現行の楽曲データを維持し、原因も未特定のままとする。WBS-001-01771はincompleteを維持する。
