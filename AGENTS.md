# Pocket Sweeper AI作業ガイド

## 正本

- `PROJECT.md`: プロジェクト概要・主要方針
- `wbs/tasks/*.md`: WBS詳細・状態の正本
- `wbs/schema.md`: WBS記述規則
- `docs/*.md`: 分野別仕様の正本
- `reports/wbs.xlsx`: 自動生成一覧（直接編集しない）

WBSを指定された場合、標準依頼は `WBS-001-01003を実施してください。` とする。タイトル指定より完全なWBS IDを優先し、同名候補が複数なら推測しない。

## 作業開始時

1. `git status --short --branch`
2. `git fetch`
3. 最新コミットとリモート状態を確認する
4. 未コミット変更を確認し、必要な場合だけ `git pull --ff-only`
5. 指定IDから `wbs/tasks/<WBS ID>.md` を開く
6. YAML front matterを確認する
7. 本文の目的、作業内容、完了条件、証跡条件を確認する
8. `specs` の仕様書、`related_files` の実装・テスト、`depends_on` の完了状態を確認する

仕様を推測で補完しない。未確定事項や仕様書間の矛盾は記録して報告する。

## 担当別の処理

- `actor: codex`: Codexが実装、文書更新、自動テストを行う。
- `actor: human`: AIは人が実施する具体的な手順を提示し、人の結果が提供されるまで完了にしない。
- `actor: none`: groupとして未完了の子タスクを案内する。
- `actor_review_required: true`: 担当を推測せず、要確認として報告する。

人のGUI、実機、エミュレータ、音声、画像、操作感確認はAIだけで完了扱いにしない。

## WBS更新

WBSを変更した場合は、対象Markdownを更新し、必要な確認結果と証跡を本文へ記録する。その後、次を順に実行する。

1. `python3 tools/validate_wbs.py`
2. `python3 tools/generate_wbs_excel.py`
3. `reports/wbs.xlsx` を確認する
4. 正本MarkdownとExcelを一緒にcommitする

WBSの状態は対象Markdownだけで管理する。親は子孫がすべて完了した場合だけ完了とし、ExcelとMarkdownが不一致ならMarkdownを正とする。

## 仕様・変更範囲

- 詳細仕様は分野別仕様書を正本とし、WBS移行や実装の都合で無関係な仕様を変更しない。
- 既存WBSのID、title、status、parent、depends_onを根拠なく変更しない。
- `source_wbs` は流用元専用であり、現行の`parent`や`depends_on`に使用しない。
- 無関係な実装、生成物、テスト、未コミット変更を変更しない。

## テストとGit

- 変更内容に応じた既存テストと標準テストを実行する。
- 検証・テストが失敗した場合は修正するまでcommit・pushしない。
- RGBDS、SameBoy、BGB、hUGETracker等を実行できない場合、実行したと報告しない。
- Gitコマンドは1コマンドずつ実行し、対象ファイルを明示してstageする。`git add .`と`git add -A`は禁止する。
- `git reset --hard`、`git clean -fd`、amend、force push、rebase、変更破棄目的のcheckoutは禁止する。
- WBS作業では、検証・テスト成功後にcommit・pushする。pushがnon-fast-forwardならforce pushせず報告する。

## Python

プロジェクトの`.venv`を優先し、利用できなければ`python3`を使用する。Excel生成は`openpyxl`、YAML解析は`PyYAML`を使用する。
