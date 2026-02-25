# CLAUDE.md — Claude Code 運用ルール (REQ-OPS-RULES-CLAUDE-001)

このファイルは `RULES/REQ-OPS-RULES-CLAUDE-001.yaml` に基づき、Claude Code が要件定義作業を行う際に従うべきルールをまとめたものです。

---

## 適用範囲

- 対象ファイル: `AIDD/requirements/**/*.yaml`
- 使用ツール: Cline / Claude Code / issue_id.py / stampingMeta.py / ambiguous_checker.py / run_gates.py

---

## 要件定義ワークフロー

### Step 1 — 要件定義 YAML 作成

- テンプレート (`template.yaml`) を基に作成する
- **すべての ID フィールドは `PENDING` のままにする**
- **meta セクションも `PENDING` のままにする**
- 入力: 企画書 YAML（例: `PLN-PLN-CONCEPT-005`）
- 出力: `requirements_draft.yaml`（ID/meta 未確定）

### Step 2 — ID 付与

```powershell
python AIDD/tools/issue_id.py --prefix REQ --phase <PHASE> --purpose <PURPOSE>
```

- 要件ごとに**個別実行**する
- PHASE / PURPOSE は `AIDD/RULES/id_rules_registry.yaml` に従う
- 発行された ID を YAML に転記する

**実行例:**
```powershell
python AIDD/tools/issue_id.py --prefix REQ --phase FUNC --purpose WF
python AIDD/tools/issue_id.py --prefix REQ --phase NFUNC --purpose USABILITY
python AIDD/tools/issue_id.py --prefix REQ --phase CONST --purpose TECH
```

### Step 3 — 曖昧語チェック

```powershell
python AIDD/tools/ambiguous_checker.py --file <YAML_PATH>
```

- **合格条件: 曖昧語検出数 = 0**
- 検出された場合は定量的・検証可能な表現に修正し、再実行する
- PASS するまで次工程へ進まない

**曖昧語の例:** 適切に、十分に、できるだけ、なるべく、基本的に、一般的に、必要に応じて、適宜

### Step 4 — スキーマ検証

- スキーマ定義: `AIDD/RULES/schema_registry.yaml` の `requirements` キー
- **合格条件: 標準出力に `VALID` を含む**
- 失敗時はエラーメッセージを確認し YAML 構造を修正して再実行する

### Step 5 — meta 情報スタンプ

```powershell
python AIDD/tools/stampingMeta.py --file <YAML_PATH>
```

- **スキーマ検証 PASS 後にのみ実行する**
- 実行後に `meta.run_id` がファイル名と一致することを確認する
- 実行後に `meta.content_hash` が `PENDING` でないことを確認する

### Step 6 — 統合品質ゲート実行

```powershell
python AIDD\tools\run_gates.py --repo-root . --target AIDD/requirements/yaml/<VERSION_DIR> --schema-registry AIDD\RULES\schema_registry.yaml --report-out AIDD\reports\gate_report_requirements_<VERSION>.json
```

- **合格条件: 標準出力に `GATES: PASS` を含む**
- **PASS するまで次工程（設計フェーズ）へ進まない**
- 失敗時はレポート JSON (`AIDD/reports/gate_report_requirements_*.json`) を確認し原因を修正して再実行する
- すべての成果物が完成した**最後に 1 回**実行する

### Step 7 — トレーサビリティ検証

```powershell
python AIDD\tools\verify_traceability.py check ^
    --dirs AIDD/planning/yaml/planning_v2.2 AIDD/requirements/yaml/<VERSION_DIR> ^
    --report-out AIDD/reports/traceability_report_<VERSION>.json
```

- **合格条件: 標準出力に `TRACEABILITY: PASS` を含む**
- **PASS するまで次工程（設計フェーズ）へ進まない**
- 失敗時はレポート JSON (`AIDD/reports/traceability_report_*.json`) で原因を確認し、下記の `fix` コマンドで修正する

**PENDING な `derived_from` を対話的に修正する場合:**
```powershell
python AIDD\tools\verify_traceability.py fix ^
    --dirs AIDD/planning/yaml/planning_v2.2 AIDD/requirements/yaml/<VERSION_DIR> ^
    --target AIDD/requirements/yaml/<VERSION_DIR>
```

