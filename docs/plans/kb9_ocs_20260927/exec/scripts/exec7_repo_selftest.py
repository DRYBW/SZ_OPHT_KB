#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec7 — 仓镜像副本行为自测（脱敏后仓面）
① 仓 core 直调: 默认 all 类清单(集合)=线上 post 清单(60); EYEKB_ACT_V6=off 态=43+10 别名口径;
② 仓 k9_ocs 显式路由: 4 类 marker 值与线上权威 json 逐基因全等（脱敏只动 provenance 文本字段，不动 markers）;
③ 仓 server stdio 真往返: initialize+list_tools==5 + query_marker(k9_ocs/list) 两调用;
④ 版本面: 仓 server.py version=KB1v2-0.5-k9reg。
输出 exec/out/exec7_repo_selftest.json"""
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
ONLINE = Path("/mnt/D/EyeKB")
CARD = ONLINE / "plans/kb9_ocs_20260927"
K9N = {"Melanocyte", "Schwann", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}

# ①② 仓 core 直调（repo 树自带 kb/clients）
os.environ.pop("EYEKB_ACT_V6", None)
os.environ["EYEKB_MCP_SOFTFLAGS"] = "1"
sys.path.insert(0, str(REPO / "clients" / "ocularkb" / "rag" / "scripts"))
sys.path.insert(0, str(REPO / "mcp_server"))
import eyekb_core as rcore  # noqa: E402  (repo copy)

assert str(Path(rcore.__file__).resolve()).startswith(str(REPO)), rcore.__file__
fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:200]})
    if not cond:
        fails.append([tag, str(detail)[:200]])


post = json.load(open(CARD / "exec/out/postdiff_selfproof.json"))["post_probe_shas"]
r_all = set(rcore.query_marker()["cell_types"])
o_all = set(json.load(open(CARD / "exec/out/pre_change_baseline_kb9reg.json"))
            ["probes"]["k9leak_default_list"]["response"]["cell_types"])
ck("repo-default-classes==online", r_all == o_all and len(r_all) == 60, f"|r|={len(r_all)}")
os.environ["EYEKB_ACT_V6"] = "off"
r_off = set(rcore.query_marker()["cell_types"])
ck("repo-off-classes==43", len(r_off) == 43 and not (r_off & K9N), f"|off|={len(r_off)}")
os.environ.pop("EYEKB_ACT_V6")
k9 = rcore.query_marker(library="k9_ocs")
ck("repo-k9-list", sorted(k9.get("cell_types", [])) == sorted(K9N), k9.get("cell_types"))
onl_terms = json.load(open(ONLINE / "kb/markers/markers_k9_ocs_increment.json"))["markers"]
rep_terms = k9["cell_types"]
mk = {t: rcore.query_marker(cell_type=t, library="k9_ocs")["markers"].get(t) for t in K9N}
ck("repo-k9-genes==online", all(mk[t] == onl_terms[t] for t in K9N),
   {t: (mk[t] == onl_terms[t]) for t in K9N})
rules = json.load(open(REPO / "kb/markers/_k9_ocs_rules_overlay_v1.json"))
ck("repo-rules-counts", rules["r2r3_shield"]["n_rows"] == 283 and rules["r1_item_scope_table"]["n_rows"] == 34,
   (rules["r2r3_shield"]["n_rows"], rules["r1_item_scope_table"]["n_rows"]))

# ③ stdio 真往返（仓 server）
async def stdio_test():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    sp = StdioServerParameters(command="/home/ubuntu/training-venv/bin/python",
                               args=[str(REPO / "mcp_server/server.py")], env=None)
    async with stdio_client(sp) as (rd, wr):
        async with ClientSession(rd, wr) as s:
            init = await s.initialize()
            ck("stdio-server-title", init.server_info.name == "eyekb", init.server_info.name)
            ck("stdio-version", init.server_info.version == "KB1v2-0.5-k9reg",
               init.server_info.version)
            tools = await s.list_tools()
            ck("stdio-list-tools-5", len(tools.tools) == 5, len(tools.tools))
            res = await s.call_tool("query_marker", {"library": "k9_ocs"})
            if res.is_error:
                body = {"__isError__": [c.text for c in res.content]}
            else:
                sc = getattr(res, "structured_content", None)
                if isinstance(sc, dict):
                    body = sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
                else:
                    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
                    body = json.loads(texts[0]) if texts else None
            ck("stdio-k9-route", sorted((body or {}).get("cell_types", [])) == sorted(K9N), str(body)[:160])


asyncio.run(stdio_test())
report = {"card": "t_4bb75b26", "n_checks": len(checks), "n_fails": len(fails),
          "verdict": "PASS" if not fails else "FAIL", "checks": checks, "failures": fails}
(CARD / "exec/out/exec7_repo_selftest.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=1)[:1500])
sys.exit(0 if not fails else 1)
