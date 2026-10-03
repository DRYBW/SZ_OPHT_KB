#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP soft-review hint layer (t_d6f2a0a0 / D4 released, PI 2026-09-25)
v0.2 · rewritten per the seven mandatory items of the REVIEWER_LLM CONDITIONAL reply
(the original reply is an online-side file, not included in this repo)

Two soft hints (reminders, not hard flags; no new naming/abstention/candidate-exclusion conditions):
  1) rod_bc_review  —— basis /mnt/D/OcularKB/models/V2PROD_ROD_BC_BLINDSPOT_20260925.md
     (C18 case: 2/48,517 in the clean window excluding C18; an isolated cluster is not a systematic
     blind spot → soft hint only, no flag)
  2) mural_crosstalk —— basis /mnt/D/EyeKB/plans/kb6b_face_20260925/AUDIT_KB6b_D002_separation.md
     + STROMAL_WARNING_DRAFT.md; wording baseline = EVAL_RUN5FACE_20260925.md v1.1 errata
     (Q6::24 = Myofibroblast/SMC mural entry takeover chain, NOT Keratocytes).

Discipline (REVIEWER_LLM §3.6/§3.7/B4/B5/B7):
- Notes are attached only after existing results are produced; no feedback onto candidates/scores/
  ordering/original fields; no new field that could be read as a weight/risk score (severity-type
  fields were removed per §3.7).
- The tied-score group (TOP) semantics remove dict insertion-order dependence; no secondary sort is
  added to ranking.
- Three role tiers: audited shared/reverse evidence / target-class survival anchor / panel-membership
  fact only.
- Runtime messages never output CL identifiers not corroborated by OLS through this executor
  (red line 3); ontology subsumption is quoted from audited definition text (source = KB6b §2
  point 4, whose OLS citation is on file).
- Panel = the markers snapshot actually loaded by the current query_marker call (source/version
  written into the trigger), never an implicit rollup of historical or future versions.
- Switch: env EYEKB_MCP_SOFTFLAGS read once per call; strip().casefold() ∈ {0,false,off,no}
  → off; all other values → on; when off the whole key is absent.
