#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_gates.py
Gate runner for AIDD artifacts (Windows PowerShell friendly).

What it does (minimum useful gates):
- G3: JSON Schema validation for YAML files (schema chosen by schema_registry.yaml)
- META: meta required keys exist + no PENDING
- ID: ID format check (<PREFIX>-<PHASE>-<PURPOSE>-<NNN>) across common fields
- G1 (lightweight): Ambiguity-term scan (Japanese vague words) across YAML text

It prints:
- Console summary with PASS/FAIL
- Writes JSON report to --report-out (default: ./gate_report.json)

Exit code:
- 0 if overall PASS
- 1 if FAIL
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema is required. pip install jsonschema", file=sys.stderr)
    sys.exit(2)


# ---- Defaults (can be overridden by files/args) ----

DEFAULT_META_KEYS = ["run_id", "prompt_id", "timestamp", "model", "output_hash"]

# A pragmatic default set; you can extend via --ambiguity-terms-yaml
DEFAULT_AMBIGUITY_TERMS = [
    # generic vague / subjective
    "直感的", "わかりやすい", "簡単", "詳細な", "適切", "十分", "なるべく", "できるだけ",
    "最小", "最適", "高品質", "高い", "低い", "多い", "少ない",
    # time vagueness
    "即座に", "すぐ", "迅速", "短期間", "近日", "なるはや",
    # severity / frequency vagueness
    "深刻", "多発", "爆発的", "急速", "急速に", "大幅", "大きい", "小さい",
    # impact vagueness
    "影響が最小", "影響が少ない", "影響は小さい",
]

# Generic ID regex for PREFIX-PHASE-PURPOSE-NNN
GEN_ID_PATTERN = re.compile(r"^[A-Z]{2,5}-[A-Z]{2,5}-[A-Z0-9_]+-\d{3}$")


# ---- Helpers ----

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(read_text(path))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def is_yaml_file(path: Path) -> bool:
    return path.suffix.lower() in [".yaml", ".yml"]


def collect_files(target: Path) -> List[Path]:
    if target.is_file():
        return [target]
    files = [p for p in target.rglob("*") if p.is_file() and is_yaml_file(p)]
    files.sort()
    return files


def load_schema_registry(registry_path: Path) -> List[Tuple[re.Pattern, str]]:
    reg = load_yaml(registry_path)
    if not isinstance(reg, dict) or "schema_registry" not in reg:
        raise ValueError("schema_registry.yaml must be a mapping with key: schema_registry")
    entries = reg["schema_registry"]
    if not isinstance(entries, list):
        raise ValueError("schema_registry must be a list")

    compiled: List[Tuple[re.Pattern, str]] = []
    for e in entries:
        if not isinstance(e, dict) or "match" not in e or "schema" not in e:
            raise ValueError("Each schema_registry entry needs: match, schema")
        compiled.append((re.compile(str(e["match"])), str(e["schema"])))
    return compiled


def choose_schema(rel_path_str: str, compiled_registry: List[Tuple[re.Pattern, str]]) -> Optional[str]:
    for pat, schema_path in compiled_registry:
        if pat.search(rel_path_str):
            return schema_path
    return None


def load_json_schema(schema_path: Path) -> Dict[str, Any]:
    return json.loads(read_text(schema_path))


