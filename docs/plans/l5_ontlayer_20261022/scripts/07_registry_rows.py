#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register (or re-take) this card's rows in the ownership ledger, from live bytes.

    python3 docs/plans/l5_ontlayer_20261022/scripts/07_registry_rows.py            # re-take only
    python3 docs/plans/l5_ontlayer_20261022/scripts/07_registry_rows.py --add      # add the rows

Rules this follows (VERIFY_CONTRACT §5, unchanged):
  * sha256 / bytes / mtime are taken from the live file in this run - never quoted from a report;
  * a row that already exists is re-taken, never duplicated;
  * new artefacts are entered in the ownership table when they are added;
  * repo-surface rows carry repository-relative paths and no absolute path of any machine.

Exit codes: 0 = done; 1 = the ledger is missing a required column (nothing written).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents)
            if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
REG = ROOT / "docs/W3_PIPELINE_REGISTRY.tsv"
INVENTORY = ROOT / "docs/GATE_INVENTORY_G5G6.tsv"
# Files this card changed that another surface already registers by sha. Both surfaces are re-taken
# in the same commit: the ledger's own row, and the gate inventory's row for a file that is a gate's
# entry point (G2 registers docs/VERIFY_CONTRACT.md, which this card appends §5.4 to).
INVENTORY_RETAKE = {"docs/VERIFY_CONTRACT.md": "§5.4 appended: the ontology explanation layer, the "
                                               "two new gates in the one-click entry, the "
                                               "four-layer identity"}

RETAKE = {"README.md": ("L6-06", "README: the Cell Ontology explanation layer section, and the "
                                  "four-layer release identity with its manifest"),
          "docs/VERIFY_CONTRACT.md": ("L6-01", "§5.4: the ontology explanation layer, the two new "
                                               "gates in the one-click entry, and the four-layer "
                                               "identity"),
          "docs/VERSION_NOTES.md": ("L6-07", "version notes for the ontology explanation layer wave "
                                             "(card t_ad7463d9)")}
