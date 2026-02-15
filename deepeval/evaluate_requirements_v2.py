import json
from pathlib import Path
from typing import Dict, List
import yaml

# Deep Eval version: 3.8.4
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import HallucinationMetric, FaithfulnessMetric, GEval
from deepeval.evaluate import AsyncConfig, ErrorConfig

# スクリプト場所を固定
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 入力
PLANNING_MD = r"planning\planning.md"
CHECKLIST_MD = r"checklist\checklist_requirements.md"
REQUIREMENTS_DIR = r"requirements"  # FR-001.yaml, AR-005.yaml ...

# 出力
OUTPUT_JSON = r"deepeval\output\eval_requirements.json"


def resolve_path(p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def read_text(path_str: str) -> str:
    path = resolve_path(path_str)
    if not path.exists():
        raise FileNotFoundError(
            f"ファイルが見つかりません:\n"
            f"- 指定: {path_str}\n"
            f"- 解決: {path}\n"
            f"（ヒント）evaluate_requirements.py の位置を基準に相対パスを解決しています。"
        )
    return path.read_text(encoding="utf-8")


def ensure_parent_dir(path_str: str) -> Path:
    path = resolve_path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_requirements_from_yaml_dir(dir_str: str) -> Dict[str, dict]:
    req_dir = resolve_path(dir_str)
    if not req_dir.exists():
        raise FileNotFoundError(f"requirements dir not found: {req_dir}")

    targets = sorted(
        list(req_dir.glob("FR-*.yaml")) + list(req_dir.glob("AR-*.yaml"))
    )

    if not targets:
        # デバッグ用：実際に見えているファイルを出す
        debug = sorted([p.name for p in req_dir.glob("*.yaml")] + [p.name for p in req_dir.glob("*.yml")])
        raise ValueError(
            f"No requirement YAMLs found in: {req_dir}\n"
            f"YAML files visible in that dir: {debug if debug else '(none)'}"
        )

    reqs: Dict[str, dict] = {}
    for f in targets:
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"YAML root must be a mapping: {f}")
        rid = data.get("id") or f.stem
        reqs[str(rid)] = data

    return reqs


def requirement_to_eval_text(req: dict) -> str:
    """YAML→評価用テキスト（形式揺れの影響を減らす）"""
    def join_list(key: str) -> str:
        v = req.get(key, [])
        if not v:
            return "- (none)"
        if not isinstance(v, list):
            return f"- (invalid type: {type(v).__name__})"
        return "\n".join([f"- {str(x)}" for x in v])

    lines = []
    lines.append(f"ID: {req.get('id', '')}")
    lines.append(f"Type: {req.get('type', '')}")
    lines.append(f"Title: {req.get('title', '')}")
    lines.append(f"Role: {req.get('role', '')}")
    lines.append(f"What: {req.get('what', '')}")
    lines.append(f"Why: {req.get('why', '')}")

    lines.append("Acceptance Criteria:\n" + join_list("acceptance_criteria"))
    lines.append("Exceptions:\n" + join_list("exceptions"))
    lines.append("Logs:\n" + join_list("logs"))
    lines.append("Dependencies:\n" + join_list("dependencies"))
    lines.append("Permissions:\n" + join_list("permissions"))
    lines.append("NFR:\n" + join_list("nfr"))
    lines.append("Evidence:\n" + join_list("evidence"))
    lines.append("Changes From Current:\n" + join_list("changes_from_current"))
    lines.append("TBD:\n" + join_list("tbd"))

    return "\n\n".join(lines).strip()


