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

The panel spells its arguments the way the README documents them (the "exact signatures" table), so
a tool that starts rejecting a documented argument shows up here rather than in a user's first call.
Two rules follow from that, and both are enforced below:

  * a refused call is a FAILURE, never an anchor. The text of a refusal is produced by the MCP
    layer's argument validation, not by the tool: it embeds the validating library's own version
    string, so a baseline containing one is not reproducible on an interpreter with a different
    pydantic. A refusal therefore means the panel did not exercise that tool at all. The baseline
    records the refused calls it saw, and the probe exits non-zero when a run has any.
  * a digest that moves must be attributed in the same commit. When a change to an answer is
    intended, re-record the baseline in that commit and say so in the change record
    (docs/CHANGE_CONTROL_G6_INSTANCE.tsv). The probe prints the differing calls so that the
    attribution is mechanical rather than remembered.

Interpreter: the panel drives the server with one interpreter, and the baseline records which one
(its `provenance` block). Any interpreter that can import `mcp.server.MCPServer` will drive the
server, but the recorded digests are comparable only on the interpreter they were taken with, so a
run under a different interpreter is reported as an advisory -- the same shape as the G4 gate's
`[g4] interpreter:` line (docs/VERIFY_CONTRACT.md §G4.1). Set EYEKB_PROBE_PY to choose it;
the default is the interpreter running this script.

Usage (from the repo root):
  python tests/probe_tool_panel_identity.py                       # print the digests
  python tests/probe_tool_panel_identity.py --baseline f.json     # compare against a recorded run
  python tests/probe_tool_panel_identity.py --record f.json       # store this run as the baseline

Exit codes: 0 = digests match the baseline (or none was given) and no call was refused;
            1 = a digest moved, or a panel call was refused;
            3 = the server could not be driven at all (an interpreter without the MCP SDK, say),
                which is not a result about the service and is reported separately rather than as a
                regression.
"""
import argparse, asyncio, hashlib, json, os, pathlib, platform, sys

LEGACY = ["query_marker", "get_tissue_composition", "get_disease_prior", "get_kb_page",
          "search_literature"]

REPO = pathlib.Path(__file__).resolve().parents[1]
SRV = str(REPO / "mcp_server" / "server.py")

# The panel. Arguments are the ones README.md's exact-signature table documents: `scope` (not
# `kind`) for get_kb_page, a string (`full`/`answer`) for detail, and the required `cell_type` for
# search_literature. A call spelled against a signature the service does not have is refused before
# the tool runs, so it measures the MCP layer's error text instead of the tool's answer.
PANEL = [
    ("query_marker", {"cell_type": "RPE", "library": "retina"}),
    ("query_marker", {"cell_type": "MG"}),
    ("query_marker", {"genes": ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]}),
    ("get_tissue_composition", {"species": "human", "tissue": "retina", "detail": "full"}),
    ("get_tissue_composition", {"species": "mouse", "tissue": "retina"}),
    ("get_disease_prior", {"disease": "PDR"}),
    ("get_kb_page", {"scope": "topic", "name": "vascular"}),
    ("get_kb_page", {"scope": "index"}),
    ("search_literature", {"cell_type": "Muller glia", "query": "Mueller cell gliosis", "top_k": 3}),
    ("search_literature", {"cell_type": "Rod", "top_k": 3}),
    ("explain_annotation", {"cell_type": "Rod"}),
    ("explain_annotation", {"cell_type": "Mueller cell"}),
]


def provenance():
    """Which interpreter took (or is taking) this panel. Recorded, and compared as an advisory."""
    pv = ""
    try:
        import pydantic
        pv = pydantic.VERSION
    except Exception:
        pv = "absent"
    return {"executable": sys.executable, "python": platform.python_version(), "pydantic": pv}


async def drive():
    """Run the panel over stdio.

    Returns {"responses": {call: md5}, "refused": [call, ...], "tools": [...],
             "provenance": {...}}.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    py = os.environ.get("EYEKB_PROBE_PY", sys.executable)
    responses, refused = {}, []
    sp = StdioServerParameters(command=py, args=[SRV], env=dict(os.environ))
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = sorted(t.name for t in (await s.list_tools()).tools)
            for name, args in PANEL:
                key = f"{name}:{json.dumps(args, sort_keys=True)}"
                res = await s.call_tool(name, args)
                if getattr(res, "is_error", getattr(res, "isError", False)):
                    refused.append(key)
                parts = [getattr(c, "text", "") or "" for c in (res.content or [])]
                txt = "".join(parts)
                # The response echoes the install path in a few places; normalising it keeps the
                # digest comparable between two clones at different locations.
                txt = txt.replace(str(REPO), "<REPO>")
                responses[key] = hashlib.md5(txt.encode()).hexdigest()
    return {"responses": responses, "refused": refused, "tools": tools,
            "provenance": provenance(), "interpreter": py}


