[PROJECT.mdへ戻る](../PROJECT.md)

# サウンド仕様

## サウンド設計

- hUGEDriver本体は `src/hUGEDriver.asm`、hUGETracker用マクロとノートテーブルは `include/hUGE.inc` / `include/hUGE_note_table.inc` に配置する。
- hUGETrackerから出力したASMデータは `src/*.asm` として配置し、通常のRGBASMビルド対象へ含める。
- 曲データはROM ONLY方針を維持するため、当面は `ROM0` セクションへ配置する。
- `src/sound.asm` がAPU初期化、曲開始、毎フレーム更新を担当する。
- `Sound_Init` はNR52/NR50/NR51を初期化し、BGM再生中フラグとSFX再生状態をクリアする。
- `Sound_PlayTestBgm` はテストBGMの曲ディスクリプタをHLに設定して `hUGE_init` を呼び、再生中フラグを立てる。`Sound_PlayBgmV2` はHLで渡されたVersion 2曲ディスクリプタを `hUGE_init_v2` へ渡す。
- `Sound_Update` はBGM再生中のみ `hUGE_dosound` を呼び出し、その後にSFX管理処理を更新する。
- Version 2 `loop.mode = "none"` の終了判定は、JSONから生成した曲ディスクリプタの終了メタデータとhUGEDriverの再生位置（最終order・最終row）を組み合わせて行う。UGEのOrderMatrixだけから推測しない。`full` / `range` は通常のループ遷移を継続する。
- 非ループ曲が終了したフレームの最終row処理までは `hUGE_dosound` を呼び、その後はBGM更新を停止する。停止状態のhUGEDriverを毎フレーム呼び続ける方式は採用しない。終了後のrow、current_order、tickは終了位置を保持し、再生開始時の `hUGE_init` で初期化する。
- 自然終了時はBGMの音を即時に止める。ただしSFXが占有しているチャンネルは消音対象から除外し、SFXの発音とミュート状態を変更しない。hUGEDriverのチャンネルミュート/note cutまたは同等のBGM専用消音APIを、チャンネル占有状態を確認して使う。hardware envelope、length、自然減衰を終了条件・無音維持の手段にはしない。
- BGM再生状態は少なくとも「再生中」「自然終了」「呼び出し元停止」「新曲による置換」を区別する。終了通知は自然終了イベントを1回だけ観測できる状態フラグとし、`wSoundPlaybackActive` は更新呼び出し可否の内部状態として扱う。停止・置換では自然終了イベントを発生させない。新曲開始時に状態とhUGEDriverを初期化する。
- ゲーム開始時およびリスタート時に `Sound_PlayTestBgm` を呼び、テストBGMを再生開始する。
- `hUGE_dosound` はAF/BC/DE/HLを破壊するため、呼び出し側はレジスタ値を跨いで依存しない。
- SFX管理用WRAMとして、現在の効果音ID、step pointer、残りwait frames、現在のpriority、channel kind、残りstep数、SFX再生中フラグを保持する。
- `Sound_PlaySfx` はAレジスタで効果音IDを受け取り、`SfxTable` からSFXデータを取得してヘッダを読み込む。
- `Sound_PlaySfx` はSFX未再生中なら常に再生開始し、SFX再生中は新しいSFXのpriorityが現在のpriorityより高い場合のみ上書き再生する。同等以下のpriorityは無視し、初版では効果音キューを持たない。
- SFX開始時はchannel kindに応じて `hUGE_mute_channel` で対象チャンネルをミュートする。現行実装ではPulse1効果音はCH1、Noise効果音はCH4を使う。カーソル移動効果音はCH4 / Noiseを使用する。
- `Sound_UpdateSfx` は残りwait framesを更新し、waitが0になったらstep countに基づいて次stepを読み込む。Pulse1 stepではNR10/NR11/NR12/NR13/NR14、Noise stepではNR41/NR42/NR43/NR44へ書き込む。
- SFX終了時は対象チャンネルのミュートを解除し、SFX管理用WRAMとSFX再生中フラグをクリアする。
- カーソル移動効果音は、通常プレイの盤面カーソル移動、難易度選択画面の選択カーソル移動、ポーズメニューの項目移動で `SFX_CURSOR` を共通利用する。
- 十字キー入力があっても画面端やメニュー端などで実際のカーソル位置・選択値が変わらなかった場合は、カーソル移動効果音を鳴らさない。
- 決定、キャンセル、マス開封、旗操作などのSFX呼び出しは後続WBSで行う。

### BGMと効果音の再生制御方針

#### 非ループBGMの終了

`loop.mode = "none"` は最終orderの最終rowを一度処理した時点で自然終了とする。終了判定とBGM更新停止はROM側の `Sound_Update` 系管理で行い、hUGEDriver用生成ASMの終了メタデータを参照する。終了後は `hUGE_dosound` を呼ばず、hUGEDriverの再生位置はデバッグ・状態確認のため終了位置に保持する。Version 2曲の再生開始は `Sound_PlayBgmV2` から `hUGE_init_v2` を呼び、row、current_order、tick、ミュート、終了状態を新曲用に初期化する。

自然終了時の消音は、最終noteのhardware envelopeまたはlengthによる減衰待ちではなく、BGMが管理する4チャンネルの即時消音とする。Pulse（CH1/CH2）、Wave（CH3）、Noise（CH4）は、更新停止だけではAPU上の音が残る可能性があるためである。NR51全体を変更して全音源を切る方法や、APUレジスタを無条件に直接書き換える方法は、SFXを破壊するため採用しない。終了時点でSFXが占有しているチャンネルはそのSFXに任せ、未占有のBGMチャンネルだけをnote cut/ミュートする。

BGM終了後も `Sound_UpdateSfx` は毎フレーム呼び続ける。SFX終了時のunmuteはSFXが占有していたチャンネルに限定し、終了済みBGMを再開させる処理を行わない。BGM自然終了時は `wSoundBgmFinishedEvent` を立て、`Sound_TakeBgmFinishedEvent` が値を返すと同時にクリアする。SFX終了は `wSoundSfxActive` とSFX管理状態で扱い、BGM終了通知とは独立させる。

自然終了時の未占有チャンネル消音は `Sound_SilenceFinishedBgmChannels` が担当する。各未占有チャンネルを `hUGE_mute_channel` でミュートした後、CH1/CH2はenvelopeを0、CH3はDACをoff、CH4はenvelopeを0にする。`wSoundSfxActive` と `wSoundSfxChannelKind` が示すSFX占有チャンネルには、ミュート呼び出しもAPUレジスタ書き込みも行わない。NR52によるAPU全停止とNR51の一括変更は行わない。

#### BGM終了後SFX確認ROM

- ROM: `build/bgm_v2_loop_none_sfx_test.gb`
- 入力曲: `assets/bgm_v2_loop_none_manual_test.json`から生成した `obj/bgm_v2_loop_none_manual_test.asm`
- SFX: `assets/se_cursor.json`から生成したCH4 / NoiseのカーソルSFX
- エミュレータ: SameBoyまたはBGB
- BGM再生中は `BGM PLAYING` を表示し、入力は受け付けない（予約もしない）。
- 自然終了後は `BGM FINISHED`、`A: PLAY SFX`、`READY` を表示する。ここでAボタンを一度押すとSFXを開始する。
- SFX中は `SFX PLAYING`、終了後60フレームは `SFX FINISHED`、`UNMUTE COMPLETE` を表示し、その後 `READY` へ戻る。
- `READY`へ戻った後はAボタンで同じSFXを再度開始できる。
- 正常時は、BGMが自然終了して無音になった後、Aボタンごとに短いNoiseクリック音が1回鳴る。SFX中にBGM由来のCH4音が重ならず、終了時にクリック音が途切れず完了することをmute/unmute経路の聴感基準とする。
- `UNMUTE COMPLETE`および次の`READY`でBGMが鳴り始めないことを、終了済みBGMが再開していない基準とする。
- 異常例は、曲末後もBGMが続く、曲末でAPU全体が停止してAボタンのSFXが鳴らない、SFX中に異常音または完全な無音化が起きる、SFX終了後にBGMが再開する、2回目のAボタンでSFXが鳴らない、表示状態が遷移しない、である。

- 初版では、BGMはhUGEDriverで再生する。
- hUGEDriverは1つの曲状態を持つ前提で扱い、効果音再生のたびに `hUGE_init` で別曲へ切り替える運用は採用しない。
- `hUGE_dosound` は毎フレーム1回だけ呼び出し、BGM更新を担当する。
- 効果音実装方式は、hUGEDriverとAPU直接制御を組み合わせるハイブリッド方式を採用する。
- hUGEDriverの `hUGE_mute_channel` は、ミュートしたチャンネルを効果音などへ転用できる想定のAPIである。
- 効果音再生時は、効果音で使うチャンネルを `hUGE_mute_channel` で一時的にミュートし、そのチャンネルのAPUレジスタを直接書き換えて鳴らす。
- 効果音終了後は、該当チャンネルのミュートを解除し、BGM制御をhUGEDriverへ戻す。
- 効果音更新は `hUGE_dosound` の後に行い、hUGEDriverによるBGM更新後に必要なチャンネルだけを上書きする。
- UI効果音は短いため、BGMの該当チャンネルが一瞬上書きされることは許容する。
- BGM制作では、CH2が一時的にミュートされても違和感が少なくなるように作曲する。CH1は主旋律への影響が大きいため、重要な効果音以外では常用しない。
- 効果音制作で作成したJSONは本番用データの正本として維持する。
- hUGEDriver用ASMは単体確認用テストROMでの確認に使い、本体ROM向けには同じJSONからAPU直接制御用のSFX ASMデータを生成する方針とする。

### BGMのチャンネル役割とミュート耐性

BGMでは、CH1 / Pulse1を主旋律、CH3 / Waveをベースまたは曲の土台として使用し、CH1とCH3だけでも主旋律、調性、拍、フレーズ進行を認識できる構成とする。CH2 / Pulse2は補助旋律・和音補助・対旋律・アルペジオ・装飾・短いリズム補強、CH4 / NoiseはドラムやNoiseによるリズム補強として扱う。効果音再生によってCH2またはCH4が一時的にミュートされても、曲の構造が破綻しないことを優先する。

この方針でいう「骨格」は、主旋律、調性またはコード進行、拍、フレーズ進行、ループ位置を指す。音数や和音の厚みが一時的に減少することは許容するが、主旋律・曲の進行・ループ位置が分からなくなる構成は採用しない。必須の音楽情報をCH2またはCH4だけに配置しない。

#### CH1 / Pulse1

- 曲を識別する重要な主旋律をCH1へ配置する。
- 主旋律は原則としてCH1だけでも追えるようにする。
- CH2との掛け合いを使う場合も、CH2が消えてCH1のフレーズが不自然に途切れないようにする。
- 重要なフレーズをCH2だけへ置かない。
- CH4が消えても拍を感じやすいよう、必要に応じて主旋律自体にリズム感を持たせる。
- CH2のミュート中にCH1へ長い休符だけが残り、主旋律が消失する構成を避ける。

#### CH3 / Wave

- ベース、持続音、ルート音、重要なコード構成音など、曲の土台を担当させる。
- CH2が消えても、CH1とCH3だけで調性やコード進行を認識できるようにする。
- CH4が消えても、CH3の発音タイミングからある程度の拍を感じられるようにする。
- 必要に応じて拍、コード変更、フレーズ境界を示す発音を行う。
- CH3を装飾音だけに使用し、必須のベースや和声情報をCH2だけへ置く構成を避ける。
- CH1と音域や役割が重なりすぎないようにする。

#### CH2 / Pulse2

CH2は一時的な消失を許容する補助チャンネルとする。コード補助、アルペジオ、対旋律、主旋律の部分的な重ね、短いリズム補強、フレーズ終端の装飾に使用する。主旋律、必須のコード進行、必須のベースラインをCH2だけで表現しない。CH2が消えるとCH1のフレーズが成立しない掛け合いや、長い独立フレーズの途中欠落に依存する構成も避ける。

#### CH4 / Noise

CH4はリズム補強チャンネルとする。キック、スネア、ハイハット等に相当するNoiseリズムへ使用するが、拍やテンポの認識をCH4だけに依存させない。CH4が消えてもCH1とCH3の発音タイミングからテンポを維持できるようにする。曲の開始位置、フレーズ境界、ループ境界をCH4だけで示さず、重要なアクセントは必要に応じてCH1またはCH3の発音とも同期させる。CH4は1拍または短い周期で完結する反復中心のリズムとし、復帰後につながりやすくする。

#### 効果音中と復帰時の許容範囲

許容する変化は、音数の減少、和音の厚みの減少、対旋律・装飾の一時的な欠落、ドラムやNoiseリズムの一時的な欠落とする。主旋律の認識不能、調性・コード進行の認識不能、拍・テンポの喪失、フレーズ進行やループ位置の破綻、CH2またはCH4の欠落による誤った和音、復帰時の不自然な接続は許容しない。

効果音中もBGM全体の再生位置は進行を継続する。hUGEDriverのミュートは対象チャンネルを処理対象から外し、`Sound_Update`は毎フレーム `hUGE_dosound` を呼び続けるため、CH2とCH4は効果音終了後に現在のBGM位置から復帰する。消音前に鳴る予定だった音を復帰後に遅れて再生しない。CH2は途中欠落しても成立する短い補助フレーズを中心にし、CH4は短い周期の反復を基本とする。復帰時にCH1・CH3との和音やリズムが大きく衝突しないようにする。

設計基準は「音数や厚みの減少は許容するが、曲の構造の消失は許容しない」とする。

#### BGM制作時の確認方法と合格基準

4チャンネルBGMの制作・調整時は、通常再生、CH2のみミュート、CH4のみミュート、CH2とCH4を同時にミュート、CH2とCH4を途中から復帰する5状態を確認する。可能であればタイトルBGM、プレイ中BGM、クリアBGMを対象とする。

次を合格基準とする。

- CH1だけでも主旋律を認識できる。
- CH1とCH3だけで曲の骨格を認識できる。
- CH2が消えても主旋律とコード進行が破綻しない。
- CH4が消えてもテンポと拍を見失いにくい。
- CH2とCH4が同時に消えても、曲が停止・崩壊したように聞こえない。
- CH2とCH4の復帰時に大きな違和感がない。
- ミュート中に誤った和音や不自然な空白が発生しない。
- フレーズ境界とループ境界が維持される。

