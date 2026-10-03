#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB KB1v2-W1 + KB2c: composition-baseline layer builder (kb/baselines/)

KB2c (t_be336eee, late-night adjudication 2026-09-23, plans/KB2C_ADJUDICATION_20260923.md):
  - Separate developmental axis: every product carries a top-level axis
    organism_stage ∈ {fetal, adult, developing, unknown}
  - adult main tier = donor units with donor_age >= 18y (adjudication Q2); the v1.0 mixed-scope
    tier is demoted to the adult_pool contrast tier — the two tiers keep separate
    entry_id/identity signatures and are never mixed
  - Non-adult donors and unknown sources are disclosed row by row
    (stage_disclosure/excluded_nonadult_units/_STAGE_DISCLOSURE.md) —— silent assignment to
    adult is forbidden (red line 2)
  - fetal/developing are not recomputed; only the transition-state concept entry
    fetal_development_transitions is built (adjudication Q5)

Scope = BRIEF_KB1v2_20260923.md W1 + ASTRA_ANNOTATION_GUIDANCE_v1.md T2:
  - Fractions = donor-level conditional reference distribution (compute each donor's
    composition first, then summarize the between-donor distribution; never pool all cells
    where large donors dominate —— pooled values are shown for contrast only)
  - Stratified display (study × enrichment strategy × sampling region); merge only when
    sufficiently comparable
  - Every entry records at least: sampling_material/disease_stage/treatment_background/
    scRNA vs snRNA/enrichment_step/dissociation_method/donor_count/counting_denominator/evidence_source
  - If the literature is qualitative only, store qualitative; "interval not estimable" is a
    legal state, never pad numbers
  - Usage scope fixed: identity reference + background contrast; never a composition compliance line

输入 (全部只读):
  /mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad  (D001, obs-only)
  /mnt/D/OcularKB/data/D002_ocularsurface/D002_allcells_578K.h5ad   (D002, obs-only)
  /mnt/D/OcularKB/plans/tissue_reference_inventory_20260923/inventory.json  (t_6f5cc731 inventory)
  /mnt/D/EyeKB/kb/priors/composition/human_retina.json              (old KB1 entry; inherits subtypes/states/flags)

Outputs:
  /mnt/D/EyeKB/kb/baselines/baselines.json          (index)
  /mnt/D/EyeKB/kb/baselines/<tissue>.json|.md       (2 filled entries + 9 skeletons, mappings backfilled)

