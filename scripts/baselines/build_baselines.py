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

Inputs (all read-only):
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
    "cornea": "cornea (includes corneal epithelium/stroma)",
    "substantia propria of cornea": "cornea (includes corneal epithelium/stroma)",
    "corneal epithelium": "cornea (includes corneal epithelium/stroma)",
    "corneal endothelium": "corneal endothelium (separate layer, only 404 cells)",
    "corneo-scleral junction": "corneo-scleral junction (limbus region)",
    "sclera": "sclera",
    "tunica fibrosa of eyeball": "sclera",
    "ocular surface region": "ocular surface region (mixed)",
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
            guard = ("FALLBACK_BLOCKED: All donors in this tissue group are non-adult (e.g., newborn-only layer), "
                     "adult-only does not exist — silent fallback to pool prohibited (KB2c Red Line 2)")
        strata.append({"tissue_group": g, "n_donors": nu,
                       "n_cells": len(rows_s), "donor_level": stats,
                       "donor_level_adult_only": stats_a,
                       "n_units_adult_only": nu_a,
                       "adult_fallback_guard": guard})
    # Primary reference (KB2c)= adult donors only among full-library donor-level (donor|tissue group units); control tier= old v1.0 whole-pool scope"
    main_rows = [r for g in rows_by_g for r in rows_by_g[g]]
    pool_stats, pool_nd = donor_stats(main_rows, classes)
    main_rows_a = [r for r in main_rows if dsm[r[0][-1]][1] == "adult"]
    main_stats, main_nd = donor_stats(main_rows_a, classes)
    pooled_adult_main = (pct_table(Counter([r[1] for r in main_rows_a]), classes)
                         if main_rows_a else None)
    all_adult = [i for i in range(n) if dsm[donor[i]][1] == "adult"]
    excluded = excluded_units(donor, mc, dsm, classes)
    # Top author_cell_type within class (pooled within class, criteria annotated)
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
        "title": "Composition baseline: Human (normal) ocular surface adult-only primary archive — Cornea/Limbus/Sclera super-class (D002, donor-level conditional reference distribution, KB2c developmental axis listed separately)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_16c3e020",
        "anchor": {
            "registry_row": "OA-D002 (CELLxGENE-OcularSurface)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": D002,
            "collection": "https://cellxgene.cziscience.com/collections/0f7d022a-46c7-4e64-be4c-e34adbb78089",
            "tier": "T1 annotated standard set",
        },
        "category_note": ("Ocular surface is a super-class (merged scope of cornea/limbus/sclera/conjunctiva; category=per-region, cross-region application prohibited); "
                          "conjunctiva/sclera independent skeleton established separately (t_6f5cc731 adjudication: conjunctiva=insufficient data, recommend merging into ocular surface subpopulation annotation)."),
        "t2_fields": {
            "Sampling material": "Human ocular surface ex vivo tissues: cornea / corneo-scleral junction(limbus) / sclera / "
                       "ocular surface region / corneal endothelium (fragments from the edge of transplanted corneal endothelium)",
            "Disease stage": "normal (disease column all normal; donors are eye bank donated limbus/scleral ring)",
            "Treatment background": "Not recorded (eye bank donation metadata lacks treatment column)",
            "Platform": "scRNA-seq (suspension_type=cell 100%, 10x 3' v2/v3) —— Different scope from D001 retina(nuclei), note when comparing across baselines",
            "Enrichment steps": "No cell sorting records (whole tissue dissociation directly loaded onto machine)",
            "Dissociation method": "Mechanical + enzymatic dissociation; key reagents: " + "; ".join(f"{k}×{v:,} cells" for k, v in diss.items()),
            "Donor count": f"{len(set(donor.tolist()))} donors (local 578K file); collection-level registry records 102 — local is a subset extraction",
            "Count denominator": f"{n:,} cells (majorclass fully annotated)",
            "Evidence source": "Local empirical recalculation (A) + CELLxGENE collection official annotation (portal)",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "Donor-level (donor|tissue group unit); tissue groups stratified first, no cross-group merging (Astra T2); KB2c: primary archive contains only adult donor units; pooled used only for contrast",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type intra-class proportion (pooled within class, for reference)",
                       **fine},
        "states": None,
        "flags": {
            "expected_low_but_present": [
                "Corneal Endothelium (pooled 0.07%) —— Contributed only by eye bank endothelial edge fragments, near-zero in routine limbal samples",
                "Melanocytes/Schwann Cells/Smooth Muscle Cells <2%"],
            "unexpected": ["Photoreceptor/retinal neuron classes appear (sampling overreach into retina?)",
                           "High abundance of hematopoietic maturity markers (FCN1/LYZ granulocytic lineage) —— Donor blood residue flag"],
            "contamination_suspect": [
                "published_annotation column dominated by red blood cells layer (525,617 annotations) —— Blood residue is known primary contamination in this library, see caveat",
                "Melanin granule/pigmented tissue contamination (pigmented donor sclera)"],
        },
        "caveats": [
            "Local D002 file = 577,857 cells / 50 donors, a subset extraction from collection level (>1M/102) (metric=local measurement); "
            "Backfilling the entire collection requires download approval; listed as 'pending backfill'.",
            "'Majorclass=Immune Cells' only 1.7%: Ocular surface resident immunity scarce + no immune enrichment step —— Immune proportion cannot be compared against inflammatory disease samples.",
            "published_annotation coexists with majorclass: published_annotation='red blood cells' predominance indicates RBCs not removed from "
            "completely removed in majorclass? No — the 9 majorclass categories lack an RBC class; RBC signals are dispersed across all classes, and the count denominator includes RBC-contaminated nuclei,"
            "Percentages per category represent 'captured event composition', not tissue ground truth (Astra T2 scope statement).",
            "Sclera/conjunctiva independent entries see corresponding skeleton files; this entry's corneo-scleral junction layer ≠ independent conjunctival baseline.",
        ],
        "sources": [
            {"sid": "D002_LOCAL", "kind": "dataset", "label": f"Local file {D002}", "path": D002,
             "computation": f"{__file__} build_ocular_surface()"},
            {"sid": "D002_PORTAL", "kind": "dataset",
             "label": "Human Ocular Surface Cell Atlas, CELLxGENE collection (portal official annotation)",
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
    entry["t2_fields"]["Donor count"] = (
        f"Main file adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} donor units; control adult_pool {len(set(donor.tolist()))} donors / {pool_nd} units "
        f"(includes {len(excluded)} non-adult donors such as newborn 0-28d → see excluded_nonadult_units for line-by-line details)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): Primary archive=adult-only (>=18y); v1.0 mixed scope (including newborn 0-28d 25,018 cells + "
        "postnatal/children/adolescents) retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0)."
        "FALLBACK_BLOCKED guard implemented (triggers fallback prohibition when tissue group has 0 adult donors) — this run triggered 0 layers, "
        "All adult-only tissue groups have real support.")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     len(set(donor.tolist())), len(all_adult))
    return entry


# ------------------------------------------------- optic_nerve (HRA006282 / OA-D003)
ON = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"
ON_TISSUE_LABEL = {"cranial nerve II": "ON (Optic Nerve)",
                   "optic disc": "ONH (Optic Nerve Head/Papilla)"}
# ON/ONH acquisition data includes peripapillary retinal tissue — these classes represent 'capture composition' rather than true optic nerve composition (Astra T2)
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
            guard = ("FALLBACK_BLOCKED: No adult donors in this source×site layer, adult-only does not exist —— "
                     "Silent fallback to pool prohibited (KB2c red line 2)")
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
        "title": "Composition baseline: Human (normal) optic nerve + optic nerve head snRNA adult-only master file (OA-D003 HRA006282, donor-level conditional reference distribution, KB2c developmental axis listed separately).",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "OA-D003 (CELLxGENE-OpticNerve)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": ON,
            "collection": "https://cellxgene.cziscience.com/collections/05e3d0fc-c9dd-4f14-9163-2b242b3bb5c2",
            "tier": "T1 Annotated standard set (portal official annotations, three layers: majorclass/author_cell_type/cell_type).",
        },
        "t2_fields": {
            "Sampling material": "Human optic nerve/optic disc ex vivo tissues (surgical specimens, eye bank donors; regional composition: "
                       + ", ".join(f"{k} {v:,} nuclei" for k, v in regions.items()) + ")",
            "Disease stage": "normal (disease column entirely normal; donors are systemic death organ donors,"
                       "donor_cause_of_death includes tumor/sepsis etc., no eye disease records for the globe itself)",
            "Treatment background": "Not recorded (eye bank donation metadata lacks treatment column) — marked 'not recorded', no speculation.",
            "scRNA_vs_snRNA": "snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes) —— "
                              "Proportions cannot be directly compared with scRNA cell suspension entries (e.g., D002 ocular surface)",
            "Enrichment steps": "No sorting records (metadata lacks enrichment column; whole-tissue nuclear suspension loaded directly).",
            "Dissociation method": "; ".join(f"{k}×{v:,} nuclei" for k, v in diss.items())
                       + " (sample_preservation=frozen in liquid nitrogen; collection=surgical resection)",
            "Donor count": f"{n_donors} unique donor_id; stratified by source|site|donor yielding {main_nd} donor units",
            "Count denominator": f"{n:,} nuclei (majorclass fully annotated)",
            "Evidence source": "Local empirical recalculation (A) + CELLxGENE HRA006282 collection official annotations (portal) + Registry OA-D003.",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "Donor-level (Source|Site|Donor unit); stratified display by Site(ON vs ONH) × Study Source, "
                               "main aggregates adult donor units (KB2c: non-adult not merged into main archive) — optic nerve ON and ONH"
                               "Significant biological composition differences; prioritize corresponding layer intervals for controls (Astra T2); pooled data for control only",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type intra-class proportion (pooled within class, for reference); "
                                           "ON/ONH/retina suffixes = official portal location subtype annotations"},
        "states": None,
        "flags": {
            "expected_low_but_present": [
                "T/B/NK/DC/Mast total <1% (immune cells sparse in normal neural tissue).",
                "Schwann_cell 0.22% (PN myelin supporting cells; PN enrichment limited to central segment under nuclear suspension).",
                "Mural_cell 1.8% / Endothelial_cell 3.6% (vascular support layer)."],
            "unexpected": [
                f"Retinal neuron classes (Rod/Cone/BC/HC/AC/RGC) pooled {ret_pct}% + RPE/pigmented cells {rpe_pct}% —— "
                "Optic disc sampling introduces peripapillary retina/choroid tissue; this reflects capture composition, not the true composition of the optic nerve itself."
                "When controlling for disease samples, do not treat this layer as 'expected proportion for optic nerve'"],
            "contamination_suspect": [
                "Melanocyte 0.86% (incidental leptomeningeal/pigmented tissue, slightly high within normal range, interpret in context of sampling plane)."],
        },
        "caveats": [
            "MG=Müller glia (1.7%) and Microglia=microglia (5.0%) are two distinct identities, portal vocabulary coexists —— "
            "downstream citations must not conflate them; the same rule applies to retinal abbreviations such as AC (amacrine, 'without a long process') / BC (bipolar cells).",
            "Chen (Baylor, ~85%) and Sanes (Harvard) donor pools differ significantly in scale, displayed stratified by Source × Site into 4 layers;"
            "main donor-level unit equal weighting, large pools no longer dominate, but inter-stratum differences require examining strata rather than only main.",
            "The denominator for this count includes peripapillary retinal sources (~15%); for a 'pure optic nerve' reference interval, use strata containing "
            "ON (cranial nerve II) layer.",
            "Comparison between snRNA scope (nuclear suspension, intronic reads counted) and scRNA data requires caution (Astra T2).",
        ],
        "sources": [
            {"sid": "ON_LOCAL", "kind": "dataset", "label": f"Local file {ON}", "path": ON,
             "computation": f"{__file__} build_optic_nerve()"},
            {"sid": "ON_PORTAL", "kind": "dataset",
             "label": "Human Optic Nerve / Optic Nerve Head Atlas, CELLxGENE collection HRA006282 "
                      "(portal official annotation; registry OA-D003, verified 2026-08-11)",
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
            "note": ("Retina-derived classes — brought in by optic disc sampling, see caveats/flags." if c in ON_RETINA_ASSOC
                     else ("Pigment/RPE-derived classes — same as above." if c in ON_RPE_ASSOC else "")),
        })
    entry["t2_fields"]["Donor count"] = (
        f"Main file adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} donor units; control adult_pool {n_donors} donors / {pool_nd} units "
        f"(includes {len(excluded)} non-adult donors including newborn 15,177 nuclei → see excluded_nonadult_units for line-by-line details)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): Primary archive=adult-only (>=18y, adjudication Q2); v1.0 mixed scope (including newborn/ages 3-17) "
        "Retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0); two-tier identity signatures are separated and not mixed.")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     n_donors, len(all_adult))
    return entry


