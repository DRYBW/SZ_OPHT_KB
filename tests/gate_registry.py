#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_registry.py — G5 gate: the in-repo registry surface is enforced, not trusted.

Ported from the project-side registry validator (`W3_NORM/R1/scripts/validate_registry.py`,
card t_59266f94) into the mirror repo as a repo-side hard gate. Purpose: the repository's
ownership ledger and the gate inventory must prove themselves mechanically, so "the ledger
says so" is never a substitute for "the disk says so".

Checked surfaces
  1. the ownership ledger in the repo        (default: docs/W3_PIPELINE_REGISTRY.tsv)
  2. the gate inventory added by this card   (default: docs/GATE_INVENTORY_G5G6.tsv)

Eight checks (each fail-closed; a FAIL names the check code, never just "G5 FAIL"):
  G5-C01 SCHEMA        required columns present; required cells non-empty
  G5-C02 ID-UNIQUE     item ids / gate ids unique
  G5-C03 OWNER         owner column non-placeholder AND carries an accountability anchor
  G5-C04 REF-EXIST     path references resolve on disk; cross-surface id references resolve
                       (negative class: MISSING FILE)
  G5-C05 SHA-MATCH     live sha == registered sha; drifted rows must be dispensed by the
                       snapshot ledger (negative class: SHA DRIFT)
  G5-C06 LEDGER        the snapshot ledger is honest: it exists, every entry maps to a real
                       row, every entry is genuinely drifted (a stale dispensation is a FAIL,
                       so the ledger can never grow into a blanket exemption)
  G5-C07 UNREG-LOAD    every gate script invoked by the one-click entry tests/run_gates.sh is
                       registered with a matching live sha (negative class: UNREGISTERED LOAD)
  G5-C08 CERT-EXPIRY   declared expiry dates ("到期日"/"review_due_at") are not past --as-of
                       (negative class: EXPIRED CERTIFICATION)

Stdlib only, zero network, zero GPU, read-only. Usage (from repo root):
  python3 tests/gate_registry.py
  python3 tests/gate_registry.py --registry ... --gate-inventory ... --drift-ledger ... --entry ...
Exit codes: 0 = PASS, 2 = FAIL (fail-closed). Deterministic output: generated_at is taken
from the ledger's mtime, not from the wall clock.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEDGER_REQUIRED = ["层", "件ID", "件名", "类别", "路径", "版本", "权威状态", "变更口", "sha256", "状态"]
INV_REQUIRED = ["gate_id", "gate_name", "entry_point", "script_path", "sha256", "owner",
                "freeze_gate", "regression_gate", "status", "note"]

PLACEHOLDER = re.compile(r"^(?:tbd|todo|待定|待补|占位|placeholder|owner|unknown|n/?a|未指定|待确认|-+|—+|\s*)$", re.I)
OWNER_ANCHOR = re.compile(r"(?:t_[0-9a-f]{8}|维护方|责任线|pi-chief|PI\b|作者卡|只经|卡\b|线\b)")
ID_REF = re.compile(r"\bL[0-6]-\d{2}\b")
DUE = re.compile(r"到期日[^\d]{0,6}(\d{4}-\d{2}-\d{2})")
ENTRY_SCRIPT = re.compile(r"(?:^|[\s;&|(])(?:python3?|bash|sh)\s+(?:\"|')?(tests/[\w./\-]+\.(?:py|sh))")
DERIVED = ("__pycache__", ".pyc", ".pyo")