**非対話的に一括設定する場合（同一の上流 ID を全 PENDING に適用）:**
```powershell
python AIDD\tools\verify_traceability.py fix ^
    --dirs AIDD/planning/yaml/planning_v2.2 AIDD/requirements/yaml/<VERSION_DIR> ^
    --target AIDD/requirements/yaml/<VERSION_DIR> ^
    --set-derived-from PLN-PLN-CONCEPT-005 [--dry-run]
```

---

## ハードルール（必須遵守）

| ID | ルール | 強制内容 |
|----|--------|----------|
| HR-001 | 手採番 ID 禁止 | すべての ID は `issue_id.py` で発行し、`id_issued_log.yaml` に記録する |
| HR-002 | 曖昧語ゼロ要求 | `ambiguous_checker.py` で検出数 = 0 でなければ次工程不可 |
| HR-003 | meta 情報必須 | `stampingMeta.py` 実行後、PENDING フィールドが残存していないこと |
| HR-004 | 統合ゲート PASS 必須 | `run_gates.py` が PASS するまで次工程（設計）へ進まない |
| HR-005 | トレーサビリティ完全性 | すべての要件が `derived_from` で企画書 ID にトレース可能であること（`verify_traceability.py check` が PASS すること） |

---

## ターミナル操作ルール（Windows PowerShell）

- `python` を引数なしで起動して REPL（`>>>`）に入らない
- bash のヒアドキュメント（`<<`）を使わない
- `>>>` が出たら `exit()` して `PS>` に戻る

---

## ディレクトリ構造

```
AIDD/requirements/yaml/
  requirements_v1/
    requirements_document.yaml
    functional_requirements_detail.yaml
    non_functional_requirements_detail.yaml
  requirements_v2/
    ...
AIDD/reports/
  gate_report_requirements_v*.json
```

### ファイル命名規則

- 形式: `<phase>_<purpose>_<version>.yaml`
- 例: `requirements_document_v1.yaml` / `requirements_functional_v1.yaml`
- `meta.run_id` はファイル名（拡張子除く）と一致させる

---

## 品質チェックリスト

| 項目 | 自動化 | ツール |
|------|--------|--------|
| すべての ID が PENDING でない | 手動確認 | — |
| すべての meta フィールドが PENDING でない | 自動 | run_gates.py |
| 曖昧語検出数 = 0 | 自動 | ambiguous_checker.py |
| スキーマ検証 PASS | 自動 | jsonschema |
| すべての機能要件に `acceptance_criteria` が存在 | 手動確認 | — |
| すべての非機能要件に `metrics` と `target_value` が存在 | 手動確認 | — |
| トレーサビリティマトリクスが完全（すべての要件が `derived_from` を持つ） | 自動 | verify_traceability.py |
| `validation_summary` の数値が実際の要件数と一致 | 手動確認 | — |

---

## 変更管理

- 要件の追加・変更時は新バージョンディレクトリを作成する
- 変更理由を README.md または変更履歴 YAML に記録する
- ステータス遷移: `draft` → `review` → `approved` → `baseline`
- `approved` 以降の変更は変更管理プロセスに従う
- 要件変更時、`traces_to` で影響を受ける設計・テストも更新する

---

## エラー対処

| エラー | 原因 | 対処 |
|--------|------|------|
| YAML syntax error | インデント不正、コロン/ハイフン位置ミス | YAML バリデーターで構文チェック、サンプルと比較 |
| Schema validation failed | 必須フィールド欠落、型不一致 | エラーメッセージから該当箇所を特定、schema 定義と照合 |
| Ambiguous terms detected | 曖昧語が残存 | 検出された用語を定量的・検証可能な表現に置換 |
| meta.content_hash is PENDING | stampingMeta.py 未実行またはファイル保存後に再実行していない | ファイル保存後、stampingMeta.py を再実行 |
| GATES: FAIL | いずれかのゲート条件が不合格 | レポート JSON を確認し、FAIL の具体的原因（schema/meta/ID/曖昧語）を修正 |
| TRACEABILITY: FAIL | `derived_from` が未設定または無効な ID を参照 | レポート JSON で該当 ID を確認し、`verify_traceability.py fix` で修正 |
| broken link 検出 | 参照先 ID が存在しない | 参照先 YAML の `--dirs` への追加漏れを確認、または参照 ID を修正 |
