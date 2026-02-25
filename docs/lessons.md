# lessons.md — 学習記録・パターン集

> AIDDプロセス実践の中で得た知見を蓄積する。
> 更新ルール: 気づきが生まれたら即追記。根拠なき削除は禁止。

---

## 1. ID規約

### ルール
- 形式: `PREFIX-PHASE-PURPOSE-NNN`（必ず4セグメント）
- ID付与は必ず `AIDD/tools/id_registry/issue_id.py` で行う（手採番禁止）
- item ID の NNN はファイル内のリスト順番（1始まり）と一致させる

### 発見した問題パターン
- **症状**: `07_quality_assurance_design.yaml` の `PLN-PLN-QA_AMBIGUOUS_EXAMPLES-013` が位置5にあり NNN が不一致
  - **原因**: 後から挿入した item の NNN が総件数（13）になっていた
  - **対処**: item を正しい位置（末尾）に移動し NNN と位置を一致させた
  - **教訓**: item を中間挿入する際は NNN の付け直しが必要

---

## 2. 曖昧語について

### 検出対象語リスト（2026-02-24 時点）
```
適切に、十分に、柔軟に、簡単に、最適に、
基本的に、一般的に、必要に応じて、適宜、
なるべく、できるだけ、スムーズに、うまく
```

### 置換パターン例
| 曖昧語 | 置換例 |
|--------|--------|
| 「適切に処理する」 | 「3秒以内に処理を完了する」 |
| 「簡単にログインできる」 | 「3ステップ以内でログインできる」 |
| 「柔軟に対応する」 | 「設定ファイルを変更することで対応できる」 |
| 「十分なパフォーマンス」 | 「API応答時間が95パーセンタイルで500ms以内」 |

---

## 3. 品質ゲート

### G4（Deep Eval）について
- 閾値: 0.8（合格）/ 0.75（アラート）
- OpenAI API を使用。コストが発生するためログを保存する
- 評価指標は4等分（各0.25）: Contextual Relevancy / Faithfulness / Contextual Precision / Answer Relevancy
- プロンプト変更後は必ず Promptfoo でも評価する

### G1（曖昧語チェック）の運用
- フロントエンドでもリアルタイム検出を行う（UX向上）
- バックエンドでも独立して検出する（通過基準はバックエンドのみ）
- 同じ正規表現リストを `shared/` に置いてFE/BEで共用する

---

## 4. Windows環境での注意事項

### PowerShell運用ルール
- `python` を引数なしで実行してREPL（`>>>`）に入らない
- bash のヒアドキュメント（`<<`）を使わない
- コマンドは `python.exe` を明示することで PATH 問題を回避できる
- パス区切りは `\` または `/` どちらも動作するが、Pythonスクリプト内では `/` を推奨

---

## 5. YAMLファイル設計

### planning_v2.2 の設計パターン
- セクション分割: `NN_<section_name>.yaml`（ゼロパディングあり）
- 各ファイルは `meta` + `section` の2キーで構成
- `meta.run_id` = ファイル名（拡張子除く）と一致させる
- `section.id` の PURPOSE は section の内容を表す短縮語（例: EXEC, BG, QA）
- item の PURPOSE は `<section_PURPOSE>_<item_description>` の複合形式（例: QA_GATE_PHILOSOPHY）

### スキーマ検証
- スキーマ: `planning.section.schema.json` / `planning.index.schema.json`
- `type` フィールドの許容値: statement, definition, table, list, quote, metric, decision_rule, constraint
- `gate_exempt: true` を設定した item は曖昧語チェック（G1）から除外される

---

## 6. AIコーディング効率化

### 効果があった方法
- 定義書（PRD/画面遷移/技術スタック/FE指針/BE構造/実装計画）を先に準備することで、AIへの指示の構造が明確になる
- `progress.txt` でセッションをまたぐ状態を維持することで、再説明コストがゼロになる
- 要件定義YAMLを先に品質ゲートに通してから実装に入ることで、手戻りが減る

### 失敗パターン
- 要件が曖昧な状態でAIに実装を依頼すると、解釈がバラバラになる
- ID を手採番すると重複や連番ズレが起きる（必ずスクリプト経由）
- `progress.txt` を更新しないとセッション間で状態が失われる

---

## 7. 更新履歴

| 日付 | 追記内容 |
|------|---------|
| 2026-02-24 | 初版作成（lessons.md） |
| 2026-02-24 | ID規約の発見パターン追記（QA_AMBIGUOUS_EXAMPLES-013問題） |
| 2026-02-24 | Windows環境の注意事項追記 |
