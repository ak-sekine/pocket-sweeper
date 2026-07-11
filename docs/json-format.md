[PROJECT.mdへ戻る](../PROJECT.md)

# 楽曲定義JSON仕様

### 楽曲定義JSON仕様

- 楽曲定義JSONは `assets/` 直下に配置する。
- ファイル名は用途が分かる名前にする。
  - 例: `assets/bgm_title.json`
  - 例: `assets/bgm_game.json`
  - 例: `assets/se_cursor.json`
- JSONから生成した `.uge` も `assets/` 直下に配置する。
- `.uge` はhUGETrackerで再生確認・微調整するための生成物として扱う。
- `.uge` はひとまずGit管理対象とする。hUGETrackerで手修正した結果も確認・比較しやすくするためである。
- JSONは人間とChatGPTが読み書きしやすいことを優先する。
- 初版では高度な編集機能を目指さず、短いBGM・効果音の下書き生成を目的とする。
- hUGETrackerの全機能をJSONで表現する必要はない。
- `.uge` の詳細仕様が不明な箇所は、既存の `.uge` ファイルやhUGETracker出力を確認してから実装する。
- 不明点は推測で確定せず、TODOまたはWBSに残す。
- `.uge` 変換時に必要なら、JSON仕様を後から拡張してよい。

初版で扱うJSON項目:

- `version`: JSON仕様バージョン。
- `title`: 曲名または効果音名。
- `type`: `bgm` または `sfx`。
- `priority`: `type = "sfx"` の本番SFX用優先度。値が大きいほど高優先度とする。
- `tempo`: Song Version 6の `TicksPerRow` として保存する。
- `instruments`: 音色定義。音色番号、名前、種別、およびPulse/Noise向けの最小Instrument詳細を扱う。
- `order`: 再生するパターン順。
- `patterns`: パターン定義。
- `channels`: `pulse1`、`pulse2`、`wave`、`noise` の4チャンネル。
- 各ノート情報:
  - `note`: 音名。休符は `rest` とする。
  - `length`: 音の長さ。初版ではpattern row数として扱い、音符セルと空行へ展開する。
  - `instrument`: 使用する音色番号。
  - `effect`: 効果指定。未使用時は `null` とする。
  - `effect_param`: 効果パラメータ。未使用時は `null` とする。

Pulse Instrument詳細項目:

- `duty`: Pulse duty設定。0～3を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- `initial_volume`: 初期音量。0～15を指定する。未指定時は15を使う。
- `envelope_direction`: 音量エンベロープ方向。`"up"` または `"down"` を指定する。未指定時は `"down"` を使う。
- `envelope_sweep`: 音量エンベロープのsweep値。0～7を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- これらのInstrument詳細項目は、初版では `pulse1` / `pulse2` 用Instrumentのみ対応する。
- 不正な範囲や未対応チャンネルでの指定は、変換ツールでバリデーションエラーにする。

### Version 2のPulse Instrument共通項目

Version 2では、CH1 / Pulse1とCH2 / Pulse2が同じPulse Instrument共通項目を使用する。Version 1で扱っている項目の意味は変更せず、`length` と `length_enable` はVersion 2で追加する項目として扱う。Version 1入力時にはVersion 2専用項目を参照しない。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 使用可能チャンネル | 意味 |
| --- | --- | --- | --- | --- |
| `duty` | 整数、0～3 | Version 1のInstrument IDに応じた既存デフォルト | `pulse1` / `pulse2` | Pulse波形のduty設定。Version 1の意味を変更しない。 |
| `length` | 整数、0～63 | `0` | `pulse1` / `pulse2` | ハードウェアのsound length設定。 |
| `length_enable` | boolean | `false` | `pulse1` / `pulse2` | length counterを有効にするかどうか。 |
| `initial_volume` | 整数、0～15 | `15` | `pulse1` / `pulse2` | 音量エンベロープの初期音量。Version 1の意味を変更しない。 |
| `envelope_direction` | `"up"` または `"down"` | `"down"` | `pulse1` / `pulse2` | 音量エンベロープの方向。Version 1の意味を変更しない。 |
| `envelope_sweep` | 整数、0～7 | Version 1のInstrument IDに応じた既存デフォルト | `pulse1` / `pulse2` | 音量エンベロープの周期設定。Version 1の意味を変更しない。 |

Instrument側の `length` はGame Boyハードウェアのsound length設定であり、pattern内のnote側にある `length` とは別の項目である。note側の `length` はpattern row数を表し、Instrument側の `length` はハードウェアのsound length registerへ反映する値を表す。

hUGETrackerの初期Duty Instrumentは `SweepIncDec = stDown` であり、Version 2 JSONの `sweep_direction` 未指定時は対応する `"down"` とする。hUGETrackerの `stDown`、JSONの `"down"`、NR10 bit 3の1（周波数減算）は同じ方向を表す。

Pulse InstrumentのJSON項目を未指定にした場合は、可能な限りhUGETrackerの初期値を採用する。これはhUGETrackerで新規作成したInstrumentとJSONの初期状態を一致させ、JSONからUGEを経由してhUGETrackerで扱う場合の不要な差分を抑えるためである。Version 1から引き継ぐ `duty` と `envelope_sweep` のInstrument ID別デフォルトなど、既存JSONの意味に関わる値はVersion 1互換性方針を優先して維持する。`length = 0`、`length_enable = false`、`initial_volume = 15`、`envelope_direction = "down"` は、今回のVersion 2共通項目で採用する未指定時の値であり、length counterを無効、その他を標準的な初期状態として扱うためである。

JSONのデフォルト値は、hUGETrackerの初期値との互換性を優先して決定する。将来、hUGETrackerの初期値と異なるデフォルト値を採用する場合は、その理由をこの仕様書に明記する。

### CH1 / Pulse1専用項目

CH1 / Pulse1だけがハードウェアの周波数Sweep機能を持つため、次の項目は`channel = "pulse1"`でのみ使用可能とする。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 意味 |
| --- | --- | --- | --- |
| `sweep_time` | 整数、0～7 | `0` | CH1周波数スイープの周期設定。 |
| `sweep_direction` | `"up"` または `"down"` | `"down"` | CH1周波数スイープの方向。 |
| `sweep_shift` | 整数、0～7 | `0` | CH1周波数スイープのshift設定。 |

`sweep_direction` のJSON上の意味は、ハードウェアの周波数変化方向として定義する。`"up"` は周波数加算でNR10のbit 3を0、`"down"` は周波数減算でNR10のbit 3を1とする。既存のhUGETracker / hUGEDriver側では、hUGETrackerの `SweepIncDec` および変換ツールの `ST_UP = 0` / `ST_DOWN = 1` に対応する。hUGEDriverはInstrumentのSweep値をNR10へ書き込む。

### CH2 / Pulse2用Instrument

CH2 / Pulse2はPulse Instrument共通項目だけを使用する。`channel` は必ず `"pulse2"` とし、使用可能な項目は `duty`、`length`、`length_enable`、`initial_volume`、`envelope_direction`、`envelope_sweep` の6項目とする。CH2固有の新しいInstrument項目は追加しない。

CH2にはハードウェア上の周波数Sweep機能がないため、`sweep_time`、`sweep_direction`、`sweep_shift` は指定禁止とする。`channel = "pulse2"` のInstrumentでこれらが指定された場合は、無視せずバリデーションエラーとする。

FrequencyとTriggerはInstrument JSONの項目にしない。実際の周波数はpattern内の `note` から生成し、再生開始時のTriggerはASMまたはUGE生成側で設定する。

Version 2のPulse Instrumentでは、次の共通バリデーションを行う。

