#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_f3fa8c95 kc_sidecar_sync: EyeKB-side metadata/annotation layer sync (does not touch retrieval semantics, additive)
1) evidence_meta_v2.0_2026-09.jsonl += 4 rows (live reason sidecar — eyekb_core._reason_map
   hard-codes reading this file; without appending, the acceptance criterion "reason-joined table" cannot be met. No sha anchoring, no evalset reference)
2) evidence_meta_v2.3_2026-09.jsonl created = full v2.2 copy of 3696 rows + 4 new rows (version-complete table, POINTER-registered)
3) EYEKB_DB_POINTER.yaml appends the v2.3 entry (role: latest-kbadd; default not switched, following precedent pending user sign-off)
4) kbadd_KERATOCYTE_20260924.jsonl 4 rows retrieval_status -> IN_MAIN_DB (measured results passed in by selfcheck)
Idempotent: rows for pmids that already exist are skipped (dedup by pmid, no duplicate appends).
Red line: do not touch plans/evalset/; do not modify existing _reason_map rows.
"""
import json, os, re, sys
from pathlib import Path

EYEKB = Path("/mnt/D/EyeKB")
LIT = EYEKB / "kb/literature_db"
BASE = "/mnt/D/OcularKB/ocularkb/rag"
KC_PMIDS = ["41060151", "42115719", "11328728", "15914606"]

sel = {json.loads(l)["pmid"]: json.loads(l) for l in open(f"{BASE}/data_kc/kc_selected.jsonl")}
adm = json.load(open(f"{BASE}/data_kc/kc_admission.json"))
per = json.load(open(f"{BASE}/data_kc/kc_chunks_per_paper.json"))
side = {}
for l in open(LIT / "kbadd_KERATOCYTE_20260924.jsonl", encoding="utf-8"):
    d = json.loads(l)
    side[str(d["pmid"])] = d

# selfcheck measured results (optional, used for the retrievable annotation on kbadd status rows)
retr_note = {}
sc_path = f"{BASE}/data_kc/kc_selfcheck.json"
if os.path.exists(sc_path):
    sc = json.load(open(sc_path))
    for pm, v in (sc.get("anchor_rank") or {}).items():
        retr_note[pm] = v

# reason -> claim_relation axis mapping (following KB1v2-W4 three-field semantics)
AXIS_MAP = {
    "composition_baseline": ("composition", "support"),
    "state_signature": ("state", "qualify"),
    "disease_mechanism_background": ("mechanism_background", "qualify"),
    "disease_cell_composition": ("composition", "support"),
    "method_reference": ("technical_artifact", "support"),
}


def make_row(pm, with_source_db):
    s = sel[pm]
    a = adm[pm]
    axis, rel = AXIS_MAP[a["inclusion_reason"]]
    abstract_only = a["fulltext_status"] != "full_text"
    row = {
        "schema": "eyekb-evidence-meta/1.0",
        "generated_by": "kbadd_keratocyte_targeted (t_f3fa8c95; upstream t_e1febb8e sidecar)",
        "paper_id": pm, "pmid": pm,
        "pmcid": s.get("pmcid", ""),
        "title": s.get("title", ""),
        "year": s.get("year", ""),
        "journal": s.get("journal", ""),
        "inclusion_reason": a["inclusion_reason"],
        "inclusion_reasons": [a["inclusion_reason"]],
        "confidence": "high",
        "matched_rule": "kbadd-keratocyte-targeted(t_e1febb8e sidecar; eutils bibliographic verification)",
        "claim_relation": [{
            "axis": axis, "relation": rel,
            "note": (a.get("upstream_reason_detail") or "")[:300],
        }],
        "evidence_context": {
            "species": s.get("species", "unknown"),
            "tissue_labels": ["cornea"],
            "materials_hint": [],
            "disease_hint": (["fuchs"] if pm == "15914606" else []),
            "methods": ["transcriptomics"],
            "locator_anchor": ("upstream sidecar evidence sentences carry embedded provenance (t_e1febb8e)"
                               + ("; abstract-only (non-OA, no PMCID)" if abstract_only else "")),
        },
        "n_chunks": int(per.get(pm, 0)),
        "verification_status": "kbadd_review_20260925",
        "reviewer": "pi-chief",
        "review_note": ("PENDING_MAIN_DB->v2.3_2026-09 admission loop closed (t_f3fa8c95)"
                        + ("; abstract-only" if abstract_only else "")),
        "review_track": "kbadd_keratocyte",
    }
    if with_source_db:
        row["source_db"] = f"{BASE}/literature_db/v2.3_2026-09/manifest.yaml"
    return row


def append_unique(path, rows, tag):
    existing = set()
    for l in open(path, encoding="utf-8"):
        try:
            existing.add(str(json.loads(l)["pmid"]))
        except Exception:
            continue
    add = [r for r in rows if r["pmid"] not in existing]
    if add:
        with open(path, "a", encoding="utf-8") as f:
            for r in add:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[{tag}] appended {len(add)}/{len(rows)} (existing hits skipped)")


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--stage", choices=["meta", "status", "all"], default="all",
                help="meta=evidence_meta+POINTER (run before selfcheck); status=backfill the 4 kbadd status rows (run after selfcheck); all=both steps in order")
STAGE = ap.parse_args().stage

# 1) live sidecar (v2.0 file) append — the object eyekb_core._reason_map reads
if STAGE in ("meta", "all"):
    rows_v20 = [make_row(pm, with_source_db=False) for pm in KC_PMIDS]
    append_unique(LIT / "evidence_meta_v2.0_2026-09.jsonl", rows_v20, "evidence_meta_v2.0(live)")

    # 2) v2.3 version-complete table = v2.2 copy + 4 rows
    out23 = LIT / "evidence_meta_v2.3_2026-09.jsonl"
    if not out23.exists():
        src = open(LIT / "evidence_meta_v2.2_2026-09.jsonl", encoding="utf-8").read()
        with open(out23, "w", encoding="utf-8") as f:
            f.write(src)
            for pm in KC_PMIDS:
                f.write(json.dumps(make_row(pm, with_source_db=True), ensure_ascii=False) + "\n")
        print(f"[evidence_meta_v2.3] created = v2.2 lines + 4")
    else:
        append_unique(out23, [make_row(pm, with_source_db=True) for pm in KC_PMIDS], "evidence_meta_v2.3")

    # 3) register v2.3 in POINTER.yaml (idempotent)
    ptr_path = LIT / "EYEKB_DB_POINTER.yaml"
    ptr = ptr_path.read_text(encoding="utf-8")
    if "v2.3_2026-09:" not in ptr:
        entry = """  v2.3_2026-09:
    path: /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.3_2026-09
    role: latest-kbadd (frozen read-only; = v2.2 full inheritance with zero recompute + kbadd_keratocyte_targeted 4 papers; card t_f3fa8c95)
    chunks: CHUNKS_PLACEHOLDER
    unique_papers: PAPERS_PLACEHOLDER   # papers.jsonl line count = LINES_PLACEHOLDER (includes historical 0-chunk ghosts)
    sidecar: /mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.3_2026-09.jsonl
    manifest: /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.3_2026-09/manifest.yaml
    # MCP/stage3 default not switched (service behavior change, pending user sign-off per precedent; this card's acceptance was measured with the db parameter explicitly pointed at v2.3)
