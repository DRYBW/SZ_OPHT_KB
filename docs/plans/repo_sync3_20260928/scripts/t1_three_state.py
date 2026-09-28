#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T1a+T1c — staging 仓副本起真 MCP stdio：
三态断言（人源零干预/鼠源拒答/B5=0 回退）——协调者独立探针 /tmp/probe_b5_coord.py 同款，
仓副本路径版（SRV=STG/mcp_server/server.py）；
+ probe_repo 系断言沿 b507 移植（版本/tools/Microglia 两态全等/KRT12 两态序全等/lacrimal 泄漏=0
  + k9 REGISTERED_DEFAULT_OFF 三态语义保持）。输出 out/t1_three_state.json。exit 0=全 PASS。"""
import asyncio
import json
import os
import sys
from pathlib import Path

STG = Path(os.environ.get("EYEKB_STG", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"))
PY = "/home/ubuntu/training-venv/bin/python"
SRV = str(STG / "mcp_server" / "server.py")
OUT = STG / "docs/plans/repo_sync3_20260928/out"
OUT.mkdir(parents=True, exist_ok=True)

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:280]})
    if not cond:
        fails.append([tag, str(detail)[:280]])


def parse(res):
    txt = res.content[0].text if res.content else "{}"
    try:
        return json.loads(txt)
    except Exception:
        return {"_raw": txt[:200]}


async def session(env_extra, calls):
    env = dict(os.environ)
    env.update(env_extra)
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)  # 显式全 env（MCP 默认白名单不含 EYEKB_* 先例）
    out = {}
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["_server_version"] = getattr(init.server_info, "version", "?")
            tools = await s.list_tools()
            out["_tools"] = sorted(t.name for t in tools.tools)
            out["_ver_desc"] = next((t.description[:60] for t in tools.tools if t.name == "query_marker"), "?")
            for label, genes in calls:
                d = parse(await s.call_tool("query_marker", {"genes": genes}))
                rank = d.get("celltype_ranking") or d.get("ranking") or []
                out[label] = {
                    "species": d.get("input_species"),
                    "named": d.get("no_named_ranking_for"),
                    "n_ranking": len(rank) if isinstance(rank, list) else "NA",
                    "top1": (rank[0].get("cell_type") if rank and isinstance(rank[0], dict) else (rank[0] if rank else None)) if isinstance(rank, list) else None,
                    "unranked": len(d.get("unranked_candidates") or []),
                    "canon": json.dumps(d, ensure_ascii=False, sort_keys=True),
                }
    return out


CALLS = [("HUM_KERA_ALDH3A1", ["KERA", "ALDH3A1"]),
         ("MOUSE_titlecase", ["Thy1", "Grin3a"]),
         ("MOUSE_GmRik", ["Gm3339", "Ccdc126", "Slc17a6"])]


async def main():
    # ---- T1a 三态 ----
    on = await session({}, CALLS)
    off = await session({"EYEKB_KBGOV_B5": "0"}, CALLS)
    ck("t1a-version", on["_server_version"] == "KB1v2-0.6-kbgov5" and off["_server_version"] == "KB1v2-0.6-kbgov5",
       (on["_server_version"], off["_server_version"]))
    ck("t1a-tools5", len(on["_tools"]) == 5 and on["_tools"] == off["_tools"], on["_tools"])
    ck("t1a-human-zero-intervention",
       on["HUM_KERA_ALDH3A1"]["n_ranking"] > 0 and on["HUM_KERA_ALDH3A1"]["species"] == "human_assumed",
       on["HUM_KERA_ALDH3A1"])
    ck("t1a-mouse-refuse-titlecase",
       on["MOUSE_titlecase"]["named"] == "mouse_input" and on["MOUSE_titlecase"]["n_ranking"] == 0
       and on["MOUSE_titlecase"]["unranked"] > 0, on["MOUSE_titlecase"])
    ck("t1a-mouse-refuse-gmrik",
       on["MOUSE_GmRik"]["named"] == "mouse_input" and on["MOUSE_GmRik"]["n_ranking"] == 0, on["MOUSE_GmRik"])
    ck("t1a-B5=0-rollback-present", off["MOUSE_titlecase"]["named"] != "mouse_input", off["MOUSE_titlecase"])
    ck("t1a-B5=0-human-canonical", off["HUM_KERA_ALDH3A1"]["named"] != "mouse_input", off["HUM_KERA_ALDH3A1"])
    # ---- T1c probe_repo 系（b507 移植）----
    micro_genes = ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]
    krt_genes = ["KRT12", "PAX6", "ALDH1A1", "MLANA", "TYR", "SOX10", "LMX1B", "KERA"]
    pr = await session({}, [("MICRO", micro_genes), ("KRT12", krt_genes)])
    pr_off = await session({"EYEKB_KBGOV_B5": "0"}, [("MICRO", micro_genes), ("KRT12", krt_genes)])
    ck("t1c-microglia-top1-stable", pr["MICRO"]["top1"] == pr_off["MICRO"]["top1"] and pr["MICRO"]["top1"] is not None,
       (pr["MICRO"]["top1"], pr_off["MICRO"]["top1"]))
    ck("t1c-microglia-len-stable", pr["MICRO"]["n_ranking"] == pr_off["MICRO"]["n_ranking"],
       (pr["MICRO"]["n_ranking"], pr_off["MICRO"]["n_ranking"]))
    # b507 口径=两态排序全等（cell_type 序列+n_shared），非全响应等（ON 态按设计附加治理字段）
    import json as _J
    env2 = dict(os.environ)
    sp2 = StdioServerParameters(command=PY, args=[SRV], env=env2)
    async def rank_seq(env_extra):
        spx = StdioServerParameters(command=PY, args=[SRV], env={**os.environ, **env_extra})
        async with stdio_client(spx) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                d = parse(await s.call_tool("query_marker", {"genes": krt_genes}))
                rank = d.get("celltype_ranking") or []
                return [(x.get("cell_type"), x.get("n_shared")) for x in rank]
    rk_on = await rank_seq({})
    rk_off = await rank_seq({"EYEKB_KBGOV_B5": "0"})
    ck("t1c-krt12-order-stable", rk_on == rk_off, f"n={len(rk_on)}")
    # lacrimal 泄漏 + k9 默认 OFF：list-mode（query_marker 无参 = 默认 all）
    lst_on = await session({}, [("DEFAULT_LIST", [])])
    # 空 genes → 走 list 分支
    dlist = lst_on["DEFAULT_LIST"]
    # list-mode 无 species 治理面（管辖面=genes-mode），单独取原始体
    env = dict(os.environ)
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            dl = parse(await s.call_tool("query_marker", {}))
            ct = dl.get("cell_types", [])
            k9n = {"Melanocyte", "Schwann", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}
            ck("t1c-no-lacrimal-leak", not any(("lacrimal" in str(x).lower() or "泪腺" in str(x)) for x in ct), len(ct))
            ck("t1c-k9-not-in-default", not (set(ct) & k9n), f"n_classes={len(ct)}")
            k9 = parse(await s.call_tool("query_marker", {"library": "k9_ocs"}))
            ck("t1c-k9-route-reachable", sorted(k9.get("cell_types", [])) == sorted(k9n), k9.get("cell_types"))
    res = {"on": {k: v for k, v in on.items()}, "off": {k: v for k, v in off.items()},
           "checks": checks, "fails": fails,
           "RESULT": "ALL_PASS" if not fails else "FAIL"}
    (OUT / "t1_three_state.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"T1a/T1c checks={len(checks)} fails={len(fails)} RESULT={'ALL_PASS' if not fails else 'FAIL'}")
    for f_ in fails:
        print("FAIL:", f_)
    sys.exit(0 if not fails else 1)


asyncio.run(main())
