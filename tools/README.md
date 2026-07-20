# 開発ツール

このディレクトリには、ゲーム本体(RGBDS)とは独立した開発支援ツールを配置します。

例:

* フォント画像生成
* タイル画像変換
* マップデータ変換
* 各種アセット生成
* その他の開発補助ツール

---

# 開発環境

Pythonツールはプロジェクトルートに作成した仮想環境 (`.venv`) を使用します。

## 初回セットアップ

### 1. Python環境を準備

Ubuntuの場合

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. 仮想環境を作成

プロジェクトルートで実行します。

```bash
python3 -m venv .venv
```

### 3. 仮想環境を有効化

```bash
source .venv/bin/activate
```

有効化されるとプロンプトの先頭に

```text
(.venv)
```

が表示されます。

### 4. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

---

# 仮想環境の有効化

開発を再開するときは、プロジェクトルートで以下を実行してください。

```bash
source .venv/bin/activate
```

終了する場合は

```bash
deactivate
```

を実行します。

---

# フォント画像生成

Nuきなこもちフォントから `assets/font.png` を生成します。

```bash
python tools/generate_font_png.py
```

入力ファイル

```text
assets/NuKinakoMochi-Reg.otf
```

出力ファイル

```text
assets/font.png
```

---

# BG画像タイル変換

Indexed Color PNGを8×8タイルへ分割し、重複タイルを削除したタイルセットPNGと、1タイル1バイトのBGマップファイルを生成します。

```bash
python tools/convert_bg_image.py assets/title.png obj/title_tiles.png obj/title_map.bin
```

入力画像の条件:

* Indexed Color PNG
* 使用パレットインデックスは0〜3の4色
* アルファチャンネルなし
* 幅と高さが8の倍数
* 重複削除後のタイル数が256以下

出力ファイル:

```text
obj/title_tiles.png
obj/title_map.bin
```

`obj/title_map.bin` は元画像を左上から右下へ8×8タイル単位で走査したタイル番号列です。

---

# 楽曲定義JSONからuge生成

ChatGPTで作成した楽曲定義JSONから、hUGETracker v1.0.11向けのSong Version 6 `.uge` ファイルを生成します。

```bash
python tools/json_to_uge.py assets/test_draft.json assets/test_draft.uge
```

入力JSON:

```text
assets/test_draft.json
```

出力ファイル:

```text
assets/test_draft.uge
```

Version 1では、従来形式のJSONを引き続き変換できます。共通の`order`配列でpattern順を指定し、各patternの`channels`内に
`pulse1`、`pulse2`、`wave`、`noise`のセル列を記述します。noteは`C3`〜`B8`と`rest`、`length`は64行固定patternへ展開されます。
Version 1ではVersion 2専用のチャンネル別`order` / `patterns`構造、`loop`、Pulse Instrumentの`length` / `length_enable` / Pulse1専用sweep項目（`sweep_time`、`sweep_direction`、`sweep_shift`）、Wave Instrument、Wave table参照、Noise Instrument、Noise note、note `volume`などは使用できません。
effectは`effect: null`、`effect_param: null`のみ対応します。

Version 1の主な対応範囲:

* `version`, `title`, `type`, `tempo`, `instruments`、共通`order`、`patterns.<name>.channels`を読み込む
* 未使用チャンネルには空patternを出力する
* Instrument IDは1〜15を使用する
* Pulse Instrumentの`duty`, `initial_volume`, `envelope_direction`, `envelope_sweep`を任意指定できる

Pulse Instrument詳細:

```json
{
  "id": 5,
  "name": "cursor_tick",
  "channel": "pulse1",
  "duty": 0,
  "initial_volume": 3,
  "envelope_direction": "down",
  "envelope_sweep": 1
}
```

* `duty`: 0〜3
* `initial_volume`: 0〜15
* `envelope_direction`: `"up"` または `"down"`
* `envelope_sweep`: 0〜7
* 未指定項目は従来のデフォルトInstrument相当の値を使う