完全に同じ響きを維持することは合格条件としない。

#### CH2・CH4同時ミュートのSameBoy確認結果

SameBoy v1.0.3で、`build/bgm_v2_ch1_ch3_skeleton_test_ch2_ch4_mute.gb` を確認した。起動時の `ALL CHANNELS`、Select操作後の `CH1 CH3 SOLO`、A操作後の `CH2 CH4 MUTED` は数字を含めて欠けなく表示され、B操作による全チャンネル復帰も正常だった。CH1とCH3だけの状態でも曲の骨格が維持され、CH2とCH4の同時ミュートおよび全チャンネル復帰が意図どおり動作した。表示・サウンドとも問題はなく、異常音、意図しない無音、再生停止、テンポずれ、ループ位置ずれ、遅延発音は確認されなかった。

本方針はCH2 / Pulse2およびCH4 / Noiseが効果音に使用される場合を対象とする。現行実装ではPulse1効果音がCH1を、Noise効果音がCH4を使用し、Pulse2効果音は未対応である。したがって、CH1を効果音へ割り当てた場合にもCH1 / CH3の骨格を保証する方針ではなく、CH1使用効果音は主旋律への影響が大きい重要な演出に限定する既存方針を維持する。CH2効果音の実装と、CH1を含む各ミュート状態の実機・エミュレータ検証は後続WBSで扱う。

### 運用確認用BGMのMIDI試作条件

既存のVersion 2 JSONをSameBoyで試聴した結果、音数やNoise音量の調整だけでは軽快さ・変化・Noiseの音楽的な役割を改善できなかった。このため、次のWBS「ChatGPTで短いMIDI候補を複数作成し、楽曲設計メモを作成する」では、既存の `assets/bgm_v2_workflow_check.json` のnote列、pattern構成、Instrument値、Wave table、Noise pitchをMIDIへ単純移植しない。曲構成、短い主旋律モチーフ、リズム、コード進行、フレーズ変化から新しく候補を設計する。

#### 目的・方向性・規模

- MIDI段階の目的はGame Boy音源の完全再現ではなく、まず曲として良いかを比較試聴すること。人が短時間で複数候補を聴き比べられることを優先する。
- 運用確認用BGMは本番BGMではなく、サウンドテストROM等で制作フローを確認するための曲とする。明るく軽快で、単調にならず、プレイ中などに繰り返し聴いても邪魔になりにくい方向を目指す。
- 音符数だけで軽快さを作らず、短い主旋律モチーフ、休符を含むリズム、コード進行、反復時のフレーズ変化、アクセント位置から設計する。音数過密、変化不足、補助やNoiseだけに依存する骨格、試聴を妨げる過度な暗さ・攻撃性は避ける。
- 候補数は4候補を基準（増減可）。1候補は約15～30秒、8～16小節、4/4拍子を基準とする。これは比較試聴用の目安であり、最終版の長さやJSONのorder数を固定しない。
- イントロは原則含めない。必要な候補だけ最初の1～2小節の導入を含める。完全な最終ループは作らず、末尾から先頭へ戻れる可能性を確認できる短い主部と接続までとし、採用案の最終長さ・ループ構成は後続WBSで決定する。

#### MIDIパートとミュート耐性

後でGame Boy 4chへの割り当てを判断できるよう、MIDIでは次の4パートを分離する。MIDI音色でPulse、Wave、Noiseを再現する必要はない。

- `melody`（将来のCH1 / Pulse1）: 曲を識別する主旋律。単独でも主題と拍を認識できる。
- `bass`（将来のCH3 / Wave）: ベース、ルート音、または曲の骨格。melodyと合わせて調性、コード進行、フレーズ進行を認識できる。
- `support`（将来のCH2 / Pulse2）: 消失しても成立する補助旋律、和音補助、対旋律、アルペジオ、装飾。必須の主旋律・ベース・コード進行を担当しない。
- `rhythm`（将来のCH4 / Noise）: 消失しても成立するリズム補強。拍、tempo、曲の開始・境界をこのパートだけに依存させない。

候補は `melody`単独、`melody + bass`、`support`ミュート、`rhythm`ミュート、`support + rhythm`ミュート、途中からの復帰を試聴する。主旋律、主旋律とベースの骨格、コード進行、拍、フレーズ境界が保たれ、曲が停止・崩壊したように聞こえないことを条件とする。復帰時に不自然な和音にならないよう、短い区切りやコード構成音を用いる。

#### MIDIで決めるもの・決めないもの

MIDI試作で決めるのは melody、rhythm、harmony / chord progression、bass line、phrase structure、note duration、rest、おおよそのtempo、おおよそのvelocity、各パートの役割である。調性とコード進行は候補ごとに明記するが、全候補で固定するかは未確定とし、比較しやすさを優先して後続WBSで決定する。

原則として決めないのは Game Boy Pulse duty、hUGEDriver Instrument番号、Wave tableの32 sample値、NoiseのC3～B8 pitch index、Noise `width_mode`、hardware envelope、Version 2 JSONのpattern名、64rowへの具体的展開、order番号、JSON固有のeffect値である。これらは採用MIDIの4ch変換方針とVersion 2 JSON作成時に決定する。

#### 4ch化を妨げないMIDI制約

- 4パートを基本とし、各パートは原則単音、全体の同時発音は原則4音以下とする。和音はsupportで分散・アルペジオ化し、必須の和声を同時発音だけに依存させない。
- 極端に広い音域、細かすぎる連打、過度に短い装飾音、複雑なポリリズムを避ける。ただし音楽品質を損なわない範囲の短い音符と休符は使用する。各パートのおおよその音域は設計メモに記す。
- pitch bend、aftertouch、複雑なCC、sustain pedalは使用しない。velocityは弱・標準・強の3段階程度に抑える。tempoは候補全体でおおよそ一定とし、tempo changeは使用しない。
- これらは4ch化を不必要に難しくしない目安であり、MIDIの曲としての比較をGame Boy制約へ過度に従属させない。例外は理由を設計メモに残し、後続WBSで判断する。

#### ChatGPTへ渡す「運用確認用BGM MIDI試作条件」

```text
用途: 運用確認用BGM。本番採用曲ではなく、サウンドテストROM等で候補を比較する。
目指す雰囲気: 明るく軽快、変化があり、繰り返し聴いても邪魔になりにくい。
避ける特徴: 音符数だけに頼る軽快さ、単調さ、音数過密、補助やNoiseだけに依存する骨格。
候補数: 4候補を基準（増減可）。1候補: 約15～30秒、8～16小節、4/4。イントロ原則なし、完全ループは未作成。
tempo: 候補全体でおおよそ一定。具体値は候補で提案し最終値は未確定。
調性・コード進行: 候補ごとに提案。全候補で固定するかは未確定。
パート: melody / bass / support / rhythm。各パートの役割、音域、単音性を記す。
制約: 原則各パート単音、全体同時発音4音以下、極端な音域・細かすぎる音符を避ける。
velocity: 弱・標準・強の3段階程度。pitch bend、aftertouch、複雑なCC、sustain pedal、tempo changeは使用しない。
ミュート確認: melody単独、melody+bass、supportミュート、rhythmミュート、support+rhythmミュート、途中復帰。
MIDIで決めないもの: duty、Instrument番号、Wave table、Noise pitch/width、envelope、JSON pattern/order/effect、64row展開。
各候補の楽曲設計メモ: モチーフ、コード進行、拍・リズム、フレーズ構成、パート役割、音域、tempo/velocity、ミュート時の成立理由、ループ可能性、例外。
比較試聴項目: 軽快さ、単調さ、繰り返しの邪魔になりにくさ、主旋律の認識、melody+bassの骨格、ミュート耐性、復帰時の和音、採用理由。
未確定事項: 具体的tempo・調性・コード進行、採用候補、最終長さ・ループ構成、4chへの具体的割り当て。
```

未確定事項は推測で埋めず、理由と「採用したMIDI案を必要な長さ・ループ構成へ仕上げる」または「採用MIDIと楽曲設計メモからGame Boy 4chへの変換方針を決める」で決定する。このWBSではMIDIファイルを作成せず、候補の採用、最終ループ、具体的な4ch変換方針も決定しない。

#### MIDI候補間の差の作り方

同じ比較セット内では、候補間のMIDI音色を原則として統一する。候補ごとにマリンバ、フルート、Brassなどの音色を変えて個性を作る方法は採用しない。比較用の標準音色は、`melody`を単純なSquare系Lead、`support`をmelodyと同じまたは同系統のSquare系、`bass`を単純なSynth Bass系、`rhythm`を簡素なDrum Kitとする。これはGame Boy音源の完全再現や特定のGM Program番号の固定を目的とせず、必要なら音色カテゴリだけを制作条件に記載する。

候補の主要な差は、Game Boyへ変換しても残る次の音楽構造から作る。

- melody、chord progression / harmony、bass line
- note duration、rest、rhythm、phrase structure
- accent、note density、発音タイミング
- tempo、調性、modal color

目的は「MIDI音色をGame Boy音源へ置換しても残る音楽的差だけを比較する」ことである。MIDI候補は一般的なMIDI曲を後からGame Boy向けに縮小するための完成品ではなく、Game Boy 4chで成立する曲をMIDIで先に比較試聴するための中間表現とする。

従来の役割分離、すなわち `melody` → 将来のCH1 / Pulse1、`bass` → CH3 / Wave、`support` → CH2 / Pulse2、`rhythm` → CH4 / Noise、を維持する。候補設計では、melody単独でも候補固有の主題と前進感を認識でき、melody + bassだけでも候補固有の調性・コード・フレーズ進行が残ることを目標とする。supportまたはrhythmを削除しても候補同士が同じ曲のように聞こえる状態へ戻らないよう、候補差を補助パートや音色だけに置かない。

#### 候補比較の試聴記録

最初の候補群は構造差が小さく、人による試聴で「全部同じ曲に聞こえる」と評価された。次の候補群はMIDI音色を大きく変えたため違いは明確になったが、マリンバ、フルート、Brassなどの差はGame Boy移行後に失われる懸念が生じた。そのため最終候補群では全候補のMIDI音色を統一し、melody、和声、bass line、note duration、rest、rhythm、phrase structure、発音密度、accent、発音タイミングなど、Game Boy移行後にも残る音楽構造だけで差を作った。この方式では候補差を十分に感じられ、人による試聴では候補D「Pulse Chase」が最も良いと判断された。

#### 採用候補D「Pulse Chase」の試作設計

以下は人による比較試聴で最も良いと判断された、運用確認用BGMの8小節試作Dを再生成するための設計情報である。最終完成曲の長さ、イントロ、ループ構成、最終tempoを固定する仕様ではなく、後続WBSで採用案を仕上げる前の候補設計である。

- 仮タイトルは `Pulse Chase`、用途は運用確認用BGMとする。
- 拍子は4/4、試作長は8小節、tempoは136 BPM、調性感はE minor系とする。
- 基本和声はEm、D、C、Bm系を中心にする。8分音符主体とし、4候補の中では前進感を強くする。
- 「速いから軽快」とはせず、note placement、発音密度、rest、accent、発音タイミングによって推進力を作る。

`melody`は将来のCH1 / Pulse1を想定し、E minor系の短い8分音符モチーフを使う。上下運動を繰り返し、1小節を8分音符で埋め尽くさず適度なrestを残す。2～4音程度の短いセルを変形しながら展開し、同じモチーフを完全コピーで延々と繰り返さない。E5 / G5 / B5などE minorを認識しやすい構成音を基準に、D、C、Bm系の小節では対応する構成音へ展開する。おおよその音域はE5～D6付近とし、melody単独で主題と前進感を認識できるようにする。主旋律をsupportへ預けない。

`bass`は将来のCH3 / Waveを想定し、Em / D / C / B系のrootを中心にする。1小節1音の長音だけにせず、1小節内で2～3回程度発音して前進感を補強する。おおよその音域はB2～E2周辺を中心とする低音域とし、rhythmをミュートしても拍・tempo感を完全に失わないようにする。melody + bassだけで調性、コード進行、フレーズ進行を認識できることを条件とする。

`support`は将来のCH2 / Pulse2を想定し、短い単音だけをmelodyの隙間や弱拍へ置く。和声音・コード構成音を中心にし、melodyをコピーしない。supportを完全にミュートしても曲として成立し、必須のコード進行をsupportだけに依存させない。

`rhythm`は将来のCH4 / Noiseを想定する。MIDIでは全候補で統一した簡素なDrum Kitを使い、GM DrumそのものをGame Boyで再現することは前提にしない。8分系の細かいaccentを含む単純なリズムで前進感を補強し、kick / snare / hi-hat相当の役割を単純化して使う。rhythmをミュートしてもmelody + bassで拍を認識できるようにし、Noise音そのものを目立たせず楽曲のaccentとして機能させる。既存のVersion 2 JSONで発生した「Noiseが文字どおりノイズとして聞こえる」問題を繰り返さない。

#### Pulse ChaseをCodexで再生成する条件

次の条件を使えば、MIDIイベントを1ノート単位で固定せず、同じ設計思想と主要構造を持つ試作DをCodexで再生成できる。

```text
仮タイトル: Pulse Chase
用途: 運用確認用BGM
拍子: 4/4
試作長: 8小節
tempo: 136 BPM（試作Dの再生成条件。最終完成曲の固定値ではない）
調性感: E minor系
和声: Em - D - C - Bm系を中心にする

パート: melody / bass / support / rhythm

共通:
- 各パートは原則単音、全体同時発音は原則4音以下
- MIDI音色は比較セット内で統一する
- melodyは単純なSquare系Lead、supportは同系統のSquare系、bassは単純なSynth Bass系、rhythmは簡素なDrum Kit
- pitch bend / aftertouch / 複雑なCC / sustain pedal / tempo changeは使用しない

melody:
- 8分音符主体、E5～D6付近
- E minor系の2～4音セルを上下運動させ、変形して展開する
- 適度にrestを入れ、1小節を埋め尽くさない
- E5 / G5 / B5を基準に、D / C / Bm系では対応する構成音へ展開する
- 単独で主題と前進感が分かり、supportに主旋律を依存しない

bass:
- Em / D / C / B系root中心、B2～E2周辺
- 1小節内で2～3回程度発音し、長音だけにしない
- rhythmがなくても拍・tempo感を補強し、melody+bassで曲の骨格を維持する

support:
- 短い単音のコード構成音をmelodyの隙間・弱拍へ置く
- melodyをコピーせず、完全ミュート可能にする

rhythm:
- 簡素なDrum Kitで8分系accentを含むリズム補強
- kick / snare / hi-hat相当の役割を単純化する
- Noise化を想定し、音色そのものへ依存せず、消失しても拍を失わない

避ける:
- MIDI音色による個性付け
- supportだけに依存する和声、rhythmだけに依存するtempo感
- 過度なポリフォニー、音数だけで作る軽快さ
- 既存失敗曲のnote列・pattern・Instrument・Wave table・Noise pitchの流用
```

