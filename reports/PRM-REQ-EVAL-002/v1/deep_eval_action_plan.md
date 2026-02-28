# Deep Eval Action Plan (1 week)

## 根拠（reason/error集計；timeout由来はEに切り分け）

- Top patterns: 曖昧語残存(134), AC/Given-When-Then不足(105), How混入（技術/実装詳細の混入）(104), 手順/形式の欠落（評価手順・出力形式不一致）(82), 主語（ロール）不明確(75), 境界条件（数値/範囲）不足(69), 外部観測可能性が弱い(66), 異常系/失敗時定義不足(42)

## Day0: runtime issue 切り分け（timeout/cancelled）
- reports/PRM-REQ-EVAL-002/deep_eval_runtime_issues.md を確認
- 必要なら timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）、対象分割、入力短縮で再評価

## Day1: How混入除去ルール化（最優先）
- 技術固有語（SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等）を要件文から排除
- 置換方針: ‘手段’→‘外部から観測できる結果（表示/出力/通知/永続性）’

## Day2: ロール主語の統一（user/admin/viewer/system）
- reason/errorで『主語不明/誰が/許可ロール』が指摘された要件を優先
- 主語を必ず user/admin/viewer/system のいずれかに正規化

## Day3: ACをGiven-When-Thenで最低1件付与
- When（トリガー）とThen（合否判定）を一意にし、テストケース化できる形へ

## Day4: 境界条件の数値化（上限/時間/件数/閾値）
- reason/errorで不足指摘された境界条件（件数/時間/サイズ/保持期間/閾値/タイムアウト）をACに追記
- 曖昧語（適切に/等/リアルタイム等）を数値・条件に置換

## Day5: coverage/traceability 改善（企画↔要件 対応付け）
- 企画項目（PLN-*）→要件（REQ-*）の対応表を作成（不足/重複/不要/粒度違いを分類）
- derived_from を企画IDへ揃え、traces_to を空にしない（設計/テストIDへ接続）

## Day6: 再評価→差分確認
- Deep Evalを再実行し、deep_eval_findings.csv の差分で改善/悪化を確認

## Day7: 回帰防止（テンプレ・ルールの固定）
- deep_eval_patch_suggestions.md のテンプレ/機械ルールをレビュー観点とCIに組み込み
