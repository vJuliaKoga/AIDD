# Deep Eval Patch Suggestions

## 修正テンプレ（What/Why/AC/GWT/Not-How/Role/Boundaries/Errors/Trace）

以下のテンプレで各要件を修正してください（特にHow混入・主語不明・AC不足・境界条件不足に効きます）。

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
   OK: 「system は毎日 02:00（JST）にバックアップ処理を開始し、完了/失敗を外部から確認できる状態にする」

3. NG: 「React Flow形式で生成する」
   OK: 「system は品質フロー図データを構造化形式で出力し、ノード/エッジ/ラベルが再構築可能である」

4. NG: 「GitHub ActionsでCI/CDを構築する」
   OK: 「system は自動検証パイプラインを提供し、検証結果（PASS/FAILと理由）が毎回出力される」

5. NG: 「ajvでスキーマ検証する」
   OK: 「system は成果物が規定スキーマに適合するか検証し、不適合時は違反箇所と修正ガイドを返す」

6. NG: 「モード設定はlocalStorageに保存される」
   OK: 「user のモード選択は次回起動後も維持され、user が再設定せずに同一モードで開始できる」

7. NG: 「全機能がキーボードショートカットで操作できる」
   OK: 「user は主要操作（対象を列挙）をショートカットで実行でき、操作成功/失敗が画面に表示される」

8. NG: 「即座に切り替わる」
   OK: 「切替操作から 300ms 以内に表示状態が更新される」

9. NG: 「管理できる」「参照できる」
   OK: 「user が一覧画面で対象を検索し、選択すると詳細が表示される（表示項目を列挙）」

10. NG: 「設計ドキュメントに記録する」
    OK: 「system は変更履歴（日時/変更者/変更内容）を出力し、第三者が差分を確認できる」