Version 2では、4チャンネルを独立した構造として扱います。`order`と`patterns`は
`pulse1`、`pulse2`、`wave`、`noise`ごとに指定します。未使用チャンネルには空pattern参照を補完し、使用チャンネル間のorder数は一致していなければなりません。同じpattern名を異なるチャンネルで使用することもできます。

Version 2の主な対応範囲:

* Pulse Instrument（`duty`、音量envelope、`length`、`length_enable`、CH1専用sweep）
* Wave InstrumentとWave table
* Noise Instrument（音量envelope、`length`、`length_enable`、`width_mode`）
* CH4 / Noise noteの音名からNR43のNoise poly値を生成する処理
* `loop.mode`の`full`、`range`、`none`
* `range`の`start_order` / `end_order`境界とorder数に関する制約。SFXでは`none`以外のloopを使用できない
* note単位の`volume`。省略または`null`はvolume commandなし、`0`は明示的な0、`1`〜`15`は指定値としてCxyへ変換する
* CH1〜CH4のvolume command出力。CH1 / CH2 / CH3は`C0y`、CH4はNoise Instrumentのenvelope direction / sweepを上位nibbleへ反映した`Cxy`
* `length`展開で生成される後続の空行とpattern末尾の補完行にはvolume commandや再triggerを出力しない
* 上記の変換結果をUGEとhUGEDriver用ASMの両方へ出力する

詳細なJSON項目、既定値、境界、CH4のNR43とCxyの規則は[`docs/json-format.md`](../docs/json-format.md)を参照してください。

未対応またはこのツールの対象外:

* 非nullの汎用effect
* Routine編集、Instrument subpattern編集
* 64行を超える単一pattern
* hUGETracker GUIでの読み込み・保存・ASM Exportそのもの

---

# 楽曲定義JSONからhUGEDriver ASM生成

ChatGPTで作成した楽曲定義JSONから、hUGEDriver用のRGBDS ASMを直接生成します。

```bash
python tools/json_to_huge_asm.py assets/test_draft.json obj/test_draft.asm
```

入力JSON:

```text
assets/test_draft.json
```

出力ファイル:

```text
obj/test_draft.asm
```

Version 1 / Version 2のJSON構造に対応し、hUGETracker Export ASMに近いsong descriptor、order、pattern、Instrument、routine、wave構造を出力します。song descriptorのラベル名は出力ASMファイル名から生成します。

Version 1では従来の共通orderと`patterns.<name>.channels`を読み込み、noteを`C_4`、`C#4`、`___`へ変換し、通常行を`$000` effectで出力します。Version 2では、UGE生成と同じチャンネル別order / pattern、Pulse / Wave / Noise Instrument、Wave table、CH4 Noise noteのNR43生成、`full` / `range` / `none`のloop、note volumeのCxyを出力します。volume省略または`null`はeffectなし、CH1〜CH3の指定volumeは`C0y`、CH4はNoise Instrumentのenvelope情報を含む`Cxy`です。length展開後の空行にはCxyや再triggerを出力しません。

Version 2の対応内容はUGE生成と共通です。詳細は[`docs/json-format.md`](../docs/json-format.md)を参照してください。

未対応またはこのツールの対象外:

* 非nullの汎用effect
* Routine編集、Instrument subpattern編集
* 64行を超える単一pattern
* hUGETracker Export ASMとの完全一致を自動保証すること
* サウンド再生確認用テストROMの生成（専用ツール[`build_sound_test_rom.py`](build_sound_test_rom.py)を使用する）

---

# 効果音JSONから本体ROM向けSFX ASM生成

効果音JSONから、APUレジスタ直接制御用のSFX ASMを生成します。

```bash
python tools/json_to_sfx_asm.py assets/se_cursor.json obj/se_cursor_sfx.asm
```

入力JSON:

```text
assets/se_cursor.json
```

出力ファイル:

```text
obj/se_cursor_sfx.asm
```

入力JSONの条件:

* `version = 1`
* `type = "sfx"`
* `priority` は必須で、1〜5の整数
* 初版では `pulse1` または `noise` の単一チャンネルのみ対応
* `pulse2`, `wave`, 複数チャンネル同時SFXは未対応
* `length` は1以上
* `effect` / `effect_param` は `null` のみ対応

出力ASMの概要:

* `SFX_<NAME> EQU 0` 形式の効果音ID定数
* `SFX_CH_PULSE1`, `SFX_CH_NOISE` のchannel kind定数
* `SfxTable` ポインタテーブル
* ヘッダ `channel kind, priority, step count, total frames`
* Pulse1 step: `wait_frames, NR10, NR11, NR12, NR13, NR14`
* Noise step: `wait_frames, NR41, NR42, NR43, NR44`

初版では未対応:

* 複数ファイルをまとめたSFXテーブル生成
* `pulse2`, `wave`
* 複数チャンネル同時SFX
* 非null effect

---

# サウンド確認用テストROM生成

hUGEDriver用RGBDS ASMから、サウンド確認専用の最小Game Boy ROMを生成します。

```bash
python tools/build_sound_test_rom.py obj/test_draft.asm build/test_sound.gb
```

入力ASM:

```text
obj/test_draft.asm
```

出力ファイル:

```text
build/test_sound.gb
```

中間ファイル:

```text
obj/test_sound_sound_test.asm
obj/test_sound_sound_test.o
obj/test_sound_hUGEDriver.o
obj/test_sound.map
obj/test_sound.sym
```

処理内容:

* 入力ASMからsong descriptorラベルを読み取る
* 入力ASMをincludeする最小ROM用ASMを `obj/` に生成する
* hUGEDriverを組み込む
* 起動後に指定曲を自動再生する
* `rgbasm`, `rgblink`, `rgbfix` を呼び出してROMを生成する

このツールはROM生成のみを担当します。SameBoyなどのエミュレータ起動は行いません。

---

# requirements.txt

Pythonライブラリはプロジェクトルートの

```text
requirements.txt
```

で管理します。

ライブラリを追加した場合は

```bash
pip freeze > requirements.txt
```

ではなく、必要なライブラリのみを手動で管理してください。

例

```text
Pillow
```

---

# 開発方針

## CH2ミュート確認用ROM

既存の4チャンネル曲を使い、hUGEDriverのチャンネルミュートAPIでCH2（Pulse2）だけを切り替えるROMを生成する。

```bash
python tools/json_to_huge_asm.py assets/bgm_v2_ch1_ch3_skeleton_test.json obj/bgm_v2_ch1_ch3_skeleton_test.asm
python tools/build_sound_test_rom.py --ch2-mute-toggle obj/bgm_v2_ch1_ch3_skeleton_test.asm build/bgm_v2_ch1_ch3_skeleton_test_ch2_mute.gb
```

起動後に `ALL CHANNELS` が表示されることを確認する。Nintendoロゴ画面が残る場合は不具合である。Aボタンで `CH2 MUTED`、Bボタンで `ALL CHANNELS` に戻る。状態表示を確認してから聴感確認を行う。ボタン群だけを選択し、押下エッジを検出するため、方向キーは状態を変更せず、ボタンを押し続けても1回の操作として扱う。各フレームで `hUGE_dosound` を呼ぶため、ミュート中も曲の再生位置は進み、解除時は現在位置から復帰する。SameBoyでは通常再生を聴いた後、AでCH2をミュートし、複数フレーズとループ境界を確認してからBで復帰する。主旋律、CH1とCH3の調性・コード進行、拍・テンポ、フレーズ・ループ境界が維持され、誤った和音・不自然な空白・遅れて鳴るCH2音がないことを合格基準とする。

* ゲーム本体はRGBDSでビルドする。
* Pythonは開発支援ツール専用とする。
* Pythonツールは可能な限り再利用できるよう、ゲーム固有処理への依存を避ける。
* 新しいツールを追加した場合は、このREADMEへ用途と実行方法を追記する。
