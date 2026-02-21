---
meta:
  artifact_id: PLN-PLN-GOAL-001
  file: "planning_v2.2.md"
  author: "@juria.koga"
  source_type: "human"
  timestamp: 2026-02-21 10:34
  content_hash: 7af3e46493b652d77a42610d55ea3b91d56b3791782049e3fd0c2b4c0f783f9f
  supersedes: "planning_v2.1.md"
---

### 上流工程品質保証の構造化・可視化プラットフォーム

AI駆動開発における品質保証基盤の確立

### エグゼクティブサマリー

本企画は、AI駆動開発（AIDD）における上流工程の品質保証を構造化・可視化・検証可能にするWebアプリケーションプラットフォームの構築である。

単なるチェックリストツールではなく、AIDDの品質保証手法そのものを実証するサンプルプロジェクトとして位置づけ、このアプリ自体をAIDDで開発することで、提示する品質保証手法の実効性を証明する。

核心的価値提案：

> 「仕様書と実装の乖離」という現場最大の課題に対し、
> 構造化された品質ゲートとトレーサビリティにより、
> 検証可能な品質保証プロセスを提供する。

### 企画背景と課題定義

#### 1.1 AI駆動開発の現状

AI駆動開発の導入により、コード生成・設計支援の適用範囲が拡大している。
しかし、現場では品質課題が顕在化している（本企画では遅延率・手戻り発生率・テスト工数倍率をKPIとして定量管理し、Phase 1のパイロットで実測値に置換する）。

■ 現場で観測されている課題

| カテゴリ         | 具体的課題                           | 影響                                                                                       |
| ---------------- | ------------------------------------ | ------------------------------------------------------------------------------------------ |
| 仕様の曖昧性     | 「適切に」「柔軟に」等の曖昧語が頻出 | AIが誤解釈し、意図しない実装を生成                                                         |
| 仕様と実装の乖離 | 要件定義・設計書・実UIが一致しない   | テスト工数が計画比で平均2.5倍に増加（仮説）、手戻り発生率が50%以上となる案件が発生（仮説） |
| QA観点の属人化   | 何を確認すべきか個人の経験に依存     | 品質のバラつき、新人の戦力化遅延                                                           |
| 判断根拠の不在   | なぜその設計にしたか記録されない     | 保守時の意図不明、同じ議論の繰り返し                                                       |
| 品質の不可視性   | QA実施有無は分かるが中身が見えない   | 品質リスクの早期検知不能                                                                   |

■ 根本原因分析

これらの課題の根本原因は以下3点に集約される：

構造化されていない知識：QA観点がドキュメントに散在
検証不可能な記述：テスト設計ができない要件定義
トレーサビリティの欠如：要件と実装の紐付けがない

結果として、

> 「動けば満足」の文化が蔓延し、
> 本質的な品質保証が機能していない

状態が発生している。

#### 1.2 本企画が解決する問題

本プラットフォームは、以下の問題を解決する：

**Primary Goal（主要目標）**
仕様書の妥当性を検証可能にし、仕様と実装の乖離を防止する

**Secondary Goals（副次目標）**
上流工程のQA観点を標準化・構造化する
判断根拠とプロセスを記録・可視化する
AIDDにおける品質保証手法を確立・実証する
検索工数の削減とPoC段階での観点提案を可能にする

### プロジェクトの位置づけと戦略的意義

#### 2.1 本プロジェクトの性質

本プロジェクトはサンプルプロジェクトとして設計されている。

| 側面     | 説明                                                 |
| -------- | ---------------------------------------------------- |
| 一次目的 | QA4AIDDの実践手法を確立し、実証する                  |
| 二次目的 | 現場への段階的導入の足掛かりとする                   |
| 実証方法 | このアプリ自体をAIDDで開発し、品質保証プロセスを適用 |
| 成果物   | 動作するアプリ + CI/CD環境 + 品質保証テンプレート集  |

■ サンプルプロジェクトとしての戦略的価値
実証可能性：提案する手法が実際に機能することを示す
再現可能性：CI/CD環境ごと提示し、他プロジェクトへの適用を容易にする
段階的浸透：まず仕様書妥当性評価から現場導入を開始
ナレッジベース：プロンプト・チェックリスト・テンプレートを蓄積

#### 2.2 QA4AIDD定義と本プロジェクトでの解釈

■ QA4AIDD（社内定義）

| 項目 | 内容                             |
| ---- | -------------------------------- |
| ①    | AIに正しく指示を与える           |
| ②    | 指示が守られていることを確認する |

■ 本プロジェクトにおける実装

| QA4AIDD要素    | 本プロジェクトでの実現方法                          |
| -------------- | --------------------------------------------------- |
| 正しく指示     | 構造化プロンプトテンプレート、曖昧語排除チェック    |
| 指示の遵守確認 | JSON Schema検証、Deep Eval評価、構造一貫性テスト    |
| 品質の可視化   | Allure Reportによる品質ゲート採点結果のモニタリング |
| 継続的改善     | Promptfooによるプロンプト評価、評価スコア推移グラフ |

### 用語定義と前提条件

#### 3.1 重要用語の定義

| 用語             | 定義                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| AIDD             | AI駆動開発（AI-Driven Development）。LLMを活用した要件定義・設計・実装・テストの自動化開発手法 |
| QA4AIDD          | AI駆動開発における品質保証。①AIに正しく指示を与える ②指示が守られていることを確認する          |
| 上流工程         | （企画）、要件定義、基本設計、詳細設計の各工程                                                 |
| 品質保証（QA）   | プロセスに焦点を当て、欠陥の予防と品質目標の達成を目指す活動                                   |
| 品質管理（QC）   | 成果物に焦点を当て、欠陥の検出と是正を行う活動                                                 |
| 構造化           | 情報を階層的・体系的に整理し、ID体系により追跡可能にすること                                   |
| 検証可能性       | 要件や設計がテスト可能な形で記述され、合否判定できること                                       |
| 曖昧語           | 「適切に」「十分に」「柔軟に」「簡単に」「最適に」等、解釈が分かれる表現                       |
| 品質ゲート       | 次工程への移行可否を判定する品質基準チェックポイント                                           |
| トレーサビリティ | 要件から実装・テストまでの追跡可能性。変更影響分析を可能にする                                 |

#### 3.2 プロジェクト制約事項

■ 技術的制約

| 制約項目     | 内容                           |
| ------------ | ------------------------------ |
| AI基盤       | OpenAI API のみ使用可能        |
| OS環境       | Windows のみ                   |
| 開発体制     | 1人での開発・検証              |
| 対応ブラウザ | Edge、Chrome（モバイル非対応） |

■ プロジェクト制約

| 制約項目 | 内容                                       |
| -------- | ------------------------------------------ |
| 予算     | 月額予算10万円以内（個人プロジェクト規模） |
| 期間     | 明確な期限設定なし（品質優先）             |
| スコープ | サンプルプロジェクトとしての完成度を優先   |

■ ユーザー要件制約

| 制約項目   | 内容                                                   |
| ---------- | ------------------------------------------------------ |
| 必須スキル | JSON・YAMLの構造を読み書きできること                   |
| 理由       | テンプレート内容の理解と、人による最終判断の実施に必要 |

#### 3.3 スコープ定義

**本プロジェクトのスコープ内**
• 上流工程（要件定義・基本設計・詳細設計）の品質保証ワークフロー
• 構造化テンプレート・チェックリスト・プロンプト集の提供
• 品質ゲート評価の自動化（Deep Eval、JSON Schema検証）
• トレーサビリティID体系の実装
• CI/CD環境構築とAllure Reportによるモニタリング
• Promptfooによるプロンプト品質評価
• Abort理由記録と判断ログの保存
• JSON/YAMLエクスポート機能
• データベースによる承認者管理

**本プロジェクトのスコープ外（将来拡張候補）**

| 項目                   | 理由                           | 将来優先度 |
| ---------------------- | ------------------------------ | ---------- |
| アプリ内AI自動生成機能 | 人の判断重視の思想             | 低         |
| 外部ツールAPI連携      | サンプルプロジェクトの範囲超過 | 中         |
| ユーザー満足度測定     | 社内展開前段階                 | 低         |
| モバイル対応           | 利用シーン想定外               | 低         |
| プロンプト共有機能     | 最優先の将来機能として明記     | 最高       |

### 基本思想とコンセプト

#### 4.1 設計哲学

「考えなくていいQA」ではなく「考える順番を固定するQA」

本アプリはAIに判断を委譲しない。

| 役割   | 担当     | 理由                   |
| ------ | -------- | ---------------------- |
| 判断   | 人間     | 責任の所在を明確にする |
| 記憶   | システム | 観点の漏れを防ぐ       |
| 構造化 | システム | 思考順序を標準化する   |
| 検証   | 自動化   | 機械的チェックは自動化 |

