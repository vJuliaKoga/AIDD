"""
Generate Deep Eval analysis reports under reports/ (v2).

Reads:
  1) Deep Eval result JSON:
     - deepeval/output/eval_req_vs_planning_v1.json
  2) Checklist definition:
     - checklist/CHK-REQ-REVIEW-001.yaml
  3) Requirements YAMLs (for fallback indexing only):
     - requirements/yaml/requirements_v1/*.yaml

Outputs (UTF-8, under --reports-dir):
  - deep_eval_summary.md
  - deep_eval_findings.csv
  - deep_eval_action_plan.md
  - deep_eval_patch_suggestions.md
  - deep_eval_runtime_issues.md
  - deep_eval_fix_backlog.csv            (NEW v2)
  - deep_eval_triage_summary.md          (NEW v2)

Hard constraints:
  - Any claim must be grounded in eval JSON reason or error (no speculation).
  - timeout/cancelled/context deadline exceeded => is_timeout_related=true.
  - is_timeout_related rows: priority_score=0, excluded from Top10 and pattern aggregation.
  - Checklist item mapping must be mechanical; if unmapped, checklist_item_id empty.
  - Do NOT modify any existing requirement YAMLs; report generation only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml


# ----------------------------
# Paths (repo-relative defaults)
# ----------------------------

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVAL_JSON_PATH = ROOT / "deepeval" / "output" / "eval_req_vs_planning_v1.json"
DEFAULT_CHECKLIST_PATH = ROOT / "checklist" / "CHK-REQ-REVIEW-001.yaml"
DEFAULT_REQ_DIR = ROOT / "requirements" / "yaml" / "requirements_v1"
DEFAULT_REPORTS_DIR = ROOT / "reports" / "PRM-REQ-EVAL-002"


# ----------------------------
# Types
# ----------------------------

@dataclass(frozen=True)
class ChecklistItem:
    category_id: str
    category_name: str
    category_name_en: str
    item_id: str
    item_title: str


@dataclass(frozen=True)
class DetectedIssue:
    key: str
    label: str
    checklist_item_id: str
    weight: float


@dataclass(frozen=True)
class RuntimeIssue:
    requirement_id: str
    source_file: str
    doc_id: str
    metric_name: str
    reason: str
    error: str


# ----------------------------
# Helpers
# ----------------------------

def _safe_str(x: Any) -> str:
    return "" if x is None else str(x)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def short_text(text: str, max_len: int = 200) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def join_uniq(items: Iterable[str], sep: str = "; ") -> str:
    out: List[str] = []
    seen: set[str] = set()
    for x in items:
        x = (x or "").strip()
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return sep.join(out)


# ----------------------------
# Checklist & requirement indexing
# ----------------------------

def build_checklist_index(checklist: Dict[str, Any]) -> Dict[str, ChecklistItem]:
    idx: Dict[str, ChecklistItem] = {}
    for cat in checklist.get("categories", []) or []:
        cat_id = _safe_str(cat.get("id"))
        cat_name = _safe_str(cat.get("name"))
        cat_name_en = _safe_str(cat.get("name_en"))
        for item in cat.get("items", []) or []:
            item_id = _safe_str(item.get("id"))
            if not item_id:
                continue
            idx[item_id] = ChecklistItem(
                category_id=cat_id,
                category_name=cat_name,
                category_name_en=cat_name_en,
                item_id=item_id,
                item_title=_safe_str(item.get("title")),
            )
    return idx


def build_requirement_index(req_dir: Path) -> Dict[str, Dict[str, str]]:
    """Map req_id -> {source_file, doc_id} (best-effort)."""
    out: Dict[str, Dict[str, str]] = {}
    for path in sorted(req_dir.glob("*.yaml")):
        try:
            y = load_yaml(path) or {}
        except Exception:
            continue
        doc = (y.get("requirements_document") or {}) if isinstance(y, dict) else {}
        doc_id = _safe_str(doc.get("doc_id"))
        for sec in ("functional_requirements", "non_functional_requirements"):
            for r in (doc.get(sec) or []):
                if not isinstance(r, dict):
                    continue
                req_id = _safe_str(r.get("req_id"))
                if not req_id:
                    continue
                out[req_id] = {"source_file": path.name, "doc_id": doc_id}
    return out


# ----------------------------
# Detection rules (must be supported by reason/error text)
# ----------------------------

DANGER_WORDS = [
    "SQLite", "PostgreSQL", "MongoDB", "DB", "テーブル", "カラム",
    "node-cron", "Node.js", "Express",
    "React", "localStorage", "Zod", "Tailwind", "shadcn", "React Flow", "Storybook",
    "Chromatic", "Playwright", "Vitest",
    "ajv",
    "GitHub Actions", "Allure", "Promptfoo",
    ".github/workflows", "workflow", "endpoint", "API", "REST", "GraphQL",
]

AMBIGUOUS_WORDS = [
    "適切に", "十分に", "柔軟に", "簡単に", "最適に", "迅速に",
    "など", "等", "その他", "必要に応じて", "すぐに", "リアルタイム", "大量", "多く",
]

TIMEOUT_PATTERNS = [
    "timeout", "timed out", "cancelled", "canceled",
    "context deadline", "deadline exceeded",
    "タイムアウト", "時間切れ", "キャンセル",
]


def is_timeout_related(reason_or_error: str) -> bool:
    s = (reason_or_error or "").lower()
    return any(p.lower() in s for p in TIMEOUT_PATTERNS)


def detect_issues(reason_or_error: str) -> List[DetectedIssue]:
    r = reason_or_error or ""
    issues: List[DetectedIssue] = []

    def has_any(words: Iterable[str]) -> bool:
        return any(w in r for w in words)

    if (
        "実装詳細" in r
        or ("技術" in r and "混入" in r)
        or "How" in r
        or has_any(DANGER_WORDS)
        or "危険ワード" in r
        or "技術スタック" in r
    ):
        issues.append(DetectedIssue("how_mixing", "How混入（技術/実装詳細の混入）", "CHK-02-02", 3.0))

    if (
        "主語" in r
        or "誰が" in r
        or "ロール" in r
        or "user/admin/viewer/system" in r
        or "許可ロール" in r
        or ("主体" in r and "曖昧" in r)
    ):
        issues.append(DetectedIssue("role_ambiguous", "主語（ロール）不明確", "CHK-02-03", 2.6))

    if (
        "acceptance_criteria" in r
        or "受入基準" in r
        or "テストケース化" in r
        or ("Given" in r or "When" in r or "Then" in r)
        or "(なし)" in r
    ):
        issues.append(DetectedIssue("ac_gwt", "受入基準/ Given-When-Then が不足", "CHK-03-02", 2.4))

    if ("外部観測" in r) or ("内部処理" in r) or ("観測可能" in r):
        issues.append(DetectedIssue("observability", "外部観測可能性が弱い（内部処理寄り）", "CHK-03-01", 2.0))

    if ("曖昧語" in r) or has_any(AMBIGUOUS_WORDS):
        issues.append(DetectedIssue("ambiguous_terms", "曖昧語が残存", "CHK-03-03", 1.9))

    if ("境界条件" in r) or ("閾値" in r) or ("上限" in r) or ("数値" in r) or ("未定義" in r and "境界" in r):
        issues.append(DetectedIssue("boundaries", "境界条件（数値/範囲/限界値）が不足", "CHK-03-04", 1.8))

    if (
        "評価手順" in r
        or "スコアリング" in r
        or "0.0〜1.0" in r
        or ("INPUT" in r and "ACTUAL_OUTPUT" in r)
        or ("形式" in r and "不一致" in r)
        or ("体裁" in r and "満た" in r)
    ):
        issues.append(DetectedIssue("prompt_structure", "手順/形式の欠落（プロンプト構造化不足）", "CHK-04-01", 1.6))

    if (
        "到達不能" in r
        or ("参照先" in r and "存在" in r and "しない" in r)
        or ("定義" in r and "欠如" in r)
        or "暗黙" in r
    ):
        issues.append(DetectedIssue("context_completeness", "コンテキスト完全性不足（用語定義/参照到達性）", "CHK-04-02", 1.5))

    if ("derived_from" in r and ("不一致" in r or "欠落" in r or "不整合" in r)) or ("traces_to" in r):
        if "traces_to" in r:
            issues.append(DetectedIssue("traces_to_missing", "traces_to が未整備", "CHK-05-03", 1.4))
        issues.append(DetectedIssue("derived_from_alignment", "derived_from 参照整合性の問題", "CHK-05-02", 1.4))

    if ("種別" in r) or ("スキーマ" in r) or ("必須" in r and "フィールド" in r):
        issues.append(DetectedIssue("schema_compliance", "スキーマ/メタデータの不整合", "CHK-06-01", 1.3))

    if ("例外" in r) or ("失敗時" in r) or ("リカバリ" in r) or ("通知" in r):
        issues.append(DetectedIssue("exceptions", "異常系/失敗時の定義が不足", "CHK-07-01", 1.2))

    return issues


def choose_primary_item(issues: List[DetectedIssue], reason_or_error: str) -> str:
    m = re.search(r"\bCHK-\d{2}-\d{2}\b", reason_or_error or "")
    if m:
        return m.group(0)
    if issues:
        return sorted(issues, key=lambda x: x.weight, reverse=True)[0].checklist_item_id
    return ""


def extract_evidence_terms(text: str, terms: List[str], limit: int = 6) -> List[str]:
    hits: List[str] = []
    for t in terms:
        if t in text:
            hits.append(t)
            if len(hits) >= limit:
                break
    return hits


def fix_hint_from(reason_or_error: str, issues: List[DetectedIssue]) -> str:
    r = reason_or_error or ""
    keys = {i.key for i in issues}
    hints: List[str] = []

    if "how_mixing" in keys:
        hits = extract_evidence_terms(r, DANGER_WORDS, limit=6)
        if hits:
            hints.append(
                "How混入を除去: reason/errorで指摘された技術語（{}）を要件文から削除し、『外部から観測できる結果（表示/出力/通知/永続性）』に言い換える"
                .format(", ".join(hits))
            )
        else:
            hints.append("How混入を除去: 実装手段ではなく観測可能な結果で記述する")

    if "role_ambiguous" in keys:
        hints.append("主語を統一: user/admin/viewer/system のいずれかで『誰が〜する』を明記する")

    if "ac_gwt" in keys:
        hints.append("ACを強化: 最低1件はGiven-When-Thenで追記し、When（トリガー）とThen（合否判定）を一意にする")

    if "observability" in keys:
        hints.append("外部観測可能に修正: 『内部で処理』ではなく『何がどこに表示/出力/通知されるか』をThenに置く")

    if "ambiguous_terms" in keys:
        hits = extract_evidence_terms(r, AMBIGUOUS_WORDS, limit=4)
        if hits:
            hints.append("曖昧語を置換: 指摘された曖昧語（{}）を削除し、数値・範囲・条件で具体化する".format(", ".join(hits)))
        else:
            hints.append("曖昧語を置換: 禁止語（適切に/等/リアルタイム等）を数値や条件に置き換える")

    if "boundaries" in keys:
        hints.append("境界条件を数値化: 件数上限/時間/サイズ/保持期間/閾値/タイムアウト等をACに追記する")

    if "context_completeness" in keys:
        hints.append("参照到達性を確保: 未定義の用語・IDを本文で定義、または参照先を明記する")

    if "derived_from_alignment" in keys or "traces_to_missing" in keys:
        hints.append("トレーサビリティを補強: derived_from整合を確認し、traces_to を空にしない（設計/テストIDを追記）")

    if "schema_compliance" in keys:
        hints.append("スキーマ/メタデータを整備: 必須フィールド（target_role/priority/AC等）の欠落や不一致を解消する")

    if "exceptions" in keys:
        hints.append("異常系を明記: 失敗時の通知/ログ/リカバリ手順/次アクションをACまたは例外仕様として追記する")

    if not hints:
        if r:
            return "reason/errorの不足点を要件本文とACに反映し、合否判定が機械的にできる形へ具体化する"
        return "(reason/errorが空) 再評価してreason/errorを取得し、指摘に基づき修正する"

    return " / ".join(hints[:3])


def issue_label(issue_key: str) -> str:
    return {
        "how_mixing": "How混入（技術/実装詳細の混入）",
        "role_ambiguous": "主語（ロール）不明確",
        "ac_gwt": "AC/Given-When-Then不足",
        "observability": "外部観測可能性が弱い",
        "ambiguous_terms": "曖昧語残存",
        "boundaries": "境界条件（数値/範囲）不足",
        "prompt_structure": "手順/形式の欠落（評価手順・出力形式不一致）",
        "context_completeness": "参照不能/用語定義不足（コンテキスト完全性）",
        "derived_from_alignment": "derived_from整合性の問題",
        "traces_to_missing": "traces_to 未整備",
        "schema_compliance": "スキーマ/メタデータ不整合",
        "exceptions": "異常系/失敗時定義不足",
    }.get(issue_key, issue_key)


# ----------------------------
# Priority scoring
# ----------------------------

ISSUE_WEIGHTS: Dict[str, float] = {
    "how_mixing": 3.0,
    "role_ambiguous": 2.0,
    "ac_gwt": 2.0,
    "observability": 1.7,
    "boundaries": 1.5,
    "ambiguous_terms": 1.5,
    "prompt_structure": 1.2,
    "context_completeness": 2.0,
    "derived_from_alignment": 2.0,
    "traces_to_missing": 2.0,
    "schema_compliance": 1.2,
    "exceptions": 1.2,
}


def metric_base_shortfall(score: Any, threshold: Any, passed: bool) -> float:
    if passed:
        return 0.0
    if threshold is None:
        return 0.5
    if score is None:
        try:
            return max(0.0, float(threshold) - 0.0)
        except Exception:
            return 0.5
    try:
        return max(0.0, float(threshold) - float(score))
    except Exception:
        return 0.5


def metric_weight_from_issues(issues: List[DetectedIssue]) -> float:
    if not issues:
        return 1.0
    return max(ISSUE_WEIGHTS.get(i.key, 1.0) for i in issues)


def requirement_priority(failed_metrics: List[Dict[str, Any]]) -> float:
    return sum(m.get("priority_score", 0.0) for m in failed_metrics)


# ----------------------------
# v2 Triage / Backlog helpers
# ----------------------------

S_KEYS = {"how_mixing", "role_ambiguous", "ac_gwt", "context_completeness", "derived_from_alignment", "traces_to_missing"}
A_KEYS = {"ambiguous_terms", "boundaries", "observability", "prompt_structure", "schema_compliance", "exceptions"}


def triage_priority_label(has_runtime_only: bool, issue_keys: Iterable[str], checklist_item_ids: Iterable[str], priority_score: float) -> str:
    if has_runtime_only:
        return "R"
    keys = set(issue_keys)
    ids = set([x for x in checklist_item_ids if x])
    s_ids = {"CHK-02-02", "CHK-02-03", "CHK-03-02", "CHK-04-02", "CHK-05-02", "CHK-05-03"}

    label = "B"
    if (keys & S_KEYS) or (ids & s_ids):
        label = "S"
    elif keys & A_KEYS:
        label = "A"

    if priority_score >= 1.5:
        if label == "B":
            label = "A"
        elif label == "A":
            label = "S"
    return label


def grounding_status_from_signals(has_reason_or_error: bool, has_chk_id: bool, has_detected_issue: bool) -> Tuple[str, str, bool]:
    if not has_reason_or_error:
        return ("MISSING", "reason/errorが空（再評価が必要）", True)
    if has_chk_id or has_detected_issue:
        return ("OK", "", False)
    return ("MISSING", "reason/errorにチェックリストIDも検出語も無く、機械分類できない", True)


# ----------------------------
# Renderers
# ----------------------------

def render_summary_md(
    eval_data: Dict[str, Any],
    metric_avgs: Dict[str, Any],
    pattern_counts: List[Tuple[str, int]],
    top10: List[Dict[str, Any]],
    runtime_issue_count: int,
    coverage_notes: List[str],
    coverage_overall_evidence: str,
    unmapped_checklist_item_count: int,
) -> str:
    summary = eval_data.get("summary", {}) or {}

    def as_num(v: Any) -> float:
        try:
            return float(v)
        except Exception:
            return -1.0

    low5 = sorted(metric_avgs.items(), key=lambda kv: as_num(kv[1]))[:5]

    lines: List[str] = []
    lines.append("# Deep Eval Summary\n")
    lines.append("## 全体サマリ\n")
    lines.append(f"- total_test_cases: {summary.get('total_test_cases')}")
    lines.append(f"- passed: {summary.get('passed')}")
    lines.append(f"- failed: {summary.get('failed')}")
    lines.append(f"- pass_rate: {summary.get('pass_rate')}")
    lines.append(f"- total_requirements_evaluated: {summary.get('total_requirements_evaluated')}")
    lines.append(f"- runtime_issues (timeout/cancelled): {runtime_issue_count}\n")

    lines.append("### メトリクス平均\n")
    for k, v in metric_avgs.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("### 特に低い項目トップ5（平均スコア）\n")
    for k, v in low5:
        lines.append(f"- {k}: {v}")
    lines.append("")

    if coverage_notes:
        lines.append("## 企画→要件 網羅性（coverage）が低い/0.0 の場合の要約\n")
        if coverage_overall_evidence:
            lines.append(f"- evidence (reason/error抜粋): {short_text(coverage_overall_evidence, 360)}")
        for n in coverage_notes:
            lines.append(f"- {n}")
        lines.append("")

    if unmapped_checklist_item_count > 0:
        lines.append("## チェックリスト項目IDへのマッピングについて\n")
        lines.append(f"- checklist_item_id を機械的に決定できない行が {unmapped_checklist_item_count} 件ありました。")
        lines.append("- reason/error内にCHK-IDが含まれず、かつ検出語（How混入/主語不明/AC不足等）も見つからない場合は空欄としています。\n")

    lines.append("## 低スコア要因（reason/error由来の頻出パターン）\n")
    for label, cnt in pattern_counts[:20]:
        lines.append(f"- {label}: {cnt}")
    lines.append("")

    lines.append("## “最優先で直すべき10件”（timeout由来を除外したランキング）\n")
    lines.append("> 注: ランキングは、失敗メトリクスの閾値未達度と、reason/errorから抽出したパターン（How混入/主語不明等）の重みを合成して算出。\n")
    for i, item in enumerate(top10, start=1):
        lines.append(f"### {i}. {item['requirement_id']} ({item['source_file']})")
        lines.append(f"- priority_score: {item['priority_score']:.3f}")
        lines.append(f"- worst_metrics: {', '.join(item['worst_metrics'])}")
        lines.append(f"- patterns: {', '.join(item['patterns'])}")
        lines.append(f"- evidence (reason/error抜粋): {item['evidence']}\n")

    return "\n".join(lines).rstrip() + "\n"


def render_action_plan_md(pattern_counts: List[Tuple[str, int]], reports_dir: Path) -> str:
    top_patterns = ", ".join([f"{lbl}({cnt})" for lbl, cnt in pattern_counts[:8]])
    lines: List[str] = []
    lines.append("# Deep Eval Action Plan (1 week)\n")
    lines.append("## 根拠（reason/error集計；timeout由来はEに切り分け）\n")
    lines.append(f"- Top patterns: {top_patterns}\n" if top_patterns else "- Top patterns: (なし)\n")

    lines.append("## Day0: runtime issue 切り分け（timeout/cancelled）")
    lines.append(f"- {reports_dir.as_posix()}/deep_eval_runtime_issues.md を確認")
    lines.append("- 必要なら timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）、対象分割、入力短縮で再評価\n")

    lines.append("## Day1: How混入除去ルール化（最優先）")
    lines.append("- 技術固有語（SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等）を要件文から排除")
    lines.append("- 置換方針: ‘手段’→‘外部から観測できる結果（表示/出力/通知/永続性）’\n")

    lines.append("## Day2: ロール主語の統一（user/admin/viewer/system）")
    lines.append("- reason/errorで『主語不明/誰が/許可ロール』が指摘された要件を優先")
    lines.append("- 主語を必ず user/admin/viewer/system のいずれかに正規化\n")

    lines.append("## Day3: ACをGiven-When-Thenで最低1件付与")
    lines.append("- When（トリガー）とThen（合否判定）を一意にし、テストケース化できる形へ\n")

    lines.append("## Day4: 境界条件の数値化（上限/時間/件数/閾値）")
    lines.append("- reason/errorで不足指摘された境界条件（件数/時間/サイズ/保持期間/閾値/タイムアウト）をACに追記")
    lines.append("- 曖昧語（適切に/等/リアルタイム等）を数値・条件に置換\n")

    lines.append("## Day5: coverage/traceability 改善（企画↔要件 対応付け）")
    lines.append("- 企画項目（PLN-*）→要件（REQ-*）の対応表を作成（不足/重複/不要/粒度違いを分類）")
    lines.append("- derived_from を企画IDへ揃え、traces_to を空にしない（設計/テストIDへ接続）\n")

    lines.append("## Day6: 再評価→差分確認")
    lines.append("- Deep Evalを再実行し、deep_eval_findings.csv の差分で改善/悪化を確認\n")

    lines.append("## Day7: 回帰防止（テンプレ・ルールの固定）")
    lines.append("- deep_eval_patch_suggestions.md のテンプレ/機械ルールをレビュー観点とCIに組み込み\n")

    return "\n".join(lines).rstrip() + "\n"


def render_patch_suggestions_md() -> str:
    lines: List[str] = []
    lines.append("# Deep Eval Patch Suggestions\n")
    lines.append("## 修正テンプレ（What/Why/AC/GWT/Not-How/Role/Boundaries/Errors/Trace）\n")
    lines.append(
        "```yaml\n"
        "req_id: REQ-...\n"
        "title: ...\n"
        "target_role: system  # user/admin/viewer/system のいずれか\n"
        "description: |\n"
        "  # What: 外部から観測できる結果で書く\n"
        "  # Not-How: DB/ライブラリ/フレームワーク/CI/CD等の手段は書かない\n"
        "rationale: |\n"
        "  # Why: 企画目的（構造化/可視化/検証可能化）への貢献を明記\n"
        "acceptance_criteria:\n"
        "  - criterion: |\n"
        "      Given ...\n"
        "      When ...\n"
        "      Then ...\n"
        "    verification_method: テスト\n"
        "boundaries:\n"
        "  # 例: max_items, timeout_seconds, retention_days, response_time_ms など\n"
        "exceptions:\n"
        "  # 失敗時の通知/表示/ログ/次アクション\n"
        "trace:\n"
        "  derived_from: PLN-...\n"
        "  traces_to: [DES-..., TST-...]\n"
        "```\n"
    )

    lines.append("## よくあるNG→OK言い換え例（10個）\n")
    examples = [
        ("システムはSQLiteに保存する", "system はデータを永続化し、再起動後も同一データを参照できる"),
        ("node-cronで深夜2時に実行する", "system は毎日 02:00（JST）に処理を開始し、完了/失敗を外部から確認できる"),
        ("React Flow形式で生成する", "system はフロー図データを構造化形式で出力し、再構築可能である"),
        ("GitHub ActionsでCI/CDを構築する", "system は自動検証を実行し、検証結果（PASS/FAILと理由）を出力する"),
        ("ajvでスキーマ検証する", "system は成果物が規定スキーマに適合するか検証し、不適合時は違反箇所と修正ガイドを返す"),
        ("モード設定はlocalStorageに保存される", "user の設定は次回起動後も維持され、user が再設定せずに同一設定で開始できる"),
        ("全機能がキーボードショートカットで操作できる", "user は主要操作（対象を列挙）をショートカットで実行でき、成功/失敗が画面に表示される"),
        ("即座に切り替わる", "切替操作から 300ms 以内に表示状態が更新される"),
        ("管理できる/参照できる", "user が一覧画面で対象を検索し、選択すると詳細が表示される（表示項目を列挙）"),
        ("設計ドキュメントに記録する", "system は変更履歴（日時/変更者/変更内容）を出力し、第三者が差分を確認できる"),
    ]
    for i, (ng, ok) in enumerate(examples, start=1):
        lines.append(f"{i}. NG: 「{ng}」")
        lines.append(f"   OK: 「{ok}」\n")

    lines.append("## 修正の『機械ルール』（重要ルール準拠）\n")
    rules = [
        "How混入は最優先: SQLite/node-cron/React/ajv/GitHub Actions/Allure/Promptfoo/localStorage 等の技術語が出たら ‘観測可能な結果’ に言い換える",
        "主語は user/admin/viewer/system に統一し、曖昧主語（ユーザー/第三者/判断者等）は正規化する",
        "acceptance_criteria は1件以上。Given/When/Then を揃え、Then に合否判定可能な結果を書く",
        "曖昧語（適切に/等/リアルタイム等）を検出したら数値・条件に置換する",
        "境界条件（件数/時間/サイズ/保持/閾値）が不足と指摘されたらACに数値で追記する",
        "derived_from/traces_to を整備し、参照不能/未定義が出たら本文内定義 or 参照先明記で解消する",
        "異常系（失敗時の通知/ログ/リカバリ/次アクション）を明記する",
    ]
    for r in rules:
        lines.append(f"- {r}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_runtime_issues_md(runtime_issues: List[RuntimeIssue]) -> str:
    lines: List[str] = []
    lines.append("# Deep Eval Runtime Issues (timeout/cancelled)\n")
    if not runtime_issues:
        lines.append("- runtime issues は検出されませんでした。\n")
        return "\n".join(lines)

    lines.append("## 一覧（要件修正の優先順位から除外）\n")
    lines.append("> 注: ここは要件品質ではなく、評価実行条件に起因する問題の切り分け専用です。\n")
    for i, ri in enumerate(runtime_issues, start=1):
        lines.append(f"### {i}. {ri.requirement_id} ({ri.source_file}) / {ri.metric_name}\n")
        if ri.error:
            lines.append(f"- error: {short_text(ri.error, 420)}")
        if ri.reason:
            lines.append(f"- reason: {short_text(ri.reason, 420)}")
        if (not ri.reason) and (not ri.error):
            lines.append("- (reason/errorが空)")
        lines.append("- 対処案: timeout延長（DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE）/対象分割/入力短縮/DEEPEVAL_LOG_STACK_TRACES=1\n")

    lines.append("## 再実行の対処案（一般）\n")
    lines.append("- 評価のtimeoutを延長する（特にLLM呼び出しや長文入力がある場合）")
    lines.append("- 対象要件を分割して評価する（バッチサイズを下げる）")
    lines.append("- 1要件あたりの入力（企画書/背景等）を短縮し、参照箇所を絞る")
    lines.append("- 同一要件で特定metricのみtimeoutする場合、そのmetricのプロンプトを簡素化する\n")
    return "\n".join(lines).rstrip() + "\n"


# ----------------------------
# CSV writers
# ----------------------------

CSV_FIELDS = [
    "requirement_id", "source_file", "doc_id",
    "metric_name", "score", "threshold", "passed",
    "reason", "error", "fix_hint",
    "checklist_category", "checklist_item_id",
    "is_timeout_related", "priority_score",
]

BACKLOG_FIELDS = [
    "requirement_id", "source_file", "doc_id",
    "priority", "priority_score",
    "primary_pattern", "patterns",
    "checklist_item_ids", "checklist_categories",
    "metrics_failed", "evidence", "merged_fix_hint",
    "runtime_issue_count",
    "grounding_status", "grounding_notes", "needs_human_review",
]


def write_csv(rows: List[Dict[str, Any]], out_path: Path, fields: List[str]) -> None:
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def render_triage_summary_md(
    reports_dir: Path,
    backlog_rows: List[Dict[str, Any]],
    pattern_counts: List[Tuple[str, int]],
    missing_grounding_examples: List[Dict[str, Any]],
) -> str:
    total = len(backlog_rows)
    by_pri: Dict[str, int] = {"S": 0, "A": 0, "B": 0, "R": 0}
    by_file: Dict[str, int] = {}
    missing = 0
    human = 0

    for r in backlog_rows:
        p = (r.get("priority") or "").strip()
        if p in by_pri:
            by_pri[p] += 1
        sf = (r.get("source_file") or "").strip()
        if sf:
            by_file[sf] = by_file.get(sf, 0) + 1
        if (r.get("grounding_status") or "") == "MISSING":
            missing += 1
        if (r.get("needs_human_review") or "") == "true":
            human += 1

    top_files = sorted(by_file.items(), key=lambda kv: kv[1], reverse=True)[:10]

    lines: List[str] = []
    lines.append("# Deep Eval Triage Summary (v2)\n")
    lines.append(f"- reports_dir: {reports_dir.as_posix()}")
    lines.append(f"- backlog_total_requirements: {total}")
    lines.append(f"- priority_counts: S={by_pri['S']}, A={by_pri['A']}, B={by_pri['B']}, R={by_pri['R']}")
    lines.append(f"- grounding_missing_count: {missing}")
    lines.append(f"- needs_human_review_count: {human}\n")

    lines.append("## 優先度ルール（機械付与）\n")
    lines.append("- R: timeout/cancelled 等の評価実行条件起因（要件修正では解けない）")
    lines.append("- S: 仕様/テスト成立に直結（How混入、主語不明、AC不足、参照不能、トレーサビリティ欠落 等）")
    lines.append("- A: 品質改善（曖昧語、境界条件不足、外部観測不足、形式不足 等）")
    lines.append("- B: 上記以外（軽微/局所）\n")

    lines.append("## 低スコア要因（reason/error由来；timeout除外）\n")
    for label, cnt in pattern_counts[:15]:
        lines.append(f"- {label}: {cnt}")
    lines.append("")

    lines.append("## source_file 別（着手の目安）\n")
    for sf, cnt in top_files:
        lines.append(f"- {sf}: {cnt}")
    lines.append("")

    if missing_grounding_examples:
        lines.append("## 根拠シグナル不足（MISSING）の例（人手精査キュー）\n")
        for ex in missing_grounding_examples[:10]:
            lines.append(f"- {ex.get('requirement_id')} ({ex.get('source_file')}): {ex.get('grounding_notes')}")
            ev = ex.get("evidence") or ""
            if ev:
                lines.append(f"  - evidence: {ev}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ----------------------------
# Main
# ----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Deep Eval reports under reports/ (v2; no source modifications).")
    p.add_argument("--eval-json", type=Path, default=DEFAULT_EVAL_JSON_PATH)
    p.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST_PATH)
    p.add_argument("--req-dir", type=Path, default=DEFAULT_REQ_DIR)
    p.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dir(args.reports_dir)

    eval_data = load_json(args.eval_json)
    checklist = load_yaml(args.checklist)
    checklist_idx = build_checklist_index(checklist)
    req_idx = build_requirement_index(args.req_dir)

    test_results = eval_data.get("test_results", []) or []

    findings_rows: List[Dict[str, Any]] = []
    runtime_issues: List[RuntimeIssue] = []
    pattern_freq: Dict[str, int] = {}
    unmapped_checklist_item_count = 0

    # requirement-level aggregation for backlog
    per_req_failed_metric_rows: Dict[str, List[Dict[str, Any]]] = {}
    per_req_patterns: Dict[str, List[str]] = {}
    per_req_issue_keys: Dict[str, List[str]] = {}
    per_req_checklist_ids: Dict[str, List[str]] = {}
    per_req_checklist_cats: Dict[str, List[str]] = {}
    per_req_evidence: Dict[str, str] = {}
    per_req_fix_hints: Dict[str, List[str]] = {}
    per_req_failed_metrics: Dict[str, List[str]] = {}
    per_req_source: Dict[str, Tuple[str, str]] = {}
    per_req_runtime_count: Dict[str, int] = {}
    per_req_has_chk_signal: Dict[str, bool] = {}
    per_req_has_issue_signal: Dict[str, bool] = {}
    per_req_has_reason_error: Dict[str, bool] = {}

    # coverage evidence grounded from OVERALL reason/error
    coverage_overall_evidence = ""
    for tr in test_results:
        if _safe_str(tr.get("requirement_id")) != "OVERALL":
            continue
        for mm in (tr.get("metrics") or []):
            if _safe_str(mm.get("name")) == "全体網羅性（企画→要件） [GEval]":
                coverage_overall_evidence = _safe_str(mm.get("reason")) or _safe_str(mm.get("error"))

    for tr in test_results:
        requirement_id = _safe_str(tr.get("requirement_id"))
        source_file = _safe_str(tr.get("source_file"))
        doc_id = _safe_str(tr.get("doc_id"))

        if requirement_id and (not source_file or not doc_id) and requirement_id in req_idx:
            source_file = source_file or _safe_str(req_idx[requirement_id].get("source_file"))
            doc_id = doc_id or _safe_str(req_idx[requirement_id].get("doc_id"))

        if requirement_id:
            per_req_source[requirement_id] = (source_file, doc_id)

        for m in (tr.get("metrics") or []):
            metric_name = _safe_str(m.get("name"))
            score = m.get("score")
            threshold = m.get("threshold")
            passed = bool(m.get("success"))
            reason = _safe_str(m.get("reason"))
            error = _safe_str(m.get("error"))

            reason_or_error = reason if reason else (error if error else "")
            timeout_related = is_timeout_related(reason_or_error)
            issues = detect_issues(reason_or_error)
            primary_item_id = choose_primary_item(issues, reason_or_error)

            checklist_category = ""
            if primary_item_id:
                item = checklist_idx.get(primary_item_id)
                cat_en = (item.category_name_en if item else "")
                cat_map = {
                    "purpose_alignment": "purpose",
                    "scope_validity": "scope",
                    "verifiability": "verifiability",
                    "ai_readability": "ai_readability",
                    "traceability": "traceability",
                    "schema_compliance": "schema",
                    "operational_consideration": "operational",
                }
                checklist_category = cat_map.get(cat_en, "")
            else:
                unmapped_checklist_item_count += 1

            base = metric_base_shortfall(score, threshold, passed)
            weight = metric_weight_from_issues(issues)
            metric_priority = 0.0 if timeout_related else (base * weight)

            if not timeout_related:
                for iss in issues:
                    pattern_freq[iss.key] = pattern_freq.get(iss.key, 0) + 1

            fix_hint = fix_hint_from(reason_or_error, issues)

            row = {
                "requirement_id": requirement_id,
                "source_file": source_file,
                "doc_id": doc_id,
                "metric_name": metric_name,
                "score": "" if score is None else score,
                "threshold": "" if threshold is None else threshold,
                "passed": passed,
                "reason": reason,
                "error": error,
                "fix_hint": fix_hint,
                "checklist_category": checklist_category,
                "checklist_item_id": primary_item_id,
                "is_timeout_related": "true" if timeout_related else "false",
                "priority_score": round(metric_priority, 6),
            }
            if (not row["reason"]) and (not row["error"]):
                row["error"] = "(reason/error both empty in eval json)"
            findings_rows.append(row)

            if requirement_id:
                if reason or error:
                    per_req_has_reason_error[requirement_id] = True
                if re.search(r"\bCHK-\d{2}-\d{2}\b", reason_or_error or ""):
                    per_req_has_chk_signal[requirement_id] = True
                if issues:
                    per_req_has_issue_signal[requirement_id] = True

            if timeout_related and (not passed):
                runtime_issues.append(
                    RuntimeIssue(
                        requirement_id=requirement_id,
                        source_file=source_file,
                        doc_id=doc_id,
                        metric_name=metric_name,
                        reason=reason,
                        error=error,
                    )
                )
                if requirement_id:
                    per_req_runtime_count[requirement_id] = per_req_runtime_count.get(requirement_id, 0) + 1

            if requirement_id and (not passed) and (not timeout_related):
                per_req_failed_metric_rows.setdefault(requirement_id, []).append(
                    {
                        "metric_name": metric_name,
                        "score": score,
                        "threshold": threshold,
                        "success": passed,
                        "reason_or_error": reason_or_error,
                        "priority_score": metric_priority,
                        "issues": [i.key for i in issues],
                    }
                )
                per_req_patterns.setdefault(requirement_id, []).extend([issue_label(i.key) for i in issues])
                per_req_issue_keys.setdefault(requirement_id, []).extend([i.key for i in issues])
                if primary_item_id:
                    per_req_checklist_ids.setdefault(requirement_id, []).append(primary_item_id)
                if checklist_category:
                    per_req_checklist_cats.setdefault(requirement_id, []).append(checklist_category)
                per_req_failed_metrics.setdefault(requirement_id, []).append(metric_name)
                if fix_hint:
                    per_req_fix_hints.setdefault(requirement_id, []).append(fix_hint)
                if requirement_id not in per_req_evidence and reason_or_error:
                    per_req_evidence[requirement_id] = short_text(reason_or_error, 220)

    summary = eval_data.get("summary", {}) or {}
    metric_avgs = (summary.get("metric_averages", {}) or {})

    coverage_notes: List[str] = []
    for k, v in metric_avgs.items():
        name = str(k)
        try:
            val = float(v)
        except Exception:
            continue
        if ("網羅" in name) or ("coverage" in name.lower()):
            if val <= 0.05:
                coverage_notes.append(
                    f"{name} が {val} です。要件の書き方だけでなく、企画項目→要件の対応付け（不足/重複/不要/粒度違い）不足として別枠で整理してください。"
                )
            elif val <= 0.2:
                coverage_notes.append(f"{name} が低め（{val}）です。企画項目→要件の対応表と traces_to 整備を推奨します。")

    pattern_counts_sorted = sorted(
        [(issue_label(k), v) for k, v in pattern_freq.items()],
        key=lambda kv: kv[1],
        reverse=True,
    )

    # Top10 (timeout excluded already)
    req_rank: List[Dict[str, Any]] = []
    for req_id, rows in per_req_failed_metric_rows.items():
        source_file, _doc_id = per_req_source.get(req_id, ("", ""))
        priority = requirement_priority(rows)
        worst = sorted(
            rows,
            key=lambda x: metric_base_shortfall(x.get("score"), x.get("threshold"), x.get("success") is True),
            reverse=True,
        )
        worst_metrics = [w.get("metric_name", "") for w in worst[:3] if w.get("metric_name")]
        patterns = per_req_patterns.get(req_id, []) or []
        req_rank.append(
            {
                "requirement_id": req_id,
                "source_file": source_file,
                "priority_score": float(priority),
                "worst_metrics": worst_metrics,
                "patterns": patterns[:6],
                "evidence": per_req_evidence.get(req_id, ""),
            }
        )
    top10 = sorted(req_rank, key=lambda x: x["priority_score"], reverse=True)[:10]

    # Fix backlog (requirement-level triage)
    backlog_rows: List[Dict[str, Any]] = []
    missing_examples: List[Dict[str, Any]] = []

    all_req_ids = set(per_req_source.keys()) | set(per_req_failed_metric_rows.keys()) | set(per_req_runtime_count.keys())
    for req_id in sorted(all_req_ids):
        source_file, doc_id = per_req_source.get(req_id, ("", ""))
        failed_rows = per_req_failed_metric_rows.get(req_id, []) or []
        runtime_cnt = per_req_runtime_count.get(req_id, 0)
        has_runtime_only = (runtime_cnt > 0) and (len(failed_rows) == 0)

        agg_priority_score = float(requirement_priority(failed_rows)) if failed_rows else 0.0
        issue_keys = per_req_issue_keys.get(req_id, []) or []
        checklist_ids = per_req_checklist_ids.get(req_id, []) or []
        checklist_cats = per_req_checklist_cats.get(req_id, []) or []

        primary_pattern = ""
        if issue_keys:
            primary_key = sorted(set(issue_keys), key=lambda k: (-ISSUE_WEIGHTS.get(k, 0.0), k))[0]
            primary_pattern = issue_label(primary_key)
        else:
            pats = per_req_patterns.get(req_id, []) or []
            primary_pattern = pats[0] if pats else ("runtime_issue" if runtime_cnt > 0 else "")

        priority_label = triage_priority_label(has_runtime_only, issue_keys, checklist_ids, agg_priority_score)

        has_reason_error = bool(per_req_has_reason_error.get(req_id, False))
        has_chk_signal = bool(per_req_has_chk_signal.get(req_id, False))
        has_issue_signal = bool(per_req_has_issue_signal.get(req_id, False))
        grounding_status, grounding_notes, needs_human = grounding_status_from_signals(
            has_reason_error, has_chk_signal, has_issue_signal
        )

        merged_fix_hint = join_uniq(per_req_fix_hints.get(req_id, [])[:6], sep=" / ")

        row = {
            "requirement_id": req_id,
            "source_file": source_file,
            "doc_id": doc_id,
            "priority": priority_label,
            "priority_score": round(agg_priority_score, 6),
            "primary_pattern": primary_pattern,
            "patterns": join_uniq(per_req_patterns.get(req_id, []) or []),
            "checklist_item_ids": join_uniq(checklist_ids),
            "checklist_categories": join_uniq(checklist_cats),
            "metrics_failed": join_uniq(per_req_failed_metrics.get(req_id, []) or []),
            "evidence": per_req_evidence.get(req_id, ""),
            "merged_fix_hint": merged_fix_hint,
            "runtime_issue_count": runtime_cnt,
            "grounding_status": grounding_status,
            "grounding_notes": grounding_notes,
            "needs_human_review": "true" if needs_human else "false",
        }
        backlog_rows.append(row)
        if grounding_status == "MISSING":
            missing_examples.append(row)

    # Write outputs
    write_csv(findings_rows, args.reports_dir / "deep_eval_findings.csv", CSV_FIELDS)
    write_csv(backlog_rows, args.reports_dir / "deep_eval_fix_backlog.csv", BACKLOG_FIELDS)

    (args.reports_dir / "deep_eval_summary.md").write_text(
        render_summary_md(
            eval_data=eval_data,
            metric_avgs=metric_avgs,
            pattern_counts=pattern_counts_sorted,
            top10=top10,
            runtime_issue_count=len(runtime_issues),
            coverage_notes=coverage_notes,
            coverage_overall_evidence=coverage_overall_evidence,
            unmapped_checklist_item_count=unmapped_checklist_item_count,
        ),
        encoding="utf-8",
    )
    (args.reports_dir / "deep_eval_action_plan.md").write_text(
        render_action_plan_md(pattern_counts_sorted, args.reports_dir),
        encoding="utf-8",
    )
    (args.reports_dir / "deep_eval_patch_suggestions.md").write_text(
        render_patch_suggestions_md(),
        encoding="utf-8",
    )
    (args.reports_dir / "deep_eval_runtime_issues.md").write_text(
        render_runtime_issues_md(runtime_issues),
        encoding="utf-8",
    )
    (args.reports_dir / "deep_eval_triage_summary.md").write_text(
        render_triage_summary_md(
            reports_dir=args.reports_dir,
            backlog_rows=backlog_rows,
            pattern_counts=pattern_counts_sorted,
            missing_grounding_examples=missing_examples,
        ),
        encoding="utf-8",
    )

    # Self-checks (stdout)
    timeout_re = re.compile(
        r"timeout|timed out|cancelled|canceled|context deadline|deadline exceeded|タイムアウト|時間切れ|キャンセル",
        re.I,
    )
    top10_has_timeout = any(timeout_re.search((t.get("evidence") or "")) for t in top10)
    print("[SELF-CHECK]")
    print(f"- E_runtime_issues_count: {len(runtime_issues)}")
    print(f"- A_top10_excludes_timeout: {'OK' if (not top10_has_timeout) else 'NG'}")
    print(f"- F_fix_backlog_exists: OK")
    print(f"- G_triage_summary_exists: OK")

    print("[OK] Generated reports:")
    for p in [
        args.reports_dir / "deep_eval_summary.md",
        args.reports_dir / "deep_eval_findings.csv",
        args.reports_dir / "deep_eval_action_plan.md",
        args.reports_dir / "deep_eval_patch_suggestions.md",
        args.reports_dir / "deep_eval_runtime_issues.md",
        args.reports_dir / "deep_eval_fix_backlog.csv",
        args.reports_dir / "deep_eval_triage_summary.md",
    ]:
        print(f"- {p.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
