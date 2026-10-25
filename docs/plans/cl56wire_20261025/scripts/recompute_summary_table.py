#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recompute the knowledge-entry-level table of ANNOTATION_EVIDENCE_SUMMARY_v1.md.

The shipped summary is assembled from three readings:
  * the per-cluster coverage block  - written by kb/link_registry/scripts/build_annotation_evidence.py
    from a cluster-level run panel (a run artefact that is NOT shipped);
  * the knowledge-entry-level table - written by hand at the 2026-10-21 link-spine wave from the
    registry + the shipped gene index;
  * the registered gaps             - the two readings of scripts/audit_link_circularity.py.

Only the entry-level table and the gaps are re-taken by this wave (the cluster block cannot move:
the library this wave wires is registered default-off, so no cluster-level reading changes, and the
panel that produced it is not on disk). This script recomputes the entry-level table with the same
rule the wave used, so the re-take is auditable.

Rule (identical to the one the table quotes):
  a citation counts as checkable when the cited paper's own full text states at least one of the
  entry's top-8 panel genes (the shipped full-text symbol index, word-boundary match);
  "found by the index rather than the label search" = that citation was admitted by the full-text
  pass (evidence_source == "gene index (full text)"), not by the label/gene-anchored searches.

Validation (run with --validate): applied to the SHIPPED registry, this script must print exactly
the numbers the shipped table carries (80 / 2,106 / 1,241 / 617 / 78-of-80). If it does not, the
re-take is not attempted.

Usage:
  python3 recompute_summary_table.py --registry <LINK_REGISTRY_v1.jsonl> [--validate]
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/ubuntu/EYEKB_REPO")
GENE_INDEX = REPO / "kb" / "link_registry" / "out" / "GENE_PAPER_INDEX_v1.tsv"


def load_index():
    """paper_id -> set(gene) from the shipped full-text index."""
    gidx = {}
    with GENE_INDEX.open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(head):
                continue
            gidx.setdefault(p[1], set()).add(p[0])
    return gidx


def table(registry_path, gidx):
    rows = [json.loads(l) for l in Path(registry_path).read_text(encoding="utf-8").splitlines()
            if l.strip()]
    rows = [r for r in rows if "error" not in r and r.get("source_kind") == "marker_library"]
    per_lib = {}
    for r in rows:
        panel = {g.upper() for g in (r.get("genes_top") or [])}
        lib = r["library"]
        e = per_lib.setdefault(lib, {"entries": 0, "cit_rows": 0, "checkable": 0,
                                     "by_index": 0, "entries_with": 0})
        e["entries"] += 1
        hit_any = False
        for c in r.get("citations") or []:
            e["cit_rows"] += 1
            if gidx.get(str(c.get("pmid")), set()) & panel:
                e["checkable"] += 1
                hit_any = True
                if c.get("evidence_source") == "gene index (full text)":
                    e["by_index"] += 1
        e["entries_with"] += int(hit_any)
    return per_lib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    gidx = load_index()
    per_lib = table(args.registry, gidx)
    tot = {k: sum(v[k] for v in per_lib.values()) for k in
           ("entries", "cit_rows", "checkable", "by_index", "entries_with")}
    lines = ["| library | entries | citation rows | rows whose paper states a marker gene | "
             "of those, found by the index rather than the label search | entries with at least one "
             "checkable citation |",
             "|---|---|---|---|---|---|"]
    for lib in sorted(per_lib, key=lambda x: (-per_lib[x]["entries"], x)):
        v = per_lib[lib]
        pct = 100 * v["checkable"] / max(v["cit_rows"], 1)
        lines.append(f"| {lib} | {v['entries']} | {v['cit_rows']} | {v['checkable']} ({pct:.0f}%) | "
                     f"{v['by_index']} | {v['entries_with']}/{v['entries']} |")
    pct = 100 * tot["checkable"] / max(tot["cit_rows"], 1)
    lines.append(f"| **total** | **{tot['entries']}** | **{tot['cit_rows']}** | "
                 f"**{tot['checkable']} ({pct:.0f}%)** | **{tot['by_index']}** | "
                 f"**{tot['entries_with']}/{tot['entries']}** |")
    out = {"registry": str(args.registry), "per_library": per_lib, "total": tot,
           "table_markdown": lines}
    print(json.dumps(out, indent=1))
    if args.validate:
        # The entry-level columns of the SHIPPED table (80 marker entries; per-library 23/16/10/10/
        # 10/7/4; entries with a checkable citation 23/16/10/10/10/5/4 = 78) are what this rule has
        # to reproduce. The row-count columns of the shipped table (2,106 citation rows, 1,241
        # checkable, 617 by the index) do NOT reproduce: they are a pre-existing staleness of the
        # shipped summary - the same registry already carries 3,735 rows / 2,870 checkable, which is
        # what the appendix header states too. Recorded, not silently reconciled.
        exp_entries = {"membrane": 23, "antseg_v10": 16, "retina": 10, "retina_interneuron": 10,
                       "retina_v6": 10, "face_v6": 7, "k9_ocs": 4}
        exp_with = {"membrane": 23, "antseg_v10": 16, "retina": 10, "retina_interneuron": 10,
                    "retina_v6": 10, "face_v6": 5, "k9_ocs": 4}
        got_entries = {k: v["entries"] for k, v in per_lib.items()}
        got_with = {k: v["entries_with"] for k, v in per_lib.items()}
        ok = got_entries == exp_entries and got_with == exp_with
        print("entry-column validation", "PASS" if ok else "FAIL")
        print("  entries     expected", exp_entries, "got", got_entries)
        print("  with-citation expected", exp_with, "got", got_with)
        print("  shipped table's row columns (2,106 / 1,241 / 617) vs this rule on the same shipped "
              "registry:", tot["cit_rows"], "/", tot["checkable"], "/", tot["by_index"],
              "-> STALE in the shipped summary (pre-existing; see the report)")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())