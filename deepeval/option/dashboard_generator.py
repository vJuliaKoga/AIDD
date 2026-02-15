import json
from typing import Any, Dict, List

SUCCESS_THRESHOLD = 0.7


def _safe_get(d: Any, *keys, default=None):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def to_dashboard_json(deepeval_results: Any) -> Dict[str, Any]:
    """
    deepeval_results の構造はバージョンで変わり得るので、
    可能な範囲で情報を拾って template.html が期待する形式へ変換する。
    """
    test_cases_out: List[Dict[str, Any]] = []

    # 1. 代表的な構造候補を取得
    candidates = None
    if isinstance(deepeval_results, list):
        candidates = deepeval_results
    elif isinstance(deepeval_results, dict):
        candidates = deepeval_results.get("test_results") or deepeval_results.get("results") or deepeval_results.get("testCases")
    if candidates is None:
        candidates = [deepeval_results]

    for idx, tr in enumerate(candidates, start=1):
        # 2. テストケース情報の抽出
        tc = _safe_get(tr, "test_case", default={}) if isinstance(tr, dict) else {}
        inp = _safe_get(tc, "input", default=_safe_get(tr, "input", default=""))
        actual = _safe_get(tc, "actual_output", default=_safe_get(tr, "actual_output", default=""))
        meta = _safe_get(tc, "additional_metadata", default=_safe_get(tr, "additional_metadata", default={})) or {}

        req_id = meta.get("requirement_id") or meta.get("id") or f"TC-{idx:03d}"
        name = f"{req_id}"

        # 3. メトリクス情報を template 形式へ
        metrics_in = _safe_get(tr, "metrics_data", default=_safe_get(tr, "metrics", default=[])) or []
        metrics_out = []
        for m in metrics_in:
            if not isinstance(m, dict):
                continue
            m_name = m.get("name") or m.get("metric") or "Metric"
            score = m.get("score")
            if score is None:
                score = m.get("value", 0.0)
            weight = m.get("weight", 1.0)
            reason = m.get("reason") or m.get("explanation") or ""
            metrics_out.append({
                "name": m_name,
                "score": float(score) if score is not None else 0.0,
                "weight": float(weight),
                "reason": str(reason),
            })

        fails = [mm for mm in metrics_out if mm["score"] < SUCCESS_THRESHOLD]
        summary = {
            "判定": "FAIL" if len(fails) else "PASS",
            "指摘": [f'{mm["name"]} が閾値未満（{mm["score"]:.2f}）' for mm in fails][:8],
            "追記案": []
        }

        test_cases_out.append({
            "name": name,
            "input": inp,
            "actualOutput": actual,
            "summary": summary,          # ← 追加欄
            "metrics": metrics_out,
        })

    return {"testCases": test_cases_out}


def save_results_json(deepeval_results: Any, out_path: str = "results.json"):
    data = to_dashboard_json(deepeval_results)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
