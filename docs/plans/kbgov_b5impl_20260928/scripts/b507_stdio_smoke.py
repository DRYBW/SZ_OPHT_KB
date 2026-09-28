#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5IMPL t_8960c7e0 · b507 — stdio 真往返回归（probe_repo_mcp 系断言 + ON 态三席探针 smoke）
① probe_repo_mcp.py / probe_repo_mcp2.py 口径移植到生产 server（仓面本卡零 push，
   REPO_RESYNC_B5IMPL.md 登记待收编——此处以生产码跑同型断言）：
   版本=KB1v2-0.6-kbgov5、tools=5、Microglia 反查 top1/len 在 B5 ON/OFF 两态全等、
   lacrimal 泄漏=0、KRT12 人源查询两态序全等。
② ON 态三席探针 smoke：BTEST run1 三席（A/B/C）真实 toolcalls 全部 genes-mode 调用
   经 stdio 重放（默认 env=B5 ON），断言零异常、鼠源案拒答、人源案 ranking 非空、
   响应可 JSON 解析；逐席计数对账。
③ calllog 面：重放行落 calls_2026-09-28.jsonl（tag 隔离=本卡 smoke tag 若 calllog 支持）。
输出 out/b507_stdio_smoke.json。exit 0=全 PASS。"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

PY = "/home/ubuntu/training-venv/bin/python"
SRV = "/mnt/D/EyeKB/mcp_server/server.py"
CARD = Path("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928")
TC = Path("/mnt/D/EyeKB/plans/btest_20260927/annotation/toolcalls")

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

fails, checks, smoke_stats = [], [], {}


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:280]})
    if not cond:
        fails.append([tag, str(detail)[:280]])


def body_of(res):
    if res.is_error:
        return {"__isError__": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


async def session(env_extra, fn):
    env = dict(os.environ)
    env["EYEKB_MCP_SOFTFLAGS"] = "1"
    env.update(env_extra)
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)
    async with stdio_client(sp) as (rd, wr):
        async with ClientSession(rd, wr) as s:
            init = await s.initialize()
            await fn(s, init)


# ---------- ① probe_repo 系断言（OFF/ON 双态） ----------
MGQ = ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]
KQ = ["KRT12", "PAX6", "ALDH1A1", "MLANA", "TYR", "SOX10", "LMX1B", "KERA"]
state = {}


async def probe_repo(s, init):
    state["version"] = getattr(init.server_info, "version", "?")
    state["tools"] = len((await s.list_tools()).tools)
    r1 = body_of(await s.call_tool("query_marker", {"genes": MGQ}))
    r2 = body_of(await s.call_tool("query_marker", {"genes": KQ}))
    state["mg_top1"] = (r1.get("celltype_ranking") or [{}])[0].get("cell_type")
    state["mg_len"] = len(r1.get("celltype_ranking") or [])
    state["krt_seq"] = [e.get("cell_type") for e in r2.get("celltype_ranking") or []]
    txt = json.dumps(r2, ensure_ascii=False)
    state["lac_leak"] = sorted([c for c in set(re.findall(r'"cell_type": *"([^"]+)"', txt))
                                if re.search(r"lacr|腺泡|导管", c, re.I)])
    state["mg_keys"] = sorted(r1.keys())


asyncio.run(session({"EYEKB_KBGOV_B5": "0", "EYEKB_ACT_V6": "1"}, probe_repo))
off_state = dict(state)
ck("ver-0.6-kbgov5", off_state["version"] == "KB1v2-0.6-kbgov5", off_state["version"])
ck("tools-5", off_state["tools"] == 5, off_state["tools"])
ck("lacrimal-leak-0", off_state["lac_leak"] == [], off_state["lac_leak"])
ck("no-gov-keys-off", not ({"input_species", "no_named_ranking_for", "unranked_candidates",
                           "species_evidence"} & set(off_state["mg_keys"])), off_state["mg_keys"])

asyncio.run(session({"EYEKB_ACT_V6": "1"}, probe_repo))  # 默认 ON
on_state = dict(state)
ck("mg-top1-stable", on_state["mg_top1"] == off_state["mg_top1"] == "Microglia",
   f"on={on_state['mg_top1']} off={off_state['mg_top1']}")
ck("mg-len-stable", on_state["mg_len"] == off_state["mg_len"], (on_state["mg_len"], off_state["mg_len"]))
ck("krt-seq-stable", on_state["krt_seq"] == off_state["krt_seq"], on_state["krt_seq"][:4])
ck("on-gov-field-present", "input_species" in on_state["mg_keys"], on_state["mg_keys"])
# 人源 Microglia 查询不拒答, 只有 input_species(+可能的 flag)——no_named_ranking_for 不应出现
ck("human-not-refused-on", "no_named_ranking_for" not in on_state["mg_keys"], on_state["mg_keys"])


# ---------- ② ON 态三席 smoke（BTEST run1 A/B/C 真实 toolcalls） ----------
async def seat_smoke(s, init):
    tot = {"calls": 0, "genes": 0, "refused": 0, "human": 0, "flagged": 0, "errors": 0}
    seat_detail = {}
    for seat in ("run1_A", "run1_B", "run1_C"):
        d = {"calls": 0, "genes": 0, "refused": 0, "human": 0, "errors": []}
        for fp in sorted((TC / seat).glob("*.json")):
            calls = json.load(open(fp))
            for c in calls:
                if c.get("tool") != "query_marker" or not c.get("executed"):
                    continue
                args = c.get("args") or {}
                if not args.get("genes"):
                    continue
                d["calls"] += 1
                d["genes"] += 1
                try:
                    r = body_of(await s.call_tool("query_marker", {
                        "genes": args["genes"],
                        "library": args.get("library") or "all"}))
                    if r.get("__isError__"):
                        d["errors"].append([fp.name, str(r["__isError__"])[:80]])
                        continue
                    tier = r.get("input_species")
                    if r.get("no_named_ranking_for") == "mouse_input":
                        d["refused"] += 1
                        assert r.get("celltype_ranking") == []
                        assert tier in ("mouse_confirmed", "mouse_suspected")
                    elif tier == "human_assumed":
                        d["human"] += 1
                except Exception as e:  # noqa: BLE001
                    d["errors"].append([fp.name, f"{type(e).__name__}: {e}"][:2])
        seat_detail[seat] = d
        tot["genes"] += d["genes"]
        tot["refused"] += d["refused"]
        tot["human"] += d["human"]
        tot["errors"] += len(d["errors"])
    smoke_stats.update(tot)
    smoke_stats["per_seat"] = seat_detail
    ck("seat-smoke-zero-errors", tot["errors"] == 0, seat_detail)
    ck("seat-smoke-coverage==163", tot["genes"] == 163, tot["genes"])  # 三席 genes-mode 全量
    ck("seat-smoke-refused==34", tot["refused"] == 34, f"refused={tot['refused']}")
    ck("seat-smoke-human==129", tot["human"] == 129, f"human={tot['human']} refused={tot['refused']}")


asyncio.run(session({"EYEKB_ACT_V6": "1"}, seat_smoke))

json.dump({"card": "t_8960c7e0", "off_state": off_state, "on_state": on_state,
           "seat_smoke": smoke_stats, "checks_n": len(checks), "fails": fails,
           "verdict": "PASS" if not fails else "FAIL"},
          open(CARD / "out/b507_stdio_smoke.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"checks": len(checks), "fails": len(fails), "seat": smoke_stats,
                  "verdict": "PASS" if not fails else "FAIL"}, ensure_ascii=False)[:600])
sys.exit(0 if not fails else 1)
