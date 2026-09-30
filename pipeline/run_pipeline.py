#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — 一键批注入口（S0 样本预判 shadow 层 + 阶段 A 标准处理 + 阶段 B 逐簇证据采集）。

用法（仓根目录）:
  python pipeline/run_pipeline.py --input <10X目录|多10X父目录|data.h5ad> \
      [--species human|mouse|auto] [--tissue <词典名|auto>] --out results/run1 \
      [--group-col treatment]

S0 样本预判（WIRE-P1，REV-1=astra 定盘：Phase-1 为 shadow mode）:
  - 默认运行：三证据+六硬门自动判定物种 × 组织，读数全量落 `s0_gate_report.json`；
    判定过门 → 回填阶段 A/B 参数（人工显式 --species/--tissue 视为 override，
    报告记 s0_overridden_by_user 留痕）。
  - **shadow 语义：判不过（abstain）不阻断运行**——写 REPORT_ABSTAIN.md（人读记录件，
    非终止件）后继续执行（前提：物种/组织仍可从人工参数解析；均不可解析时按缺参退出）。
    阻断式硬门=Phase 3（WIRE-2 另批验收后经 `EYEKB_S0_ENFORCE=1` 切换，本批默认不阻断）。
  - 已知问题消费同为 shadow：风险旗标+复核要求进 decisions 两列与报告头段
    （pipeline/pitfalls/，盲评安全条带短规则；非盲评安全条只出结构化旗标）；
    **禁止任何自动改标/降档/覆票**——判读改判仍走原三席票与硬门。
  - 整体回退：`EYEKB_S0_GATE=0` = 接线前旧行为（不跑 S0、不产旗标、
    --species/--tissue 必填），用于无网基线对比（astra T4.3）与应急。

