#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB-P1opt O4: MCP stdio 自测 v2 — query_marker 多库支持验收。
v1 自测 (selftest_tools_20260923.py) 保留为历史产物不重跑; 本文件覆盖:
  ① 三工具握手/白名单等 v1 全部等价检查;
  ② 旧行为复现: library=retina → 10 类, RHO/GFAP 反查与 v1 断言逐项相等;
  ③ 新能力: 默认 all=31 类; membrane 正查/反查带溯源; 冲突消歧字段存在。
"""
import asyncio, json, sys, time

sys.path.insert(0, "/mnt/D/EyeKB/evals")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = "/mnt/D/EyeKB/mcp_server/server.py"
OUT = "/mnt/D/EyeKB/evals/selftest_tools_v2_20260923.json"


def parse(res):
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
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

            # ---- 旧行为复现 (v1 selftest 等价断言, library=retina)
            r1 = parse(await s.call_tool("query_marker", {"cell_type": "MG", "library": "retina"}))
            check("retina: cell_type=MG", r1.get("found") and "RLBP1" in r1["markers"]["MG"], r1.get("markers"))
            r2 = parse(await s.call_tool("query_marker", {"genes": ["RHO", "GFAP", "NOPE"], "library": "retina"}))
            hits = r2.get("gene_to_celltypes", {})
            check("retina: genes 反查 (v1 断言等价)",
                  hits.get("RHO") == ["Rod"] and hits.get("GFAP") == ["Astro"] and hits.get("NOPE") == [],
                  r2.get("celltype_ranking"))
            r3 = parse(await s.call_tool("query_marker", {"library": "retina"}))
            check("retina: 类目清单==10 (v1 断言等价)",
                  r3.get("mode") == "list" and len(r3.get("cell_types", [])) == 10, r3.get("cell_types"))

            # ---- 新能力 (membrane / all)
            r4 = parse(await s.call_tool("query_marker", {}))  # 默认 all
            ct_all = r4.get("cell_types", [])
            check("all: 类目清单==31 (10+21)", len(ct_all) == 31 and "Endo" in ct_all and "pDC" in ct_all,
                  len(ct_all))
            r5 = parse(await s.call_tool("query_marker", {"cell_type": "Endo"}))
            check("membrane: Endo 正查含溯源",
                  r5.get("found") and "CLDN5" in r5["markers"]["Endo"]
                  and "provenance_Endo" in r5.get("detail", {}),
                  list(r5.get("detail", {}).keys()))
            prov_endo = r5.get("detail", {}).get("provenance_Endo", {}).get("CLDN5", [])
            check("membrane: CLDN5 溯源三态 (canonical+data_driven rank1+pmid_context)",
                  any(e["type"] == "canonical" for e in prov_endo)
                  and any(e["type"] == "data_driven" and e.get("wilcoxon_rank") == 1 for e in prov_endo)
                  and any(e["type"] == "pmid_context" for e in prov_endo),
                  [e["type"] for e in prov_endo])
            r6 = parse(await s.call_tool("query_marker", {"genes": ["CLDN5", "FCN1", "LILRA4"]}))
            h6 = r6.get("gene_to_celltypes", {})
            check("membrane: genes 反查 Endo/Mono_Classical/pDC",
                  h6.get("CLDN5") == ["Endo"] and h6.get("FCN1") == ["Mono_Classical"] and h6.get("LILRA4") == ["pDC"],
                  h6)
            r7 = parse(await s.call_tool("query_marker", {"cell_type": "Micro"}))
            check("跨库: Micro detail 仍返回 (retina micro_detail)",
                  r7.get("found") and "micro_detail" in r7.get("detail", {}), r7.get("detail", {}).keys())
            r8 = parse(await s.call_tool("query_marker", {"genes": ["RHO", "CLDN5"]}))
            check("all: 反查 celltype_ranking 带 library 字段",
                  all("library" in x for x in r8.get("celltype_ranking", [])),
                  r8.get("celltype_ranking", [])[:2])
            check("provenance.files 双库分列",
                  len(r8.get("provenance", {}).get("files", [])) == 2
                  and r8.get("provenance", {}).get("conflicts") == [], r8.get("provenance", {}).get("files"))

            # ---- get_kb_page + 白名单 (v1 等价)
            r9 = parse(await s.call_tool("get_kb_page", {"scope": "topic", "name": "../../etc/passwd"}))
            check("get_kb_page 越界拒绝", "error" in r9, r9.get("error"))
            r10 = parse(await s.call_tool("get_kb_page", {"scope": "index"}))
            check("get_kb_page(index)", "OcularKB 文献索引" in r10.get("content", ""), r10.get("file"))

            # ---- search_literature 冒烟 (行为归 41 项回归, 此处只证明可用)
            t0 = time.time()
            r11 = parse(await s.call_tool("search_literature",
                                          {"cell_type": "pericyte", "species": "human", "top_k": 3}))
            check(f"search_literature 冒烟({time.time()-t0:.0f}s)",
                  isinstance(r11, dict) and len(r11.get("results", [])) == 3,
                  [x["pmid"] for x in r11.get("results", [])])

    json.dump(report, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\n== SELFTEST-V2 {report['pass']} PASS / {report['fail']} FAIL -> {OUT}")
    return 0 if report["fail"] == 0 else 1


sys.exit(asyncio.run(main()))
