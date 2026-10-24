# -*- coding: utf-8 -*-
"""b1_build_increment.py -- build the CL-56 naming increment (default OFF) and extend the naming map.

Writes:
  /home/ubuntu/EYEKB_REPO/kb/markers/markers_v15_cl56_increment.json   (new file)
  (edit) kb/markers/markers_cl_alignment_v2_unified.json               (additive rows only)
  out/PREIMAGE.json  pre_images/  pre-images of BOTH files before the write
  out/BUILD.json     what was written: every entry, its panel, its provenance

The scope list is NOT recomputed here: it is read from out/SCOPE.json, which s1_scope.py produced by
applying the pre-registered rule. Only pairs with adopted=true get an entry.

Run: /usr/bin/python3 b1_build_increment.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
PRE = os.path.join(WAVE, "pre_images")
REPO = "/home/ubuntu/EYEKB_REPO"
INCR = os.path.join(REPO, "kb/markers/markers_v15_cl56_increment.json")
CLMAP = os.path.join(REPO, "kb/markers/markers_cl_alignment_v2_unified.json")
CLD = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021"
SUB = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
sys.path.insert(0, "/mnt/D/EyeKB/plans/noregr_20261022/scripts")
import wave_common as W  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    scope = json.load(open(os.path.join(OUT, "SCOPE.json")))
    cand = {(c["our_labels"], c["child_cl"]): c
            for c in json.load(open(os.path.join(CLD, "out", "CHILD_TERM_CANDIDATES.json")))["candidates"]}
    adopted = [r for r in scope["rows"] if r["adopted"]]
    calls = W.load_set()
    cm_before = json.load(open(CLMAP, encoding="utf-8"))
    labels_with_cl = {}
    for lbl, v in cm_before["labels"].items():
        if v.get("cl_id"):
            labels_with_cl.setdefault(v["cl_id"], []).append(lbl)

    os.makedirs(PRE, exist_ok=True)
    # IDEMPOTENCE GUARD: once the increment exists, this script must not re-take its own pre-images
    # (that would overwrite "the state this card started from" with an already-modified file). Verified
    # against out/BUILD.json and the live bytes instead.
    if os.path.exists(INCR) and os.path.exists(os.path.join(OUT, "BUILD.json")):
        import hashlib as _h
        live = _h.sha256(open(INCR, "rb").read()).hexdigest()
        pre_rec = json.load(open(os.path.join(OUT, "PREIMAGE.json"), encoding="utf-8"))
        inc_rec = [f for f in pre_rec["files"] if f["kind"] == "increment"][0]
        map_rec = [f for f in pre_rec["files"] if f["kind"] == "labelmap"][0]
        live_map = _h.sha256(open(CLMAP, "rb").read()).hexdigest()
        print("already built: increment sha=%s (recorded %s) %s"
              % (live[:16], inc_rec.get("sha256_after", "")[:16],
                 "MATCH" if live == inc_rec.get("sha256_after") else "MISMATCH"))
        print("label map sha=%s (recorded %s) %s"
              % (live_map[:16], map_rec.get("sha256_after", "")[:16],
                 "MATCH" if live_map == map_rec.get("sha256_after") else "MISMATCH"))
        if live != inc_rec.get("sha256_after") or live_map != map_rec.get("sha256_after"):
            raise SystemExit("refusing to rebuild over an already-built tree; restore with "
                             "scripts/reset_tree.sh first")
        return
    pre = {"generated_by": "scripts/b1_build_increment.py",
           "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "files": []}
    for src, tag in ((INCR, "increment"), (CLMAP, "labelmap")):
        e = {"path": src, "kind": tag, "existed_before": os.path.exists(src)}
        if e["existed_before"]:
            dst = os.path.join(PRE, os.path.basename(src) + ".pre_cl56")
            shutil.copy2(src, dst)
            e["pre_image"] = dst
            e["sha256_before"] = sha(src)
        pre["files"].append(e)

    entries = []
    for r in adopted:
        c = cand[(r["our_label"], r["child_cl"])]
        cells = [x for x in calls if x["ref_cell_type"].strip() == r["child_label"].strip()]
        dm_tissues = sorted({(x["tissue"] or "unstated") for x in cells})
        already = labels_with_cl.get(r["child_cl"], [])
        entries.append({
            "class_name": r["child_label"],
            "cl_id": r["child_cl"],
            "cl_label": r["a_snapshot_label"],
            "cl_resolves": bool(r["a_term_present"] and not r["a_obsolete"]),
            "adoption": "child_term_adoption",
            "parent_class": r["our_label"],
            "parent_cl": r["ours_cl"],
            "tissue": dm_tissues,
            "markers": r["panel"],
            "n_markers": len(r["panel"]),
            "cl_overlap_note": ("shipped label-map rows already carrying CL:%s before this card: %s"
                                % (r["child_cl"], already or "none")),
            "why": ("the author's own label for %d recorded clusters (%d cells) is literally this term, "
                    "which is a strict is_a descendant of our `%s` (%s); the panel is the pair's "
                    "discriminating positive genes with parent-shared genes removed, so the entry names "
                    "the finer cell type without re-stating the parent's identity genes"
                    % (r["c1_demand_clusters"], r["c1_demand_cells"], r["our_label"], r["ours_cl"])),
            "evidence": {
                "scope_rule": "PREREG_ADOPT_CL56_20261022.md section 4 (a)+(b)+(c1,c2,c3)",
                "corpus_support_status": r["corpus_support_status"],
                "corpus_n_chunks": c.get("corpus_n_chunks"),
                "corpus_n_papers": c.get("corpus_n_papers"),
                "corpus_best_phrase": c.get("corpus_best_phrase"),
                "corpus_best_phrase_kind": c.get("corpus_best_phrase_kind"),
                "corpus_locator_examples": c.get("corpus_locator_examples"),
                "is_a_depth": r["a_depth"],
                "is_a_path": c.get("is_a_path"),
                "child_obo_line": c.get("child_obo_line"),
                "panel_source": "plans/subdivision_readiness_20261022/out/pair_table.json "
                                "field discriminating_genes (T-GENES: >=2 studies, parent-shared removed)",
                "removed_not_in_assay_vocab": r["c2_removed_not_in_assay_vocab"],
                "readiness_tier": r["readiness_tier"],
                "readiness_reason": r["readiness_reason"],
                "demand_clusters": r["c1_demand_clusters"],
                "demand_cells": r["c1_demand_cells"],
                "author_label_is_the_term": r["c1_author_label_is_the_term"],
                "observable_in_window": r["c3_observable_clusters"],
            },
        })

    doc = {
        "version": "v15.0-cl56-child-term-adoption-20261024",
        "created": "2026-10-24",
        "scope": ("the author-side finer Cell-Ontology terms our coarser shipped classes were scored "
                  "against: the corpus-supported child-term candidates of the CL-depth wave, restricted "
                  "by the pre-registered scope rule to the pairs that can be named at all"),
        "status": ("staging only; library `cl56_v15` is NOT merged into the default `all` set and has an "
                   "EMPTY whitelist, so the default route is byte-identical in every state. Merging it into "
                   "the default route is a separate decision taken only if the pre-registered acceptance "
                   "rule passes (see out/ACCEPTANCE.json)."),
        "registered_by": "plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md",
        "card": "t_fabddb85",
        "cl_release": "cl/releases/2026-06-08/cl-base.owl",
        "cl_ontology_file": "kb/ontology/cl/releases/2026-06-08/cl-base.obo",
        "source_corpus": ("the served in-repo literature corpus (v2.6-dev lineage); this card mines nothing "
                          "new from it - the panels are read from the pre-registered readiness wave's "
                          "discriminating-gene column"),
        "scope_tissues": sorted({t for e in entries for t in e["tissue"]}),
        "admission_rule": {
            "a_ontology": "the child term resolves in the frozen snapshot and is a strict is_a descendant "
                          "of our current class's term",
            "b_naming_support": "the held corpus states the term (the 25 supported pairs); the 31 pairs "
                                "with no corpus hit stay out and are listed as pending",
            "c_floor": ">=1 recorded cluster whose reference is the child term; >=2 discriminating positive "
                       "genes in the assay vocabulary; and >=2 of them observable in a demand cluster's "
                       "recorded window (the readiness wave's T-GENES and T-OBS floors)",
        },
        "reading_is_in_sample": ("the panels were selected and measured on the same 28 recorded volumes; a "
                                 "reading here is a harm-line/naming-agreement reading, NOT an accuracy "
                                 "claim, and an ontology-consistent name is not evidence of a better call"),
        "n_entries": len(entries),
        "markers": {e["class_name"]: e["markers"] for e in entries},
        "entries": entries,
        "pending_pairs": [{"our_label": r["our_label"], "child_cl": r["child_cl"],
                           "child_label": r["child_label"], "fails": r["fails"],
                           "corpus_support_status": r["corpus_support_status"],
                           "demand_clusters": r["c1_demand_clusters"],
                           "n_panel_genes": r["c2_n_genes"]}
                          for r in scope["rows"] if not r["adopted"]],
        "out_of_scope_no_corpus_hit": {"count": scope["n_no_corpus_hit_out_of_scope"],
                                       "reason": "the held corpus does not state these terms; adopting them "
                                                 "would be a vocabulary import with no local evidence"},
        "we_are_finer_note": ("the 8 `we_are_finer_pairs` of the predecessor wave (our term finer than the "
                              "author's) are a different question and are NOT folded into this adoption"),
    }
    os.makedirs(os.path.dirname(INCR), exist_ok=True)
    with open(INCR, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    pre["files"][0]["sha256_after"] = sha(INCR)

    # ---- the naming map: additive rows for the adopted names only -------------------------------
    cm = json.load(open(CLMAP, encoding="utf-8"))
    before_labels = len(cm["labels"])
    added = []
    for e in entries:
        nm = e["class_name"]
        if nm in cm["labels"]:
            cur = cm["labels"][nm]
            if cur.get("cl_id") != e["cl_id"]:
                raise SystemExit("REFUSING: label %r already maps to %r, adopted cl_id is %r"
                                 % (nm, cur.get("cl_id"), e["cl_id"]))
            continue
        cm["labels"][nm] = {"cl_id": e["cl_id"], "cl_label": e["cl_label"], "status": "mapped",
                            "reason": None, "qualifier": None, "libraries": ["cl56_v15"]}
        added.append(nm)
    cm["version"] = "cl-labelmap-unified-v1.2"
    note_tag = "v1.2 (2026-10-24, card t_fabddb85)"
    if note_tag not in cm.get("supersedes_note", ""):
        cm["supersedes_note"] = (cm.get("supersedes_note", "") +
                                 " | %s: added the %d adopted CL-56 child-term names so an entry of "
                                 "`cl56_v15` is mappable by the ontology ruler; additive rows only, no "
                                 "existing row edited or removed. Reason: the activation card t_be11fd4a "
                                 "measured that an entry name the map cannot resolve is graded "
                                 "`unmappable_pred` and read as an inconsistency." % (note_tag, len(added)))
    with open(CLMAP, "w", encoding="utf-8") as f:
        json.dump(cm, f, ensure_ascii=False, indent=1)
    pre["files"][1]["sha256_after"] = sha(CLMAP)
    pre["labelmap_rows_before"] = before_labels
    pre["labelmap_rows_added"] = added
    pre["labelmap_rows_after"] = len(cm["labels"])

    with open(os.path.join(OUT, "PREIMAGE.json"), "w", encoding="utf-8") as f:
        json.dump(pre, f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(OUT, "BUILD.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    print("increment written: %s  entries=%d  (%s)" % (INCR, len(entries), sha(INCR)[:16]))
    for e in entries:
        print("  %-12s %-12s %-38s genes=%2d  tissues=%s"
              % (e["parent_class"], e["cl_id"], e["class_name"][:38], e["n_markers"], e["tissue"]))
    print("labelmap: %d -> %d rows, added %s" % (before_labels, len(cm["labels"]), added))


if __name__ == "__main__":
    main()