# PRM-REQ-YAML-003 — 要件定義 YAML 生成プロンプト（生成専用）

---

## ▼ セッション情報（毎回手動でペーストしてください）

```
prompt_id : PRM-REQ-YAML-003
author    :
target_dir: requirements/yaml/                  # 例: requirements/yaml/requirements_v1
version   :                                      # 例: v1
```

---

> prompt_id: PRM-REQ-YAML-003
> phase: REQ（要件定義フェーズ）
> purpose: 企画書 YAML から要件定義 YAML を生成する（Step 1 専任）
> derived_from: PRM-REQ-YAML-002（バッチ生成パターン継承）
> next_prompt: PRM-REQ-REVIEW-001（確認・修正・スクリプト実行）

---

## このプロンプトの位置づけ

あなたは AIDD（AI駆動開発）プロジェクトの要件定義作業者です。
企画書 YAML（planning_v2.2）を入力として、`req.template.yaml` の構造に従った要件定義 YAML を**生成する**ことが本プロンプトの責務です。

> **重要: ID付与・曖昧語チェック・スキーマ検証・meta情報スタンプ・品質ゲート実行・トレーサビリティ確認（Step 2〜7）は、本プロンプトでは実施しない。**
> YAML 生成完了後、別セッションで `prompts/PRM-REQ-REVIEW-001.md` を使用して実施すること。

---

## 事前読み込み（必須・作業開始前に全て読むこと）

以下のファイルを **この順番で** 読み込み、内容を作業全体に反映させること。

### 1. 作業ルール（最優先）

- `docs/CLAUDE.md`
  → ハードルール（HR-001〜HR-005）、ディレクトリ構造、ファイル命名規則を把握する
  → Step 2〜7 のスクリプト実行ルールは `RULES/TPL-OPS-RULES-003.yaml` を参照

### 2. プロダクト要件（スコープ確認）

- `docs/PRD.md`
  → プロダクト概要・ゴール・KPI・機能要件（F-001〜F-010）・品質ゲート定義を確認する

### 3. 技術スタック（非機能要件・制約の参照元）

- `docs/技術スタック.md`
  → 技術選定・DB設計・AI評価ツール設定・制約事項を確認する

### 4. テンプレート（構造の厳守）

- `requirements/yaml/req.template.yaml`
  → 全セクション構造・フィールド名・コメントを把握する。**このテンプレートからキーを削除しない・キー名を変えない**

### 5. JSON スキーマ（検証基準の把握）

- `requirements/JSONScheme/req.schema.json`
  → G3 検証で使用するスキーマ。enum 値・必須フィールド・ID パターンを事前把握し、**生成時点から構造的に正しい YAML を作る**

---

## 入力

```
対象企画書 YAML ディレクトリ: AIDD/planning/yaml/planning_v2.2/
対象セクション: 01〜16（全セクション一括処理）
処理モード: バッチ処理（スキップ対象セクションを自動除外）
```

---

## セクション定義と処理判定

| セクション番号 | ファイル名例            | 内容                   | 処理判定                             |
| -------------- | ----------------------- | ---------------------- | ------------------------------------ |
| 01             | 01executivesummary.yaml | エグゼクティブサマリー | スキップ（要約のため要件化不要）     |
| 02             | 02.yaml                 | —                      | 要件定義作成                         |
| 03             | 03.yaml                 | —                      | 要件定義作成                         |
| 04             | 04.yaml                 | —                      | 要件定義作成                         |
| 05             | 05.yaml                 | —                      | 要件定義作成                         |
| 06             | 06.yaml                 | —                      | 要件定義作成                         |
| 07             | 07.yaml                 | —                      | 要件定義作成                         |
| 08             | 08.yaml                 | —                      | 要件定義作成                         |
| 09             | 09.yaml                 | —                      | 要件定義作成                         |
| 10             | 10.yaml                 | —                      | 要件定義作成                         |
| 11             | 11.yaml                 | —                      | 要件定義作成                         |
| 12             | 12.yaml                 | —                      | 要件定義作成                         |
| 13             | 13.yaml                 | —                      | 要件定義作成                         |
| 14             | 14.yaml                 | —                      | 要件定義作成                         |
| 15             | 15.yaml                 | —                      | 要件定義作成                         |
| 16             | 16appendix.yaml         | 付録                   | スキップ（参考資料のため要件化不要） |

