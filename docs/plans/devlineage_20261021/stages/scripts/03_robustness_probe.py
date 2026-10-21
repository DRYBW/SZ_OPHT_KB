#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 3 — robustness pass on the recognition probe.

Why this pass exists (a limitation of the primary probe, disclosed rather than hidden): the fetal
window of step 2 is drawn from the same file the shipped `off_domain` advisory reads, so the
advisory necessarily fires whenever that window is supplied. A firing advisory therefore measures
"this window looks like the developmental panel", not "an independent fetal sample would be
recognised". This pass re-measures the same question with windows that are NOT the panel's own
final list:

  * v9_K5          a narrower window from the same panel (5 genes instead of 10)
  * v8_*           the superseded v8 panel build (its own ban list permits word-level reference to
                   v8 while forbidding numeric reference - so the gene names are usable here, and
                   they are a different build's list, not the file the advisory reads)
  * mature_filtered  the genes the panel build itself REMOVED from an entry because they mark
                   mature clusters; these are explicitly not in the advisory's reference sets, so
                   they are the strongest available non-circular window

Every window is measured against the shipped service, and the dev-panel overlap is recomputed here
from the shipped panel file, so no number comes from the advisory's own output alone.
"""
import argparse
import asyncio
import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = HERE / "out"
SCRIPTS = Path(__file__).resolve().parent
TAG = "devlineage-v3-stage-probe"

spec = importlib.util.spec_from_file_location("p02", SCRIPTS / "02_probe_recognition.py")
p02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p02)


def devsets():
    d = json.loads((REPO / "kb" / "markers" / "markers_v9_dev_retina.json").read_text(encoding="utf-8"))
    return {e: set(g.upper() for g in gs) for e, gs in d["markers"].items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interpreter", default="/home/ubuntu/training-venv/bin/python3")
    a = ap.parse_args()

    v9 = json.loads((REPO / "kb" / "markers" / "markers_v9_dev_retina.json").read_text(encoding="utf-8"))
    # The superseded v8 panel build exists only in the data-mount working copy, not in the
    # repository (recorded as a finding: the repo keeps the active v9 file only). Its own ban list
    # permits word-level reference to v8 while forbidding numeric reference, so its gene lists are
    # usable here; the file path and sha256 are recorded with the results.
    v8_candidates = [REPO / "kb" / "markers" / "markers_v8_dev_retina.json",
                     Path("/mnt/D/EyeKB/kb/markers/markers_v8_dev_retina.json")]
    v8_path = next((p for p in v8_candidates if p.is_file()), None)
    if v8_path is None:
        raise SystemExit("markers_v8_dev_retina.json not found on either face; robustness pass needs it")
    v8 = json.loads(v8_path.read_text(encoding="utf-8"))
    import hashlib as _h
    V8_SHA = _h.sha256(v8_path.read_bytes()).hexdigest()
    DS = devsets()
    mature = v9["mature_filter_stats"]["filtered_per_entry"]

    nodes = list(csv.DictReader(open(OUT / "NODE_KEYS.tsv", encoding="utf-8"), delimiter="\t"))
    adult_of = {}
    for n in nodes:
        if n["node_kind"] == "fetal_entry":
            adult_of[n["lineage_id"]] = [c for c in n["adult_counterpart_classes"].split(";") if c]

    windows = []
    for n in nodes:
        if n["node_kind"] != "fetal_entry":
            continue
        e, lin = n["in_house_entry"], n["lineage_id"]
        full = list(v9["markers"][e])
        if len(full) >= 5:
            windows.append({"wid": f"{lin}.{e}.v9K5", "lineage_id": lin, "source": "v9 panel (narrower)",
                            "entry": e, "genes": full[:5]})
        if e in v8["markers"] and len(v8["markers"][e]) >= 2:
            windows.append({"wid": f"{lin}.{e}.v8", "lineage_id": lin, "source": "v8 panel build",
                            "entry": e, "genes": list(v8["markers"][e])})
        if e in mature and len(mature[e]) >= 2:
            windows.append({"wid": f"{lin}.{e}.mature_filtered", "lineage_id": lin,
                            "source": "genes this build removed as mature markers", "entry": e,
                            "genes": list(mature[e])})

    calls = [{"id": w["wid"], "tool": "query_marker", "args": {"genes": w["genes"]},
              "lineage_id": w["lineage_id"], "side": "fetal_window_variant", "window": None,
              "route": "default", "n_genes": len(w["genes"]), "declared_but_unrunnable": False}
             for w in windows]

    rows = asyncio.run(p02.drive(calls, a.interpreter))
    rows["_meta"] = {"server": str(REPO / "mcp_server" / "server.py"), "interpreter": a.interpreter,
                     "trace_tag": TAG, "n_calls": len(calls), "purpose": "robustness / non-circular windows",
                     "v8_panel_file": str(v8_path), "v8_panel_sha256": V8_SHA}
    (OUT / "ROBUSTNESS_RESULTS.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")

    out = []
    for w in windows:
        r = rows[w["wid"]]
        resp = r.get("response") or {}
        g = set(x.upper() for x in w["genes"])
        best, terms = 0, []
        for e2, gs in DS.items():
            k = len(g & gs)
            if k > best:
                best, terms = k, [e2]
            elif k == best and k > 0:
                terms.append(e2)
        t1 = p02.top1(resp)
        adv = bool(resp.get("off_domain"))
        adult_hit = bool(t1 and t1.get("cell_type") in adult_of.get(w["lineage_id"], []))
        out.append({"wid": w["wid"], "lineage_id": w["lineage_id"], "window_source": w["source"],
                    "entry": w["entry"], "n_genes": len(w["genes"]),
                    "dev_best": best, "dev_terms": ";".join(sorted(terms)[:3]),
                    "advisory_fired": "Y" if adv else "N",
                    "top1": (t1 or {}).get("cell_type", ""), "top1_n_shared": (t1 or {}).get("n_shared", ""),
                    "top1_is_adult_counterpart": "Y" if adult_hit else "N",
                    "ranking_empty": "Y" if not resp.get("celltype_ranking") else "N",
                    "genes": " ".join(w["genes"])})
    cols = list(out[0].keys())
    with open(OUT / "ROBUSTNESS_WINDOWS.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    by_src = {}
    for r in out:
        b = by_src.setdefault(r["window_source"], {"n": 0, "advisory": 0, "dev_best_ge1": 0, "dev_best_ge2": 0})
        b["n"] += 1
        b["advisory"] += (r["advisory_fired"] == "Y")
        b["dev_best_ge1"] += (r["dev_best"] >= 1)
        b["dev_best_ge2"] += (r["dev_best"] >= 2)
    print(json.dumps({"n_windows": len(out), "by_window_source": by_src,
                      "n_errors": sum(1 for k, v in rows.items() if isinstance(v, dict) and v.get("is_error"))},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()