def digests(rows):
    """Per-call hashes plus the two panel digests."""
    calls = dict(rows)
    legacy = {k: v for k, v in rows.items() if k.split(":", 1)[0] in LEGACY}

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
        run = asyncio.run(drive())
    except ImportError as e:
        print(f"CANNOT RUN: the MCP SDK is not importable with this interpreter ({e}).")
        print("Set EYEKB_PROBE_PY to one that has it, then re-run. No statement is made about the service.")
        return 3
    except Exception as e:
        print(f"CANNOT RUN: the server could not be driven ({type(e).__name__}: {e}). "
              "No statement is made about the service.")
        return 3

    got = digests(run["responses"])
    shown = {k: got[k] for k in ("legacy_panel", "full_panel", "n_legacy_calls", "n_calls")}
    print(json.dumps(shown, indent=1))
    print(f"tools advertised: {', '.join(run['tools'])}")
    print(f"interpreter: {run['interpreter']} "
          f"(python {run['provenance']['python']}, pydantic {run['provenance']['pydantic']})")

    if run["refused"]:
        print(f"REFUSED: {len(run['refused'])} of {len(PANEL)} panel calls were refused on their "
              "arguments; a refusal measures the MCP layer's error text, not the tool's answer, so "
              "it cannot be an anchor:")
        for k in run["refused"]:
            print(f"  refused: {k}")
    if got["n_calls"] != len(PANEL):
        print(f"WARN: {len(PANEL)} panel calls were issued but {got['n_calls']} produced a digest.")

    if a.record:
        pathlib.Path(a.record).write_text(
            json.dumps({"tools": run["tools"], "provenance": run["provenance"],
                        "refused_calls": run["refused"], **got}, indent=1, sort_keys=True),
            encoding="utf-8")
        print(f"recorded baseline -> {a.record}"
              f"{'' if not run['refused'] else ' (WARNING: recorded WITH refused calls)'}")

    if run["refused"]:
        return 1

    if a.baseline:
        base = json.loads(pathlib.Path(a.baseline).read_text(encoding="utf-8"))
        moved = [k for k in ("legacy_panel", "full_panel") if base.get(k) != got.get(k)]
        if not moved:
            print("IDENTITY PASS: both panel digests match the baseline.")
            bp = base.get("provenance") or {}
            if bp and bp.get("executable") and bp.get("executable") != run["provenance"]["executable"]:
                print(f"note (advisory): the baseline was taken with {bp.get('executable')} "
                      f"(python {bp.get('python')}, pydantic {bp.get('pydantic')}); this run used "
                      f"{run['provenance']['executable']} (python {run['provenance']['python']}, "
                      f"pydantic {run['provenance']['pydantic']}). Advice only: no call was "
                      "refused, so the answers are comparable.")
            return 0
        print(f"IDENTITY FAIL: {', '.join(moved)} moved.")
        for k in sorted(got["calls"]):
            if base.get("calls", {}).get(k) not in (None, got["calls"][k]):
                print(f"  different: {k}")
        print("If the change was intended, re-record the baseline in the same commit and say so "
              "in the change record (docs/CHANGE_CONTROL_G6_INSTANCE.tsv).")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())