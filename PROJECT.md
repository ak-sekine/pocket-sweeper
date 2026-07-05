# AIへの指示

- このファイルを、仕様・設計・進捗を集約するプロジェクト唯一の管理ドキュメントとして扱うこと。
- 仕様、設計、進捗を変更した場合は、実装と合わせてこのファイルを更新すること。
- 作業を始める前にこのファイルを確認し、作業後に変更内容を反映する必要がないか確認すること。
- 新しい管理ドキュメントを安易に増やさず、まずこのファイルへの追記・整理を検討すること。
- 未確定事項を推測で確定せず、必要に応じてWBSへTODOとして記録すること。
- 更新履歴はGit logで管理し、PROJECT.mdには記載しない。

# プロジェクト概要

- **プロジェクト名:** Pocket Sweeper
- **日本語表記:** ポケットスイーパー
- **概要:** 初代ゲームボーイで動作する、シンプルなマインスイーパー。
- **目的:** RGBDSによるゲームボーイ開発の基礎を習得し、将来のゲームボーイRPG開発に流用できる共通処理を整備する。
- **開発環境:**
  - WSL2 Ubuntu
  - VS Code + Remote WSL
  - RGBDS 1.0.1系（アセンブラ、リンカ、ROM修正ツール）
  - SameBoy / BGBなどのエミュレータ
  - hUGETracker（BGM・効果音制作に利用予定）
  - Git / GitHub

# ゲーム仕様

## 操作方法

- 十字キー: カーソル移動
- Aボタン: 選択中のマスを開く
- Bボタン: 選択中のマスにフラグを設置・解除
- STARTボタン:
  - タイトル画面: 難易度選択画面へ進む
  - 難易度選択画面: 選択中の難易度でゲーム開始
  - 通常プレイ中: ポーズメニューを表示
  - ゲームオーバー／ゲームクリア後: タイトル画面へ戻る
- SELECTボタン: 未定

## ルール

- **クリア条件:** 地雷以外のすべてのマスを開く。
- **ゲームオーバー条件:** 地雷のあるマスを開く。
- **盤面サイズ:** 固定ではなく、選択した難易度に応じて決定する。
- **地雷数:** 固定ではなく、選択した難易度に応じて決定する。
- 難易度は初版から実装する。
  - EASY: 盤面8×8、地雷10個
  - NORMAL: 盤面9×9、地雷15個
  - HARD: 盤面10×10、地雷20個
- ゲーム開始時は選択した難易度を使用して盤面を生成する。
- 地雷はゲーム開始時には配置しない。
- 最初にAボタンでマスを開いた時点で地雷を配置する。
- 最初に開いたマスには地雷を配置しない。
- それ以外のマスからランダムに地雷を配置する。

## 表示内容

- タイトル画面
  - 初期実装では何も表示しない状態でもよい。
  - 最終的にはタイトルロゴ、`PRESS START`、`©2026 AKIHIRO SEKINE` を表示する。
  - STARTボタンで難易度選択画面へ進む。
- 難易度選択画面
  - `SELECT LEVEL` を表示する。
  - `EASY`、`NORMAL`、`HARD` を表示する。
  - 選択中の難易度の左に `▶` を表示する。
  - AボタンまたはSTARTボタンで選択中の難易度を決定してゲームを開始する。
  - Bボタンでタイトル画面へ戻る。
- 1行目：ステータスバー
  - 残地雷数 例 MINE:xxx（難易度の地雷数に応じて初期値を変える）
  - 経過時間 例 TIME:123
- 2～18行目：盤面
  - 盤面（未開封、開封済み、数字、地雷、フラグ）
  - 操作カーソル(Spriteで表示)
- ゲームオーバー時は盤面下に `GAME OVER` を表示する。
- ゲームクリア時は盤面下に `CLEAR` を表示する。
- 通常プレイ中にSTARTボタンを押した場合はポーズメニューを表示する。
  - `RESUME`: ポーズメニューを閉じて通常プレイに戻る。
  - `RESTART`: 現在のゲームを破棄し、現在選択中の難易度を維持して新しいゲームを開始する。
  - `BACK TO TITLE`: 現在のゲームを破棄してタイトル画面へ戻る。

# システム構成

## ディレクトリ構成

```
pocket-sweeper/
├── .venv/            # Python仮想環境（Git管理外）
├── README.md         # 公開向けドキュメント
├── PROJECT.md        # プロジェクト管理
├── Makefile          # ビルド定義
├── requirements.txt  # Pythonライブラリ管理
├── src/              # RGBDSソースコード
├── include/          # 共通定義・定数
├── assets/           # BGタイル、Sprite、BGM・効果音素材
├── tools/            # 開発支援ツール
├── obj/              # 中間生成物
└── build/            # ビルド成果物
```

- Git管理しないディレクトリ（obj、build）は、Makefileが必要に応じて自動生成する。
- 本プロジェクトでは画像・BGM・効果音の数が少ないため、すべて `assets/` 直下で管理する。
- 用途別のサブディレクトリ（graphics/、sound/など）は作成しない。
- 将来、素材数が増えて管理が煩雑になった場合のみサブディレクトリ化を検討する。

## 開発ツール

### Python開発環境

- Pythonツールはプロジェクトルートの `.venv` を使用する。
- 必要なライブラリは `requirements.txt` で管理する。
- `.venv` はGit管理対象外とする。
- Pythonツールは `tools/` に配置する。
- Pythonツールの利用方法は `tools/README.md` に記載する。
- BG画像タイル変換ツールはタイトル専用ではなく、将来のBG画像にも使える汎用Pythonツールとして `tools/` に配置する。
- BG画像タイル変換ツールは入力画像を8×8タイルへ分割し、重複タイルを削除したタイルセット画像とBGマップファイルを生成する。

### VS Code

- RGBDS拡張を使用する。
- RGBDS拡張では、includeパスをワークスペース相対で設定する。
  - `include`
  - `src`
- `.vscode` ディレクトリはGit管理対象外とする。

## ビルド成果物の配置

- `obj/`: ビルド途中で生成される中間ファイル、およびデバッグ時のみに使用するファイルを配置する。
  - `*.o`
  - 画像素材から生成した `*.2bpp`
  - 自動生成された一時的なASM/INCファイル
  - `pocket-sweeper.sym`
  - `pocket-sweeper.map`
- `build/`: 最終的に利用するビルド成果物を配置する。
  - `pocket-sweeper.gb`
- Gitで管理するファイルは `build/` に置かない。
- 実行時に不要な自動生成物は `obj/` に置く。
- Makefileの `PROJECT` 値は `pocket-sweeper` に変更済みで、`$(PROJECT)` を利用する `obj/` / `build/` 配下の生成物名も `pocket-sweeper.*` へ追従する。

## Makefileの構成

Makefileは以下を行う。

- `src/*.asm` をアセンブルして `obj/*.o` を生成する
- 必要に応じて `assets/` の素材を `obj/` へ変換する
- `obj/*.o` をリンクしてROMを生成する
- `rgbfix` を実行して `build/pocket-sweeper.gb` を完成させる
- `clean` で `obj/` と `build/` の生成物を削除する

主なターゲットは以下とする。

- `make`: ROMをビルドする。
- `make clean`: 中間生成物とビルド成果物を削除する
- `make run`: `EMULATOR`で指定されたエミュレータでROMを起動する。ユーザーが手動で実行することを前提とする。
- `EMULATOR` は環境変数で指定する。
- `EMULATOR` が未指定の場合は `sameboy` を既定値とする。

`build/` には最終的に利用するROMのみを置き、実行時に不要な生成物は `obj/` に置く。

### ビルド確認

Codexによるビルド確認は以下までとする。

```bash
make clean
make
```

`make` が成功すればビルド確認完了とする。

### エミュレータ実行

- `make run` はユーザーが手動で実行する。
- Codexは `make run` を実行しない。
- CodexがWSL上で自動実行する際は、Windows GUIアプリ（SameBoy）の起動に環境上の制約があるためである。
- ROMの動作確認はユーザーが手動でSameBoy上で実施する。

### ROMヘッダ

- ROMヘッダはrgbfixで設定する。
- カートリッジタイプはROM ONLYとする。
- タイトルはrgbfixで `POCKET SWEEPER` を設定する。

## 想定モジュール

- `main`: 初期化、ゲームループ、状態遷移
- `hardware`: ハードウェア定義、割り込み、VBlank待機
- `input`: joypad入力取得
- `graphics`: LCD、BG、タイル、OAMの初期化と描画
- `cursor`: カーソル位置と表示
- `board`: 盤面データ初期化、地雷配置、周囲地雷数生成
- `game`: マスを開く処理、フラグ、勝敗判定
- `random`: 擬似乱数生成、シード初期化
- `ui`: 残り地雷数、メッセージなどの表示
- `sound`: APU初期化、BGM・効果音の再生制御、hUGETracker連携
- `hUGEDriver`: hUGETracker出力データを再生するサウンドドライバ
- `bgm_test`: hUGETracker ASMデータ組み込み確認用のテストBGM

## 共通ライブラリ化したい処理

- joypad入力（押下、押し始め、リピート）
- LCD・BG・Window・Spriteの初期化と描画
- タイル転送、数値・文字列表示
- VBlank同期、割り込み処理
- 擬似乱数
- OAM管理
- ゲーム状態遷移
- BGM・効果音の再生制御

ゲーム固有コードへの依存を避け、将来のRPGでも利用できる単位に分離する。

## ゲームループの概略

1. VBlankを待つ。
2. VBlank直後にVRAM/OAMへ必要な表示更新を反映する。
3. サウンド処理を更新する。
4. 入力を取得する。
5. ゲーム状態に応じてカーソル、盤面、勝敗を更新する。
6. 次のフレームへ進む。

# データ設計メモ

## セルデータ構造案

1セルを1バイトで保持する案を基本とする。

- bit 0-3: 周囲の地雷数（0～8）
- bit 4: 地雷
- bit 5: 開封済み
- bit 6: フラグ
- bit 7: 予備

実装時に、判定の単純さとROM/RAM使用量を比較して確定する。

## 盤面生成方針

- 盤面データはゲーム開始時に初期化する。
- 盤面幅、盤面高さ、地雷数は、選択した難易度に応じてゲーム開始時にWRAMへ設定する。
- 地雷は最初のマスを開くまで配置しない。
- 初回に開いたマスを除外し、現在の盤面幅、盤面高さ、地雷数を参照して地雷を配置する。
- 地雷配置済みフラグを保持し、初回配置後は再配置しない。
- 地雷配置後に各セルの周囲地雷数を生成する。
- 周囲地雷数は非地雷セルのbit 0-3へ保存し、地雷・開封済み・フラグ等のbit 4以降は壊さない。
- 地雷配置と数字生成は初回のみ実施し、その後は再生成しない。
- 地雷配置、数字生成、盤面外判定は固定値ではなく現在の盤面幅と盤面高さを参照する。

## マスを開く処理

- Aボタンで選択中マスを1マス開く。
- Aボタン押下時は、地雷配置や数字生成を呼ぶ前に選択中マスの盤面インデックスを保存し、その保存したインデックスを開封対象にする。
- 地雷未配置の場合は、先に地雷配置と数字生成を実行してから選択中マスを開く。
- 開いたマスはセルデータのbit 5を立て、bit 0-4およびbit 6以降は壊さない。
- すでに開封済みのマスを選択した場合は何もしない。
- 開いたマスのBG表示は、周囲地雷数0～8をタイル1～9へ対応させる。
- 地雷セルを開いた場合はゲームオーバー状態へ遷移し、プレイヤーが開いた地雷マスは爆発した地雷タイル12を表示する。
- 1マスのBG更新はVBlankで反映するため、必要に応じて表示更新を次フレームへ保留する。

## 0の連鎖オープン方式

- 0のマスを開いた場合は、再帰処理を使わず、キューを使った幅優先探索（BFS）で連鎖オープンする。
- 盤面サイズは最大10×10のため、最大100セルを対象とする。
- キューには盤面インデックス、またはx/y座標を保持する。実装時に扱いやすい形式を選ぶ。
- 実装では、BFSキューにx/y座標を保持し、BG表示更新キューに盤面インデックスを保持する。
- 0のマスを開いた場合、その周囲8方向のマスを確認する。
- 周囲の非地雷セルを開く。
- 周囲にある数字セルは開くが、数字セルからはさらに探索を広げない。
- 周囲にある0セルはキューへ追加し、同じ処理を繰り返す。
- すでに開封済みのセルは処理しない。
- フラグ済みセルは開かない。
- 盤面外は参照しない。
- 地雷セルは開かない。
- 1フレームで大量のBG更新が発生する可能性があるため、VBlank更新方針に従い、BG表示更新キューを使って複数フレームに分割して表示更新する。

## フラグ処理

