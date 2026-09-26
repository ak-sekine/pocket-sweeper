# 生成楽曲の確認用ROM生成契約

## 範囲

01589は、01588のhUGEDriver用ASMを既存`tools/build_sound_test_rom.py`で確認用Game Boy ROMへ組み立てる。JSONやlogical layerから直接ROMを作る経路、UGEを必須中間形式にする経路、01590のseed再生成、01591の一括CLIは追加しない。

## Version 1 / Version 2

ツールは入力ASMのsong descriptorと`_loop_metadata`を検査し、Version 1では`hUGE_init`、Version 2では`hUGE_init_v2`を呼ぶ。Version 2の`none`は`hUGE_bgm_finished`を確認して更新を停止し、APUを停止する既存main loopを使用する。`full`と`range`は既存のhUGEDriver/loop metadataおよびB effect処理を変更せず利用する。

入力label不在、Version判定不能、include不足、RGBDS失敗はfallbackせず失敗する。既存Version 1確認ROMの挙動を変更しない。

## Build pipelineと出力

正式経路は次のとおり。

```text
01587 JSON Version 2
  → json_to_huge_asm.build_asm
  → ASM file
  → build_sound_test_rom.py
  → rgbasm → rgblink → rgbfix
  → build/<name>.gb
```

`.gb`は`build/`、中間ASM/OBJ/MAP/SYMは`obj/`へ置く既存方針を維持する。本体ROMを上書きせず、生成物はGitへ追加しない。

確認ROMはGame Boy header、APU初期化、song descriptor、hUGEDriver、VBlank待機、毎フレーム更新を既存builderから得る。SFX共存は01585の範囲であり、このROMの完了条件ではない。

## 検証範囲と限界

01587のJSON→01588 ASM→ROMをテストで連続実行し、Version 2 `hUGE_init_v2`、loop metadata、ROMサイズを機械検証する。使用したRGBDSはrgbasm/rgblink/rgbfix `v1.0.1-157-gdecc5f71`。

ROM生成成功はSameBoy再生、hUGETracker、実機、聴感、SFX欠損耐性、音楽品質、end-to-end seed再生成を意味しない。これらは未解決事項または後続WBSへ残す。