■ 核心的な設計原則
検証可能性の強制：曖昧語を含む記述を品質ゲートで阻止
構造の一貫性：Codexによる自動生成でも同じ構造を保証
判断根拠の記録義務：すべての決定に理由を付与
形骸化の防止：品質ゲートを満たさないものはデプロイしない

#### 4.2 コンセプト

「押せば展開されるQAワークフロー」

NotebookLMのマインドマップUIを参考に、3クリック以内で目的の情報にアクセス可能な操作で品質保証活動を実施できる。

``工程選択
  ↓
タスク展開
  ↓
観点・テンプレート表示
  ↓
実施・判断記録
  ↓
品質ゲート評価
  ↓
トレーサビリティ確保`

### システム設計

#### 5.1 階層構造とID体系

■ 3層構造

| レイヤー | 名称   | 内容                                   | ID形式例                   |
| -------- | ------ | -------------------------------------- | -------------------------- |
| L1       | 工程   | 要件定義、基本設計、詳細設計           | REQ, BAS, DET              |
| L2       | タスク | 非機能確認、前提整理、仕様妥当性評価等 | REQ-T001, BAS-T002         |
| L3       | 詳細   | チェック観点、テンプレート、プロンプト | REQ-T001-C01, REQ-T001-P01 |

■ トレーサビリティID体系

すべての成果物に一意のIDを付与し、紐付け（derivedfrom / tracesto / promptsused など）を記録する。

### 共通ルール（採用）

**基本形：`<PREFIX>-<PHASE>-<PURPOSE>-<NNN>`**

- `PREFIX`：成果物種別（REQ/BAS/DET/TST/PRM/CHK/RES/PLN/ARC/UI/API/DB/WF/TPL/ABT/DEC/BUG…）
- `PHASE`：工程・対象領域（PLN/REQ/BAS/DET/ARC/UI/API/DB/WF/TPL/OPS…）
- `PURPOSE`：用途（FNC/DES/CMP/AMB/YAML/REVIEW/EVAL… ※固定語彙化推奨）
- `NNN`：3桁連番（001〜）

> 例：要件の曖昧語チェック用プロンプト → `PRM-REQ-AMB-001`

| 成果物種別           | ID形式（推奨）            | 例                                        |
| -------------------- | ------------------------- | ----------------------------------------- |
| 企画（本企画書）     | PLN-PLN-<PURPOSE>-NNN     | PLN-PLN-GOAL-001（企画ゴール1）           |
| 要件                 | REQ-REQ-<PURPOSE>-NNN     | REQ-REQ-FNC-001（機能要件1）              |
| 基本設計             | BAS-BAS-<PURPOSE>-NNN     | BAS-BAS-DES-001（設計項目1）              |
| 詳細設計             | DET-DET-<PURPOSE>-NNN     | DET-DET-CMP-001（コンポーネント1）        |
| テストケース         | TST-<PHASE>-<PURPOSE>-NNN | TST-REQ-FNC-001（REQ-FNC-001のTST）       |
| プロンプト           | PRM-<PHASE>-<PURPOSE>-NNN | PRM-REQ-AMB-001（曖昧語チェック）         |
| チェックリスト       | CHK-<PHASE>-<PURPOSE>-NNN | CHK-REQ-AMB-001（曖昧語チェック）         |
| テスト結果           | RES-<PHASE>-<PURPOSE>-NNN | RES-TST-RUN-001（テスト実行結果）         |
| アーキテクチャ設計   | ARC-ARC-<PURPOSE>-NNN     | ARC-ARC-SYS-001（システム構成1）          |
| UI設計               | UI-UI-<PURPOSE>-NNN       | UI-UI-CMP-001（UIコンポーネント1）        |
| APIエンドポイント    | API-API-<PURPOSE>-NNN     | API-API-GET-001（GETエンドポイント）      |
| DBスキーマ           | DB-DB-<PURPOSE>-NNN       | DB-DB-TBL-001（テーブル1）                |
| ワークフロー定義     | WF-<PHASE>-<PURPOSE>-NNN  | WF-REQ-YAML-001（要件WF定義）             |
| テンプレート         | TPL-<PHASE>-<PURPOSE>-NNN | TPL-REQ-AMB-001（曖昧語TPL）              |
| Abortログ            | ABT-<PHASE>-<PURPOSE>-NNN | ABT-REQ-SCOPEOUT-001（Abort記録）         |
| 判断ログ             | DEC-<PHASE>-<PURPOSE>-NNN | DEC-ARC-CHOICE-001（設計判断1）           |
| バグレポート（拡張） | BUG-<PHASE>-<PURPOSE>-NNN | BUG-OPS-DEFECT-001（バグ1）               |
| --------------       | ----------------          | -----------------------------------       |
| 要件                 | REQ-                      | REQ-FNC-001（機能要件1）                  |
| 基本設計             | BAS-                      | BAS-DES-001（設計項目1）                  |
| 詳細設計             | DET-                      | DET-CMP-001（コンポーネント1）            |
| テストケース         | TST-                      | TST-REQ-FNC-001（要件F001のテスト）       |
| プロンプト           | PRM-                      | PRM-REQ-AMB-001（要件定義用プロンプト）   |
| チェックリスト       | CHK-                      | CHK-REQ-AMB-001（曖昧語チェック）         |
| テスト結果           | RES-                      | RES-TST-REQ-FNC-001-001（テスト実行結果） |
| 企画（本企画書）     | PLN-                      | PLN-GOAL-001（企画ゴール1）               |
| アーキテクチャ設計   | ARC-                      | ARC-SYS-001（システム構成1）              |
| UI設計               | UI-                       | UI-CMP-001（コンポーネント1）             |
| APIエンドポイント    | API-                      | API-GET-001（GETエンドポイント1）         |
| DBスキーマ           | DB-                       | DB-TBL-001（テーブル1）                   |
| ワークフロー定義     | WF-                       | WF-REQ-001（要件定義ワークフロー）        |
| テンプレート         | TPL-                      | TPL-REQ-AMB-001（チェックリスト雛形1）    |
| Abortログ            | ABT-                      | ABT-REQ-T005-001（Abort記録）             |
| 判断ログ             | DEC-                      | DEC-ARC-001（設計判断1）                  |
| バグレポート（拡張） | BUG-                      | BUG-001（バグ1）                          |

#### 略語の定義

| 略語 | 意味（日本語）     | 主な対象/説明                        | 例                    |
| ---- | ------------------ | ------------------------------------ | --------------------- |
| PLN  | 企画               | 企画書・企画主張・KPI・品質ゲート等  | `PLN-PLN-GOAL-001`    |
| REQ  | 要件               | 機能/非機能/制約/受入条件            | `REQ-REQ-FNC-001`     |
| BAS  | 基本設計           | 方式設計・全体設計・主要設計項目     | `BAS-BAS-DES-001`     |
| DET  | 詳細設計           | コンポーネント/詳細仕様              | `DET-DET-CMP-001`     |
| ARC  | アーキテクチャ設計 | 構成図・コンポーネント構成・配置     | `ARC-ARC-SYS-001`     |
| UI   | UI設計             | 画面・UIコンポーネント・遷移         | `UI-UI-CMP-001`       |
| API  | API設計            | エンドポイント・I/F・契約            | `API-API-GET-001`     |
| DB   | DB設計             | テーブル/カラム/ER・マイグレーション | `DB-DB-TBL-001`       |
| WF   | ワークフロー定義   | 業務/処理フロー・BPMN等              | `WF-WF-REQ-001`       |
| TST  | テストケース       | テスト仕様・ケース・手順             | `TST-REQ-FNC-001`     |
| RES  | テスト結果         | 実行結果・証跡                       | `RES-TST-REQ-FNC-001` |
| CHK  | チェックリスト     | レビュー観点・検査項目               | `CHK-REQ-AMB-001`     |
| PRM  | プロンプト         | 生成/レビュー/検査用プロンプト       | `PRM-PLN-YAML-001`    |
| TPL  | テンプレート       | YAML/チェックリスト/文書雛形         | `TPL-REQ-AMB-001`     |
| ABT  | Abortログ          | 生成中断・失敗・中止記録             | `ABT-REQ-EVAL-001`    |
| DEC  | 判断ログ           | 設計判断・採否・理由                 | `DEC-ARC-DES-001`     |
| BUG  | バグレポート       | 不具合/課題チケット                  | `BUG-OPS-FIX-001`     |

| 略語 | 意味（日本語） | 主な対象/説明                  |
| ---- | -------------- | ------------------------------ |
| PLN  | 企画           | 企画立案・目的/方針/KPI/ゲート |
| REQ  | 要件定義       | 要件抽出・整理・受入条件       |
| BAS  | 基本設計       | 方式/構成/主要設計・I/F方針    |
| DET  | 詳細設計       | 実装可能レベルの詳細仕様       |
| ARC  | アーキテクチャ | 構成設計（論理/物理）・依存    |
| UI   | UI/UX          | 画面/遷移/コンポーネント設計   |
| API  | API            | API契約・入出力・エラー設計    |
| DB   | DB             | スキーマ・制約・クエリ方針     |
| WF   | Workflow       | 手順/フロー/BPMN/状態遷移      |
| TPL  | Template       | 雛形整備（再利用資産）         |
| OPS  | 運用           | 運用手順・監視・障害対応・改善 |
| TST  | テスト         | テスト設計・実行・評価         |

| 略語   | 意味（日本語）   | 主な用途                   | 例                   |
| ------ | ---------------- | -------------------------- | -------------------- |
| GOAL   | ゴール           | 目的/到達点                | `PLN-PLN-GOAL-001`   |
| PROB   | 課題             | 課題定義                   | `PLN-PLN-PROB-001`   |
| SCOPE  | スコープ         | 範囲/対象                  | `REQ-REQ-SCOPE-001`  |
| CONS   | 制約             | 制約条件                   | `REQ-REQ-CONS-001`   |
| FNC    | 機能             | 機能要件/機能設計          | `REQ-REQ-FNC-001`    |
| NFR    | 非機能           | 性能/可用性/セキュリティ等 | `REQ-REQ-NFR-001`    |
| DES    | 設計             | 設計項目（方式/方針含む）  | `BAS-BAS-DES-001`    |
| CMP    | コンポーネント   | 部品/モジュール/画面部品   | `DET-DET-CMP-001`    |
| IFS    | インターフェース | API/I/F 契約               | `API-API-IFS-001`    |
| TBL    | テーブル         | DBテーブル                 | `DB-DB-TBL-001`      |
| FLW    | フロー           | BPMN/処理フロー            | `WF-WF-FLW-001`      |
| AMB    | 曖昧語           | 曖昧語チェック/是正        | `CHK-REQ-AMB-001`    |
| YAML   | YAML化           | YAML変換・構造化           | `PRM-PLN-YAML-001`   |
| REVIEW | レビュー         | レビュー実施/観点          | `PRM-BAS-REVIEW-001` |
| EVAL   | 評価             | 評価/スコアリング/判定     | `PRM-REQ-EVAL-001`   |
| EXPORT | 出力             | 変換/エクスポート          | `PRM-PLN-EXPORT-001` |
| FIX    | 修正             | 改修/是正                  | `BUG-OPS-FIX-001`    |

■ トレーサビリティマトリクス

`yaml
traceability:
  REQ-FNC-001:
    title: "ユーザーログイン機能"
    derivedfrom:
      - PLN-GOAL-001  # 企画ゴール: 仕様書と実装の乖離防止
    tracesto:
      - BAS-DES-001  # 基本設計：認証フロー設計
      - DET-CMP-001  # 詳細設計：LoginComponentの実装仕様
      - TST-REQ-FNC-001  # テストケース：ログイン正常系
      - TST-REQ-FNC-002  # テストケース：ログイン異常系
    promptsused:
      - PRM-REQ-AMB-001  # 使用したプロンプト
    evaluation:
      - RES-EVAL-001  # Deep Eval評価結果
