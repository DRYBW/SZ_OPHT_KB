#!/usr/bin/env python3
"""Confusion-pair EVIDENCE PACKAGE (card item 5; ruling section D4) for RPE vs melanocyte.

Six elements, in the ruling's order: shared support; discriminating positive evidence; which changes are
state programmes; which distinctions need information the interface does not have; when several candidates
must be kept; when abstention is required. A thicker positive panel is not an answer and is not emitted as one.

Local material only, read-only, no network.
"""
import collections
import importlib.util as _ilu
import json
import os
import re
import sys

import pyarrow.dataset as ds

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
REPO = "/home/ubuntu/EYEKB_REPO"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
GENE_VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"
ALIGN = f"{REPO}/kb/markers/markers_cl_alignment_v2_unified.json"
RESULTS = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/results"
WAVE_MEAS = "/mnt/D/EyeKB/plans/holefill_v12_20261021/out/wave_measurement.json"

_s = _ilu.spec_from_file_location("m_scan", f"{WAVE}/scripts/m_scan.py")
_m = _ilu.module_from_spec(_s)
_s.loader.exec_module(_m)
TOKEN = _m.TOKEN
STOP = _m.STOP

CONTRAST = re.compile(r"differ|distinct|versus|\bvs\b|contrast|discriminat|separate|distinguish|"
                      r"unique to|specific to|unlike|whereas", re.I)

# (side, CL preferred name, corpus terms) -- the terms are name forms, not reference labels
SIDES = [
    ("rpe", "retinal pigment epithelial cell",
     ["retinal pigment epithelial cell", "retinal pigment epithelium", "rpe cell"]),
    ("melanocyte", "melanocyte",
     ["melanocyte", "melanocytes", "melanocyte-like"]),
]


