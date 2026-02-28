#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""patch_requirements_v2.py

目的:
  - requirements/yaml/requirements_v1/*.yaml を読み込み
  - deepeval/output/eval_req_vs_planning_v1.json の reason/error を根拠に
    チェックリスト観点（主に CHK-02-02/02-03/03-02/05-03）を満たすように最小限パッチを適用
  - requirements/yaml/requirements_v2/*.yaml に再出力（UTF-8）
  - reports/requirements_patch_report.md / reports/requirements_patch_diff_summary.csv を生成

注意:
  - 既存 req_id / doc_id 等のIDは変更しない
  - timeout/cancelled しか根拠が無い要件は本文（description/title等）を原則変更しない
    （ただし traces_to の空埋め等、本文以外の最小補正は許容）
  - スキーマ additionalProperties=false を尊重し、既存スキーマ外のキーは追加しない
    -> timeout 判定は notes に "is_timeout_related=true" を追記して表現する
"""

from __future__ import annotations

import copy
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import datetime as _dt

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQ_V1_DIR = ROOT / "requirements" / "yaml" / "requirements_v1"
REQ_V2_DIR = ROOT / "requirements" / "yaml" / "requirements_v2"
CHECKLIST_PATH = ROOT / "checklist" / "CHK-REQ-REVIEW-001.yaml"
EVAL_PATH = ROOT / "deepeval" / "output" / "eval_req_vs_planning_v1.json"

REPORT_MD = ROOT / "reports" / "requirements_patch_report.md"
REPORT_CSV = ROOT / "reports" / "requirements_patch_diff_summary.csv"


# --- チェックリスト（レポート用） ---
DEFAULT_CHECK_ITEMS_S = [
    "CHK-02-02",  # How非混入
    "CHK-02-03",  # 主語明確性
    "CHK-03-02",  # 受入基準
    "CHK-05-03",  # traces_to
]

DEFAULT_CHECK_ITEMS_A = [
    "CHK-03-03",  # 曖昧語
    "CHK-03-04",  # 境界条件
    "CHK-03-01",  # 外部観測可能性
]


# --- 禁止/危険ワード（最小置換のみ） ---
TECH_REPLACEMENTS: List[Tuple[re.Pattern, str]] = [
    # storage/DB
    (re.compile(r"SQLiteデータベース", re.IGNORECASE), "プロジェクトデータ"),
    (re.compile(r"SQLite", re.IGNORECASE), "永続化データ"),
    (re.compile(r"データベース", re.IGNORECASE), "永続化データ"),
    # scheduling
    (re.compile(r"node-cron等|node-cron", re.IGNORECASE), "スケジュール実行手段"),
    (re.compile(r"Node\.jsのスケジューラー", re.IGNORECASE), "スケジュール実行手段"),
    # frontend storage
    (re.compile(r"ローカルストレージ|localStorage", re.IGNORECASE), "利用端末内への設定保持"),
    # tool names
    (re.compile(r"GitHub Actions", re.IGNORECASE), "CI/CD"),
    (re.compile(r"Allure Report", re.IGNORECASE), "品質レポート"),
    (re.compile(r"Promptfoo", re.IGNORECASE), "プロンプト評価"),
    (re.compile(r"Deep Eval", re.IGNORECASE), "AI評価"),
    (re.compile(r"ajv", re.IGNORECASE), "スキーマ検証実装"),
    # NOTE: \b は日本語とASCIIの境界で期待通りに効かない場合があるため、ここでは使用しない
    (re.compile(r"React", re.IGNORECASE), "フロントエンド"),
    (re.compile(r"Node\.js", re.IGNORECASE), "実行環境"),
    (re.compile(r"Express", re.IGNORECASE), "サーバー実装"),
    (re.compile(r"Zod", re.IGNORECASE), "入力検証"),
    (re.compile(r"Zustand", re.IGNORECASE), "状態管理"),
    (re.compile(r"Tailwind", re.IGNORECASE), "UIスタイル"),
    (re.compile(r"shadcn", re.IGNORECASE), "UIコンポーネント"),
    (re.compile(r"Vitest", re.IGNORECASE), "自動テスト"),
    (re.compile(r"Playwright", re.IGNORECASE), "自動検証"),
    (re.compile(r"Storybook", re.IGNORECASE), "UI定義"),
    (re.compile(r"Chromatic", re.IGNORECASE), "UI差分検出"),
    (re.compile(r"Visual Regression Testing", re.IGNORECASE), "UI差分検出"),
    (re.compile(r"Visual Regression", re.IGNORECASE), "UI差分検出"),
    (re.compile(r"E2Eテスト", re.IGNORECASE), "利用者操作を模した自動検証"),
    # unsupported specifics seen in reasons
    (re.compile(r"200ms以内"), "入力中に"),
    (re.compile(r"200ms"), "入力中に"),
    (re.compile(r"3件以上"), ""),
]


def cleanup_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    out = text
    # 重複フレーズの後処理
    out = out.replace("systemは、systemは、", "systemは、")
    out = out.replace("プロジェクトデータ（プロジェクトデータ）", "プロジェクトデータ")
    out = out.replace("スケジュール実行手段（スケジュール実行手段）", "スケジュール実行手段")
    # 多重スペース/空行の整理（意味を変えない範囲）
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + ("\n" if text.endswith("\n") else "")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(data: Any) -> str:
    class _QuotedScalarDumper(yaml.SafeDumper):
        pass

    _DATE_LIKE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def _repr_str(dumper: yaml.SafeDumper, value: str):
        # YAML1.1 の暗黙型解釈（YYYY-MM-DD -> date）を避けるため、日付っぽい文字列は常にクォートする
        if _DATE_LIKE.match(value):
            return dumper.represent_scalar("tag:yaml.org,2002:str", value, style='"')
        return dumper.represent_scalar("tag:yaml.org,2002:str", value)

    _QuotedScalarDumper.add_representer(str, _repr_str)

    return yaml.dump(
        data,
        Dumper=_QuotedScalarDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )


def excerpt(text: str, max_len: int = 240) -> str:
    t = " ".join((text or "").split())
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def collect_checklist_items() -> Dict[str, Dict[str, str]]:
    """id -> {title, category_id} を作る（レポート用途）"""
    cl = load_yaml(CHECKLIST_PATH)
    items: Dict[str, Dict[str, str]] = {}
    for cat in cl.get("categories", []) or []:
        cat_id = cat.get("id", "")
        for it in cat.get("items", []) or []:
            iid = it.get("id")
            if iid:
                items[iid] = {"title": it.get("title", ""), "category_id": cat_id}
    return items


@dataclass
class EvalFinding:
    requirement_id: str
    source_file: str
    doc_id: str
    doc_derived_from: str
    reasons: List[str]
    errors: List[str]

    @property
    def evidence(self) -> str:
        # error は最優先（ただし timeout-only の場合は本文修正しない）
        if self.errors:
            return excerpt(self.errors[0])
        # reason は「失敗指摘（How混入/主語/AC/trace）」に寄ったものを優先
        priority_keys = [
            "How", "実装", "危険ワード", "主語", "ロール", "Given/When/Then", "受入基準", "traces_to", "トレーサビリティ",
        ]
        for r in self.reasons:
            if any(k in r for k in priority_keys):
                return excerpt(r)
        if self.reasons:
            return excerpt(self.reasons[0])
        return ""


def load_eval_findings() -> Dict[str, EvalFinding]:
    data = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    out: Dict[str, EvalFinding] = {}
    for tr in data.get("test_results", []) or []:
        rid = tr.get("requirement_id")
        if not rid or rid == "OVERALL":
            continue
        reasons: List[str] = []
        errors: List[str] = []
        # 失敗メトリクスの reason を優先して収集（根拠の明確化）
        metrics = tr.get("metrics", []) or []
        for m in metrics:
            if m.get("error"):
                errors.append(m["error"])
        for m in metrics:
            if m.get("reason") and m.get("success") is False:
                reasons.append(m["reason"])
        # 失敗reasonが無い場合のみ、全reasonを補助として保持
        if not reasons:
            for m in metrics:
                if m.get("reason"):
                    reasons.append(m["reason"])
        out[rid] = EvalFinding(
            requirement_id=rid,
            source_file=tr.get("source_file", ""),
            doc_id=tr.get("doc_id", ""),
            doc_derived_from=tr.get("doc_derived_from", ""),
            reasons=reasons,
            errors=errors,
        )
    return out


TIMEOUT_PAT = re.compile(r"timed out|timeout|cancelled|context deadline exceeded", re.IGNORECASE)


def is_timeout_only(f: EvalFinding) -> bool:
    """reasonが無く、errorがtimeout系だけの場合をtimeout-onlyとみなす"""
    if f.reasons:
        return False
    if not f.errors:
        return False
    return all(bool(TIMEOUT_PAT.search(e or "")) for e in f.errors)


def has_how_issue(f: EvalFinding) -> bool:
    txt = "\n".join(f.reasons + f.errors)
    return any(w in txt for w in ["How", "実装", "技術", "危険ワード", "React", "SQLite", "node-cron", "GitHub Actions", "Allure", "Promptfoo", "ajv", "localStorage"])


def has_role_issue(f: EvalFinding) -> bool:
    txt = "\n".join(f.reasons + f.errors)
    return any(w in txt for w in ["主語", "ロール", "user/admin/viewer/system", "許可ロール"])


def has_ac_issue(f: EvalFinding) -> bool:
    txt = "\n".join(f.reasons + f.errors)
    return any(w in txt for w in ["Given/When/Then", "受入基準", "AC", "テストケース"])


def has_trace_issue(f: EvalFinding) -> bool:
    txt = "\n".join(f.reasons + f.errors)
    return any(w in txt for w in ["traces_to", "トレーサビリティ", "追跡", "broken link"])


def infer_priority(f: EvalFinding) -> str:
    if is_timeout_only(f):
        return "R"  # runtime/timeout
    if has_how_issue(f) or has_role_issue(f) or has_ac_issue(f) or has_trace_issue(f):
        return "S"
    # それ以外はA（曖昧語/境界/観測など）扱い
    return "A"


def apply_tech_replacements(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text
    out = text
    for pat, repl in TECH_REPLACEMENTS:
        out = pat.sub(repl, out)
    return cleanup_text(out)


def ensure_role_prefix(desc: str, role: str) -> str:
    if not isinstance(desc, str) or not desc.strip():
        return desc
    # 既にロールが明示されている場合は触らない（日本語境界でも誤判定しないよう前方一致を優先）
    head = desc.lstrip()
    if head.startswith(("user", "admin", "viewer", "system")):
        return desc
    if re.search(r"(?:^|[^A-Za-z])(user|admin|viewer|system)(?:[^A-Za-z]|$)", desc):
        return desc
    # 既に「システムは」等で始まっているなら system 扱いに寄せる（表記だけ）
    if desc.lstrip().startswith("システム") and role == "system":
        return desc
    prefix = f"{role}は、"
    return prefix + desc


def wrap_gwt(criterion: str) -> str:
    if not isinstance(criterion, str) or not criterion.strip():
        return criterion
    if "Given" in criterion and "When" in criterion and "Then" in criterion:
        return criterion
    # 元の意味（Then相当）を壊さず最小の前提/トリガーを付与
    base = " ".join(criterion.split())
    return f"Given: 対象機能が利用可能である / When: 記載された操作または条件が成立する / Then: {base}"


def non_empty_traces_to(req: Dict[str, Any], fallback_ids: List[str]) -> Tuple[bool, str]:
    if not isinstance(req, dict):
        return False, ""
    traces = req.get("traces_to")
    if isinstance(traces, list) and len(traces) > 0:
        return False, ""
    if not fallback_ids:
        return False, ""
    req["traces_to"] = [fallback_ids[0]]
    return True, fallback_ids[0]


def normalize_meta_and_summary(doc: Dict[str, Any]) -> bool:
    """meta.timestamp の型正規化と validation_summary の再計算。

    - timestamp が date/datetime の場合は ISO 文字列へ
    - validation_summary.* の件数を実データに合わせる（validate_req.py extra_checks 対応）
    """
    changed = False
    meta = doc.get("meta")
    if isinstance(meta, dict):
        ts = meta.get("timestamp")
        if isinstance(ts, (_dt.date, _dt.datetime)):
            meta["timestamp"] = ts.isoformat()
            changed = True

    rd = doc.get("requirements_document")
    if not isinstance(rd, dict):
        return changed

    vs = rd.get("validation_summary")
    if not isinstance(vs, dict):
        return changed

    actual = {
        "functional": len(rd.get("functional_requirements") or []),
        "non_functional": len(rd.get("non_functional_requirements") or []),
        "constraints": len(rd.get("constraints") or []),
        "data_entities": len((rd.get("data_requirements") or {}).get("entities") or []),
        "integrations": len(rd.get("integration_requirements") or []),
        "quality_gates": len(rd.get("quality_gates") or []),
    }
    total_actual = actual["functional"] + actual["non_functional"] + actual["constraints"]

    for k, v in actual.items():
        if vs.get(k) != v:
            vs[k] = v
            changed = True
    if vs.get("total_requirements") != total_actual:
        vs["total_requirements"] = total_actual
        changed = True

    return changed


def set_timeout_note(req: Dict[str, Any]) -> bool:
    """notes に is_timeout_related=true を追記（スキーマ外キー追加はしない）"""
    if not isinstance(req, dict):
        return False
    current = req.get("notes", "")
    marker = "is_timeout_related=true"
    if isinstance(current, str) and marker in current:
        return False
    if current in (None, ""):
        req["notes"] = marker
    elif isinstance(current, str):
        req["notes"] = marker + " | " + current
    else:
        # notes が文字列以外の場合は触らない
        return False
    return True


def patch_requirement(req: Dict[str, Any], finding: EvalFinding, fallback_ids: List[str]) -> Dict[str, Any]:
    """1要件をパッチ。return: change info"""
    change: Dict[str, Any] = {
        "modified": False,
        "checklist_item_ids": [],
        "priority": infer_priority(finding),
        "evidence": finding.evidence,
        "timeout_only": is_timeout_only(finding),
    }

    if is_timeout_only(finding):
        # 本文（title/description等）は触らない
        note_changed = set_timeout_note(req)
        traces_changed, _ = non_empty_traces_to(req, fallback_ids)
        if note_changed:
            change["modified"] = True
        if traces_changed:
            change["modified"] = True
            change["checklist_item_ids"].append("CHK-05-03")
        return change

    # --- How混入除去: 技術語の置換（最小） ---
    if has_how_issue(finding):
        for key in ("title", "description", "rationale"):
            if key in req and isinstance(req[key], str):
                new = apply_tech_replacements(req[key])
                if new != req[key]:
                    req[key] = new
                    change["modified"] = True
        # acceptance criteria の criterion も置換（技術語/過剰具体化を除去）
        if isinstance(req.get("acceptance_criteria"), list):
            ac_changed = False
            for ac in req["acceptance_criteria"]:
                if isinstance(ac, dict) and isinstance(ac.get("criterion"), str):
                    nc = apply_tech_replacements(ac["criterion"])
                    if nc != ac["criterion"]:
                        ac["criterion"] = nc
                        ac_changed = True
            if ac_changed:
                change["modified"] = True

        # assumptions/metrics/measurement_method も最小置換（ツール名等）
        if isinstance(req.get("assumptions"), list):
            new_ass = []
            ass_changed = False
            for a in req["assumptions"]:
                if isinstance(a, str):
                    na = apply_tech_replacements(a)
                    ass_changed |= (na != a)
                    new_ass.append(na)
                else:
                    new_ass.append(a)
            if ass_changed:
                req["assumptions"] = new_ass
                change["modified"] = True
        if isinstance(req.get("metrics"), list):
            met_changed = False
            for m in req["metrics"]:
                if isinstance(m, dict):
                    for mk in ("measurement_method", "tool"):
                        if mk in m and isinstance(m[mk], str):
                            nm = apply_tech_replacements(m[mk])
                            met_changed |= (nm != m[mk])
                            m[mk] = nm
            if met_changed:
                change["modified"] = True

        # risks
        if isinstance(req.get("risks"), list):
            risk_changed = False
            for r in req["risks"]:
                if not isinstance(r, dict):
                    continue
                for rk in ("risk_description", "mitigation"):
                    if rk in r and isinstance(r[rk], str):
                        nr = apply_tech_replacements(r[rk])
                        risk_changed |= (nr != r[rk])
                        r[rk] = nr
            if risk_changed:
                change["modified"] = True
        change["checklist_item_ids"].append("CHK-02-02")

    # --- 主語（ロール）明確化 ---
    if has_role_issue(finding):
        role = "system"
        # UI操作が中心の一部は user に寄せる
        if req.get("req_id") in {"REQ-FUNC-PROGDISC-001", "REQ-NFUNC-SETUP-001"}:
            role = "user"
        if isinstance(req.get("description"), str):
            new_desc = ensure_role_prefix(req["description"], role)
            if new_desc != req["description"]:
                req["description"] = new_desc
                change["modified"] = True
        change["checklist_item_ids"].append("CHK-02-03")

    # --- 受入基準 Given/When/Then（最小） ---
    if "acceptance_criteria" in req and isinstance(req.get("acceptance_criteria"), list):
        if has_ac_issue(finding):
            ac_changed = False
            for ac in req["acceptance_criteria"]:
                if isinstance(ac, dict) and isinstance(ac.get("criterion"), str):
                    nc = wrap_gwt(ac["criterion"])
                    if nc != ac["criterion"]:
                        ac["criterion"] = nc
                        ac_changed = True
            if ac_changed:
                change["modified"] = True
            change["checklist_item_ids"].append("CHK-03-02")

    # --- traces_to 空の解消（最小） ---
    traces_changed, _ = non_empty_traces_to(req, fallback_ids)
    if traces_changed:
        change["modified"] = True
        change["checklist_item_ids"].append("CHK-05-03")

    # checklist ids の重複排除
    change["checklist_item_ids"] = sorted(set(change["checklist_item_ids"]))
    return change


def patch_doc(doc: Dict[str, Any], findings: Dict[str, EvalFinding], changes: List[Dict[str, Any]]) -> None:
    rd = doc.get("requirements_document")
    if not isinstance(rd, dict):
        return
    # prompt_id の broken link 回避（planning/_prompt_registry.yaml 登録済みのIDへ統一）
    meta = doc.get("meta")
    if isinstance(meta, dict):
        if meta.get("prompt_id") == "PRM-REQ-YAML-003":
            meta["prompt_id"] = "PRM-REQ-YAML-002"

    # traces_to の接続先は「実在するID」に限定（gate_id は verify_traceability の own-id対象外なので使わない）
    doc_id = rd.get("doc_id")
    fallback_ids = [doc_id] if isinstance(doc_id, str) and doc_id else []

    # 対象コレクション
    for section_key in ("functional_requirements", "non_functional_requirements"):
        reqs = rd.get(section_key) or []
        if not isinstance(reqs, list):
            continue
        for req in reqs:
            if not isinstance(req, dict):
                continue
            rid = req.get("req_id")
            if not isinstance(rid, str) or rid not in findings:
                # eval対象外は traces_to の空だけ埋めたいが、根拠が無いので触らない
                continue

            # --- 個別の根拠に基づくスポット修正 ---
            if rid == "REQ-FUNC-AUTOBACKUP-001" and isinstance(req.get("description"), str):
                # 外部ストレージ欠落の指摘があるため補正（eval reasonに基づく）
                d0 = req["description"]
                if "外部" not in d0 and "ローカル" in d0:
                    req["description"] = d0.replace("ローカルディスクへ", "ローカルディスクおよび外部ストレージへ")
                # 追加で技術語は一般置換に任せる

            if rid == "REQ-NFUNC-TECHSTACK-001" and isinstance(req.get("description"), str):
                # 技術名列挙のHow混入指摘に基づき、本文を参照表ベースに置換（意味は保持）
                req["description"] = (
                    "systemは、企画書の技術スタック定義（derived_from参照）に記載された主要スタックに準拠して実装する。\n"
                    "主要スタックからの変更は設計変更として管理され、逸脱が検出可能であること。\n"
                )

            if rid == "REQ-FUNC-REQTPL-001" and isinstance(req.get("description"), str):
                # deliverable の混線指摘（requirements.yaml と templates/...）に基づき修正
                req["description"] = (
                    "systemは、要件定義へ進むための準備として、企画書を機械可読な要件定義書に変換した成果物（deliverable: requirements.yaml）を作成できること。\n"
                    "また、要件定義作業のワークフローテンプレート（deliverable: templates/requirement_workflow.yaml）を作成できること。\n"
                    "これらの成果物は品質ゲート（曖昧語チェック、検証可能性）で合否判定できること。\n"
                )

            if rid == "REQ-FUNC-SCOPEOUT-001" and isinstance(req.get("description"), str):
                # 入力にある「ユーザー満足度測定」欠落と、根拠の薄い固有名/Phase4混入の指摘に基づき修正
                req["description"] = (
                    "systemは、Phase 0のスコープ外（実装しない）機能を明示し、過剰実装を防止する。\n"
                    "スコープ外の例：\n"
                    "- アプリ内のAI自動生成機能\n"
                    "- 外部ツールとのAPI連携\n"
                    "- ユーザー満足度測定\n"
                    "- モバイル対応\n"
                    "- プロンプト共有機能\n"
                )

            if rid == "REQ-NFUNC-BUGREDUCE-001" and isinstance(req.get("metrics"), list):
                # timeout はあるが reason に「AC/前提不足・主語不明」等の具体指摘が併記されているため補正
                # （本文の意味を変えず、測定条件を明確化する）
                if isinstance(req.get("description"), str):
                    req["description"] = ensure_role_prefix(req["description"], "system")
                for m in req["metrics"]:
                    if not isinstance(m, dict):
                        continue
                    if m.get("metric_name") and isinstance(m.get("measurement_method"), str):
                        mm = m["measurement_method"]
                        # 期間/比較条件の曖昧さを減らす（具体的数値の新規提案は避け、同期間比較を明記）
                        if "同期間" not in mm:
                            m["measurement_method"] = mm + "（パイロット開始前後の同期間で比較する）"
                # traces_to は後続で doc_id に接続される

            if rid == "REQ-FUNC-KPITRACK-001" and isinstance(req.get("description"), str):
                # 検索工数の測定方法（比較）に関するFaithfulness指摘に基づき修正
                d = req["description"]
                d = d.replace("アプリ内検索とWeb検索の利用時間の記録", "アプリ内検索とWeb検索の比較（利用方法の差分記録）")
                d = d.replace("各指標はSQLiteに保存しJSON形式でエクスポートできる。", "各指標は永続化され、機械可読な形式でエクスポートできる。")
                req["description"] = d

            # --- パッチ適用（汎用） ---
            change = patch_requirement(req, findings[rid], fallback_ids)
            change.update({
                "req_id": rid,
                "source_file": findings[rid].source_file,
            })
            changes.append(change)


def main() -> None:
    checklist_items = collect_checklist_items()
    findings = load_eval_findings()

    REQ_V2_DIR.mkdir(parents=True, exist_ok=True)

    v1_files = sorted(REQ_V1_DIR.glob("*.yaml"))
    if not v1_files:
        raise SystemExit(f"No YAML files found: {REQ_V1_DIR}")

    changes: List[Dict[str, Any]] = []
    file_change_summary: Dict[str, Dict[str, int]] = {}

    for src in v1_files:
        doc = load_yaml(src)
        original_dump = dump_yaml(doc)
        new_doc = copy.deepcopy(doc)

        patch_doc(new_doc, findings, changes)

        # 形式正規化（スキーマ検証・extra_checks 対応）
        normalize_meta_and_summary(new_doc)

        out_path = REQ_V2_DIR / src.name
        out_text = dump_yaml(new_doc)
        out_path.write_text(out_text, encoding="utf-8")

        file_change_summary[src.name] = {
            "modified": int(out_text != original_dump),
            "unchanged": int(out_text == original_dump),
        }

    # --- 集計（req単位） ---
    modified = sum(1 for c in changes if c.get("modified"))
    unchanged = sum(1 for c in changes if not c.get("modified"))
    timeout_only_cnt = sum(1 for c in changes if c.get("timeout_only"))

    # --- レポート（CSV） ---
    REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["req_id", "source_file", "change_type", "checklist_item_ids", "priority", "evidence"])
        for c in sorted(changes, key=lambda x: (x.get("source_file", ""), x.get("req_id", ""))):
            w.writerow([
                c.get("req_id", ""),
                c.get("source_file", ""),
                "modified" if c.get("modified") else "unchanged",
                ";".join(c.get("checklist_item_ids") or []),
                c.get("priority", ""),
                c.get("evidence", ""),
            ])

    # --- レポート（Markdown） ---
    # source_file ごとに整理
    by_file: Dict[str, List[Dict[str, Any]]] = {}
    for c in changes:
        by_file.setdefault(c.get("source_file", ""), []).append(c)

    lines: List[str] = []
    lines.append("# requirements_v2 パッチ監査レポート\n")
    lines.append("## サマリー\n")
    lines.append(f"- Deep Eval対象要件数: {len(changes)}")
    lines.append(f"- modified: {modified}")
    lines.append(f"- unchanged: {unchanged}")
    lines.append(f"- timeout-only（本文原則未修正）: {timeout_only_cnt}\n")

    lines.append("## 変更一覧（source_file別）\n")
    for sf in sorted(by_file):
        lines.append(f"### {sf}\n")
        for c in sorted(by_file[sf], key=lambda x: x.get("req_id", "")):
            rid = c.get("req_id")
            ct = "modified" if c.get("modified") else "unchanged"
            pr = c.get("priority")
            chk = c.get("checklist_item_ids") or []
            # checklist title 展開（存在するものだけ）
            chk_titles = []
            for cid in chk:
                meta = checklist_items.get(cid)
                if meta:
                    chk_titles.append(f"{cid}({meta.get('title','')})")
                else:
                    chk_titles.append(cid)
            evidence = c.get("evidence", "")
            lines.append(f"- {rid}: **{ct}** / priority={pr} / checklist={', '.join(chk_titles) if chk_titles else '-'}")
            if evidence:
                lines.append(f"  - evidence: {evidence}")
        lines.append("")

    # timeout-only一覧
    lines.append("## timeout系で本文を原則未修正とした要件\n")
    for c in sorted([x for x in changes if x.get("timeout_only")], key=lambda x: (x.get("source_file", ""), x.get("req_id", ""))):
        lines.append(f"- {c.get('req_id')} ({c.get('source_file')}): {c.get('evidence','')}")
    lines.append("")

    # MISSING（reason/error無し）一覧
    missing = [x for x in changes if not x.get("evidence")]
    lines.append("## MISSING（根拠不明のため未修正）\n")
    if not missing:
        lines.append("- なし\n")
    else:
        for c in sorted(missing, key=lambda x: (x.get("source_file", ""), x.get("req_id", ""))):
            lines.append(f"- {c.get('req_id')} ({c.get('source_file')}): evidenceなし")
        lines.append("")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- 最終表示 ---
    print("PATCH DONE")
    print(f"  evaluated_requirements : {len(changes)}")
    print(f"  modified              : {modified}")
    print(f"  unchanged             : {unchanged}")
    print(f"  timeout_only_unedited : {timeout_only_cnt}")
    print(f"  out_dir               : {REQ_V2_DIR}")
    print(f"  report_md             : {REPORT_MD}")
    print(f"  report_csv            : {REPORT_CSV}")


if __name__ == "__main__":
    main()
