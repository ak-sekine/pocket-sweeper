# Seed付き生成基盤

対象WBS: `WBS-001-01579`

## 契約

`tools/bgm_generator.py` の `GenerationContext` は、明示された整数 `seed` から独立した `random.Random` を作る。seedの省略、`None`、文字列、浮動小数点、`bool` は受け付けない。負数とPythonの任意精度整数は許可する。

同一repository revision・同一generator version・同一入力順序・同一seedで、同じcontext APIの結果を再現する。Pythonやアルゴリズムの変更後まで同じ結果を永続保証する契約ではない。結果には `seed` と `generator_version` を保存する。

候補は順序を持つlist/tuple等で渡す。setは順序が不明なため拒否し、dict等を候補に使う場合も呼び出し側が決定的なsequenceへ変換する。weighted choiceは非負weight、正の合計、空でない候補、同じ長さを要求する。音楽的weightやdefault seedは定義しない。

モジュールglobalの乱数状態には依存しない。現版は単一のcontext streamを提供し、layerごとのsub-seedは後続WBSで必要性と安定した派生方式（組み込み`hash()`ではなくSHA-256等）を判断する。

`deterministic_probe` はchoice・range選択・weighted choice・shuffleを含む非音楽的な再現性確認用であり、BGM品質や21曲UGEの統計を評価しない。01580〜01585の曲構成・各layer生成・4ch/SFX制約保証は本WBSの範囲外である。
