# 既存UGEコーパスのテスト利用方針

対象WBS: `WBS-001-01574`
調査基準日: 2026-09-26

## 1. 目的

既存UGEを、UGE parser、形式多様性、回帰テスト、生成結果の構造比較に利用できる範囲を定義する。既存UGEは「良い作曲」の統計的根拠、default parameter、品質scoreの学習資料には使用しない。

原則は次のとおりである。

```text
既存UGE → parser / format / regression / edge case / structural comparison
既存UGE -X→ composition-quality evidence / default estimation
```

本書は利用方針の定義であり、外部UGEを新たにGitへ追加せず、`analyze_uge.py`、converter、既存fixtureを変更しない。

## 2. 対象コーパスと「21曲」の定義

`docs/game-boy-music-source-candidates.md`の正本では、次の数が区別されている。

|数|意味|本方針での扱い|
|---:|---|---|
|36曲|配布ページ上で収録数を確認できた候補。Yogi #1/#2 18曲、lillstrumpa vol.1〜3 11曲、objetdiscret 7曲|候補総数。実ファイル数とはみなさない|
|25曲|実ファイル詳細確認済み。Yogi #1/#2 18曲 + objetdiscret 7曲|UGE実体を確認した集合|
|21曲|A判定の曲。Yogi #1のA 4曲 + Yogi #2のA候補10曲 + objetdiscretのA 7曲|過去文書で「21曲」と呼ばれた集合。品質コーパスではない|
|11曲|lillstrumpa vol.1〜3のページ記載曲数。個別UGE未確認|実ファイル解析対象ではない|
|4曲|Yogi #1の第三者作品由来としてD判定された曲|実体が存在しても採用・再配布の根拠にしない|

したがって、本書で「21曲」と書く場合は、25個の実ファイル詳細確認済みUGEから、ライセンス・由来の運用上Aと判定された21曲を指す。25実ファイルとの差は、Yogi #1の第三者作品由来4曲である。21曲、25曲、配布ページ上の36曲を相互に置き換えない。

A判定は、公開一次情報、形式、由来、ライセンス表示に基づくプロジェクト上の受入判定であり、法的保証でも作曲品質の判定でもない。A判定でも、ローカル解析、プロジェクト内テスト、Gitへの元UGE再配布、派生データ公開、商用ROM採用の可否は別々に確認する。

## 3. コーパスの役割

|分類|許可する利用|禁止する解釈|
|---|---|---|
|A. Parser input sample|`analyze_uge.read_file()`が実在UGEを読めるか確認する|読めたことを良い曲・正しい曲の証拠にしない|
|B. Format diversity sample|pattern/order/channel/effect/tempo/loop/未使用channel等の構造差をparserへ与える|頻度や平均値を良い値・defaultにしない|
|C. Regression test sample|parser/converter変更後も以前の構造を読めるか確認する|既存ファイル全体を無条件に不変な正本snapshotにしない|
|D. Error/edge-case discovery|position jump、unused channel、複雑なorder、未対応構造の発見|edge caseの存在を推奨仕様にしない|
|E. Generated-output compatibility comparison|自動生成UGEと実在UGEの値域・構造・形式を比較する|実在曲への類似度を品質scoreにしない|
|F. Composition-quality evidence|禁止|「多いから良い」「似ているから良い」と結論しない|
|G. Default parameter estimation|禁止|tempo、scale、motif長、density、channel役割等を統計から決めない|
|H. Human listening reference|このWBSでは実施しない|解析結果を試聴評価へ読み替えない|

## 4. 許可する利用と禁止する推論

### 許可する利用

- UGE parser compatibility、parse success/failureの確認
- Song Version、pattern/order構造、4ch alignmentの確認
- pattern count、order count、channel `used`/unusedの形式回帰
- raw cell、note、Instrument、volume、effect code/parameterの保持確認
- loop classifier（implicit cycle、simple jump、complex jump、invalid jump）の回帰
- structural diversity、edge-case discovery、local corpus smoke test
- generated UGEと実在UGEの構造・値域・形式比較
- SHA-256によるローカル入力同一性確認
- 01570で既に実施したanalyzer結果とhUGETracker表示の対応確認の参照

### 禁止する推論

