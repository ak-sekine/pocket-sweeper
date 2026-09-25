# プロジェクト概要

- **プロジェクト名:** Pocket Sweeper
- **日本語表記:** ポケットスイーパー
- **概要:** 初代ゲームボーイで動作する、シンプルなマインスイーパー。
- **目的:** RGBDSによるゲームボーイ開発の基礎を習得し、将来のゲームボーイRPG開発へ流用できる共通処理を整備する。

## プロジェクト全体の主要方針

- 初代ゲームボーイ向けのシンプルなマインスイーパーをRGBDSで開発する。
- 詳細なゲーム、システム、サウンド、楽曲定義JSON、画像・描画の仕様は分野別仕様書で管理する。
- 固定パズルモードは未確定事項が多く、WBSで管理する。

## プロジェクト識別子

- プロジェクト番号: `001`
- プロジェクト名: `Pocket Sweeper`
- WBS ID形式: `WBS-001-NNNNN`

## 正本

- プロジェクト概要・主要方針：`PROJECT.md`
- WBS詳細：`wbs/tasks/*.md`
- WBS定義：`wbs/schema.md`
- 分野別仕様：`docs/*.md`
- WBS一覧：`reports/wbs.md`（自動生成の閲覧用一覧。直接編集しない）

WBS変更は `wbs/tasks/*.md` に対して行い、更新後に `tools/validate_wbs.py` と `tools/generate_wbs_markdown.py` を実行する。生成一覧は直接編集せず、正本Markdownと不一致の場合は正本Markdownを正とする。WBS指定は完全なWBS IDを優先する。

## 詳細仕様書

- [ゲーム仕様](docs/game-spec.md)
- [システム設計](docs/system-design.md)
- [サウンド仕様](docs/sound-spec.md)
- [楽曲定義JSON仕様](docs/json-format.md)
- [画像・描画仕様](docs/graphics-spec.md)

## WBS移行

PROJECT.mdに記載していた詳細チェックリストは、出現順を保ったまま `wbs/tasks/` へ移行した。移行前後の件数・状態・対応は [移行報告](docs/wbs-migration-report.md) と生成された `reports/wbs.md` を参照する。
