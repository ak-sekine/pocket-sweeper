# Game Boy APU 4chの音源特性と編曲制約

対象WBS: `WBS-001-01559`
調査日: 2026-09-25
対象ハードウェア: 初代Game Boy（DMG）のAPU

## 結論と範囲

DMGのAPUは、2つのpulse（square）ch、32サンプル×4 bitのwave ch、LFSR noise chの4 chで構成される。各chは単音の発音器であり、4 chを超える独立した同時発音はハードウェア上できない。これは「CH1をmelody、CH3をbass、CH4をdrumにする」という役割決定ではない。役割は後続の編曲・試聴で決める。

以下では、`hardware-valid`（レジスタ仕様として検証できる）と `musically-suitable`（音楽的に聞きやすいか、人が判断する）を分ける。

## 情報源

### Game Boy CPU Manual, Nintendo/Sharp系公式技術資料

- 資料名: *Game Boy CPU Manual*, version 1.01, Nintendo/Sharp系の技術資料。参照先: [PDF](https://meatfighter.com/gameboy/GBCPUman.pdf)、pp.39–50。
- NR10〜NR52のビット配置、duty、envelope、周波数式、length、wave RAM、NR43、routing、NR52を採用した。ハードウェアレジスタの一次資料に準ずるため、数値制約の主根拠とする。
- 同資料のNR43記述には古い表現・禁止コードの説明があるため、モデル差や実装差が問題になる箇所はPan Docsとも照合する。

### Pan Docs, gbdev community

- 資料名: *Pan Docs — Hardware Registers*、gbdev。参照先: [Hardware Register List](https://gbdev.io/pandocs/Hardware_Reg_List.html)。
- NR10〜NR52とWave RAMのアドレス・名称・読み書き属性を採用した。Game Boyハードウェア仕様の広く参照される整理として、公式資料のレジスタ対応を追跡する。

### Game Boy sound hardware, GbdevWiki

- 資料名: *Gameboy sound hardware*、GbdevWiki。参照先: [記事](https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware)。
- DMGのフレームシーケンサ、wave RAMアクセス制約、DACとchの動作差を補足確認した。実機差を含む注意点は「仕様確定値」と「実装・試聴確認」を分けて記録する。

## Game Boy APU全体

- CH1/CH2はpulse、CH3はwave、CH4はnoise。各chは基本的に1つの発振／生成状態を持つため、ch内で和音を同時発音する機能はない。
- NR52 bit7はAPU全体の電源、bit0〜3はCH1〜CH4のON状態である。NR50は左右出力レベル（各3 bit）とVIN入力、NR51は各chをSO1/SO2へ個別routingする。左右へ出せるが、DMG本体スピーカーでは左右分離を音楽上の前提にしない。
- length counterはchごとにあり、triggerは各chの高周波レジスタbit7で発音を再開始する。length enableを有効にすると設定された期間後にchが停止する。
- したがって機械検証できる共通制約は「4 ch以内」「1 ch 1発音状態」「NR50/NR51/NR52の値域・bit配置」「trigger/length enableの整合」である。音量バランス、左右routingが聞きやすいか、ミュート耐性は聴感判断である。

## CH1: pulse / square

- NR10〜NR14を使用する。NR11のdutyは2 bitで、`00=12.5%`, `01=25%`, `10=50%`, `11=75%`。NR11下位6 bitはlength data（0〜63）。
- NR12はinitial volume 0〜15、envelope方向、sweep period 0〜7。period 0はhardware envelopeの変化なし。envelope stepは資料上 `n × 1/64 s`。
- NR13とNR14下位3 bitを合わせたfrequency data `x` は0〜2047。pulse周波数は `131072/(2048-x) Hz`（x=2047は式上の上限付近で、実用音域とは別）。NR14 bit7がtrigger、bit6がlength enable。
- NR10はCH1だけに存在するfrequency sweep。time 0〜7、増減、shift 0〜7を持ち、マニュアル式は `X(t)=X(t-1) ± X(t-1)/2^n`。overflow等の停止挙動は、生成時に無条件で音楽効果として扱わず、後続の実装・試聴対象とする。
- hardware-validにはduty、volume、envelope、frequency、length、trigger、sweepの範囲を含める。主旋律向き、明瞭、聞きやすいdutyや音域はhardware仕様からは決まらない。

## CH2: pulse / square

- NR21〜NR24を使用し、duty、envelope、frequency、length、trigger、length enableはCH1と同じ構造・値域である。
- CH1とのハードウェア差は、CH2にはNR10相当のfrequency sweepがなく、NR21〜NR24の4レジスタだけである。したがってCH2でCH1 sweepを指定することはhardware-invalid。
- CH2を伴奏・和音・対旋律に固定すること、CH1より弱くすること、特定dutyが適することは作曲上の選択であり、この調査の結論ではない。

## CH3: wave

- NR30〜NR34と`$FF30-$FF3F`のWave RAMを使用する。Wave RAMは16 byte、上位nibble・下位nibbleで32個の4-bit sample（値域0〜15）を格納する。
- NR30 bit7はDAC enable。DACがoffなら出力しない。NR32 bit6〜5はoutput levelで、`00=mute`, `01=100%`, `10=50%`, `11=25%`。pulse/CH4のようなhardware envelopeはない。
- NR31はlength data 0〜255、length期間はマニュアル式で `(256-t1)×1/2 s`。NR33/NR34下位3 bitのfrequency dataは0〜2047、周波数は `65536/(2048-x) Hz`。NR34 bit7がtrigger、bit6がlength enable。
- CH3は固定の1-bit pulse dutyではなく、32 sampleの波形を周期再生する。Wave RAMの書き換えは、DMGでは再生中の読み出しタイミングに依存し、アクセスが制限・破損の原因になり得る。hUGEDriver実装も、trigger時にwave RAMを読みながら書き換えないためDACを一時停止する経路を持つ（`src/hUGEDriver.asm`の`play_note3`/`update_ch3_waveform`周辺）。
- waveformをbassやleadへ固定する根拠、特定wave形状が聞きやすいという判断、wave RAMを曲中に安全に更新できる頻度は、hardware-validとは別の実装・聴感検討である。

## CH4: noise

- NR41〜NR44を使用する。NR41のlength dataは0〜63、NR42はCH1/2と同じinitial volume 0〜15、方向、envelope period 0〜7。NR44 bit7がtrigger、bit6がlength enable。
- NR43はclock shift 0〜15、width mode bit（7-bitまたは15-bit LFSR）、divisor code 0〜7。LFSRの幅とclock/divisor/shiftの組合せで乱数列の周期と更新速度が変わる。古いCPU Manualではshiftの14/15を禁止コードとして記載しているため、DMG対象の生成器は対象エミュレータ・実機仕様を明示し、未確認値を音楽データへ許可しない。
- CH4は周波数レジスタで音程を指定するpulse/wave chではない。NR43が決めるLFSR更新の時間スケールによって、音高に近く聞こえる周期的成分が生じる場合はあるが、「pitch付き音程ch」や特定の音名として扱えることは仕様から確定しない。
- `CH4=drums`、tonal noiseの採用条件、密度、kick/snare相当の分類は01564と人の試聴へ引き継ぐ。

## 機械検証可能な制約

生成器は少なくとも次を `hardware-valid` として検査できる。

|項目|検査内容|
|---|---|
|ch種別|CH1/2=pulse、CH3=wave、CH4=noise。各chの専用レジスタ以外を参照しない|
|同時発音|独立状態は最大4、各chの同時noteは1|
|pulse|duty∈{0,1,2,3}、length 0..63、volume 0..15、envelope period 0..7、frequency 0..2047|
|sweep|CH1のみ、time/direction/shiftのbit範囲。CH2には指定しない|
|wave|32 sample、各0..15、length 0..255、output level∈{mute,100%,50%,25%}、frequency 0..2047|
|noise|length 0..63、volume 0..15、envelope period 0..7、shift 0..15、divisor 0..7、width∈{7bit,15bit}。禁止コード方針を対象モデル別に適用|
|共通制御|trigger、length enable、NR50/NR51/NR52のbit値、DAC enableの整合|

上表は発音可能性の検証であり、hUGETracker/hUGEDriverの入力範囲、JSON変換範囲、音楽的な実用音域を意味しない。後者は01565または後続の変換仕様で扱う。

## 作曲ルールとして確定してはいけない事項

CH1=melody、CH2=harmony、CH3=bass、CH4=drums、duty 50%が主旋律向き、特定音域が聞きやすい、一定の音量比が良い、noiseを何密度で使うべき、wave形状がbassに適する、という規則はAPU仕様だけでは導けない。試聴なしに確認済みとしない。

## Pocket Sweeperへの適用

- 4chを超える同時発音を生成しない。ch内和音は単音列へ分解するか、後続の編曲ルールで扱う。
- CH1/CH2でsweep有無を混同しない。CH3のwave envelopeをpulseのenvelopeとして扱わない。CH4をpitch channelとして周波数・音名へ直接変換しない。
- SFXがCH1またはCH4を一時占有すると、そのchのBGM発音状態は失われる。現行`docs/sound-spec.md`のミュート方針を変更せず、BGMの必須情報を特定chだけへ固定する判断は後続の編曲・試聴で行う。
- `docs/sound-spec.md`と`docs/json-format.md`のJSON項目（wave table 32×0..15、pulse sweepはCH1のみ、NR43の詳細値をJSONで直接指定しない等）は、今回確認したAPU仕様と整合する。ただしJSON/hUGEDriverで表現できる範囲の確定は01565の対象である。

## 未確定事項と後続WBS

- 実機または同等エミュレータでの音量、音域、duty、wave形状、noiseのtonal感、SFXミュート耐性は未試聴である。
- 01560は一般音楽理論、01561はmotif/variation/layer、01562はpulse伴奏、01563はwave/bassの具体設計、01564はCH4 rhythm/density、01565はhUGETracker/hUGEDriver/Instrument/effectの表現範囲を担当する。本資料はAPUの能力と物理制約に限定する。

## 21曲UGE素材

既存21曲のUGE素材は品質根拠・channel役割の多数派根拠として使用していない。形式・実装確認が必要になった場合の補助資料に限定する。