### Version 2 BGM制作の作曲条件

ChatGPTまたはCodexがVersion 2楽曲定義JSONの初稿を直接作成する前に、曲ごとの作曲条件を本節のテンプレートで整理する。作曲条件は自然言語による制作指示であり、JSONへ `purpose`、`mood`、`duration` などの新しい項目を追加するものではない。JSONの構造と値の正本は[楽曲定義JSON仕様](json-format.md)とし、本節では作曲時に先に決める内容と既存仕様への適合条件だけを扱う。

タイトルBGM、プレイ中BGM、クリアBGMそれぞれの具体的な用途、雰囲気、長さ、tempo、ループ方式、イントロの有無は、各曲の後続WBSで決定する。本節では値を先回りして決めない。条件が決まっていない項目は推測で補完せず、`未確定`、未確定の理由、決定するWBSを記載する。後述の旧2チャンネル試作と既存の `assets/bgm_title.json`、`assets/bgm_game.json`、`assets/bgm_clear.json` にある具体値も、新しい4チャンネル曲の作曲条件として自動的に流用しない。

#### 作曲前に固定しておくJSON制約

- 出力対象は `version = 2`、`type = "bgm"` の楽曲定義JSONとする。曲名はトップレベルの `title` に記載する。
- `tempo` は必須の正整数で、曲全体と4チャンネルに共通する単一値とする。order、pattern、row、noteごとのtempoや曲中tempo変更は指定しない。値が大きいほど、固定更新頻度では1rowの再生が遅くなる。
- `order` と `patterns` は `pulse1`、`pulse2`、`wave`、`noise` のチャンネル別オブジェクトとする。Version 1の共通orderや `patterns.<pattern名>.channels` と混在させない。
- 使用する全チャンネルのorder数を一致させる。各order位置は全チャンネル共通の64row区間として扱う。新しい4チャンネルBGMではCH1～CH4それぞれのorderとpatternの計画を作曲条件へ記載する。
- 各patternはnoteの `length` を展開した結果で最大64rowとする。64row未満は変換ツールが空行で補完し、64rowを超えるフレーズは複数patternへ分割する。
- `loop` は必須とし、曲ごとに次のいずれかを選ぶ。
  - `{"mode": "full"}`: 全order範囲を繰り返す。`start_order` と `end_order` は指定しない。
  - `{"mode": "range", "start_order": S, "end_order": N}`: order 0から再生し、`S` より前を1回だけのイントロ、半開区間 `[S, N)` をループとする。`N` は全使用チャンネル共通のorder数と同じ値にし、`0 <= S < N` とする。境界はorder単位とし、pattern途中やrow単位のループは使用しない。
  - `{"mode": "none"}`: 全orderを1回だけ再生し、最終orderの最終row処理後に自然終了する。`start_order` と `end_order` は指定しない。
- 1回だけ再生するイントロが必要な場合は `loop.mode = "range"` を使用し、イントロのorder数とループ開始orderを明記する。`full` では先頭部分も毎回ループし、`none` では曲全体が1回再生になるため、非ループ区間としてのイントロを別指定しない。
- noteの `note` は `C3`～`B8`または`rest`、`length`は1以上のrow数、`instrument`は1～15とする。`effect` と `effect_param` は現行変換で非nullに対応していないため、効果を使わず省略するか `null` とする。
- Instrumentは使用チャンネル、役割、音色意図とJSON値を対応させる。同じbank内でInstrument IDを重複させない。CH1 / CH2は同じDuty bank、CH3はWave bank、CH4はNoise bankを使用する。
  - Pulse Instrumentは `duty`、hardware側の `length` / `length_enable`、`initial_volume`、`envelope_direction`、`envelope_sweep` を選ぶ。`sweep_time`、`sweep_direction`、`sweep_shift` はCH1だけで使用でき、CH2では指定しない。
  - Wave Instrumentは参照する `waveform` を必ず決め、`output_level`、hardware側の `length` / `length_enable` を選ぶ。参照先は `wave_tables` に名前付きで定義し、各Wave tableは0～15の値を32サンプル、最大16個までとする。
  - Noise Instrumentはhardware側の `length` / `length_enable`、`initial_volume`、`envelope_direction`、`envelope_sweep`、`width_mode`を選ぶ。`clock_shift`、`divisor_code`、完成済みNR43値は指定しない。
- CH4のnoteも `C3`～`B8`の音名で記載するが、旋律上の正確な音程ではなくNoise pitch indexとして扱う。`kick`、`snare`、`hat`などをnote値にせず、作曲条件側で「どのNoise Instrumentと音名の組み合わせをどのリズム役に使うか」を記載する。固定の打楽器対応を推測しない。
- note単位の `volume` は必要な発音だけ0～15で指定できる。省略はvolume commandなし、`volume: 0`は明示的な音量0であり、同じ意味ではない。`length`展開後の空行へvolumeやInstrumentを再適用しない。CH4の `note: "rest"` では、`null`を含めて `volume` キー自体を指定しない。
- note側の `length` はpatternのrow数、Instrument側の `length` はGame Boyハードウェアのsound lengthであり、別の項目として決める。

項目の全許容値、デフォルト値、未使用チャンネルの省略規則、Wave tableの命名規則、変換時の詳細は[楽曲定義JSON仕様](json-format.md)を参照する。具体的なVersion 2の4チャンネル構造は[4チャンネルBGM JSONサンプル](json_examples/bgm_4ch_sample.json)、CH1 / CH3の骨格とミュート耐性を確認した既存資産は `assets/bgm_v2_ch1_ch3_skeleton_test.json` を参照する。これらは構造例・確認用データであり、新曲のフレーズや具体値を流用する指定ではない。

#### チャンネル別に記載する作曲条件

- CH1 / Pulse1:
  - 曲を識別する重要な主旋律を担当させ、主旋律を原則としてCH1だけでも追えるようにする。
  - 曲固有の重要フレーズ、主な音域、リズムの持たせ方、使用するPulse Instrumentを記載する。
  - CH2との掛け合いを使う場合も、CH2の消失でCH1のフレーズが不自然に途切れない構成を記載する。
- CH3 / Wave:
  - ベース、持続音、ルート音、重要なコード構成音など曲の土台を担当させ、CH1とCH3だけで曲の骨格を認識できるようにする。
  - 調性またはコード進行、拍やフレーズ境界を支える発音、主な音域、使用するWave InstrumentとWave tableを記載する。
  - 必須のベースや和声情報をCH2だけへ置かず、CH1と音域・役割が重なりすぎない構成を記載する。
- CH2 / Pulse2:
  - 補助旋律、和音補助、対旋律、アルペジオ、装飾、短いリズム補強のうち、曲に必要な役割を記載する。
  - 一時的に消えても曲が成立する短い補助フレーズを中心とし、主旋律、必須のコード進行、必須のベースラインをCH2だけへ配置しない。
  - ミュート途中で欠落しても不自然になりにくく、現在の再生位置から復帰してもCH1 / CH3と和音が衝突しにくい構成を記載する。
- CH4 / Noise:
  - リズム補強を担当させ、使用するNoise Instrument、Noise note、発音周期、アクセント位置を記載する。
  - CH4だけに拍、tempo、曲の開始、フレーズ境界、ループ境界の認識を依存させない。
  - 1拍または短い周期で完結する反復を中心とし、途中復帰してもリズム衝突が起きにくい構成を記載する。

#### 作曲条件テンプレート

次のテンプレートを埋めた内容を、そのままVersion 2楽曲定義JSON初稿作成の入力にする。`未確定`が残る場合はJSONを推測で作成せず、後続WBSで決定する。

```text
Version 2 BGM作曲条件

基本情報:
  title: <JSONのtitle>
  用途: <再生する画面・状態、開始契機、終了または切替契機>
  目指す雰囲気: <形容、避けたい印象、必要なら参考となる音楽的特徴>
  想定する長さ:
    聴感上の目安: <秒、短いジングル、継続再生向け等。未確定可>
    構造上の目安: <共通order数、1order = 64row>
  tempo: <曲全体で共通の正整数。未確定可>
  loop:
    mode: <full | range | none。未確定可>
    start_order: <rangeの場合のみ。0始まり>
    end_order: <rangeの場合のみ。全使用チャンネル共通order数Nと同じ値>
  イントロ: <なし | rangeの先頭S orderを1回だけ再生。未確定可>

曲の構造:
  調性・コード進行: <CH1 + CH3で認識できる内容>
  拍子・リズム: <CH4がなくてもCH1 + CH3から拍を追える内容>
  フレーズ構成: <orderごとの役割とpattern分割。各patternは展開後最大64row>
  ループ接続または終止: <境界前後の和声・旋律・リズム。noneでは自然終了位置>

チャンネル:
  CH1 / Pulse1:
    固定役割: 主旋律と曲を識別する重要フレーズ
    曲固有の内容: <フレーズ、音域、リズム、Instrument>
  CH2 / Pulse2:
    固定役割: 消失可能な補助旋律・和音補助・対旋律・アルペジオ・装飾
    曲固有の内容: <短い補助フレーズ、Instrument、復帰時の接続>
  CH3 / Wave:
    固定役割: ベース・持続音・ルート音等の曲の土台
    曲固有の内容: <ベース/和声、発音タイミング、Instrument、Wave table>
  CH4 / Noise:
    固定役割: 消失可能なリズム補強
    曲固有の内容: <Noise Instrument + noteの組み合わせ、周期、アクセント>

音色・音量:
  Instruments: <ID、channel、用途、使用するVersion 2 Instrument項目>
  Wave tables: <name、32サンプルの方針。CH3使用時>
  note volume: <必要な発音と0～15の値。不要なら省略>
  音域・音量バランス: <CH1とCH3の分離、CH2/CH4消失時も残る情報>

order / patterns:
  共通order数: <N>
  pulse1 order: <pattern名をN個>
  pulse2 order: <pattern名をN個>
  wave order: <pattern名をN個>
  noise order: <pattern名をN個>
  pattern計画: <各チャンネル・各patternの役割と展開後row数>

ミュート耐性:
  CH2のみミュート: <主旋律・調性・コード進行が維持される理由>
  CH4のみミュート: <tempo・拍・フレーズ境界を見失いにくい理由>
  CH2 + CH4同時ミュート: <CH1 + CH3で骨格を認識できる理由>
  復帰時: <CH2の和音、CH4の周期が現在位置から復帰しても衝突しにくい理由>

その他の制約:
  JSON固定値: version = 2、type = "bgm"
  effect: <使用しない。省略またはnull>
  未確定事項: <項目、理由、決定する後続WBS>
  避ける構成: <曲固有に避けるフレーズ、音域、音色、反復等>
```

#### 運用確認用BGMの確定済み作曲条件

運用確認用BGMは、本番のタイトル画面・通常プレイ・クリア画面で使用する曲ではなく、AIによるVersion 2 BGM直接制作フローを確認するための独立した検証曲とする。JSONからASM・確認用ROMを生成し、SameBoyで通常再生、ミュート、復帰、境界の聴感を確認する用途に限定する。本番BGMの採用版や既存の旧2チャンネルBGMを置き換えるものではない。

今回決定する作曲条件は次のとおりとする。

```text
基本情報:
  title: Version 2 BGM Workflow Check
  用途: AIが自然言語の作曲条件からVersion 2楽曲定義JSONを直接作成し、JSON→ASM→確認用ROM→SameBoy試聴→自然言語フィードバック→再生成の制作フローを確認するための運用確認用BGM。ゲーム本編の画面・状態では再生せず、サウンドテストROMまたは同等の確認環境で再生する。
  目指す雰囲気: 明るく軽快で、音の重なりと構造を聞き取りやすい、短時間の検証に集中できるゲームボーイ向けの雰囲気。避けたい印象は、音数が過密で各チャンネルの有無を聞き分けにくいこと、過度に暗い・攻撃的で試聴時の差分確認を妨げること、変化が乏しく境界や復帰を把握しにくいこととする。
  想定する長さ:
    聴感上の目安: 20～40秒程度。1回の短い試聴で曲の構造を把握でき、ミュート・復帰・境界の確認を複数回行える長さとする。
    構造上の目安: 共通6 order（1 order = 64row）。tempo 6、固定更新60Hzを基準にした構造上の長さは約38.4秒で、イントロ後のループ区間は約25.6秒とする。
  tempo: 6
  loop:
    mode: range
    start_order: 2
    end_order: 6
  イントロ: 先頭2 order（order 0～1）を1回だけ再生する。
```

`range` は仕様どおり order 0から再生し、先頭2 orderだけを1回再生した後、半開区間 `[2, 6)` を繰り返す。共通order数6と `end_order: 6` が一致するため、後続orderへ到達しない余剰データもなく、ループ境界をSameBoyで明確に確認できる。約38.4秒の初回再生と約25.6秒の反復区間により、短時間で曲の構造を把握しながらミュート・復帰・境界の確認を複数回行える。

今回決定する曲の構造とpattern計画は次のとおりとする。コード名は作曲上の区分であり、具体的なnote列は後続WBSで展開する。音域、Instrument、note length / volumeは本節の確定条件に従う。

