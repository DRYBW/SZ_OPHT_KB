#!/usr/bin/env python
"""Closure probe: start the real stdio server and confirm the shipped defaults."""
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO = "/home/ubuntu/EYEKB_REPO"
PY = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"
SRV = os.path.join(REPO, "mcp_server", "server.py")

CASES = [
    ("cornea_default", {"scope": "tissue", "name": "cornea"}),
    ("cornea_full", {"scope": "tissue", "name": "cornea", "detail": "full"}),
    ("cornea_outline", {"scope": "tissue", "name": "cornea", "detail": "outline"}),
    ("inclusions_default", {"scope": "topic", "name": "INCLUSIONS_RECENT"}),
    ("models_default", {"scope": "topic", "name": "models"}),
    ("index_default", {"scope": "index"}),
]

async def run(label):
    params = StdioServerParameters(command=PY, args=[SRV], env=dict(os.environ))
    out = {}
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for name, args in CASES:
                res = await s.call_tool("get_kb_page", args)
                text = "".join(c.text for c in res.content if hasattr(c, "text"))
                fol = getattr(res, "structured_content", None) or {}
                out[name] = {"chars": len(text),
                             "view": fol.get("view") or fol.get("detail_applied"),
                             "md5_fields": fol.get("md5")}
                print(f"{label} {name:20s} chars={len(text):7d} view={fol.get('view') or fol.get('detail_applied')}")
    return out

async def main():
    a = await run("plain ")
    os.environ["EYEKB_DEFAULT_DETAIL"] = "full"
    b = await run("envfull")
    print("\n--- revert check (EYEKB_DEFAULT_DETAIL=full) ---")
    for k in ("cornea_default", "inclusions_default", "models_default"):
        print(f"{k:20s} plain={a[k]['chars']:7d}  envfull={b[k]['chars']:7d}  "
              f"{'MATCHES pre-change full text' if b[k]['chars'] > 20000 or k=='index_default' else 'SMALL'}")
    print("\ncornea_default envfull == cornea_full plain ?",
          b["cornea_default"]["chars"] == a["cornea_full"]["chars"])

asyncio.run(main())