`

■ 企画 → 要件 トレーサビリティ（追加定義）

- 企画書内の主要主張（Goal / Challenge / Scope / Constraint 等）に **PLN-** IDを付与する。
- 要件定義書側の各要件に `derivedfrom` フィールドを追加し、企画の根拠を明示する。
- これにより「企画意図が要件に正しく反映されたか」を自動で検証できる。

`yaml

# 企画（例）

planning:

- id: PLN-GOAL-001
  content: "仕様書と実装の乖離を防止する"

# 要件（例）

requirements:

- id: REQ-FNC-001
  title: "曖昧語検出機能"
  derivedfrom: - PLN-GOAL-001 - PLN-CHALLENGE-001
  rationale: "仕様の曖昧性が乖離の主要因であるため"
  `

#### 5.2 タスクチケット構成

各タスクチケットは以下の構造を持つ：

`yaml
task:
id: "REQ-T001"
title: "曖昧語排除チェック"
layer: "L2"
phase: "要件定義"

purpose: |
AIが誤解釈しうる曖昧な表現を特定し、
検証可能な記述に修正する

checkpoints: - id: "CHK-REQ-AMB-001-001"
description: "「適切に」「十分に」「柔軟に」等の曖昧語がないか"
validationmethod: "正規表現によるキーワード検索"

template:
id: "TPL-REQ-AMB-001"
type: "checklist"
content: | ## 曖昧語チェックリスト - [ ] 「適切に」→具体的な基準に置換 - [ ] 「柔軟に」→変更可能な範囲を明記 - [ ] 「簡単に」→操作手順数で定義
...

prompttemplate:
id: "PRM-REQ-AMB-001"
usedintasks:

- REQ-T001
  content: |
  以下の要件定義文から曖昧な表現を抽出し、
  具体的な表現に修正してください。

        【対象文書】
        {{requirementstext}}

        【曖昧語リスト】
        - 適切に、十分に、柔軟に、簡単に、最適に...

referencematerials: - title: "曖昧語辞典"
url: "/docs/ambiguous-words" - title: "検証可能な要件の書き方"
url: "/docs/testable-requirements"

acceptancecriteria: - "曖昧語が0件であること" - "各要件に成功条件（受入基準）が明記されていること" - "成功条件がテスト可能であること（検証方法が想像できる）"

status: "ToDo" # ToDo | InProgress | Done | Abort

decisionlog:
decidedby: "Sam"
decidedat: "2024-01-15T10:30:00Z"
reason: |
要件R-001, R-003に「適切に処理する」という記述があり、
これを「3秒以内に応答を返す」に修正した。
evidence: - file: "requirementsv1.2.yaml" - evaluation: "RES-EVAL-001"
`

#### 5.3 ステータス設計

■ タスクステータス定義

| ステータス | 意味             | 遷移条件         |
| ---------- | ---------------- | ---------------- |
| ToDo       | 未着手           | 初期状態         |
| InProgress | 作業中           | 担当者が着手     |
| Done       | 完了             | 品質ゲート通過   |
| Abort      | 中止（理由必須） | スコープ外判断等 |

■ Abort設計思想

Abortは例外ではなく、正式な品質判断である。

Abortに許容率を設けない理由：
• 要件定義まで完了済の委託案件の存在
• プロジェクト特性による必須タスクの変動
• 過剰な制約による形骸化リスク

代わりに、Abort理由の明示を必須とする。

■ Abort理由のガイドライン

Abort時には以下の情報を記録する：

`yaml
abortlog:
  taskid: "REQ-T005"
  abortedby: "Jim"
  abortedat: "2024-01-16T14:20:00Z"
  reasoncategory: "scopeout"  # scopeout | prerequisitemissing | delegated | notapplicable
  reasondetail: |
    本プロジェクトではログイン機能は既存システムを流用するため、
    認証仕様の詳細設計は対象外と判断。
    既存システム仕様書（doc-auth-v2.3）を参照することで代替。
  alternativeaction: "既存仕様書doc-auth-v2.3へのトレーサビリティを記録"
  approvedby: "プロジェクトリーダー Tom"
`

■ Abort理由カテゴリ

| カテゴリ            | 説明                   | 例                         |
| ------------------- | ---------------------- | -------------------------- |
| scopeout            | プロジェクトスコープ外 | 既存システム流用部分       |
| prerequisitemissing | 前提条件未確定         | 顧客仕様待ち               |
| delegated           | 委託元で実施済         | 要件定義済案件             |
| notapplicable       | 今回適用不要           | 非機能要件なしの簡易ツール |

### 品質保証の核心設計

#### 6.1 品質基準とメトリクス

■ 品質ゲート定義

品質ゲートは構造の逸脱を最大リスクとして設計する。

| ゲート               | 評価内容               | 合格基準                     | 自動検証              |
| -------------------- | ---------------------- | ---------------------------- | --------------------- |
| G1: 曖昧語チェック   | 曖昧な表現の有無       | 曖昧語0件                    | 正規表現              |
| G2: 検証可能性       | 受入基準の存在と具体性 | 全要件に検証可能な基準       | チェックリスト        |
| G3: 構造一貫性       | JSON Schema準拠        | スキーマ検証100%パス         | JSON Schema Validator |
| G4: AI評価スコア     | Deep Evalによる評価    | スコア0.8以上                | Deep Eval             |
| G5: トレーサビリティ | ID紐付けの完全性       | 全要件が設計・テストに紐付く | カスタムスクリプト    |

■ Deep Eval評価基準

`python
Deep Eval評価項目（顧客合意形成の下決定想定）
evaluationcriteria:
threshold: 0.8 # 合格ライン

metrics: - name: "Contextual Relevancy" # 文脈的関連性
weight: 0.25

    - name: "Faithfulness"  # 忠実性（ハルシネーション検出）
      weight: 0.25

    - name: "Contextual Precision"  # 文脈的精度
      weight: 0.25

    - name: "Answer Relevancy"  # 回答関連性
      weight: 0.25

`

■ 必須チェックリスト（AI駆動開発特化）

すべてのプロジェクトで必須となるチェック項目：

`yaml
mandatorychecks:

- id: "CHK-AIDD-001"
  category: "曖昧語排除"
  items:
  - "「適切に」「十分に」「柔軟に」「簡単に」「最適に」等の曖昧語がない"
  - "数値基準またはテスト可能な記述に置換されている"

- id: "CHK-AIDD-002"
  category: "検証可能性"
  items:
  - "各要件に成功条件（受入基準）が明記されている"
  - "成功条件がテスト可能である（テストケースが想像できる）"
  - "成功条件に具体的な期待値が含まれている"

- id: "CHK-AIDD-003"
  category: "構造整合性"
  items: - "YAML/JSON形式の構文エラーがない" - "必須フィールドがすべて存在する" - "ID命名規則に準拠している"
  `

■ レビュー完了条件

| 承認者         | 承認内容         | 承認基準               |
| -------------- | ---------------- | ---------------------- |
| 企画者（顧客） | 要件の妥当性     | ビジネス要求との整合性 |
| QAエンジニア   | 品質ゲート通過   | すべてのゲートが合格   |
| アーキテクト   | 構造設計の妥当性 | 技術的実現可能性       |

#### 6.2 評価スコア推移モニタリング

■ 目的

AIモデルの変動やプロンプト改善による品質変化を観測する。

■ 監視項目

`yaml
monitoring:
metrics: - name: "Deep Eval Score"
type: "timeseries"
visualization: "linechart"
alertthreshold: 0.75 # 0.8を下回った場合に警告

    - name: "Ambiguous Word Count"
      type: "timeseries"
      visualization: "barchart"
      target: 0

    - name: "Schema Validation Pass Rate"
      type: "percentage"
      target: 100

    - name: "Traceability Coverage"
      type: "percentage"
      target: 100
      description: "要件→設計→テストの紐付け完全性"

`

■ 変動パターンの分析

| 変動パターン | 想定原因                          | 対応アクション                     |
| ------------ | --------------------------------- | ---------------------------------- |
| 徐々に低下   | プロンプトの劣化、要件複雑化      | プロンプト改善、チェックリスト追加 |
| 急激な低下   | AIモデル変更、APIバージョンアップ | モデル固定、プロンプト再調整       |
| 振動         | 評価基準の曖昧性                  | 評価基準の明確化                   |
| 安定高値     | 品質保証プロセスの成熟            | ベストプラクティス化               |

■ Allure Reportによる可視化

`Allure Report Dashboard
├── Quality Gate Results
│   ├── G1: Ambiguous Word Check [PASSED]
│   ├── G2: Testability Check [PASSED]
│   ├── G3: Schema Validation [PASSED]
│   ├── G4: Deep Eval Score [0.85] ✓
│   └── G5: Traceability [100%] ✓
│
├── Score Trends (Last 30 Days)
│   └── [Line Chart: Deep Eval Score推移]
│
├── Abort Analysis
│   ├── Total Aborts: 3
│   ├── By Category:
│   │   ├── scopeout: 2
│   │   └── prerequisitemissing: 1
│   └── [Pie Chart: Abort理由分布]
│
└── Traceability Matrix
    └── [Heatmap: 要件→設計→テストの紐付け状況]`

#### 6.3 データ品質管理

■ Abort理由記述ガイドライン

必須記載事項：

カテゴリ選択（4種から選択）
詳細理由（最低50文字以上の説明）
代替措置（何で代替するか）
承認者（判断を承認した責任者）

記述品質基準：

`yaml
abortqualitycheck:

- "「スコープ外のため」だけでは不可"
- "具体的な判断根拠を記述"
- "将来的な再検討条件があれば明記"
- "関連ドキュメントへのリンク推奨"
  `

良い例：
`yaml
reasondetail: |
本プロジェクトではユーザー認証機能は既存の
社内SSOシステム（auth.example.com）を利用する。
認証フローの詳細設計は既存システムの仕様書
（SSO-SPEC-v3.2.pdf）に準拠するため、
本プロジェクトでの新規設計は不要と判断。

ただし、SSO連携部分のインターフェース設計は
BAS-T008「外部連携設計」にて実施する。

alternativeaction: |

- 既存仕様書SSO-SPEC-v3.2へのトレーサビリティ記録
- BAS-T008にて連携I/F設計を実施
  `

悪い例：
`yaml
reasondetail: "スコープ外のため"  # NG: 情報不足
`

■ 判断ログ記述ガイドライン

必須記載事項：

`yaml
decisionlogtemplate:
decidedby: "[氏名]" # 必須
decidedat: "[ISO8601形式の日時]" # 必須

decisionsummary: | # 50文字以上の要約
何を、どう判断したか

rationale: | # 判断根拠（必須）- なぜその判断をしたか - 検討した代替案 - 選択理由

evidence: | # 判断の根拠資料（推奨）- 参照したドキュメント - 評価結果ID - 議事録等

risksandmitigation: | # 判断に伴うリスクと軽減策（該当時）- 想定されるリスク - リスク軽減のための措置
`

記述粒度の基準：

| 判断の重要度 | 記述粒度                                      | 例                                   |
| ------------ | --------------------------------------------- | ------------------------------------ |
| High         | 判断理由200文字以上 + 代替案2つ以上の検討記録 | アーキテクチャ選定、データモデル設計 |
| Medium       | 判断理由と参考資料                            | UI配置、バリデーションルール         |
| Low          | 簡潔な理由                                    | 表記ゆれ修正、軽微な表現調整         |

■ データ整合性自動チェック

`python
CI/CDで実行されるデータ品質チェック
dataqualitychecks:

- name: "Abort Log Completeness"
  check: "すべてのAbortステータスに理由が記載されているか"
- name: "Decision Log Minimum Length"
  check: "判断ログが最低50文字以上か"
- name: "ID Uniqueness"
  check: "すべてのIDが一意か"
- name: "Traceability Integrity"
  check: "参照されているIDがすべて存在するか"
- name: "Date Format Validation"
  check: "日時がISO8601形式か"
  `

#### 6.4 リスク管理と軽減策

■ 想定リスクと対策

| リスク         | 影響度 | 発生確率 | 軽減策                               | 検知方法         |
| -------------- | ------ | -------- | ------------------------------------ | ---------------- |
| 形骸化         | High   | Medium   | 品質ゲートでデプロイブロック         | CI/CD監視        |
| 適当なDone     | High   | High     | チェックリスト必須、承認フロー       | レビュー記録確認 |
| AIモデル変動   | Medium | Medium   | モデルバージョン固定、評価スコア監視 | Allure Report    |
| プロンプト劣化 | Medium | Low      | Promptfoo継続評価                    | スコア推移グラフ |
| 保守放棄       | Medium | Low      | サンプルプロジェクトとして割り切り   | -                |

■ 品質劣化検知システム

`yaml
qualitydegradationdetection:

# 自動アラート条件

alerts: - condition: "Deep Eval Score < 0.75 for 3 consecutive runs"
action: "Email to QA Lead + CI/CD block"

    - condition: "Ambiguous Word Count > 0"
      action: "Build Warning"

    - condition: "Schema Validation Fail"
      action: "Build Failure"

    - condition: "Traceability Coverage < 95%"
      action: "Review Required"

# 定期監査

periodicaudit:
frequency: "Weekly"
checks: - "Abort理由の妥当性レビュー" - "チェックリストの陳腐化確認" - "プロンプトテンプレートの有効性確認"
`

6.5 プロンプト品質管理
■ Promptfooによる評価

`yaml
promptfooConfig.yaml
prompts:

- id: "PRM-REQ-AMB-001"
  file: "prompts/requirementambiguitycheck.txt"

tests:

- description: "曖昧語を正しく検出できるか"
  vars:
  requirementstext: "システムは適切にエラー処理を行う"
  assert:
  - type: contains
    value: "適切に"
- description: "具体的な修正案を提示できるか"
  vars:
  requirementstext: "ユーザーは簡単にログインできる"
  assert:
  - type: contains-any
    value:
    - "3ステップ以内"
    - "5秒以内"
    - "クリック数"

scoring:
threshold: 0.8
metrics: - accuracy - consistency - completeness
`

■ プロンプト改善サイクル

`Promptfoo評価実行
   ↓
スコア0.8未満の検出
   ↓
プロンプト修正
   ↓
Deep Evalで実運用評価
   ↓
スコア推移をAllure Reportで確認
   ↓
改善効果を記録`

アーキテクチャとUI設計

#### 7.1 UI設計における品質観点

本プロジェクトではUI統一性の検証も品質保証の対象とする。

■ UI統一性の検証目的
設計仕様に対する再現性の確認

- JSON Schema定義に準拠した構造の要素が、同一のReactコンポーネントで実装されているか

プロンプトの品質検証

- Codexによる自動生成でも一貫したUIが生成されるか

保守性の担保

- 一貫したUI設計パターンによる認知負荷軽減

■ UI統一対象

| UI要素         | 統一観点                               | 検証方法                  |
| -------------- | -------------------------------------- | ------------------------- |
| 工程スイッチ   | サイズ、配色、アイコン配置             | Visual Regression Testing |
| タスクチケット | レイアウト、ステータス表示             | Storybook + Chromatic     |
| 親子関係表現   | インデント、接続線、展開アニメーション | E2Eテスト                 |
| オーバーレイ   | 表示タイミング、閉じ方、背景処理       | インタラクションテスト    |

■ UI設計パターン

`yaml
uidesignpatterns:

