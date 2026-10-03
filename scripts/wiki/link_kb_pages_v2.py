#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB1v2-W5: vk literature index pages <-> interpretation layer four-way links (idempotent append, pages carry version)

Four-way = disease entries <-> composition baselines <-> RAG reason-tag (evidence_meta sidecar) <-> literature index pages.
Astra T5: literature links alone are insufficient for audit -> each page links to stable concept IDs / entry files / sidecar field paths.
"""
import re
from pathlib import Path

VK = Path("/mnt/D/EyeKB/kb/vk_literature_index")
MARK = "<!-- KB1V2-WIKILINKS v1.1 -->"
VER = "Interpretation-layer link version: KB1v2 (2026-09-23, t_16c3e020)"

TISSUE_BASELINE = {  # vk tissue pages -> kb/baselines files
    "cornea": "ocular_surface", "conjunctiva": "conjunctiva", "sclera": "sclera",
    "RPE": "RPE", "choroid": "choroid", "ciliary_body": "ciliary_body",
    "iris": "iris", "lens": "lens", "optic_nerve": "optic_nerve",
    "trabecular_meshwork": "trabecular_meshwork",
}
TOPIC_HINT = {
    "dr-diabetic-retinopathy": "Disease matrix: kb/priors/disease/_DISEASE_TISSUE_MATRIX.md; "
                               "example cell: PDR__fibrovascular_membrane.md",
    "vascular": "Disease matrix PDR cell, patho_endothelial signature (signature_evidence_T4)",
    "glial-microglia": "Concept table EYEKBC-0001/0011/0012 (source-attribution cap = transcriptional similarity, Astra T4)",
    "amd": "Disease matrix nAMD/GA rows (placeholder)", "glaucoma": "Disease matrix glaucoma rows (placeholder)",
    "inherited-disease": "Disease matrix (no cell; minimum-viable bar enforced)",
    "metabolism": "signature-layer metabolic work goes through evidence_context.methods",
    "methods-scrna": "Annotation protocol ANNOTATION_PROTOCOL_v1.1.md + EVAL_Rubric_v1.md",
    "photoreceptor": "Retina baseline kb/baselines/retina.md (Rod/Cone donor-level distribution)",
    "retina-development": "Retina baseline caveat 4 (adult baselines do not apply to developmental/organoid data)",
    "regeneration": "Concept table EYEKBC-0009/0011", "rpe": "RPE baseline skeleton + retina baseline RPE-contamination flag",
    "aging": "Retina baseline (mostly elderly donor band)", "models": "sampling-material mismatch warning (example cell §)",
    "other": "", "visual-function": "",
}


def block_for(name: str) -> str:
    base = TISSUE_BASELINE.get(name)
    lines = ["", "---", MARK, f"## Interpretation-layer links ({VER})", ""]
    if base:
        lines.append(f"- **Composition baseline**: [kb/baselines/{base}.md](/mnt/D/EyeKB/kb/baselines/{base}.md)"
                     f" — donor-level conditional reference distribution (anchored to registry standard set or t_6f5cc731 mapping)")
    hint = TOPIC_HINT.get(name)
    if hint:
        lines.append(f"- **Interpretation-layer anchor**: {hint}")
    lines += [
        "- **RAG reason-tag**: per-PMID inclusion reason / claim relation / evidence conditions in "
        "`/mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.0_2026-09.jsonl` "
        "(key=pmid; fields inclusion_reasons / claim_relation / evidence_context / verification_status); "
        "auto-joined into MCP `search_literature` hits",
        "- **Concept ID mapping**: `/mnt/D/EyeKB/kb/priors/concepts.tsv`",
        "- Red line: this page and all linked content carry evidence citations and QC flags only; scoring use is forbidden (ANNOTATION_PROTOCOL_v1.1.md §0)",
        ""]
    return "\n".join(lines)


def main():
    n_new = n_skip = 0
    for p in sorted(VK.glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        if MARK in txt:
            n_skip += 1
            continue
        name = re.sub(r"^(tissue-|topic-)", "", p.stem)
        p.write_text(txt.rstrip() + "\n" + block_for(name), encoding="utf-8")
        n_new += 1
    print("vk pages linked:", n_new, "| already had links (skipped):", n_skip)


if __name__ == "__main__":
    main()
