# hUGE系Instrument・effect・変換表現範囲調査

対象WBS: `WBS-001-01565`
調査日: 2026-09-25

## 1. 調査範囲

本調査は、Pocket Sweeperで実際に使用しているhUGEDriver、Song Version 6 UGE、JSON Version 1/2、`tools/json_to_uge.py`、`tools/analyze_uge.py`、テストを根拠に、Instrument、Wave、Noise、note、pattern/order、effectの表現可能範囲を整理する。

「hUGETrackerやhUGEDriverに機能がある」ことと、「Pocket SweeperのJSONから自動生成できる」ことは分ける。hUGETracker GUIをこの作業中に操作していないため、GUI表示・再生・保存の未確認事項は文書上で明示する。

## 2. version / 実装基準

- **UGE:** `tools/analyze_uge.py` と`tools/json_to_uge.py`はSong Version **6**を対象とする。UGEには3 bank × 15 Instrument、16 Wave bank × 32 samples、64-row pattern、4 channel order、16 routine recordがある構造として実装されている。
- **hUGEDriver:** リポジトリの`src/hUGEDriver.asm`を基準とする。Song Version 6互換の通常descriptorに加え、Pocket Sweeper独自のVersion 2 descriptor末尾loop metadataを`hUGE_init_v2`で読む。
- **JSON:** `tools/json_to_uge.py`はVersion 1とVersion 2を受け付ける。Version 2では4 channel別order/pattern、loop、Instrument詳細、Wave table、note volumeを扱う。
- **hUGETracker GUI:** `docs/json-v2-4ch-hugetracker-check.md`に人によるSong Version 6確認記録はあるが、本調査で新たにGUI操作はしていない。upstream最新版・別branchの機能は現在のPocket Sweeperへ自動的に適用しない。

## 3. 情報源

### Pocket Sweeperの仕様・実装

- [`docs/json-format.md`](json-format.md): JSON Version 1/2、channel、Instrument、Wave、Noise、note、loop、effect方針。
- [`docs/sound-spec.md`](sound-spec.md): hUGEDriver、4ch、SFX、Noise、BGM loop、現在のSound運用。
- [`src/hUGEDriver.asm`](../src/hUGEDriver.asm): note再生、Instrument load、CH1〜CH4、effect dispatch、order/pattern、mute、loop終了。
- [`include/hUGE.inc`](../include/hUGE.inc): `dn(note, instrument, effect)`、note table、descriptor定数。
- [`tools/json_to_uge.py`](../tools/json_to_uge.py): JSON validation、Instrument/byte packing、pattern/order/loop生成。
- [`tools/analyze_uge.py`](../tools/analyze_uge.py): Song Version 6 binary parser、cell/order/pattern/loop構造解析。
- [`tests/test_json_to_uge.py`](../tests/test_json_to_uge.py)、[`tests/test_analyze_uge.py`](../tests/test_analyze_uge.py): 変換・検証・解析の自動テスト。
- [`docs/json-v2-4ch-hugetracker-check.md`](json-v2-4ch-hugetracker-check.md): Song Version 6のGUI確認手順と既存の人による確認記録。ただし本調査の新規GUI確認ではない。

### 外部技術資料

