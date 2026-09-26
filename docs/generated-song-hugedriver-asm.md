# 生成JSONからhUGEDriver用ASMへの変換契約

## 範囲

01588は、01587が生成した既存JSON Version 2を、既存の`tools/json_to_huge_asm.py`でhUGEDriver用RGBDS ASMへ変換する。JSONをUGEへ変換してからASMにする経路や、logical layerから直接ASMを生成する経路は追加しない。

ROM link、RGBDSによる確認用ROM、SameBoy、実機、試聴は01589以降の責務である。

## 入力と既存converter

入力の正本はVersion 2 JSONの`version`、`title`、`type`、`tempo`、`instruments`、channel別`order`/`patterns`、`loop`である。noteの`note`、`length`、`instrument`、`volume`、`effect`、`effect_param`は既存converterのvalidationと展開規則に従う。01588はこれらを再解釈せず、`json_to_huge_asm.build_asm(data, label)`を利用する。

JSON→UGEとJSON→ASMは同じJSON Version 2 validation、channel order、pattern、instrument、note/rest、length、volume/effect、loop semanticsを共有する。byte列の一致は要求しない。

## ASM構造

既存converterはsong descriptor、channel order、pattern cell、duty/wave/noise instrument table、routine、wave table、Version 2 loop metadataを出力する。hUGEDriverのdescriptor ABIと`hUGE_init_v2`等の既存実装に合わせ、descriptorの不要な変更は行わない。Version 2のloop metadataは既存のdescriptor offset契約に従う。

patternのlength展開後はhUGEの64 row制約に従う。不正length、overflow、unsupported effectは既存validatorで拒否する。empty rowはnote/instrument/volume/effectを再適用しない既存仕様を維持する。

## Channel、instrument、wave、noise

JSONで解決済みのinstrumentをそのまま使用する。pulse duty、envelope、wave table、output level、noise parameterを01588で推測しない。CH3 wave tableとCH4 noise noteはJSON→ASM既存実装へ委譲し、logical `character_ref`等へ戻らない。

## loopと決定性

`none`、`full`、`range`はVersion 2の既存loop処理へ渡す。range loopのB effect挿入や既存effectとの競合は既存converterの検証対象であり、新しいloop semanticsを作らない。同じJSONとlabelから同じASM文字列が得られ、乱数は使用しない。

## 統合テストと未解決事項

01587の`convert_to_json_v2()`出力を`json_to_uge.build_uge()`と`json_to_huge_asm.build_asm()`へ連続して渡すintegration testを保持する。これはmachine correctnessの確認であり、SFX共存、CH1 Pulse1 SFX競合、3ch/4ch方針、音楽品質、ROM integration、RGBDS/link、SameBoy、end-to-end seed再生成を解決した証拠ではない。21曲UGEはformat/parser/regression/structural observation以外の根拠に使用しない。
