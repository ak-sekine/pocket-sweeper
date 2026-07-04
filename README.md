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
cd gb-minesweeper
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