- [Pan Docs Audio](https://gbdev.io/pandocs/Audio.html)、[Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html): Game Boy APU registerとCH1〜CH4のhardware仕様を照合した。
- hUGETracker / hUGEDriver固有の機能は、まずリポジトリ内の`src/hUGEDriver.asm`、変換コード、テストを優先し、GUI未確認事項を推測で補完していない。

## 4. Pulse Instrument

### 層ごとの対応

| Parameter | hUGE/UGE record | hUGEDriver | JSON Version 2 | converter | 判定 |
|---|---|---|---|---|---|
| Instrument ID/name/type | Duty bank、type/name | channel別bankからID 1〜15を読む | `id`、`name`、`channel` | validation・bank packing | Supported |
| duty | Instrument `Duty` | NR11/NR21へload。effect 9でも変更可能 | `duty` 0〜3相当 | validation・packing | Supported |
| initial volume | Instrument volume | NR12/NR22へload | `initial_volume` 0〜15 | validation・packing | Supported |
| envelope direction/sweep | Instrument volume envelope | NR12/NR22へload | `envelope_direction`、`envelope_sweep` 0〜7 | validation・packing | Supported |
| hardware length | Instrument length/enable | NR11/NR21へload | Version 2の`length` 0〜63、`length_enable` | validation・packing | Supported |
| CH1 sweep | Instrument sweep fields | NR10へload、CH1処理 | `sweep_time`、`sweep_direction`、`sweep_shift`はpulse1のみ | validation・packing | Supported for pulse1 |
| CH2 sweep | UGE record fieldは共通構造でもCH2用途なし | CH2 loadでsweepを読まない | pulse2で指定禁止 | validation rejects | Unsupported for pulse2 |
| note volume | cell effect Cxyとして保持 | `fx_set_volume`がNR12/NR22へ反映 | note側`volume` 0〜15 | Cxyを内部生成 | Supported, not Instrument field |

CH1/CH2のnoteは`C3`〜`B8`のnote indexへ変換される。note側`length`はpattern row数であり、Instrumentのhardware lengthとは別である。restはVersion 2で内部的にE00を生成してnote cut相当として扱う。

## 5. Wave Instrument / Wave table

Waveform（32 sample値）、Wave Instrument（そのtable参照とoutput/length）、note/event（pitch・duration）は別層である。

| Layer | 実装上の表現 |
|---|---|
| Wave table | Version 2の`wave_tables`。最大16 table、各32 samples、各sample 0〜15。UGEには16 × 32のWave bankをpackする。 |
| Wave Instrument | `channel: "wave"`、`waveform`名、`output_level`（mute/100%/50%/25%）、`length` 0〜63、`length_enable`。waveform名をtable indexへ解決する。 |
| Wave note | 共通note `C3`〜`B8`、`length` row数、Instrument ID、note volume。CH3のNR33/NR34 periodとtriggerへつながる。 |
| Wave volume | note側CxyはhUGEDriverがCH3 output levelの4段階へ量子化する。Instrumentのoutput levelと同一ではない。 |
| Wave trigger | JSONでtrigger/frequencyを直接指定しない。driverのnote処理がNR34をtriggerし、CH3のwave RAM安全手順を行う。 |

`json_to_uge.py`はWave tableのsample数・値域、table数、Instrumentのtable参照、output level、lengthを検証する。Version 1ではWave Instrument詳細を公開せず、Version 2で対応する。hUGEDriverの`play_ch3_note`はNR30を一時的に切り、wave RAM更新・再有効化・NR33/NR34書込みを行う。これは発音経路の実装確認であり、waveformがbassとして良いことの確認ではない。

## 6. Noise Instrument

| Layer | 直接指定 / 導出 / 内部処理 |
|---|---|
| Noise Instrument ID/name/type | JSON `id`、`name`、`channel: "noise"`。Noise bank 1〜15へpack。 |
| initial volume / envelope | JSON Version 2の`initial_volume`、`envelope_direction`、`envelope_sweep`。NR42へpack。 |
| hardware length | JSON Version 2の`length`、`length_enable`。NR41/NR44へpack。Version 1は`noise_length`。 |
| LFSR width | JSON Version 2の`width_mode: "15bit"/"7bit"`。UGE InstrumentのCounterStepへpackし、driverがNR43 bit 3へ合成。 |
| Noise note | 共通note `C3`〜`B8`は正確なpitchではなくNoise pitch index。note番号からconverterの`noise_note_to_poly`がclock shift/divisor codeを導出する。 |
| clock shift / divisor | Version 2 JSONのInstrument/noteで直接指定禁止。Noise noteからconverterが導出し、driver/UGE cellのNR43相当polyへ渡す。 |
| trigger | JSON項目ではない。driverの`play_ch4_note`がNR44 high bitを使う。SFX生成ではstep処理がtriggerを立てる。 |
| effect/volume | note volumeはCxyとして内部生成し、Noise Instrumentのenvelope nibbleを維持する。effect入力そのものはnull限定。 |

従って、`lfsr_width`はJSON Instrument parameter、`clock_shift`/`divisor`は現行JSONから直接生成者が指定する低レベルparameterではなく、Noise noteからconverterが導出する値である。完成済みNR43 byte、frequency、triggerもJSON直接指定ではない。

## 7. Note / Event / Pattern / Order

- **note:** channelごとのnote文字列。CH1〜CH3は音高table、CH4はNoise pitch index。
- **rest:** Version 1/2の`rest`。Version 2 converterはE00を内部生成し、hUGEDriverのnote cutで明示的無音にする。通常のhUGEDriver NO_NOTE自体は直前noteを停止しないため、converterの処理が重要である。
- **Instrument selection:** 有効noteのcellにInstrument IDを格納。Instrument 0はJSON入力で禁止、cell上の0はno instrument/blank用。
- **duration:** JSON eventの`length`を64-row pattern内のnote先頭＋空cellへ展開。tick内の任意durationをJSONで直接表現しない。
- **row/tick:** patternは固定64 row。`tempo`はSong Version 6 `TicksPerRow`。effectはrow cellに保持され、driverはtick 0または後続tickで処理する。
- **pattern/order:** Version 2のchannel-local `order`と`patterns`をconverterが共通order matrixへpack。使用order数は全channelで一致させる。UGE analyzerは4 channel order、pattern key、64 cellsを検証・報告する。
- **loop:** Version 2の`full`/`range`/`none`はPocket Sweeper JSONの高レベルmetadata。converterはrangeの必要箇所に内部B effectを生成し、ASM descriptorにはloop metadataも付ける。UGE標準OrderMatrixだけからVersion 2の終了意味を推測しない。

## 8. Effect

### hUGEDriver sourceのdispatch

`src/hUGEDriver.asm`のjump tableは次の0〜Fを実装している。

| Code | hUGEDriver source上の意味 | channel/global | JSON input | converter direct input |
|---|---|---|---|---|
| 0 | arpeggio | channel | null限定 | Unsupported as user effect |
| 1 | portamento up | channel | null限定 | Unsupported |
| 2 | portamento down | channel | null限定 | Unsupported |
| 3 | tone portamento | channel | null限定 | Unsupported |
| 4 | vibrato | channel | null限定 | Unsupported |
| 5 | set master volume | global | null限定 | Unsupported |
| 6 | call routine | global/routine | null限定 | Unsupported |
| 7 | note delay | channel | null限定 | Unsupported |
| 8 | set pan | global | null限定 | Unsupported |
| 9 | set duty | pulse/CH4-specific code path | null限定 | Unsupported |
| A | volume slide | channel | null限定 | Unsupported |
| B | position jump | global/order | null限定 | Internally generated for Version 2 range loop |
| C | set volume | channel | null限定 | Internally generated for Version 2 note volume |
| D | pattern break | global/order | null限定 | Unsupported as user effect |
| E | note cut | channel | null限定 | Internally generated for Version 2 rest |
| F | set speed | global | null限定 | Unsupported |

この表のhUGEDriver列はsource dispatchの確認であり、hUGETracker GUIで各effectを操作した確認ではない。UGE cellにはeffect code/parameterを保持できるが、Pocket Sweeper JSONの`effect`/`effect_param`は初版入力でnull以外を拒否する。

effectの動作はchannel・tick・状態に依存する。例えばCはtick 0でvolumeを変更し、Eは指定tickでnote cut、B/Dはorder/row制御、Fはticks per row変更である。したがって自動作曲器がeffectを直接自由生成するには、loop、tick、状態、各channelの副作用を別途検証する必要があり、現在のgenerator責務には含めない。

## 9. 層別対応表

| 対象 | hUGETracker GUI | UGE Song Version 6 | Pocket Sweeper hUGEDriver | JSON | `json_to_uge.py` | `analyze_uge.py` | 判定 |
|---|---|---|---|---|---|---|---|
| 4 channel order/pattern | 人によるGUI確認記録あり | 4 order lists、pattern keys | order/pattern pointerを処理 | V1/V2対応 | 生成・整合性検証 | 読取・検証 | Supported |
| Pulse Instrument | 既存GUI確認記録あり、今回GUI未操作 | Duty bank 15 records | CH1/CH2 load | V1/V2対応 | 対応 | bank構造は固定skip、詳細意味は解析しない | Supported / analyzer partial |
| Wave table | 既存GUI確認記録あり、今回GUI未操作 | 16×32 bytes | `waves`からCH3へcopy | V2 table | 値域・参照・packing | wave bankを構造上読める | Supported / GUI not verified here |
| Wave Instrument | 既存GUI確認記録あり | Wave bank record | output/length/tableをload | V2対応 | 対応 | Instrument詳細は意味解析しない | Supported / analyzer partial |
| Noise Instrument | 既存GUI確認記録あり | Noise bank record | envelope/length/widthをload | V1/V2対応 | 対応 | Noise bank詳細は意味解析しない | Supported / analyzer partial |
| note/rest/duration | 既存GUI確認記録あり、今回GUI未操作 | cell note/instrument/effect | note trigger/cut | 対応 | 64-row展開、E/C生成 | cell非空数・effectを解析 | Supported |
| User effect | GUI/source機能は未GUI確認 | cell effect field | 0〜F dispatch | null以外拒否 | 直接変換なし | raw effect/B jumpの一部解析 | Partial overall |
| Version 2 loop | Pocket Sweeper仕様 | 標準UGEだけでは表現しないmetadata | `hUGE_init_v2` + B/終了metadata | full/range/none | 対応 | UGE B effectを構造解析 | Supported in Pocket Sweeper path |

## 10. JSON Version 2と変換範囲

### Supported

- `version: 2`、`type`、title、tempo、4 channel別order/pattern、loop mode。
- Pulse Instrumentのduty、length、length_enable、initial volume、envelope、CH1 sweep。
- Wave table、Wave Instrument、output level、length、length_enable。
- Noise Instrumentのlength、length_enable、initial volume、envelope、width mode。
- note、rest、Instrument ID、event length、note volume。
- channel/order数、pattern参照、64-row上限、note range、Instrument ID、値域のvalidation。

### Partial / Derived

- Note volumeはJSONに存在するが、UGE `Cell.Volume`へ直接packせず、Cxy effectへ変換する。
- Noise noteは音高ではなく、clock shift/divisorを導出するindex。
- `loop.range`は高レベルJSONから内部B effectとVersion 2終了metadataへ変換される。
- UGE analyzerはSong Version 6の構造、effect raw値、B jump、order/patternを扱うが、Instrument semantics、NR43、全effectの再生意味は解析しない。

### Unsupported in current JSON input

- ユーザー指定のeffect code/parameter（null以外）。
- Pulse2のsweep項目。
- Wave Instrumentの`trigger`、`frequency`直接指定。
- Noise Instrument/noteの`clock_shift`、`divisor_code`、完成NR43、`frequency`、`trigger`直接指定。
- JSONからの任意tick duration、任意pattern row effect、hUGE routine内容。

## 11. JSON → UGE → hUGEDriver

1. JSON validatorがversion、channel、order、pattern、Instrument、Wave table、note、loopを検証する。
2. event `length`を64-row cell列へ展開し、Instrument ID、note、effect code/paramをcellへ格納する。
3. Version 2ではnote volumeにCxy、restにE00、range loop終端にB effectをconverter内部で付加する。
4. Instrumentは3 bank × 15 record、Wave tableは16 bankへpackし、Song Version 6 binaryを生成する。
5. `analyze_uge.py`はversion=6、bank/pattern/order/routineサイズ、cell、order整合性、B effect loopを解析する。全Instrument/effectの意味を保証しない。
6. hUGEDriverはdescriptorからorder/instrument/routine/wave pointerを初期化し、各rowでInstrumentをAPU registerへload、note period/polyを計算、effectをdispatchする。
7. CH3はwave RAMを更新してからtrigger、CH4はNoise polyとNR44 triggerを更新する。SFX mute maskはBGM channel処理を抑制する。

この経路はbinary/assembly上の接続確認であり、今回の作業でhUGETracker GUI、実機、エミュレータ、聴感の新規確認は行っていない。

## 12. 01558〜01564のparameter対応

| 高レベルparameter | 現行での扱い |
|---|---|
| `accompaniment_pattern` / `bass_pattern` / `rhythm_pattern` | Generatorがnote列、rest、length、pattern/orderへ展開すれば直接生成可能。音楽的適否はHuman evaluation。 |
| `chord_tone_selection` / `bass_note_selection` | Generator側のnote選択。UGEは最終note indexのみ保持し、理論関係は保持しない。 |
| `waveform` | Wave table samplesを生成し、Wave Instrumentのwaveform参照へ変換可能。理想波形名の聴感はHuman evaluation。 |
| `output_level` | Wave Instrumentでmute/100%/50%/25%として生成可能。note volumeは別途Cxyで4段階化。 |
| `noise_texture` | 高レベル名は直接保存しない。`width_mode`、Noise note、envelope等の低レベル候補へconverter前に写像する必要がある。 |
| `lfsr_width` | Version 2 Noise Instrumentの`width_mode`へ直接生成可能。 |
| `clock_shift` / `divisor` | 現行JSON直接指定不可。Noise noteからconverterが導出可能。任意値生成にはconverter拡張が必要。 |
| `density` / `variation_amount` | 高レベルGeneratorがevent列やlayer presenceへ変換。UGEに高レベル意味は保持しない。 |
| duty/envelope/register/note length | duty/envelopeはInstrument、note lengthはcell展開、registerはnote値として生成可能。良否はHuman evaluation。 |

## 13. Generator / Converter責務

### Generatorが直接決める候補

motif、accompaniment/bass/rhythm pattern、note、onset、duration、rest、Instrument ID、pattern/order、loop意図、高レベルnoise texture候補、wave table候補。

### Converterが導出・検証するもの

64-row cell、note index、UGE binary fields、Instrument bank packing、Wave bank packing、Noise noteからNR43相当poly、width bit、C/E/B internal effects、order/pattern references、Version 2 loop metadata。

### 現在Generatorへ直接渡せないもの

任意effect、完成NR43、clock shift/divisorの直接指定、trigger、frequency、driver内部state、hUGE routine。必要なら後続WBSで仕様・converter・テストを同時に拡張する。

## 14. Validation境界

機械検証する項目:

- JSON version/type、Instrument ID 1〜15、channel compatibility。
- Pulse duty、volume、envelope、length、CH1 sweepの範囲。
- Wave table数、32 sample数、sample 0〜15、Wave Instrument参照、output level、length。
- Noise width mode、volume、envelope、length、Noise note C3〜B8、内部NR43導出範囲。
- note、rest、event length、64-row上限、pattern/order参照、全channel order数。
- effect入力がnullであること、内部生成C/E/Bの衝突・loop条件。
- UGE Song Version 6、pattern cell、order terminator、routine、truncation、未参照pattern等。

機械検証しない項目:

waveform/dutyの良さ、bass register、noise texture、percussion-likeな認識、density、attention、long-loop fatigue、harmony、layer欠落時の自然さ。

## 15. Supported / Partial / Unsupported / Not verified

### Supported

Song Version 6 binary構造、JSON Version 1/2の現行項目、4 channel order/pattern、Pulse/Wave/Noise Instrumentの現行公開field、Wave table、note/rest/length、内部C/E/B、hUGEDriverの0〜F effect dispatch、Version 2 loop経路。

### Partially supported

Effect全般（driverは実装、JSON直接入力は不可）、note volume（Cxy変換）、Noise texture（高レベル名なし、低レベルfield/indexへ写像）、loop（Pocket SweepermetadataとUGE B effectの二層）、UGE analyzer（構造と一部effectのみ）。

### Unsupported

現行JSONからの任意effect、任意NR43、Noise clock/divisor直接指定、trigger/frequency直接指定、任意tick duration、hUGE routine生成、GUIの全機能をJSONで再現すること。

### Not verified

今回のhUGETracker GUI操作、最新版upstreamとの差分、全effectのGUI入力・保存互換性、実機/エミュレータでの全Instrument/effect聴感、wave/noiseの音楽的品質。

## 16. Human evaluation / 21曲UGE素材

duty、waveform、bass register、noise texture、percussion-likeな聞こえ方、density、attention、long-loop fatigue、harmony、layer欠落は機械仕様から決めない。今回試聴・実機・エミュレータ確認は行っていない。

既存約21曲のUGEはInstrument/effect出現頻度を品質根拠に使用していない。UGE parser/analyzerのformat variation、binary構造、regression確認に限定する。

## 17. Pocket Sweeperへの適用と未対応事項

現行の自動作曲で安全に使えるのは、JSON Version 2の明示項目、note列、pattern/order、Wave table、Instrument、Noise note/index、loop意図を、converterのvalidation範囲内で生成することまでである。高レベル音楽parameterはGeneratorで低レベルnote/layerへ展開し、UGEに高レベルのmotif・density・役割情報を保存する仕様ではない。

未対応事項の候補:

- effectを自動生成入力として許可する場合のsubset仕様とchannel/tick/state検証。
- Noiseのclock shift/divisorを高レベルtextureから直接制御するconverter拡張。
- UGE analyzerによるInstrument詳細、Wave bank、Noise bank、全effect semanticsの解析拡張。
- hUGETracker GUIとupstream version差分の検証。

これらは本WBSで実装せず、必要なら後続WBSへ引き継ぐ。

## 18. 後続WBSへの引き継ぎ

01565完了後、01557配下の01558〜01565はすべてcompleteとなる。次の自動作曲器・GB編曲設計では、まず現行JSON Version 2のSupported範囲を生成対象とし、effect直接生成や高レベルtextureの低レベル写像は別途仕様化する。
