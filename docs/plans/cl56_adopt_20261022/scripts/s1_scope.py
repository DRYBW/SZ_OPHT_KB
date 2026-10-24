# -*- coding: utf-8 -*-
"""s1_scope.py -- apply the PRE-REGISTERED scope rule (PREREG §4) to the 25 corpus-supported pairs.

Read-only against the frozen inputs. Writes out/SCOPE.json + out/SCOPE.tsv.
The rule is fixed in the pre-registration document; this script only applies it.

  (a) child term resolves in the frozen snapshot, active, STRICT is_a descendant of ours_cl
  (b) corpus_support_status in {corpus_states_the_term, corpus_states_a_synonym_only}
  (c1) >= 1 recorded cluster whose ref_cell_type is literally the child term
  (c2) panel = pair's discriminating_genes (I8) INTERSECT assay vocab (I11) ; >= 2 genes
  (c3) >= 1 demand cluster whose recorded window (I1) shares >= 2 genes with that panel

Run: /usr/bin/python3 s1_scope.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
CLD = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021"
SUB = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OSS = "/mnt/D/EyeKB/plans/oss_check_20261019"
ANT = "/mnt/D/EyeKB/plans/antseg_fill_20261020"
OBO = "/home/ubuntu/EYEKB_REPO/kb/ontology/cl/releases/2026-06-08/cl-base.obo"
sys.path.insert(0, os.path.join(WAVE, "scripts"))
sys.path.insert(0, "/mnt/D/EyeKB/plans/noregr_20261022/scripts")
import wave_common as W  # noqa: E402


def load_obo():
    terms, cur = {}, None
    with open(OBO, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                cur = {}
                continue
            if line.startswith("[") and line.endswith("]"):
                cur = None
                continue
            if cur is None or ":" not in line:
                continue
            k, v = line.split(":", 1)
            v = v.strip()
            if k == "id":
                cur["id"] = v
                terms[v] = cur
            elif k == "name":
                cur["name"] = v
            elif k == "is_obsolete":
                cur["obsolete"] = (v == "true")
            elif k == "is_a":
                # strip the trailing "! comment" AND the qualifier, e.g. {is_inferred="true"} --
                # 662 of this release's is_a lines carry it and the predecessor wave's gate A3
                # (and its four-way relation reads) include those edges. Not stripping it silently
                # drops most of the closure.
                parent = v.split("!")[0].strip()
                parent = parent.split("{")[0].strip()
                cur["is_a"] = cur.get("is_a", []) + [parent]
    return terms


def shipped_entries_by_cl(repo):
    """cl_id -> [(library, class_name, n_genes)] over the shipped marker bodies (informational)."""
    import glob
    out = {}
    for p in sorted(glob.glob(os.path.join(repo, "kb/markers/*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for e in (d.get("entries") or []):
            if isinstance(e, dict) and e.get("cl_id"):
                out.setdefault(e["cl_id"], []).append(
                    (os.path.basename(p), e.get("class_name"), len(e.get("markers") or [])))
    return out


def ancestors(terms, cid):
    seen, stack = set(), [cid]
    while stack:
        x = stack.pop()
        t = terms.get(x)
        if not t:
            continue
        for p in (t.get("is_a") or []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen


def main():
    cand = json.load(open(os.path.join(CLD, "out", "CHILD_TERM_CANDIDATES.json")))
    sup = [c for c in cand["candidates"] if c["corpus_support_status"].startswith("corpus_")]
    unsup = [c for c in cand["candidates"] if not c["corpus_support_status"].startswith("corpus_")]

    terms = load_obo()
    shipped = shipped_entries_by_cl("/home/ubuntu/EYEKB_REPO")
    pair_rows = {(r["parent"], r["child_cl"]): r for r in json.load(open(os.path.join(SUB, "out", "pair_table.json")))}
    vocab = set(json.load(open(os.path.join(ANT, "out", "gene_vocab.json"))))

    calls = W.load_set()
    by_key = {(c["vol"], c["cluster"]): c for c in calls}
    demand = {}
    for c in calls:
        demand.setdefault(c["ref_cell_type"].strip(), []).append(c)

    rows, adopted, pending = [], [], []
    for c in sup:
        child_cl, child_label = c["child_cl"], c["child_cl_label"]
        ours_cl, our_label = c["ours_cl"], c["our_labels"]
        rec = {"our_label": our_label, "ours_cl": ours_cl, "child_cl": child_cl,
               "child_label": child_label, "corpus_support_status": c["corpus_support_status"],
               "declared_clusters": c["clusters"], "declared_cells": c["cells"]}
        # (a)
        t = terms.get(child_cl)
        rec["a_term_present"] = bool(t)
        rec["a_obsolete"] = bool(t.get("obsolete")) if t else None
        rec["a_snapshot_label"] = (t.get("name") if t else None)
        rec["a_label_matches_candidate"] = bool(t and (t.get("name") or "").strip() == child_label.strip())
        anc = ancestors(terms, child_cl) if t else set()
        rec["a_is_descendant"] = ours_cl in anc
        rec["a_depth"] = c["is_a_depth"]
        # (b)
        rec["b_supported"] = c["corpus_support_status"].startswith("corpus_")
        # (c1)
        dem = demand.get(child_label.strip(), [])
        rec["c1_demand_clusters"] = len(dem)
        rec["c1_demand_cells"] = sum(x["n_cells"] for x in dem)
        rec["c1_author_label_is_the_term"] = bool(dem) and all(
            x["truth"]["ref_cell_type"].strip() == child_label.strip() for x in dem)
        # (c2)
        pr = pair_rows.get((our_label, child_cl)) or {}
        genes_all = list(pr.get("discriminating_genes") or [])
        panel = sorted({g.upper() for g in genes_all if g.upper() in vocab})
        rec["c2_discriminating_genes_all"] = genes_all
        rec["c2_removed_not_in_assay_vocab"] = sorted({g.upper() for g in genes_all if g.upper() not in vocab})
        rec["panel"] = panel
        rec["c2_n_genes"] = len(panel)
        rec["c2_ok"] = len(panel) >= 2
        rec["readiness_tier"] = pr.get("tier")
        rec["readiness_reason"] = pr.get("reason")
        rec["readiness_obs"] = pr.get("n_observable_in_recorded_window")
        rec["child_already_shipped_as"] = shipped.get(child_cl, [])
        # (c3)
        observable = []
        for x in dem:
            gs = [str(g).upper() for g in x["genes"]]
            sh = sorted(set(gs) & set(panel))
            if len(sh) >= 2:
                observable.append({"vol": x["vol"], "cluster": x["cluster"], "n_cells": x["n_cells"],
                                   "n_shared": len(sh), "shared_genes": sh})
        rec["c3_observable_clusters"] = observable
        rec["c3_ok"] = len(observable) >= 1

        # disposition
        fails = []
        if not (rec["a_term_present"] and not rec["a_obsolete"]):
            fails.append("a_term_missing_or_obsolete")
        elif not rec["a_is_descendant"]:
            fails.append("a_not_a_strict_descendant")
        if not rec["b_supported"]:
            fails.append("b_no_corpus_support")
        if rec["c1_demand_clusters"] < 1:
            fails.append("c1_no_demand_cluster")
        if not rec["c2_ok"]:
            fails.append("c2_below_two_discriminating_genes")
        if not rec["c3_ok"]:
            fails.append("c3_panel_not_observable_in_window")
        rec["fails"] = fails
        rec["adopted"] = (not fails)
        rows.append(rec)
        (adopted if not fails else pending).append(rec)

    rows.sort(key=lambda r: (not r["adopted"], -r["declared_cells"], r["child_label"]))
    doc = {"generated_by": "scripts/s1_scope.py",
           "rule": "PREREG_ADOPT_CL56_20261022.md section 4 (a)+(b)+(c1,c2,c3), fixed before this list",
           "n_corpus_supported": len(sup), "n_adopted": len(adopted), "n_pending": len(pending),
           "n_no_corpus_hit_out_of_scope": len(unsup),
           "adopted_cells": sum(r["c1_demand_cells"] for r in adopted),
           "adopted_clusters": sum(r["c1_demand_clusters"] for r in adopted),
           "rows": rows}
    with open(os.path.join(OUT, "SCOPE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    cols = ["adopted", "our_label", "ours_cl", "child_cl", "child_label", "readiness_tier",
            "readiness_reason", "c1_demand_clusters", "c1_demand_cells", "c2_n_genes",
            "c3_observable_clusters", "fails"]
    with open(os.path.join(OUT, "SCOPE.tsv"), "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) if c != "c3_observable_clusters"
                              else str(len(r["c3_observable_clusters"]))
                              for c in cols) + "\n")
    print("corpus-supported pairs: %d | adopted: %d (%d clusters / %d cells) | pending: %d | no-corpus-hit: %d out of scope"
          % (len(sup), len(adopted), doc["adopted_clusters"], doc["adopted_cells"], len(pending), len(unsup)))
    for r in rows:
        print(" %-1s %-10s %-12s %-38s tier=%-9s demand=%2d cells=%6d genes=%2d obs=%2d  %s"
              % ("A" if r["adopted"] else "-", r["our_label"], r["child_cl"], r["child_label"][:38],
                 r["readiness_tier"], r["c1_demand_clusters"], r["c1_demand_cells"], r["c2_n_genes"],
                 len(r["c3_observable_clusters"]), ",".join(r["fails"])))
    print("wrote out/SCOPE.json / out/SCOPE.tsv")


if __name__ == "__main__":
    main()