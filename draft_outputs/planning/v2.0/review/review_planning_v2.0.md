### Review

企画書バージョン: v2.0
最終更新日: 2026-02-21
Review担当者: 古賀

### Quality Gate 1: 曖昧語チェック

■ 検出された曖昧語と修正提案

| 箇所 | 検出された曖昧語         | 文脈                                                             | 修正提案                                                                 | 優先度 |
| ---- | ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------------ | ------ |
| 1.1  | "急速に進展"             | AI駆動開発の導入により、コード生成・設計支援が急速に進展している | "2022年比で導入率が300%増加" または削除                                  | Medium |
| 1.1  | "深刻な"                 | しかし、現場では深刻な品質課題が顕在化                           | "プロジェクト遅延率40%増加などの"                                        | High   |
| 1.1  | "爆発的増加"             | テスト工数の爆発的増加                                           | "テスト工数が平均2.5倍に増加"                                            | High   |
| 1.1  | "多発"                   | 手戻り多発                                                       | "手戻り発生率が50%以上"                                                  | High   |
| 2.1  | "サンプルプロジェクト"   | サンプルプロジェクトとして設計                                   | 定義済（2.1で明確化済）のため許容                                        | Low    |
| 3.1  | "限定的"                 | 限定的（個人プロジェクト規模）                                   | "月額予算10万円以内"                                                     | Medium |
| 4.1  | "直感的な"               | 直感的な操作で品質保証活動                                       | "3クリック以内で目的の情報にアクセス可能な"                              | Medium |
| 6.1  | "詳細な"                 | 詳細な根拠と代替案検討記録                                       | "判断理由200文字以上、代替案2つ以上記載の"                               | High   |
| 7.1  | "同じ"                   | 同じ構造の要素が同じUIで実装                                     | "JSON Schema定義に準拠した構造の要素が、同一のReactコンポーネントで実装" | High   |
| 8.1  | "実施したQAタスクの流れ" | 実施したQAタスクの流れを視覚化                                   | 許容（一般的な表現）                                                     | Low    |
| 10.1 | "即座に"                 | 効果が即座に可視化                                               | "1週間以内に"                                                            | Medium |
| 10.1 | "最小"                   | 既存プロセスへの影響が最小                                       | "既存プロセス変更箇所が3ステップ以内"                                    | Medium |
| 11.3 | "限定的な"               | 限定的なプロジェクト経験                                         | "過去5プロジェクトの"                                                    | Medium |
| 13.1 | "すべての"               | すべての画面が設計通りに動作                                     | "定義された15画面すべてが"                                               | Medium |
| 15.1 | "本質的"                 | 本企画の本質的価値                                               | 削除可能（強調表現）                                                     | Low    |

■ 曖昧語チェック結果サマリー

``yaml
ambiguouswordcheckresult:
totaldetected: 15

bypriority:
high: 6 # 数値化必須
medium: 7 # 数値化推奨
low: 2 # 許容範囲

bycategory:
quantitativemissing: 8 # 数値基準が必要
definitionmissing: 4 # 定義が必要
acceptable: 3 # 文脈上許容

