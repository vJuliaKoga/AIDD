from pathlib import Path
import json
import re
import yaml
from jsonschema import Draft202012Validator

"""
requirements配下の YAML ファイルを JSON Schema で検証するスクリプト。

- ファイル名は FR-xxx.yaml / AR-xxx.yaml のみ対象
- Ajv の $data 拡張を python-jsonschema で扱えないため、該当する allOf 要素は事前に除去してから検証する
- スキーマ検証後に、追加の業務ルールチェックも実施する
"""


ROOT = Path(__file__).resolve().parents[1]  # requirements ディレクトリ
SCHEMA_PATH = ROOT / "JsonScheme" / "requirements.schema.json"  # 使用するJSON Schema

REQ_FILE_RE = re.compile(r"^(FR|AR)-\d{3}\.ya?ml$")  # 対象ファイル名パターン（例: FR-001.yaml, AR-123.yml）


def strip_allof_items_with_data_const(schema: dict) -> dict:
    # dict 以外はそのまま返す
    if not isinstance(schema, dict):
        return schema

    # 元スキーマを壊さないため shallow copy
    schema = dict(schema)

    # allOf がある場合の処理
    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        filtered = []
        # allOf 内の各要素をチェック
        for item in all_of:
            # $data を含む const を持つ場合は除外
            if contains_data_const(item):
                continue
            filtered.append(item)

        # フィルタ結果を反映
        if filtered:
            schema["allOf"] = filtered
        else:
            schema.pop("allOf", None)

    return schema


def contains_data_const(obj) -> bool:
    if isinstance(obj, dict):
        for k, v in obj.items():
            # const: { "$data": ... } を検出
            if k == "const" and isinstance(v, dict) and "$data" in v:
                return True
            # 再帰探索
            if contains_data_const(v):
                return True
    # list の場合
    elif isinstance(obj, list):
        return any(contains_data_const(x) for x in obj)
    return False


def extra_checks(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["YAMLファイルの構造は、インデントを使って階層構造を表現する必要があります。"]

    rid = data.get("id")
    meta = data.get("meta")
    mid = meta.get("run_id") if isinstance(meta, dict) else None

    if rid is not None and mid is not None and rid != mid:
        errors.append(f"$.meta.run_id must equal $.id (got meta.run_id={mid!r}, id={rid!r})")

    return errors


def main():
    # 1. スキーマ読み込み ---
    raw_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    # Ajv拡張($data)に依存する allOf 要素を除去
    schema = strip_allof_items_with_data_const(raw_schema)
    # バリデータ初期化
    validator = Draft202012Validator(schema)

    # 2. 検証対象ファイルの抽出
    targets = sorted([p for p in ROOT.glob("*.y*ml") if REQ_FILE_RE.match(p.name)])

    if not targets:
        print("requirementsファイル内にyamlが存在しません。/. (e.g., FR-001.yaml)")
        return

    ok = True
    # 3. 各ファイルを検証
    for f in targets:
        # YAML読み込み
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        # JSON Schema検証
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        # 業務ルール検証
        extra = extra_checks(data)

        # 4. 結果出力
        if errors or extra:
            ok = False
            print(f"❌ {f.name}")
            # スキーマエラー出力
            for e in errors[:20]:
                path = "$" + "".join([f"[{repr(p)}]" if isinstance(p, int) else f".{p}" for p in e.path])
                print(f"  - {path}: {e.message}")
            # 追加チェックエラー出力
            for msg in extra[:20]:
                print(f"  - {msg}")
        else:
            print(f"✅ {f.name}")

    # 5. 終了コード制御
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