- `channel` は対象チャンネルに応じた値とし、CH2 / Pulse2用Instrumentでは `"pulse2"` とする。
- `duty` は整数で0～3の範囲とする。
- `length` は整数で0～63の範囲とする。
- `length_enable` はbooleanとする。
- `initial_volume` は整数で0～15の範囲とする。
- `envelope_direction` は `"up"` または `"down"` とする。
- `envelope_sweep` は整数で0～7の範囲とする。
- `sweep_time`、`sweep_direction`、`sweep_shift` は `channel = "pulse1"` でのみ指定可能とする。CH2 / Pulse2での指定は禁止する。
- 未対応チャンネルで指定された項目は無視せずエラーとする。
- 型が不正な場合はエラーとする。
- 未指定時は、上記で定めた項目ごとのデフォルト値を使用する。

Version 1の既存JSONでは、既存の項目の意味、デフォルト値、バリデーション規則を変更しない。今回整理した `length`、`length_enable`、`sweep_time`、`sweep_direction`、`sweep_shift` はVersion 2向けの項目として扱い、Version 1入力時には参照しない。

### Version 2のCH3 / Wave用Instrument

CH3 / Wave用Instrumentは、hUGETracker Song Version 6の `TInstrumentV3` におけるWave固有の役割をJSONで表現する。使用可能な項目は `waveform`、`output_level`、`length`、`length_enable` の4項目とする。Wave Instrument本体とWave tableの32サンプルデータは分離し、InstrumentにはWave tableへの参照だけを持たせる。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 意味 |
| --- | --- | --- | --- |
| `waveform` | 文字列。空文字列は禁止 | デフォルトなし。必須 | Wave table定義の一意な名前を参照する。 |
| `output_level` | `"mute"`、`"100%"`、`"50%"`、`"25%"` | `"100%"` | CH3のNR32出力レベル。 |
| `length` | 整数、0～255 | `0` | CH3のハードウェアsound length設定。 |
| `length_enable` | boolean | `false` | CH3のlength counterを有効にするかどうか。 |

`waveform` は配列位置や数値IDをJSONに直接記録せず、Wave table定義側の名前を参照する。hUGETrackerの `TInstrumentV3.Waveform` および既存のVersion 6生成処理では内部的に0始まりの数値を使用するため、変換時には名前をWave table側で定義された数値へ解決する。名前から数値への対応、数値IDの範囲、Wave tableの最大定義数は本節で確定する。

`waveform` はInstrument IDから暗黙に補完しない。hUGETrackerの新規Wave InstrumentにはWave bankの位置に応じた数値初期値があるが、JSONで名前参照を採用する以上、対応するWave table名が確定していない状態で推測した名前をデフォルトにしないためである。したがって、Version 2のWave Instrumentでは `waveform` を必須とする。

`output_level` は人間が読み書きしやすい文字列表現を採用する。hUGETrackerの `OutputLevel` は数値で保存されるが、JSONから内部数値へ単純に変換でき、次の値に対応する。

| JSON値 | hUGETracker / 内部値 | NR32値 | 意味 |
| --- | ---: | ---: | --- |
| `"mute"` | `0` | `$00` | 無音。DAC自体の有効・無効とは別である。 |
| `"100%"` | `1` | `$20` | 100%出力。 |
| `"50%"` | `2` | `$40` | 50%出力。 |
| `"25%"` | `3` | `$60` | 25%出力。 |

hUGETrackerのWave bank初期値は、`Length = 0`、`LengthEnabled = false`、`OutputLevel = 1` であるため、JSONの `output_level`、`length`、`length_enable` のデフォルトはそれぞれ `"100%"`、`0`、`false` とする。CH3のsound lengthはGame Boyハードウェアの8-bit設定であるため、Pulseの0～63とは異なり0～255を許容する。

Instrument側の `length` はCH3ハードウェアのsound length設定であり、pattern内のnote側にある `length` とは別の項目である。note側の `length` はpattern row数を表し、Instrument側の `length` はCH3のsound length registerへ反映する値を表す。

Frequency、Trigger、DAC enableはWave Instrument JSONの項目にしない。周波数はpattern内の `note` から生成し、TriggerはASMまたはUGE生成側で設定する。DAC enableはCH3再生時に再生処理側が管理する。hUGEDriverではWave tableをWave RAMへコピーする際にCH3を一時停止し、コピー後に有効化するため、これを人が調整する音色項目として公開しない。

hUGEDriverにはeffect 9によって再生中のWave tableを変更する処理があるが、これはInstrument本体の項目ではない。今回のWave Instrument仕様ではInstrumentの `waveform` を初期参照として扱い、pattern effectによる途中変更のJSON表現・バリデーションは別途effect仕様で扱う。現行JSONのeffectは未使用であるため、今回その機能を確定しない。

CH3 / Wave用Instrumentでは、次の項目を指定禁止とする。

- Pulse専用項目: `duty`、`initial_volume`、`envelope_direction`、`envelope_sweep`、`sweep_time`、`sweep_direction`、`sweep_shift`
- Noise専用項目: `noise_length`、`clock_shift`、`width_mode`、`divisor_code`
- `trigger`、`frequency`、Wave tableの32サンプルデータ

Version 2のCH3 / Wave用Instrumentでは、次のバリデーションを行う。

- `channel` は必ず `"wave"` とする。
- `waveform` は空でない文字列とし、Wave table定義に存在する名前を指定する。Wave tableの名前・数値対応表が未確定の間は、完全な存在確認の実装条件を後続WBSで確定する。
- `output_level` は `"mute"`、`"100%"`、`"50%"`、`"25%"` のいずれかとする。
- `length` は整数で0～255の範囲とする。
- `length_enable` はbooleanとする。
- Pulse専用項目、Noise専用項目、その他の未対応項目は無視せずエラーとする。
- 型不正はエラーとする。
- 未指定時は、`waveform`を除き上記のデフォルト値を使用する。`waveform`未指定はエラーとする。

Version 1の既存JSONでは、既存の項目の意味、デフォルト値、バリデーション規則を変更しない。今回の `waveform`、`output_level`、CH3用の `length`、`length_enable` はVersion 2向けの項目として扱い、Version 1入力時には参照しない。既存のVersion 1 JSONは書き換えない。

### Version 2のCH3 / Wave table定義

Version 2では、Wave tableをトップレベルの `wave_tables` 配列で定義する。Wave tableはWave Instrument本体から分離し、Wave Instrumentの `waveform` がこの配列内の `name` を参照する。Wave tableを使用しないJSONでは `wave_tables` を省略するか、空配列にできる。Version 1入力時には `wave_tables` を参照しない。

```json
{
  "version": 2,
  "title": "Wave Example",
  "type": "bgm",
  "wave_tables": [
    {
      "name": "bass_wave",
      "samples": [
        0, 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14, 15,
        15, 14, 13, 12, 11, 10, 9, 8,
        7, 6, 5, 4, 3, 2, 1, 0
      ]
    }
  ],
  "instruments": [
    {
      "id": 3,
      "name": "Wave Bass",
      "channel": "wave",
      "waveform": "bass_wave",
      "output_level": "50%",
      "length": 0,
      "length_enable": false
    }
  ]
}
```

#### `wave_tables` と `name`

- `wave_tables` は配列とする。
- 配列要素はWave tableオブジェクトとする。
- Wave tableの `name` は必須の文字列とし、空文字列を禁止する。
- `name` はJSON内で一意とする。大文字・小文字を区別する。
- `name` の前後に空白を許可しない。
- 命名規則は `^[a-z][a-z0-9_]*$` とする。先頭は英小文字、2文字目以降は英小文字・数字・アンダースコアを使用する。
- Wave Instrumentの `waveform` は `name` を参照する。数値IDや配列位置をJSONに明示しない。
- Wave tableを定義したがInstrumentから参照していない場合もエラーにしない。配列順どおり出力し、必要に応じた未参照警告は変換ツール実装時に決める。