passthreshold: 0 # 必須曖昧語（High優先度）= 0
currentstatus: "FAILED"
requiredaction: "High優先度の6箇所を修正"
`

### Quality Gate 2: 検証可能性チェック

■ 検証可能性の評価

各セクションの成功条件・受入基準が検証可能（テスト可能）かを評価します。

| セクション            | 成功条件の記述                             | 検証可能性 | 検証方法が想像できるか                           | 判定 | 改善提案                                                              |
| --------------------- | ------------------------------------------ | ---------- | ------------------------------------------------ | ---- | --------------------------------------------------------------------- |
| 6.1 品質基準          | "Deep Eval 0.8以上"                        | ✅ Yes     | スクリプト実行で数値取得                         | PASS | -                                                                     |
| 6.1 品質基準          | "曖昧語0件"                                | ✅ Yes     | 正規表現マッチング                               | PASS | -                                                                     |
| 6.1 品質基準          | "トレーサビリティ >= 95%"                  | ✅ Yes     | カバレッジ計算                                   | PASS | -                                                                     |
| 8.1 可視化            | "品質フロー図生成"                         | ⚠️ Partial | 「生成される」は確認可能だが品質基準なし         | WARN | "React Flow形式で出力され、全タスクノードが表示されること"            |
| 10.1 導入戦略         | "仕様書起因バグ30%削減"                    | ✅ Yes     | バグトラッキングデータ比較                       | PASS | -                                                                     |
| 10.2 プロセス統合     | "既存プロセス変更箇所が3ステップ以内"      | ❌ No      | 修正後の基準、何をもって「ステップ」とするか不明 | FAIL | "既存ワークフローのフローチャート上で、追加ノードが3個以内であること" |
| 11.2 ワークフロー検証 | "人間が読んで違和感がない"                 | ❌ No      | 主観的、判定基準なし                             | FAIL | "5名のレビュアーによる評価で、平均4.0/5.0以上のスコア"                |
| 11.3 コンテンツ品質   | "実際のプロジェクトで使用して有効性を確認" | ⚠️ Partial | 「有効性」の定義が曖昧                           | WARN | "Deep Evalスコア0.8以上を達成、かつ手戻り発生0件"                     |
| 13.1 Phase 0完了基準  | "第三者が1時間以内にセットアップ可能"      | ✅ Yes     | タイマー計測                                     | PASS | -                                                                     |
| 15.1 Phase 0成功基準  | "品質ゲートをすべて通過"                   | ✅ Yes     | CI/CDログ確認                                    | PASS | -                                                                     |
| 15.1 Phase 1成功基準  | "現場から改善提案を5件以上収集"            | ✅ Yes     | フィードバックDB件数カウント                     | PASS | -                                                                     |

■ 検証可能性チェック結果サマリー

`yaml
testabilitycheckresult:
totalcriteria: 11

bystatus:
pass: 7 # 明確に検証可能
warn: 2 # 部分的に検証可能
fail: 2 # 検証方法が不明確

passthreshold: "FAIL = 0, WARN <= 2"
currentstatus: "FAILED"

requiredactions: - "FAIL 2件の修正（主観的基準の定量化）" - "WARN 2件の明確化（品質基準の追加）"

criticalissues: - issue: "「人間が読んで違和感がない」は主観的"
impact: "ワークフロー妥当性検証の核心部分"
priority: "Critical"

    - issue: "「既存プロセス変更箇所が3ステップ以内」の定義不足"
      impact: "段階的導入の成功基準が曖昧"
      priority: "High"

`

### Quality Gate 3: トレーサビリティ設計の妥当性検証

■ トレーサビリティマトリクスの完全性チェック

企画書内で提示されたトレーサビリティ設計が、実際に追跡可能な構造になっているかを検証します。

### 3.1 ID体系の完全性

`yaml
idsystemcompleteness:

# 定義されているID体系

definedprefixes: - "REQ-" # 要件 - "BAS-" # 基本設計 - "DET-" # 詳細設計 - "TST-" # テストケース - "PRM-" # プロンプト - "CHK-" # チェックリスト - "RES-" # テスト結果 - "SNAP-" # スナップショット

# 欠落しているID体系

missingprefixes: - "PLN-" # 企画（この企画書自体のID）- "ARC-" # アーキテクチャ設計 - "UI-" # UI設計・コンポーネント - "API-" # APIエンドポイント - "DB-" # データベーススキーマ - "WF-" # ワークフロー定義 - "TPL-" # テンプレート - "ABT-" # Abortログ - "DEC-" # 判断ログ

coverage: "47%" # 8/17
status: "FAILED"
threshold: "90%以上"
`

### 3.2 トレーサビリティリンクの検証

企画書内の各要素が相互に参照可能かを確認します。

| 上流要素                | 下流要素               | リンク方法の定義 | 定義の有無 | 判定 |
| ----------------------- | ---------------------- | ---------------- | ---------- | ---- |
| 企画書セクション        | 要件定義項目           | ❌ 未定義        | No         | FAIL |
| 要件 → 基本設計         | tracesto フィールド    | ✅ 定義済（5.1） | Yes        | PASS |
| 基本設計 → 詳細設計     | tracesto フィールド    | ✅ 定義済（5.1） | Yes        | PASS |
| 詳細設計 → テストケース | tracesto フィールド    | ✅ 定義済（5.1） | Yes        | PASS |
| 要件 → プロンプト       | promptsused フィールド | ✅ 定義済（5.1） | Yes        | PASS |
| プロンプト → 評価結果   | evaluation フィールド  | ✅ 定義済（5.1） | Yes        | PASS |
| タスク → チェックリスト | checkpoints[].id       | ✅ 定義済（5.2） | Yes        | PASS |
| タスク → テンプレート   | template.id            | ⚠️ ID未定義      | Partial    | WARN |
| Abort → 代替措置        | alternativeaction      | ✅ 定義済（5.3） | Yes        | PASS |
| 判断ログ → エビデンス   | evidence[]             | ✅ 定義済（6.3） | Yes        | PASS |

`yaml
traceabilitylinkcheck:
totallinks: 10