- 多数派channel役割から推奨channel役割を作る
- 平均tempoからdefault tempoを作る
- 多数派scale/keyからdefault scale/keyを作る
- 多数派progressionからdefault progressionを作る
- 平均motif/phrase長からdefault長を作る
- 平均event densityから推奨densityを作る
- effect使用率から推奨effectを作る
- Instrument使用率から推奨音色を作る
- loop多数派からPocket Sweeperのdefault loopを作る
- 既存曲との構造・音楽的類似度をquality scoreにする
- `CH1=melody`、`CH3=bass`、`CH4=rhythm`等を多数派から確定する

## 5. analyzer観測値の扱い

現在の`tools/analyze_uge.py::read_file()`の戻り値は、構造観測として次の用途に限定する。

|データ/観測値|許可用途|禁止用途|自動検証可否|備考|
|---|---|---|---|---|
|`song_version`|対応version・parse経路確認|versionが新しい/古いほど品質が高いと評価|可|Song Version 6対応を確認|
|`sha256`|入力ファイル同一性、local baseline識別|品質score、内容の良否判定|可|ファイルversion変更時はbaseline更新を検討|
|`size_bytes`|truncated・入力差分・診断|サイズを複雑さ・品質へ変換|可|構造の直接的品質指標ではない|
|`internal_song_name`、`artist`、`comment`|metadata、対象ファイル対応|作者・タイトルから品質や用途を断定|可|metadataがないことをparse失敗としない|
|`tempo_raw`|値の保持、converter出力比較|平均からdefault tempoを決める|可|実際のBPMや聴感tempoと同一視しない|
|`pattern_count`|pattern領域、参照整合、形式多様性|pattern数が多いほど良いと評価|可|構造値|
|`pattern_cells`|64-row、raw note/Instrument/volume/effect保持、parser/converter regression|melody/harmony/motif/naturalnessをraw cellから判定|可|各cellは`[note, instrument, volume, effect, effect_param]`|
|channel別`order_pattern_keys`|order参照、pattern reuse、channel構造|特定channelの役割や使用量を品質根拠にする|可|order列を順番どおり保持|
|`order_count`、`order_counts`、`order_alignment`|4ch order整合、format diversity|order数が長いほど良いと評価|可|JSON Version 2の同期条件とは別に観測|
|`unique_patterns`、`unique_pattern_keys`|pattern reuseと参照構造の回帰|reuse率を作曲品質へ変換|可|順序付きunique集合|
|`non_empty_patterns`、`non_empty_pattern_keys`|空pattern・未使用構造の確認|non-emptyが多いほど良いと評価|可|空判定はcell値に基づく|
|`used`|CH1〜CH4のused/unused認識|使用率からchannel allocation defaultを作る|可|音楽的重要度ではなくnon-empty patternの有無|
|`event_count`|non-empty cell数のparser regression|note density、良さ、推奨densityのscore|可|note数ではなくnon-empty cell数|
|`position_jumps`|B effect raw target、source order/rowの確認|最頻loopを標準loopにする|可|control-flow観測|
|`loop.kind`|implicit、simple、complex、invalid分類の回帰|多数派loopをdefaultにする|可|UGE制御フロー分類|
|`loop_order_count`、start/end、unreachable|loop構造、edge case、生成比較|loop長をphrase長・品質へ変換|可|endはsimple loopのsource order由来|
|`routine_count`|UGE構造・parse保持|routine数を作曲複雑度や品質へ変換|可|詳細routine意味は別範囲|

特に`event_count`、pattern reuse、loop length、channel count、note count、effect countは構造観測値であり、品質scoreではない。

## 6. Raw cell

01568/01569で契約化された`pattern_cells`は、pattern keyごとに64行、各cellが次の5整数を持つ。

```text
[note, instrument, volume, effect, effect_param]
```

次の検証には使用してよい。

- parser regression
- converter regression
- raw note/Instrument/volume/effect保持確認
- pattern row数・padding確認
- generated JSONから期待するcellとの比較
- effect code/parameterが変換で失われていないかの確認

raw cellから次を直接判定してはならない。

- melody quality
- harmony quality
- motif quality
- naturalness
- instrumentの音色品質

Instrument内部parameter、Wave table、Noise詳細、effectの全音楽的意味など、現在の`analyze_uge.py`で取得していない情報を取得済みとして扱わない。必要なら別の解析契約・WBSで扱う。

## 7. Loop