- Bボタンで選択中の未開封マスにフラグを設置・解除する。
- 開封済みマスでは何もしない。
- フラグ設置時はセルデータのbit 6を立て、フラグ解除時はbit 6をクリアする。
- bit 0-5およびbit 7は壊さない。
- フラグ設置時はBGタイル10、フラグ解除時は未開封タイル0を表示する。
- フラグ済みセルはAボタンによる開封や0連鎖オープンでは開かない。
- フラグ数はWRAM上のカウンタで管理し、盤面を毎回走査しない。
- 残り地雷数は `地雷数 - フラグ数` とし、ステータスバーのMINE表示へ反映する。
- ゲーム開始時とRESTART時は、現在選択中の難易度の地雷数を `MINE` 表示へ反映する。
- フラグ設置時はMINE表示を1減らし、フラグ解除時はMINE表示を1増やす。
- 残り地雷数が0のときは新しいフラグを設置しない。ただし、既に設置済みのフラグ解除は可能とする。
- MINE表示は000未満にならない。
- 開封済みマス、ゲームオーバー状態、ゲームクリア状態ではフラグ操作できないため、MINE表示も変化させない。
- MINE表示はフラグ数の変更時とリスタート時のみ更新する。

## 経過時間表示

- 初版では手数表示ではなく、経過時間表示を採用する。
- ステータスバーの `TIME:000` は制限時間ではなく、経過時間を表す。
- 経過時間は、最初にマスを開いた時点からカウント開始する。
- 経過時間は通常プレイ中のみ1秒ごとに加算する。
- ポーズ中は経過時間を停止する。
- ゲームオーバーまたはゲームクリア時点で経過時間を停止する。
- 表示は3桁、最大999秒とし、999秒を超えた場合は999のままにする。
- 新規ゲーム開始時とRESTART時は、経過時間を000へ初期化する。
- 制限時間は初版では実装しない。
- 手数表示は初版では実装しない。
- デバッグ機能として、経過時間の初期値を `DEBUG_INITIAL_TIME` で変更できる。
- `DEBUG_INITIAL_TIME` の通常値は0とし、通常ビルドでは経過時間を000から開始する。
- 999秒到達確認時のみ、`DEBUG_INITIAL_TIME` を995などへ一時的に変更して確認する想定とする。
- `DEBUG_INITIAL_TIME` が999を超える値の場合は、999として扱う。

## ゲームオーバー判定

- Aボタンで開いたマスが地雷だった場合、ゲームオーバー状態へ遷移する。
- プレイヤーが開いた地雷マスは爆発した地雷タイル12を表示する。
- その他の地雷マスは地雷タイル11を表示する。
- 地雷ではないマスに置かれていたフラグは誤ったフラグタイル13を表示する。
- ゲームオーバー時は、盤面に重ねず、盤面下のBG座標y=14付近に `GAME OVER` を中央寄せで表示する。
- ゲームオーバー後は、カーソル移動、Aボタン、Bボタンによる盤面操作を無効にする。
- ゲームオーバー時の盤面表示更新はBG更新キューに積み、VBlank中に複数フレームへ分割して反映する。

## クリア判定

- クリア条件は、地雷以外のすべてのマスを開くこととする。
- Aボタンでマスを開いた後、ゲームオーバー状態でない場合にクリア判定を行う。
- 0連鎖オープンで複数マスが開いた場合も、連鎖処理後にクリア判定を行う。
- クリア判定は固定値ではなく、`盤面マス数 - 地雷数` の非地雷マスがすべて開いていればクリアとする。
- クリアした場合はゲームクリア状態へ遷移する。
- ゲームクリア後は、カーソル移動、Aボタン、Bボタンによる盤面操作を無効にする。
- クリア時は、盤面に重ねず、ゲームオーバー表示と同じ盤面下のBG座標y=14付近に `CLEAR` を中央寄せで表示する。
- クリア表示はBG更新キューの盤面更新が完了した後、VBlank中に反映する。

## ゲーム終了後のタイトル復帰

- ゲームオーバー状態、またはゲームクリア状態のときにSTARTボタンを押すと、タイトル画面へ戻る。
- ゲームオーバー画面またはゲームクリア画面でSTARTボタンを押すとタイトル画面へ戻る。
- START入力は `wJoyPressed` を使い、押しっぱなしで連続遷移しないようにする。
- タイトル画面へ戻る時点では、新規ゲームの盤面初期化は行わない。
- タイトル画面へ戻るときは、タイトル用タイル、BGマップ、OAMを再初期化し、タイトルロゴ、`PRESS START`、`©2026 AKIHIRO SEKINE` を再描画する。
- タイトル画面でSTARTボタンを押すと難易度選択画面へ進み、難易度選択画面でAボタンまたはSTARTボタンを押すと新しいゲームを開始する。

## タイトル画面・ポーズメニュー

- タイトル画面は「画面遷移処理」と「表示処理」を分けて実装する。
- まずはタイトル画面に中身を表示しない状態でもよいため、状態遷移だけを先に作る。
- 起動時はタイトル画面状態から開始する。
- タイトル画面状態の初期実装ではBGを空白にし、タイトルロゴ、`PRESS START`、著作権表示はまだ表示しない。
- タイトル画面状態では、カーソル移動、Aボタン、Bボタンによる盤面操作を無効にする。
- タイトル画面でSTARTボタンを押すと難易度選択画面へ遷移する。
- タイトル画面からゲーム本編へ直接遷移しない。
- タイトル画面の表示内容は後続タスクで実装する。
- ゲーム終了後やポーズメニューからタイトル画面へ戻れるようにする。
- ゲーム終了後やポーズメニューの `BACK TO TITLE` ではタイトル画面へ戻る。
- `BACK TO TITLE` 後は、タイトル画面でSTARTボタンを押すと再び難易度選択画面へ進む。
- 難易度選択画面では `SELECT LEVEL`、`EASY`、`NORMAL`、`HARD` を表示する。
- 難易度選択画面の初期選択は `EASY` とする。
- 難易度選択画面の選択カーソルは既存のポーズメニューと同じ `▶` を使用する。
- 難易度選択画面では十字キー上下で選択項目を変更する。
- 難易度選択画面ではAボタンまたはSTARTボタンで選択中の難易度を決定し、ゲーム本編へ遷移する。
- 難易度選択画面でBボタンを押すとタイトル画面へ戻る。
- 難易度選択画面からゲーム本編へ遷移するときは、新規ゲームとして盤面を初期化する。
- 難易度選択画面からゲーム本編へ遷移するときは、現在選択中の難易度、盤面幅、盤面高さ、地雷数、盤面データ、地雷配置済みフラグ、カーソル位置、フラグ数、残り地雷数表示を初期化する。
- 難易度選択画面からゲーム本編へ遷移するときは、ステータスバーと未開封盤面をVBlank中に描画する。
- 通常プレイ中にSTARTボタンを押した場合は、即リスタートせずポーズメニューを表示する。
- ポーズメニュー項目は `RESUME`、`RESTART`、`BACK TO TITLE` とする。
- `RESUME` はポーズメニューを閉じて通常プレイに戻る。
- ポーズメニュー中は十字キー上下で項目を選択し、AボタンまたはSTARTボタンで決定する。
- ポーズメニュー中のBボタンは `RESUME` と同じ動作とする。
- `RESUME` は盤面状態、カーソル位置、フラグ状態、残り地雷数を維持して通常プレイへ戻る。
- `RESTART` は現在のゲームを破棄し、現在選択中の難易度を維持して新しいゲームを開始し、タイトル画面には戻らない。
- `BACK TO TITLE` は現在のゲームを破棄してタイトル画面へ戻る。
- ポーズ中はカーソル移動、Aボタンによるマス開封、Bボタンによるフラグ操作を行わない。
- ポーズ中はカーソルSpriteを非表示にする。
- ポーズメニューは盤面中央付近へウィンドウ枠を表示し、その内側に項目テキストを表示する。
- ウィンドウ枠用タイルはPNG素材から作成し、枠、角、内側塗りつぶし用タイルを用意する。
- ウィンドウ枠は盤面の一部を隠してよい。
- ポーズメニューの選択カーソルは `▶` を使用する。
- `▶` はUIフォントに追加し、PNG素材から生成する。
- `▶` はプログラム中の直接タイル定義ではなく、フォント生成対象またはPNG素材へ追加して文字描画で表示する。
- `>` は今後使用しない。
- ポーズメニュー表示時は、ウィンドウ枠の内側に `RESUME`、`RESTART`、`BACK TO TITLE` を表示する。
- 十字キー上下で選択項目が変わったときは、選択中項目の左にある `▶` の位置を更新する。
- ポーズメニュー表示・選択更新はゲーム進行が停止しているため、VBlank分割更新の例外としてLCD OFF中にBGを一括描画してよい。
- ポーズメニューの初回表示時はLCD OFF中にウィンドウ枠と項目文字を一括描画する。
- ポーズメニュー表示後の選択変更時は、画面全体を再描画せず、旧選択行の `▶` を空白タイル14へ戻し、新選択行へ `▶` を描画する。
- ポーズメニュー表示時は、盤面セル選択用カーソルSpriteのOAMをクリアする。
- `RESUME` で戻るときは、LCD停止中にポーズメニュー領域、ステータスバー、現在の盤面状態、カーソルOAMを一括再描画する。
- ポーズ解除時は通常の1マスずつのBG更新キューを使わず、WRAM上の盤面状態から直接BGへ復元する。
- 通常プレイ中のマス開封や0連鎖オープンのVBlank分割更新方針は維持する。
- ゲームオーバーまたはゲームクリア後のSTARTボタンは、タイトル画面へ戻る。
- ゲームオーバーまたはゲームクリア後にタイトル画面へ戻る時点では、新規ゲームの盤面初期化は行わない。
- タイトル画面へ戻るときは、タイトル用タイル、BGマップ、OAMを再初期化し、タイトルロゴ、`PRESS START`、`©2026 AKIHIRO SEKINE` を再描画する。
- SELECTボタンの役割は未定のままとする。
- タイトル画面にはレベル選択、OPTIONS、RECORDSは表示しない。
- タイトル画面には難易度選択項目を表示しない。
- 難易度選択はタイトル画面とは別の画面として追加する。

## 難易度選択画面

- タイトル画面でSTARTボタンを押すと難易度選択画面へ遷移する。
- 難易度選択画面では以下を表示する。

```text
SELECT LEVEL

▶ EASY
  NORMAL
  HARD
```

- 難易度は以下とする。
  - EASY: 盤面8×8、地雷10個
  - NORMAL: 盤面9×9、地雷15個
  - HARD: 盤面10×10、地雷20個
- 十字キー上下で選択項目を変更する。
- AボタンまたはSTARTボタンで選択中の難易度を決定し、ゲームを開始する。
- Bボタンでタイトル画面へ戻る。
- 選択カーソルは既存のポーズメニューと同じ `▶` を使用する。
- 段階実装では、`SELECT LEVEL`、`EASY`、`NORMAL`、`HARD` の表示、`▶` カーソル表示、上下キーの選択変更、AボタンまたはSTARTボタンでのゲーム開始、Bボタンでのタイトル復帰までを先に実装する。
- 難易度確定時に、現在の難易度、盤面幅、盤面高さ、地雷数をWRAMへ保持する。
- 現時点では、MINE表示、フラグ上限、地雷配置数は現在の地雷数を参照する。
- 盤面データ領域は最大10×10の100セルを確保し、盤面初期化時は100セル分をクリアする。
- 盤面描画は現在の盤面幅・盤面高さに応じた未開封マス描画と全体再描画に対応する。
- クリア判定ロジックは、現在の盤面セル数から地雷数を引いた非地雷マス数を基準にする。
- 0連鎖オープンの周囲セル判定は現在の盤面幅・盤面高さを参照し、範囲外セルをBG表示更新キューへ積まない。
- カーソル移動範囲は現在の盤面幅・盤面高さを参照する。
- 盤面左上BG座標は現在の盤面幅から算出し、EASYはX=6、NORMAL/HARDはX=5、Yは既存の4を使用する。初期盤面描画、1マス更新、全体再描画、ゲームオーバー時表示、カーソルSpriteは同じ盤面左上座標を参照する。
- BFSキュー、表示更新キュー、盤面データ領域は最大100セル分を確保し、キュー投入上限は100セル対応の容量定数を参照する。
- ポーズメニューのRESTARTは現在の難易度を維持し、難易度に応じた盤面幅、盤面高さ、セル数、地雷数、盤面左上座標を再設定してから盤面を初期化する。
- 数字生成処理は不具合修正済み。周囲地雷数は低ニブルだけを更新し、BG表示位置計算も現在の盤面幅を参照する。
- ゲーム開始時は、選択した難易度を現在の難易度としてWRAMに保持する。
- ゲーム開始時は、選択した難易度に対応する盤面幅、盤面高さ、地雷数をWRAMに保持する。

## セーブ・記録保存方針

- 初版ではセーブ機能は実装しない。
- 初版ではハイスコア、ベストタイム、記録保存機能は実装しない。
- ゲームボーイのSRAM保存は使わず、ROM ONLY方針を維持する。
- 将来的に必要になった場合のみ、別タスクとして再検討する。

## タイトル画面表示

