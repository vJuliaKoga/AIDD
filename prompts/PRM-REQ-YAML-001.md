# PRM-REQ-YAML-001 — 要件定義 YAML 生成プロンプト

> prompt_id: PRM-REQ-YAML-001
> phase: REQ（要件定義フェーズ）
> purpose: 企画書 YAML から要件定義 YAML を生成し、品質ゲートを全て通過させる
> derived_from: PRM-PLN-YAML-002（プロンプト設計パターン継承）

---

## このプロンプトの位置づけ

あなたは AIDD（AI駆動開発）プロジェクトの要件定義作業者です。
企画書 YAML（planning_v2.2）を入力として、`req.template.yaml` の構造に従った要件定義 YAML を生成し、
**品質ゲート（G1〜G5 + トレーサビリティ）を全て通過させる**ことが責務です。

---

## 事前読み込み（必須・作業開始前に全て読むこと）

以下のファイルを **この順番で** 読み込み、内容を作業全体に反映させること。

### 1. 作業ルール（最優先）
- `docs/CLAUDE.md`
  → Step 1〜7 のワークフロー、ハードルール（HR-001〜HR-005）、ターミナル操作ルールを把握する

### 2. プロダクト要件（スコープ確認）
- `docs/PRD.md`
  → プロダクト概要・ゴール・KPI・機能要件（F-001〜F-010）・品質ゲート定義を確認する

### 3. 技術スタック（非機能要件・制約の参照元）
- `docs/技術スタック.md`
  → 技術選定・DB設計・AI評価ツール設定・制約事項を確認する

### 4. テンプレート（構造の厳守）
- `requirements/yaml/req.template.yaml`
  → 全セクション構造・フィールド名・コメントを把握する。**このテンプレートからキーを削除しない・キー名を変えない**

### 5. JSON スキーマ（検証基準）
- `requirements/JSONScheme/req.schema.json`
  → G3 検証で使用するスキーマ。enum 値・必須フィールド・ID パターンを把握する

---

## 入力

```
対象企画書 YAML ディレクトリ: AIDD/planning/yaml/planning_v2.2/
対象セクション: <ユーザーが指定したセクション番号または全セクション>
```

---

## テンプレート（必読・厳守）

- `requirements/yaml/req.template.yaml`

生成する要件定義 YAML は、このテンプレートの構造に **厳密準拠** すること。

```
厳守事項:
- YAML root は必ず mapping（配列にしない）
- meta セクションは必須（prompt_id / model / timestamp / content_hash は PENDING でよい）
- req_id / constraint_id / entity_id 等は PENDING のまま作成（Step 2 で issue_id.py が付与）
- derived_from は企画書 YAML の該当 ID を記載（不明な場合は PENDING）
- acceptance_criteria は必ず 1 件以上（functional_requirements 各項目）
- metrics は必ず 1 件以上（non_functional_requirements 各項目・target_value は定量値）
- description / title 等のコンテンツフィールドに空文字を残さない
- 曖昧語（適切に、十分に、できるだけ、なるべく、基本的に、一般的に、必要に応じて、適宜）を使用しない
```

---

## 品質ゲート定義（本プロンプトで達成すべき合格基準）

| ゲート | 内容 | 合格基準 | ツール |
|--------|------|---------|--------|
| G1 | 曖昧語チェック | 検出数 = 0 | ambiguous_checker.py |
| G2 | 検証可能性 | 全機能要件に acceptance_criteria ≥ 1 / 全非機能要件に metrics ≥ 1（定量値） | 手動確認 + スキーマ |
| G3 | 構造一貫性 | req.schema.json 検証 VALID | validate_req.py |
| G4 | AI 評価スコア | Deep Eval スコア ≥ 0.8 | run_gates.py |
| G5 | トレーサビリティ | 全要件に derived_from が設定済み | verify_traceability.py |

---

## 実行手順（必須・ステップを省略しない）

【重要：ターミナル操作ルール（Windows PowerShell）】
- PowerShell を使用すること（cmd/bash に切り替えない）
- `python` を引数なしで実行して REPL（`>>>`）に入らないこと
- bash のヒアドキュメント（`<<`）を使わないこと
- `>>>` が出たら `exit()` してから続行すること

---

### Step 1 — 企画書 YAML の読み込みと要件抽出

1. `planning/yaml/planning_v2.2/00_index.yaml` を読み、セクション一覧を把握する
2. 指定セクションの YAML（例: `05_core_concepts_and_principles.yaml`）を読む
3. `items[]` を精査し、要件として落とすべき主張（Goal / Problem / Principle / KPI / Gate / Constraint 等）を抽出する
4. `req.template.yaml` をベースに **1つの** 要件定義 YAML のドラフトを生成する
   - 全 ID フィールドは `PENDING` のままにする
   - meta フィールドも `PENDING` のままにする（`author` と `source_type` のみ記載）
   - `derived_from` には企画書の該当 ID を記載する（例: `PLN-PLN-CONCEPT-005`）

**出力先:** `requirements/yaml/<VERSION_DIR>/<filename>.yaml`
（例: `requirements/yaml/requirements_v1/req_core_concepts_v1.yaml`）

---

### Step 2 — ID 付与

各要件・制約・エンティティ・統合要件・品質ゲートに ID を付与する。
**手採番禁止（HR-001）**。必ず `issue_id.py` を経由すること。

