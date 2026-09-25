#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB P1c: MCP stdio 三工具自测 (真协议往返, 不走内部捷径)"""
import asyncio, json, sys, time

sys.path.insert(0, "/mnt/D/EyeKB/evals")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = "/mnt/D/EyeKB/mcp_server/server.py"
OUT = "/mnt/D/EyeKB/evals/selftest_tools_20260923.json"


def parse(res):
    """CallToolResult → dict。mcp 2.0: structured_content 优先, 回退 JSON text。"""
    if res.is_error:
        texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
        return {"__isError__": True, "text": texts}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        # MCPServer 可能包一层 {"result": {...}}
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


async def main():
    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    report = {"started": time.strftime("%F %T"), "checks": [], "pass": 0, "fail": 0}

    def check(name, ok, detail=""):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
        report["pass" if ok else "fail"] += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:120]}")

    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            check("initialize 握手", init.server_info.name == "eyekb",
                  f"{init.server_info.name} v{init.server_info.version}")
            tools = await s.list_tools()
            names = sorted(t.name for t in tools.tools)
            check("list_tools == 三工具", names == ["get_kb_page", "query_marker", "search_literature"], names)

            # ---- query_marker (轻量, 先测)
            r1 = parse(await s.call_tool("query_marker", {"cell_type": "MG"}))
            check("query_marker(cell_type=MG)", r1.get("found") and "RLBP1" in r1["markers"]["MG"], r1)
            r2 = parse(await s.call_tool("query_marker", {"genes": ["RHO", "GFAP", "NOPE"]}))
            hits = r2.get("gene_to_celltypes", {})
            check("query_marker(genes 反查)", hits.get("RHO") == ["Rod"] and hits.get("GFAP") == ["Astro"]
                  and hits.get("NOPE") == [], r2.get("celltype_ranking"))
            r3 = parse(await s.call_tool("query_marker", {}))
            check("query_marker(空=类目清单)", r3.get("mode") == "list" and len(r3.get("cell_types", [])) == 10, r3.get("cell_types"))

            # ---- get_kb_page + 白名单
            r4 = parse(await s.call_tool("get_kb_page", {"scope": "index"}))
            check("get_kb_page(index)", "OcularKB 文献索引" in r4.get("content", ""), r4.get("file"))
            r5 = parse(await s.call_tool("get_kb_page", {"scope": "tissue", "name": "cornea"}))
            check("get_kb_page(tissue=cornea)", r5.get("file", "").endswith("tissue-cornea.md") and len(r5.get("content", "")) > 1000, r5.get("file"))
            r6 = parse(await s.call_tool("get_kb_page", {"scope": "topic", "name": "../../etc/passwd"}))
            check("get_kb_page 越界拒绝", "error" in r6, r6.get("error"))
            r7 = parse(await s.call_tool("get_kb_page", {"scope": "topic", "name": "nonexistent_page"}))
            check("get_kb_page 不存在→回清单", "error" in r7 and r7.get("available"), len(r7.get("available", [])))

            # ---- search_literature (触发模型加载, 计时)
            t0 = time.time()
            r8 = parse(await s.call_tool("search_literature",
                                         {"cell_type": "Muller Glia", "species": "human",
                                          "tissue": "retina", "top_k": 5}))
            dt = time.time() - t0
            ok8 = (isinstance(r8, dict) and len(r8.get("results", [])) == 5
                   and all(("pmid" in x and "relevance_score" in x) for x in r8["results"]))
            check(f"search_literature 首轮({dt:.0f}s 含加载)", ok8, [x["pmid"] for x in r8.get("results", [])])
            t0 = time.time()
            r9 = parse(await s.call_tool("search_literature",
                                         {"cell_type": "corneal endothelium", "tissue": "cornea", "top_k": 3}))
            check(f"search_literature 复用({time.time()-t0:.0f}s)", len(r9.get("results", [])) == 3,
                  [x["pmid"] for x in r9.get("results", [])])

    json.dump(report, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\n== SELFTEST {report['pass']} PASS / {report['fail']} FAIL -> {OUT}")
    return 0 if report["fail"] == 0 else 1


sys.exit(asyncio.run(main()))
