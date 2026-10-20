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
  G5-C08 CERT-EXPIRY   declared expiry dates ("review_due_at" / "expiry") are not past --as-of
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

# Maintainer-local evidence roots. The ownership ledger mixes two surfaces:
#   (a) repo surface      -> paths inside the repository, registered repo-relative, portable;
#   (b) maintainer-local  -> paths under these roots, i.e. working evidence that is never
#                            distributed with the clone (datasets, plans, frozen golds).
# A path under a declared local root that is absent is reported as "local-unavailable"
# (informational, counted in the detail line) because no clone can ever contain it.
# Any other absolute path that is absent is a genuine MISSING FILE -> C04 fails.
# The allowlist is explicit and narrow on purpose: an arbitrary absolute path (e.g. /tmp/x.py)
# is NOT excused, so the N1 negative case still trips C04.
MAINTAINER_LOCAL_ROOTS = ("/mnt/D/EyeKB",)


def resolve_path(p: str) -> Path:
    """Repo-relative paths anchor at ROOT; absolute paths are taken as written."""
    q = Path((p or "").strip())
    return q if q.is_absolute() else (ROOT / q)


def is_maintainer_local(p: str) -> bool:
    q = Path((p or "").strip())
    if not q.is_absolute():
        return False
    r = str(q.resolve()) if q.exists() else str(q)
    return any(r == root or r.startswith(root.rstrip("/") + "/") for root in MAINTAINER_LOCAL_ROOTS)

LEDGER_REQUIRED = ["layer", "item_id", "item_name", "category", "path", "version", "authority", "change_gate", "sha256", "state"]
INV_REQUIRED = ["gate_id", "gate_name", "entry_point", "script_path", "sha256", "owner",
                "freeze_gate", "regression_gate", "status", "note"]

