from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

# ---- DeepEval imports (version-tolerant) ----
try:
    from deepeval import evaluate
    from deepeval.test_case import LLMTestCaseParams
    from deepeval.test_case import LLMTestCase
except Exception as e:
    raise SystemExit(f"DeepEval import failed. Is deepeval installed? Error: {e}")

# Metrics: name changes across versions, so we try multiple import paths.
HallucinationMetric = None
FaithfulnessMetric = None
GEval = None
EvaluationParams = None

_import_errors = []

for _cand in [
    ("deepeval.metrics", "HallucinationMetric", "FaithfulnessMetric", "GEval", "EvaluationParams"),
    ("deepeval.metrics.hallucination", "HallucinationMetric", None, None, None),
    ("deepeval.metrics.faithfulness", "FaithfulnessMetric", None, None, None),
    ("deepeval.metrics.g_eval", "GEval", "EvaluationParams", None, None),
]:
    try:
        mod = __import__(_cand[0], fromlist=["*"])
        if _cand[1] and HallucinationMetric is None:
            HallucinationMetric = getattr(mod, _cand[1], HallucinationMetric)
        if _cand[2] and FaithfulnessMetric is None:
            FaithfulnessMetric = getattr(mod, _cand[2], FaithfulnessMetric)
        if _cand[3] and GEval is None:
            GEval = getattr(mod, _cand[3], GEval)
        if _cand[4] and EvaluationParams is None:
            EvaluationParams = getattr(mod, _cand[4], EvaluationParams)
    except Exception as e:
        _import_errors.append((str(_cand), str(e)))

if HallucinationMetric is None or FaithfulnessMetric is None or GEval is None:
    raise SystemExit(
        "DeepEval metric imports failed.\n"
        f"HallucinationMetric={HallucinationMetric}, FaithfulnessMetric={FaithfulnessMetric}, "
        f"GEval={GEval}, EvaluationParams={EvaluationParams}\n"
        f"Import attempts:\n{json.dumps(_import_errors, ensure_ascii=False, indent=2)}"
    )

# ---- Paths ----
ROOT = Path(__file__).resolve().parents[1]  # assumes deepeval/ is directly under repo root
PLANNING_MD = ROOT / "planning" / "planning.md"
COMPILED_YAML = ROOT / "planning" / "planning.compiled.yaml"
OUT_JSON = ROOT / "deepeval" / "output" / "eval_planning_compiled.json"

# ---- Config ----
# If you want to force model:
# export OPENAI_MODEL="gpt-5.2"
# export DEEPEVAL_MODEL="gpt-5.2"
OPENAI_MODEL_DEFAULT = "gpt-5.2"

# Reduce timeouts if you got CancelledError/TimeoutError before (tune as needed)
ASYNC_MODE = True
MAX_CONCURRENCY = 6


@dataclass
class Item:
    item_id: str
    label: str
    value_text: str


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def to_text(v: Any) -> str:
    # compact, human readable string
    if v is None:
        return "null"
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    return yaml.safe_dump(v, allow_unicode=True, sort_keys=False).strip()


def extract_items(compiled: Dict[str, Any]) -> List[Item]:
    """
    Flatten planning.compiled.yaml into evaluatable items.
    Each item becomes one LLMTestCase.
    """
    items: List[Item] = []

    def add(item_id: str, label: str, v: Any):
        txt = to_text(v).strip()
        if not txt:
            return
        items.append(Item(item_id=item_id, label=label, value_text=txt))

    # meta (except output_hash check is handled in schema/validator; still evaluate for faithfulness if you want)
    meta = compiled.get("meta", {})
    add("META-001", "meta.source_file", (meta or {}).get("source_file"))
    add("META-002", "meta.compiler", (meta or {}).get("compiler"))
    add("META-003", "meta.version", (meta or {}).get("version"))
    # compiled_at/output_hash are not derived from planning.md, so we DON'T faithfulness-check them strongly.
    # keep them out of evaluation by default.

    project = compiled.get("project", {})

    add("P-001", "project.title", project.get("title"))
    add("P-010", "project.background.context", (project.get("background") or {}).get("context"))
    add("P-011", "project.background.summary", (project.get("background") or {}).get("summary"))

    for i, s in enumerate(project.get("problems") or [], start=1):
        add(f"P-020-{i:02d}", f"project.problems[{i}]", s)

    purpose = project.get("purpose") or {}
    for i, s in enumerate(purpose.get("goals") or [], start=1):
        add(f"P-030-G-{i:02d}", f"project.purpose.goals[{i}]", s)
    for i, s in enumerate(purpose.get("outcomes") or [], start=1):
        add(f"P-030-O-{i:02d}", f"project.purpose.outcomes[{i}]", s)

    principles = project.get("principles") or {}
    add("P-040-CORE", "project.principles.core_statement", principles.get("core_statement"))
    for i, s in enumerate(principles.get("do") or [], start=1):
        add(f"P-040-DO-{i:02d}", f"project.principles.do[{i}]", s)
    for i, s in enumerate(principles.get("dont") or [], start=1):
        add(f"P-040-DONT-{i:02d}", f"project.principles.dont[{i}]", s)
    add("P-040-HIC", "project.principles.human_in_charge", principles.get("human_in_charge"))

    ss = project.get("system_structure") or {}
    for i, layer in enumerate(ss.get("layers") or [], start=1):
        add(f"P-050-L-{i:02d}", f"project.system_structure.layers[{i}]", layer)
    for i, s in enumerate(ss.get("task_ticket_fields") or [], start=1):
        add(f"P-050-F-{i:02d}", f"project.system_structure.task_ticket_fields[{i}]", s)
    add("P-050-AUTO", "project.system_structure.auto_generation_allowed", ss.get("auto_generation_allowed"))

    status = project.get("status_model") or {}
    add("P-060-STAT", "project.status_model.statuses", status.get("statuses"))
    add("P-060-ABR", "project.status_model.abort_requires_reason", status.get("abort_requires_reason"))
    add("P-060-ABX", "project.status_model.abort_reason_examples", status.get("abort_reason_examples"))
    add("P-060-AOJ", "project.status_model.abort_is_official_judgment", status.get("abort_is_official_judgment"))

    viz = project.get("visualization") or {}
    add("P-070-FEAT", "project.visualization.features", viz.get("features"))
    add("P-070-FLOW", "project.visualization.flow_diagram", viz.get("flow_diagram"))
    add("P-070-SNAP", "project.visualization.snapshot", viz.get("snapshot"))

    uiq = project.get("ui_quality_points") or {}
    add("P-080-IN", "project.ui_quality_points.included_in_scope", uiq.get("included_in_scope"))
    add("P-080-TG", "project.ui_quality_points.targets", uiq.get("targets"))
    add("P-080-PS", "project.ui_quality_points.purpose_statement", uiq.get("purpose_statement"))

    pos = project.get("positioning") or {}
    add("P-090-NOT", "project.positioning.is_not", pos.get("is_not"))
    add("P-090-IS", "project.positioning.is", pos.get("is"))

    for i, ph in enumerate(project.get("roadmap") or [], start=1):
        add(f"P-100-{i:02d}", f"project.roadmap[{i}]", ph)

    for i, s in enumerate(project.get("expected_effects") or [], start=1):
        add(f"P-110-{i:02d}", f"project.expected_effects[{i}]", s)

    for i, s in enumerate(project.get("open_questions") or [], start=1):
        add(f"P-120-{i:02d}", f"project.open_questions[{i}]", s)

    # citations (important for grounding quality)
    sot = compiled.get("source_of_truth") or {}
    for i, c in enumerate(sot.get("citations") or [], start=1):
        add(f"C-001-{i:02d}", f"source_of_truth.citations[{i}]", c)

    return items


