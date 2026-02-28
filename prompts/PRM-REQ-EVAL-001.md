あなたはリポジトリ内の要件YAML群とチェックリスト、Deep Evalの評価JSONを読み込み、
「評価レポート」を reports/ 配下に生成するツールです。

# 目的

Deep Evalの評価が悪かった原因を、チェックリスト観点（purpose/scope/verifiability/ai_readability/traceability/schema/operational）に沿って整理し、
“どのファイル/どの要件ID/どの観点が”悪いのかを特定し、改善に直結する修正ガイドを作る。

# 入力（この順で読む）

1. Deep Eval結果:

- eval_req_vs_planning_v1.json

2. チェックリスト定義:

- checklist.yaml

3. 評価対象の要件YAML（req\_\*.yaml と requirements_document_v1.yaml）:

- req_architecture_and_ui_v1.yaml
- req_background_and_problem_v1.yaml
- req_conclusion_next_steps_v1.yaml
- req_core_concepts_v1.yaml
- req_execution_plan_v1.yaml
- req_glossary_and_constraints_v1.yaml
- req_measurement_and_kpi_v1.yaml
- req_positioning_and_strategy_v1.yaml
- req_quality_assurance_design_v1.yaml
- req_risks_and_constraints_v1.yaml
- req_rollout_plan_v1.yaml
- req_system_design_v1.yaml
- req_validation_and_meta_quality_v1.yaml
- req_visualization_and_export_v1.yaml
- requirements_document_v1.yaml

# 出力（reports/ 配下に必ず作る）

A) reports/deep_eval_summary.md

- 全体サマリ（pass率、メトリクス平均、特に低い項目トップ5）
- 低スコア要因を「頻出パターン」として分類（例: How混入、ロール主語不明、AC欠落、根拠なし追加、曖昧語、境界条件不足、参照不能、traces_to空、deliverable不整合 等）
- “最優先で直すべき10件”を、影響度×頻度でランキング

B) reports/deep_eval_findings.csv
列: requirement_id, source_file, doc_id, metric_name, score, threshold, passed, reason, fix_hint, checklist_category, checklist_item_id

- fix_hint は reason から具体化（例: 「SQLite/node-cron等の実装詳細を削り、外部観測可能な結果に言い換え」など）

C) reports/deep_eval_action_plan.md

- 1週間でスコアを上げるための改善計画
  - Day1: How混入除去ルール化（禁止語/危険ワード辞書）
  - Day2: ロール主語の統一（user/admin/viewer/system）
  - Day3: ACをGiven-When-Thenで最低1件付与（機能要件）
  - Day4: 境界条件の数値化（上限/時間/件数/閾値）
  - Day5: 参照可能性（derived_from/traces_to/用語定義）修正
  - Day6-7: 再評価→差分確認→回帰防止ルール

D) reports/deep_eval_patch_suggestions.md

- “修正テンプレ”を提示（What/Why/AC/GWT/Not-How/Role/Boundaries/Errors/Trace）
- よくあるNG→OK言い換え例を10個（例: 「システムはSQLiteに保存する」→「system は永続化され、再起動後も参照できる」）

# 補足（優先ルール）

- “How混入”は最優先で扱う。SQLite/node-cron/React/ajv/GitHub Actions 等の技術固有語が要件文に出た場合は、
  原則「観測可能な結果」に言い換える修正案を必ず fix_hint に書く。
- 主語は user/admin/viewer/system のいずれかに統一し、主語が曖昧な要件を優先的にトップ10へ入れる。

# 重要ルール

- レポート内の主張は必ず eval_req_vs_planning_v1.json の reason を根拠にする（推測しない）
- チェックリスト（checklist.yaml）のカテゴリ/項目IDにマッピングして原因を分類する
- 可能な範囲で “機械的に検出できる違反” を抽出（例: 危険ワード: DB/API/UI/技術固有語、曖昧語、acceptance_criteria欠落 等）
- 既存ファイルは変更しない（レポート生成のみ）
- 出力ファイルは UTF-8、Markdownは見出し構造を持つ

# 実行手順

1. JSONをパースして全test_resultsを走査
2. metricごとに失敗理由を分類し、チェックリストカテゴリへマッピング
3. 失敗が多いパターン上位を抽出
4. reports/ に A〜D を生成
5. 生成したファイル一覧を最後に表示

以上を実行してください。
