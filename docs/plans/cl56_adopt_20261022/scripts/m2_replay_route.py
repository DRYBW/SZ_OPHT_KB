# -*- coding: utf-8 -*-
"""m2_replay_route.py -- child replay of the DEFAULT route, recording raw and canonical response bytes
per query, for the CL-56 wave.

Run as a separate process with the core bytes under test already in place at their absolute path (the
parent script swaps the file, so "which code answered" is a property of the process, not of an import
order inside one run).

argv: <fmode> <out.json>
  fmode = "clusters"  -> the 721 recorded cluster gene windows (genes mode, NO tissue argument)
  fmode = "battery"   -> the default-route battery: page listing + cell_type mode for every label
                         x three species arguments
  fmode = "explicit"  -> the EXPLICIT-route battery: every named library in MARKER_LIBS, so a
                         registration line whose body cannot answer anything is visible as an empty
                         ranking rather than as silence

Two byte readings per query: raw_md5 (field order as the service builds it) and canon_md5
(sort_keys=True, the predecessor wave's reading, kept so the numbers stay comparable).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L6 = "/mnt/D/EyeKB/plans/noregr_20261022/scripts"
sys.path.insert(0, L6)
import wave_common as W  # noqa: E402

LIB_TOP_PREFIX = "cl56_v15::"
LIB_BASENAME = "markers_v15_cl56_increment.json"
EXPLICIT_LIBS = ("retina", "membrane", "retina_interneuron", "retina_v6", "face_v6", "lacrimal_v6",
                 "k9_ocs", "retina_v7", "retina_dev", "antseg_v10", "lensiris_v11", "holefill_v12",
                 "onfibro_v13", "subtype_v14", "cl56_v15")


def raw(resp):
    return hashlib.md5(json.dumps(resp, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def canon(resp):
    return hashlib.md5(json.dumps(resp, sort_keys=True, ensure_ascii=False,
                                  default=str).encode("utf-8")).hexdigest()


def main():
    fmode, out = sys.argv[1], sys.argv[2]
    sys.path.insert(0, os.path.join(W.REPO, "mcp_server"))
    import eyekb_core as core
    rows = {}
    if fmode == "clusters":
        for c in W.load_set():
            kw = {"genes": list(c["genes"]), "library": "all"}
            if c["species"] in ("human", "mouse"):
                kw.update({"species": c["species"], "volume_species": c["species"],
                           "volume_id": "cl56_default_probe"})
            r = core.query_marker(**kw)          # no `tissue` key: the shipped default route
            rank = r.get("celltype_ranking") or []
            rows["%s|%s" % (c["vol"], c["cluster"])] = {
                "raw_md5": raw(r), "canon_md5": canon(r),
                "top": rank[0]["cell_type"] if rank else None,
                "n_shared": rank[0].get("n_shared") if rank else None,
                "n_ranked": len(rank),
                "top_lib": (str((rank[0].get("library") if rank else "") or "").split("/")[-1] or None),
                "lib_present": any(str(x.get("library") or "").endswith(LIB_BASENAME) or
                                   str(x.get("cell_type") or "").startswith(LIB_TOP_PREFIX)
                                   for x in rank)}
    elif fmode == "battery":
        rows["list_kb_pages"] = {"raw_md5": raw(core.list_kb_pages()),
                                 "canon_md5": canon(core.list_kb_pages())}
        labs = sorted(json.load(open(W.CL_MAP))["labels"].keys())
        for lab in labs:
            for sp in ("human", "mouse", None):
                kw = {"cell_type": lab, "library": "all"}
                if sp:
                    kw.update({"species": sp, "volume_species": sp, "volume_id": "cl56_default_probe"})
                try:
                    r = core.query_marker(**kw)
                except Exception as e:                      # a refusal is part of the bytes
                    r = {"__error__": "%s: %s" % (type(e).__name__, e)}
                rows["cls:%s:%s" % (lab, sp)] = {"raw_md5": raw(r), "canon_md5": canon(r)}
    elif fmode == "explicit":
        probe_genes = sorted(W.load_set(), key=lambda c: -c["n_cells"])[0]["genes"]
        for lib in EXPLICIT_LIBS:
            kw = {"genes": list(probe_genes), "library": lib}
            try:
                r = core.query_marker(**kw)
                rank = r.get("celltype_ranking") or []
                rows["lib:%s" % lib] = {"raw_md5": raw(r), "canon_md5": canon(r), "refused": False,
                                        "n_ranked": len(rank),
                                        "top": rank[0]["cell_type"] if rank else None}
            except Exception as e:
                err = {"__error__": "%s: %s" % (type(e).__name__, e)}
                rows["lib:%s" % lib] = {"raw_md5": raw(err), "canon_md5": canon(err), "refused": True,
                                        "error": err["__error__"]}
    else:
        raise SystemExit("unknown fmode %r" % fmode)
    core_file = core.__file__
    doc = {"fmode": fmode, "n": len(rows), "rows": rows, "core_file": core_file,
           "core_sha256": W.sha256_file(core_file),
           "raw_combined_md5": hashlib.md5(json.dumps(
               {k: v["raw_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "canon_combined_md5": hashlib.md5(json.dumps(
               {k: v["canon_md5"] for k, v in rows.items()}, sort_keys=True).encode()).hexdigest(),
           "act_cl56": os.environ.get("EYEKB_ACT_CL56", "(unset)"),
           "marker_libs_at_import": sorted(core.MARKER_LIBS.keys()),
           "whitelist_branch_libs": sorted(getattr(core, "CL56_DEFAULT_LIBS", ()))}
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)
    print("%s n=%d core=%s raw_md5=%s canon_md5=%s"
          % (fmode, doc["n"], doc["core_sha256"][:16], doc["raw_combined_md5"],
             doc["canon_combined_md5"]))


if __name__ == "__main__":
    main()