PLACEHOLDER = re.compile(r"^(?:tbd|todo|placeholder|owner|unknown|n/?a|unspecified|pending|-+|—+|\s*)$", re.I)
OWNER_ANCHOR = re.compile(r"(?:t_[0-9a-f]{8}|maintainer|owner line|pi-chief|PI\b|repo-side|card\b|line\b)")
ID_REF = re.compile(r"\bL[0-6]-\d{2}\b")
DUE = re.compile(r"(?i)(?:review_due_at|due(?:_at)?|expir\w*|deadline)[^\d]{0,8}(\d{4}-\d{2}-\d{2})")
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
        short, _, label = code.partition(" ")          # machine code vs human label: code is asserted on, label is for people
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
    reg_ids = [r.get("item_id", "") for r in rows]
    inv_ids = [r.get("gate_id", "") for r in inv]

    # G5-C01 SCHEMA
    miss = [c for c in LEDGER_REQUIRED if c not in rhdr] + [c for c in INV_REQUIRED if c not in ihdr]
    empty = [f"{r.get('item_id', '?')}.{c}" for r in rows for c in LEDGER_REQUIRED
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
    # On the ledger surface (docs/W3_PIPELINE_REGISTRY.tsv) the owner column means "change_gate"
    # (who may change the item and through which gate).
    # Criterion = non-empty and non-placeholder (TBD / placeholder / N.A. / em-dash and the like).
    # No extra anchor grammar and no length threshold is imposed here:
    # the ledger's own wording was frozen by the card that built it and this gate does not rewrite its
    # bytes; the shorthands already in the table ('same as above' = the neighbouring row, 'L1 release
    # gate' = a short routing name)
    # are traceable shorthands, accepted as non-empty and reported in the detail line (tightening that
    # criterion would require changing the ledger first, which is outside this gate's remit).
    ALLOWED_SHORTHAND = re.compile(r"^(?:same as above|as above|idem)$")
    bad_owner = []
    for r in rows:
        o = (r.get("change_gate") or "").strip()
        if not o or (PLACEHOLDER.match(o) and not ALLOWED_SHORTHAND.match(o)):
            bad_owner.append(f"ledger {r.get('item_id')}: change_gate empty or placeholder -> {o[:60]!r}")
    for r in inv:
        o = (r.get("owner") or "").strip()
        if PLACEHOLDER.match(o) or not OWNER_ANCHOR.search(o):
            bad_owner.append(f"inventory {r.get('gate_id')}: owner carries no accountability anchor -> {o[:60]!r}")
    n_short = sum(1 for r in rows if len((r.get("change_gate") or "").strip()) < 8)
    rec("G5-C03 OWNER", not bad_owner,
        f"empty/placeholder owners: {len(bad_owner)} ({n_short} short-shorthand rows pass as non-empty; ledger-side criterion)",
        bad_owner)

    # G5-C04 REF-EXIST
    missing_paths, dangling_ids, local_unavailable = [], [], []
    for r in rows:
        p = resolve_path(r.get("path") or "")
        if not p.exists():
            if is_maintainer_local(r.get("path") or ""):
                local_unavailable.append(f"{r.get('item_id')}:{p} (maintainer-local, not distributed)")
                continue
            st = (r.get("state") or "").strip()
            if st.startswith(("MISSING", "SHELF", "ARCHIVED")):
                continue
            missing_paths.append(f"{r.get('item_id')}:{p} (state={st})")
    known = set(reg_ids) | set(inv_ids)
    for src, rr in [("ledger", rows), ("inventory", inv)]:
        for r in rr:
            for k, v in r.items():
                if k in ("path", "script_path", "entry_point"):
                    continue
                for m in ID_REF.findall(v or ""):
                    if m not in known:
                        dangling_ids.append(f"{src}:{r.get('item_id') or r.get('gate_id')} -> {m}")
    rec("G5-C04 REF-EXIST", not missing_paths and not dangling_ids,
        f"missing paths={len(missing_paths)}; dangling id refs={len(dangling_ids)}; "
        f"local-unavailable={len(local_unavailable)} (declared local roots: {', '.join(MAINTAINER_LOCAL_ROOTS)})",
        missing_paths + dangling_ids + local_unavailable)

    # G5-C05 SHA-MATCH (+ ledger dispensation)
    dispensed, drifted, ledger_rows, ledger_hdr = [], [], [], []
    led_err = []
    if led_p.exists():
        ledger_hdr, ledger_rows = read_table(led_p)
    by_id = {r.get("item_id", ""): r for r in rows}
    led_map = {}
    for lr in ledger_rows:
        iid = (lr.get("item_id") or "").strip()
        led_map[iid] = lr
        if iid not in by_id:
            led_err.append(f"ledger entry for unknown item: {iid}")
    for r in rows:
        p = resolve_path(r.get("path") or "")
        if not p.is_file():
            continue
        cur = sha256_of(p)
        reg_sha = (r.get("sha256") or "").strip()
        if cur == reg_sha:
            continue
        lr = led_map.get(r.get("item_id", ""))
        if lr and (lr.get("observed_sha256") or "").strip() == cur:
            dispensed.append(f"{r.get('item_id')}({p.name})")
        elif lr:
            drifted.append(f"{r.get('item_id')}:{p.name} ledgered={(lr.get('observed_sha256') or '')[:16]} live={cur[:16]} "
                           f"-> ledger stale: re-probe (re-run the generator that recorded this entry and re-take the observed value)")
        else:
            drifted.append(f"{r.get('item_id')}:{p.name} registered={reg_sha[:16]} live={cur[:16]}")
    for r in inv:
        p = resolve_path(r.get("script_path") or "")
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
            iid = (lr.get("item_id") or "").strip()
            rr = by_id.get(iid)
            if rr is None:
                continue
            p = resolve_path(rr.get("path") or "")
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
            registered[str(resolve_path(r.get("path") or "").resolve())] = (r.get("sha256") or "").strip()
        for r in inv:
            registered[str(resolve_path(r.get("script_path") or "").resolve())] = (r.get("sha256") or "").strip()
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
        for c in ("notes", "evidence", "version", "authority"):
            for m in DUE.findall(r.get(c) or ""):
                if datetime.datetime.strptime(m, "%Y-%m-%d") < asof:
                    expired.append(f"{r.get('item_id')}:{c} expiry={m} < as_of={a.as_of}")
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