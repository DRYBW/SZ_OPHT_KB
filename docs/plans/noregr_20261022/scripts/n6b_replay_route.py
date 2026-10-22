#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n6b -- child replay: canonical response bytes for the DEFAULT route over the recorded query set.

Run as a separate process with the core surface under test first on sys.path, so "which code
answered" is a property of the process, not of an import order inside this run.

argv: <fmode> <out.json>
  fmode = "clusters"  -> the 721 recorded cluster gene windows (genes mode, NO tissue argument)
  fmode = "battery"   -> the default-route battery: class listing + cell_type mode for every label
                         + three species arguments
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import wave_common as W  # noqa: E402


def canon(resp):
    return hashlib.md5(json.dumps(resp, sort_keys=True, ensure_ascii=False,
                                  default=str).encode("utf-8")).hexdigest()


def main():
    fmode, out = sys.argv[1], sys.argv[2]
    sys.path.insert(0, os.environ.get("NR_CORE_DIR", os.path.join(W.REPO, "mcp_server")))
    import eyekb_core as core
    import json as _j
    hashes = {}
    if fmode == "clusters":
        for c in W.load_set():
            kw = {"genes": list(c["genes"]), "library": "all"}
            if c["species"] in ("human", "mouse"):
                kw.update({"species": c["species"], "volume_species": c["species"],
                           "volume_id": "default_face_probe"})
            # NOTE: no `tissue` key at all -- this is the shipped default route
            r = core.query_marker(**kw)
            hashes["%s|%s" % (c["vol"], c["cluster"])] = canon(r)
    elif fmode == "battery":
        hashes["list_kb_pages"] = canon(core.list_kb_pages())
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
                hashes["cls:%s:%s" % (lab, sp)] = canon(r)
    else:
        raise SystemExit("unknown fmode %r" % fmode)
    doc = {"fmode": fmode, "n": len(hashes), "hashes": hashes,
           "core_file": __import__("eyekb_core").__file__,
           "core_sha256": W.sha256_file(__import__("eyekb_core").__file__),
           "combined_md5": hashlib.md5(json.dumps(hashes, sort_keys=True).encode()).hexdigest()}
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)
    print("%s n=%d combined_md5=%s" % (fmode, doc["n"], doc["combined_md5"]))


if __name__ == "__main__":
    main()