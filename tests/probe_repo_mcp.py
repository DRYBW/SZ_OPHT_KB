import asyncio, json, sys, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = os.environ.get("EYEKB_PROBE_PY", sys.executable)
SRV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server", "server.py")

async def run_case(env_extra, label):
    env = dict(os.environ)
    env.update(env_extra)
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            ver = getattr(init.server_info, "version", "?")
            tools = [t.name for t in (await s.list_tools()).tools]
            res = await s.call_tool("query_marker", {"genes": ["TMEM119","CX3CR1","P2RY12","C1QA","SALL1","CSF1R","AIF1"]})
            txt = res.content[0].text if res.content else ""
            data = json.loads(txt)
            rank = data.get("kb_celltype_ranking") or data.get("celltype_ranking") or []
            top = None
            if isinstance(rank, list) and rank:
                first = rank[0]
                top = first.get("celltype") or first.get("class") or str(first)[:40]
            # class-count: measure the ranking length
            n = len(rank) if isinstance(rank, list) else 0
            print(json.dumps({"case": label, "server_version": ver, "tools": len(tools), "top1_MG_query": top, "ranking_len": n}, ensure_ascii=False))
            return ver, len(tools), top, n

async def main():
    await run_case({"EYEKB_ACT_V6": "1"}, "ON_all")
    await run_case({"EYEKB_ACT_V6": "0"}, "OFF_pre")

asyncio.run(main())
