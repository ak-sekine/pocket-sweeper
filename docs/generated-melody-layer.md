# 生成logical melody layer

対象WBS: `WBS-001-01581`

## Scope

`generate_melody()` は01580の`CompositionStructure`を受け取り、phraseと整数tick上にmotif instanceとmelody eventを生成する。結果はlogical melody layerであり、`physical_channel`は常に未割当である。CH1、pulse duty、sweep、Instrument、UGE note/order、harmony、伴奏、bass、noise、SFX方針はこのWBSで決めない。

## Motifとpitch relation

`MotifDefinition`はIDと`MotifStep`列を持ち、stepはduration、rest、relative interval、scale degree、absolute pitch、accentを表す。restはpitch relationを持たず、非rest stepは3種類のpitch relationのうち1つだけを持つ。key/scale未確定でもrelative intervalで生成でき、absolute pitchへのresolveは後続の責務候補である。

`MotifInstance`はdefinitionから分離され、`motif_ref`、`phrase_ref`、開始tick、transformationを保持する。初版のvariationは`exact`と`relative_interval_offset`に限定し、offsetは呼び出し側が指定する。motif identityは生成後に推測し直さずinstance referenceで保持する。

## Eventと検証

melody eventはphrase reference、start/duration、rest、排他的なpitch relation、motif instance reference、accent、rule refsを持つ。同一logical melody phrase内のevent overlapは禁止する初版model constraintとし、phrase末尾の未使用時間は明示rest eventで埋める。これは音楽的に全phraseを必ず発音で満たす規則ではない。

固定parametersとcandidate optionsを分け、motif選択・variation選択に暗黙defaultを置かない。候補weightを利用する場合も呼び出し側または根拠付きruleから与え、21曲UGEの頻度から導出しない。

## 再現性と未確定事項

01579の単一shared `GenerationContext` streamを使用する。同一contextでstructure生成後にmelodyを生成する場合と、melodyだけを呼ぶ場合ではstream位置が異なるため、pipelineは同じ呼び出し順を共有する。layer別sub-streamは導入していない。

最終key/scale、absolute pitch、register/range、motif長、rhythm/restのdefault、step/leap weighting、repetition/variation default、cadence、harmony reference、logical melodyからphysical channel/UGE rowへのmapping、SFX欠損時の聴感は未確定またはHuman evaluation対象である。自動検証成功を「良いmelody」の証拠とはしない。
