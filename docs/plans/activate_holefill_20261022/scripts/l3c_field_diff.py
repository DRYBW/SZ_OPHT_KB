#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3c -- field-level diff of the default-face responses, PARENT vs the activated core.

The raw-byte census in l3 answers "how many responses moved". This script answers **what** moved: for
a handful of representative queries (a rod cluster the library takes over, two clusters whose grade
falls, the optic-nerve cluster the preceding activation repaired, and a few non-ranking calls) it dumps
the full response under both cores at the same absolute path and reports the differing JSON paths.
Without this, "721/721 moved in bytes" would be an unexplained number, and the two legacy
tool-panel calls that move would be unattributed.

Writes out/FIELD_DIFF.json.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
OUT = os.path.join(WAVE, "out")
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
L6 = os.path.join(REPO, "docs", "plans", "noregr_20261022", "scripts")
sys.path.insert(0, L6)

PICKS = [("CX01_retina_snRNA", "27"),     # rod-truth cluster the library takes over (2 shared genes)
         ("CX02_adult_retina", "4"),      # rod-truth cluster whose grade falls
         ("CX04_cowan_periphery", "7"),   # rod-truth cluster whose grade falls
         ("CX15_optic_nerve_all", "31")]  # the cluster the preceding activation repaired


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(tag, tmp, arm_env):
    p = os.path.join(tmp, "dump_%s.json" % tag)
    code = r'''
import json, os, sys
sys.path.insert(0, os.environ["HF_L6"])
sys.path.insert(0, os.environ["HF_HERE"])
import wave_common as W
sys.path.insert(0, os.path.join(W.REPO, "mcp_server"))
import eyekb_core as core
calls = W.load_set()
by = {(c["vol"], c["cluster"]): c for c in calls}
picks = json.loads(os.environ["HF_PICKS"])
out = {}
for vol, cl in picks:
    c = by.get((vol, cl))
    if not c:
        continue
    kw = {"genes": list(c["genes"]), "library": "all"}
    if c["species"] in ("human", "mouse"):
        kw.update({"species": c["species"], "volume_species": c["species"],
                   "volume_id": "field_diff_probe"})
    out["cluster:" + vol + "|" + cl] = core.query_marker(**kw)
out["genes:legacy_panel_microglia"] = core.query_marker(
    genes=["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"], library="all")
out["celltype:MG"] = core.query_marker(cell_type="MG", library="all")
out["pages:list_kb_pages"] = core.list_kb_pages()
json.dump(out, open(os.environ["HF_OUT"], "w"), ensure_ascii=False, indent=1, default=str)
print("core", W.sha256_file(os.path.join(W.REPO, "mcp_server", "eyekb_core.py"))[:16],
      "keys", len(out))
'''
    e = dict(os.environ)
    for k in ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
              "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_HOLEFILL", "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD",
              "EYEKB_CL_KEY"):
        e.pop(k, None)
    e.update(arm_env)
    # pinned PYTHONPATH: only the audit-hook directory is inherited, so another venv's site-packages
    # (which the worker sandbox can export) cannot shadow the repository's dependencies
    e["PYTHONPATH"] = os.path.join(HERE, "netaudit")
    e["HF_L6"] = L6
    e["HF_HERE"] = HERE
    e["HF_OUT"] = p
    e["HF_PICKS"] = json.dumps(PICKS)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e["PYTHONHASHSEED"] = "0"
    r = subprocess.run(["/usr/bin/python3", "-c", code], capture_output=True, text=True, env=e,
                       cwd=WAVE)
    if r.returncode != 0:
        raise SystemExit("dump %s failed: %s" % (tag, r.stderr[-2000:]))
    return json.load(open(p)), r.stdout.strip()


def paths_diff(a, b, prefix=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append({"path": prefix + "/" + k,
                            "before": "<absent>" if k not in a else a[k],
                            "after": "<absent>" if k not in b else b[k],
                            "kind": "key_added" if k not in a else "key_removed"})
            else:
                out += paths_diff(a[k], b[k], prefix + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if a != b:
            out.append({"path": prefix, "before": a, "after": b, "kind": "list_changed",
                        "n_before": len(a), "n_after": len(b)})
    elif a != b:
        out.append({"path": prefix, "before": a, "after": b, "kind": "value_changed"})
    return out


def main():
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    # pinned to the commit recorded by this card's pre-image: once this card's change is committed,
    # HEAD stops being a valid reference (a comparison against it degenerates into a self-comparison
    # with an empty diff)
    ref = json.load(open(os.path.join(OUT, "PREIMAGE.json")))["base_commit"]
    parent = subprocess.run(["git", "-C", REPO, "show", "%s:mcp_server/eyekb_core.py" % ref],
                            capture_output=True, text=True).stdout.encode()
    pre = open(os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_activation"), "rb").read()
    doc = {"probe": "l3c_field_diff.py", "activated_core_sha256": cur_sha,
           "pre_flip_reference_commit": ref, "parent_core_sha256": sha(parent),
           "parent_core_equals_kept_preimage": sha(parent) == sha(pre),
           "preimage_note": ("the kept pre-image is the pre-activation state, which already carries "
                             "this card's registration restoration (out/RESTORE.json)"),
           "activation_present_in_the_tree": "_holefill_act_enabled" in cur.decode("utf-8"),
           "picks": PICKS}
    try:
        with open(CORE, "wb") as f:
            f.write(parent)
        a, loga = dump("parent", tmp, {})
        doc["parent_dump_log"] = loga
    finally:
        with open(CORE, "wb") as f:
            f.write(cur)
    b, logb = dump("flip", tmp, {})
    doc["activated_dump_log"] = logb
    doc["restored_matches_snapshot"] = sha(open(CORE, "rb").read()) == cur_sha

    per_query = {}
    for q in sorted(a):
        d = paths_diff(a[q], b[q], q)
        per_query[q] = {"n_differing_paths": len(d), "differing": d[:12]}
    shapes = {}
    for q, v in per_query.items():
        for item in v["differing"]:
            p = item["path"].split(":", 1)[-1]
            key = p.split("/")[1] if "/" in p else p
            shapes.setdefault(key, set()).add(q)
    doc["queries"] = per_query
    doc["changed_response_fields"] = {k: sorted(v) for k, v in shapes.items()}
    doc["verdict"] = "PASS" if doc["restored_matches_snapshot"] else "FAIL"
    json.dump(doc, open(os.path.join(OUT, "FIELD_DIFF.json"), "w"), ensure_ascii=False, indent=1)
    for q, v in per_query.items():
        print("%-38s differing paths=%d" % (q, v["n_differing_paths"]))
        for item in v["differing"][:4]:
            print("      %s: %s -> %s" % (item["path"], str(item.get("before"))[:80],
                                          str(item.get("after"))[:80]))
    print("changed response fields:", json.dumps(doc["changed_response_fields"], indent=1)[:900])
    print("l3c verdict:", doc["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())