# L1: 工程スイッチ

phaseswitch:
component: "PhaseCard"
props: - phaseid: string - title: string - status: "active" | "completed" | "pending" - taskcount: number - completionrate: number
visual:
width: "300px"
height: "120px"
borderradius: "8px"
elevation: "2"

# L2: タスクチケット

taskticket:
component: "TaskCard"
props: - taskid: string - title: string - status: "ToDo" | "InProgress" | "Done" | "Abort" - priority: "high" | "medium" | "low"
visual:
width: "280px"
height: "auto"
borderleft: "4px solid {statuscolor}"
padding: "16px"

# L3: 詳細オーバーレイ

detailoverlay:
component: "DetailPanel"
props: - contenttype: "checklist" | "template" | "prompt" | "reference" - data: object
visual:
position: "fixed"
width: "60vw"
maxwidth: "800px"
animation: "slide-in-right 0.3s"
`

7.2 インタラクション設計
■ よくある誤りへの警告機能

| 誤りパターン         | 検知タイミング                 | 警告内容                         | 対処ガイド                    |
| -------------------- | ------------------------------ | -------------------------------- | ----------------------------- |
| 曖昧語入力           | テキスト入力時（リアルタイム） | 「「適切に」は曖昧な表現です」   | 「3秒以内に」等の具体例を提示 |
| 必須項目未入力でDone | Done遷移時                     | 「チェックリスト未完了」         | 未完了項目をハイライト        |
| Abort理由不足        | Abort実行時                    | 「理由が50文字未満です」         | 記述ガイドライン表示          |
| トレーサビリティ欠落 | 工程完了時                     | 「未紐付けの要件があります」     | 該当要件リスト表示            |
| 同一IDの重複         | ID入力時                       | 「このIDは既に使用されています」 | ID命名規則を再提示            |
| JSON/YAML構文エラー  | テンプレート編集時             | 「構文エラー: 行12」             | エラー箇所をハイライト        |

■ 段階的情報開示（Progressive Disclosure）

`
初心者モード：

- ガイドツールチップ表示
- サンプル記入例を常時表示
- 各項目にヘルプアイコン
- 推奨アクション順を番号表示

熟練者モード：

- ガイド非表示
- キーボードショートカット有効
- 一括操作機能解放
- カスタムビュー作成可能
  `

#### 7.3 システムアーキテクチャ

■ 技術スタック

| レイヤー               | 技術選定                 | 選定理由                         |
| ---------------------- | ------------------------ | -------------------------------- |
| フロントエンド         | React + TypeScript       | コンポーネント再利用性、型安全性 |
| 状態管理               | Zustand                  | 軽量、学習コスト低               |
| UI Framework           | Tailwind CSS + shadcn/ui | 統一性、カスタマイズ性           |
| データ検証             | Zod                      | ランタイム型検証、スキーマベース |
| ビジュアライゼーション | React Flow               | ワークフロー図生成               |
| バックエンド           | Node.js + Express        | JSON/YAML処理の容易さ            |
| データベース           | SQLite                   | ローカル完結、ポータビリティ     |
| CI/CD                  | GitHub Actions           | 無料、YAML設定                   |
| テスト                 | Vitest + Playwright      | 高速、モダン                     |
| レポート               | Allure Report            | 視覚的、多機能                   |
| プロンプト評価         | Promptfoo                | プロンプト専用評価               |
| AI評価                 | Deep Eval                | LLM出力品質評価                  |

■ データフロー

`
[ユーザー入力]
↓
[フロントエンド検証]

- リアルタイム曖昧語チェック
- 構文チェック
  ↓
  [バックエンドAPI]
  ↓
  [品質ゲート実行]
- Deep Eval評価
- JSON Schema検証
- トレーサビリティチェック
  ↓
  [合格] → [データベース保存] → [Allure Report更新]
  ↓
  [不合格] → [エラーフィードバック] → [ユーザーへ返却]
  `

#### 7.4 バックアップ・リカバリ方針

■ データ保護戦略

| データ種別         | バックアップ頻度 | 保存先                            | 保持期間 |
| ------------------ | ---------------- | --------------------------------- | -------- |
| プロジェクトデータ | 毎日深夜2時      | ローカルディスク + 外部ストレージ | 30日     |
| 判断ログ           | リアルタイム     | データベース + JSON Export        | 無期限   |
| テンプレート       | バージョン管理   | Git Repository                    | 無期限   |
| 評価結果           | テスト実行毎     | Allure Report履歴                 | 90日     |

■ リカバリ手順

`yaml
recoveryprocedures:

# レベル1: データベース破損

databasecorruption:
detection: "起動時整合性チェック失敗"
procedure: - "前日バックアップからリストア" - "最新JSONエクスポートとマージ" - "トレーサビリティ再検証"
estimatedtime: "15分"

# レベル2: CI/CD環境破壊

cicdfailure:
detection: "GitHub Actions実行失敗"
procedure: - "設定ファイル(.github/workflows)をリポジトリから復元" - "シークレット変数を再設定" - "テスト実行で動作確認"
estimatedtime: "30分"

# レベル3: 完全なデータ損失

totalloss:
detection: "すべてのバックアップ失敗"
procedure: - "テンプレートはGitから復元可能" - "プロジェクトデータは最終エクスポートから復元" - "判断ログの一部損失は許容"
estimatedtime: "2時間"
`

可視化と報告機能

#### 8.1 品質フロー図生成

■ 目的

実施したQAタスクの流れを視覚化し、プロジェクト固有の品質履歴を生成する。

■ 品質基準（検証可能性）

- React Flow形式のJSONデータとして出力されること
- 全タスクノード（Done/Abort含む）が表示されること
- ノード間の接続関係が正しいこと（親子関係、実施順序）
- Abort分岐が点線で表示されること

■ 表示要素

`yaml
workflowvisualization:

nodes: - type: "phase"
display: "工程名（完了率）"
color: "status依存"

    - type: "task"
      display: "タスク名（ステータス）"
      color:
        ToDo: "#gray"
        InProgress: "#blue"
        Done: "#green"
        Abort: "#orange"

edges: - type: "flow"
display: "実施順序"
style: "solid line"

    - type: "abortbranch"
      display: "Abort分岐"
      style: "dashed line"
      label: "Abort理由要約"

layout:
algorithm: "hierarchical"
direction: "left-to-right"
`

■ サンプル出力イメージ

`
[要件定義 100%] ──┬─> [非機能要件確認 Done]
├─> [曖昧語チェック Done]
├─> [トレーサビリティ設定 Done]
└─> [ログイン仕様詳細 Abort]
└─ "既存SSO利用のため"

[基本設計 60%] ───┬─> [画面遷移設計 Done]
├─> [データモデル設計 InProgress]
└─> [API設計 ToDo]
`

#### 8.2 スナップショット保存とエクスポート

■ セッション保存機能

`yaml
snapshot:
id: "SNAP-20240115-143000"
createdat: "2024-01-15T14:30:00Z"
createdby: "Sam"

project:
name: "顧客管理システムリニューアル"
phase: "要件定義"

statussummary:
totaltasks: 15
done: 12
inprogress: 2
abort: 1

qualitymetrics:
deepevalscore: 0.85
ambiguouswordcount: 0
traceabilitycoverage: 100

exportformats: - json: "snapshot20240115.json" - yaml: "snapshot20240115.yaml" - pdf: "qualityreport20240115.pdf"
`

■ 日報利用フォーマット

`markdown
品質保証活動報告 (2024-01-15)
実施タスク
• ✅ REQ-T001: 曖昧語チェック → Done
• ✅ REQ-T002: 非機能要件確認 → Done
• ⏸️ REQ-T005: ログイン詳細仕様 → Abort（既存SSO利用）

品質メトリクス
• Deep Eval Score: 0.85 (目標: 0.8以上) ✓
• 曖昧語検出: 0件
• トレーサビリティ: 100%

判断事項
• ログイン機能は既存SSOシステムを利用する方針決定

- 理由: コスト削減、統一認証の維持
- 承認者: プロジェクトリーダー Tom

次回アクション
• BAS-T001: 画面遷移設計の着手
• REQ-T002で指摘された性能要件の具体化
`

コンテンツ管理と更新運用

#### 9.1 承認者管理

■ データベーススキーマ

`sql
CREATE TABLE approvers (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
role TEXT NOT NULL, -- 'admin' | 'qalead' | 'architect'
email TEXT,
active BOOLEAN DEFAULT 1,
createdat TIMESTAMP DEFAULT CURRENTTIMESTAMP
);