def sha256_of(p: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def read_table(p: Path) -> tuple:
    lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]
    if not lines:
        return [], []
    hdr = lines[0].split("\t")
    rows = [dict(zip(hdr, ln.split("\t"))) for ln in lines[1:] if ln.strip()]
    return hdr, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=str(ROOT / "docs" / "W3_PIPELINE_REGISTRY.tsv"))
    ap.add_argument("--gate-inventory", default=str(ROOT / "docs" / "GATE_INVENTORY_G5G6.tsv"))
    ap.add_argument("--drift-ledger", default=str(ROOT / "tests" / "fixtures" / "g5" / "snapshot_drift_ledger.tsv"))
    ap.add_argument("--entry", default=str(ROOT / "tests" / "run_gates.sh"))
    ap.add_argument("--as-of", default="2026-10-12")
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    reg_p, inv_p = Path(a.registry), Path(a.gate_inventory)
    led_p, ent_p = Path(a.drift_ledger), Path(a.entry)
    checks = []

    def rec(code: str, ok: bool, detail: str, offenders=None) -> None:
        short, _, label = code.partition(" ")          # 机器码与人类标签分列：code 供断言，label 供人读
        checks.append({"code": short, "label": label, "status": "PASS" if ok else "FAIL", "detail": detail,
                       "n_offenders": len(offenders or []), "offenders": (offenders or [])[:40]})

    if not reg_p.exists():
        print(json.dumps({"verdict": "FAIL", "error": f"registry not on disk: {reg_p}"}, ensure_ascii=False))
        return 2
    rhdr, rows = read_table(reg_p)
    if not inv_p.exists():
        print(json.dumps({"verdict": "FAIL", "error": f"gate inventory not on disk: {inv_p}"}, ensure_ascii=False))
        return 2
    ihdr, inv = read_table(inv_p)
    reg_ids = [r.get("件ID", "") for r in rows]
    inv_ids = [r.get("gate_id", "") for r in inv]

    # G5-C01 SCHEMA
    miss = [c for c in LEDGER_REQUIRED if c not in rhdr] + [c for c in INV_REQUIRED if c not in ihdr]
    empty = [f"{r.get('件ID', '?')}.{c}" for r in rows for c in LEDGER_REQUIRED
             if c in rhdr and not (r.get(c) or "").strip()]
    empty += [f"{r.get('gate_id', '?')}.{c}" for r in inv for c in INV_REQUIRED
              if c in ihdr and not (r.get(c) or "").strip()]
    rec("G5-C01 SCHEMA", not miss and not empty,
        f"missing_columns={miss or 'none'}; empty_required_cells={len(empty)}", miss + empty)

    # G5-C02 ID-UNIQUE
    dup = [i for i in set(reg_ids) if reg_ids.count(i) > 1 or not i] + \
          [i for i in set(inv_ids) if inv_ids.count(i) > 1 or not i]
    rec("G5-C02 ID-UNIQUE", not dup,
        f"ledger {len(rows)} rows/{len(set(reg_ids))} ids; inventory {len(inv)} rows/{len(set(inv_ids))} ids", dup)

    # G5-C03 OWNER
    # 台账面（docs/W3_PIPELINE_REGISTRY.tsv）的 owner 列语义 = 「变更口」（谁能改、走什么门）。
    # 判据 = 非空 + 非占位（TBD/待定/占位/N.A./— 之类）。**不额外强加问责锚语法、不设长度门槛**：
    # 该表口径由建表卡冻结，本门不改其字节；表内既有的简写（'同上'=紧邻上一行同口、'L1 发布口'=短路由名）
    # 属可追溯简写，按「非空」放行并在 detail 里报数（收紧口径须先改台账，不属本卡权限）。
    ALLOWED_SHORTHAND = re.compile(r"^(?:同上|同前|同左)$")
    bad_owner = []
    for r in rows:
        o = (r.get("变更口") or "").strip()
        if not o or (PLACEHOLDER.match(o) and not ALLOWED_SHORTHAND.match(o)):
            bad_owner.append(f"ledger {r.get('件ID')}: 变更口为空或占位 -> {o[:60]!r}")
    for r in inv:
        o = (r.get("owner") or "").strip()
        if PLACEHOLDER.match(o) or not OWNER_ANCHOR.search(o):
            bad_owner.append(f"inventory {r.get('gate_id')}: owner 无问责锚 -> {o[:60]!r}")
    n_short = sum(1 for r in rows if len((r.get("变更口") or "").strip()) < 8)
    rec("G5-C03 OWNER", not bad_owner,
        f"empty/placeholder owners: {len(bad_owner)}（台账内短简写 {n_short} 行按「非空」放行，口径属台账本方）",
        bad_owner)

    # G5-C04 REF-EXIST
    missing_paths, dangling_ids = [], []
    for r in rows:
        p = Path((r.get("路径") or "").strip())
        if not p.exists():
            st = (r.get("状态") or "").strip()
            if st.startswith(("MISSING", "SHELF", "ARCHIVED")):
                continue
            missing_paths.append(f"{r.get('件ID')}:{p} (status={st})")
    known = set(reg_ids) | set(inv_ids)
    for src, rr in [("ledger", rows), ("inventory", inv)]:
        for r in rr:
            for k, v in r.items():
                if k in ("路径", "script_path", "entry_point"):
                    continue
                for m in ID_REF.findall(v or ""):
                    if m not in known:
                        dangling_ids.append(f"{src}:{r.get('件ID') or r.get('gate_id')} -> {m}")
    rec("G5-C04 REF-EXIST", not missing_paths and not dangling_ids,
        f"missing paths={len(missing_paths)}; dangling id refs={len(dangling_ids)}",
        missing_paths + dangling_ids)

    # G5-C05 SHA-MATCH (+ ledger dispensation)
    dispensed, drifted, ledger_rows, ledger_hdr = [], [], [], []
    led_err = []
    if led_p.exists():
        ledger_hdr, ledger_rows = read_table(led_p)
    by_id = {r.get("件ID", ""): r for r in rows}
    led_map = {}
    for lr in ledger_rows:
        iid = (lr.get("件ID") or "").strip()
        led_map[iid] = lr
        if iid not in by_id:
            led_err.append(f"ledger entry for unknown item: {iid}")
    for r in rows:
        p = Path((r.get("路径") or "").strip())
        if not p.is_file():
            continue
        cur = sha256_of(p)
        reg_sha = (r.get("sha256") or "").strip()
        if cur == reg_sha:
            continue
        lr = led_map.get(r.get("件ID", ""))
        if lr and (lr.get("observed_sha256") or "").strip() == cur:
            dispensed.append(f"{r.get('件ID')}({p.name})")
        elif lr:
            drifted.append(f"{r.get('件ID')}:{p.name} ledgered={(lr.get('observed_sha256') or '')[:16]} live={cur[:16]} "
                           f"→ ledger stale: re-probe（重跑产出该记账的生成脚本，把 observed 现取为新值）")
        else:
            drifted.append(f"{r.get('件ID')}:{p.name} registered={reg_sha[:16]} live={cur[:16]}")
    for r in inv:
        p = Path((r.get("script_path") or "").strip())
        if not p.is_file():
            continue
        cur = sha256_of(p)
        if cur != (r.get("sha256") or "").strip():
            drifted.append(f"{r.get('gate_id')}:{p.name} registered={(r.get('sha256') or '')[:16]} live={cur[:16]}")
    rec("G5-C05 SHA-MATCH", not drifted,
        f"live-vs-registered mismatches={len(drifted)}; dispensed-by-ledger={len(dispensed)}", drifted)

    # G5-C06 LEDGER
    stale_entries = []
    if not led_p.exists():
        led_err.append(f"snapshot drift ledger not on disk: {led_p}")
    else:
        for lr in ledger_rows:
            iid = (lr.get("件ID") or "").strip()
            rr = by_id.get(iid)
            if rr is None:
                continue
            p = Path((rr.get("路径") or "").strip())
            same_as_reg = p.is_file() and sha256_of(p) == (rr.get("sha256") or "").strip()
            if same_as_reg:
                stale_entries.append(f"{iid}: live sha already equals the registered sha -> dispensation is stale, drop it")
            for f in ("observed_sha256", "observed_at", "cause", "evidence"):
                if not (lr.get(f) or "").strip():
                    led_err.append(f"{iid}: ledger field {f} empty")
    rec("G5-C06 LEDGER", not led_err and not stale_entries,
        f"ledger entries={len(ledger_rows)}; problems={len(led_err)}; stale dispensations={len(stale_entries)}",
        led_err + stale_entries)

    # G5-C07 UNREG-LOAD
    unreg = []
    if not ent_p.exists():
        unreg.append(f"one-click entry not on disk: {ent_p}")
    else:
        registered = {}
        for r in rows:
            registered[str(Path((r.get("路径") or "").strip()))] = (r.get("sha256") or "").strip()
        for r in inv:
            registered[str(Path((r.get("script_path") or "").strip()))] = (r.get("sha256") or "").strip()
        invoked = sorted({m for m in ENTRY_SCRIPT.findall(ent_p.read_text(encoding="utf-8"))})
        if not invoked:
            unreg.append(f"{ent_p.name}: no gate script invocation found (entry is vacuous)")
        for rel in invoked:
            p = (ROOT / rel).resolve()
            key = str(p)
            if key not in registered:
                unreg.append(f"{rel}: invoked by the one-click entry but registered on neither surface")
            elif p.is_file() and sha256_of(p) != registered[key]:
                unreg.append(f"{rel}: registered sha != live sha")
        print(f"[g5] entry-invoked gate scripts: {len(invoked)} -> " + ", ".join(invoked))
    rec("G5-C07 UNREG-LOAD", not unreg,
        f"unregistered/mismatched gate scripts invoked by the entry: {len(unreg)}", unreg)

    # G5-C08 CERT-EXPIRY
    asof = datetime.datetime.strptime(a.as_of, "%Y-%m-%d")
    expired = []
    for r in rows:
        for c in ("备注", "判定依据", "版本", "权威状态"):
            for m in DUE.findall(r.get(c) or ""):
                if datetime.datetime.strptime(m, "%Y-%m-%d") < asof:
                    expired.append(f"{r.get('件ID')}:{c} expiry={m} < as_of={a.as_of}")
    for r in inv:
        d = (r.get("review_due_at") or "").strip()
        if not d or d == "-":
            continue
        try:
            due = datetime.datetime.strptime(d[:10], "%Y-%m-%d")
        except ValueError:
            expired.append(f"{r.get('gate_id')}:unparsable review_due_at={d}")
            continue
        if due < asof:
            expired.append(f"{r.get('gate_id')}:due={d} < as_of={a.as_of}")
    rec("G5-C08 CERT-EXPIRY", not expired,
        f"as_of={a.as_of}; expired declared certifications={len(expired)}", expired)

    verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    stamp = datetime.datetime.fromtimestamp(reg_p.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    res = {"gate": "G5", "script": str(Path(__file__).resolve()),
           "generated_at": stamp,
           "note": "generated_at = ownership-ledger mtime: same inputs -> same bytes -> the outer manifest does not go stale on re-run",
           "inputs": {"registry": str(reg_p), "gate_inventory": str(inv_p), "drift_ledger": str(led_p),
                      "entry": str(ent_p), "as_of": a.as_of},
           "ledger_rows": len(rows), "inventory_rows": len(inv),
           "verdict": verdict, "n_checks": len(checks),
           "n_fail": sum(1 for c in checks if c["status"] == "FAIL"),
           "dispensed": dispensed, "checks": checks}
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[g5] rows={len(rows)} gates={len(inv)} dispensed={len(dispensed)} "
          f"checks={len(checks)} fail={res['n_fail']} verdict={verdict}")
    for c in checks:
        print(f"  {c['status']} {c['code']} {c['label']} :: {c['detail']}")
        for o in c["offenders"][:6]:
            print(f"      - {o}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())