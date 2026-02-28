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

実行:
  python deepeval/evaluate_req_vs_planning_v1.py

環境変数:
  OPENAI_API_KEY  : OpenAI APIキー（必須）
  DEEPEVAL_MODEL  : 使用モデル（省略時: gpt-4o）
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
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

# ---- 設定 ----
ASYNC_MODE = True
MAX_CONCURRENCY = 4      # 並列実行数（API制限に合わせて調整）
FAITHFULNESS_THRESHOLD = 0.5
GEVAL_THRESHOLD = 0.5    # GEvalはスコア0-1、0.5以上で合格


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
    doc_derived_from: str # ドキュメントレベルのderived_from（企画書セクションID）

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


def extract_requirements_from_yaml(
    data: Dict[str, Any], source_file: str
) -> List[Requirement]:
    """要件YAMLから Requirement のリストを生成"""
    reqs: List[Requirement] = []
    doc = data.get("requirements_document", {})
    doc_id = doc.get("doc_id", "")
    doc_derived_from = doc.get("derived_from", "")

    def parse_req_list(raw_list: Optional[List], req_type: str) -> None:
        for r in (raw_list or []):
            if not isinstance(r, dict):
                continue
            reqs.append(Requirement(
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
            ))

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
                # 評価基準を簡潔に
                criteria_lines = [ln.strip() for ln in criteria.strip().splitlines() if ln.strip()]
                parts.append("    評価基準: " + " / ".join(criteria_lines[:3]))

    judgment = checklist.get("judgment", {})
    thresh = (judgment.get("thresholds") or {})
    parts.append(
        f"\n判定閾値: "
        f"A採用≥0.8 / B将来≥0.5 / C却下<0.5"
    )
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

    # 要件レベルの derived_from（item IDレベル）
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

    # ドキュメントレベルのderived_from（セクションID）でフォールバック
    if not found_items and req.doc_derived_from:
        section_id = req.doc_derived_from
        matching = [pi for pi in planning_index.values() if pi.section_id == section_id]
        for pi in matching[:max_items]:
            found_items.append(pi.to_text())

    if found_items:
        return "\n\n---\n\n".join(found_items)

    # どちらも見つからない場合は全体テキストを縮小して返す
    # （コンテキスト長削減のため先頭2000文字）
    return planning_full_text[:2000] + "\n...(省略)"


# ===========================================================================
# メトリクス定義
# ===========================================================================

