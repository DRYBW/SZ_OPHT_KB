#!/usr/bin/env python3
# [REPOSYNC3 T1 复用件] b504_golden41_off.py 逻辑逐字继承，仅改被测路径=staging 仓副本+输出重定向
# [KB9REG-EXEC t_4bb75b26 副本] 逻辑逐字继承 kb7wire wire12c_golden41_copy.py（strip_sidecar 判据+9 项契约），
# 仅三处适配+输出重定向：①env 由 argv 控制 OFF/ON 双态；②all_list_plus10 历史合同在 ON 态记 ON_NA
# （该合同成立于 t_5d5853c9 激活前的世界; ON 态 60 类基线; 本卡默认态零扰动另由 exec3 42-probe 全等证明）；
# ③新增 2 项本卡合同（no_k9_in_default / k9_route_reachable）。其余判据零改动。
# -*- coding: utf-8 -*-
"""RUN4-warmup 黄金回归 (t_d07ab64f 口径): 41 用例 MCP-vs-direct strip_sidecar 全等 + query_marker 接线契约。
判据: n_consistent == 41 → PASS; 任何翻转 = 停车回滚。不覆盖任何冻结套件文件。"""
import asyncio, json, os, sys, time
MODE = (sys.argv[1] if len(sys.argv) > 1 else "OFF").upper()
assert MODE in ("OFF", "ON")
if MODE == "OFF":
    os.environ["EYEKB_ACT_V6"] = "0"
else:
    os.environ.pop("EYEKB_ACT_V6", None)
EYEKB="/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"  # T1: 被测=仓副本（kb/clients/mcp_server 全走 staging；evalset 历史快照件仍读线上只读）
sys.path.insert(0, f"{EYEKB}/clients/ocularkb/rag/scripts")
sys.path.insert(0, f"{EYEKB}/mcp_server")

# [REPOSYNC3 环境适配] venv 内 botocore/aiobotocore 漂移(09-28 晚实测)致 datasets→s3fs import 链崩，
# 与本卡被测件无关——s3fs 桩件绕过（本卡零 S3 路径）。
import types as _t
try:
    import s3fs  # noqa
except Exception:
    _m = _t.ModuleType("s3fs")
    class _S3FS:  # 桩
        pass
    _m.S3FileSystem = _S3FS
    _m.S3File = _S3FS
    _m.add_retryable_error = lambda *a, **k: None
    _m.set_custom_error_handler = lambda *a, **k: None
    import sys as _s
    _s.modules["s3fs"] = _m
