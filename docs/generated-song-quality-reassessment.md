# 新しい品質評価候補の実用性再評価

対象: WBS-001-01678

## Scope

01675〜01677で得られたquality_candidate_01〜03について、machine evidenceとHuman evidenceを分離して実用候補の有無を再評価する。自動作曲方式全体の継続・見直し・中止はWBS-001-01598のHuman判断に残す。今回、generator、profile、composition ruleは変更していない。

## Previous evaluation

01593〜01597の旧candidate 01〜03（seed 1/5/7）は、JSON/UGE/ASM/ROM生成・構造検証に成功したが、当時のHuman試聴では「1音しかならず曲になっていません。」と記録された。その後、旧UGE（tempo 120）と修正ROM（tempo 1）が別runだったこと、tempo/TicksPerRow契約の不整合が判明・修正された。旧Human観測は当時の成果物に対する証拠として保持し、削除・書換えはしていない。

旧評価から、原因や作曲方式全体の可否は確定していない。

## Technical reevaluation

01675ではevaluation-only profileからseed 1/5/7を生成した。01676で、各candidateのJSON/UGE/ASM/GBが同一runであること、manifest hash一致、JSON Version 2、UGE Song Version 6、tempo=1、ASM descriptor tempo=1、runtime ticks_per_row=1、order alignment、CH1〜CH4構造、pattern/order、full loop、RGBDS ROM build、seed 1の再現性を確認した。

同一runのUGE/GBについてHumanは「ugeとgbを再生した感じは同じに聞こえました。」と報告した。これは技術的な聴感一致の確認であり、音楽品質の評価ではない。

## Human reevaluation

01677で、技術確認済みの次の3候補をHumanが試聴した。

- quality_candidate_01 / seed 1
- quality_candidate_02 / seed 5
- quality_candidate_03 / seed 7

Humanの原文は次のとおりである。

> 全部、音を並べただけで曲になっていません。

この証拠から確認できるのは、現在のquality evaluation profileで生成した3候補すべてについて、Humanが曲として成立していないと評価したことである。原因、改善方法、特定のcomposition ruleの問題はこの証拠から確定していない。

## Practical candidate assessment

今回の3候補には、Human evidenceで支持された実用BGM候補はない。したがって、現時点の証拠からPocket Sweeperのプレイ中BGMとして実用的であることは肯定できない。ただし、これは今回の3候補に対する評価であり、自動作曲方式一般が成立しないこと、将来改善しても利用できないこと、絶対的不適合を意味しない。

技術的なfull loopは確認済みだが、長時間loop品質の独立評価は未確認である。SFX共存も未確認である。

## Unresolved items

以下は未確定である。

- 曲として成立しなかった理由
- profile parameterとgenerator modelの寄与
- melody、harmony、accompaniment、bass、rhythm、noise、allocationのどこを変更すべきか
- 必要な改善方法と、その改善でHuman評価が変わるか
- 長時間loop品質
- SFX共存
- 将来のproduction composition rule
- 自動作曲方式を継続する価値

## Rule evidence impact

今回のHuman結果は、現在のevaluation profileによる3候補に対するHuman evidenceとして扱う。最低note数、harmony必須、4ch必須、motif長、scale、chord progression等のproduction composition rule/defaultは新たに確定しない。必要なrule見直しは、composition-rule evidence schemaとreturn workflowに従う後続調査へ渡す。

## Handoff to WBS-001-01598

Humanが判断するための事実は次のとおりである。

- JSON→UGE→ASM→ROM pipelineは機械的に成立した。
- runtime timing mismatchはtempo/TicksPerRow契約修正後、同一runで再発しなかった。
- 同一runのUGE/GBはHumanに聴感上同じに聞こえた。
- quality evaluation profileからseed 1/5/7の3候補を生成した。
- 3候補すべてHumanには「音を並べただけで曲になっていない」と評価された。
- 今回の3候補にはHuman evidenceで支持された実用候補がない。
- 原因と改善方法は未確定である。
- 長時間loop品質とSFX共存は未確認である。
- 自動作曲方式全体の継続・見直し・中止は01598でHumanが判断する。
