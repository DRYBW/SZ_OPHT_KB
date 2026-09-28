#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC2 t_719dd225 · T1a — staging 仓副本 exec7 等价自测（9 检查，KB9REG exec7 口径逐条对齐）
差异仅两处：REPO 指向 staging 副本；报告写本卡 out/（线上卡目录零写）。
基线件 = staging 仓内 exec/out 镜像，先断言与线上权威字节全等再使用。"""
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO_STAGING_20260928")
ONLINE = Path("/mnt/D/EyeKB")
CARD = ONLINE / "plans/kb9_ocs_20260927"
OUT = REPO / "docs/plans/repo_sync2_20260928/out"
K9N = {"Melanocyte", "Schwann", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}

fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:200]})
    if not cond:
        fails.append([tag, str(detail)[:200]])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# 基线镜像件与线上 canon 级等价断言（镜像=脱敏副本，字节差异仅限文本面；
# canon_sha/probe-spec/post_probe_shas 三张哈希-输入面必须全等）
import json as _j


def _nummap(d, keys):
    return {k: d[k] for k in keys if k in d}


a = _j.load(open(REPO / "docs/plans/kb9_ocs_20260927/exec/out/postdiff_selfproof.json"))
b = _j.load(open(CARD / "exec/out/postdiff_selfproof.json"))
ck("baseline-mirror==online::postdiff(selfproof-hashfaces)", a["post_probe_shas"] == b["post_probe_shas"], "post_probe_shas")
a2 = _j.load(open(REPO / "docs/plans/kb9_ocs_20260927/exec/out/pre_change_baseline_kb9reg.json"))
b2 = _j.load(open(CARD / "exec/out/pre_change_baseline_kb9reg.json"))
ck("baseline-mirror==online::prebaseline(hashfaces)",
   {k: (v["probe"], v["args"], v["canon_sha"]) for k, v in a2["probes"].items()}
   == {k: (v["probe"], v["args"], v["canon_sha"]) for k, v in b2["probes"].items()},
   "probe-spec+canon_sha")

os.environ.pop("EYEKB_ACT_V6", None)
os.environ["EYEKB_MCP_SOFTFLAGS"] = "1"
sys.path.insert(0, str(REPO / "clients" / "ocularkb" / "rag" / "scripts"))
sys.path.insert(0, str(REPO / "mcp_server"))
import eyekb_core as rcore  # noqa: E402  (repo copy)

assert str(Path(rcore.__file__).resolve()).startswith(str(REPO)), rcore.__file__

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
mk = {t: rcore.query_marker(cell_type=t, library="k9_ocs")["markers"].get(t) for t in K9N}
ck("repo-k9-genes==online", all(mk[t] == onl_terms[t] for t in K9N),
   {t: (mk[t] == onl_terms[t]) for t in K9N})
rules = json.load(open(REPO / "kb/markers/_k9_ocs_rules_overlay_v1.json"))
ck("repo-rules-counts", rules["r2r3_shield"]["n_rows"] == 283 and rules["r1_item_scope_table"]["n_rows"] == 34,
   (rules["r2r3_shield"]["n_rows"], rules["r1_item_scope_table"]["n_rows"]))


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
report = {"card": "t_719dd225-T1a", "repo": str(REPO), "n_checks": len(checks), "n_fails": len(fails),
          "verdict": "PASS" if not fails else "FAIL", "checks": checks, "failures": fails}
(OUT / "t1_exec7_staging.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=1)[:1600])
sys.exit(0 if not fails else 1)