产出（全部落 --out）:
  stage_a/processed.h5ad          处理后矩阵（QC/归一化/Harmony 标记/leiden）
  stage_a/figures/*.png           质控图（线粒体、基因检出、doublet、UMAP 前后）
  stage_a/cluster_markers.csv     每簇 wilcoxon top30
  annotation_evidence_report.json 每簇五字段证据（结构=接线前口径，known-issues 不进本件）
  annotation_evidence_report.md    证据报告（S0 启用时头段附本格注意清单=人类面 shadow 注入）
  decisions_template.csv          每簇一行待人工裁决（decision/proposed_label 留空；
                                   S0 启用时附 pitfall_risk_flags / pitfall_review_required
                                   两列——仅风险提示，无自动改判列）
  mcp_calls.jsonl                 证据服务调用留痕
  s0_gate_report.json             S0 三证据读数+门因+全排名+override 留痕（回退态无）
  shadow_attention.json           本格适用 claim 清单（含盲评安全/判读后开放标注）
  shadow_flags.jsonl              逐簇风险旗标审计（自动具名/降级变化恒=0）

纪律红线：默认路径**零 LLM**；本入口不含任何自动打分/自动定标逻辑；
needs_review/弃权是合法输出；证据→结论的最后一步永远由研究者完成。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---- 数值确定性钉（ERRATA-E3, 2026-09-30）----
# 实测：不钉线程时同一输入连跑可见 16/15/16 簇抖动（结果随机器负载与 BLAS/numba
# 线程调度变化）；钉 OMP_NUM_THREADS=1 后两次运行逐字节一致（processed.h5ad sha 相同）。
# 阶段 A（Scrublet/邻域图/Harmony/leiden）为串行实现，单线程耗时 ≈ 多线程（实测 110s），
# 故以确定性优先。用 setdefault 保留显式覆盖（复现契约=保持默认钉）。
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def known_tissues():
    """词典已知组织清单 = kb/baselines 主档 + 判读层条目 tissue 字段（机械枚举，不硬编码）。"""
    tis = set()
    for p in (REPO_ROOT / "kb" / "baselines").glob("*.json"):
        if not p.name.startswith(("_", "fetal", "retina__")):
            tis.add(p.stem)
    priors = REPO_ROOT / "kb" / "priors"
    for sub in ("composition", "disease"):
        d = priors / sub
        if d.is_dir():
            for p in d.glob("*.json"):
                try:
                    e = json.loads(p.read_text(encoding="utf-8"))
                    t = (e.get("tissue") or "").strip().lower()
                    if t:
                        tis.add(t)
                except Exception:
                    continue
    return sorted(tis)


def _s0_enabled():
    return (os.environ.get("EYEKB_S0_GATE", "1") or "1").strip().casefold() not in (
        "0", "false", "off", "no")


def _s0_enforce():
    """Phase-3 前瞻开关：显式 EYEKB_S0_ENFORCE=1 才阻断；本批默认 shadow 不阻断。"""
    return (os.environ.get("EYEKB_S0_ENFORCE", "") or "").strip().casefold() in (
        "1", "true", "on", "yes")


def run_s0_gate(input_path, sample_col, species_arg, tissue_arg, out, thr_json=None):
    """S0 判卷。返回 (can_run, species, tissue, meta)。always 落 s0_gate_report.json。"""
    import s0_check
    if thr_json:
        s0_check.THR.update(json.load(open(thr_json)))
    rec = s0_check.gate_from_input(input_path, sample_col=sample_col)
    final = rec["final"]
    overridden = bool(species_arg != "auto" or tissue_arg != "auto")
    meta = {"s0_name": rec["name"], "input_kind": rec["input_kind"],
            "evidence_A_id": rec["evidence_A_id"],
            "evidence_B_symbol": rec["evidence_B_symbol"],
            "evidence_C_tissue": rec["evidence_C_tissue"],
            "final": final, "thresholds": rec["thresholds"],
            "mode": "enforce" if _s0_enforce() else "shadow",
            "s0_overridden_by_user": overridden,
            "manual_species": None if species_arg == "auto" else species_arg,
            "manual_tissue": None if tissue_arg == "auto" else tissue_arg}
    out.mkdir(parents=True, exist_ok=True)

    def _dump():
        (out / "s0_gate_report.json").write_text(
            json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    species = species_arg if species_arg != "auto" else (
        final["species_call"] if final["species_call"] in ("human", "mouse") else None)
    tissue = tissue_arg if tissue_arg != "auto" else None
    if tissue is None and final.get("tissue_top1"):
        tissue, note = s0_check.map_tissue_to_dict(final["tissue_top1"])
        meta["tissue_map_note"] = note
    if final["abstain"]:
        lines = ["# REPORT_ABSTAIN — S0 样本预判弃权记录（shadow：不阻断运行）", "",
                 f"- 输入：`{input_path}`",
                 f"- 时间：{time.strftime('%F %T')}",
                 f"- 物种判定：`{final['species_call']}`；组织 top1：`{final['tissue_top1']}`",
                 f"- 门因（任一命中即记弃权）：{'; '.join(final['gate_reasons'])}",
                 f"- 模式：shadow（本批默认）。" +
                 ("已按人工参数继续运行" if (species and tissue) else
                  "无法继续：物种/组织不可解析（缺参退出，非硬门阻断）"),
                 "- 判读改判通道：三席票与既有硬门；本件不改任何标签。"
                 "Phase 3（WIRE-2 另批验收）切换 EYEKB_S0_ENFORCE=1 后本弃权才阻断。",
                 "- 完整读数：`s0_gate_report.json`（同目录）。"]
        (out / "REPORT_ABSTAIN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        meta["abstain"] = True
        meta["continued"] = bool(species and tissue)
        _dump()
        if _s0_enforce():
            return False, None, None, meta
        if not (species and tissue):
            return False, None, None, meta
    # 人工 override 与判定的分歧留痕
    if species_arg != "auto" and final["species_call"] not in ("undetermined", "conflicted", "out_of_domain") \
            and final["species_call"] != species_arg:
        meta["s0_conflict_manual_vs_auto"] = {"s0": final["species_call"], "manual": species_arg}
    meta["backfill"] = {"species": species, "tissue": tissue}
    _dump()
    return True, species, tissue, meta


def _candidates_of(rep_cluster):
    qm = rep_cluster.get("kb_marker") or {}
    cands = [x.get("cell_type", "") for x in (qm.get("celltype_ranking") or [])][:3]
    cands += [x.get("cell_type", "") for x in (qm.get("unranked_candidates") or [])][:3]
    return [c for c in cands if c]


def inject_shadow(out, species, tissue, meta):
    """人类面 shadow 注入：md 头段注意清单 + decisions 两列旗标 + 机读/审计件。
    证据 JSON 零改动（喂料面防火墙）；不写任何自动改标列。"""
    sys.path.insert(0, str(HERE / "pitfalls"))
    import consume
    lines, machine, claims, dangling = consume.attention_section(species, tissue, {
        "source": "s0" if meta and not meta.get("s0_overridden_by_user") else "manual",
        "overridden_by_user": bool(meta and meta.get("s0_overridden_by_user"))})
    rep_path = out / "annotation_evidence_report.json"
    dec_path = out / "decisions_template.csv"
    per_cluster_audit = []
    if rep_path.exists():
        import csv
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        run_id = f"{species}__{tissue}__{time.strftime('%Y%m%dT%H%M%S')}"
        by_cluster = {}
        for c in rep.get("clusters") or []:
            flags, rows = consume.cluster_flags(claims, _candidates_of(c))
            by_cluster[str(c["cluster"])] = flags
            for r in rows:
                per_cluster_audit.append({"cluster_id": str(c["cluster"]), **r})
        consume.write_outputs(out, species, tissue, claims, per_cluster_audit, run_id, dangling)
        if dec_path.exists():
            rows = list(csv.reader(open(dec_path, encoding="utf-8")))
            if rows:
                rows[0] += ["pitfall_risk_flags", "pitfall_review_required"]
                cid_i = rows[0].index("cluster_id")
                for r in rows[1:]:
                    fl = by_cluster.get(str(r[cid_i]), [])
                    r += [";".join(fl), "yes" if fl else "no"]
                import io
                buf = io.StringIO()
                csv.writer(buf, lineterminator="\n").writerows(rows)
                dec_path.write_text(buf.getvalue(), encoding="utf-8")
    md_path = out / "annotation_evidence_report.md"
    if md_path.exists():
        txt = md_path.read_text(encoding="utf-8")
        idx = txt.find("## 簇 ")
        block = "\n".join(lines) + "\n"
        txt = (txt[:idx] + block + txt[idx:]) if idx >= 0 else (txt + "\n" + block)
        md_path.write_text(txt, encoding="utf-8")
    return {"n_claims_applicable": len(claims), "n_flag_rows": len(per_cluster_audit),
            "dangling_pointers": len(dangling)}


def main():
    ap = argparse.ArgumentParser(
        description="EyeKB 批量注释证据入口（阶段 S0(shadow)+A+B；默认零 LLM）")
    ap.add_argument("--input", required=True,
                    help="10X 三件套目录 / 含多份三件套子目录的父目录 / .h5ad")
    ap.add_argument("--species", default="auto", choices=["human", "mouse", "auto"],
                    help="默认 auto（S0 判定回填）；显式指定=S0 override 留痕（回退态必填）")
    ap.add_argument("--tissue", default="auto",
                    help="词典已知组织（见 --list-tissues）或 auto（S0 判定回填）")
    ap.add_argument("--out", required=True, help="输出目录（不存在则创建）")
    ap.add_argument("--sample-col", default="", help="h5ad 样本列（默认 obs.sample/输入名）")
    ap.add_argument("--sample-group", default="", dest="group_col",
                    help="分组：h5ad 列名，或三件套形态的 '样本名=组名;…' 映射"
                         "（提供分组才启用疾病先验比对）")
    ap.add_argument("--group-col", default="", dest="group_col",
                    help="同 --sample-group（别名）")
    ap.add_argument("--disease", default="", help="疾病名（配合分组；默认用非对照分组标签查询）")
    ap.add_argument("--gene-symbol-col", default="")
    ap.add_argument("--ensg-map", default="", help="ENSG<TAB>SYMBOL 两列 TSV")
    ap.add_argument("--resolution", type=float, default=1.0)
    ap.add_argument("--min-genes", type=int, default=200)
    ap.add_argument("--max-pct-mt", type=float, default=20.0)
    ap.add_argument("--top-genes-n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260929)
    ap.add_argument("--no-scrublet", action="store_true")
    ap.add_argument("--no-harmony", action="store_true")
    ap.add_argument("--s0-thr", default=None, dest="s0_thr",
                    help="S0 阈值覆盖 JSON（灵敏度扫描用；默认写死阈值）")
    ap.add_argument("--list-tissues", action="store_true", help="打印词典已知组织后退出")
    ap.add_argument("--llm-assist", action="store_true",
                    help="可选开关：调用用户自备通道生成证据摘要草稿（默认关闭，不影响分级）")
    a = ap.parse_args()

    if a.list_tissues:
        print("\n".join(known_tissues()))
        return 0

    gate = _s0_enabled()
    out = Path(a.out)
    meta = None
    if not gate:
        # 回退态（无网基线对比/应急）：与接线前逐字节等价的旧语义——人工参数必填
        if a.species == "auto" or a.tissue == "auto":
            print("[run_pipeline] EYEKB_S0_GATE=0（回退态）要求 --species 与 --tissue "
                  "显式给定（旧版必填语义）。", file=sys.stderr)
            return 2
        species, tissue = a.species, a.tissue
    else:
        ok, species, tissue, meta = run_s0_gate(a.input, a.sample_col,
                                                a.species, a.tissue, out, a.s0_thr)
        if not ok:
            if _s0_enforce() and meta["final"]["abstain"]:
                print("[run_pipeline] S0 硬门（enforce 模式，Phase-3 前瞻开关）弃权："
                      f"pipeline 停止。见 {out/'REPORT_ABSTAIN.md'}", file=sys.stderr)
                return 3
            print("[run_pipeline] S0 弃权且物种/组织不可解析（人工参数缺失）："
                  "缺参退出（非硬门阻断）。请显式补 --species/--tissue，"
                  f"或查看 {out/'REPORT_ABSTAIN.md'}", file=sys.stderr)
            return 4
        mode = meta.get("mode", "shadow")
        extra = "（弃权 shadow 继续）" if meta.get("abstain") else ""
        print(f"[run_pipeline] S0 判定：species={species} tissue={tissue}"
              f"（confidence={meta['final']['confidence']}，mode={mode}{extra}"
              f"{ '，manual override 留痕' if meta['s0_overridden_by_user'] else ''}）",
              flush=True)

    kt = known_tissues()
    if tissue.lower() not in {t.lower() for t in kt}:
        print(f"[warn] --tissue={tissue!r} 不在词典已知组织清单（继续执行，"
              f"组成对照可能返回无匹配条目并如实记入报告）。清单: {', '.join(kt)}",
              file=sys.stderr)

    (out / "stage_a").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    from stage_a_processing import run_stage_a
    from stage_b_evidence import run_stage_b

    sa = run_stage_a(a.input, out / "stage_a", species, sample_col=a.sample_col,
                     group_col=a.group_col, gene_symbol_col=a.gene_symbol_col,
                     ensg_map=a.ensg_map, min_genes=a.min_genes,
                     max_pct_mt=a.max_pct_mt, resolution=a.resolution,
                     expected_doublet_rate=0.06, seed=a.seed,
                     no_scrublet=a.no_scrublet, no_harmony=a.no_harmony)
    rep = run_stage_b(out / "stage_a" / "processed.h5ad",
                      out / "stage_a" / "cluster_markers.csv",
                      out / "stage_a" / "cluster_sizes.csv",
                      out, species, tissue, disease=a.disease,
                      group_col="group" if sa["group_present"] else "",
                      gene_degraded=bool(sa["gene_id"].get("degraded")),
                      top_genes_n=a.top_genes_n, llm_assist=a.llm_assist)
    att_stats = inject_shadow(out, species, tissue, meta) if gate else None
    grades = {}
    for c in rep["clusters"]:
        grades[c["confidence"]] = grades.get(c["confidence"], 0) + 1
    summary = {"out": str(out), "secs": round(time.time() - t0, 1),
               "n_clusters": len(rep["clusters"]), "grades": grades,
               "empty_decision_cells": True,
               "next_step": "逐簇在 decisions_template.csv 填 decision "
                            "(accept|modify|abstain) 与 proposed_label；弃权合法"}
    if gate:
        summary["s0"] = {"species": species, "tissue": tissue,
                         "confidence": meta["final"]["confidence"],
                         "abstain": bool(meta.get("abstain", meta["final"]["abstain"])),
                         "mode": meta.get("mode", "shadow"),
                         "overridden_by_user": meta["s0_overridden_by_user"]}
        summary["pitfalls_shadow"] = att_stats
    (out / "run_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print("[pipeline] DONE", json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