現在のanalyzerは次のUGE上の制御フローを分類する。

- `implicit_full_order_cycle`: 明示B effectがなく、driverのorder末尾wrapを表す
- `explicit_simple_loop`: 単純なB effect範囲
- `complex_position_jumps`: 複数・不一致の制御経路
- `invalid_position_jump`: forward jumpや範囲外などの診断

これらを分類する解析経路の回帰、B effectのsource/target、unreachable orderの発見には利用してよい。しかし、最も多いloop kindをPocket Sweeper標準にしない。

UGE単独の`implicit_full_order_cycle`は、JSON Version 2の`loop.mode=full`と`none`を区別できない場合がある。`none`をanalyzer結果から推測せず、生成側のloop metadataや期待値を別に検証する。UGEのloop分類と作曲上のphrase closure・loopの自然さも同一視しない。

## 8. Channel usage

`channels.ch1`〜`ch4`の`used`、event、non-empty patternを使って、parserが4ch使用曲と未使用channelを正しく認識するか確認できる。未使用channelを含むファイル、4chを使うファイル、order数・pattern数が異なるファイルをformat diversityとして扱う。

一方、既存21曲のCH使用割合から、CH1=melody、CH2=accompaniment、CH3=bass、CH4=rhythmや、自動生成時の使用率を決めない。channel usageは構造観測であり、音楽的役割の証拠ではない。

## 9. Instrument / effect

Instrument番号、effect code、effect parameterは、parserが値を保持できるか、converterが意図したraw値を出力したか、回帰で変化していないかを確認するために使う。番号や使用率から音色品質、推奨Instrument、推奨effectを推論しない。

01565で確認したInstrument内部parameter、Wave table、Noise詳細、effectの全意味のうち、現行analyzerが返さない項目は観測対象外である。`event_count`とeffect countを音楽的な複雑さや良さへ変換しない。

## 10. ライセンス・再配布との境界

次の段階は同義ではない。

|段階|意味|本WBSの判断|
|---|---|---|
|1. ローカルで解析可能|取得済みファイルを開発者の作業領域で読む|配布ページ・ファイル・条件の確認が必要|
|2. プロジェクト内テストに利用可能|local corpusをparser/regressionの入力にする|ライセンス・由来を曲単位で確認する|
|3. Git repositoryへ元UGEをcommit可能|バイナリをリポジトリで再配布する|自動的に許可されない。明示条件が必要|
|4. 派生データを公開可能|解析JSON、ASM、統計等を公開する|元データの条件、帰属、派生物の範囲を確認する|
|5. 商用ROMへ採用可能|ゲームへ組み込んで配布する|商用・改変・再配布・第三者由来を別途確認する|

`local/music-source-candidates/`のUGEを本WBSの都合でGitへ追加しない。A判定のobjetdiscret 7曲やYogi曲でも、ローカル解析可能、Git再配布可能、商用ROM採用可能は個別条件で判断する。Yogi #1の第三者作品由来D判定曲は、品質・採用・再配布の根拠にしない。

## 11. テスト分類

### Repository-contained automated test

Git管理された自作JSON→UGE fixture、生成UGE、既存の`tests/test_analyze_uge.py`、`tests/test_generated_uge_validation.py`で完結する。CI向きであり、標準unit testの必須入力とする。現在の生成検証は21曲UGEに依存していない。

### Local corpus regression

`local/music-source-candidates/`が存在する開発環境でのみ、ライセンス条件を確認した実在UGEを入力に実行する。CI必須fixtureにはしない。存在しない場合にbuild、validator、標準unit testを失敗させない。

### Manual corpus inspection

必要な場合に開発者が取得元、SHA-256、形式、Song Version、構造、ライセンス文書を確認する。解析結果を音楽品質の確認結果にしない。

### Human listening evaluation

試聴、hUGETracker GUI、実機、エミュレータによる比較は別WBSで扱う。既存曲との類似や好みを自動品質scoreにしない。

## 12. コーパス不在環境

clone直後などで`local/music-source-candidates/`が存在しなくても、build、標準unit test、WBS validator、生成UGE検証が成立することを原則とする。現在確認した`tests/test_analyze_uge.py`と`tests/test_generated_uge_validation.py`は、生成fixture・一時ファイルを使用し、外部21曲を必須依存にしていない。