def build_test_cases(items: List[Item], planning_text: str) -> List[LLMTestCase]:
    test_cases: List[LLMTestCase] = []
    for it in items:
        # For Faithfulness/Hallucination, we treat each compiled item as "actual_output"
        # and give planning.md as retrieval_context/context.
        tc = LLMTestCase(
            input=f"[項目] {it.label}\n[値]\n{it.value_text}",
            actual_output=it.value_text,
            # DeepEval metric requirements (these names differ per version, but LLMTestCase generally supports both)
            context=[planning_text],
            retrieval_context=[planning_text],
            additional_metadata={"item_id": it.item_id, "label": it.label},
        )
        test_cases.append(tc)
    return test_cases


def main() -> None:
    if not PLANNING_MD.exists():
        raise SystemExit(f"planning.md not found: {PLANNING_MD}")
    if not COMPILED_YAML.exists():
        raise SystemExit(f"planning.compiled.yaml not found: {COMPILED_YAML}")

    planning_text = read_text(PLANNING_MD)
    compiled = yaml.safe_load(read_text(COMPILED_YAML))

    if not isinstance(compiled, dict):
        raise SystemExit("compiled yaml root must be a map/object")

    items = extract_items(compiled)
    test_cases = build_test_cases(items, planning_text)

    # ---- Metrics ----
    hallucination = HallucinationMetric(threshold=0.5, include_reason=True)
    faithfulness = FaithfulnessMetric(threshold=0.5, include_reason=True)

    # GEval: completeness & citation quality (Japanese reasons)
    # We evaluate at item-level: "Is this item supported by planning.md? If not, call it out."
    # and "Is citation (if present) adequate?"
    support_g_eval = GEval(
        name="企画書根拠整合（項目単位）",
        criteria=(
            "あなたは企画書（planning.md）と compiled YAML の1項目を突合する評価者。\n"
            "次を判定し、日本語で理由を書く。\n"
            "1) compiled項目が企画書に明示されている内容に基づくか（推測・断定の追加はNG）\n"
            "2) 企画書に根拠が薄い/無い場合は、その旨と不足情報を具体に指摘する\n"
            "3) How（実装語/DB/API/クラウド等）が混入していたらNGとする\n"
            "出力は簡潔で、どの表現が問題かを具体に示す。"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT,
        ],
    )

    metrics = [hallucination, faithfulness, support_g_eval]

    # DeepEval evaluate config: keep concurrency moderate to avoid timeouts
    # async_config name differs by version; evaluate() accepts async_config in your environment.
    from deepeval.evaluate import AsyncConfig, ErrorConfig

    results = evaluate(
        test_cases=test_cases,
        metrics=metrics,
        async_config=AsyncConfig(run_async=ASYNC_MODE, max_concurrent=MAX_CONCURRENCY, throttle_value=1.0),
        error_config=ErrorConfig(ignore_errors=True),
        identifier="planning_compiled_vs_planning_md",
    )

    # ---- Save minimal JSON ----
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    # DeepEval result object differs by version; we try to serialize robustly.
    payload = {
        "identifier": "planning_compiled_vs_planning_md",
        "planning_md": str(PLANNING_MD.as_posix()),
        "compiled_yaml": str(COMPILED_YAML.as_posix()),
        "test_case_count": len(test_cases),
        "raw_results": None,
    }

    try:
        payload["raw_results"] = results.model_dump()  # pydantic style
    except Exception:
        try:
            payload["raw_results"] = results.dict()
        except Exception:
            payload["raw_results"] = str(results)

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT_JSON.as_posix()}")


if __name__ == "__main__":
    main()