---

## スキップ判定ルール

以下の条件に該当するセクションは**自動スキップ**し、要件定義 YAML を生成しない。

**セクション番号 01（エグゼクティブサマリー）**
- 理由: プロジェクト全体の要約であり、個別要件として定義する内容を含まない

**セクション番号 16（付録）**
- 理由: 参考資料・補足情報であり、要件として実装・検証する対象ではない

**ファイル名に以下のキーワードを含む場合（追加スキップ対象）**
- summary、appendix、glossary、reference、index
- 理由: 要件定義の対象外となる補助的コンテンツ

**items[] が空または存在しない場合**
- 理由: 要件として抽出すべき内容がない

### スキップ時の出力

スキップしたセクションは以下の形式でログ出力し、次のセクションへ進む：

`[SKIP] セクション XX: <ファイル名> — <スキップ理由>`

---

## テンプレート（必読・厳守）

- `requirements/yaml/req.template.yaml`

生成する要件定義 YAML は、このテンプレートの構造に **厳密準拠** すること。

```
厳守事項:
- YAML root は必ず mapping（配列にしない）
- meta セクションは必須（prompt_id / model / timestamp / content_hash は PENDING でよい）
- req_id / constraint_id / entity_id 等は PENDING のまま作成（後工程の Step 2 で issue_id.py が付与）
- derived_from は企画書 YAML の該当 ID を記載（不明な場合は PENDING）
- acceptance_criteria は必ず 1 件以上（functional_requirements 各項目）
- metrics は必ず 1 件以上（non_functional_requirements 各項目・target_value は定量値）
- description / title 等のコンテンツフィールドに空文字を残さない
- 曖昧語（適切に、十分に、できるだけ、なるべく、基本的に、一般的に、必要に応じて、適宜）を使用しない
```

---

## 品質ゲート定義（達成目標・確認は後工程 PRM-REQ-REVIEW-001 で実施）

| ゲート | 内容             | 合格基準                                                                    | 確認ツール（後工程）   |
| ------ | ---------------- | --------------------------------------------------------------------------- | ---------------------- |
| G1     | 曖昧語チェック   | 検出数 = 0                                                                  | ambiguous_checker.py   |
| G2     | 検証可能性       | 全機能要件に acceptance_criteria ≥ 1 / 全非機能要件に metrics ≥ 1（定量値） | 手動確認 + スキーマ    |
| G3     | 構造一貫性       | req.schema.json 検証 VALID                                                  | validate_req.py        |
| G4     | AI 評価スコア    | Deep Eval スコア ≥ 0.8                                                      | run_gates.py           |
| G5     | トレーサビリティ | 全要件に derived_from が設定済み                                            | verify_traceability.py |

> スクリプトによる実際の確認・修正は `prompts/PRM-REQ-REVIEW-001.md` で別セッションにて実施する。
> 本プロンプトでは YAML 生成時点から上記基準を**構造的に満たす状態**で出力することを目指す。

---

## 実行手順

### Step 1 — 企画書 YAML の読み込みと要件抽出・生成

処理単位は**1セクション = 1ファイル**。必ず以下の手順で1ファイルずつ完成させてから次へ進む。

1. `planning/yaml/planning_v2.2/00_index.yaml` を読み、セクション一覧を把握する
2. セクション01から順に処理する（スキップ判定を先に行う）
3. 対象セクションの YAML（例: `05_core_concepts_and_principles.yaml`）を読む
4. `items[]` を精査し、要件として落とすべき主張（Goal / Problem / Principle / KPI / Gate / Constraint 等）を抽出する
5. `req.template.yaml` をベースに **1つの** 要件定義 YAML のドラフトを生成する

**生成時の必須事項:**