"""
        st = json.load(open(f"{BASE}/literature_db/v2.3_2026-09/build_stats.json"))
        nlines = sum(1 for _ in open(f"{BASE}/literature_db/v2.3_2026-09/papers.jsonl"))
        entry = (entry.replace("CHUNKS_PLACEHOLDER", str(st["n_chunks"]))
                     .replace("PAPERS_PLACEHOLDER", str(st["n_papers"]))
                     .replace("LINES_PLACEHOLDER", str(nlines)))
        # insert before the embedding_model: section
        ptr = ptr.replace("embedding_model:", entry + "embedding_model:")
        ptr_path.write_text(ptr, encoding="utf-8")
        print("[POINTER] v2.3 registered")
    else:
        print("[POINTER] v2.3 already registered (skip)")

# 4) update kbadd jsonl status rows (PENDING_MAIN_DB -> IN_MAIN_DB, with measured rank appended)
if STAGE in ("status", "all"):
    kbadd = LIT / "kbadd_KERATOCYTE_20260924.jsonl"
    lines = [json.loads(l) for l in open(kbadd, encoding="utf-8")]
    n_up = 0
    for d in lines:
        pm = str(d.get("pmid"))
        if pm in KC_PMIDS and d.get("retrieval_status", "").startswith("PENDING"):
            rk = retr_note.get(pm, {})
            rank = rk.get("raw_paper_rank")
            d["retrieval_status"] = (f"IN_MAIN_DB (v2.3_2026-09, admitted+measured 2026-09-25 t_f3fa8c95"
                                     + (f"; anchor title-query paper rank={rank}" if rank else "") + ")")
            n_up += 1
    if n_up:
        with open(kbadd, "w", encoding="utf-8") as f:
            for d in lines:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"[kbadd jsonl] {n_up} status rows updated")

print("DONE kc_sidecar_sync")
