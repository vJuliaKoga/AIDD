あなたはリポジトリ内の要件YAML群とチェックリスト、Deep Evalの評価JSONを読み込み、
「評価レポート」を reports/ 配下に生成するツールです。

# 目的

Deep Evalの評価が悪かった原因を、チェックリスト観点（purpose/scope/verifiability/ai_readability/traceability/schema/operational）に沿って整理し、
“どのファイル/どの要件ID/どの観点が”悪いのかを特定し、改善に直結する修正ガイドを作る。
加えて、timeout/キャンセル等「評価実行条件に起因する失敗」を切り分け、要件修正の優先順位がブレないようにする。

# 入力（この順で読む）

1. Deep Eval結果:

- eval_req_vs_planning_v1.json

2. チェックリスト定義:

- checklist.yaml

3. 評価対象の要件YAML（req\_\*.yaml と requirements_document_v1.yaml）:

- （略：既存の列挙そのまま）

# 出力（reports/ 配下に必ず作る）

A) reports/deep_eval_summary.md

- 全体サマリ（pass率、メトリクス平均、特に低い項目トップ5）
- 低スコア要因を「頻出パターン」として分類（例: How混入、ロール主語不明、AC欠落、根拠なし追加、曖昧語、境界条件不足、参照不能、traces_to空、deliverable不整合 等）
- “最優先で直すべき10件”を、影響度×頻度でランキング（※timeout由来は除外、下記ルール参照）
- 「企画→要件 網羅性（coverage）が低い/0.0」場合は、要件の書き方だけでなく
  企画項目との対応付け（不足/重複/不要/粒度違い）不足として別枠で要約する

B) reports/deep_eval_findings.csv
列: requirement_id, source_file, doc_id, metric_name, score, threshold, passed, reason, error, fix_hint, checklist_category, checklist_item_id, is_timeout_related, priority_score

- reason または error を必ず格納（片方が無ければ空）
- is_timeout_related は timeout/cancelled/context deadline など実行条件由来の判定フラグ
- priority_score は「閾値未達度 × 重み」で算出（timeout由来はスコア計算から除外し 0 扱い）

C) reports/deep_eval_action_plan.md

- 1週間でスコアを上げるための改善計画（既存の Day1〜Day7 を維持）
- 追加: まず Day0 として「timeout/キャンセルを切り分け、再評価条件を整える（必要ならtimeout延長）」を入れる
- 追加: “coverage/traceabilityが低い”を改善するための手順（企画項目→要件の対応表作成、derived_from/traces_to整備）を明記

D) reports/deep_eval_patch_suggestions.md

- “修正テンプレ”を提示（What/Why/AC/GWT/Not-How/Role/Boundaries/Errors/Trace）
- よくあるNG→OK言い換え例を10個
- 追加: 修正の「機械ルール」を明文化（後述の重要ルールに準拠）

E) reports/deep_eval_runtime_issues.md（★追加）

- timeout / cancelled / context deadline exceeded など「評価実行に起因」する問題だけを一覧化
- どのmetric/要件で発生したか、error全文（短い場合）と再実行時の対処案（timeout延長・対象分割・サンプル削減など）を記載
- 重要: このファイルの内容は要件修正の優先度計算には使わない（切り分け専用）

# 補足（優先ルール）

- “How混入”は最優先で扱う。SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等の技術固有語が要件文に出た場合は、
  原則「観測可能な結果」に言い換える修正案を必ず fix_hint に書く。
- 主語は user/admin/viewer/system のいずれかに統一し、主語が曖昧な要件を優先的にトップ10へ入れる。
- 重要: timeout/キャンセル由来（is_timeout_related=true）の項目は「最優先10件」から除外し、Eにのみ出す。

# 重要ルール（精度と再現性のための必須制約）

- レポート内の主張・指摘は必ず eval_req_vs_planning_v1.json の reason または error を根拠にする（推測しない）
- チェックリスト項目IDへ機械的にマッピングする（マッピングできない場合は checklist_item_id を空にし、理由を summary に記載）
- timeout/実行条件由来の判定ルール:
  - error/reason に "timeout", "timed out", "cancelled", "context deadline", "deadline exceeded" 等が含まれる場合 is_timeout_related=true
  - is_timeout_related=true の行は priority_score=0 とし、Top10算出から除外
- priority_score（Top10算出）ルール:
  - base = max(0, threshold - score) （閾値未達度）
  - weight は reason から判定（例: How混入=3, 主語不明=2, AC不足=2, 曖昧語=1.5, 参照不能/traces_to空=2, 境界条件不足=1.5 など）
  - priority_score = base \* weight （timeout由来は除外）
- 可能な範囲で “機械的に検出できる違反” を抽出（危険ワード、曖昧語、AC欠落、主語不明など）
- 既存ファイルは変更しない（レポート生成のみ）
- 出力ファイルは UTF-8、Markdownは見出し構造を持つ
- 自己検証:
  - E（runtime issues）が1件以上あるのに、AのTop10にtimeout由来が混入していないことを最終チェックする
  - B（CSV）に error 列と is_timeout_related 列が存在することを最終チェックする

# 実行手順

1. JSONをパースして全test_resultsを走査し、reason/error/score/threshold/passed を抽出
2. reason/error からチェックリストカテゴリ/項目IDへマッピング（できない場合は未マップ扱い）
3. is_timeout_related 判定を付与し、runtime issues を別枠抽出
4. priority_score を算出（timeout由来は除外）し、Top10を生成
5. 頻出パターン上位を集計（timeout由来は集計から除外し、Eで集計）
6. reports/PRM-REQ-EVAL-002 に A〜E を生成
7. 生成したファイル一覧と、自己検証結果（チェックOK/NG）を最後に表示

以上を実行してください。
