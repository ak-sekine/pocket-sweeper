# Maple Leaf Rag 6.25〜7.375秒 bridge診断

## 結論

元MIDIファイルは今回のworkspace/repositoryに存在しない。既存変換レポートに残るイベント値のみを使い、上段・下段trackや伴奏声部の選択を推測していない。既存レポートからJSON、UGE、ASM、hUGEDriverへ進む各段階では、9音の発音順と開始row、休符配置、order継続に不一致は確認できなかった。

ただし、hUGEDriverのnote tableをPulse1の周波数レジスタへ適用すると、現行JSONの音名から得る基音周波数は、同じ標準MIDI音名の周波数より約1オクターブ低い。これは現行の音名・音域と実際のAPU周波数の差として確認できる。event 30〜38だけをJSON上で+12半音した比較ROMを作成した。橋渡し以外を変えずにHumanがA/B試聴するための候補であり、Humanの音楽判断前に修正版採用・問題解決とは扱わない。

## 入力・証拠境界

- 入力はHumanが採用した `maple_leaf_rag_16bars_melody_bridge.mid`、既存記録SHA-256 `b009472e114c5527125c5a56cb58a01683cb7cd8d38b903ea0673a02044820a0`。
- 同MIDIはリポジトリ内・現在のworkspace内で見つからず、独立した再parseはできなかった。
- 従って元MIDIの上段・下段track、9音が元のどの声部から採用されたか、分散和音を旋律化したかは未確認。既存レポートには対象MIDIが1 note track、87音、同時発音0と記録されるが、そこから元の楽譜上の編曲意図は復元しない。
- 既存変換レポートに記録されたevent 30〜38、tick、note名、JSONおよびUGEの照合結果を利用した。

## 9音とタイミング

PPQ 384、120 BPMの既存source recordでは各音が0.125秒。MIDI開始時刻を最近傍1/60秒rowへ量子化すると、開始は次のとおり。JSON/UGE/ASMでは同じ音名・順序・rowである。

| event | MIDI tick | MIDI時刻 | 現行JSON/UGE名 | row | row時刻 | 開始差 |
|---:|---:|---:|---|---:|---:|---:|
| 30 | 4800 | 6.250 s | G#4 | 375 | 6.250 s | 0.000 ms |
| 31 | 4896 | 6.375 s | G#4 | 383 | 6.383 s | +8.333 ms |
| 32 | 4992 | 6.500 s | B4 | 390 | 6.500 s | 0.000 ms |
| 33 | 5088 | 6.625 s | G#5 | 398 | 6.633 s | +8.333 ms |
| 34 | 5184 | 6.750 s | G#4 | 405 | 6.750 s | 0.000 ms |
| 35 | 5280 | 6.875 s | G#5 | 413 | 6.883 s | +8.333 ms |
| 36 | 5376 | 7.000 s | B5 | 420 | 7.000 s | 0.000 ms |
| 37 | 5472 | 7.125 s | G#5 | 428 | 7.133 s | +8.333 ms |
| 38 | 5568 | 7.250 s | G#4 | 435 | 7.250 s | 0.000 ms |

現行JSONは9音をeventとして保ち、row 375〜442に配置する。row 382のE00は同じG#4を続けて再発音するevent 30/31の間にある。同じ演奏を次orderへ維持するrow 384〜389は`hold`。event 38のnoteはrow 442で終了し、直後のrow 442にE00、その後row 443で次のG#4が開始する。既存11か所の同音articulation E00のうち、bridge前後の2か所も維持した。

## JSON → UGE → ASM → Pulse1

- 現行JSONからのUGE再生成結果: `Song Version 6`、`tempo_raw=1`、15 orders、full implicit order cycle、CH1イベント109（87音と22 E00）、CH2/3/4は各0音。
- 既存UGE解析でもbridge onset/note codeは `(375,20),(383,20),(390,23),(398,32),(405,20),(413,32),(420,35),(428,32),(435,20)`。これはJSONの `G#4,G#4,B4,G#5,G#4,G#5,B5,G#5,G#4` と一致する。
- bridge variant UGEは同rowのnote codeだけが `(375,32),(383,32),(390,35),(398,44),(405,32),(413,44),(420,47),(428,44),(435,32)` へ変わる。他のrow/cell、order、tempo、rest、E00、loopは同一。
- ASM exportはugeと同じnote table/indexを表し、Pulse1用Instrument 1のみを参照する。現行・候補ともduty 2、initial volume 11、down方向、envelope sweep 0、CH1/Sweep無効、CH2〜4の音符なし。
- hUGEDriverは毎回の有効note cellで`get_note_period`からperiodを引き、Pulse1のNR13/NR14へ書く。note開始時はhighmaskのtrigger bitで再triggerする。E00はtick 0でAPU envelopeを0にしNR14を書いてcutする。bridgeのE00と次noteは別rowで、変換器/hUGEDriverにbridge固有の再trigger欠落は見つからなかった。
- `hold`はorder境界を越えて状態を維持するために使われる。bridgeのevent 31はrow 383からorder_05末尾とorder_06 row 0〜5をまたぎ、次の音event 32 row 390で新しいnoteをtriggerする。

## APU周波数と音域

`include/hUGE.inc`のnote index、`include/hUGE_note_table.inc`のperiod、およびPulse channel式 `f = 131072 / (2048 - period)` Hzから算出。hUGEDriverのperiod読み出しに追加のoctave補正はない。

