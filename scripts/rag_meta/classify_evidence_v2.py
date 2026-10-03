#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB KB1v2-W4: RAG admission reclassified into three fields (Astra T5, additive)

Touches only the EyeKB-side metadata/annotation layer (kb/literature_db/ sidecar); no corpus
recrawl, no embedding recompute, no writes into v2.x library directories (that is t_08f0741e
v2.1 territory, parallel-isolated; v2.0 read-only).

Three fields (schema eyekb-evidence-meta/1.0):
  inclusion_reason(s)  why admitted -- five categories retained, now multi-select
  claim_relation       which specific claim it supports (composition/identity/state/technical artifact x support/refute/qualify)
  evidence_context     under what conditions, with what method (species/material/disease/method/locator anchor)
+ verification_status  auto_draft | human_single_review_20260923 (review switched to stratified sampling; random-50 acceptance dropped)

Usage:
  pass1: python classify_evidence_v2.py            -> evidence_meta_v2.0_2026-09.jsonl (all auto_draft)
                                                    + REVIEW_SHEET_v2.tsv (pending review list) + stratum counts
  pass2: python classify_evidence_v2.py --overlay REDECISIONS.json
        -> merge manual decisions, update verification_status (re-runnable, idempotent)
"""
import json
import re
import sys
import random
from collections import Counter
from pathlib import Path

EYEKB = Path("/mnt/D/EyeKB")
PAPERS = Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09/papers.jsonl")  # read-only
OLD_SIDE = EYEKB / "kb/literature_db/inclusion_reason_v2.0_2026-09.jsonl"  # v1 single-label archive, read-only
OUT = EYEKB / "kb/literature_db/evidence_meta_v2.0_2026-09.jsonl"
SHEET = EYEKB / "kb/literature_db/REVIEW_SHEET_v2.tsv"
DISEASES_IN_USE = EYEKB / "kb/priors/disease/PDR__fibrovascular_membrane.json"
BASELINES = EYEKB / "kb/baselines/retina.json"
SURFACE = EYEKB / "kb/baselines/ocular_surface.json"

LABELS = ["composition_baseline", "disease_cell_composition", "state_signature",
          "method_reference", "disease_mechanism_background"]
GEN = "classify_evidence_v2.py (KB1v2 t_16c3e020)"

RE_METHOD = re.compile(
    r"pipeline|benchmark|tool|framework|platform|integration|software|package|"
    r"algorithm|classifier|classification of|reference[- ]based|doublet|ambient|"
    r"hashing|demultiplex|quantification|evaluation|comparison|guide|practice|"
    r"consensus|standardi|assay|protocol|database|resource of|search engine|"
    r"foundation model|cell[- ]type annotation|annotat", re.I)
RE_STATE = re.compile(
    r"activat|phenotyp|polariz|reactiv|exhaust|disease[- ]associated|"
    r"cell states?|state transition|subcluster|functional state|stimulat|"
    r"primed|trained immunity|senescen", re.I)
RE_COMPO = re.compile(
    r"atlas|catalog|cell landscape|landscape|diversity|composit|cellularity|"
    r"single[-. ]cell (?:map|transcriptomic|characteri)|reference map", re.I)
RE_IDENTITY = re.compile(
    r"marker|cell type|celltype|classif|annotat|identif|characteri", re.I)
RE_DISEASE = re.compile(
    r"diabetic|retinopath|proliferative|macular degeneration|\bAMD\b|\bGA\b|"
    r"glaucoma|cataract|keratoconus|keratitis|\bFuchs\b|retinitis|pigmentosa|"
    r"uveitis|dry eye|degeneration|hyperoxia|\bOIR\b|retinopathy of prematurity|"
    r"\bROP\b|trauma|ischemia|ischaemia|fibrosis|tumor|glioma|melanoma|"
    r"injur|damage|aging|aged\b|old age", re.I)
RE_MECH = re.compile(
    r"mechanism|role|pathway|signaling|regulat|drives|promot|required|therapeut|"
    r"target|progression|onset|effect|treat|supplement|deficien", re.I)
RE_SC = re.compile(r"single[-. ]?cell|scRNA|snRNA|single[-. ]?nucleus|transcriptomic|"
                   r"CITE|ATAC|multi[-. ]?omic|spatial|Xenium|Visium", re.I)

RE_MATERIAL = re.compile(
    r"fibrovascular|membrane|vitreous|subretinal fluid|subretinal|inner limiting|"
    r"neural retina|retinal explant|explant|whole retina|macula|fovea|peripheral retina|"
    r"cornea|corneal|limbus|sclera|conjunctiva|lens|RPE|retinal pigment epithel|"
    r"choroid|retinal pigment epithelium|trabecular|Schlemm|optic nerve|optic head|"
    r"PBMC|blood|serum|plasma|organoid|iPSC|stem cell|aqueous|mouse retina|immortalized|"
    r"cell line|xenograft|devitalized", re.I)
RE_METHODSEQ = re.compile(
    r"single[-. ]?cell|scRNA|snRNA|single[-. ]?nucleus|spatial|CITE|ATAC|multi[-. ]?omic|"
    r"bulk|RNA[- ]velocity|smFISH|MERFISH|immunostain|immunohisto|proteomic|代谢组|model|"
    r"simulation|review|meta[-. ]?analy", re.I)


def uniq(x):
    return list(dict.fromkeys(x))


def classify(title, species, tissues, old):
    t = title
    dis = bool(RE_DISEASE.search(t))
    sc = bool(RE_SC.search(t))
    reasons = []
    rules = []
    if RE_METHOD.search(t):
        reasons.append("method_reference"); rules.append("v2-method")
    if RE_COMPO.search(t) and (sc or dis is False):
        reasons.append("composition_baseline"); rules.append("v2-compo")
    if dis and sc:
        reasons.append("disease_cell_composition"); rules.append("v2-disease+sc")
    if RE_STATE.search(t) and (sc or dis):
        reasons.append("state_signature"); rules.append("v2-state")
    if dis and RE_MECH.search(t):
        reasons.append("disease_mechanism_background"); rules.append("v2-mech")
    elif dis and not sc:
        reasons.append("disease_mechanism_background"); rules.append("v2-disease-fallback")
    elif dis:
        reasons.append("disease_mechanism_background"); rules.append("v2-disease-fallback")
    if old.get("inclusion_reason"):
        mr = str(old.get("matched_rule", ""))
        strong = (not any(w in mr for w in ("fallback", "weak"))
                  and mr != "normal-development-biology")
        reasons.append(old["inclusion_reason"])  # v1 vote (additive; weak votes only fall back, never lead)
        rules.append(("v1-inherit:" if strong else "v1-weak-inherit:") + mr)
    reasons = [r for r in uniq(reasons) if r in LABELS]
    if not reasons:
        reasons = ["disease_mechanism_background"] if dis else ["composition_baseline"]
        rules.append("v2-default")
    conf = old.get("confidence", "low")
    strong_v1 = any(r.startswith("v1-inherit:") for r in rules)
    if (len(rules) >= 2 and any(not r.startswith("v1-weak") for r in rules)
            and conf != "high") or strong_v1:
        if conf == "low" and not any(r.startswith(("v2-", "title")) for r in rules):
            conf = "low"
        elif conf != "high":
            conf = "medium"
    # claim_relation (coarse at paper level; claim-level precision = manual review layer)
    claims = []
    if any(r in ("composition_baseline", "disease_cell_composition") for r in reasons):
        claims.append({"axis": "composition", "relation": "support"})
    if RE_IDENTITY.search(t) and sc:
        claims.append({"axis": "identity", "relation": "support"})
    if "state_signature" in reasons:
        claims.append({"axis": "state", "relation": "support"})
    if "method_reference" in reasons:
        claims.append({"axis": "technical_artifact", "relation": "qualify"})
    if "disease_mechanism_background" in reasons and not claims:
        claims.append({"axis": "mechanism_background", "relation": "support",
                       "note": "mechanistic background; does not constitute a composition/identity/state-level interpretation claim (Astra T4: do not upgrade correlation to functional proof)"})
    materials = uniq([m.group(0).lower() for m in RE_MATERIAL.finditer(t)])
    methods = uniq([m.group(0).lower() for m in RE_METHODSEQ.finditer(t)])
    dset = uniq([d.group(0).lower() for d in RE_DISEASE.finditer(t)])
    ev_ctx = {
        "species": species,
        "tissue_labels": tissues,
        "materials_hint": materials,
        "disease_hint": dset,
        "methods": methods,
        "locator_anchor": "title-level rules; abstract/figure locator anchors to be added at review",
    }
    return reasons, conf, rules, claims, ev_ctx


def d0_critical_pmids():
    """PMIDs of key claims directly supporting D0 rules/baselines (item-by-item manual verification list, Astra T5)."""
    s = set()
    for p in (DISEASES_IN_USE, BASELINES, SURFACE):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            for src in d.get("sources", []):
                if src.get("pmid"):
                    s.add(str(src["pmid"]))
        except Exception:
            pass
    return s


def strata_of(rec):
    m = rec["evidence_context"]["materials_hint"]
    mat = m[0] if m else "none"
    sp = rec["evidence_context"]["species"]
    return (",".join(sorted(rec["inclusion_reasons"][:2])), mat, sp)


def main(overlay_path=None, papers_path=None, out_path=None, sheet_path=None,
         source_db=None, gen_tag=None):
    papers_path = Path(papers_path or PAPERS)
    out_path = Path(out_path or OUT)
    sheet_path = Path(sheet_path or SHEET)
    gen = gen_tag or GEN
    old_map = {}
    with open(OLD_SIDE, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            old_map[str(d["pmid"])] = d
    recs, cnt, low = [], Counter(), 0
    with open(papers_path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            pmid = str(d.get("paper_id"))
            reasons, conf, rules, claims, ctx = classify(
                d.get("title", ""), d.get("species", "unknown"),
                d.get("tissues", []) or [], old_map.get(pmid, {}))
            rec = {"schema": "eyekb-evidence-meta/1.0", "generated_by": gen,
                   "paper_id": pmid, "pmid": pmid, "pmcid": d.get("pmcid"),
                   "title": d.get("title"), "year": d.get("year"),
                   "journal": d.get("journal"),
                   "inclusion_reason": reasons[0],       # legacy key compatibility = primary label
                   "inclusion_reasons": reasons,          # T5 multi-select
                   "confidence": conf, "matched_rule": ";".join(rules),
                   "claim_relation": claims,
                   "evidence_context": ctx,
                   "n_chunks": d.get("n_chunks", 0),
                   "verification_status": "auto_draft", "reviewer": None,
                   "review_note": None}
            if source_db:
                rec["source_db"] = source_db
            if conf == "low":
                low += 1
            cnt[tuple(sorted(reasons))[:1]] += 1
            recs.append(rec)
    # review set = D0 critical (all) union stratified quota sample (5 primary classes x confidence tier; low-confidence tier doubled, multi-label prioritized)
    d0 = d0_critical_pmids()
    rng = random.Random(20260923)
    by_strata = {}
    for r in recs:
        by_strata.setdefault(strata_of(r), []).append(r)
    sample = set(d0)
    strata2 = {}
    for r in recs:
        key = (r["inclusion_reason"], "low" if r["confidence"] == "low" else "highmed")
        strata2.setdefault(key, []).append(r)
    for k, v in sorted(strata2.items()):
        q = 12 if k[1] == "low" else 6
        v_sorted = sorted(v, key=lambda r: -(len(r["inclusion_reasons"]) > 1))
        half = q // 2
        take = list(v_sorted[:half])
        rest = v_sorted[half:]
        take += rng.sample(rest, k=min(q - half, len(rest)))
        sample.update(r["pmid"] for r in take)
    for r in recs:
        if r["pmid"] in d0:
            r["review_track"] = "D0_critical"
        elif r["pmid"] in sample:
            r["review_track"] = ("low_confidence_sample" if r["confidence"] == "low"
                                 else "stratified_sample")
    overlay = {}
    ov_paths = ([overlay_path] if isinstance(overlay_path, (str, Path)) else list(overlay_path or []))
    for op in ov_paths:
        if op and Path(op).exists():
            d = json.loads(Path(op).read_text(encoding="utf-8"))
            overlay.update({k: v for k, v in d.items() if not k.startswith("_")})
    n_ver = 0
    for r in recs:
        ov = overlay.get(r["pmid"])
        if ov:
            r.update({k: v for k, v in ov.items() if k in (
                "inclusion_reasons", "inclusion_reason", "claim_relation")})
            r["verification_status"] = ov.get("status", "human_single_review_20260923")
            r["reviewer"] = ov.get("reviewer", "pi-chief(t_16c3e020) single reviewer")
            r["review_note"] = ov.get("note")
            n_ver += 1
    with open(out_path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(sheet_path, "w", encoding="utf-8") as f:
        f.write("pmid\ttrack\tspecies\tn_chunks\tconfidence\tproposed_reasons\ttitle\n")
        for r in sorted(recs, key=lambda x: (x.get("review_track", "z"), x["pmid"])):
            if r.get("review_track"):
                f.write("\t".join(map(str, [r["pmid"], r["review_track"],
                                            r["evidence_context"]["species"], r["n_chunks"],
                                            r["confidence"], "|".join(r["inclusion_reasons"]),
                                            (r["title"] or "")[:220]])) + "\n")
    # stats output
    prim = Counter(r["inclusion_reason"] for r in recs)
    multi = Counter(l for r in recs for l in r["inclusion_reasons"])
    print("papers:", len(recs), "| low-conf:", low, "| review set:",
          sum(1 for r in recs if r.get("review_track")), "| verified in:", n_ver)
    print("primary-label dist:", dict(prim))
    print("multi-label dist:", dict(multi))
    print("D0 critical pmids:", len(d0))
    print("strata keys:", len(by_strata))
    print("OUT:", out_path, "SHEET:", sheet_path)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="KB1v2-W4 evidence sidecar (parametrized in v2.2 by KB1v2d t_bb170f1b)")
    ap.add_argument("--overlay", nargs="*", default=None)
    ap.add_argument("--papers", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--source-db", default=None)
    ap.add_argument("--gen", default=None)
    a = ap.parse_args()
    main(a.overlay, a.papers, a.out, a.sheet, a.source_db, a.gen)