| 項目 | 設定値 |
|------|--------|
| 全 ID フィールド | `PENDING`（issue_id.py 実行前） |
| meta.prompt_id | `PRM-REQ-YAML-003` |
| meta.author | セッション情報の `author` 値 |
| meta.source_type | `ai` |
| meta.model / timestamp / content_hash | `PENDING` |
| derived_from | 企画書の該当 ID（例: `PLN-PLN-CONCEPT-005`）。不明な場合は `PENDING` |
| acceptance_criteria | 各機能要件に 1 件以上（verification_method は `テスト` / `レビュー` / `デモ` / `分析` のいずれか） |
| metrics | 各非機能要件に 1 件以上（target_value は定量値: 例 `≤200ms`, `≥99.9%`, `100%`） |

**出力先:** `requirements/yaml/<VERSION_DIR>/<filename>.yaml`
（例: `requirements/yaml/requirements_v1/req_core_concepts_v1.yaml`）

6. 上記を02〜15まで繰り返す（スキップ対象を除く）
7. 全ファイルが生成完了したら、生成ファイル一覧を出力する

---

### Step 2〜7 — 確認・修正・スクリプト実行（本プロンプトでは実施しない）

> **YAML 生成完了後、新しいセッションで以下のプロンプトを使用して実施すること。**
>
> - 実行プロンプト: `prompts/PRM-REQ-REVIEW-001.md`
> - スクリプト実行ルール: `RULES/TPL-OPS-RULES-003.yaml`
>
> 引き継ぎ情報（次セッションのセッション情報欄にペースト）:
> ```
> prompt_id : PRM-REQ-REVIEW-001
> author    : <本セッションの author>
> target_dir: requirements/yaml/<VERSION_DIR>
> version   : <VERSION>
> ```

---

## 変換ルール

| ルール              | 内容                                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| 粒度                | 企画書の 1 items[] エントリ = 原則 1 要件（複合する場合は分割可）                                        |
| 曖昧語禁止          | 「適切に」「十分に」「できるだけ」「なるべく」「基本的に」「一般的に」「必要に応じて」「適宜」を使わない |
| 定量化              | 非機能要件の target_value は必ず数値または比率で記載（例: `≤200ms`, `≥99.9%`, `100%`）                   |
| トレーサビリティ    | derived_from に企画書 ID（`PLN-PLN-XXXXX-NNN`）を記載。設計・テストの traces_to は後工程で追加           |
| acceptance_criteria | verification_method は `テスト` / `レビュー` / `デモ` / `分析` のいずれかを選択                          |
| 要約禁止            | 後工程で設計できる粒度を保持する。企画書の意図を削らない                                                 |

---

## 出力先・命名規則

```
requirements/yaml/
  requirements_v<N>/
    req_<セクション名>_v<N>.yaml   # 例: req_core_concepts_v1.yaml
    req_quality_gates_v<N>.yaml
    ...
```

> レポートファイル（gate_report / traceability_report）は `PRM-REQ-REVIEW-001.md` 実行後に生成される。

---

## 期待する最終状態（本プロンプト完了基準）

本プロンプトの完了条件は **YAML 生成完了** である。スクリプト確認は後工程。

```
[ ] 対象セクション（02〜15、スキップ除く）の YAML ファイルが全て生成されている
[ ] 各 YAML が req.template.yaml の全セクション構造を持つ
[ ] 全 ID フィールドが PENDING のままである（手採番していない）
[ ] meta.prompt_id = PRM-REQ-YAML-003 が設定されている
[ ] meta.author が設定されている（PENDING でない）
[ ] meta.content_hash が PENDING のままである（stampingMeta.py 実行前）
[ ] derived_from に企画書 ID が設定されている（判明分。不明は PENDING）
[ ] acceptance_criteria が各機能要件に 1 件以上設定されている
[ ] metrics が各非機能要件に 1 件以上設定されている（target_value は定量値）
[ ] 曖昧語（適切に・十分に等）を含まない（目視確認）
[ ] 生成ファイル一覧が出力されている（次セッションへの引き継ぎ情報付き）
```
