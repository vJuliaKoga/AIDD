# Deep Eval Action Plan (1 week)

## 根拠（reason由来の頻出パターン）

- Top patterns: 曖昧語残存(136), AC/Given-When-Then不足(107), How混入（技術/実装詳細の混入）(106), 手順/形式の欠落（評価手順・出力形式不一致）(83), 主語（ロール）不明確(76), 外部観測可能性が弱い(73)

## Day1: How混入除去ルール化（禁止語/危険ワード辞書）
- reasonで頻出の技術固有語（例: SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等）の混入を、要件文から排除するルールを策定
- 置換方針: ‘手段’→‘外部観測可能な結果’（表示/出力/通知/永続性/合否）に言い換える

## Day2: ロール主語の統一（user/admin/viewer/system）
- reasonで ‘主語不明/誰が’ 指摘のある要件を優先して、主語を許可ロールへ統一
- ‘システム’ 等の曖昧表現は system に置換し、操作主体（user/admin/viewer）を明示

## Day3: ACをGiven-When-Thenで最低1件付与（機能要件）
- reasonで ‘AC不足/Given-When-Thenが導出不能’ 指摘のある要件から着手
- 各要件で最低1件はGWT形式に落とし、Thenを合否判定可能な観測結果にする

## Day4: 境界条件の数値化（上限/時間/件数/閾値）
- reasonで ‘境界条件不足/数値不在/閾値未定義’ とされた要件に、応答時間・件数上限・保持期間・タイムアウト等を追記

## Day5: 参照可能性（derived_from/traces_to/用語定義）修正
- reasonで ‘参照不能/到達不能/定義欠如/traces_to空’ 指摘のある要件を、参照先の実在/用語定義/リンク整合へ修正

## Day6-7: 再評価→差分確認→回帰防止ルール
- Deep Evalを再実行し、reports/deep_eval_findings.csv の差分で改善が出た要件を確認
- 再発パターン（How混入/主語不明/AC不足/境界条件不足）をルール化してテンプレ・レビュー観点に組み込む
