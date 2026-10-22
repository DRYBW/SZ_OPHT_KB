#!/usr/bin/env python3
"""Golden regression on real production queries (721 clusters x 28 volumes).

For every cluster in the 2026-10-18 production evidence reports, the report recorded the
query (top_genes) AND the ranking the production code returned at that moment. Re-running
query_marker today must reproduce that ranking exactly when the guard is OFF (and also when
it is ON, because the production panels contain no composite entries).

This is the strongest available identity test: real queries, real recordings, no synthetic data.

Usage: python golden_721.py [out.json]
"""
import glob
import json
import os
import sys

sys.path.insert(0, "/home/ubuntu/EYEKB_REPO/mcp_server")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import eyekb_core as core  # noqa: E402

BASE = "/mnt/D/EyeKB/plans/oss_check_20261019"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{BASE}/scorer_guard_20261020/golden_721_result.json"


def clusters():
    for p in sorted(glob.glob(f"{BASE}/dl/results/*/annotation_evidence_report.json")):
        vol = p.split("/")[-2]
        d = json.load(open(p))
        species = ((d.get("inputs") or {}).get("species") or "").strip().lower()
        for c in d.get("clusters", []):
            km = c.get("kb_marker") or {}
            rec = km.get("celltype_ranking") or []
            # Replay the RAW-CASE gene list (top_genes), not kb_marker.query: the recorded query is
            # post-uppercase, and the cross-species governance layer decides from raw case
            # (title_frac). Feeding the normalized list would silently turn mouse volumes into
            # "human_assumed" and break identity for the wrong reason.
            genes = c.get("top_genes") or km.get("query") or []
            if genes:
                yield vol, str(c.get("cluster")), genes, rec, species


def now_ranking(genes, species):
    # the production call carried the volume's species (mouse volumes are refused by the
    # cross-species governance layer, which is why their recorded ranking is empty)
    kw = {"genes": list(genes), "library": "all"}
    if species in ("mouse", "human"):
        kw["species"] = species
        kw["volume_species"] = species
        kw["volume_id"] = f"golden_probe_{species}"
    r = core.query_marker(**kw)
    return r.get("celltype_ranking") or [], "composite_demoted" in r


def main():
    stats = {"off": {"n": 0, "identical": 0, "differ": 0, "examples": []},
             "on": {"n": 0, "identical": 0, "differ": 0, "n_with_demoted": 0, "examples": []}}
    for vol, cl, genes, rec, species in clusters():
        rec_pairs = [(x["cell_type"], x["n_shared"]) for x in rec]
        os.environ.pop("EYEKB_KB_ANTIUNION", None)
        off_rank, off_key = now_ranking(genes, species)
        off_pairs = [(x["cell_type"], x["n_shared"]) for x in off_rank]
        s = stats["off"]
        s["n"] += 1
        if off_pairs == rec_pairs and not off_key:
            s["identical"] += 1
        else:
            s["differ"] += 1
            if len(s["examples"]) < 5:
                s["examples"].append({"vol": vol, "cluster": cl,
                                      "recorded_n": len(rec_pairs), "now_n": len(off_pairs),
                                      "recorded_head": rec_pairs[:3], "now_head": off_pairs[:3]})

        os.environ["EYEKB_KB_ANTIUNION"] = "1"
        on_rank, on_key = now_ranking(genes, species)
        os.environ.pop("EYEKB_KB_ANTIUNION", None)
        on_pairs = [(x["cell_type"], x["n_shared"]) for x in on_rank]
        s = stats["on"]
        s["n"] += 1
        if on_key:
            s["n_with_demoted"] += 1
        if on_pairs == rec_pairs:
            s["identical"] += 1
        else:
            s["differ"] += 1
            if len(s["examples"]) < 5:
                s["examples"].append({"vol": vol, "cluster": cl,
                                      "recorded_head": rec_pairs[:3], "now_head": on_pairs[:3]})

    doc = {"probe": "golden_721.py",
           "source": "dl/results/*/annotation_evidence_report.json (recorded 2026-10-18)",
           "note": "recorded ranking = production output at generation time, before this change",
           "stats": stats}
    json.dump(doc, open(OUT, "w"), ensure_ascii=False, indent=1)
    for k, s in stats.items():
        print(f'{k.upper():>3}: n={s["n"]}  identical_to_2026-10-18={s["identical"]}  '
              f'differ={s["differ"]}  with_composite_demoted={s.get("n_with_demoted", "-")}')
        for e in s["examples"]:
            print("   DIFF", e)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
