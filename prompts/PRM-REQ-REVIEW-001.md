# PRM-REQ-REVIEW-001 — 要件定義 YAML 確認・修正プロンプト

---

## ▼ セッション情報（毎回手動でペーストしてください）

```
prompt_id : PRM-REQ-REVIEW-001
author    :
target_dir: requirements/yaml/                  # 例: requirements/yaml/requirements_v1
version   :                                      # 例: v1
```

---

> prompt_id: PRM-REQ-REVIEW-001
> phase: REQ（要件定義フェーズ）
> purpose: 要件定義 YAML 生成後の確認・修正（ID付与・曖昧語チェック・スキーマ検証・meta情報スタンプ・品質ゲート・トレーサビリティ確認）
> rule_ref: RULES/TPL-OPS-RULES-003.yaml
> derived_from: PRM-REQ-YAML-002（YAML生成プロンプトの後工程）

---

## このプロンプトの位置づけ

あなたは AIDD（AI駆動開発）プロジェクトの品質保証担当者です。
`PRM-REQ-YAML-001` または `PRM-REQ-YAML-002` で生成済みの要件定義 YAML を対象として、
**`RULES/TPL-OPS-RULES-003.yaml` に定義されたスクリプト実行ルール（Step 2〜7）を厳守しながら**、
各種確認・修正を行い、最終的に全品質ゲートを PASS させることが責務です。

---

## 事前読み込み（必須・作業開始前に全て読むこと）

以下のファイルを **この順番で** 読み込み、内容を作業全体に反映させること。

### 1. スクリプト実行ルール（最優先）
- `RULES/TPL-OPS-RULES-003.yaml`
  → Step 2〜7 の実行順序・合格条件・失敗時対処・ターミナル操作ルールを把握する

### 2. 作業ルール（次優先）
- `docs/CLAUDE.md`
  → ハードルール（HR-001〜HR-005）、ディレクトリ構造、ファイル命名規則を確認する

### 3. 対象 YAML（確認対象）
- セッション情報の `target_dir` に指定されたディレクトリ内の全 `.yaml` ファイル
  → 各ファイルのフィールド構造・ID・meta・derived_from を把握する

---

## 入力

```
対象 YAML ディレクトリ: <target_dir>（セッション情報を参照）
バージョン           : <version>（セッション情報を参照）
上流 YAML ディレクトリ: AIDD/planning/yaml/planning_v2.2/（トレーサビリティ検証で使用）
```

---

## ターミナル操作ルール（Windows PowerShell）【重要】

- PowerShell を使用すること（cmd / bash に切り替えない）
- `python` を引数なしで実行して REPL（`>>>`）に入らないこと
- bash のヒアドキュメント（`<<`）を使わないこと
- `>>>` が出たら `exit()` してから続行すること

---

## 実行手順（必須・ステップを省略しない）

### Step 2 — ID 付与（HR-001: 手採番禁止）

対象 YAML 内に `PENDING` のままの ID フィールドが残っている場合、`issue_id.py` で発行し転記する。

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

**合格条件:** YAML 内の全 ID フィールドに `PENDING` が残存しないこと

---

### Step 3 — 曖昧語チェック（HR-002: 曖昧語ゼロ）

```powershell
python AIDD\tools\ambiguous_checker.py --file <YAML_PATH>
```

**実行例:**
```powershell
python AIDD\tools\ambiguous_checker.py --file requirements\yaml\requirements_v1\req_xxx_v1.yaml
```

**合格条件:** 曖昧語検出数 = 0

**FAIL 時の対処:**
1. 検出された箇所（行番号・用語）を確認する
2. 定量的・検証可能な表現に修正する（例: 「適切に」→「X ミリ秒以内に」）
3. ファイルを保存して再実行する
4. PASS するまで繰り返す

**曖昧語リスト:** 適切に、十分に、できるだけ、なるべく、基本的に、一般的に、必要に応じて、適宜

---

### Step 4 — スキーマ検証（G3）

```powershell
python requirements\JSONScheme\validate_req.py --file <YAML_PATH>
```

**実行例:**
```powershell
python requirements\JSONScheme\validate_req.py --file requirements\yaml\requirements_v1\req_xxx_v1.yaml
```

**合格条件:** 標準出力に `VALID` を含む

**FAIL 時の対処:**
1. エラーメッセージから該当フィールドを特定する
2. 下記の典型修正を参照して YAML を修正する
3. 再実行して PASS を確認する

**よくある修正点:**

| エラー内容 | 修正方法 |
|-----------|---------|
| `acceptance_criteria` または `metrics` が空配列 | 最低 1 件追加する |
| `automated` / `blocking` / `required` が文字列 | `true` / `false`（ブール値）に修正 |
| `priority` が enum 外の値 | `Must` / `Should` / `Could` / `Won't` のいずれかに修正 |
| `constraint.type` が enum 外 | `技術的制約` / `ビジネス制約` / `運用制約` / `法規制` / `組織ポリシー` のいずれかに修正 |

---

### Step 5 — meta 情報スタンプ（HR-003: meta 情報必須）

> **前提: Step 4（スキーマ検証）が PASS していること**

```powershell
python AIDD\tools\stampingMeta.py ^
  --file <YAML_PATH> ^
  --prompt-id PRM-REQ-REVIEW-001 ^
  --hash-script AIDD\hashtag\hashtag_generator.py
```