- タイトルロゴ画像は `assets/title.png` を使用する予定とする。
- タイトルロゴ画像サイズは160×48とする。
- タイトルロゴは画面幅160pxいっぱいのロゴとして扱い、BG座標は画面左端の `(0, 1)` 付近から表示する想定とする。
- タイトルロゴのBGマップ幅は20タイルとする。
- タイトルロゴ画像はBG画像タイル変換ツールで `obj/title_tiles.png` と `obj/title_map.bin` を生成し、`obj/title_tiles.png` をrgbgfxで `obj/title_tiles.2bpp` へ変換してROMに組み込む。
- タイトルロゴ用タイルは、既存の盤面タイル、UIフォント、カーソルSpriteタイルと衝突しないVRAMタイル番号へ配置する。
- タイトルロゴ表示時は、`obj/title_map.bin` をもとにBG座標 `(0, 1)` 付近へBGマップを配置する。
- `PRESS START` は文字描画で表示する。
- `©2026 AKIHIRO SEKINE` は文字描画で表示する。
- タイトル画面中はカーソルSpriteを非表示にする。
- タイトル画面から難易度選択画面へ遷移するときは、タイトルロゴとタイトル文字の表示領域を消去し、難易度選択画面用の文字表示へ切り替える。
- タイトル画面にはレベル選択、OPTIONS、RECORDSは表示しない。
- タイトル画面には難易度選択項目を表示しない。
- 難易度選択画面からゲーム本編へ遷移するときは、難易度選択画面の表示領域を消去し、ゲーム本編用のステータスバー、盤面、カーソル表示へ戻す。

## BG画像タイル変換ツール

- BG画像タイル変換ツールは、タイトルロゴだけでなく将来のBG画像にも使える汎用ツールとして扱う。
- ツールは `tools/convert_bg_image.py` に配置する。
- 入力はIndexed Color PNG、使用パレットインデックス0〜3の4色、アルファチャンネルなし、幅と高さが8の倍数であることを必須とする。
- 入力画像を8×8タイルへ分割する。
- タイルは左上から右下へ走査する。
- 重複タイルを削除する。
- 重複削除後のタイルセット画像を生成する。
- 出力されるタイルセットPNGもIndexed Color、4色パレットを維持する。
- 元画像上で各タイルをどう並べるかを表すBGマップファイルを生成する。
- BGマップファイルは1タイル1バイトのバイナリ形式とする。
- 重複削除後のタイル数が256を超える場合はエラーにする。
- 自動生成物は `obj/` へ出力し、原則としてGit管理しない。
- ツールの使い方は `tools/README.md` に記載する。
- `make` はタイトル画面用に `obj/title_tiles.png`、`obj/title_map.bin`、`obj/title_tiles.2bpp` を生成する。
- `make clean` はタイトル画面用の自動生成物も削除する。

## 擬似乱数

- 擬似乱数生成器を使用する。
- 乱数シードはゲーム開始から最初にマスを開くまでのフレーム数を利用する。
- フレームカウンタは毎フレーム更新する。
- 初回にマスを開いた時点のフレーム数を初期シードとして使用する。

## 検証・デバッグ

- 開発中はデバッグ表示モードを使用する場合がある。
- `DEBUG_SHOW_MINES` を有効にすると、地雷配置と数字生成後に地雷セルと周囲地雷数を画面上に表示する。
- 通常プレイに近い確認では `DEBUG_SHOW_MINES` を無効化する。
- デバッグ表示は、地雷配置と同一フレームではなく次のVBlank以降に1行ずつBGへ反映する。
- デバッグ表示は動作確認用であり、最終版では無効化する。

## RAM使用方針

- 盤面データはWRAMに保持し、最大10×10の100セルまで扱える領域を確保する。
- 現在選択中の難易度をWRAMに保持する。
- 現在の盤面幅、盤面高さ、地雷数をWRAMに保持する。
- 地雷配置済みフラグをWRAMに保持する。
- ゲーム開始から初回Aボタン押下までのフレームカウンタと乱数シードをWRAMに保持する。
- BG表示更新をVBlankへ送るための表示更新キューと必要に応じた上書きタイル番号をWRAMに保持する。表示更新キューは最大100セル分を確保する。
- 表示更新キューの上書きタイル番号は、0を自動計算、1以上を `tile + 1` として扱う。
- 0連鎖オープン用のBFSキュー領域をWRAMに保持する。BFSキューは最大100セル分を確保する。
- カーソル位置、ゲーム状態、残りマス数、フラグ数、乱数状態もWRAMに保持する。
- フラグ数はWRAM上のカウンタで保持し、残り地雷数表示の更新に使用する。
- MINE表示更新の保留フラグをWRAMに保持し、VBlank中にステータスバーの数字3桁のみ更新する。
- 経過時間の秒数、1秒加算用フレームカウンタ、計測中フラグをWRAMに保持する。
- TIME表示更新の保留フラグをWRAMに保持し、VBlank中にステータスバーの数字3桁のみ更新する。
- Joypad入力は共通 `input` モジュールで管理し、`wJoyCurrent`（押下中）、`wJoyPrevious`（前フレーム）、`wJoyPressed`（今フレームで新しく押したボタン）をWRAMに保持する。
- Joypadの各状態は、bit 0から順に Right、Left、Up、Down、A、B、Select、Startを表す。ゲーム固有処理は `input` モジュールに含めない。
- カーソル位置は `wCursorX`、`wCursorY` に盤面内座標として保持し、範囲は現在の盤面幅・盤面高さを参照する。
- 盤面内座標から盤面データのインデックスへの変換は `index = y * 現在の盤面幅 + x` とする。
- タイトル画面、通常プレイ、ポーズ、ゲームオーバー、ゲームクリアなどの画面・ゲーム状態をWRAM上の状態変数で管理する。
- タイトル画面状態かどうかをWRAMに保持し、タイトル画面中の盤面操作とカーソル表示を無効化する。
- 難易度選択画面状態かどうかと、難易度選択画面で選択中の項目をWRAMに保持する。
- ポーズメニューでは選択中の項目をWRAMに保持する。
- フレームごとの一時値はHRAMの利用も検討する。
- スタック領域を圧迫しないよう、大きな一時データや深い呼び出しを避ける。

## VRAM / BG / Spriteの使い分け方針

- VRAM: BGタイル（盤面・UI）とSpriteタイル（カーソル等）のタイルデータを格納する。
- BGマップ: 盤面と固定UIを表示する。
- Sprite: カーソル表示を基本とし、必要に応じて演出にも使用する。
- Window: UI分離に有効な場合に採用するが、初期実装では必須としない。
- VRAM/OAMの更新はLCDの制約を守り、原則としてVBlank中に行う。

### 初期画面のBG配置

- ステータスバーはBG座標 `(1, 0)` から `MINE:xxx TIME:000` を表示し、`MINE` は現在の地雷数から初期化し、`TIME` は経過時間0秒から初期化する。
- 盤面は現在の盤面幅・盤面高さに応じて中央寄せで表示する。
- 8×8、9×9、10×10の各盤面で、盤面左上のBG座標を計算して未開封タイルを表示する。
- BG座標と盤面サイズはタイル単位で扱う。
- 初期画面はステータスバーと盤面にBG、カーソルにSpriteを使用し、Windowは使用しない。
- BGタイルはタイル番号0～13を盤面用、14をBG消去用の空白、15～20をポーズメニュー枠用、21以降をUIフォントに使用する。
- カーソル用Spriteは別画像として管理し、BGタイル番号とは独立してVRAMのタイル52～55へ配置する。

### カーソル表示

- カーソルは16×16・4Spriteとする。
- カーソル用Spriteは `assets/cursor.png` に管理する。
- OAMのSprite 0～3をカーソル表示に使用する。
- カーソル用SpriteのOAMタイル番号は、左上52、右上53、左下54、右下55とする。
- Sprite表示では `rOBP0` を使用し、BG用の `rBGP` とは別に設定する。
- カーソル用Spriteでは色番号0を透明、色番号1を最も明るい色として表示する。
- 初期位置は盤面左上の `(0, 0)` とする。
- 盤面内座標からOAM座標への変換は、Xを `(現在の盤面左上BG X + wCursorX) * 8 + 8`、Yを `(現在の盤面左上BG Y + wCursorY) * 8 + 16` とする。
- 16×16外枠の左上Spriteは、選択中8×8マスを囲むため、この基準座標からX/Yとも4px左上へオフセットして表示する。
- `wJoyPressed` の十字キー入力で1回の押し始めにつき1マス移動し、X/Yとも現在の盤面幅・盤面高さの範囲外へ移動させない。
- OAMはLCD停止中に初期化し、カーソルのSprite 0～3への反映はVBlank中に行う。

### VBlank更新方針

- VRAMおよびOAMへの更新は、原則としてVBlank期間内に行う。
- VBlank中にBG更新とOAM更新を同じフレームで行う場合は、VBlank直後にまとめて実行し、その後に時間のかかるゲームロジックを実行する。
- `hUGE_dosound` はVRAM/OAM更新の後、ゲームロジックの前に毎フレーム1回呼び出す。
- サウンド更新はAPUレジスタ更新のみを行い、VRAM/OAM更新キューとは独立させる。
- VBlank内で完了しない可能性がある大量のBG更新は、1フレームで無理に実行しない。
- 大量のBG更新が必要な場合は、必要に応じて複数フレームへ分割して反映する。
- 例外として、ポーズメニューのようにゲーム進行を停止している画面では、LCD OFF中にBGを一括描画してよい。
- 時間のかかるゲームロジックと大量のVRAM更新を同一フレームへ集中させないよう設計する。
- デバッグ表示など一括描画を行う処理も、この方針に従う。

## サウンド設計

- hUGEDriver本体は `src/hUGEDriver.asm`、hUGETracker用マクロとノートテーブルは `include/hUGE.inc` / `include/hUGE_note_table.inc` に配置する。
- hUGETrackerから出力したASMデータは `src/*.asm` として配置し、通常のRGBASMビルド対象へ含める。
- 曲データはROM ONLY方針を維持するため、当面は `ROM0` セクションへ配置する。
- `src/sound.asm` がAPU初期化、曲開始、毎フレーム更新を担当する。
- `Sound_Init` はNR52/NR50/NR51を初期化し、再生中フラグをクリアする。
- `Sound_PlayTestBgm` はテストBGMの曲ディスクリプタをHLに設定して `hUGE_init` を呼び、再生中フラグを立てる。
- `Sound_Update` は再生中のみ `hUGE_dosound` を呼び出す。
- ゲーム開始時およびリスタート時に `Sound_PlayTestBgm` を呼び、テストBGMを再生開始する。
- `hUGE_dosound` はAF/BC/DE/HLを破壊するため、呼び出し側はレジスタ値を跨いで依存しない。

### BGMと効果音の再生制御方針

- 初版では、BGMはhUGEDriverで再生する。
- hUGEDriverは1つの曲状態を持つ前提で扱い、効果音再生のたびに `hUGE_init` で別曲へ切り替える運用は採用しない。
- `hUGE_dosound` は毎フレーム1回だけ呼び出し、BGM更新を担当する。
- 効果音は初版では複雑なミキシングを行わず、短時間だけAPUレジスタを直接書き換える軽量SFXとして再生する。
- 効果音更新は `hUGE_dosound` の後に行い、効果音が使うチャンネルだけをそのフレームで短時間上書きする。
- UI効果音は短いため、BGMの該当チャンネルが一瞬上書きされることは許容する。
- BGM制作では、初版は可能な範囲でPulse2とWaveを中心に使い、Pulse1はUI効果音用に上書きされても破綻しにくい使い方にする。
- 効果音制作で作成したJSONおよびhUGEDriver ASMは、単体確認用テストROMでの確認に使う。本体組み込み時は、同じJSON方針を正本としつつ、初版ではSFX用APU書き込みデータとして扱う。

チャンネル割り当て方針:

| チャンネル | 初版方針 |
| --- | --- |
| Pulse1 | UI効果音の主チャンネル。カーソル移動、決定、キャンセル、マス開封、旗操作などの短いPulse音に使う。 |
| Pulse2 | BGMの主旋律または伴奏の中心として使う。 |
| Wave | BGMの低音、持続音、補助メロディに使う。 |
| Noise | 地雷爆発、ゲームオーバーなどノイズ系効果音に使う。通常BGMでは初版では原則使わない。 |

効果音の優先順位:

1. 地雷爆発、ゲームオーバー
2. クリア
3. マス開封、旗設置、旗解除
4. 決定、キャンセル
5. カーソル移動

- 同じフレームで複数の効果音要求が発生した場合は、最も優先度の高い1つだけを鳴らす。
- 効果音キューは初版では持たない。
- 効果音再生中に高優先度の効果音が要求された場合は、高優先度の効果音で上書きする。
- 効果音再生中に同等以下の優先度の効果音が要求された場合は、初版では無視する。
- 地雷爆発やゲームオーバーなど重要な効果音では、必要に応じてBGMを停止または該当チャンネルを強く上書きしてよい。

未確定事項:

- BGM制作後、Pulse1をどの程度BGMに使えるかは実際の曲で確認する。
- SFX用APU書き込みデータをJSONから直接生成するか、既存のhUGEDriver ASM生成結果から派生させるかは本体組み込み時に決める。
- クリア時にBGMを停止するか、クリアジングルをBGM扱いで再生するか、短い効果音扱いにするかはクリアBGM制作時に決める。

### BGM・効果音制作フロー

