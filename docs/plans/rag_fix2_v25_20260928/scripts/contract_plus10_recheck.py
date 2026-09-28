#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 all_list_plus10 失效两分句复证 (REVIEWER_LLM Q5 方法, 只读取证):
  ①set(pre)⊆current (超集关系) ②retina_interneuron:: 行数==10 ③绝对计数现值 (解释 43 期望为何过期)"""
import asyncio, json, sys
EYEKB = "/mnt/D/EyeKB"
sys.path.insert(0, f"{EYEKB}/mcp_server")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = f"{EYEKB}/mcp_server/server.py"

def parse(res):
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None

async def main():
    pre_all = json.load(open("/home/ubuntu/.hermes/kanban/boards/pi-briefing/workspaces/t_d07ab64f/marker_snapshot_pre.json"))["all_list"]["cell_types"]
    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    async with stdio_client(params) as (rd, wr):
        async with ClientSession(rd, wr) as s:
            await s.initialize()
            r = parse(await s.call_tool("query_marker", {}))
            ct = r["cell_types"]
            superset = set(pre_all) <= set(ct)
            ri = sum(1 for x in ct if x.startswith("retina_interneuron::"))
            out = {"clause1_superset_pre_current": superset,
                   "clause2_retina_interneuron_count_10": ri == 10,
                   "len_pre": len(pre_all), "len_current": len(ct),
                   "expected_by_contract": len(pre_all) + 10,
                   "verdict": "失效仅绝对计数半句 (前置 KB8泪腺/KB9 k9 合法注册使 all_list 增长先于本卡)"
                              if (superset and ri == 10) else "需深查"}
            print(json.dumps(out, ensure_ascii=False, indent=1))
            json.dump(out, open("/mnt/D/EyeKB/plans/rag_fix2_v25_20260928/out/CONTRACT_PLUS10_RECHECK_v25.json", "w"), ensure_ascii=False, indent=1)
asyncio.run(main())
