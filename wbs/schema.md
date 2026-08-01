# WBS定義

Pocket SweeperのWBSは、1項目1Markdownファイルを正本とする。IDは `WBS-001-NNNNN`、ファイル名はIDと完全一致させ、親子は `parent`、依存は `depends_on` に完全IDで記録する。プロジェクト番号は文字列 `001` とし、一度使用した番号は別プロジェクトへ再利用しない。

`type` は `group` / `task`、`status` は `complete` / `incomplete`、`actor` は `codex` / `human` / `none` のみとする。groupのactorはnone、実行対象taskはcodexまたはhumanとする。人とCodexの作業は別項目へ分け、確定できない担当は `actor_review_required: true` と移行報告へ記録する。

YAMLの型は、`id/title/type/status/actor/updated` が文字列、`parent` がnullまたは文字列、`depends_on/specs/related_files/outputs/blocked_by/source_wbs` が文字列配列、`evidence_required` が真偽値である。`updated` は `YYYY-MM-DD` 形式とする。`specs` と `related_files` はリポジトリルートからの相対パスで、実在を検証する。`related_files` はファイルまたはディレクトリを指定できる。`*`、`?`、`[`を含む場合はglobとして扱い、一件以上の一致を必須とする。

番号はPROJECT.mdの移行時の出現順に1000から連番で採番した。新規項目は既存最大番号の次の空き番号を使い、IDから階層や担当を推測しない。流用元は `source_wbs` に形式だけ正しいIDとして記録し、現行のparent/depends_onには使用しない。

taskは「目的」「作業内容」「入力」「成果物」「完了条件」「完了にしてはいけない条件」「確認結果」「証跡」、groupは「概要」「配下の作業」を必須とする。仕様参照は `specs`、関連対象は `related_files` に記録する。

`tools/validate_wbs.py` は不正な構造をエラー、同名・担当確認・移行前からの親状態矛盾を警告として出力する。エラー終了は1、警告だけは0である。Excelは検証エラー時に生成しない。`reports/wbs.xlsx` は自動生成物で直接編集しない。

自己参照と親子・依存関係の循環はエラーであり、循環経路を表示する。`source_wbs` は形式が正しい限り実在不要で、parent/depends_onとは分離する。同一親配下の同名項目は警告、異なる親配下の同名項目は許可する。Excelの完了条件・証跡はMarkdown本文から抽出し、進捗集計にはgroupを含めず、最上位groupごとのtask集計も出力する。ルートtaskは「ルートtask」区分として集計する。