def validate_with_schema(data: Any, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    v = Draft202012Validator(schema)
    errs = sorted(v.iter_errors(data), key=lambda e: list(e.path))
    out = []
    for e in errs:
        out.append({
            "path": list(e.path),
            "message": e.message,
        })
    return out


def find_all_strings(obj: Any) -> List[str]:
    """Collect all string values from nested dict/list structures (values only)."""
    res: List[str] = []
    if isinstance(obj, dict):
        for _, v in obj.items():
            res.extend(find_all_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            res.extend(find_all_strings(v))
    elif isinstance(obj, str):
        res.append(obj)
    return res


def _is_gate_exempt(node: Any, gate_name: str) -> bool:
    """Return True if this node declares exemption from a given gate."""
    if not isinstance(node, dict):
        return False
    v = node.get("gate_exempt")
    if v is True:
        return True
    if isinstance(v, list):
        norm = {str(x).strip().upper() for x in v if str(x).strip()}
        return gate_name.strip().upper() in norm or "ALL" in norm
    if isinstance(v, str):
        # Allow a single string for convenience
        return v.strip().upper() in {gate_name.strip().upper(), "ALL"}
    return False


def find_all_strings_excluding_item_types(
    obj: Any,
    excluded_item_types: List[str],
    *,
    gate_name: str,
) -> List[str]:
    """Collect all string values, skipping subtrees that are excluded for a given gate.

    Exclusion rules:
    - item.type in excluded_item_types
    - gate_exempt indicates this subtree is exempt from the given gate
    """
    res: List[str] = []

    if isinstance(obj, dict):
        if _is_gate_exempt(obj, gate_name):
            return []

        t = obj.get("type")
        # Exclude the entire subtree for quote/example-like items (examples/quotations are not gate targets).
        if isinstance(t, str) and t in set(excluded_item_types):
            return []

        for _, v in obj.items():
            res.extend(find_all_strings_excluding_item_types(v, excluded_item_types, gate_name=gate_name))
        return res

    if isinstance(obj, list):
        for v in obj:
            res.extend(find_all_strings_excluding_item_types(v, excluded_item_types, gate_name=gate_name))
        return res

    if isinstance(obj, str):
        return [obj]

    return []


def meta_check(doc: Any, required_keys: List[str]) -> Tuple[bool, List[str]]:
    """Return (ok, issues)."""
    issues: List[str] = []
    if not isinstance(doc, dict):
        return False, ["YAML root is not a mapping (object/dict)"]
    meta = doc.get("meta")
    if not isinstance(meta, dict):
        return False, ["meta is missing or not a mapping"]
    for k in required_keys:
        if k not in meta:
            issues.append(f"meta.{k} missing")
        else:
            v = str(meta[k]).strip()
            if v == "PENDING":
                issues.append(f"meta.{k} is PENDING")
    return (len(issues) == 0), issues


def id_check(doc: Any) -> Tuple[bool, List[str]]:
    """
    Heuristic ID checks:
    - planning_index.id
    - planning_index.sections[].id
    - section.id
    - items[].id
    """
    issues: List[str] = []
    if not isinstance(doc, dict):
        return False, ["YAML root is not a mapping"]

    # index-style
    if "planning_index" in doc and isinstance(doc.get("planning_index"), dict):
        pi = doc["planning_index"]
        pid = pi.get("id")
        if isinstance(pid, str) and pid and not GEN_ID_PATTERN.match(pid):
            issues.append(f"planning_index.id invalid: {pid}")
        secs = pi.get("sections", [])
        if isinstance(secs, list):
            for s in secs:
                if isinstance(s, dict):
                    sid = s.get("id")
                    if isinstance(sid, str) and sid and not GEN_ID_PATTERN.match(sid):
                        issues.append(f"planning_index.sections[].id invalid: {sid}")

    # section-style
    if "section" in doc and isinstance(doc.get("section"), dict):
        sec = doc["section"]
        sid = sec.get("id")
        if isinstance(sid, str) and sid and not GEN_ID_PATTERN.match(sid):
            issues.append(f"section.id invalid: {sid}")
        items = sec.get("items", [])
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    iid = it.get("id")
                    if isinstance(iid, str) and iid and not GEN_ID_PATTERN.match(iid):
                        issues.append(f"items[].id invalid: {iid}")

    return (len(issues) == 0), issues


def ambiguity_scan(doc: Any, terms: List[str]) -> Tuple[bool, List[Dict[str, Any]]]:
    """Scan string fields for ambiguity terms.

    Gate policy:
    - items[].type == quote (and future example) are treated as *citations/examples* and excluded from G1.
      Rationale: documents often enumerate ambiguous words as examples; those examples must not fail G1.
    """
    texts = find_all_strings_excluding_item_types(doc, excluded_item_types=["quote", "example"], gate_name="G1")
    hits: List[Dict[str, Any]] = []
    for t in terms:
        for s in texts:
            if t in s:
                hits.append({"term": t, "sample": s[:140] + ("…" if len(s) > 140 else "")})
                break
    ok = len(hits) == 0
    return ok, hits


def load_ambiguity_terms_yaml(path: Path) -> List[str]:
    data = load_yaml(path)
    if isinstance(data, dict) and "terms" in data and isinstance(data["terms"], list):
        return [str(x) for x in data["terms"]]
    if isinstance(data, list):
        return [str(x) for x in data]
    raise ValueError("Ambiguity terms YAML must be a list or {terms:[...]}")


def rel_from_repo_root(repo_root: Path, file_path: Path) -> str:
    # Return posix-ish relative path string starting with AIDD/...
    rel = file_path.resolve().relative_to(repo_root.resolve())
    return str(rel).replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Repo root (default: current dir)")
    ap.add_argument("--target", required=True, help="Target dir or YAML file")
    ap.add_argument("--schema-registry", required=True, help="schema_registry.yaml path")
    ap.add_argument("--meta-required", default=",".join(DEFAULT_META_KEYS), help="Comma-separated required meta keys")
    ap.add_argument("--ambiguity-terms-yaml", default="", help="Optional YAML file for ambiguity terms")
    ap.add_argument("--report-out", default="gate_report.json", help="Report JSON output path")
    ap.add_argument("--fail-on-ambiguity", action="store_true", help="If set, ambiguity hits make gate fail (default: true anyway)")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    target = (repo_root / args.target).resolve() if not Path(args.target).is_absolute() else Path(args.target).resolve()
    schema_registry_path = (repo_root / args.schema_registry).resolve() if not Path(args.schema_registry).is_absolute() else Path(args.schema_registry).resolve()
    report_out = (repo_root / args.report_out).resolve() if not Path(args.report_out).is_absolute() else Path(args.report_out).resolve()

    required_meta = [x.strip() for x in args.meta_required.split(",") if x.strip()]
    ambiguity_terms = DEFAULT_AMBIGUITY_TERMS
    if args.ambiguity_terms_yaml:
        terms_path = (repo_root / args.ambiguity_terms_yaml).resolve() if not Path(args.ambiguity_terms_yaml).is_absolute() else Path(args.ambiguity_terms_yaml).resolve()
        ambiguity_terms = load_ambiguity_terms_yaml(terms_path)

    registry = load_schema_registry(schema_registry_path)

    files = collect_files(target)
    if not files:
        print("FAIL: No YAML files found in target.", file=sys.stderr)
        sys.exit(1)

    schemas_cache: Dict[str, Dict[str, Any]] = {}

    g3_results = {"checked": 0, "failed": 0, "failures": []}
    meta_results = {"checked": 0, "failed": 0, "failures": []}
    id_results = {"checked": 0, "failed": 0, "failures": []}
    g1_results = {"checked": 0, "failed": 0, "hits": []}

    for f in files:
        rel = rel_from_repo_root(repo_root, f)
        doc = load_yaml(f)

        # META
        meta_ok, meta_issues = meta_check(doc, required_meta)
        meta_results["checked"] += 1
        if not meta_ok:
            meta_results["failed"] += 1
            meta_results["failures"].append({"file": rel, "issues": meta_issues})

        # ID
        id_ok, id_issues = id_check(doc)
        id_results["checked"] += 1
        if not id_ok:
            id_results["failed"] += 1
            id_results["failures"].append({"file": rel, "issues": id_issues})

        # G1 ambiguity
        amb_ok, amb_hits = ambiguity_scan(doc, ambiguity_terms)
        g1_results["checked"] += 1
        if not amb_ok:
            g1_results["failed"] += 1
            g1_results["hits"].append({"file": rel, "hits": amb_hits[:30]})

        # G3 schema (only if schema can be chosen)
        schema_rel = choose_schema(rel, registry)
        if schema_rel is None:
            g3_results["failed"] += 1
            g3_results["checked"] += 1
            g3_results["failures"].append({"file": rel, "issues": ["No matching schema in schema_registry"]})
        else:
            # schema path is relative to repo root by convention
            schema_abs = (repo_root / schema_rel).resolve() if not Path(schema_rel).is_absolute() else Path(schema_rel).resolve()
            if schema_rel not in schemas_cache:
                schemas_cache[schema_rel] = load_json_schema(schema_abs)
            errs = validate_with_schema(doc, schemas_cache[schema_rel])
            g3_results["checked"] += 1
            if errs:
                g3_results["failed"] += 1
                g3_results["failures"].append({"file": rel, "schema": schema_rel, "errors": errs[:50]})

    gates = {
        "G1_ambiguity": {
            "pass": g1_results["failed"] == 0,
            "checked": g1_results["checked"],
            "failed": g1_results["failed"],
            "hits": g1_results["hits"],
            "terms_source": args.ambiguity_terms_yaml or "DEFAULT_AMBIGUITY_TERMS",
        },
        "G3_schema": {
            "pass": g3_results["failed"] == 0,
            "checked": g3_results["checked"],
            "failed": g3_results["failed"],
            "failures": g3_results["failures"],
            "schema_registry": str(schema_registry_path),
        },
        "META": {
            "pass": meta_results["failed"] == 0,
            "checked": meta_results["checked"],
            "failed": meta_results["failed"],
            "failures": meta_results["failures"],
            "required_keys": required_meta,
        },
        "ID_format": {
            "pass": id_results["failed"] == 0,
            "checked": id_results["checked"],
            "failed": id_results["failed"],
            "failures": id_results["failures"],
            "pattern": GEN_ID_PATTERN.pattern,
        },
        "G4_deep_eval": {
            "pass": False,
            "reason": "not_run_in_this_environment",
            "note": "Deep Eval is expected to be executed via your agent/tooling (e.g., Cline). This runner can be extended to ingest results JSON.",
        },
        "G4_promptfoo": {
            "pass": False,
            "reason": "not_available",
            "note": "promptfoo is not available in your environment. Gate kept as N/A.",
        }
    }

    overall_pass = all([
        gates["G1_ambiguity"]["pass"],
        gates["G3_schema"]["pass"],
        gates["META"]["pass"],
        gates["ID_format"]["pass"],
        # G4 are informational here
    ])

    report = {
        "generated_at": datetime_now_iso(),
        "repo_root": str(repo_root),
        "target": str(target),
        "files_checked": [rel_from_repo_root(repo_root, f) for f in files],
        "overall_pass": overall_pass,
        "gates": gates,
    }

    dump_json(report_out, report)

    # Console summary (agent-friendly)
    print(f"GATES: {'PASS' if overall_pass else 'FAIL'}")
    print(f"- META: {'PASS' if gates['META']['pass'] else 'FAIL'} (failed={gates['META']['failed']})")
    print(f"- ID:   {'PASS' if gates['ID_format']['pass'] else 'FAIL'} (failed={gates['ID_format']['failed']})")
    print(f"- G1:   {'PASS' if gates['G1_ambiguity']['pass'] else 'FAIL'} (failed={gates['G1_ambiguity']['failed']})")
    print(f"- G3:   {'PASS' if gates['G3_schema']['pass'] else 'FAIL'} (failed={gates['G3_schema']['failed']})")
    print(f"- report: {report_out}")

    sys.exit(0 if overall_pass else 1)


def datetime_now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


if __name__ == "__main__":
    main()
