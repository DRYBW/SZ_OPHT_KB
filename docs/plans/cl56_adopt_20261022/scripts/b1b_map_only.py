# -*- coding: utf-8 -*-
"""b1b_map_only.py -- re-apply ONLY the naming-map half of b1 (the additive CL-56 rows).

Why this exists: b1_build_increment.py re-takes its own pre-images when it runs, so re-running it to
repair the map would overwrite the recorded pre-image with an already-modified file and break the
"pre-image = the state this card started from" record. This script touches the map and nothing else,
asserts the pre-image is still the pristine file, and is idempotent (a row already present is only
checked, never rewritten).

Run: /usr/bin/python3 b1b_map_only.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
PRE = os.path.join(WAVE, "pre_images")
CLMAP = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json"
PRISTINE_SHA = "48051cdae915b82e6e7812da9b98f93b41f51c5fac14bdb370bd5ccdb969a0a1"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    pre = os.path.join(PRE, "markers_cl_alignment_v2_unified.json.pre_cl56")
    assert sha(pre) == PRISTINE_SHA, "kept pre-image is not the pristine map -- refusing to edit"
    scope = json.load(open(os.path.join(OUT, "SCOPE.json")))
    adopted = [r for r in scope["rows"] if r["adopted"]]

    cm = json.load(open(CLMAP, encoding="utf-8"))
    added, present = [], []
    for r in adopted:
        nm = r["child_label"]
        if nm in cm["labels"]:
            assert cm["labels"][nm].get("cl_id") == r["child_cl"], (
                "label %r already maps to %r, adopted cl_id is %r" % (nm, cm["labels"][nm].get("cl_id"),
                                                                      r["child_cl"]))
            present.append(nm)
            continue
        cm["labels"][nm] = {"cl_id": r["child_cl"], "cl_label": r["a_snapshot_label"],
                            "status": "mapped", "reason": None, "qualifier": None,
                            "libraries": ["cl56_v15"]}
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
    print("map rows: %d added=%s already_present=%s -> total %d rows; sha=%s"
          % (len(adopted), added, present, len(cm["labels"]), sha(CLMAP)[:16]))
    print("pristine pre-image sha verified:", PRISTINE_SHA[:16])


if __name__ == "__main__":
    main()