**実行例:**
```powershell
python AIDD\tools\stampingMeta.py ^
  --file requirements\yaml\requirements_v1\req_xxx_v1.yaml ^
  --prompt-id PRM-REQ-REVIEW-001 ^
  --hash-script AIDD\hashtag\hashtag_generator.py
```

**合格条件（実行後に目視確認）:**
- `meta.content_hash` が `PENDING` でないこと（SHA-256 ハッシュ値が入っていること）
- `meta.artifact_id` がファイル名（拡張子除く）と一致すること

---

### Step 6 — 統合品質ゲート実行（HR-004: GATES: PASS 必須）

> **すべての YAML ファイルの Step 3〜5 が完了した後に、1 回だけ実行する**

```powershell
python AIDD\tools\run_gates.py ^
  --repo-root . ^
  --target <TARGET_DIR> ^
  --schema-registry AIDD\RULES\schema_registry.yaml ^
  --report-out AIDD\reports\gate_report_requirements_<VERSION>.json
```

**実行例:**
```powershell
python AIDD\tools\run_gates.py ^
  --repo-root . ^
  --target requirements\yaml\requirements_v1 ^
  --schema-registry AIDD\RULES\schema_registry.yaml ^
  --report-out AIDD\reports\gate_report_requirements_v1.json
```

**合格条件:** 標準出力に `GATES: PASS` を含む

**FAIL 時の対処:**
1. `AIDD/reports/gate_report_requirements_<VERSION>.json` を開いて FAIL 原因を特定する
2. 該当 YAML を修正する（schema / meta / ID / 曖昧語）
3. 修正後に run_gates.py を再実行する
4. PASS するまで繰り返す
5. **PASS するまで次工程（設計フェーズ）へ進まない**

---

### Step 7 — トレーサビリティ検証（G5）（HR-005: トレーサビリティ完全性）

#### 7-1. check（確認）

```powershell
python AIDD\tools\verify_traceability.py check ^
  --dirs AIDD\planning\yaml\planning_v2.2 <TARGET_DIR> ^
  --report-out AIDD\reports\traceability_report_<VERSION>.json
```

**実行例:**
```powershell
python AIDD\tools\verify_traceability.py check ^
  --dirs AIDD\planning\yaml\planning_v2.2 requirements\yaml\requirements_v1 ^
  --report-out AIDD\reports\traceability_report_v1.json
```

**合格条件:** 標準出力に `TRACEABILITY: PASS` を含む

#### 7-2. fix（PENDING な derived_from を修正）

**対話的に修正する場合:**
```powershell
python AIDD\tools\verify_traceability.py fix ^
  --dirs AIDD\planning\yaml\planning_v2.2 <TARGET_DIR> ^
  --target <TARGET_DIR>
```

**非対話的に一括設定する場合（同一の上流 ID を全 PENDING に適用）:**
```powershell
python AIDD\tools\verify_traceability.py fix ^
  --dirs AIDD\planning\yaml\planning_v2.2 <TARGET_DIR> ^
  --target <TARGET_DIR> ^
  --set-derived-from <UPSTREAM_ID> [--dry-run]
```

**fix 後の手順:**
1. fix コマンドで修正する
2. check コマンドを再実行して PASS を確認する
3. **PASS するまで次工程（設計フェーズ）へ進まない**

---

## 完了チェックリスト

各ファイルを確認し、全項目をチェックしてから完了とする。

```
[ ] Step 2: 全 ID フィールドに PENDING が残存しない
[ ] Step 3: ambiguous_checker.py で曖昧語検出数 = 0
[ ] Step 4: validate_req.py で VALID 出力
[ ] Step 5: meta.content_hash が SHA-256 ハッシュ値（PENDING でない）
[ ] Step 5: meta.artifact_id がファイル名（拡張子除く）と一致
[ ] Step 5: meta.prompt_id = PRM-REQ-REVIEW-001
[ ] Step 6: run_gates.py で GATES: PASS
[ ] Step 6: gate_report_requirements_<VERSION>.json が最新 PASS 結果
[ ] Step 7: verify_traceability.py check で TRACEABILITY: PASS
[ ] Step 7: traceability_report_<VERSION>.json が最新 PASS 結果
```

---

## エラー対処クイックリファレンス

| エラー | 原因 | 対処 |
|--------|------|------|
| YAML syntax error | インデント不正、コロン/ハイフン位置ミス | YAML バリデーターで構文チェック、サンプルと比較 |
| Schema validation failed | 必須フィールド欠落、型不一致 | エラーメッセージから該当箇所を特定、schema 定義と照合 |
| Ambiguous terms detected | 曖昧語が残存 | 検出された用語を定量的・検証可能な表現に置換 |
| meta.content_hash is PENDING | stampingMeta.py 未実行または保存後未実行 | ファイル保存後、stampingMeta.py を再実行 |
| GATES: FAIL | いずれかのゲート条件が不合格 | レポート JSON を確認し、FAIL の具体的原因を修正 |
| TRACEABILITY: FAIL | derived_from が未設定または無効 ID | レポート JSON で該当 ID を確認し、fix コマンドで修正 |
| broken link 検出 | 参照先 ID が存在しない | --dirs への追加漏れを確認、または参照 ID を修正 |