def build_per_req_metrics(checklist_summary: str) -> List:
    """要件1件ごとに適用するメトリクスを構築"""
    metrics = []

    # 1. 企画書に対する忠実性（幻覚検出）
    faithfulness = FaithfulnessMetric(threshold=FAITHFULNESS_THRESHOLD, include_reason=True)
    metrics.append(faithfulness)

    # 2. 企画整合性（GEval）
    # CHK-01-01, CHK-01-02 相当
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

    # 3. スコープ適切性 + How非混入（GEval）
    # CHK-02-01, CHK-02-02, CHK-02-03 相当
    scope_validity = GEval(
        name="スコープ適切性・How非混入",
        criteria=(
            "あなたはAIDD要件定義のスコープレビュアです。【要件】（ACTUAL_OUTPUT）を以下の観点で評価してください。\n\n"
            "評価観点:\n"
            "1) フェーズ適切性: Phase0（MVP）に必須の内容か、Phase1以降に回すべき内容を含まないか\n"
            "2) How非混入（最重要）: 実装詳細が混入していないか\n"
            "   危険ワード: テーブル名/カラム/SQL/PostgreSQL/REST/GraphQL/エンドポイント/"
            "ボタン配置/px指定/React/Python/AWS/Docker等の技術固有語\n"
            "   ※技術スタックへの言及は×、機能的な振る舞いの記述は○\n"
            "3) 主語明確性: 誰が（user/admin/viewer/system）が明確か\n\n"
            "スコア: 0.0〜1.0（1.0=全て○、0.0=重大なHow混入あり）\n"
            "理由: 日本語で。How混入がある場合は該当フレーズを引用して指摘。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(scope_validity)

    # 4. 検証可能性（GEval）★最重要（チェックリスト weight=2.0）
    # CHK-03-01〜04 相当
    verifiability = GEval(
        name="検証可能性（AIDD最重要）",
        criteria=(
            "あなたはAIDD品質保証の検証可能性評価者です。【要件】（ACTUAL_OUTPUT）を以下の観点で評価してください。\n\n"
            "評価観点（CHK-03-01〜04相当、チェックリスト最重要カテゴリ）:\n"
            "1) 外部観測可能性: 「〜が表示される」「〜が出力される」等、外から確認できる記述か\n"
            "   NG例: 「内部で計算する」「バックグラウンドで処理する」\n"
            "2) 受入基準の検証可能性: Given-When-Then形式でテストケースを導出できるか\n"
            "   Given（前提）/ When（トリガー）/ Then（期待結果）が全て導出可能か\n"
            "3) 曖昧語排除: 禁止ワードが含まれていないか\n"
            "   禁止: 適切に/十分に/柔軟に/簡単に/最適に/迅速に/など/等/必要に応じて/"
            "すぐに/リアルタイムに(定義なし)/大量の/多くの\n"
            "4) 境界条件の明示: 数値・上限・下限が具体的に定義されているか\n"
            "   ○: 「最大100件」「5秒以内」 ×: 「大量」「高速」\n\n"
            "スコア: 0.0〜1.0（1.0=全観点クリア、0.5=一部不足、0.0=検証不能）\n"
            "理由: 日本語で。曖昧語や境界条件の不備があれば具体的に抽出して改善案を提示。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(verifiability)

    # 5. AI可読性（GEval）
    # CHK-04-01〜03 相当（AIDD固有評価）
    ai_readability = GEval(
        name="AI可読性（AIDD固有）",
        criteria=(
            "あなたはAIDD（AI駆動開発）の要件品質評価者です。\n"
            "【要件】（ACTUAL_OUTPUT）をAIがそのままコード化できるか、以下の観点で評価してください。\n\n"
            "評価観点（CHK-04-01〜03相当）:\n"
            "1) プロンプト構造化度: 入力/出力が分離し、条件分岐が明示的で、LLMプロンプトとしてそのまま使えるか\n"
            "2) コンテキスト完全性: 前提知識なしでAIが理解可能か。暗黙の前提が排除されているか\n"
            "   ドメイン固有用語は定義済みか、参照先が到達可能か\n"
            "3) ハルシネーション耐性: AI生成結果の正誤を検証する基準があるか\n"
            "   期待出力例・制約条件・不正出力の判定基準が含まれているか\n\n"
            "スコア: 0.0〜1.0（1.0=そのままAIプロンプトとして使用可能、0.0=大幅な書き換えが必要）\n"
            "理由: 日本語で。AIコード化の際に問題になる箇所を具体的に指摘。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
    )
    metrics.append(ai_readability)

    return metrics


def build_overall_metric() -> Any:
    """全体網羅性評価（企画書の全要素が要件に落ちているか）"""
    return GEval(
        name="全体網羅性（企画→要件）",
        criteria=(
            "あなたは要件定義の網羅性レビュアです。\n"
            "【企画書の全内容】（INPUT）と【要件定義の全件】（ACTUAL_OUTPUT）を照合し、評価してください。\n\n"
            "手順:\n"
            "A) 企画書の重要要素を8〜15個に列挙する\n"
            "B) 各要素に対応する要件ID（REQ-FUNC-*/REQ-NFR-*等）を特定する\n"
            "   - 対応する要件がない場合は「不足」と記録\n"
            "C) 不足している場合は、追加すべき要件のタイトル案を提示する\n"
            "D) 逆に要件が企画書に根拠のない内容を含む場合も指摘する\n\n"
            "スコア: 0.0〜1.0（1.0=企画の全重要要素が要件に網羅、0.0=重大な抜け漏れあり）\n"
            "理由: 日本語で。不足要件のタイトル案を箇条書きで提示。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.7,  # 網羅性はより高い閾値
    )


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

    for req in reqs:
        planning_ctx = get_planning_context_for_req(req, planning_index, planning_full_text)
        req_text = req.to_text()

        # input: 企画書コンテキスト + チェックリスト要約
        input_text = (
            f"=== 企画書コンテキスト（derived_from: {req.derived_from}） ===\n"
            f"{planning_ctx}\n\n"
            f"{checklist_summary}"
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


def build_overall_test_case(
    reqs: List[Requirement],
    planning_full_text: str,
) -> LLMTestCase:
    """全体網羅性評価用テストケース（1件）"""
    # 要件を全件テキスト化（ID + タイトル + 説明の要約）
    req_summaries = []
    for req in reqs:
        req_summaries.append(
            f"[{req.req_id}]({req.req_type}) {req.title}\n"
            f"  説明: {req.description[:100].strip()}..."
        )
    all_reqs_text = "\n".join(req_summaries)

    return LLMTestCase(
        input=f"=== 企画書（全内容） ===\n{planning_full_text}",
        actual_output=f"=== 要件定義書（全件サマリー: {len(reqs)}件） ===\n{all_reqs_text}",
        context=[planning_full_text],
        retrieval_context=[planning_full_text],
        additional_metadata={
            "requirement_id": "OVERALL",
            "total_requirements": len(reqs),
        },
    )


# ===========================================================================
# 結果シリアライズ
# ===========================================================================

def serialize_metric(md: Any) -> Dict[str, Any]:
    return {
        "name": getattr(md, "name", None),
        "score": getattr(md, "score", None),
        "threshold": getattr(md, "threshold", None),
        "success": getattr(md, "success", None),
        "reason": getattr(md, "reason", None),
        "evaluation_model": getattr(md, "evaluation_model", None),
        "evaluation_cost": getattr(md, "evaluation_cost", None),
        "error": getattr(md, "error", None),
    }


def serialize_results(results: Any, reqs: List[Requirement]) -> Dict[str, Any]:
    """DeepEval結果を構造化JSONに変換"""
    test_results = getattr(results, "test_results", results) or []

    # 集計
    passed = sum(1 for tr in test_results if getattr(tr, "success", False))
    failed = len(test_results) - passed

    # 要件ごとのスコアを集計してサマリを計算
    metric_scores: Dict[str, List[float]] = {}
    for tr in test_results:
        for mdata in (getattr(tr, "metrics_data", []) or []):
            name = getattr(mdata, "name", None) or ""
            score = getattr(mdata, "score", None)
            if score is not None:
                metric_scores.setdefault(name, []).append(float(score))

    metric_averages = {
        name: round(sum(scores) / len(scores), 3)
        for name, scores in metric_scores.items()
        if scores
    }

    out: Dict[str, Any] = {
        "summary": {
            "total_test_cases": len(test_results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(test_results), 3) if test_results else 0.0,
            "metric_averages": metric_averages,
            "total_requirements_evaluated": len(reqs),
        },
        "test_results": [],
    }

    for tr in test_results:
        meta = getattr(tr, "additional_metadata", {}) or {}
        req_id = meta.get("requirement_id") or getattr(tr, "name", "")

        tr_dict: Dict[str, Any] = {
            "requirement_id": req_id,
            "req_type": meta.get("req_type", ""),
            "source_file": meta.get("source_file", ""),
            "doc_id": meta.get("doc_id", ""),
            "doc_derived_from": meta.get("doc_derived_from", ""),
            "success": getattr(tr, "success", None),
            "metrics": [
                serialize_metric(mdata)
                for mdata in (getattr(tr, "metrics_data", []) or [])
            ],
        }
        out["test_results"].append(tr_dict)

    return out


# ===========================================================================
# エントリーポイント
# ===========================================================================

def main() -> None:
    # ---- ファイル存在確認 ----
    for p in [PLANNING_DIR, REQUIREMENTS_DIR, CHECKLIST_YAML]:
        if not p.exists():
            raise SystemExit(f"パスが見つかりません: {p}")

    print("=== AIDD 要件妥当性評価（Deep Eval） ===")
    print(f"企画書ディレクトリ : {PLANNING_DIR}")
    print(f"要件定義ディレクトリ: {REQUIREMENTS_DIR}")
    print(f"チェックリスト    : {CHECKLIST_YAML}")
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

    # ---- テストケース構築 ----
    print("[4/4] テストケースを構築中...")
    per_req_cases = build_test_cases(reqs, planning_index, planning_full_text, checklist_summary)
    overall_case = build_overall_test_case(reqs, planning_full_text)
    all_cases = per_req_cases + [overall_case]
    print(f"      テストケース数: {len(all_cases)} 件（要件{len(per_req_cases)}件 + 全体網羅性1件）")

    # ---- メトリクス構築 ----
    per_req_metrics = build_per_req_metrics(checklist_summary)
    overall_metric = build_overall_metric()

    # 要件個別テストは per_req_metrics、全体テストは overall_metric を適用
    # DeepEvalはtest_case単位でメトリクスを指定できないため、
    # 2回に分けてevaluateを実行する
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
    # test_results を結合してシリアライズ
    class MergedResults:
        def __init__(self, r1: Any, r2: Any):
            tr1 = getattr(r1, "test_results", []) or []
            tr2 = getattr(r2, "test_results", []) or []
            self.test_results = tr1 + tr2

    merged = MergedResults(results_per_req, results_overall)
    structured = serialize_results(merged, reqs)

    # ---- 保存 ----
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(structured, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print()
    print(f"=== 評価完了 ===")
    print(f"テストケース数 : {structured['summary']['total_test_cases']}")
    print(f"合格 / 不合格  : {structured['summary']['passed']} / {structured['summary']['failed']}")
    print(f"合格率         : {structured['summary']['pass_rate'] * 100:.1f}%")
    print()
    print("メトリクス平均スコア:")
    for name, avg in structured["summary"]["metric_averages"].items():
        verdict = "OK" if avg >= GEVAL_THRESHOLD else "NG"
        print(f"  [{verdict}] {name}: {avg:.3f}")
    print()
    print(f"結果ファイル: {OUT_JSON}")


if __name__ == "__main__":
    main()
