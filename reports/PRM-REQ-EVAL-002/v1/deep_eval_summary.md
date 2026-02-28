# Deep Eval Summary

## 全体サマリ

- total_test_cases: 40
- passed: 3
- failed: 37
- pass_rate: 0.075
- total_requirements_evaluated: 97
- runtime_issues (timeout/cancelled): 12

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

## 企画→要件 網羅性（coverage）が低い/0.0 の場合の要約

- evidence (reason/error抜粋): 評価手順1〜4に沿った出力（要素の8〜15個要約列挙、各要素の要件IDへの紐づけ、不足要件のタイトル案、逆方向チェックと0.0〜1.0採点）が一切提示されていない。与えられているのは企画書全文と要件定義サマリーのみで、要素抽出・対応付け・不足/過剰の指摘・網羅性スコアの日本語理由が欠落しているため、評価ステップへの整合がほぼない。
- 全体網羅性（企画→要件） [GEval] が 0.0 です。要件の書き方だけでなく、企画項目→要件の対応付け（不足/重複/不要/粒度違い）不足として別枠で整理してください。

## チェックリスト項目IDへのマッピングについて

- checklist_item_id を機械的に決定できない行が 36 件ありました。
- reason/error内にCHK-IDが含まれず、かつ検出語（How混入/主語不明/AC不足等）も見つからない場合は空欄としています。

## 低スコア要因（reason/error由来の頻出パターン）

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

## “最優先で直すべき10件”（timeout由来を除外したランキング）

> 注: ランキングは、失敗メトリクスの閾値未達度と、reason/errorから抽出したパターン（How混入/主語不明等）の重みを合成して算出。

### 1. REQ-NFUNC-SELFPROOF-001 (req_conclusion_next_steps_v1.yaml)

- priority_score: 3.600
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, derived_from整合性の問題, 主語（ロール）不明確, 外部観測可能性が弱い
- evidence (reason/error抜粋): 評価手順1〜4に基づく抽出・対応付け・必要性判断・方針適合/逸脱検出（0.0〜1.0の整合度採点＋具体指摘）が一切実施されていない。企画目的（構造化・可視化・検証可能化）や制約（禁止事項・原則）をINPUT/Contextから抽出した形跡がなく、Actual Output各項目が目的貢献しているかの根拠対応付けもない。また「Deep Eval≥0.8」「ト…

### 2. REQ-NFUNC-WINDOWS-001 (req_glossary_and_constraints_v1.yaml)

- priority_score: 2.700
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 参照不能/用語定義不足（コンテキスト完全性）, 主語（ロール）不明確, 外部観測可能性が弱い
- evidence (reason/error抜粋): 評価手順が求める(1)目的・方針/制約の抽出と基準整理、(2)要件ごとの目的貢献の照合、(3)MustかNice-to-haveかの判定、(4)方針違反/根拠なき追加の検出と0.0〜1.0の総合整合度スコア(日本語)の提示、のいずれも実施されていない。提示されているのはWindows制約に沿う単一要件本文で、受入基準なし・Node.js LTSなどINPU…

### 3. REQ-NFUNC-TECHSTACK-001 (req_architecture_and_ui_v1.yaml)

- priority_score: 2.400
- worst_metrics: スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 主語（ロール）不明確, 外部観測可能性が弱い, 曖昧語残存
- evidence (reason/error抜粋): Retrieval Contextには技術スタック表（React+TS、Zustand、Tailwind+shadcn、Zod、React Flow、Node+Express、SQLite、Vitest+Playwright等）が含まれており、Actual Outputの「技術スタック準拠」という主旨自体はderived_from=PLN-PLN-ARCH…

### 4. REQ-FUNC-CONTENT-001 (req_conclusion_next_steps_v1.yaml)

- priority_score: 2.400
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 主語（ロール）不明確, 外部観測可能性が弱い, 曖昧語残存
- evidence (reason/error抜粋): 企画目的（構造化・可視化・検証可能化）や方針/制約（曖昧語禁止、検証可能なAC、Phase1範囲、実装詳細混入回避、ロール明確化等）を基準として整理し、Actual Output各項目の目的貢献・Must性・逸脱/違反を0.0〜1.0で日本語根拠付き採点することが求められている。しかし提示されたActual Outputは要件そのものであり、評価手順に沿っ…

### 5. REQ-NFUNC-E2EPASS-001 (req_execution_plan_v1.yaml)