#### `samples`

- `samples` は必須の配列とする。
- 要素数は必ず32とする。
- 各要素はbooleanではない整数で、0～15の範囲とする。
- 小数、文字列、boolean、null、負数、16以上はエラーとする。
- 配列の順序はWave RAM上の再生順と一致させる。
- JSONでは4bitサンプルを可読な整数配列で表現し、圧縮済み16byte配列、16進文字列、Base64、外部PCMファイル参照は使用しない。

Game BoyのWave RAMは16バイトで32個の4bitサンプルを保持し、各バイトの上位nibbleが先のサンプル、下位nibbleが後のサンプルになる。したがって、JSONの `[1, 2, 10, 15]` は内部のWave RAM形式では `0x12, 0xAF` となる。hUGETracker Version 6の`.uge`では各Wave tableを32個の `uint8` nibble値として保存し、hUGEDriver用ASM・実行時データでは隣接する2サンプルを1バイトへパックして出力する。

#### 内部Waveform番号と最大定義数

- `wave_tables` の配列順を内部Waveform番号へ対応させる。
- 配列先頭を内部番号0とし、以降を1ずつ増加させる。
- 使用可能な内部番号は0～15、最大定義数は16とする。
- 変換ツールがInstrumentの `waveform` 名を検索して内部番号へ解決する。JSON利用者は内部番号を直接指定しない。
- 配列順を変更すると内部番号は変わるが、Instrumentは名前参照のため、同じ名前と内容を維持する限りJSON上の参照意味は維持される。
- 同名Wave tableの重複を許可しないため、名前解決は一意になる。

これはhUGETracker Version 6のWave table固定数16、Wave index 0～15、およびhUGEDriverがWave indexから16バイト単位でWave RAMデータを選択する構造に合わせたものである。

#### 未使用Wave bankの補完

- JSON利用者は未使用Wave bankを明示的に記述しない。
- `.uge`の固定構造に必要な16個のWave bankは変換ツールが補完する。
- `wave_tables`に記述されたWave tableを配列先頭から内部index 0以降へ割り当て、利用者定義済みのindexはその内容を優先する。補完対象は利用者が定義していない残りのindexだけとし、利用者定義済みindexを標準Waveや全サンプル0で上書きしない。
- 未定義のindex 0～10は同じindexのhUGETracker初期値相当の標準Waveで補完し、未定義のindex 11～15は全サンプル0で補完する。
- 16個すべてを利用者定義した場合は、補完を行わない。
- 補完Wave bankはJSON上のInstrumentから参照されない。
- JSONに定義したWave tableと変換ツールが補完したWave bankは、`.uge`上では同じ固定配列に保存される。将来JSONへ逆変換する場合に補完値を自動的に利用者定義と区別する仕組みは、今回追加しない。

例えば3個を定義した場合は、index 0～2を利用者定義、index 3～10を同じindexの標準Wave、index 11～15を全サンプル0で補完する。

#### CH3 Instrumentとの参照整合性

- `channel = "wave"` のInstrumentは `waveform` を必須とする。
- `waveform` は `wave_tables` 内の一意な `name` を参照する。
- 参照先が存在しない場合、空文字列の場合、名前が重複している場合はエラーとする。
- `channel != "wave"` のInstrumentで `waveform` を指定した場合は、無視せずエラーとする。
- Wave tableの途中変更を表すpattern effectはInstrument参照とは別の仕様であり、今回のWave table定義では扱わない。

#### Wave tableのバリデーション

- `wave_tables` は省略可能だが、存在する場合は配列とする。
- 配列要素はオブジェクトとする。
- 要素数は0～16の範囲とする。空配列はWave table未使用として許可する。
- `name` は必須の文字列、空文字禁止、命名規則一致、前後空白禁止、重複禁止とする。
- `samples` は必須の配列で、要素数32、各要素はbooleanではない整数0～15とする。
- 要素不足、要素超過、型不正、範囲外はエラーとする。
- Wave tableオブジェクトの未知の項目は無視せずエラーとする。
- Wave Instrumentの `waveform` 参照先が存在しない場合はエラーとする。
- `channel != "wave"` のInstrumentにある `waveform` はエラーとする。
- Version 2でWave Instrumentを使用する場合、`wave_tables` を省略または空配列にはできない。

#### JSONで扱わない項目

Wave table定義には、出力レベル、sound length、length enable、Instrument ID、note、Frequency、Trigger、DAC enable、pattern effectによる途中Wave変更、手動内部番号、圧縮済みデータ、外部音声ファイル参照を含めない。これらはWave Instrument、pattern、変換処理、または将来のeffect仕様の責務とする。

Version 1のJSONでは `wave_tables` を参照せず、既存の未使用Wave bank出力方針を変更しない。今回のWave table定義はVersion 2専用であり、既存のVersion 1 JSONは書き換えない。

Noise Instrument詳細項目:

- `noise_length`: NR41のsound length。0～63を指定する。未指定時は0を使う。
- `initial_volume`: NR42の初期音量。Pulseと同じく0～15を指定する。未指定時は15を使う。
- `envelope_direction`: NR42の音量エンベロープ方向。Pulseと同じく `"up"` または `"down"` を指定する。未指定時は `"down"` を使う。
- `envelope_sweep`: NR42の音量エンベロープsweep値。Pulseと同じく0～7を指定する。未指定時は0を使う。
- `clock_shift`: NR43のclock shift。0～15を指定する。未指定時は4を使う。
- `width_mode`: NR43のLFSR幅。`"15bit"` または `"7bit"` を指定する。未指定時は `"15bit"` を使う。
- `divisor_code`: NR43のdivisor code。0～7を指定する。未指定時は0を使う。
- `length_enable`: NR44のlength enable。booleanを指定する。未指定時は `false` を使う。
- `trigger` はJSON項目にしない。SFX step出力時にNR44のtrigger bitを常に立てる。
- これらのNoise Instrument詳細項目は、初版では `noise` 用Instrumentのみ対応する。
- 不正な範囲、未対応文字列、未対応チャンネルでの指定は、`json_to_sfx_asm.py` 実装時にバリデーションエラーとする。

SFX priority:

- `priority` は `type = "sfx"` のJSONで使用する。
- `priority` は整数値とし、初版では1～5を使う。
- 値が大きいほど高優先度とする。
- `priority = 5`: 地雷爆発、ゲームオーバー。
- `priority = 4`: クリア。
- `priority = 3`: マス開封、旗設置、旗解除。
- `priority = 2`: 決定、キャンセル。
- `priority = 1`: カーソル移動。
- `type = "sfx"` で `priority` が未指定の場合、初版の本番SFX ASM生成ではバリデーションエラーとする。
- `type = "bgm"` では `priority` は使用しない。

JSON側の設計例:

```json
{
  "version": 1,
  "title": "Game Draft",
  "type": "bgm",
  "tempo": 6,
  "instruments": [
    { "id": 1, "name": "lead", "channel": "pulse1" },
    { "id": 2, "name": "bass", "channel": "pulse2" }
  ],
  "order": ["intro"],
  "patterns": {
    "intro": {
      "channels": {
        "pulse1": [
          { "note": "C4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "E4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "G4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "C5", "length": 4, "instrument": 1, "effect": null, "effect_param": null }
        ],
        "pulse2": [
          { "note": "C3", "length": 8, "instrument": 2, "effect": null, "effect_param": null },
          { "note": "G3", "length": 8, "instrument": 2, "effect": null, "effect_param": null }
        ],
        "wave": [],
        "noise": []
      }
    }
  }
}
```

