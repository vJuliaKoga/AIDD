あなたは仕様書（Markdown）を、分割 YAML（複数ファイル）へ変換し、さらに **品質ゲート（run_gates.py）で合格するまで修正**する作業者です。

# このプロンプトの位置づけ

- 本プロンプト（PRM-PLN-YAML-002）は、PRM-PLN-YAML-001の作業手順を「ルール参照＋ゲート強制」に拡張したものです。
- 実行前に必ず以下の3ファイルを読み、**ルールを最優先**してください。
  1. AIDD\prompts\PRM-PLN-YAML-001.md（前提の基本手順）
  2. AIDD\RULES\TPL-OPS-RULES-002.yaml（運用ルール：ID/検査/meta/terminal + Gate Runner命名規約）
  3. AIDD\RULES\schema_registry.yaml（対象YAML→適用schemaの対応表）

# 入力

- AIDD\planning\planning_v2.2.md

# 共通テンプレ（必読）

- AIDD\planning\yaml\planning_v2.2\planning.template.yaml
  以降で生成する各セクション YAML（01〜16）は、このテンプレの構造（meta/section/items/related）に厳密準拠すること。
  ※テンプレからキーを削除しない。キー名を変えない。rootは必ずmapping。
  ※ID規約は PREFIX-PHASE-PURPOSE-NNN に従うこと。

# 構造検査（必須）

- schema_registry.yaml に従い、生成した各 YAML に対して適切な JSON Schema を選択して検査すること。
  （planning v2.2 の期待値：section=planning.section.schema.json / index=planning.index.schema.json）

【重要：ターミナル操作ルール（Windows PowerShell）】

- VSCodeターミナルでは PowerShell を使用すること（cmd/bashに切り替えない）
- `python` を引数なしで実行して REPL（>>>）に入らないこと
- 複数行Pythonは .py を `python path/to/script.py` で実行、1行なら `python -c "..."` を使う
- bashのヒアドキュメント（<<）は使わない
- もし誤って `>>>` が表示されたら、必ず `exit()` して PowerShell に戻ってから続行する

# 出力（必須）

出力先：AIDD\planning\yaml\planning_v2.2\

1. セクション YAML（01〜16）を **1つずつ**生成
2. 01〜16 が全て確定した後にのみ 00_index.yaml を作成

（ファイル一覧）

- 01_executive_summary.yaml
- 02_background_and_problem.yaml
- 03_positioning_and_strategy.yaml
- 04_glossary_and_constraints.yaml
- 05_core_concepts_and_principles.yaml
- 06_system_design.yaml
- 07_quality_assurance_design.yaml
- 08_architecture_and_ui.yaml
- 09_visualization_and_export.yaml
- 10_rollout_plan.yaml
- 11_validation_and_meta_quality.yaml
- 12_measurement_and_kpi.yaml
- 13_execution_plan.yaml
- 14_risks_and_constraints.yaml
- 15_conclusion_next_steps.yaml
- 16_appendix.yaml
- 00_index.yaml（最後）

# 変換ルール（最低限）

- YAML root を配列にしない（rootはobject/mapping）
- meta は必ず含める（初期値は PENDING でよい：stampingMeta.py が確定させる）
- 重要主張（Goal/Problem/Principle/KPI/Gate/Constraint/Decision rule 等）は items に分解し、ID規約に従うIDを付与する
- items[].related.derivedfrom / tracesto は必ず空配列でも持たせる（わかる範囲で埋めてよい）
- 要約しすぎない（後工程で要件化できる粒度で保持する）

# 必須ツール（meta確定）

出力した全 YAML に対して、必ず以下を実行して meta を確定すること：

- AIDD\tools\stampingMeta.py を使用（prompt_id は全ファイル共通で "PRM-PLN-YAML-002"）
- hash-script は AIDD\hashtag\hashtag_generator.py を使用

# 実行手順（必須：1ファイルずつ）

各ファイルについて必ず次を順に実施：

1. 生成（対象1ファイルのみ）
2. schema_registry.yaml に基づく schema 検査（VALID確認）
3. stampingMeta.py を実行し meta.output_hash を確定（PENDING禁止）
4. 次の1ファイルへ

最後に（重要）：
A) 00_index.yaml を作成（meta必須、sections参照必須）
B) schema_registry.yaml に基づき index schema で VALID を確認
C) stampingMeta.py を実行し meta.output_hash を確定

# 追加ルール2：Gate強制（run_gates.py）

このタスクでは、成果物生成が完了したら必ず最後に run_gates.py を実行し、「GATES: PASS」を確認すること。
PASS が出ない限り、次工程へ進んではいけない（作業は未完了）。

実行コマンド（命名は TPL-OPS-RULES-002.yaml の規約に従う）：
python AIDD\tools\run_gates.py --repo-root . --target AIDD\planning\yaml\planning_v2.2 --schema-registry AIDD\RULES\schema_registry.yaml --report-out AIDD\reports\gate_report_planning_v2.2.json

判定：

- GATES: PASS → 合格
- GATES: FAIL / ERROR → 不合格
  - report JSON を確認し、FAIL原因（schema/meta/ID/曖昧語）を修正して再実行
  - PASS になるまで繰り返す

# 期待する最終状態（合格条件）

- 01〜16＋00_index が schema_registry.yaml に従う schema 検査で VALID
- 全ファイルに meta があり、PENDING が残っていない（output_hash含む）
- run_gates.py で GATES: PASS
- report: AIDD\reports\gate_report_planning_v2.2.json が最新PASS結果になっている