def build_metrics() -> List:
    hallucination = HallucinationMetric(threshold=0.5, include_reason=True)
    faithfulness = FaithfulnessMetric(threshold=0.5, include_reason=True)

    validity = GEval(
        name="企画遵守（ID単位）",
        criteria=(
            "あなたは上流工程QAのレビュアです。『企画書』に照らして『要件（1件）』が企画意図に沿うか評価してください。\n"
            "観点：目的・スコープと矛盾/逸脱がないか、企画で禁止されたこと（例：自動判定など）を要求していないか。\n"
            "出力：日本語で、逸脱があればどの文が問題かを具体に指摘。"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    checklist_fit = GEval(
        name="チェックリスト適合（ID単位）",
        criteria=(
            "あなたはQA基盤の要件レビュアです。『チェックリスト（本企画向け）』の必須ゲート観点を中心に、"
            "『要件（1件）』が満たしているか評価してください。\n"
            "出力形式：\n"
            "- 判定：満たす/一部不足/満たさない\n"
            "- 不足：不足している観点名\n"
            "- 追記案：要件に追加すべき短文\n"
            "出力：日本語。"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    completeness_overall = GEval(
        name="抜け漏れ（全体網羅性）",
        criteria=(
            "あなたは要件定義レビューアです。『企画書』の重要要素が『要件一覧（全件）』に落ちているか評価してください。\n"
            "手順：\n"
            "A) 企画書の重要要素を7〜12個に要約\n"
            "B) 各要素に対応する要件ID（FR/AR）を列挙。無ければ「不足」とする\n"
            "C) 不足なら追加すべき要件のタイトル案を出す\n"
            "出力：日本語。"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    return [hallucination, faithfulness, validity, checklist_fit, completeness_overall]


def main():
    planning = read_text(PLANNING_MD)
    checklist = read_text(CHECKLIST_MD)

    req_map = load_requirements_from_yaml_dir(REQUIREMENTS_DIR)
    metrics = build_metrics()

    test_cases: List[LLMTestCase] = []

    # ID単位
    for req_id, req_obj in req_map.items():
        req_text = requirement_to_eval_text(req_obj)

        inp = (
            f"【企画書】\n{planning}\n\n"
            f"【チェックリスト（本企画向け）】\n{checklist}\n\n"
            f"【要件ID】{req_id}\n"
            f"【要件（1件）】\n{req_text}\n"
        )

        meta = req_obj.get("meta") if isinstance(req_obj.get("meta"), dict) else {}
        additional = {"requirement_id": req_id, "meta": meta}

        test_cases.append(
            LLMTestCase(
                input=inp,
                actual_output=req_text,
                context=[planning],
                retrieval_context=[planning],
                additional_metadata=additional,
            )
        )

    # 全体網羅性（全件連結）
    all_reqs_text = "\n\n".join([f"---\n{requirement_to_eval_text(v)}" for v in req_map.values()])
    overall_inp = f"【企画書】\n{planning}\n\n【要件一覧（全件）】\n{all_reqs_text}\n"
    test_cases.append(
        LLMTestCase(
            input=overall_inp,
            actual_output=all_reqs_text,
            context=[planning],
            retrieval_context=[planning],
            additional_metadata={"requirement_id": "OVERALL"},
        )
    )

    # API混雑を防ぐため並列実行を禁止（現行踏襲）
    results = evaluate(
        test_cases=test_cases,
        metrics=metrics,
        async_config=AsyncConfig(run_async=False),
        error_config=ErrorConfig(ignore_errors=True),
    )

    OUT_JSON = ensure_parent_dir(OUTPUT_JSON)

    def serialize_results(results):
        test_results = getattr(results, "test_results", results)

        out = {
            "summary": {
                "total": len(test_results),
                "passed": sum(1 for tr in test_results if getattr(tr, "success", False)),
                "failed": sum(1 for tr in test_results if not getattr(tr, "success", False)),
            },
            "test_results": [],
        }

        for tr in test_results:
            meta = getattr(tr, "additional_metadata", None) or {}
            req_id = meta.get("requirement_id") or getattr(tr, "name", None)

            tr_dict = {
                "requirement_id": req_id,
                "success": getattr(tr, "success", None),
                "input": getattr(tr, "input", None),
                "actual_output": getattr(tr, "actual_output", None),
                "metrics": [],
                "additional_metadata": meta,
            }

            metrics_data = getattr(tr, "metrics_data", []) or []
            for md in metrics_data:
                tr_dict["metrics"].append({
                    "name": getattr(md, "name", None),
                    "score": getattr(md, "score", None),
                    "threshold": getattr(md, "threshold", None),
                    "success": getattr(md, "success", None),
                    "reason": getattr(md, "reason", None),
                    "evaluation_model": getattr(md, "evaluation_model", None),
                    "evaluation_cost": getattr(md, "evaluation_cost", None),
                    "error": getattr(md, "error", None),
                })

            out["test_results"].append(tr_dict)

        return out

    structured = serialize_results(results)
    OUT_JSON.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT_JSON}")


if __name__ == "__main__":
    main()