- BGM・効果音制作では、ChatGPTで楽曲定義JSONを作成し、PythonツールでhUGEDriver用データへ変換する運用を採用する。
- 楽曲の正本はJSONとする。
- hUGETracker上で最初から手作業で打ち込むのではなく、まずJSONで曲の構造を管理する。
- hUGETracker上で直接微調整することは基本方針としない。
- 再生確認で問題があった場合は、hUGETracker上で修正するのではなく、JSONを修正して再生成する。
- hUGETrackerは主に `.uge` 読み込み確認、仕様調査、必要時の手動確認に使う。
- hUGETrackerには `.uge` からASMを自動ExportするCLIが確認できないため、通常フローへ組み込まない。
- 楽曲定義JSONはChatGPTが作成・編集しやすい中間形式として扱い、`assets/` 直下に配置する。
- JSONからhUGEDriver用RGBDS ASMを直接生成する主フローでは `tools/json_to_huge_asm.py` を使う。
- ASMからサウンド再生確認用テストROMを生成する主フローでは `tools/build_sound_test_rom.py` を使う。
- 既存の `tools/json_to_uge.py` は、hUGETracker確認用・互換確認用として残す。
- `.uge` 生成は主フローではなく補助フローとする。
- `tools/json_to_uge.py` の使い方は `tools/README.md` に記載する。
- 初版では完全な自動作曲ではなく、短いBGMや効果音の下書きを作る用途とする。
- JSON仕様は最初から複雑にしすぎず、曲名、テンポ、パターン、チャンネル、ノート、長さ、音色番号程度を扱う。
- `.uge` 形式の詳細が不明な部分は、既存のhUGETracker出力ファイルやサンプルを確認しながら実装する。
- 不明点は推測で確定せず、WBSまたはTODOとして記録する。
- 各BGM・効果音制作では、JSON作成、JSON修正、`tools/json_to_huge_asm.py` によるASM生成、`tools/build_sound_test_rom.py` によるテストROM生成、Game Boyエミュレータでの確認、必要に応じたJSON再修正のサイクルで制作する。
- サウンド制作では、原則としてhUGETracker上で直接編集するのではなく、JSONを修正して再生成する運用を維持する。
- WBS上では、BGM制作と効果音制作はJSON作成・調整・テストROM確認までを扱い、サウンド実装は作成済みのBGM・効果音をゲーム本体へ組み込み、適切なタイミングで再生する処理を扱う。
- BGMと効果音の同時再生、優先順位、チャンネル割り当ては未確定のため、サウンド実装では最初に再生制御方針を決める。

目標フロー:

```text
JSON
  ↓
hUGEDriver用RGBDS ASMを生成
  ↓
サウンド確認用テストROMを生成
  ↓
SameBoyなどのGBエミュレータで再生確認
  ↓
問題があればJSONを修正して再生成
```

`tools/json_to_uge.py`:

- 楽曲定義JSONをUTF-8で読み込み、hUGETracker v1.0.11向けのSong Version 6 `.uge` を書き出す。
- コマンドライン引数は、入力JSON、出力 `.uge` の順に指定する。
- 使用例:

```bash
python tools/json_to_uge.py assets/test_draft.json assets/test_draft.uge
```

- サンプルJSONは `assets/test_draft.json` に配置する。
- サンプルJSONから生成した `.uge` は `assets/test_draft.uge` に配置する。
- hUGETrackerでの読み込み、保存、RGBDS ASM Export確認は後続WBSで実施する。

初版 `tools/json_to_uge.py` の対応範囲:

- JSON仕様 `version = 1` を読み込む。
- `title` を `.uge` の曲名として保存する。
- `type` は `bgm` / `sfx` のバリデーション対象とし、`.uge` には直接保存しない。
- `tempo` はSong Version 6の `TicksPerRow` として保存する。
- `order` と `patterns` から4チャンネル分の `OrderMatrix` と64行固定patternを生成する。
- `length` は行数として扱い、音符セル1行と残りの空行へ展開する。
- noteは `C3`～`B8`、シャープ表記、`rest` を扱う。
- effectは `effect: null`、`effect_param: null` のみ扱い、`.uge` では `EffectCode = 0`、`EffectParams.Value = 0` を出力する。
- `wave` / `noise` が未使用の場合は空pattern参照と空patternを出力する。
- Instrument IDは1～15のみ許可し、0はJSON入力では禁止する。
- Instrument詳細パラメータはJSONでは扱わず、hUGETracker初期値相当で出力する。

初版 `tools/json_to_uge.py` の未対応範囲:

- hUGETracker GUIでの読み込み・保存・ASM Exportの自動確認。
- 非null effect。
- Instrument詳細パラメータ編集。
- Wave table編集。
- Routine、Instrument subpattern編集。
- 64行を超えるpattern。

`tools/json_to_huge_asm.py`:

- 楽曲定義JSONをUTF-8で読み込み、hUGEDriver用RGBDS ASMを直接書き出す。
- コマンドライン引数は、入力JSON、出力ASMの順に指定する。
- song descriptorのラベル名は、出力ASMファイル名からRGBDS symbolとして安全な名前を生成する。
- 使用例:

```bash
python tools/json_to_huge_asm.py assets/test_draft.json obj/test_draft.asm
```

- サンプルJSONから生成したASMは `obj/test_draft.asm` に配置する。
- 自動生成ASMは `obj/` 直下へ出力し、サブディレクトリは使わない。
- hUGETracker Export ASMとの比較は `obj/test_draft.asm` と `obj/test_draft_huge.asm` で実施済みである。

初版 `tools/json_to_huge_asm.py` の対応範囲:

- `include "hUGE.inc"`、`SECTION`、song descriptor、order、pattern、instrument、routine、waveラベルを出力する。
- noteはJSON表記からRGBDS ASM表記へ変換する。例: `C4` は `C_4`、`C#4` は `C#4`、`rest` は `___`。
- `length` は行数として扱い、音符行と空行へ展開する。
- patternは64行固定とし、不足分は `dn ___,0,$000` で埋める。
- effectは `effect: null`、`effect_param: null` のみ扱い、ASMでは `$000` を出力する。
- `wave` / `noise` が未使用の場合は空patternを出力する。
- duty instrumentsは使用された最大Instrument IDまで出力する。
- wave instruments / noise instrumentsは初版では未使用前提で空ラベルを出力する。
- routinesは16個の `ret` routineを出力する。

初版 `tools/json_to_huge_asm.py` の未対応範囲:

- 非null effect。
- Wave / Noise instrumentsの実質利用。
- Wave tableの実質利用。
- Routine、Instrument subpattern編集。
- サウンド再生確認用テストROM生成。

hUGETracker Export ASMとの比較結果:

- 比較対象は `obj/test_draft.asm` と `obj/test_draft_huge.asm` とする。
- `obj/test_draft.asm` は `tools/json_to_huge_asm.py` で `assets/test_draft.json` から生成したASMである。
- `obj/test_draft_huge.asm` は `assets/test_draft.uge` をhUGETracker v1.0.11でExportした比較用ASMである。
- song descriptorは、tempo、order参照、instrument参照、routine参照、wave参照が一致した。
- order count、order1～order4は一致した。
- pattern数はP0～P3の4patternで一致した。
- 各patternは64行で、note、instrument、effect、effect parameterが一致した。
- duty instrumentsはInstrument 1～2の出力内容が一致した。
- wave instruments / noise instrumentsは未使用の空ラベルとして一致した。
- routinesは16個の `ret` routineとして一致した。
- wavesは未使用の空ラベルとして一致した。
- コメント、空白、インデント、ラベル名の差分は比較上許容する方針だが、今回の比較では再生に影響する差分は確認されなかった。
- 今回の比較では `tools/json_to_huge_asm.py` の修正は不要だった。
- 将来、非null effect、Wave / Noise instruments、Wave table、routine、instrument subpatternを対応する場合は、同様にhUGETracker Export ASMと比較する。

`tools/build_sound_test_rom.py`:

- hUGEDriver用RGBDS ASMから、サウンド確認専用の最小Game Boy ROMを生成する。
- 本ツールはASMからROMを生成することだけを担当し、JSONの読み込みやASM生成は行わない。
- エミュレータ起動は本ツールの責務に含めない。
- コマンドライン引数は、入力ASM、出力ROMの順に指定する。
- 使用例:

```bash
python tools/build_sound_test_rom.py obj/test_draft.asm build/test_sound.gb
```

- 入力ASMはhUGEDriver用RGBDS ASMとし、song descriptorのglobal labelを含む必要がある。
- 出力ROM名は固定せず、コマンドライン引数で指定する。
- Pocket Sweeperプロジェクトでは、テストROMは `build/` に出力する想定とする。
- `build/` には最終成果物である `.gb` のみを出力し、`.map` / `.sym` などのビルド副産物は `obj/` に出力する。

`tools/build_sound_test_rom.py` の処理フロー:

1. 入力ASMからsong descriptor labelを読み取る。
2. 入力ASMを `INCLUDE` する最小ROM用ASMを `obj/` に生成する。
3. 最小ROM用ASMでAPUを初期化する。
4. 起動後に `hUGE_init` で指定曲を開始する。
5. メインループでVBlankを待ち、毎フレーム `hUGE_dosound` を呼び出す。
6. `src/hUGEDriver.asm` を別objectとして組み込む。
7. `rgbasm`、`rgblink`、`rgbfix` をPythonから呼び出す。
8. 指定した出力先にROMを出力し、`obj/` に中間ASM / OBJ / map / symを出力する。

生成物:

- `obj/<rom名>_sound_test.asm`: 入力ASMをincludeする最小ROM用ASM。
- `obj/<rom名>_sound_test.o`: 最小ROM用ASMのobject。
- `obj/<rom名>_hUGEDriver.o`: hUGEDriverのobject。
- `obj/<rom名>.map`: link map。
- `obj/<rom名>.sym`: symbol file。
- `<出力ROM>.gb`: サウンド確認用Game Boy ROM。

想定する制作フロー:

1. ChatGPTで楽曲定義JSONを作成する。
2. JSONからhUGEDriver用RGBDS ASMを生成する。
3. 生成したASMからサウンド再生確認用テストROMを生成する。
4. SameBoyなどのGBエミュレータで再生確認する。
5. 問題があればJSONを修正して再生成する。
6. 問題がなければ生成したASMをROMへ組み込む。
7. `tools/json_to_uge.py` はhUGETracker確認用・互換確認用の補助フローとして使用する。

初版で使用する効果音一覧:

| 効果音 | 使用場面 | 方針 |
| --- | --- | --- |
| カーソル移動 | 難易度選択、通常プレイの盤面カーソル移動、ポーズメニュー項目移動 | 画面ごとに分けず共通化する。 |
| 決定 | タイトル画面START、難易度決定、ポーズメニュー決定、ゲーム終了後のタイトル復帰 | START / Aによる画面遷移・項目決定で共通化する。 |
| キャンセル | 難易度選択画面のB戻り、ポーズメニューのBによるRESUME | 戻る・閉じる操作として共通化する。 |
| マスを開く | 通常プレイで非地雷マスを開く | 1マス開封と0連鎖オープン開始時で共通化する。 |
| 旗を立てる | 未開封マスへのフラグ設置 | 旗解除とは別の短い音にする。 |
| 旗を外す | フラグ済みマスの解除 | 旗設置とは別の短い音にする。 |
| 地雷爆発 | 地雷マスを開いてゲームオーバーになる瞬間 | ゲームオーバー効果音とは別に、爆発の操作結果として鳴らす。 |
| クリア | ゲームクリア状態へ遷移する瞬間 | クリア表示と合わせて鳴らす。 |
| ゲームオーバー | ゲームオーバー状態へ遷移した後 | 地雷爆発の直後または短い間隔で鳴らす想定とする。 |

初版では、0連鎖オープン専用効果音は作成しない。0連鎖で開く各マスに効果音を鳴らすと連続再生で耳障りになりやすく、初版ではAボタンで開封を開始したタイミングの「マスを開く」効果音に集約する。

カーソル移動効果音:

- 正本JSONは `assets/se_cursor.json` とする。
- 生成ASMは `obj/se_cursor.asm` とする。
- 確認用ROMは `build/se_cursor.gb` とする。
- 用途は、難易度選択、通常プレイの盤面カーソル移動、ポーズメニュー項目移動で共通利用する。
- 初版はPulse1のみを使い、高音 `C8`、`tempo = 1`、短い減衰のPulse Instrumentで構成する。
- Instrument詳細は `duty = 0`、`initial_volume = 3`、`envelope_direction = "down"`、`envelope_sweep = 1` とし、余韻を抑えた軽い「ピッ」という音を狙う。

### 楽曲定義JSON仕様

- 楽曲定義JSONは `assets/` 直下に配置する。
- ファイル名は用途が分かる名前にする。
  - 例: `assets/bgm_title.json`
  - 例: `assets/bgm_game.json`
  - 例: `assets/se_cursor.json`
- JSONから生成した `.uge` も `assets/` 直下に配置する。
- `.uge` はhUGETrackerで再生確認・微調整するための生成物として扱う。
- `.uge` はひとまずGit管理対象とする。hUGETrackerで手修正した結果も確認・比較しやすくするためである。
- JSONは人間とChatGPTが読み書きしやすいことを優先する。
- 初版では高度な編集機能を目指さず、短いBGM・効果音の下書き生成を目的とする。
- hUGETrackerの全機能をJSONで表現する必要はない。
- `.uge` の詳細仕様が不明な箇所は、既存の `.uge` ファイルやhUGETracker出力を確認してから実装する。
- 不明点は推測で確定せず、TODOまたはWBSに残す。
- `.uge` 変換時に必要なら、JSON仕様を後から拡張してよい。

初版で扱うJSON項目:

- `version`: JSON仕様バージョン。
- `title`: 曲名または効果音名。
- `type`: `bgm` または `sfx`。
- `tempo`: Song Version 6の `TicksPerRow` として保存する。
- `instruments`: 音色定義。音色番号、名前、種別、およびPulse向けの最小Instrument詳細を扱う。
- `order`: 再生するパターン順。
- `patterns`: パターン定義。
- `channels`: `pulse1`、`pulse2`、`wave`、`noise` の4チャンネル。
- 各ノート情報:
  - `note`: 音名。休符は `rest` とする。
  - `length`: 音の長さ。初版ではpattern row数として扱い、音符セルと空行へ展開する。
  - `instrument`: 使用する音色番号。
  - `effect`: 効果指定。未使用時は `null` とする。
  - `effect_param`: 効果パラメータ。未使用時は `null` とする。

Pulse Instrument詳細項目:

- `duty`: Pulse duty設定。0～3を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- `initial_volume`: 初期音量。0～15を指定する。未指定時は15を使う。
- `envelope_direction`: 音量エンベロープ方向。`"up"` または `"down"` を指定する。未指定時は `"down"` を使う。
- `envelope_sweep`: 音量エンベロープのsweep値。0～7を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- これらのInstrument詳細項目は、初版では `pulse1` / `pulse2` 用Instrumentのみ対応する。
- 不正な範囲や未対応チャンネルでの指定は、変換ツールでバリデーションエラーにする。

JSON側の設計例:

```json
{
  "version": 1,
  "title": "Game Draft",
  "type": "bgm",
  "tempo": 6,
  "instruments": [
    { "id": 1, "name": "lead", "channel": "pulse1" },
    { "id": 2, "name": "bass", "channel": "pulse2" }
  ],
  "order": ["intro"],
  "patterns": {
    "intro": {
      "channels": {
        "pulse1": [
          { "note": "C4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "E4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "G4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "C5", "length": 4, "instrument": 1, "effect": null, "effect_param": null }
        ],
        "pulse2": [
          { "note": "C3", "length": 8, "instrument": 2, "effect": null, "effect_param": null },
          { "note": "G3", "length": 8, "instrument": 2, "effect": null, "effect_param": null }
        ],
        "wave": [],
        "noise": []
      }
    }
  }
}
```

### .uge形式調査結果

調査対象:

- `/home/akihiro/gbdev/hello/assets/twinkle.uge`
- `/home/akihiro/gbdev/hello/src/music/bgm_twinkle.asm`
- hUGETracker公式ソース `src/song.pas`
- hUGETracker公式ソース `src/hugedatatypes.pas`

確認できたこと:

- `.uge` はテキスト形式ではなくバイナリ形式である。
- ローカルの `twinkle.uge` は先頭4バイトが `06 00 00 00` で、hUGETrackerのSong Version 6として読める構造である。
- hUGETracker公式ソースでは、現行の `TSong` はSong Version 7として定義され、Version 1～7を読み込んで現行形式へUpgradeする処理がある。
- `.uge` は曲全体をFreePascalのrecord構造に近い形で保存している。
- Song Version 7の主な構成要素は、`Version`、`Name`、`Artist`、`Comment`、`Instruments`、`Waves`、`TicksPerRow`、`TimerEnabled`、`TimerDivider`、`Patterns`、`OrderMatrix`、`Routines` である。
- `Patterns` はパターン番号と64行分のセルデータを持つ。セルには `Note`、`Instrument`、`Volume`、`EffectCode`、`EffectParams` が含まれる。
- `OrderMatrix` は4チャンネル分の配列で、各チャンネルが再生するパターン番号の並びを保持する。
- `Routines` は16個の文字列として保存される。
- ローカルの `twinkle.uge` には、音色名やデフォルト波形名がASCII文字列として含まれているが、ファイル全体はバイナリである。
- ローカルの `twinkle.uge` には `0x5A` が多数含まれており、後続のnote番号調査で、hUGETracker / hUGEDriver側の `NO_NOTE = 90` と対応することを確認した。

Song Versionの決定:

- 本プロジェクト初版では、hUGETracker 1.0.11の安定版で扱えるSong Version 6を対象とする。
- 初版 `tools/json_to_uge.py` が書き出す `.uge` は、Song Version 6を採用する。
- Version 7はGitHub公式リポジトリの最新ブランチ上では現行 `TSong` として確認できるが、現在使用中のhUGETracker v1.0.11配布バイナリには含まれていないため、初版採用は見送る。
- 使用中のhUGETracker実行版は `/mnt/c/Users/akihiro/OneDrive/tools/hUGETracker-1.0.11-windows/hUGETracker.exe` で、実行ファイル内の表示文字列からv1.0.11であることを確認した。
- GitHub Releasesでは、hUGETracker 1.0.11が最新Releaseで、Release commitは `0623f3f` と確認した。
- `0623f3f` 時点の公式ソースでは `UGE_FORMAT_VERSION = 6`、`TSong = TSongV6`、読み込み対応はVersion 1～6までである。
- GitHub最新ブランチ先頭は `aa259a4936b9b539131abf51cdc8486829d2bab4` で、`UGE_FORMAT_VERSION = 7`、`TSong = TSongV7`、Version 6をVersion 7へUpgradeする処理が追加されている。
- v1.0.11実行ファイル内の文字列には `TSongV1`、`TSongV2`、`TSongV3`、`TSongV4`、`TSongV6` が確認できる一方、`TSongV7` は確認できなかった。
- v1.0.11配布物の `Sample Songs` にはVersion 1～6の `.uge` が含まれ、Version 7のサンプルは確認できなかった。
- ローカルの `twinkle.uge` もVersion 6であり、Windows版hUGETrackerで作成・再生確認・RGBDS ASM Exportまで行った実績がある。
- 公式ソースではVersion 6を読み込んでVersion 7へUpgradeする処理があるため、Version 6は新しいhUGETracker系でも読み込み対象である。
- Release Notes、Issue、Pull Request上でVersion 7を正式Release済み仕様として説明している情報は確認できなかった。
- 以上から、Version 7は次期Release向けの開発ブランチ上の保存形式と判断し、現行の安定運用対象はVersion 6とする。

Version 6/7の比較:

| 項目 | Version 6 | Version 7 |
| --- | --- | --- |
| `TicksPerRow` | `Integer` 1つ | 4チャンネル分の `Integer` 配列 |
| チャンネル別tempo | 直接は持たない | 持てる |
| `TimerEnabled` / `TimerDivider` | 持つ | 持つ |
| `Patterns` | `TCellV2` 64行pattern | Version 6と同系統 |
| `OrderMatrix` | 4チャンネル分のorder配列 | Version 6と同系統 |
| 公式ソース上の扱い | 読み込み後Version 7へUpgrade | 現行 `TSong` として読み書き |
| 使用中のv1.0.11実行版 | 配布サンプルと運用実績あり | 対応未確認 |
| v1.0.11 Release source | `TSong = TSongV6` | 存在しない |
| 最新ブランチ source | 読み込み互換対象 | `TSong = TSongV7` |
| 初版ツール実装難度 | 低い | `TicksPerRow` 配列対応が必要 |

Version 6採用理由:

- 初版目的は短いBGM・効果音の下書き生成であり、チャンネル別tempoは不要である。
- `tempo` を単一の `TicksPerRow` に対応させられるため、JSON仕様と実装が単純になる。
- 使用中のhUGETracker v1.0.11配布物にVersion 6サンプルが含まれ、ローカルでもVersion 6の `twinkle.uge` を運用済みである。
- 使用中のv1.0.11実行版でVersion 7を読める根拠が確認できず、Version 7を書き出すと「新しいhUGETrackerで作成された曲」として開けない可能性がある。
- 公式ソースでVersion 6読み込みとVersion 7へのUpgrade経路が確認できるため、将来のhUGETrackerへ移行してもVersion 6資産は読み込める可能性が高い。
- Version 7は最新ブランチ上では確認できるが、現行安定Releaseには含まれていないため、本プロジェクト初版では対象外とする。
- 将来Version 7対応版を使う場合は、`.uge` 形式やJSONから `.uge` への変換処理の見直しが必要になる可能性がある。

`json_to_uge.py` 実装時の注意:

- 先頭のSong Versionはlittle-endianの4バイト整数として `6` を書き出す。
- Version 6の `TicksPerRow` は単一整数として書き出し、JSONの `tempo` を対応させる。
- Version 7形式の `TicksPerRow[0..3]` は初版では書き出さない。
- hUGETrackerで保存し直すと、保存したhUGETracker実行版の対応Song Versionへ更新される可能性があるため、生成直後の `.uge` とhUGETracker保存後の `.uge` は差分が出る前提で扱う。
- Version 7は初版スコープ外とし、WBS上の未完了タスクとしては管理しない。
- 将来Version 7へ移行する場合は、JSONの `tempo` を単一値のまま全チャンネルへ複製するか、チャンネル別tempoを表現できるようJSON仕様を拡張する。

JSON項目と `.uge` 側の対応:

| JSON項目 | `.uge`側の対応 | 備考 |
| --- | --- | --- |
| `version` | JSON仕様バージョン | `.uge` のSong Versionとは別物として扱う。 |
| `title` | `Name` | 曲名・効果音名として保存する。 |
| `type` | 直接対応なし | `bgm` / `sfx` は制作・出力運用上の区分として扱う。 |
| `tempo` | `TicksPerRow` | Version 6では単一値、Version 7では4チャンネル分の配列。初版では全チャンネル同値にする。 |
| `instruments` | `Instruments` | 初版ではsquare/pulse用の最低限の音色定義を中心に扱う。 |
| `order` | `OrderMatrix` | JSONのパターン順を4チャンネル分のorder配列へ変換する。 |
| `patterns` | `Patterns` | パターン名を内部パターン番号へ割り当てる。 |
| `channels.pulse1` | `OrderMatrix[0]` / CH1 pattern cells | 矩形波チャンネル1。 |
| `channels.pulse2` | `OrderMatrix[1]` / CH2 pattern cells | 矩形波チャンネル2。 |
| `channels.wave` | `OrderMatrix[2]` / CH3 pattern cells | 波形メモリチャンネル。初版では未使用または空にしてよい。 |
| `channels.noise` | `OrderMatrix[3]` / CH4 pattern cells | ノイズチャンネル。初版では未使用または空にしてよい。 |
| `note` | `TCell.Note` | 音名をhUGETrackerのnote番号へ変換する。休符はNo Note値へ変換する。 |
| `length` | 直接対応なし | 1セルに長さは無い。音符行と休符行へ展開して表現する。 |
| `instrument` | `TCell.Instrument` | 1～15の音色番号として扱う。 |
| `effect` | `TCell.EffectCode` | 初版では未指定または基本effectのみ扱う。 |
| `effect_param` | `TCell.EffectParams` | 1バイト値として扱う。nibble分割が必要なeffectは実装時に確認する。 |

note番号・休符値:

- hUGETracker v1.0.11の公式ソース `src/constants.pas` では、`LOWEST_NOTE = 0`、`C_3 = 0`、`HIGHEST_NOTE = 71`、`B_8 = 71`、`NO_NOTE = 90` と定義されている。
- `include/hUGE.inc` でも `C_3 = 0` から `B_8 = 71` まで同じ番号で定義され、`___ = 90`、`NO_NOTE = ___` と定義されている。
- hUGETracker上の音名表記は `C-3`、`C#3`、`D-3` のように、ナチュラル音では音名とオクターブの間に `-` を入れる。
- RGBDS Export ASMでは `C_3`、`C#3`、`D_3` のように、ナチュラル音は `_`、シャープ音は `#` を使う。
- ローカルの `twinkle.uge` とExport ASM `bgm_twinkle.asm` を照合し、ASM上の `C_4`、`G_4`、`A_4`、`___` が `.uge` 内でそれぞれ `12`、`19`、`21`、`90` として現れることを確認した。
- JSON側では、ChatGPTと人間が読み書きしやすい表記として、ナチュラル音は `C3`、`D3`、シャープ音は `C#3`、`D#3`、休符は `rest` を採用する。
- JSON側では `C-3` や `C_3` は採用しない。これらはhUGETracker UIまたはExport ASM側の表記として扱う。

note番号対応:

| JSON音名 | `.uge` `TCell.Note` |
| --- | --- |
| `C3`～`B3` | 0～11 |
| `C4`～`B4` | 12～23 |
| `C5`～`B5` | 24～35 |
| `C6`～`B6` | 36～47 |
| `C7`～`B7` | 48～59 |
| `C8`～`B8` | 60～71 |
| `rest` | 90 |

各オクターブ内の半音順:

| 音名 | オクターブ内オフセット |
| --- | --- |
| `C` | 0 |
| `C#` | 1 |
| `D` | 2 |
| `D#` | 3 |
| `E` | 4 |
| `F` | 5 |
| `F#` | 6 |
| `G` | 7 |
| `G#` | 8 |
| `A` | 9 |
| `A#` | 10 |
| `B` | 11 |

JSON音名から `.uge` note番号への変換方針:

- `rest` は `NO_NOTE = 90` へ変換する。
- 音名は `C3`～`B8` の範囲に限定する。
- シャープは `#` で表記する。フラット表記は初版では扱わない。
- 変換式は `note_number = (octave - 3) * 12 + semitone_offset` とする。
- 例: `C3 = 0`、`C#3 = 1`、`D3 = 2`、`C4 = 12`、`C5 = 24`、`B8 = 71`。
- 範囲外の音名、未対応表記、空文字はバリデーションエラーとする。
- JSONから行展開するとき、音を伸ばすために追加する空行は `rest` と同じ `NO_NOTE = 90` を使う。

