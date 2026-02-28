# Deep Eval Runtime Issues (timeout/cancelled)

## 一覧（要件修正の優先順位から除外）

> 注: ここは要件品質ではなく、評価実行条件に起因する問題の切り分け専用です。

### 1. REQ-NFUNC-BUGREDUCE-001 (req_measurement_and_kpi_v1.yaml) / Faithfulness

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 2. REQ-FUNC-SCOPEOUT-001 (req_glossary_and_constraints_v1.yaml) / Faithfulness

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 3. REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml) / Faithfulness

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 4. REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml) / 企画整合性 [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 5. REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml) / スコープ適切性・How非混入 [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 6. REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml) / 検証可能性（AIDD最重要） [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 7. REQ-FUNC-QAVERIFY-001 (req_positioning_and_strategy_v1.yaml) / AI可読性（AIDD固有） [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 8. REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml) / Faithfulness

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 9. REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml) / 企画整合性 [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 10. REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml) / スコープ適切性・How非混入 [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 11. REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml) / 検証可能性（AIDD最重要） [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

### 12. REQ-FUNC-PRMTPL-001 (req_positioning_and_strategy_v1.yaml) / AI可読性（AIDD固有） [GEval]

- error: Timed out/cancelled while evaluating metric. Increase DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE or set DEEPEVAL_LOG_STACK_TRACES=1 for full traceback.
- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1

## 再実行の対処案（一般）

- 評価のtimeoutを延長する（特にLLM呼び出しや長文入力がある場合）
- 対象要件を分割して評価する（バッチサイズを下げる）
- 1要件あたりの入力（企画書/背景等）を短縮し、参照箇所を絞る
- 同一要件で特定metricのみtimeoutする場合、そのmetricのプロンプトを簡素化する
