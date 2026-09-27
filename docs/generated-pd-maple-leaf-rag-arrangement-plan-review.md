# ArrangementPlan再設計・machine検証

## Human判断

「まずはArrangementPlanを作る際の問題を解決してください。」

対象はNormalizedScore→ArrangementPlan。JSON 64-row windowは別段階として扱う。

## 原因調査

旧方式はroleごとに量子化rowをdictionary keyとし、同じkeyの後続eventを`polyphony_omitted`にした。統合方式でabsolute timeline rowをkeyへ含めたため、別小節の同一local位置を誤って衝突させる問題は0になった。新sidecarの全2566 event結果は、selected 1337、omitted 1229、multi-event groups 891、cross-measure false collision 0。

| role | input | selected | omitted |
|---|---:|---:|---:|
| melody/P2 | 1193 | 762 | 431 |
| bass/P3 | 1373 | 575 | 798 |
| harmony | 0 | 0 | 0 |
| rhythm | 0 | 0 | 0 |

omittedは同一role/channel/quantized absolute rowのgroup内で、明示rule `longer duration → higher pitch → source_event_id` により選ばれなかったeventとして記録した。これは全てが音楽的に不要という意味ではない。

## 再設計の責務

ArrangementPlanはsource eventのrole/channel、absolute timeline、pitch/duration transformation、collision group、selection/loss reasonを持つ。JSON pattern/window、runtime timingは後段である。JSON V2は変更していない。

## 後段接続

新sidecar planを既存JSON V2へ適応し、UGE parse、ASM生成、RGBDS ROM buildまで成功した。後段artifact:

| artifact | path | SHA-256 |
|---|---|---|
| JSON | `/tmp/pocket-sweeper-01734/artifacts/integrated-arrangement.json` | `a3cfd73f5971f51721b11c15d2b6e6196daa0f8a14f6495461f75c3a91ec0436` |
| UGE | `/tmp/pocket-sweeper-01734/artifacts/integrated-arrangement.uge` | `a969192f9cc8e597612b7e0b6fc34f4694636414acc53ec660e09a13f57c82c3` |
| ASM | `/tmp/pocket-sweeper-01734/artifacts/integrated-arrangement.asm` | `c7f205afc5ca60d49b3c399371567897e80044e066a783b7dab9c54c41d78674` |
| ROM | `/tmp/pocket-sweeper-01734/artifacts/integrated-arrangement.gb` | `a70a6b932af41732c192e900c6ded88da6968bc69f1735096057ccb5668d875e` |

現行JSONは単一64-row patternのため、ArrangementPlanの全selected eventがJSONへ入ることは保証しない。これはArrangementPlanの1229 omissionとは別の後段lossである。

## 未確認

Humanが音楽的に正しいと感じるmelody/bass、polyphony reductionの妥当性、ROMの音楽品質は未評価。Human試聴taskへhandoffする。
