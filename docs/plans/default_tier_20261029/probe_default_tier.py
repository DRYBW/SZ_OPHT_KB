#!/usr/bin/env python
"""Measure the shipped default tier of the two heavy tools, through the real stdio server.

Every reading is (characters, md5 of the response text, and — for composition — the number of
citations carried inside each row). The probe runs the server as a subprocess with a controlled
environment so the environment-variable revert path can be measured, not asserted.

Usage:
    EYEKB_REPO_ROOT=/home/ubuntu/EYEKB_REPO \
    UX_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \
    python probe_default_tier.py --label before --out out/BEFORE.json
"""
import argparse
import asyncio
import hashlib
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO = os.environ.get("EYEKB_REPO_ROOT", "/home/ubuntu/EYEKB_REPO")
PY = os.environ.get("UX_PY", sys.executable)
SRV = os.path.join(REPO, "mcp_server", "server.py")

# (case id, tool, arguments). The first four are the default calls; the rest are the explicit
# heavy/light tiers that must keep working exactly as they do now.
CASES = [
    ("index_default", "get_kb_page", {"scope": "index"}),
    ("tissue_default", "get_kb_page", {"scope": "tissue", "name": "cornea"}),
    ("comp_default", "get_tissue_composition", {"species": "human", "tissue": "retina"}),
    ("comp_mouse_default", "get_tissue_composition", {"species": "mouse", "tissue": "retina"}),
    ("index_summary_true", "get_kb_page", {"scope": "index", "summary": True}),
    ("index_detail_full", "get_kb_page", {"scope": "index", "detail": "full"}),
    ("index_summary_false", "get_kb_page", {"scope": "index", "summary": False}),
    ("tissue_detail_full", "get_kb_page", {"scope": "tissue", "name": "cornea", "detail": "full"}),
    ("comp_detail_full", "get_tissue_composition",
     {"species": "human", "tissue": "retina", "detail": "full"}),
    ("comp_detail_answer", "get_tissue_composition",
     {"species": "human", "tissue": "retina", "detail": "answer"}),
    ("disease_prior_pdr", "get_disease_prior", {"disease": "PDR"}),
]


def _citations_in_rows(obj):
    """Count citations carried inside rows, plus the row count.

    A row's citations live in its own sources_resolved; the response may also carry a top-level
    provenance block, which is deliberately not counted here — the question this answers is
    whether the light tier keeps the per-row evidence, not whether it keeps the global index.
    """
    rows = obj.get("rows") if isinstance(obj, dict) else None
    if not isinstance(rows, list):
        return None, None
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        src = row.get("sources_resolved")
        if isinstance(src, list):
            total += len(src)
        elif isinstance(src, dict):
            total += len(src)
        elif isinstance(src, str) and src.strip():
            total += 1
    return len(rows), total


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="run")
    ap.add_argument("--out", required=True)
    ap.add_argument("--env", action="append", default=[],
                    help="extra KEY=VALUE pairs for the server environment, repeatable")
    args = ap.parse_args()

    extra = {}
    for pair in args.env:
        k, _, v = pair.partition("=")
        extra[k.strip()] = v

    env = dict(os.environ)
    env.pop("EYEKB_DEFAULT_DETAIL", None)
    env.update(extra)

    sp = StdioServerParameters(command=PY, args=[SRV], env=env)
    record = {"label": args.label, "env_extra": extra, "cases": {}}
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            record["tools"] = len(tools)
            record["tool_names"] = tools
            for cid, tool, argv in CASES:
                try:
                    res = await s.call_tool(tool, argv)
                    text = getattr(res.content[0], "text", "") if res.content else ""
                    try:
                        obj = json.loads(text)
                    except Exception:
                        obj = None
                    rows, cites = _citations_in_rows(obj) if obj is not None else (None, None)
                    record["cases"][cid] = {
                        "tool": tool,
                        "args": argv,
                        "chars": len(text),
                        "md5": hashlib.md5(text.encode()).hexdigest(),
                        "rows": rows,
                        "row_citations": cites,
                        "detail_field": obj.get("detail") if isinstance(obj, dict) else None,
                        "detail_applied": (obj.get("detail_applied")
                                           if isinstance(obj, dict) else None),
                        "has_detail_note": bool(isinstance(obj, dict)
                                                and obj.get("detail_note")),
                        "view_field": obj.get("view") if isinstance(obj, dict) else None,
                        "omitted_fields": (obj.get("omitted_fields")
                                           if isinstance(obj, dict) else None),
                        "is_error": bool(getattr(res, "isError", False)),
                    }
                except Exception as exc:  # a failed call is a reading, not a crash
                    record["cases"][cid] = {"tool": tool, "args": argv,
                                            "error": f"{type(exc).__name__}: {exc}"}

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(record, fh, indent=1, ensure_ascii=False, sort_keys=True)
    for cid, row in record["cases"].items():
        print(f"{cid:22s} chars={row.get('chars'):>7} rows={row.get('rows')} "
              f"cites={row.get('row_citations')} md5={row.get('md5','')[:8]}")


asyncio.run(main())