# Deep Eval Triage Summary (v2)

- reports_dir: reports/PRM-REQ-EVAL-002/v2
- backlog_total_requirements: 40
- priority_counts: S=34, A=1, B=3, R=2
- grounding_missing_count: 2
- needs_human_review_count: 2

## 優先度ルール（機械付与）

- R: timeout/cancelled 等の評価実行条件起因（要件修正では解けない）
- S: 仕様/テスト成立に直結（How混入、主語不明、AC不足、参照不能、トレーサビリティ欠落 等）
- A: 品質改善（曖昧語、境界条件不足、外部観測不足、形式不足 等）
- B: 上記以外（軽微/局所）

## 低スコア要因（reason/error由来；timeout除外）

- 曖昧語残存: 134
- AC/Given-When-Then不足: 105
- How混入（技術/実装詳細の混入）: 104
- 手順/形式の欠落（評価手順・出力形式不一致）: 82
- 主語（ロール）不明確: 75
- 境界条件（数値/範囲）不足: 69
- 外部観測可能性が弱い: 66
- 異常系/失敗時定義不足: 42
- スキーマ/メタデータ不整合: 35
- derived_from整合性の問題: 23
- 参照不能/用語定義不足（コンテキスト完全性）: 17
- traces_to 未整備: 11

## source_file 別（着手の目安）

- req_core_concepts_v1.yaml: 6
- req_architecture_and_ui_v1.yaml: 6
- req_execution_plan_v1.yaml: 6
- req_conclusion_next_steps_v1.yaml: 5
- req_measurement_and_kpi_v1.yaml: 5
- req_background_and_problem_v1.yaml: 4
- req_glossary_and_constraints_v1.yaml: 4
- req_positioning_and_strategy_v1.yaml: 3

## 根拠シグナル不足（MISSING）の例（人手精査キュー）

- REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml): reason/errorにチェックリストIDも検出語も無く、機械分類できない
- REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml): reason/errorにチェックリストIDも検出語も無く、機械分類できない