local corpusを使う補助スクリプトや手動調査を将来追加する場合も、入力ディレクトリ不在を標準CIの失敗にしない。外部UGEを取得する処理、利用許諾を自動推測する処理、品質統計を生成する処理は本WBSの範囲外である。

## 13. Regression baseline

固定候補は、parse success/failure、Song Version、pattern/order構造、channel used、order alignment、loop classification、selected raw cells、structural error detectionとする。SHA-256はローカル入力同一性の確認に使えるが、品質scoreではない。

外部ファイル全体の巨大なsnapshotを無条件に正本化しない。baselineは、取得元・ライセンス・ファイルversion・SHA-256を記録したうえで、構造上必要な観測値と選択raw cellへ限定する。外部ファイルの更新・再取得・ライセンス変更時は、baselineを機械的に更新せず、入力同一性と利用条件を再確認する。

## 14. 01570 Human verificationとの関係

01570で実施済みのPrelude in C majorとHypergolic Blast OffのhUGETracker GUI照合は、analyzerの解析結果と実UGE/hUGETracker表示が対応することの人手検証として参照する。

この結果を、その2曲の作曲技法がPocket Sweeperに適している証拠、品質ランキング、default parameterの根拠へ読み替えない。Hypergolic Blast Offは第三者作品由来のライセンス判断も別に存在するため、解析できることと採用できることを分離する。

## 15. 01572 / 01573との関係

|根拠|例|コーパス観測との関係|
|---|---|---|
|01572 / Hardware・Tool|CH1のみsweep、4ch、CH4 Noise、JSON note値域|既存UGEでの出現率とは無関係に、hardware/tool根拠として扱う|
|01573 / Theory|scale degree、chord、cadence、rhythm、motif|既存UGEの多数派統計と同格に扱わない|
|01574 / Corpus observation|pattern count、event_count、loop.kind、used|形式・回帰・構造比較に限定し、品質根拠にしない|

例えば、既存UGEでCH1 sweepが多くても「CH1でsweepを使うべき」という理論・hardware ruleにはならない。CH1のみsweep可能なのは01572のhardware evidenceであり、scale degreeやcadenceは01573のtheory evidenceである。

## 16. 01575への引き継ぎ

01575では、少なくとも次の区別を表現できる根拠記録形式が必要である。

- `source_type`: theory、hardware、tool、game-bgm、corpus observation、human evaluation等
- `evidence_type`: definition、format test、parser regression、structural observation、listening等
- `allowed_use`: parser、regression、format comparison、composition rule等
- `prohibited_inference`: quality、default、role、style等への不許可推論

本WBSではこの最終schemaを固定せず、「Corpus observation / Format test evidenceはComposition-quality evidenceではない」という境界だけを引き継ぐ。

## 17. 01576への引き継ぎ

melody、motif、rhythm、harmony、bass、noiseのschemaへ、既存21曲の固定patternや多数派値を直接コピーすることを前提にしない。UGEは、01576で定義した抽象表現が実際のUGEへ変換可能か、`analyze_uge.py`で読める構造になるかを後から検証するサンプルとして利用できる。

## 18. 未確定事項

- local corpusを使う補助回帰テストの実行者、頻度、baseline管理方法。
- 外部UGEの取得・更新時にどのライセンス記録を必須化するか。
- どの構造差を最小限のrepository-contained fixtureへ追加するか。
- `analyze_uge.py`が返さないInstrument内部、Wave、Noise、effect詳細を別WBSで解析するか。
- Human listening evaluationでの既存曲の選定基準。選定しても品質統計にはしない。

## 19. 21曲から禁止する推論一覧

1. 多数派channel役割 → 推奨channel役割
2. 平均tempo → default tempo
3. 多数派scale/key → default scale/key
4. 多数派progression → default progression
5. 平均motif/phrase長 → default長
6. 平均density → 推奨density
7. effect使用率 → 推奨effect
8. Instrument使用率 → 推奨音色
9. loop多数派 → default loop
10. 既存曲との類似度 → quality score

## 20. 完了範囲

本方針は、既存UGEを形式・parser・回帰・edge case・生成結果の構造比較へ利用し、作曲品質の根拠とdefault parameter推定から除外する境界を定義した。外部UGEの追加取得、Gitへの追加、parser機能追加、統計分析、品質score、試聴評価は実施していない。
