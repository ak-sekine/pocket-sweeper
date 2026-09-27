# Maple Leaf Rag prototype 音程・melody診断

## 結論（先に）

ROMのpulse1で鳴る8音は、source MIDIのP2（prototypeの平均pitch heuristicがmelodyと呼ぶpart）から選ばれています。しかしsource上の連続した8音ではなく、measure 45、47、127〜129に散在しています。選択は音楽的重要性ではなく、roleごとの`(measure-local onsetを30 tick量子化したrow)`で最初に来るeventを残す実装規則です。ArrangementPlan→JSON→UGEでは、確認したpitchの追加変更はありません。

これは構造的なmachine evidenceであり、選択音が正しい主旋律か、Human評価の原因かは判断していません。

## Source / role assignment

- source: Mutopia `Mutopia-2011/11/13-23`, SHA-256 `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- events: 2566
- source pitch range: MIDI 32–92、unique pitches 44

| part | events | pitch range | average | unique pitches | role | channel |
|---|---:|---:|---:|---:|---|---|
| P2 | 1193 | 60–92 | 73.471920 | 29 | melody | pulse1 |
| P3 | 1373 | 32–73 | 54.663511 | 38 | bass | wave |

P2/P3以外のpitched partはなく、harmonyは0、rhythm/noiseは0である。role判定は平均pitch降順で最上位をmelody、最下位をbass（2 partの場合）とする既存heuristicで、主旋律の意味を判定する処理ではない。

## Selected 16 events

以下はsource onset順。`Δ`はsource pitchからArrangementPlan pitchへの半音差。JSON/UGE pitchはArrangementPlanと一致した。

| source_event_id | part/role | measure | onset tick | source | plan | Δ | group size | plan row | JSON row | channel |
|---|---|---:|---:|---|---|---:|---:|---:|---:|---|
| midi:t2:e210 | P3/bass | 23 | 17088 | G#1 (32) | G#3 (56) | +24 | 314 | 6 | 9 | wave |
| midi:t2:e211 | P3/bass | 23 | 17184 | G#2 (44) | G#3 (56) | +12 | 5 | 10 | 15 | wave |
| midi:t2:e213 | P3/bass | 23 | 17376 | G#3 (56) | G#3 (56) | 0 | 5 | 16 | 24 | wave |
| midi:t2:e215 | P3/bass | 23 | 17568 | G#3 (56) | G#3 (56) | 0 | 5 | 22 | 33 | wave |
| midi:t1:e337 | P2/melody | 45 | 34080 | F4 (65) | F4 (65) | 0 | 103 | 10 | 18 | pulse1 |
| midi:t1:e359 | P2/melody | 47 | 35808 | D4 (62) | D4 (62) | 0 | 192 | 16 | 24 | pulse1 |
| midi:t2:e985 | P3/bass | 103 | 78336 | C2 (36) | C3 (48) | +12 | 323 | 0 | 0 | wave |
| midi:t2:e1052 | P3/bass | 110 | 83808 | G3 (55) | G3 (55) | 0 | 5 | 3 | 6 | wave |
| midi:t2:e1197 | P3/bass | 125 | 95616 | C#2 (37) | C#3 (49) | +12 | 389 | 13 | 18 | wave |
| midi:t1:e1051 | P2/melody | 127 | 96864 | D4 (62) | D4 (62) | 0 | 140 | 3 | 6 | pulse1 |
| midi:t1:e1053 | P2/melody | 127 | 97152 | D4 (62) | D4 (62) | 0 | 199 | 13 | 21 | pulse1 |
| midi:t1:e1057 | P2/melody | 127 | 97440 | C#4 (61) | C#4 (61) | 0 | 168 | 22 | 33 | pulse1 |
| midi:t1:e1060 | P2/melody | 128 | 97728 | C4 (60) | C4 (60) | 0 | 166 | 6 | 12 | pulse1 |
| midi:t1:e1063 | P2/melody | 128 | 98112 | D#4 (63) | D#4 (63) | 0 | 116 | 19 | 27 | pulse1 |
| midi:t1:e1066 | P2/melody | 129 | 98304 | D#4 (63) | D#4 (63) | 0 | 109 | 0 | 0 | pulse1 |
| midi:t2:e1372 | P3/bass | 144 | 110400 | G#1 (32) | G#3 (56) | +24 | 327 | 19 | 27 | wave |

selection ruleは、role eventsを`(start, pitch, event_id)`でソートし、同じrole/local rowの最初のeventを残すもの。音楽的重要性・旋律判定・最高音選択ではない。selected/omitted countsはmelody 8/1185、bass 8/1365、harmony 0/0、rhythm 0/0。

## Melody continuity

melody selected 8音のsource measureは`45, 47, 127, 127, 127, 128, 128, 129`。従ってsource上で連続する8音ではなく、少なくともmeasure 45〜129に分散したevent列である。source pitch列は `65, 62, 62, 62, 61, 60, 63, 63`、隣接intervalは `-3, 0, 0, -1, -1, +3, 0` 半音。octave adjustmentはなく、prototype pitch intervalも同じ値だが、source上の間に多数のomitted melody eventsがある。これは「pitch intervalが一致した」ことと「原曲melodyが保持された」ことを同一視しない。

## Omitted pitch / octave

2550 omitted eventsの内訳はmelody 1185、bass 1365、harmony 0、rhythm 0。selected 16のoctave adjustmentは unchanged 11、+12 が3、+24が2、-12/-24は0、range rejectionは0。pitch classが維持されるshiftでもabsolute MIDI pitchは変化している。

## JSON / UGE

ArrangementPlan pitchからJSON noteへの比較は16/16 exact。JSONはpulse1 8、wave 8で、JSON→UGEも01701のformat-level evidenceで16/16 exact、mismatch 0。確認した範囲ではUGE/ASM/runtime向けに追加のpitch transformationはない。APU周波数やHuman聴感は本診断範囲外である。

## Harmony / noise

harmony 0はsourceに音がないという意味ではなく、今回の2 part構成ではrole rankingにより全P2をmelody、全P3をbassへ割り当てたためである。noise 0はpiano MIDIをnoise roleへ変換する処理がなく、CH4 policyがunusedだからである。これらを音楽品質の結論とはしない。

## Machine conclusions / non-conclusions

確認できたのは、role割当、selected 16のsource位置とpitch、selection rule、octave変換、JSON/UGE pitch一致である。確認できないのは、melody roleが人間にとって正しい主旋律か、bassが正しいか、これがHumanの「音程が違う」の原因かである。長さ・テンポ・リズムにも変換が確認されているため、単一原因は断定しない。

## Reproducibility

実行:

```text
python3 tools/analyze_pd_pitch_melody_diagnostic.py /tmp/pocket-sweeper-01705/maple.mid /tmp/pocket-sweeper-01705/artifacts /tmp/pocket-sweeper-01714/run1
python3 tools/analyze_pd_pitch_melody_diagnostic.py /tmp/pocket-sweeper-01705/maple.mid /tmp/pocket-sweeper-01705/artifacts /tmp/pocket-sweeper-01714/run2
```

run1/run2 hash: diagnostic JSON `8df2be09de43bba23e4fa8ce62538f32750775d5c07d881914319ced38960eff`、Markdown `e59501cc66a2bee862af7a1ff47bb46120f687202eb08dafb76022a8a5bba04c`。

## Handoff

WBS-001-01715で、診断結果を確認したHumanが改善対象を選択する。Codexは音楽品質や改善方針を代行しない。
