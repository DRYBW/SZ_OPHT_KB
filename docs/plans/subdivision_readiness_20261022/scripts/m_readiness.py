#!/usr/bin/env python3
"""Step 2: assemble the per-parent subdivision_readiness table, the tier assignment, and the
output-shape emission (Annex A + the frozen pre-registration).

One row per shipped parent class (76). Per-pair detail is kept in full. Nothing is activated.
"""
import collections
import csv
import json
import sys

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"
DICT = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json"

T1, T1K, T2, T3 = "T1", "T1k", "T2", "T3"


def main():
    obo = cl_nav.load(OBO)
    terms = obo["terms"]
    desc_cache = {}

    def desc_of(cid):
        if cid not in desc_cache:
            desc_cache[cid] = set(cl_nav.descendants(cid, OBO))
        return desc_cache[cid]

    parents = json.load(open(f"{OUT}/S1_parents_context.json"))
    depth = {r["class"]: r for r in json.load(open(f"{OUT}/R1R2_parent_depth.json"))}
    occ = json.load(open(f"{OUT}/S5_occurrence.json"))
    genes = json.load(open(f"{OUT}/S5_genes.json"))
    contrast = json.load(open(f"{OUT}/S5_contrast_cooccurrence.json"))
    window = json.load(open(f"{OUT}/O_observable_window.json"))
    state = json.load(open(f"{OUT}/O_state_reference.json"))
    state_ratio = json.load(open(f"{OUT}/O_state_ratio.json"))
    state_dep = set(state_ratio["state_dependent_by_cutoff"]["0.75"])
    import re as _re
    PROGEN_TOKENS = ["progenitor", "precursor", "blast", "stem cell", "transit amplifying"]
    _PROGEN_RX = _re.compile(r"\b(?:" + "|".join(_re.escape(t) for t in PROGEN_TOKENS) + r")\b")
    kids_map = collections.defaultdict(list)
    for _tid, _t in terms.items():
        for _pa in _t.get("is_a") or []:
            kids_map[_pa].append(_tid)

    def dist_to(root, term):
        if not root or not term:
            return 99
        if term == root:
            return 0
        q = collections.deque([(root, 0)])
        seen = {root}
        while q:
            cur, dep = q.popleft()
            if dep > 6:
                continue
            for ch in kids_map.get(cur, []):
                if ch in seen:
                    continue
                if ch == term:
                    return dep + 1
                seen.add(ch)
                q.append((ch, dep + 1))
        return 99
    material = json.load(open(f"{OUT}/M_non_evaluation_material.json"))
    dic = json.load(open(DICT))
    labels = dic["labels"]

    win_vocab = set(window["gene_frequency"] and
                    [g for g, _ in window["gene_frequency"]])
    state_genes = set(state["state_reference_genes"])
    state_cc = (set(state["dictionary_proliferation_genes"])
                | set(state["corpus_arms"]["cell_cycle"]["genes"]))

    # shipped class identity, for the `already_shipped_as_own_class` scope class
    shipped_ids, shipped_names = {}, {}
    for lab, m in labels.items():
        if m.get("cl_id"):
            shipped_ids.setdefault(m["cl_id"], []).append(lab)
        shipped_names[lab.lower()] = lab
        if m.get("cl_label"):
            shipped_names[str(m["cl_label"]).lower()] = lab

    # non-evaluation datasets, with a disclosed secondary flag for prior-exam material
    ds_list = []
    for p, r in material["datasets"].items():
        if not r.get("resolved_cl_ids"):
            continue
        flag = (("exam" in p.lower()) or ("/evalset/" in p.lower()) or ("gold" in p.lower()))
        ds_list.append({"path": p, "ids": set(r["resolved_cl_ids"]),
                        "n_labels": r["n_labels_resolved"], "n_obs": r.get("n_obs"),
                        "prior_exam": flag})

    pair_rows, parent_rows, emission = [], [], {}

    for P in parents:
        par = P["parent"]
        dr = depth.get(par) or {}
        children = P["children"]
        child_cids = {}
        for c in children:
            for tid, t in terms.items():
                if t.get("name") == c:
                    child_cids[c] = tid
                    break

        # --- positive gene sets per child, then parent-shared genes (ruling C2) -----------------
        pos = {}
        for c in children:
            g = genes.get(f"{par}\t{c}")
            pos[c] = set((g or {}).get("positive") or {})
        shared_count = collections.Counter()
        for c in children:
            for g in pos[c]:
                shared_count[g] += 1
        parent_shared = {g for g, n in shared_count.items() if n >= 2}

        def pair_contrast(a, b):
            key = "\t".join(sorted([a, b]))
            return contrast.get(key) or []

        # --- per pair --------------------------------------------------------------------------
        pairs = []
        for c in children:
            o = occ.get(f"{par}\t{c}") or {}
            n_studies = o.get("n_studies_in_context", 0)
            n_chunks = o.get("n_chunks_in_context", 0)
            n_any = o.get("n_chunks_any_context", 0)
            cid = child_cids.get(c)
            scope = "in_scope_adult_celltype"
            siblings = [x for x in children if x != c]
            if cid and len(shipped_ids.get(cid, [])) > 0:
                others = [l for l in shipped_ids[cid] if l != par]
                if others or c.lower() in shipped_names and shipped_names[c.lower()] != par:
                    scope = "already_shipped_as_own_class"
            if scope == "in_scope_adult_celltype":
                plow = (str(P["cl_label"] or "") + " " + par).lower()
                if _PROGEN_RX.search(plow):
                    scope = "developmental_axis"
                elif P["stage"] == "fetal_developing":
                    scope = "developmental_axis"
                elif P["system"] == "organoid_or_ipsc":
                    scope = "system_axis_organoid_or_ipsc"

            # nearest sibling by positive-set overlap
            rank_sib = []
            for s in siblings:
                ov = len(pos[c] & pos[s])
                rank_sib.append((s, ov, dist_to(cid, child_cids.get(s))))
            rank_sib.sort(key=lambda x: (-x[1], x[2], x[0]))
            nearest = rank_sib[0][0] if rank_sib else None
            nearest_ov = rank_sib[0][1] if rank_sib else 0
            disc = sorted(pos[c] - (pos[nearest] if nearest else set()) - parent_shared)
            if not pos[c]:
                disc = []
            cset = ({cid} | desc_of(cid)) if cid else set()
            cohorts = [d for d in ds_list if d["ids"] & cset]
            cohorts_clean = [d for d in cohorts if not d["prior_exam"]]
            ctr = pair_contrast(c, nearest) if nearest else []
            n_sources = n_studies + len(cohorts)
            n_obs = len(set(disc) & win_vocab)
            sfrac = (len(set(disc) & state_dep) / len(disc)) if disc else None
            sfrac_cc = (len(set(disc) & state_cc) / len(disc)) if disc else None
            n_state_dep = len(set(disc) & state_dep)

            rec = {
                "parent": par, "parent_cl": P["cl_id"], "child": c, "child_cl": cid,
                "scope_class": scope, "stage": P["stage"], "system": P["system"],
                "n_chunks_any_context": n_any, "n_chunks_in_context": n_chunks,
                "n_studies_in_context": n_studies,
                "n_cohorts_non_evaluation": len(cohorts),
                "n_cohorts_non_evaluation_no_prior_exam": len(cohorts_clean),
                "n_indep_sources": n_sources,
                "has_adjacent_type_contrast": bool(ctr),
                "contrast_papers": ctr,
                "nearest_sibling": nearest, "n_shared_with_nearest_sibling": nearest_ov,
                "n_parent_shared_genes_removed": len(parent_shared & pos[c]),
                "n_positive_genes": len(pos[c]),
                "n_discriminating_positive_genes": len(disc),
                "discriminating_genes": disc[:60],
                "state_fraction_union": (round(sfrac, 4) if sfrac is not None else None),
                "n_state_dependent_discriminating_genes": n_state_dep,
                "state_fraction_cellcycle": (round(sfrac_cc, 4) if sfrac_cc is not None else None),
                "n_observable_in_recorded_window": n_obs,
                "cohort_paths": [d["path"] for d in cohorts][:20],
            }
            # ---- tier -------------------------------------------------------------------------
            reason = None
            n_pos = len(pos[c])
            separates_any = False
            for sx in siblings:
                if pos[c] - (pos[sx] | parent_shared):
                    separates_any = True
                    break
            if scope == "already_shipped_as_own_class":
                tier, reason = "excluded", "already_shipped_as_own_class"
            elif scope != "in_scope_adult_celltype":
                tier, reason = "excluded", scope
            elif not P["cl_id"]:
                tier, reason = T3, "no_ontology_term"
            elif not children:
                tier, reason = T3, "leaf_term"
            elif not dr.get("n_descendant_names_resolve"):
                tier, reason = T3, "ontology_thin"
            elif n_any == 0:
                tier, reason = T3, "never_mentioned"
            elif n_chunks == 0:
                tier, reason = T3, "outside_declared_context"
            elif n_pos < 2:
                tier, reason = T2, "needs_deeper_panel_genes"
            elif sfrac is not None and sfrac >= 0.50:
                tier, reason = T3, "state_programme_only"
            elif not separates_any:
                tier, reason = T3, "spectrum_only"
            elif len(disc) < 2 or n_sources < 2 or not ctr:
                tier, reason = T2, "needs_deeper_panel_genes"
            elif n_obs < 2:
                tier, reason = T2, "needs_wider_window"
            elif not cohorts:
                tier, reason = T1K, "knowledge_subdividable_only"
            else:
                tier, reason = T1, "available_now"
            rec["tier"], rec["reason"] = tier, reason
            pairs.append(rec)

        # --- parent row ------------------------------------------------------------------------
        elig = [p for p in pairs if p["tier"] in (T1, T1K, T2, T3)]
        rank = {T1: 0, T1K: 1, T2: 2, T3: 3}
        elig.sort(key=lambda p: (rank[p["tier"]], -p["n_indep_sources"],
                                 -p["n_discriminating_positive_genes"], p["child"]))
        best = elig[0] if elig else None
        passing = [p for p in pairs if p["tier"] in (T1, T1K)]

        status, reasons = "parent_only", []
        if not P["cl_id"]:
            status, reasons = "parent_abstain", ["no resolvable ontology term for this class"]
        elif not passing:
            status = "parent_only"
            rs = collections.Counter(p["reason"] for p in pairs)
            reasons = [f"{k}:{v}" for k, v in rs.most_common(4)] or ["no subclass candidate carries evidence"]
        else:
            worst = 0.0
            for i, a in enumerate(passing):
                for b in passing[i + 1:]:
                    da, db = set(a["discriminating_genes"]), set(b["discriminating_genes"])
                    denom = max(1, min(len(da), len(db)))
                    worst = max(worst, len(da & db) / denom)
            if len(passing) >= 2 and worst >= 0.50:
                status, reasons = "subtype_ambiguous", [f"pairwise discriminating-set overlap {worst:.2f} >= 0.50"]
            else:
                status = "subtype_suggested"
                reasons = [f"{p['child']} ({p['tier']}, {p['reason']})" for p in passing]

        emission[par] = {
            "parent_candidates": [{"class": par, "cl_id": P["cl_id"], "cl_label": P["cl_label"]}],
            "subtype_suggestions_by_parent": {
                par: [{"class": p["child"], "cl_id": p["child_cl"], "tier": p["tier"],
                       "n_discriminating_positive_genes": p["n_discriminating_positive_genes"],
                       "has_adjacent_type_contrast": p["has_adjacent_type_contrast"],
                       "n_indep_sources": p["n_indep_sources"]} for p in passing]},
            "resolution_status": status,
            "review_reasons": reasons,
        }

        parent_rows.append({
            "parent": par, "cl_id": P["cl_id"], "cl_label": P["cl_label"],
            "stage": P["stage"], "system": P["system"],
            "tissue_scope": "|".join(P["tissues"]) or "undeclared",
            "tissue_source": P.get("tissue_source"),
            "ontology_depth_descendants": dr.get("n_is_a_descendants"),
            "ontology_depth_names_resolved": dr.get("n_descendant_names_resolve"),
            "n_children_candidates": len(children),
            "n_children_with_any_occurrence": sum(1 for p in pairs if p["n_chunks_any_context"] > 0),
            "n_children_with_2plus_sources": sum(1 for p in pairs if p["n_indep_sources"] >= 2),
            "best_child": best["child"] if best else None,
            "best_child_cl": best["child_cl"] if best else None,
            "best_tier": best["tier"] if best else None,
            "best_reason": (best["reason"] if best else
                            ("no_ontology_term" if not P["cl_id"] else
                             ("leaf_term" if not children else "no_candidate_child"))),
            "occ_in_target_context": (best["n_chunks_in_context"] > 0) if best else False,
            "occ_studies": best["n_studies_in_context"] if best else 0,
            "occ_chunks": best["n_chunks_in_context"] if best else 0,
            "occ_chunks_any_context": best["n_chunks_any_context"] if best else 0,
            "n_indep_studies": best["n_studies_in_context"] if best else 0,
            "n_indep_cohorts": best["n_cohorts_non_evaluation"] if best else 0,
            "n_indep_sources": best["n_indep_sources"] if best else 0,
            "has_adjacent_type_contrast": best["has_adjacent_type_contrast"] if best else False,
            "n_discriminating_positive_genes": best["n_discriminating_positive_genes"] if best else 0,
            "nearest_sibling": best["nearest_sibling"] if best else None,
            "state_fraction_union": best["state_fraction_union"] if best else None,
            "state_programme_dependent": (best["state_fraction_union"] is not None
                                          and best["state_fraction_union"] >= 0.50) if best else None,
            "n_observable_in_recorded_window": best["n_observable_in_recorded_window"] if best else 0,
            "observable_in_current_window": (best["n_observable_in_recorded_window"] >= 2) if best else False,
            "n_non_eval_datasets_best_child": best["n_cohorts_non_evaluation"] if best else 0,
            "resolution_status": status,
            "review_reasons": "; ".join(reasons),
            "n_pairs_T1": sum(1 for p in pairs if p["tier"] == T1),
            "n_pairs_T1k": sum(1 for p in pairs if p["tier"] == T1K),
            "n_pairs_T2": sum(1 for p in pairs if p["tier"] == T2),
            "n_pairs_T3": sum(1 for p in pairs if p["tier"] == T3),
            "n_pairs_excluded_scope": sum(1 for p in pairs if p["tier"] == "excluded"),
        })
        pair_rows.extend(pairs)

    # ---- outputs ---------------------------------------------------------------------------
    json.dump(parent_rows, open(f"{OUT}/subdivision_readiness.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pair_rows, open(f"{OUT}/pair_table.json", "w"), ensure_ascii=False, indent=1)
    json.dump(emission, open(f"{OUT}/output_shape_emission.json", "w"), ensure_ascii=False, indent=1)

    cols = list(parent_rows[0].keys())
    with open(f"{OUT}/subdivision_readiness.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in parent_rows:
            w.writerow(r)
    pcols = list(pair_rows[0].keys())
    with open(f"{OUT}/pair_table.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=pcols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in pair_rows:
            w.writerow({k: ("|".join(v) if isinstance(v, list) else v) for k, v in r.items()})

    tc = collections.Counter(p["tier"] for p in pair_rows)
    sc = collections.Counter(p["scope_class"] for p in pair_rows)
    st = collections.Counter(r["resolution_status"] for r in parent_rows)
    print(f"parents={len(parent_rows)}  pairs={len(pair_rows)}")
    print("tier distribution:", dict(tc))
    print("scope distribution:", dict(sc))
    print("resolution_status:", dict(st))
    print("\ntop parents by best tier:")
    for r in sorted(parent_rows, key=lambda r: (str(r["best_tier"]), -r["n_indep_sources"]))[:20]:
        print(f"   {r['parent']:24s} {str(r['best_tier']):4s} {str(r['best_child'])[:38]:38s} "
              f"studies={r['n_indep_studies']:>3} disc={r['n_discriminating_positive_genes']:>3} "
              f"obs={r['n_observable_in_recorded_window']:>2} coh={r['n_indep_cohorts']}")


if __name__ == "__main__":
    main()