#!/usr/bin/env python
# -*- coding: utf-8 -*-


stampingHumanMeta.py
A "little brother" of stampingMeta.py for human-authored artifacts.

Supports:
- YAML files: expects a top-level mapping with a `meta:` mapping.
- Markdown files: uses YAML Front Matter between `---` and `---` at the top of the file.
  If front matter doesn't exist, it will be inserted.

Workflow:
- Writes meta with `content_hash: PENDING`
- Runs `--hash-script` (e.g., AIDD/hashtag/hashtag_generator.py) to compute sha256 for the file
- Writes meta again with `content_hash` set to the computed hash

Note:
Like stampingMeta.py, the hash is computed after the first write (with PENDING),
so the final file bytes won't match `content_hash` exactly. This is intentional
and consistent with the existing stampingMeta workflow.

import argparse
import datetime as _dt
import subprocess
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required. Please install pyyaml.", file=sys.stderr)
    sys.exit(2)

REQUIRED_KEYS = ["artifact_id", "file", "author", "source_type", "timestamp", "content_hash"]

def now_local_str():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

def run_hash_script(hash_script: str, target_file: Path) -> str:
    cmd = [sys.executable, hash_script, str(target_file)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"hash-script failed: {p.stderr.strip() or p.stdout.strip()}")
    out = (p.stdout or "").strip()
    if not out:
        raise RuntimeError("hash-script produced empty output")
    return out.split()[0].strip()

def ensure_meta(meta: dict, args, target_file: Path):
    meta["artifact_id"] = args.artifact_id
    meta["file"] = args.file_value or target_file.name
    meta["author"] = args.author
    meta["source_type"] = args.source_type
    meta["timestamp"] = args.timestamp or now_local_str()
    if args.supersedes:
        meta["supersedes"] = args.supersedes
    for k in REQUIRED_KEYS:
        meta.setdefault(k, "PENDING")

def stamp_yaml(path: Path, args) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping (object/dict)")
    meta = data.get("meta")
    if meta is None or not isinstance(meta, dict):
        meta = {}
        data["meta"] = meta

    ensure_meta(meta, args, path)
    meta["content_hash"] = "PENDING"
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    h = run_hash_script(args.hash_script, path)
    meta["content_hash"] = h
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

def parse_front_matter(md_text: str):
    if md_text.startswith("---
"):
        end = md_text.find("
---
", 4)
        if end != -1:
            fm_raw = md_text[4:end]
            body = md_text[end+5:]
            fm = yaml.safe_load(fm_raw) if fm_raw.strip() else {}
            if fm is None:
                fm = {}
            if not isinstance(fm, dict):
                raise ValueError("Front matter must be a YAML mapping")
            return fm, body, True
    return None, md_text, False

def build_front_matter(fm: dict) -> str:
    return "---
" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).rstrip() + "
---
"

def stamp_markdown(path: Path, args) -> None:
    text = path.read_text(encoding="utf-8")
    fm, body, _had = parse_front_matter(text)
    if fm is None:
        fm = {}
    meta = fm.get("meta")
    if meta is None or not isinstance(meta, dict):
        meta = {}
        fm["meta"] = meta

    ensure_meta(meta, args, path)
    meta["content_hash"] = "PENDING"

    first = build_front_matter(fm) + body
    path.write_text(first, encoding="utf-8")

    h = run_hash_script(args.hash_script, path)
    meta["content_hash"] = h
    final = build_front_matter(fm) + body
    path.write_text(final, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Target file path (.yaml/.yml/.md)")
    ap.add_argument("--artifact-id", required=True, help="Artifact ID (e.g., TPL-OPS-RULES-001)")
    ap.add_argument("--author", required=True, help="Author handle (e.g., @juria.koga)")
    ap.add_argument("--source-type", default="human", choices=["human","ai","mixed"], help="Source type")
    ap.add_argument("--timestamp", default="", help="Timestamp string (default: now)")
    ap.add_argument("--supersedes", default="", help="Optional supersedes reference (file or artifact id)")
    ap.add_argument("--hash-script", default="AIDD/hashtag/hashtag_generator.py", help="Hash script path")
    ap.add_argument("--file-name", default="", help="Override meta.file (default: basename)")
    args = ap.parse_args()

    target = Path(args.file)
    if not target.exists():
        print(f"Target not found: {target}", file=sys.stderr)
        sys.exit(2)

    args.file_value = args.file_name or target.name

    suf = target.suffix.lower()
    try:
        if suf in [".yaml", ".yml"]:
            stamp_yaml(target, args)
        elif suf == ".md":
            stamp_markdown(target, args)
        else:
            print("Unsupported file type. Use .yaml/.yml/.md", file=sys.stderr)
            sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Stamped human meta into: {target}")

if __name__ == "__main__":
    main()