### 4チャンネル対応へ向けた不足項目（調査結果）

必須
- CH3 Wave Instrument定義
- CH3 Wave table定義
- CH4をBGM利用するためのNoiseノート表現
- Instrument種別(type/channel)の整理

推奨
- CH1周波数スイープ
- Pulse length / length enable
- noteごとのvolume
- チャンネル別order
- ループ範囲指定
- Instrument使用可能チャンネルのバリデーション

将来対応
- 非null effect
- note cut / gate
- Instrument subpattern
- 曲中テンポ変更
- Routine
- Version 7対応

### .uge形式調査結果

調査対象:

- `/home/akihiro/gbdev/hello/assets/twinkle.uge`
- `/home/akihiro/gbdev/hello/src/music/bgm_twinkle.asm`
- hUGETracker公式ソース `src/song.pas`
- hUGETracker公式ソース `src/hugedatatypes.pas`

確認できたこと:

- `.uge` はテキスト形式ではなくバイナリ形式である。
- ローカルの `twinkle.uge` は先頭4バイトが `06 00 00 00` で、hUGETrackerのSong Version 6として読める構造である。
- hUGETracker公式ソースでは、現行の `TSong` はSong Version 7として定義され、Version 1～7を読み込んで現行形式へUpgradeする処理がある。
- `.uge` は曲全体をFreePascalのrecord構造に近い形で保存している。
- Song Version 7の主な構成要素は、`Version`、`Name`、`Artist`、`Comment`、`Instruments`、`Waves`、`TicksPerRow`、`TimerEnabled`、`TimerDivider`、`Patterns`、`OrderMatrix`、`Routines` である。
- `Patterns` はパターン番号と64行分のセルデータを持つ。セルには `Note`、`Instrument`、`Volume`、`EffectCode`、`EffectParams` が含まれる。
- `OrderMatrix` は4チャンネル分の配列で、各チャンネルが再生するパターン番号の並びを保持する。
- `Routines` は16個の文字列として保存される。
- ローカルの `twinkle.uge` には、音色名やデフォルト波形名がASCII文字列として含まれているが、ファイル全体はバイナリである。
- ローカルの `twinkle.uge` には `0x5A` が多数含まれており、後続のnote番号調査で、hUGETracker / hUGEDriver側の `NO_NOTE = 90` と対応することを確認した。

Song Versionの決定:

- 本プロジェクト初版では、hUGETracker 1.0.11の安定版で扱えるSong Version 6を対象とする。
- 初版 `tools/json_to_uge.py` が書き出す `.uge` は、Song Version 6を採用する。
- Version 7はGitHub公式リポジトリの最新ブランチ上では現行 `TSong` として確認できるが、現在使用中のhUGETracker v1.0.11配布バイナリには含まれていないため、初版採用は見送る。
- 使用中のhUGETracker実行版は `/mnt/c/Users/akihiro/OneDrive/tools/hUGETracker-1.0.11-windows/hUGETracker.exe` で、実行ファイル内の表示文字列からv1.0.11であることを確認した。
- GitHub Releasesでは、hUGETracker 1.0.11が最新Releaseで、Release commitは `0623f3f` と確認した。
- `0623f3f` 時点の公式ソースでは `UGE_FORMAT_VERSION = 6`、`TSong = TSongV6`、読み込み対応はVersion 1～6までである。
- GitHub最新ブランチ先頭は `aa259a4936b9b539131abf51cdc8486829d2bab4` で、`UGE_FORMAT_VERSION = 7`、`TSong = TSongV7`、Version 6をVersion 7へUpgradeする処理が追加されている。
- v1.0.11実行ファイル内の文字列には `TSongV1`、`TSongV2`、`TSongV3`、`TSongV4`、`TSongV6` が確認できる一方、`TSongV7` は確認できなかった。
- v1.0.11配布物の `Sample Songs` にはVersion 1～6の `.uge` が含まれ、Version 7のサンプルは確認できなかった。
- ローカルの `twinkle.uge` もVersion 6であり、Windows版hUGETrackerで作成・再生確認・RGBDS ASM Exportまで行った実績がある。
- 公式ソースではVersion 6を読み込んでVersion 7へUpgradeする処理があるため、Version 6は新しいhUGETracker系でも読み込み対象である。
- Release Notes、Issue、Pull Request上でVersion 7を正式Release済み仕様として説明している情報は確認できなかった。
- 以上から、Version 7は次期Release向けの開発ブランチ上の保存形式と判断し、現行の安定運用対象はVersion 6とする。

Version 6/7の比較:

| 項目 | Version 6 | Version 7 |
| --- | --- | --- |
| `TicksPerRow` | `Integer` 1つ | 4チャンネル分の `Integer` 配列 |
| チャンネル別tempo | 直接は持たない | 持てる |
| `TimerEnabled` / `TimerDivider` | 持つ | 持つ |
| `Patterns` | `TCellV2` 64行pattern | Version 6と同系統 |
| `OrderMatrix` | 4チャンネル分のorder配列 | Version 6と同系統 |
| 公式ソース上の扱い | 読み込み後Version 7へUpgrade | 現行 `TSong` として読み書き |
| 使用中のv1.0.11実行版 | 配布サンプルと運用実績あり | 対応未確認 |
| v1.0.11 Release source | `TSong = TSongV6` | 存在しない |
| 最新ブランチ source | 読み込み互換対象 | `TSong = TSongV7` |
| 初版ツール実装難度 | 低い | `TicksPerRow` 配列対応が必要 |

Version 6採用理由:

- 初版目的は短いBGM・効果音の下書き生成であり、チャンネル別tempoは不要である。
- `tempo` を単一の `TicksPerRow` に対応させられるため、JSON仕様と実装が単純になる。
- 使用中のhUGETracker v1.0.11配布物にVersion 6サンプルが含まれ、ローカルでもVersion 6の `twinkle.uge` を運用済みである。
- 使用中のv1.0.11実行版でVersion 7を読める根拠が確認できず、Version 7を書き出すと「新しいhUGETrackerで作成された曲」として開けない可能性がある。
- 公式ソースでVersion 6読み込みとVersion 7へのUpgrade経路が確認できるため、将来のhUGETrackerへ移行してもVersion 6資産は読み込める可能性が高い。
- Version 7は最新ブランチ上では確認できるが、現行安定Releaseには含まれていないため、本プロジェクト初版では対象外とする。
- 将来Version 7対応版を使う場合は、`.uge` 形式やJSONから `.uge` への変換処理の見直しが必要になる可能性がある。

`json_to_uge.py` 実装時の注意:

- 先頭のSong Versionはlittle-endianの4バイト整数として `6` を書き出す。
- Version 6の `TicksPerRow` は単一整数として書き出し、JSONの `tempo` を対応させる。
- Version 7形式の `TicksPerRow[0..3]` は初版では書き出さない。
- hUGETrackerで保存し直すと、保存したhUGETracker実行版の対応Song Versionへ更新される可能性があるため、生成直後の `.uge` とhUGETracker保存後の `.uge` は差分が出る前提で扱う。
- Version 7は初版スコープ外とし、WBS上の未完了タスクとしては管理しない。
- 将来Version 7へ移行する場合は、JSONの `tempo` を単一値のまま全チャンネルへ複製するか、チャンネル別tempoを表現できるようJSON仕様を拡張する。

JSON項目と `.uge` 側の対応:

| JSON項目 | `.uge`側の対応 | 備考 |
| --- | --- | --- |
| `version` | JSON仕様バージョン | `.uge` のSong Versionとは別物として扱う。 |
| `title` | `Name` | 曲名・効果音名として保存する。 |
| `type` | 直接対応なし | `bgm` / `sfx` は制作・出力運用上の区分として扱う。 |
| `tempo` | `TicksPerRow` | Version 6では単一値、Version 7では4チャンネル分の配列。初版では全チャンネル同値にする。 |
| `instruments` | `Instruments` | 初版ではsquare/pulse用の最低限の音色定義を中心に扱う。 |
| `order` | `OrderMatrix` | JSONのパターン順を4チャンネル分のorder配列へ変換する。 |
| `patterns` | `Patterns` | パターン名を内部パターン番号へ割り当てる。 |
| `channels.pulse1` | `OrderMatrix[0]` / CH1 pattern cells | 矩形波チャンネル1。 |
| `channels.pulse2` | `OrderMatrix[1]` / CH2 pattern cells | 矩形波チャンネル2。 |
| `channels.wave` | `OrderMatrix[2]` / CH3 pattern cells | 波形メモリチャンネル。初版では未使用または空にしてよい。 |
| `channels.noise` | `OrderMatrix[3]` / CH4 pattern cells | ノイズチャンネル。初版では未使用または空にしてよい。 |
| `note` | `TCell.Note` | 音名をhUGETrackerのnote番号へ変換する。休符はNo Note値へ変換する。 |
| `length` | 直接対応なし | 1セルに長さは無い。音符行と休符行へ展開して表現する。 |
| `instrument` | `TCell.Instrument` | 1～15の音色番号として扱う。 |
| `effect` | `TCell.EffectCode` | 初版では未指定または基本effectのみ扱う。 |
| `effect_param` | `TCell.EffectParams` | 1バイト値として扱う。nibble分割が必要なeffectは実装時に確認する。 |

note番号・休符値:

- hUGETracker v1.0.11の公式ソース `src/constants.pas` では、`LOWEST_NOTE = 0`、`C_3 = 0`、`HIGHEST_NOTE = 71`、`B_8 = 71`、`NO_NOTE = 90` と定義されている。
- `include/hUGE.inc` でも `C_3 = 0` から `B_8 = 71` まで同じ番号で定義され、`___ = 90`、`NO_NOTE = ___` と定義されている。
- hUGETracker上の音名表記は `C-3`、`C#3`、`D-3` のように、ナチュラル音では音名とオクターブの間に `-` を入れる。
- RGBDS Export ASMでは `C_3`、`C#3`、`D_3` のように、ナチュラル音は `_`、シャープ音は `#` を使う。
- ローカルの `twinkle.uge` とExport ASM `bgm_twinkle.asm` を照合し、ASM上の `C_4`、`G_4`、`A_4`、`___` が `.uge` 内でそれぞれ `12`、`19`、`21`、`90` として現れることを確認した。
- JSON側では、ChatGPTと人間が読み書きしやすい表記として、ナチュラル音は `C3`、`D3`、シャープ音は `C#3`、`D#3`、休符は `rest` を採用する。
- JSON側では `C-3` や `C_3` は採用しない。これらはhUGETracker UIまたはExport ASM側の表記として扱う。

note番号対応:

| JSON音名 | `.uge` `TCell.Note` |
| --- | --- |
| `C3`～`B3` | 0～11 |
| `C4`～`B4` | 12～23 |
| `C5`～`B5` | 24～35 |
| `C6`～`B6` | 36～47 |
| `C7`～`B7` | 48～59 |
| `C8`～`B8` | 60～71 |
| `rest` | 90 |

各オクターブ内の半音順:

| 音名 | オクターブ内オフセット |
| --- | --- |
| `C` | 0 |
| `C#` | 1 |
| `D` | 2 |
| `D#` | 3 |
| `E` | 4 |
| `F` | 5 |
| `F#` | 6 |
| `G` | 7 |
| `G#` | 8 |
| `A` | 9 |
| `A#` | 10 |
| `B` | 11 |

JSON音名から `.uge` note番号への変換方針:

- `rest` は `NO_NOTE = 90` へ変換する。
- 音名は `C3`～`B8` の範囲に限定する。
- シャープは `#` で表記する。フラット表記は初版では扱わない。
- 変換式は `note_number = (octave - 3) * 12 + semitone_offset` とする。
- 例: `C3 = 0`、`C#3 = 1`、`D3 = 2`、`C4 = 12`、`C5 = 24`、`B8 = 71`。
- 範囲外の音名、未対応表記、空文字はバリデーションエラーとする。
- JSONから行展開するとき、音を伸ばすために追加する空行は `rest` と同じ `NO_NOTE = 90` を使う。

note変換実装時の注意:

- hUGETracker UI表記の `C-4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- Export ASM表記の `C_4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- `C#3` のようなシャープ表記はJSON文字列として問題なく扱えるため、`Cs3` 形式は採用しない。
- `NO_NOTE = 90` はhUGETracker公式ソースとhUGEDriver用 `hUGE.inc` の双方で確認済みのため、休符値として使用する。
- ノイズチャンネルでは音名がノイズ周波数選択として扱われるため、BGM音程と同じ意味で鳴るとは限らない。初版では同じnote番号変換を使い、音色・聴こえ方はhUGETracker上で確認する。

effect code・effect parameter:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、`TCellV2` が `EffectCode: Integer` と `EffectParams: TEffectParams` を持つ。
- `TEffectParams` は `Value: Byte` としても、`Param1` / `Param2` の2つの4bit nibbleとしても扱える `bitpacked record` である。
- `.uge` Version 6では、pattern内の各セルに `TCellV2.EffectCode` と `TCellV2.EffectParams` が保存される。
- hUGEDriverのpattern rowは `NNNNNNNN, IIIIEEEE, XXXXYYYY` の3バイトで、`E` がeffect code、`X` / `Y` がeffect parameterの上位/下位nibbleである。
- RGBDS Export ASMでは `dn note,instrument,$EPP` の形で出力される。`E` はeffect code、`PP` は `EffectParams.Value` である。
- `include/hUGE.inc` の `dn` macroは、`$EPP` の上位nibbleをeffect code、下位1バイトをeffect parameterとしてdriver用3バイトへpackする。
- hUGEDriver上のeffect未使用は `000`、つまり `EffectCode = 0` かつ `EffectParams.Value = 0` である。
- `EffectCode = 0` でも `EffectParams.Value` が0以外の場合は `0xy` Arpeggioとして扱われるため、未使用effectとは区別する。

effect未使用時の値:

- effect未使用とは、`EffectCode = 0` かつ `EffectParam = 0` の場合である。
- `EffectCode = 0` でも `EffectParam` が0以外の場合は、Arpeggio `0xy` として扱われる。
- そのため、effect未使用判定は `EffectCode` だけでは判定できない。
- 初版 `tools/json_to_uge.py` では、JSONの `effect = null`、`effect_param = null` の場合のみ `EffectCode = 0`、`EffectParam = 0` を出力する。
- 初版では `effect` が `null` 以外の場合は未対応とし、バリデーションエラーとする方針を維持する。

effect code対応:

| code | hUGEDriver表記 | JSON側の予約表記 | 初版対応 |
| --- | --- | --- | --- |
| `0` | `0xy` Arpeggio | `arpeggio` | 未対応 |
| `1` | `1xy` Slide up | `slide_up` | 未対応 |
| `2` | `2xy` Slide down | `slide_down` | 未対応 |
| `3` | `3xy` Toneporta | `tone_portamento` | 未対応 |
| `4` | `4xy` Vibrato | `vibrato` | 未対応 |
| `5` | `5xy` Set master volume | `set_master_volume` | 未対応 |
| `6` | `6xy` Call routine | `call_routine` | 未対応 |
| `7` | `7xy` Note delay | `note_delay` | 未対応 |
| `8` | `8xy` Set panning | `set_panning` | 未対応 |
| `9` | `9xy` Set duty cycle | `set_duty_cycle` | 未対応 |
| `A` | `Axy` Volslide | `volume_slide` | 未対応 |
| `B` | `Bxy` Position jump | `position_jump` | 未対応 |
| `C` | `Cxy` Set volume | `set_volume` | 未対応 |
| `D` | `Dxy` Pattern break | `pattern_break` | 未対応 |
| `E` | `Exy` Note cut | `note_cut` | 未対応 |
| `F` | `Fxy` Set speed | `set_speed` | 未対応 |

