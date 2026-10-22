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

Two byte readings per query, both reported:
  raw_md5   md5 of `json.dumps(resp)`, field order as the service builds it -- the response bytes;
  canon_md5 md5 of `json.dumps(resp, sort_keys=True)`, the predecessor wave's reading, so this
            card's numbers are comparable with the numbers that wave recorded.
Plus, for the clusters arm, the answer itself (top-1, n_shared, candidate count, whether the
carrier entry is present), so every moved query can be attributed rather than counted.
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

CARRIER_TOP_PREFIX = "onfibro_v13::"


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
                "carrier_present": any(str(x.get("library") or "").endswith(
                    "markers_v13_onfibro_increment.json") or
                    str(x.get("cell_type") or "").startswith(CARRIER_TOP_PREFIX)
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
                                                 "carrier_present": CARRIER_TOP_PREFIX in
                                                 json.dumps(r, default=str)}
    else:
        raise SystemExit("unknown fmode %r" % fmode)
    core_file = __import__("eyekb_core").__file__
    doc = {"fmode": fmode, "n": len(rows), "rows": rows,
           "core_file": core_file, "core_sha256": W.sha256_file(core_file),
           "raw_combined_md5": hashlib.md5(json.dumps(
               {k: v["raw_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "canon_combined_md5": hashlib.md5(json.dumps(
               {k: v["canon_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "act_onfibro": os.environ.get("EYEKB_ACT_ONFIBRO", "(unset)")}
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)
    print("%s n=%d core=%s raw_md5=%s canon_md5=%s"
          % (fmode, doc["n"], doc["core_sha256"][:16], doc["raw_combined_md5"],
             doc["canon_combined_md5"]))


if __name__ == "__main__":
    main()