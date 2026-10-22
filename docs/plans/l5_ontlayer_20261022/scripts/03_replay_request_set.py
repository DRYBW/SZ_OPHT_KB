#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replay one recorded request set over stdio and compare RAW response bytes.

The recorded request set is fixed and declared here: the repository's own 12-call tool panel, the
42-call development-stage sweep (14 stage literals x 3 species/tissue pairs), and one call to the
release-identity tool - 55 calls in all. Nothing in it depends on the ontology layer.

    python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --take PRE.json
    python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --out POST.json
    python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --compare PRE.json POST.json

Discipline
  * Raw response text is compared, not parsed JSON, and the two dumps must be taken in the SAME
    absolute checkout directory: several answers echo the install path, so a second checkout
    produces differences that mean nothing. The dump records the absolute path it was taken from
    and `--compare` refuses to compare two dumps taken from different paths.
  * A refused call (is_error) is recorded as such and never treated as an anchor.
  * `--take` records the interpreter and the versions it actually ran under.
  * Zero network: the server is a local stdio subprocess.

Exit codes: 0 = identical (or a dump was taken); 1 = bytes differ (every differing call is listed);
            3 = the comparison could not be made (the SDK is missing, or the two dumps came from
            different paths).
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents) if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
SERVER = ROOT / "mcp_server" / "server.py"

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
STAGE_LITERALS = ["", "adult", "any", "fetal", "developing", "postnatal", "unknown", "organoid",
                  "embryonic", "neonatal", "juvenile", "aged", "old", "unspecified"]
STAGE_TARGETS = [("human", "retina"), ("mouse", "retina"), ("human", "cornea")]
IDENTITY_CALL = ("get_release_identity", {})


def request_set() -> list:
    calls = list(PANEL)
    for lit in STAGE_LITERALS:
        for sp, ti in STAGE_TARGETS:
            calls.append(("get_tissue_composition",
                          {"species": sp, "tissue": ti, "development_stage": lit}))
    calls.append(IDENTITY_CALL)
    return calls


def provenance() -> dict:
    pv = "absent"
    try:
        import pydantic
        pv = pydantic.VERSION
    except Exception:
        pass
    try:
        import mcp
        mv = getattr(mcp, "__version__", "unknown")
    except Exception:
        mv = "absent"
    return {"executable": sys.executable, "python": platform.python_version(),
            "pydantic": pv, "mcp": mv}


async def drive() -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    calls = request_set()
    out = {"calls": {}, "refused": [], "tools": [], "order": []}
    sp = StdioServerParameters(command=sys.executable, args=[str(SERVER)], env=dict(os.environ))
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out["tools"] = sorted(t.name for t in (await s.list_tools()).tools)
            for name, args in calls:
                key = f"{name}:{json.dumps(args, sort_keys=True)}"
                res = await s.call_tool(name, args)
                if getattr(res, "is_error", getattr(res, "isError", False)):
                    out["refused"].append(key)
                txt = "".join((getattr(c, "text", "") or "") for c in (res.content or []))
                # Two digests per call. The raw one is the byte-identity evidence and is only
                # comparable between runs at the same absolute checkout path; the normalised one
                # replaces the checkout path with <REPO>, so it is comparable between checkouts and
                # is what the frozen baseline is stated in.
                out["calls"][key] = {"text": txt, "md5": hashlib.md5(txt.encode()).hexdigest(),
                                     "md5_normalised": hashlib.md5(
                                         txt.replace(str(ROOT), "<REPO>").encode()).hexdigest(),
                                     "bytes": len(txt.encode())}
                out["order"].append(key)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", help="write this run to this path")
    ap.add_argument("--out", help="write this run to this path without baseline semantics")
    ap.add_argument("--compare", nargs=2, metavar=("PRE", "POST"))
    a = ap.parse_args()

    if a.compare:
        pre = json.loads(Path(a.compare[0]).read_text(encoding="utf-8"))
        post = json.loads(Path(a.compare[1]).read_text(encoding="utf-8"))
        if pre.get("checkout_path") != post.get("checkout_path"):
            print(f"CANNOT COMPARE: the dumps were taken from different directories "
                  f"({pre.get('checkout_path')} vs {post.get('checkout_path')}); answers echo the "
                  f"install path, so differences between two checkouts mean nothing.")
            return 3
        diffs = []
        for k in pre.get("order", []):
            p = pre["calls"].get(k) or {}
            q = post["calls"].get(k) or {}
            if p.get("md5") != q.get("md5") or p.get("bytes") != q.get("bytes"):
                diffs.append({"call": k, "pre_md5": p.get("md5"), "post_md5": q.get("md5"),
                              "pre_bytes": p.get("bytes"), "post_bytes": q.get("bytes")})
        tools_moved = pre.get("tools") != post.get("tools")
        print(f"checkout        {pre.get('checkout_path')}")
        print(f"calls compared  {len(pre.get('order', []))}")
        print(f"raw bytes differing  {len(diffs)}")
        for d in diffs:
            print(f"  moved: {d['call']}")
        print(f"tool list       {pre.get('tools')} -> {post.get('tools')}"
              + ("   (MOVED)" if tools_moved else "   (unchanged)"))
        print(f"refused calls   pre={len(pre.get('refused', []))} post={len(post.get('refused', []))}")
        print(json.dumps({"path": pre.get("checkout_path"), "calls": len(pre.get("order", [])),
                          "differing": len(diffs), "moved": [d["call"] for d in diffs],
                          "tools_moved": tools_moved}, ensure_ascii=False))
        return 0 if not diffs and not tools_moved else 1

    try:
        run = asyncio.run(drive())
    except ImportError as e:
        print(f"CANNOT RUN: the MCP SDK is not importable with this interpreter ({e}).")
        return 3
    except Exception as e:
        print(f"CANNOT RUN: the server could not be driven ({type(e).__name__}: {e}).")
        return 3
    run.update({"checkout_path": str(ROOT), "interpreter": sys.executable,
                "provenance": provenance(),
                "recorded_request_set": {"n_calls": len(request_set()),
                                         "panel": 12, "stage_sweep": len(request_set()) - 13,
                                         "identity": 1},
                "ontology_route_env": os.environ.get("EYEKB_ONT_LAYER", "")})
    target = a.take or a.out
    if target:
        Path(target).write_text(json.dumps(run, ensure_ascii=False, indent=1, sort_keys=True),
                                encoding="utf-8")
        print(f"recorded {len(run['calls'])} calls -> {target}")
    print(f"checkout {run['checkout_path']}  tools={len(run['tools'])}  "
          f"refused={len(run['refused'])}  route={run['ontology_route_env'] or '(unset)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())