-- サンプルデータ
INSERT INTO approvers (name, role) VALUES
('Sam', 'admin'),
('Jim', 'qalead'),
('Tom', 'architect');
`

■ 承認フロー

`yaml
approvalflow:

# テンプレート更新

templateupdate:
proposer: "任意のユーザー"
reviewers: - role: "qalead"
action: "技術的妥当性確認" - role: "admin"
action: "最終承認"
approvalthreshold: "全員承認"

# チェックリスト追加

checklistaddition:
proposer: "任意のユーザー"
reviewers: - role: "qalead"
action: "承認"
approvalthreshold: "QAリード承認"

# 品質ゲート基準変更

qualitygatechange:
proposer: "admin のみ"
reviewers: - role: "architect"
action: "技術影響評価" - role: "admin"
action: "承認"
approvalthreshold: "全員承認"
additionalrequirement: "変更理由書必須"
`

#### 9.2 コンテンツバージョン管理

■ バージョニング戦略

`yaml
contentversioning:

# テンプレート

templates:
storage: "Git Repository"
format: "YAML"
versionscheme: "Semantic Versioning (v1.2.3)"
example:
path: "templates/requirement/ambiguitycheckv1.2.0.yaml"

# チェックリスト

checklists:
storage: "Database + Git Backup"
format: "YAML"
versionscheme: "Date-based (YYYYMMDD)"
example:
id: "CHK-AIDD-001-20240115"

# プロンプト

prompts:
storage: "Git Repository"
format: "Text/Markdown"
versionscheme: "Semantic Versioning"
evaluationhistory: "Promptfoo結果を紐付け"
`

■ 陳腐化検知

`yaml
obsolescencedetection:

triggers: - name: "長期間未使用"
condition: "90日間参照ゼロ"
action: "レビュー依頼通知"

    - name: "評価スコア低下"
      condition: "Promptfooスコア < 0.6"
      action: "改善提案フラグ"

    - name: "エラー率上昇"
      condition: "使用時エラー > 10%"
      action: "緊急レビュー"

reviewcycle:
frequency: "Quarterly"
responsible: "QA Lead"
checklist: - "最新のAIDD手法との整合性" - "現場フィードバックの反映" - "競合ツール・手法の調査"
`

#### 9.3 フィードバック収集

■ フィードバック機能（将来最優先実装）

`yaml
feedbacksystem:

# プロンプト共有機能

promptsharing:
priority: "最高"
description: |
使用したプロンプトをコピペ&送信で
データベースに蓄積し、
効果的なプロンプトを組織で共有

    ui:
      location: "各タスク詳細画面"
      action: |
        [実際に使ったプロンプト]入力欄
        [Deep Eval結果]自動取得
        [送信]ボタン

    datastructure:
      - prompttext: string
      - taskid: string
      - deepevalscore: number
      - userrating: 1-5
      - tags: string[]
      - sharedby: string
      - sharedat: timestamp

    benefits:
      - "良いプロンプトのパターン学習"
      - "プロンプトライブラリの充実"
      - "新人の学習教材"

`

段階的導入戦略と展開計画

#### 10.1 現場導入の戦略

■ 最大のブロッカーへのアプローチ

現場での最大の課題は「仕様書と実UIの乖離」である。
この課題に対し、最も効果を実感しやすいポイントから導入する。

■ 導入ステップ

| Phase   | 対象                     | 目的         | 成功指標                 |
| ------- | ------------------------ | ------------ | ------------------------ |
| Phase 0 | サンプルプロジェクト完成 | 手法の実証   | アプリ完成 + CI/CD構築   |
| Phase 1 | 仕様書妥当性評価のみ     | 即効性の実感 | 仕様書起因のバグ30%削減  |
| Phase 2 | 要件定義工程追加         | 上流への拡大 | 手戻り工数20%削減        |
| Phase 3 | 基本設計・詳細設計追加   | 全工程カバー | トレーサビリティ100%達成 |
| Phase 4 | プロンプト共有機能追加   | ナレッジ蓄積 | プロンプトDB 100件以上   |

■ Phase 1: 仕様書妥当性評価の詳細

なぜ仕様書から始めるか：
• 現場が最も苦労しているポイント
• 効果が1週間以内に可視化される
• 既存ワークフローのフローチャート上で、追加ノードが3個以内
• テストエンジニアの専門領域

実施内容：
`yaml
phase1scope:

targetdocuments: - "画面仕様書" - "API仕様書" - "データモデル仕様書"

checks: - id: "仕様書曖昧語チェック"
benefit: "実装者の誤解を防ぐ"

    - id: "受入基準の検証可能性"
      benefit: "テスト設計の前倒し"

    - id: "UI統一性チェック"
      benefit: "デザインシステムとの整合"

pilotprojects: - "小規模な新機能開発 (1-2週間規模)" - "専任QAエンジニア1名をアサイン" - "週次で効果測定"
`

#### 10.2 既存プロセスとの整合性

■ 現行プロセスへの組み込み

`yaml
processintegration:

# 要件定義フェーズ

requirementphase:
existing: "要件定義書作成 → レビュー → 承認"
new: "要件定義書作成 → 【品質ゲート実行】 → レビュー → 承認"
change: "レビュー前に自動品質チェック挿入"

# 設計フェーズ

designphase:
existing: "設計書作成 → レビュー → 承認"
new: "設計書作成 → 【構造一貫性チェック】 → レビュー → 承認"
change: "構造の逸脱を事前検知"

# テストフェーズ

testphase:
existing: "テスト設計 → 実施 → バグ報告"
new: "【トレーサビリティ確認】 → テスト設計 → 実施 → バグ報告"
change: "テスト漏れの事前検知"
`

■ 「既存ワークフロー変更ノード数」の定義（検証方法）

- 10.1で用いる「追加ノードが3個以内」は、**既存ワークフローのBPMN図**（または同等のフローチャート）を基準に、
  追加される **判断ノード** と **タスクノード** の合計数をカウントする。
- 検証は、改修前後のBPMN図差分でノード増分を数え、3以下であることを確認する。

`

■ 既存ツールとの連携（Phase 4以降想定）

`yaml
toolintegrationroadmap:

# 短期（Phase 2）

immediate: - tool: "Markdown/Word"
integration: "エクスポート機能"
benefit: "既存ドキュメント形式での共有"

# 中期（Phase 3）

mediumterm: - tool: "Git"
integration: "自動コミット・タグ付け"
benefit: "バージョン管理との統合"

    - tool: "Slack"
      integration: "品質アラート通知"
      benefit: "リアルタイム状況共有"

# 長期（Phase 4）

longterm: - tool: "Jira"
integration: "タスク自動生成"
benefit: "プロジェクト管理統合"

    - tool: "Confluence"
      integration: "ドキュメント自動反映"
      benefit: "一元的な情報管理"

`

#### 10.3 教育・オンボーディング

■ サンプルプロジェクトによる学習

`yaml
learningresources:

# CI/CD環境の提示

cicdshowcase:
repository: "GitHub Public Repository"
contents: - "完全な.github/workflowsディレクトリ" - "品質ゲート設定ファイル" - "Deep Eval / Promptfoo設定例" - "Allure Report生成スクリプト"
benefit: "そのままコピーして使える"

# チュートリアルプロジェクト

tutorial:
scenario: "シンプルなTodoアプリの品質保証"
steps: - "要件定義書のYAML化" - "曖昧語チェックの実行" - "トレーサビリティの設定" - "品質ゲート通過の体験"
duration: "2時間"

# ドキュメント

documentation: - "クイックスタートガイド" - "品質ゲート解説" - "トラブルシューティング" - "ベストプラクティス集"
`

検証可能性の担保

#### 11.1 このアプリ自体の品質保証

本プロジェクトは自己言及的な品質保証を実施する。

> 「提案する品質保証手法を、このアプリの開発に適用する」

■ メタ品質保証の構造

`yaml
metaqualityassurance:

principle: |
このアプリが提示するワークフロー通りに、
このアプリ自体を開発する

validation: - "要件定義フローに従った要件定義書の作成" - "曖昧語チェックを自己適用" - "Deep Eval評価を自己実施" - "構造一貫性の自動検証"

evidence: - "CI/CDログの公開" - "Allure Reportの公開" - "品質ゲート通過履歴の公開"
`

#### 11.2 ワークフロー定義の妥当性検証

■ 検証方法

手法：
要件定義フローのみ人手で作成し、基本設計・詳細設計のワークフローをCodexで生成して構造一貫性を検証する。

