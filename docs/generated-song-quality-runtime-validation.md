# 評価候補のUGE/GB ROM技術一致確認

対象: WBS-001-01676

## Scope

WBS-001-01675で生成した同一runのJSON、UGE、ASM、GB ROMについて、artifact identityと構造・時間契約を機械確認した。これは聴感一致や音楽品質の判定ではない。

## Artifact identity

各manifestに記録されたSHA-256と現在のJSON/UGE/ASM/ROMを照合し、3候補すべてで一致した。

| candidate | seed | UGE | GB ROM | identity |
|---|---:|---|---|---|
| quality_candidate_01 | 1 | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_01/quality_candidate_01.uge`<br>`1e275ed24b32689c9c0f9eebecaa01aefd946d7ccc5c304dae788bfd352c915a` | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_01/quality_candidate_01.gb`<br>`5a9628660fbbd5e2fb610173dd9944f45e3f39893c7c35bad95e17d08d7f25a3` | 一致 |
| quality_candidate_02 | 5 | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_02/quality_candidate_02.uge`<br>`c323d7f76aff1eb933a03752b79b2a92121af11003ebb47e8e97d567d026aaf8` | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_02/quality_candidate_02.gb`<br>`8b9223f4d8d47039f0999108435442039048a91ef48ed9962616142956b03ce7` | 一致 |
| quality_candidate_03 | 7 | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_03/quality_candidate_03.uge`<br>`fc1cb808f08978283f0b6b7e79ed9784d8c81bbe8ca13e38cbb9ac691527d0cc` | `/home/akihiro/gbdev/pocket-sweeper/build/generated-quality-candidates/quality_candidate_03/quality_candidate_03.gb`<br>`49785e8292e7520cc2cef790238af7cb2eb19a04f28f29811abd07c7ac56e91a` | 一致 |

JSON/ASMも同じmanifestのartifact hashと一致し、別runの混在は確認されなかった。

## Timing and structure

全candidateでJSON `version=2`, `tempo=1`, `loop.mode=full`、各channelのorderは2件（`section-001`, `section-002`）だった。JSONの各channelは6 eventを2 patternへ展開し、UGE analyzerではCH1〜CH4が各2 order、2 non-empty pattern、12 events、order alignment一致、Song Version 6を示した。

ASM descriptor先頭のtempo byteは全candidateで`db 1`であり、UGE raw tempoと一致する。loop metadataはfull loop（mode 0）として生成されている。

## Runtime contract

既存`src/hUGEDriver.asm`の契約では、`hUGE_init_v2`がVersion 2 descriptorのloop metadataを読み、descriptor tempoを`ticks_per_row`へ渡す。`tick_time`は`hUGE_dosound`呼び出しごとにtickを進め、ticks_per_rowに達した時にrowを進める。確認ROM builderはVersion 2で`hUGE_init_v2`を呼び、VBlank待ちごとに`hUGE_dosound`を呼び、`hUGE_bgm_finished`を確認する。

したがって今回のmachine evidenceでは、UGE raw tempo、ASM descriptor tempo、runtime TicksPerRow入力が全て1であること、JSON→UGE/ASM→ROMが同じartifact runであることまで確認できる。実際の再生速度・音色・4ch聴感の一致はHuman確認が必要である。

## Human confirmation request

Humanは各同一run組をhUGETrackerとSameBoyで比較する。

1. UGEとGB ROMでtempoが概ね同じか。
2. UGEとGB ROMでloop周期が概ね同じか。
3. 主要な音の進行が大きく異ならないか。
4. GB ROMでUGEのchannel/layerが丸ごと欠落していないか。

「良い曲か」「Pocket Sweeperに合うか」「単調か」「長時間品質」「SFX共存」は今回の確認対象外である。Human確認結果: 未確認。