```text
曲の構造:
  調性・コード進行: C major、4/4拍子。各orderは大きな2区間で和声を示す。
    order 0（イントロ導入）: C (I) → G/B (V6)。C majorを提示し、次orderへ進む。
    order 1（イントロ展開）: Am (vi) → G (V)。Gで区切り、order 2のC (I)への開始を明確にする。
    order 2（ループ主題A）: C (I) → F (IV)。主題の開始と明るい展開を示す。
    order 3（ループ主題B）: G (V) → Am (vi)。主題Aに対する応答とする。
    order 4（ループ変化）: F (IV) → G (V)。終止へ向けて緊張を高める。
    order 5（ループ接続）: C (I) → G (V)。Gを末尾の接続和音として置き、order 2のCへ戻す。
  拍子・リズム: 4/4。CH1の主題リズムとCH3の発音位置で拍と2区間の境界を示す。CH4は短い反復の補強とし、拍や境界の唯一の手掛かりにはしない。
  フレーズ構成:
    order 0: イントロ導入。C majorと基本モチーフを提示する。
    order 1: イントロ展開。AmからGへ進む終止前区間とする。
    order 2: ループ主題A。CからFへ進むループ冒頭の主題提示とする。
    order 3: ループ主題B。GからAmへ進む旋律・和声上の応答とする。
    order 4: ループ変化。FからGへ進み、接続へ向けて展開する。
    order 5: ループ接続。Cを確認した後Gで止め、order 2のCへ戻す接続句とする。
  ループ接続または終止: order 1 → 2はG (V)からC (I)へ解決し、イントロ終了とループ開始を認識できるようにする。order 5 → 2もG (V)からC (I)へ解決する。CH1とCH3にも境界のアクセントまたは発音位置を持たせ、CH4だけに依存しない。

order / patterns:
  共通order数: 6（各orderは4チャンネル共通の64 row区間）
  pulse1 order: [intro_cadence, intro_turn, loop_theme_a, loop_theme_b, loop_build, loop_link]
  pulse2 order: [intro_harmony_a, intro_harmony_b, loop_support_a, loop_support_b, loop_support_c, loop_link_support]
  wave order: [intro_root_a, intro_root_b, loop_foundation_a, loop_foundation_b, loop_foundation_c, loop_link_foundation]
  noise order: [intro_rhythm_a, intro_rhythm_b, loop_rhythm_a, loop_rhythm_b, loop_rhythm_c, loop_link_rhythm]
  pattern計画:
    pulse1: イントロ調性提示・終端、ループ主題A/B、展開、接続を担当する。主旋律はCH1単独で追える構成とする。
    pulse2: 補助和声と短い接続補助を担当する。CH1の主旋律や必須のコード進行には依存しない。
    wave: イントロの土台、ループ内のルートまたは重要な和声変化、GからCへの接続を担当する。CH1 + CH3で骨格を保持する。
    noise: イントロ・ループ各区間の短い反復と接続アクセントを担当する。CH4が消えてもCH1・CH3から境界を認識できるようにする。
    各patternは展開後最大64 rowとし、下記のnote length方針で64 row以内に構成する。異なるorder間でpatternを再利用する計画は採用しない。各orderの境界を独立して調整する。

ミュート耐性:
  CH1 + CH3で曲の骨格を保持可能か: 可能と判断する。CH1が主題とorder境界のリズムを担い、CH3がC major内のルート・和声変化と発音位置を担うため、CH2とCH4がなくても主題、調性、コード進行、拍、フレーズ進行、ループ位置を追える。
  必須のコード進行をCH2だけに依存していないか: 依存しない。C、F、G、Amの進行とG (V)からC (I)への解決はCH1 + CH3で成立させる。
  拍・フレーズ境界をCH4だけに依存していないか: 依存しない。CH1の主題リズムとCH3の発音位置、orderごとの和声変化で示す。
  order 5 → order 2のループ位置: CH1の接続句の再提示とCH3のG (V) → C (I)の解決を同期させるため、CH1 + CH3でも認識できる。
```

上記に加え、JSON初稿へ機械的・作曲的に展開できる音色、発音長、音量条件を次のとおり確定する。具体的なnote列の全展開は後続WBSで行う。

音色・音量:
  Instruments:
    - CH1 / Pulse1: ID 1 `workflow_lead`。channelは`pulse1`、dutyは2、hardware lengthは0、length_enableはfalse、initial_volumeは12、envelope_directionは`down`、envelope_sweepは0。Sweepは使用せず、`sweep_time: 0`、`sweep_direction: down`、`sweep_shift: 0`を明示する。主旋律の輪郭を保つため、Pulse bankで最も明瞭な基準音色とする。
    - CH2 / Pulse2: ID 2 `workflow_support`。channelは`pulse2`、dutyは1、hardware lengthは0、length_enableはfalse、initial_volumeは7、envelope_directionは`down`、envelope_sweepは0。CH1専用のSweep項目は指定しない。CH1より一段控えめで、短い和音補助・対旋律として聞き分けられる音量にする。
    - CH3 / Wave: ID 1 `workflow_foundation`。channelは`wave`、waveformは`workflow_triangle`、output_levelは`100%`、hardware lengthは0、length_enableはfalse。低域のルートと和声を明瞭にする基準音色とする。
    - CH4 / Noise: ID 1 `workflow_low_accent`、ID 2 `workflow_mid_accent`、ID 3 `workflow_high_accent`。すべてchannelは`noise`、hardware lengthは0、length_enableはfalse、envelope_directionは`down`、envelope_sweepは0。ID 1はinitial_volume 8、width_mode `15bit`、ID 2はinitial_volume 6、width_mode `7bit`、ID 3はinitial_volume 4、width_mode `7bit`とする。Noiseの音量は補助に限定し、NR43の`clock_shift`、`divisor_code`、完成済みNR43値は指定しない。
  Wave tables:
    - name: `workflow_triangle`。samplesは`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]`の32個とする。既存の`bass_triangle`と同じ単純な上昇・下降波形を新曲固有名で定義し、CH3の低域を角の立ちすぎない明るいベースとして聞き取りやすくする。既存資産の波形形状とWave tableテストの32値・0～15制約に適合する。
  Noise Instrument + note対応:
    - ID 1 `workflow_low_accent` + `C3`: 1拍目およびコード変更の低域的な拍頭アクセント。
    - ID 2 `workflow_mid_accent` + `C5`: 4拍目または各4/4区間の区切りアクセント。
    - ID 3 `workflow_high_accent` + `C7`: 2拍目・4拍目の裏または短い補助アクセント。細かい反復では連続使用せず、CH1/CH3の発音間へ置く。
    これらのnoteはすべてNoise pitch indexとして扱い、`kick`、`snare`、`hat`等はJSON note値に使用しない。上記対応はこの曲固有の作曲条件であり、一般仕様の固定対応表ではない。必要に応じて`D3`～`B8`の範囲内で同じ役割の隣接Noise noteへ置換してよいが、初稿では上記3組を基準とする。
  note length:
    - CH1は主に4 row、フレーズ終端または強調する持続音だけ8 row、短い経過・装飾は2 rowとする。
    - CH2は主に4 row、和音の区切りを示す補助音は8 rowまでとし、常時連続させない。
    - CH3は主に8 row（4/4の半区間）でルートまたは和声音を置き、区間終端や持続する土台は16 rowまでとする。
    - CH4は主に2 rowの発音と2 row以上のrestを組み合わせ、拍頭だけ4 rowまでとする。1拍または短周期で完結する反復に限定する。
    - 各patternの合計は展開後64 row以内にする。末尾の不足行は変換ツールの空行補完に任せ、空行へInstrumentやvolumeを再適用しない。
  note volume:
    - 基本は省略し、Instrumentの音量を使用する。CH1のorder開始音・フレーズ終端の発音だけ`volume: 12`、CH2の区切り音だけ`volume: 7`、CH3のorder開始・コード変更音だけ`volume: 10`を指定する。
    - CH4はID 1の拍頭を`volume: 8`、ID 2を`volume: 6`、ID 3を`volume: 4`とし、通常はnote volumeを省略する。追加の音量変化が必要な場合も上限は8とする。
    - `volume: 0`は今回使用しない。省略はvolume commandなし、Instrumentの`initial_volume`とは別物であり、CH4のrestにはvolumeキーを付けない。length展開後の空行へvolumeを再適用しない。
  音域・音量バランス: CH1のinitial_volume 12を最大の旋律基準、CH3のWave output_level 100%を低域の基準、CH2の7を厚み付け、CH4の8/6/4を短い補助として配置する。CH1は`C5`～`G6`、CH2は`C4`～`E5`、CH3は`C3`～`C4`を基本範囲とし、音域と音量の両方で分離する。
  ミュート耐性: CH2を外してもCH1の主旋律とCH3の低域ルート／和声が残るため、厚みだけが減る。CH4を外してもCH1の4 row主体の主題リズムとCH3の8 row主体の拍頭・和声区間からtempo、拍、境界を追える。CH2 + CH4を同時に外してもCH1 + CH3で主旋律、C major、コード進行、フレーズ進行、ループ解決を保持する。CH2は短い和声音、CH4は独立した2 row反復なので、途中復帰しても保留音や長いフィルの続きに依存せず、他チャンネルを覆わない。

#### 今回決定するチャンネル設計条件

運用確認用BGMのJSON初稿では、次の音域を使用する。ここでいう音域は作曲上の使用範囲であり、各音の具体的なnote列を指定するものではない。Version 2の共通note表記である`C3`～`B8`の範囲内で、短時間の試聴時にもチャンネルを聞き分けやすい位置を選ぶ。

- CH1 / Pulse1: `C5`～`G6`を主な使用音域とする。主旋律を最も聞き取りやすい高めの中音域へ置き、主題・応答・接続句をこの範囲を中心に構成する。必要な旋律上の跳躍で一時的に範囲端を使うことは許容するが、CH3の土台と常時重なる低音域へ主旋律を移さない。
- CH2 / Pulse2: `C4`～`E5`を主な使用音域とする。CH1よりおおむね1オクターブ低い補助位置を基本とし、CH1の主音域と長時間ユニゾンにしない。和音補助でCH1と同じ音名を使う場合も、短い重ねまたは隣接音に限定し、主旋律の輪郭を埋めない。
- CH3 / Wave: `C3`～`C4`を主な使用音域とする。各コードのルートを中心に、必要な5度・経過音もこの低域内で扱う。CH1/CH2の旋律帯と分離したベース／持続音として、C majorと`C`、`F`、`G`、`Am`の進行を支える。
- CH4 / Noise: 音高音域は定義しない。低域的に聞こえるNoiseは拍頭・大きな区切りの基礎アクセント、中域的なNoiseは4拍目や和声区間の区切り、高域的に聞こえるNoiseは細かい拍・裏拍の補助アクセントに割り当てる。

この配置により、CH1は主旋律、CH3は低域の調性・和声・拍の土台として分離し、CH2はその間を補う。CH1とCH2が過度に重なり続けず、CH2をミュートしてもCH1とCH3が残るため、各チャンネルの有無を運用確認で判別しやすい。音域と確定したInstrumentの音量、duty、waveform、envelopeを組み合わせ、4チャンネルを同時に鳴らしても聞き分けられるようにする。

発音方針は次のとおりとする。

- CH1は、主旋律の輪郭がCH1単独で追えるよう、主題の重要音とフレーズの始端・終端を原則としてCH1自身に置く。長い休符だけで重要フレーズをCH2へ受け渡さず、拍を感じられる短音と適度な休符を組み合わせる。order境界とループ境界では、主旋律の再提示または明確な接続をCH1で示す。
- CH2は、短い和音補助、対旋律、アルペジオ、装飾を区切って発音する。常時鳴らし続けず、主旋律の合間やコードが変わる箇所に隙間を設ける。必須のルート、コード進行、主旋律の続き、order境界の唯一の標識はCH2に置かない。
- CH3は、コード変更と拍頭を認識できるルート音または持続音を基本とし、各order内の二つの和声区間とフレーズ境界を発音位置で支える。低域の発音を完全に途切れさせてCH4だけへ拍を委ねず、必要な箇所では短い区切りも使う。CH3単独を旋律化しすぎず、CH1との役割分担を保つ。
- CH4は、1拍または短い周期で完結する単純な反復を中心とし、拍頭・裏拍・区切りの補助に限定する。各反復は途中から聞こえても意味が成立するようにし、曲開始、order境界、ループ境界をCH4だけのフィルや長いパターンに依存させない。具体的なnote列の全展開は後続WBSで行う。

ミュートと復帰に関するJSON初稿の制約は次のとおりとする。

- CH2のみミュートしても、CH1は主旋律を連続して追え、CH3はルートまたは必要なコード構成音と二つの和声区間を示す。C major、主要コード進行、フレーズ進行、order 5からorder 2へのループ位置をCH2に依存させない。
- CH4のみミュートしても、CH1の主題リズムとCH3の発音位置からtempo・4/4拍子・二つの和声区間を追えるようにする。拍頭アクセント、order境界、ループ境界の少なくとも一つをCH1またはCH3でも示し、CH4を唯一のリズム情報源にしない。
- CH2とCH4を同時にミュートしても、CH1 + CH3だけで主旋律、C major、`C`/`F`/`G`/`Am`の主要進行、拍、フレーズ進行、order 5 → order 2の`G`から`C`への解決を認識できる構成にする。
- CH2の各発音はCH1またはCH3が同時に鳴っていなくても必須情報を失わせない短い補助単位とし、復帰時に直前のCH2音を聞いていないと成立しない掛け合いを置かない。CH2の和音補助は、その時点のCH1/CH3の和声音または経過として説明できる音に限定し、復帰直後だけ不協和になる保留音を避ける。
- CH4の反復は拍単位または短い周期の先頭から独立して成立するものとし、途中復帰時に直前のフィルの続きや周期の前半を必須にしない。復帰後の最初の発音は通常の反復内の拍頭または補助アクセントとして扱い、CH4だけが周期を再同期する必要がある構成を避ける。
- CH2/CH4のミュート中も再生位置は進む既存仕様を前提とし、復帰後に消音中の音を遅れて再生しない。再生位置上の現在のnoteからCH2/CH4が再開しても、CH1/CH3の和声・拍と衝突しない独立した発音単位にする。

ミュート耐性は作曲後の試聴だけに委ねず、初稿作成前の条件として記述する。最低限、CH1だけでも主旋律を追えること、CH1 + CH3で主旋律・調性またはコード進行・拍・フレーズ進行・ループ位置からなる骨格を認識できること、必須の音楽情報をCH2 / CH4だけへ配置しないこと、CH4がなくてもtempoや拍を見失いにくいこと、CH2 / CH4の復帰時に不自然な和音・リズム衝突を起こしにくいことを明示する。

#### 運用確認用BGMのSameBoy試聴結果

人によるSameBoy試聴を実施し、`build/bgm_v2_workflow_check.gb` を確認用ROMとして再生した。試聴結果は次のとおりだった。

- 軽快ではないと感じた。
- 全体的に単調に感じた。
- CH4 / Noiseがうるさく感じた。