```powershell
# 機能要件
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase FUNC --purpose <カテゴリ英語>

# 非機能要件
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase NFUNC --purpose <カテゴリ英語>

# 制約
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase CONST --purpose <内容英語>

# データエンティティ
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase DATA --purpose <エンティティ名>

# 統合要件
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase INTEG --purpose <目的英語>

# 品質ゲート
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase QG --purpose <フェーズ名>

# 要件定義書（doc_id）
python AIDD\tools\id_registry\issue_id.py --prefix REQ --phase REQ --purpose DOC
```

発行された ID を YAML に転記し、`PENDING` を置き換える。

---

### Step 3 — 曖昧語チェック

```powershell
python AIDD\tools\ambiguous_checker.py --file requirements\yaml\<VERSION_DIR>\<filename>.yaml
```

- **合格条件: 検出数 = 0**
- 検出された場合は定量的・検証可能な表現に修正して再実行する
- PASS するまで次工程へ進まない（HR-002）

---

### Step 4 — スキーマ検証（G3）

```powershell
python requirements\JSONScheme\validate_req.py --file requirements\yaml\<VERSION_DIR>\<filename>.yaml
```

- **合格条件: 標準出力に `VALID` を含む**
- 失敗時はエラーメッセージを確認し YAML 構造を修正して再実行する
- PASS するまで次工程へ進まない

**よくある修正点:**
- `acceptance_criteria` または `metrics` が空配列になっている → 最低 1 件追加
- `automated` / `blocking` / `required` がブール値でなく文字列になっている → `true` / `false` に修正
- `priority` が enum 外の値になっている → `Must` / `Should` / `Could` / `Won't` のいずれかに修正
- `constraint.type` が enum 外 → `技術的制約` / `ビジネス制約` / `運用制約` / `法規制` / `組織ポリシー` のいずれかに修正

---

### Step 5 — meta 情報スタンプ

```powershell
python AIDD\tools\stampingMeta.py ^
  --file requirements\yaml\<VERSION_DIR>\<filename>.yaml ^
  --prompt-id PRM-REQ-YAML-001 ^
  --hash-script AIDD\hashtag\hashtag_generator.py
```

- **スキーマ検証 PASS 後にのみ実行する**
- 実行後に `meta.content_hash` が `PENDING` でないことを確認する
- 実行後に `meta.artifact_id` がファイル名と一致することを確認する（HR-003）

---

### Step 6 — 統合品質ゲート実行

```powershell
python AIDD\tools\run_gates.py ^
  --repo-root . ^
  --target requirements\yaml\<VERSION_DIR> ^
  --schema-registry AIDD\RULES\schema_registry.yaml ^
  --report-out AIDD\reports\gate_report_requirements_<VERSION>.json
```

- **合格条件: 標準出力に `GATES: PASS` を含む**
- PASS するまで次工程へ進まない（HR-004）
- 失敗時はレポート JSON を確認し、FAIL 原因（schema / meta / ID / 曖昧語）を修正して再実行する

---

### Step 7 — トレーサビリティ検証（G5）

```powershell
python AIDD\tools\verify_traceability.py check ^
  --dirs AIDD\planning\yaml\planning_v2.2 requirements\yaml\<VERSION_DIR> ^
  --report-out AIDD\reports\traceability_report_<VERSION>.json
```

- **合格条件: 標準出力に `TRACEABILITY: PASS` を含む**
- PASS するまで次工程（設計フェーズ）へ進まない（HR-005）
- PENDING な `derived_from` が残っている場合は `fix` コマンドで修正する:

```powershell
python AIDD\tools\verify_traceability.py fix ^
  --dirs AIDD\planning\yaml\planning_v2.2 requirements\yaml\<VERSION_DIR> ^
  --target requirements\yaml\<VERSION_DIR>
```

---

## 変換ルール

| ルール | 内容 |
|--------|------|
| 粒度 | 企画書の 1 items[] エントリ = 原則 1 要件（分割可） |
| 曖昧語禁止 | 「適切に」「十分に」「できるだけ」「なるべく」「基本的に」「一般的に」「必要に応じて」「適宜」を使わない |
| 定量化 | 非機能要件の target_value は必ず数値または比率で記載（例: `≤200ms`, `≥99.9%`, `100%`） |
| トレーサビリティ | derived_from に企画書 ID（`PLN-PLN-XXXXX-NNN`）を記載。設計・テストの traces_to は後工程で追加 |
| acceptance_criteria | verification_method は `テスト` / `レビュー` / `デモ` / `分析` のいずれかを選択 |
| 要約禁止 | 後工程で設計できる粒度を保持する。企画書の意図を削らない |

---

## 出力先・命名規則

```
requirements/yaml/
  requirements_v<N>/
    req_<セクション名>_v<N>.yaml   # 例: req_core_concepts_v1.yaml
    req_quality_gates_v<N>.yaml
    ...
AIDD/reports/
  gate_report_requirements_v<N>.json
  traceability_report_v<N>.json
```

---

## 期待する最終状態（合格条件）

- [ ] YAML が `req.template.yaml` の全セクション構造を持つ
- [ ] 全 ID フィールドに `REQ-*` 形式の ID が設定されている（PENDING なし）
- [ ] `meta.content_hash` が SHA-256 ハッシュ値（PENDING なし）
- [ ] `meta.prompt_id` = `PRM-REQ-YAML-001`
- [ ] G1: `ambiguous_checker.py` で検出数 = 0
- [ ] G3: `validate_req.py` で `VALID` 出力
- [ ] G4: `run_gates.py` で `GATES: PASS`
- [ ] G5: `verify_traceability.py check` で `TRACEABILITY: PASS`
- [ ] レポート JSON（gate_report / traceability_report）が最新 PASS 結果
