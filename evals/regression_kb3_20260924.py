#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 发育轴全量单列回归 (t_5425a7ca, 2026-09-24)。

组 1 W1: 11 条成人档 development_stage 必填+枚举合法+禁令+参考分布段禁令+头行
组 2 W1: 概念条 development_stage+锚点核实表 (3 锚 verdict)
组 3 W1: 发育期独立条 retina__fetal_developing (schema 隔离/枚举/双锚/数字与素材全等/排除层)
组 4 W1: 索引 development_entries 登记 + entries=11 未混入发育条 (回归锁)
组 5 W2: 矩阵 12 行全带 development_axis=adult + ROP 预留格 (独立键) + PDR 双显式
组 6 W3: EVALSET_FREEZE KB3-ADJ 增补段在位 + 前缀逐字节全等 (本体未动) + RUN1 无混池复核
组 7 W4: dev_stage sidecar 行数/枚举/词表单一真源 + retrieve_v3 参数与旧行为
组 8 W5: 两处 WIKI 红线在位
MCP 组: adult 查询零新条泄漏 + fetal 查询仍概念条 + 检索无 dev_stage 字段=旧行为
"""
import asyncio
import difflib
import json
import re
import sys
from pathlib import Path

KB = Path("/mnt/D/EyeKB/kb/baselines")
DIS = Path("/mnt/D/EyeKB/kb/priors/disease")
RAG = Path("/mnt/D/OcularKB/ocularkb/rag")
EYE = Path("/mnt/D/EyeKB")
EV = EYE / "plans/kb3_evidence"
TISSUES = ["retina", "ocular_surface", "optic_nerve", "trabecular_meshwork",
           "ciliary_body", "RPE", "choroid", "conjunctiva", "iris", "lens", "sclera"]
ENUM = {"adult", "fetal_developing", "postnatal_neonatal", "mixed_not_separable", "unknown"}
PROH = "发育期数据不得进成人基线统计池"

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append({"check": name, "pass": bool(cond), "detail": str(detail)[:400]})
    print(("  [PASS] " if cond else "  [FAIL] ") + name + ("  " + str(detail)[:120] if detail else ""))


def main():
    # ================= 组 1 W1 =================
    print("== 组 1: W1 成人档 development_stage ==")
    ent = {t: json.loads((KB / f"{t}.json").read_text(encoding="utf-8")) for t in TISSUES}
    check("11 条全带 development_stage", all("development_stage" in e for e in ent.values()))
    check("枚举合法 (5 值, mixed 未新建)",
          all(e["development_stage"] in ENUM for e in ent.values())
          and not any(e["development_stage"] == "mixed_not_separable" for e in ent.values()))
    filled_adult = [t for t in TISSUES if ent[t]["status"] == "filled_donor_level"
                    and ent[t].get("organism_stage") == "adult"]
    check("5 个 adult 实数档 → development_stage=adult (与 organism_stage 一致)",
          sorted(filled_adult) == sorted(["retina", "ocular_surface", "optic_nerve",
                                          "trabecular_meshwork", "ciliary_body"])
          and all(ent[t]["development_stage"] == "adult" for t in filled_adult), filled_adult)
    check("RPE=unknown 不静默归 adult (KB2c 红线2 继承)",
          ent["RPE"]["development_stage"] == "unknown"
          and "禁静默归 adult" in ent["RPE"].get("kb3_applicable_stage_at_backfill", ""))
    check("骨架=unknown+适用锚写死",
          all(ent[t]["development_stage"] == "unknown"
              and "成人锚" in ent[t].get("kb3_applicable_stage_at_backfill", "")
              for t in TISSUES if ent[t]["status"] == "skeleton_mapping_backfilled"))
    check("禁令字段在位 11/11",
          all(PROH in e.get("development_stage_prohibition", "") for e in ent.values()))
    mdok = []
    for t in TISSUES:
        md = (KB / f"{t}.md").read_text(encoding="utf-8")
        head_ok = "KB3 发育档" in md.split("\n", 6)[3]
        if ent[t]["status"] == "filled_donor_level":
            i_main = md.find("## 主参考")
            # KB3 修复 (run 1768): 原 md.find(PROH) 命中头行第 4 行 (与 head_ok 要求自相矛盾,
            # 永假); 段禁令必须锚定 主参考 标题之后 search。内容侧同轮修复:
            # build_baselines.py UnboundLocalError 崩溃致段禁令行从未渲染, 重渲链后已入 (retina.md L38)。
            i_proh = md.find(PROH, i_main) if i_main >= 0 else -1
            sec_ok = i_main >= 0 and 0 <= i_proh - i_main < 400
        else:
            sec_ok = "发育轴单列" in md or PROH in md[:2000]
        mdok.append((t, head_ok, sec_ok))
    check("MD 头行+参考分布段禁令 11/11", all(h and s for _, h, s in mdok),
          [t for t, h, s in mdok if not (h and s)])

    # ================= 组 2 概念条 =================
    print("== 组 2: W1 概念条 ==")
    fc = json.loads((KB / "fetal_development_transitions.json").read_text(encoding="utf-8"))
    check("概念条 development_stage=fetal_developing+禁令",
          fc.get("development_stage") == "fetal_developing"
          and PROH in fc.get("development_stage_prohibition", ""))
    av = fc.get("kb3_anchor_verification", {})
    verdicts = {a["acc"]: a["verdict"] for a in av.get("anchors", [])}
    check("三锚核实表 verdict 正确",
          verdicts.get("GSE268630") == "AVAILABLE_WITH_LABELS"
          and verdicts.get("GSE234963") == "AVAILABLE_NO_PUBLISHED_LABELS"
          and verdicts.get("GSE138002") == "AVAILABLE_MIXED_CONTENT", verdicts)
    check("概念条 candidates 原数组未动 (KB2c 回归 6 候选锁)",
          len(fc["candidates"]) >= 6 and all("acc" in c for c in fc["candidates"]))

    # ================= 组 3 发育期独立条 =================
    print("== 组 3: W1 retina__fetal_developing ==")
    dev_p = KB / "retina__fetal_developing.json"
    check("独立文件在位 (.json/.md)", dev_p.is_file() and (KB / "retina__fetal_developing.md").is_file())
    de = json.loads(dev_p.read_text(encoding="utf-8")) if dev_p.is_file() else {}
    check("schema=eyekb-baseline-development/1.0 (MCP 成人扫描不可见前缀)",
          de.get("schema") == "eyekb-baseline-development/1.0"
          and not str(de.get("schema", "")).startswith("eyekb-baseline/"))
    check("development_stage=fetal_developing 枚举合法 + mixed 未用",
          de.get("development_stage") == "fetal_developing")
    check("entry_id 与成人条分离", de.get("entry_id") == "baseline_human_retina__fetal_developing__kb3"
          and de.get("entry_id") != "baseline_human_retina")
    agg = json.loads((EV / "fetal_agg_20260924.json").read_text(encoding="utf-8"))
    p268 = de.get("portal_majorclass_reference", {})
    check("GSE268630 数字与聚合素材全等",
          p268.get("pct") == agg["GSE268630_portal"]["majorclass_pct"]
          and p268.get("hist") == agg["GSE268630_portal"]["majorclass_hist"]
          and p268.get("cells") == agg["GSE268630_portal"]["cells_total"])
    fl = de.get("author_labels_fetal_layer(GSE138002)", {})
    check("GSE138002 胎层数字与素材全等 (Hgw9-27)",
          fl.get("pct_by_celltype")
          == agg["GSE138002_final_author_labels"]["layers"]["fetal_Hgw"]["celltype_pct"]
          and fl.get("cells")
          == agg["GSE138002_final_author_labels"]["layers"]["fetal_Hgw"]["n_cells"]
          and "Hgw9" in fl.get("samples", []) and "Hgw27" in fl.get("samples", []))
    check("排除层在位: Adult/organoid 只登记不并入",
          de["excluded_layers"]["adult_Adult"]["cells"]
          == agg["GSE138002_final_author_labels"]["layers"]["adult_Adult"]["n_cells"]
          and "禁并入" in de["excluded_layers"]["adult_Adult"]["disposition"])
    check("GSE234963 数据卡: 无据不建 (composition=None)",
          next(c for c in de["anchors"] if c["acc"] == "GSE234963")["composition"] is None)
    check("新生层单列 postnatal_neonatal (枚举第三值有据)",
          de.get("postnatal_neonatal_layer(GSE138002)", {}).get("development_stage")
          == "postnatal_neonatal")
    md = (KB / "retina__fetal_developing.md").read_text(encoding="utf-8")
    check("发育条 MD 禁令+非引擎声明",
          PROH in md and "现役判读引擎" in md)

    # ================= 组 4 索引 =================
    print("== 组 4: W1 索引 ==")
    idx = json.loads((KB / "baselines.json").read_text(encoding="utf-8"))
    check("索引 entries=11 (成人数组未混入发育条)",
          len(idx["entries"]) == 11
          and not any("development_stage" in str(x.get("entry_id", "")) for x in idx["entries"]))
    check("索引 development_entries 登记",
          any(x.get("entry_id") == "baseline_human_retina__fetal_developing__kb3"
              for x in idx.get("development_entries", [])))
    check("索引 entries 全带 development_stage",
          all("development_stage" in x for x in idx["entries"]))

    # ================= 组 5 W2 =================
    print("== 组 5: W2 疾病矩阵 ==")
    dm = json.loads((DIS / "_DISEASE_TISSUE_MATRIX.json").read_text(encoding="utf-8"))
    check("12 行全带 development_axis=adult",
          len(dm["rows"]) == 12 and all(r.get("development_axis") == "adult" for r in dm["rows"]))
    res = dm.get("development_axis_reservations", [])
    check("ROP 预留格在位且只立不填",
          len(res) == 1 and res[0]["disease"] == "ROP"
          and res[0]["development_axis"] == "fetal_neonatal"
          and "RESERVED" in res[0]["status"])
    pdr = json.loads((DIS / "PDR__fibrovascular_membrane.json").read_text(encoding="utf-8"))
    check("PDR 条目 development_stage+organism_stage 双显式 adult",
          pdr.get("development_stage") == "adult" and pdr.get("organism_stage") == "adult")
    pmdb = (DIS / "PDR__fibrovascular_membrane.md").read_text(encoding="utf-8")
    check("PDR MD 头显式 development_stage=adult", "development_stage=adult" in pmdb[:800])
    mmd = (DIS / "_DISEASE_TISSUE_MATRIX.md").read_text(encoding="utf-8")
    check("矩阵 MD 含 development_axis 列+ROP 预留",
          "development_axis" in mmd.split("\n")[6] and "ROP" in mmd)

    # ================= 组 6 W3 =================
    print("== 组 6: W3 评估集 ==")
    fz = (EYE / "plans/evalset/EVALSET_FREEZE_20260924.md").read_text(encoding="utf-8")
    check("KB3-ADJ 增补段在位", "增补 KB3-ADJ" in fz and "永久规则" in fz)
    pre = (EV / "EVALSET_FREEZE_pre_kb3.md").read_text(encoding="utf-8")
    check("冻结件本体零改动 (前缀逐字节全等)", fz.startswith(pre),
          "增补为纯追加")
    oa = json.loads((EYE / "plans/evalset/scoring/object_A.json").read_text(encoding="utf-8"))
    q8 = [x for x in oa if x.get("member") == "Q8"]
    check("RUN1 复查: Q8 两行 behavior_only=True",
          len(q8) == 2 and all(x.get("behavior_only") for x in q8))
    check("RUN1 复查: Q8 无成人评分字段",
          all(not any(k in x for k in ("cell_macroF1", "donor_macroF1", "concordance",
                                       "truth_coverage")) for x in q8))
    pd = json.loads((EYE / "plans/evalset/scoring/paired_delta.json").read_text(encoding="utf-8"))
    check("RUN1 复查: paired_delta 无 Q8",
          not any("Q8" in str(r.get("member")) for r in pd), [r.get("member") for r in pd])

    # ================= 组 7 W4 =================
    print("== 组 7: W4 RAG sidecar+参数 ==")
    side = [json.loads(l) for l in
            (EYE / "kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl").read_text(
                encoding="utf-8").splitlines() if l.strip()]
    head, body = side[0], side[1:]
    check("sidecar schema/行数=3696 papers",
          head["schema"] == "eyekb-dev-stage-meta/1.0" and len(body) == 3696)
    check("final 枚举三值合法", all(r["dev_stage_final"] in ENUM for r in body))
    check("chunk 级不做=声明在位", "chunk 级" in head["scope_note"] and "本次不做" in head["scope_note"])
    em = [json.loads(l) for l in
          (EYE / "kb/literature_db/evidence_meta_v2.2_2026-09.jsonl").read_text(
              encoding="utf-8").splitlines() if l.strip()]
    em_ids = {str(d["paper_id"]) for d in em if "paper_id" in d}
    check("sidecar paper_id 集合与 evidence_meta 全等",
          {str(r["paper_id"]) for r in body} == em_ids)
    rev = (EV / "REVIEW_SHEET_devstage.tsv").read_text(encoding="utf-8").splitlines()
    check("人工抽验 30 篇表在位 (30 行+表头, manual_call 全填)",
          len(rev) == 31 and all(l.split("\t")[4] for l in rev[1:]))
    src = (RAG / "scripts/stage3_retrieve_v3.py").read_text(encoding="utf-8")
    check("retrieve_v3 --dev-stage 参数+默认不过滤",
          "--dev-stage" in src and "dev_stage=None" in src
          and 'assert dev_stage in (None, "", "any", "adult", "fetal_developing", "unknown")' in src)
    # 真 import 冒烟 (不加载 embedding 模型, 只测 map/合并链)
    sys.path.insert(0, str(RAG / "scripts"))
    spec = __import__("importlib.util", fromlist=["util"])
    import importlib.util as iu
    m = iu.spec_from_file_location("s3v3", RAG / "scripts/stage3_retrieve_v3.py")
    mod = iu.module_from_spec(m)
    m.loader.exec_module(mod)
    dsm = mod._dev_stage_map()
    check("dev_stage_map 装载 3696 条", len(dsm) == 3696)
    ab = mod._dev_stage_map("/nonexistent.jsonl")
    check("meta 缺失→None (过滤自动禁用)", ab is None)

    # ================= 组 8 W5 =================
    print("== 组 8: W5 文档红线 ==")
    oc_wiki = Path("/mnt/D/OcularKB/WIKI/结论速查.md").read_text(encoding="utf-8")
    check("OcularKB WIKI §6 发育轴红线", "发育轴红线" in oc_wiki and "不互为参照" in oc_wiki)
    eb_readme = (EYE / "README.md").read_text(encoding="utf-8")
    check("EyeKB README 红线第 5 条", "发育轴红线（KB3" in eb_readme)
    cur = Path("/mnt/D/OcularKB/WIKI/当前状态.md").read_text(encoding="utf-8")
    check("当前状态: KB3 行在位", "t_5425a7ca" in cur)

    # ================= MCP 组 =================
    print("== MCP: 成人/fetal 查询行为 ==")
    from mcp import ClientSession, StdioServerParameters  # noqa: E402
    from mcp.client.stdio import stdio_client  # noqa: E402

    async def mcp_tests():
        params = StdioServerParameters(
            command=sys.executable, args=[str(EYE / "mcp_server/server.py")])
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()

                def parse(res):
                    for c in res.content:
                        if getattr(c, "type", "") == "text":
                            try:
                                return json.loads(c.text)
                            except Exception:
                                pass
                    return None
                adult = parse(await s.call_tool("get_tissue_composition",
                                                {"species": "human", "tissue": "retina"}))
                rf = json.loads((KB / "retina.json").read_text(encoding="utf-8"))
                check("MCP retina: 全等不破 + development_stage=adult 透传",
                      adult.get("donor_level_main") == rf["donor_level_main"]
                      and adult.get("development_stage") == "adult")
                check("MCP 成人查询零发育条泄漏",
                      "fetal_developing" not in json.dumps(adult))
                fetal = parse(await s.call_tool(
                    "get_tissue_composition",
                    {"species": "human", "tissue": "retina", "development_stage": "fetal"}))
                js = json.dumps(fetal)
                check("MCP fetal 查询仍=概念条 (不泄漏发育数据; 指针允许)",
                      fetal.get("mode") == "fetal_development_concept"
                      and "PRPC" not in js and "majorclass_pct" not in js
                      and "portal_majorclass_reference" not in js)
                ad = parse(await s.call_tool(
                    "get_tissue_composition",
                    {"species": "human", "tissue": "retina", "development_stage": "adult"}))
                check("MCP development_stage=adult 显式查询不泄漏发育数据",
                      "portal_majorclass_reference" not in json.dumps(ad)
                      and "PRPC" not in json.dumps(ad))
                # 检索侧: 无 dev_stage 字段的旧行为
                res = parse(await s.call_tool("search_literature",
                                              {"cell_type": "Rod Bipolar Cell", "top_k": 2}))
                old_keys = {"pmid", "title", "journal", "year", "species", "is_preprint",
                            "tissue_labels", "section", "snippet",
                            "cell_type_mentioned", "marker_genes", "relevance_score",
                            # KB3 修复 (run 1768): 原键集漏了 pre-KB3 时代既有字段, 误报 KB3 破坏旧行为。
                            # 出处实证: _full_text=OcularKB stage3_retrieve.py:136 (RAG v2.1, 09-23, 非 KB3);
                            # inclusion_reason/reason_confidence/reason_method=eyekb_core.py:44 "K3 additive
                            # 联表" (KB1v2b); inclusion_reasons/claim_relation/evidence_context/
                            # evidence_verification_status=mcp_server/server.py:7 KB1v2 联表注释 (09-23 23:27,
                            # 早于 KB3 开工 01:30); is_preprint 为条件字段 (仅预印本命中挂)。
                            # KB3 唯一 eyekb_core 编辑=L327 composition 透传, 检索路径零改动
                            # (grep dev_stage mcp_server/eyekb_core.py = 空)。
                            "_full_text", "inclusion_reason", "reason_confidence", "reason_method",
                            "inclusion_reasons", "claim_relation", "evidence_context",
                            "evidence_verification_status"}
                check("search_literature 结果 schema 未加 dev_stage (旧行为不变)",
                      res and all("dev_stage" not in x and old_keys >= set(x.keys())
                                  for x in res["results"]),
                      list(res["results"][0].keys()) if res and res["results"] else "-")

    asyncio.run(mcp_tests())

    npass = sum(1 for x in RESULTS if x["pass"])
    out = {"card": "t_5425a7ca", "date": "2026-09-24", "suite": "REGRESSION_KB3_20260924",
           "pass": npass, "fail": len(RESULTS) - npass, "checks": RESULTS}
    (EYE / "evals/REGRESSION_KB3_20260924.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nKB3 REGRESSION: {npass} PASS / {len(RESULTS) - npass} FAIL → "
          f"/mnt/D/EyeKB/evals/REGRESSION_KB3_20260924.json")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
