# 生成楽曲から確認用ROMまでの一括pipeline

## 1コマンドの定義

`tools/generate_bgm_test_rom.py`を1回呼び出すと、明示されたPython profileとmaster seedから、JSON Version 2、UGE、hUGEDriver ASM、確認用ROM、manifestを順に生成する。profileはcaller-owned入力であり、Pocket Sweeperの作曲defaultではない。

```text
master seed + profile
 → generate_logical_composition
 → convert_to_json_v2
 → json_to_uge.build_uge
 → analyze_uge.read_file (必須検証)
 → json_to_huge_asm.build_asm
 → build_sound_test_rom.build_rom
```

## 入力と実行例

profile Python fileは`build_profile(seed)`を提供し、`LogicalGenerationPlan`、明示allocation、resolution、instrument、timing、title等を返す。seedだけでは曲を決めず、profileが不足する場合は失敗する。

```bash
python3 tools/generate_bgm_test_rom.py --seed 42 \
  --profile tools/generation_profile_fixture.py \
  --output-dir /tmp/generated-song --name generated_seed_42
```

`generation_profile_fixture.py`はpipelineの構造を検証する明示fixtureであり、品質評価済みのproduction profileではない。

## UGE機械検証

JSONを正本・中間成果物としてUGEを生成し、01569の既存`analyze_uge.read_file()`でSong Version 6、order整列を確認してからASM/ROMへ進む。解析失敗、unsupported version、order不整合はfail-fastし、後段成果物を成功扱いにしない。UGE解析は形式・構造検証であり、音楽品質評価ではない。

## Artifactsとmanifest

指定output directoryへ`<name>.json`、`.uge`、`.asm`、`.gb`、`.manifest.json`を保存する。manifestにはseed、generator version、profile、各artifact path、SHA-256、UGE検証要約を記録する。本体BGM (`obj/bgm_*.asm`) と本体ROM (`build/pocket-sweeper.gb`) は上書きしない。評価用artifactは再生成可能なためGitへ追加しない。

## 決定性とエラー

同じrepository/generator version、profile、seed、toolchainで、JSON/UGE/ASM/ROMのSHA-256が一致することを実測した。invalid seed/profile、logical generation、allocation、resolution、JSON/UGE解析、ASM、RGBDS、ROM出力の失敗はnon-zeroで終了する。途中失敗時のartifact cleanupは行わないため、出力directoryを確認して再実行する。

## 境界

SameBoy、実機、hUGETracker、試聴、SFX共存、音楽品質は実施しない。01592はpipelineの有効性評価、01593は複数seed候補生成を担当する。21曲UGEはseed、weight、default、品質の根拠に使用しない。
