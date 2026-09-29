#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — 阶段 B：逐簇五工具证据采集（MCP stdio 起仓内 mcp_server）。

本文件复制改写自 /mnt/D/EyeKB/plans/evalset/scripts/kb2_mcp_v2.py（原文件冻结未动）。
解绑内容：不再绑 evalset 冻结卷 / 不再读外部 ENSG 映射 / 不再硬编码组织映射，
改为消费阶段 A 的产物（processed.h5ad + cluster_markers.csv）。

═══ 纪律红线（与服务端红线一致，勿改）═══
1. 默认路径**零 LLM**——五个查询工具是本地机械检索，只出证据、不出结论。
2. 本脚本不含任何自动打分/自动定标/自动命名逻辑。下面的"置信度分级"是
   预注册的机械 QC 旗（触发条件逐条写进报告，可复核），不是注释结论；
   needs_review / 弃权是合法输出，禁止把 needs_review 写成确定标签。
3. decisions_template.csv 的 decision/proposed_label 列一律留空，交研究者裁决
   （accept / modify / abstain 三值由人来填）。
4. 服务端 B5 跨物种治理对鼠源输入清空具名排名（no_named_ranking_for），本脚本
   原样透传，不绕过、不补名次。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER = REPO_ROOT / "mcp_server" / "server.py"

CONTROLISH = {"control", "ctrl", "normal", "untrig", "unpaired", "vehicle",
              "rrd_control", "non_dm", "nondisease", "healthy"}


