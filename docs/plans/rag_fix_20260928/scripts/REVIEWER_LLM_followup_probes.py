#!/usr/bin/env python3
"""REVIEWER_LLM Q4/Q5 补验: (a) 问题链 PMID 是否混入门①答案/门③消除链
   (b) all_list_plus10 契约两分句现状 (绝对计数 vs 超集关系 vs retina_interneuron::10)"""
import json, sys, asyncio

PLAN="/mnt/D/EyeKB/plans/rag_fix_20260928"
bad={"38528295","35590283","37381815","36167259","24449362","29561967","41349939","35920172"}
g1=json.load(open(f"{PLAN}/out/GOLDEN41_OFFSTATE_ragfix.json"))
top5=set()
for r in g1["results"]:
    top5.update(r["top_pmids"])
closed=set(l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip())
print("Q4a bad ∩ golden41-top5:", sorted(bad.intersection(top5)))
print("Q4b bad ∩ closed64:", sorted(bad.intersection(closed)))

# Q5: 现时 all_list 对预快照的两分句
PRE='/home/ubuntu/.hermes/kanban/boards/pi-briefing/workspaces/t_d07ab64f/marker_snapshot_pre.json'
pre=json.load(open(PRE))['all_list']['cell_types']
sys.path.insert(0,"/mnt/D/EyeKB/mcp_server")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
def parse(res):
    sc=getattr(res,"structured_content",None)
    if isinstance(sc,dict):
        return sc.get("result",sc) if set(sc.keys())=={"result"} else sc
    texts=[c.text for c in res.content if getattr(c,"type","")=="text"]
    return json.loads(texts[0]) if texts else None
async def m():
    p=StdioServerParameters(command="/home/ubuntu/training-venv/bin/python",
                            args=["/mnt/D/EyeKB/mcp_server/server.py"],env=None)
    async with stdio_client(p) as (rd,wr):
        async with ClientSession(rd,wr) as s:
            await s.initialize()
            r=parse(await s.call_tool("query_marker",{}))
            ct=r["cell_types"]
            print(json.dumps({"Q5":{
                "n_now":len(ct),"n_pre":len(pre),"abs_plus10_expect":len(pre)+10,
                "superset_pre":bool(set(pre).issubset(set(ct))),
                "retina_interneuron_count":sum(1 for x in ct if x.startswith("retina_interneuron::"))}}))
asyncio.run(m())