`yaml
workflowvalidation:

step1:
action: "要件定義ワークフローを手動作成"
format: "YAML"
structure: - phase: "要件定義"
tasks: - id: "REQ-T001"
title: "曖昧語チェック"
checkpoints: [...]

step2:
action: "Codexに基本設計ワークフロー生成を指示"
prompt: |
以下の要件定義ワークフローと同じYAML構造で、
基本設計フェーズのワークフローを生成してください。

      【要件定義ワークフロー】
      {{requirementworkflow.yaml}}

      【生成条件】
      - 同じフィールド構造（id, title, checkpoints等）
      - 同じインデント・記法
      - 基本設計に適したタスク内容

step3:
action: "構造一貫性の自動検証"
checks: - "JSON Schemaでの構造検証" - "必須フィールドの存在確認" - "ID命名規則の一致" - "階層の深さの一致"

acceptancecriteria: - "生成されたワークフローがスキーマ検証を100%パス" - "手動作成と自動生成で同じUIレンダリング" - "5名のレビュアー（QAエンジニア3名、開発者2名）による5段階評価の平均が4.0以上"
`

■ JSON Schema定義例

`json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Workflow Definition",
  "type": "object",
  "required": ["phase", "tasks"],
  "properties": {
    "phase": {
      "type": "string",
      "enum": ["要件定義", "基本設計", "詳細設計"]
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title", "checkpoints"],
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^(REQ|BAS|DET)-T\\d{3}$"
          },
          "title": {"type": "string"},
          "checkpoints": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "description"]
            }
          }
        }
      }
    }
  }
}
`

#### 11.3 テンプレート・チェックリストの品質基準

■ 作成方針

`yaml
contentqualitystandard:

creationmethod: "人手作成"
reason: |
AIDDの初期フェーズでは、
人間の専門知識によるキュレーションが不可欠

qualitycriteria:

    # テンプレート
    templates:
      - "そのテンプレート使用時にDeep Evalスコア0.8以上を達成"
      - "使用したプロジェクトで手戻り発生0件（当該テンプレート起因の手戻り）"
      - "プロンプトの場合、Promptfooスコア0.8以上"
      - "Deep Evalスコア0.8以上を達成したもの"
      - "複数のユースケースで再利用可能"
      - "コメントで意図を明記"

    # チェックリスト
    checklists:
      - "各項目が検証可能（Yes/No判定できる）"
      - "MECE（漏れなく重複なく）"
      - "実施者のスキルレベルを明記"
      - "参考資料へのリンク"

    # プロンプト
    prompts:
      - "Promptfooスコア0.8以上"
      - "期待する出力形式を明記"
      - "制約条件を明確に記述"
      - "バージョン履歴を記録"

improvementcycle:
frequency: "毎プロジェクト終了時"
process: - "実施結果のレビュー" - "効果測定（スコア、工数等）" - "改善案の提案" - "次バージョンへの反映"
`

■ 現時点での限界と対応

認識している弱点：
• 初期テンプレートは過去5プロジェクトの経験に基づく
• 網羅性の保証が困難
• 業界・ドメイン依存の可能性

軽減策：
`yaml
mitigation:

- action: "サンプルプロジェクトでの実証"
  benefit: "少なくとも1プロジェクトでの有効性は証明"
- action: "フィードバック機能の早期実装"
  benefit: "現場からの改善提案を収集"
- action: "オープンソース化の検討"
  benefit: "コミュニティによる改善"
- action: "定期的な外部監査"
  benefit: "第三者視点でのレビュー"
  `

#### 11.4 継続的品質監視（CI/CD）

■ CI/CDパイプライン設計

`yaml
.github/workflows/quality-assurance.yml

name: Quality Assurance Pipeline

on:
push:
branches: [main, develop]
pullrequest:
branches: [main]

jobs:

# Job 1: 構文検証

syntax-validation:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3

      - name: Validate YAML files
        run: yamllint */.yaml

      - name: Validate JSON Schema
        run: |
          npm install -g ajv-cli
          ajv validate -s schema/workflow.json -d workflows/*/.yaml

# Job 2: 曖昧語チェック

ambiguity-check:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3

      - name: Run Ambiguous Word Detector
        run: python scripts/checkambiguouswords.py

      - name: Fail if ambiguous words found
        run: |
          if [ -f ambiguouswords.log ]; then
            cat ambiguouswords.log
            exit 1
          fi

# Job 3: Deep Eval評価

deep-eval:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Deep Eval
        run: pip install deepeval

      - name: Run Deep Eval
        run: |
          deepeval test run tests/deepeval/
        env:
          OPENAIAPIKEY: ${{ secrets.OPENAIAPIKEY }}

      - name: Check Score Threshold
        run: |
          SCORE=$(cat deepevalresults.json | jq '.overallscore')
          if (( $(echo "$SCORE < 0.8" | bc -l) )); then
            echo "Deep Eval score $SCORE is below threshold 0.8"
            exit 1
          fi

# Job 4: Promptfoo評価

promptfoo:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3

      - name: Run Promptfoo
        run: npx promptfoo eval
        env:
          OPENAIAPIKEY: ${{ secrets.OPENAIAPIKEY }}

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: promptfoo-results
          path: promptfoo-output/

# Job 5: トレーサビリティチェック

traceability:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3

      - name: Check Traceability Matrix
        run: python scripts/checktraceability.py

      - name: Generate Coverage Report
        run: |
          echo "Requirements: $(cat traceability.json | jq '.coverage.requirements')"
          echo "Design: $(cat traceability.json | jq '.coverage.design')"
          echo "Tests: $(cat traceability.json | jq '.coverage.tests')"

# Job 6: Allure Report生成

allure-report:
runs-on: ubuntu-latest
needs: [syntax-validation, ambiguity-check, deep-eval, promptfoo, traceability]
steps: - uses: actions/checkout@v3

      - name: Download Artifacts
        uses: actions/download-artifact@v3

      - name: Generate Allure Report
        run: |
          npm install -g allure-commandline
          allure generate allure-results -o allure-report

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          githubtoken: ${{ secrets.GITHUBTOKEN }}
          publishdir: ./allure-report

# Job 7: スコア推移記録

score-tracking:
runs-on: ubuntu-latest
needs: [deep-eval]
steps: - uses: actions/checkout@v3

      - name: Record Score History
        run: |
          DATE=$(date +%Y-%m-%d)
          SCORE=$(cat deepevalresults.json | jq '.overallscore')
          echo "$DATE,$SCORE" >> scorehistory.csv

      - name: Commit History
        run: |
          git config user.name "QA Bot"
          git add scorehistory.csv
          git commit -m "Update score history [skip ci]"
          git push

`

■ デプロイブロック条件

`yaml
deploymentgate:

conditions:
allmustpass: - "構文検証: PASS" - "曖昧語チェック: 0件" - "JSON Schema検証: 100%" - "Deep Eval Score: >= 0.8" - "トレーサビリティ: >= 95%"

onfailure:
actions: - "デプロイをブロック" - "Slack/Emailで通知" - "詳細レポートへのリンク提示" - "修正ガイドの表示"

override:
allowed: false
reason: "形骸化防止のため、上書きデプロイを禁止"
`

成果測定と効果検証
12.1 定量的指標

■ 測定項目

| 指標             | 測定方法                      | 目標値   | 現実的期待値 |
| ---------------- | ----------------------------- | -------- | ------------ |
| QA工数           | タスク実施時間の記録          | －       | むしろ増加   |
| 検索工数         | アプリ内検索 vs Web検索の比較 | 50%削減  | 30%削減      |
| 仕様書起因バグ   | バグ原因分析                  | 30%削減  | 20%削減      |
| 手戻り回数       | 設計変更回数の記録            | 20%削減  | 15%削減      |
| 仕様-実装乖離    | レビュー指摘数                | 40%削減  | 25%削減      |
| 品質ゲート通過率 | CI/CD成功率                   | 90%以上  | 85%以上      |
| Deep Eval安定性  | スコア標準偏差                | σ < 0.05 | σ < 0.1      |

■ QA工数増加の前提と意義

`yaml
qaeffortexpectation:

currentsituation: |
「動けば満足」の文化により、
QA工数は実質ゼロに近い状態

afterintroduction: |
適切な品質保証活動により、
QA工数は確実に増加する

truevalue: |
「工数削減」ではなく、
「適切なQA活動の定着」が真の目標

secondarybenefits: - "検索時間の削減" - "PoC段階での観点提案" - "属人化の解消" - "新人の早期戦力化"
`

12.2 定性的指標（将来測定）

| 指標             | 測定方法                 | タイミング    |
| ---------------- | ------------------------ | ------------- |
| 精神的負担の軽減 | アンケート               | Phase 1完了後 |
| チーム内知識共有 | インタビュー             | Phase 2完了後 |
| 新人教育効果     | オンボーディング期間比較 | Phase 3完了後 |

※サンプルプロジェクト段階ではスコープ外

#### 12.3 実証の構造

■ 3層の実証

