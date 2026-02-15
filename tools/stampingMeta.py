import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import yaml


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def run_sha256(script_path: Path, target_file: Path) -> str:
    res = subprocess.run(
        [sys.executable, str(script_path), str(target_file)],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        raise SystemExit(
            "Hash script failed.\n"
            f"cmd: {sys.executable} {script_path} {target_file}\n"
            f"stdout:\n{res.stdout}\n"
            f"stderr:\n{res.stderr}\n"
        )
    out = res.stdout.strip().splitlines()
    if not out:
        raise SystemExit("Hash script produced no output.")
    return out[-1].strip()


def assert_meta_present(f: Path, expected_run_id: str, expected_prompt_id: str):
    data = yaml.safe_load(f.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("YAML root must be an object")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        raise SystemExit("meta is missing after stamping.")

    required = ["run_id", "prompt_id", "timestamp", "model", "output_hash"]
    missing = [k for k in required if k not in meta]
    if missing:
        raise SystemExit(f"meta missing keys after stamping: {missing}")

    if meta["run_id"] != expected_run_id:
        raise SystemExit(f"meta.run_id mismatch: {meta['run_id']} != {expected_run_id}")
    if meta["prompt_id"] != expected_prompt_id:
        raise SystemExit(f"meta.prompt_id mismatch: {meta['prompt_id']} != {expected_prompt_id}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="requirements/FR-001.yaml etc.")
    ap.add_argument("--prompt-id", required=True, help="PR-003 etc.")
    ap.add_argument("--hash-script", default="hashtag/hashtag_generator.py")
    args = ap.parse_args()

    f = Path(args.file).resolve()
    if not f.exists():
        raise SystemExit(f"--file not found: {f}")

    prompt_id = args.prompt_id.strip()
    hash_script = Path(args.hash_script).resolve()
    if not hash_script.exists():
        raise SystemExit(f"--hash-script not found: {hash_script}")

    data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit("YAML root must be a mapping/object")

    run_id = f.stem  # FR-002 etc.

    meta = data.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    meta.update({
        "run_id": run_id,
        "prompt_id": prompt_id,
        "timestamp": now_str(),
        "model": "gpt-5.2",
        "output_hash": "PENDING"
    })
    data["meta"] = meta

    # 1回保存（meta込み最終形でハッシュを取るため）
    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # ハッシュ確定
    h = run_sha256(hash_script, f)
    data["meta"]["output_hash"] = h

    # 最終保存
    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # 再読込して確認
    assert_meta_present(f, expected_run_id=run_id, expected_prompt_id=prompt_id)

    print(f"Stamped meta into: {f}")


if __name__ == "__main__":
    main()
