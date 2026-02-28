# Deep Eval Summary

## 全体サマリ

- total_test_cases: 40
- passed: 3
- failed: 37
- pass_rate: 0.075
- total_requirements_evaluated: 97

### メトリクス平均

- Faithfulness: 0.943
- 企画整合性 [GEval]: 0.386
- スコープ適切性・How非混入 [GEval]: 0.381
- 検証可能性（AIDD最重要） [GEval]: 0.53
- AI可読性（AIDD固有） [GEval]: 0.495
- 全体網羅性（企画→要件） [GEval]: 0.0

### 特に低い項目トップ5（平均スコア）

- 全体網羅性（企画→要件） [GEval]: 0.0
- スコープ適切性・How非混入 [GEval]: 0.381
- 企画整合性 [GEval]: 0.386
- AI可読性（AIDD固有） [GEval]: 0.495
- 検証可能性（AIDD最重要） [GEval]: 0.53

## 低スコア要因（reason由来の頻出パターン）

- 曖昧語残存: 136
- AC/Given-When-Then不足: 107
- How混入（技術/実装詳細の混入）: 106
- 手順/形式の欠落（評価手順・出力形式不一致）: 83
- 主語（ロール）不明確: 76
- 外部観測可能性が弱い: 73
- 境界条件（数値/範囲）不足: 71
- 異常系/失敗時定義不足: 42
- スキーマ/メタデータ不整合: 35
- derived_from整合性の問題: 23
- 参照不能/用語定義不足（コンテキスト完全性）: 17
- traces_to 未整備: 11

## “最優先で直すべき10件”（影響度×頻度ランキング）

> 注: ランキングは、失敗メトリクスの閾値未達度と、reasonから抽出したパターン（How混入/主語不明等）の重みを合成して算出。

### 1. REQ-NFUNC-BUGREDUCE-001 (req_measurement_and_kpi_v1.yaml)

- priority_score: 27.030
- worst_metrics: Faithfulness, 企画整合性 [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.

### 2. REQ-NFUNC-SELFPROOF-001 (req_conclusion_next_steps_v1.yaml)

- priority_score: 20.160
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順1〜4に基づく抽出・対応付け・必要性判断・方針適合/逸脱検出（0.0〜1.0の整合度採点＋具体指摘）が一切実施されていない。企画目的（構造化・可視化・検証可能化）や制約（禁止事項・原則）をINPUT/Contextから抽出した形跡がなく、Actual Output各項目が目的貢献しているかの根拠対応付けもない…

### 3. REQ-FUNC-SCOPEOUT-001 (req_glossary_and_constraints_v1.yaml)

- priority_score: 17.680
- worst_metrics: Faithfulness, スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.

### 4. REQ-FUNC-SCOPEIN-001 (req_glossary_and_constraints_v1.yaml)

- priority_score: 15.920
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順に沿った整理・判定がほぼ行われていないため低評価。求められているのは、Inputから目的（構造化・可視化・検証可能化）と方針/制約（禁止事項・原則、例：ロールはuser/admin/viewer/systemのみ、曖昧語禁止、実装詳細混入検知など）を抽出して評価基準化し、Actual Outputを項目別に目…

### 5. REQ-NFUNC-WINDOWS-001 (req_glossary_and_constraints_v1.yaml)

- priority_score: 15.120
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順が求める(1)目的・方針/制約の抽出と基準整理、(2)要件ごとの目的貢献の照合、(3)MustかNice-to-haveかの判定、(4)方針違反/根拠なき追加の検出と0.0〜1.0の総合整合度スコア(日本語)の提示、のいずれも実施されていない。提示されているのはWindows制約に沿う単一要件本文で、受入基準…

### 6. REQ-NFUNC-E2EPASS-001 (req_execution_plan_v1.yaml)

- priority_score: 12.720
- worst_metrics: スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順（目的・制約抽出→目的貢献/必要性→違反・根拠なし追加の検出→0.0〜1.0採点と日本語理由）に照らすと、このACTUAL_OUTPUTは入力の完了基準「定義された15画面すべてが設計通りに動作」に部分的に整合し、derived_fromもPLN-PLN-PLAN_PHASE0_CRITERIA-002で妥当…

### 7. REQ-NFUNC-TECHSTACK-001 (req_architecture_and_ui_v1.yaml)

- priority_score: 12.560
- worst_metrics: スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): Retrieval Contextには技術スタック表（React+TS、Zustand、Tailwind+shadcn、Zod、React Flow、Node+Express、SQLite、Vitest+Playwright等）が含まれており、Actual Outputの「技術スタック準拠」という主旨自体はderiv…

### 8. REQ-NFUNC-SETUP-001 (req_execution_plan_v1.yaml)

- priority_score: 12.560
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順(1)〜(4)に沿った分析が行われておらず、企画書コンテキストから目的（構造化・可視化・検証可能化）や禁止事項・原則の抽出と整理がない。Actual Outputの各要件（本件はREQ-NFUNC-SETUP-001の1件）について、目的貢献・必要性（Must/ Nice-to-have判定）・方針適合/逸脱…

### 9. REQ-FUNC-CONTENT-001 (req_conclusion_next_steps_v1.yaml)

- priority_score: 12.560
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 企画目的（構造化・可視化・検証可能化）や方針/制約（曖昧語禁止、検証可能なAC、Phase1範囲、実装詳細混入回避、ロール明確化等）を基準として整理し、Actual Output各項目の目的貢献・Must性・逸脱/違反を0.0〜1.0で日本語根拠付き採点することが求められている。しかし提示されたActual Outp…

### 10. REQ-FUNC-QAWFUI-001 (req_core_concepts_v1.yaml)

- priority_score: 11.130
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, AC/Given-When-Then不足, 曖昧語残存, 境界条件（数値/範囲）不足
- evidence (reason抜粋): 評価手順(1)〜(4)に沿った抽出・対応付けの記述がなく、Retrieval Contextから「構造化・可視化・検証可能化」や禁止事項/原則（例: 実装詳細混入禁止、許可ロール、曖昧語禁止等）を根拠付きで必須条件化していない。目的貢献(0.0〜1.0)、必要性(0.0〜1.0)、方針適合/逸脱(0.0〜1.0)の判…
