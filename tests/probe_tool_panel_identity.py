#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool-panel identity probe.

Every change to the service has to be able to show that the answers the tools already gave are
unchanged. This script is the machine check behind that claim: it drives a fixed panel of calls
over stdio, hashes each response, and prints two panel digests.

  legacy panel  the five tools that were in the shipped service before the evidence-trail tool was
                added. This is the byte-identity guarantee: it must not move when a new tool is
                added or an existing one is widened.
  full panel    all six tools, including the newer ones, so their drift is visible too.

Usage (from the repo root):
  python tests/probe_tool_panel_identity.py                       # print the digests
  python tests/probe_tool_panel_identity.py --baseline f.json     # compare against a recorded run
  python tests/probe_tool_panel_identity.py --record f.json       # store this run as the baseline

Exit codes: 0 = digests match the baseline (or none was given); 1 = a digest moved; 3 = the server
could not be driven at all (an interpreter without the MCP SDK, say), which is not a result about
the service and is reported separately rather than as a regression.

Set EYEKB_PROBE_PY to the interpreter that has the MCP SDK when the default python3 does not
(conda envs on this workstation hold it; the bare system python usually does not).
"""
import argparse, asyncio, hashlib, json, os, pathlib, sys

LEGACY = ["query_marker", "get_tissue_composition", "get_disease_prior", "get_kb_page",
          "search_literature"]

REPO = pathlib.Path(__file__).resolve().parents[1]
SRV = str(REPO / "mcp_server" / "server.py")

# The panel. Arguments are spelled the way the README documents them, so a tool that starts
# rejecting a documented argument shows up here rather than in a user's first call.
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


async def drive():
    """Run the panel over stdio; return {call: md5} plus the advertised tool list."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    py = os.environ.get("EYEKB_PROBE_PY", sys.executable)
    out = {}
    sp = StdioServerParameters(command=py, args=[SRV], env=dict(os.environ))
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out["_tools"] = sorted(t.name for t in (await s.list_tools()).tools)
            for name, args in PANEL:
                key = f"{name}:{json.dumps(args, sort_keys=True)}"
                res = await s.call_tool(name, args)
                parts = [getattr(c, "text", "") or "" for c in (res.content or [])]
                txt = "".join(parts)
                # The response echoes the install path in a few places; normalising it keeps the
                # digest comparable between two clones at different locations.
                txt = txt.replace(str(REPO), "<REPO>")
                out[key] = hashlib.md5(txt.encode()).hexdigest()
    return out


def digests(rows):
    """Per-call hashes plus the two panel digests."""
    legacy = {k: v for k, v in rows.items() if k.split(":", 1)[0] in LEGACY}
    calls = {k: v for k, v in rows.items() if not k.startswith("_")}

    def panel(d):
        blob = json.dumps(d, sort_keys=True).encode()
        return hashlib.md5(blob).hexdigest()

    return {"legacy_panel": panel(legacy), "full_panel": panel(calls),
            "n_legacy_calls": len(legacy), "n_calls": len(calls), "calls": calls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", help="a recorded run to compare against")
    ap.add_argument("--record", help="write this run to this path as the new baseline")
    a = ap.parse_args()

    if not pathlib.Path(SRV).is_file():
        print(f"CANNOT RUN: server not found at {SRV}")
        return 3
    try:
        rows = asyncio.run(drive())
    except ImportError as e:
        print(f"CANNOT RUN: the MCP SDK is not importable with this interpreter ({e}).")
        print("Set EYEKB_PROBE_PY to one that has it, then re-run. No statement is made about the service.")
        return 3
    except Exception as e:
        print(f"CANNOT RUN: the server could not be driven ({type(e).__name__}: {e}). "
              "No statement is made about the service.")
        return 3

    got = digests(rows)
    shown = {k: got[k] for k in ("legacy_panel", "full_panel", "n_legacy_calls", "n_calls")}
    print(json.dumps(shown, indent=1))
    if got["n_calls"] != len(PANEL):
        print(f"WARN: {len(PANEL)} panel calls were issued but {got['n_calls']} produced a digest; "
              "the server may have refused an argument.")
    print(f"tools advertised: {', '.join(rows.get('_tools', []))}")

    if a.record:
        pathlib.Path(a.record).write_text(
            json.dumps({"tools": rows.get("_tools"), **got}, indent=1), encoding="utf-8")
        print(f"recorded baseline -> {a.record}")

    if a.baseline:
        base = json.loads(pathlib.Path(a.baseline).read_text(encoding="utf-8"))
        moved = [k for k in ("legacy_panel", "full_panel") if base.get(k) != got.get(k)]
        if not moved:
            print("IDENTITY PASS: both panel digests match the baseline.")
            return 0
        print(f"IDENTITY FAIL: {', '.join(moved)} moved.")
        for k in sorted(got["calls"]):
            if base.get("calls", {}).get(k) not in (None, got["calls"][k]):
                print(f"  different: {k}")
        print("If the change was intended, re-record the baseline in the same commit and say so "
              "in the change record.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())