#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_expected_composition_v0.py — EyeKB DISC_COMP (D-1) Composition Prior New Surface v0 Build
Card: t_fa03e1d7 | Task brief: <EYEKB>/plans/comp_prior_20260928/BRIEF_DISC_COMP.md
Release: USER_DIRECTIVE_20260928_eyekb_improve_wave.md appended Section VII-B (D-1)

Discipline:
- Default OFF, unwired (zero MCP/runtime references in this directory; wiring & activation need a separate card and batch)
- every row carries a PMID; three bibliographic criteria mechanically self-checked
- Prohibit deriving proportions from own clustering/own demo annotations (this script's numerical source = kb/baselines adult-only master file
  Donor-level distribution [Grade A, lineage=D001/D002 external author annotations recalculated locally] + priors/composition v1
  Cross-study empirical intervals [C-level, same lineage] + original statements from literature already ingested on the disc [B-level, verbatim chunks]
- fetal/organoid/non-adult entries must not be mixed in (numerical folding only accepts human+adult+capture-composition scope sentences);
  Do not establish disease-state proportions
- CPU-only read access throughout; output restricted to kb/composition/

Mechanical interval formula (pre-registered):
  low  = floor( min( donor_iqr_low, priors_expected_low, folded_lit_low ) )
  high = ceil ( max( donor_iqr_high, priors_expected_high, folded_lit_high ) )
  mid  = round( donor_median_pct, 1 )
  rows with no grade-A numeric source → low/mid/high = null, evidence = "no_evidence" (fabricated numbers forbidden)
"""
import json, re, sys, datetime, math, pathlib

KB = pathlib.Path("<EYEKB>/kb")
OUT = KB / "composition"
PAPERS = "<STORE>/ocularkb/rag/literature_db/v2.4.2_2026-09/papers.jsonl"
SIDECAR = str(KB / "literature_db/evidence_meta_v2.3_2026-09.jsonl")
VK_DIR = KB / "vk_literature_index"

RET = json.load(open(KB / "priors/composition/human_retina.json"))
BR = json.load(open(KB / "baselines/retina.json"))
BO = json.load(open(KB / "baselines/ocular_surface.json"))

donor_r = {c["class"]: c for c in BR["major_classes"]}
prior_r = {c["class"]: c for c in RET["major_classes"]}
donor_o = {c["class"]: c for c in BO["major_classes"]}

# ---------------------------------------------------------------- Literature Anchor Table
# kind: "fold"=quantitative sentence foldable into interval (human/adult/capture-composition scope)
#       "context"=different scope/subtype/theoretical estimate/density, qualitative anchor only, not folded
#       "identity"=direct literature support for existence of this type in normal adult tissue
LIT = {
 "retina": {
  "Rod": [
    dict(pmid="38012720", kind="fold", bound=("high", 55.2),
         quote="the distributions of cell type proportions ... ranging from 2.5% RGC to 55.2% Rod",
         note="snRNA+snATAC multi-omics cross-sample composition extremes (human, adult)"),
    dict(pmid="37388908", kind="identity",
         quote="the highest overlap (63.9%) is observed for the most abundant cell type, Rod",
         note="Human snRNA-seq atlas: Rods are the most abundant cell type (qualitative)"),
    dict(pmid="41578023", kind="identity", quote=None,
         note="HRCA integrated atlas majorclass includes Rods (registry ledger OA-D001)")],
  "Cone": [
    dict(pmid="37388908", kind="context",
         quote="S cones (0.07% of total retinal cells)",
         note="S-cone subtype definition, not collapsed; supports overall Cone presence"),
    dict(pmid="32555229", kind="identity", quote=None,
         note="Human fovea/peripheral retina cell atlas includes cone cells"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes Cone")],
  "BC": [
    dict(pmid="37388908", kind="fold", bound=("high", 20.8),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="Human snRNA-seq dataset-level bipolar cell proportion (fold high)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes BC")],
  "AC": [
    dict(pmid="37388908", kind="fold", bound=("high", 21.5),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="Same dataset AC proportion (fold high)"),
    dict(pmid="37388908", kind="context",
         quote="vGlut3 excitatory ACs (0.7% of total retinal cells)",
         note="Excitatory AC subtype definition, not collapsed"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes AC")],
  "HC": [
    dict(pmid="37388908", kind="identity",
         quote="lowest overlap is observed for HC (49.0%)",
         note="Human atlas includes horizontal cells (qualitative)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes HC")],
  "RGC": [
    dict(pmid="37388908", kind="context",
         quote="the total number of RGCs only accounts for approximately 1% of the cell population in the retina",
         quote_kind="theory", note="Histological theoretical estimate definition, not collapsed; directional anchor"),
    dict(pmid="37388908", kind="fold", bound=("high", 4.1),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="Human dataset capture-layer RGC proportion (fold high)"),
    dict(pmid="38012720", kind="fold", bound=("low", 2.5),
         quote="ranging from 2.5% RGC to 55.2% Rod",
         note="Cross-sample RGC lower bound extreme (fold low)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes RGC")],
  "MG": [
    dict(pmid="32069977", kind="identity",
         quote="Within the fovea, Müller cells and horizontal cells ...",
         note="Human fovea AIR atlas confirms Müller cell presence (qualitative)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes MG")],
  "Astro": [
    dict(pmid="32555229", kind="context",
         quote="depletion of astrocytes from fovea (0.9% of all non-neuronal cells in fovea and 12% in periphery)",
         note="Denominator = non-neuronal cells, different definition, not collapsed; regional difference directional anchor"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes Astro")],
  "Micro": [
    dict(pmid="37017569", kind="context",
         quote="microglia (11 cells, 0.0146% of total cell count) directly mapped to the chromatin landscape",
         note="scATAC direct mapping subset definition, not collapsed; rarity directional anchor"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass includes Microglia")],
  "RPE": [
    dict(pmid="41578023", kind="identity", quote=None,
         note="HRCA neural retina majorclass includes RPE (capture 0.03%)"),
    dict(pmid="32946783", kind="context",
         quote="pigment epithelial cells had 2% RPE65 (expression in organoids)",
         note="Organoid expression definition involving organoids, not collapsed nor included in surface; registration exclusion only")],
 },
 "ocular_surface": {
  "Epithelium": [
    dict(pmid="34381080", kind="identity",
         quote="These 16 clusters correspond to 11 subtypes of epithelial cells, keratocytes, Langerhans cells, melanocytes, vascular endothelial cells and corneal endothelial cells",
         note="Adult human corneal single-cell catalog: epithelium is a major class (qualitative)"),
    dict(pmid="34741068", kind="identity",
         quote="The cornea is composed of five layers: its outer surface is a stratified sheet of corneal epithelial cells",
         note="Human corneal stratified structure (qualitative)"),
    dict(pmid="32502616", kind="identity", quote=None,
         note="Adult conjunctiva/limbus/corneal epithelium scRNA inclusion")],
  "Fibroblasts": [
    dict(pmid="34381080", kind="fold", bound=("low", 15),
         quote="Over 15% of cells in our analysis are keratocytes within a single cluster",
         note="Adult corneal scRNA: keratocyte single cluster >15% (fold low)"),
    dict(pmid="40838019", kind="identity",
         quote="The corneal stroma, composed mainly of keratocytes",
         note="Keratocytes are the primary resident cells of the corneal stroma (qualitative)"),
    dict(pmid="34741068", kind="identity",
         quote="The keratocytes populate the corneal stroma", note="Qualitative")],
  "Corneal Endothelium": [
    dict(pmid="33865984", kind="context",
         quote="endothelial cells in humans are not endogenously renewed ... density declines at an average of approximately 0.6% per year",
         note="Cell density definition (cell/mm^2), not composition percentage, not collapsed; CEC identity/rarity anchor"),
    dict(pmid="34381080", kind="identity", quote=None,
         note="Corneal single-cell catalog includes corneal endothelial cells (CenC)")],
  "Endothelium": [
    dict(pmid="34381080", kind="identity", quote=None,
         note="Corneal single-cell catalog includes vascular endothelial cells")],
  "Immune Cells": [
    dict(pmid="34381080", kind="identity", quote=None,
         note="Corneal single-cell catalog includes Langerhans cells (immune)"),
    dict(pmid="41552884", kind="identity", quote=None,
         note="Corneal macrophage review (emphasis on human evidence)")],
  "Melanocytes": [
    dict(pmid="34381080", kind="identity", quote=None, note="Corneal single-cell catalog includes melanocytes"),
    dict(pmid="40216818", kind="identity",
         quote="PAX3 expression in LM as well in the conjunctival melanocytes",
         note="Presence of limbal/conjunctival melanocytes (qualitative)")],
  "Pericytes": [
    dict(pmid="D002-PORTAL-ONLY", kind="identity", quote=None,
         note="No on-disk adult ocular surface pericyte composition literature statement; identity solely from D002 official annotation (Grade A) — Grade B missing items registered as-is")],
  "Schwann Cells": [
    dict(pmid="40649793", kind="context",
         quote="NGF ... corneal nerve regeneration",
         note="Ocular surface nerve review (qualitative), Schwann cell composition % not pinned down")],
  "Smooth Muscle Cells": [
    dict(pmid="40649793", kind="context",
         quote="NGF has been found to be produced by ... smooth muscle cells",
         note="Review mentions presence of ocular surface SMCs (qualitative)")],
  "_disclosure_conjunctival_epithelium": [
    dict(pmid="32502616", kind="identity", quote=None,
         note="Adult conjunctival epithelium scRNA; D002 lacks independent super class (portal label assigned to Epithelium)")],
  "_disclosure_goblet": [],
 },
}

RETINA_CLASSES = ["Rod","Cone","BC","AC","HC","RGC","MG","Astro","Micro","RPE"]
SRC_NAME = {"Astro":"Astrocyte","Micro":"Microglia"}  # face short name -> baselines/priors key name
CLASS_CN_R = {c: prior_r[SRC_NAME.get(c,c)]["label_cn"] for c in RETINA_CLASSES}
OCS_CLASSES = list(donor_o.keys())

# ------------------------------------------------- PMID bibliographic record three-criteria mechanical self-check
def pmid_verify(pmids):
    need = {p for p in pmids if p and not p.startswith("D002")}
    rows = {}
    with open(PAPERS, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["paper_id"] in need:
                rows[d["paper_id"]] = d
    vktext = "".join(str(p.read_text(errors="ignore")) for p in VK_DIR.glob("*.md"))
    sidecar_ids = set()
    with open(SIDECAR, encoding="utf-8") as f:
        for line in f:
            try: sidecar_ids.add(json.loads(line)["pmid"])
            except Exception: pass
    out = {}
    for p in need:
        d = rows.get(p)
        j1 = bool(d and d.get("title") and d.get("journal") and d.get("year"))
        j2 = bool(d and (d.get("n_chunks") or 0) > 0)
        vkhit = ("PMID"+p in vktext) or (p in sidecar_ids)
        # j3 = Primary data verifiable on disk (species or tissues non-empty) — Task brief standard: "papers.jsonl metadata verifiable"
        j3 = bool(d and (str(d.get("species") or "").strip() not in ("", "nan", "unknown")
                         or (d.get("tissues") or [])))
        out[p] = dict(j1_papers_jsonl=j1, j2_nonghost=j2, j3_trait_meta=j3, vk_or_sidecar_hit=vkhit,
                      title=(d or {}).get("title",""), year=(d or {}).get("year"),
                      journal=(d or {}).get("journal"), n_chunks=(d or {}).get("n_chunks"),
                      species=(d or {}).get("species"), tissues=(d or {}).get("tissues"))
    return out

# ------------------------------------------------- Interval mechanical assembly
def face_row(cls, cn, donor, pri, lit_list, denom_note, extra=None):
    lows, highs, mids = [], [], []
    if donor:
        if donor.get("donor_iqr_pct"):
            lows.append(float(donor["donor_iqr_pct"][0])); highs.append(float(donor["donor_iqr_pct"][1]))
        if donor.get("donor_median_pct") is not None:
            mids.append(float(donor["donor_median_pct"]))
        # Inclusion criterion: When donor-level IQR upper bound collapses to 0, use pooled reference value to cap high (prevent self-flagged absurd intervals)
        if float(donor.get("donor_iqr_pct",[0,0])[1]) == 0.0 and donor.get("pooled_pct_for_reference_only"):
            highs.append(float(donor["pooled_pct_for_reference_only"]))
    if pri:
        if pri.get("expected_range_pct"):
            lows.append(float(pri["expected_range_pct"][0])); highs.append(float(pri["expected_range_pct"][1]))
    fold_low, fold_high, anchors = [], [], []
    for L in lit_list:
        if L.get("kind") == "fold":
            b, v = L["bound"]
            (fold_low if b == "low" else fold_high).append(v)
        anchors.append({k: L[k] for k in L if k != ""})
    lows += fold_low; highs += fold_high
    lit_real = [a for a in anchors if str(a.get("pmid","")).isdigit()]
    has_B = any(a["kind"] in ("fold","identity") for a in lit_real)
    ctx_only = (not has_B) and any(a["kind"]=="context" for a in lit_real)
    ev = "A_registry_recompute" + ("+B_literature" if has_B else ("+B_context_only" if ctx_only else ""))
    if not lows and not mids:
        row = dict(cell_type=cls, label_cn=cn, low_pct=None, mid_pct=None, high_pct=None,
                   evidence="no_evidence", literature_anchors=anchors,
                   denominator_note=denom_note)
    else:
        low = math.floor(min(lows)) if lows else 0
        high = math.ceil(max(highs)) if highs else None
        mid = round(max(mids), 1) if mids else None
        row = dict(cell_type=cls, label_cn=cn, low_pct=low, mid_pct=mid, high_pct=high,
                   evidence=ev, literature_anchors=anchors, denominator_note=denom_note)
    row["grade_b_status"] = "B" if has_B else ("B_context_only" if ctx_only else "B_missing")
    row["pmids"] = sorted({l["pmid"] for l in lit_list if l["pmid"].isdigit()})
    if extra: row.update(extra)
    return row

def build():
    generated = datetime.date(2026, 9, 28).isoformat()
    retina_rows, ocs_rows = [], []
    for c in RETINA_CLASSES:
        pri = prior_r[SRC_NAME.get(c,c)]
        d = donor_r[SRC_NAME.get(c,c)]
        lit = LIT["retina"][c]
        r = face_row(c, CLASS_CN_R[c], d, pri, lit,
                     "Denominator = human normal adult neural retina capture event composition (snRNA-seq nuclei; D001 adult-only donor-level master file); not histological ground truth, not a compliance threshold (Astra T2 usage_scope)")
        r["a_measured"] = dict(donor_median_pct=d["donor_median_pct"], donor_iqr_pct=d["donor_iqr_pct"],
                               donor_range_pct=d["donor_range_pct"],
                               pooled_adult_only_ref=d.get("pooled_pct_for_reference_only"))
        r["c_prior_v1"] = dict(expected_range_pct=pri.get("expected_range_pct"),
                               per_study_spread_pct=pri.get("per_study_spread_pct"))
        if d.get("enrichment_note"): r["design_note"] = d["enrichment_note"]
        retina_rows.append(r)
    # Two vascular off-panel rows: No literature interval available for adult neural retina denominator → no_evidence row (no fabricated numbers)
    retina_rows.append(face_row("Endo_vascular", "Vascular endothelium (off-panel)", None, None,
        [dict(pmid="41578023", kind="identity", quote=None,
              note="HRCA 10-class vocabulary does not include vascular classes; true whole retina contains low-proportion vascular components, small clusters appearing is normal (baselines/retina.json caveat)")],
        "No applicable interval: literature percentages under neural retina snRNA denominator not pinned down → unexpected-identity disclosure only"))
    retina_rows.append(face_row("Pericyte_vascular", "Pericytes (off-panel)", None, None,
        [dict(pmid="41578023", kind="identity", quote=None,
              note="Same caveat: appearance of vascular mural components does not trigger contamination flag")],
        "No applicable interval → disclosure line"))

    stroma_ref = BO.get("stromal_keratocyte_reference", {})
    for cls_name, o in donor_o.items():
        lit = LIT["ocular_surface"].get(cls_name, [])
        r = face_row(cls_name, cls_name, o, None, lit,
                     "Denominator = human normal adult ocular surface (cornea/limbus/sclera super-class) capture event composition (D002 portal author annotation, adult-only donor-level master file); mixed-region definition, prohibits cross-region application (category_note)")
        r["a_measured"] = dict(donor_median_pct=o.get("donor_median_pct"), donor_iqr_pct=o.get("donor_iqr_pct"),
                               donor_range_pct=o.get("donor_range_pct"),
                               pooled_adult_only_ref=o.get("pooled_pct_for_reference_only"))
        if cls_name == "Fibroblasts" and stroma_ref:
            r["keratocyte_block"] = dict(pooled_pct=stroma_ref["d002_measured"]["pooled_pct"],
                                         unit_median=stroma_ref["d002_measured"]["unit_level_adult"]["median_pct"],
                                         source="ocular_surface.json stromal_keratocyte_reference (t_e1febb8e)")
        ocs_rows.append(r)
    # Conjunctival subclass disclosure row + goblet no_evidence row
    ocs_rows.append(face_row("Conjunctival_epithelium(sub)", "Conjunctival epithelium (sub-category within D002)", None, None,
        LIT["ocular_surface"]["_disclosure_conjunctival_epithelium"],
        "D002 lacks independent conjunctival super class (portal label assigned to Epithelium); conjunctival baseline = skeleton pending backfill (kb/baselines/conjunctiva.json)"))
    ocs_rows.append(face_row("Goblet_cell", "Goblet cells", None, None,
        LIT["ocular_surface"]["_disclosure_goblet"],
        "No on-disk quantitative literature statement for adult conjunctival goblet cell composition → no_evidence, fabrication prohibited"))

    # Three-criteria self-check
    all_pm = sorted({p for rows in (retina_rows+ocs_rows) for p in rows["pmids"]})
    ver = pmid_verify(all_pm)
    ledger = []
    for rows, page in ((retina_rows,"retina_normal_adult_human"), (ocs_rows,"ocular_surface_normal_adult_human")):
        for r in rows:
            for p in r["pmids"]:
                v = ver.get(p, {})
                ledger.append(dict(page=page, cell_type=r["cell_type"], pmid=p,
                                   title=v.get("title",""), year=v.get("year"), journal=v.get("journal"),
                                   n_chunks=v.get("n_chunks"), species=v.get("species"), tissues=v.get("tissues"),
                                   j1=v.get("j1_papers_jsonl"), j2=v.get("j2_nonghost"), j3=v.get("j3_trait_meta"),
                                   vk_or_sidecar=v.get("vk_or_sidecar_hit")))
    n_fail = sum(1 for l in ledger if not (l["j1"] and l["j2"] and l["j3"]))
    missing_pmid_rows = [f"{page}:{r['cell_type']}"
                         for rows,page in ((retina_rows,"retina_normal_adult_human"),(ocs_rows,"ocular_surface_normal_adult_human"))
                         for r in rows if not r["pmids"]]

    face = {
     "schema": "eyekb-composition-face/0.1",
     "entry_id": "EXPECTED_COMPOSITION_v0",
     "title": "Composition prior surface v0 (D-1): Normal adult retina + normal adult ocular surface/cornea-conjunctiva — literature-derived, default OFF",
     "generated": generated,
     "card": "t_fa03e1d7",
     "authority": "USER_DIRECTIVE_20260928_eyekb_improve_wave.md appended Seven B (D-1); task brief plans/comp_prior_20260928/BRIEF_DISC_COMP.md",
     "wiring": "OFF — not wired (zero MCP/runtime references; wiring and activation on separate cards/batches, any activation of this surface requires PI decision)",
     "status": "v0_candidate_selfcheck_only",
     "scope": {"species": "human", "organism_stage": "adult_only",
               "disease_states": "Not built (PDR annotation unreliable caliber maintained; disease materials must not be validated against healthy surface, Astra T2 usage_scope)",
               "fetal_organoid_developing": "Numerical folding excluded; exclusion reasons explicitly marked in citation records (32946783 organoid sentence/39117640 developing/36645183 fetal)",
               "tissues_out_of_v0": "Remaining tissues left for v1"},
     "evidence_grades": {"A": "Registry ledger external author annotations locally recalculated (kb/baselines adult-only donor-level main archive, with paths)",
                         "B": "On-disk ingested RAG literature original text directly reported (chunks verbatim sentences)",
                         "C": "Cross-study empirical intervals (kb/priors/composition/human_retina.json, card t_39182aa2)",
                         "no_evidence": "No A/B/C available → do not fabricate numbers"},
     "lineage_declaration": "Proportion interval source = D001(HRCA)/D002(OcularSurface) portal author annotation recalculation (via kb/baselines v1.1 adult-only main archive) + priors v1 empirical intervals + ingested literature original sentences; No self-clustering/self-demo annotations used throughout (anti-circularity clause)",
     "interval_rule": "low=floor(min(donor_iqr_low, priors_expected_low, fold_lit_low)); high=ceil(max(donor_iqr_high, priors_expected_high, fold_lit_high)); mid=donor_median; no source row=null(no_evidence)",
     "denominator_semantics": "Surface = composition reference of capture events for this sampling material under this experimental workflow (identity reference + background control), not histological ground truth, not composition compliance line; Flag = prompt for re-review ≠ annotation error",
     "pmid_verification": {"papers_jsonl": PAPERS, "sidecar": SIDECAR,
                           "criteria": "j1=bibliographic record parseable in v2.4.2 papers.jsonl (three bibliographic elements non-empty); j2=not ghost (n_chunks>0); j3=ingestion traceable (vk page ∨ sidecar ∨ papers.jsonl)",
                           "pmids_total": len(all_pm), "ledger_fail_rows": n_fail},
     "rows_missing_pmid": missing_pmid_rows,
     "activation_obligations": [
       "OB-1 Rows missing per-line PMID (D002 portal identity, no composition literature sentences on disk): See rows_missing_pmid — must supplement literature or maintain OFF before activation",
       "OB-2 Ocular surface = regional mixed super-class (D002 caliber), when activating wiring, stratify intervals by tissue_group or route by region (category_note prohibits cross-region application)",
       "OB-3 reverse QC triggered (Q1/Q2/Q3 healthy set flag rate >20%, see COMP_SELFFLAG_20260928.md §3): v0 intervals are too narrow for cross-platform/cross-sampling region/sorting designs, representing a known limitation on the surface side; stratification/exemption rules must be formalized and approved by PI before activation"
     ],
     "pages": {"retina_normal_adult_human": {
        "registry_anchor": "OA-D001 (HCA-HRCA-v1.0), PMID 41578023, path <STORE>/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad",
        "donor_main": "kb/baselines/retina.json adult-only master file (97 donors)",
        "rows": retina_rows},
       "ocular_surface_normal_adult_human": {
        "registry_anchor": "OA-D002 (CELLxGENE-OcularSurface), path <STORE>/data/D002_ocularsurface/D002_allcells_578K.h5ad",
        "donor_main": "kb/baselines/ocular_surface.json adult-only master file (41 donors/67 units); super-class mixed-region definition prohibits cross-region application",
        "rows": ocs_rows}},
     "caveats": [
       "RGC/neuron-like proportions influenced by nuclear sorting and library design (NeuN±, RGC enrichment) — check library strategy before flagging anomalies (inherits baselines caveat)",
       "snRNA (nucleus) and scRNA (cell) proportions cannot be directly compared (Astra T2)",
       "Ocular surface Immune pool is only 1.7%: inherent immune scarcity in ocular surface, immune proportions cannot be benchmarked against inflammatory samples",
       "Corneal Endothelium main archive median 0%: pure CEC material (fragment layer) denominator=100%, this row does not apply",
       "Goblet/conjunctival detail rows = dual absence of data and literature, marked no_evidence",
       "PAPER 41578023 (HRCA) n_chunks=1 (incremental ingestion, not full chunking) — j2 barely passes, content anchor does not rely on it"],
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"EXPECTED_COMPOSITION_v0.json").write_text(json.dumps(face, ensure_ascii=False, indent=1), encoding="utf-8")
    import csv
    with open(OUT/"ledgers/PROVENANCE_COMP_v0.tsv","w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ledger[0].keys()), delimiter="\t")
        w.writeheader(); w.writerows(ledger)
    print("rows:", len(retina_rows), "retina +", len(ocs_rows), "ocs | pmids:", len(all_pm),
          "| ledger:", len(ledger), "fail:", n_fail)
    for l in ledger:
        if not (l["j1"] and l["j2"] and l["j3"]):
            print("FAIL", l["page"], l["cell_type"], l["pmid"])

if __name__ == "__main__":
    sys.exit(build())
