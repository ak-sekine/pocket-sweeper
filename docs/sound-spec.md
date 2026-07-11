[PROJECT.mdへ戻る](../PROJECT.md)

# サウンド仕様

## サウンド設計

- hUGEDriver本体は `src/hUGEDriver.asm`、hUGETracker用マクロとノートテーブルは `include/hUGE.inc` / `include/hUGE_note_table.inc` に配置する。
- hUGETrackerから出力したASMデータは `src/*.asm` として配置し、通常のRGBASMビルド対象へ含める。
- 曲データはROM ONLY方針を維持するため、当面は `ROM0` セクションへ配置する。
- `src/sound.asm` がAPU初期化、曲開始、毎フレーム更新を担当する。
- `Sound_Init` はNR52/NR50/NR51を初期化し、BGM再生中フラグとSFX再生状態をクリアする。
- `Sound_PlayTestBgm` はテストBGMの曲ディスクリプタをHLに設定して `hUGE_init` を呼び、再生中フラグを立てる。
- `Sound_Update` はBGM再生中のみ `hUGE_dosound` を呼び出し、その後にSFX管理処理を更新する。
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

本方針はCH2 / Pulse2およびCH4 / Noiseが効果音に使用される場合を対象とする。現行実装ではPulse1効果音がCH1を、Noise効果音がCH4を使用し、Pulse2効果音は未対応である。したがって、CH1を効果音へ割り当てた場合にもCH1 / CH3の骨格を保証する方針ではなく、CH1使用効果音は主旋律への影響が大きい重要な演出に限定する既存方針を維持する。CH2効果音の実装と、CH1を含む各ミュート状態の実機・エミュレータ検証は後続WBSで扱う。

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

### 初版BGM仕様

初版で使用するBGMは以下の3曲とする。

| BGM | 正本JSON | 用途 | 方針 |
| --- | --- | --- | --- |
| タイトルBGM | `assets/bgm_title.json` | タイトル画面 | 明るく短い2パターンのループとし、ゲーム開始前の期待感を出す。 |
| プレイ中BGM | `assets/bgm_game.json` | 通常プレイ中 | 長時間聴いても邪魔になりにくい、落ち着いた2パターンのループとする。 |
| クリアBGM | `assets/bgm_clear.json` | クリア時 | 短い達成感のあるフレーズとし、初版ではBGMデータとして作成する。 |

- BGMの正本はJSONとし、`assets/` 直下へ配置する。
- 初版ではPulse1 / Pulse2を使用し、Wave / Noiseは空patternとする。
- 効果音との競合を抑えるため、Pulse2は伴奏中心とし、一時的にミュートされても曲の輪郭が失われにくい構成にする。
- `tools/json_to_huge_asm.py` は `SECTION "...", ROMX` を出力するが、ROM ONLY構成でも `rgblink` が32KiB内のbanked sectionとして配置できるため、カートリッジタイプ変更は不要とする。
- 各JSONは `tools/json_to_huge_asm.py` でASMへ変換し、`tools/build_sound_test_rom.py` で確認用ROMを生成する。
- SameBoyでの再生確認後、問題があればJSONを修正して再生成する。
- クリアBGMをループさせるか、一度だけ再生して停止させるかは本体組み込み時に決める。

### BGM・効果音制作フロー

- BGM・効果音制作では、ChatGPTで楽曲定義JSONを作成し、PythonツールでhUGEDriver用データへ変換する運用を採用する。
- 楽曲の正本はJSONとする。
- hUGETracker上で最初から手作業で打ち込むのではなく、まずJSONで曲の構造を管理する。
- hUGETracker上で直接微調整することは基本方針としない。
- 再生確認で問題があった場合は、hUGETracker上で修正するのではなく、JSONを修正して再生成する。
- hUGETrackerは主に `.uge` 読み込み確認、仕様調査、必要時の手動確認に使う。
- hUGETrackerには `.uge` からASMを自動ExportするCLIが確認できないため、通常フローへ組み込まない。
- 楽曲定義JSONはChatGPTが作成・編集しやすい中間形式として扱い、`assets/` 直下に配置する。
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

1. ChatGPTで楽曲定義JSONを作成する。
2. JSONからhUGEDriver用RGBDS ASMを生成する。
3. 生成したASMからサウンド再生確認用テストROMを生成する。
4. SameBoyなどのGBエミュレータで再生確認する。
5. 問題があればJSONを修正して再生成する。
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


## 関連仕様

楽曲定義JSONの詳細は [楽曲定義JSON仕様](json-format.md) を参照する。
