# 生成UGE検証用 `read_file()` 解析結果契約

## 目的

WBS-001-01569で生成UGEを機械検証するため、`tools/analyze_uge.py::read_file()`の戻り値を契約化する。新しい汎用中間表現は作らず、Song Version 6 UGEを読んだ既存dictを検証入力として再利用する。

## 01569から逆算した必要項目

| 検証対象 | 期待値の出所 | 使用する結果 | 現状 |
| --- | --- | --- | --- |
| Song Version | `json_to_uge.py`のUGE出力 | `song_version` | 可能 |
| 4ch order数 | JSONの4 channel order | `order_counts`, `order_count` | 可能 |
| order整合 | 4 channelの構造 | `order_alignment`, `channels.*.order_count` | 可能 |
| pattern参照 | UGE order/pattern | `channels.*.order_pattern_keys` | 可能 |
| pattern再利用 | order構造 | `unique_pattern_keys`, `pattern_reuse_in_orders` | 可能 |
| 64-row | Song Version 6 parser | `pattern_cells`の各配列長 | 追加後に可能 |
| note/Instrument/volume/effect cell | 生成JSONとUGE cell | `pattern_cells` | 追加後に可能 |
| channel使用 | 空でないcellの有無 | `channels.*.used` | 可能 |
| loop | UGE B effectと順序 | `loop`, `position_jumps` | 可能（意味の差に注意） |
| parser構造正常性 | UGE reader | `read_file()`が例外なく完了 | 可能 |

## 現在の `read_file()` contract

トップレベルには、`file`、`sha256`、`size_bytes`、`song_version`、`internal_song_name`、`artist`、`comment`、`tempo_raw`、`pattern_count`、`channels`、`order_count`、`order_counts`、`order_alignment`、`loop`、`routine_count`がある。

`channels[chN]`には、`order_count`、`order_pattern_keys`、`unique_patterns`、`unique_pattern_keys`、`non_empty_patterns`、`non_empty_pattern_keys`、`loop_pattern_keys`、`position_jumps`、`event_count`、`used`、loop範囲に関するpattern/event項目、`pattern_reuse_in_orders`、`unreachable_order_pattern_keys`がある。`used`は音楽的な重要度ではなく、non-empty patternの有無を示す。

### Pattern raw cell

今回、トップレベルに`pattern_cells`を追加した。型は`dict[str, list[list[int]]]`で、keyはUGE pattern keyを文字列化したもの、各patternは必ず64行、各cellは`[note, instrument, volume, effect, effect_param]`の5整数である。これは既存parserが内部で読んでいた値をそのまま公開するだけで、別のIRではない。

`cell_is_non_empty()`の定義はnote（`NO_NOTE=90`）またはinstrument、volume、effect、effect parameterのいずれかが非ゼロならnon-emptyである。従って`event_count`はnote数ではなく、cellがnon-emptyである行数である。`loop_event_count`も同じ意味でloop orderが参照する全cellを数える。

## Pattern / Order契約

`order_pattern_keys`はchannelごとのorder列を順番どおり保持する。`order_count`はその列の長さ、トップレベル`order_counts`は`ch1`〜`ch4`の列長である。`order_alignment`は4列の長さが一致すれば`一致`、それ以外は`不一致`となる。

`unique_pattern_keys`はorder列から重複を除いた順序付き集合であり、`non_empty_pattern_keys`はそのうち1行以上non-emptyなpatternである。pattern数や参照整合性はparserが検証し、欠落参照は`UgeError`とする。

## Loop契約

`loop.kind`は現在、`explicit_simple_loop`、`implicit_full_order_cycle`、`complex_position_jumps`、`invalid_position_jump`を区別する。単純なB effectでは`start_order`、`end_order_inclusive`、`intro_order_count`、`loop_order_count`、`reachable_order_range`、`unreachable_orders`等を返す。B effectがない場合はhUGEDriverのorder末尾wrapを`implicit_full_order_cycle`とする。

これはUGE上のorder/B effect制御フローの契約であり、JSON Version 2のloop metadataの`full`、`range`、`none`と同一ではない。特にJSONの`none`をUGE解析だけから復元することはできない。01569では、生成器が期待するUGE上のB effectまたは暗黙wrapを別途期待値として比較し、JSON loop semanticを推測しない。

## Effect契約

`pattern_cells`のeffect codeとparameterがraw値で検証できる。現在の解析はB effectをloop分類に利用するが、C（volume）やE（note cut）を音楽的意味へ再解釈しない。01569で必要な場合は、生成入力から期待するraw code/parameterを直接比較する。converter内部生成されたC/E/Bも同じraw cellとして現れる。

## Error contract

`read_file()`が成功することを、Song Version 6、固定サイズのinstrument/wave領域、pattern count、64行cell、order終端と参照、routine、末尾byteの構造検証成功と定義する。unsupported Song Version、truncated file、negative count、order terminator欠落、missing pattern reference、trailing bytes等は`UgeError`として検証失敗にする。invalid position jumpはファイル読込例外ではなく、`loop.kind`の構造診断結果である。

## 01569のRequired / Optional / Out of scope

### Required

- parserが例外なく成功すること
- `song_version`が対応版であること
- `order_counts`と`order_alignment`
- 4 channelの`order_pattern_keys`
- `pattern_cells`のpattern key、64行、5整数cell
- `channels.*.used`、必要な`event_count`
- `loop.kind`と、単純loopならstart/end・unreachable情報
- 期待するraw note/Instrument/volume/effectのcell比較

### Optional / Diagnostic

`sha256`、`size_bytes`、曲名、artist、comment、`tempo_raw`、`routine_count`、pattern reuse、unreachable order pattern、loop内pattern/event集計は診断・失敗箇所の説明に使えるが、最小構造判定の必須条件ではない。

### Out of scope

Instrumentの聴感、Wave tableの音色、Noise texture、bass/registerの適否、音楽的品質、注意、長時間疲労、人による試聴、hUGETracker GUI、実機・エミュレータ再生はこの契約で判定しない。詳細Instrument解析も01569の構造検証には不要であり、別WBS候補とする。

## 不足項目と追加実装

追加が必要だったのは、生成cell内容と64-rowを外部から比較するための`pattern_cells`だけである。`pattern_cells`は既存の内部`patterns`から導出し、pattern keyごとに64行を返す。order、loop、channel、eventの別解析や新しいdataclass/IRは追加していない。

## 01569での使用方法

生成入力から期待するorder列、pattern key、使用channel、loop形式、raw cellを作り、`json_to_uge.build_uge()`後に`read_file()`を呼ぶ。Required項目を比較し、不一致または`UgeError`を機械検証失敗とする。高レベルJSONの`length`をUGEから逆構築することはせず、converterが展開した開始cell・空cell・生成effectのraw結果を比較する。

## Human verificationとの境界

この契約定義ではGUI、試聴、実機、エミュレータを実施していない。01570および後続のHuman evaluationで、解析値と実際の曲・再生結果の対応を確認する。
