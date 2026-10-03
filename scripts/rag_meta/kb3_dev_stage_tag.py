#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W4: RAG paper-level dev_stage label sidecar (additive; chunk level not done this round).

Input: /mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.2_2026-09.jsonl (3,696 paper rows, with titles)
Output: /mnt/D/EyeKB/kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl
      -- new file (v2.2 sidecar itself untouched, OcularKB library untouched);
      plans/kb3_evidence/REVIEW_SHEET_devstage.tsv (manual spot-check of 30 papers, with audit trail)
Scope:
  - three values to start: adult / fetal_developing / unknown (task brief W4); mixed signals
    (both sides hit) -> unknown + conflict flag; fabricating a mixed value is forbidden.
  - rule = title regex (vocabulary below, all in the file header for provenance); spot-check =
    stratified random 30 papers manually judged ok/mismatch; mismatches are reassigned and
    recorded (matched_terms keeps the original value, the final fields override).
  - chunk-level development_stage explicitly out of scope -> deferred to v2.3+ corpus iteration
    (task brief: "not this round, state it").
Usage: python3 kb3_dev_stage_tag.py            # full tagging + emit review sheet
      python3 kb3_dev_stage_tag.py --apply-review  # rebuild final sidecar after manual review
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

SRC = Path("/mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.2_2026-09.jsonl")
OUT = Path("/mnt/D/EyeKB/kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl")
REV = Path("/mnt/D/EyeKB/plans/kb3_evidence/REVIEW_SHEET_devstage.tsv")
ABSTRACTS = Path("/mnt/D/EyeKB/plans/kb3_evidence/abstract_dev_stage_hits_20260924.json")
CARD = "t_5425a7ca"

FETAL_RE = re.compile(
    r"\b(fetal|foetal|embryon\w*|embryo\w*|prenatal|gestational|postnat\w*|neonat\w*|"
    r"infant\w*|juvenile|pediatric|paediatric|developing|organoids?\b|hESC|iPSC|"
    r"pluripotent stem cell\w*|retinal progenitor|time.?course of (retinal )?development|"
    r"in vitro (retinal )?differentiation)\b"
    # v1.1 (corrections from manual review of 30 papers, see REVIEW_SHEET_devstage.tsv #23): developmental-noun collocations.
    # Only accept tissue+development collocations, never bare development (avoids 'drug development' methodology false hits).
    r"|\b(ocular|retinal|retina|eye|corneal|cornea|lens|neural retina|visual system)\s+"
    r"development(?! of \w*(?:drug|therap|marker|method|tool|pipeline|model system))", re.I)
ADULT_RE = re.compile(
    r"\b(adult\w*|aged|aging|age-?related|senile|geriatric|mature\w*\s+(donor|eye|retina)|"
    r"(older|elderly)\s+adult\w*)\b", re.I)
# adult vocabulary note: bare "mature" is highly ambiguous (mature splicing); only mature+noun collocations accepted; AMD-type disease terms do not count as adult
# (age-related disease literature is mostly adult, but titles lacking the word "adult" are treated as unknown, conservative).


def tag(title, ab=None):
    """v1.2 merge: title signal takes priority; if the title has no signal, fall back to the abstract
    (only one side hits -> that side + abs_only flag; both sides / neither -> unknown).
    Title and abstract hitting opposite sides is mutually exclusive -> conflict -> unknown."""
    f, a = FETAL_RE.findall(title), ADULT_RE.findall(title)
    tf = bool(f)
    ta = bool(a)
    af = aa = False
    if ab:
        af, aa = bool(ab.get("fetal_hits")), bool(ab.get("adult_hits"))
    terms = {"fetal": f, "adult": [x if isinstance(x, str) else x[0] for x in a]}
    if tf and ta:
        return "unknown", {**terms, "conflict": "title_both"}
    if tf and aa and not af:      # title developmental vs abstract adult -> conflict, conservative
        return "unknown", {**terms, "conflict": "title_fetal_abstract_adult"}
    if ta and af and not aa:      # title adult vs abstract developmental -> conflict, conservative
        return "unknown", {**terms, "conflict": "title_adult_abstract_fetal"}
    if tf:
        return "fetal_developing", terms
    if ta:
        return "adult", terms
    # no title signal -> abstract layer
    if ab:
        terms["abstract"] = {"fetal": ab.get("fetal_hits", []),
                             "adult": ab.get("adult_hits", [])}
        if af and aa:
            return "unknown", {**terms, "conflict": "abstract_both"}
        if af:
            return "fetal_developing", {**terms, "abs_only": 1}
        if aa:
            return "adult", {**terms, "abs_only": 1}
    return "unknown", terms