def main():
    obo = cl_nav.load(OBO)
    terms = obo["terms"]
    vocab = set(json.load(open(GENE_VOCAB)))
    align = json.load(open(ALIGN))
    labels = align["labels"]

    # ---- recorded readings: the fixed reference and what each arm answered -------------------
    meas = json.load(open(WAVE_MEAS))["per_cluster"]
    ranked, query = {}, {}
    for vol in sorted(os.listdir(RESULTS)):
        p = os.path.join(RESULTS, vol, "annotation_evidence_report.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for c in d.get("clusters") or []:
            k = f"{vol}|{c.get('cluster')}"
            km = c.get("kb_marker") or {}
            ranked[k] = [(x.get("cell_type"), x.get("n_shared")) for x in (km.get("celltype_ranking") or [])]
            query[k] = [x.upper() for x in (c.get("top_genes") or [])[:10]]

    PIG = ["retinal pigment epithelial cell", "melanocyte", "pigmented epithelial cell",
           "pigmented ciliary epithelial cell", "non-pigmented ciliary epithelial cell"]

    def arm_top(k, arm):
        return (meas.get(k) or {}).get(f"{arm}_top")

    confusion = collections.Counter()
    truth_cells = collections.defaultdict(int)
    rpe_rows, mel_rows = [], []
    for k, r in meas.items():
        t = r.get("truth")
        if t not in PIG:
            continue
        truth_cells[t] += r.get("n_cells") or 0
        base = arm_top(k, "BASE")
        merged = arm_top(k, "MERGED")
        confusion[(t, base, merged)] += 1
        row = {"key": k, "truth": t, "n_cells": r.get("n_cells"),
               "BASE_top": base, "MERGED_top": merged,
               "BASE_n_shared": r.get("BASE_n_shared"), "ranking": ranked.get(k, [])[:4]}
        (rpe_rows if t == "retinal pigment epithelial cell" else mel_rows).append(row)

    # ---- literature support for each side, from the discovery corpus ------------------------
    pdf = ds.dataset(CORPUS).to_table(
        columns=["paper_id", "species", "tissue", "tissue_labels", "text"]).to_pandas()
    low = pdf["text"].fillna("").str.lower()

    # corpus-wide paper count per gene, so a slice's genes can be scored for SPECIFICITY
    global_gp = collections.Counter()
    for body in pdf["text"].fillna(""):
        gs = {t for t in TOKEN.findall(body) if t in vocab and t not in STOP}
        for g in gs:
            global_gp[g] += 1
    print(f"corpus-wide scored genes: {len(global_gp)}", flush=True)
    side_genes, side_papers, side_chunks, examples = {}, {}, {}, {}
    contrast_papers = collections.Counter()
    for side, canon, termsx in SIDES:
        pat = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in termsx)
                         + r")(?:s|es)?(?![a-z0-9])")
        hit = low.str.findall(pat).map(bool).to_numpy()
        sub = pdf.loc[hit]
        gp = collections.Counter()
        ex = {}
        for pid, body in zip(sub["paper_id"], sub["text"].fillna("")):
            gs = {t for t in TOKEN.findall(body) if t in vocab and t not in STOP}
            for g in gs:
                gp[g] += 1
            for g in gs:
                if len(ex.get(g, [])) < 2:
                    m = re.search(r"[^.!?]{0,180}\b%s\b[^.!?]{0,140}[.!?]" % re.escape(g), body)
                    ex.setdefault(g, []).append({"paper": str(pid),
                                                 "snippet": (m.group(0).strip()[:280] if m else "")})
        side_genes[side] = {g: n for g, n in gp.items() if n >= 2}
        side_papers[side] = int(sub["paper_id"].nunique())
        side_chunks[side] = int(len(sub))
        examples[side] = ex

    # contrast sentences naming both sides in one chunk
    both = SIDES[0][2] + SIDES[1][2]
    pat_both = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in both) + r")(?:s|es)?(?![a-z0-9])")
    hits = low.str.findall(pat_both)
    vocab_rpe = set(SIDES[0][2])
    vocab_mel = set(SIDES[1][2])
    for pid, xs, body in zip(pdf["paper_id"], hits, pdf["text"].fillna("")):
        x = set(xs)
        if (x & vocab_rpe) and (x & vocab_mel) and CONTRAST.search(body):
            contrast_papers[str(pid)] += 1

    # ---- shipped panels per side ------------------------------------------------------------
    import glob as _glob
    cls2cl = {k: (v or {}).get("cl_id") for k, v in labels.items()}
    shipped = {}
    for p in sorted(_glob.glob(f"{REPO}/kb/markers/markers_*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        pairs = []
        mk = d.get("markers")
        if isinstance(mk, dict):
            for kk, vv in mk.items():
                if isinstance(vv, list):
                    pairs.append((kk, vv))
                elif isinstance(vv, dict):
                    pairs.append((kk, vv.get("markers") or []))
        if isinstance(d.get("entries"), list):
            for e in d["entries"]:
                if e.get("class_name"):
                    pairs.append((e["class_name"], e.get("markers") or []))
        for nm, gs in pairs:
            if nm in ("RPE", "Melanocyte") or cls2cl.get(nm) in ("CL:0002586", "CL:0000148"):
                shipped.setdefault(nm, set()).update(str(g).upper() for g in gs)

    rpe_panel = set()
    mel_panel = set()
    for nm, gs in shipped.items():
        cid = cls2cl.get(nm)
        if cid == "CL:0002586" or nm == "RPE":
            rpe_panel |= gs
        if cid == "CL:0000148" or nm == "Melanocyte":
            mel_panel |= gs

    # ---- discriminating positive evidence ---------------------------------------------------
    rpe_pos, mel_pos = side_genes["rpe"], side_genes["melanocyte"]
    SPEC_FLOOR = 0.10          # at least a tenth of the papers mentioning the gene are in the slice
    rpe_spec = {g: round(n / global_gp[g], 4) for g, n in rpe_pos.items() if global_gp.get(g)}
    mel_spec = {g: round(n / global_gp[g], 4) for g, n in mel_pos.items() if global_gp.get(g)}
    rpe_only_all = {g: rpe_pos[g] for g in rpe_pos if g not in mel_pos}
    mel_only_all = {g: mel_pos[g] for g in mel_pos if g not in rpe_pos}
    rpe_only = {g: rpe_pos[g] for g in rpe_only_all if rpe_spec.get(g, 0) >= SPEC_FLOOR}
    mel_only = {g: mel_pos[g] for g in mel_only_all if mel_spec.get(g, 0) >= SPEC_FLOOR}
    shared_lit = sorted(set(rpe_pos) & set(mel_pos))
    shipped_shared = sorted(rpe_panel & mel_panel)

    # ---- state programme share ---------------------------------------------------------------
    state = json.load(open(f"{OUT}/O_state_ratio.json"))
    ratios = state["ratios"]

    def state_share(genes):
        if not genes:
            return None
        dep = [g for g in genes if ratios.get(g, 0) >= 0.75]
        return round(len(dep) / len(genes), 4)

    # ---- what the interface cannot see -------------------------------------------------------
    win = json.load(open(f"{OUT}/O_observable_window.json"))
    win_vocab = {g for g, _ in win["gene_frequency"]}

    # ---- emission ---------------------------------------------------------------------------
    doc = {
        "pair": "retinal pigment epithelial cell (CL:0002586) vs melanocyte (CL:0000148)",
        "why_this_pair": "the measured instance named in the brief; both are shipped dictionary classes, and "
                         "the audit shows RPE is a leaf term with zero is_a descendants, so this is a "
                         "SIBLING confusion pair, not a subdivision question",
        "1_shared_support": {
            "shipped_panel_overlap_genes": shipped_shared,
            "n_shipped_overlap": len(shipped_shared),
            "literature_genes_positive_for_both": shared_lit[:80],
            "n_literature_shared": len(shared_lit),
            "reading": "both sides are driven by the MITF/TYR-family pigment programme; the shared block is the "
                       "reason a marker panel cannot separate them"},
        "2_discriminating_positive_evidence": {
            "rpe_only_genes_ge2_studies_specific": dict(sorted(rpe_only.items(), key=lambda x: -x[1])[:40]),
            "n_rpe_only_specific": len(rpe_only),
            "n_rpe_only_unfiltered": len(rpe_only_all),
            "melanocyte_only_genes_ge2_studies_specific": dict(sorted(mel_only.items(), key=lambda x: -x[1])[:40]),
            "n_melanocyte_only_specific": len(mel_only),
            "n_melanocyte_only_unfiltered": len(mel_only_all),
            "specificity_floor": SPEC_FLOOR,
            "specificity_definition": "papers in the side's slice / papers corpus-wide mentioning the gene",
            "literature_slice_asymmetry_disclosed": {
                "rpe": {"chunks": side_chunks["rpe"], "papers": side_papers["rpe"]},
                "melanocyte": {"chunks": side_chunks["melanocyte"], "papers": side_papers["melanocyte"]},
                "note": "the RPE slice is far larger than the melanocyte slice, which is why an unfiltered "
                        "difference is dominated by whatever the RPE literature happens to discuss; the "
                        "specificity floor is what makes the two comparable, and the unfiltered counts are "
                        "kept beside the filtered ones rather than dropped"},
            "n_papers_with_adjacent_type_contrast": len(contrast_papers),
            "contrast_paper_examples": sorted(contrast_papers)[:15],
        },
        "3_state_programmes": {
            "state_share_rpe_only": state_share(list(rpe_only)),
            "state_share_melanocyte_only": state_share(list(mel_only)),
            "state_share_shared": state_share(shared_lit),
            "state_share_shipped_overlap": state_share(shipped_shared),
            "cutoff": ">= 0.75 of mentioning chunks in state context (Annex A7-b)",
        },
        "4_information_the_interface_does_not_have": {
            "n_rpe_only_genes_visible_in_recorded_window": len(set(rpe_only) & win_vocab),
            "n_melanocyte_only_genes_visible_in_recorded_window": len(set(mel_only) & win_vocab),
            "rpe_only_visible": sorted(set(rpe_only) & win_vocab)[:30],
            "melanocyte_only_visible": sorted(set(mel_only) & win_vocab)[:30],
            "window_definition": "union of the recorded top-10 gene lists of the 721 clusters",
            "reading": "a distinction whose discriminating genes do not reach the window cannot be made here; "
                       "absence from the window is NOT evidence the gene or class does not exist",
        },
        "5_when_several_candidates_must_be_kept": {
            "clusters_with_both_candidates_in_ranking": sum(
                1 for k, r in ranked.items()
                if any((a or "").lower().find("rpe") >= 0 or (a or "").lower().find("pigment") >= 0 for a, _ in r)
                and any((a or "").lower().find("melan") >= 0 for a, _ in r)),
            "note": "when the top-ranking candidates carry the shared pigment block, keep them side by side; "
                    "the emission has no automatic winner",
        },
        "6_when_abstention_is_required": {
            "clusters_with_no_candidate": sum(1 for k in meas if not ranked.get(k)),
            "rule": "if the window excludes the discriminating block and no independent material exists, the "
                    "correct output is the parent plus a named confusion reason, not a thinner guess",
        },
        "recorded_reading": {
            "truth_cells": dict(truth_cells),
            "confusion_counts": {f"{t} || BASE={b} || MERGED={m}": n for (t, b, m), n in confusion.items()},
            "rpe_truth_clusters": rpe_rows,
            "melanocyte_truth_clusters": mel_rows,
            "reading_class": "probing/regression reading on the fixed 28-volume set against a fixed reference "
                             "(author labels); not validation, and the reference is not an automatic gold standard",
        },
        "literature_support": {s: {"chunks": side_chunks[s], "papers": side_papers[s],
                                   "positive_genes": len(side_genes[s])} for s, _, _ in SIDES},
        "evidence_examples": {s: dict(list(examples[s].items())[:25]) for s, _, _ in SIDES},
        "red_line_check": "no candidate class name and no panel gene in this package was taken from a reference "
                          "label of an evaluation volume; the reference labels appear only in the recorded "
                          "reading block, which measures cost and confusion, not discovery",
    }
    json.dump(doc, open(f"{OUT}/confusion_rpe_melanocyte.json", "w"), ensure_ascii=False, indent=1)
    print("RPE-truth clusters:", len(rpe_rows), " melanocyte-truth clusters:", len(mel_rows))
    print("shared shipped overlap:", len(shipped_shared), "| literature shared:", len(shared_lit))
    print("rpe-only(pos>=2):", len(rpe_only), " melanocyte-only:", len(mel_only))
    print("contrast papers naming both:", len(contrast_papers))
    print("rpe-only visible in window:", len(set(rpe_only) & win_vocab),
          "| mel-only visible:", len(set(mel_only) & win_vocab))
    print("wrote", f"{OUT}/confusion_rpe_melanocyte.json")


if __name__ == "__main__":
    main()