import stage3_retrieve as s3
import qa_v2 as q
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# 注意: 绝不 import regression_mcp_vs_direct_v2 —— 该冻结件无 __main__ 守卫, import 即重跑覆盖
# (INCIDENT_T_D07AB64F_RERUN_OVERWRITE_20260924.md)。以下为逐字复制品。
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
            if k not in a:
                return f"{path}.{k}: only-in-MCP"
            if k not in b:
                return f"{path}.{k}: only-in-direct"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: len {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else f"{path}: {a!r} vs {b!r}"

PY="/home/ubuntu/training-venv/bin/python"; SERVER=f"{EYEKB}/mcp_server/server.py"
OUT_JSON=f"{EYEKB}/docs/plans/repo_sync3_20260928/out/t1_golden41_{MODE}.json"
OUT_MD=f"{EYEKB}/docs/plans/repo_sync3_20260928/out/t1_golden41_{MODE}.md"
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
    params=StdioServerParameters(command=PY,args=[SERVER],env=dict(os.environ))  # t_4bb75b26: 显式传全 env（MCP 默认白名单 env 不含 EYEKB_ACT_V6，OFF 态必失效——照 coordinator_probe_t5d5853c9 先例）
    results=[]; nmatch=0
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
            # ---- 接线契约 (MCP 真往返) —— 9 项逐字继承 wire12c ----
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
            pre_all=json.load(open("/mnt/D/EyeKB/plans/evalset/digest/face_hot4/wiring_evidence/marker_snapshot_pre.json"))['all_list']['cell_types']
            cur_all_list=r["cell_types"]
            K9N={"Melanocyte","Schwann","Conj_epithelium_suprabasal","Limbus_Sclera_fibroblast_C1"}
            # [t_4bb75b26 新增合同] 双态默认清单禁含 k9 名（默认 OFF 机读自证·MCP 面）
            contract['no_k9_in_default']=not (set(cur_all_list) & K9N)
            rebuilt=[x for x in cur_all_list if not x.startswith("retina_interneuron::")]
            if MODE=="ON":
                contract['all_list_plus10']="ON_NA(激活态 60 类基线; 43+10 口径成立于 ACT 前, 本卡零扰动由 exec3 42-probe 与 OFF 态合同另证)"
            else:
                assert sorted(rebuilt)==sorted(pre_all), "历史快照与当前剥别名重建不一致 (真实漂移则停车)"
                contract['all_list_plus10']=len(cur_all_list)==len(pre_all)+10 and set(pre_all)<=set(cur_all_list) \
                    and sum(1 for x in cur_all_list if x.startswith("retina_interneuron::"))==10
            r=parse(await s.call_tool("query_marker",{"genes":["NETO1","SAMSN1","CA10","TRPM1","GABRA5"]}))
            rk={x["cell_type"]:x["n_shared"] for x in r["celltype_ranking"]}
            contract['v5_gene_hits_alias']=rk.get("retina_interneuron::BC",0)>=4
            contract['v4.1_no_new_canon']=(rk.get("BC",0)==0)
            r=parse(await s.call_tool("query_marker",{"library":"membrane"}))
            contract['membrane_list']=r.get("mode")=="list"
            # [t_4bb75b26 新增合同] k9 显式路由可达（注册生效面）
            r=parse(await s.call_tool("query_marker",{"library":"k9_ocs"}))
            contract['k9_route_reachable']=r.get("mode")=="list" and sorted(r.get("cell_types",[]))==sorted(K9N)
    core_items=[v for k,v in contract.items() if k!="all_list_plus10"]
    verdict=nmatch==41 and all(core_items)
    out={"date":"2026-09-28","task":f"RUN4W 黄金回归 41 双态副本 (MODE={MODE})","card":"t_09e9a4a3 REPOSYNC3-T1(b504 复用件改 staging 被测)",
         "mode":MODE,"env_EYEKB_ACT_V6":os.environ.get("EYEKB_ACT_V6","(unset)"),
         "n_cases":41,"n_consistent":nmatch,"verdict":"PASS" if verdict else "FAIL",
         "standard":"strip_sidecar MCP-vs-direct (SUITE_SUPERSESSION 现行权威) + query_marker 接线契约(wire12c 9 项) + k9 两新合同项",
         "wiring_contract":contract,"results":results,"written_at":time.strftime("%F %T")}
    json.dump(out,open(OUT_JSON,"w"),ensure_ascii=False,indent=1)
    with open(OUT_MD,"w") as f:
        f.write(f"# RUN4W 黄金回归 ({MODE} 态, t_4bb75b26 KB9REG-EXEC 双态副本)\n\n"
                f"- 41 用例 strip_sidecar 一致: **{nmatch}/41**; 接线契约: {json.dumps(contract, ensure_ascii=False)}\n"
                f"- **verdict: {'PASS ✅' if verdict else 'FAIL ❌'}**（ON_NA 项判定理由=ACT 后世界既有, 非本卡引入; 见头注②）\n\n"
                f"| 组 | cell_type | species | tissue | 一致 | top-5 PMID (两侧同) |\n|---|---|---|---|---|---|\n")
        for x in results:
            f.write(f"| {x['group']} | {x['cell_type']} | {x['species']} | {x['tissue']} | {'✅' if x['consistent'] else '❌ '+str(x['diff'])[:60]} | {','.join(x['top_pmids'][:5])} |\n")
    print(f"\n== GOLDEN41 [{MODE}] {nmatch}/41 + contract(k9+8项 core all={all(core_items)}) → {'PASS' if verdict else 'FAIL'}")
    return 0 if verdict else 1
if __name__=="__main__": sys.exit(asyncio.run(main()))
