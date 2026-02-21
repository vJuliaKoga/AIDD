あなたは仕様書（Markdown）を、分割 YAML（複数ファイル）へ変換し、さらに JSON Schema で構造検査まで行う作業者です。

# 入力

- AIDD\planning\planning_v2.2.md

# 共通テンプレ（必読）

- AIDD\planning\yaml\planning_v2.2\planning.template.yaml
  以降で生成する各セクション YAML（01〜16）は、このテンプレの構造（meta/section/items/related）に厳密準拠すること。
  ※テンプレからキーを削除しない。キー名を変えない。rootは必ずmapping。
  ※ID規約は PREFIX-PHASE-PURPOSE-NNN に従うこと（例：PLN-PLN-EXEC-001 / PRM-PLN-YAML-001）。

# 構造検査（必須）

- AIDD\planning\yaml\planning_v2.2\planning.section.schema.json
  生成した各セクション YAML（01〜16）を、上記 JSON Schema に適合するか必ず検査し、不適合なら修正すること。
- AIDD\planning\yaml\planning_v2.2\planning.index.schema.json
  最後に作成する 00_index.yaml を、上記 JSON Schema に適合するか必ず検査し、不適合なら修正すること。

【重要：ターミナル操作ルール（Windows PowerShell）】

- VSCodeターミナルでは PowerShell を使用すること（cmd/bashに切り替えない）
- `python` を引数なしで実行して REPL（>>>）に入らないこと
- 複数行Pythonは作成した .py ファイルを `python path/to/script.py` で実行するか、1行なら `python -c "..."` を使う
- bashのヒアドキュメント（<<）は使わないこと
- もし誤って `>>>` が表示されたら、必ず `exit()` して PowerShell に戻ってから続行すること

# 出力（必須）

出力先：AIDD\planning\yaml\planning_v2.2\

1. 00_index.yaml

- 企画全体のインデックス（セクション一覧、参照先ファイル名、version、source path など）を記載
- root は mapping
- meta を必ず含める（値はPENDINGでOK）
- 重要：00_index.yaml は 01〜16 の生成・検査・meta確定がすべて完了した後にのみ作成すること

2. セクション YAML（必須：01〜16）

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

# 変換ルール

A) 各セクション YAML は planning.template.yaml の構造に厳密準拠すること（必須）
B) YAML root を配列にしない（rootはobject/mapping）
C) meta は必ず含める（初期値は PENDING でよい：stampingMeta.py が確定させる）
D) 重要主張（Goal/Problem/Principle/KPI/Gate/Constraint/Decision rule 等）は items に分解し、ID規約（PREFIX-PHASE-PURPOSE-NNN）に従うIDを付与する
E) 企画書内の定量基準（例：3クリック以内、1週間以内、追加ノード3個以内、Deep Eval 0.8 等）は metric / decision_rule として落とす
F) items[].related.derivedfrom / tracesto は必ず空配列でも持たせる（わかる範囲で埋めてよい）
G) 要約しすぎない（後工程で要件化できる粒度で保持する）

# 必須ツール（meta確定）

出力した全 YAML に対して、必ず以下を実行して meta を確定すること：

- AIDD\tools\stampingMeta.py を使用（prompt_id は全ファイル共通で "PRM-PLN-YAML-001"）
- hash-script は AIDD\hashtag\hashtag_generator.py を使用
  stampingMeta.py は YAML を読み込み、hash-script で sha256 を算出して meta.output_hash を埋めて保存する。

# 実行手順（必須：1ファイルずつ生成して品質を担保）

※実行はPowerShellで行い、pythonを引数なしで起動してREPL(>>>)に入らないこと。

0. planning_v2.2.md を読み、セクション分割の方針（01〜16の対応）だけ決める（この時点ではYAMLを一括生成しない）

1. 01_executive_summary.yaml を生成（planning.template.yaml に厳密準拠）
2. planning.section.schema.json で 01 を構造検査 → 不適合なら修正して再検査
3. 01 に stampingMeta.py（hash-script=hashtag_generator.py）を実行して meta.output_hash を確定

4. 02_background_and_problem.yaml を生成
5. schema 検査 → 修正 → 再検査
6. stampingMeta 実行（meta確定）

...（同様に 16 まで繰り返す）
※注意：同時に複数セクションYAMLを生成してはいけません。必ず「1ファイル生成→schema検査→stampingMetaで確定」を完了してから次へ進んでください。

最後に（重要）：
A) 00_index.yaml を作成（meta必須、sections参照必須）
B) planning.index.schema.json で 00_index.yaml を構造検査 → 不適合なら修正して再検査
C) 00_index.yaml に stampingMeta.py を実行して meta.output_hash を確定

# stampingMeta 実行例（Windows）

python AIDD\tools\stampingMeta.py --file AIDD\planning\yaml\planning_v2.2\01_executive_summary.yaml --prompt-id PRM-PLN-YAML-001 --hash-script AIDD\hashtag\hashtag_generator.py
...
python AIDD\tools\stampingMeta.py --file AIDD\planning\yaml\planning_v2.2\16_appendix.yaml --prompt-id PRM-PLN-YAML-001 --hash-script AIDD\hashtag\hashtag_generator.py
python AIDD\tools\stampingMeta.py --file AIDD\planning\yaml\planning_v2.2\00_index.yaml --prompt-id PRM-PLN-YAML-001 --hash-script AIDD\hashtag\hashtag_generator.py

# 期待する最終状態（合格条件）

- 01〜16 が planning.section.schema.json に適合している
- 00_index.yaml が planning.index.schema.json に適合している
- 全ファイル（00〜16）に meta.run_id / meta.prompt_id / meta.timestamp / meta.model / meta.output_hash が存在する
- meta.output_hash が PENDING のまま残らない（必ず sha256 が入っている）
- 00_index.yaml から各セクション YAML を参照できる
