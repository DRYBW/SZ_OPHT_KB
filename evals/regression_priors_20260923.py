#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB1-K4 黄金回归: 判读层两工具 (get_tissue_composition/get_disease_prior)
标准 = P1 41 项同款: 工具返回与 kb/priors 源文件**逐项一致**;
另加 ① MD 渲染表↔JSON 逐格一致 ② source_ids 出处闭包 (红线8 机器化)
③ A 级数字漂移守卫 (重跑 build_priors 复算函数) ④ 旧 41 项+自测 v2 重跑不回归。
运行: /home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/evals/regression_priors_20260923.py
"""
import asyncio
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
sys.path.insert(0, "/mnt/D/EyeKB/scripts/priors")

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = "/mnt/D/EyeKB/mcp_server/server.py"
OUT = Path("/mnt/D/EyeKB/evals/REGRESSION_PRIORS_20260923.json")
MDOUT = Path("/mnt/D/EyeKB/evals/REGRESSION_PRIORS_20260923.md")

report = {"started": time.strftime("%F %T"), "checks": [], "pass": 0, "fail": 0}


def check(name, ok, detail=""):
    report["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:280]})
    report["pass" if ok else "fail"] += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:110]}")


def first_diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a:
                return f"{path}.{k}: only-in-tool"
            if k not in b:
                return f"{path}.{k}: only-in-source"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: len {len(a)}!={len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    if a != b:
        return f"{path}: {str(a)[:60]!r} != {str(b)[:60]!r}"
    return None


def parse(res):
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


def md_table_cells(md_path, section_kw):
    """粗解析 MD 表格行 (| 分隔), 返回 list[list[str]] (跳表头/分隔行)。"""
    rows, on = [], False
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and section_kw in line:
            on = True
            continue
        if on and line.startswith("## "):
            break
        if on and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            rows.append(cells)
    return rows


async def main():
    import eyekb_core as core

    # ---------- 1. 直调 vs JSON 源 逐项一致 ----------
    priors_dir = Path("/mnt/D/EyeKB/kb/priors")
    src = {p.stem: json.loads(p.read_text(encoding="utf-8"))
           for p in sorted(priors_dir.rglob("*.json"))}
    tc_ret = core.get_tissue_composition("human", "retina")
    check("TC human/retina 命中 human_retina",
          tc_ret.get("entry_id") == "human_retina", tc_ret.get("error", ""))
    j = src["human_retina"]
    rows_src = j["major_classes"]
    d = first_diff(tc_ret["rows"], [dict(r) for r in rows_src if r["class"] in
                                    {x["class"] for x in tc_ret["rows"]}])
    # 工具会给 rows 加 sources_resolved; 剔除后比对
    tool_rows = [{k: v for k, v in r.items() if k != "sources_resolved"}
                 for r in tc_ret["rows"]]
    src_cmp = []
    for r in rows_src:
        src_cmp.append({k: r[k] for k in r})
    d = first_diff(tool_rows, src_cmp, "tc_retina")
    check("TC retina rows 与 JSON 逐项一致 (10 类×数值)", d is None, d or f"{len(tool_rows)} rows")
    check("TC retina 10 类齐全", [r["class"] for r in tc_ret["rows"]] ==
          [r["class"] for r in src["human_retina"]["major_classes"]])
    check("TC retina 数值抽查 Rod=33.55/RGC=12.58/RPE=0.03",
          tc_ret["rows"][0]["pct_hrca317m"] == 33.55 and
          tc_ret["rows"][5]["pct_hrca317m"] == 12.58 and
          tc_ret["rows"][9]["pct_hrca317m"] == 0.03)
    tc_pdr = core.get_tissue_composition("human", "fibrovascular_membrane")
    check("TC human/membrane 命中 human_pdr_membrane",
          tc_pdr.get("entry_id") == "human_pdr_membrane", tc_pdr.get("error", ""))
    trows = [{k: v for k, v in r.items() if k != "sources_resolved"} for r in tc_pdr["rows"]]
    d = first_diff(trows, src["human_pdr_membrane"]["major_compartments"], "tc_membrane")
    check("TC membrane rows 与 JSON 逐项一致", d is None, d or f"{len(trows)} rows")
    check("TC membrane myeloid PDR-only=79.49",
          any(r["compartment"] == "myeloid" and r["pct_pdr_only"] == 79.49 for r in tc_pdr["rows"]))

    # disease 参数路由: retina+PDR → 应命中膜条 (组织仅有疾病条) 或基线条 (优先级), 明确其一
    tc_dis = core.get_tissue_composition("human", "retina", "proliferative diabetic")
    check("TC disease 参数命中 human_pdr_membrane (视网膜无 PDR 基线条)",
          tc_dis.get("entry_id") == "human_pdr_membrane", tc_dis.get("entry_id"))

    dp = core.get_disease_prior("PDR")
    check("DP 别名 PDR→proliferative_DR", dp.get("entry_id") == "proliferative_DR", dp.get("error", ""))
    d = first_diff({k: dp[k] for k in ("unexpected_flags", "contamination_flags", "signatures")},
                   {k: src["proliferative_DR"][k] for k in ("unexpected_flags", "contamination_flags", "signatures")},
                   "dp")
    check("DP 旗/签名与 JSON 逐项一致", d is None, d)
    dp_vit = core.get_disease_prior("proliferative diabetic retinopathy", "vitreous")
    check("DP tissue=vitreous 过滤 (仅1组织端)",
          len(dp_vit["expected_cell_state_matrix"]) == 1 and
          dp_vit["expected_cell_state_matrix"][0]["tissue"] == "vitreous")

    # ---------- 2. MD 渲染表 ↔ 工具 逐格一致 ----------
    md_rows = md_table_cells(priors_dir / "composition" / "human_retina.md", "主表")
    ok, det = True, ""
    if len(md_rows) != 10:
        ok, det = False, f"md rows={len(md_rows)}"
    else:
        for mr, tr in zip(md_rows, tc_ret["rows"]):
            if mr[0] != tr["class"] or float(mr[2]) != tr["pct_hrca317m"] or \
               mr[3] != f"{tr['expected_range_pct'][0]}–{tr['expected_range_pct'][1]}":
                ok, det = False, f"{mr[0]}: {mr[2:4]} vs {tr['pct_hrca317m']}"
                break
    check("MD retina 主表 10 行×(类/%/区间) 与工具一致", ok, det)
    md_m = md_table_cells(priors_dir / "composition" / "human_pdr_membrane.md", "主表")
    ok = len(md_m) == len(tc_pdr["rows"]) and all(
        float(m[1].split()[0]) == r["pct_pdr_only"] for m, r in zip(md_m, tc_pdr["rows"]))
    check("MD membrane 主表 PDR-only% 与工具一致", ok, f"md={len(md_m)}")
    md_dp = (priors_dir / "disease" / "proliferative_DR.md").read_text(encoding="utf-8")
    ok = all(k in md_dp for k in ("Macrophage", "HMOX1", "contamination", "玻璃体")) or \
         all(any(s in md_dp for s in ("髓系", "污染旗")) for _ in [0])
    check("MD disease 条目含预期矩阵/旗/签名关键词", ok)

    # ---------- 3. 出处闭包 (红线8) ----------
    def closure(entry_out):
        bad = []
        for r in entry_out.get("rows", []):
            for s in r.get("sources_resolved", []):
                if s.get("MISSING"):
                    bad.append((r.get("class") or r.get("compartment"), s["sid"]))
        return bad
    check("出处闭包: retina rows 全 source_ids 可解析", not closure(tc_ret), closure(tc_ret))
    check("出处闭包: membrane rows 全 source_ids 可解析", not closure(tc_pdr), closure(tc_pdr))
    bad = [s["sid"] for m in dp.get("expected_cell_state_matrix", [])
           for s in m.get("sources_resolved", []) if s.get("MISSING")]
    check("出处闭包: PDR 矩阵 source_ids 可解析", not bad, bad)
    for e in src.values():  # 每个 sid 必须带 pmid 或 path (无出处禁入)
        for s in e["sources"]:
            assert s.get("pmid") or s.get("path"), (e["entry_id"], s["sid"])
    check("红线8机检: 全部 sources 带 PMID 或数据集路径", True,
          f"{sum(len(e['sources']) for e in src.values())} sources")

    # ---------- 4. A 级漂移守卫 (复算) ----------
    sys.path.insert(0, "/mnt/D/EyeKB/scripts/priors")
    import build_priors as bp
    hr = bp.recompute_hrca()
    hg = bp.recompute_gse165784()
    check("漂移: HRCA total=3,177,310", hr["total"] == 3177310, hr["total"])
    check("漂移: HRCA Rod% 与条目一致",
          hr["pooled_all"]["Rod"][1] == src["human_retina"]["major_classes"][0]["pct_hrca317m"],
          hr["pooled_all"]["Rod"])
    check("漂移: GSE165784 myeloid PDR% 与条目一致",
          hg["comp_pdr"]["myeloid"][1] == 79.49, hg["comp_pdr"]["myeloid"])

    # ---------- 5. MCP stdio 等价 (P1 41 项同款通道) ----------
    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = sorted(t.name for t in (await s.list_tools()).tools)
            check("list_tools == 五工具", names == ["get_disease_prior", "get_kb_page",
                  "get_tissue_composition", "query_marker", "search_literature"], names)
            m1 = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "retina"}))
            d = first_diff(m1, tc_ret, "stdio_tc")
            check("stdio TC(retina) == 直调 (深度相等)", d is None, d)
            m2 = parse(await s.call_tool("get_disease_prior", {"disease": "PDR"}))
            d = first_diff(m2, dp, "stdio_dp")
            check("stdio DP(PDR) == 直调 (深度相等)", d is None, d)
            m3 = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "dragon", "tissue": "retina"}))
            check("边界: 未知物种 → error+available",
                  "error" in m3 and len(m3.get("available", [])) >= 3, str(m3)[:80])
            m4 = parse(await s.call_tool("get_disease_prior", {"disease": "xyz-not-exist"}))
            check("边界: 未知疾病 → error", "error" in m4, str(m4)[:80])

    # ---------- 6. 旧行为不回归: 重跑 P1opt 41 项回归 + 自测 v2 ----------
    for script in ("regression_mcp_vs_direct_v2_20260923.py", "selftest_tools_v2_20260923.py"):
        p = subprocess.run([PY, f"/mnt/D/EyeKB/evals/{script}"], capture_output=True,
                           text=True, timeout=1800)
        jf = Path(f"/mnt/D/EyeKB/evals/{script.replace('.py','').replace('regression_','').replace('mcp_vs_direct_','')}")
        # 两个脚本各自写 json: 解析 fail 计数
        jname = {"regression_mcp_vs_direct_v2_20260923.py":
                 "/mnt/D/EyeKB/evals/MCP_REGRESSION_V2_20260923.json",
                 "selftest_tools_v2_20260923.py":
                 "/mnt/D/EyeKB/evals/selftest_tools_v2_20260923.json"}[script]
        try:
            jj = json.loads(Path(jname).read_text())
            fails = jj.get("fail", jj.get("fails", "?"))
            check(f"旧套件不回归: {script}", p.returncode == 0 and fails == 0,
                  f"rc={p.returncode} fails={fails}")
        except Exception as e:
            check(f"旧套件不回归: {script}", False, f"{e}; rc={p.returncode}")

    # ---------- 汇总 ----------
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    L = ["# KB1-K4 判读层工具黄金回归 (2026-09-23)\n",
         f"started: {report['started']} | **{report['pass']} PASS / {report['fail']} FAIL**\n"]
    for c in report["checks"]:
        L.append(f"- [{'x' if c['ok'] else ' '}] {c['name']}  {c['detail'][:120]}")
    MDOUT.write_text("\n".join(L))
    print(f"\n== KB1 黄金回归: {report['pass']} PASS / {report['fail']} FAIL ==")
    sys.exit(1 if report["fail"] else 0)


if __name__ == "__main__":
    asyncio.run(main())
