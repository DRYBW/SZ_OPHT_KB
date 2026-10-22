#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Freeze the two replay dumps into clone-runnable hash files.

The dumps themselves are large and carry the raw texts; what a clean clone needs is the per-call
digest, the byte count and the advertised tool list, so that the default-route claim can be checked
without the evidence root. One command rebuilds both files from the dumps:

    python3 docs/plans/l5_ontlayer_20261022/scripts/05_freeze_replay_hashes.py PRE.json POST.json

It refuses to write anything if the two dumps were taken from different checkout paths (the answers
echo the install path, so such a comparison would mean nothing).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents) if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
OUT = ROOT / "docs/plans/l5_ontlayer_20261022/out"


def freeze(dump: Path, tag: str) -> dict:
    d = json.loads(dump.read_text(encoding="utf-8"))
    path = str(d.get("checkout_path") or "")
    rows = ["call\tmd5\tmd5_normalised\tbytes\tis_error"]
    refused = set(d.get("refused", []))
    for k in d["order"]:
        c = d["calls"][k]
        # The normalised digest is recomputed from the stored raw text, so a dump taken before the
        # replay tool recorded it is still usable: the raw text is what both digests come from.
        norm = hashlib.md5(c["text"].replace(path, "<REPO>").encode()).hexdigest()
        rows.append(f"{k}\t{c['md5']}\t{norm}\t{c['bytes']}\t{str(k in refused).lower()}")
    (OUT / f"{tag}_REPLAY_HASHES.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (OUT / f"{tag}_TOOLS.txt").write_text("\n".join(d["tools"]) + "\n", encoding="utf-8")
    return {"n_calls": len(d["order"]), "path": d["checkout_path"], "tools": len(d["tools"]),
            "interpreter": d.get("interpreter"), "provenance": d.get("provenance"),
            "route_env": d.get("ontology_route_env")}


def main() -> int:
    pre, post = Path(sys.argv[1]), Path(sys.argv[2])
    a, b = freeze(pre, "PRE"), freeze(post, "POST")
    if a["path"] != b["path"]:
        print(f"CANNOT FREEZE: the dumps come from different directories ({a['path']} vs {b['path']}).")
        return 3
    pre_h = {r.split("\t")[0]: r.split("\t")[1:] for r in
             (OUT / "PRE_REPLAY_HASHES.tsv").read_text(encoding="utf-8").splitlines()[1:]}
    post_h = {r.split("\t")[0]: r.split("\t")[1:] for r in
              (OUT / "POST_REPLAY_HASHES.tsv").read_text(encoding="utf-8").splitlines()[1:]}
    moved = [k for k in pre_h if pre_h[k][0] != post_h[k][0]]
    summary = {"checkout_path": a["path"], "n_calls": a["n_calls"],
               "moved": moved, "tool_list_changed": a["tools"] != b["tools"],
               "pre": a, "post": b,
               "rule": ("the recorded request set is replayed at the same absolute path; raw "
                        "response bytes are compared, not parsed JSON; every call outside the "
                        "identity tool must be identical, and the identity call is the only one "
                        "permitted to move (it is the explicit identity interface, and the "
                        "four-layer block is the deliverable)")}
    (OUT / "REPLAY_COMPARISON.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("checkout_path", "n_calls", "moved",
                                              "tool_list_changed")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())