def load_papers():
    rows = []
    for ln in SRC.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        d = json.loads(ln)
        if "paper_id" in d:
            rows.append(d)
    return rows


def build(apply_review=False):
    papers = load_papers()
    review_map = {}
    if apply_review and REV.is_file():
        with open(REV, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("manual_call") in ("adult", "fetal_developing", "unknown"):
                    review_map[r["paper_id"]] = r["manual_call"]
    head = {"schema": "eyekb-dev-stage-meta/1.0", "generated": "2026-09-24",
            "card": CARD, "source_db": "v2.2_2026-09 (OcularKB, read-only) ← titles via "
                                        "evidence_meta_v2.2 sidecar (EyeKB)",
            "method": "title+abstract regex v1.2 (vocabulary single source of truth = "
                      "scripts/rag_meta/kb3_dev_stage_tag.py; abstract hit material = "
                      "plans/kb3_evidence/abstract_dev_stage_hits_20260924.json, "
                      "merge = title priority / mutually exclusive conflicts conservatively unknown / abs_only flag) + "
                      "manual spot-check of 30 papers (REVIEW_SHEET_devstage.tsv)",
            "values": ["adult", "fetal_developing", "unknown"],
            "scope_note": "paper-level labels; **chunk-level development_stage not done this round**, deferred to v2.3+ "
                          "corpus iteration (KB3 task brief W4). Both sides hitting = unknown + conflict flag; fabricating a mixed value is forbidden."}
    ab_hits = {}
    if ABSTRACTS.is_file():
        ab_hits = json.loads(ABSTRACTS.read_text(encoding="utf-8")).get("hits", {})
    out, stats = [head], {"adult": 0, "fetal_developing": 0, "unknown": 0, "conflict": 0,
                          "manual_overridden": 0, "abs_only": 0}
    tagged = []
    for d in papers:
        dev, terms = tag(d.get("title", ""), ab_hits.get(str(d["paper_id"])))
        row = {"paper_id": d["paper_id"], "pmid": d.get("pmid", d["paper_id"]),
               "title": d.get("title", ""), "year": d.get("year"),
               "dev_stage": dev, "matched_terms": terms,
               "dev_stage_final": dev, "manual_check": None}
        if terms.get("conflict"):
            stats["conflict"] += 1
        if terms.get("abs_only"):
            stats["abs_only"] += 1
        tagged.append(row)
    # spot-check 30: 10 per class, top up with unknown if short; deterministic seed=20260924
    rng = random.Random(20260924)
    sample = []
    for v in ("adult", "fetal_developing", "unknown"):
        pool = [r for r in tagged if r["dev_stage"] == v]
        sample += rng.sample(pool, min(10, len(pool)))
    ids = {r["paper_id"] for r in sample}
    for r in tagged:
        if apply_review and r["paper_id"] in review_map:
            r["dev_stage_final"] = review_map[r["paper_id"]]
            r["manual_check"] = "sample30:reviewed"
            if r["dev_stage_final"] != r["dev_stage"]:
                r["manual_check"] = "sample30:mismatch->reassigned"
                stats["manual_overridden"] += 1
        stats[r["dev_stage_final"]] += 1
        out.append(r)
    OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n",
                   encoding="utf-8")
    if not apply_review:  # first pass: emit the pending-manual sheet (judgment columns left blank)
        with open(REV, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["paper_id", "auto_call", "matched", "title", "manual_call", "note"])
            for r in sample:
                w.writerow([r["paper_id"], r["dev_stage"],
                            json.dumps(r["matched_terms"], ensure_ascii=False),
                            r["title"], "", ""])
    print(json.dumps(stats, ensure_ascii=False), "| papers:", len(tagged),
          "| sample:", len(sample), "| mode:", "apply-review" if apply_review else "tag+sheet")


if __name__ == "__main__":
    build(apply_review="--apply-review" in sys.argv)
