# -*- coding: utf-8 -*-
"""d2_field_diff.py -- field-level attribution of the two moved tool-panel calls.
Reads out/DUMP_435bb92.json vs out/DUMP_HEAD.json, diffs the two moved calls' response
JSONs field by field, and writes out/D2_FIELD_DIFF.json. Read-only otherwise."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
a = json.load(open(os.path.join(OUT, "DUMP_435bb92.json"), encoding="utf-8"))
b = json.load(open(os.path.join(OUT, "DUMP_HEAD.json"), encoding="utf-8"))
moved = [k for k in a["responses"] if a["responses"][k] != b["responses"][k]]
res = {"probe": "d2_field_diff.py", "n_calls_compared": len(a["responses"]),
       "n_differing": len(moved), "calls": {}}
for k in sorted(moved):
    ta, tb = a["responses"][k], b["responses"][k]
    try:
        ja = json.loads(ta)
        jb = json.loads(tb)
    except Exception as e:
        res["calls"][k] = {"parse_error": str(e), "len_435": len(ta), "len_head": len(tb)}
        continue
    keys = sorted(set(ja) | set(jb))
    fields = {}
    for f in keys:
        va, vb = ja.get(f, "<ABSENT>"), jb.get(f, "<ABSENT>")
        if va == vb:
            fields[f] = "same"
        else:
            entry = {"435bb92": va, "HEAD": vb}
            if isinstance(va, str) and isinstance(vb, str):
                entry["note"] = "both strings; common_prefix_len=%d" % len(os.path.commonprefix([va, vb]))
            fields[f] = entry
    res["calls"][k] = {"n_keys": len(keys), "fields": fields}
    # semantic surface check: the ranking / markers content, abstracted from bytes
    sem = {}
    for tag, j in (("435bb92", ja), ("HEAD", jb)):
        sem[tag] = {
            "mode": j.get("mode"), "found": j.get("found"),
            "markers_keys": sorted((j.get("markers") or {}).keys()) if isinstance(j.get("markers"), dict) else None,
            "cell_types": (j.get("cell_types") or []) if isinstance(j.get("cell_types"), list) else None,
            "celltype_ranking": [r.get("cell_type") for r in (j.get("celltype_ranking") or [])],
            "n_shared_first": ((j.get("celltype_ranking") or [{}])[0]).get("n_shared"),
            "matched_by": j.get("matched_by"),
        }
    res["calls"][k]["semantic_summary"] = sem
with open(os.path.join(OUT, "D2_FIELD_DIFF.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:6000])
