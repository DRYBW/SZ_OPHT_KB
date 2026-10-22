#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m9 -- the default-face red line: this card's change, isolated and measured.

What is compared
----------------
Two cores, **both imported in one process and both living inside the live `mcp_server/` directory**
so that every path-derived value (`MARKER_DIR`, the library paths, any path echoed in a response) is
identical and the only variable is the file's bytes:

  A = the parent commit's `mcp_server/eyekb_core.py` (`git show HEAD:...`)
  B = A + this card's four registration edits (m7's anchors, applied to A)

Neither contains another card's in-flight edit: the shared working tree carried a concurrent card's
activation at measurement time (recorded in the artefact), and absorbing it would corrupt both cards'
evidence.  This comparison therefore isolates **this** card's delta, which is the claim being made.

What is replayed
----------------
* the recorded 721-cluster set (genes mode, `library="all"`, no `tissue` argument -- the shipped
  DEFAULT route), canonicalised per call;
* the default-route battery: page listing + `cell_type` mode for every labelled class x three species
  arguments;
* plus explicit route-composition checks: the `all` name list is identical, `subtype_v14` is present
  in B's `MARKER_LIBS` and reachable **by name only**, absent from A, and B's `all` route does not
  contain it in any switch state.

Temporary probe modules are written inside the live `mcp_server/` directory and removed in a
`finally`; their absence is verified afterwards.

Writes out/DEFAULT_FACE.json and out/COMMITTED_eyekb_core.py (the blob to commit).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/scripts")
import m7_register_library as M7  # noqa: E402  (anchor constants only; main() is guarded)

REPO = "/home/ubuntu/EYEKB_REPO"
CORE_REL = "mcp_server/eyekb_core.py"
CORE = os.path.join(REPO, CORE_REL)
NOREGR = os.path.join(REPO, "docs", "plans", "noregr_20261022", "scripts")
PROBE_A = os.path.join(REPO, "mcp_server", "_probe_core_A.py")
PROBE_B = os.path.join(REPO, "mcp_server", "_probe_core_B.py")


def apply_edits(text):
    for old, new in ((M7.ANCHOR_LIBS, M7.NEW_LIBS), (M7.ANCHOR_PRED, M7.NEW_PRED),
                     (M7.ANCHOR_LOAD, M7.NEW_LOAD), (M7.ANCHOR_ERR, M7.NEW_ERR)):
        n = text.count(old)
        assert n == 1, "anchor occurs %d times in the parent blob: %r" % (n, old[:70])
        text = text.replace(old, new)
    return text


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(resp):
    return hashlib.md5(json.dumps(resp, sort_keys=True, ensure_ascii=False,
                                  default=str).encode("utf-8")).hexdigest()