| JSON名 | note index | period | Pulse基音 | 標準MIDI同名 | +12候補のJSON名 | 候補period / 基音 |
|---|---:|---:|---:|---:|---|---:|
| G#4 | 20 | 1417 | 207.73 Hz | G#4 415.30 Hz | G#5 | 1732 / 414.78 Hz |
| B4 | 23 | 1517 | 246.84 Hz | B4 493.88 Hz | B5 | 1783 / 494.61 Hz |
| G#5 | 32 | 1732 | 414.78 Hz | G#5 830.61 Hz | G#6 | 1890 / 829.57 Hz |
| B5 | 35 | 1783 | 494.61 Hz | B5 987.77 Hz | B6 | 1915 / 985.50 Hz |

上記は振動数に基づく比較で、SameBoyの音質・音楽性を評価するものではない。hUGE内部のnote labelと標準MIDIの科学的音名に1 octave差がある可能性を示すが、残り78音も同様に変えることは今回の変更範囲外とした。bridge候補は元MIDI音高の周波数に合わせて聴感比較するデータ案である。

## 原因分類

1. **音符データの変換不具合:** JSON→UGE→ASMのbridge音名、発音順、開始row、note数の追加変更は確認されない。元MIDIがないためMIDI→JSONを独立検証してはいない。
2. **GB再生上の周波数問題:** 現行JSON音名に対し実APU基音が標準MIDI同名より約1 octave低い点を確認。candidateは該当9音のみ+12半音。
3. **単旋律編曲でのフレーズ選定:** 元MIDIのtrack/score contentsを確認できないので、元の9音が主旋律か伴奏アルペジオ由来かは判断不能。既存report上は単一note track / monophonic source。
4. **Human NGの最終原因:** まだ未特定。音域差が関連する可能性はあるが、フレーズ選定、音色、周囲との接続その他の聴感差を除外できない。2 ROMのSameBoy比較が次の判別手段。

## 修正案とROM

採用済みJSON/UGE/ASMは対照用として保持し、`*_bridge_octave_up`の並行データを追加した。event 30〜38のピッチ以外は同一。一般converterとhUGEDriverは変更していない。変換レポートで確認済みの8〜9秒・12〜13秒同音articulation E00、rest、約16秒loop、CH1単旋律は両ROMで維持した。

| artifact | path | SHA-256 |
|---|---|---|
| baseline JSON | `assets/maple_leaf_rag_16bars_melody.json` | `2fe5b061b2850bcba702c88eb5965ee019ca73f526bdb2cac642e229dd95e9f1` |
| baseline UGE | `assets/maple_leaf_rag_16bars_melody.uge` | `8127480d9fc8c565312f17cf2548aa3ae9683ebdd4e84a1145a0ce69839f0ed7` |
| baseline ASM | `assets/maple_leaf_rag_16bars_melody.asm` | `e63a3eb0aa472d427fcb44d24190a850f55c6b94eb563a647c906660320beded` |
| baseline ROM | `build/maple_leaf_rag_16bars_melody_original.gb` | `82773f4ac58a4f676110feb72eeb29e0208c0795a4c46ca213be1ce2f14bfd3f` |
| bridge +12 JSON | `assets/maple_leaf_rag_16bars_melody_bridge_octave_up.json` | `21468fed64220951ff64e2585cf1c2a00a523471bd4ca9ae890eb565ac64344c` |
| bridge +12 UGE | `assets/maple_leaf_rag_16bars_melody_bridge_octave_up.uge` | `d8acec7d69bc6255df7d776a30b2785a77d8325999c7ca1cb584cdeff4608595` |
| bridge +12 ASM | `assets/maple_leaf_rag_16bars_melody_bridge_octave_up.asm` | `3a17466cbc596dc61a4912309faf8679dc1eed1a7855a61015cc0acd61c1bf0d` |
| bridge +12 ROM | `build/maple_leaf_rag_16bars_melody_bridge_octave_up.gb` | `08564ccf6793d35e3bd7f3fcdaf5c6ab7fc654f6b4b7c4481fa69db9925ea5fb` |

## 機械検証とHuman確認

- `tests/test_maple_leaf_rag_bridge_octave_variant.py`: +12半音の9音以外のJSON event/cell不変、87発音、960 rows、11の同音articulation E00、expected APU frequenciesを検証。
- RGBDS `rgbasm v1.0.4`、rgbfixでbaselineとcandidateの32 KiB ROMをビルド。baseline ROM SHAはHumanが試聴した既存ROMと一致した。
- `python3 tools/analyze_uge.py`で両UGEがCH1 15 orders、CH1 87音+22 E00、他channel無音、960 row full cycle、loop一致を確認。
- WBS-001-01771でHumanが現行ROMと+12半音候補をSameBoyで比較し、候補は現行より違和感が大きいため不採用、現行データを維持すると評価した。原因は未特定でbridge問題は未解決。Humanの試聴結果の詳細は`docs/generated-maple-leaf-rag-16bars-melody-human-evaluation.md`を参照。
- GitHub Actions [run `41586140138`](https://github.com/ak-sekine/pocket-sweeper/actions/runs/41586140138)はsuccessし、artifact `maple-leaf-rag-bridge-comparison-roms` (ID `13207473800`)に2 ROMを格納した。iPhoneから上記runのArtifacts欄で取得できる。期限は2026-12-03。
