#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — 一键批注入口（阶段 A 标准处理 + 阶段 B 逐簇五工具证据采集）。

用法（仓根目录）:
  python pipeline/run_pipeline.py --input <10X目录|多10X父目录|data.h5ad> \
      --species human --tissue retina --out results/run1 [--group-col treatment]

产出（全部落 --out）:
  stage_a/processed.h5ad          处理后矩阵（QC/归一化/Harmony 标记/leiden）
  stage_a/figures/*.png           质控图（线粒体、基因检出、doublet、UMAP 前后）
  stage_a/cluster_markers.csv     每簇 wilcoxon top30
  annotation_evidence_report.json 每簇五字段证据（top 基因/marker 候选/组成对照/
  annotation_evidence_report.md    疾病先验[有分组时]/文献片段+PMID/置信度分级）
  decisions_template.csv          每簇一行待人工裁决（accept|modify|abstain 列留空）
  mcp_calls.jsonl                 证据服务调用留痕

纪律红线：默认路径**零 LLM**；本入口不含任何自动打分/自动定标逻辑；
needs_review/弃权是合法输出；证据→结论的最后一步永远由研究者完成。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

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


def main():
    ap = argparse.ArgumentParser(
        description="EyeKB 批量注释证据入口（阶段 A + 阶段 B；默认零 LLM）")
    ap.add_argument("--input", required=True,
                    help="10X 三件套目录 / 含多份三件套子目录的父目录 / .h5ad")
    ap.add_argument("--species", required=True, choices=["human", "mouse"])
    ap.add_argument("--tissue", required=True,
                    help="词典已知组织（见 --list-tissues）")
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
    ap.add_argument("--list-tissues", action="store_true", help="打印词典已知组织后退出")
    ap.add_argument("--llm-assist", action="store_true",
                    help="可选开关：调用用户自备通道生成证据摘要草稿（默认关闭，不影响分级）")
    a = ap.parse_args()

    if a.list_tissues:
        print("\n".join(known_tissues()))
        return 0
    kt = known_tissues()
    if a.tissue.lower() not in {t.lower() for t in kt}:
        print(f"[warn] --tissue={a.tissue!r} 不在词典已知组织清单（继续执行，"
              f"组成对照可能返回无匹配条目并如实记入报告）。清单: {', '.join(kt)}",
              file=sys.stderr)

    out = Path(a.out)
    (out / "stage_a").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    from stage_a_processing import run_stage_a
    from stage_b_evidence import run_stage_b

    sa = run_stage_a(a.input, out / "stage_a", a.species, sample_col=a.sample_col,
                     group_col=a.group_col, gene_symbol_col=a.gene_symbol_col,
                     ensg_map=a.ensg_map, min_genes=a.min_genes,
                     max_pct_mt=a.max_pct_mt, resolution=a.resolution,
                     expected_doublet_rate=0.06, seed=a.seed,
                     no_scrublet=a.no_scrublet, no_harmony=a.no_harmony)
    rep = run_stage_b(out / "stage_a" / "processed.h5ad",
                      out / "stage_a" / "cluster_markers.csv",
                      out / "stage_a" / "cluster_sizes.csv",
                      out, a.species, a.tissue, disease=a.disease,
                      group_col="group" if sa["group_present"] else "",
                      gene_degraded=bool(sa["gene_id"].get("degraded")),
                      top_genes_n=a.top_genes_n, llm_assist=a.llm_assist)
    grades = {}
    for c in rep["clusters"]:
        grades[c["confidence"]] = grades.get(c["confidence"], 0) + 1
    summary = {"out": str(out), "secs": round(time.time() - t0, 1),
               "n_clusters": len(rep["clusters"]), "grades": grades,
               "empty_decision_cells": True,
               "next_step": "逐簇在 decisions_template.csv 填 decision "
                            "(accept|modify|abstain) 与 proposed_label；弃权合法"}
    (out / "run_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print("[pipeline] DONE", json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
