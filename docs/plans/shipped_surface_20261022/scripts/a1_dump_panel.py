#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shipped-surface probe, step 1 — dump the raw answer of every call we intend to reason about.

Two surfaces are dumped:

  panel    the twelve calls of tests/probe_tool_panel_identity.py, so that each of the five moved
           digests can be attributed to either a refused call or an answer whose text changed.
  literal  get_tissue_composition driven once per development_stage literal, over three
           (species, tissue) pairs, so the whole fall-through surface of the stage argument is
           measured instead of the single literal the report happened to name.

Unlike the panel probe this dump keeps the response text of every call, the is_error flag the MCP
client reports, and the parsed payload when the text parses as JSON. The panel probe keeps only the
digest, which cannot tell a refusal from an answer.

Usage:
  <sdk-interpreter> a1_dump_panel.py --repo <repo root> --out <file.json>
"""
import argparse
import asyncio
import hashlib
import json
import os
import pathlib
import sys

TAG = "shipped-surface-20261022"

# The twelve calls of tests/probe_tool_panel_identity.py, verbatim (argument spellings included).
PANEL = [
    ("query_marker", {"cell_type": "RPE", "library": "retina"}),
    ("query_marker", {"cell_type": "MG"}),
    ("query_marker", {"genes": ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]}),
    ("get_tissue_composition", {"species": "human", "tissue": "retina", "detail": True}),
    ("get_tissue_composition", {"species": "mouse", "tissue": "retina"}),
    ("get_disease_prior", {"disease": "PDR"}),
    ("get_kb_page", {"kind": "topic", "name": "vascular"}),
    ("get_kb_page", {"kind": "index"}),
    ("search_literature", {"query": "Mueller cell gliosis", "top_k": 3}),
    ("search_literature", {"cell_type": "Rod", "top_k": 3}),
    ("explain_annotation", {"cell_type": "Rod"}),
    ("explain_annotation", {"cell_type": "Mueller cell"}),
]

# Stage literals. The seven the prereg's own probe used, plus the spellings a caller actually
# reaches for: the documented synonyms, a case variant, the KB3 source literal, and a typo.
LITERALS = ["", "adult", "any", "fetal", "developing", "postnatal", "unknown",
            "organoid", "ORGANOID", "organoid_Day30", "adult_or_unspecified", "fetel", "neonatal",
            " fetal "]
# (species, tissue) pairs: retina has an adult baseline and no unknown-tier entry; RPE has an
# unknown-tier entry; mouse retina covers the second species.
PAIRS = [("human", "retina"), ("human", "RPE"), ("mouse", "retina")]


def md5(txt):
    return hashlib.md5(txt.encode()).hexdigest()


def build_calls():
    calls = []
    for name, args in PANEL:
        # The id is the baseline's own key shape (`<tool>:<json>`), so a dump can be joined against
        # tests/fixtures/tool_panel_baseline.json without a translation step.
        calls.append({"id": f"panel::{name}:{json.dumps(args, sort_keys=True)}",
                      "surface": "panel", "tool": name, "args": args})
    for sp, ti in PAIRS:
        for lit in LITERALS:
            calls.append({"id": f"literal::{sp}::{ti}::{lit!r}", "surface": "literal",
                          "tool": "get_tissue_composition",
                          "args": {"species": sp, "tissue": ti, "development_stage": lit}})
    return calls


async def drive(calls, repo, interpreter):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    srv = str(pathlib.Path(repo) / "mcp_server" / "server.py")
    env = dict(os.environ)
    env["EYEKB_MCP_TRACE_TAG"] = TAG
    out = {}
    sp = StdioServerParameters(command=interpreter, args=[srv], env=env)
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["_repo"] = str(repo)
            out["_interpreter"] = interpreter
            out["_tools"] = sorted(t.name for t in (await s.list_tools()).tools)
            out["_server_info"] = str(getattr(init, "serverInfo", None))
            for c in calls:
                res = await s.call_tool(c["tool"], c["args"])
                parts = [getattr(x, "text", "") or "" for x in (res.content or [])]
                txt = "".join(parts)
                norm = txt.replace(str(repo), "<REPO>")
                rec = {"tool": c["tool"], "args": c["args"], "surface": c["surface"],
                       "is_error": bool(getattr(res, "is_error",
                                                getattr(res, "isError", False))),
                       "md5": md5(norm), "bytes": len(txt.encode()), "text": norm}
                try:
                    rec["payload"] = json.loads(txt)
                except Exception:
                    rec["payload"] = None
                out[c["id"]] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--interpreter", default="/home/ubuntu/training-venv/bin/python3")
    a = ap.parse_args()
    rows = asyncio.run(drive(build_calls(), a.repo, a.interpreter))
    dest = pathlib.Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8")
    refused = sum(1 for k, v in rows.items() if not k.startswith("_") and v["is_error"])
    print(f"{dest}  calls={sum(1 for k in rows if not k.startswith('_'))} refused={refused}")
    return 0


if __name__ == "__main__":
    sys.exit(main())