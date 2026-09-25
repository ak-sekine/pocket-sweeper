# Game Boy制約下のpulse accompaniment / harmony調査

対象WBS: `WBS-001-01562`
調査日: 2026-09-25

## 範囲と結論

本調査は、一般音楽理論のharmony/accompanimentを、Game Boyの単音pulse channelでどう表現するかを整理する。01560の用語整理、01559のAPU仕様、01561のlayer設計を接続するが、CH1/CH2の固定役割やhUGETracker固有の詳細仕様は決めない。

単音pulseは同時に通常のpolyphonic chordを発音しない。しかし、chord toneを時間方向へ配置するarpeggio、broken chord、pedal tone、ostinato、rhythmic chord-tone pattern等により、和声関係を暗示する候補は作れる。これはhardware-validであることと、聴取者がharmonyとして認識することを分けて評価する必要がある。

## 情報源と採用根拠

### 1. Open University OpenLearn: Arpeggiation

- 資料名: “Voice-leading analysis of music 1: the foreground – 3.4.1 Arpeggiation”
- 組織: The Open University
- URL: [OpenLearn](https://www.open.edu/openlearn/history-the-arts/music/voice-leading-analysis-music-1-the-foreground/content-section-3.4.1)
- 参照内容: 同じchordの音へ跳躍するarpeggiationを、chordを時間的に延長する方法として説明し、表層の音がchord toneであり得ることを示す。
- 採用根拠: 単音を順番に鳴らしても、chord toneの関係を時間方向に表現できるという理論上の根拠とした。認識の保証ではない。

### 2. Ithaca College Music Theory: Texture / Accompaniment

- 資料名: “IC Theory: Texture” / “Accompaniment”
- 組織: Ithaca College School of Music
- URL: [Texture](https://musictech.ithaca.edu/MusicTech/ICTheory/OnlineText/TheoryI/Unit%20I/Texture/Texture.html)、[Accompaniment](https://musictech.ithaca.edu/IPWASite/IPWA/CCPacket/CC18.pdf)
- 参照内容: block/repeated/sustained chord、broken chord、arpeggiated accompaniment、Alberti bass、ornamental tones、bass-afterbeat等を伴奏テクスチャとして区別する。broken chordはchord memberを時間へ展開し、textureを軽くし前進感を作り得るが、harmonyやvoice leading自体を変更する必要はないと説明する。
- 採用根拠: `accompaniment_pattern`を単一の正解でなく、複数パターンの候補集合として表現する根拠とした。

### 3. Fresno State Music Theory: Accompaniment

- 資料名: “Accompaniment”
- 著者・組織: Fresno State music theory teaching material
- URL: [Accompaniment](https://zimmer.fresnostate.edu/~sasanr/Music/Music-Theory/Accompaniment.htm)
- 参照内容: chordal accompaniment、sustained chord、block chord、repeated chord、broken chord、arpeggio、Alberti bass、walking bass、ostinato等を分類する。
- 採用根拠: sustained/pedal、repeated-note、alternating tone、ostinato、arpeggioを、pulse上の候補パターンへ写像する際の用語と適用範囲の根拠とした。

### 4. Berklee Online: Voice-leading paradigms

- 資料名: “Voice Leading Paradigms for Harmony in Music Composition”
- 組織: Berklee Online
- URL: [Berklee Online](https://online.berklee.edu/takenote/voice-leading-paradigms-for-harmony-in-music-composition/)
- 参照内容: conjunct/disjunct motion、bassを最低音の声部として扱うこと、次のchordの声部へmelodicで演奏しやすい接続を考えることを説明する。
- 採用根拠: current chordからnext chordへnote候補を選ぶ際のnearest chord tone、common tone、voice-leadingをsoft rule候補として扱う根拠とした。必須規則にはしない。

### 5. Pan Docs: Game Boy Audio

- 資料名: “Audio Overview” / “Audio Details”
- 組織: gbdev / Pan Docs
- URL: [Audio](https://gbdev.io/pandocs/Audio.html)、[Audio details](https://gbdev.io/pandocs/Audio_details.html)
- 参照内容: Game Boyの4 sound channel、CH1/CH2のpulse、4種類の固定duty、length timer、pulseのduty step、CH1 sweep等を記載する。
- 採用根拠: pulseを同時発音数のない時間的なnote列として扱うhardware境界、duty・length・trigger・sweepの物理的差を確認する根拠とした。音楽的な適否は導かない。

### 6. Pocket Sweeper内部資料・実装

- `docs/game-boy-apu-4ch-constraints.md`: 01559のhardware-validとmusically-suitableの分離。
- `docs/general-music-theory-for-rule-based-generation.md`: chord、chord tone、inversion、voice leading、accompanimentの一般理論。
- `docs/game-bgm-motif-variation-layer-research.md`: accompanimentをlayerとして扱い、densityと欠落時評価を分ける整理。
- `docs/sound-spec.md`、`docs/json-format.md`、`tools/json_to_uge.py`: 4 channel、SFX mute、pulse1/pulse2のJSON表現を確認した。
- 採用根拠: 外部資料の一般原則を現行仕様・実装へ適用する際の境界確認に使用した。既存実装の使用傾向を品質根拠にはしていない。

## Monophonic pulseでのharmony

### 表現候補

| 候補 | 一般理論上の意味 | 単音pulseでのhardware-validな形 | 自動生成候補 | Human evaluation |
| --- | --- | --- | --- | --- |
| arpeggio | chord toneを順に展開する | 時系列の単音note列 | chord tone順序、方向、register | harmonyとして聞こえるか、melodyと衝突しないか |
| broken chord | chord memberを時間へ分散する伴奏 | note onsetを分散したchord-tone列 | pattern、onset、duration、rest | chord identity、前進感、密度 |
| alternating tones | 2つ以上のchord toneを交互に反復 | A-B-A-B等の単音列 | tone pair、順序、反復 | ostinato化や単調感 |
| pedal / sustained tone | 一音を保持し、その上で和声を変化させる | 長いnoteまたは再発音の同音 | pedal pitch、保持期間、変更条件 | next chordとの不協和、調性の明瞭さ |
| ostinato | 同じpatternを区間反復する | patternをorder/rowへ反復 | pattern length、variation | melodyの邪魔、反復疲労 |
| rhythmic chord-tone pattern | chord toneをrhythmで伴奏する | onset、duration、rest、accentの列 | rhythmic pattern、chord-tone selection | harmonic rhythm、拍、密度 |
| implied harmony | 同時chordを鳴らさず関係から和声を想起させる | chord tone、bass等の時間配置 | current/next chord、tone priority | 実際に和声として認識できるか |
| melodyとのinterlocking | melodyと時間・音域・素材を補完する | 別pulseまたは別layerとの交互配置 | onset separation、register、density | foreground/backgroundの明瞭さ |

これらは候補であり、すべてを同時に採用する必要はない。「chord toneを順に鳴らせば必ずchordとして認識される」とはしない。

### Hardware-validとmusically-suitable

- **Hardware-valid:** 1 pulse channelの各時点に複数noteを同時設定せず、許容pitch、length、instrument、duty、volume、envelope等のデータ範囲と4ch時間gridを満たすこと。
- **Theoretical relationship:** noteがcurrent chordのroot/third/fifth等、inversion、scale、next chord、non-chord toneとどう関係するかを記録すること。
- **Musically-suitable:** harmonyが認識できる、melodyを支える、密度・音域・音量が適切、loopやSFX欠落でも成立すること。資料だけでは機械判定できず、試聴が必要である。

## Chord progressionとの関係

生成では、少なくとも`current_chord`、`chord_tones`、`root`、`inversion`、`next_chord`、`scale`、`harmonic_rhythm`を分離する。pulse note候補は、次のような候補集合から選べる。

- chord tone（root、third、fifth等）
- current chordとnext chordのcommon tone
- 次のchordへ近く接続するchord tone
- scale上のpassing / neighbor tone
- pedalとして保持するtone

`root -> third -> fifth`、root開始、common tone使用、chord-tone-onlyを全曲の必須規則にはしない。chord-tone-onlyを選択した生成モードで集合外を禁止することはhard constraint候補だが、どのtoneを選ぶかはsoft ruleまたはparameterである。

## Accompaniment pattern

`accompaniment_pattern`の候補として、`arpeggio_up`、`arpeggio_down`、`broken_alternating`、`pedal`、`ostinato`、`repeated_note`、`rhythmic_chord_tone`、`interlocking`等を持てる。名称は実装仕様ではなく、将来の抽象表現候補である。

各候補は、tone selection、order、register、onset、duration、rest、accent、variation、chord change時の再計算を別parameterにする。具体的なpattern長、note density、rest量、variation量、default patternは本調査では決定しない。

## Melodyとの関係

一般的なvoice leadingでは、声部を次のchordへmelodicに接続すること、stepwiseまたはleap、common tone等を検討する。編曲上は次を候補として評価する。

- **register:** melodyと同じpitch/registerに集中し過ぎる場合のmasking、octave separation、voice crossing。
- **motion:** contrary/similar motion、parallelな動き、melodyとの独立性。
- **doubling:** melodyを補強する同音・octave doubling。ただしforegroundを強める可能性がある。
- **rhythm:** onsetを重ねる、ずらす、休符を入れる、syncopationを使うなどのseparation。
- **density:** accompanimentがmelodyより高密度になりforeground化する可能性。

これらは編曲・聴感のsoft rule候補であり、「必ず1 octave下」「常にcontrary motion」「同時onset禁止」とはしない。melodyの重要性、曲のlayer、register、duty、volumeとの組合せを試聴する。

## Rhythm

pulse accompanimentはpitch列だけでなく、`start_tick`、`duration_ticks`、rest、beat position、subdivision、accent、pattern repetition、harmonic rhythmとの関係で生成候補を表す。broken chordのtone順序が同じでも、onsetを均等にするか、beatを強調するか、melodyとずらすかでforeground性と和声の感じ方が変わる。

pattern lengthやnote densityを一般資料からPocket Sweeperの既定値として導かない。rhythmic separation、harmonic rhythmへの追従、motif/layer variationとの関係をsoft rule候補とし、loop・長時間再生で試聴する。

## Duty / Envelope / Register

Pan Docsおよび01559から、CH1/CH2は4種類の固定dutyを持つpulse channelであり、length、frequency、envelope等を持つこと、CH1にはsweepがありCH2にはないことを確認している。JSON/変換実装ではpulse1/pulse2用Instrumentにduty、initial volume、envelope、length等を持たせる一方、初版のeffect入力はnullのみである。

これらから機械的に言えるのは発音可能範囲であり、`25% duty = accompaniment`、特定volume・envelope・registerが常にbackgroundになる、といった規則ではない。duty、音量、note duration、envelope、registerは、音色、foreground/background、masking、反復疲労へ影響し得るparameter候補だが、曲ごとのHuman evaluationを要する。CH1 sweepの有無も、CH1をmelodyへ固定する根拠にはしない。

## 4ch制約

伴奏に1 channelを割り当てると、melody、bass、rhythm、texture等と同時に使える物理layerが減る。候補となる設計判断は次の通りである。

- accompanimentを常時鳴らさず、phraseやchord changeの要点だけで示す。
- sustained/pedalやsparse patternでnote数を減らす。
- melodyやbassと共有されるchord informationを使い、伴奏専用情報を減らす。
- accompanimentをoptional layerとして加減し、他layerとの競合を避ける。
- 伴奏を別channelへ移す候補を持つが、CH1/CH2の固定役割は決めない。

これは4chの資源制約から導く設計候補であり、最適な割当ではない。01561のlayer設計と同様、sparse arrangementやlayer densityは人の聴感を含めて評価する。

## SFX共存

現行仕様ではSFXによりBGM channelが一時mute/占有され得る。pulse accompanimentが欠落すると、chord identity、harmonic rhythm、rhythmic pulse、texture、densityの一部が失われる可能性がある。失われる情報の重要度は、伴奏がmelody・bass・別layerとどの程度共有しているかで変わる。

したがって「伴奏はoptionalだから常に消えてよい」とはしない。通常、伴奏欠落、複数layer欠落、途中復帰を比較し、melody、調性、phrase、拍、loop位置が維持されるか、和声が誤解されないか、復帰が不自然でないかをHuman evaluationする。どのpulse channelをSFXが占有するかは今回決めない。

## 自動生成への利用候補

### Hard constraint候補

- 1 pulse channelの同一時点に複数noteを配置しない。
- pitch、length、time grid、instrument、duty、volume、envelope等がhardware/JSON仕様の範囲内にある。
- `chord-tone-only`モードを選択した場合、選択noteがその時点のchord tone集合に属する。
- pattern、order、channel参照、note durationが構造上整合する。

「良い伴奏」「harmonyとして聞こえる」「melodyを邪魔しない」はhard constraintにしない。

### Soft rule候補

- current/next chordとの関係を保つ。
- common tone、nearest chord tone、smooth voice leadingを重み付けする。
- melodyとのregister、voice crossing、rhythm、accent、densityの衝突を抑える候補を持つ。
- accompanimentのpattern反復、ostinato、pedal、broken chordを曲のlayer目的に応じて選ぶ。
- sparse arrangement、layer density、SFX欠落時の情報共有を評価する。

### Parameter候補

`accompaniment_pattern`、`chord_tone_selection`、`current_chord`、`next_chord`、`common_tone_weight`、`nearest_tone_weight`、`register`、`octave`、`rhythmic_pattern`、`note_length`、`rest_probability`、`density`、`variation_amount`、`duty`、`initial_volume`、`envelope`、`volume`、`layer_presence`。

default値、octave、duty、envelope、volume、density、pattern長、root開始、variation率は決定しない。

### Human evaluation

harmony/chord identityの認識、melodyのforeground性、音の薄さ・密度、register・duty・volumeのバランス、長時間の疲労、loop境界、SFXによる伴奏欠落と復帰の自然さを試聴する。今回、試聴・実機・エミュレータ確認は実施していない。

## Pocket Sweeperへの適用

### 採用候補

- pulse accompanimentをCH2固定ではなく、抽象layerとして生成候補にする。
- current/next chord、chord tones、scale、inversion、common toneからnote候補を作る。
- arpeggio、broken chord、alternating tone、pedal、ostinato、rhythmic chord-tone patternを候補集合として持つ。
- melodyとのregister、onset、duration、density、accentを評価対象にする。
- accompaniment欠落を含む試聴条件を設ける。

### 未確定事項

- CH1/CH2のどちらを伴奏へ使うか。
- accompaniment pattern、chord progression、octave/register、duty、envelope、volume、density、note length、rest、variationのdefault。
- pulse accompanimentがessentialかoptionalか、SFX時にどの情報を他layerへ冗長化するか。
- hUGETracker/hUGEDriverのInstrument/effectへの具体的落とし込み。

## 21曲UGE素材

既存約21曲のUGE素材から、CH2の伴奏頻度、arpeggio頻度、duty、patternを品質ルールとして導いていない。parser/analyzer、format variation、regression用途に限定する。

## 後続WBSとの役割分担

- **01563:** wave channelをbassへ使う具体設計、bassとharmonyの関係。
- **01564:** CH4 noise rhythm / density、伴奏とのrhythmic競合。
- **01565:** hUGETracker / hUGEDriver / Instrument / effectの詳細表現範囲と変換実装。

01562では、pulseの一般的な設計条件とhardware境界のみを扱い、CH1/CH2割当、具体pattern、hUGE effect仕様を確定しない。

## 限界

資料は、単音を時間配置したarpeggio/broken chord等が和声を表現する理論的候補であること、伴奏patternに複数の形式があること、Game Boy pulseに物理的制約があることを支持する。しかし、特定patternが最適、chordとして必ず知覚される、特定duty・register・densityがbackgroundに適する、SFX欠落でも自然に成立する、とは証明しない。これらは生成候補とHuman evaluationへ残す。