"""
import os

SCHEMA = "eyekb-softflag/1.0"

# ---- flag#1 parameters (§2 + REVIEWER_LLM Q1/Q2 ruling: TOP tie group, not extended to the strict runner-up) ----
ROD_MIN_HITS = 2         # |R| >= 2 (gene-evidence-level heuristic; not an expression-dominance observation)
ROD_GE_BCCORE = True     # |R| >= |B| clause retained (REVIEWER_LLM Q1: do not delete the comparison term to widen hits)

# ---- flag#2 parameters (§3 + REVIEWER_LLM Q3 ruling A: single hit = "family-panel association reminder") ----
MURAL_RANK_BOUNDARY = 3  # TOP3 = the hit-count boundary of the 3rd distinct class and all classes tied with it

# canonical normalization (REVIEWER_LLM §3.1): strip whitespace → take the "::" suffix → casefold →
# finite synonym table; used only for notes criteria, never written back into responses/entry parsing;
# no fuzzy matching for names outside the table.
_SYNONYM = {
    "pericyte": "Pericyte", "pericytes": "Pericyte",
    "fibroblast": "Fibroblast", "fibroblasts": "Fibroblast",
    "myofibroblast": "Myofibroblast", "myofibroblasts": "Myofibroblast",
    "keratocyte": "Keratocytes", "keratocytes": "Keratocytes",
    "smc": "SMC", "smooth muscle cells": "SMC",
    "bc": "BC", "rod": "Rod",
}
MURAL_CLASSES = {"Keratocytes", "Fibroblast", "Pericyte", "SMC", "Myofibroblast"}


def _canon(ct):
    s = str(ct).strip()
    s = s.split("::")[-1]
    return _SYNONYM.get(s.casefold(), None) if s.casefold() in _SYNONYM else s


# Three role tiers (evidence layering, no overclaiming):
#   T2 = shared/reverse evidence on file in the KB6b per-cell three-color audit (file + section
#        number disclosed with the message)
#   T2a = direction-reversal / epithelial-origin / blanket-signature readings on file in
#         STROMAL_WARNING_DRAFT
#   T3 = panel-membership fact only (no independent audit role) — must not be read as proven crosstalk
ROLES = {
    "audited_shared": {  # KB6b §2 per-cell red criteria on file (T2)
        "NNMT": "audited: reverse false anchor for the Keratocytes entry — donor agreement rate 0.167 "
                "against fibrous stroma, direction reversed"
                " (KB6b §2 point 2)",
        "ALDH3A1": "audited: reverse against corneal-epithelium subtypes — Corneal_suprabasal_PMC "
                   "lfc=-0.32/cons=0.125;"
                   " a corneal-epithelium differentiation-program gene, masked by pooling → RED "
                   "(KB6b §2 point 3)",
        "DCN": "audited: reverse against Keratocytes lfc≤-1.96 (red gene of the Fibroblast entry, "
               "KB6b §2 table)",
        "LUM": "audited: reverse against Keratocytes lfc≤-1.96 (same as above)",
        "PTGDS": "audited: reverse against Keratocytes lfc≤-1.96 (same as above)",
        "COL1A2": "audited: common red gene of both the Fibroblast and Pericyte entries; reverse "
                  "-1.99 against Keratocytes, "
                  "-2.81 against fibrous stroma (KB6b §2 table)",
        "ACTA2": "audited: red gene of the SMC entry, lfc 0.83@Pericytes (triggered by the neighbour "
                 "group, KB6b §2 table)",
        "TAGLN": "audited: SMC red gene (-0.25@Pericytes) and the highest-loading group of the "
                 "Myofibroblast entry "
                 "= Pericytes (KB6b §2 table/§3)",
        "PRRX1": "audited: red gene of the Pericyte entry (KB6b §2 table)",
        "MGP": "audited: red gene of the Pericyte entry (KB6b §2 table)",
        "ITGA1": "audited: red gene of the Pericyte entry (KB6b §2 table)",
        "THY1": "audited: red gene of the Pericyte entry; Fibroblast's THY1/COL3A1 also fail against "
                "Schwann/arterial subtypes"
                " (KB6b §2 table/§4)",
        "FN1": "audited: red gene of the Fibroblast entry (KB6b §2 table)",
    },
    "survival_anchor": {  # KB6b §2 point 5/§8 survival anchors, by target-class context (B2 fix: no cross-class counting)
        "KERA": "survival anchor on the Keratocytes side (D002 three-color all-green, all-green against "
                "all 9 neighbour groups) — if naming Keratocytes, re-check"
                " KERA and the corneal-stroma context",
        "NOTCH3": "survival anchor on the Pericyte side — used for Pericyte neighbour-class comparison; "
                  "does not substitute for support evidence of other classes",
        "HIGD1B": "survival anchor on the Pericyte side — same as above",
        "CALD1": "survival anchor on the Pericyte side (also a member of the mural-cell general signature; "
                 "each of the two contexts is read per its own audit entry)",
        "CNN1": "survival anchor on the SMC side — used for SMC neighbour-class comparison; does not "
                "substitute for support evidence of other classes",
        "MYH11": "survival anchor on the SMC side — same as above",
        "MYL9": "survival anchor on the SMC side; also a shared member of the SMC/Myofibroblast panels "
                "(keep the contexts separate)",
        "DES": "survival anchor on the SMC side — same as above (the structural-zero audit touches only "
               "the SMC·DES cell, KB6b §7 A4)",
        "LMOD1": "survival anchor on the SMC side — same as above",
    },
}


def panel_member_note(gene):
    """T3: family-panel genes not listed in the audit role table — report the panel-membership fact only."""
    return ("panel-membership fact (in the mural family panel of the markers snapshot loaded by this "
            "call; this executor carries no independent audit role for it)")


def enabled():
    v = (os.environ.get("EYEKB_MCP_SOFTFLAGS") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _class_hits(markers):
    """Derive (canonical class name → gene set) from the current markers snapshot, plus the file-version list."""
    per_class = {}
    for ct, gs in markers.items():
        c = _canon(ct)
        s = per_class.setdefault(c, set())
        s.update(str(g).strip().upper() for g in gs)
    return per_class


def _snapshot_sources(prov):
    return [{"library": f.get("library"), "version": f.get("version"), "path": f.get("path")}
            for f in (prov or {}).get("files", [])]


def _top_groups(ranking):
    """h(c) = the maximum of the existing n_shared across rows of canonical class c (no summing, no
    new ranking output). TOP = the set of classes reaching the global max h."""
    h = {}
    for e in ranking or []:
        try:
            n = int(e.get("n_shared", 0))
        except (TypeError, ValueError):
            n = 0
        if n <= 0:
            continue  # zero-hit rows do not constitute evidence
        c = _canon(e.get("cell_type", ""))
        h[c] = max(h.get(c, 0), n)
    if not h:
        return {}, set(), set()
    mx = max(h.values())
    top = {c for c, v in h.items() if v == mx}
    # TOP3 = the hit-count boundary of the 3rd distinct **class** and all classes tied with it
    # (REVIEWER_LLM R2 mandatory-fix 4: keep one score per class, no dedup of the score layer;
    #  already distinguished from the "top three distinct score tiers" counterexample)
    scores = sorted(h.values(), reverse=True)   # counted per class, no set() dedup
    b3 = scores[min(2, len(scores) - 1)]
    top3 = {c for c, v in h.items() if v >= b3}
    return h, top, top3


SUFFIX = ("this hint is not a hard flag and constitutes neither a naming condition nor an abstention "
          "condition; its presence does not indicate mis-annotation; "
          "it must not be used for module score, label weighting, confidence bonus, or candidate "
          "ranking input (service-level red line).")


def build_notes(markers, mode, query_genes=None, ranking=None, found_classes=None,
                provenance=None):
    """Return the notes list (may be empty). Pure annotation: does not touch ranking/other fields."""
    if not enabled():
        return []
    per_class = _class_hits(markers)
    rod = per_class.get("Rod", set())
    bc_all = per_class.get("BC", set())
    # BC core = the v4.1 canonical-naming panel of canonical BC (the one whose display name is exactly
    # "BC"); if the current libraries have no "BC" display name (e.g. library=retina_interneuron alone),
    # the core degrades to that BC panel itself.
    bc_core = set()
    for ct, gs in markers.items():
        if str(ct).strip() == "BC":
            bc_core = {str(g).strip().upper() for g in gs}
    if not bc_core:
        bc_core = bc_all
    mural_union = set()
    for c, gs in per_class.items():
        if c in MURAL_CLASSES:
            mural_union |= gs

    # Symbol set U = the deduplicated canonical per-call sequence used for core matching (the query was
    # already uppercased by core; its output is not modified)
    u = {str(g).strip().upper() for g in (query_genes or []) if str(g).strip()}
    r_hits = sorted(u & rod)
    b_hits_n = len(u & bc_core)
    h_map, top, top3 = _top_groups(ranking)
    notes = []
    src = _snapshot_sources(provenance)

    # ---------- flag#1 rod_bc_review (genes mode only) ----------
    if mode == "genes" and "BC" in top and len(r_hits) >= ROD_MIN_HITS \
            and (not ROD_GE_BCCORE or len(r_hits) >= b_hits_n):
        bc_max = h_map.get("BC", 0)
        tied = sorted(top)
        notes.append({
            "flag_id": "rod_bc_review",
            "hard_flag": False,
            "affects_score": False,
            "trigger": {
                "mode": "genes",
                "rod_panel_hits": r_hits,
                "rod_hits_n": len(r_hits),
                "bc_core_hits_n": b_hits_n,
                "bc_h": bc_max,
                "max_tied_classes": tied,
                "rule": ("mode==genes ∧ BC∈TOP(highest-hit tie group) ∧ |R|≥%d ∧ |R|≥|B_core|"
                         % ROD_MIN_HITS),
                "data_snapshot": src,
            },
            "message": (
                "review reminder: the gene evidence of this query contains rod-panel genes " + ",".join(r_hits) +
                ", and BC sits in the highest-hit tie group of this tool's ranking"
                + (f" (tied with {'|'.join(x for x in tied if x != 'BC') or '—'})" if len(tied) > 1 else "")
                + ". If you intend to name BC, re-check together with expression levels (rod3/bc3 per-10k "
                "caliber) and the co-expression background;"
                " this tool observes neither expression dominance nor the final annotation. Historical audit "
                "background (caliber = out-of-training-pool"
                " truth=Rod∧rod_dominant clean window; not the accuracy of a proxy rule on the current gene "
                "set,"
                " nor a risk estimate for the current query): excluding the C18 single cluster"
                " 2/48,517 (0.004%); C18 at the same caliber 511/660 (77.42%); including C18 513/49,177"
                " (1.043%) — the blind spot is the isolated-cluster pattern of GSE155288 C18 (direction "
                "pointing at degenerated/low-quality rod),"
                " not a systematic low-margin blind spot; this summary includes the Q8 fetal set and so does "
                "not constitute an adult population rate — do not extrapolate the size of the blind spot from"
                " low-bar band rates computed without truth filtering." + SUFFIX),
            "evidence": {
                "interpretation_source":
                    "/mnt/D/OcularKB/models/V2PROD_ROD_BC_BLINDSPOT_20260925.md",
                "note": "this note is a gene-set-layer review heuristic, not an expression-dominance detector."},
        })

    # ---------- flag#2 mural_crosstalk ----------
    conditions = []
    role_lines = []
    if mode == "cell_type":
        hit_classes = sorted({_canon(ct) for ct in (found_classes or []) if ct})
        fam = [c for c in hit_classes if c in MURAL_CLASSES]
        if fam:
            conditions.append("entry query hit family classes: " + "|".join(fam))
    elif mode == "genes":
        gene_hits = sorted(u & mural_union)
        if gene_hits:
            conditions.append(f"family-panel association reminder: {len(gene_hits)} of the input genes"
                              f" hit the mural family panel: " + ",".join(gene_hits) +
                              " (a single hit already gets an annotation; this is not evidence of "
                              "discovered crosstalk)")
            for g in gene_hits:
                role = ROLES["audited_shared"].get(g) or ROLES["survival_anchor"].get(g) \
                    or panel_member_note(g)
                kind = ("T2-audited shared/reverse evidence" if g in ROLES["audited_shared"] else
                        "T2a-target-class survival anchor" if g in ROLES["survival_anchor"] else
                        "T3-panel-membership fact only")
                role_lines.append(f"[{kind}] {g}: {role}")
        fam_top3 = sorted(c for c in top3 if c in MURAL_CLASSES)
        if fam_top3:
            conditions.append("family classes appear inside the ranking's highest-hit tie group / the "
                              "3rd-class boundary: "
                              + "|".join(fam_top3))
    if conditions:
        notes.append({
            "flag_id": "mural_crosstalk",
            "hard_flag": False,
            "affects_score": False,
            "trigger": {
                "mode": mode,
                "conditions": conditions,
                "rule": ("cell_type: found entry canonical∈family; genes: U∩family panel≠∅ or "
                         "TOP3∩family≠∅ (TOP3 = the hit-count boundary of the 3rd distinct class, ties "
                         "included)"),
                "data_snapshot": src,
            },
            "message": (
            "crosstalk warning (D002 ocular surface): the Pericytes/Smooth Muscle Cells/Fibroblasts/"
            "Myofibroblasts/Keratocytes family carries a shared-marker reading risk — under the KB6b "
            "three-color re-review"
            " 4 entries are all-red and the fibrous-stroma entry has 0 green; audited definition "
            "(OLS original text in KB6b §2 point 4,"
            " this runtime message does not transcribe CL identifiers, per red line 3): a keratocyte is a "
            "fibroblast specialised for residence in the corneal stroma (keratocyte⊂fibroblast in the "
            "ontological sense). When a reading involves this family—"
            " ① NNMT is an audited reverse false anchor (donor agreement rate 0.167, direction reversed); "
            "that audit does not support using it "
            "as interstitium-discrimination evidence;"
            " ② ALDH3A1 is an audited epithelial-program gene (reverse against suprabasal PMC); when you see "
            "it, check the epithelial context first;"
            " ③ direction relations follow the KB6b per-cell table: DCN/LUM/PTGDS are audited reverse "
            "against Keratocytes"
            " (lfc≤-1.96); COL1A2 is audited reverse against Keratocytes (-1.99) and -2.81 against fibrous "
            "stroma;"
            " for the remaining red-gene members such as FN1: red-gene identity does not imply a direction "
            "toward a particular neighbour class — the corresponding table cell is authoritative;"
            " for Keratocytes↔Fibroblast mutual calls, re-check against the KB6b red/green criteria; the only"
            " all-green anchor on the Keratocytes side is KERA — if you intend to name Keratocytes, re-check "
            "KERA and the corneal-stroma context;"
            " the Pericyte-side survival anchors NOTCH3/HIGD1B/CALD1 and the SMC-side "
            "CNN1/MYH11/MYL9/DES/LMOD1"
            " are each used for neighbour-class comparison within their own target class — no cross-class "
            "counting and no substituting for each other's support evidence;"
            " ④ when comparing Pericyte vs SMC vs Myofibroblast, interpret them together with the "
            "co-expression background;"
            " ⑤ the Myofibroblast entry: the KB6b §3 cross-scan records that it has no exclusive "
            "high-expression home group"
            " on the D002 ocular surface (see that section's per-cell table); keep this audit background in "
            "mind when a reading cites it."
                " Falsified-wording reminder: the attribution of RUN5-face Q6::24 (truth=Pericytes 98.7% pure) "
                "is"
                " expression-layer-compatible evidence of the Myofibroblast/SMC mural entry takeover chain "
                "(kb_top1=Myofibroblast, three votes=SMC,"
                " the Pericyte entry never ranked), not Keratocytes; the query-engine-side ranking"
                " mechanism is unaudited (KB6b REVIEWER_LLM A10 boundary)."
                + ("".join(" per-gene role " + ln + ";" for ln in role_lines[:14]))
                + SUFFIX),
            "evidence": {
                "interpretation_source": [
                    "/mnt/D/EyeKB/plans/kb6b_face_20260925/AUDIT_KB6b_D002_separation.md",
                    "/mnt/D/EyeKB/plans/kb6b_face_20260925/STROMAL_WARNING_DRAFT.md",
                    "/mnt/D/EyeKB/plans/evalset/EVAL_RUN5FACE_20260925.md (v1.1 errata)"],
                "role_layers": "T2=on file in the KB6b per-cell audit; T2a=survival anchors by target-class "
                               "context; "
                               "T3=panel-membership fact of this call only (no independent audit role)"},
        })

    notes.sort(key=lambda n: n["flag_id"])
    return notes


def wrap_resp(resp, markers, mode, provenance=None, **kw):
    """eyekb_core mounting helper: add the soft_flags key only when notes exist (off/empty → key not
    mounted; equivalence with the pre-change output is verified by sf13 at the canonical serialization
    layer — no claim of session-level byte identity)."""
    notes = build_notes(markers, mode, provenance=provenance, **kw)
    if notes:
        resp["soft_flags"] = {"schema": SCHEMA, "enabled": True, "notes": notes}
    return resp