effect parameterの扱い:

- `EffectParams.Value` は1バイト値 `0x00`～`0xFF` として扱う。
- hUGETracker / hUGEDriver上ではeffectによって `Param1` / `Param2` のnibble単位で意味を持つものと、1バイト値として意味を持つものがある。
- `0xy` Arpeggio、`5xy` Set master volume、`Axy` Volslide、`Cxy` Set volumeなどはnibble単位の意味があることを公式ソース `src/utils.pas` の説明文字列で確認した。
- `1xy` Slide up、`2xy` Slide down、`3xy` Toneporta、`6xy` Call routine、`7xy` Note delay、`Bxy` Position jump、`Dxy` Pattern break、`Exy` Note cut、`Fxy` Set speedなどは `EffectParams.Value` の1バイト値として扱うことを確認した。
- `4xy` Vibrato、`8xy` Set panning、`9xy` Set duty cycleはdriver-formatおよびhUGEDriverのjump table上に存在するが、パラメータの詳細説明は `src/utils.pas` の `EffectToExplanation` では確認できなかった。

JSON側で採用するeffect表記:

- effect未使用は `effect: null`、`effect_param: null` とする。
- 初版 `tools/json_to_uge.py` では、`effect: null`、`effect_param: null` のみを対応対象とする。
- 初版で `effect` に非null値が指定された場合は、将来の実装ではバリデーションエラーにする方針とする。
- 非null effectを将来対応する場合は、上記のJSON側予約表記を使う。
- 非null effect対応時の `effect_param` は、まず `0`～`255` の整数として扱う方針とする。nibble単位の指定が必要になった場合はJSON仕様を拡張する。

初版 `tools/json_to_uge.py` で対応するeffect:

- effect未使用のみ対応する。
- `effect: null`、`effect_param: null` を `.uge` の `EffectCode = 0`、`EffectParams.Value = 0` へ変換する。
- Export ASM上では `$000` として出力される状態を目標にする。

初版 `tools/json_to_uge.py` では対応しないeffect:

- `arpeggio`
- `slide_up`
- `slide_down`
- `tone_portamento`
- `vibrato`
- `set_master_volume`
- `call_routine`
- `note_delay`
- `set_panning`
- `set_duty_cycle`
- `volume_slide`
- `position_jump`
- `set_volume`
- `pattern_break`
- `note_cut`
- `set_speed`

effect変換実装時の注意:

- `EffectCode = 0`、`EffectParams.Value = 0` はeffect未使用だが、`EffectCode = 0`、`EffectParams.Value != 0` はArpeggioである。
- 未使用判定を `EffectCode == 0` のみで実装してはいけない。必ず `EffectCode == 0` かつ `EffectParams.Value == 0` で判定する。
- `effect_param` を扱う場合は、`TEffectParams.Param1` / `Param2` のbitpacked上の並びと、hUGEDriver document上の `X` / `Y` の対応をeffectごとに確認する。
- `5xy`、`8xy`、`Bxy`、`Dxy`、`Fxy` はhUGEDriver上でglobal effectとして扱われるため、BGM全体への影響を確認してから対応する。
- `6xy` Call routineはroutine定義と組み合わせる必要があるため、初版では扱わない。
- `9xy` Set duty cycleはチャンネルやinstrument状態との関係を確認してから対応する。
- 非null effectを追加する場合は、hUGETrackerで読み込み、再生、保存、ASM Exportした結果を必ず確認する。

Instrument構造:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、Version 6の `TInstrument` は `TInstrumentV3` である。
- `TInstrumentV3` はInstrument種別にかかわらず同じrecord構造を持ち、`Type_` によってSquare/Duty、Wave、Noiseとして扱う。
- `TInstrumentType` は `itSquare = 0`、`itWave = 1`、`itNoise = 2` である。
- `TInstrumentCollectionV3` は `Duty`、`Wave`、`Noise` の3 bankを持ち、各bankは `1..15` の15個である。`All[1..45]` としても参照できる。
- Instrument番号 `0` はhUGEDriver上で「Instrumentなし」として扱われるため、JSONで指定できるInstrument IDは `1`～`15` とする。

`TInstrumentV3` の主なメンバー:

| メンバー | 用途 |
| --- | --- |
| `Type_` | `itSquare` / `itWave` / `itNoise` の種別。 |
| `Name` | hUGETracker上のInstrument名。 |
| `Length` | 各チャンネルのlength registerへ反映される値。 |
| `LengthEnabled` | length counterを使うかどうか。 |
| `InitialVolume` | Square/Noiseの初期音量。 |
| `VolSweepDirection` | Square/Noiseのvolume envelope方向。 |
| `VolSweepAmount` | Square/Noiseのvolume envelope量。 |
| `SweepTime` | SquareのNR10 sweep time。 |
| `SweepIncDec` | SquareのNR10 sweep方向。 |
| `SweepShift` | SquareのNR10 sweep shift。 |
| `Duty` | Squareのduty比。 |
| `OutputLevel` | Waveの出力レベル。 |
| `Waveform` | Waveが参照する波形番号。 |
| `CounterStep` | Noiseの7bit/15bit counter設定。 |
| `SubpatternEnabled` | Instrument subpatternを使うかどうか。 |
| `Subpattern` | Instrument subpattern。64行の `TPattern`。 |

Version 6でのInstrument保存形式:

- `TSongV6` は固定長record部分に `Instruments: TInstrumentCollection` を含む。
- `WriteSongToStream` は `TSong` から `TPatternMap`、`TOrderMatrix`、`TRoutineBank` を除いた固定長部分を先に書き出すため、Instrumentは曲名、作者、コメントの後、Wave bankやtempoより前に保存される。
- 保存されるInstrumentはDuty 15個、Wave 15個、Noise 15個の合計45個である。
- `.uge` 内では `TInstrumentV3` recordとして保存される。ASM Export時のdriver用Instrumentは `.uge` 内のrecordそのものではなく、`InstrumentToBytes` でhUGEDriver用のバイト列へ変換される。
- hUGEDriver用ASMでは、Square/Wave/Noiseの各Instrument entryは実質6バイト単位で出力される。Square/Waveは4バイトのregister系値とsubpattern pointer、Noiseはenvelope、subpattern pointer、highmask/length相当、paddingで構成される。
- `src/song.pas` は保存時に `SizeOf(TSong)` や `SizeOf(TInstrumentV3)` を使う。Pythonで実装する場合は手計算したサイズだけに依存せず、hUGETrackerが保存した `.uge` と照合する。
- この環境ではFreePascalコンパイラが無く、`SizeOf(TInstrumentV3)` の数値を実行確認できなかった。実装時は実ファイルとの照合で確定する。

hUGETracker新規作成時のInstrument初期値:

- `InitializeSong` は全Instrumentを `Default(TInstrument)` で初期化し、全Instrumentの `Subpattern` を `BlankPattern` で空パターン化する。
- Duty bankは全15個に `Type_ = itSquare`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`SweepTime = 0`、`SweepIncDec = stDown`、`SweepShift = 0`、`Duty = 2`、`OutputLevel = 1` を設定する。
- Wave bankは全15個に `Type_ = itWave`、`Length = 0`、`LengthEnabled = False`、`OutputLevel = 1`、`Waveform = I - 1` を設定する。
- Noise bankは全15個に `Type_ = itNoise`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen` を設定する。
- `LoadDefaultInstruments` はDuty 1～8に名前とduty比を設定し、Duty 5～8には `VolSweepAmount = 1` を設定する。
- `LoadDefaultInstruments` はWave 1～11にデフォルト波形名を設定し、`DefaultWaves` を `Waves[0..10]` へ設定する。
- ローカルの `twinkle.uge` には `Lead 12.5%`、`Base 25%`、`Coin 50%`、`Laser75%`、`Duty 25% plink`、`Square wave 12.5%` などのInstrument名文字列が含まれることを確認した。

Instrumentの最小構成:

- 再生に必要な最小構成は、使用するbankのInstrument `Type_`、鳴る音量設定、長さ設定、subpattern無効状態、空のsubpatternである。
- Square/Dutyを鳴らすには、少なくとも `Type_ = itSquare`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`Duty`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- Waveを鳴らすには、`Type_ = itWave`、`OutputLevel = 1`、`Waveform`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。`OutputLevel = 0` は無音になるため避ける。
- Noiseを鳴らすには、`Type_ = itNoise`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- `Default(TInstrument)` のままではSquare/Noiseの `InitialVolume` が0になり、無音になるため、0初期化だけでInstrumentを生成してはいけない。
- `Subpattern` は未使用でもrecord上は存在するため、`BlankPattern` 相当で全セルを `NO_NOTE` にした空パターンとして保存する。
- Wave/Noiseを初版で未使用にする場合でも、`.uge` Version 6の固定record構造として15個ずつ保存する必要がある。

JSON項目とInstrumentの対応:

| JSON項目 | `.uge`側の対応 | 初版方針 |
| --- | --- | --- |
| `id` | bank内のInstrument番号 `1..15` | 1～15のみ許可する。 |
| `name` | `TInstrument.Name` | 指定された名前を保存する。未指定ならデフォルト名を使う。 |
| `channel` | `Duty` / `Wave` / `Noise` bank選択 | `pulse1` / `pulse2` はDuty、`wave` はWave、`noise` はNoiseへ割り当てる。 |
| 詳細音色パラメータ | `Duty`、`InitialVolume`、`VolSweepDirection`、`VolSweepAmount` など | Pulse向けに `duty`、`initial_volume`、`envelope_direction`、`envelope_sweep` を扱う。 |

- 初版では、JSONの `id`、`name`、`channel` と、任意のPulse Instrument詳細からInstrumentを生成する。
- `pulse1` と `pulse2` はどちらも同じDuty bankのInstrument番号を参照する。
- JSONの `channel` は主にどのbankへInstrumentを配置するかを決めるための情報であり、pattern cell側では `TCell.Instrument` に `id` を入れる。
- 同じ `id` を異なるbankで使うことは可能だが、同じbank内で重複した `id` はバリデーションエラーとする。
- Pulse Instrument詳細が未指定の場合は、従来どおりhUGETracker初期値またはデフォルトInstrument相当を使う。

初版 `tools/json_to_uge.py` のInstrument方針:

- Pulse向けInstrumentを主対象とし、`pulse1` / `pulse2` はDuty bankへ出力する。
- Duty bank、Wave bank、Noise bankは常に15個ずつ生成する。
- 使用されていないInstrumentもhUGETrackerの初期値相当で出力する。
- Duty 1～8は `LoadDefaultInstruments` 相当の名前、duty比、volume envelopeを使う。JSONでPulse Instrument詳細が指定されたInstrumentは、その値で上書きする。
- Wave/Noiseは初版では詳細編集を行わず、hUGETracker初期値相当の固定値で生成する。
- `SubpatternEnabled` は全Instrumentで `False` とし、`Subpattern` は空パターンにする。
- `tools/json_to_huge_asm.py` はPulse Instrument詳細をhUGEDriver ASMのduty instrument entryへ反映する。
- `tools/json_to_uge.py` はPulse Instrument詳細をSong Version 6のDuty bank Instrumentへ反映する。

Instrument実装時の注意:

- Instrument ID `0` は「Instrumentなし」なのでJSONでは禁止する。
- `InitialVolume = 0` のSquare/Noise、`OutputLevel = 0` のWaveは無音になるため、デフォルト値を必ず設定する。
- Instrumentのrecordサイズ、`ShortString`、enum、Boolean、subrange型の保存サイズはFreePascalのバイナリ表現に合わせる必要がある。
- Python実装時は、公式ソースのfield順に従って書き出し、hUGETrackerで保存した `.uge` との比較でoffsetとサイズを確認する。
- `.uge` 内のInstrument recordと、ASM Export後のhUGEDriver用Instrumentバイト列は同一ではない。`.uge` 生成では `TInstrumentV3` を書き、ASM出力はhUGETrackerに任せる。
- Wave bankを使わない場合でも、`Waves` とWave InstrumentはVersion 6の固定構造として保存する。

wave/noise未使用時の扱い:

- 初版では、`wave` / `noise` チャンネルを省略するのではなく、空patternを再生する未使用チャンネルとして扱う。
- hUGETracker v1.0.11の `InitializeSong` は4チャンネルすべての `OrderMatrix` を長さ2に初期化し、各チャンネルの先頭にpattern番号を設定する。
- hUGETrackerのExport処理は `OrderMatrix[I]` の `High(...)-1` までを有効orderとして扱う実装になっているため、空配列ではなく、少なくとも長さ2のOrderMatrixを持たせる方針にする。
- `WriteSongToStream` はOrderMatrixの長さを書いた後、`OrderMatrix[i][0]` から内容を書き出すため、長さ0のOrderMatrixは避ける。
- `wave` / `noise` を未使用にする場合も、pulse側と同じorder数にそろえ、各orderで空patternを参照させる。
- 空patternは `BlankPattern` 相当とし、64行すべて `Note = NO_NOTE`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` にする。
- `Instrument = 0` はhUGEDriverで「Instrumentなし」として扱われるため、空pattern内ではWave/Noise Instrumentを参照しない。

確認できたこと:

- hUGETracker公式ソース `src/utils.pas` の `BlankPattern` は、全セルを `Default(TCell)` にした上で `Note = NO_NOTE` を設定する。
- hUGETracker公式ソース `src/hugedatatypes.pas` の `TPatternMap.GetOrCreateNew` は、存在しないpattern番号を参照した場合に `BlankPattern` で空patternを作成する。
- hUGETracker公式ソース `src/codegen.pas` の `FindUsedStuff` は、Wave/Noise channelのpattern内で `Instrument = 0` のセルをInstrument未使用として扱い、Wave/Noise Instrumentの使用数を増やさない。
- hUGETracker公式ソース `src/codegen.pas` の `RenderInstruments` は、使用上限が `-1` のbankではInstrument entryを出力しない。
- ローカルの `bgm_twinkle.uge` はhUGETracker v1.0.11で作成・保存・RGBDS ASM Export済みのVersion 6ファイルであり、Export ASM `bgm_twinkle.asm` ではCH3に対応する `bgm_twinkle_P2` が64行すべて `dn ___,0,$000` の空patternとして出力されている。
- 現在の `src/bgm_test.asm` では、CH3/CH4に対応する `TestBgmPattern3` / `TestBgmPattern4` を64行すべて `dn ___, 0, $000` とし、`TestBgmWaveInstruments` / `TestBgmNoiseInstruments` は空sectionとして扱っている。

OrderMatrixの扱い:

- 初版 `tools/json_to_uge.py` では、4チャンネルすべてにOrderMatrixを出力する。
- `wave` / `noise` が未使用の場合でも、OrderMatrix自体は省略しない。
- `wave` / `noise` の各orderは、空pattern番号を参照させる。
- hUGETrackerの初期化・Export処理に合わせ、OrderMatrixは長さ0にしない。
- pulse側に複数orderがある場合、`wave` / `noise` も同じorder数分だけ空patternを並べる。