これは運用確認用BGMの初回試聴結果の記録であり、この節ではJSON・ASM・ROMの修正内容を決定しない。修正内容の決定は、後続WBS「試聴結果を反映して運用確認用JSONの修正内容を決める」で扱う。

#### 運用確認用BGMの試聴結果を受けた次回修正内容

初回試聴で確認された「軽快ではない」「全体的に単調」「CH4 / Noiseがうるさい」の3点について、現行JSONの構造とVersion 2仕様を照合し、次回のJSON修正内容を次のとおり決定する。ここに記載する値は次回修正の目標であり、未修正の `assets/bgm_v2_workflow_check.json` の現在値を表すものではない。

##### 1. 軽快さ

現行の `tempo: 6` はVersion 2の `TicksPerRow` であり、値を大きくすると1rowが遅くなる。したがって軽快さの改善では、値を小さくする。次回は全チャンネル共通の `tempo` を **6 → 5** に変更する。曲中・order別・note別tempoは仕様にないため追加しない。

tempoだけでなく、現行CH1が全orderで16音×4row、休符なしで連続していることも、音の粒が重く聞こえる原因候補と判断した。次回は次のようにCH1を短く発音して空間を作る。

- `pulse1` の `intro_cadence`、`intro_turn`、`loop_theme_a`、`loop_theme_b`、`loop_build`、`loop_link` は、既存のnote順と音域（`C5`～`G6`）を維持する。
- 各patternの16個の発音を原則 **length 4 → length 2** とし、各発音の直後に **length 2 の `rest`** を置く。各patternは発音16個と休符16個で64rowにする。フレーズ終端だけを長くする案は今回採用せず、まず全patternで同じrow密度にしてtempo変更の効果と切り分ける。
- これによりCH1の主旋律の音列、C majorの調性、order 5からorder 2への接続句は維持しつつ、休符とアタック間隔を明確にする。CH1の音域を下げたり、主旋律をCH2へ移したりしない。
- CH2は現在も4row主体で休符があるため、軽快さの主変更対象にはせず、後述の単調さ対策で伴奏の反復を変える。CH3の8row主体の土台と、CH4の短い発音という役割も維持する。
- イントロ2 orderと `loop: {"mode":"range","start_order":2,"end_order":6}` は維持する。tempo 5への変更後の構造上の再生時間は、固定更新60Hzの定義に従い、後続WBSで生成ROMの聴感を確認して記録する。

##### 2. 単調さ

現行では、CH1は音列こそorderごとに異なるが、6 patternすべてが同じ16個×4rowのリズムである。CH4は6 patternが完全同一であり、CH2とCH3も同じ発音型をコードだけ置き換えている。このため、C major、4/4拍子、6 order、イントロ後range loop、コード進行 `C → F → G → Am → F → G` は維持したまま、各orderのリズムと補助内容に差を付ける。

次回の対象と変更は次のとおりとする。

| 対象 | 次回JSONでの変更 | 維持するもの |
| --- | --- | --- |
| CH1 / `loop_theme_a`（order 2） | 上記の2row発音＋2row休符で主題Aを提示する。既存note列は維持する。 | C→Fの主題A、CH1単独で追える主旋律 |
| CH1 / `loop_theme_b`（order 3） | 既存note列をそのまま反復せず、16音のうち前半8音は2row発音＋2row休符、後半8音は4row発音とし、後半は休符を置かず応答句として密度を上げる。合計64rowになるよう前半8音の後に2row休符を8個置く。 | G→Amの応答、`C5`～`G6`、CH1の主旋律性 |
| CH1 / `loop_build`（order 4） | 1～8番音は2row発音＋2row休符、9～16番音は2row発音＋2row休符のままにし、既存のF→G上行・反復を維持する。ただし9番音以降の2回目のG系まとまりは、既存列の先頭音を繰り返さず、最後の4音を `G5, B5, D6, G6` にする。 | F→Gの展開とorder 5への接続、音域 |
| CH1 / `loop_link`（order 5） | 既存note列と2row発音＋2row休符を維持し、最後の `G5` は最後の2row休符を置かずlength 4にする（pattern合計は64rowのまま）。 | C確認→G終止、order 2のCへの解決、ループ境界 |
| CH2 / `loop_support_a`（order 2） | 既存の4音＋restのまとまりを維持し、2つ目の和声区間（F）だけ `F4,A4,C5,rest` から `F4,C5,A4,rest` へ順序を変える。 | 補助役、CH1不在でも必須情報を担わないこと |
| CH2 / `loop_support_b`（order 3） | G区間を `G4,B4,D5,rest`、Am区間を `A4,E5,C5,rest` とし、現行の後半の機械的な同型反復をやめる。 | G→Amの和声、主旋律との音域分離 |
| CH2 / `loop_support_c`（order 4） | 8row単位の4音＋restを維持しつつ、前半F区間を `F4,C5,A4,rest`、後半G区間を `G4,D5,B4,rest` にする。 | F→G、CH2をミュートしてもCH1+CH3で骨格が残ること |
| CH3 / `loop_foundation_c`（order 4） | 8rowの同音反復をやめ、前半4音を `F3,F3,A3,C4`、後半4音を `G3,G3,B3,C4` とする。rootを失わない範囲の短い上行で展開感を出す。 | CH3の低域、F→G、CH1+CH3の調性・拍・境界 |
| CH4 / 全loop pattern | patternごとの差は下記のNoise方針で作る。CH4だけでorder境界を示すフィルは追加しない。 | order数6、range loop、CH1+CH3による境界認識 |

上表のlength変更はすべてnoteのpattern row長であり、Instrumentのhardware `length` とは変更しない。すべてのpatternの展開後行数は64row以内とし、note列と休符を明示して64rowに収める。C major、4/4、6 order、先頭2 orderのイントロ、order 1→2およびorder 5→2のG→C解決は変更しない。

##### 3. CH4 / Noiseの音量と密度

現行CH4は、`workflow_low_accent`（initial_volume 8 / 15bit）をC3、`workflow_mid_accent`（6 / 7bit）をC5、`workflow_high_accent`（4 / 7bit）をC7に割り当て、全6patternでC3を拍頭、C7を2回、C5を1回、計8発音（各2row、restは2～6row）を同一位置で繰り返している。発音回数・高域アクセントの反復・ID 1の音量が、補助以上に前面へ出た原因候補である。

Noiseのwidth_modeやnote値を先に変えると音色・pitch indexの差と音量差を切り分けにくいため、次回はまず次を変更する。

- Instrumentの `initial_volume` は **8 → 5**、**6 → 4**、**4 → 3**（ID 1/2/3）へ下げる。`envelope_direction: down`、`envelope_sweep: 0`、hardware `length: 0` / `length_enable: false`、width_mode（ID 1は15bit、ID 2/3は7bit）は維持する。
- 発音note側のvolumeは **8 → 5**、**6 → 4**、**4 → 3**（ID 1/2/3）へ下げる。CH4の通常noteのvolume上限8という仕様内であり、restにはvolumeキーを付けない。
- `loop_rhythm_a`（order 2）はID 1のC3を1拍目に1回、ID 2のC5を4拍目に1回だけ鳴らし、それぞれlength 2、間はrestとする。ID 3は使わない。
- `loop_rhythm_b`（order 3）はID 1のC3を1拍目に1回、ID 3のC7を3拍目の補助に1回だけ鳴らす。各length 2、他はrestとする。
- `loop_rhythm_c`（order 4）はID 1のC3を1拍目に1回だけ鳴らし、残りはrestとする。
- `loop_link_rhythm`（order 5）はID 1のC3を1拍目に1回、ID 2のC5を4拍目に1回だけ鳴らす。ループ直前のフィルや連続C7は追加しない。
- `intro_rhythm_a` / `intro_rhythm_b` は、イントロの拍をCH1+CH3で確認できるため、各patternをID 1のC3を1拍目に1回、ID 2のC5を4拍目に1回だけとする。イントロだけ別のNoise密度にはしない。

発音を各pattern 2回以下にすることでCH4を補助へ戻し、Noiseの音色（width_mode）を変更せずに音量と発音頻度の効果を確認できるようにする。CH4をミュートしても、CH1の2row発音と休符、CH3の8rowの発音位置、C/F/G/Amの進行で拍・フレーズ境界・ループ解決を認識できる構成を維持する。CH4復帰時は単発の通常アクセントから再開し、消音中のフィルの続きや再同期を要求しない。

##### 後続WBSでの確認ポイントと未確定事項

後続WBS「修正した運用確認用JSONからASMと確認用ROMを再生成する」では、上記の値をJSONへ実装し、次をSameBoyで確認する。

- tempo 5とCH1の2row発音＋2row休符で、軽快さが改善し、主旋律が途切れて聞こえないこと。
- order 0～5のCH1/CH2/CH3の差、order境界、order 5→2のG→C解決が、通常再生とCH4ミュートの双方で聞き取れること。
- CH4単独、CH2+CH4ミュート時にもCH1+CH3の骨格が成立し、復帰時に不協和・過大なNoise・不自然な再同期がないこと。
- Noiseのvolume低下と発音回数削減で「うるさい」が解消すること。width_mode変更、Noise noteの隣接値への変更、さらなるtempoやnote列変更は、上記実装後の人による試聴結果がないため **未確定** とし、今回決めない。

#### 運用確認用BGMの修正後SameBoy再試聴結果

人による再試聴を実施し、前回修正後の `build/bgm_v2_workflow_check.gb` を確認用ROMとして再生した。再試聴結果は次のとおりだった。

- 前回の修正で `tempo` を `6` から `5` へ変更し、CH1を2row発音＋2row休符へ変更した。再生速度が速くなったことは感じられたが、軽快さは改善しなかった。評価は「テンポが速くなっただけ」だった。したがって、tempo変更だけで軽快さを解決する方針は不十分だった。
- CH1 / CH2 / CH3のpatternを変更した後も、単調さは改善しなかった。現在のorder構成やnote列の差だけでは、聴感上十分な変化になっていない可能性がある。ただし、今回の試聴結果だけでは原因を確定できないため、これを仕様として確定しない。
- 前回はCH4 / Noiseが「うるさい」と評価されたため、Noise Instrumentとnoteのvolumeを下げ、発音回数も削減した。再試聴では通常再生中にNoiseが聞き取れなくなった。「うるさい」は解消したが、CH4の固定役割である「消失可能なリズム補強」として存在を認識できる状態ではなかった。現在の音量・発音頻度の組み合わせは下げすぎだったと扱う。
- `build/bgm_v2_workflow_check.gb` では、ボタン操作によるチャンネルミュートを確認できなかった。ただし、このROMはミュート操作対応オプションなしの通常ROMとして生成されている。`tools/build_sound_test_rom.py` は `--ch2-mute-toggle`、`--ch4-mute-toggle`、`--ch2-ch4-mute-toggle` を持ち、`tools/README.md` に記載された専用ROMでCH2、CH4、CH2+CH4のミュートを確認する方式である。したがって、通常ROMでミュート操作を確認できなかったことは実装不具合とは扱わず、BGMの聴感上の不合格とは分離して記録する。

この再試聴では、軽快さ、単調さ、CH4の認識性について期待した修正効果を満たさなかった。よって、修正後の人によるSameBoy確認および親WBSは完了扱いにしない。今回の記録ではJSON、ASM、ROMの新しい具体値を決定しない。

#### 再試聴結果を受けた次回修正方針の検討論点

次回の修正方針を決める際は、今回の結果を踏まえて次の論点を検討する。以下は検討対象であり、具体的なnote列、`length`、tempo、Noise volume、Instrument値を確定するものではない。

##### 1. 軽快さ

tempoをさらに速くするだけの修正は行わない方向で検討する。CH1のリズムパターン、音価の一律な繰り返しを避けること、同じ「発音→休符」の反復による機械的な印象、フレーズ内のアクセント位置、上行・下行や跳躍を含むメロディ変化、CH2との掛け合い、CH3のリズム変化を検討対象とする。具体的なnote列やlength値は次回の方針決定まで未確定とする。

##### 2. 単調さ

orderごとのnote列を少し変えるだけでなく、聴感上区別できるフレーズ構成を検討する。フレーズA/Bなどの明確な区別、主旋律のリズム変化、CH2の対旋律・応答、CH3のベースパターン変化、orderごとの密度差、休符の位置、ループ前の展開や解決感を論点とする。これらは今回の段階では仕様値として確定しない。

##### 3. Noise

現在の発音回数をそのまま維持するかも含めて再検討する。以前の音量に完全には戻さず、現在の「聞こえない」状態も採用しない方向とし、volumeと発音頻度を別々のパラメータとして調整する。CH4は主役ではなく、消失しても曲が成立する補助リズムとして認識できる程度を目標にする。具体的なvolume値や発音配置は根拠なく確定しない。

#### 次回修正用の確定JSON仕様

前回再試聴結果を受けた検討論点について、次回JSON修正で使用する具体値を確定する。ここに記載する内容は候補ではなく、次WBS「再修正した運用確認用JSONからASMと確認用ROMを再生成する」で実装する正本仕様である。各patternの展開後row数を実計算し、すべて64rowとなることを確認した。

##### 共通条件

- `version = 2`、`tempo = 5`、C major、共通6 order、先頭2 orderのイントロ、`loop = {"mode":"range","start_order":2,"end_order":6}`を維持する。
- tempoはさらに速くしない。前回は再生速度だけが速くなり軽快さが改善しなかったため、次回はtempoではなくリズム、休符、フレーズ差の効果を切り分けて試聴する。
- Pulse1 Instrumentと`volume = 12`、Pulse2 Instrumentと`volume = 7`、Wave Instrument・Wave tableと`volume = 10`は維持する。

##### CH1 / Pulse1

一律の2row発音＋2row休符の反復を廃止し、patternごとにアクセント、密度、応答、終止を変える。各patternは次のとおりとする。

