# Maple Leaf Rag 統合方式 machine evidence

## 実施範囲

01715のHuman判断に従い、時間軸・音符・melody構造を一つの縮約方式として扱った。旧方式のmeasure-local row collisionを変更し、`(role, quantized absolute timeline row)`をcollision identityにした。JSON Version 2とUGEの形式は変更していない。

## 設計・実装

- source: Mutopia-2011/11/13-23
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- PPQ: 384、meter: 2/4、measure ticks: 768、source BPM: 120
- grid: 30 source ticks
- role rule: 現行の平均pitch rankingを明示的暫定ruleとして維持（P2→melody、P3→bass）
- channel: melody→pulse1、harmony→pulse2、bass→wave、rhythm→noise
- source provenanceはmanifest/reportで追跡し、JSON V2は変更しない

## 再検証

source 2566 eventsに対して、absolute timeline基準でroleごとに縮約した。cross-measure local-row false collisionは0。true same-absolute-onset/quantization collisionは個別event mappingとしてmanifest/reportのlossへ記録される。今回のplanはpulse1 762、wave 575、pulse2/noise 0 eventsで、旧16音への誤ったcross-measure集約は解消された。

64-row JSON windowはprototype境界として維持され、JSONへ入ったnoteはpulse1 11、wave 10、合計21。window外はpolyphony omissionと別に扱うべき後続診断対象である。旧方式の16音との比較では、絶対時刻をcollision identityへ含めたmachine metricが変化したが、Human音楽品質の改善は未評価である。

## Timing contract

source BPM 120とruntime `TicksPerRow=6`を分離した。既存runtime contractでは1 rowは約0.1秒、source tickは120 BPMで約0.001302083秒。absolute source rowとruntime rowの変換・window境界をmanifestへ記録する。時間圧縮・pattern window・polyphony reductionは別変換として扱う。

## ROM artifact

生成先: `/tmp/pocket-sweeper-01722/artifacts/maple-leaf-rag-integrated.gb`

| artifact | SHA-256 |
|---|---|
| MusicXML | `3a776f6875e2becb8117a397301bec36c7873a9dc2847960210866af2dec0779` |
| JSON | `ead2205f5aa426cb90b4ed29c008e28b8ff346706c45f85f8ebe0f4a50b2c666` |
| UGE | `958f69da928ba09d245c144b1180d56ac6dcb70efa637c7bd74277fb10c51c16` |
| ASM | `f8efcb35edc5a5d72b4c285f7773a7a895f6b5d7b6cdc4b00d71489ddc10d11c` |
| ROM | `71888719e31a7212224607237baa90b252f863d94e8207b971f069ad8cafe486` |

RGBDS `rgbasm v1.0.1-157-gdecc5f71`、rgblink、rgbfixでbuild成功。JSON validation、UGE parse、ASM生成も成功した。ROM生成はmachine validationであり、音楽的成功の判定ではない。

## 未評価 / handoff

HumanがSameBoyで次を確認するまで、音楽的な改善は未確認である。

1. Maple Leaf Ragとして認識できるか
2. 曲として成立しているか
3. 長さ、テンポ、リズム、音程・メロディが前回よりどう聞こえるか
4. その他の不自然な点