bystatus:
pass: 8
warn: 1
fail: 1

coverage: "80%"
status: "FAILED"
threshold: "95%以上"

criticalgap: - "企画書から要件定義へのトレーサビリティが未定義" - "テンプレートIDの体系が未定義"
`

### 3.3 逆トレーサビリティの検証

下流から上流への追跡可能性を確認します。

`yaml
backwardtraceability:

scenarios: - scenario: "テストケースから要件を特定できるか"
mechanism: "TST-R001 → tracesfrom → REQ-F001"
defined: true
status: "PASS"

    - scenario: "バグ報告から設計を特定できるか"
      mechanism: "未定義"
      defined: false
      status: "FAIL"
      note: "バグレポートのID体系が未定義"

    - scenario: "Abort理由から元のタスクを特定できるか"
      mechanism: "abortlog.taskid → REQ-T005"
      defined: true
      status: "PASS"

    - scenario: "プロンプト改善履歴から元の要件を特定できるか"
      mechanism: "PRM-REQ-001 → 使用元のタスクID"
      defined: false
      status: "FAIL"
      note: "プロンプトから使用元タスクへのリンクが未定義"

coverage: "50%"
status: "FAILED"
threshold: "90%以上"
`

### 3.4 変更影響分析の実行可能性

`yaml
impactanalysiscapability:

testcases: - change: "要件REQ-F001の変更"
requiredtrace: "REQ-F001 → BAS-, DET-, TST-, PRM-"
canidentifyimpact: true
automationpossible: true
status: "PASS"

    - change: "UI設計の変更"
      requiredtrace: "UI- → 影響を受ける実装"
      canidentifyimpact: false
      reason: "UI設計のID体系が未定義"
      status: "FAIL"

    - change: "プロンプトテンプレートの変更"
      requiredtrace: "PRM- → 使用しているタスク"
      canidentifyimpact: false
      reason: "逆方向のトレースが未定義"
      status: "FAIL"

    - change: "チェックリストの追加"
      requiredtrace: "CHK-* → 適用されるタスク"
      canidentifyimpact: true
      status: "PASS"

coverage: "50%"
status: "FAILED"
threshold: "100%"
`

■ トレーサビリティ設計チェック結果サマリー

`yaml
traceabilitydesigncheckresult:

dimensions:
idsystemcoverage: "47%" # FAIL (threshold: 90%)
forwardtracecoverage: "80%" # FAIL (threshold: 95%)
backwardtracecoverage: "50%" # FAIL (threshold: 90%)
impactanalysiscoverage: "50%" # FAIL (threshold: 100%)

overallstatus: "FAILED"

criticalgaps:
1:
issue: "企画書→要件定義のトレーサビリティ未定義"
impact: "企画意図が要件に正しく反映されたか検証不能"
priority: "Critical"

    2:
      issue: "ID体系が不完全（9種類が未定義）"
      impact: "アーキテクチャ・UI・ワークフロー等の追跡不能"
      priority: "Critical"

    3:
      issue: "逆トレーサビリティが50%"
      impact: "バグや変更から上流への影響分析が困難"
      priority: "High"

    4:
      issue: "変更影響分析が50%しか実行不可"
      impact: "保守性・拡張性に重大な欠陥"
      priority: "High"

`

### 品質ゲート総合判定

`yaml
overallqualitygateresult:

gateresults:
G1ambiguouswords:
status: "FAILED"
score: "6/15 (40%)"
threshold: "High優先度 = 0"

    G2testability:
      status: "FAILED"
      score: "7/11 (64%)"
      threshold: "FAIL = 0"

    G3traceabilitydesign:
      status: "FAILED"
      score: "56.75%"  # 平均
      threshold: "90%"

finaljudgment: "❌ REJECTED - 修正必須"

