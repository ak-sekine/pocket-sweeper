# 01593 候補曲一覧

## 目的とprofile

01591の一括pipelineを、事前に固定したseed集合へ適用し、01594のSameBoy試聴へ渡す候補ROMを準備した。使用profileは`tools/generation_profile_candidates.py`で、既存のmotif candidate選択機構とcaller-owned patternを使う評価専用profileである。Pocket Sweeperのproduction profile、default、品質判定ではない。

既存`tools/generation_profile_fixture.py`もseed 1〜3で実測したが、JSON/UGE/ROMが同一となりcandidate variationがなかったため、候補一覧には採用しなかった。候補profileでは3つの明示motif candidateを用い、seedそのものを音楽値へ変換していない。

## Candidate index

生成rootは`build/generated-candidates/`である。build artifactsは再生成可能で`.gitignore`対象であり、Gitへcommitしていない。

| Candidate | Seed | JSON | UGE | ASM | ROM | UGE validation |
|---|---:|---|---|---|---|---|
| candidate-01 | 1 | `build/generated-candidates/candidate_01/candidate_01.json`<br>`9164b9576203540154780d98205c0b941eabd1a641979418133626885d4bf4c7` | `.../candidate_01.uge`<br>`b95cb0e2a4abf6eb27ef4fcd1c5d7baec9e309772111e04776de50f6c11e1f4e` | `.../candidate_01.asm`<br>`54d8446f19d96e0295a7d7f6b9d7273cad668330a739d4d8e4af2e0a07f0d7e2` | `.../candidate_01.gb`<br>`18ddf091a7382ce5ae2bab960008cee735644d3a01b536ed6e03cf35b69d7e24` | Song Version 6、order alignment 一致 |
| candidate-02 | 5 | `build/generated-candidates/candidate_02/candidate_02.json`<br>`19b3665ed79e4a31e1762175d6de796a88c396264fead9c2ee4e498f56eae62f` | `.../candidate_02.uge`<br>`ca0d05a82691fe90e2bb50b9dc751a2fff3d6713c8bc6f495f67d12afea976ff` | `.../candidate_02.asm`<br>`1847806cb025dfebb50056cb9bb59f5fd402aeea91077f69d1adb734a7427064` | `.../candidate_02.gb`<br>`46cfe8b5ad8b0d45dc67eb033f2cbb0a7fb2807feea01a5f122a8fffd9bfa0cf` | Song Version 6、order alignment 一致 |
| candidate-03 | 7 | `build/generated-candidates/candidate_03/candidate_03.json`<br>`9adda7252c02b5465b0be9251c564ba4e68864247254c0fc063d8035ea1e0598` | `.../candidate_03.uge`<br>`7e065e01994b94328ca3aa128d0053ab9e268f3d67804be62c0f89dd9d609945` | `.../candidate_03.asm`<br>`addbac2f19ec0eb78ba463fc5c3bedb8c278c3cb47cd73fda7d79eb1800e640e` | `.../candidate_03.gb`<br>`9cb2cf219708807381c509a8c060e6c1495183ade889bbd08853acb23b3e0aa9` | Song Version 6、order alignment 一致 |

各manifestにもseed、generator version、全path/hash、UGE解析要約を保存している。RGBDSはrgbasm/rgblink/rgbfix `v1.0.1-157-gdecc5f71`で生成した。

## Unique、再現性、引き継ぎ

3候補のJSON/UGE/ASM/ROMはいずれも相互に異なり、duplicateはない。候補-01（seed 1）を別outputへ再生成し、4 artifactのhash一致を確認した。候補生成は形式・構造・変換・再現性のみを確認しており、音楽品質、長時間loop、SFX共存、Pocket Sweeper適合性は未評価である。

01594では次のROMをSameBoyで開く。

1. `build/generated-candidates/candidate_01/candidate_01.gb`（candidate-01 / seed 1）
2. `build/generated-candidates/candidate_02/candidate_02.gb`（candidate-02 / seed 5）
3. `build/generated-candidates/candidate_03/candidate_03.gb`（candidate-03 / seed 7）

SameBoyを起動していないため、試聴結果欄は未記入である。
