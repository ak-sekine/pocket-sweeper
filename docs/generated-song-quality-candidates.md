# 評価用profileの複数seed候補

対象: WBS-001-01675

## Scope

`tools/generation_profile_quality_evaluation.py`を変更せず、同profileを
`logical generation → JSON Version 2 → UGE → hUGEDriver ASM → RGBDS ROM`
へ接続した機械検証記録である。Humanによる試聴・音楽品質の選別は実施していない。

## Profileとseed

- profile: `tools/generation_profile_quality_evaluation.py`
- purpose: Human BGM quality evaluation用のevaluation-only profile
- production composition rule/defaultおよびpipeline minimum fixtureではない
- seed: `1, 5, 7`
- seed選択: 01593で使用した固定集合を再利用したevaluation methodology parameter。候補を生成後に選別するためのseedではない
- generator version: `0.2.0`
- tempo/TicksPerRow: profile明示値 `1`。BPM値としては扱わない

## Candidate artifacts

全candidateで、JSON/UGE/ASM/ROMを同一runの同一directoryへ出力した。各UGEはSong Version 6、order alignment一致、CH1〜CH4使用、各channel 2 order / 2 non-empty pattern / 12 eventsとしてanalyzerを通過し、ASM生成とRGBDS buildに成功した。

| candidate | seed | JSON SHA-256 | UGE SHA-256 | ASM SHA-256 | ROM SHA-256 |
|---|---:|---|---|---|---|
| quality_candidate_01 | 1 | `0bdd1a3acc84e48ba0e1bbe0d2519b096df1e352bc0e3196a88644435f7f28fd` | `1e275ed24b32689c9c0f9eebecaa01aefd946d7ccc5c304dae788bfd352c915a` | `4bf75ba205e264e77e0af2c7e05125f037bff14f1b4a0ce8046e22b3409f9e4f` | `5a9628660fbbd5e2fb610173dd9944f45e3f39893c7c35bad95e17d08d7f25a3` |
| quality_candidate_02 | 5 | `2b3d29a5f585333b25aa83469061f9e874c48f73c403cea61f27c65dd7c6897b` | `c323d7f76aff1eb933a03752b79b2a92121af11003ebb47e8e97d567d026aaf8` | `5ecd7b0ab144db4cb5a6e50ecba1a54b55833e41cad60d9b6b1ad0626d3b7af0` | `8b9223f4d8d47039f0999108435442039048a91ef48ed9962616142956b03ce7` |
| quality_candidate_03 | 7 | `3f58ce64498774ba89887b6eff4309ebc7f37e92e7698e28040d9997d16b5475` | `fc1cb808f08978283f0b6b7e79ed9784d8c81bbe8ca13e38cbb9ac691527d0cc` | `fec14e09bcda490fc51500483ea3f337d865ea540a49d166362f54aa94dd5a98` | `49785e8292e7520cc2cef790238af7cb2eb19a04f28f29811abd07c7ac56e91a` |

Artifact pathsは`build/generated-quality-candidates/quality_candidate_0{1,2,3}/`以下で、各manifestがseed・version・paths・hash・UGE validationを保持する。build artifactは再生成可能なためGitには追加していない。

## Logical coverage

各seedでstructureは2 sections / 4 phrases / full loop、melody・accompaniment・bass・noiseの各layerは12 eventsを生成した。melodyのmotif選択は、seed 1が`a,c,a,b`、seed 5が`c,b,c,b`、seed 7が`b,a,b,c`。他3 layerは各phraseで同一の明示patternを使用した。これはlayer coverageとseed差の機械的記録であり、音楽品質の判定ではない。

## Reproducibility and differences

seed 1を同じprofile・同じseed・同じartifact nameで一時directoryへ再生成した。JSON/UGE/ASM/ROMの全SHA-256が一致した。異なるseedではJSON/UGE/ASM/ROMの全artifact hashが異なり、melody motif選択も異なった。これは差異の存在を示すだけで、品質・多様性の評価ではない。

## Human evaluation and handoff

Human試聴は未実施である。次のWBS-001-01676では、同一candidate runの次の組を比較対象とする。

- `quality_candidate_01.uge` と `quality_candidate_01.gb`（seed 1）
- `quality_candidate_02.uge` と `quality_candidate_02.gb`（seed 5）
- `quality_candidate_03.uge` と `quality_candidate_03.gb`（seed 7）

音楽品質、SFX共存、Pocket Sweeper適合性は未評価であり、01677以降へ残す。

## Human BGM evaluation (WBS-001-01677)

対象は、01675で生成し01676で技術的一致を確認した次の3候補である。

- quality_candidate_01 / seed 1
- quality_candidate_02 / seed 5
- quality_candidate_03 / seed 7

Humanは3候補を実際に試聴し、次の報告を行った。

> 全部、音を並べただけで曲になっていません。

このHuman evidenceの範囲では、3候補すべてが「曲として成立していない」と評価された。したがって今回の候補について、実用的なPocket Sweeperプレイ中BGMであることは肯定できない。ただし、自動作曲方式一般の成立可能性や絶対的不適合を示すものではない。

技術的なfull loopはmachine validation済みだが、長時間loop品質の独立したHuman評価は未確認である。SFX共存も未確認である。今回の記録では原因分析、profile変更、composition rule変更は行っていない。