def _log(logf, step, **kw):
    rec = {"ts": time.strftime("%F %T"), "step": step, **kw}
    with open(logf, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(f"[stageB] {step}: " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)


def parse_mcp(res):
    """MCP CallToolResult -> dict（与 kb2_mcp_v2 同法）。"""
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc_ = getattr(res, "structured_content", None)
    if isinstance(sc_, dict):
        return sc_.get("result", sc_) if set(sc_.keys()) == {"result"} else sc_
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


# ---------------------------------------------------------------- 机械 QC 旗
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _find_baseline_row(rows, cand):
    """候选类名 ↔ 基线行 class/label 的机械匹配（规范化全等，或包含且长度>=4）。"""
    nc = _norm(cand)
    if len(nc) < 2:
        return None
    for r in rows:
        for key in ("class", "label_cn"):
            nr = _norm(r.get(key, ""))
            if nr == nc or (len(nc) >= 4 and nc in nr):
                return r
    return None


def composition_flag(rows, candidate, fraction_pct):
    """簇比例（%细胞）对照基线供者级区间 —— 只做旗标，不做打分。"""
    if not candidate:
        return {"flag": "no_candidate", "note": "query_marker 无具名候选，不比对"}
    row = _find_baseline_row(rows, candidate)
    if row is None:
        return {"flag": "no_baseline_row",
                "note": f"候选 {candidate!r} 在该组织组成基线中无对应行，不比对"}
    lo_hi = row.get("donor_range_pct")
    iqr = row.get("donor_iqr_pct")
    out = {"flag": "", "candidate": candidate, "baseline_class": row.get("class"),
           "observed_pct": round(fraction_pct, 3),
           "donor_median_pct": row.get("donor_median_pct"),
           "donor_iqr_pct": iqr, "donor_range_pct": lo_hi,
           "provenance": [s.get("label") or s.get("pmid") or s.get("sid", "")
                          for s in (row.get("sources_resolved") or [])][:6]}
    if not lo_hi:
        out["flag"] = "range_not_estimated"
        out["note"] = "基线行未提供供者级区间（骨架条/样本不足），不判越界"
    elif fraction_pct < lo_hi[0] or fraction_pct > lo_hi[1]:
        out["flag"] = "outside_range"
    elif iqr and not (iqr[0] <= fraction_pct <= iqr[1]):
        out["flag"] = "within_range_outside_iqr"
    else:
        out["flag"] = "within_iqr"
    return out


def prior_hits_for_cluster(dp, candidates):
    """疾病先验 expected_cell_state_matrix 中对候选类的机械提及（证据摘录，非一致性打分）。"""
    if not dp or dp.get("error") or dp.get("__isError__"):
        return []
    hits = []
    for row in dp.get("expected_cell_state_matrix") or []:
        for exp in row.get("expected") or []:
            low = str(exp).lower()
            for cand in candidates:
                if cand and len(cand) >= 3 and cand.lower() in low:
                    hits.append({"cell_type": cand, "tissue": row.get("tissue"),
                                 "expected_line": str(exp)[:220],
                                 "evidence_grade": row.get("evidence")})
                    break
    return hits[:8]


def grade_cluster(kb_marker, comp, lit, group_present, gene_degraded):
    """预注册机械分级规则（顺序即优先级；触发原因写入报告，可复核）。
    输出三值之一: evidence_consistent | mixed_or_insufficient | needs_review
    —— 这是判读顺序提示旗，不是注释结论，不参与任何打分。"""
    ranking = (kb_marker or {}).get("celltype_ranking") or []
    unranked = (kb_marker or {}).get("unranked_candidates") or []
    no_named = (kb_marker or {}).get("no_named_ranking_for")
    if isinstance(lit, dict) and lit.get("per_celltype"):
        n_lit = sum(len((v or {}).get("results") or []) for v in lit["per_celltype"].values())
        degraded = any(bool((v or {}).get("degraded")) for v in lit["per_celltype"].values())
    else:
        n_lit = len((lit or {}).get("results") or [])
        degraded = bool((lit or {}).get("degraded"))
    rules = []
    if gene_degraded:
        rules.append("gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠")
    if no_named:
        rules.append(f"named_ranking_removed_by_server: {no_named}（服务端跨物种治理，具名排名不可用）")
    if not ranking:
        rules.append("no_named_marker_candidates")
    if n_lit == 0:
        rules.append("no_literature_results")
    if rules or (not unranked and not ranking):
        return "needs_review", (rules or ["no_evidence"])
    reasons = list(rules)
    top1 = ranking[0]
    if top1.get("n_shared", 0) <= 1:
        reasons.append("weak_marker_match: top1 共享基因数 <=1")
    if len(ranking) > 1 and ranking[1].get("n_shared") == top1.get("n_shared"):
        reasons.append("candidate_tie: top1/top2 共享基因数并列")
    if comp.get("flag") == "outside_range":
        reasons.append("composition_outside_baseline_range")
    if degraded:
        reasons.append("literature_degraded: 检索降级（向量模型/语料不可用），片段仅供参考")
    if reasons:
        return "mixed_or_insufficient", reasons
    return "evidence_consistent", ["marker_candidate+within_baseline+literature_present"]


# ---------------------------------------------------------------- 主流程
def run_stage_b(processed_h5ad, markers_csv, sizes_csv, out_dir, species, tissue,
                disease="", group_col="group", gene_degraded=False, top_genes_n=10,
                llm_assist=False, logf=None):
    import anyio
    import pandas as pd
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    logf = logf or (out / "stage_b_log.jsonl")

    mk = pd.read_csv(markers_csv)
    sizes = pd.read_csv(sizes_csv)
    total_cells = int(sizes["n_cells"].sum())
    clusters = [str(c) for c in sizes["cluster"].astype(str)]

    try:  # 组标签（供疾病先验启用判断 + 簇级分组比例证据）
        import anndata as ad
        a = ad.read_h5ad(processed_h5ad, backed="r")
        gcol = None
        if group_col and group_col in a.obs.columns:
            gcol = group_col
        elif "group" in a.obs.columns:
            gcol = "group"
        obs = None
        if gcol:
            obs = a.obs[["sample", gcol]].copy()
            obs["cluster"] = a.obs["leiden"].astype(str)
        del a
    except Exception as e:  # 读不到不影响证据主流程，如实记录
        _log(logf, "warn", note=f"group 列读取失败: {e!r}")
        obs = None
    group_present = bool(obs is not None and obs[gcol].nunique() >= 2)

    calls = []
    dp_cache = {}  # run 级疾病先验缓存（闭包内填充，报告段读取）

    async def collect():
        params = StdioServerParameters(command=sys.executable, args=[str(SERVER)], env=None)
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()

                async def call(tool, args):
                    t0 = time.time()
                    res = parse_mcp(await s.call_tool(tool, args))
                    ok = not (isinstance(res, dict) and res.get("__isError__"))
                    calls.append({"tool": tool, "args": {k: (str(v)[:120] if isinstance(v, list) else v)
                                                        for k, v in args.items()},
                                  "secs": round(time.time() - t0, 2), "ok": ok})
                    return res

                # 组织基线与疾病先验都是 run 级缓存（同参数只查一次）
                tc = await call("get_tissue_composition", {"species": species, "tissue": tissue})
                rows = (tc or {}).get("rows") or []
                dp_cache.clear()
                if group_present:
                    labels = [str(x) for x in sorted(obs[gcol].unique())]
                    want = [disease] if disease else \
                        [l for l in labels if _norm(l) not in {_norm(x) for x in CONTROLISH}] \
                        or labels
                    for lab in dict.fromkeys(want):
                        dp_cache[lab] = await call("get_disease_prior",
                                                  {"disease": lab, "tissue": tissue})
                per_cluster = []
                for i, cl in enumerate(clusters, 1):
                    sub = mk[mk["cluster"].astype(str) == cl].sort_values("rank")
                    top = [str(g) for g in sub["gene"].head(top_genes_n)]
                    frac_pct = 100.0 * int(sizes.loc[sizes["cluster"].astype(str) == cl, "n_cells"].iloc[0]) \
                        / max(total_cells, 1)
                    qm = await call("query_marker", {"genes": top}) if top else None
                    cands = [x.get("cell_type") for x in ((qm or {}).get("celltype_ranking") or [])][:3]
                    cands_unranked = [x.get("cell_type") for x in ((qm or {}).get("unranked_candidates") or [])][:3]
                    comp = composition_flag(rows, cands[0] if cands else None, frac_pct)
                    lit = {"per_celltype": {}}
                    query_cands = cands or cands_unranked
                    if query_cands:
                        for ct in query_cands:
                            lit["per_celltype"][ct] = await call(
                                "search_literature",
                                {"cell_type": ct, "species": species, "tissue": tissue, "top_k": 4})
                    else:  # 无候选：用 top 基因做词法查询，仍出证据不出结论
                        lit["gene_query"] = await call(
                            "search_literature",
                            {"cell_type": "", "species": species, "tissue": tissue,
                             "query": " ".join(top[:6]) + f" {tissue}", "top_k": 4})
                    dp_hits = {}
                    if group_present:
                        for lab, dp in dp_cache.items():
                            dp_hits[lab] = {
                                "entry_id": (dp or {}).get("entry_id") or (dp or {}).get("error"),
                                "mentions": prior_hits_for_cluster(dp, query_cands)}
                    gf = {}
                    if group_present and obs is not None:
                        cm = obs[obs["cluster"] == cl]
                        n = max(len(cm), 1)
                        gf = {str(k): round(100.0 * v / n, 2)
                              for k, v in cm[gcol].value_counts().items()}
                    grade, reasons = grade_cluster(qm, comp, lit, group_present, gene_degraded)
                    per_cluster.append({
                        "cluster": cl,
                        "n_cells": int(sizes.loc[sizes["cluster"].astype(str) == cl, "n_cells"].iloc[0]),
                        "fraction_pct": round(frac_pct, 3),
                        "top_genes": top,
                        "kb_marker": qm,
                        "tissue_composition": {"observed_vs_baseline": comp,
                                               "baseline_entry_id": (tc or {}).get("entry_id"),
                                               "baseline_tissue": (tc or {}).get("tissue"),
                                               "usage_redline": (tc or {}).get("usage_redline")},
                        "disease_prior": ({"group_fractions_pct": gf, "per_disease": dp_hits}
                                          if group_present else
                                          {"enabled": False,
                                           "reason": "未提供分组列或分组只有一组（--group-col），疾病先验比对不启用"}),
                        "literature": _trim_lit(lit),
                        "confidence": grade,
                        "confidence_rules_fired": reasons,
                    })
                    if i % 5 == 0:
                        print(f"[stageB] progress {i}/{len(clusters)} clusters", flush=True)
                return tc, per_cluster

    tc, per_cluster = anyio.run(collect)

    # 可选 LLM 辅助（默认关闭；只写证据摘要叙述，不改分级、不定标签）
    llm_meta = {"enabled": False, "note": "默认零 LLM；--llm-assist 才启用，且需用户自备通道"}
    if llm_assist:
        from llm_assist import assist  # noqa: E402
        llm_meta = assist(per_cluster, out)

    report = {
        "schema": "eyekb-pipeline-evidence-v1",
        "generated_at": time.strftime("%F %T"),
        "inputs": {"processed_h5ad": str(processed_h5ad), "species": species,
                   "tissue": tissue, "group_col_enabled": group_present,
                   "disease_queried": list(dp_cache.keys()) if group_present else [],
                   "top_genes_n": top_genes_n},
        "redlines": [
            "默认路径零 LLM；本文件由本地五工具机械检索生成",
            "置信度分级是预注册机械 QC 旗（规则触发原因逐条可查），不是注释结论",
            "弃权(needs_review)/复核(mixed_or_insufficient) 是合法输出；禁止把 QC 旗当确定标签",
            "全部证据（marker 命中/基线区间/疾病先验提及/文献片段）带出处，供人工裁决",
        ],
        "baseline_entry": {"entry_id": (tc or {}).get("entry_id"),
                           "tissue": (tc or {}).get("tissue"),
                           "frozen_date": (tc or {}).get("frozen_date"),
                           "error": (tc or {}).get("error")},
        "llm_assist": llm_meta,
        "mcp_calls": {"total": len(calls),
                      "errors": sum(1 for c in calls if not c["ok"])},
        "clusters": per_cluster,
    }
    (out / "annotation_evidence_report.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "annotation_evidence_report.md").write_text(
        render_md(report), encoding="utf-8")

    dec = out / "decisions_template.csv"
    with open(dec, "w", encoding="utf-8") as f:
        f.write("cluster_id,n_cells,fraction_pct,top_candidates,composition_flag,"
                "confidence_grade,decision,proposed_label,notes\n")
        for c in per_cluster:
            qm = c["kb_marker"] or {}
            tops = ";".join(x.get("cell_type", "")
                            for x in (qm.get("celltype_ranking") or [])[:3]) or "ABSTAIN(no candidate)"
            f.write(f'{c["cluster"]},{c["n_cells"]},{c["fraction_pct"]},"{tops}",'
                    f'{c["tissue_composition"]["observed_vs_baseline"].get("flag","")},'
                    f'{c["confidence"]},,,\n')
    (out / "mcp_calls.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False, default=str) for c in calls) + "\n",
        encoding="utf-8")
    sha = hashlib.sha256((out / "annotation_evidence_report.json").read_bytes()).hexdigest()
    _log(logf, "done", clusters=len(per_cluster), report_sha=sha[:16],
         grades={g: sum(1 for c in per_cluster if c["confidence"] == g)
                 for g in ("evidence_consistent", "mixed_or_insufficient", "needs_review")},
         calls=len(calls))
    return report


def _trim_lit(lit):
    """文献片段瘦身：每个候选保留 top3 结果、snippet 截 300 字符（证据报告可读性）。"""
    out = {}
    for k, v in (lit or {}).items():
        if k == "per_celltype":
            out[k] = {}
            for ct, resp in v.items():
                r = dict(resp or {})
                rs = []
                for h in (r.get("results") or [])[:3]:
                    h2 = dict(h)
                    h2["snippet"] = str(h2.get("snippet", ""))[:300]
                    rs.append(h2)
                r["results"] = rs
                out[k][ct] = r
        else:
            r = dict(v or {})
            rs = []
            for h in (r.get("results") or [])[:3]:
                h2 = dict(h)
                h2["snippet"] = str(h2.get("snippet", ""))[:300]
                rs.append(h2)
            r["results"] = rs
            out[k] = r
    return out


def render_md(rep):
    L = ["# 注释证据报告（EyeKB pipeline 阶段 B 输出）", "",
         f"- 生成时间：{rep['generated_at']}",
         f"- 输入：`{rep['inputs']['processed_h5ad']}`（物种 {rep['inputs']['species']}，"
         f"组织 {rep['inputs']['tissue']}，疾病先验{'启用' if rep['inputs']['group_col_enabled'] else '未启用（无分组）'}）",
         f"- MCP 调用：{rep['mcp_calls']['total']} 次，错误 {rep['mcp_calls']['errors']} 次",
         "- **阅读须知**：本报告只呈现证据与机械 QC 旗，不含注释结论；每簇的最终命名由研究者在 "
         "decisions_template.csv 填写 accept / modify / abstain。弃权是合法输出。", ""]
    for r in rep["redlines"]:
        L.append(f"- 红线：{r}")
    L.append("")
    for c in rep["clusters"]:
        qm = c["kb_marker"] or {}
        cr = qm.get("celltype_ranking") or []
        ur = qm.get("unranked_candidates") or []
        comp = c["tissue_composition"]["observed_vs_baseline"]
        L += [f"## 簇 {c['cluster']}（{c['n_cells']} 细胞，占 {c['fraction_pct']}%）",
              f"- 置信度分级（机械 QC 旗）：**{c['confidence']}**",
              f"  - 触发规则: {', '.join(c['confidence_rules_fired'])}",
              f"- top 基因: {', '.join(c['top_genes'])}",
              "- query_marker 候选: " + (
                  "; ".join(f"{x['cell_type']} (n_shared={x['n_shared']}, "
                            f"{','.join(x.get('shared_genes', [])[:4])})" for x in cr[:3])
                  or ("无具名候选" + (f"（unranked: {', '.join(x['cell_type'] for x in ur[:3])}；"
                                       f"{qm.get('no_named_ranking_for', '')}）" if ur else ""))),
              f"- 组成对照（基线条 {c['tissue_composition'].get('baseline_entry_id')}）: "
              f"flag={comp.get('flag')}" + (
                  f"；观测 {comp.get('observed_pct')}% vs 供者中位 {comp.get('donor_median_pct')}%"
                  f"（IQR {comp.get('donor_iqr_pct')}，range {comp.get('donor_range_pct')}）"
                  if comp.get("observed_pct") is not None and comp.get("flag") not in
                  ("no_candidate", "no_baseline_row") else ""),
              "- 疾病先验: " + (
                  "; ".join(f"{k}: {v.get('entry_id')} 提及 {len(v.get('mentions') or [])} 条"
                            for k, v in (c["disease_prior"].get("per_disease") or {}).items())
                  if c["disease_prior"].get("per_disease") else str(c["disease_prior"].get("reason"))),
              "- 文献片段（top3，逐条带 PMID）:"]
        lit = c["literature"] or {}
        anyres = False
        for ct, resp in (lit.get("per_celltype") or {}).items():
            for h in (resp.get("results") or [])[:2]:
                anyres = True
                L.append(f"  - [{ct}] PMID {h.get('pmid')} ({h.get('journal')} {h.get('year')}): "
                         f"{str(h.get('snippet'))[:140]}…")
        for k, resp in lit.items():
            if k == "per_celltype":
                continue
            for h in (resp.get("results") or [])[:2]:
                anyres = True
                L.append(f"  - [gene_query] PMID {h.get('pmid')} ({h.get('journal')} "
                         f"{h.get('year')}): {str(h.get('snippet'))[:140]}…")
        if not anyres:
            L.append("  - （无检索结果——按弃权路径处理）")
        if c["disease_prior"].get("group_fractions_pct"):
            L.append(f"- 分组构成（%细胞）: {c['disease_prior']['group_fractions_pct']}")
        L.append("")
    L.append("---\n*本报告由 EyeKB 仓内 `pipeline/` 生成；服务红线：证据只作人工判读与 QC 旗，"
             "禁止接进任何打分/加权/排序。*")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="EyeKB pipeline 阶段 B（逐簇五工具证据采集，默认零 LLM）")
    ap.add_argument("--processed", required=True, help="阶段 A 的 processed.h5ad")
    ap.add_argument("--markers", required=True, help="阶段 A 的 cluster_markers.csv")
    ap.add_argument("--sizes", required=True, help="阶段 A 的 cluster_sizes.csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--species", required=True, choices=["human", "mouse"])
    ap.add_argument("--tissue", required=True, help="词典已知组织（如 retina / fibrovascular_membrane / ocular_surface …）")
    ap.add_argument("--disease", default="", help="疾病名（不填则尝试用分组标签查疾病条目）")
    ap.add_argument("--group-col", default="group")
    ap.add_argument("--top-genes-n", type=int, default=10)
    ap.add_argument("--gene-degraded", action="store_true",
                    help="阶段 A 报告基因 ID 未映射为符号时置位（影响分级）")
    ap.add_argument("--llm-assist", action="store_true",
                    help="可选：调用用户自备 OpenAI 兼容通道生成证据摘要（默认关闭；不影响分级）")
    a = ap.parse_args()
    run_stage_b(a.processed, a.markers, a.sizes, a.out, a.species, a.tissue,
                disease=a.disease, group_col=a.group_col,
                gene_degraded=a.gene_degraded, top_genes_n=a.top_genes_n,
                llm_assist=a.llm_assist)


if __name__ == "__main__":
    main()
