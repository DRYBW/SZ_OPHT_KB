#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m6 -- build the candidate library (kb/markers/markers_v14_subtype_second_increment.json).

One entry per in-scope subtype that has at least one admitted candidate.  Each entry:

  * is NAMED by the Cell Ontology label of the term it carries, resolved against the frozen snapshot
    `kb/ontology/cl/releases/2026-06-08/cl-base.obo` (the CL id is the one the frozen 94-entry list
    already verified as resolvable);
  * carries the frozen panel genes AND the admitted candidates, with the two groups kept separate so
    the library can never be read as if the added genes replaced the frozen ones;
  * carries, per added gene, its literature evidence (paper ids + the segment) and its per-volume
    measurability, so nothing in the file is a bare symbol.

The library is REGISTERED DEFAULT OFF with an EMPTY whitelist (registration is m7): it is reachable
only by naming it, and no switch can merge it into the default route.

Writes the repo file, a byte-identical copy under the wave dir, and out/SUBTYPE_SECOND_MARKER_PANEL.json.
"""
import hashlib
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
REPO = "/home/ubuntu/EYEKB_REPO"
OBO = os.path.join(REPO, "kb", "ontology", "cl", "releases", "2026-06-08", "cl-base.obo")
LIB = os.path.join(REPO, "kb", "markers", "markers_v14_subtype_second_increment.json")
LIB_NAME = "subtype_v14"


def load_obo():
    terms, cur = {}, None
    for line in open(OBO, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = {}
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if k == "id":
            cur["id"] = v
            terms[v] = cur
        elif k == "name":
            cur["name"] = v
        elif k == "is_obsolete":
            cur["obsolete"] = (v == "true")
    return {k: v for k, v in terms.items() if not v.get("obsolete")}


def main():
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    meas = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.json"),
                          encoding="utf-8"))
    obs = json.load(open(os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json"), encoding="utf-8"))
    flips = json.load(open(os.path.join(OUT, "FLIPS.json"), encoding="utf-8"))["flips"]
    rob = json.load(open(os.path.join(OUT, "ROBUSTNESS.json"), encoding="utf-8"))
    terms = load_obo()

    meta = {r["subtype"]: r for r in obs}
    scope = sorted({r["subtype"] for r in json.load(
        open(os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json"), encoding="utf-8"))
        if r["result"] == "not_separated"
        and str(r.get("reason", "")).startswith("1 marker(s) cleared the gate")})
    kept = defaultdict(list)
    admitted_all = defaultdict(list)
    for r in lit["rows"]:
        if r["admitted"]:
            admitted_all[r["subtype"]].append(r)
        if r["kept_l5"]:
            kept[r["subtype"]].append(r)
    flip_by_sub = defaultdict(list)
    for f in flips:
        flip_by_sub[f["subtype"]].append(f)
    rob_by_key = {(r["volume"], r["subtype"]): r for r in rob["rows"]}

    entries, panel_rows = [], []
    for s in scope:
        m = meta[s]
        cl_id = m.get("subtype_cl_id")
        cl_name = terms.get(cl_id, {}).get("name") if cl_id else None
        cl_resolves = bool(cl_name)
        frozen = list(m.get("_markers_all") or [])
        added = [r["gene"] for r in kept.get(s, [])]
        meas_block = {}
        for vol, d in meas["volumes"].items():
            meas_block[vol] = {g: (d.get("genes") or {}).get(g) for g in added}
        entries.append({
            "class_name": cl_name or s,
            "cl_id": cl_id,
            "cl_label": cl_name,
            "cl_resolves": cl_resolves,
            "our_alias_for_the_literature_subtype": s,
            "parent_type": m.get("parent"),
            "consensus_level": m.get("consensus_level"),
            "tissue": ["retina"],
            "markers": frozen + added,
            "markers_frozen_panel": frozen,
            "markers_added_by_this_wave": added,
            "added_evidence": [{"gene": r["gene"], "papers": r["channel_a_papers"] + r["channel_c_sources"],
                                "channel_b_sources": r["channel_b_sources"],
                                "papers_total": r["papers_total"],
                                "l1_strict_papers_ge2": r["l1_strict_papers_ge2"],
                                "segments": [x.get("segment") or x.get("clause") or x.get("snippet")
                                             for x in r["snippets"]]} for r in kept.get(s, [])],
            "measurability": meas_block,
            "l4_pan_family_rejections": [{"gene": r["gene"], "subtypes_l1_passing": r["subtypes_l1_passing"]}
                                         for r in lit["rows"]
                                         if r["subtype"] == s and r["L1_lit"] and r["L2_assay_vocab"]
                                         and r["L3_not_duplicate"] and not r["L4_not_pan_family"]],
        })
        panel_rows.append({"subtype": s, "cl_id": cl_id, "cl_resolves": cl_resolves,
                           "n_frozen": len(frozen), "frozen": frozen, "added": added,
                           "n_admitted_before_cap": len(admitted_all.get(s, [])),
                           "admitted_all": [r["gene"] for r in admitted_all.get(s, [])],
                           "rows_in_scope": len([f for f in flip_by_sub[s]]),
                           "flips": [{"volume": f["volume"], "verdict": f["verdict"],
                                      "clearing_added": f["clearing_added"],
                                      "robust": rob_by_key.get((f["volume"], s), {}).get("verdict")}
                                     for f in flip_by_sub[s]]})

    doc = {
        "version": "v14.0-subtype-second-marker-20261022",
        "created": "2026-10-22",
        "scope": "the 26 subtype-by-volume rows of the frozen consensus wave whose panel is one gene "
                 "thick (exactly one marker clears the pre-registered gate and no second one does), "
                 "across 16 literature-consensus retinal subtypes and 7 volumes",
        "status": "staging only; library `%s` is NOT merged into the default `all` set and has an EMPTY "
                  "whitelist, so the default route is byte-identical in every state.  Activating a "
                  "default face is a separate PI decision and is not made here." % LIB_NAME,
        "registered_by": "plans/subtype_second_marker_20261022/PREREG_SUBTYPE_SECOND_MARKER_20261022.md "
                         "(+ AMENDMENT 1-4)",
        "card": "t_7509a1a2",
        "cl_release": "cl/releases/2026-06-08/cl-base.owl",
        "cl_ontology_file": "kb/ontology/cl/releases/2026-06-08/cl-base.obo",
        "source_corpus": "the served in-repo literature corpus (v2.6-dev lineage) indexed at build time; "
                         "corpus path is not distributed",
        "scope_tissues": ["retina"],
        "species_scope": "human (the volumes are human adult retina)",
        "admission_rule": {
            "channels": "A = literature corpus segment co-mention; B = the sources the frozen wave "
                        "already fetched (what_it_supports clauses); C = the textbook layer",
            "attachment": "segment-level structural: the segment must carry a marker predicate and name "
                          "exactly one in-scope subtype (see AMENDMENT 4); no proximity constant",
            "L1": ">= 1 attached statement (paper count recorded; a stricter papers >= 2 reading is "
                  "recorded per gene)",
            "L2": "the symbol is in the assay gene vocabulary (42,267 symbols)",
            "L3": "not already one of the subtype's frozen defining markers",
            "L4": "a symbol attached to >= 3 in-scope subtypes is rejected for all of them",
            "L5": "cap K = 2 per subtype, ranked by paper count then channel-B then symbol",
            "measurability": "in a given volume: present in var/_index and detected (>0) in >= 5 % of "
                             "that volume's cells; unmeasurable genes are recorded, not claimed",
        },
        "reading_is_in_sample": "the panel was selected and measured on the same seven volumes; a flip "
                                "shows that a literature-sourced second marker exists and is measurable, "
                                "and is NOT an accuracy claim about the annotator",
        "evidence": {
            "prereg": "PREREG_SUBTYPE_SECOND_MARKER_20261022.md",
            "amendments": ["AMENDMENT_1_ATTACHMENT_RULE_20261022.md",
                           "AMENDMENT_2_ATTACHMENT_UNIT_20261022.md",
                           "AMENDMENT_3_PREDICATE_LIST_20261022.md",
                           "AMENDMENT_4_NO_PROXIMITY_CONSTANT_20261022.md"],
            "report": "REPORT.md",
            "flips": "out/FLIPS.json", "robustness": "out/ROBUSTNESS.json",
            "ruler_patch": "out/RULER_PATCH.json",
        },
        "entries": entries,
    }
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    with open(LIB, "w", encoding="utf-8") as f:
        f.write(body)
    mirror = os.path.join(WAVE, "out", os.path.basename(LIB))
    with open(mirror, "w", encoding="utf-8") as f:
        f.write(body)
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    json.dump({"probe": "m6_build_panel.py", "library": LIB_NAME, "path": LIB,
               "sha256": sha, "bytes": len(body.encode("utf-8")),
               "n_entries": len(entries), "n_entries_with_added": sum(1 for e in entries if e["markers_added_by_this_wave"]),
               "panel_rows": panel_rows},
              open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_PANEL.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    unresolved = [e["cl_id"] for e in entries if not e["cl_resolves"]]
    print("library %s: %d entries, %d carry added genes, sha256=%s bytes=%d"
          % (LIB_NAME, len(entries), sum(1 for e in entries if e["markers_added_by_this_wave"]),
             sha[:16], len(body.encode("utf-8"))))
    print("CL ids that do NOT resolve against the frozen snapshot:", unresolved)
    for e in entries:
        print("  %-34s %-12s frozen=%-2d added=%s"
              % ((e["cl_label"] or "?")[:34], e["cl_id"], len(e["markers_frozen_panel"]),
                 e["markers_added_by_this_wave"]))
    assert not unresolved, "a class name must resolve against the frozen ontology snapshot"
    return 0


if __name__ == "__main__":
    sys.exit(main())