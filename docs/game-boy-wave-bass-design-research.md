# Game Boy wave channelとbass layerの設計条件調査

対象WBS: `WBS-001-01563`
調査日: 2026-09-25

## 範囲と結論

本調査は、bassの音楽的役割とGame Boy CH3 waveのhardware制約を接続する。01560の一般理論、01561のlayer設計、01562のchord-tone候補、01559のAPU仕様を前提にするが、`CH3 = bass`、bass専用channel、具体waveform、octave、pattern、densityは決めない。

bassはchord rootを鳴らす場合も、inversionのthird/fifth、passing tone、pedal、ostinato、stepwise line等を担う場合もある。したがって生成上は`chord.root`と`bass.note`を別概念として扱う候補が必要である。CH3は32 samples × 4 bitのwavetableを単音で再生するhardwareであり、waveform、output level、frequency、length、trigger、wave RAMアクセスは発音可能性を決めるが、bassとして聞き取りやすいかは別の聴感問題である。

## 情報源と採用根拠

### 1. Open Music Theory: Inversion and Figured Bass

- 資料名: “Inversion and Figured Bass”
- 著者: Chelsey Hamm, Samuel Brady
- 組織: Open Music Theory / University of Nebraska Pressbooks
- URL: [Open Music Theory](https://pressbooks.nebraska.edu/openmusictheory/chapter/inversion-and-figured-bass/)
- 参照内容: chordのrootはinversionで変わらず、bass voiceはroot、third、fifth等へ変化すること、bass voiceとchord rootは同じ概念ではないことを説明する。
- 採用根拠: `chord.root`と`bass.note`を分離し、root-based以外のbass候補を許す理論的根拠とした。

### 2. University of Minnesota: Music Composition & Theory

- 資料名: “Understanding Inversions of Triads and Seventh Chords”
- 組織: University of Minnesota Open Textbook Library
- URL: [Music Composition & Theory](https://open.lib.umn.edu/musiccomposition/chapter/understanding-inversions-of-triads-and-seventh-chords/)
- 参照内容: inversionの位置はbassで決まり、bass motionがvoice leadingのimpulseに関係することを説明する。
- 採用根拠: current/next chord、bass motion、smooth connectionをsoft rule候補とする根拠にした。古典的声部書法をPocket Sweeperの必須規則にはしない。

### 3. University of Puget Sound: Passing Tones / Six-four chords

- 資料名: “Passing Tones” / “Other Occurrences of Six-Four Chords”
- 組織: University of Puget Sound
- URL: [Passing Tones](https://musictheory.pugetsound.edu/mt21c/PassingTones.html)、[Six-four chords](https://musictheory.pugetsound.edu/mt21c/OtherOccurrencesofSixFourChords.html)
- 参照内容: passing toneはchord tone間を通過するnon-chord toneであり、bassのpassing、arpeggiated、pedal motion等が和声を延長・接続する例を示す。
- 採用根拠: bass候補をchord-tone-onlyに限定せず、passing、pedal、arpeggiated、stepwiseを別候補にする根拠とした。

### 4. CMU Intro to Computer Music

- 資料名: “Basic waveform shapes” / “Time and frequency”
- 著者: Chris Donahue
- 組織: Carnegie Mellon University
- URL: [Basic waveform shapes](https://www.cs.cmu.edu/~15322/book/ch03/03.html)、[Time and frequency](https://www.cs.cmu.edu/~15322/book/ch05/00.html)
- 参照内容: periodic waveformにはfundamentalとharmonicsがあり、harmonic amplitudeの違いがtimbreを作る。理想化したsaw、square、triangleはharmonic構成が異なり、sawは明るく、triangleはより穏やかという音色差を説明する。
- 採用根拠: CH3 waveformをfundamental、overtone、timbreのparameter候補として扱う根拠とした。ただし32×4 bitのGame Boy wavetableが理想波形と同一とはしない。

### 5. Pan Docs: Game Boy Audio

- 資料名: “Audio Overview” / “Audio details”
- 組織: gbdev / Pan Docs
- URL: [Audio](https://gbdev.io/pandocs/Audio.html)、[Audio details](https://gbdev.io/pandocs/Audio_details.html)
- 参照内容: Game Boyの4 channel、CH3 wave、wave RAM、frequency、length、trigger、CH3のwave再生動作とDMG固有のwave RAMアクセス注意を記載する。
- 採用根拠: CH3のhardware-valid範囲とpulseとの差を確認する根拠とした。音楽的にbassへ割り当てる結論は導かない。

### 6. Pocket Sweeper仕様・実装

- `docs/game-boy-apu-4ch-constraints.md`: CH3が32 sample × 4 bit wave、output level、length、frequency、triggerを持ち、hardware-validとmusically-suitableを分ける整理。
- `docs/general-music-theory-for-rule-based-generation.md`: bass、root、inversion、chord tone、passing tone、accompaniment。
- `docs/game-bgm-motif-variation-layer-research.md`: bassをabstract layerとし、essential/optionalや欠落時評価を分離。
- `docs/game-boy-pulse-accompaniment-harmony-research.md`: current/next chord、chord tone、common/nearest tone、rhythmとの接続。
- `docs/sound-spec.md`、`docs/json-format.md`、`tools/json_to_uge.py`、`src/hUGEDriver.asm`: 現行のCH3 mute/SFX方針、JSON wave table、output level、wave Instrument、wave RAM更新処理。
- 採用根拠: 外部資料をPocket Sweeperの現行仕様・実装へ適用する境界確認に使用した。21曲の使用傾向は品質根拠にしていない。

## Bassの一般的役割

bassは最低域のvoice/lineとして知覚・編曲上の土台になり得るが、音楽理論上のbass noteとchord rootは別である。root positionでは一致するが、first/second inversionではthird/fifthがbassとなり得る。bassは次の役割を単独または組合せで担う。

- chord rootやchord toneによるharmonic support
- inversionを示すbass note
- current chordからnext chordへ向かうvoice-leading
- passing / neighbor toneによる接続・装飾
- pedal pointによる持続的な調性・緊張
- ostinato、stepwise、walking、rhythmic lineによる時間的・拍的基盤

「bassは常にroot」「bassは必ず最低周波数」「bassは常に鳴り続ける」は、一般理論、編曲、Game Boy hardwareのいずれからもこのWBSのhard ruleにはしない。

## Chord / harmonyとの関係

生成時には少なくとも次の情報を分けて扱える。

- `current_chord.root` / chord quality / inversion
- `bass.note` / bass register
- chord tonesとscale
- `next_chord`、common tone、nearest chord tone
- harmonic rhythm

候補noteはroot、third、fifth等のchord tone、inversion note、current/next chordのcommon tone、nearest chord tone、scale上のpassing/neighbor tone、pedal toneから作れる。root/chord-tone weighting、smooth bass motion、stepwise motionはsoft rule候補であり、root開始・root必須・common tone必須ではない。

## Bass pattern候補

| 候補 | 音楽的意味 | monophonic CH3での形 | 生成候補 | Human evaluation |
| --- | --- | --- | --- | --- |
| root-based | rootをharmonic anchorにする | root note列 | root選択、chord change onset | root感、単調さ |
| chord-tone bass | chord toneでharmonyを支える | root/third/fifth等の単音列 | tone weighting、inversion | chord identity |
| alternating bass | 2音以上を交互に置く | A-B-A-B列 | tone pair、rhythm | ostinato化、密度 |
| pedal bass | 同音を保持・反復して緊張や中心を作る | 長いnoteまたは再発音 | pedal pitch、解除条件 | 不協和、飽和 |
| ostinato bass | 区間内でpatternを反復 | patternのrow反復 | pattern length、variation | 疲労、melodyとの競合 |
| stepwise / walking | stepやpassingでchord間を接続 | 隣接pitch中心の単音列 | direction、passing tone | bassとしての流れ |
| rhythmic bass | onset、rest、accentで拍を支える | rhythmic note/rest列 | rhythmic pattern、density | 拍、CH4との競合 |
| arpeggiated bass | chord toneを跳躍展開 | chord toneの時系列列 | order、register、duration | harmony認識、跳躍感 |

候補は併用可能だが、全候補を採用したり、特定patternを最適としたりしない。pattern length、rest量、density、variation量は未確定である。

## Wave channelのhardware特性

01559とPan Docsを前提に、bass layerへ関係する範囲をまとめる。

- CH3はwave channelで、32個の4-bit sample（16 bytes）から1周期のwave tableを扱う。
- frequency、length、trigger、output levelが発音の時間・pitch・音量・停止条件に関係する。
- pulseのhardware envelopeとは異なり、CH3をpulseのenvelope規則で扱わない。
- DMGではwave RAMへのアクセスとCH3再生のタイミングに注意が必要で、driverはnote trigger前後のwave更新順序を考慮する。
- CH3は単音のwave発振状態であり、1 channel内にchordを同時発音しない。複数chord toneを使う場合は時間方向に配置する。

これらは発音可能性の条件であって、CH3をbassにする音楽的根拠ではない。現行hUGEDriverにはCH3 waveform更新処理があり、JSON変換はwave table、wave Instrument、output level、lengthを検証・変換するが、詳細なUGЕ/Instrument/effect仕様は01565で扱う。

## Waveformとbass

周期波形のfundamentalはpitch知覚の基礎となり、harmonic amplitudeの分布はtimbreに影響する。一般的な理想波形では、sawは上位harmonicが比較的強く明るい、squareはodd harmonic中心、triangleは上位harmonicが速く減衰し穏やか、という傾向を教材から確認できる。

ただし、Game Boyの32 sample × 4 bit wavetableは量子化・sample数・output level・再生周波数・実機回路の影響を受けるため、理想sine/triangle/saw/squareと完全同一ではない。waveform名やharmonic contentはparameter候補だが、「triangleがbassに最適」「sawはbass禁止」などの固定規則は作らない。fundamentalが明瞭か、低域でpitchが追えるか、上位harmonicがmelodyやpulseをmaskしないかはHuman evaluationで確認する。

## Register / pitch range

次の3層を分離する。

1. **理論上のbass register:** 低域voiceとして扱う編曲・声部の概念。作品、編成、聴取条件に依存する。
2. **CH3 hardware range:** frequencyレジスタとnote tableが表現できる値域。これは発音可能範囲であり、bass知覚を保証しない。
3. **聴感上のbass range:** 低すぎてpitchが不明瞭、高すぎてmelody/accompanimentと競合、waveformのharmonicがmaskingする等を含む試聴判断。

したがってoctaveや下限を固定しない。生成では`register`、`octave`、`range`をparameter候補として持ち、melody・accompanimentとのseparation、bass noteの連続性、実機/エミュレータでの聞き取りを別々に評価する。

## Rhythm

bassはharmonyだけでなく、note onset、duration、rest、beat position、subdivision、accent、harmonic rhythmを通じてrhythmic foundationになり得る。melody/accompanimentとの同時発音、ずらし、休み、CH4との同期・非同期はforeground、拍、densityに影響する。

CH4 patternを決めるのは01564であり、01563ではbassがCH4 rhythmを支える・補完する・競合する可能性だけを記録する。具体的なbass density、pattern長、rest probabilityは固定しない。

## Melody / Accompanimentとの関係

- bassとpulse accompanimentが同じroot/chord toneを共有するとharmonyを強め得る一方、同じonset・register・音量でmaskingやdensityを増やし得る。
- inversionや別chord toneをbassへ置く場合、accompanimentのchord identityとbass noteの関係を明示する必要がある。
- register separation、contrary/similar motion、doubling、rhythmic separation、sparse arrangement、bassが休む区間を候補として比較する。
- 「常にbassを鳴らす」「pulseとrootを重複させない」「bassを休ませない」は固定しない。曲のlayer構造と聴感で判断する。

## 4ch制約

CH3をbass layerへ使うと、最大4chのうち1つを継続的に消費し、melody、pulse accompaniment、noise rhythm、textureとの選択が生じる。候補は、bassを常時鳴らす、chord change等の要点だけ鳴らす、pedal/ostinatoで少ないnoteから支える、bassを休ませて他layerを前景化する、bassと他layerでchord情報を共有する、である。

これらは資源配分の候補であり、CH3専用bass仕様ではない。bass layerを削減した場合に調性、harmonic rhythm、拍、phrase、motif identityがどう変わるかは01561のlayer評価と接続してHuman evaluationする。

## SFX / layer欠落

現行`docs/sound-spec.md`ではPulse1/CH1とNoise/CH4のSFXが明記され、CH3を通常SFXが占有するとは決められていない。しかし、これは「bassは常に安全」を意味しない。将来のSFX方式変更、別layerの欠落、CH3自体のmute、CH3以外のmelody/accompaniment欠落により、bassの相対的な役割は変化する。

bass欠落時にはroot/調性、inversion、harmonic rhythm、低域の拍、texture、音域の支えが失われる可能性がある。逆にbassだけ残る場合は、harmonyやmelodyが曖昧になる可能性もある。通常、bass欠落、accompaniment欠落、rhythm欠落、複数欠落、途中復帰を比較し、曲が停止・誤った和音・不自然な復帰にならないかを試聴する。今回その確認は実施していない。

## Hardware-valid / Theoretical / Musically-suitable

### Hardware-valid

- CH3のwave tableが16 bytes / 32 samples / 4-bit範囲にある。
- output level、frequency、length、trigger、time grid、note dataが仕様・変換範囲内にある。
- 1つのCH3へ同時に複数noteを置かない。
- wave RAM更新とCH3 triggerの順序・アクセス条件をdriver仕様に反しない。

### Theoretical relationship

- bass noteとcurrent chord root/chord tone/inversionの関係。
- next chord、common/nearest tone、stepwise、passing/neighbor、pedal、harmonic rhythm。
- melody/accompanimentとのvoice-leading、doubling、rhythmic relation。

### Musically-suitable

bassとして聞こえるか、pitchが明瞭か、harmonyを支えるか、melody/accompanimentをmaskしないか、waveform・register・output level・densityが適切か、長時間疲労やlayer欠落時の自然さが保たれるか。資料と機械検証だけでは確定できない。

## 自動生成への利用候補

### Hard constraint候補

- CH3 hardware/JSONのwave table、sample、output level、frequency、length、trigger範囲。
- 1 channel 1発音状態、time grid、pattern/order参照の整合。
- `chord-tone-only`等のモードを選択した場合、bass noteが指定chord tone集合に属すること。

音楽的に良いbass、低ければbass、root必須、triangle必須はhard constraintにしない。

### Soft rule候補

- current/next chordとの関係、root/chord tone weighting。
- common/nearest tone、stepwise motion、passing tone、pedal、smooth bass line。
- melody/accompanimentとのregister、rhythm、density、doubling、sparse arrangement。
- harmonic/rhythmic foundationとCH4 layerの競合を抑える候補。

### Parameter候補

`bass_pattern`、`bass_note_selection`、`chord.root`、`bass.note`、`register`、`octave`、`range`、`rhythmic_pattern`、`note_length`、`rest_probability`、`density`、`waveform`、`output_level`、`variation_amount`、`pedal_probability`。

具体的default、wave sample値、octave、bass range、density、pattern長、root/chord-tone weightingは決めない。

### Human evaluation

bassとして認識できるか、pitchが明瞭か、harmonyを支えるか、melody/accompanimentとのbalance、waveform・register・output level、density、loop/長時間疲労、bass/layer欠落と復帰の自然さを評価する。今回は試聴、実機、エミュレータ確認を行っていない。

## Pocket Sweeperへの適用

### 採用候補

- bassをCH3固定ではなく抽象layerとして扱う。
- `chord.root`と`bass.note`を分離し、inversionを表現できる候補を持つ。
- current/next chord、chord tone、common/nearest tone、passing、pedal、ostinato、stepwiseをbass候補とする。
- waveform、output level、register、rhythm、densityを独立parameter候補とする。
- bassを休ませる候補を持ち、4ch資源とlayer欠落を試聴評価する。

### 未確定事項

- CH3をbass専用にするか、他用途と共有するか。
- bass pattern、octave/register/range、waveform、output level、note length、rest、density、variation。
- root/chord tone/passing/pedalの重み、melody/accompanimentとのdoubling、CH4とのrhythm関係。
- wave Instrument/effectの具体的hUGETracker/hUGEDriver表現。

## 21曲UGE素材

既存約21曲のUGE素材から、CH3がbassに使われる頻度、waveform、octave、root bass、patternを品質ルールとして導いていない。parser/analyzer、format variation、regression用途に限定する。

## 後続WBSへの引き継ぎ

- **01564:** CH4 noise rhythm / density。bassとの同期・競合は本資料の候補を入力として扱うが、CH4 pattern自体は決めない。
- **01565:** wave Instrument、waveform、output level、effect、UGE、hUGEDriverの実際の表現範囲と変換実装。

01563では、bassの理論とCH3 hardwareを接続する条件までとし、CH3専用化、具体wave sample、note range、hUGE詳細を確定しない。

## 限界

資料はbassとchord rootの分離、passing/pedal/ostinato等のbass候補、waveformとharmonic contentの一般関係、CH3のhardware制約を支持する。しかし、特定waveform・octave・pattern・densityが最適、CH3がbassに必須、またはlayer欠落時に自然に成立することは証明しない。これらは生成候補とHuman evaluationに残す。