- priority_score: 2.400
- worst_metrics: スコープ適切性・How非混入 [GEval], 検証可能性（AIDD最重要） [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 参照不能/用語定義不足（コンテキスト完全性）, 主語（ロール）不明確, 外部観測可能性が弱い
- evidence (reason/error抜粋): 評価手順（目的・制約抽出→目的貢献/必要性→違反・根拠なし追加の検出→0.0〜1.0採点と日本語理由）に照らすと、このACTUAL_OUTPUTは入力の完了基準「定義された15画面すべてが設計通りに動作」に部分的に整合し、derived_fromもPLN-PLN-PLAN_PHASE0_CRITERIA-002で妥当。一方で(1) 15画面が要件内で明示さ…

### 6. REQ-FUNC-SCOPEIN-001 (req_glossary_and_constraints_v1.yaml)

- priority_score: 2.300
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 参照不能/用語定義不足（コンテキスト完全性）, derived_from整合性の問題, 主語（ロール）不明確
- evidence (reason/error抜粋): 評価手順に沿った整理・判定がほぼ行われていないため低評価。求められているのは、Inputから目的（構造化・可視化・検証可能化）と方針/制約（禁止事項・原則、例：ロールはuser/admin/viewer/systemのみ、曖昧語禁止、実装詳細混入検知など）を抽出して評価基準化し、Actual Outputを項目別に目的貢献・核心要件性・逸脱（根拠なし/方針…

### 7. REQ-FUNC-RTWARN-001 (req_architecture_and_ui_v1.yaml)

- priority_score: 2.100
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, 曖昧語残存, 境界条件（数値/範囲）不足, 手順/形式の欠落（評価手順・出力形式不一致）
- evidence (reason/error抜粋): 評価手順（目的・方針抽出→要件の目的貢献/必要性→方針違反特定→逸脱検出と0.0〜1.0採点＋日本語理由）に沿った評価が提示されていない。提示されているのは要件本文であり、企画目的（構造化・可視化・検証可能化）や禁止事項/原則の抽出・固定、各項目の必要性判定、方針/制約違反（例：Zod+正規表現など実装詳細混入）指摘、根拠のない過剰仕様（例：200ms、送…

### 8. REQ-FUNC-QAWFUI-001 (req_core_concepts_v1.yaml)

- priority_score: 2.100
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval], AI可読性（AIDD固有） [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, derived_from整合性の問題, 主語（ロール）不明確, 外部観測可能性が弱い
- evidence (reason/error抜粋): 評価手順(1)〜(4)に沿った抽出・対応付けの記述がなく、Retrieval Contextから「構造化・可視化・検証可能化」や禁止事項/原則（例: 実装詳細混入禁止、許可ロール、曖昧語禁止等）を根拠付きで必須条件化していない。目的貢献(0.0〜1.0)、必要性(0.0〜1.0)、方針適合/逸脱(0.0〜1.0)の判定も提示されず、引用や該当箇所指摘もない…

### 9. REQ-FUNC-QPROOF-001 (req_measurement_and_kpi_v1.yaml)

- priority_score: 2.100
- worst_metrics: スコープ適切性・How非混入 [GEval], AI可読性（AIDD固有） [GEval], 企画整合性 [GEval]
- patterns: How混入（技術/実装詳細の混入）, AC/Given-When-Then不足, 参照不能/用語定義不足（コンテキスト完全性）, 主語（ロール）不明確, 曖昧語残存
- evidence (reason/error抜粋): Retrieval ContextはINPUTの3層実証構造（technical/methodological/practicalのwhat/how/evidence）を過不足なく含んでおり問題ない。一方Actual Outputは、technicalproofの証跡（GitHub Actionsログ、Allure公開URL、品質スコア推移グラフ）やmet…

### 10. REQ-FUNC-ROLEUI-001 (req_core_concepts_v1.yaml)

- priority_score: 1.800
- worst_metrics: 企画整合性 [GEval], スコープ適切性・How非混入 [GEval]
- patterns: How混入（技術/実装詳細の混入）, 主語（ロール）不明確, 曖昧語残存, 手順/形式の欠落（評価手順・出力形式不一致）
- evidence (reason/error抜粋): 評価手順1〜4で求められる「INPUTから目的・方針/制約（原則/禁止事項）を抽出して基準化」「Actual Output各項目を目的貢献/必要性で判定」「方針・制約違反の有無を具体指摘」「根拠（Retrieval Context）にない要素混入や過剰推測を検出し、0.0〜1.0で採点し日本語理由を書く」といった評価行為が、提示された“応答”内で一切行われ…