This file is dispatched by t_16c3e020; to change content edit this script and rerun — hand edits to the MD are overwritten.
"""
import json
import sys
import hashlib
import datetime
import re as _re
from pathlib import Path

import h5py
import numpy as np
from collections import Counter, defaultdict

EYEKB = Path("/mnt/D/EyeKB")
OUT_DIR = EYEKB / "kb" / "baselines"
HRCA = "/mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad"
D002 = "/mnt/D/OcularKB/data/D002_ocularsurface/D002_allcells_578K.h5ad"
INVENTORY = "/mnt/D/OcularKB/plans/tissue_reference_inventory_20260923/inventory.json"
OLD_RETINA = EYEKB / "kb/priors/composition/human_retina.json"
GEN = "build_baselines.py (KB1v2 t_16c3e020; KB2c separate developmental axis t_be336eee)"
TODAY = "2026-09-23"

USAGE_SCOPE = ("Usage scope (fixed by the Astra T2 adjudication): this baseline = identity reference + "
               "background contrast for the cellular composition captured from that sampling material under "
               "that experimental workflow; **never a composition compliance line**. The sampling target of "
               "disease surgical material ≠ the healthy organ (e.g. a PDR fibrovascular membrane must not be "
               "acceptance-checked against healthy-retina composition); if annotated data shows an identity "
               "outside the list → raise the unexpected flag only; labels must never be forced into listed "
               "identities (labels undergo context-consistency checks, not whitelist enforcement).")

EVIDENCE_GRADES = {
    "A": "local recomputation from measured data (file paths + script included)",
    "B": "directly reported in the primary literature",
    "C": "empirical intervals derived from donor-level / cross-study distributions of grade-A source data",
    "qualitative": "literature is qualitative only → store qualitative only, never fabricate intervals (Astra T2)",
    "not_estimable": "interval not estimable —— a legal state; annotation can still proceed (Astra T2)",
}


def obs_col(f, k):
    g = f["obs"][k]
    try:
        cats = [x.decode() for x in g["categories"][:]]
        return np.array(cats)[g["codes"][:]]
    except (KeyError, ValueError, TypeError):
        v = g[:]
        return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in v])


def donor_stats(df_rows, classes):
    """df_rows: list of (unit_key, cls). Per-unit composition % → distribution stats across units."""
    per_unit = defaultdict(Counter)
    for u, c in df_rows:
        per_unit[u][c] += 1
    fractions = defaultdict(list)  # cls -> [pct per unit]
    for u, cnt in per_unit.items():
        tot = sum(cnt.values())
        if tot == 0:
            continue
        for c in classes:
            fractions[c].append(100.0 * cnt.get(c, 0) / tot)
    out = {}
    for c in classes:
        arr = np.array(fractions[c])
        out[c] = {
            "n_units": int(len(arr)),
            "median_pct": round(float(np.median(arr)), 2),
            "iqr_pct": [round(float(np.percentile(arr, 25)), 2),
                        round(float(np.percentile(arr, 75)), 2)],
            "range_pct": [round(float(arr.min()), 2), round(float(arr.max()), 2)],
        }
    return out, len(per_unit)


def pct_table(counts, classes):
    tot = sum(counts.values())
    return {c: round(100.0 * counts.get(c, 0) / tot, 2) for c in classes}


# =============================================================================
# KB2c separate developmental axis (t_be336eee, 2026-09-23) — adjudication: plans/KB2C_ADJUDICATION_20260923.md
# PI verbatim: "developmental samples must all be listed separately; fetal ones vs adult ones are
#               not the same even for one and the same tissue"
# Red lines: 1) fetal/developing never merged into the adult main tier
#            2) unknown must be disclosed row by row; silent assignment to adult forbidden
#            3) the threshold (>=18y) is written into product fields; changes require re-adjudication
#            4) completion/blocking is logged to the card
# =============================================================================
ADULT_MIN_YEARS = 18  # adjudication Q2: adult = donor_age >= 18y; changes require re-adjudication
DECADE_WORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
               "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}


def classify_uberon(stage):
    """Map raw UBERON development_stage -> organism_stage 4 levels (adjudication Q1/Q2).
    Returns (cls, rule). Unmapped terms are always unknown + disclosed; guessing adult is
    forbidden (red line 2)."""
    s = (stage or "").strip().lower()
    if not s or s in ("nan", "none", "unknown", "na", ""):
        return "unknown", "empty/missing → unknown (silent adult assignment forbidden)"
    if "organoid" in s:
        return "unknown", "organoid → unknown + flag (adjudication Q1 mapping)"
    if any(t in s for t in ("fetal", "foetal", "embryonic", "embryo", "gestation",
                            "carnegie", "conceptus")):
        return "fetal", "fetal/embryonic term (red line 1: never merged into adult)"
    m = _re.match(r"^(\d+)[-\s]year-old stage$", s)
    if m:
        y = int(m.group(1))
        return (("adult" if y >= ADULT_MIN_YEARS else "developing"),
                f"numeric age {y}y vs threshold {ADULT_MIN_YEARS}y")
    m = _re.match(r"^(\d+)[-\s]year-old and over stage$", s)
    if m:
        y = int(m.group(1))
        return (("adult" if y >= ADULT_MIN_YEARS else "unknown"),
                f"'{y} year-old and over' lower bound >= threshold" if y >= ADULT_MIN_YEARS
                else f"'{y} year-old and over' lower bound straddles threshold → unknown")
    m = _re.match(r"^(\d+)-(\d+)[-\s]year-old stage$", s)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo >= ADULT_MIN_YEARS:
            return "adult", f"age band {lo}-{hi} lower bound >= threshold"
        if hi < ADULT_MIN_YEARS:
            return "developing", f"age band {lo}-{hi} upper bound < threshold"
        return "unknown", f"age band {lo}-{hi} straddles threshold → unknown (no tier call)"
    m = _re.match(r"^(\w+)\s+decade stage$", s)
    if m and m.group(1) in DECADE_WORD:
        lo = (DECADE_WORD[m.group(1)] - 1) * 10
        hi = lo + 9
        if lo >= ADULT_MIN_YEARS:
            return "adult", f"{m.group(1)} decade = {lo}-{hi}y lower bound >= threshold"
        if hi < ADULT_MIN_YEARS:
            return "developing", f"{m.group(1)} decade = {lo}-{hi}y upper bound < threshold"
        return "unknown", f"{m.group(1)} decade = {lo}-{hi}y straddles threshold → unknown"
    if "newborn" in s or "infant" in s:
        return "developing", "newborn/infant early-postnatal → developing (adjudication Q2)"
    if s == "postnatal stage":
        return "developing", "postnatal → developing (adjudication Q1 mapping)"
    if _re.search(r"\b(?:late|prime|middle|old|mature|human)?\s*adult stage\b", s):
        return "adult", "UBERON adult term tier (no numeric age; mapping rules in stage_axis)"
    return "unknown", "unmapped term → unknown (no guessing; disclosed pending adjudication)"


def donor_stage_map(donor_arr, stage_arr):
    """donor -> (uberon_raw, organism_stage, rule); conflicting values within one donor → unknown + flag."""
    per = defaultdict(set)
    for d, s in zip(donor_arr.tolist(), stage_arr.tolist()):
        per[d].add(s)
    out, amb = {}, []
    for d, ss in per.items():
        if len(ss) == 1:
            raw = next(iter(ss))
            cls, rule = classify_uberon(raw)
            out[d] = (raw, cls, rule)
        else:
            out[d] = ("|".join(sorted(ss)), "unknown",
                      "multiple stage values within donor (data defect) → unknown")
            amb.append(d)
    return out, amb


def stage_tally(donor_arr, stage_arr, dsm):
    """Tally per raw UBERON value: {uberon: {cells, n_donors, organism_stage, rule}}."""
    tal = {}
    for d, s in zip(donor_arr.tolist(), stage_arr.tolist()):
        t = tal.setdefault(s, {"cells": 0, "donors": set(),
                               "organism_stage": dsm[d][1], "rule": dsm[d][2]})
        t["cells"] += 1
        t["donors"].add(d)
    return {s: {"cells": v["cells"], "n_donors": len(v["donors"]),
                "organism_stage": v["organism_stage"], "rule": v["rule"]}
            for s, v in sorted(tal.items(), key=lambda kv: -kv[1]["cells"])}


def excluded_units(donor_arr, mc_arr, dsm, classes):
    """Per-donor disclosure rows excluded from the adult main tier (red line 2: row-by-row disclosure)."""
    rows = defaultdict(lambda: {"cells": 0, "uberon": "", "organism_stage": "", "rule": ""})
    for i, d in enumerate(donor_arr.tolist()):
        raw, cls, rule = dsm[d]
        if cls != "adult":
            r = rows[d]
            r["cells"] += 1
            r["uberon"] = raw
            r["organism_stage"] = cls
            r["rule"] = rule
    return [{"donor_id": d, **v} for d, v in
            sorted(rows.items(), key=lambda kv: -kv[1]["cells"])]


# ---- KB3 (t_5425a7ca) full separate developmental axis: constants and decision rules (brief BRIEF_KB3_DEVELOPMENT_AXIS) ----
KB3_CARD = "t_5425a7ca"
KB3_PROHIBITION = ("KB3 prohibition (PI red line 2026-09-23): developmental-stage data must not enter the "
                   "adult baseline statistics pool and vice versa —— fetal ≠ adult for the same tissue; "
                   "adult/fetal are never mutual references.")
KB3_DEV_ENUM = ("adult", "fetal_developing", "postnatal_neonatal",
                "mixed_not_separable", "unknown")  # mixed: no new entries; existing ones must be split/downgraded


def kb3_dev_stage(e):
    """KB3 required field development_stage (the KB3 5-value projection of organism_stage).
    adult tier = adult; everything else (skeleton not recomputed / RPE has no age source) = unknown
    —— silent assignment to adult is forbidden (KB2c red line 2)."""
    return "adult" if e.get("organism_stage") == "adult" else "unknown"


def kb3_applicable_note(e):
    """Hard-code the applicable stage into the file header (brief W1): the target tier at backfill time, not the current value."""
    if e.get("organism_stage") == "adult":
        return None
    if e.get("status") == "skeleton_mapping_backfilled":
        return ("adult —— applicable anchor = adult anchors such as HRCA/D002 (hard-coded); but donor-level "
                "fractions are not recomputed, so development_stage stays unknown until backfill; writing adult "
                "early is forbidden (KB2c red line 2)")
    return ("unknown —— the source tier (e.g. GSE158629 RPE) has no donor-age column; per-donor ages must be "
            "completed and a further adjudication passed before upgrading to adult (out-of-scope KB2c item); "
            "silent assignment to adult is forbidden")


def kb3_augment(e):
    e["development_stage"] = kb3_dev_stage(e)
    e["development_stage_prohibition"] = KB3_PROHIBITION
    e["kb3_card"] = KB3_CARD
    na = kb3_applicable_note(e)
    if na:
        e["kb3_applicable_stage_at_backfill"] = na
    return e
# ---- KB3 end ----


def stage_axis_block(eid):
    """Write the full adjudication scope into product fields (red line 3: thresholds live in products; changes require re-adjudication)."""
    return {
        "field": "organism_stage",
        "levels": ["fetal", "adult", "developing", "unknown"],
        "adult_rule": (f"UBERON development_stage with digitized age >= {ADULT_MIN_YEARS}y is called adult; "
                       "explicit adult terms (late/prime/middle/mature/human adult stage, decade band >=3rd) are "
                       "also called adult with the rule recorded; threshold changes require re-adjudication "
                       "(KB2c Q2, 2026-09-23)"),
        "developing_rule": "newborn/infant/postnatal stage and <18y numeric ages/age bands → developing (KB2c Q2)",
        "fetal_rule": "fetal/embryonic/gestation/Carnegie terms → fetal; never merged into the adult main tier (red line 1)",
        "unknown_rule": "no age column / unmapped term / organoid / age band straddling the threshold → unknown; "
                        "rows must be disclosed, silent assignment to adult is forbidden (red line 2)",
        "aging_note": ">=60 aging stratification is not on this axis — aging is an orthogonal independent axis, "
                      "to be listed as its own entry later (adjudication Q2)",
        "source_col": "obs/development_stage (raw UBERON values kept row by row; tallies in stage_disclosure, "
                      "exclusion list in excluded_nonadult_units)",
        "tier_ids": {"adult_only": f"{eid}__adult_only__kb2c",
                     "adult_pool": f"{eid}__adult_pool__v1.0"},
    }


def sha256_obj(obj):
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def kb2c_adult_entry(e, tally, excluded, pool_stats, pool_nd, pool_pooled,
                     n_donors_all, n_cells_adult):
    """Wire the adult-only dual tiers for the 4 filled h5ad entries (donor_level_main is already adult-only)."""
    eid = e["entry_id"]
    e["organism_stage"] = "adult"
    e["stage_axis"] = stage_axis_block(eid)
    e["stage_disclosure"] = tally
    e["excluded_nonadult_units"] = excluded
    e["donor_level_adult_pool_contrast"] = pool_stats
    e["pooled_adult_pool_contrast"] = pool_pooled
    e["adult_only_meta"] = {
        "n_donors_adult": n_donors_all - len(excluded),
        "n_donors_excluded_nonadult": len(excluded),
        "n_cells_adult": n_cells_adult,
        "n_units_adult_main": e["_tmp_main_nd"],
        "n_units_pool": pool_nd,
    }
    del e["_tmp_main_nd"]


def kb2c_unknown_entry(e, note, disclosure):
    """Sources without an age column (RPE etc.): unknown tier, disclosure rows, no silent adult assignment (red line 2)."""
    eid = e["entry_id"]
    e["organism_stage"] = "unknown"
    e["stage_axis"] = stage_axis_block(eid)
    e["stage_axis"]["tier_ids"] = {"unknown_descriptive": f"{eid}__stage_unknown__kb2c"}
    e["stage_note"] = note
    e["stage_disclosure"] = disclosure
    e["donor_level_adult_pool_contrast"] = None
    e["adult_only_meta"] = None


# ---------------------------------------------------------------- retina (D001)
def build_retina(old):
    f = h5py.File(HRCA, "r")
    study = obs_col(f, "study_name")
    donor = obs_col(f, "donor_id")
    mc = obs_col(f, "majorclass")
    enr = obs_col(f, "suspension_enrichment_factors")
    tis = obs_col(f, "tissue")
    susp = obs_col(f, "suspension_type")
    dev = obs_col(f, "development_stage")
    n = len(donor)
    classes = sorted(set(mc.tolist()))
    dsm, amb = donor_stage_map(donor, dev)
    tally = stage_tally(donor, dev, dsm)
    # enrichment strata: NeuN+ sorted vs naive
    enrich = np.array(["NeuN+" if "NeuN" in e else "naive" for e in enr])
    units, stratum_rows = [], defaultdict(list)
    for i in range(n):
        key = (study[i], enrich[i], donor[i])
        units.append(key)
        stratum_rows[(study[i], enrich[i])].append((key, mc[i]))
    pooled = pct_table(Counter(mc.tolist()), classes)
    strata = []
    for s in sorted(stratum_rows):
        rows_s = stratum_rows[s]
        stats, nu = donor_stats(rows_s, classes)
        rows_a = [r for r in rows_s if dsm[r[0][-1]][1] == "adult"]
        if rows_a:
            stats_a, nu_a = donor_stats(rows_a, classes)
            guard = None
        else:
            stats_a, nu_a = None, 0
            guard = ("FALLBACK_BLOCKED: this stratum has no adult donors, the adult-only distribution does not "
                     "exist —— silent fallback to pool is forbidden (KB2c red line 2); donor_level=pool is for contrast only")
        cells = len(rows_s)
        strata.append({
            "study": s[0], "enrichment": s[1], "n_donors": nu, "n_cells": cells,
            "share_of_atlas_pct": round(100.0 * cells / n, 2),
            "donor_level": stats,
            "donor_level_adult_only": stats_a,
            "n_units_adult_only": nu_a,
            "adult_fallback_guard": guard,
            "sorted_design_flag": (s[0] == "Chen_rgc") or (s[1] == "NeuN+"),
        })
    # main reference = after excluding sorted-design strata (all Chen_rgc + each study's NeuN+ strata),
    # then dropping non-adult donor units per KB2c
    main_rows = [r for k, v in stratum_rows.items()
                 if k[0] != "Chen_rgc" and k[1] != "NeuN+" for r in v]
    pool_stats, pool_nd = donor_stats(main_rows, classes)
    main_rows_a = [r for r in main_rows if dsm[r[0][-1]][1] == "adult"]
    main_stats, main_nd = donor_stats(main_rows_a, classes)
    pooled_adult_main = (pct_table(Counter([r[1] for r in main_rows_a]), classes)
                         if main_rows_a else None)
    all_adult = [i for i in range(n) if dsm[donor[i]][1] == "adult"]
    excluded = excluded_units(donor, mc, dsm, classes)
    regions = dict(Counter(tis.tolist()).most_common())
    f.close()

    per_study_diss = {
        "Chen_a": "0.02% NP40 (nuclei extraction)", "Chen_ancestry": "0.02% NP40 (nuclei extraction)",
        "Chen_b_GSE226108": "0.02% NP40 (nuclei extraction)", "Chen_c_GSE247157": "0.02% NP40 (nuclei extraction)",
        "Chen_rgc": "0.02% NP40 (nuclei extraction)", "Shekhar_GSE237204": "unknown",
    }
    entry = {
        "schema": "eyekb-baseline/1.0",
        "entry_id": "baseline_human_retina",
        "tissue": "retina", "species": "human",
        "title": "Composition baseline: human (normal) neural retina adult-only main tier (D001 HRCA, donor-level conditional reference distribution, KB2c separate developmental axis)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_16c3e020",
        "anchor": {
            "registry_row": "OA-D001 (HCA-HRCA-v1.0)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": HRCA,
            "pmid": "41578023",
            "tier": "T1 annotated standard set",
        },
        "t2_fields": {
            "sampling_material": "human neural retina ex vivo tissue (regional composition: "
                       + ", ".join(f"{k} {v:,}" for k, v in regions.items()) + ")",
            "disease_stage": "normal (disease column all normal; donors predominantly elderly, the 90+ age band is the largest)",
            "treatment_background": "not recorded (public atlas metadata has no treatment column) —— marked 'not recorded', no speculation",
            "platform": "snRNA-seq (suspension_type=nucleus 100%, nuclear suspension)",
            "enrichment_step": "stratified: mostly naive; 1,334,033 nuclei went through NeuN+ neuronal-nuclei sorting "
                       "(part of Chen_a/ancestry); the entire Chen_rgc study stratum is an RGC-enriched design",
            "dissociation_method": "; ".join(f"{k}={v}" for k, v in per_study_diss.items()),
            "donor_count": "104 unique donor_id; %d donor units when stratified by study|donor|enrichment" % len(set(units)),
            "counting_denominator": f"{n:,} nuclei (majorclass fully annotated)",
            "evidence_source": "local recomputation (A) + HRCA paper (B, PMID 41578023) + old KB1 literature anchors",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": ("donor-level: per donor unit compute the 10-class shares first, then aggregate "
                                "median/IQR/range across donors; strata = study × enrichment (× region, D002 side); "
                                "pooled columns are contrast only and suffer large-donor domination"),
        "primary_reference_stratum": ("main tier = %d donor units from the 6 studies after excluding Chen_rgc "
                                      "(RGC-enriched design) and each study's NeuN+ sorted strata, keeping only "
                                      "organism_stage=adult (>=18y)" % main_nd),
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],   # tool-compatibility view, filled below
        "fine_types": old.get("fine_types"),
        "states": old.get("states"),
        "flags": old.get("flags"),
        "caveats": (old.get("caveats") or []) + [
            "v1.1 (this entry): fraction scope upgraded from 'all-cell pooled + cross-study spread' to "
            "'donor-level stratified distribution' (Astra T2); old pooled values are kept in pooled_all_cells for "
            "contrast only —— Chen_ancestry is 42.6% of the 3.17M nuclei, so pooled values are dominated by large donors.",
            "The NeuN+ sorted stratum systematically elevates neuronal classes and depresses MG/Astro/RPE; until "
            "control samples' nuclear-sorting status is known, the two strata's intervals must not be mixed.",
            "suspension_type is all nuclei —— snRNA intronic reads are counted (intronic_reads_counted=yes), so class "
            "fractions are not directly comparable with scRNA cell-suspension data (Astra T2: the scRNA vs snRNA "
            "difference alone can change the observed composition).",
        ],
        "sources": old.get("sources", []) + [
            {"sid": "D001_DONOR_LEVEL", "kind": "dataset", "pmid": "41578023",
             "label": f"this entry's donor-level distribution recomputed from {HRCA} obs by {GEN}", "path": HRCA,
             "computation": f"{__file__} build_retina()"},
        ],
    }
    # tool-compatible major_classes rows: markers/sources inherited from the old entry, intervals replaced with donor-level stats
    old_rows = {r["class"]: r for r in old.get("major_classes", [])}
    for c in classes:
        src = old_rows.get(c, {})
        entry["major_classes"].append({
            "class": c, "label_cn": src.get("label_cn", ""),
            "donor_median_pct": main_stats[c]["median_pct"],
            "donor_iqr_pct": main_stats[c]["iqr_pct"],
            "donor_range_pct": main_stats[c]["range_pct"],
            "pooled_pct_for_reference_only": pooled[c],
            "markers_local_lib": src.get("markers_local_lib", []),
            "evidence": "A", "source_ids": ["D001_DONOR_LEVEL"] + [
                s for s in src.get("source_ids", []) if s != "HRCA317M"],
            "note": src.get("note", ""),
        })
    entry["t2_fields"]["donor_count"] = (
        f"main tier adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} donor units; contrast tier adult_pool {len(set(donor.tolist()))} donors / {pool_nd} units "
        f"(includes {len(excluded)} non-adult donors → see excluded_nonadult_units row by row; KB2c adjudication Q2 threshold >=18y)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): the main tier was upgraded to adult-only scope (donor_age>=18y, adjudication Q2) "
        "—— the v1.0 mixed scope (which once included 3-17-year-old developmental donors; measured fetal nuclei = 0) "
        "is fully preserved in donor_level_adult_pool_contrast (tier_id=...__adult_pool__v1.0); citing v1.0 numbers "
        "must attach the contrast-tier identity; the two tier signatures are never mixed (red line).")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     len(set(donor.tolist())), len(all_adult))
    return entry


# ------------------------------------------------------- ocular_surface (D002)
TISSUE_GROUP = {
    "cornea": "cornea (含角膜上皮/固有质)",
    "substantia propria of cornea": "cornea (含角膜上皮/固有质)",
    "corneal epithelium": "cornea (含角膜上皮/固有质)",
    "corneal endothelium": "corneal endothelium (单独层, 仅 404 细胞)",
    "corneo-scleral junction": "corneo-scleral junction (limbus 区)",
    "sclera": "sclera",
    "tunica fibrosa of eyeball": "sclera",
    "ocular surface region": "ocular surface region (混合)",
}


def build_ocular_surface():
    f = h5py.File(D002, "r")
    donor = obs_col(f, "donor_id")
    mc = obs_col(f, "majorclass")
    tis = obs_col(f, "tissue")
    study = obs_col(f, "study")
    susp = obs_col(f, "suspension_type")
    dev = obs_col(f, "development_stage")
    n = len(donor)
    classes = sorted(set(mc.tolist()))
    dsm, amb = donor_stage_map(donor, dev)
    tally = stage_tally(donor, dev, dsm)
    grp = np.array([TISSUE_GROUP.get(t, "other") for t in tis])
    rows_by_g, units = defaultdict(list), set()
    for i in range(n):
        u = (grp[i], donor[i])
        units.add(u)
        rows_by_g[grp[i]].append((u, mc[i]))
    pooled = pct_table(Counter(mc.tolist()), classes)
    strata = []
    for g in sorted(rows_by_g):
        rows_s = rows_by_g[g]
        stats, nu = donor_stats(rows_s, classes)
        rows_a = [r for r in rows_s if dsm[r[0][-1]][1] == "adult"]
        if rows_a:
            stats_a, nu_a = donor_stats(rows_a, classes)
            guard = None
        else:
            stats_a, nu_a = None, 0
            guard = ("FALLBACK_BLOCKED: 该组织组全部供者非 adult (如 newborn-only 层), "
                     "adult-only 不存在 —— 禁静默回退 pool (KB2c 红线2)")
        strata.append({"tissue_group": g, "n_donors": nu,
                       "n_cells": len(rows_s), "donor_level": stats,
                       "donor_level_adult_only": stats_a,
                       "n_units_adult_only": nu_a,
                       "adult_fallback_guard": guard})
    # 主参考(KB2c)= 全库供者级(donor|组织组 单元)中仅 adult 供者; 对照档=旧 v1.0 全池口径
    main_rows = [r for g in rows_by_g for r in rows_by_g[g]]
    pool_stats, pool_nd = donor_stats(main_rows, classes)
    main_rows_a = [r for r in main_rows if dsm[r[0][-1]][1] == "adult"]
    main_stats, main_nd = donor_stats(main_rows_a, classes)
    pooled_adult_main = (pct_table(Counter([r[1] for r in main_rows_a]), classes)
                         if main_rows_a else None)
    all_adult = [i for i in range(n) if dsm[donor[i]][1] == "adult"]
    excluded = excluded_units(donor, mc, dsm, classes)
    # 类内 author_cell_type top (pooled within class, 口径标注)
    act = obs_col(f, "author_cell_type")
    fine = {}
    byc = defaultdict(Counter)
    for i in range(n):
        byc[mc[i]][act[i]] += 1
    for c, cnt in byc.items():
        tot = sum(cnt.values())
        fine[c] = [[k, round(100.0 * v / tot, 1)] for k, v in cnt.most_common(6)]
    diss = dict(Counter(obs_col(f, "suspension_dissociation_reagent").tolist()).most_common(4))
    f.close()
    entry = {
        "schema": "eyekb-baseline/1.0",
        "entry_id": "baseline_human_ocular_surface",
        "tissue": "ocular_surface", "species": "human",
        "title": "组成基线: 人(正常)眼表 adult-only 主档 — 角膜/limbus/巩膜超级类 (D002, 供者级条件参考分布, KB2c 发育轴单列)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_16c3e020",
        "anchor": {
            "registry_row": "OA-D002 (CELLxGENE-OcularSurface)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": D002,
            "collection": "https://cellxgene.cziscience.com/collections/0f7d022a-46c7-4e64-be4c-e34adbb78089",
            "tier": "T1 annotated standard set",
        },
        "category_note": ("眼表为超级类 (cornea/limbus/sclera/conjunctiva 合并口径, 类目=per-region 多套禁跨区套用); "
                          "conjunctiva/sclera 独立骨架另立 (t_6f5cc731 裁定: 结膜=数据不足, 建议并入眼表亚群标注)。"),
        "t2_fields": {
            "取样材料": "人眼表离体组织: cornea / corneo-scleral junction(limbus) / sclera / "
                       "ocular surface region / corneal endothelium (移植角膜内皮边缘碎块)",
            "疾病阶段": "normal (disease 列全 normal; 供者为眼库捐献角膜缘/巩膜环)",
            "治疗背景": "未记录 (眼库捐献元数据无治疗列)",
            "平台": "scRNA-seq (suspension_type=cell 100%, 10x 3' v2/v3) —— 与 D001 retina(核) 不同口径, 跨基线比较注意",
            "富集步骤": "无细胞分选记录 (全组织解离直接上机)",
            "解离方法": "机械+酶解离; 主要试剂: " + "; ".join(f"{k}×{v:,}细胞" for k, v in diss.items()),
            "供者数": f"{len(set(donor.tolist()))} donors (本地 578K 文件); collection 级 registry 记 102 —— 本地为子集提取",
            "计数分母": f"{n:,} cells (majorclass 全标注)",
            "证据来源": "本地实测复算 (A) + CELLxGENE collection 官方注释 (portal)",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "供者级 (donor|组织组 单元); 组织组先分层, 不跨组合并 (Astra T2); KB2c: 主档仅 adult 供者单元; pooled 仅对照",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type 类内占比 (pooled within class, 供参考)",
                       **fine},
        "states": None,
        "flags": {
            "expected_low_but_present": [
                "Corneal Endothelium (pooled 0.07%) —— 仅眼库内皮边缘碎块贡献, 常规角膜缘样本近零",
                "Melanocytes/Schwann Cells/Smooth Muscle Cells <2%"],
            "unexpected": ["光感受器/视网膜神经元类出现 (取材越界到视网膜?)",
                           "大量造血成熟标志 (FCN1/LYZ 粒系) —— 供体血液残留旗"],
            "contamination_suspect": [
                "published_annotation 列含 red blood cells 主导层 (525,617 标注) —— 血液残留是本库已知主污染, 见 caveat",
                "黑素颗粒/色素组织污染 (色素性供者巩膜)"],
        },
        "caveats": [
            "本地 D002 文件 = 577,857 cells / 50 donors, 为 collection 级 (>1M/102) 的子集提取 (口径=本地实测); "
            "回填全 collection 需下载审批, 列'待回填'。",
            "'Majorclass=Immune Cells' 仅 1.7%: 眼表固有免疫稀少 + 无免疫富集步骤 —— 免疫比例不可对照炎症疾病样本。",
            "published_annotation 与 majorclass 并存: published_annotation='red blood cells' 占大头说明 RBC 未从 "
            "majorclass 里剔除干净? 不 —— majorclass 9 类无 RBC 类, RBC 信号散入各类, 计数分母含 RBC 污染核, "
            "各类% 为'捕获事件构成'非组织真值 (Astra T2 口径声明)。",
            "sclera/conjunctiva 独立条目见对应骨架文件; 本条 corneo-scleral junction 层 ≠ 独立结膜基线。",
        ],
        "sources": [
            {"sid": "D002_LOCAL", "kind": "dataset", "label": f"本地文件 {D002}", "path": D002,
             "computation": f"{__file__} build_ocular_surface()"},
            {"sid": "D002_PORTAL", "kind": "dataset",
             "label": "Human Ocular Surface Cell Atlas, CELLxGENE collection (portal 官方注释)",
             "url": "https://cellxgene.cziscience.com/collections/0f7d022a-46c7-4e64-be4c-e34adbb78089"},
        ],
    }
    for c in classes:
        entry["major_classes"].append({
            "class": c,
            "donor_median_pct": main_stats[c]["median_pct"],
            "donor_iqr_pct": main_stats[c]["iqr_pct"],
            "donor_range_pct": main_stats[c]["range_pct"],
            "pooled_pct_for_reference_only": pooled[c],
            "evidence": "A", "source_ids": ["D002_LOCAL", "D002_PORTAL"],
        })
    entry["t2_fields"]["供者数"] = (
        f"主档 adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} 供者单元; 对照档 adult_pool {len(set(donor.tolist()))} donors / {pool_nd} 单元 "
        f"(含 {len(excluded)} 非 adult 供者如 newborn 0-28d → 逐行见 excluded_nonadult_units)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y); v1.0 混口径 (含 newborn 0-28d 25,018 细胞 + "
        "postnatal/儿童青少年) 保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0)。"
        "FALLBACK_BLOCKED 守卫已实装（组织组 0 adult 供者时触发禁回退）——本次实测 0 层触发, "
        "各组织组 adult-only 均有真实支撑。")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     len(set(donor.tolist())), len(all_adult))
    return entry


# ------------------------------------------------- optic_nerve (HRA006282 / OA-D003)
ON = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"
ON_TISSUE_LABEL = {"cranial nerve II": "ON (视神经)",
                   "optic disc": "ONH (视神经盘/视乳头)"}
# ON/ONH 采集数据里会带入视盘旁视网膜组织 —— 这些类是"捕获构成"而非视神经本体真组成 (Astra T2)
ON_RETINA_ASSOC = {"Rod", "Cone", "BC", "HC", "AC", "RGC"}
ON_RPE_ASSOC = {"RPE", "Pigmented_cell"}


def build_optic_nerve():
    f = h5py.File(ON, "r")
    donor = obs_col(f, "donor_id")
    mc = obs_col(f, "majorclass")
    tis = obs_col(f, "tissue")
    src = obs_col(f, "source")
    act = obs_col(f, "author_cell_type")
    dev = obs_col(f, "development_stage")
    n = len(mc)
    classes = sorted(set(mc.tolist()))
    dsm, amb = donor_stage_map(donor, dev)
    tally = stage_tally(donor, dev, dsm)
    tl = np.array([ON_TISSUE_LABEL.get(t, t) for t in tis])
    rows_by, units = defaultdict(list), set()
    for i in range(n):
        u = (src[i], tl[i], donor[i])
        units.add(u)
        rows_by[(src[i], tl[i])].append((u, mc[i]))
    pooled = pct_table(Counter(mc.tolist()), classes)
    strata = []
    for s in sorted(rows_by):
        rows_s = rows_by[s]
        stats, nu = donor_stats(rows_s, classes)
        rows_a = [r for r in rows_s if dsm[r[0][-1]][1] == "adult"]
        if rows_a:
            stats_a, nu_a = donor_stats(rows_a, classes)
            guard = None
        else:
            stats_a, nu_a = None, 0
            guard = ("FALLBACK_BLOCKED: 该来源×部位层无 adult 供者, adult-only 不存在 —— "
                     "禁静默回退 pool (KB2c 红线2)")
        strata.append({"study": s[0], "tissue_group": s[1], "n_donors": nu,
                       "n_cells": len(rows_s),
                       "share_of_atlas_pct": round(100.0 * len(rows_s) / n, 2),
                       "donor_level": stats,
                       "donor_level_adult_only": stats_a,
                       "n_units_adult_only": nu_a,
                       "adult_fallback_guard": guard})
    main_rows = [r for v in rows_by.values() for r in v]
    pool_stats, pool_nd = donor_stats(main_rows, classes)
    main_rows_a = [r for r in main_rows if dsm[r[0][-1]][1] == "adult"]
    main_stats, main_nd = donor_stats(main_rows_a, classes)
    pooled_adult_main = (pct_table(Counter([r[1] for r in main_rows_a]), classes)
                         if main_rows_a else None)
    all_adult = [i for i in range(n) if dsm[donor[i]][1] == "adult"]
    excluded = excluded_units(donor, mc, dsm, classes)
    byc = defaultdict(Counter)
    for i in range(n):
        byc[mc[i]][act[i]] += 1
    fine = {}
    for c, cnt in byc.items():
        tot = sum(cnt.values())
        fine[c] = [[k, round(100.0 * v / tot, 1)] for k, v in cnt.most_common(6)]
    diss = dict(Counter(obs_col(f, "suspension_derivation_process").tolist()).most_common())
    regions = dict(Counter(tl.tolist()))
    n_donors = len(set(donor.tolist()))
    ret_pct = round(sum(pooled[c] for c in ON_RETINA_ASSOC & set(classes)), 2)
    rpe_pct = round(sum(pooled[c] for c in ON_RPE_ASSOC & set(classes)), 2)
    f.close()
    entry = {
        "schema": "eyekb-baseline/1.0",
        "entry_id": "baseline_human_optic_nerve",
        "tissue": "optic_nerve", "species": "human",
        "title": "组成基线: 人(正常)视神经+视神经盘 snRNA adult-only 主档 (OA-D003 HRA006282, 供者级条件参考分布, KB2c 发育轴单列)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "OA-D003 (CELLxGENE-OpticNerve)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": ON,
            "collection": "https://cellxgene.cziscience.com/collections/05e3d0fc-c9dd-4f14-9163-2b242b3bb5c2",
            "tier": "T1 已注释标准集 (portal 官方注释, majorclass/author_cell_type/cell_type 三层)",
        },
        "t2_fields": {
            "取样材料": "人视神经/视神经盘离体组织 (手术取材, 眼库供体; 区域构成: "
                       + ", ".join(f"{k} {v:,}核" for k, v in regions.items()) + ")",
            "疾病阶段": "normal (disease 列全 normal; 供者为系统性死亡捐献者, "
                       "donor_cause_of_death 含肿瘤/脓毒症等, 眼球本身无眼病记录)",
            "治疗背景": "未记录 (眼库捐献元数据无治疗列) —— 标'未记录', 不臆测",
            "scRNA_vs_snRNA": "snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes) —— "
                              "与 scRNA 细胞悬液条 (如 D002 眼表) 类比例不可直接互比",
            "富集步骤": "无分选记录 (metadata 无 enrichment 列; 全组织核悬液直接上机)",
            "解离方法": "; ".join(f"{k}×{v:,}核" for k, v in diss.items())
                       + " (sample_preservation=frozen in liquid nitrogen; collection=surgical resection)",
            "供者数": f"{n_donors} 唯一 donor_id; 按 研究来源|部位|供者 分层共 {main_nd} 个供者单元",
            "计数分母": f"{n:,} 核 (majorclass 全标注)",
            "证据来源": "本地实测复算 (A) + CELLxGENE HRA006282 collection 官方注释 (portal) + 注册表 OA-D003",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "供者级 (来源|部位|供者 单元); 部位(ON vs ONH)×研究来源先分层展示, "
                               "main 为 adult 供者单元汇总 (KB2c: 非 adult 不并入主档) —— 视神经 ON 与 ONH "
                               "生物学构成差异大, 对照时优先看对应层区间 (Astra T2); pooled 仅对照",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type 类内占比 (pooled within class, 供参考); "
                                           "ON/ONH/retina 后缀=portal 官方位置亚型标注"},
        "states": None,
        "flags": {
            "expected_low_but_present": [
                "T/B/NK/DC/Mast 合计 <1% (正常神经组织免疫稀少)",
                "Schwann_cell 0.22% (PN 髓鞘支持细胞; 核悬液下 PN 富集度受限于中枢段)",
                "Mural_cell 1.8% / Endothelial_cell 3.6% (血管支持层)"],
            "unexpected": [
                f"视网膜神经元类 (Rod/Cone/BC/HC/AC/RGC) pooled {ret_pct}% + RPE/色素类 {rpe_pct}% —— "
                "视盘取材带入盘旁视网膜/脉络膜组织, 属捕获构成非视神经本体真组成; "
                "疾病样本对照时不得把该层当'视神经应有比例'"],
            "contamination_suspect": [
                "Melanocyte 0.86% (软脑膜/色素组织附带, 正常范围内偏高需结合取材平面解读)"],
        },
        "caveats": [
            "MG=Müller 胶质细胞 (1.7%) 与 Microglia=小胶质细胞 (5.0%) 为两套不同身份, portal 词表并存 —— "
            "下游引用勿混; 同规则适用 AC(无长细胞)/BC(双极细胞)等视网膜缩写。",
            "Chen (Baylor, ~85%) 与 Sanes (Harvard) 两供体池规模悬殊, 已按 来源×部位 分 4 层展示; "
            "main 供者级每单元等权, 大池不再压秤, 但层间差异需看 strata 而非只看 main。",
            "本条计数分母含视盘旁视网膜来源类 (~15%); 如需'纯视神经'参考区间, 用 strata 中 "
            "ON (cranial nerve II) 层。",
            "snRNA 口径 (核悬液, 内含子 reads 计入) 与 scRNA 数据比较须谨慎 (Astra T2)。",
        ],
        "sources": [
            {"sid": "ON_LOCAL", "kind": "dataset", "label": f"本地文件 {ON}", "path": ON,
             "computation": f"{__file__} build_optic_nerve()"},
            {"sid": "ON_PORTAL", "kind": "dataset",
             "label": "Human Optic Nerve / Optic Nerve Head Atlas, CELLxGENE collection HRA006282 "
                      "(portal 官方注释; registry OA-D003, verified 2026-08-11)",
             "url": "https://cellxgene.cziscience.com/collections/05e3d0fc-c9dd-4f14-9163-2b242b3bb5c2"},
        ],
    }
    for c in classes:
        entry["major_classes"].append({
            "class": c,
            "donor_median_pct": main_stats[c]["median_pct"],
            "donor_iqr_pct": main_stats[c]["iqr_pct"],
            "donor_range_pct": main_stats[c]["range_pct"],
            "pooled_pct_for_reference_only": pooled[c],
            "evidence": "A", "source_ids": ["ON_LOCAL", "ON_PORTAL"],
            "note": ("视网膜来源类 — 视盘取材带入, 见 caveats/flags" if c in ON_RETINA_ASSOC
                     else ("色素/RPE 来源类 — 同上" if c in ON_RPE_ASSOC else "")),
        })
    entry["t2_fields"]["供者数"] = (
        f"主档 adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} 供者单元; 对照档 adult_pool {n_donors} donors / {pool_nd} 单元 "
        f"(含 {len(excluded)} 非 adult 供者含 newborn 15,177 核 → 逐行见 excluded_nonadult_units)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y, 裁定 Q2); v1.0 混口径 (含 newborn/3-17 岁) "
        "保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), 两档身份签名分离不混用。")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     n_donors, len(all_adult))
    return entry


# ------------------------------------------------- TM + CB (HRA000728_tm_cb / HASA)
# 本地文件实为 HASA 系前节段 snRNA 集成件 (obs study=chen_tm_cb + sanes_GSE199013);
# t_6f5cc731 盘点: TM 主力参考底座 = GSE199013/HASA (OA-D004=OA-D016) snRNA 1,102,250核 ——
# 与本文件实测 n=1,102,250 精确吻合, 判为同一资源。目录名 HRA000728 与 registry OA-D028
# (Keratoconus cornea) 名称不符 —— 内容判决优先, 该 registry 错位另行登记, 本条不引用 OA-D028。
TMCB = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
TMCB_UVEA_EXCLUDED = 53406  # tissue=uvea 分量 (5 供者, 含 sanes 层) 不入 TM/CB 切片


def _build_tmcb(tissue_value, cn, extra_caveats, extra_flags_unexpected):
    f = h5py.File(TMCB, "r")
    donor = obs_col(f, "donor_id")
    mc = obs_col(f, "majorclass")
    tis = obs_col(f, "tissue")
    study = obs_col(f, "study")
    act = obs_col(f, "author_cell_type")
    dev = obs_col(f, "development_stage")
    m = tis == tissue_value
    idx = np.where(m)[0]
    n = len(idx)
    sub_mc = mc[idx]
    sub_dn = donor[idx]
    sub_dev = dev[idx]
    classes = sorted(set(sub_mc.tolist()))
    dsm, amb = donor_stage_map(sub_dn, sub_dev)
    tally = stage_tally(sub_dn, sub_dev, dsm)
    rows_by, units = defaultdict(list), set()
    for i in idx:
        u = (study[i], donor[i])
        units.add(u)
        rows_by[study[i]].append((u, mc[i]))
    pooled = pct_table(Counter(sub_mc.tolist()), classes)
    strata = []
    for st in sorted(rows_by):
        rows_s = rows_by[st]
        stats, nu = donor_stats(rows_s, classes)
        rows_a = [r for r in rows_s if dsm[r[0][-1]][1] == "adult"]
        if rows_a:
            stats_a, nu_a = donor_stats(rows_a, classes)
            guard = None
        else:
            stats_a, nu_a = None, 0
            guard = ("FALLBACK_BLOCKED: 该研究层无 adult 供者, adult-only 不存在 —— "
                     "禁静默回退 pool (KB2c 红线2)")
        strata.append({"study": st, "tissue_group": cn, "n_donors": nu,
                       "n_cells": len(rows_s),
                       "share_of_atlas_pct": round(100.0 * len(rows_s) / n, 2),
                       "donor_level": stats,
                       "donor_level_adult_only": stats_a,
                       "n_units_adult_only": nu_a,
                       "adult_fallback_guard": guard})
    main_rows = [r for v in rows_by.values() for r in v]
    pool_stats, pool_nd = donor_stats(main_rows, classes)
    main_rows_a = [r for r in main_rows if dsm[r[0][-1]][1] == "adult"]
    main_stats, main_nd = donor_stats(main_rows_a, classes)
    pooled_adult_main = (pct_table(Counter([r[1] for r in main_rows_a]), classes)
                         if main_rows_a else None)
    all_adult = int(sum(1 for d in sub_dn.tolist() if dsm[d][1] == "adult"))
    excluded = excluded_units(sub_dn, sub_mc, dsm, classes)
    byc = defaultdict(Counter)
    for i in idx:
        byc[mc[i]][act[i]] += 1
    fine = {}
    for c, cnt in byc.items():
        tot = sum(cnt.values())
        fine[c] = [[k, round(100.0 * v / tot, 1)] for k, v in cnt.most_common(6)]
    diss = dict(Counter(obs_col(f, "suspension_derivation_process")[idx].tolist()).most_common())
    n_donors = len(set(donor[idx].tolist()))
    f.close()
    entry = {
        "schema": "eyekb-baseline/1.0",
        "entry_id": f"baseline_human_{cn}",
        "tissue": cn, "species": "human",
        "title": f"组成基线: 人(正常){cn} snRNA adult-only 主档 ({cn} 切片 {n:,} 核 / {n_donors} 供者, 供者级条件参考分布, KB2c 发育轴单列)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "OA-D004=OA-D016 (GSE199013/HASA, t_6f5cc731 盘点 TM/CB 主力底座; "
                            "本地件核数与 HASA 条目 1,102,250 精确吻合)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": TMCB,
            "tier": "T1 portal 官方注释 (majorclass/author_cell_type/cell_type; study=chen_tm_cb+sanes_GSE199013)",
        },
        "t2_fields": {
            "取样材料": f"人前节段手术取材中 {cn} 解剖组分 (tissue 列='{tissue_value}' 切片; "
                       f"另有 uvea 分量 {TMCB_UVEA_EXCLUDED:,} 核未入本条)",
            "疾病阶段": "normal (disease 列全 normal; 供者系统性死亡眼库/手术材料)",
            "治疗背景": "未记录 (元数据无治疗列) —— 标'未记录', 不臆测",
            "scRNA_vs_snRNA": "snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)",
            "富集步骤": "无分选记录 (全组织核悬液直接上机)",
            "解离方法": "; ".join(f"{k}×{v:,}核" for k, v in diss.items())
                       + " (sample_collection_method=surgical resection)",
            "供者数": f"{n_donors} 唯一 donor_id; 按 研究|供者 分层共 {main_nd} 个供者单元",
            "计数分母": f"{n:,} 核 ({cn} 切片内 majorclass 全标注)",
            "证据来源": "本地实测复算 (A) + portal/HASA 官方注释 (t_6f5cc731 判 'portal官方')",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "供者级 (研究|供者 单元); 研究层先分层展示; KB2c: 主档仅 adult 供者单元; pooled 仅对照",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type 类内占比 (pooled within class, 供参考)"},
        "states": None,
        "flags": {
            "expected_low_but_present": extra_flags_unexpected[0],
            "unexpected": extra_flags_unexpected[1],
            "contamination_suspect": extra_flags_unexpected[2],
        },
        "caveats": extra_caveats,
        "sources": [
            {"sid": f"{cn.upper()}_LOCAL", "kind": "dataset", "label": f"本地文件 {TMCB}", "path": TMCB,
             "computation": f"{__file__} _build_tmcb('{tissue_value}','{cn}')"},
            {"sid": f"{cn.upper()}_HASA", "kind": "dataset",
             "label": "HASA/前节段 snRNA collection (t_6f5cc731 盘点映射 OA-D004/OA-D016; "
                      "本切片=其 chen_tm_cb+sanes 集成件的 " + cn + " 分量)",
             "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE199013"},
        ],
    }
    for c in classes:
        entry["major_classes"].append({
            "class": c,
            "donor_median_pct": main_stats[c]["median_pct"],
            "donor_iqr_pct": main_stats[c]["iqr_pct"],
            "donor_range_pct": main_stats[c]["range_pct"],
            "pooled_pct_for_reference_only": pooled[c],
            "evidence": "A", "source_ids": [f"{cn.upper()}_LOCAL", f"{cn.upper()}_HASA"],
        })
    entry["t2_fields"]["供者数"] = (
        f"主档 adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} 供者单元; 对照档 adult_pool {n_donors} donors / {pool_nd} 单元 "
        f"(含 {len(excluded)} 非 adult 供者 → 逐行见 excluded_nonadult_units)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y, 裁定 Q2) —— 本切片实测剔除 "
        + (f"{len(excluded)} 个非 adult 供者单元 (青少年段, 逐行见 excluded_nonadult_units); "
           if excluded else
           "0 个 (本切片全部供者 >=18y → 两档数值合法全等, 仅身份签名分离); ")
        + "v1.0 混口径保留于 donor_level_adult_pool_contrast "
        "(tier=...__adult_pool__v1.0), 两档签名分离。")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     n_donors, all_adult)
    return entry


def build_trabecular_meshwork():
    return _build_tmcb(
        "eye trabecular meshwork", "trabecular_meshwork",
        extra_caveats=[
            "本条=小梁网解剖组分取材切片: Ciliary_Muscle 占比高系紧邻的巩膜 spur/小梁肌一体取材, "
            "属捕获构成非 TM 细胞层真值; 作者级 TM 特异亚型 (BeamA/BeamB/JCT, author_cell_type) 见 fine_types。",
            "Fibroblast 主表类在本切片 = TM 成纤维/梁细胞 (TMFibro) —— 勿与角膜/巩膜成纤维直接混比。",
            "CB_PCE/CB_NPCE 少量 (合计 ~0.5%) = 睫状体取材边界污染。",
            "供者 25 但单元内供者规模不均; n=25 供者级区间仍属中等支撑, 疾病对照用后须复核方向。",
            "snRNA 口径, 与 scRNA 条不可直接互比 (Astra T2); uvea 分量 (53,406 核) 与巩膜/葡萄膜条另议。",
        ],
        extra_flags_unexpected=(
            [["Schwann Cell ~12% (神经支配组织)", "Pericyte ~0.4%"],
             ["Melanocyte ~6% (葡萄膜色素组织附带, 取材平面相关)"],
             ["CB_PCE/CB_NPCE ~0.5% (取材越界到睫状体)"]]),
    )


def build_ciliary_body():
    return _build_tmcb(
        "ciliary body", "ciliary_body",
        extra_caveats=[
            "本条=睫状体解剖组分取材切片: PCE/NPCE/睫状肌三主类为组织本体; "
            "Melanocyte/Schwann Cell 比例为葡萄膜色素+神经支配层的捕获构成 —— 疾病对照注意 (Astra T2)。",
            "Fibroblast 在本切片 = CB 成纤维 (CBFibro), 与 TM/角膜成纤维不同亚层 (author_cell_type 可辨)。",
            "供者 59, 支撑较强; 但两研究层规模悬殊 (chen_tm_cb 主力 vs sanes uvea 分量在本切片外), "
            "分层明细必看。",
            "snRNA 口径 (核悬液, 内含子 reads 计入), 与 scRNA 条不可直接互比。",
        ],
        extra_flags_unexpected=(
            [["Pericyte <1% (Endothelium 也仅 ~2%: 大血管为主, 毛细血管核捕获效率低)"],
             ["Immune Cell ~5% (巨噬为主) 属固有免疫正常水平, 供炎症对照基线"],
             ["无需额外污染旗 (切片边界即本组织)"]]),
    )



# ------------------------------------------------------------------- RPE (GSE158629)
# KB1v2b: RPE 处理件为 Seurat v3 RData (4 donor 对象, 每对象独立聚类, 无官方 celltype 列)。
# 簇→身份标注由本项目 marker 推断 (证据 C), 锚定 GEO 记录作者簇描述 (证据 B: rod/cone 转录本簇、
# TF+SPP1 VEGF 簇、RPE65+/VIM/GNL3/MKI67 干细胞候选小群)。转换与导出脚本:
#   scripts/baselines/data/export_rpe_meta.R -> cells_meta.csv + cluster_markers.csv (证据 A 输入)
RPE_DIR = Path(__file__).resolve().parent / "data"
RPE_CELLS = (RPE_DIR / "rpe_GSE158629_cells_meta.csv").as_posix()
RPE_MARKERS = (RPE_DIR / "rpe_GSE158629_cluster_markers.csv").as_posix()
RPE_RDATA = "/mnt/D/OcularKB/data/GSE158629/GSE158629_scrRNA_RPE_donors1-4.RData.gz"

# donor × cluster -> (canonical_class, state_label, 标注依据)
RPE_CLUSTER_LABELS = {
    ("donor1", "0"): ("RPE", "pigment-high (TYRP1+/BEST1+/RPE65+)",
                      "marker: RPE65#3 TYRP1#11 BEST1#12 TIMP3#1 (A)"),
    ("donor1", "1"): ("RPE", "canonical (RBP1/RLBP1)", "marker (A)"),
    ("donor1", "2"): ("PR-associated", "rod-program (SAG/PDE6A/RHO)",
                      "作者描述 rod RNA 簇 RHO/PDE6A (B) + marker (A)"),
    ("donor1", "3"): ("RPE", "TF+SPP1/VEGF state (VIM+/TF+/SPP1+/MT1X+)",
                      "作者描述 VEGF signaling 簇 TF/SPP1 (B) + marker (A)"),
    ("donor1", "4"): ("PR-associated", "rod-pure (RHO/RBP3/IMPG1/CNGA1)", "marker (A)"),
    ("donor1", "5"): ("PR-associated", "rod/cone-mixed (SAG/GNAT1/PDE6G)",
                      "marker (A); 作者 cone 簇 ARR3/PDE6H 未入本簇 top25, 归属存疑 (C)"),
    ("donor1", "6"): ("neuron-like", "VSX1+/SNAP25+ (bipolar/cone-like)", "marker (A)"),
    ("donor1", "7"): ("neuron-like", "ISL1+/SNAP25+ (amacrine-like)", "marker (A)"),
    ("donor2", "0"): ("RPE", "canonical", "marker: RPE65#7 TTR (A)"),
    ("donor2", "1"): ("RPE", "mito-high", "marker: MT-* 主导 + RPE65/BEST1 (A)"),
    ("donor2", "2"): ("PR-associated", "rod/cone-transcripts", "marker (A)"),
    ("donor2", "3"): ("RPE", "canonical (NDUFS7+)", "marker (A)"),
    ("donor2", "4"): ("RPE", "pigment (TYRP1+/BEST1+)", "marker (A)"),
    ("donor2", "5"): ("erythroid", "HBG1/HBG2+ribosomal", "marker (A)"),
    ("donor2", "6"): ("RPE", "complement-high (C4A/C4B+/PMEL+/TRPM3+)",
                      "RPE 谱系 (TRPM3/PMEL) + 补体状态 (A)"),
    ("donor2", "7"): ("myeloid", "CD74/AIF1/HLA-DR/CCL3", "marker (A)"),
    ("donor3", "0"): ("RPE", "canonical", "marker: RPE65#2 (A)"),
    ("donor3", "1"): ("erythroid", "HBG+ribosomal", "marker (A)"),
    ("donor3", "2"): ("PR-associated", "rod-transcripts (RHO/RCVRN/ABCA4)", "marker (A)"),
    ("donor3", "3"): ("RPE", "pigment-high (TYRP1+/BEST1+)", "marker (A)"),
    ("donor3", "4"): ("erythroid", "HBG+ribosomal", "marker (A)"),
    ("donor4", "0"): ("PR-associated", "rod-program (SAG/RHO/PDE6A)", "marker (A)"),
    ("donor4", "1"): ("RPE", "mito-high", "marker (A)"),
    ("donor4", "2"): ("erythroid", "HBG+ribosomal", "marker (A)"),
    ("donor4", "3"): ("RPE", "TF/GPX3 stress state (TF#2/TRPM3+)",
                      "与 donor1 TF+SPP1 簇 marker 重叠 (C)"),
    ("donor4", "4"): ("RPE", "canonical (HSP-high)", "marker (A)"),
}


def build_RPE():
    import csv as _csv
    rows = list(_csv.DictReader(open(RPE_CELLS, encoding="utf-8")))
    per_unit = defaultdict(Counter)
    tech_by_donor = {}
    for r in rows:
        key = (r["donor"], r["cluster"])
        cls = RPE_CLUSTER_LABELS[key][0]
        per_unit[r["donor"]][cls] += 1
        tech_by_donor[r["donor"]] = r["tech"]
    classes = ["RPE", "PR-associated", "neuron-like", "erythroid", "myeloid"]
    fr = defaultdict(list)
    for u, cnt in per_unit.items():
        tot = sum(cnt.values())
        for c in classes:
            fr[c].append(100.0 * cnt.get(c, 0) / tot)
    main_stats = {}
    for c in classes:
        arr = np.array(fr[c])
        main_stats[c] = {
            "n_units": int(len(arr)),
            "median_pct": round(float(np.median(arr)), 2),
            "iqr_pct": [round(float(np.percentile(arr, 25)), 2),
                        round(float(np.percentile(arr, 75)), 2)],
            "range_pct": [round(float(arr.min()), 2), round(float(arr.max()), 2)],
        }
    pooled = Counter()
    for cnt in per_unit.values():
        pooled.update(cnt)
    pooled_pct = pct_table(pooled, classes)
    n_tot = sum(pooled.values())
    # fine_types: donor × cluster 占比 + 状态标签
    mk = defaultdict(list)
    for r2 in rows:
        mk[(r2["donor"], r2["cluster"])].append(r2)
    fine = {}
    for d in sorted(per_unit):
        tot = sum(per_unit[d].values())
        lst = []
        for (dd, cl), rs in sorted(mk.items(), key=lambda x: (x[0][0], int(x[0][1]))):
            if dd != d:
                continue
            cls, state, _ev = RPE_CLUSTER_LABELS[(dd, cl)]
            lst.append([f"cl{cl}→{cls} [{state}]", round(100.0 * len(rs) / tot, 1)])
        fine[d] = lst
    states = []
    for (d, cl), (cls, state, ev) in sorted(RPE_CLUSTER_LABELS.items(),
                                            key=lambda x: (x[0][0], int(x[0][1]))):
        states.append({"cell_type": f"{d} cl{cl}", "state": f"{cls}: {state}",
                       "markers": ev, "evidence": "A+B/C"})
    entry = {
        "schema": "eyekb-baseline/1.0",
        "entry_id": "baseline_human_RPE",
        "tissue": "RPE", "species": "human",
        "title": "组成基线: 人(正常)新鲜分离 RPE 悬液 scRNA — 发育阶段=unknown 档 (OA GSE158629, 供者级 4 供者, 簇身份 marker 推断, KB2c 披露)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "mapping_from_t_6f5cc731 GSE158629 行 (未单列 OA-D 号)",
            "local_path": RPE_RDATA,
            "geo": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158629",
            "tier": "T2 处理件回填 (作者 Seurat RData; 无官方 celltype 列 → 本项目 marker 标注)",
        },
        "t2_fields": {
            "取样材料": "人新鲜分离 RPE 单层细胞 (4 具成人供体眼, stage=Fresh; "
                       "GEO: 'RPE cells were isolated from four adult human donor eyes')",
            "疾病阶段": "normal (健康供体; 处理件元数据无疾病列)",
            "治疗背景": "未记录 (处理件元数据无治疗列) —— 标'未记录', 不臆测",
            "scRNA_vs_snRNA": "scRNA-seq 全细胞 (donor1=10x 3'; donor2-4=ICELL8 液滴克隆) —— "
                              "与 snRNA 条 (retina/optic_nerve) 口径不同, 不可直接互比",
            "富集步骤": "RPE 层机械+酶分离富集 (组织级); 无荧光分选记录 —— 分离流程本身即'富集'",
            "解离方法": "新鲜眼离体后 RPE 分离 (GEO Methods; 处理件无解离试剂列, 细节未记录)",
            "供者数": "4 (donor1=10x, donor2-4=ICELL8 —— 平台与供者完全捆绑, tech 分层=描述性)",
            "计数分母": f"{n_tot:,} cells (4 个 donor 对象 26 簇, 全标注)",
            "证据来源": "本地实测复算 (A: 比例; RData→CSV 导出脚本 export_rpe_meta.R) + "
                       "GEO 记录作者簇描述 (B: rod/cone/TF+SPP1/干细胞候选) + 本项目 marker 推断 (C)",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "供者级 (4 供者单元; 每供者内先把 marker 同类簇合并成 canonical 类再算占比; "
                               "各 donor 对象独立聚类, 跨 donor 簇定义靠 marker 对齐 —— 见 caveats)",
        "main_heading": "主参考: 供者级条件参考分布 (n=4 供者; marker 推断 canonical 类)",
        "donor_level_main": main_stats,
        "pooled_all_cells": pooled_pct,
        "strata": None,
        "major_classes": [],
        "fine_types": {"denominator_note": "donor × 原簇 → canonical 类 [状态标签] 占该 donor 细胞%; "
                                           "RData 原生簇编号原样保留"},
        "states": states,
        "flags": {
            "expected_low_but_present": [
                "myeloid (CD74/AIF1/HLA-DR) 仅 donor2 检出; erythroid 仅 ICELL8 供者检出",
                "干细胞候选群 (RPE65+/VIM/GNL3/MKI67, 作者描述 B): 未在任何簇 top25 浮现 —— 小群未量化, "
                "区间无法估计 (合法状态, Astra T2)"],
            "unexpected": [
                "PR-associated 类 3.8–28.5%: 作者称 RPE 亚群 (cone/rod 转录本簇, B), 亦可为吞噬 PR 外节"
                "mRNA 或盘膜附着污染 —— 双重解释保留, 不下单一结论",
                "neuron-like 类 (VSX1/ISL1/SNAP25) 仅 donor1 (10x) 检出 2.2% —— 视网膜神经污染或低丰度前体, 存疑"],
            "contamination_suspect": [
                f"erythroid (HBG1/HBG2) 供者内最高 {main_stats['erythroid']['range_pct'][1]}% —— 血液残留"],
        },
        "caveats": [
            "身份标注非作者官方命名: 处理件只有 donor×cluster 编号, canonical 类标签为本项目 marker 推断 "
            "(证据 C), 仅 rod/cone/TF+SPP1/干细胞候选四类有 GEO 作者描述锚 (证据 B)。对外引用须带此口径。",
            "n=4 供者, donor 级 median/IQR 极粗 (每供者权重 25%); 区间只作'新鲜分离 RPE 捕获构成'的描述性参考。",
            "各 donor 对象独立聚类无全局整合; 同类簇跨 donor 合并依赖 marker 一致性 (RPE/PR/erythroid 清晰, "
            "neuron-like/状态细分谨慎)。",
            "平台×供者完全捆绑 (10x n=1 / ICELL8 n=3): donor1 独有 neuron-like、donor2-4 独有 erythroid 的差异"
            "不能区分平台效应与供者变异。",
            "本条=分离后 RPE 悬液的捕获构成 (计数分母不含非 RPE 组织的完整组织学), 不代表 RPE 层在完整眼球/脉络膜"
            "组织中的位置丰度; 组织学丰度参考须用带 RPE 的全组织条 (retina/choroid 骨架)。",
        ],
        "sources": [
            {"sid": "RPE_LOCAL", "kind": "dataset",
             "label": f"作者处理件 {RPE_RDATA} (GSE158629); 导出件 "
                      f"{RPE_CELLS} + {RPE_MARKERS} (scripts/baselines/data/export_rpe_meta.R)",
             "path": RPE_RDATA, "computation": f"{__file__} build_RPE()"},
            {"sid": "RPE_GEO", "kind": "dataset",
             "label": "GEO GSE158629 — Single-Cell RNA Sequencing Reveals the Heterogeneity of the "
                      "Human RPE (摘要含 rod/cone/TF+SPP1/干细胞候选簇描述)",
             "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158629"},
        ],
    }
    for c in classes:
        entry["major_classes"].append({
            "class": c,
            "donor_median_pct": main_stats[c]["median_pct"],
            "donor_iqr_pct": main_stats[c]["iqr_pct"],
            "donor_range_pct": main_stats[c]["range_pct"],
            "pooled_pct_for_reference_only": pooled_pct[c],
            "evidence": "A", "source_ids": ["RPE_LOCAL", "RPE_GEO"],
            "note": ("身份=marker 推断 (C), 部分有作者簇描述锚 (B)" if c != "RPE"
                     else "canonical RPE: RPE65/BEST1/TTR/SERPINF1 核心"),
        })
    entry["t2_fields"]["供者数"] = (
        entry["t2_fields"]["供者数"] + " —— KB2c: cells_meta 无年龄列, 本条 organism_stage=unknown "
        "(GEO 文字记 'four adult human donor eyes' 为 B 级文献描述, 不可逐行核验, 禁静默归 adult)")
    entry["caveats"].append(
        "KB2c t_be336eee 红线2: 本条无逐供者发育/年龄元数据 → 发育档=unknown + 披露行, "
        "不得作为 '成人 RPE 基线' 引用; 升级 adult-only 需补逐 donor 年龄 (GEO 附表/作者通信) 后另裁。")
    kb2c_unknown_entry(
        entry,
        "本地 GSE158629 cells_meta (export_rpe_meta.R 导出) 仅 donor/cluster/tech 列, 无 "
        "development_stage/年龄列; GEO Summary 记 'four adult human donor eyes' (证据 B 级)。",
        [{"source": "GSE158629 cells_meta (全 4 donor)", "cells": n_tot, "donors": 4,
          "organism_stage": "unknown", "rule": "无年龄列 → 禁静默归 adult (红线2)",
          "literature_grade_B": "GEO: 'RPE cells were isolated from four adult human donor eyes'"}])
    return entry



# ---------------------------------------------------------------- 9 组织骨架
SKELETON_TISSUES = ["RPE", "choroid", "ciliary_body", "iris", "lens",
                    "optic_nerve", "trabecular_meshwork", "conjunctiva", "sclera"]
FILLED_EXTRAS = {}  # tissue -> builder; main() 中注册, 已回填者从骨架清单剔除

LOCAL_POINTERS = {  # 本地已有文件 (实勘 2026-09-23, find 实证)
    "optic_nerve": "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad",
    "RPE": "/mnt/D/OcularKB/data/GSE158629/ (处理件 RData, 需转换; t_6f5cc731 标注'即拉即用')",
}


def build_skeletons(inv):
    out = []
    for t in SKELETON_TISSUES:
        if t in FILLED_EXTRAS:   # KB1v2b: 已回填供者级的组织不再出骨架
            continue
        rows = inv.get(t, [])
        verdict = (inv.get("verdicts") or {}).get(t, "见 TISSUE_REFERENCE_INVENTORY.md")
        entry = {
            "schema": "eyekb-baseline/1.0",
            "entry_id": f"baseline_human_{t}",
            "tissue": t, "species": "human",
            "title": f"组成基线骨架: 人 {t} (字段全, 比例=待回填)",
            "status": "skeleton_mapping_backfilled",
            "organism_stage": "unknown",
            "stage_note": ("KB2c 发育轴: 骨架条=unknown (未实算)。回填时必须按发育轴单列 — "
                           "adult 材料出 adult-only 主档 (>=18y 裁定 Q2), 胎儿/发育期材料另立条目, "
                           "禁止胎儿与成人同组织混档 (PI 红线)。"),
            "stage_axis": stage_axis_block(f"baseline_human_{t}"),
            "generated": TODAY, "generator": GEN, "card": "t_16c3e020",
            "anchor": {"tier": "骨架 (t_6f5cc731 盘点映射已回填; 供者级比例未算)"},
            "mapping_from_t_6f5cc731": [
                {k: r.get(k) for k in ("acc", "sp", "scale", "annot", "avail", "note")}
                for r in rows],
            "verdict": verdict,
            "local_file_pointer": LOCAL_POINTERS.get(t),
            "t2_fields": {
                "取样材料": "待定 (骨架: 建基线前必须先固定实际取样材料口径, Astra T2)",
                "疾病阶段": "待定", "治疗背景": "待定",
                "scRNA_vs_snRNA": "待定", "富集步骤": "待定", "解离方法": "待定",
                "供者数": "待定", "计数分母": "待定",
                "证据来源": "见 mapping_from_t_6f5cc731 各候选数据集",
            },
            "usage_scope": USAGE_SCOPE,
            "evidence_grades": EVIDENCE_GRADES,
            "distribution_method": None,
            "donor_level_main": None,
            "composition_status": "区间无法估计 (合法状态, Astra T2) —— 待按映射候选数据集做供者级计算; "
                                  "数据不在本地者须先过下载审批铁律",
            "major_classes": [],
            "backfill_path": ("①候选数据本地化状态核实 → ②官方注释切片 (celltype-annotation-sourcing 纪律) → "
                              "③本脚本追加 build_<tissue>() 供者级复算 → ④基线状态改 filled_donor_level → "
                              "⑤KB2c 发育轴: 仅 adult (>=18y) 供者入主档, 非 adult 逐行披露; "
                              "胎儿/发育期材料单独立条目, 禁并入 adult"),
            "caveats": ["骨架条目不得用于'该组织已有组成基线'的对外表述 (Astra T6: 工程一致性≠正确性证据)"],
        }
        out.append(entry)
    return out


# ---------------------------------------------------------------- 渲染
def fmt_dist(stats, classes):
    lines = ["| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |",
             "|---|---|---|---|---|"]
    for c in classes:
        s = stats[c]
        lines.append(f"| {c} | {s['median_pct']} | {s['iqr_pct'][0]}–{s['iqr_pct'][1]} "
                     f"| {s['range_pct'][0]}–{s['range_pct'][1]} | {s['n_units']} |")
    return "\n".join(lines)


def render_md(e):
    L = [f"# {e['title']}", ""]
    L.append(f"> schema: `{e['schema']}` | entry_id: `{e['entry_id']}` | 状态: {e['status']} "
             f"| 发育轴: **organism_stage={e.get('organism_stage', '—')}** "
             f"| 生成: {e['generated']} | 卡片: {e['card']}")
    if e.get("development_stage"):
        L.append(f"> **KB3 发育档 (卡片 {KB3_CARD})**: development_stage=**{e['development_stage']}**"
                 + (f" | 适用档(回填时写死): {e['kb3_applicable_stage_at_backfill'].split(' ——')[0]}"
                    if e.get("kb3_applicable_stage_at_backfill") else "")
                 + f" —— {KB3_PROHIBITION}")
    L.append(f"> 本文件由 `/mnt/D/EyeKB/scripts/baselines/{Path(__file__).name}` 从同名 .json 自动渲染 "
             f"—— 改内容改 JSON+脚本, 手改 MD 会被覆盖。")
    if e.get("stage_note"):
        L.append(f"> ⚠ 发育轴披露: {e['stage_note']}")
    L.append("")
    L.append(f"**{e['usage_scope']}**")
    L.append("")
    L.append("## 证据等级口径")
    for k, v in e["evidence_grades"].items():
        L.append(f"- **{k}**: {v}")
    L.append("")
    if e.get("stage_axis"):
        sa = e["stage_axis"]
        L.append("## 发育轴口径 (KB2c 裁定 2026-09-23 — 阈值改动须过裁定)")
        L.append(f"- 顶层轴: `{sa['field']}` ∈ {sa['levels']}")
        L.append(f"- **adult**: {sa['adult_rule']}")
        L.append(f"- **developing**: {sa['developing_rule']}")
        L.append(f"- **fetal**: {sa['fetal_rule']}")
        L.append(f"- **unknown**: {sa['unknown_rule']}")
        L.append(f"- aging 正交轴: {sa['aging_note']}")
        L.append(f"- 两档身份: {sa['tier_ids']}")
        L.append("")
    L.append("## Astra T2 元数据字段")
    for k, v in e["t2_fields"].items():
        L.append(f"- **{k}**: {v}")
    L.append("")
    if e["status"] == "filled_donor_level":
        classes = [r["class"] for r in e["major_classes"]]
        L.append("## " + (e.get("main_heading")
                           or "主参考: 供者级条件参考分布 (排除分选设计层)"))
        if e.get("primary_reference_stratum"):
            L.append(f"> 分层口径: {e['primary_reference_stratum']}; 方法: {e['distribution_method']}")
        L.append(f"> ⚠ {KB3_PROHIBITION}")
        L.append("")
        L.append(fmt_dist(e["donor_level_main"], classes))
        L.append("")
        if e.get("donor_level_adult_pool_contrast"):
            L.append(f"### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; "
                     f"tier=`{e['stage_axis']['tier_ids']['adult_pool']}`) —— 引用 v1.0 旧数字只能挂此档身份")
            L.append("")
            L.append(fmt_dist(e["donor_level_adult_pool_contrast"], classes))
            L.append("")
        if e.get("stage_disclosure"):
            L.append("### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)")
            if isinstance(e["stage_disclosure"], list):
                L.append("| 来源 | organism_stage | 规则 | 细胞数 | 供者数 | 文献级描述 (B) |")
                L.append("|---|---|---|---|---|---|")
                for x in e["stage_disclosure"]:
                    L.append(f"| {x.get('source','')} | {x.get('organism_stage','')} "
                             f"| {x.get('rule','')} | {x.get('cells', 0):,} | {x.get('donors','')} "
                             f"| {x.get('literature_grade_B','')} |")
            else:
                L.append("| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |")
                L.append("|---|---|---|---|---|")
                for ub, v in e["stage_disclosure"].items():
                    L.append(f"| {ub} | {v['organism_stage']} | {v['rule']} "
                             f"| {v['cells']:,} | {v['n_donors']} |")
                if e.get("excluded_nonadult_units"):
                    L.append("")
                    L.append(f"被剔出 adult 主档的供者 {len(e['excluded_nonadult_units'])} 个: "
                             + "; ".join(f"`{x['donor_id']}`({x['organism_stage']}, {x['uberon']}, "
                                         f"{x['cells']:,}核)" for x in e["excluded_nonadult_units"]))
            L.append("")
        L.append("## 工具兼容主表 (major_classes)")
        L.append("| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |")
        L.append("|---|---|---|---|---|---|---|")
        for r in e["major_classes"]:
            mk = ", ".join(r.get("markers_local_lib") or [])
            L.append(f"| {r['class']} | {r['donor_median_pct']} | {r['donor_iqr_pct'][0]}–{r['donor_iqr_pct'][1]} "
                     f"| {r['donor_range_pct'][0]}–{r['donor_range_pct'][1]} "
                     f"| {r['pooled_pct_for_reference_only']} | {mk} | {r['evidence']} |")
        L.append("")
        if e.get("strata"):
            L.append("## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)")
            for s in e["strata"]:
                key = (s.get("study") or "") + (f"|{s['enrichment']}" if "enrichment" in s
                                                else f"|{s.get('tissue_group','')}")
                flag = " ⚠分选设计层" if s.get("sorted_design_flag") else ""
                if s.get("adult_fallback_guard"):
                    flag += " ⚠FALLBACK_BLOCKED"
                L.append(f"### 层: {key}{flag}  (n_donors={s['n_donors']}, n_cells={s['n_cells']:,}"
                         + (f", 占图谱{s['share_of_atlas_pct']}%" if "share_of_atlas_pct" in s else "") + ")")
                L.append("")
                if s.get("adult_fallback_guard"):
                    L.append(f"> {s['adult_fallback_guard']}")
                    L.append("")
                    L.append("*下表=该层 pool 口径 (仅对照):*")
                    L.append("")
                    L.append(fmt_dist(s["donor_level"], classes))
                else:
                    L.append(fmt_dist(s["donor_level_adult_only"], classes))
                L.append("")
        if e.get("fine_types"):
            L.append("## 亚型层 (类内注释细胞占比%, pooled within class 口径)")
            for c, v in e["fine_types"].items():
                if c == "denominator_note":
                    continue
                if isinstance(v, dict) and "top" in v:
                    L.append(f"- **{c}** ({v['basis']}): " + "; ".join(f"{k} {p}%" for k, p in v["top"]))
                elif isinstance(v, list):
                    L.append(f"- **{c}**: " + "; ".join(f"{k} {p}%" for k, p in v))
            L.append("")
        if e.get("states"):
            L.append("## 状态层")
            for s in e["states"]:
                L.append(f"- **{s['cell_type']}** [{s['state']}]: {', '.join(s['markers'])} "
                         f"(证据 {s['evidence']})")
            L.append("")
    else:
        L.append("## 组成数据状态")
        L.append(f"**{e['composition_status']}**")
        L.append("")
        L.append("## 候选数据集映射 (t_6f5cc731 盘点回填)")
        for r in e["mapping_from_t_6f5cc731"]:
            L.append(f"- `{r.get('acc')}` [{r.get('sp')}] {r.get('scale')} | 注释: {r.get('annot')} "
                     f"| 可得性: {r.get('avail')} | {r.get('note') or ''}")
        L.append("")
        L.append(f"**裁定 (t_6f5cc731)**: {e['verdict']}")
        L.append("")
        if e.get("local_file_pointer"):
            L.append(f"**本地文件**: `{e['local_file_pointer']}`")
            L.append("")
        L.append(f"**回填路径**: {e['backfill_path']}")
        L.append("")
    if e.get("flags"):
        L.append("## 旗标语义")
        for g in ("expected_low_but_present", "unexpected", "contamination_suspect"):
            if e["flags"].get(g):
                L.append(f"**{g}**: " + "; ".join(e["flags"][g]))
                L.append("")
    if e.get("caveats"):
        L.append("## 注意事项")
        for i, c in enumerate(e["caveats"], 1):
            L.append(f"{i}. {c}")
        L.append("")
    if e.get("sources"):
        L.append("## 出处清单")
        L.append("| sid | 类型 | 标签 |")
        L.append("|---|---|---|")
        for s in e["sources"]:
            L.append(f"| `{s['sid']}` | {s.get('kind','')} | {s.get('label','')} "
                     f"{'(PMID '+str(s.get('pmid'))+')' if s.get('pmid') else ''} |")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    old = json.loads(OLD_RETINA.read_text(encoding="utf-8"))
    inv_full = json.loads(Path(INVENTORY).read_text(encoding="utf-8"))
    inv = inv_full["inventory"]
    inv_wrapped = dict(inv)
    inv_wrapped["verdicts"] = inv_full.get("verdicts", {})

    FILLED_EXTRAS.update({"optic_nerve": build_optic_nerve,
                        "trabecular_meshwork": build_trabecular_meshwork,
                        "ciliary_body": build_ciliary_body})
    if "build_RPE" in globals():
        FILLED_EXTRAS["RPE"] = build_RPE
    entries = ([build_retina(old), build_ocular_surface()]
               + [fn() for fn in FILLED_EXTRAS.values()]
               + build_skeletons(inv_wrapped))
    # ---- KB2c finalize: schema 1.1 + 两档身份签名 (红线: 签名不混用) ----
    for e in entries:
        e["schema"] = "eyekb-baseline/1.1"
        e["axis_version"] = "kb2c-1.1"
        kb3_augment(e)  # KB3 (t_5425a7ca): development_stage 必填 + 禁令入档
        if e.get("organism_stage") == "adult":
            tids = e["stage_axis"]["tier_ids"]
            e["identity_signature"] = {
                tids["adult_only"]: sha256_obj(
                    {"tier": tids["adult_only"],
                     "donor_level_main": e["donor_level_main"],
                     "pooled_adult_only_main": e.get("pooled_adult_only_main")}),
                tids["adult_pool"]: sha256_obj(
                    {"tier": tids["adult_pool"],
                     "donor_level": e["donor_level_adult_pool_contrast"],
                     "pooled_all_cells": e["pooled_all_cells"]}),
            }
        elif e.get("stage_axis"):
            tids = e["stage_axis"]["tier_ids"]
            key = next(iter(tids))
            e["identity_signature"] = {
                tids[key]: sha256_obj({"tier": tids[key],
                                       "organism_stage": e["organism_stage"],
                                       "donor_level_main": e.get("donor_level_main")})}
    index = {"schema": "eyekb-baselines-index/1.1", "generated": TODAY,
             "generator": GEN, "card": "t_be336eee",
             "supersedes": "index 1.0 (card t_16c3e020)",
             "note": ("眼科通用架构 (PI 2026-09-23 口径): 组成基线按组织锚定 registry 已注释标准集; "
                      "旧 kb/priors/composition/ 为 v1 口径存档, MCP get_tissue_composition 优先读本目录。"
                      "KB2c (t_be336eee) 发育轴单列: 顶层轴 organism_stage 4 级 "
                      "{fetal, adult, developing, unknown}; adult 主档=donor_age>=18y 供者单元 "
                      "(裁定 Q2, 阈值改动须过裁定); v1.0 混口径降为 adult_pool 对照档, "
                      "两档 entry_id/身份签名分离; unknown 必须披露行禁静默归 adult; "
                      "fetal/developing 组成条目见 fetal_development_transitions。"),
             "stage_axis": stage_axis_block("baseline_human_<tissue>"),
             "entries": []}
    for e in entries:
        t = e["tissue"]
        (OUT_DIR / f"{t}.json").write_text(
            json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT_DIR / f"{t}.md").write_text(render_md(e), encoding="utf-8")
        index["entries"].append({
            "tissue": t, "file": f"{t}.md", "status": e["status"],
            "organism_stage": e.get("organism_stage", "unknown"),
            "development_stage": e.get("development_stage", "unknown"),
            "anchor": (e.get("anchor") or {}).get("registry_row", "—"),
            "n_donors": (e["t2_fields"].get("供者数") if e["status"] == "filled_donor_level"
                         else None),
            "tiers": (e.get("stage_axis") or {}).get("tier_ids"),
            "identity_signature": e.get("identity_signature")})
    # ---- KB3 (t_5425a7ca): 发育期独立条目登记 (不进 entries=11 成人档数组; 见回归锁) ----
    index["kb3_note"] = ("KB3 发育轴全量单列: 每条基线增 development_stage 必填字段 "
                         "(枚举 adult/fetal_developing/postnatal_neonatal/mixed_not_separable/"
                         "unknown); 发育期条目独立文件 (schema eyekb-baseline-development/1.0, "
                         "MCP 成人查询不可见), 登记于 development_entries; 参考分布段禁令已入档。")
    _dev_files = sorted(OUT_DIR.glob("*__*.json"))
    _dev_recs = []
    for p in _dev_files:  # KB3 修复 (run 1768): 原海象推导式 if 子句引用未绑定 d → UnboundLocalError
        d = json.loads(p.read_text(encoding="utf-8"))
        if not (d.get("schema") or "").startswith("eyekb-baseline-development/"):
            continue
        _dev_recs.append({"entry_id": d["entry_id"], "file": p.name,
                          "tissue": d.get("tissue"),
                          "development_stage": d.get("development_stage"),
                          "anchors": [c["acc"] for c in d.get("anchors", [])],
                          "status": d.get("status")})
    index["development_entries"] = _dev_recs
    # ---- KB2c: 汇总逐行披露表 (_STAGE_DISCLOSURE) ----
    disc = {t: {"organism_stage_main": e.get("organism_stage"),
                "stage_disclosure": e.get("stage_disclosure"),
                "excluded_nonadult_units": e.get("excluded_nonadult_units"),
                "source": (e.get("anchor") or {}).get("local_path")}
            for e in entries if (t := e["tissue"]) and e.get("stage_disclosure")}
    (OUT_DIR / "_STAGE_DISCLOSURE.json").write_text(
        json.dumps({"schema": "eyekb-stage-disclosure/1.0", "generated": TODAY,
                    "card": "t_be336eee",
                    "note": "KB2c 红线2: adult 基线中全部非 adult 供者/unknown 源逐行披露; "
                            "fetal 期实测=0 (污染源实为 newborn/儿童/青少年)。",
                    "by_tissue": disc}, ensure_ascii=False, indent=1), encoding="utf-8")
    dl = ["# 发育轴逐行披露表 (KB2c t_be336eee — 红线2: 禁静默)", "",
          f"> schema: eyekb-stage-disclosure/1.0 | 生成: {TODAY} | 生成器: {GEN}",
          "> adult 主档 = donor_age>=18y (裁定 Q2); 下表列出每个 filled 条的全部非 adult 供者单元。",
          "> 实测: 4 个 h5ad 源胎儿期核数=0 —— 红线条面'含胎儿 donor'实为 newborn/儿童/青少年混入, 已全部剔出主档。", ""]
    for t, d in disc.items():
        dl.append(f"## {t} (主档 organism_stage={d['organism_stage_main']})")
        if d.get("excluded_nonadult_units"):
            dl.append("| 被剔供者 | organism_stage | UBERON 原值 | 核数 | 规则 |")
            dl.append("|---|---|---|---|---|")
            for x in d["excluded_nonadult_units"]:
                dl.append(f"| `{x['donor_id']}` | {x['organism_stage']} | {x['uberon']} "
                          f"| {x['cells']:,} | {x['rule']} |")
        elif isinstance(d.get("stage_disclosure"), list):
            for x in d["stage_disclosure"]:
                dl.append(f"- unknown 披露: {x.get('source')} — {x.get('rule')}; "
                          f"文献级: {x.get('literature_grade_B','')}")
        dl.append("")
    (OUT_DIR / "_STAGE_DISCLOSURE.md").write_text("\n".join(dl) + "\n", encoding="utf-8")
    # ---- KB2c Q5: fetal/developing 转换态概念条目 (不实算) ----
    fetal = {
        "schema": "eyekb-baseline-concept/1.0",
        "entry_id": "fetal_development_transitions",
        "title": "胎儿/发育期 眼组织 转换态概念条目 (KB2c 裁定 Q5 — 非成人桶分身, 不实算组成)",
        "generated": TODAY, "generator": GEN, "card": "t_be336eee",
        "organism_stage": ["fetal", "developing"],
        "nature": ("本条目=概念占位: 登记未来的 fetal/developing 基线候选与其前提, "
                   "**不是组成基线** —— 胎儿的这些和成人的即使是一个组织也不对 (PI 红线), "
                   "禁止把本条目当任何组织的成人桶引用或反向借用。"),
        "current_facts": {
            "filled_adult_baselines": 6,
            "fetal_stage_nuclei_in_filled_sources": 0,
            "nonadult_in_filled_sources": ("newborn/儿童/青少年供者 (逐行见 _STAGE_DISCLOSURE.md), "
                                           "已从 adult 主档剔除; 未来 developing 基线的本地素材"),
            "engine_applicability": "现役判读引擎 (OcularKB M3 等) 训练/适用域=成人组织 —— 现役引擎"
                                    "不适用 fetal/发育期样本, 对这类材料必须弃权 (评估层 E4=OOD_严格, "
                                    "指令条款3); 需另建 fetal 参考管线后方可立组成条目",
        },
        "candidates": [
            {"acc": "GSE268630", "desc": "人胎视网膜 multiome ~22万核", "tier": "fetal",
             "local": True, "note": "指令条款4 首选候选; 入基线前需 fetal 参考管线任务"},
            {"acc": "GSE137828", "desc": "人胎视网膜 (fetal)", "tier": "fetal",
             "local": "待核", "note": "指令条款4 列名"},
            {"acc": "GSE137863", "desc": "人胎视网膜发育 (fetal)", "tier": "fetal",
             "local": "待核", "note": "指令条款4 列名"},
            {"acc": "GSE138002", "desc": "视网膜类器官", "tier": "organoid→unknown+旗标 (裁定 Q1)",
             "local": "待核", "note": "类器官≠胎儿组织, 也≠成人; 单列"},
            {"acc": "GSE234963", "desc": "类器官集", "tier": "organoid→unknown+旗标",
             "local": "待核", "note": "指令条款4 列名"},
            {"acc": "GSE235577", "desc": "类器官/多组学", "tier": "organoid→unknown+旗标",
             "local": "待核", "note": "08-28 盘点实为 snATAC/多组学 ATAC 组分 — 转换前须重核平台口径"},
        ],
        "out_of_scope": ("胎儿/发育期组成实算=另批任务 (裁定 Q5); >=60 老年分层=正交 aging 轴, 不在发育轴内。"),
        "usage_redline": ("本条目所有候选不得并入任何 adult 条; 引用本条目必须连带"
                          "'需 fetal 参考管线, 现役引擎不适用'声明。"),
    }
    (OUT_DIR / "fetal_development_transitions.json").write_text(
        json.dumps(fetal, ensure_ascii=False, indent=1), encoding="utf-8")
    fl = [f"# {fetal['title']}", "",
          f"> schema: `{fetal['schema']}` | entry_id: `{fetal['entry_id']}` | 生成: {TODAY} | 卡片: {fetal['card']}",
          f"> 本文件由 build_baselines.py (KB2c) 生成; 手改会被覆盖。", "",
          fetal["nature"], "", "## 现状事实", ""]
    for k, v in fetal["current_facts"].items():
        fl.append(f"- **{k}**: {v}")
    fl += ["", "## 候选数据集 (指令条款4 — 全部未入基线)", "",
           "| accession | 描述 | 发育档 | 本地 | 备注 |", "|---|---|---|---|---|"]
    for c in fetal["candidates"]:
        fl.append(f"| `{c['acc']}` | {c['desc']} | {c['tier']} | {c['local']} | {c['note']} |")
    fl += ["", f"**范围外**: {fetal['out_of_scope']}", "",
           f"**使用红线**: {fetal['usage_redline']}", ""]
    (OUT_DIR / "fetal_development_transitions.md").write_text("\n".join(fl) + "\n", encoding="utf-8")
    (OUT_DIR / "baselines.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written:", len(entries), "entries + _STAGE_DISCLOSURE + fetal transitions →", OUT_DIR)
    # 快速自检: retina adult-only 主档 vs 对照档
    r = entries[0]
    print("retina main(adult-only) n_units:", r["donor_level_main"]["Rod"]["n_units"],
          "| pool n_units:", r["donor_level_adult_pool_contrast"]["Rod"]["n_units"],
          "| excluded nonadult donors:", len(r["excluded_nonadult_units"]))
    for c in ["Rod", "MG", "Microglia", "RPE"]:
        s = r["donor_level_main"][c]
        print(f"  {c}: adult-only median {s['median_pct']}% IQR {s['iqr_pct']} "
              f"(pool对照 {r['donor_level_adult_pool_contrast'][c]['median_pct']}%)")
    o = entries[1]
    print("ocular_surface main n_units:", o["donor_level_main"]["Epithelium"]["n_units"])
    for c in ["Epithelium", "Fibroblasts", "Immune Cells", "Corneal Endothelium"]:
        s = o["donor_level_main"][c]
        print(f"  {c}: donor-median {s['median_pct']}% IQR {s['iqr_pct']} (pooled {o['pooled_all_cells'][c]}%)")


if __name__ == "__main__":
    sys.exit(main())
