# -*- coding: utf-8 -*-
"""dump_panel.py -- drive the fixed 12-call tool panel over stdio and store the FULL response
texts (not digests), for field-level drift attribution between two trees.

Usage: <THIS_PY runs under the training venv> python3 dump_panel.py <tree_root> <out.json>
The probe module is imported from <tree_root>/tests so SRV/REPO bind to that tree.
Zero writes besides the out.json; zero network (stdio pipes only).
"""
import asyncio, hashlib, json, os, pathlib, sys

tree = pathlib.Path(sys.argv[1]).resolve()
out = sys.argv[2]
sys.path.insert(0, str(tree / "tests"))
import probe_tool_panel_identity as P  # noqa: E402


async def drive_full():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    py = os.environ.get("EYEKB_PROBE_PY", sys.executable)
    responses, refused = {}, []
    sp = StdioServerParameters(command=py, args=[P.SRV], env=dict(os.environ))
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = sorted(t.name for t in (await s.list_tools()).tools)
            for name, args in P.PANEL:
                key = f"{name}:{json.dumps(args, sort_keys=True)}"
                res = await s.call_tool(name, args)
                if getattr(res, "is_error", getattr(res, "isError", False)):
                    refused.append(key)
                parts = [getattr(c, "text", "") or "" for c in (res.content or [])]
                txt = "".join(parts)
                txt = txt.replace(str(P.REPO), "<REPO>")
                responses[key] = txt
    return {"responses": responses, "refused": refused, "tools": tools,
            "provenance": P.provenance(), "interpreter": py}


run = asyncio.run(drive_full())
doc = {"tree": str(tree), "srv": P.SRV, "tools": run["tools"],
       "provenance": run["provenance"], "interpreter": run["interpreter"],
       "refused": run["refused"], "responses": run["responses"],
       "per_call_md5": {k: hashlib.md5(v.encode()).hexdigest()
                        for k, v in run["responses"].items()}}
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps({"tree": str(tree), "n_calls": len(run["responses"]),
                  "refused": run["refused"],
                  "per_call_md5": doc["per_call_md5"]}, indent=1))