```text
intro_cadence (64row):
C5/4, rest/2, E5/2, G5/4, rest/4,
E5/2, rest/2, G5/4, rest/2, B5/2, rest/4,
G5/4, rest/2, B5/2, D6/4, rest/4,
B5/4, rest/2, G5/2, rest/2, C6/4, rest/2

intro_turn (64row):
A5/2, rest/2, C6/4, rest/2, E6/2, rest/4,
C6/4, rest/2, A5/2, E5/4, rest/4,
G5/4, B5/2, rest/2, D6/4, rest/2, B5/2,
G5/4, rest/2, D6/2, rest/2, G5/4, rest/2

loop_theme_a (64row, C→F):
C5/4, rest/2, E5/2, G5/4, rest/4,
E5/2, rest/2, G5/4, rest/2, C6/2, rest/4,
F5/4, rest/2, A5/2, C6/4, rest/4,
A5/2, rest/2, G5/4, rest/2, F5/2, rest/4

loop_theme_b (64row, G→Am):
G5/4, B5/2, rest/2, D6/4, rest/2, B5/2,
D6/4, B5/2, rest/2, G5/4, rest/2, D6/2,
A5/4, rest/2, C6/2, E6/4, rest/4,
E6/4, C6/2, rest/2, A5/4, rest/2, E5/2

loop_build (64row, F→G):
F5/2, rest/2, A5/4, rest/2, C6/2, rest/4,
A5/4, rest/2, F5/2, C6/4, rest/4,
G5/4, B5/2, rest/2, D6/4, rest/2, B5/2,
G5/4, B5/2, rest/2, D6/4, rest/2, G6/2

loop_link (64row, loop resolution toward C):
C6/4, rest/2, G5/2, E5/4, rest/4,
G5/2, rest/2, B5/4, rest/2, D6/2, rest/4,
B5/4, rest/2, G5/2, D6/4, rest/4,
D6/4, rest/2, B5/2, rest/2, G5/6
```

`intro_turn`の終端はGとし、イントロ後のloop先頭Cへの解決を明確にする。`loop_build`の`G6`は現行JSONですでに使用している音域内であり、新規音域拡張とは扱わない。`loop_link`の最終`G5`はlength 6を維持する。

##### CH2 / Pulse2

常時アルペジオではなくCH1への応答として聞こえる構成にする。既存note列とコード進行を維持し、Pulse2 Instrumentと`volume = 7`は変更しない。

```text
intro_harmony_a (64row, C→G):
rest/4, C4/4, rest/4, G4/4, rest/4, E4/4, rest/8,
rest/4, G4/4, rest/4, B4/4, rest/4, D5/4, rest/8

intro_harmony_b (64row, Am→G):
rest/4, A4/4, rest/4, C5/4, rest/4, E5/4, rest/8,
rest/4, G4/4, rest/4, B4/4, rest/4, D5/4, rest/8

loop_support_a (64row):
rest/4, E4/4, rest/4, G4/4,
rest/4, G4/4, rest/4, E4/4,
rest/4, A4/4, rest/4, C5/4,
rest/4, C5/4, rest/4, A4/4

loop_support_b (64row):
rest/4, B4/4, rest/4, D5/4,
rest/4, D5/4, rest/4, B4/4,
rest/4, C5/4, rest/4, E5/4,
rest/4, E5/4, rest/4, C5/4

loop_support_c (64row):
rest/2, A4/2, rest/2, C5/2, rest/4, F4/4,
rest/2, C5/2, rest/2, A4/2, rest/4, F4/4,
rest/2, B4/2, rest/2, D5/2, rest/4, G4/4,
rest/2, D5/2, rest/2, B4/2, rest/4, G4/4

loop_link_support (64row):
rest/4, E4/4, rest/4, G4/4,
rest/4, G4/4, rest/4, E4/4,
rest/4, B4/4, rest/4, D5/4,
rest/8, D5/4, rest/4
```

`loop_support_c`は各16row単位を`2+2+2+2+4+4=16` rowとし、4単位で64rowとする。introを含め、CH2はCH1の主旋律を置き換えず、休符を含む短い応答単位として構成する。

##### CH3 / Wave

鳴りっぱなし感を減らすため、8row発音と8row休符を混ぜる。Wave Instrument、Wave table、`volume = 10`、低域の土台という役割を維持する。指定noteは現行JSONの音域・進行内であり、`E3`も既存テストのCH3音域`C3`〜`C4`内である。

```text
intro_root_a (64row, C→G):
C3/8, rest/8, C3/8, rest/8,
G3/8, rest/8, B3/8, rest/8

intro_root_b (64row, Am→G):
A3/8, rest/8, C4/8, A3/8,
G3/8, rest/8, G3/8, rest/8

loop_foundation_a (64row, C→F):
C3/8, rest/8, G3/8, C4/8,
F3/8, rest/8, C4/8, F3/8

loop_foundation_b (64row, G→Am):
G3/8, rest/8, B3/8, G3/8,
A3/8, rest/8, E3/8, A3/8

loop_foundation_c (64row, F→G):
F3/8, rest/8, A3/8, C4/8,
G3/8, rest/8, B3/8, G3/8

loop_link_foundation (64row, C→G):
C3/8, rest/8, G3/8, C4/8,
G3/8, rest/8, B3/8, G3/8
```

CH4をミュートしても、CH1＋CH3で拍、コード進行、フレーズ境界、ループ境界が認識できることを次回試聴で評価する。

##### CH4 / Noise

発音回数、発音位置、note、width_modeは変更せず、volumeだけを1段階戻す。通常再生で「聞こえない」と前回の「うるさい」の中間になり、主役ではない補助リズムとして認識できるかを切り分ける。

- Instrument 1 / C3: `initial_volume = 6`、note `volume = 6`
- Instrument 2 / C5: `initial_volume = 5`、note `volume = 5`
- Instrument 3 / C7: `initial_volume = 4`、note `volume = 4`
- width_modeはID1が`15bit`、ID2/3が`7bit`、hardware length関連、`envelope_direction`、`envelope_sweep`は維持する。
- 発音位置は現行JSONと同一とし、`intro_rhythm_a/b`、`loop_rhythm_a`、`loop_link_rhythm`はrow 0のID1/C3とrow 48のID2/C5、`loop_rhythm_b`はrow 0のID1/C3とrow 32のID3/C7、`loop_rhythm_c`はrow 0のID1/C3を使用する。各patternの発音回数は増やさない。
- CH4のrestにはvolumeを付けない。

##### 次回SameBoy試聴で評価する項目

次回の試聴では、tempo 5を固定したまま、pattern構成変更によって軽快さが改善したかを評価する。CH1の一律反復が解消され、intro終端Gからloop先頭C、各orderのC/F/G/Am、loop境界が聴感上区別できるか、CH2の応答とCH3の休符を含む骨格がCH4ミュート時にも成立するかを確認する。Noiseは「聞こえない」と「うるさい」の中間で、補助リズムとして認識できるかを評価する。期待結果を満たすまで、JSONの本番採用や正本確定には進まない。

##### 再修正後SameBoy試聴結果

人によるSameBoy試聴を実施し、再修正後の `build/bgm_v2_workflow_check.gb` を確認した。今回の再修正は期待した効果を満たさなかった。

- 軽快さは改善しなかった。「ゆったりした曲調に無理やり音符を重ねたような感じ」で違和感があり、tempo 5を維持してpattern構成・音価・休符・フレーズ差で改善する狙いは不合格だった。単純に音符を増やしたり、現在の旋律へ細かい音を重ねたりする修正は継続しない。
- 単調さも改善しなかった。CH1 / CH2 / CH3のnote列、休符、pattern差を変更しても聴感上の変化はなく、局所的なnote列変更だけでは解決しないと判断する。ただし、この試聴結果だけから原因を一意に断定しない。
- Noiseの音量そのものは問題なかった。一方で、発音位置、発音パターン、note / Noise Instrumentの使い分け、曲中のリズム上の役割が曲と全く合っておらず、文字どおりのノイズとして邪魔に感じられた。volume 6 / 5 / 4自体を音量問題とは扱わない。

今回の再修正版は本番採用しない。この結果を受けた再設計と再試聴が完了するまで、運用確認用JSONを本番採用JSONと分離した正本として確定する運用には進まない。

##### 今後の方針：曲構成からの再設計

既存曲の局所的な修正を繰り返さず、「軽快な運用確認用BGMとして、曲の骨格から再設計する」方針へ移行する。新しいtempo、調性、コード進行、note列、patternの `length`、order構成、Noiseのnote / Instrument / `width_mode`、各チャンネルの具体的なvolumeは後続WBSで決定し、ここでは確定しない。

- CH1 / Pulse1は、現在の旋律を細かく加工せず、軽快さを最初から意図した短い主旋律モチーフを新しく設計する。
- CH2 / Pulse2は、CH1と常時重ならず、CH1の隙間やフレーズ境界へ短く応答する役割として再設計する。
- CH3 / Waveは、単なる長い低音の土台ではなく、曲の拍とコード進行を感じられるベースとして再設計する。CH4が消えてもCH1＋CH3で曲の骨格が成立するミュート耐性要件は維持する。
- CH4 / Noiseは、volume調整を主な修正手段にせず、曲の拍・アクセント・フレーズに合った簡単なドラム／リズムパートとして再設計する。消失しても曲が成立する補助リズムという役割は維持する。

効果音実装方式の比較:

| 方式 | 実装難易度 | 保守性 | CPU/RAM/ROM | BGM干渉 | 効果音品質 | hUGETracker/JSONフロー | 評価 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hUGEDriverのみで共存 | 高い | 低い | RAM状態管理が複雑 | 曲状態切替や同時再生が難しい | hUGE表現に依存 | JSON→hUGEDriver ASMは流用しやすい | 初版では不採用。hUGEDriverを複数曲SFXプレイヤーとして扱う設計が重い。 |
| APU直接制御のみ | 中程度 | 中程度 | 軽い | BGMをhUGEDriverで鳴らせない | レジスタ単位で制御しやすい | BGM用JSON→ASM資産を活かしにくい | BGM制作フローと合わないため不採用。 |
| hUGEDriver + APU直接制御 | 中程度 | 高い | SFX状態分の小RAMで済む | 使用チャンネルだけ短時間干渉 | 短いUI/爆発音を作りやすい | JSONを正本にし、確認用ASMと本番用SFX ASMを分けられる | 初版で採用。 |
| JSON→ASM生成フロー活用 | 中程度 | 高い | 生成データ量次第 | 採用方式に依存 | JSON仕様を拡張しやすい | 正本JSONを維持できる | ハイブリッド方式と組み合わせて採用。 |

採用理由:

- Pocket Sweeper初版の効果音は短いUI音と短い結果通知音が中心で、複雑なミキシングは不要である。
- BGMはhUGEDriverで安定再生しつつ、効果音は必要なチャンネルだけ一時的に借りる方が実装範囲を小さくできる。
- `hUGE_mute_channel` により、効果音中のチャンネルをhUGEDriverが触らない状態にできるため、APU直接制御との役割分担が明確になる。
- JSONを正本とする運用は維持し、単体確認用には既存のJSON→hUGEDriver ASM、実装用にはJSON→SFX ASMデータを使う。
- 将来、より高度なSFXが必要になった場合も、SFX ASM生成ツールやJSON仕様を拡張しやすい。

効果音用SFX ASMデータ形式:

- 本体ROM向け効果音は、JSONから `tools/json_to_sfx_asm.py` でSFX ASMへ生成する想定とする。
- ASMは効果音ID定数、効果音ポインタテーブル、各効果音データで構成する。
- 各効果音データはヘッダとstep列で構成する。
- step列はヘッダ内のstep数で管理し、終端マーカーは持たない。
- 初版ではPulse1用とNoise用を対象にする。
- Pulse2、Wave、複数チャンネル同時SFXは初版対象外とし、将来必要になった場合にchannel種別を追加する。

効果音ID管理:

- `json_to_sfx_asm.py` は効果音ごとにASM定数を出力する。
- IDは0から連番とし、ポインタテーブルのindexと一致させる。
- ID定数名は `SFX_<NAME>` 形式とする。例: `SFX_CURSOR = 0`。
- 効果音ポインタテーブルは `SfxTable` とし、`dw SfxCursor` のように各効果音データへのポインタを並べる。
- ゲーム本体は効果音IDを指定して `SfxTable` から効果音データを取得する。

SFXヘッダ形式:

```asm
; offset  size  meaning
; 0       1     channel kind
; 1       1     priority
; 2       1     step count
; 3       1     total frames
```

- `channel kind` は `SFX_CH_PULSE1 = 0`、`SFX_CH_NOISE = 3` とする。値はGame BoyのCH1/CH4に対応させる。
- `priority` は値が大きいほど高優先度とする。
- `step count` は後続step数を表す。0は不正データとする。
- `total frames` は効果音全体の目安長さで、再生管理やデバッグ表示に使える値とする。実再生は各stepのwait frame合計で管理する。

Pulse step形式:

```asm
; offset  size  meaning
; 0       1     wait frames
; 1       1     NR10
; 2       1     NR11
; 3       1     NR12
; 4       1     NR13
; 5       1     NR14
```

- Pulse1効果音では各stepでNR10/NR11/NR12/NR13/NR14を書き込む。
- `wait frames` はそのstepを書き込んだ後に保持するフレーム数とする。
- `NR14` は必要に応じてtrigger bitを立てた値を出力する。
- 初版のUI効果音は1stepを基本とする。

Noise step形式:

```asm
; offset  size  meaning
; 0       1     wait frames
; 1       1     NR41
; 2       1     NR42
; 3       1     NR43
; 4       1     NR44
```

- Noise効果音では各stepでNR41/NR42/NR43/NR44を書き込む。
- `wait frames` はそのstepを書き込んだ後に保持するフレーム数とする。
- `NR44` は必要に応じてtrigger bitを立てた値を出力する。
- 地雷爆発やゲームオーバーなどはNoise効果音として作成する。

再生時間管理:

- SFX再生中は、現在の効果音ID、step pointer、残りwait frames、priority、channel kindをWRAMに保持する。
- `wait frames` が0のstepは不正データとする。
- stepを最後まで処理したら、対象チャンネルのhUGEDriverミュートを解除し、SFX再生状態をクリアする。
- 終端マーカーではなくstep countで終了を判定するため、再生処理は固定回数で読み進められる。

JSONから生成する範囲:

- 既存の楽曲定義JSONを正本とし、`type = "sfx"` のJSONからSFX ASMを生成する。
- Pulse効果音では、`channel`、`note`、`length`、`instrument`、Pulse Instrument詳細からNR10/NR11/NR12/NR13/NR14を生成する。
- Noise効果音では、`channel`、`length`、`instrument`、Noise Instrument詳細からNR41/NR42/NR43/NR44を生成する。
- `priority` は効果音JSONで明示する。未指定時は本番SFX ASM生成時にバリデーションエラーとする。
- 複数noteを含むSFX JSONは複数stepへ変換できる形式とするが、初版のUI効果音は1stepを基本とする。

