"""
evaluate_req_vs_planning_v1.py
==============================
要件定義書（requirements/yaml/requirements_v1/）が
  1. 企画書（planning/yaml/planning_v2.2/）の内容に対して妥当か
  2. チェックリスト（checklist/checklist.yaml）に則っているか
をDeep Evalで評価するスクリプト。

評価メトリクス（要件1件ごと）:
  - FaithfulnessMetric      : 要件が企画書の記述に根拠を持つか（幻覚検出）
  - GEval[企画整合性]       : 企画の目的・方針・制約との整合（CHK-01-01, CHK-01-02相当）
  - GEval[スコープ適切性]   : How非混入 + フェーズ適切性（CHK-02-01, CHK-02-02, CHK-02-03相当）
  - GEval[検証可能性]       : 受入基準・曖昧語・境界条件（CHK-03-01〜04相当, 最重要 weight=2.0）
  - GEval[AI可読性]         : プロンプト構造化度・コンテキスト完全性（CHK-04-01〜03相当）

評価メトリクス（全体1件）:
  - GEval[全体網羅性]       : 企画書の重要要素が要件に落ちているか

出力:
  deepeval/output/eval_req_vs_planning_v1.json

実行例（逐次＋timeout延長）:
  python deepeval/evaluate_req_vs_planning_v1.py --no-async --timeout-seconds 600

環境変数:
  OPENAI_API_KEY  : OpenAI APIキー（必須）
  DEEPEVAL_MODEL  : 使用モデル（省略時: gpt-4o）
"""

from __future__ import annotations

import argparse
import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ---- DeepEval imports（バージョン差吸収） ----
try:
    from deepeval import evaluate
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
except Exception as e:
    raise SystemExit(f"DeepEval import failed. `pip install deepeval` を確認してください。Error: {e}")

HallucinationMetric = None
FaithfulnessMetric = None
GEval = None

_import_errors: list = []

for _cand in [
    ("deepeval.metrics", "HallucinationMetric", "FaithfulnessMetric", "GEval"),
    ("deepeval.metrics.hallucination", "HallucinationMetric", None, None),
    ("deepeval.metrics.faithfulness", "FaithfulnessMetric", None, None),
    ("deepeval.metrics.g_eval", "GEval", None, None),
]:
    try:
        mod = __import__(_cand[0], fromlist=["*"])
        if _cand[1] and HallucinationMetric is None:
            HallucinationMetric = getattr(mod, _cand[1], None)
        if _cand[2] and FaithfulnessMetric is None:
            FaithfulnessMetric = getattr(mod, _cand[2], None)
        if _cand[3] and GEval is None:
            GEval = getattr(mod, _cand[3], None)
    except Exception as e:
        _import_errors.append(str(e))

if FaithfulnessMetric is None or GEval is None:
    raise SystemExit(
        "DeepEval metric imports に失敗しました。\n"
        f"FaithfulnessMetric={FaithfulnessMetric}, GEval={GEval}\n"
        f"Errors: {_import_errors}"
    )

# ---- パス定義 ----
ROOT = Path(__file__).resolve().parents[1]
PLANNING_DIR = ROOT / "planning" / "yaml" / "planning_v2.2"
REQUIREMENTS_DIR = ROOT / "requirements" / "yaml" / "requirements_v1"
CHECKLIST_YAML = ROOT / "checklist" / "checklist.yaml"
OUT_JSON = ROOT / "deepeval" / "output" / "eval_req_vs_planning_v1.json"

# ---- 設定（デフォルトは“安定優先”）----
# ★並列しない：デフォルト逐次
ASYNC_MODE = False
MAX_CONCURRENCY = 1

FAITHFULNESS_THRESHOLD = 0.5
GEVAL_THRESHOLD = 0.5    # GEvalはスコア0-1、0.5以上で合格

# ---- 入力サイズ上限（timeout対策）----
MAX_PLANNING_FULL_CHARS = 4000   # OVERALL の planning input 上限（長すぎるとtimeoutしやすい）
MAX_CHECKLIST_CHARS = 4000       # checklist_summary 上限
MAX_CONTEXT_CHARS = 2000         # per-req planning_ctx フォールバック上限

# ---- DeepEval timeout override（環境変数名）----
DEEPEVAL_TIMEOUT_ENV = "DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE"


