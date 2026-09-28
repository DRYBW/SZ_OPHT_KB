#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 gate1 (t_b94d0999): 黄金 41 用例 MCP-vs-direct off 态全等 (strip_sidecar 现行权威口径),
判据逐字=克隆 gate1_golden41_offstate_v25.py (t_6848d3de)；附加任务书明令:
top-5 PMID 逐字对 rag_fix2 基线 (out/GOLDEN41_OFFSTATE_ragfix2.json) 零漂移 (diff=0)。
禁 GPU: server/stage3 全程 CPU (沿前轮先例)。不覆盖任何冻结套件文件。
注意: 绝不 import regression_mcp_vs_direct_v2 (无 __main__ 守卫, import 即重跑覆盖)。"""
import asyncio, json, sys, time
EYEKB="/mnt/D/EyeKB"
sys.path.insert(0, f"{EYEKB}/clients/ocularkb/rag/scripts")
sys.path.insert(0, f"{EYEKB}/mcp_server")
import stage3_retrieve as s3
import qa_v2 as q
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
def parse(res):
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None
def build_cases():
    cases = []
    for c in q.GOLDEN:
        cases.append({"group": "golden_retina", "cell_type": c["cell_type"],
                      "species": c["species"], "tissue": "retina"})
    for tissue, rows in q.TISSUE_SPOT.items():
        for c in rows:
            cases.append({"group": f"spot_{tissue}", "cell_type": c["cell_type"],
                          "species": c["species"], "tissue": tissue})
    return cases
def first_diff(a, b, path=""):
    if type(a) is not type(b):
        return f"{path}: type {type(a).__name__} vs {type(b).__name__}"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: return f"{path}.{k}: only-in-MCP"
            if k not in b: return f"{path}.{k}: only-in-direct"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d: return d
        return None
    if isinstance(a, list):
        if len(a) != len(b): return f"{path}: len {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d: return d
        return None
    return None if a == b else f"{path}: {a!r} vs {b!r}"
PY="/home/ubuntu/training-venv/bin/python"; SERVER=f"{EYEKB}/mcp_server/server.py"
PLAN3="/mnt/D/EyeKB/plans/rag_fix3_20260928"
BASE2="/mnt/D/EyeKB/plans/rag_fix2_v25_20260928/out/GOLDEN41_OFFSTATE_ragfix2.json"
OUT_JSON=f"{PLAN3}/out/GOLDEN41_OFFSTATE_ragfix3.json"; OUT_MD=f"{PLAN3}/out/GOLDEN41_OFFSTATE_ragfix3.md"
SIDECAR_KEYS={"inclusion_reason","reason_confidence","reason_method","inclusion_reasons",
              "claim_relation","evidence_context","evidence_verification_status"}
def strip_sidecar(o):
    if isinstance(o,dict): return {k:strip_sidecar(v) for k,v in o.items() if k not in SIDECAR_KEYS}
    if isinstance(o,list): return [strip_sidecar(x) for x in o]
    return o
async def main():
    cases=build_cases(); assert len(cases)==41
    t0=time.time(); direct=[]
    for c in cases:
        direct.append(s3.retrieve(c["cell_type"],species=c["species"],top_k=5,query=None,
                                  tissue=c["tissue"],db_dir="/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09"))
    print(f"direct side done {len(direct)} {time.time()-t0:.0f}s",flush=True)
    params=StdioServerParameters(command=PY,args=[SERVER],env=None); results=[]; nmatch=0
    async with stdio_client(params) as (rd,wr):
        async with ClientSession(rd,wr) as s:
            await s.initialize()
            for c,dref in zip(cases,direct):
                res=parse(await s.call_tool("search_literature",{"cell_type":c["cell_type"],
                    "species":c["species"],"tissue":c["tissue"],"top_k":5}))
                same=strip_sidecar(res)==strip_sidecar(dref)
                diff=None if same else first_diff(strip_sidecar(dref),strip_sidecar(res))
                pmids=[x["pmid"] for x in dref.get("results",[])]
                results.append({**c,"consistent":same,"diff":diff,"top_pmids":pmids})
                nmatch+=int(same)
                print(f"[{'OK ' if same else 'DIFF'}] {c['group']:22s} {c['cell_type'][:30]:30s} {'' if same else diff}",flush=True)
            contract={}
            r=parse(await s.call_tool("query_marker",{"library":"retina"}))
            contract['retina_list10']=r.get("mode")=="list" and len(r.get("cell_types",[]))==10
            r=parse(await s.call_tool("query_marker",{"cell_type":"BC","library":"retina"}))
            contract['retina_BC_v4.1_5genes']=len(r["markers"]["BC"])==5
            r=parse(await s.call_tool("query_marker",{"cell_type":"BC","library":"retina_interneuron"}))
            contract['v5_BC_pure']=len(r["markers"]["BC"])==50 and r["provenance"]["files"][0]["library"]=="retina_interneuron"
            r=parse(await s.call_tool("query_marker",{"cell_type":"AC","library":"retina_interneuron"}))
            contract['v5_AC_49']=len(r["markers"]["AC"])==49
            r=parse(await s.call_tool("query_marker",{"cell_type":"HC","library":"retina_interneuron"}))
            contract['v5_HC_31']=len(r["markers"]["HC"])==31
            r=parse(await s.call_tool("query_marker",{}))
            pre_all=json.load(open("/home/ubuntu/.hermes/kanban/boards/pi-briefing/workspaces/t_d07ab64f/marker_snapshot_pre.json"))['all_list']['cell_types']
            ct_all=r["cell_types"]
            contract['all_list_plus10']=len(ct_all)==len(pre_all)+10 and set(pre_all)<=set(ct_all) \
                and sum(1 for x in ct_all if x.startswith("retina_interneuron::"))==10
            superset=set(pre_all)<=set(ct_all); n_reti=sum(1 for x in ct_all if x.startswith("retina_interneuron::"))
            r=parse(await s.call_tool("query_marker",{"genes":["NETO1","SAMSN1","CA10","TRPM1","GABRA5"]}))
            rk={x["cell_type"]:x["n_shared"] for x in r["celltype_ranking"]}
            contract['v5_gene_hits_alias']=rk.get("retina_interneuron::BC",0)>=4
            contract['v4.1_no_new_canon']=(rk.get("BC",0)==0)
            r=parse(await s.call_tool("query_marker",{"library":"membrane"}))
            contract['membrane_list']=r.get("mode")=="list"
    # top5 逐字对 rag_fix2 基线
    base=json.load(open(BASE2))
    bmap={ (x["group"],x["cell_type"],x["species"]): x["top_pmids"] for x in base["results"]}
    drift=[]
    for x in results:
        k=(x["group"],x["cell_type"],x["species"])
        if bmap.get(k)!=x["top_pmids"]:
            drift.append({"case":k,"ragfix2":bmap.get(k),"ragfix3":x["top_pmids"]})
    verdict=nmatch==41 and all(contract.values()) and not drift
    top5_zero_drift_ok = not drift
    out={"date":"2026-09-28","task":"RAGFIX3 gate1 黄金回归 41 off态全等 (克隆 ragfix2 runner, 判据逐字) + top5 对 ragfix2 基线逐字","card":"t_b94d0999",
         "n_cases":41,"n_consistent":nmatch,"verdict":"PASS" if verdict else "FAIL",
         "top5_vs_ragfix2_baseline":"zero-drift" if top5_zero_drift_ok else "DRIFT",
         "top5_drift_detail":drift,
         "standard":"strip_sidecar MCP-vs-direct (SUITE_SUPERSESSION 现行权威) + query_marker 接线契约",
         "wiring_contract":contract,"wiring_contract_plus10_clauses":{"superset_relation":superset,"reti_count_10":n_reti==10},
         "results":results,"written_at":time.strftime("%F %T")}
    json.dump(out,open(OUT_JSON,"w"),ensure_ascii=False,indent=1)
    with open(OUT_MD,"w") as f:
        f.write(f"# RAGFIX3 黄金回归 (gate1, off 态)\n\n- 用例 41 = GOLDEN 10 retina + TISSUE_SPOT 31; 判据 = strip_sidecar 全等 (现行权威口径); top5 逐字对 ragfix2 基线\n- **{nmatch}/41 consistent; top5 漂移 {len(drift)}; 接线契约 {sum(contract.values())}/{len(contract)} → {'PASS ✅' if verdict else 'FAIL ❌'}**\n\n| 组 | cell_type | species | tissue | 一致 | top-5 PMID (两侧同) |\n|---|---|---|---|---|---|\n")
        for x in results:
            f.write(f"| {x['group']} | {x['cell_type']} | {x['species']} | {x['tissue']} | {'✅' if x['consistent'] else '❌ ' + str(x['diff'])[:60]} | {','.join(x['top_pmids'][:5])} |\n")
        f.write("\n## 接线契约 (MCP stdio 真往返)\n\n")
        for k,v in contract.items(): f.write(f"- {k}: {'✅' if v else '❌'}\n")
    print(f"\n== RAGFIX3 GOLDEN {nmatch}/41 + top5-drift {len(drift)} + contract {sum(contract.values())}/{len(contract)} → {'PASS' if verdict else 'FAIL'}")
    return 0 if verdict else 1
if __name__=="__main__": sys.exit(asyncio.run(main()))