deploymentblocked: true

requiredactions:
immediate: - "曖昧語6箇所の数値化（High優先度）" - "検証不可能な基準2箇所の定量化" - "ID体系の完全化（9種類追加）" - "企画書→要件のトレーサビリティ定義"

    highpriority:
      - "曖昧語7箇所の数値化（Medium優先度）"
      - "検証可能性WARN 2箇所の明確化"
      - "逆トレーサビリティの定義"
      - "変更影響分析の完全化"

`

### 修正版企画書への要求仕様

品質ゲートを通過するための修正要求を構造化します。

■ 修正要求一覧

`yaml
correctionrequirements:

# CR-001: 曖昧語の排除

CR-001:
title: "High優先度曖昧語の数値化"
category: "曖昧語チェック"
priority: "Critical"
items: - location: "1.1 課題定義"
original: "深刻な品質課題"
corrected: "プロジェクト遅延率40%増加、手戻り発生率50%以上などの品質課題"

      - location: "1.1 課題定義"
        original: "テスト工数の爆発的増加"
        corrected: "テスト工数が計画比で平均2.5倍に増加"

      - location: "1.1 課題定義"
        original: "手戻り多発"
        corrected: "手戻り発生率が50%以上のプロジェクトが全体の60%"

      - location: "6.1 判断ログ"
        original: "詳細な根拠と代替案検討記録"
        corrected: "判断理由200文字以上、検討した代替案2つ以上を記載した根拠"

      - location: "7.1 UI統一性"
        original: "同じ構造の要素が同じUIで実装"
        corrected: "JSON Schema定義に準拠した構造の要素が、同一のReactコンポーネントで実装"

      - location: "10.1 導入戦略"
        original: "既存プロセスへの影響が最小"
        corrected: "既存ワークフローのフローチャート上で、追加ノードが3個以内"

# CR-002: 検証可能性の確保

CR-002:
title: "主観的基準の定量化"
category: "検証可能性"
priority: "Critical"
items: - location: "11.2 ワークフロー妥当性検証"
original: "人間が読んで違和感がない"
corrected: "5名のレビュアー（QAエンジニア3名、開発者2名）による評価で、5段階評価の平均4.0以上"
testmethod: "Googleフォームでの評価収集、平均値計算"

      - location: "10.2 プロセス統合"
        original: "既存プロセス変更箇所が3ステップ以内"
        corrected: "既存ワークフローのBPMN図上で、追加される判断ノード・タスクノードが合計3個以内"
        testmethod: "BPMN図の差分カウント"

# CR-003: 検証可能性の明確化

CR-003:
title: "WARN項目の品質基準追加"
category: "検証可能性"
priority: "High"
items: - location: "8.1 品質フロー図生成"
original: "品質フロー図生成"
addcriteria: | - React Flow形式のJSONデータとして出力されること - 全タスクノード（Done/Abort含む）が表示されること - ノード間の接続関係が正しいこと（親子関係、実施順序）- Abort分岐が点線で表示されること
testmethod: "出力JSONのスキーマ検証、描画結果のスクリーンショット比較"

      - location: "11.3 コンテンツ品質"
        original: "実際のプロジェクトで使用して有効性を確認"
        addcriteria: |
          - そのテンプレート使用時にDeep Evalスコア0.8以上を達成
          - 使用したプロジェクトで手戻り発生0件
          - プロンプトの場合、Promptfooスコア0.8以上
        testmethod: "評価スコアの記録、プロジェクト完了報告の確認"

# CR-004: ID体系の完全化

