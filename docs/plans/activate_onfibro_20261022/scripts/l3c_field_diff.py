#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3c -- field-level diff of the default-face responses, PARENT vs FLIP.

The raw-byte census in l3 answers "how many responses moved". This script answers **what** moved:
for a handful of representative queries (a cluster whose ranking did not move, the motivating
cluster, and a few non-ranking calls) it dumps the full response under both cores at the same
absolute path and prints the differing JSON paths. Without this, "721/721 moved" would be an
unexplained number.

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
import wave_common as W          # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(tag, tmp, arm_env):
    p = os.path.join(tmp, "dump_%s.json" % tag)
    # the child code is passed verbatim and reads its paths from the environment, so no format
    # placeholders can collide with the code's own %-formatting
    code = r'''
import json, os, sys
sys.path.insert(0, os.environ["ONF_L6"])
sys.path.insert(0, os.environ["ONF_HERE"])
import wave_common as W
sys.path.insert(0, os.path.join(W.REPO, "mcp_server"))
import eyekb_core as core
calls = W.load_set()
by = {(c["vol"], c["cluster"]): c for c in calls}
picks = [("CX01_retina_snRNA", "0"), ("CX15_optic_nerve_all", "31"),
         ("CX08_RPE_choroid_scRNA", "0")]
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
out["celltype:Fibroblast"] = core.query_marker(cell_type="Fibroblast", library="all")
out["celltype:MG"] = core.query_marker(cell_type="MG", library="all")
out["pages:list_kb_pages"] = core.list_kb_pages()
json.dump(out, open(os.environ["ONF_OUT"], "w"), ensure_ascii=False, indent=1, default=str)
print("core", W.sha256_file(os.path.join(W.REPO, "mcp_server", "eyekb_core.py"))[:16],
      "keys", len(out))
'''
    e = dict(os.environ)
    for k in ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
              "EYEKB_ACT_ONFIBRO", "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD", "EYEKB_CL_KEY"):
        e.pop(k, None)
    e.update(arm_env)
    # pinned PYTHONPATH: only the audit-hook directory is inherited, so another venv's
    # site-packages (which the worker sandbox exports) cannot shadow the repository's dependencies
    e["PYTHONPATH"] = os.path.join(HERE, "netaudit")
    e["ONF_L6"] = L6
    e["ONF_HERE"] = HERE
    e["ONF_OUT"] = p
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
                out.append({"path": prefix + "/" + k, "before": "<absent>" if k not in a else a[k],
                            "after": "<absent>" if k not in b else b[k],
                            "kind": "key_added" if k not in a else "key_removed"})
            else:
                out += paths_diff(a[k], b[k], prefix + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if a != b:
            out.append({"path": prefix, "before": a, "after": b,
                        "kind": "list_changed", "n_before": len(a), "n_after": len(b)})
    elif a != b:
        out.append({"path": prefix, "before": a, "after": b, "kind": "value_changed"})
    return out


def main():
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    parent = subprocess.run(["git", "-C", REPO, "show", "HEAD:mcp_server/eyekb_core.py"],
                            capture_output=True, text=True).stdout.encode()
    doc = {"probe": "l3c_field_diff.py", "flipped_core_sha256": cur_sha,
           "parent_core_sha256": sha(parent)}
    try:
        with open(CORE, "wb") as f:
            f.write(parent)
        a, loga = dump("parent", tmp, {})
        doc["parent_dump_log"] = loga
    finally:
        with open(CORE, "wb") as f:
            f.write(cur)
    b, logb = dump("flip", tmp, {})
    doc["flip_dump_log"] = logb
    doc["restored_matches_snapshot"] = sha(open(CORE, "rb").read()) == cur_sha

    per_query = {}
    for q in sorted(a):
        d = paths_diff(a[q], b[q], q)
        per_query[q] = {"n_differing_paths": len(d), "differing": d[:12]}
    # which JSON paths moved, summed over the sample (the shape of the delta)
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
        print("%-34s differing paths=%d" % (q, v["n_differing_paths"]))
        for item in v["differing"][:6]:
            print("      %s: %s -> %s" % (item["path"], str(item.get("before"))[:90],
                                          str(item.get("after"))[:90]))
    print("changed response fields:", json.dumps(doc["changed_response_fields"], indent=1)[:1200])
    print("l3c verdict:", doc["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())