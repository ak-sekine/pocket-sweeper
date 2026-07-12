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

初版の対応範囲:

* `version`, `title`, `type`, `tempo`, `instruments`, `order`, `patterns`, `channels` を読み込む
* `pulse1`, `pulse2`, `wave`, `noise` の4チャンネルを扱う
* noteは `C3`〜`B8` と `rest` を扱う
* `length` は64行固定patternへ行展開する
* effectは `effect: null`, `effect_param: null` のみ対応する
* `wave` / `noise` 未使用時は空patternを出力する
* Instrument IDは1〜15のみ使用できる
* Pulse Instrumentでは `duty`, `initial_volume`, `envelope_direction`, `envelope_sweep` を任意指定できる

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

Version 2ではPulse Instrumentの`length`、`length_enable`、Pulse1専用の
`sweep_time`、`sweep_direction`、`sweep_shift`も検証し、UGEおよびhUGEDriver用ASMへ出力する。
Wave Instrumentも検証、Wave table名前解決、UGE、hUGEDriver用ASM出力に対応する。
Wave tableのUGE・hUGEDriver用ASM出力に対応する。Noise Instrumentの検証、UGE、hUGEDriver用ASM出力にも対応する。
Version 2のorder / patterns / loop、CH4 Noise note変換、NR43生成、note volumeは未対応である。
Version 1は引き続き利用できる。

初版では未対応:

* hUGETracker上での読み込み・保存・ASM Export自動確認
* 非null effect
* Wave table編集
* Routine / Instrument subpattern編集
* 64行を超えるpattern

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

初版の対応範囲:

* hUGETracker Export ASMに近いsong descriptor、order、pattern、instrument、routine、wave構造を出力する
* song descriptorのラベル名は出力ASMファイル名から生成する
* `pulse1`, `pulse2`, `wave`, `noise` の4チャンネルを扱う
* noteはRGBDS ASM表記の `C_4`, `C#4`, `___` へ変換する
* `length` は64行固定patternへ行展開する
* effectは `$000` のみ対応する
* `wave` / `noise` 未使用時は空patternを出力する
* duty instrumentsを出力する
* Pulse Instrument詳細をduty instrumentsへ反映する

初版では未対応:

* hUGETracker Export ASMとの完全一致確認
* 非null effect
* CH4 Noise note変換と実質的なNoise再生
* Routine / Instrument subpattern編集
* サウンド再生確認用テストROM生成

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

* ゲーム本体はRGBDSでビルドする。
* Pythonは開発支援ツール専用とする。
* Pythonツールは可能な限り再利用できるよう、ゲーム固有処理への依存を避ける。
* 新しいツールを追加した場合は、このREADMEへ用途と実行方法を追記する。
