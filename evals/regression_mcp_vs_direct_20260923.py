#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB P1d 黄金集回归: 同一批查询, 直调 stage3_retrieve.retrieve() vs 经 MCP stdio 调用。
逐项一致 = PASS; 任何不一致 → 修复后重测, 不带病交付 (USER_DIRECTIVE_20260923 §5)。

查询批 = qa_v2.GOLDEN 10 retina 用例 + qa_v2.TISSUE_SPOT 全部 31 逐组织用例。
两侧统一: db=v2.0_2026-09, top_k=5, species/cell_type/tissue 透传。
"""
import asyncio, json, sys, time, difflib

EYEKB = "/mnt/D/EyeKB"
sys.path.insert(0, f"{EYEKB}/clients/ocularkb/rag/scripts")   # verbatim 复制品
sys.path.insert(0, f"{EYEKB}/mcp_server")

import stage3_retrieve as s3      # 直调对象
import qa_v2 as q                 # 黄金集用例来源
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = f"{EYEKB}/mcp_server/server.py"
OUT_JSON = f"{EYEKB}/evals/MCP_REGRESSION_20260923.json"
OUT_MD = f"{EYEKB}/evals/MCP_REGRESSION_20260923.md"


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
    """返回第一个不一致点 (类型/值), 用于定位。"""
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


async def main():
    cases = build_cases()
    print(f"回归用例: {len(cases)} (golden_retina 10 + tissue_spot {len(cases)-10})", flush=True)

    # ---- 直调侧 (本进程加载模型+库)
    t0 = time.time()
    direct = []
    for i, c in enumerate(cases):
        r = s3.retrieve(c["cell_type"], species=c["species"], top_k=5,
                        query=None, tissue=c["tissue"],
                        db_dir="/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09")
        # 直调与 MCP 侧同库 = v2.0_2026-09 (EyeKB 默认库, 见 EYEKB_DB_POINTER.yaml)
        direct.append(r)
        if i == 0:
            print(f"  直调首轮 {time.time()-t0:.0f}s (含模型/库加载)", flush=True)
    print(f"  直调侧完成 {len(direct)} 用例, {time.time()-t0:.0f}s", flush=True)

    # ---- MCP 侧 (真 stdio 往返)
    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    results = []
    nmatch = 0
    async with stdio_client(params) as (rd, wr):
        async with ClientSession(rd, wr) as s:
            await s.initialize()
            for c, dref in zip(cases, direct):
                t1 = time.time()
                res = parse(await s.call_tool("search_literature", {
                    "cell_type": c["cell_type"], "species": c["species"],
                    "tissue": c["tissue"], "top_k": 5}))
                same = (res == dref)
                diff = None if same else first_diff(dref, res)
                pmids = [x["pmid"] for x in dref.get("results", [])]
                row = {**c, "consistent": same, "diff": diff,
                       "n_results": len(dref.get("results", [])),
                       "top_pmids": pmids,
                       "scores": [x["relevance_score"] for x in dref.get("results", [])],
                       "secs_mcp": round(time.time() - t1, 2)}
                results.append(row)
                nmatch += int(same)
                print(f"[{'OK ' if same else 'DIFF'}] {c['group']:22s} {c['cell_type'][:30]:30s} "
                      f"pmids={','.join(pmids[:3])}... {'' if same else diff}", flush=True)

    verdict = nmatch == len(cases)
    out = {"date": "2026-09-23", "task": "EyeKB P1d MCP-vs-direct 黄金集回归",
           "n_cases": len(cases), "n_consistent": nmatch, "verdict": "PASS" if verdict else "FAIL",
           "db": "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09",
           "results": results}
    json.dump(out, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)

    with open(OUT_MD, "w") as f:
        f.write("# EyeKB P1d 黄金集回归报告 (MCP vs stage3 直调)\n\n")
        f.write(f"- 日期: 2026-09-23 | 用例: {len(cases)} (GOLDEN 10 retina + TISSUE_SPOT {len(cases)-10})\n")
        f.write(f"- 判据: 同一查询直调 stage3_retrieve.retrieve() 与经 MCP stdio 调用, "
                f"返回 JSON **逐项完全一致** (含 pmid 序、relevance_score、marker_genes、tissue_labels)\n")
        f.write(f"- 库: v2.0_2026-09 (EyeKB 默认库, 引用 OcularKB 现路径只读)\n\n")
        f.write(f"**判定: {nmatch}/{len(cases)} 一致 → {'PASS ✅' if verdict else 'FAIL ❌ (修复后重测)'}**\n\n")
        f.write("| 组 | cell_type | species | tissue | 一致 | top-5 PMID (两侧同) |\n|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['group']} | {r['cell_type']} | {r['species']} | {r['tissue']} | "
                    f"{'✅' if r['consistent'] else '❌ ' + str(r['diff'])} | {','.join(r['top_pmids'])} |\n")
        f.write("\n注: 本回归验证 MCP 服务层保真 (不劣化/不变形); v2.0 检索质量对 v1.0 基线的 "
                "recall 口径见 OcularKB 侧 QA_V2.md (OCB-RAG2), 两回事不混称。\n")
    print(f"\n== REGRESSION {nmatch}/{len(cases)} consistent → {'PASS' if verdict else 'FAIL'} -> {OUT_MD}")
    return 0 if verdict else 1


sys.exit(asyncio.run(main()))