# ===========================================================================
# データ構造
# ===========================================================================

@dataclass
class PlanningItem:
    """企画書のアイテム1件"""
    item_id: str          # PLN-PLN-SYS_LAYERS-001 など
    section_id: str       # PLN-PLN-SYS-006 など
    section_title: str
    item_type: str        # statement / table / decision_rule など
    title: str
    content: str

    def to_text(self) -> str:
        return (
            f"[企画書セクション] {self.section_id}: {self.section_title}\n"
            f"[項目ID] {self.item_id}\n"
            f"[種別] {self.item_type}\n"
            f"[タイトル] {self.title}\n"
            f"[内容]\n{self.content}"
        )


@dataclass
class Requirement:
    """要件1件（機能・非機能共通）"""
    req_id: str
    req_type: str         # functional / non_functional
    category: str
    priority: str
    title: str
    description: str
    rationale: str
    acceptance_criteria: List[Dict[str, str]]
    assumptions: List[str]
    risks: List[Dict[str, Any]]
    derived_from: Any     # str or list
    traces_to: Any
    dependencies: List[str]
    notes: str
    source_file: str      # どのYAMLファイルから来たか
    doc_id: str           # 要件ドキュメントID
    doc_derived_from: str  # ドキュメントレベルのderived_from（企画書セクションID）

    def to_text(self) -> str:
        """評価プロンプト用テキスト表現"""
        ac_text = "\n".join(
            f"  - {c.get('criterion', c) if isinstance(c, dict) else c}"
            + (f" [検証: {c.get('verification_method', '')}]" if isinstance(c, dict) and c.get('verification_method') else "")
            for c in (self.acceptance_criteria or [])
        ) or "  (なし)"

        risks_text = "\n".join(
            f"  - {r.get('risk_description', r)}"
            + (f" [確率:{r.get('probability','')} 影響:{r.get('impact','')}]" if isinstance(r, dict) else "")
            for r in (self.risks or [])
        ) or "  (なし)"

        derived_str = (
            ", ".join(self.derived_from) if isinstance(self.derived_from, list)
            else str(self.derived_from or "(なし)")
        )
        traces_str = (
            ", ".join(self.traces_to) if isinstance(self.traces_to, list)
            else str(self.traces_to or "(なし)")
        )

        return (
            f"【要件ID】{self.req_id}\n"
            f"【種別】{self.req_type} | 【カテゴリ】{self.category} | 【優先度】{self.priority}\n"
            f"【タイトル】{self.title}\n"
            f"【説明】\n{self.description.strip()}\n"
            f"【根拠（rationale）】\n{self.rationale or '(なし)'}\n"
            f"【受入基準（acceptance_criteria）】\n{ac_text}\n"
            f"【前提条件（assumptions）】\n{chr(10).join('  - ' + str(a) for a in (self.assumptions or [])) or '  (なし)'}\n"
            f"【リスク】\n{risks_text}\n"
            f"【上流参照（derived_from）】{derived_str}\n"
            f"【下流追跡（traces_to）】{traces_str}\n"
            f"【備考】{self.notes or '(なし)'}"
        )


# ===========================================================================
# データ読み込み
# ===========================================================================