# (layer, id, name, category, path, version, authority, change_gate, freeze_gate,
#  regression_gate, notes)
NEW = [
    ("L1", "L1-27", "Cell Ontology explanation layer (read-only service module)", "KB 版本件",
     "mcp_server/ontology_layer.py", "ont-layer/1.0",
     "AUTHORITATIVE(service module; registered OFF by default)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json (logical addresses + content hashes)",
     "tests/gate_ontology_layer.py (G7) + tests/gate_ontlayer_portability.py (G8)",
     "Read-only: parses one fixed snapshot, resolves every asset through the manifest, carries no "
     "author-machine absolute path, and contains no write call at all. Four functions: resolve_term "
     "/ get_ancestors / compare_terms / explain_class_mapping. Registered OFF: not imported and not "
     "advertised unless EYEKB_ONT_LAYER names a tool."),
    ("L1", "L1-28", "Cell Ontology snapshot (release 2026-06-08, shipped)", "KB 数据件",
     "kb/ontology/cl/releases/2026-06-08/cl-base.obo", "cl/releases/2026-06-08",
     "AUTHORITATIVE(fixed local snapshot; read-only)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json (sha256 recorded)",
     "tests/gate_ontology_layer.py G7-C01/C02 (anchor + parse)",
     "Shipped so a clean clone answers without the data mount; nothing was downloaded. Read through "
     "the logical address; a wrong hash refuses to answer instead of answering from a placeholder."),
    ("L1", "L1-29", "Ontology capability registration (OFF by default, empty whitelist)",
     "门控配置", "kb/ontology/ONT_LAYER_REGISTRY_v1.json", "v1",
     "AUTHORITATIVE(registration record)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "payload_sha256 sealed over its own canonical content, excluding that field",
     "tests/gate_ontology_layer.py G7-C06 (registration + default tool set)",
     "Declares the capability, its anchors, its failure policy (a missing shipped asset is a FAIL, "
     "never an ENV_ERROR), the granularity rule (blanket ancestor threshold 200, declared before any "
     "comparison) and the stop line."),
    ("L6", "L6-40", "G7 ontology layer gate", "交付工具",
     "tests/gate_ontology_layer.py", "v1 (2026-10-22 first registration)",
     "AUTHORITATIVE(check tool)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "Stated rule = the gate's own nine checks, all mandatory",
     "Invoked by tests/run_gates.sh; registered in docs/GATE_INVENTORY_G5G6.tsv",
     "Nine checks: anchors, snapshot parse, the semantics battery over the real snapshot, a labelled "
     "synthetic unit battery, the two-layer separation, the registration state, the frozen replay "
     "hashes, the three tables and the stop line. Reports should_run/did_run/pass/fail/not_run."),
    ("L6", "L6-41", "G8 ontology layer portability gate", "交付工具",
     "tests/gate_ontlayer_portability.py", "v1 (2026-10-22 first registration)",
     "AUTHORITATIVE(check tool)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "Stated rule = the gate's own six checks, all mandatory",
     "Invoked by tests/run_gates.sh; registered in docs/GATE_INVENTORY_G5G6.tsv",
     "Six checks across three environments (author tree, a temporary working directory, a copy whose "
     "directory name contains spaces): foreign cwd, foreign root, no author absolute paths, "
     "read-only, fail-closed for a missing/altered/unlisted asset, and the gate report shape."),
    ("L6", "L6-42", "Cell Ontology explanation layer contract (reader facing)", "交付文档",
     "docs/ONTOLOGY_LAYER_CONTRACT_v1.md", "v1 (2026-10-22 first registration)",
     "AUTHORITATIVE(reader-facing contract)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "Not frozen (contract document)",
     "Cited by tests/gate_ontology_layer.py and tests/gate_ontlayer_portability.py",
     "What the capability answers, the five buckets, the two records never collapsed, the three "
     "tables, the anchors and their failure policy, how it is reached, the four identity layers and "
     "the stop line."),
    ("L6", "L6-43", "Card record: baseline freeze, tables, replay and the panel settlement",
     "交付记录", "docs/plans/l5_ontlayer_20261022/REPORT.md", "v1 (2026-10-22 first registration)",
     "AUTHORITATIVE(card report)",
     "Same commit as the change (VERIFY_CONTRACT §5)",
     "Frozen inputs under the same directory/out (hashes recorded)",
     "The commands it prints are the ones the gates run",
     "Report of the card that delivered the explanation layer, including the frozen baseline, the "
     "three reporting tables, the recorded-request byte comparison and the panel settlement."),
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", action="store_true")
    a = ap.parse_args()
    lines = REG.read_text(encoding="utf-8").splitlines()
    hdr_i = next(i for i, ln in enumerate(lines) if ln and not ln.startswith("#"))
    hdr = lines[hdr_i].split("\t")
    need = ["layer", "item_id", "item_name", "category", "path", "version", "authority",
            "change_gate", "freeze_gate", "regression_gate", "sha256", "bytes", "mtime", "state",
            "notes", "surface"]
    if not all(c in hdr for c in need):
        print(f"FAIL: the ledger is missing a required column; present={hdr}")
        return 1
    rows = [dict(zip(hdr, ln.split("\t"))) for ln in lines[hdr_i + 1:] if ln.strip()]
    by_path = {r["path"]: r for r in rows}
    ids = {r["item_id"] for r in rows}
    changed = []

    def refill(path: str, notes: str):
        r = by_path[path]
        p = ROOT / path
        r["sha256"] = sha(p)
        r["bytes"] = str(p.stat().st_size)
        r["mtime"] = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        r["state"] = "ON_DISK"
        r["notes"] = (r["notes"].rstrip(" |") + " | " + notes) if r.get("notes") else notes
        changed.append(path)
        return r

    for path, (_iid, note) in RETAKE.items():
        if path not in by_path:
            print(f"FAIL: no ledger row for {path}; nothing written")
            return 1
        refill(path, note)

    if a.add:
        for (layer, iid, name, cat, path, ver, auth, cg, fg, rg, note) in NEW:
            if path in by_path:
                print(f"row already present, not duplicated: {path}")
                continue
            if iid in ids:
                print(f"FAIL: item_id already used: {iid}")
                return 1
            p = ROOT / path
            if not p.is_file():
                print(f"FAIL: new row points at a missing file: {path}")
                return 1
            row = dict.fromkeys(hdr, "")
            row.update({"layer": layer, "item_id": iid, "item_name": name, "category": cat,
                        "path": path, "version": ver, "authority": auth, "change_gate": cg,
                        "freeze_gate": fg, "regression_gate": rg, "sha256": sha(p),
                        "bytes": str(p.stat().st_size),
                        "mtime": datetime.datetime.fromtimestamp(
                            p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "state": "ON_DISK", "notes": note, "surface": "repo"})
            rows.append(row)
            by_path[path] = row
            ids.add(iid)
            changed.append(path)

    out = lines[:hdr_i + 1] + ["\t".join(r.get(c, "") for c in hdr) for r in rows]
    REG.write_text("\n".join(out) + "\n", encoding="utf-8")

    # the gate inventory surface: rows whose script_path is a file this card changed
    ilines = INVENTORY.read_text(encoding="utf-8").splitlines()
    ihdr_i = next(i for i, ln in enumerate(ilines) if ln and not ln.startswith("#"))
    ihdr = ilines[ihdr_i].split("\t")
    irows = [dict(zip(ihdr, ln.split("\t"))) for ln in ilines[ihdr_i + 1:] if ln.strip()]
    for r in irows:
        sp = r.get("script_path", "")
        if sp in INVENTORY_RETAKE:
            p = ROOT / sp
            r["sha256"] = sha(p)
            r["note"] = (r.get("note", "").rstrip(" |") + " ｜ " + INVENTORY_RETAKE[sp]).strip(" ｜")
            changed.append(f"inventory:{sp}")
    INVENTORY.write_text("\n".join(ilines[:ihdr_i + 1]
                                   + ["\t".join(r.get(c, "") for c in ihdr) for r in irows]) + "\n",
                         encoding="utf-8")

    print(f"rows={len(rows)} re-taken/added={len(changed)}")
    for p in changed:
        if p.startswith("inventory:"):
            print(f"  inventory  {p.split(':', 1)[1]}  sha re-taken")
            continue
        r = by_path[p]
        print(f"  {r['item_id']:6s} {p:60s} {r['bytes']:>9s} B  {r['sha256'][:16]}  "
              f"{r['mtime']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())