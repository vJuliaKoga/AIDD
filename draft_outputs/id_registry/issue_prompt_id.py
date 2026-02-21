#!/usr/bin/env python
# -*- coding: utf-8 -*-

issue_prompt_id.py
One-person prompt-id issuer.
- Reads a registry YAML, issues next PRM-{PHASE}-{PURPOSE}-{NNN}
- Updates registry next_nnn
- Appends to issued log YAML
- Prints issued prompt_id to stdout (so Cline can capture it)

No file locking (single-user assumption).

import argparse
import datetime as _dt
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required. Please install pyyaml.", file=sys.stderr)
    sys.exit(2)

def _now_iso():
    return _dt.datetime.now().isoformat(timespec="seconds")

def _load_yaml(path: Path):
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _save_yaml(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

def _pad(n: int, digits: int) -> str:
    return str(n).zfill(digits)

def infer_phase_from_paths(text: str, alias_map: dict):
    t = (text or "").replace("\\", "/").lower()
    for token, phase in (alias_map or {}).items():
        if f"/{token}/" in t or t.endswith(f"/{token}"):
            return phase
    if "planning_v" in t:
        return "PLN"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="AIDD/id_registry/prompt_id_registry.yaml", help="registry YAML path")
    ap.add_argument("--log", default="AIDD/id_registry/prompt_id_issued_log.yaml", help="issued log YAML path")
    ap.add_argument("--phase", default=None, help="PHASE override (e.g., PLN/REQ/BAS/DET...)")
    ap.add_argument("--purpose", default=None, help="PURPOSE (e.g., YAML/DRAFT/REVIEW/CHECK/EVAL...)")
    ap.add_argument("--key", default=None, help="sequence key override (e.g., PRM-PLN-YAML). If set, phase/purpose are ignored.")
    ap.add_argument("--context", default="", help="free text for inference (paths, filenames, etc.)")
    ap.add_argument("--title", default="", help="human-readable title for issued log")
    ap.add_argument("--note", default="", help="note for issued log")
    ap.add_argument("--out", default="", help="optional file to write issued prompt_id")
    args = ap.parse_args()

    reg_path = Path(args.registry)
    log_path = Path(args.log)

    reg = _load_yaml(reg_path)
    if not isinstance(reg, dict) or "sequences" not in reg:
        print(f"Registry not found or invalid: {reg_path}", file=sys.stderr)
        sys.exit(2)

    digits = int(reg.get("rules", {}).get("nnn_digits", 3))
    alias_map = reg.get("phase_alias", {}) or {}

    if args.key:
        seq_key = args.key.strip()
    else:
        phase = (args.phase or "").strip().upper() or None
        purpose = (args.purpose or "").strip().upper() or None

        if not phase:
            phase = infer_phase_from_paths(args.context, alias_map)

        if not phase:
            print("PHASE could not be inferred. Provide --phase or --key.", file=sys.stderr)
            sys.exit(2)

        if not purpose:
            print("PURPOSE is required. Provide --purpose or --key.", file=sys.stderr)
            sys.exit(2)

        seq_key = f"PRM-{phase}-{purpose}"

    seq = None
    for s in reg.get("sequences", []):
        if s.get("key") == seq_key:
            seq = s
            break

    if seq is None:
        parts = seq_key.split("-")
        if len(parts) < 3:
            print(f"Invalid key format: {seq_key}", file=sys.stderr)
            sys.exit(2)
        seq = {"key": seq_key, "phase": parts[1], "purpose": parts[2], "next_nnn": 1, "notes": "auto-created"}
        reg.setdefault("sequences", []).append(seq)

    n = int(seq.get("next_nnn", 1))
    prompt_id = f"PRM-{seq.get('phase')}-{seq.get('purpose')}-{_pad(n, digits)}"

    seq["next_nnn"] = n + 1
    reg.setdefault("meta", {})["last_updated"] = _now_iso()

    log = _load_yaml(log_path)
    if not isinstance(log, dict):
        log = {"meta": {"version":"1.0", "last_updated":"PENDING"}, "issued": []}

    log.setdefault("issued", []).append({
        "prompt_id": prompt_id,
        "issued_at": _now_iso(),
        "sequence_key": seq_key,
        "title": args.title,
        "note": args.note,
        "context": args.context,
    })
    log.setdefault("meta", {})["last_updated"] = _now_iso()

    _save_yaml(reg_path, reg)
    _save_yaml(log_path, log)

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(prompt_id, encoding="utf-8")

    print(prompt_id)

if __name__ == "__main__":
    main()