def load_yaml_safe(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_planning_items(planning_dir: Path) -> Tuple[List[PlanningItem], str]:
    """
    planning/yaml/planning_v2.2/ 以下の全YAMLを読み込み、
    PlanningItemのリストと全体テキスト（網羅性評価用）を返す。
    """
    items: List[PlanningItem] = []
    all_text_parts: List[str] = []

    yaml_files = sorted(planning_dir.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"企画書YAMLが見つかりません: {planning_dir}")

    for f in yaml_files:
        if f.name.startswith("00_"):
            # インデックスファイルはスキップ
            continue
        data = load_yaml_safe(f)
        section = data.get("section", {})
        section_id = section.get("id", "")
        section_title = section.get("title", "")

        for raw_item in (section.get("items") or []):
            item_id = raw_item.get("id", "")
            content_val = raw_item.get("content", "")
            content_str = (
                yaml.safe_dump(content_val, allow_unicode=True).strip()
                if not isinstance(content_val, str)
                else content_val
            )
            pi = PlanningItem(
                item_id=item_id,
                section_id=section_id,
                section_title=section_title,
                item_type=raw_item.get("type", ""),
                title=raw_item.get("title", ""),
                content=content_str,
            )
            items.append(pi)
            all_text_parts.append(pi.to_text())

    return items, "\n\n---\n\n".join(all_text_parts)


def build_planning_index(items: List[PlanningItem]) -> Dict[str, PlanningItem]:
    """item_id → PlanningItem のインデックスを構築"""
    return {pi.item_id: pi for pi in items}


def extract_requirements_from_yaml(data: Dict[str, Any], source_file: str) -> List[Requirement]:
    """要件YAMLから Requirement のリストを生成"""
    reqs: List[Requirement] = []
    doc = data.get("requirements_document", {})
    doc_id = doc.get("doc_id", "")
    doc_derived_from = doc.get("derived_from", "")

    def parse_req_list(raw_list: Optional[List], req_type: str) -> None:
        for r in (raw_list or []):
            if not isinstance(r, dict):
                continue
            reqs.append(
                Requirement(
                    req_id=r.get("req_id", ""),
                    req_type=req_type,
                    category=r.get("category", ""),
                    priority=str(r.get("priority", "")),
                    title=r.get("title", ""),
                    description=str(r.get("description", "")),
                    rationale=str(r.get("rationale", "")),
                    acceptance_criteria=r.get("acceptance_criteria") or [],
                    assumptions=r.get("assumptions") or [],
                    risks=r.get("risks") or [],
                    derived_from=r.get("derived_from"),
                    traces_to=r.get("traces_to"),
                    dependencies=r.get("dependencies") or [],
                    notes=str(r.get("notes", "")),
                    source_file=source_file,
                    doc_id=doc_id,
                    doc_derived_from=str(doc_derived_from),
                )
            )

    parse_req_list(doc.get("functional_requirements"), "functional")
    parse_req_list(doc.get("non_functional_requirements"), "non_functional")
    return reqs


def load_all_requirements(req_dir: Path) -> List[Requirement]:
    """requirements/yaml/requirements_v1/ 以下の全YAMLを読み込み"""
    all_reqs: List[Requirement] = []
    yaml_files = sorted(req_dir.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"要件定義YAMLが見つかりません: {req_dir}")

    for f in yaml_files:
        data = load_yaml_safe(f)
        reqs = extract_requirements_from_yaml(data, f.name)
        all_reqs.extend(reqs)

    return all_reqs


def format_checklist_summary(checklist: Dict[str, Any]) -> str:
    """チェックリストを評価プロンプト用テキストに変換"""
    parts = ["=== AIDD要件妥当性チェックリスト（要約）==="]
    for cat in (checklist.get("categories") or []):
        cat_id = cat.get("id", "")
        cat_name = cat.get("name", "")
        weight = cat.get("weight", 1.0)
        parts.append(f"\n[{cat_id}] {cat_name}（重み: {weight}）")
        for item in (cat.get("items") or []):
            chk_id = item.get("id", "")
            q = item.get("question", "")
            criteria = item.get("eval_criteria", "")
            parts.append(f"  {chk_id}: {q}")
            if criteria:
                criteria_lines = [ln.strip() for ln in criteria.strip().splitlines() if ln.strip()]
                parts.append("    評価基準: " + " / ".join(criteria_lines[:3]))

    parts.append("\n判定閾値: A採用≥0.8 / B将来≥0.5 / C却下<0.5")
    return "\n".join(parts)


def get_planning_context_for_req(
    req: Requirement,
    planning_index: Dict[str, PlanningItem],
    planning_full_text: str,
    max_items: int = 5,
) -> str:
    """
    要件のderived_fromに対応する企画書項目を取得してコンテキストを構築。
    見つからない場合はdoc_derived_fromのセクション情報を全体から抽出。
    """
    found_items: List[str] = []

    derived = req.derived_from
    if isinstance(derived, str) and derived:
        derived_ids = [derived]
    elif isinstance(derived, list):
        derived_ids = [str(d) for d in derived if d]
    else:
        derived_ids = []

    for did in derived_ids:
        pi = planning_index.get(did)
        if pi:
            found_items.append(pi.to_text())

    if not found_items and req.doc_derived_from:
        section_id = req.doc_derived_from
        matching = [pi for pi in planning_index.values() if pi.section_id == section_id]
        for pi in matching[:max_items]:
            found_items.append(pi.to_text())

    if found_items:
        return "\n\n---\n\n".join(found_items)

    # どちらも見つからない場合は全体テキストを縮小して返す（timeout対策）
    return planning_full_text[:MAX_CONTEXT_CHARS] + "\n...(省略)"


# ===========================================================================
# メトリクス定義
# ===========================================================================

def build_per_req_metrics(checklist_summary: str) -> List:
    """要件1件ごとに適用するメトリクスを構築"""
    metrics = []

    faithfulness = FaithfulnessMetric(threshold=FAITHFULNESS_THRESHOLD, include_reason=True)
    metrics.append(faithfulness)

    planning_alignment = GEval(
        name="企画整合性",
        criteria=(
            "あなたは上流工程QAの専門レビュアです。\n"
            "【企画書コンテキスト】（以下、INPUT冒頭に記載）を参照し、【要件】（ACTUAL_OUTPUT）が\n"
            "以下の観点で企画の意図に沿っているか評価してください。\n\n"
            "評価観点:\n"
            "1) 目的貢献: 企画目的（構造化・可視化・検証可能化）に直接貢献しているか\n"
            "2) 必要性: 「ないと成立しない」核心要件か（Nice-to-haveでないか）\n"
            "3) 方針適合: 企画の基本方針・制約（禁止事項・原則）に違反していないか\n"
            "4) 逸脱検出: 企画書に根拠のない要素が含まれていないか\n\n"
            "スコア: 0.0〜1.0（1.0=完全整合、0.5=部分整合、0.0=逸脱）\n"
            "理由: 日本語で具体的に。問題があれば該当箇所を指摘。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(planning_alignment)

    scope_validity = GEval(
        name="スコープ適切性・How非混入",
        criteria=(
            "あなたはAIDD要件定義のスコープレビュアです。【要件】（ACTUAL_OUTPUT）を以下の観点で評価してください。\n\n"
            "評価観点:\n"
            "1) フェーズ適切性: Phase0（MVP）に必須の内容か、Phase1以降に回すべき内容を含まないか\n"
            "2) How非混入（最重要）: 実装詳細が混入していないか（SQLite/node-cron/React等の技術や手段の断定は減点）\n"
            "3) 主語/ロール: user/admin/viewer/system などの主体が明確か\n\n"
            "スコア: 0.0〜1.0\n"
            "理由: 日本語で具体的に。How混入があれば該当語を列挙。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(scope_validity)

    verifiability = GEval(
        name="検証可能性",
        criteria=(
            "あなたはQAの受入基準レビュアです。【要件】（ACTUAL_OUTPUT）を以下の観点で評価してください。\n\n"
            "評価観点:\n"
            "1) 受入基準: acceptance_criteria が存在し、Given/When/Then 形式でテスト可能か\n"
            "2) 曖昧語: 「適切に」「等」「リアルタイム」など曖昧語が残っていないか\n"
            "3) 境界条件: 上限/閾値/保持期間/時間等が数値・条件として定義されているか\n"
            "4) 観測可能性: 外部から結果が観測可能か（表示/出力/通知/永続性）\n\n"
            "スコア: 0.0〜1.0\n"
            "理由: 日本語で具体的に。不足があれば何を追加すべきか指摘。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    # weight指定ができる版なら重みを上げる（互換）
    if hasattr(verifiability, "weight"):
        try:
            verifiability.weight = 2.0
        except Exception:
            pass
    metrics.append(verifiability)

    ai_readability = GEval(
        name="AI可読性",
        criteria=(
            "あなたはAI向け要件定義のレビュアです。【要件】（ACTUAL_OUTPUT）を以下の観点で評価してください。\n\n"
            "評価観点:\n"
            "1) 構造化: What/Why/AC/例外/境界条件/トレースが読み取りやすい構造になっているか\n"
            "2) コンテキスト完全性: 未定義用語や参照不能なIDがないか\n"
            "3) トレーサビリティ: derived_from/traces_to が妥当か\n\n"
            "スコア: 0.0〜1.0\n"
            "理由: 日本語で具体的に。参照不能があれば指摘。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(ai_readability)

    return metrics


def build_overall_metric() -> Any:
    overall_metric = GEval(
        name="全体網羅性（企画→要件） [GEval]",
        criteria=(
            "あなたは上流QAのレビュー担当です。\n"
            "INPUTは企画書（全内容の抜粋）です。ACTUAL_OUTPUTは要件定義の全件サマリーです。\n"
            "企画の重要要素（目的/方針/制約/主要スコープ/成果物/運用想定/リスク等）が要件に落ちているかを評価してください。\n\n"
            "評価観点:\n"
            "1) 重要要素の落ち: 企画にあるのに要件に無い重要要素があるか（具体例を挙げる）\n"
            "2) 余計な要素: 企画に根拠のない要件が多数含まれていないか\n"
            "3) 粒度: 重要要素が大雑把すぎず、要件として分解されているか\n\n"
            "スコア: 0.0〜1.0\n"
            "理由: 日本語で具体的に。特に不足している要素を列挙。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    return overall_metric


# ===========================================================================
# テストケース構築
# ===========================================================================

def build_test_cases(
    reqs: List[Requirement],
    planning_index: Dict[str, PlanningItem],
    planning_full_text: str,
    checklist_summary: str,
) -> List[LLMTestCase]:
    """要件1件ごとのテストケースを構築"""
    test_cases: List[LLMTestCase] = []

    # timeout対策: checklist_summaryを上限でカット
    checklist_trimmed = checklist_summary
    if len(checklist_trimmed) > MAX_CHECKLIST_CHARS:
        checklist_trimmed = checklist_trimmed[:MAX_CHECKLIST_CHARS] + "\n...(省略)"

    for req in reqs:
        planning_ctx = get_planning_context_for_req(req, planning_index, planning_full_text)
        req_text = req.to_text()

        input_text = (
            f"=== 企画書コンテキスト（derived_from: {req.derived_from}） ===\n"
            f"{planning_ctx}\n\n"
            f"{checklist_trimmed}"
        )

        tc = LLMTestCase(
            input=input_text,
            actual_output=req_text,
            context=[planning_ctx],
            retrieval_context=[planning_ctx],
            additional_metadata={
                "requirement_id": req.req_id,
                "req_type": req.req_type,
                "source_file": req.source_file,
                "doc_id": req.doc_id,
                "doc_derived_from": req.doc_derived_from,
            },
        )
        test_cases.append(tc)

    return test_cases


def build_overall_test_case(reqs: List[Requirement], planning_full_text: str) -> LLMTestCase:
    """全体網羅性評価用テストケース（1件）"""
    req_summaries = []
    for req in reqs:
        req_summaries.append(
            f"[{req.req_id}]({req.req_type}) {req.title}\n"
            f"  説明: {req.description[:100].strip()}..."
        )
    all_reqs_text = "\n".join(req_summaries)

    planning_trimmed = planning_full_text
    if len(planning_trimmed) > MAX_PLANNING_FULL_CHARS:
        planning_trimmed = planning_trimmed[:MAX_PLANNING_FULL_CHARS] + "\n...(省略)"

    return LLMTestCase(
        input=f"=== 企画書（全内容） ===\n{planning_trimmed}",
        actual_output=f"=== 要件定義書（全件サマリー: {len(reqs)}件） ===\n{all_reqs_text}",
        context=[planning_trimmed],
        retrieval_context=[planning_trimmed],
        additional_metadata={
            "requirement_id": "OVERALL",
            "total_requirements": len(reqs),
        },
    )


# ===========================================================================
# 結果シリアライズ
# ===========================================================================

def serialize_metric(mdata: Any) -> Dict[str, Any]:
    return {
        "name": getattr(mdata, "name", type(mdata).__name__),
        "score": getattr(mdata, "score", None),
        "threshold": getattr(mdata, "threshold", None),
        "success": getattr(mdata, "success", None),
        "reason": getattr(mdata, "reason", None),
        "error": getattr(mdata, "error", None),
    }


def serialize_results(results: Any, reqs: List[Requirement]) -> Dict[str, Any]:
    """DeepEval結果をJSONに落としやすい形へ変換"""
    out: Dict[str, Any] = {
        "summary": {
            "total_test_cases": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "total_requirements_evaluated": len(reqs),
            "metric_averages": {},
        },
        "test_results": [],
    }

    test_results = getattr(results, "test_results", []) or []
    out["summary"]["total_test_cases"] = len(test_results)

    # requirement_id -> meta
    req_meta: Dict[str, Dict[str, Any]] = {r.req_id: {
        "req_type": r.req_type,
        "source_file": r.source_file,
        "doc_id": r.doc_id,
        "doc_derived_from": r.doc_derived_from,
    } for r in reqs}
    req_meta["OVERALL"] = {"req_type": "overall", "source_file": "", "doc_id": "", "doc_derived_from": ""}

    metric_sums: Dict[str, float] = {}
    metric_counts: Dict[str, int] = {}

    for tr in test_results:
        meta = getattr(tr, "additional_metadata", {}) or {}
        req_id = meta.get("requirement_id") or "UNKNOWN"

        success = getattr(tr, "success", None)
        if success is True:
            out["summary"]["passed"] += 1
        elif success is False:
            out["summary"]["failed"] += 1

        for mdata in (getattr(tr, "metrics_data", []) or []):
            name = getattr(mdata, "name", type(mdata).__name__)
            score = getattr(mdata, "score", None)
            if isinstance(score, (int, float)):
                metric_sums[name] = metric_sums.get(name, 0.0) + float(score)
                metric_counts[name] = metric_counts.get(name, 0) + 1

        tr_dict = {
            "requirement_id": req_id,
            "req_type": req_meta.get(req_id, {}).get("req_type", ""),
            "source_file": req_meta.get(req_id, {}).get("source_file", ""),
            "doc_id": req_meta.get(req_id, {}).get("doc_id", ""),
            "doc_derived_from": req_meta.get(req_id, {}).get("doc_derived_from", ""),
            "success": success,
            "metrics": [serialize_metric(m) for m in (getattr(tr, "metrics_data", []) or [])],
        }
        out["test_results"].append(tr_dict)

    out["summary"]["pass_rate"] = (
        out["summary"]["passed"] / out["summary"]["total_test_cases"]
        if out["summary"]["total_test_cases"] > 0 else 0.0
    )

    for name, s in metric_sums.items():
        c = metric_counts.get(name, 0)
        if c > 0:
            out["summary"]["metric_averages"][name] = s / c

    return out


# ===========================================================================
# エントリーポイント
# ===========================================================================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AIDD DeepEval: requirements vs planning")
    p.add_argument("--async", dest="async_mode", action="store_true", help="Run DeepEval in async mode (parallel).")
    p.add_argument("--no-async", dest="async_mode", action="store_false", help="Run DeepEval sequentially (no parallel).")
    p.set_defaults(async_mode=False)  # ★デフォルトは逐次

    p.add_argument("--max-concurrency", type=int, default=1, help="Max concurrency when async mode is enabled.")
    p.add_argument("--timeout-seconds", type=int, default=0, help="Set DeepEval per-task timeout override seconds (0=do not set).")

    p.add_argument("--max-planning-chars", type=int, default=MAX_PLANNING_FULL_CHARS, help="Max chars for OVERALL planning input.")
    p.add_argument("--max-checklist-chars", type=int, default=MAX_CHECKLIST_CHARS, help="Max chars for checklist summary in per-req input.")
    p.add_argument("--max-ctx-chars", type=int, default=MAX_CONTEXT_CHARS, help="Max chars for per-req planning context fallback.")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    # apply CLI to globals
    global ASYNC_MODE, MAX_CONCURRENCY, MAX_PLANNING_FULL_CHARS, MAX_CHECKLIST_CHARS, MAX_CONTEXT_CHARS
    ASYNC_MODE = bool(args.async_mode)
    MAX_CONCURRENCY = int(args.max_concurrency)
    MAX_PLANNING_FULL_CHARS = int(args.max_planning_chars)
    MAX_CHECKLIST_CHARS = int(args.max_checklist_chars)
    MAX_CONTEXT_CHARS = int(args.max_ctx_chars)

    # timeout override (if requested)
    if args.timeout_seconds and args.timeout_seconds > 0:
        os.environ[DEEPEVAL_TIMEOUT_ENV] = str(args.timeout_seconds)

    # ---- ファイル存在確認 ----
    for pth in [PLANNING_DIR, REQUIREMENTS_DIR, CHECKLIST_YAML]:
        if not pth.exists():
            raise SystemExit(f"パスが見つかりません: {pth}")

    print("=== AIDD 要件妥当性評価（Deep Eval） ===")
    print(f"企画書ディレクトリ : {PLANNING_DIR}")
    print(f"要件定義ディレクトリ: {REQUIREMENTS_DIR}")
    print(f"チェックリスト    : {CHECKLIST_YAML}")
    print(f"実行モード        : {'ASYNC' if ASYNC_MODE else 'SEQUENTIAL'} (max_concurrency={MAX_CONCURRENCY})")
    if os.environ.get(DEEPEVAL_TIMEOUT_ENV):
        print(f"DeepEval timeout   : {DEEPEVAL_TIMEOUT_ENV}={os.environ.get(DEEPEVAL_TIMEOUT_ENV)}")
    print()

    # ---- データ読み込み ----
    print("[1/4] 企画書YAMLを読み込み中...")
    planning_items, planning_full_text = load_planning_items(PLANNING_DIR)
    planning_index = build_planning_index(planning_items)
    print(f"      企画書アイテム数: {len(planning_items)}")

    print("[2/4] 要件定義YAMLを読み込み中...")
    reqs = load_all_requirements(REQUIREMENTS_DIR)
    print(f"      要件数: {len(reqs)} 件")

    print("[3/4] チェックリストを読み込み中...")
    checklist = load_yaml_safe(CHECKLIST_YAML)
    checklist_summary = format_checklist_summary(checklist)
    if len(checklist_summary) > MAX_CHECKLIST_CHARS:
        checklist_summary = checklist_summary[:MAX_CHECKLIST_CHARS] + "\n...(省略)"

    # ---- テストケース構築 ----
    print("[4/4] テストケースを構築中...")
    per_req_cases = build_test_cases(reqs, planning_index, planning_full_text, checklist_summary)
    overall_case = build_overall_test_case(reqs, planning_full_text)
    print(f"      テストケース数: {len(per_req_cases) + 1} 件（要件{len(per_req_cases)}件 + 全体網羅性1件）")

    # ---- メトリクス構築 ----
    per_req_metrics = build_per_req_metrics(checklist_summary)
    overall_metric = build_overall_metric()

    # DeepEvalはtest_case単位でメトリクスを指定できないため、2回に分けてevaluate
    print()
    print("=== 評価実行（要件個別）===")
    print(f"使用メトリクス: {[m.name if hasattr(m, 'name') else type(m).__name__ for m in per_req_metrics]}")

    try:
        from deepeval.evaluate import AsyncConfig, ErrorConfig
        async_config = AsyncConfig(
            run_async=ASYNC_MODE,
            max_concurrent=MAX_CONCURRENCY,
            throttle_value=1.0,
        )
        error_config = ErrorConfig(ignore_errors=True)
    except ImportError:
        async_config = None
        error_config = None

    eval_kwargs: Dict[str, Any] = {"error_config": error_config} if error_config else {}
    if async_config:
        eval_kwargs["async_config"] = async_config

    results_per_req = evaluate(
        test_cases=per_req_cases,
        metrics=per_req_metrics,
        identifier="req_vs_planning_per_requirement",
        **eval_kwargs,
    )

    print()
    print("=== 評価実行（全体網羅性）===")
    results_overall = evaluate(
        test_cases=[overall_case],
        metrics=[overall_metric],
        identifier="req_vs_planning_overall_completeness",
        **eval_kwargs,
    )

    # ---- 結果マージ ----
    class MergedResults:
        def __init__(self, r1: Any, r2: Any):
            tr1 = getattr(r1, "test_results", []) or []
            tr2 = getattr(r2, "test_results", []) or []
            self.test_results = tr1 + tr2

    merged = MergedResults(results_per_req, results_overall)
    structured = serialize_results(merged, reqs)

    # ---- 保存 ----
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print("=== 評価完了 ===")
    print(f"テストケース数 : {structured['summary']['total_test_cases']}")
    print(f"合格 / 不合格  : {structured['summary']['passed']} / {structured['summary']['failed']}")
    print(f"合格率         : {structured['summary']['pass_rate'] * 100:.1f}%")
    print()
    print("メトリクス平均スコア:")
    for name, avg in structured["summary"]["metric_averages"].items():
        try:
            verdict = "OK" if float(avg) >= GEVAL_THRESHOLD else "NG"
            print(f"  [{verdict}] {name}: {float(avg):.3f}")
        except Exception:
            print(f"  [--] {name}: {avg}")
    print()
    print(f"結果ファイル: {OUT_JSON}")


if __name__ == "__main__":
    main()