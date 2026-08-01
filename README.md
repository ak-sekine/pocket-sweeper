# Pocket Sweeper

Game Boy向けマインスイーパーです。

RGBDSを使用して開発しています。

## 開発環境

* WSL2 (Ubuntu)
* RGBDS
* Python 3
* VS Code
* SameBoy

## セットアップ

### リポジトリを取得

```bash
git clone <repository>
cd pocket-sweeper
```

### Python仮想環境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### ライブラリをインストール

```bash
pip install -r requirements.txt
```

### RGBDS

RGBDSをインストールしてください。

## ビルド

```bash
make
```

## 実行

```bash
make run
```

## VS Code

RGBDS拡張を使用してください。

includePath はワークスペース相対で設定します。

```json
{
  "rgbdsz80.includePath": [
    "include",
    "src"
  ]
}
```

※ `.vscode` は Git 管理対象外です。

## 開発ツール

Pythonツールは `tools/` にあります。

詳細は

```text
tools/README.md
```

を参照してください。

## プロジェクト管理

ゲーム仕様・設計・WBSは

```text
PROJECT.md
```

で管理しています。

AI向けの作業ルールは `AGENTS.md` を参照してください。
## WBS管理

- プロジェクト番号: `001`
- WBS ID形式: `WBS-001-NNNNN`
- 詳細正本: `wbs/tasks/*.md`
- 定義: `wbs/schema.md`
- 生成一覧: `reports/wbs.xlsx`（直接編集しない）

WBSを追加するときは、既存最大番号の次の5桁番号でMarkdownを作成し、front matterの `id` とファイル名を一致させます。状態は `complete` / `incomplete`、親と依存先は完全なWBS IDで指定し、流用元は `source_wbs` に記録します。

`.venv` を使う場合は `python3 -m venv .venv` と ` .venv/bin/pip install -r requirements.txt` を実行してください。検証とExcel生成は次のコマンドです。

```bash
.venv/bin/python tools/validate_wbs.py
.venv/bin/python tools/generate_wbs_excel.py
```

WBS変更後は検証、Excel再生成、`reports/wbs.xlsx` の確認を行います。MarkdownとExcelが不一致ならMarkdownを正とします。

検証ではYAML各フィールドの型、日付形式、ID・親・依存の循環、`specs` と `related_files` の存在、`source_wbs` の分離、同一親配下の同名を確認します。同名は警告、それ以外の不正はエラーです。Excelの完了条件・証跡は各Markdownの本文から生成され、最上位group別のtask進捗も集計されます。`reports/wbs.xlsx` は読み取り専用推奨として生成されますが、暗号化や完全な編集禁止ではありません。Excelを直接編集せず、変更時はMarkdownを更新してExcelを再生成してください。
