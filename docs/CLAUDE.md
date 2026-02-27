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

### Step 2〜7 — スクリプト実行（確認・修正）

> **YAML 生成後のスクリプト実行（ID付与・曖昧語チェック・スキーマ検証・meta情報スタンプ・品質ゲート・トレーサビリティ確認）は、別セッションで実施する。**
>
> - ルール定義: `RULES/TPL-OPS-RULES-003.yaml`
> - 実行プロンプト: `prompts/PRM-REQ-REVIEW-001.md`

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
