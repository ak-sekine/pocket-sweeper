# Game Boyハードウェア由来の作曲生成ルール

対象WBS: `WBS-001-01572`
調査基準日: 2026-09-26

## 1. 目的

`docs/game-boy-apu-4ch-constraints.md`（01559）で確認したAPUの事実を、自動作曲器が守る生成ルールと機械検証条件へ変換する。本書は作曲上の良し悪しを決める文書ではなく、発音可能性、値域、変換経路、SFX共存の境界を定義する。

CH1=melody、CH3=bass、CH4=drumsのような役割は、ハードウェア事実からは導出しない。Pocket Sweeper固有の運用方針は別分類で記録し、音程、scale、motif、phrase、harmony、rhythm patternの設計は01573/01576へ渡す。

## 2. 根拠資料

### 2.1 調査文書と一次資料の対応

|資料|この文書で利用する根拠|
|---|---|
|`docs/game-boy-apu-4ch-constraints.md`（01559）|CH1〜CH4、レジスタ値域、周波数式、Wave RAM、LFSR、4ch制約、未確定事項。一次資料への対応表を含む。|
|Game Boy CPU Manual 1.01, pp.39–50|NR10〜NR52、duty、envelope、frequency、length、Wave RAM、NR43のレジスタ値域。参照先は01559の[PDF](https://meatfighter.com/gameboy/GBCPUman.pdf)。|
|Pan Docs Hardware Registers / Audio|現行のレジスタ名、ビット配置、CH種別の照合。01559の[Hardware Register List](https://gbdev.io/pandocs/Hardware_Reg_List.html)および[Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html)。|
|GbdevWiki Gameboy sound hardware|フレームシーケンサ、DAC、Wave RAMアクセスの補足。01559の[記事](https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware)。|
|`docs/huge-instrument-effect-capability-research.md`（01565）|UGE Version 6、Instrument、note、Wave/Noise、converterが直接指定できる範囲。|
|`docs/json-format.md`|Version 1/2のchannel名、note範囲、Instrument値域、Wave table、Noise note、volume、未対応項目。|
|`docs/sound-spec.md`|BGM/SFXのchannel共有、`hUGE_mute_channel`、現行SFXのCH1/CH4占有とミュート方針。|
|`src/hUGEDriver.asm` / `include/hUGE.inc`|4 channel状態、note table、CH3 Wave RAM更新、CH4 poly導出、mute処理。|
|`tools/json_to_uge.py`|JSON validation、Instrument/Pattern packing、Wave/Noise変換、Version 1/2の受理範囲。|

## 3. ルール分類

- **Hardware invariant**: DMG APUの能力・値域・物理的な同時発音制約。別のドライバでも変わらない範囲。
- **Driver / tool constraint**: hUGETracker/UGE、hUGEDriver、現行JSON/converterが表現・受理する範囲。ハードウェアで可能でも入力できないものを含む。
- **Pocket Sweeper policy**: BGM生成とSFXを共存させる本プロジェクトの運用方針。ハードウェア必須条件ではない。
- **Recommendation / hypothesis**: 音楽的に良い可能性、聴感、役割の候補。01572では確定ルールにしない。

## 4. ルール一覧

|ID|分類|ルール|根拠となる事実|生成器が守る条件|機械検証|適用範囲|未確定事項|
|---|---|---|---|---|---|---|---|
|GB-HW-001|Hardware invariant|APUの独立channelはCH1 pulse、CH2 pulse、CH3 wave、CH4 noiseの4本|CPU Manual/Pan Docs、01559|5本目の独立channelを生成しない。各channel内は同時に1発音状態|可。channel集合とイベント数を検査|DMG APU|役割配分は未確定|
|GB-HW-002|Hardware invariant|1 channelへ和音を同時割当てできない|各CHが単一の発音状態|同一channel・同一rowの同時noteを1つへ解決する|可|全CH|分解・省略の音楽判断は01573/01576|
|GB-HW-003|Hardware invariant|CH1/CH2 pulseのdutyは4値|NR11/NR21の2 bit|dutyは0,1,2,3だけ|可|CH1/CH2|どのdutyが適切かは未確定|
|GB-HW-004|Hardware invariant|周波数dataはpulse/waveとも0..2047|NR13/14、NR33/34|レジスタ値を範囲内にする|可|CH1〜CH3のpitch経路|音楽的な実用音域は未確定|
|GB-HW-005|Hardware invariant|周波数sweep capabilityはCH1だけ|NR10がCH1専用|CH1以外へsweep capabilityを割り当てない|可|CH1〜CH4|overflow時の音楽効果は未確定|
|GB-HW-006|Hardware invariant|CH3は32個の4-bit Wave sampleを再生する|Wave RAM 16 byte、各sample 0..15|tableは32要素、各値0..15|可|CH3|波形の良さ・役割は未確定|
|GB-HW-007|Hardware invariant|CH3はpulse/CH4のenvelope方式を持たずoutput levelを持つ|NR30/NR32|CH3にpulse/Noise envelope項目を適用しない|可|CH3|音量バランスは未確定|
|GB-HW-008|Hardware invariant|CH4はLFSR noiseであり、通常のpitch channelではない|NR43のshift/divisor/width|CH4 noteを通常の音階pitchとして検証・解釈しない|部分可。channel種別と低レベル項目の禁止を検査|CH4|tonalに聞こえる条件は未確定|
|GB-HW-009|Hardware invariant|CH1/2/4のinitial volume/envelopeとCH3 output levelは別機能|NR12/22/42対NR32|channelに対応しないvolume fieldを生成しない|可|全CH|聴感上の音量比は未確定|
|GB-TOOL-001|Driver / tool constraint|現行JSONのchannel名はpulse1/pulse2/wave/noise|`json-format.md`、converter|未知channelを拒否し、未使用channelは省略可|可|JSON Version 2|将来の形式拡張は別WBS|
|GB-TOOL-002|Driver / tool constraint|CH1/2/3のJSON noteはC3..B8、CH4も同じnote index範囲|hUGE note table 0..71、NO_NOTE=90|有効noteをC3..B8、restへ限定|可|JSON Version 2|CH1〜3のhardware register全域をJSONで直接指定しない|
|GB-TOOL-003|Driver / tool constraint|CH1 sweep fieldはpulse1だけ|converterのpulse1 packing、JSON仕様|pulse2/wave/noiseにsweep項目を出力しない|可|JSON Version 2|hUGE GUIの別version差は未確認|
|GB-TOOL-004|Driver / tool constraint|Noiseのclock_shift/divisor/完成NR43はJSONから直接指定しない|`noise_note_to_poly`がnoteから導出|Noise noteはC3..B8の抽象index、低レベル値はconverterが生成|可|BGM JSON Version 2|SFX JSONは既存の直接step方式を維持|
|GB-TOOL-005|Driver / tool constraint|Wave tableは最大16 table、各32 sample、各0..15|UGE bank、converter validation|table数・長さ・sample値を検証|可|JSON Version 2 / UGE|曲中更新頻度の聴感・実機差は未確定|
|GB-TOOL-006|Driver / tool constraint|note volumeとInstrument initial_volumeを混同しない|CxyとNR12/22/42 packing|initial_volumeは0..15、note volumeも0..15として別検証|可|JSON Version 2|全channelのrest+volume意味は未確定|
|GB-TOOL-007|Driver / tool constraint|patternは64 row、使用channelのorder数は同期する|UGE Version 6、converter|展開後64 row以下、order数不一致を拒否|可|JSON Version 2|可変tempo/effect拡張は別WBS|
|PS-SOUND-001|Pocket Sweeper policy|SFXはBGM channelを一時占有し、`hUGE_mute_channel`でBGM更新を止める|`sound-spec.md`、driver API|占有channelをSFX管理状態へ登録し、BGMの必須構造を未確定channelだけへ置かない|可（割当・状態）/聴感は不可|Pocket Sweeper sound system|仕様中のCH1重要SFX方針とCH2/CH4欠損耐性の適用範囲は後続確認|
|PS-SOUND-002|Pocket Sweeper policy|現行SFXはPulse1=CH1、Noise=CH4、カーソルSFX=CH4|`sound-spec.md`/`src/sound.asm`|SFX channel kindと実CHを一致させる|可|現行SFX|CH2 SFXは未対応|
|PS-SOUND-003|Pocket Sweeper policy|SFX中もBGMの時間位置は進み、終了後に対象channelをunmuteする|`Sound_Update`とdriver mute semantics|BGM order/rowをSFX再生のために巻き戻さない|可（状態遷移）|BGM/SFX共存|CH1を占有した場合の主旋律欠損許容は人の確認が必要|

## 5. CH1

CH1はpulse/squareで、duty、length、音量envelope、frequency、CH1専用sweepを持つ。dutyは`00=12.5%`、`01=25%`、`10=50%`、`11=75%`。hardware frequency dataは0..2047、length dataは0..63、initial volumeとenvelope periodは0..15 / 0..7である。sweepはtime、direction、shift各0..7で、NR10にだけ存在する。

生成ルールは「これらの値域を守る」「sweep項目をCH1以外へ出さない」であり、CH1を必ずmelodyにすることではない。hUGE InstrumentとJSON Version 2はduty、initial volume、envelope、length、CH1 sweepを表現できる。JSONのnoteはC3..B8へ量子化され、frequency registerの全域を利用者が直接指定する形式ではない。

## 6. CH2

CH2もCH1と同じpulse、duty、length、envelope、frequency値域を持つが、NR10相当のsweepがない。したがってCH2へCH1 sweep相当の設定を要求する入力はhardware/tool invalidであり、converterは受理しない。CH2を伴奏・和音・対旋律へ固定することは本書では定義しない。

## 7. CH3

CH3はwave channelで、Wave RAMの32 sample（各0..15）を周期再生する。NR32のoutput levelはmute/100%/50%/25%の4段階で、pulse/Noiseのhardware envelopeとは異なる。lengthは0..255、frequency dataは0..2047である。hUGEDriverはnote発音時にWave RAM更新の安全手順を取り、JSONはWave table名とoutput levelを経由して指定する。

CH3をbass専用とすること、特定波形を良いとすること、tableを曲中どの頻度で更新するかはhardware ruleではない。既存sound-specのCH3土台方針はPocket Sweeper policyまたは後続の作曲ルールとして扱う。

## 8. CH4

CH4はLFSR noiseで、NR43のclock shift 0..15、divisor code 0..7、7-bit/15-bit widthを組み合わせる。lengthは0..63、initial volumeは0..15、envelope periodは0..7である。CH4に通常のfrequency/pitch registerはなく、hUGEDriverは共通note番号からnoise polyを導出する。

従ってJSONの`C3`..`B8`は通常の旋律音程ではなく、converterの決定的なNoise pitch indexである。`NR43`完成値、clock shift、divisor codeをBGM JSONへ直接書かせない。kick/snare/hatという役割名やnoise densityは01572で確定しない。

## 9. 4ch共通制約

独立発音は最大4 channelで、未使用channelは許容する。JSON Version 2ではchannelを省略でき、全channelを常時鳴らすことは要求しない。pattern内で同一channelへ重なるnoteを生成した場合は、単音列へ解決する規則を01576で設計する。ここで「4chすべて常時発音」「特定channelを必ず使用」は定義しない。

## 10. frequency / note範囲

次の層を区別する。

|層|範囲・意味|
|---|---|
|hardware register|Pulse/Wave frequency dataは0..2047。これはレジスタ表現可能域で、音楽的な実用音域ではない。|
|hUGE/UGE note|有効note番号0..71（C3..B8）、rest/NO_NOTEは90。CH4も同じ番号形式だがnoise indexとして使う。|
|Pocket Sweeper JSON|音名C3..B8または`rest`。低レベルfrequency、NR43、triggerを直接指定しない。|
|音楽的適切性|聞きやすい音域、CH間の衝突、noiseのtonal感。hardware ruleではなく01573/01576と人の確認へ渡す。|

## 11. volume / envelope

CH1/CH2/CH4のinitial volumeはNR12/NR22/NR42の0..15で、envelope directionとperiodを伴う。CH3はNR32 output levelの4段階であり、同じenvelopeではない。JSONのInstrument `initial_volume`は基本音量、note `volume`はcell単位のCxy表現である。したがって、CH3のoutput level、pulse/Noiseのenvelope、note volumeを同じフィールドや同じ意味にしない。

## 12. duty / sweep

JSON/converterで指定できるpulse dutyは0..3だけである。CH1 sweepは`sweep_time` 0..7、`sweep_direction` up/down、`sweep_shift` 0..7で、pulse1専用である。sweep capabilityがあることは、すべてのCH1 noteでsweepを使うことを意味しない。CH2/CH3/CH4へのsweep項目は生成禁止とする。

## 13. wave table

Wave tableはUGE上で最大16 table、1 table 32 sample、sample値0..15。JSONの`wave_tables`とWave Instrumentの参照先を検証し、長さ・値域・table数を超える入力を拒否する。特定の波形形状、bass向き、音量の良し悪しはこの制約から導かない。

## 14. noise parameter

経路は `JSON noise note + width_mode` → `json_to_uge.py` の `noise_note_to_poly` → UGE/Instrument → hUGEDriverのCH4処理 → NR43相当のpoly である。現行のBGM JSONはNR43を自由指定する経路ではない。hardware上はNR43の組合せを持つが、自動生成経路では抽象noteとwidth modeだけを入力とする。この差を検証エラーや仕様説明で明示する。

## 15. hUGETracker / hUGEDriver / JSON制約

- Song Version 6は4 channel order、64-row pattern、Pulse/Wave/Noise Instrument bankを持つ。JSON Version 2はchannel別order/patternを使い、使用channelのorder数を一致させる。
- hUGEDriverの`hUGE_mute_channel`は対象CHをdriver処理から外し、SFX等への転用を可能にする。これはAPUのchannel数を増やす機能ではない。
- `effect`は現行JSONで非null入力を原則未対応とする。note volumeは仕様上Cxyへ内部変換されるため、一般effect入力と混同しない。
- `trigger`、低レベルfrequency、DAC enable、完成済みNR43は現行JSONの公開入力ではない。driverがnote処理の一部として生成する。
- Version 1の既存意味をVersion 2の制約で暗黙変更しない。

## 16. Pocket Sweeper SFX共存制約

SFXによる一時muteはGame Boy hardware invariantではない。Pocket Sweeperの現行方針では、Pulse1 SFXがCH1、Noise SFXとカーソルSFXがCH4を占有し、開始時に`hUGE_mute_channel`、終了時に対象CHだけunmuteする。BGMのorder/rowは進め続ける。

これは「CH1を常に空ける」「CH2/CH4を必ず補助にする」というhardware ruleではない。sound-specにはCH2/CH4の欠損耐性とCH1重要SFXの影響に関する方針がある一方、CH1を占有する全SFXとBGM骨格の許容範囲は未確定である。推測で統一せず、01576/01575および必要な人の試聴へ引き継ぐ。

## 17. 機械検証条件

生成・変換時に少なくとも以下を検査する。

1. channel集合が`pulse1`,`pulse2`,`wave`,`noise`の部分集合で、独立channel数が4以下である。
2. 各channelの同一時刻の発音状態が1つ以下である。
3. pulseのdutyが0..3、lengthが0..63、volumeが0..15、envelope periodが0..7である。
4. CH1だけがsweepを持ち、sweep各値が0..7、CH2/CH3/CH4にはsweep項目がない。
5. Wave tableが最大16×32、各sample 0..15で、Wave output levelが定義済み4値である。
6. CH3 lengthが0..255、pulse/wave frequency dataが0..2047である（直接入力可能な場合）。
7. Noise lengthが0..63、volumeが0..15、envelope periodが0..7、widthが7bit/15bitである。
8. BGM JSONのNoiseにclock shift、divisor、完成NR43、低レベルfrequencyを直接指定していない。
9. 有効noteがC3..B8、restが規則に従い、CH4のnoteをpitch品質の検査へ流用していない。
10. pattern展開後が64 row以下、使用channelのorder数が一致している。
11. SFX定義のchannel kindとCH番号が現行方針（Pulse1=CH1、Noise=CH4）に一致している。

値域検査は自動化できるが、音域の適切性、音量バランス、noiseの聞こえ方、SFX中の自然さは機械検証だけで完了扱いにしない。

## 18. 未確定事項

- CH1/CH3を骨格とするsound-specの方針を、一般生成器の必須構造へ適用する範囲。
- CH1 SFX占有時に主旋律欠損をどこまで許容するか。CH2/CH4欠損耐性との仕様上の境界。
- CH4の各Noise indexがどの打楽器・tonal感に対応するか、noise patternの密度。
- 各channelの音楽的に適切な音域、duty、Wave形状、音量比。
- DMG以外のモデル、エミュレータ、実機でのNR43禁止コード・Wave RAMタイミングの差。
- hUGETracker GUIの別versionにおける表示・保存差。現行文書はリポジトリの実装と既存調査を基準にする。

## 19. 後続WBSへの引き継ぎ

- **01573**: scale、melody、motif、harmony、rhythm、bass等の一般音楽理論。ここで定めた4ch・note範囲を前提にするが、役割をhardware factとして扱わない。
- **01575**: 本書の暫定ID（GB-HW/GB-TOOL/PS-SOUND）を正式な根拠・確度・出典schemaへ整理する。
- **01576**: melody/motif/rhythm/harmony/bass/noiseの層を4chへ割り当てる表現、同時発音、SFXによる一時欠損の管理方法を決める。
- **01574**: 既存21曲UGEは品質ルールの根拠にせず、形式・回帰テスト用途として扱う。

## 20. 21曲UGEの扱い

本定義では既存21曲の多数派、channel役割、頻度を使用していない。根拠は01559の調査、一次資料、現行仕様、実装、converter validationであり、21曲は01574の形式・回帰テスト範囲に限定する。
