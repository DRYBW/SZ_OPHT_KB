#!/usr/bin/env python3
"""What a subdivision would COST the parent (card item 6), re-measured on the recorded 721 clusters.

Follows holefill_v12 REPORT.md section 5's definitions exactly, so the numbers are comparable:
  demand = clusters whose fixed reference is the CHILD term
  gain   = demand clusters that reach the >= 2 shared-gene bar with the CHILD panel while the parent panel cannot
  keep   = clusters the parent answers today that the child panel would still reach
  loss   = clusters the parent answers today that a thinner child panel would lose

Child panels are this wave's literature-derived positive sets (Annex A6); parent panels are the shipped
libraries. This is a probing/regression reading on a fixed set against a fixed reference, NOT validation.
"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
REPO = "/home/ubuntu/EYEKB_REPO"
ALIGN = f"{REPO}/kb/markers/markers_cl_alignment_v2_unified.json"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"
WAVE_MEAS = "/mnt/D/EyeKB/plans/holefill_v12_20261021/out/wave_measurement.json"
RESULTS = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/results"


def shipped_genes_by_cl(cls2cl):
    out = {}
    for p in sorted(glob.glob(f"{REPO}/kb/markers/markers_*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        pairs = []
        if isinstance(d.get("entries"), list):
            for e in d["entries"]:
                if e.get("class_name"):
                    pairs.append((e["class_name"], e.get("markers") or []))
        mk = d.get("markers")
        if isinstance(mk, dict):
            for k, v in mk.items():
                if isinstance(v, list):
                    pairs.append((k, v))
                elif isinstance(v, dict):
                    pairs.append((k, v.get("markers") or []))
        for nm, genes in pairs:
            cid = cls2cl.get(nm)
            if not cid:
                continue
            src = f"{os.path.basename(p)}::{nm}"
            for g in genes:
                out.setdefault(cid, {})[str(g).upper()] = src
    return out


def main():
    obo = cl_nav.load(OBO)
    terms = obo["terms"]
    align = json.load(open(ALIGN))
    cls2cl = {k: (v or {}).get("cl_id") for k, v in (align.get("labels") or {}).items()}
    name2cl = {}
    for tid, t in terms.items():
        if t.get("name"):
            name2cl[t["name"].lower()] = tid
            for s in t.get("synonyms") or []:
                name2cl.setdefault(s.lower(), tid)

    shipped = shipped_genes_by_cl(cls2cl)
    meas = json.load(open(WAVE_MEAS))["per_cluster"]
    stones = json.load(open(f"{WAVE}/out/pair_table.json"))
    occ = json.load(open(f"{WAVE}/out/S5_genes.json"))

    # recorded query windows
    QUERY, TRUTH, BASE = {}, {}, {}
    for vol in sorted(os.listdir(RESULTS)):
        p = os.path.join(RESULTS, vol, "annotation_evidence_report.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for c in d.get("clusters") or []:
            k = f"{vol}|{c.get('cluster')}"
            g = c.get("top_genes") or []
            if g:
                QUERY[k] = [x.upper() for x in g[:10]]
    for k, r in meas.items():
        TRUTH[k] = r.get("truth")
        BASE[k] = r.get("BASE_top")
        if k not in QUERY and r.get("n_cells"):
            pass
    print(f"clusters with a recorded query: {len(QUERY)}  with a truth: {len(TRUTH)}")

    def cl_of_name(x):
        if not x:
            return None
        return name2cl.get(str(x).strip().lower())

    def cl_of_pred(x):
        if not x:
            return None
        lab = str(x).split("::")[-1].strip()
        cid = cls2cl.get(lab) or name2cl.get(lab.lower())
        return cid

    rows = []
    for p in stones:
        par, ch = p["parent"], p["child"]
        pcl, ccl = p["parent_cl"], p["child_cl"]
        pos = (occ.get(f"{par}\t{ch}") or {}).get("positive") or {}
        child_panel = set(sorted(pos, key=lambda g: -pos[g])[:40])
        parent_panel = set(shipped.get(pcl, {}))
        demand = gain = keep = loss = parent_ans = 0
        demand_cells = gain_cells = 0
        for k, genes in QUERY.items():
            gs = set(genes)
            sh_p = len(gs & parent_panel)
            sh_c = len(gs & child_panel)
            tcl = cl_of_name(TRUTH.get(k))
            if tcl == ccl:
                demand += 1
                demand_cells += (meas.get(k) or {}).get("n_cells") or 0
                if sh_c >= 2 and sh_p < 2:
                    gain += 1
                    gain_cells += (meas.get(k) or {}).get("n_cells") or 0
            if cl_of_pred(BASE.get(k)) == pcl:
                parent_ans += 1
                if sh_c >= 2:
                    keep += 1
                else:
                    loss += 1
        rows.append({"parent": par, "parent_cl": pcl, "child": ch, "child_cl": ccl,
                     "tier": p["tier"], "reason": p["reason"],
                     "n_parent_panel_genes": len(parent_panel), "n_child_panel_genes": len(child_panel),
                     "n_child_positive_genes_all": len(pos),
                     "demand_clusters": demand, "demand_cells": demand_cells,
                     "gain_clusters": gain, "gain_cells": gain_cells,
                     "parent_candidate_clusters": parent_ans,
                     "keep_clusters": keep, "loss_clusters": loss,
                     "costly": bool(loss > gain)})

    json.dump(rows, open(f"{OUT}/cost_table.json", "w"), ensure_ascii=False, indent=1)
    import csv
    with open(f"{OUT}/cost_table.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    passing = [r for r in rows if r["tier"] in ("T1", "T1k")]
    print(f"\npairs measured: {len(rows)}   T1/T1k: {len(passing)}")
    print(f"{'parent':14s} {'child':40s} {'demand':>6s} {'gain':>5s} {'keep':>5s} {'loss':>5s}  costly")
    for r in passing:
        print(f"{r['parent'][:14]:14s} {r['child'][:40]:40s} {r['demand_clusters']:>6d} "
              f"{r['gain_clusters']:>5d} {r['keep_clusters']:>5d} {r['loss_clusters']:>5d}  {r['costly']}")
    tot_loss = sum(r["loss_clusters"] for r in passing)
    tot_gain = sum(r["gain_clusters"] for r in passing)
    print(f"\nT1/T1k total: gain={tot_gain} clusters, loss={tot_loss} clusters")
    print("wrote", f"{OUT}/cost_table.json")


if __name__ == "__main__":
    main()