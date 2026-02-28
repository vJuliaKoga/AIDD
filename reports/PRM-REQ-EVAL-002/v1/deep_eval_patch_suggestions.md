# Deep Eval Patch Suggestions

## 修正テンプレ（What/Why/AC/GWT/Not-How/Role/Boundaries/Errors/Trace）

```yaml
req_id: REQ-...
title: ...
target_role: system  # user/admin/viewer/system のいずれか
description: |
  # What: 外部から観測できる結果で書く
  # Not-How: DB/ライブラリ/フレームワーク/CI/CD等の手段は書かない
rationale: |
  # Why: 企画目的（構造化/可視化/検証可能化）への貢献を明記
acceptance_criteria:
  - criterion: |
      Given ...
      When ...
      Then ...
    verification_method: テスト
boundaries:
  # 例: max_items, timeout_seconds, retention_days, response_time_ms など
exceptions:
  # 失敗時の通知/表示/ログ/次アクション
trace:
  derived_from: PLN-...
  traces_to: [DES-..., TST-...]
```

## よくあるNG→OK言い換え例（10個）

1. NG: 「システムはSQLiteに保存する」
   OK: 「system はデータを永続化し、再起動後も同一データを参照できる」

2. NG: 「node-cronで深夜2時に実行する」
   OK: 「system は毎日 02:00（JST）に処理を開始し、完了/失敗を外部から確認できる」

3. NG: 「React Flow形式で生成する」
   OK: 「system はフロー図データを構造化形式で出力し、再構築可能である」

4. NG: 「GitHub ActionsでCI/CDを構築する」
   OK: 「system は自動検証を実行し、検証結果（PASS/FAILと理由）を出力する」

5. NG: 「ajvでスキーマ検証する」
   OK: 「system は成果物が規定スキーマに適合するか検証し、不適合時は違反箇所と修正ガイドを返す」

6. NG: 「モード設定はlocalStorageに保存される」
   OK: 「user の設定は次回起動後も維持され、user が再設定せずに同一設定で開始できる」

7. NG: 「全機能がキーボードショートカットで操作できる」
   OK: 「user は主要操作（対象を列挙）をショートカットで実行でき、成功/失敗が画面に表示される」

8. NG: 「即座に切り替わる」
   OK: 「切替操作から 300ms 以内に表示状態が更新される」

9. NG: 「管理できる/参照できる」
   OK: 「user が一覧画面で対象を検索し、選択すると詳細が表示される（表示項目を列挙）」

10. NG: 「設計ドキュメントに記録する」
   OK: 「system は変更履歴（日時/変更者/変更内容）を出力し、第三者が差分を確認できる」

## 修正の『機械ルール』（重要ルール準拠）

- How混入は最優先: SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等の技術語が出たら ‘観測可能な結果’ に言い換える
- 主語は user/admin/viewer/system に統一し、曖昧主語（ユーザー/第三者/判断者等）は正規化する
- acceptance_criteria は1件以上。Given/When/Then を揃え、Then に合否判定可能な結果を書く
- 曖昧語（適切に/等/リアルタイム等）を検出したら数値・条件に置換する
- 境界条件（件数/時間/サイズ/保持/閾値）が不足と指摘されたらACに数値で追記する
- derived_from/traces_to を整備し、参照不能/未定義が出たら本文内定義 or 参照先明記で解消する
- 異常系（失敗時の通知/ログ/リカバリ/次アクション）を明記する