# ------------------------------------------------- TM + CB (HRA000728_tm_cb / HASA)
# Local file is actually a HASA anterior segment snRNA integration artifact (obs study=chen_tm_cb + sanes_GSE199013);
# t_6f5cc731 inventory: TM primary reference base = GSE199013/HASA (OA-D004=OA-D016) snRNA 1,102,250 nuclei ——
# Precisely matches the measured n=1,102,250 in this file; identified as the same resource. Directory name HRA000728 and registry OA-D028
# (Keratoconus cornea) Name mismatch — content adjudication takes precedence; registry misalignment logged separately; this entry does not cite OA-D028.
TMCB = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
TMCB_UVEA_EXCLUDED = 53406  # tissue=uvea component (5 donors, including sanes layer) excluded from TM/CB sections


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
            guard = ("FALLBACK_BLOCKED: No adult donors in this study layer, adult-only does not exist —— "
                     "Silent fallback to pool prohibited (KB2c red line 2)")
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
        "title": f"Composition baseline: Human (normal){cn} snRNA adult-only main archive ({cn} slices {n:,} nuclei / {n_donors} donors, donor-level conditional reference distribution, KB2c developmental axis listed separately)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "OA-D004=OA-D016 (GSE199013/HASA, t_6f5cc731 inventory TM/CB primary base; "
                            "Local file nucleus count exactly matches HASA entry 1,102,250)",
            "registry_csv": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv",
            "local_path": TMCB,
            "tier": "T1 portal official annotation (majorclass/author_cell_type/cell_type; study=chen_tm_cb+sanes_GSE199013)",
        },
        "t2_fields": {
            "Sampling material": f"Human anterior segment surgical specimens with {cn} anatomical components (tissue column='{tissue_value}' slice; "
                       f"Additionally, uvea component {TMCB_UVEA_EXCLUDED:,} nuclei not included in this entry)",
            "Disease stage": "normal (disease column all normal; donors from systemic death eye banks/surgical materials)",
            "Treatment background": "Not recorded (no treatment column in metadata) — labeled 'not recorded'; no speculation",
            "scRNA_vs_snRNA": "snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)",
            "Enrichment steps": "No sorting records (whole-tissue nuclear suspension loaded directly)",
            "Dissociation method": "; ".join(f"{k}×{v:,} nuclei" for k, v in diss.items())
                       + " (sample_collection_method=surgical resection)",
            "Donor count": f"{n_donors} unique donor_id; stratified by study|donor yielding {main_nd} donor units",
            "Count denominator": f"{n:,} nuclei (majorclass fully annotated within {cn} slices)",
            "Evidence source": "Local empirical recalculation (A) + portal/HASA official annotation (t_6f5cc731 judged as 'portal official')",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "Donor level (study|donor unit); study layer stratified display first; KB2c: primary archive contains only adult donor units; pooled used only for control",
        "donor_level_main": main_stats,
        "pooled_adult_only_main": pooled_adult_main,
        "pooled_all_cells": pooled,
        "strata": strata,
        "major_classes": [],
        "fine_types": {"denominator_note": "author_cell_type intra-class proportion (pooled within class, for reference)"},
        "states": None,
        "flags": {
            "expected_low_but_present": extra_flags_unexpected[0],
            "unexpected": extra_flags_unexpected[1],
            "contamination_suspect": extra_flags_unexpected[2],
        },
        "caveats": extra_caveats,
        "sources": [
            {"sid": f"{cn.upper()}_LOCAL", "kind": "dataset", "label": f"Local file {TMCB}", "path": TMCB,
             "computation": f"{__file__} _build_tmcb('{tissue_value}','{cn}')"},
            {"sid": f"{cn.upper()}_HASA", "kind": "dataset",
             "label": "HASA/anterior segment snRNA collection (t_6f5cc731 inventory mapping OA-D004/OA-D016; "
                      "This slice = its chen_tm_cb + sanes integration component's " + cn + " component)",
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
    entry["t2_fields"]["Donor count"] = (
        f"Main file adult-only {sum(1 for v in dsm.values() if v[1] == 'adult')} donors / "
        f"{main_nd} donor units; control adult_pool {n_donors} donors / {pool_nd} units "
        f"(includes {len(excluded)} non-adult donors → see excluded_nonadult_units for line-by-line details)")
    entry["caveats"].append(
        "v1.1 (KB2c t_be336eee): Primary archive=adult-only (>=18y, adjudication Q2) —— This slice empirically excludes "
        + (f"{len(excluded)} non-adult donor units (adolescent segment, row-by-row see excluded_nonadult_units); "
           if excluded else
           "0 entries (all donors in this slice >=18y → numerical equality across both tiers is valid, only identity signatures separated); ")
        + "v1.0 mixed scope retained in donor_level_adult_pool_contrast "
        "(tier=...__adult_pool__v1.0), two-tier signature separation.")
    entry["_tmp_main_nd"] = main_nd
    kb2c_adult_entry(entry, tally, excluded, pool_stats, pool_nd, pooled,
                     n_donors, all_adult)
    return entry


def build_trabecular_meshwork():
    return _build_tmcb(
        "eye trabecular meshwork", "trabecular_meshwork",
        extra_caveats=[
            "This entry = trabecular meshwork anatomical component section: high Ciliary_Muscle proportion due to integrated sampling of adjacent scleral spur/trabecular muscle, "
            "Belongs to capture composition, not TM cell layer ground truth; author-level TM-specific subtypes (BeamA/BeamB/JCT, author_cell_type) see fine_types.",
            "Fibroblast main table class in this slice = TM fibroblasts/beam cells (TMFibro) — do not directly compare with corneal/scleral fibroblasts.",
            "Small amount of CB_PCE/CB_NPCE (total ~0.5%) = contamination from ciliary body dissection boundary.",
            "25 donors but uneven donor scale within unit; n=25 donor-level interval still moderate support; direction must be re-reviewed after disease control usage.",
            "snRNA caliber, cannot be directly compared with scRNA entries (Astra T2); uvea component (53,406 nuclei) discussed separately with sclera/uvea entries.",
        ],
        extra_flags_unexpected=(
            [["Schwann Cell ~12% (innervated tissue)", "Pericyte ~0.4%"],
             ["Melanocyte ~6% (incidental uveal pigmented tissue, related to dissection plane)"],
             ["CB_PCE/CB_NPCE ~0.5% (dissection overflow into ciliary body)"]]),
    )


def build_ciliary_body():
    return _build_tmcb(
        "ciliary body", "ciliary_body",
        extra_caveats=[
            "This entry = ciliary body anatomical component section: PCE/NPCE/ciliary muscle are the three main tissue classes; "
            "Melanocyte/Schwann Cell ratio reflects the captured composition of uveal pigmentation and neural innervation layers — note for disease controls (Astra T2).",
            "Fibroblast in this slice = CB fibroblasts (CBFibro), distinct sub-layers from TM/corneal fibroblasts (distinguishable by author_cell_type).",
            "Donor 59, strong support; but significant scale disparity between study layers (chen_tm_cb dominant vs sanes uvea weight outside this slice), "
            "Stratified details must be reviewed.",
            "snRNA caliber (nuclear suspension, intronic reads included); not directly comparable with scRNA entries.",
        ],
        extra_flags_unexpected=(
            [["Pericyte <1% (Endothelium also only ~2%: predominantly large vessels; low capture efficiency for capillary nuclei)"],
             ["Immune Cell ~5% (predominantly macrophages) represents normal innate immunity levels; serves as inflammatory control baseline"],
             ["No additional contamination flags required (slice boundary defines this tissue)"]]),
    )



# ------------------------------------------------------------------- RPE (GSE158629)
# KB1v2b: RPE processed files are Seurat v3 RData (4 donor objects, independent clustering per object, no official celltype column).
# Cluster-to-identity annotation inferred from project markers (Evidence C), anchored to GEO record author cluster descriptions (Evidence B: rod/cone transcript clusters,
# TF+SPP1 VEGF cluster, RPE65+/VIM/GNL3/MKI67 stem cell candidate subpopulation). Conversion and export scripts:
#   scripts/baselines/data/export_rpe_meta.R -> cells_meta.csv + cluster_markers.csv (Evidence A input)
RPE_DIR = Path(__file__).resolve().parent / "data"
RPE_CELLS = (RPE_DIR / "rpe_GSE158629_cells_meta.csv").as_posix()
RPE_MARKERS = (RPE_DIR / "rpe_GSE158629_cluster_markers.csv").as_posix()
RPE_RDATA = "/mnt/D/OcularKB/data/GSE158629/GSE158629_scrRNA_RPE_donors1-4.RData.gz"

# donor × cluster -> (canonical_class, state_label, annotation basis)
RPE_CLUSTER_LABELS = {
    ("donor1", "0"): ("RPE", "pigment-high (TYRP1+/BEST1+/RPE65+)",
                      "marker: RPE65#3 TYRP1#11 BEST1#12 TIMP3#1 (A)"),
    ("donor1", "1"): ("RPE", "canonical (RBP1/RLBP1)", "marker (A)"),
    ("donor1", "2"): ("PR-associated", "rod-program (SAG/PDE6A/RHO)",
                      "Author-described rod RNA cluster RHO/PDE6A (B) + markers (A)"),
    ("donor1", "3"): ("RPE", "TF+SPP1/VEGF state (VIM+/TF+/SPP1+/MT1X+)",
                      "Author-described VEGF signaling cluster TF/SPP1 (B) + markers (A)"),
    ("donor1", "4"): ("PR-associated", "rod-pure (RHO/RBP3/IMPG1/CNGA1)", "marker (A)"),
    ("donor1", "5"): ("PR-associated", "rod/cone-mixed (SAG/GNAT1/PDE6G)",
                      "Markers (A); author's cone cluster ARR3/PDE6H not in this cluster's top 25, assignment uncertain (C)"),
    ("donor1", "6"): ("neuron-like", "VSX1+/SNAP25+ (bipolar/cone-like)", "marker (A)"),
    ("donor1", "7"): ("neuron-like", "ISL1+/SNAP25+ (amacrine-like)", "marker (A)"),
    ("donor2", "0"): ("RPE", "canonical", "marker: RPE65#7 TTR (A)"),
    ("donor2", "1"): ("RPE", "mito-high", "Markers: MT-* dominant + RPE65/BEST1 (A)"),
    ("donor2", "2"): ("PR-associated", "rod/cone-transcripts", "marker (A)"),
    ("donor2", "3"): ("RPE", "canonical (NDUFS7+)", "marker (A)"),
    ("donor2", "4"): ("RPE", "pigment (TYRP1+/BEST1+)", "marker (A)"),
    ("donor2", "5"): ("erythroid", "HBG1/HBG2+ribosomal", "marker (A)"),
    ("donor2", "6"): ("RPE", "complement-high (C4A/C4B+/PMEL+/TRPM3+)",
                      "RPE lineage (TRPM3/PMEL) + complement status (A)"),
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
                      "Overlap with donor1 TF+SPP1 cluster markers (C)"),
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
    # fine_types: donor × cluster proportion + status labels
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
        "title": "Composition baseline: Human (normal) freshly isolated RPE suspension scRNA — developmental stage=unknown tier (OA GSE158629, donor-level 4 donors, cluster identity inferred from markers, KB2c disclosure)",
        "status": "filled_donor_level",
        "generated": TODAY, "generator": GEN, "card": "t_bad1fbab",
        "anchor": {
            "registry_row": "mapping_from_t_6f5cc731 GSE158629 row (OA-D number not listed separately)",
            "local_path": RPE_RDATA,
            "geo": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158629",
            "tier": "T2 processed file backfill (author Seurat RData; no official celltype column → marker annotation by this project)",
        },
        "t2_fields": {
            "Sampling material": "Human freshly isolated RPE monolayer cells (4 adult donor eyes, stage=Fresh; "
                       "GEO: 'RPE cells were isolated from four adult human donor eyes')",
            "Disease stage": "normal (healthy donors; no disease column in processed file metadata)",
            "Treatment background": "Not recorded (no treatment column in processed file metadata) — marked 'Not recorded', no speculation",
            "scRNA_vs_snRNA": "scRNA-seq whole-cell (donor1=10x 3'; donor2-4=ICELL8 droplet-based) —— "
                              "Different scope than snRNA entries (retina/optic_nerve); direct comparison not permitted",
            "Enrichment steps": "Mechanical + enzymatic dissociation enrichment of RPE layer (tissue level); no fluorescence sorting records —— the dissociation protocol itself constitutes 'enrichment'",
            "Dissociation method": "RPE isolation from fresh enucleated eyes (GEO Methods; processing files lack dissociation reagent columns, details not recorded)",
            "Donor count": "4 (donor1=10x, donor2-4=ICELL8 —— platform and donor fully confounded, tech stratification=descriptive)",
            "Count denominator": f"{n_tot:,} cells (4 donor objects, 26 clusters, fully annotated)",
            "Evidence source": "Local measured recomputation (A: proportions; RData→CSV export script export_rpe_meta.R) + "
                       "GEO record author cluster description (B: rod/cone/TF+SPP1/stem cell candidates) + project marker inference (C)",
        },
        "usage_scope": USAGE_SCOPE,
        "evidence_grades": EVIDENCE_GRADES,
        "distribution_method": "Donor-level (4 donor units; within each donor, merge marker-similar clusters into canonical classes before calculating proportions; "
                               "Each donor object clustered independently; cross-donor cluster definitions rely on marker alignment — see caveats)",
        "main_heading": "Primary reference: donor-level conditional reference distribution (n=4 donors; canonical classes inferred by markers)",
        "donor_level_main": main_stats,
        "pooled_all_cells": pooled_pct,
        "strata": None,
        "major_classes": [],
        "fine_types": {"denominator_note": "donor × original cluster → canonical class [status label] percentage of that donor's cells;"
                                           "RData native cluster IDs retained as-is"},
        "states": states,
        "flags": {
            "expected_low_but_present": [
                "Myeloid (CD74/AIF1/HLA-DR) detected only in donor2; erythroid detected only in ICELL8 donors",
                "Stem cell candidate cluster (RPE65+/VIM/GNL3/MKI67, author description B): did not emerge in any cluster's top25 — small population unquantified, "
                "Interval unestimable (valid state, Astra T2)"],
            "unexpected": [
                "PR-associated class 3.8–28.5%: authors describe RPE subgroup (cone/rod transcript cluster, B), may also represent phagocytosed PR outer segments"
                "mRNA or disk membrane attachment contamination — dual interpretation retained, no single conclusion drawn",
                "neuron-like class (VSX1/ISL1/SNAP25) detected only in donor1 (10x) at 2.2% — retinal neural contamination or low-abundance precursors, questionable"],
            "contamination_suspect": [
                f"erythroid (HBG1/HBG2) highest within donor {main_stats['erythroid']['range_pct'][1]}% —— blood residue"],
        },
        "caveats": [
            "Identity annotations are not official author naming: processed files contain only donor×cluster IDs; canonical class labels are inferred via project markers."
            "(Evidence C), only the four categories of rod/cone/TF+SPP1/stem cell candidates have GEO author description anchors (Evidence B). External citations must include this qualification.",
            "n=4 donors, donor-level median/IQR is very coarse (each donor weighted 25%); intervals serve only as descriptive reference for 'freshly isolated RPE capture composition'.",
            "Each donor object clustered independently without global integration; merging similar clusters across donors depends on marker consistency (RPE/PR/erythroid clear, "
            "(exercise caution with neuron-like/state subdivision).",
            "Platform×donor fully confounded (10x n=1 / ICELL8 n=3): differences where donor1 uniquely has neuron-like and donors 2-4 uniquely have erythroid"
            "Cannot distinguish platform effects from donor variability.",
            "This entry = capture composition of RPE suspension after dissociation (count denominator excludes intact histology of non-RPE tissue); does not represent the RPE layer in whole eye/choroid"
            "Positional abundance in tissue; histological abundance reference must use whole-tissue strips including RPE (retina/choroid skeleton).",
        ],
        "sources": [
            {"sid": "RPE_LOCAL", "kind": "dataset",
             "label": f"Author-processed file {RPE_RDATA} (GSE158629); exported file "
                      f"{RPE_CELLS} + {RPE_MARKERS} (scripts/baselines/data/export_rpe_meta.R)",
             "path": RPE_RDATA, "computation": f"{__file__} build_RPE()"},
            {"sid": "RPE_GEO", "kind": "dataset",
             "label": "GEO GSE158629 — Single-Cell RNA Sequencing Reveals the Heterogeneity of the "
                      "Human RPE (abstract includes rod/cone/TF+SPP1/stem cell candidate cluster descriptions)",
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
            "note": ("Identity = marker-inferred (C), partially anchored by author's cluster descriptions (B)" if c != "RPE"
                     else "Canonical RPE: RPE65/BEST1/TTR/SERPINF1 core"),
        })
    entry["t2_fields"]["Donor count"] = (
        entry["t2_fields"]["Donor count"] + " —— KB2c: cells_meta lacks age column, this entry organism_stage=unknown "
        "(GEO text records 'four adult human donor eyes' as B-level literature description, cannot be verified line-by-line, silent attribution to adult prohibited)")
    entry["caveats"].append(
        "KB2c t_be336eee red line 2: this entry lacks per-donor development/age metadata → development stage=unknown + disclosure row, "
        "Must not be cited as 'adult RPE baseline'; upgrade to adult-only requires supplementing per-donor age (GEO supplementary tables/author correspondence) followed by separate adjudication.")
    kb2c_unknown_entry(
        entry,
        "Local GSE158629 cells_meta (exported by export_rpe_meta.R) contains only donor/cluster/tech columns, no "
        "development_stage/age column; GEO Summary states 'four adult human donor eyes' (evidence grade B).",
        [{"source": "GSE158629 cells_meta (all 4 donors)", "cells": n_tot, "donors": 4,
          "organism_stage": "unknown", "rule": "No age column → silent assignment to adult prohibited (Red Line 2)",
          "literature_grade_B": "GEO: 'RPE cells were isolated from four adult human donor eyes'"}])
    return entry



# ---------------------------------------------------------------- 9 Tissue skeleton
SKELETON_TISSUES = ["RPE", "choroid", "ciliary_body", "iris", "lens",
                    "optic_nerve", "trabecular_meshwork", "conjunctiva", "sclera"]
FILLED_EXTRAS = {}  # tissue -> builder; registered in main(); already-backfilled tissues are dropped from the skeleton list

LOCAL_POINTERS = {  # files already on the local disk (field-surveyed 2026-09-23, verified via find)
    "optic_nerve": "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad",
    "RPE": "/mnt/D/OcularKB/data/GSE158629/ (processed RData files, conversion required; t_6f5cc731 annotated 'ready-to-use')",
}


def build_skeletons(inv):
    out = []
    for t in SKELETON_TISSUES:
        if t in FILLED_EXTRAS:   # KB1v2b: tissue with backfilled donor-level data no longer generates skeleton
            continue
        rows = inv.get(t, [])
        verdict = (inv.get("verdicts") or {}).get(t, "See TISSUE_REFERENCE_INVENTORY.md")
        entry = {
            "schema": "eyekb-baseline/1.0",
            "entry_id": f"baseline_human_{t}",
            "tissue": t, "species": "human",
            "title": f"Composition baseline skeleton: Human {t} (fields complete, proportions=pending backfill)",
            "status": "skeleton_mapping_backfilled",
            "organism_stage": "unknown",
            "stage_note": ("KB2c developmental axis: skeleton entry=unknown (not actually calculated). Backfilling must list by developmental axis separately — "
                           "adult material outputs adult-only main archive (>=18y adjudication Q2); fetal/developmental stage materials establish separate entries, "
                           "Prohibited from mixing fetal and adult samples in the same tissue archive (PI red line)."),
            "stage_axis": stage_axis_block(f"baseline_human_{t}"),
            "generated": TODAY, "generator": GEN, "card": "t_16c3e020",
            "anchor": {"tier": "Skeleton (t_6f5cc731 inventory mapping backfilled; donor-level ratios not calculated)"},
            "mapping_from_t_6f5cc731": [
                {k: r.get(k) for k in ("acc", "sp", "scale", "annot", "avail", "note")}
                for r in rows],
            "verdict": verdict,
            "local_file_pointer": LOCAL_POINTERS.get(t),
            "t2_fields": {
                "Sampling material": "Pending (skeleton: Must fix actual sampling material standards before building baseline, Astra T2)",
                "Disease stage": "Pending", "Treatment background": "Pending",
                "scRNA_vs_snRNA": "Pending", "Enrichment steps": "Pending", "Dissociation method": "Pending",
                "Donor count": "Pending", "Count denominator": "Pending",
                "Evidence source": "See mapping_from_t_6f5cc731 candidate datasets",
            },
            "usage_scope": USAGE_SCOPE,
            "evidence_grades": EVIDENCE_GRADES,
            "distribution_method": None,
            "donor_level_main": None,
            "composition_status": "Interval unestimable (valid state, Astra T2) — pending donor-level computation based on mapped candidate datasets;"
                                  "Data not stored locally must first pass the mandatory download approval rule",
            "major_classes": [],
            "backfill_path": ("① Verify local status of candidate data → ② Official annotation slice (celltype-annotation-sourcing discipline) → "
                              "③ This script appends build_<tissue>() for donor-level recalculation → ④ Change baseline status to filled_donor_level → "
                              "⑤KB2c developmental axis: only adult (>=18y) donors enter main archive, non-adult disclosed line by line; "
                              "Fetal/developmental stage materials listed as separate entries, prohibited from merging into adult."),
            "caveats": ["Skeleton entries must not be used for external statements claiming 'composition baseline exists for this tissue' (Astra T6: Engineering consistency ≠ evidence of correctness)"],
        }
        out.append(entry)
    return out


# ---------------------------------------------------------------- Rendering
def fmt_dist(stats, classes):
    lines = ["| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |",
             "|---|---|---|---|---|"]
    for c in classes:
        s = stats[c]
        lines.append(f"| {c} | {s['median_pct']} | {s['iqr_pct'][0]}–{s['iqr_pct'][1]} "
                     f"| {s['range_pct'][0]}–{s['range_pct'][1]} | {s['n_units']} |")
    return "\n".join(lines)


def render_md(e):
    L = [f"# {e['title']}", ""]
    L.append(f"> schema: `{e['schema']}` | entry_id: `{e['entry_id']}` | Status: {e['status']} "
             f"| Developmental axis: **organism_stage={e.get('organism_stage', '—')}** "
             f"| Generated: {e['generated']} | Card: {e['card']}")
    if e.get("development_stage"):
        L.append(f"> **KB3 Developmental Profile (Card {KB3_CARD})**: development_stage=**{e['development_stage']}**"
                 + (f" | Applicable tier (hardcoded at backfill): {e['kb3_applicable_stage_at_backfill'].split(' ——')[0]}"
                    if e.get("kb3_applicable_stage_at_backfill") else "")
                 + f" —— {KB3_PROHIBITION}")
    L.append(f"> This file is auto-rendered from the same-name .json by `/mnt/D/EyeKB/scripts/baselines/{Path(__file__).name}` "
             f"-- Modify content via JSON + scripts; manual MD edits will be overwritten.")
    if e.get("stage_note"):
        L.append(f"> ⚠ Developmental axis disclosure: {e['stage_note']}")
    L.append("")
    L.append(f"**{e['usage_scope']}**")
    L.append("")
    L.append("## Evidence grade definitions")
    for k, v in e["evidence_grades"].items():
        L.append(f"- **{k}**: {v}")
    L.append("")
    if e.get("stage_axis"):
        sa = e["stage_axis"]
        L.append("## Developmental axis definitions (KB2c adjudication 2026-09-23 — threshold changes require adjudication)")
        L.append(f"- Top-level axis: `{sa['field']}` ∈ {sa['levels']}")
        L.append(f"- **adult**: {sa['adult_rule']}")
        L.append(f"- **developing**: {sa['developing_rule']}")
        L.append(f"- **fetal**: {sa['fetal_rule']}")
        L.append(f"- **unknown**: {sa['unknown_rule']}")
        L.append(f"- aging orthogonal axis: {sa['aging_note']}")
        L.append(f"- two-tier identity: {sa['tier_ids']}")
        L.append("")
    L.append("## Astra T2 metadata fields")
    for k, v in e["t2_fields"].items():
        L.append(f"- **{k}**: {v}")
    L.append("")
    if e["status"] == "filled_donor_level":
        classes = [r["class"] for r in e["major_classes"]]
        L.append("## " + (e.get("main_heading")
                           or "Primary reference: donor-level conditional reference distribution (excluding sorting design layer)"))
        if e.get("primary_reference_stratum"):
            L.append(f"> Stratification criterion: {e['primary_reference_stratum']}; Method: {e['distribution_method']}")
        L.append(f"> ⚠ {KB3_PROHIBITION}")
        L.append("")
        L.append(fmt_dist(e["donor_level_main"], classes))
        L.append("")
        if e.get("donor_level_adult_pool_contrast"):
            L.append(f"### Comparison record adult_pool (v1.0 mixed criteria, includes non-adult donors; "
                     f"tier=`{e['stage_axis']['tier_ids']['adult_pool']}`) —— Citing v1.0 legacy figures only under this tier identity")
            L.append("")
            L.append(fmt_dist(e["donor_level_adult_pool_contrast"], classes))
            L.append("")
        if e.get("stage_disclosure"):
            L.append("### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)")
            if isinstance(e["stage_disclosure"], list):
                L.append("| Source | organism_stage | Rule | Cell count | Donor count | Literature-level description (B) |")
                L.append("|---|---|---|---|---|---|")
                for x in e["stage_disclosure"]:
                    L.append(f"| {x.get('source','')} | {x.get('organism_stage','')} "
                             f"| {x.get('rule','')} | {x.get('cells', 0):,} | {x.get('donors','')} "
                             f"| {x.get('literature_grade_B','')} |")
            else:
                L.append("| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |")
                L.append("|---|---|---|---|---|")
                for ub, v in e["stage_disclosure"].items():
                    L.append(f"| {ub} | {v['organism_stage']} | {v['rule']} "
                             f"| {v['cells']:,} | {v['n_donors']} |")
                if e.get("excluded_nonadult_units"):
                    L.append("")
                    L.append(f"{len(e['excluded_nonadult_units'])} donors excluded from adult master archive: "
                             + "; ".join(f"`{x['donor_id']}`({x['organism_stage']}, {x['uberon']}, "
                                         f"{x['cells']:,} nuclei)" for x in e["excluded_nonadult_units"]))
            L.append("")
        L.append("## Tool compatibility main table (major_classes)")
        L.append("| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |")
        L.append("|---|---|---|---|---|---|---|")
        for r in e["major_classes"]:
            mk = ", ".join(r.get("markers_local_lib") or [])
            L.append(f"| {r['class']} | {r['donor_median_pct']} | {r['donor_iqr_pct'][0]}–{r['donor_iqr_pct'][1]} "
                     f"| {r['donor_range_pct'][0]}–{r['donor_range_pct'][1]} "
                     f"| {r['pooled_pct_for_reference_only']} | {mk} | {r['evidence']} |")
        L.append("")
        if e.get("strata"):
            L.append("## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)")
            for s in e["strata"]:
                key = (s.get("study") or "") + (f"|{s['enrichment']}" if "enrichment" in s
                                                else f"|{s.get('tissue_group','')}")
                flag = " ⚠ Sorting design layer" if s.get("sorted_design_flag") else ""
                if s.get("adult_fallback_guard"):
                    flag += " ⚠FALLBACK_BLOCKED"
                L.append(f"### Layer: {key}{flag}  (n_donors={s['n_donors']}, n_cells={s['n_cells']:,}"
                         + (f", accounting for {s['share_of_atlas_pct']}% of the atlas" if "share_of_atlas_pct" in s else "") + ")")
                L.append("")
                if s.get("adult_fallback_guard"):
                    L.append(f"> {s['adult_fallback_guard']}")
                    L.append("")
                    L.append("*Table below = pool-level metrics for this layer (controls only):*")
                    L.append("")
                    L.append(fmt_dist(s["donor_level"], classes))
                else:
                    L.append(fmt_dist(s["donor_level_adult_only"], classes))
                L.append("")
        if e.get("fine_types"):
            L.append("## Subtype layer (% of annotated cells within class, pooled within class basis)")
            for c, v in e["fine_types"].items():
                if c == "denominator_note":
                    continue
                if isinstance(v, dict) and "top" in v:
                    L.append(f"- **{c}** ({v['basis']}): " + "; ".join(f"{k} {p}%" for k, p in v["top"]))
                elif isinstance(v, list):
                    L.append(f"- **{c}**: " + "; ".join(f"{k} {p}%" for k, p in v))
            L.append("")
        if e.get("states"):
            L.append("## State layer")
            for s in e["states"]:
                L.append(f"- **{s['cell_type']}** [{s['state']}]: {', '.join(s['markers'])} "
                         f"(Evidence {s['evidence']})")
            L.append("")
    else:
        L.append("## Composition data status")
        L.append(f"**{e['composition_status']}**")
        L.append("")
        L.append("## Candidate dataset mapping (t_6f5cc731 inventory backfill)")
        for r in e["mapping_from_t_6f5cc731"]:
            L.append(f"- `{r.get('acc')}` [{r.get('sp')}] {r.get('scale')} | Annotation: {r.get('annot')} "
                     f"| Availability: {r.get('avail')} | {r.get('note') or ''}")
        L.append("")
        L.append(f"**Adjudication (t_6f5cc731)**: {e['verdict']}")
        L.append("")
        if e.get("local_file_pointer"):
            L.append(f"**Local file**: `{e['local_file_pointer']}`")
            L.append("")
        L.append(f"**Backfill path**: {e['backfill_path']}")
        L.append("")
    if e.get("flags"):
        L.append("## Flag semantics")
        for g in ("expected_low_but_present", "unexpected", "contamination_suspect"):
            if e["flags"].get(g):
                L.append(f"**{g}**: " + "; ".join(e["flags"][g]))
                L.append("")
    if e.get("caveats"):
        L.append("## Notes")
        for i, c in enumerate(e["caveats"], 1):
            L.append(f"{i}. {c}")
        L.append("")
    if e.get("sources"):
        L.append("## Source List")
        L.append("| sid | Type | Label |")
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
    # ---- KB2c finalize: schema 1.1 + dual-tier identity signatures (Red line: signatures must not be mixed) ----
    for e in entries:
        e["schema"] = "eyekb-baseline/1.1"
        e["axis_version"] = "kb2c-1.1"
        kb3_augment(e)  # KB3 (t_5425a7ca): development_stage mandatory + prohibition archived
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
             "note": ("General ophthalmology architecture (PI 2026-09-23 standard): Composition baselines anchored to tissue registry annotated standard sets; "
                      "Old kb/priors/composition/ is archived as v1 standard; MCP get_tissue_composition prioritizes reading this directory."
                      "KB2c (t_be336eee) developmental axis listed separately: top-level axis organism_stage 4 levels "
                      "{fetal, adult, developing, unknown}; adult master record=donor_age>=18y donor unit "
                      "(adjudication Q2, threshold changes require adjudication); v1.0 mixed criteria downgraded to adult_pool contrast tier, "
                      "Two-tier separation of entry_id/identity signature; unknown must disclose rows and silent assignment to adult is prohibited; "
                      "See fetal_development_transitions for fetal/developing composition entries."),
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
            "n_donors": (e["t2_fields"].get("Donor count") if e["status"] == "filled_donor_level"
                         else None),
            "tiers": (e.get("stage_axis") or {}).get("tier_ids"),
            "identity_signature": e.get("identity_signature")})
    # ---- KB3 (t_5425a7ca): Developmental stage independent entry registration (not included in entries=11 adult archive array; see regression lock) ----
    index["kb3_note"] = ("KB3 full single-column development axis: each baseline adds mandatory field development_stage "
                         "(enumeration adult/fetal_developing/postnatal_neonatal/mixed_not_separable/"
                         "unknown); Developmental stage entries in separate file (schema eyekb-baseline-development/1.0, "
                         "MCP adult query invisible), registered in development_entries; prohibition on reference distribution segments archived.")
    _dev_files = sorted(OUT_DIR.glob("*__*.json"))
    _dev_recs = []
    for p in _dev_files:  # KB3 fix (run 1768): original walrus operator if clause referenced unbound d → UnboundLocalError
        d = json.loads(p.read_text(encoding="utf-8"))
        if not (d.get("schema") or "").startswith("eyekb-baseline-development/"):
            continue
        _dev_recs.append({"entry_id": d["entry_id"], "file": p.name,
                          "tissue": d.get("tissue"),
                          "development_stage": d.get("development_stage"),
                          "anchors": [c["acc"] for c in d.get("anchors", [])],
                          "status": d.get("status")})
    index["development_entries"] = _dev_recs
    # ---- KB2c: Summary line-by-line disclosure table (_STAGE_DISCLOSURE) ----
    disc = {t: {"organism_stage_main": e.get("organism_stage"),
                "stage_disclosure": e.get("stage_disclosure"),
                "excluded_nonadult_units": e.get("excluded_nonadult_units"),
                "source": (e.get("anchor") or {}).get("local_path")}
            for e in entries if (t := e["tissue"]) and e.get("stage_disclosure")}
    (OUT_DIR / "_STAGE_DISCLOSURE.json").write_text(
        json.dumps({"schema": "eyekb-stage-disclosure/1.0", "generated": TODAY,
                    "card": "t_be336eee",
                    "note": "KB2c red line 2: in adult baseline, all non-adult donors/unknown sources disclosed row by row; "
                            "fetal period measured value=0 (contamination source is actually newborn/child/adolescent).",
                    "by_tissue": disc}, ensure_ascii=False, indent=1), encoding="utf-8")
    dl = ["# Developmental Axis Row-by-Row Disclosure Table (KB2c t_be336eee — Red Line 2: Silent omission prohibited)", "",
          f"> schema: eyekb-stage-disclosure/1.0 | Generated: {TODAY} | Generator: {GEN}",
          "> Adult main archive = donor_age>=18y (Adjudication Q2); The table below lists all non-adult donor units for each filled entry.",
          "> Measured: Fetal nucleus count in 4 h5ad sources = 0 —— The red-line lexical surface 'contains fetal donors' actually refers to mixed newborn/child/adolescent samples, which have been entirely excluded from the main archive.", ""]
    for t, d in disc.items():
        dl.append(f"## {t} (main record organism_stage={d['organism_stage_main']})")
        if d.get("excluded_nonadult_units"):
            dl.append("| Excluded Donor | organism_stage | UBERON Original Value | Nucleus Count | Rule |")
            dl.append("|---|---|---|---|---|")
            for x in d["excluded_nonadult_units"]:
                dl.append(f"| `{x['donor_id']}` | {x['organism_stage']} | {x['uberon']} "
                          f"| {x['cells']:,} | {x['rule']} |")
        elif isinstance(d.get("stage_disclosure"), list):
            for x in d["stage_disclosure"]:
                dl.append(f"- unknown disclosure: {x.get('source')} — {x.get('rule')}; "
                          f"Literature grade: {x.get('literature_grade_B','')}")
        dl.append("")
    (OUT_DIR / "_STAGE_DISCLOSURE.md").write_text("\n".join(dl) + "\n", encoding="utf-8")
    # ---- KB2c Q5: Fetal/developing transitional state concept entries (no actual computation) ----
    fetal = {
        "schema": "eyekb-baseline-concept/1.0",
        "entry_id": "fetal_development_transitions",
        "title": "Fetal/developmental eye tissue transitional state conceptual entry (KB2c adjudication Q5 — not a clone of the adult bucket, no composition calculation)",
        "generated": TODAY, "generator": GEN, "card": "t_be336eee",
        "organism_stage": ["fetal", "developing"],
        "nature": ("This entry = conceptual placeholder: registers future fetal/developing baseline candidates and their prerequisites, "
                   "**Not a composition baseline** — fetal samples are incompatible with adult ones even within the same tissue (PI red line), "
                   "Prohibited from citing this entry as an adult bucket for any tissue or reverse borrowing."),
        "current_facts": {
            "filled_adult_baselines": 6,
            "fetal_stage_nuclei_in_filled_sources": 0,
            "nonadult_in_filled_sources": ("newborn/child/adolescent donors (see _STAGE_DISCLOSURE.md line by line),"
                                           "Already removed from adult master archive; local material for future developing baseline"),
            "engine_applicability": "Active reading engine (OcularKB M3 etc.) training/applicability domain = adult tissue — active engine"
                                    "Not applicable to fetal/developmental samples; must abstain for such materials (evaluation layer E4=OOD_strict, "
                                    "Directive Clause 3); Composition entries can only be established after building a separate fetal reference pipeline",
        },
        "candidates": [
            {"acc": "GSE268630", "desc": "Human fetal retina multiome ~220k nuclei", "tier": "fetal",
             "local": True, "note": "Instruction clause 4 preferred candidate; requires fetal reference pipeline task before baseline inclusion"},
            {"acc": "GSE137828", "desc": "Human fetal retina (fetal)", "tier": "fetal",
             "local": "To be verified", "note": "Instruction clause 4 named column"},
            {"acc": "GSE137863", "desc": "Human fetal retinal development (fetal)", "tier": "fetal",
             "local": "To be verified", "note": "Instruction clause 4 named column"},
            {"acc": "GSE138002", "desc": "Retinal organoids", "tier": "organoid→unknown+flag (adjudication Q1)",
             "local": "To be verified", "note": "Organoids ≠ fetal tissue, also ≠ adult; listed separately"},
            {"acc": "GSE234963", "desc": "Organoid set", "tier": "organoid→unknown+flag",
             "local": "To be verified", "note": "Instruction clause 4 named column"},
            {"acc": "GSE235577", "desc": "Organoid/multi-omics", "tier": "organoid→unknown+flag",
             "local": "To be verified", "note": "The 08-28 inventory was actually snATAC/multi-omics ATAC components — platform scope must be re-verified before conversion"},
        ],
        "out_of_scope": ("Fetal/developmental composition actual calculation = separate batch task (adjudication Q5); >=60 elderly stratification = orthogonal aging axis, not within the developmental axis."),
        "usage_redline": ("All candidates in this entry must not be merged into any adult entry; citations of this entry must include"
                          "'Requires fetal reference pipeline; current engine not applicable' declaration."),
    }
    (OUT_DIR / "fetal_development_transitions.json").write_text(
        json.dumps(fetal, ensure_ascii=False, indent=1), encoding="utf-8")
    fl = [f"# {fetal['title']}", "",
          f"> schema: `{fetal['schema']}` | entry_id: `{fetal['entry_id']}` | Generated: {TODAY} | Card: {fetal['card']}",
          f"> This file is generated by build_baselines.py (KB2c); manual edits will be overwritten.", "",
          fetal["nature"], "", "## Current Facts", ""]
    for k, v in fetal["current_facts"].items():
        fl.append(f"- **{k}**: {v}")
    fl += ["", "## Candidate Datasets (Instruction Clause 4 — All not yet included in baselines)", "",
           "| accession | description | developmental stage | local | notes |", "|---|---|---|---|---|"]
    for c in fetal["candidates"]:
        fl.append(f"| `{c['acc']}` | {c['desc']} | {c['tier']} | {c['local']} | {c['note']} |")
    fl += ["", f"**Out of scope**: {fetal['out_of_scope']}", "",
           f"**Usage redline**: {fetal['usage_redline']}", ""]
    (OUT_DIR / "fetal_development_transitions.md").write_text("\n".join(fl) + "\n", encoding="utf-8")
    (OUT_DIR / "baselines.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written:", len(entries), "entries + _STAGE_DISCLOSURE + fetal transitions →", OUT_DIR)
    # Quick self-check: retina adult-only primary archive vs control archive
    r = entries[0]
    print("retina main(adult-only) n_units:", r["donor_level_main"]["Rod"]["n_units"],
          "| pool n_units:", r["donor_level_adult_pool_contrast"]["Rod"]["n_units"],
          "| excluded nonadult donors:", len(r["excluded_nonadult_units"]))
    for c in ["Rod", "MG", "Microglia", "RPE"]:
        s = r["donor_level_main"][c]
        print(f"  {c}: adult-only median {s['median_pct']}% IQR {s['iqr_pct']} "
              f"(pool contrast {r['donor_level_adult_pool_contrast'][c]['median_pct']}%)")
    o = entries[1]
    print("ocular_surface main n_units:", o["donor_level_main"]["Epithelium"]["n_units"])
    for c in ["Epithelium", "Fibroblasts", "Immune Cells", "Corneal Endothelium"]:
        s = o["donor_level_main"][c]
        print(f"  {c}: donor-median {s['median_pct']}% IQR {s['iqr_pct']} (pooled {o['pooled_all_cells'][c]}%)")


if __name__ == "__main__":
    sys.exit(main())
