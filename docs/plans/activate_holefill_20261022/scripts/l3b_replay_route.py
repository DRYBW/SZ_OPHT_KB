#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3b -- child replay of the DEFAULT route, recording raw and canonical response bytes per query.

Run as a separate process, with the core bytes under test already in place at their absolute path
(the parent script swaps the file, so "which code answered" is a property of the process, not of an
import order inside one run).

argv: <fmode> <out.json>
  fmode = "clusters"  -> the 721 recorded cluster gene windows (genes mode, NO tissue argument)
  fmode = "battery"   -> the default-route battery: page listing + cell_type mode for every label
                         x three species arguments
  fmode = "explicit"  -> the EXPLICIT-route battery: every named library in MARKER_LIBS, so that a
                         registration line that is missing from the loader is visible as a refusal
                         (`__error__` row) rather than as silence.  Added by card t_be11fd4a after it
                         found that `library="holefill_v12"` was unresolvable while registry row L1-26
                         claimed otherwise.

Two byte readings per query, both reported:
  raw_md5   md5 of `json.dumps(resp)`, field order as the service builds it -- the response bytes;
  canon_md5 md5 of `json.dumps(resp, sort_keys=True)`, the predecessor wave's reading, so this
            card's numbers are comparable with the numbers that wave recorded.
Plus, for the clusters arm, the answer itself (top-1, n_shared, candidate count, whether the
library's entry is present), so every moved query can be attributed rather than counted.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L6 = "/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/scripts"
sys.path.insert(0, L6)
sys.path.insert(0, HERE)
import wave_common as W          # noqa: E402  (frozen inputs + recorded set, reused)

LIB_TOP_PREFIX = "holefill_v12::"
LIB_BASENAME = "markers_v12_holefill_increment.json"
EXPLICIT_LIBS = ("retina", "membrane", "retina_interneuron", "retina_v6", "face_v6", "lacrimal_v6",
                 "k9_ocs", "retina_v7", "retina_dev", "antseg_v10", "lensiris_v11", "holefill_v12",
                 "onfibro_v13")


def raw(resp):
    return hashlib.md5(json.dumps(resp, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def canon(resp):
    return hashlib.md5(json.dumps(resp, sort_keys=True, ensure_ascii=False,
                                  default=str).encode("utf-8")).hexdigest()


def main():
    fmode, out = sys.argv[1], sys.argv[2]
    sys.path.insert(0, os.environ.get("ONF_CORE_DIR", os.path.join(W.REPO, "mcp_server")))
    import eyekb_core as core
    rows = {}
    if fmode == "clusters":
        for c in W.load_set():
            kw = {"genes": list(c["genes"]), "library": "all"}
            if c["species"] in ("human", "mouse"):
                kw.update({"species": c["species"], "volume_species": c["species"],
                           "volume_id": "default_face_probe"})
            # NOTE: no `tissue` key at all -- this is the shipped default route
            r = core.query_marker(**kw)
            rank = r.get("celltype_ranking") or []
            rows["%s|%s" % (c["vol"], c["cluster"])] = {
                "raw_md5": raw(r), "canon_md5": canon(r),
                "top": rank[0]["cell_type"] if rank else None,
                "n_shared": rank[0].get("n_shared") if rank else None,
                "n_ranked": len(rank),
                "top_lib": (str((rank[0].get("library") if rank else "") or "").split("/")[-1]
                            or None),
                "lib_present": any(str(x.get("library") or "").endswith(LIB_BASENAME) or
                                   str(x.get("cell_type") or "").startswith(LIB_TOP_PREFIX)
                                   for x in rank),
                "carrier_present": any(str(x.get("library") or "").endswith(
                    "markers_v13_onfibro_increment.json") or
                    str(x.get("cell_type") or "").startswith("onfibro_v13::")
                    for x in rank)}
    elif fmode == "battery":
        rows["list_kb_pages"] = {"raw_md5": raw(core.list_kb_pages()),
                                 "canon_md5": canon(core.list_kb_pages())}
        labs = sorted(json.load(open(W.CL_MAP))["labels"].keys())
        for lab in labs:
            for sp in ("human", "mouse", None):
                kw = {"cell_type": lab, "library": "all"}
                if sp:
                    kw.update({"species": sp, "volume_species": sp,
                               "volume_id": "default_face_probe"})
                try:
                    r = core.query_marker(**kw)
                except Exception as e:                      # a refusal is part of the bytes
                    r = {"__error__": "%s: %s" % (type(e).__name__, e)}
                rows["cls:%s:%s" % (lab, sp)] = {"raw_md5": raw(r), "canon_md5": canon(r),
                                                 "carrier_present": LIB_TOP_PREFIX in
                                                 json.dumps(r, default=str)}
    elif fmode == "explicit":
        # every named library, asked for by name with one recorded gene window
        probe_genes = sorted(W.load_set(), key=lambda c: -c["n_cells"])[0]["genes"]
        for lib in EXPLICIT_LIBS:
            kw = {"genes": list(probe_genes), "library": lib}
            try:
                r = core.query_marker(**kw)
                rank = r.get("celltype_ranking") or []
                rows["lib:%s" % lib] = {"raw_md5": raw(r), "canon_md5": canon(r),
                                        "refused": False, "n_ranked": len(rank),
                                        "top": rank[0]["cell_type"] if rank else None}
            except Exception as e:
                rows["lib:%s" % lib] = {
                    "raw_md5": raw({"__error__": "%s: %s" % (type(e).__name__, e)}),
                    "canon_md5": canon({"__error__": "%s: %s" % (type(e).__name__, e)}),
                    "refused": True, "error": "%s: %s" % (type(e).__name__, e)}
    else:
        raise SystemExit("unknown fmode %r" % fmode)
    core_file = __import__("eyekb_core").__file__
    doc = {"fmode": fmode, "n": len(rows), "rows": rows,
           "core_file": core_file, "core_sha256": W.sha256_file(core_file),
           "raw_combined_md5": hashlib.md5(json.dumps(
               {k: v["raw_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "canon_combined_md5": hashlib.md5(json.dumps(
               {k: v["canon_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "act_holefill": os.environ.get("EYEKB_ACT_HOLEFILL", "(unset)"),
           "marker_libs_at_import": sorted(core.MARKER_LIBS.keys()),
           "default_whitelist_branch_libs": sorted(
               lib for lib in core.MARKER_LIBS
               if getattr(core, "HOLEFILL_DEFAULT_LIBS", ()) and
               lib in tuple(getattr(core, "HOLEFILL_DEFAULT_LIBS", ())))}
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)
    print("%s n=%d core=%s raw_md5=%s canon_md5=%s"
          % (fmode, doc["n"], doc["core_sha256"][:16], doc["raw_combined_md5"],
             doc["canon_combined_md5"]))


if __name__ == "__main__":
    main()