note変換実装時の注意:

- hUGETracker UI表記の `C-4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- Export ASM表記の `C_4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- `C#3` のようなシャープ表記はJSON文字列として問題なく扱えるため、`Cs3` 形式は採用しない。
- `NO_NOTE = 90` はhUGETracker公式ソースとhUGEDriver用 `hUGE.inc` の双方で確認済みのため、休符値として使用する。
- ノイズチャンネルでは音名がノイズ周波数選択として扱われるため、BGM音程と同じ意味で鳴るとは限らない。初版では同じnote番号変換を使い、音色・聴こえ方はhUGETracker上で確認する。

effect code・effect parameter:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、`TCellV2` が `EffectCode: Integer` と `EffectParams: TEffectParams` を持つ。
- `TEffectParams` は `Value: Byte` としても、`Param1` / `Param2` の2つの4bit nibbleとしても扱える `bitpacked record` である。
- `.uge` Version 6では、pattern内の各セルに `TCellV2.EffectCode` と `TCellV2.EffectParams` が保存される。
- hUGEDriverのpattern rowは `NNNNNNNN, IIIIEEEE, XXXXYYYY` の3バイトで、`E` がeffect code、`X` / `Y` がeffect parameterの上位/下位nibbleである。
- RGBDS Export ASMでは `dn note,instrument,$EPP` の形で出力される。`E` はeffect code、`PP` は `EffectParams.Value` である。
- `include/hUGE.inc` の `dn` macroは、`$EPP` の上位nibbleをeffect code、下位1バイトをeffect parameterとしてdriver用3バイトへpackする。
- hUGEDriver上のeffect未使用は `000`、つまり `EffectCode = 0` かつ `EffectParams.Value = 0` である。
- `EffectCode = 0` でも `EffectParams.Value` が0以外の場合は `0xy` Arpeggioとして扱われるため、未使用effectとは区別する。

effect未使用時の値:

- effect未使用とは、`EffectCode = 0` かつ `EffectParam = 0` の場合である。
- `EffectCode = 0` でも `EffectParam` が0以外の場合は、Arpeggio `0xy` として扱われる。
- そのため、effect未使用判定は `EffectCode` だけでは判定できない。
- 初版 `tools/json_to_uge.py` では、JSONの `effect = null`、`effect_param = null` の場合のみ `EffectCode = 0`、`EffectParam = 0` を出力する。
- 初版では `effect` が `null` 以外の場合は未対応とし、バリデーションエラーとする方針を維持する。

effect code対応:

| code | hUGEDriver表記 | JSON側の予約表記 | 初版対応 |
| --- | --- | --- | --- |
| `0` | `0xy` Arpeggio | `arpeggio` | 未対応 |
| `1` | `1xy` Slide up | `slide_up` | 未対応 |
| `2` | `2xy` Slide down | `slide_down` | 未対応 |
| `3` | `3xy` Toneporta | `tone_portamento` | 未対応 |
| `4` | `4xy` Vibrato | `vibrato` | 未対応 |
| `5` | `5xy` Set master volume | `set_master_volume` | 未対応 |
| `6` | `6xy` Call routine | `call_routine` | 未対応 |
| `7` | `7xy` Note delay | `note_delay` | 未対応 |
| `8` | `8xy` Set panning | `set_panning` | 未対応 |
| `9` | `9xy` Set duty cycle | `set_duty_cycle` | 未対応 |
| `A` | `Axy` Volslide | `volume_slide` | 未対応 |
| `B` | `Bxy` Position jump | `position_jump` | 未対応 |
| `C` | `Cxy` Set volume | `set_volume` | 未対応 |
| `D` | `Dxy` Pattern break | `pattern_break` | 未対応 |
| `E` | `Exy` Note cut | `note_cut` | 未対応 |
| `F` | `Fxy` Set speed | `set_speed` | 未対応 |

effect parameterの扱い:

- `EffectParams.Value` は1バイト値 `0x00`～`0xFF` として扱う。
- hUGETracker / hUGEDriver上ではeffectによって `Param1` / `Param2` のnibble単位で意味を持つものと、1バイト値として意味を持つものがある。
- `0xy` Arpeggio、`5xy` Set master volume、`Axy` Volslide、`Cxy` Set volumeなどはnibble単位の意味があることを公式ソース `src/utils.pas` の説明文字列で確認した。
- `1xy` Slide up、`2xy` Slide down、`3xy` Toneporta、`6xy` Call routine、`7xy` Note delay、`Bxy` Position jump、`Dxy` Pattern break、`Exy` Note cut、`Fxy` Set speedなどは `EffectParams.Value` の1バイト値として扱うことを確認した。
- `4xy` Vibrato、`8xy` Set panning、`9xy` Set duty cycleはdriver-formatおよびhUGEDriverのjump table上に存在するが、パラメータの詳細説明は `src/utils.pas` の `EffectToExplanation` では確認できなかった。

JSON側で採用するeffect表記:

- effect未使用は `effect: null`、`effect_param: null` とする。
- 初版 `tools/json_to_uge.py` では、`effect: null`、`effect_param: null` のみを対応対象とする。
- 初版で `effect` に非null値が指定された場合は、将来の実装ではバリデーションエラーにする方針とする。
- 非null effectを将来対応する場合は、上記のJSON側予約表記を使う。
- 非null effect対応時の `effect_param` は、まず `0`～`255` の整数として扱う方針とする。nibble単位の指定が必要になった場合はJSON仕様を拡張する。

初版 `tools/json_to_uge.py` で対応するeffect:

- effect未使用のみ対応する。
- `effect: null`、`effect_param: null` を `.uge` の `EffectCode = 0`、`EffectParams.Value = 0` へ変換する。
- Export ASM上では `$000` として出力される状態を目標にする。

初版 `tools/json_to_uge.py` では対応しないeffect:

- `arpeggio`
- `slide_up`
- `slide_down`
- `tone_portamento`
- `vibrato`
- `set_master_volume`
- `call_routine`
- `note_delay`
- `set_panning`
- `set_duty_cycle`
- `volume_slide`
- `position_jump`
- `set_volume`
- `pattern_break`
- `note_cut`
- `set_speed`

effect変換実装時の注意:

- `EffectCode = 0`、`EffectParams.Value = 0` はeffect未使用だが、`EffectCode = 0`、`EffectParams.Value != 0` はArpeggioである。
- 未使用判定を `EffectCode == 0` のみで実装してはいけない。必ず `EffectCode == 0` かつ `EffectParams.Value == 0` で判定する。
- `effect_param` を扱う場合は、`TEffectParams.Param1` / `Param2` のbitpacked上の並びと、hUGEDriver document上の `X` / `Y` の対応をeffectごとに確認する。
- `5xy`、`8xy`、`Bxy`、`Dxy`、`Fxy` はhUGEDriver上でglobal effectとして扱われるため、BGM全体への影響を確認してから対応する。
- `6xy` Call routineはroutine定義と組み合わせる必要があるため、初版では扱わない。
- `9xy` Set duty cycleはチャンネルやinstrument状態との関係を確認してから対応する。
- 非null effectを追加する場合は、hUGETrackerで読み込み、再生、保存、ASM Exportした結果を必ず確認する。

Instrument構造:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、Version 6の `TInstrument` は `TInstrumentV3` である。
- `TInstrumentV3` はInstrument種別にかかわらず同じrecord構造を持ち、`Type_` によってSquare/Duty、Wave、Noiseとして扱う。
- `TInstrumentType` は `itSquare = 0`、`itWave = 1`、`itNoise = 2` である。
- `TInstrumentCollectionV3` は `Duty`、`Wave`、`Noise` の3 bankを持ち、各bankは `1..15` の15個である。`All[1..45]` としても参照できる。
- Instrument番号 `0` はhUGEDriver上で「Instrumentなし」として扱われるため、JSONで指定できるInstrument IDは `1`～`15` とする。

`TInstrumentV3` の主なメンバー:

| メンバー | 用途 |
| --- | --- |
| `Type_` | `itSquare` / `itWave` / `itNoise` の種別。 |
| `Name` | hUGETracker上のInstrument名。 |
| `Length` | 各チャンネルのlength registerへ反映される値。 |
| `LengthEnabled` | length counterを使うかどうか。 |
| `InitialVolume` | Square/Noiseの初期音量。 |
| `VolSweepDirection` | Square/Noiseのvolume envelope方向。 |
| `VolSweepAmount` | Square/Noiseのvolume envelope量。 |
| `SweepTime` | SquareのNR10 sweep time。 |
| `SweepIncDec` | SquareのNR10 sweep方向。 |
| `SweepShift` | SquareのNR10 sweep shift。 |
| `Duty` | Squareのduty比。 |
| `OutputLevel` | Waveの出力レベル。 |
| `Waveform` | Waveが参照する波形番号。 |
| `CounterStep` | Noiseの7bit/15bit counter設定。 |
| `SubpatternEnabled` | Instrument subpatternを使うかどうか。 |
| `Subpattern` | Instrument subpattern。64行の `TPattern`。 |

Version 6でのInstrument保存形式:

- `TSongV6` は固定長record部分に `Instruments: TInstrumentCollection` を含む。
- `WriteSongToStream` は `TSong` から `TPatternMap`、`TOrderMatrix`、`TRoutineBank` を除いた固定長部分を先に書き出すため、Instrumentは曲名、作者、コメントの後、Wave bankやtempoより前に保存される。
- 保存されるInstrumentはDuty 15個、Wave 15個、Noise 15個の合計45個である。
- `.uge` 内では `TInstrumentV3` recordとして保存される。ASM Export時のdriver用Instrumentは `.uge` 内のrecordそのものではなく、`InstrumentToBytes` でhUGEDriver用のバイト列へ変換される。
- hUGEDriver用ASMでは、Square/Wave/Noiseの各Instrument entryは実質6バイト単位で出力される。Square/Waveは4バイトのregister系値とsubpattern pointer、Noiseはenvelope、subpattern pointer、highmask/length相当、paddingで構成される。
- `src/song.pas` は保存時に `SizeOf(TSong)` や `SizeOf(TInstrumentV3)` を使う。Pythonで実装する場合は手計算したサイズだけに依存せず、hUGETrackerが保存した `.uge` と照合する。
- この環境ではFreePascalコンパイラが無く、`SizeOf(TInstrumentV3)` の数値を実行確認できなかった。実装時は実ファイルとの照合で確定する。

hUGETracker新規作成時のInstrument初期値:

- `InitializeSong` は全Instrumentを `Default(TInstrument)` で初期化し、全Instrumentの `Subpattern` を `BlankPattern` で空パターン化する。
- Duty bankは全15個に `Type_ = itSquare`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`SweepTime = 0`、`SweepIncDec = stDown`、`SweepShift = 0`、`Duty = 2`、`OutputLevel = 1` を設定する。
- Wave bankは全15個に `Type_ = itWave`、`Length = 0`、`LengthEnabled = False`、`OutputLevel = 1`、`Waveform = I - 1` を設定する。
- Noise bankは全15個に `Type_ = itNoise`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen` を設定する。
- `LoadDefaultInstruments` はDuty 1～8に名前とduty比を設定し、Duty 5～8には `VolSweepAmount = 1` を設定する。
- `LoadDefaultInstruments` はWave 1～11にデフォルト波形名を設定し、`DefaultWaves` を `Waves[0..10]` へ設定する。
- ローカルの `twinkle.uge` には `Lead 12.5%`、`Base 25%`、`Coin 50%`、`Laser75%`、`Duty 25% plink`、`Square wave 12.5%` などのInstrument名文字列が含まれることを確認した。

Instrumentの最小構成:

- 再生に必要な最小構成は、使用するbankのInstrument `Type_`、鳴る音量設定、長さ設定、subpattern無効状態、空のsubpatternである。
- Square/Dutyを鳴らすには、少なくとも `Type_ = itSquare`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`Duty`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- Waveを鳴らすには、`Type_ = itWave`、`OutputLevel = 1`、`Waveform`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。`OutputLevel = 0` は無音になるため避ける。
- Noiseを鳴らすには、`Type_ = itNoise`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- `Default(TInstrument)` のままではSquare/Noiseの `InitialVolume` が0になり、無音になるため、0初期化だけでInstrumentを生成してはいけない。
- `Subpattern` は未使用でもrecord上は存在するため、`BlankPattern` 相当で全セルを `NO_NOTE` にした空パターンとして保存する。
- Wave/Noiseを初版で未使用にする場合でも、`.uge` Version 6の固定record構造として15個ずつ保存する必要がある。

JSON項目とInstrumentの対応:

| JSON項目 | `.uge`側の対応 | 初版方針 |
| --- | --- | --- |
| `id` | bank内のInstrument番号 `1..15` | 1～15のみ許可する。 |
| `name` | `TInstrument.Name` | 指定された名前を保存する。未指定ならデフォルト名を使う。 |
| `channel` | `Duty` / `Wave` / `Noise` bank選択 | `pulse1` / `pulse2` はDuty、`wave` はWave、`noise` はNoiseへ割り当てる。 |
| 詳細音色パラメータ | `Duty`、`InitialVolume`、`VolSweepDirection`、`VolSweepAmount` など | Pulse向けに `duty`、`initial_volume`、`envelope_direction`、`envelope_sweep` を扱う。 |

- 初版では、JSONの `id`、`name`、`channel` と、任意のPulse Instrument詳細からInstrumentを生成する。
- `pulse1` と `pulse2` はどちらも同じDuty bankのInstrument番号を参照する。
- JSONの `channel` は主にどのbankへInstrumentを配置するかを決めるための情報であり、pattern cell側では `TCell.Instrument` に `id` を入れる。
- 同じ `id` を異なるbankで使うことは可能だが、同じbank内で重複した `id` はバリデーションエラーとする。
- Pulse Instrument詳細が未指定の場合は、従来どおりhUGETracker初期値またはデフォルトInstrument相当を使う。

初版 `tools/json_to_uge.py` のInstrument方針:

- Pulse向けInstrumentを主対象とし、`pulse1` / `pulse2` はDuty bankへ出力する。
- Duty bank、Wave bank、Noise bankは常に15個ずつ生成する。
- 使用されていないInstrumentもhUGETrackerの初期値相当で出力する。
- Duty 1～8は `LoadDefaultInstruments` 相当の名前、duty比、volume envelopeを使う。JSONでPulse Instrument詳細が指定されたInstrumentは、その値で上書きする。
- Wave/Noiseは初版では詳細編集を行わず、hUGETracker初期値相当の固定値で生成する。
- `SubpatternEnabled` は全Instrumentで `False` とし、`Subpattern` は空パターンにする。
- `tools/json_to_huge_asm.py` はPulse Instrument詳細をhUGEDriver ASMのduty instrument entryへ反映する。
- `tools/json_to_uge.py` はPulse Instrument詳細をSong Version 6のDuty bank Instrumentへ反映する。

Instrument実装時の注意:

- Instrument ID `0` は「Instrumentなし」なのでJSONでは禁止する。
- `InitialVolume = 0` のSquare/Noise、`OutputLevel = 0` のWaveは無音になるため、デフォルト値を必ず設定する。
- Instrumentのrecordサイズ、`ShortString`、enum、Boolean、subrange型の保存サイズはFreePascalのバイナリ表現に合わせる必要がある。
- Python実装時は、公式ソースのfield順に従って書き出し、hUGETrackerで保存した `.uge` との比較でoffsetとサイズを確認する。
- `.uge` 内のInstrument recordと、ASM Export後のhUGEDriver用Instrumentバイト列は同一ではない。`.uge` 生成では `TInstrumentV3` を書き、ASM出力はhUGETrackerに任せる。
- Wave bankを使わない場合でも、`Waves` とWave InstrumentはVersion 6の固定構造として保存する。

wave/noise未使用時の扱い:

- 初版では、`wave` / `noise` チャンネルを省略するのではなく、空patternを再生する未使用チャンネルとして扱う。
- hUGETracker v1.0.11の `InitializeSong` は4チャンネルすべての `OrderMatrix` を長さ2に初期化し、各チャンネルの先頭にpattern番号を設定する。
- hUGETrackerのExport処理は `OrderMatrix[I]` の `High(...)-1` までを有効orderとして扱う実装になっているため、空配列ではなく、少なくとも長さ2のOrderMatrixを持たせる方針にする。
- `WriteSongToStream` はOrderMatrixの長さを書いた後、`OrderMatrix[i][0]` から内容を書き出すため、長さ0のOrderMatrixは避ける。
- `wave` / `noise` を未使用にする場合も、pulse側と同じorder数にそろえ、各orderで空patternを参照させる。
- 空patternは `BlankPattern` 相当とし、64行すべて `Note = NO_NOTE`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` にする。
- `Instrument = 0` はhUGEDriverで「Instrumentなし」として扱われるため、空pattern内ではWave/Noise Instrumentを参照しない。

確認できたこと:

- hUGETracker公式ソース `src/utils.pas` の `BlankPattern` は、全セルを `Default(TCell)` にした上で `Note = NO_NOTE` を設定する。
- hUGETracker公式ソース `src/hugedatatypes.pas` の `TPatternMap.GetOrCreateNew` は、存在しないpattern番号を参照した場合に `BlankPattern` で空patternを作成する。
- hUGETracker公式ソース `src/codegen.pas` の `FindUsedStuff` は、Wave/Noise channelのpattern内で `Instrument = 0` のセルをInstrument未使用として扱い、Wave/Noise Instrumentの使用数を増やさない。
- hUGETracker公式ソース `src/codegen.pas` の `RenderInstruments` は、使用上限が `-1` のbankではInstrument entryを出力しない。
- ローカルの `bgm_twinkle.uge` はhUGETracker v1.0.11で作成・保存・RGBDS ASM Export済みのVersion 6ファイルであり、Export ASM `bgm_twinkle.asm` ではCH3に対応する `bgm_twinkle_P2` が64行すべて `dn ___,0,$000` の空patternとして出力されている。
- 現在の `src/bgm_test.asm` では、CH3/CH4に対応する `TestBgmPattern3` / `TestBgmPattern4` を64行すべて `dn ___, 0, $000` とし、`TestBgmWaveInstruments` / `TestBgmNoiseInstruments` は空sectionとして扱っている。

OrderMatrixの扱い:

- 初版 `tools/json_to_uge.py` では、4チャンネルすべてにOrderMatrixを出力する。
- `wave` / `noise` が未使用の場合でも、OrderMatrix自体は省略しない。
- `wave` / `noise` の各orderは、空pattern番号を参照させる。
- hUGETrackerの初期化・Export処理に合わせ、OrderMatrixは長さ0にしない。
- pulse側に複数orderがある場合、`wave` / `noise` も同じorder数分だけ空patternを並べる。

Patternの扱い:

- 空patternは64行固定で出力する。
- 各行は `NO_NOTE = 90`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` とする。
- Export ASM上では `dn ___,0,$000` が64行並ぶpatternとして見える。
- hUGETrackerの `OptimizeSong` は同一内容のpatternをまとめるため、Wave/Noise用の空patternがExport時に1つへ統合される可能性がある。

Instrumentの扱い:

- `wave` / `noise` が未使用でも、`.uge` Version 6の固定構造としてWave bank 15個、Noise bank 15個は保存する。
- 未使用channelのpattern cellでは `Instrument = 0` とするため、Wave/Noise Instrumentは参照されない。
- Wave/Noise InstrumentはhUGETracker初期値相当の固定値で出力する。
- Export ASMでは、Wave/Noise Instrumentが参照されていない場合、`wave_instruments:` / `noise_instruments:` ラベルは出るが、その配下にInstrument entryは出力されない。

Export ASM上の見え方:

- order tableには `order3` / `order4` も出力される。
- `wave` / `noise` 未使用channelのorderは空patternを参照する。
- 空patternは `dn ___,0,$000` のみで構成される。
- Wave/Noise Instrumentが参照されない場合、`wave_instruments:` / `noise_instruments:` は空になる。

初版 `tools/json_to_uge.py` でのwave/noise出力方針:

- JSONの `channels.wave` または `channels.noise` が空配列、または未指定相当の場合は、そのチャンネルを未使用として扱う。
- 未使用channelには空OrderMatrixではなく、空pattern参照を持つ最小構成のOrderMatrixを書き出す。
- 空patternは全セル `NO_NOTE` / `Instrument = 0` / effect未使用で書き出す。
- Wave/Noise Instrument bankは常に15個ずつhUGETracker初期値相当で書き出す。
- Wave bank用の `Waves` もVersion 6の固定構造として保存する。
- 初版ではWave/Noiseの詳細編集は行わず、未使用または空patternのみを基本とする。

wave/noise未使用実装時の注意:

- OrderMatrixを長さ0にしない。
- Wave/Noise用のpattern番号が `Patterns` に存在するようにする。
- 空patternには `Instrument = 0` を使い、未使用Instrument番号を誤って参照しない。
- Wave/Noiseを未使用にしても、`.uge` の固定record領域からWave/Noise InstrumentやWave bankを削らない。
- hUGETrackerの直接GUI操作による最小 `.uge` の新規作成・再保存は今回実施していない。生成 `.uge` の読み込み・保存・ASM Export確認は、後続WBS「生成した `.uge` をhUGETrackerで読み込み・保存・ASM Exportできることを確認する」で実施する。

初版 `tools/json_to_uge.py` で対応する範囲:

- `.uge` バイナリを書き出す。
- Song VersionはVersion 6を書き出す。
- `title` を曲名として保存する。
- `tempo` を全チャンネル共通のticks-per-rowとして保存する。
- 最大64行の短いパターンを生成する。
- `pulse1` / `pulse2` を中心に、note、instrument、effect、effect_paramをセルへ変換する。
- `wave` / `noise` は空パターンまたは限定対応から始める。
- `length` は音符セルと休符セルへ展開する。
- 未使用のinstrument、wave、routineはhUGETrackerの初期値または空値に近い状態で出力する。

初版 `tools/json_to_uge.py` では対応しない範囲:

- hUGETrackerの全effect対応。
- instrument subpattern、routine、wave tableの詳細編集。
- チャンネルごとに異なるtempo。
- 高度なpattern再利用最適化。
- hUGETracker上の全GUI設定の再現。
- 既存 `.uge` の読み込み・差分マージ。

実装時の注意点:

- `.uge` はバイナリ形式のため、文字列連結ではなく `struct` などで明示的にバイト列を書き出す。
- FreePascalの `Integer` サイズ、booleanサイズ、`ShortString` の保存形式、packed recordのアラインメントを公式ソースと実ファイルで照合する。
- 初版対象はSong Version 6に固定し、`TicksPerRow` は単一整数として実装する。
- hUGETrackerが読む順序は、固定長領域、pattern数、pattern keyとpattern本体、4チャンネル分のorder配列、routine文字列の順である。
- pattern cellは64行固定として扱う。
- `length` は `.uge` に直接保存されないため、行展開後に64行を超えないようバリデーションする。
- 出力した `.uge` はhUGETrackerで開けることを必ず確認する。

未確定事項・TODO:

- 非null effectを実装対象に追加する場合、各effectのチャンネル制約、tick上の挙動、parameterの意味を個別に確認する。

## 画像仕様

ゲームボーイ向け画像は以下の仕様で作成する。

### PNG形式

- Indexed Color
- パレット数: 4色
- アルファチャンネルなし
- インターレースなし

### BGタイル用パレット（tiles.png）

|Index|Color|
|---:|---|
|0|#E0F8D0|
|1|#88C070|
|2|#346856|
|3|#081820|

### BGタイル用 rgbgfx

BGタイル画像変換時は以下のパレットを指定する。

```bash
rgbgfx -c "#E0F8D0,#88C070,#346856,#081820"
```

### カーソルSprite用パレット（cursor.png）

Spriteでは色番号0が透明色として扱われるため、カーソル用画像では透明にしたい色をインデックス0へ配置する。
`cursor.png` はBGタイルとは異なるrgbgfxパレット順で変換し、表示時は `rOBP0` を使用する。

|Index|Color|用途|
|---:|---|---|
|0|#88C070|透明（カーソル外側）|
|1|#E0F8D0|カーソル内側|
|2|#346856|カーソル内側の線|
|3|#081820|カーソル外側の線|

### カーソルSprite用 rgbgfx

カーソルSprite画像変換時は以下のパレットを指定する。

```bash
rgbgfx -c "#88C070,#E0F8D0,#346856,#081820"
```

Python等でPNGを生成する場合も、画像ごとに対応するパレットを使用すること。

### 画像タイル・文字タイル管理方針

- 画像タイルや文字タイルは、原則としてPNG素材から生成する。
- プログラム中にドットパターンを直接定義してタイルを作成しない。
- 記号や追加文字が必要な場合は、フォント生成処理またはPNG素材へ追加する。
- UI記号（©、▶など）はUIフォントとして管理する。
- UI記号も通常文字と同様にPNG素材から生成する。
- UI記号のタイルデータもプログラム中に直接書かない。
- 例外的にプログラム中でタイル定義する場合は、理由をPROJECT.mdに明記する。

## タイル画像

- BGタイルは `assets/tiles.png` に管理する。
- ポーズメニュー枠用タイルは `assets/tiles.png` に追加済みとする。
- カーソル用Spriteは `assets/cursor.png` に管理する。
- UIフォントは `assets/font.png` に管理し、数字、英字、コロン、追加記号をPNG素材から生成する。
- BGタイルとSpriteは用途ごとに画像を分けて管理する。
- Sprite素材が増えた場合も用途ごとに画像を追加して管理する。

### BGタイル構成

|番号|内容|
|---:|---|
|0|未開封|
|1|開封済み(0)|
|2|開封済み(1)|
|3|開封済み(2)|
|4|開封済み(3)|
|5|開封済み(4)|
|6|開封済み(5)|
|7|開封済み(6)|
|8|開封済み(7)|
|9|開封済み(8)|
|10|フラグ|
|11|地雷（ゲーム終了時に正解の地雷を表示）|
|12|爆発した地雷（プレイヤーが踏んだ地雷を表示）|
|13|誤ったフラグ（ゲームオーバー時に間違っていたフラグを表示）|
|14|BG消去用の空白|
|15|ポーズメニュー枠 左上|
|16|ポーズメニュー枠 右上|
|17|ポーズメニュー枠 左下|
|18|ポーズメニュー枠 右下|
|19|ポーズメニュー枠 横|
|20|ポーズメニュー枠 縦|
|21以降|UIフォント（0-9、コロン、A-Z、©、▶など）。カーソルSprite用の52～55とは衝突しないよう、必要に応じてフォントを分割配置する。|

### カーソルSprite構成

カーソル用Spriteは `assets/cursor.png` に管理する。

カーソル用画像は、カーソル外側を透明にするため、BGタイルとは異なるパレット順を使用する。

|番号|内容|
|---:|---|
|0|左上|
|1|右上|
|2|左下|
|3|右下|

# WBS

- [x] 開発基盤
  - [x] GitHubリポジトリ作成
  - [x] PROJECT.md作成
  - [x] 使用するRGBDSバージョンを決める
  - [x] ディレクトリ構成とビルド方法を決める
    - [x] ディレクトリ構成を決める
    - [x] ビルド成果物の配置を決める
    - [x] Makefileの構成を決める
  - [x] ディレクトリ構成作成
  - [x] .gitignore作成
  - [x] RGBDS最小ROM
    - [x] Makefileを作成する
    - [x] 最小構成の `src/main.asm` を作成する
    - [x] ROMエントリポイントを実装する
    - [x] rgbfixでROMヘッダを設定する
    - [x] `make` で初期ROM成果物を生成する
    - [x] `make clean` の動作を確認する
    - [x] `make run` でエミュレータ起動を確認する
- [x] 基本描画・入力
  - [x] タイル画像
  - [x] 画面初期化
  - [x] 入力処理
  - [x] カーソル表示
    - [x] 8×8・1Spriteによるカーソル表示を実装する
    - [x] カーソルを16×16（4Sprite）化し、選択中マスの外枠を表示する
      - [x] 16×16カーソル画像を作成する
      - [x] 16×16カーソル表示を実装する
- [x] 盤面生成
  - [x] 最初に開くマスの安全を保証する方法を決める
  - [x] 乱数シードの生成方法を決める
  - [x] 地雷配置
  - [x] 数字生成
- [x] ゲーム処理
  - [x] 0のマスを連続して開く処理
    - [x] 0のマスを連続して開く処理方式を決める
    - [x] 0のマスを連続して開く処理を実装する
  - [x] マスを開く処理
  - [x] フラグ処理
  - [x] ゲームオーバー判定
  - [x] クリア判定
- [ ] UI・追加仕様
  - [x] タイトル画面処理作成
    - [x] 起動時にタイトル画面状態へ遷移する
    - [x] タイトル画面でSTARTボタン入力を扱う
    - [x] タイトル画面から次の画面へ遷移できるようにする
    - [x] 初期実装ではタイトル画面に何も表示しなくてもよい
  - [x] BG画像タイル変換ツール作成
    - [x] 画像を8×8タイルへ分割する
    - [x] 重複タイルを削除する
    - [x] タイルセット画像を生成する
    - [x] BGマップファイルを生成する
    - [x] タイトルロゴだけでなく将来のBG画像にも使える汎用ツールとする
  - [x] タイトル画面表示処理作成
    - [x] タイトルロゴ画像を表示する
    - [x] `PRESS START` を文字描画で表示する
    - [x] `©2026 AKIHIRO SEKINE` を文字描画で表示する
  - [x] ゲーム終了時のタイトル復帰
    - [x] GAME OVER画面でSTARTを押すとタイトル画面へ戻る
    - [x] CLEAR画面でSTARTを押すとタイトル画面へ戻る
  - [ ] リピート入力は未実装。カーソル移動実装後に必要なら検討する
  - [x] プレイ中のSTART操作
    - [x] 通常プレイ中にSTARTボタンを押した場合にポーズメニューを表示する
    - [x] `RESUME` でポーズメニューを閉じて通常プレイに戻る
    - [x] `RESTART` で現在のゲームを破棄して新しいゲームを開始する
    - [x] `BACK TO TITLE` で現在のゲームを破棄してタイトル画面へ戻る
    - [x] ポーズメニュー枠画像作成
      - [x] ウィンドウ枠用PNGを作成する
      - [x] 枠、角、内側塗りつぶし用タイルを用意する
      - [x] 画像タイルはPNGから生成する
    - [x] ポーズメニュー枠表示処理
      - [x] ポーズメニュー表示時にウィンドウ枠を表示する
      - [x] ウィンドウ枠の内側にRESUME / RESTART / BACK TO TITLEを表示する
      - [x] 選択中項目を `▶` で表示する
      - [x] RESUME時にウィンドウで隠した盤面を復元する
    - [x] UIフォントへ▶追加
      - [x] font.pngへ▶を追加する
      - [x] フォント生成ツールを更新する
      - [x] charmapおよび文字変換テーブルを更新する
      - [x] ポーズメニューで利用可能にする
    - [x] ポーズメニューカーソル変更
      - [x] `>` を `▶` へ変更する
      - [x] ポーズメニューで▶を表示する
      - [x] 上下移動時も▶が正しく移動する
      - [x] 視認性を確認する
    - [x] ポーズ解除時の一括再描画
      - [x] RESUME時に盤面が1マスずつ表示されないようにする
      - [x] 可能であれば盤面を一括で再描画する
      - [x] 通常の0連鎖オープン等の分割更新処理は壊さない
  - [x] ゲーム終了後のSTART処理
    - [x] ゲームオーバーまたはゲームクリア後にSTARTボタンでタイトル画面へ戻る
  - [ ] SELECTボタンの役割を確定する
  - [x] 残り地雷数表示
    - [x] ステータスバーのMINE表示を実際のフラグ数に応じて更新する
  - [x] 難易度選択や別サイズの盤面を実装するか決める
    - [x] 難易度選択を初版から実装する
    - [x] 難易度選択はタイトル画面内ではなく別の設定画面として扱う
  - [x] 難易度選択画面
    - [x] タイトル画面STARTで難易度選択画面へ遷移する
    - [x] 難易度選択画面に `SELECT LEVEL` / `EASY` / `NORMAL` / `HARD` を表示する
    - [x] 上下キーで選択項目を変更する
    - [x] AボタンまたはSTARTボタンでゲームを開始する
    - [x] Bボタンでタイトル画面へ戻る
    - [x] RESTART時に現在の難易度を維持する
  - [x] 可変盤面サイズ対応
    - [x] 難易度ごとに盤面サイズ・地雷数を切り替える
    - [x] 最大10×10盤面へ対応する
    - [x] 地雷配置処理を可変サイズ対応にする
    - [x] 数字生成処理を可変サイズ対応にする
    - [x] 盤面描画を可変サイズ対応にする
    - [x] カーソル移動範囲を可変サイズ対応にする
    - [x] 盤面描画を盤面サイズに応じて中央寄せする
    - [x] クリア判定を「盤面マス数 − 地雷数」に変更する
    - [x] 0連鎖オープン(BFS)を可変サイズ対応にする
    - [x] BFSキュー・表示更新キュー・盤面データを100セル対応へ変更する
  - [x] 経過時間または手数を表示するか決める
  - [x] 経過時間表示
    - [x] 経過時間用WRAM変数を追加する
    - [x] 最初にマスを開いた時点で経過時間カウントを開始する
    - [x] 通常プレイ中のみ1秒ごとに経過時間を加算する
    - [x] ポーズ中、ゲームオーバー中、ゲームクリア中は経過時間を停止する
    - [x] `TIME:000` の3桁表示を更新する
    - [x] 999秒でカウントを停止する
    - [x] RESTART時に経過時間を000へ初期化する
    - [x] 新規ゲーム開始時に経過時間を000へ初期化する
    - [x] 999秒上限確認用に経過時間のデバッグ初期値を設定できるようにする
  - [x] セーブ機能やハイスコアを実装するか決める
  - [ ] UI表示
- [ ] サウンド
  - [ ] サウンド基盤
    - [x] hUGETrackerのデータ組み込み方法とサウンド更新タイミングを確認する
    - [x] 楽曲定義JSON方式を決める
      - [x] JSONの最小仕様を決める
      - [x] JSONファイルの配置場所を決める
      - [x] `.uge` 生成物の扱いを決める
      - [x] `.uge` 形式の調査を行う
      - [x] Pulse Instrument詳細をJSONで指定できるようにする
    - [x] hUGETrackerで使用するSong Version（6/7）を決定する
    - [x] note番号・休符値の対応を確認する
    - [x] effect code / effect parameterの対応を確認する
    - [x] instrument初期値の最小構成を確認する
    - [x] wave/noise未使用時でも正常に開けることを確認する
    - [x] 生成した `.uge` をhUGETrackerで読み込み・保存・ASM Exportできることを確認する
    - [x] JSONからugeファイルへ変換するPythonツール作成
      - [x] `tools/json_to_uge.py` を作成する
      - [x] JSONを読み込む
      - [x] 入力JSONの基本バリデーションを行う
      - [x] `.uge` ファイルを書き出す
      - [x] サンプルJSONからサンプル `.uge` を生成する
      - [x] hUGETrackerで生成した `.uge` を開けることを確認する
      - [x] `tools/README.md` に使い方を追記する
    - [x] JSONからhUGEDriver用RGBDS ASMを直接生成するPythonツールを作成する
      - [x] `tools/json_to_huge_asm.py` を作成する
      - [x] JSONを読み込む
      - [x] note / length / instrument / effect をASMへ変換する
      - [x] order / pattern / instrument / routine / wave のASMを出力する
      - [x] wave/noise未使用時の空patternを出力する
      - [x] サンプルJSONからASMを生成する
      - [x] hUGETracker Export ASMと比較する
      - [x] `tools/README.md` に使い方を追記する
    - [x] サウンド再生確認用テストROMを生成するPythonツールを作成する
      - [x] `tools/build_sound_test_rom.py` を作成する
      - [x] 指定したASMをincludeする最小ROM用ASMを生成する
      - [x] hUGEDriverを組み込む
      - [x] 起動後に指定曲を再生する
      - [x] `rgbasm` / `rgblink` / `rgbfix` を呼び出してGB ROMを生成する
      - [x] `obj/` に中間ファイルを出力する
      - [x] 指定した出力先へテストROMを出力する
      - [x] `tools/README.md` に使い方を追記する
    - [x] JSON修正からテストROM確認までのサウンド制作運用を確認する
      - [x] 実際のBGM・効果音制作を行いながら運用確認を兼ねて実施する
      - [x] JSONを修正する
      - [x] ASMを再生成する
      - [x] テストROMを再生成する
      - [x] GBエミュレータで再生確認する
      - [x] 問題があればJSONを再修正する
  - [ ] BGM制作
    - [ ] 必要なBGM一覧を決定する
    - [ ] タイトルBGMを作成する
    - [ ] プレイ中BGMを作成する
    - [ ] クリアBGMを作成する
  - [ ] 効果音制作
    - [x] 必要な効果音一覧を決定する
    - [x] カーソル移動効果音を作成する
    - [ ] 決定効果音を作成する
    - [ ] キャンセル効果音を作成する
    - [ ] マスを開く効果音を作成する
    - [ ] 旗を立てる効果音を作成する
    - [ ] 旗を外す効果音を作成する
    - [ ] 地雷爆発効果音を作成する
    - [ ] クリア効果音を作成する
    - [ ] ゲームオーバー効果音を作成する
  - [ ] サウンド実装
    - [x] BGMと効果音の再生制御方針を決める
    - [ ] 生成したBGM ASMと効果音データを本体ROMへ組み込む
    - [ ] サウンド管理処理を実装する
    - [ ] BGM再生開始処理を実装する
    - [ ] 効果音再生処理を実装する
    - [ ] タイトル画面でタイトルBGMを再生する
    - [ ] 通常プレイ中にプレイ中BGMを再生する
    - [ ] クリア時にクリアBGMまたはクリアジングルを再生する
    - [ ] カーソル移動時にカーソル移動効果音を鳴らす
    - [ ] 決定操作時に決定効果音を鳴らす
    - [ ] キャンセル操作時にキャンセル効果音を鳴らす
    - [ ] マスを開いた時にマス開封効果音を鳴らす
    - [ ] 旗を立てた時に旗設置効果音を鳴らす
    - [ ] 旗を外した時に旗解除効果音を鳴らす
    - [ ] 地雷を開いた時に地雷爆発効果音を鳴らす
    - [ ] ゲームオーバー時にゲームオーバー効果音を鳴らす
- [ ] 検証・公開準備
  - [ ] テスト
  - [ ] 実機確認に使うフラッシュカートの有無を検討する
  - [ ] README整備
    - [x] 初版作成
    - [ ] 最終版作成
  - [x] タイトル変更に伴うプロジェクト名・生成物名の統一
    - [x] リポジトリ名を `pocket-sweeper` へ変更する
    - [x] Makefileの `PROJECT` 値を `pocket-sweeper` へ変更する
    - [x] ROM成果物名を `build/pocket-sweeper.gb` へ変更する
    - [x] obj配下の `.sym` / `.map` などの生成物名を `pocket-sweeper.*` へ変更する
    - [x] README内の旧タイトル・旧成果物名を更新する
    - [x] ソース・Makefile・README・PROJECT.md全体から旧名称の残存を検索し、必要な箇所を修正する
    - [x] `make clean && make` で `build/pocket-sweeper.gb` が生成されることを確認する