`tools/json_to_sfx_asm.py`:

- 効果音JSONをUTF-8で読み込み、本体ROM向けSFX ASMを出力する。
- コマンドライン引数は、入力JSON、出力ASMの順に指定する。
- 使用例:

```bash
python tools/json_to_sfx_asm.py assets/se_cursor.json obj/se_cursor_sfx.asm
```

- `version = 1`、`type = "sfx"` のJSONのみ対応する。
- `priority` は必須で、SFX ASMヘッダへ出力する。
- 初版では `pulse1` と `noise` の単一チャンネルSFXのみ対応する。
- `pulse2`、`wave`、複数チャンネル同時SFX、非null effectはバリデーションエラーにする。
- `pulse1` ではnoteとPulse Instrument詳細からNR10/NR11/NR12/NR13/NR14を書き出す。
- `noise` ではNoise Instrument詳細からNR41/NR42/NR43/NR44を書き出す。
- 自動生成ASMは `obj/` 直下へ出力し、サブディレクトリは使わない。

本体ROMへのSFXデータ組み込み:

- Makefileは `assets/se_cursor.json` から `tools/json_to_sfx_asm.py` で `obj/se_cursor_sfx.asm` を生成する。
- `obj/se_cursor_sfx.asm` は `obj/se_cursor_sfx.o` へアセンブルし、本体ROMのリンク対象に含める。
- 自動生成SFX ASMは `obj/` 直下の中間生成物として扱い、Git管理対象にはしない。
- 生成ASMは、後続の効果音再生処理から参照できるように `SfxTable`、`SFX_CURSOR`、`SFX_CH_PULSE1`、`SFX_CH_NOISE` をRGBDS 1.0.1系で利用できる形式で公開する。
- 既存のテストBGM ASMは現状の `src/bgm_test.asm` の組み込み方法を維持し、今回の作業では新規BGM制作やBGM差し替えは行わない。
- 今回の組み込み範囲はデータをROMへリンクできる状態までとし、SFX再生API、priority判定、実際の発音タイミングは後続WBSで実装する。

Noise Instrument詳細からAPUレジスタへの変換方針:

- NR41: `noise_length & $3F`。
- NR42: `(initial_volume << 4) | (envelope_direction_bit << 3) | envelope_sweep`。
- NR43: `(clock_shift << 4) | (width_mode_bit << 3) | divisor_code`。
- NR44: `(length_enable_bit << 6) | $80`。trigger bitはSFX step出力時に常に立てる。
- `envelope_direction_bit` は `"up"` を1、`"down"` を0とする。
- `width_mode_bit` は `"7bit"` を1、`"15bit"` を0とする。
- `length_enable_bit` は `true` を1、`false` を0とする。
- 初版ではNoise効果音は地雷爆発、ゲームオーバーなどに使う。

効果音とBGMのチャンネル運用方針:

- Game Boyは4チャンネルしか同時発音できないため、効果音再生時はBGMの一部チャンネルを一時的にミュートして使用する。
- UI効果音は可能な限りCH4またはCH2で実装する。
- BGMはCH2が一時的にミュートされても違和感が少なくなるように作曲する。
- CH1を使用する効果音は、ゲームプレイ上重要な演出に限定する。

| チャンネル | 初版方針 |
| --- | --- |
| CH4 / Noise | 最優先で効果音に使用する。カーソル移動、キャンセル、旗設置など、音程を必要としないUI効果音に使う。 |
| CH2 / Pulse2 | CH4で表現しにくい音程付き効果音に使用する。決定音、マス開封音などを想定する。BGMはCH2が一時的にミュートされることを前提として作曲する。 |
| CH1 / Pulse1 | 爆発音やクリア演出など、重要な効果音で必要な場合のみ使用する。BGMの主旋律への影響が大きいため、常用しない。 |
| CH3 / Wave | 原則として効果音には使用しない。BGMのベースや持続音など、安定した再生を優先する。 |

効果音の優先順位:

1. 地雷爆発、ゲームオーバー
2. クリア
3. マス開封、旗設置、旗解除
4. 決定、キャンセル
5. カーソル移動

- 同じフレームで複数の効果音要求が発生した場合は、最も優先度の高い1つだけを鳴らす。
- 効果音キューは初版では持たない。
- 効果音再生中に高優先度の効果音が要求された場合は、高優先度の効果音で上書きする。
- 効果音再生中に同等以下の優先度の効果音が要求された場合は、初版では無視する。
- 地雷爆発やゲームオーバーなど重要な効果音では、必要に応じてBGMを停止または該当チャンネルを強く上書きしてよい。

未確定事項:

- CH2 / Pulse2効果音を扱えるように、`tools/json_to_sfx_asm.py`、SFX ASMデータ形式、`Sound_PlaySfx` / `Sound_UpdateSfx` の対応範囲を見直す。
- クリア時にBGMを停止するか、クリアジングルをBGM扱いで再生するか、短い効果音扱いにするかはクリアBGM制作時に決める。

### 旧2チャンネル構成のBGM試作仕様

Version 1 JSONとPulse1 / Pulse2を使った旧制作フローでは、以下の3曲を試作した。この表の用途・方針は旧試作時の具体値であり、後続WBSで新規作成する初版用4チャンネルBGMの最終作曲条件ではない。

| BGM | 正本JSON | 用途 | 方針 |
| --- | --- | --- | --- |
| タイトルBGM | `assets/bgm_title.json` | タイトル画面 | 明るく短い2パターンのループとし、ゲーム開始前の期待感を出す。 |
| プレイ中BGM | `assets/bgm_game.json` | 通常プレイ中 | 長時間聴いても邪魔になりにくい、落ち着いた2パターンのループとする。 |
| クリアBGM | `assets/bgm_clear.json` | クリア時 | 短い達成感のあるフレーズとし、旧試作ではBGMデータとして作成する。 |

- BGMの正本はJSONとし、`assets/` 直下へ配置する。
- 旧試作ではPulse1 / Pulse2を使用し、Wave / Noiseは空patternとする。
- 効果音との競合を抑えるため、Pulse2は伴奏中心とし、一時的にミュートされても曲の輪郭が失われにくい構成にする。
- `tools/json_to_huge_asm.py` は `SECTION "...", ROMX` を出力するが、ROM ONLY構成でも `rgblink` が32KiB内のbanked sectionとして配置できるため、カートリッジタイプ変更は不要とする。
- 各JSONは `tools/json_to_huge_asm.py` でASMへ変換し、`tools/build_sound_test_rom.py` で確認用ROMを生成する。
- SameBoyでの再生確認後、問題があればJSONを修正して再生成する。
- 旧試作時には、クリアBGMをループさせるか、一度だけ再生して停止させるかを未確定としていた。新しい4チャンネル版の判断はクリアBGM制作の後続WBSで行う。

### 運用確認用BGMの今後の制作フロー

これまでの運用確認用BGMでは、ChatGPTまたはCodexがVersion 2楽曲定義JSONを直接作曲し、SameBoy試聴後にJSONを修正する方式を試した。この方式では軽快さ、単調さ、曲とNoiseの一体感を十分に改善できなかったため、今後の運用確認用BGMではCodexを作曲担当にしない。

今後は、ChatGPTが曲の方向性、MIDI試作、必要に応じた複数候補、楽曲設計メモを作成し、人がMIDIを通常の再生環境で試聴して採用案を決める。採用MIDIにはtempo、key、曲構成、主旋律、コード進行、ベース、リズム、trackごとの役割、ループ位置を記録した設計メモを添える。人が完成MIDIをJSON化対象として承認するまでは、CodexによるJSON化へ進まない。

Codexは、採用済みMIDIと楽曲設計メモをGame Boy 4chへ編曲し、Version 2 JSON、hUGEDriver用ASM、確認用ROMを生成して仕様適合と主要構造を自動確認する担当とする。CH1 / Pulse1は主旋律、CH2 / Pulse2は補助・応答、CH3 / Waveはベース、CH4 / Noiseはドラム・リズムへ対応させる。単音化、octave調整、note length量子化、同時発音削減、ドラムからNoiseへの変換は、採用MIDIの音楽的構造を可能な限り維持する範囲で行う。

MIDI段階では人が曲調、軽快さ、単調さ、違和感、メロディ、リズム、ループ適性を評価する。MIDIが不合格なら作曲工程へ戻り、MIDIは合格だがSameBoy版が不合格なら、原則としてGB編曲・JSON変換部分だけを調整する。SameBoyではMIDIで承認した曲調、主旋律、リズム感が維持され、CH2 / CH3 / CH4の編曲やGame Boy音源への変換で違和感が生じていないことを比較確認する。

### BGM・効果音制作フロー

- BGMでは、ChatGPTがMIDIを試作し、人が試聴・採用・完成承認した後、Codexが採用MIDIと楽曲設計メモをGame Boy 4ch向けへ編曲してVersion 2楽曲定義JSONを作成する。人の完成MIDI承認前にJSON化へ進まない。
- BGMの最終的な実装上の正本はVersion 2楽曲定義JSONとする。JSONからhUGEDriver用ASMを生成し、ASMから確認用ROMを生成する。SameBoyではMIDI原曲とGB版を比較確認し、GB版だけに問題がある場合は原則としてMIDI作曲へ戻らず、GB編曲・JSON変換部分を調整する。
- 効果音は従来どおりJSONを正本とし、JSONからASMを生成し、必要に応じてAPU直接制御へ変換する。BGMのMIDI先行方式を効果音へ適用しない。
- BGM・効果音とも、hUGETracker上で最初から手作業で打ち込むのではなく、定義ファイルで構造を管理する。
- hUGETracker上で直接微調整することは基本方針としない。
- BGMのGB版再生確認で問題があった場合は、hUGETracker上で修正するのではなく、GB編曲・JSON変換部分を調整して再生成する。効果音は従来どおりJSONを修正して再生成する。
- hUGETrackerは主に `.uge` 読み込み確認、仕様調査、必要時の手動確認に使う。
- hUGETrackerには `.uge` からASMを自動ExportするCLIが確認できないため、通常フローへ組み込まない。
- BGMのVersion 2楽曲定義JSONは、採用MIDIと楽曲設計メモを基にCodexがGame Boy 4ch向けへ変換して作成し、`assets/` 直下で実装上の正本として扱う。効果音JSONも従来どおり同じ場所で正本として扱う。
- JSONからhUGEDriver用RGBDS ASMを直接生成する主フローでは `tools/json_to_huge_asm.py` を使う。
- ASMからサウンド再生確認用テストROMを生成する主フローでは `tools/build_sound_test_rom.py` を使う。
- 既存の `tools/json_to_uge.py` は、hUGETracker確認用・互換確認用として残す。
- `.uge` 生成は主フローではなく補助フローとする。
- `tools/json_to_uge.py` の使い方は `tools/README.md` に記載する。
- 初版では完全な自動作曲ではなく、短いBGMや効果音の下書きを作る用途とする。
- JSON仕様は最初から複雑にしすぎず、曲名、テンポ、パターン、チャンネル、ノート、長さ、音色番号程度を扱う。
- `.uge` 形式の詳細が不明な部分は、既存のhUGETracker出力ファイルやサンプルを確認しながら実装する。
- 不明点は推測で確定せず、WBSまたはTODOとして記録する。
- 各BGM・効果音制作では、JSON作成、JSON修正、`tools/json_to_huge_asm.py` によるASM生成、`tools/build_sound_test_rom.py` によるテストROM生成、Game Boyエミュレータでの確認、必要に応じたJSON再修正のサイクルで制作する。
- サウンド制作では、原則としてhUGETracker上で直接編集するのではなく、JSONを修正して再生成する運用を維持する。
- WBS上では、BGM制作と効果音制作はJSON作成・調整・テストROM確認までを扱い、サウンド実装は作成済みのBGM・効果音をゲーム本体へ組み込み、適切なタイミングで再生する処理を扱う。
- BGMと効果音の同時再生、優先順位、チャンネル割り当ては未確定のため、サウンド実装では最初に再生制御方針を決める。

目標フロー:

```text
JSON
  ↓
hUGEDriver用RGBDS ASMを生成
  ↓
サウンド確認用テストROMを生成
  ↓
SameBoyなどのGBエミュレータで再生確認
  ↓
問題があればJSONを修正して再生成
```

`tools/json_to_uge.py`:

- 楽曲定義JSONをUTF-8で読み込み、hUGETracker v1.0.11向けのSong Version 6 `.uge` を書き出す。
- コマンドライン引数は、入力JSON、出力 `.uge` の順に指定する。
- 使用例:

```bash
python tools/json_to_uge.py assets/test_draft.json assets/test_draft.uge
```

- サンプルJSONは `assets/test_draft.json` に配置する。
- サンプルJSONから生成した `.uge` は `assets/test_draft.uge` に配置する。
- hUGETrackerでの読み込み、保存、RGBDS ASM Export確認は後続WBSで実施する。

初版 `tools/json_to_uge.py` の対応範囲:

- JSON仕様 `version = 1` を読み込む。
- `title` を `.uge` の曲名として保存する。
- `type` は `bgm` / `sfx` のバリデーション対象とし、`.uge` には直接保存しない。
- `tempo` はSong Version 6の `TicksPerRow` として保存する。
- `order` と `patterns` から4チャンネル分の `OrderMatrix` と64行固定patternを生成する。
- `length` は行数として扱い、音符セル1行と残りの空行へ展開する。
- noteは `C3`～`B8`、シャープ表記、`rest` を扱う。
- effectは `effect: null`、`effect_param: null` のみ扱い、`.uge` では `EffectCode = 0`、`EffectParams.Value = 0` を出力する。
- `wave` / `noise` が未使用の場合は空pattern参照と空patternを出力する。
- Instrument IDは1～15のみ許可し、0はJSON入力では禁止する。
- Instrument詳細パラメータはJSONでは扱わず、hUGETracker初期値相当で出力する。

初版 `tools/json_to_uge.py` の未対応範囲:

- hUGETracker GUIでの読み込み・保存・ASM Exportの自動確認。
- 非null effect。
- Instrument詳細パラメータ編集。
- Wave table編集。
- Routine、Instrument subpattern編集。
- 64行を超えるpattern。

`tools/json_to_huge_asm.py`:

