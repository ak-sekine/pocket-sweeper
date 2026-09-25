# Game Boy CH4 noiseのrhythm / density設計条件調査

対象WBS: `WBS-001-01564`
調査日: 2026-09-25

## 範囲と結論

本調査は、一般的なrhythm layer、Game Boy CH4 noise hardware、ゲームBGMの長時間loop・注意・SFX共存を接続する。CH4をdrum専用、kick/snare/hi-hat専用、または特定pattern専用にはしない。

CH4はLFSRによりpseudo-randomな二値出力を作るnoise generatorであり、NR43のclock shift、LFSR width、divisor、NR42のvolume/envelope、NR41/NR44のlength/triggerが、発音可能性とtextureの候補を決める。これらは「percussion-likeに聞こえるか」「beatを支えるか」「長時間で耳障りか」とは別であり、Human evaluationを必要とする。

## 情報源と採用根拠

### 1. Pan Docs: Audio Registers / Audio Details

- 資料名: “Audio Registers” / “Audio Details”
- 組織: gbdev / Pan Docs
- URL: [Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html)、[Audio Details](https://gbdev.io/pandocs/Audio_details.html)、[Audio Overview](https://gbdev.io/pandocs/Audio.html)
- 参照内容: CH4のLFSR、15-bit/7-bit width、NR43のclock shift・divider、NR42 volume/envelope、NR41 length、NR44 trigger、DAC条件、7-bitでより規則的になること、clock設定によるhard/soft textureの差、LFSR lock-upを説明する。
- 採用根拠: hardware-validなnoise parameterと、noise textureについて資料が直接支持する範囲の根拠とした。kick等の楽器名への固定対応は導かない。

### 2. Open Music Theory: Syncopation

- 資料名: “Syncopation in pop/rock music”
- 組織: Open Music Theory
- URL: [Syncopation](https://openmusictheory.github.io/syncopation.html)
- 参照内容: metric pulseの間や期待されたbeat位置への発音・accentが、beat levelのsyncopationを作ることを説明する。
- 採用根拠: CH4のonset、accent、rest、subdivisionを、単なるnoise発音数ではなく、曲全体のrhythmic relationshipとして扱う根拠にした。

### 3. Texas A&M University–Corpus Christi: Advanced Rhythm and Meter

- 資料名: “Advanced Rhythm and Meter”
- 組織: Texas A&M University–Corpus Christi Pressbooks
- URL: [Advanced Rhythm and Meter](https://tamucc.pressbooks.pub/stepstomusictheory/chapter/more-rhythm-meter/)
- 参照内容: meterの強弱、downbeat、弱拍へのaccent、syncopationを説明する。
- 採用根拠: accent density、subdivision、unexpected accentをrhythm layerの設計・評価候補にした。具体的な安全なdensity値は導かない。

### 4. Berndt, Dachselt, Groh: Repetitive Games Music

- 資料名: “A Survey of Variation Techniques for Repetitive Games Music”
- 著者: Axel Berndt, Raimund Dachselt, Rainer Groh
- 書誌情報: *Audio Mostly 2012*, ACM SIGCHI, pp.61–67, [DOI](https://doi.org/10.1145/2371456.2371466)
- 参照内容: ゲーム内滞在時間が不定で音楽がloopされること、exact repetitionが露呈し得ること、反復を変化させる作曲・編曲・生成技法を扱う。
- 採用根拠: short rhythm loop、constant noise texture、accent repetition、variation量を長時間loopの設計候補へ接続する根拠とした。

### 5. Audiokinetic Wwise公式: Interactive Music

- 資料名: “Creating interactive music” / “Re-sequencing and Re-orchestration”
- 組織: Audiokinetic
- URL: [Creating interactive music](https://www.audiokinetic.com/en/public-library/2024.1.8_8893/?id=creating_interactive_music&source=Help)、[Wwise 2012 course](https://www.audiokinetic.com/courses/wwise201/?id=looping_music_segment_using_playlist_container&source=wwise201)
- 参照内容: sequential variation、layered re-orchestration、time-synced music layersを扱う。
- 採用根拠: rhythm layerの追加・削減、variation、segment/transitionを一般的なinteractive audioの参考概念として扱う。Pocket Sweeperへ高度なadaptive systemを導入する根拠にはしない。

### 6. Pocket Sweeperの既存仕様・実装

- `docs/sound-spec.md`: CH4欠落時にもCH1/CH3から拍・フレーズ境界を追える既存方針、Noise SFXによるCH4 mute、human試聴記録。
- `docs/json-format.md`: Version 2 Noise Instrumentのlength、volume/envelope、width_mode、Noise note index、NR43生成境界。
- `docs/game-boy-apu-4ch-constraints.md`: LFSR、7/15-bit、NR43、hardware-valid / musically-suitableの分離。
- `src/hUGEDriver.asm`、`tools/json_to_uge.py`: CH4 note、Noise Instrument、NR41〜NR44、noise poly生成の現行表現。
- 採用根拠: 外部原則と現行仕様・実装を分離し、既存仕様と今回の設計候補を区別するために使用した。

## CH4 hardware

- **LFSR:** CH4はLFSRを使ったpseudo-random noiseで、通常のC4のような正確なpitched note generatorではない。
- **width:** NR43の7-bit modeは15-bit modeより規則性が高く、条件によってpulseに近い質感になる可能性がある。15-bit/7-bitはtexture parameterであり、楽器名そのものではない。
- **clock:** clock shiftとdividerがLFSR clock rateを決める。Pan Docsは低いclockでhard、高いclockでsoftに聞こえる傾向を説明するが、知覚上の役割を固定しない。shift 14/15はclockされず、7-bit切替によるlock-upにも注意する。
- **volume / envelope:** NR42は初期音量とenvelopeを制御する。短いburstの輪郭、減衰、持続感に関係するが、kick/snare等の確定対応ではない。
- **length / trigger:** NR41のlength、NR44のlength enable/triggerが発音長と再開始を決める。pattern上のnote lengthとhardware sound lengthは別である。
- **DAC:** DACがoffの場合、triggerしてもchannelは有効にならない。これはhardware-valid条件であり、percussionとしての適否ではない。

JSON上は、現行Version 2でNoise Instrumentが`length`、`initial_volume`、`envelope_direction`、`envelope_sweep`、`width_mode`を持つ。`clock_shift`、`divisor_code`、完成済みNR43、triggerはJSON利用者へ直接指定せず、Noise noteと変換処理から扱う設計である。hUGETracker/hUGEDriver固有の詳細は01565へ引き継ぐ。

## Noise texture / percussion-like role

hardware parameterと聴感候補を分離する。

| hardware側の候補 | 聴感上の候補 | 注意 |
| --- | --- | --- |
| 短いlength、短いpattern note、envelope decay | short-noise burst、transient-like | kick-like / snare-like等は試聴で確認する |
| 長いlength、低いvolume変化 | long / sustained noise texture | rhythm driveではなくtextureになる可能性 |
| 15-bit width | wide / less periodic noise候補 | 白色雑音としての聞こえ方は実装・音量依存 |
| 7-bit width | narrow / more periodic、metallic候補 | pulse-likeに聞こえる場合があるが音色名へ固定しない |
| clock/divisor/shiftの変更 | hard/soft、高低のtexture候補 | Pan Docsの傾向は役割保証ではない |
| accent、volume、trigger位置 | kick-like / snare-like / hi-hat-like候補 | Game Boy noiseはdrum samplerではない |

「このNR43値がkick」「このwidthがsnare」といった固定対応は採用しない。

## Rhythm layer

rhythm informationを、(1)曲全体のbeat/meter/harmonic rhythm、(2)CH4が追加するnoise event、に分ける。CH4が無くてもpulse melody、accompaniment、bass等がbeat、phrase境界、harmonic changeを部分的に伝えられる場合がある。

CH4で扱える候補は、beat上の発音、subdivision、accent、syncopation、rest、rhythmic ostinato、phrase-ending accent、transition eventである。CH4だけへmotif、loop boundary、chord change、拍の必須情報を集中させないことは、現行仕様と整合する設計候補である。

## Density

`rhythm_density`は単純なevent countだけでなく、次を分離したparameter候補とする。

- event count / onset density
- rest density
- accent density
- subdivision density
- phrase内のdensity変化
- melody、pulse accompaniment、bassとの同時活動
- CH4 layerのpresenceと一時削減

event数が増えるほどrhythmが良くなるとはしない。densityが高いとbeatやdriveが明瞭になる可能性がある一方、noise textureがforeground化し、盤面操作への注意を奪い、長時間疲労を増やす可能性がある。具体的な1小節の音数や安全値は決めない。

## Repetition / Variation

short exact rhythm loop、constant texture、constant accent、休みのないpatternは、長時間再生でpatternやnoiseの反復を意識させ、疲労候補になる。modified repetitionの候補は、accent、rest、onset、subdivision、density、phrase-end event、temporary layer removalである。

一方、variationが多過ぎるとrhythm identity、predictability、beatの安定性を損ない、unexpected eventが注意を奪う可能性がある。fillは常時追加する規則ではなく、phrase/transitionの候補として比較する。N回ごとのfillや確率値は設定しない。

## Fill / Transition

Wwise資料のsegment/transition/layer概念と、01558/01561のvariation整理から、phrase-end accent、pickup、短いfill、layerの一時追加・削減を候補とする。ただしPocket Sweeperの静的4ch BGMに高度なvertical/horizontal adaptive systemを必須化しない。

fillはphrase境界やゲームイベントに対応する可能性があるが、盤面の重要イベントと無関係な強いtransientは注意を引き得る。fillの存在、強さ、頻度、loop境界との接続はHuman evaluationへ残す。

## Attention / Long-loop fatigue

sharp transient、strong accent、high onset density、sudden density increase、unexpected fill、反復する明るいnoise textureは、CH4をbackgroundからforegroundへ移す可能性がある。特に思考中のゲームでは、注意を奪うかを一定のBPMやdensity値から保証できない。

long loopでは、exact repetitionとconstant textureを抑える候補、しかしvariationを増やし過ぎない制約を同時に持つ。初回、複数loop、長時間でbeatの安定性、飽き、耳障りさ、注意、予測可能性を試聴する。今回は試聴していない。

## Pulse / Bassとの関係

CH4とpulse accompaniment/bassの関係は、同期、complementary rhythm、interlocking、sparse placement、rest、doublingの候補である。CH4がbass onsetを倍加する、pulseがbeatを示してCH4は補助accentにする、互いに発音しない位置を作る等を比較できる。

`bassとCH4は常に同じbeat`、`CH4は常にoffbeat`、`CH4だけが拍を示す`とはしない。rhythmic informationは全layerへ分散し、CH4欠落時に曲の骨格が残ることを試聴評価する。

## CH4欠落 / SFX

### 既存仕様

現行`docs/sound-spec.md`では、Noise SFX / cursor SFXがCH4を使用し、開始時にBGM対象channelをmute、終了時にunmuteする。BGMのCH4が一時欠落しても、CH1/CH3から拍・フレーズ境界を追えるようにする方針が既に記録されている。また、Noise単独を主役にせず、CH4復帰時に消音中のfillの続きを要求しない試聴基準も既存仕様にある。

### 設計候補

CH4欠落で失われ得るのは、beatの明示、accent、subdivision、rhythmic drive、phrase-end texture、densityである。melody、pulse accompaniment、bassがbeat、phrase、chord change、loop位置を一部共有する、CH4だけにmotif・boundaryを置かない、復帰時は現在位置から短いeventへ戻る、という候補を整理する。

これは「CH4は何をしてもよい」という意味ではない。通常、CH4あり、CH4 mute、CH4復帰、他layer欠落との組合せで、骨格、誤ったaccent、復帰の不自然さをHuman evaluationする。CH3が現行SFX対象外であることは事実だが、将来の設計変更に対する安全性を保証しない。

## Hardware-valid / Rhythmic relationship / Musically-suitable

### Hardware-valid

- LFSR width、clock shift、divisor、NR41 length、NR42 envelope、NR44 trigger、DACの範囲・整合性。
- pattern/order/time gridとevent配置。
- JSON/driverが表現可能なNoise Instrument、Noise note、volumeの構造。

### Rhythmic relationship

- beat、meter、subdivision、accent、syncopation、rest、phrase boundary。
- melody、pulse accompaniment、bass、harmonic rhythmとの同期・補完・doubling・separation。
- density、repetition、variation、fill、layer presence。

### Musically-suitable

percussion-like texture、beatの分かりやすさ、noisyさ、耳障りさ、foreground/background、長時間疲労、fillの強さ、CH4欠落・復帰時の自然さ。資料と機械検証だけでは確定できない。

## 自動生成への利用候補

### Hard constraint候補

- CH4 hardware parameterとJSON/driverの範囲・整合性。
- time grid、pattern/order参照、event配置、単一CH4発音状態。
- 選択したNoise texture modeに対応するparameterが表現可能であること。

rhythmとして良い、kickに聞こえる、特定densityが安全、はhard constraintにしない。

### Soft rule候補

- beat/subdivisionとの整合、accent配置、restによる密度調整。
- exact repetition、constant texture、強いtransient/fillの頻発抑制候補。
- phrase boundaryでのvariation候補。
- pulse/bassとのrhythmic separation、CH4欠落時の骨格維持。

### Parameter候補

`rhythm_pattern`、`noise_texture`、`lfsr_width`、`clock_shift`、`divisor`、`envelope`、`length`、`density`、`rest_probability`、`accent_probability`、`variation_amount`、`fill_probability`、`subdivision`、`layer_presence`。

default値、kick/snare/hi-hat mapping、pattern長、density、fill頻度、variation probabilityは決めない。

### Human evaluation

beatの明瞭性、rhythmとしての自然さ、percussion-like texture、noiseの耳障りさ、density、attention、long-loop fatigue、variation量、fillの強さ、CH4欠落・復帰、SFXとの競合を評価する。試聴・実機・エミュレータ確認は未実施である。

## Pocket Sweeperへの適用

### 既存仕様

- CH4はNoise SFXで一時muteされる。
- CH4の音量・発音回数・width_mode等について、既存の`docs/sound-spec.md`に試聴結果と運用候補が記録されている。
- CH4をmuteしてもCH1 + CH3から拍・フレーズ境界を追える方針が既存仕様にある。

### 採用候補

- CH4を抽象rhythm/noise layerとして扱う。
- beat、subdivision、accent、rest、density、textureを分離parameter化する。
- exact/modified repetition、phrase-end variation、temporary layer removalを候補化する。
- CH4欠落・復帰を評価条件に含め、必須情報をCH4だけへ集中させない。
- kick-like等は正式楽器名ではなく、試聴用の聴感ラベルに限定する。

### 未確定事項

- CH4を常時rhythm専用にするか。
- rhythm pattern、density、subdivision、rest、variation、fill頻度。
- kick/snare/hi-hat imitationの採否、LFSR width、clock shift、divisor、envelopeのdefault。
- CH4とpulse/bassの同期・interlocking・doublingの選択。

## 21曲UGE素材

既存約21曲からCH4使用頻度、drum-like pattern、density、fill、LFSR設定、envelope、rhythm patternを品質根拠として導いていない。parser/analyzer、format variation、regression用途に限定する。

## 01565への引き継ぎ

01565でhUGETracker/hUGEDriver、Noise Instrument、effect、UGE、noise note、NR43生成、実際の表現可能範囲を調査する。01564ではJSON/driverの実装詳細を確定せず、hardwareとrhythm/density/game-BGM設計の接続に留めた。

## 限界

Pan DocsはCH4 parameterとhard/soft noiseの傾向を支持するが、具体的なdrum imitation、density、fill、注意、長時間快適性を保証しない。rhythm layerの音楽的適否、CH4欠落時の自然さ、実機・エミュレータの聴感はHuman evaluationに残す。
