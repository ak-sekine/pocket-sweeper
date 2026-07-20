# Version 2 4チャンネルUGE確認手順

## 対象ファイル

- 入力JSON: `assets/bgm_v2_asm_compare.json`
- 生成UGE: `assets/bgm_v2_asm_compare.uge`

このJSONは `pulse1`、`pulse2`、`wave`、`noise` の4チャンネルを使用し、各チャンネルに1つのorderとpatternを持つ。`loop.mode` は `full` とする。CH1はC4、CH2はG3、CH3はC3、CH4はNoise C4を使用する。

## hUGETrackerでの確認

1. hUGETrackerを起動し、`File` → `Open` から `assets/bgm_v2_asm_compare.uge` を開く。
   - エラーや警告が表示されず、Song Version 6として読み込まれること。
2. CH1～CH4のOrderMatrixを順に表示する。
   - CH1～CH4の各OrderMatrixが存在し、それぞれ対応するpatternを参照していること。
   - 末尾のfiller orderが表示されること。
3. 各チャンネルのpatternを開く。
   - CH1にC4、CH2にG3、CH3にC3、CH4にNoise C4が表示されること。
   - 各patternが64行で表示されること。
4. Instrument画面を確認する。
   - CH1にPulse Instrument、CH2に別のPulse Instrumentが表示されること。
   - CH3にWave Instrumentと `compare_wave` Wave tableが表示されること。
   - CH4にNoise Instrumentが表示されること。
5. 再生する。
   - CH1～CH4の音が同時に使用され、各チャンネルの発音を確認できること。
6. `File` → `Save` で別名または同じファイルへ保存する。
   - 保存が成功し、保存後のUGEを閉じて再度開けること。
   - 再度開いた後もOrderMatrix、pattern、Instrument、Wave tableが維持されること。

この手順のGUI確認は人が実施する。Codexによる自動生成・バイナリ構造確認だけでは、hUGETrackerの表示・再生・保存互換性を完了扱いにしない。

## 人による確認結果

人によるhUGETracker確認を実施し、確認結果は成功だった。

- `assets/bgm_v2_asm_compare.uge`を警告・エラーなく開けた。
- CH1～CH4のOrderMatrixとpatternを確認できた。
- 4チャンネルすべてが再生されることを確認できた。
- UGEを保存できた。
- 保存後に再度開いても問題がないことを確認できた。
