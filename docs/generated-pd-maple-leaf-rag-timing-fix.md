# Maple Leaf Rag timing修正・再生成記録

## Scope

WBS-001-01705〜01708のmachine workとして、MIDI→MusicXML→NormalizedScoreの音符開始時刻を修正し、Maple Leaf Rag prototypeをROMまで再生成した。音楽品質、Human試聴、production採用は未評価である。

## 何がおかしく、何を直したか

修正前は、音符間のgapがMusicXMLに明示されず、chord・重複音符のcursorも正しく復元できなかった。修正後は、2/4のmeasure長を768 source ticks（PPQ 384）として使い、gapを`forward`、重複区間を`backup`/`forward`、同時音を`chord`で表現した。parserもnote、chord、forward、backup、restを処理するようにした。

## MusicXML timing semantics

- divisions: 384 ticks per quarter note
- source meter: 2/4
- measure length: `384 * 2 * 4 / 4 = 768` ticks
- gap: `forward/duration`
- same onset: first note plus subsequent `chord`
- overlapping notes in one part: `backup` to the earlier onset and `forward` to restore the main cursor
- pickup: source tick 0からの絶対座標を維持し、partごとの先頭gapはforwardで表現した。pickupという楽曲解釈を新たに推測していない。

## Source and hashes

- source: Mutopia `Mutopia-2011/11/13-23`
- source MIDI SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- output directory: `/tmp/pocket-sweeper-01705/artifacts`
- generated MusicXML: `/tmp/pocket-sweeper-01705/artifacts/maple_leaf_rag.generated.musicxml`
- generated MusicXML SHA-256: `3a776f6875e2becb8117a397301bec36c7873a9dc2847960210866af2dec0779`
- onset diagnostic JSON SHA-256: `67aaf08880dd82a2987cbd4f2f6c787b7f13f2a8b2bd33037d824f7f3ca69e7d`
- JSON Version 2 SHA-256: `ae430375c044f43b699d8649fdd3ad3a3a0d63f50e7279c6257392619fb761f6`
- manifest SHA-256: `02de14fd68e073b3f545b40f65ce5d46e53187d7abf5d4f2c796fe0684dc28f6`
- report SHA-256: `fc9cdfe13c69f22a3a08e68ddbc019415e817507e1327cba1a04431709ad1063`
- UGE SHA-256: `a5cee0cc96fe1dcd64261a0b52952f96f3a882398e0928e3dc76978598563ffd`
- ASM SHA-256: `38aa755ba877acf00456395912a498fc91395c96cbfb5c44e4590fc9bde8ecdd`
- ROM SHA-256: `b0df8665a9a31660dcf5f6989c7483889a9542829eff39ea469fac0787bf14e3`

## Onset preservation

| measure | 修正前 | 修正後 |
|---|---:|---:|
| total events | 2566 | 2566 |
| exact onset | 981 | 2566 |
| mismatch | 1585 | 0 |
| maximum absolute delta | 1152 | 0 |

修正後のdiagnosticは、source MIDI onset、MusicXML semantic onset、MusicXML parser onset、NormalizedScore onsetの全2566件で一致した。実行は同じsource/configurationで2回行い、generated MusicXMLとdiagnostic JSONのhashは一致した。

## 2566 → ArrangementPlan

修正前のcanonical evidenceではNormalizedScore 2566件からArrangementPlan selected 31件、polyphony omission 2535件だった。修正後のprototype reportではNormalizedScoreは2566件、ArrangementPlan相当のchannel eventはpulse1 8件、wave 8件、pulse2 0件、noise 0件の合計16件、polyphony omissionは2550件だった。

これはtiming修正後に同じprototype heuristicを再実行した結果であり、選択数が31から16へ変わったことを示す。どの変化が音楽的に改善したか、またHuman試聴結果との因果は本記録から判断しない。

## End-to-end pipeline

成功した段階:

1. corrected MusicXML generation
2. MusicXML parsing / NormalizedScore
3. ArrangementPlan/prototype JSON Version 2 generation
4. JSON→UGE
5. JSON→ASM
6. RGBDS sound-test ROM build
7. UGE format analysis

RGBDS version: `rgbasm v1.0.1-157-gdecc5f71`（同じtoolchainの`rgblink`、`rgbfix`も成功）。

UGE analyzerではsong version raw 6、tempo raw 6、pattern count 4、order count 1を確認した。JSON/runtime `tempo=6`はTicksPerRowであり、sourceの120 BPMとは別概念である。loop intended metadataはprototype設定どおりnoneである。

## Human試聴用ROM

HumanがSameBoyで再生する修正版ROMは次の1つである。

`/tmp/pocket-sweeper-01705/artifacts/maple-leaf-rag-timing-fixed.gb`

旧ROMとは異なるfilenameにしている。CodexはSameBoy試聴を実施していない。

## 未確認事項

- Humanが修正版をMaple Leaf Ragとして認識するか
- 曲として成立していると感じるか
- 前回ROMとの差
- 音楽品質、聴感、音量、loopの評価
- Pocket Sweeper production BGMとしての採用可否
- 16件への縮約がHuman結果へ与える影響

## Handoff

Humanは修正版ROMをSameBoyで再生し、少なくとも次を原文で回答する。

1. 前回よりMaple Leaf Ragらしく聞こえるか
2. 曲として成立しているように聞こえるか

この結果はWBS-001-01709へ記録する。production採用は別途Human判断とする。