CR-004:
title: "不足しているID体系の追加定義"
category: "トレーサビリティ"
priority: "Critical"
items: - idprefix: "PLN-"
name: "企画"
description: "企画書のセクション、要求事項"
example: "PLN-REQ-001（企画要求1）"

      - idprefix: "ARC-"
        name: "アーキテクチャ設計"
        description: "システムアーキテクチャの設計項目"
        example: "ARC-SYS-001（システム構成1）"

      - idprefix: "UI-"
        name: "UI設計"
        description: "UIコンポーネント、画面設計"
        example: "UI-CMP-001（コンポーネント1）"

      - idprefix: "API-"
        name: "APIエンドポイント"
        description: "API設計、エンドポイント定義"
        example: "API-GET-001（GETエンドポイント1）"

      - idprefix: "DB-"
        name: "データベーススキーマ"
        description: "テーブル、カラム定義"
        example: "DB-TBL-001（テーブル1）"

      - idprefix: "WF-"
        name: "ワークフロー定義"
        description: "品質保証ワークフローのテンプレート"
        example: "WF-REQ-001（要件定義ワークフロー）"

      - idprefix: "TPL-"
        name: "テンプレート"
        description: "ドキュメントテンプレート"
        example: "TPL-CHK-001（チェックリストテンプレート）"

      - idprefix: "ABT-"
        name: "Abortログ"
        description: "Abort判断の記録"
        example: "ABT-REQ-T005-001（タスクAbort記録）"

      - idprefix: "DEC-"
        name: "判断ログ"
        description: "重要な判断の記録"
        example: "DEC-ARC-001（アーキテクチャ判断1）"

# CR-005: 企画→要件トレーサビリティの定義

CR-005:
title: "企画書から要件定義へのトレーサビリティ定義"
category: "トレーサビリティ"
priority: "Critical"
specification: |
企画書の各セクションにPLN-IDを付与し、
要件定義書の各要件にderivedfromフィールドを追加。

      例：
      `yaml
      # 企画書
      planning:
        - id: PLN-GOAL-001
          content: "仕様書と実装の乖離を防止する"

      # 要件定義書
      requirement:
        - id: REQ-F001
          title: "曖昧語検出機能"
          derivedfrom:
            - PLN-GOAL-001
            - PLN-CHALLENGE-002
          rationale: "仕様書の曖昧性が乖離の主原因であるため"
      `

# CR-006: 逆トレーサビリティの定義

CR-006:
title: "逆方向トレーサビリティの定義"
category: "トレーサビリティ"
priority: "High"
items: - direction: "プロンプト → 使用タスク"
mechanism: |
プロンプト定義にusedintasksフィールドを追加
`yaml
          prompt:
            id: PRM-REQ-001
            usedintasks:
              - REQ-T001
              - REQ-T003
          `

      - direction: "バグ → 設計"
        mechanism: |
          バグレポートのID体系を追加（BUG-）
          `yaml
          bug:
            id: BUG-001
            tracesto:
              design: BAS-D001
              test: TST-R001
          `

`

### 修正優先度マトリクス

`yaml
correctionprioritymatrix:

criticalpath: # これらを修正しないと次工程（要件定義）に進めない - CR-001: "曖昧語の数値化（High優先度6箇所）" - CR-002: "主観的基準の定量化（2箇所）" - CR-004: "ID体系の完全化（9種類追加）" - CR-005: "企画→要件トレーサビリティ定義"

highpriority: # 品質に直結するが、暫定対応で次工程開始可能 - CR-003: "WARN項目の品質基準追加" - CR-006: "逆トレーサビリティ定義" - "Medium優先度曖昧語の数値化（7箇所）"

estimatedeffort:
CR-001: "2時間"
CR-002: "1時間"
CR-003: "1.5時間"
CR-004: "3時間"
CR-005: "2時間"
CR-006: "2.5時間"
total: "12時間"
`

### Next action

即座に実施すべきこと
Critical Path修正の実施
`yaml
actionplan:
step1:
task: "CR-001の修正（曖昧語6箇所の数値化）"
deliverable: "修正済み企画書 v2.1"
time: "2時間"

     step2:
       task: "CR-002の修正（主観的基準2箇所の定量化）"
       deliverable: "修正済み企画書 v2.2"
       time: "1時間"

     step3:
       task: "CR-004の修正（ID体系9種類追加）"
       deliverable: "完全なID体系定義書"
       time: "3時間"

     step4:
       task: "CR-005の修正（企画→要件トレーサビリティ）"
       deliverable: "トレーサビリティ設計書 v2.0"
       time: "2時間"

     step5:
       task: "修正版企画書への品質ゲート再適用"
       deliverable: "品質ゲート通過証明"
       time: "1時間"

``

修正後の再検証

- 曖昧語チェック再実行（目標: High優先度 = 0）
- 検証可能性チェック再実行（目標: FAIL = 0）
- トレーサビリティチェック再実行（目標: 全項目90%以上）

YAML構造化への移行

- 品質ゲート通過後、企画書をYAML形式に構造化
- 各セクションにPLN-ID付与
- 要件定義書テンプレートの作成開始
