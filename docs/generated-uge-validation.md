# 生成UGEの機械検証

## 検証経路

JSON Version 2を`json_to_uge.build_uge()`でSong Version 6 UGEへ変換し、一時ファイルを`analyze_uge.read_file()`で再解析した。01568の`docs/generated-uge-analysis-contract.md`を期待結果の契約として使用し、JSON入力から独立に定めたraw値と比較した。新しいparserや汎用IRは追加していない。

## 使用入力

既存の`assets/bgm_v2_workflow_check.json`を再利用した。これは4 channel、6 order、channel-local pattern、pattern reuse、note、Instrument、note volume、rest、range loopを含む。未使用channelのケースは、このfixtureからnoiseのorder/patternを除いた最小派生入力をテスト内で作成した。21曲UGE素材は使用していない。

## 自動検証結果

- Song Version: raw `6`、supported `true`
- 4ch order count: `[6, 6, 6, 6]`
- order alignment: `一致`
- channel order pattern keys: CH1=`0..5`、CH2=`6..11`、CH3=`12..17`、CH4=`18..23`
- 全pattern: 64 rows、各cellは5整数
- `used`: 通常fixtureは4chすべてtrue、noise除去fixtureはCH4のみfalse
- `event_count`: non-empty cell数として、未使用CH4は0
- raw note/Instrument: 例としてC5→`[24, 1, ...]`、CH2 C4→`[12, 2, ...]`を確認
- C effect: note volume 12/7/6を`C0C`/`C07`/`C06`として確認
- E effect: restを`E00`として確認
- B effect: range loopの最終order rowでraw target `3`、解析上target order `2`を確認
- loop: rangeは`explicit_simple_loop`、start `2`、end `5`、loop order count `4`。fullは`implicit_full_order_cycle`。
- parser: 正常生成UGEは例外なく再解析できた

JSON `loop.mode = none`はUGE上でfull cycleと区別できないため、analyzerだけからnoneを推測しないこともテストで確認した。

## Durationの扱い

JSONの`length`をanalyzerから逆算せず、converterが展開した開始row、後続空row、次のevent/restのraw cellを比較した。pattern paddingも64 rowsの空cellとして確認した。

## 範囲外

Instrument内部field、Wave table内容、Noise textureの聴感、音楽的品質、GUI、試聴、実機、エミュレータ、Human verificationは対象外である。これらは01570または後続の人による確認へ残す。
