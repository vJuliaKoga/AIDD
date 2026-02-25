#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_req.py — AIDD Requirements Document Validator

AIDD要件定義YAML（req.template.yaml 形式）を JSON Schema で検証するスクリプト。
品質ゲートG3（構造一貫性）の実行手段として使用する。

使い方:
  # 指定ディレクトリ内の全 YAML を検証
  python requirements/JSONScheme/validate_req.py --dir requirements/yaml/requirements_v1

  # ファイルを直接指定
  python requirements/JSONScheme/validate_req.py --file requirements/yaml/requirements_v1/req_v1.yaml

  # スキーマパスを明示指定（デフォルト: スクリプト隣の req.schema.json）
  python requirements/JSONScheme/validate_req.py --dir ... --schema requirements/JSONScheme/req.schema.json

Exit codes:
  0  VALID（全ファイル合格）
  1  INVALID（1件以上のエラー）
  2  引数エラー / 実行エラー
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.  pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator, SchemaError
except ImportError:
    print("ERROR: jsonschema is required.  pip install jsonschema", file=sys.stderr)
    sys.exit(2)


# ============================================================
# デフォルトスキーマパス（このスクリプトの隣の req.schema.json）
# ============================================================
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent / "req.schema.json"


def load_schema(schema_path: Path) -> dict:
    """JSON Schema を読み込む。"""
    try:
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        Draft202012Validator.check_schema(schema)
        return schema
    except SchemaError as e:
        print(f"ERROR: スキーマ自体が不正です: {e.message}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: スキーマ読み込み失敗 ({schema_path}): {e}", file=sys.stderr)
        sys.exit(2)


def collect_targets(args) -> list[Path]:
    """検証対象の YAML ファイルパス一覧を返す。"""
    targets = []
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"ERROR: ファイルが見つかりません: {p}", file=sys.stderr)
            sys.exit(2)
        targets.append(p)
    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: ディレクトリが見つかりません: {d}", file=sys.stderr)
            sys.exit(2)
        targets.extend(sorted(d.glob("*.yaml")) + sorted(d.glob("*.yml")))
    if not targets:
        print("ERROR: --file または --dir を指定してください。", file=sys.stderr)
        sys.exit(2)
    return targets


def extra_checks(data: dict, filepath: Path) -> list[str]:
    """
    JSON Schema では検証できないビジネスルールを追加チェックする。

    チェック内容:
    1. validation_summary のカウントが実際の要件数と一致するか
    2. meta.artifact_id が PENDING でない場合、meta.file とパス名が一致するか
    """
    errors = []
    if not isinstance(data, dict):
        return ["YAMLの最上位がマッピングではありません。"]

    rd = data.get("requirements_document", {})
    if not isinstance(rd, dict):
        return []

    vs = rd.get("validation_summary", {})
    if isinstance(vs, dict):
        # カウント整合性チェック
        actual = {
            "functional": len(rd.get("functional_requirements") or []),
            "non_functional": len(rd.get("non_functional_requirements") or []),
            "constraints": len(rd.get("constraints") or []),
            "data_entities": len(
                (rd.get("data_requirements") or {}).get("entities") or []
            ),
            "integrations": len(rd.get("integration_requirements") or []),
            "quality_gates": len(rd.get("quality_gates") or []),
        }
        for key, real_count in actual.items():
            stated = vs.get(key)
            if isinstance(stated, int) and stated != real_count:
                errors.append(
                    f"validation_summary.{key} = {stated} "
                    f"ですが実際の件数は {real_count} です。"
                )
        # total_requirements チェック
        total_actual = actual["functional"] + actual["non_functional"] + actual["constraints"]
        total_stated = vs.get("total_requirements")
        if isinstance(total_stated, int) and total_stated != total_actual:
            errors.append(
                f"validation_summary.total_requirements = {total_stated} "
                f"ですが functional + non_functional + constraints = {total_actual} です。"
            )

    # meta.artifact_id と doc_id の整合（両方確定値の場合のみ）
    meta = data.get("meta", {})
    if isinstance(meta, dict):
        artifact_id = meta.get("artifact_id", "PENDING")
        doc_id = rd.get("doc_id", "PENDING")
        if (
            artifact_id not in ("PENDING", "", None)
            and doc_id not in ("PENDING", "", None)
            and artifact_id != doc_id
        ):
            errors.append(
                f"meta.artifact_id ({artifact_id!r}) と "
                f"requirements_document.doc_id ({doc_id!r}) が一致しません。"
            )

    return errors


def validate_file(filepath: Path, validator: Draft202012Validator) -> bool:
    """
    1ファイルを検証して結果を出力する。
    合格なら True、不合格なら False を返す。
    """
    # YAML 読み込み
    try:
        with filepath.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ {filepath.name}  — YAML 読み込みエラー: {e}")
        return False

    if data is None:
        print(f"❌ {filepath.name}  — ファイルが空です。")
        return False

    # JSON Schema 検証
    schema_errors = sorted(
        validator.iter_errors(data),
        key=lambda e: list(e.absolute_path),
    )

    # ビジネスルール検証
    biz_errors = extra_checks(data, filepath)

    if not schema_errors and not biz_errors:
        print(f"✅ {filepath.name}")
        return True

    # エラー出力
    print(f"❌ {filepath.name}")
    for e in schema_errors[:20]:
        path = "$" + "".join(
            f"[{p!r}]" if isinstance(p, int) else f".{p}"
            for p in e.absolute_path
        )
        print(f"  [schema] {path}: {e.message}")
    for msg in biz_errors[:10]:
        print(f"  [biz]    {msg}")
    if len(schema_errors) > 20:
        print(f"  ... 他 {len(schema_errors) - 20} 件のスキーマエラー（省略）")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="AIDD要件定義YAML を JSON Schema で検証する（G3ゲート）"
    )
    parser.add_argument("--file", metavar="PATH", help="検証する YAML ファイルパス")
    parser.add_argument("--dir", metavar="DIR", help="検証する YAML が格納されたディレクトリ")
    parser.add_argument(
        "--schema",
        metavar="SCHEMA",
        default=str(DEFAULT_SCHEMA_PATH),
        help=f"JSON Schema ファイルパス（デフォルト: {DEFAULT_SCHEMA_PATH}）",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"ERROR: スキーマファイルが見つかりません: {schema_path}", file=sys.stderr)
        sys.exit(2)

    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    targets = collect_targets(args)

    print(f"スキーマ: {schema_path}")
    print(f"対象ファイル数: {len(targets)}")
    print("-" * 50)

    results = [validate_file(t, validator) for t in targets]
    ok_count = sum(results)
    ng_count = len(results) - ok_count

    print("-" * 50)
    print(f"結果: {ok_count} 合格 / {ng_count} 不合格")

    if ng_count == 0:
        print("VALID")
        sys.exit(0)
    else:
        print("INVALID")
        sys.exit(1)


if __name__ == "__main__":
    main()
