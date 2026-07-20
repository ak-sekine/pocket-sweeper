# Version 2 4チャンネルASM比較結果

## 比較対象と出所

- 入力JSON: `assets/bgm_v2_asm_compare.json`
- 入力UGE: `assets/bgm_v2_asm_compare.uge`
- 直接生成ASM: `obj/bgm_v2_asm_compare_direct.asm`
  - `.venv/bin/python tools/json_to_huge_asm.py` で生成。
- hUGETracker Export ASM: `assets/bgm_v2_loop_full_reexport.asm`
  - `assets/bgm_v2_loop_full_reexport.uge` を hUGETracker で読み込み、保存後にExportした未加工ファイル。
  - 作成記録はコミット `5d7850fae1464d2446d0abd332ed4dcbbb088ddf`（2026-07-19）。
  - `assets/bgm_v2_loop_full_reexport.uge` と対象UGEのSHA-256は同一であり、今回の入力UGEと同じバイナリである。
  - プロジェクト記録上のhUGETrackerはv1.0.11。

今回の環境ではhUGETracker GUI自体は実行できなかったため、既存の出所確認済みExport ASMを比較対象にした。比較用ASMは `obj/` のためコミットしない。

## 比較方法

`tools/compare_huge_asm.py` でASMをラベル単位に分解し、生成側prefixを除去して、descriptor、OrderMatrix、pattern、Instrument、routine、Wave tableを正規化比較した。比較器はラベル名、SECTION名、10進数/16進数、routineの空ラベル、同一patternの番号差を表記差として扱い、Version 2の`loop_metadata`は独自拡張として別扱いにする。

## 結果

- descriptor: 標準部分（tempo、order count、CH1～CH4のOrderMatrix、Duty/Wave/Noise bank、routine、Wave bank参照）は一致。生成側の`dw ..._loop_metadata` 1行は本プロジェクト独自拡張。
- OrderMatrix: order countは2。CH1～CH4の参照関係は、それぞれP0～P3相当で一致。UGE由来のfillerはASM Exportでは省略される表記差。
- pattern: CH1 C4、CH2 G3、CH3 C3、CH4 Noise C4を確認。全patternは64行で、空行は`dn ___,0,$000`相当。instrument番号とeffect `$000`も一致。
- Duty Instrument: CH1/CH2のentry bytesは一致（それぞれduty 2 / 1、指定されたvolume/envelope/length/enable、およびCH1 sweep）。
- Wave Instrument/Wave bank: Wave Instrumentのlength/enable/output level/waveform参照と、`compare_wave` 32サンプルの16byte packingは一致。
- Noise Instrument: initial volume、envelope、length/enable、width bitを含むentry bytesは一致。NR43相当のNoise polyはInstrument固定値ではなく、pattern noteとwidth設定の合成であり、CH4 note変換結果をpattern側で比較した。
- routine: 16個の空routineと`ret`の実質動作は一致。

## 差分の分類

意味的に一致する差分は、ラベルprefix、SECTION名、pattern番号表記、routineラベル形式、Wave bankの`db`分割、未使用bank entryの省略、UGEのfillerとASMの省略である。

本プロジェクト独自拡張は、Version 2 descriptor末尾の`loop_metadata`参照と、その`mode/final_order/final_row`である。hUGETracker標準Exportにないため、標準部分の一致判定から分離した。

今回確認した範囲に、再生動作へ影響する意味的不一致はない。hUGETracker GUIを今回実行したこと、また今回のExport操作の設定画面を再確認したことは未確認である。既存記録に従い、必要なら人が次を再実施する: hUGETracker v1.0.11で対象UGEを開く → `File` → `Export`（RGBDS ASM） → `obj/bgm_v2_asm_compare_hugetracker.asm`へ保存 → 生成ASMを直接生成ASMと比較する。対象UGE、既存資産、正本ASMは上書きしない。

## 回帰確認

```bash
.venv/bin/python tools/json_to_huge_asm.py \
  assets/bgm_v2_asm_compare.json obj/bgm_v2_asm_compare_direct.asm
.venv/bin/python tools/compare_huge_asm.py \
  obj/bgm_v2_asm_compare_direct.asm assets/bgm_v2_loop_full_reexport.asm
```

比較器の単体テストは `tests/test_compare_huge_asm.py` にあり、架空のExport fixtureは追加していない。既存Export ASMを更新する場合は、入力UGE、hUGETrackerバージョン、未加工Exportであること、許容する表記差をこの文書とコミット記録へ追記する。

## 今回の自動確認結果（2026-07-20）

- `.venv/bin/python tools/json_to_uge.py assets/bgm_v2_asm_compare.json obj/bgm_v2_asm_compare_generated.uge` は成功し、68102 bytesを生成した。既存の `assets/bgm_v2_asm_compare.uge` と内容が一致した。
- `.venv/bin/python tools/json_to_huge_asm.py assets/bgm_v2_asm_compare.json obj/bgm_v2_asm_compare_direct.asm` は成功した。
- `tools/compare_huge_asm.py` による比較は、意味的な不一致を報告しなかった。pattern番号・ラベルprefix・空routineラベル・UGE由来filler・Wave bankの分割／未使用bank省略は表記差として扱った。
- `loop_metadata` はhUGETracker標準ExportにないVersion 2独自拡張として分離した。`loop.mode = full`の標準再生構造との一致判定には含めていない。
- `hUGETracker`の実行、今回のGUI Export操作、今回のバージョン表示はこの環境では確認できなかった。既存記録に記載されたv1.0.11は今回の実行で再確認していない。

## 人によるhUGETracker Export・比較確認

人によるhUGETracker Exportと比較確認が完了した。実行コマンドは次のとおり。

```bash
.venv/bin/python tools/compare_huge_asm.py \
  obj/bgm_v2_asm_compare_direct.asm \
  obj/bgm_v2_asm_compare_hugetracker.asm
```

比較結果では、意味的な不一致は報告されなかった。pattern P0～P3、routine 0～15、Pulse／Wave／Noise Instrument、OrderMatrixは要素数が一致し、表記上の差異のみだった。Wave tableはgenerated側16単位、Export側1ブロックという分割上の差異だった。descriptorは標準部分が一致し、generated側の7要素とExport側の6要素の差は、hUGETracker標準Exportに存在しない本プロジェクト独自の`loop_metadata`参照だった。`loop_metadata`は独自拡張として正しく分離された。

人による確認が成功したため、PROJECT.mdの対象WBS親項目と子項目を完了にした。