def load_mod(path, name, extra_path):
    for p in extra_path:
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    parent = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + CORE_REL],
                            capture_output=True, check=True).stdout
    mine = apply_edits(parent.decode("utf-8")).encode("utf-8")
    with open(os.path.join(OUT, "COMMITTED_eyekb_core.py"), "wb") as f:
        f.write(mine)
    doc = {"probe": "m9_default_face.py", "core_path": CORE_REL,
           "parent_commit": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                           capture_output=True, text=True).stdout.strip(),
           "parent_blob_sha256": sha(parent), "committed_blob_sha256": sha(mine),
           "parent_bytes": len(parent), "committed_bytes": len(mine),
           "n_diff_lines": sum(1 for a, b in zip(parent.split(b"\n"), mine.split(b"\n")) if a != b)
           + abs(len(parent.split(b"\n")) - len(mine.split(b"\n"))),
           "working_tree_carried_a_concurrent_edit":
               sha(open(CORE, "rb").read()) != sha(parent),
           "working_tree_sha256_at_measurement": sha(open(CORE, "rb").read()),
           "concurrent_card": "t_be11fd4a (docs/plans/activate_holefill_20261022/, in-flight in the "
                              "same working tree; its core edits are NOT part of this commit)",
           "preimage_of_the_working_tree_before_this_card":
               "out/PREIMAGE_eyekb_core.py.bak_pre_subtype2m"}

    try:
        open(PROBE_A, "wb").write(parent)
        open(PROBE_B, "wb").write(mine)
        extra = [os.path.join(REPO, "mcp_server"), NOREGR]
        import wave_common as W
        calls = W.load_set()
        doc["recorded_set"] = {"n_clusters": len(calls)}
        switch_names = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
                        "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_HOLEFILL", "EYEKB_ACT_SUBTYPE",
                        "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE",
                        "EYEKB_FALLBACK_WIDEN", "EYEKB_FALLBACK_WIDEN_DENY_TISSUES", "EYEKB_CL_KEY")
        saved = {k: os.environ.pop(k, None) for k in switch_names}

        def replay(mod):
            hashes = {}
            for c in calls:
                kw = {"genes": list(c["genes"]), "library": "all"}
                if c["species"] in ("human", "mouse"):
                    kw.update({"species": c["species"], "volume_species": c["species"],
                               "volume_id": "subtype2m_face_probe"})
                hashes["%s|%s" % (c["vol"], c["cluster"])] = canon(mod.query_marker(**kw))
            labels = sorted(json.load(open(os.path.join(REPO, "kb", "markers",
                                                        "markers_cl_alignment_v2_unified.json"),
                                            encoding="utf-8"))["labels"].keys())
            hashes["list_kb_pages"] = canon(mod.list_kb_pages())
            for lab in labels:
                for sp in ("human", "mouse", None):
                    kw = {"cell_type": lab, "library": "all"}
                    if sp:
                        kw.update({"species": sp, "volume_species": sp,
                                   "volume_id": "subtype2m_face_probe"})
                    try:
                        r = mod.query_marker(**kw)
                    except Exception as e:
                        r = {"__error__": "%s: %s" % (type(e).__name__, e)}
                    hashes["cls:%s:%s" % (lab, sp)] = canon(r)
            return hashes

        A = load_mod(PROBE_A, "probe_core_A", extra)
        routeA = [(n, str(p), sha(open(p, "rb").read()) if os.path.exists(p) else None)
                  for n, p, d in A._load_marker_dbs("all")]
        try:
            A._load_marker_dbs("subtype_v14")
            a_reach = "reachable"
        except Exception as e:
            a_reach = "%s: %s" % (type(e).__name__, str(e)[:90])
        hA = replay(A)

        for m in [k for k in list(sys.modules) if k.startswith("probe_core_")]:
            del sys.modules[m]
        B = load_mod(PROBE_B, "probe_core_B", extra)
        routeB = [(n, str(p), sha(open(p, "rb").read()) if os.path.exists(p) else None)
                  for n, p, d in B._load_marker_dbs("all")]
        b_reach = "reachable" if B._load_marker_dbs("subtype_v14") else "empty"
        hB = replay(B)

        diff = [k for k in hA if hA[k] != hB.get(k)]
        doc["arms"] = {
            "n_calls_per_arm": len(hA),
            "combined_md5_parent": hashlib.md5(json.dumps(hA, sort_keys=True).encode()).hexdigest(),
            "combined_md5_committed": hashlib.md5(json.dumps(hB, sort_keys=True).encode()).hexdigest(),
            "n_differing_calls": len(diff), "differing_calls": diff[:20]}
        doc["route_composition_identical"] = routeA == routeB
        doc["route_all_names"] = [n for n, _, _ in routeA]
        doc["subtype_v14"] = {"in_parent_MARKER_LIBS": "subtype_v14" in A.MARKER_LIBS,
                             "in_committed_MARKER_LIBS": "subtype_v14" in B.MARKER_LIBS,
                             "reachable_by_name_in_parent": a_reach,
                             "reachable_by_name_in_committed": b_reach,
                             "in_all_route_any_state":
                                 any(n == "subtype_v14" for n, _, _ in routeB)}
        os.environ["EYEKB_ACT_SUBTYPE"] = "1"
        for m in [k for k in list(sys.modules) if k.startswith("probe_core_")]:
            del sys.modules[m]
        B2 = load_mod(PROBE_B, "probe_core_B", extra)
        doc["subtype_v14"]["in_all_route_with_switch_on"] = any(
            n == "subtype_v14" for n, _, _ in B2._load_marker_dbs("all"))
        doc["whitelist_is_empty"] = (list(B2.SUBTYPE_DEFAULT_LIBS) == [])
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
        ok = (doc["arms"]["n_differing_calls"] == 0 and doc["route_composition_identical"]
              and not doc["subtype_v14"]["in_all_route_any_state"]
              and not doc["subtype_v14"]["in_all_route_with_switch_on"]
              and doc["subtype_v14"]["in_committed_MARKER_LIBS"]
              and "ValueError" in str(doc["subtype_v14"]["reachable_by_name_in_parent"]))
        doc["verdict"] = "PASS" if ok else "FAIL"
    finally:
        for p in (PROBE_A, PROBE_B):
            if os.path.exists(p):
                os.remove(p)
        doc["probe_modules_removed"] = not os.path.exists(PROBE_A) and not os.path.exists(PROBE_B)

    json.dump(doc, open(os.path.join(OUT, "DEFAULT_FACE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("default-face: %d calls/arm, differing=%d, route identical=%s"
          % (doc["arms"]["n_calls_per_arm"], doc["arms"]["n_differing_calls"],
             doc["route_composition_identical"]))
    print("  parent md5=%s  committed md5=%s"
          % (doc["arms"]["combined_md5_parent"], doc["arms"]["combined_md5_committed"]))
    print("  subtype_v14 by name: parent=%s committed=%s ; in `all` any state=%s (switch on=%s)"
          % (doc["subtype_v14"]["reachable_by_name_in_parent"][:40],
             doc["subtype_v14"]["reachable_by_name_in_committed"],
             doc["subtype_v14"]["in_all_route_any_state"],
             doc["subtype_v14"]["in_all_route_with_switch_on"]))
    print("  probe modules removed:", doc["probe_modules_removed"], " verdict:", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())