- 楽曲定義JSONをUTF-8で読み込み、hUGEDriver用RGBDS ASMを直接書き出す。
- コマンドライン引数は、入力JSON、出力ASMの順に指定する。
- song descriptorのラベル名は、出力ASMファイル名からRGBDS symbolとして安全な名前を生成する。
- 使用例:

```bash
python tools/json_to_huge_asm.py assets/test_draft.json obj/test_draft.asm
```

- サンプルJSONから生成したASMは `obj/test_draft.asm` に配置する。
- 自動生成ASMは `obj/` 直下へ出力し、サブディレクトリは使わない。
- hUGETracker Export ASMとの比較は `obj/test_draft.asm` と `obj/test_draft_huge.asm` で実施済みである。

初版 `tools/json_to_huge_asm.py` の対応範囲:

- `include "hUGE.inc"`、`SECTION`、song descriptor、order、pattern、instrument、routine、waveラベルを出力する。
- noteはJSON表記からRGBDS ASM表記へ変換する。例: `C4` は `C_4`、`C#4` は `C#4`、`rest` は `___`。
- `length` は行数として扱い、音符行と空行へ展開する。
- patternは64行固定とし、不足分は `dn ___,0,$000` で埋める。
- effectは `effect: null`、`effect_param: null` のみ扱い、ASMでは `$000` を出力する。
- `wave` / `noise` が未使用の場合は空patternを出力する。
- duty instrumentsは使用された最大Instrument IDまで出力する。
- wave instruments / noise instrumentsは初版では未使用前提で空ラベルを出力する。
- routinesは16個の `ret` routineを出力する。

初版 `tools/json_to_huge_asm.py` の未対応範囲:

- 非null effect。
- Wave / Noise instrumentsの実質利用。
- Wave tableの実質利用。
- Routine、Instrument subpattern編集。
- サウンド再生確認用テストROM生成。

hUGETracker Export ASMとの比較結果:

- 比較対象は `obj/test_draft.asm` と `obj/test_draft_huge.asm` とする。
- `obj/test_draft.asm` は `tools/json_to_huge_asm.py` で `assets/test_draft.json` から生成したASMである。
- `obj/test_draft_huge.asm` は `assets/test_draft.uge` をhUGETracker v1.0.11でExportした比較用ASMである。
- song descriptorは、tempo、order参照、instrument参照、routine参照、wave参照が一致した。
- order count、order1～order4は一致した。
- pattern数はP0～P3の4patternで一致した。
- 各patternは64行で、note、instrument、effect、effect parameterが一致した。
- duty instrumentsはInstrument 1～2の出力内容が一致した。
- wave instruments / noise instrumentsは未使用の空ラベルとして一致した。
- routinesは16個の `ret` routineとして一致した。
- wavesは未使用の空ラベルとして一致した。
- コメント、空白、インデント、ラベル名の差分は比較上許容する方針だが、今回の比較では再生に影響する差分は確認されなかった。
- 今回の比較では `tools/json_to_huge_asm.py` の修正は不要だった。
- 将来、非null effect、Wave / Noise instruments、Wave table、routine、instrument subpatternを対応する場合は、同様にhUGETracker Export ASMと比較する。

`tools/build_sound_test_rom.py`:

- hUGEDriver用RGBDS ASMから、サウンド確認専用の最小Game Boy ROMを生成する。
- 本ツールはASMからROMを生成することだけを担当し、JSONの読み込みやASM生成は行わない。
- エミュレータ起動は本ツールの責務に含めない。
- コマンドライン引数は、入力ASM、出力ROMの順に指定する。
- 使用例:

```bash
python tools/build_sound_test_rom.py obj/test_draft.asm build/test_sound.gb
```

- 入力ASMはhUGEDriver用RGBDS ASMとし、song descriptorのglobal labelを含む必要がある。
- 出力ROM名は固定せず、コマンドライン引数で指定する。
- Pocket Sweeperプロジェクトでは、テストROMは `build/` に出力する想定とする。
- `build/` には最終成果物である `.gb` のみを出力し、`.map` / `.sym` などのビルド副産物は `obj/` に出力する。

`tools/build_sound_test_rom.py` の処理フロー:

1. 入力ASMからsong descriptor labelを読み取る。
2. 入力ASMを `INCLUDE` する最小ROM用ASMを `obj/` に生成する。
3. 最小ROM用ASMでAPUを初期化する。
4. 起動後に `hUGE_init` で指定曲を開始する。
5. メインループでVBlankを待ち、毎フレーム `hUGE_dosound` を呼び出す。
6. `src/hUGEDriver.asm` を別objectとして組み込む。
7. `rgbasm`、`rgblink`、`rgbfix` をPythonから呼び出す。
8. 指定した出力先にROMを出力し、`obj/` に中間ASM / OBJ / map / symを出力する。

生成物:

- `obj/<rom名>_sound_test.asm`: 入力ASMをincludeする最小ROM用ASM。
- `obj/<rom名>_sound_test.o`: 最小ROM用ASMのobject。
- `obj/<rom名>_hUGEDriver.o`: hUGEDriverのobject。
- `obj/<rom名>.map`: link map。
- `obj/<rom名>.sym`: symbol file。
- `<出力ROM>.gb`: サウンド確認用Game Boy ROM。

想定する制作フロー:

1. BGMはChatGPTでMIDIを試作し、人が採用・完成承認する。効果音はJSONを作成・確認する。
2. BGMは採用MIDIからCodexがVersion 2 JSONへ変換し、効果音はJSONを正本として扱う。
3. JSONからhUGEDriver用RGBDS ASMを生成する。
4. 生成したASMからサウンド再生確認用テストROMを生成する。
5. BGMはMIDI原曲とSameBoyなどのGB版を比較確認し、必要ならGB編曲・JSON変換を調整する。効果音は従来どおりJSONを修正して再生成する。
6. 問題がなければ生成したASMをROMへ組み込む。
7. `tools/json_to_uge.py` はhUGETracker確認用・互換確認用の補助フローとして使用する。

初版で使用する効果音一覧:

| 効果音 | 使用場面 | 方針 |
| --- | --- | --- |
| カーソル移動 | 難易度選択、通常プレイの盤面カーソル移動、ポーズメニュー項目移動 | 画面ごとに分けず共通化する。 |
| 決定 | タイトル画面START、難易度決定、ポーズメニュー決定、ゲーム終了後のタイトル復帰 | START / Aによる画面遷移・項目決定で共通化する。 |
| キャンセル | 難易度選択画面のB戻り、ポーズメニューのBによるRESUME | 戻る・閉じる操作として共通化する。 |
| マスを開く | 通常プレイで非地雷マスを開く | 1マス開封と0連鎖オープン開始時で共通化する。 |
| 旗を立てる | 未開封マスへのフラグ設置 | 旗解除とは別の短い音にする。 |
| 旗を外す | フラグ済みマスの解除 | 旗設置とは別の短い音にする。 |
| 地雷爆発 | 地雷マスを開いてゲームオーバーになる瞬間 | ゲームオーバー効果音とは別に、爆発の操作結果として鳴らす。 |
| クリア | ゲームクリア状態へ遷移する瞬間 | クリア表示と合わせて鳴らす。 |
| ゲームオーバー | ゲームオーバー状態へ遷移した後 | 地雷爆発の直後または短い間隔で鳴らす想定とする。 |

初版では、0連鎖オープン専用効果音は作成しない。0連鎖で開く各マスに効果音を鳴らすと連続再生で耳障りになりやすく、初版ではAボタンで開封を開始したタイミングの「マスを開く」効果音に集約する。

カーソル移動効果音:

- 正本JSONは `assets/se_cursor.json` とする。
- 生成ASMは `obj/se_cursor.asm` とする。
- 確認用ROMは `build/se_cursor.gb` とする。
- 用途は、難易度選択、通常プレイの盤面カーソル移動、ポーズメニュー項目移動で共通利用する。
- チャンネル運用方針に合わせ、CH4 / Noiseを使った短いクリック音として構成する。
- Noise Instrument詳細は `noise_length = 12`、`initial_volume = 8`、`envelope_direction = "down"`、`envelope_sweep = 2`、`clock_shift = 1`、`width_mode = "7bit"`、`divisor_code = 0`、`length_enable = true` とし、粗めの「ザッ」から高めで短い「チッ」「カチッ」に近いUI向けクリック音へ調整する。


#### Version 2 loopのhUGETracker Export比較記録テンプレート

この節は、hUGETracker GUIで保存・Exportを実施した後に、生成ASMとExport ASMを構造単位で比較して埋める記録欄である。GUI操作前の状態では、結果を確認済みとは扱わない。

使用ファイル:

- `full`: `assets/bgm_v2_asm_compare.json` / `assets/bgm_v2_loop_full_generated.uge` / `obj/bgm_v2_loop_full_generated.asm`
- `range`: `assets/bgm_v2_loop_range_compare.json` / `assets/bgm_v2_loop_range_generated.uge` / `obj/bgm_v2_loop_range_generated.asm`
- `none`: `assets/bgm_v2_loop_none_compare.json` / `assets/bgm_v2_loop_none_generated.uge` / `obj/bgm_v2_loop_none_generated.asm`
- 保存後UGE: `assets/bgm_v2_loop_<mode>_hugetracker_saved.uge`
- Export ASM: `obj/bgm_v2_loop_<mode>_hugetracker_export.asm`

| mode | 標準構造 | B effect | Instrument / routine / wave | loop metadata | 判定 |
|---|---|---|---|---|---|
| full | descriptor、OrderMatrix、P0～P3各64行は意味的に一致 | B effectなし（GUI確認・ASM確認） | Duty / Wave / Noise Instrument bank、各Instrument、Routine 0～15、Wave tableは表記上の差異のみ | 生成ASMの独自loop metadataは標準Exportに存在しない独自拡張 | 確認完了。再生動作に影響する不一致・比較不能なし |
| range | descriptor、OrderMatrix、P0～P4各64行は意味的に一致 | CH1最終pattern row 63だけにB02。CH2～CH4の同rowにはB effectなし | Duty / Wave / Noise Instrument、Routine 0～15は意味的に一致。Wave tableは未使用bank省略による表記上の差異 | 生成ASMの`db 1,1,63`は標準Exportにない独自拡張 | 確認完了。再生動作に影響する不一致・比較不能なし |
| none | descriptor、OrderMatrix、P0～P3各64行は意味的に一致 | B effectなし | Duty / Wave / Noise Instrument、Routine 0～15は意味的に一致。Pattern統合、Noise Instrument省略、Wave table未使用bank省略は表記上の差異 | 生成ASMの`db 2,1,63`は標準Exportに存在しない独自拡張 | 確認完了。再生動作に影響する不一致・比較不能なし |

比較分類は、`一致`、`表記上の差異`、`hUGETracker標準Exportに存在しない独自拡張`、`再生動作に影響する不一致`、`比較不能`を使用する。`*_loop_metadata`のExport側欠落は標準形式外の独自拡張として記録し、単純な不一致とはしない。

full確認済み事実（2026-07-19）:

- hUGETrackerで正常に開け、4チャンネル、order 0、row 63まで表示された。B effectはなかった。
- Duty Instrument、Wave Instrument、Noise Instrument、Wave tableを表示でき、Routine 0～15は空だった。別名保存とRGBDS ASM Exportに成功した。
- `tools/compare_huge_asm.py`で曲名プレフィックスを正規化し、P0～P3の64行、Routine、Instrumentをラベル表記から分離して比較した。
- 以前のfull比較で確認されたWave Instrument lengthの`64→63`差異は、JSON仕様を0～63へ修正した後の再生成で解消した。
- Wave tableの未使用bank省略は表記上の差異であり、実データの再生不一致ではない。
- 生成UGEとhUGETracker再保存UGEは`cmp`終了コード0で完全一致した。
- hUGETracker標準ASM部分は意味的に一致し、再生動作に影響する不一致と比較不能はなかった。
- noneのGUI確認は完了した。Pocket Sweeper側のnone停止動作確認は別途未実施である。

range確認済み事実（2026-07-19）:

- `assets/bgm_v2_loop_range_generated.uge`をhUGETrackerで正常に開けた。
- CH1の最終pattern row 63にB02が表示され、CH2～CH4の同じrowにはB effectがなかった。
- JSONの`start_order`は1で、B effectは`start_order + 1`の02だった。
- 再生時はOrder 1→Order 2の後、Order 2を繰り返した。
- 生成UGEと再保存UGEは`cmp`終了コード0で完全一致した。
- ASM比較ではP0～P4、Routine 0～15、descriptor、Instrument、OrderMatrixが意味的に一致した。
- Wave tableの未使用bank省略は表記上の差異、loop metadataは標準Exportに存在しない独自拡張と分類した。
- 再生動作に影響する不一致と比較不能はなかった。

range確認に基づく推測・未確認事項:

- 今回の確認はfullと同じ比較手順・分類基準に基づく。noneのGUI、保存、再Export、再生確認は未実施である。

none確認済み事実（2026-07-19）:

- `assets/bgm_v2_loop_none_generated.uge`をhUGETrackerで正常に開け、Pattern、Order、Instrumentを表示できた。B effectは存在しなかった。
- 生成UGEとhUGETracker再保存UGEは`cmp`終了コード0で完全一致した。
- hUGETracker標準ASM部分は意味的に一致し、再生動作に影響する不一致と比較不能はなかった。
- generated側のP4がExport側でP0へ統合されたが、Pattern内容は同一であり、Pattern番号変更は表記上の差異だった。
- generated側のNoise Instrument個別ラベルがExport側で省略されたが、UGEデータは一致しており、hUGETracker Export仕様による表記上の差異だった。
- Wave table未使用bank省略は表記上の差異だった。
- Pocket Sweeper独自loop metadataのみがhUGETracker標準Exportに存在しない独自拡張だった。
- hUGETracker標準再生では曲末から先頭Orderへ戻った。noneによる停止は標準UGEでは表現されず、Pocket Sweeper独自loop metadataをゲーム側が解釈して実現する仕様である。

noneに関する推測・未確認事項:

- 今回はhUGETracker標準再生を確認したものであり、Pocket Sweeperのゲーム側none停止処理を実機・エミュレータで確認したものではない。

Wave Instrument length仕様変更（確認済み）:

- JSON、UGE生成、ASM生成で共通して0～63を許可し、64以上は入力エラーとする。
- hUGETracker互換性維持のため、64をPocket Sweeper独自値として扱わない。

## 関連仕様

楽曲定義JSONの詳細は [楽曲定義JSON仕様](json-format.md) を参照する。