`yaml
proofstructure:

# Layer 1: 技術的実証

technicalproof:
what: "提案する品質ゲートが機械的に動作すること"
how: "CI/CDで自動実行し、結果を公開"
evidence: - "GitHub Actions実行ログ" - "Allure Reportの公開URL" - "品質スコア推移グラフ"

# Layer 2: 手法的実証

methodologicalproof:
what: "この手法がAIDDにおいて有効であること"
how: "このアプリ自体をAIDDで開発し、品質を達成"
evidence: - "要件定義から実装までのトレーサビリティ" - "Deep Eval 0.8以上の達成" - "構造一貫性の維持"

# Layer 3: 実用的実証

practicalproof:
what: "現場で実際に使えること"
how: "Phase 1で仕様書評価から小規模導入"
evidence: - "パイロットプロジェクトの成果" - "現場エンジニアのフィードバック" - "バグ削減の定量データ"
`

プロジェクト実行計画
13.1 Phase 0: サンプルプロジェクト完成

■ 成果物

`yaml
phase0deliverables:

# 1. 動作するWebアプリ

application:
features: - "3層ワークフロー表示" - "タスクステータス管理" - "Abort理由記録" - "判断ログ記録" - "トレーサビリティマトリクス" - "JSON/YAMLエクスポート" - "品質フロー図生成"

# 2. CI/CD環境

cicd:
components: - "GitHub Actions workflow" - "Deep Eval統合" - "Promptfoo統合" - "JSON Schema検証" - "Allure Report自動生成" - "スコア推移記録"

# 3. コンテンツ

contents: - "要件定義ワークフローテンプレート" - "基本設計ワークフローテンプレート" - "詳細設計ワークフローテンプレート" - "曖昧語チェックリスト" - "検証可能性チェックリスト" - "プロンプトテンプレート集（10種以上）"

# 4. ドキュメント

documentation: - "README（クイックスタート）" - "アーキテクチャ設計書" - "品質ゲート解説" - "CI/CD設定ガイド" - "トラブルシューティング"
`

■ 完了基準

`yaml
phase0completioncriteria:

functional: - "定義された15画面すべてが設計通りに動作" - "データの保存・読込が正常" - "エクスポート機能が動作"

qualitygates: - "Deep Eval Score >= 0.8" - "曖昧語検出 = 0" - "JSON Schema検証 = 100%" - "トレーサビリティ = 100%"

cicd: - "全Jobが正常実行" - "Allure Reportが自動生成" - "スコア推移が記録"

documentation: - "第三者が1時間以内にセットアップ可能" - "すべての機能に説明ドキュメント"
`

13.2 Phase 1-4 概要

| Phase   | 期間想定 | 主要活動                     | KPI                    |
| ------- | -------- | ---------------------------- | ---------------------- |
| Phase 1 | 1-2ヶ月  | 仕様書妥当性評価の現場導入   | 仕様書起因バグ20%削減  |
| Phase 2 | 2-3ヶ月  | 要件定義工程追加             | 手戻り15%削減          |
| Phase 3 | 3-4ヶ月  | 全設計工程カバー             | トレーサビリティ100%   |
| Phase 4 | 継続     | プロンプト共有機能、外部連携 | プロンプトDB 100件以上 |

リスクと制約の明確化
14.1 制約条件の整理

`yaml
constraints:

# 技術制約

technical: - constraint: "OpenAI APIのみ使用可能"
impact: "他のLLMとの比較検証ができない"
mitigation: "将来的なマルチモデル対応を設計に考慮"

    - constraint: "Windows環境のみ"
      impact: "Mac/Linux環境での動作未検証"
      mitigation: "コンテナ化を将来検討"

    - constraint: "1人開発"
      impact: "開発速度、品質レビューの限界"
      mitigation: "自動テストの充実、外部レビュー依頼"

# プロジェクト制約

project: - constraint: "サンプルプロジェクト"
impact: "実運用の課題が未発見の可能性"
mitigation: "Phase 1での小規模実証"

    - constraint: "予算制限"
      impact: "有料ツール・サービスの選択肢が限定"
      mitigation: "OSSの最大活用"

# スキル制約

skill: - constraint: "JSON/YAML読み書き必須"
impact: "ユーザー層が限定される"
mitigation: "GUIによる補助、エラーメッセージの充実"
reason: "人による最終判断の質を担保するため"
`

#### 14.2 できること・できないことの明示

**できること**

`yaml
capabilities:

- "上流工程の品質観点を構造化して提示"
- "品質ゲートによる機械的チェックの自動化"
- "判断プロセスと根拠の記録・可視化"
- "トレーサビリティの完全な追跡"
- "CI/CDによる継続的品質監視"
- "プロンプト品質の定量評価"
- "評価スコアの推移モニタリング"
- "プロジェクト固有の品質履歴生成"
  `

**できないこと**

`yaml
noncapabilities:

- "AIによる自動判断（人の判断を代替しない）"
- "完全な品質保証（あくまでプロセス支援）"
- "すべてのバグの検出（上流工程に特化）"
- "ドメイン知識の自動習得（テンプレートは人が作成）"
- "リアルタイムコラボレーション（Phase 0では）"
- "多言語対応（日本語のみ）"
  `

### 結論と次のステップ

#### 15.1 本企画の価値

本企画は、単なるツール開発ではなく、

> AI駆動開発時代における品質保証の在り方を問い直し、
> 実証可能な形で提示する取り組み

である。

■ 3つの革新性
構造化された品質保証

- 属人的なQA観点を、ID体系とトレーサビリティで構造化

検証可能な品質基準

- Deep Eval、Promptfoo等による定量的評価

自己実証的なアプローチ

- 提案手法を自らに適用し、有効性を証明

#### 15.2 成功の定義

`yaml
successcriteria:

# Phase 0: サンプルプロジェクト

phase0:
technical: "アプリが設計通りに動作し、品質ゲートをすべて通過"
methodological: "AIDDで開発し、Deep Eval 0.8以上を達成"
evidence: "CI/CD環境とAllure Reportを公開"

# Phase 1: 現場導入

phase1:
adoption: "1件以上のパイロットプロジェクトで実施"
impact: "仕様書起因のバグを定量的に削減"
feedback: "現場から改善提案を5件以上収集"

# Phase 2-3: 拡大

expansion:
coverage: "上流工程全体をカバー"
traceability: "要件→設計→テストの紐付け100%"
standardization: "社内標準プロセスとして承認"

# Phase 4: エコシステム

ecosystem:
knowledgebase: "プロンプトDB 100件以上"
community: "他プロジェクトでの自発的採用"
evolution: "コミュニティからの貢献"
`

#### 15.3 次のアクション

■ 即座に着手すべきこと

`yaml
immediateactions:

1requirementdefinition:
task: "この企画書をYAML化し、要件定義書を作成"
deliverable: "requirements.yaml"
next: "品質ゲート（曖昧語チェック、検証可能性）を通過させる"

2architecturedesign:
task: "技術スタック確定とアーキテクチャ設計"
deliverable: "architecture.yaml"
next: "JSON Schema定義、データモデル設計"

3cicdsetup:
task: "GitHub Repository作成とCI/CD初期設定"
deliverable: ".github/workflows/qa.yml"
next: "Deep Eval、Promptfoo統合"

4contentcreation:
task: "要件定義ワークフローテンプレート作成"
deliverable: "templates/requirement_workflow.yaml"
next: "チェックリスト、プロンプトテンプレート作成"
`

#### 15.4 まとめ

AI駆動開発における品質保証の未来

AI が設計し、実装する時代において、
人間の役割は「判断」と「責任」である。

本プラットフォームは、

• AIに丸投げするツールではない
• 完璧な品質を保証する魔法でもない

それは、

> 品質保証を「個人の力量」から「構造とログ」に移し、
> AIと共に働く時代の、人間の責任の取り方を示すもの

である。

「動けば満足」から
「なぜそう作ったか説明できる」開発へ。

それが、このプロジェクトが目指す未来である。

付録
16.1 参考資料

`yaml
references:

tools: - name: "Deep Eval"
url: "https://docs.confident-ai.com/"
purpose: "LLM出力の品質評価"

    - name: "Promptfoo"
      url: "https://www.promptfoo.dev/"
      purpose: "プロンプト品質評価"

    - name: "Allure Report"
      url: "https://docs.qameta.io/allure/"
      purpose: "テスト結果の可視化"

methodologies: - name: "Contract Testing"
relevance: "構造の逸脱を最大リスクとする発想の元"

    - name: "Traceability Matrix"
      relevance: "要件-設計-テストの紐付け手法"

``

#### 16.2 用語集（再掲）

| 用語             | 定義                                       |
| ---------------- | ------------------------------------------ |
| AIDD             | AI駆動開発。LLMを活用した開発手法          |
| QA4AIDD          | ①AIに正しく指示 ②指示の遵守確認            |
| 上流工程         | （企画）要件定義・基本設計・詳細設計       |
| 品質保証（QA）   | プロセスに焦点、欠陥予防                   |
| 品質管理（QC）   | 成果物に焦点、欠陥検出                     |
| 曖昧語           | 「適切に」「柔軟に」等の解釈が分かれる表現 |
| 品質ゲート       | 次工程移行の可否判定チェックポイント       |
| トレーサビリティ | 要件-実装-テストの追跡可能性               |