Patternの扱い:

- 空patternは64行固定で出力する。
- 各行は `NO_NOTE = 90`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` とする。
- Export ASM上では `dn ___,0,$000` が64行並ぶpatternとして見える。
- hUGETrackerの `OptimizeSong` は同一内容のpatternをまとめるため、Wave/Noise用の空patternがExport時に1つへ統合される可能性がある。

Instrumentの扱い:

- `wave` / `noise` が未使用でも、`.uge` Version 6の固定構造としてWave bank 15個、Noise bank 15個は保存する。
- 未使用channelのpattern cellでは `Instrument = 0` とするため、Wave/Noise Instrumentは参照されない。
- Wave/Noise InstrumentはhUGETracker初期値相当の固定値で出力する。
- Export ASMでは、Wave/Noise Instrumentが参照されていない場合、`wave_instruments:` / `noise_instruments:` ラベルは出るが、その配下にInstrument entryは出力されない。

Export ASM上の見え方:

- order tableには `order3` / `order4` も出力される。
- `wave` / `noise` 未使用channelのorderは空patternを参照する。
- 空patternは `dn ___,0,$000` のみで構成される。
- Wave/Noise Instrumentが参照されない場合、`wave_instruments:` / `noise_instruments:` は空になる。

初版 `tools/json_to_uge.py` でのwave/noise出力方針:

- JSONの `channels.wave` または `channels.noise` が空配列、または未指定相当の場合は、そのチャンネルを未使用として扱う。
- 未使用channelには空OrderMatrixではなく、空pattern参照を持つ最小構成のOrderMatrixを書き出す。
- 空patternは全セル `NO_NOTE` / `Instrument = 0` / effect未使用で書き出す。
- Wave/Noise Instrument bankは常に15個ずつhUGETracker初期値相当で書き出す。
- Wave bank用の `Waves` もVersion 6の固定構造として保存する。
- 初版ではWave/Noiseの詳細編集は行わず、未使用または空patternのみを基本とする。

wave/noise未使用実装時の注意:

- OrderMatrixを長さ0にしない。
- Wave/Noise用のpattern番号が `Patterns` に存在するようにする。
- 空patternには `Instrument = 0` を使い、未使用Instrument番号を誤って参照しない。
- Wave/Noiseを未使用にしても、`.uge` の固定record領域からWave/Noise InstrumentやWave bankを削らない。
- hUGETrackerの直接GUI操作による最小 `.uge` の新規作成・再保存は今回実施していない。生成 `.uge` の読み込み・保存・ASM Export確認は、後続WBS「生成した `.uge` をhUGETrackerで読み込み・保存・ASM Exportできることを確認する」で実施する。

初版 `tools/json_to_uge.py` で対応する範囲:

- `.uge` バイナリを書き出す。
- Song VersionはVersion 6を書き出す。
- `title` を曲名として保存する。
- `tempo` を全チャンネル共通のticks-per-rowとして保存する。
- 最大64行の短いパターンを生成する。
- `pulse1` / `pulse2` を中心に、note、instrument、effect、effect_paramをセルへ変換する。
- `wave` / `noise` は空パターンまたは限定対応から始める。
- `length` は音符セルと休符セルへ展開する。
- 未使用のinstrument、wave、routineはhUGETrackerの初期値または空値に近い状態で出力する。

初版 `tools/json_to_uge.py` では対応しない範囲:

- hUGETrackerの全effect対応。
- instrument subpattern、routine、wave tableの詳細編集。
- チャンネルごとに異なるtempo。
- 高度なpattern再利用最適化。
- hUGETracker上の全GUI設定の再現。
- 既存 `.uge` の読み込み・差分マージ。

実装時の注意点:

- `.uge` はバイナリ形式のため、文字列連結ではなく `struct` などで明示的にバイト列を書き出す。
- FreePascalの `Integer` サイズ、booleanサイズ、`ShortString` の保存形式、packed recordのアラインメントを公式ソースと実ファイルで照合する。
- 初版対象はSong Version 6に固定し、`TicksPerRow` は単一整数として実装する。
- hUGETrackerが読む順序は、固定長領域、pattern数、pattern keyとpattern本体、4チャンネル分のorder配列、routine文字列の順である。
- pattern cellは64行固定として扱う。
- `length` は `.uge` に直接保存されないため、行展開後に64行を超えないようバリデーションする。
- 出力した `.uge` はhUGETrackerで開けることを必ず確認する。

未確定事項・TODO:

- 非null effectを実装対象に追加する場合、各effectのチャンネル制約、tick上の挙動、parameterの意味を個別に確認する。

### JSON仕様のバージョン更新方針

- 楽曲定義JSONの `version` は、JSON仕様の世代を表す整数とする。
- 現行仕様は `version: 1` とする。
- バージョン番号は `1`、`2`、`3` のように1ずつ増加させる。
- 小数やセマンティックバージョニング形式は使用しない。
- JSONの構造、必須項目、項目の型、項目の意味など、変換ツールの解釈に影響する変更を行う場合はバージョンを更新する。
- 既存JSONを同じ意味で解釈できなくなる変更は、必ず新しいバージョンとして扱う。
- 誤字修正、説明の整理、実装内部の変更など、JSONの解釈結果に影響しない変更ではバージョンを更新しない。
- 変換ツールは、対応していないバージョンを推測で処理せず、分かりやすいエラーを出す。
- バージョンを更新する場合は、JSON仕様書、サンプルJSON、関連する変換ツールを同じ作業単位で更新する。
- 新しい任意項目の追加を同一バージョン内の拡張として扱うか、新しいバージョンとして扱うかは、既存JSONとの後方互換性方針と合わせて決定する。

### 既存JSONとの後方互換性方針

- 既存の楽曲定義JSONとの後方互換性を維持する。
- 現行JSON仕様は引き続き `version: 1` として扱う。
- 4チャンネル対応など、今後拡張するJSON仕様は `version: 2` とする。Version 2の具体的なJSON構造は別途確定する。
- 関連するJSON変換ツールは、当面 `version: 1` と `version: 2` の両方を明示的に処理する。
- `version: 1` のJSONは、現在と同じ項目の意味、デフォルト値、バリデーション規則を維持する。
- Version 2対応のために、Version 1の項目の意味を変更しない。
- Version 1に存在しないVersion 2項目は、Version 1入力時には参照しない。
- Version 1からVersion 2への自動変換機能は現時点では必須としない。
- Version 2からVersion 1へのダウングレード機能は作成しない。
- 既存のVersion 1 JSONを一括してVersion 2へ書き換えることは必須としない。
- Version 2仕様確定後に新規作成するJSONは、原則としてVersion 2を使用する。
- 未対応のversionは推測で読み込まず、分かりやすいエラーとする。
- 将来Version 1対応を廃止する場合は、別途WBSを追加して判断する。

後方互換性は、Version 2対応後の変換ツールへ既存のVersion 1 JSONを入力した場合に、以下を満たすことと定義する。

- Version 1 JSONがエラーにならず読み込める。
- 各項目が従来と同じ意味で解釈される。
- Instrument、音符、テンポ、パターン順、効果音priorityなどが従来と同じ意味になる。
- 生成されるASMまたはUGEの再生結果が実質的に同等になる。
- ラベル順、コメント、未使用データの配置など、再生に影響しない差分は許容する。
- バイト単位またはテキスト単位での完全一致は必須としない。


## 関連仕様

サウンド全体の再生・実装方針は [サウンド仕様](sound-spec.md) を参照する。
