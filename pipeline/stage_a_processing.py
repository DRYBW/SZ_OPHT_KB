#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — 阶段 A：标准单细胞处理（Scanpy / Harmony / Scrublet）。

输入  : 10X 目录（matrix.mtx + barcodes.tsv + genes.tsv，支持 .gz；可多子目录=多样本）
        或 .h5ad（raw counts）。
输出  : processed.h5ad（obs 含 QC 过滤、doublet 标记、Harmony 校正标记、leiden 聚类）
        + cluster_markers.csv（每簇 wilcoxon top-N）+ 质控图（线粒体/基因检出/doublet/UMAP 前后）
        + stage_a_metrics.json。

纪律红线（与 README 同步，勿删）：
- 本脚本是标准处理，不调用任何 LLM，不产出任何"注释结论标签"；
  聚类簇号只是待判读单元，不是细胞类型名。
- 阈值全部可由命令行覆盖，默认值来自仓内已实测流程（docs/plans/figure_uplift_20260928/
  scripts/v2_o1o3_harmony_scrublet_20260923.py 的协议），不做隐性自动调参。
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

ad.settings.allow_write_nullable_strings = False

# 人/鼠线粒体基因 ENSG 常量（QC 用，公开参考数据；符号名可直接前缀匹配）
MT_ENSG = {
    "human": {
        "ENSG00000198804", "ENSG00000198712", "ENSG00000194631", "ENSG00000189043",
        "ENSG00000187608", "ENSG00000188173", "ENSG00000187147", "ENSG00000189057",
        "ENSG00000185737", "ENSG00000204658", "ENSG00000204632", "ENSG00000198888",
        "ENSG00000198763", "ENSG00000228253", "ENSG00000116717", "ENSG00000116710",
        "ENSG00000198840", "ENSG00000212907", "ENSG00000188690",
    },
    "mouse": {
        "ENSMUSG00000097087", "ENSMUSG00000097082", "ENSMUSG00000097081",
        "ENSMUSG00000097078", "ENSMUSG00000097070", "ENSMUSG00000097072",
        "ENSMUSG00000097069", "ENSMUSG00000097075", "ENSMUSG00000097066",
        "ENSMUSG00000097080", "ENSMUSG00000097079", "ENSMUSG00000097086",
        "ENSMUSG00000097084", "ENSMUSG00000097073", "ENSMUSG00000059331",
        "ENSMUSG00000097071", "ENSMUSG00000097067", "ENSMUSG00000069546",
        "ENSMUSG00000097077",
    },
}


def _log(logf, step, **kw):
    rec = {"ts": time.strftime("%F %T"), "step": step, **kw}
    with open(logf, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(f"[stageA] {step}: " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)


# ---------------------------------------------------------------- 输入装载
def _looks_ensg(names) -> bool:
    arr = list(names)
    step = max(1, len(arr) // 2000)  # 均匀抽样整个基因轴（首段常被无 ENSG 映射的克隆/基因座符号占满，前缀顺序抽样会系统性低估）
    s = pd.Series([str(x) for x in arr[::step]])
    return float(s.str.match(r"^(ENS[GPT]\d{9,}|ENS\w{2,5}G\d{9,}\b)").mean()) > 0.5


def _symbol_column(adata: ad.AnnData) -> str | None:
    for c in ("gene_symbols", "symbol", "gene_name", "symbols", "symbols_of_gene_id"):
        if c in adata.var.columns and adata.var[c].notna().any():
            return c
    return None


def resolve_gene_symbols(adata: ad.AnnData, species: str, logf,
                         symbol_col: str = "", ensg_map: str = "") -> tuple[ad.AnnData, dict]:
    """把 var_names 变成 gene symbol（证据检索用）。优先级：
    --gene-symbol-col > var 自带符号列 > var_names 已是符号 > --ensg-map 映射 > 降级（保留原 ID 并在报告注明）。
    同时补 .var['mt'] 布尔列（线粒体 QC，符号前缀 MT-/mt-* 或内置 ENSG 常量）。"""
    note = {"gene_id_mode": "", "symbol_source": "", "degraded": False}
    vn = adata.var_names.astype(str)
    if symbol_col:
        if symbol_col not in adata.var.columns:
            raise SystemExit(f"--gene-symbol-col={symbol_col!r} 不在 var 列里: {list(adata.var.columns)}")
        adata.var_names = pd.Index(adata.var[symbol_col].astype(str).str.upper().to_numpy())
        note.update(gene_id_mode="symbols", symbol_source=f"--gene-symbol-col:{symbol_col}")
    elif _symbol_column(adata) and not _looks_ensg(vn):
        pass  # var_names 本身就是符号
        note.update(gene_id_mode="symbols", symbol_source="var_names")
    elif not _looks_ensg(vn):
        note.update(gene_id_mode="symbols", symbol_source="var_names")
    else:
        mapped = None
        if ensg_map:
            m = pd.read_csv(ensg_map, sep="\t", header=None, dtype=str,
                            names=["ensg", "symbol"])
            mp = dict(zip(m.ensg.str.upper(), m.symbol.str.upper()))
            vs = pd.Series(np.asarray(adata.var_names).astype(str))
            mapped = vs.str.upper().map(mp).fillna(vs)
            if float((mapped != vs).mean()) > 0.3:
                adata.var_names = pd.Index(mapped.to_numpy())
                note.update(gene_id_mode="symbols", symbol_source="ensg-map")
            else:
                mapped = None
        if mapped is None:
            note.update(gene_id_mode="ensembl_unmapped",
                        symbol_source="none (证据检索降级：marker 比对命中率会低)",
                        degraded=True)
            _log(logf, "gene_symbols", mode="ensembl_unmapped",
                 hint="给 --ensg-map <ENSG<TAB>SYMBOL 两列TSV> 可恢复符号检索")
    # 符号去重（映射后可能撞名）——保留首个，标记
    dup = adata.var_names.duplicated()
    if dup.any():
        keep = adata.var[~dup].copy()
        adata = adata[:, ~dup.values].copy()
        note["dedup_dropped_genes"] = int(dup.sum())
    mt_prefix = {"human": "MT-", "mouse": "mt-"}[species]
    mt_ids = MT_ENSG.get(species, set())
    names = pd.Series(np.asarray(adata.var_names).astype(str))
    ismt = names.str.upper().str.startswith("MT-") | names.str.startswith(mt_prefix) | \
        names.str.upper().isin(x.upper() for x in mt_ids)
    adata.var["mt"] = ismt.to_numpy()
    note["n_mt_genes"] = int(ismt.sum())
    return adata, note


def load_input(input_path: Path, logf, sample_col: str = "") -> ad.AnnData:
    """支持 .h5ad / 单 10X 目录 / 父目录（每个子目录一份 10X 三件套 = 一个样本）。"""
    import scanpy as sc
    input_path = Path(input_path)
    if input_path.is_file() and input_path.suffix in (".h5ad",):
        a = ad.read_h5ad(input_path)
        if int(a.obs_names.duplicated().sum()):
            a.obs_names_make_unique(join="-")
        if sample_col and sample_col in a.obs.columns:
            a.obs["sample"] = a.obs[sample_col].astype(str)
        elif "sample" not in a.obs.columns:
            a.obs["sample"] = input_path.stem
        a.obs["sample"] = a.obs["sample"].astype(str)
        _log(logf, "load", kind="h5ad", shape=str(a.shape),
             samples=str(sorted(a.obs["sample"].unique())[:8]))
        return a
    if input_path.is_file() and input_path.suffix in (".h5", ".hdf5"):
        a = sc.read_10x_h5(input_path)
        a.var_names_make_unique()
        a.obs["sample"] = input_path.stem
        return a
    if not input_path.is_dir():
        raise SystemExit(f"输入不存在: {input_path}")

    def _read_triplet(d: Path) -> ad.AnnData:
        # 10X mtx 三件套（.gz 可选）；genes.tsv 两列/三列(feature protocol)都吃
        mtx = next((p for p in (d / "matrix.mtx", d / "matrix.mtx.gz") if p.exists()), None)
        bc = next((p for p in (d / "barcodes.tsv", d / "barcodes.tsv.gz") if p.exists()), None)
        gg = next((p for p in (d / "genes.tsv", d / "genes.tsv.gz",
                               d / "features.tsv", d / "features.tsv.gz",
                               d / "features.tsv.csv") if p.exists()), None)
        if not (mtx and bc and gg):
            raise SystemExit(f"目录 {d} 不是 10X 三件套（缺 matrix.mtx/barcodes.tsv/genes.tsv）")
        import scipy.io as sio
        import scipy.sparse as sp
        m = sp.csc_matrix(sio.mmread(mtx)).T  # genes x cells -> cells x genes
        cells = pd.read_csv(bc, sep="\t", header=None, dtype=str).iloc[:, 0].tolist()
        gdf = pd.read_csv(gg, sep="\t", header=None, dtype=str)
        if gdf.shape[1] >= 3 and gdf.iloc[:, 2].astype(str).str.contains("Gene Expression").any():
            gdf = gdf.iloc[:, :2]  # cellranger v3 feature 协议前两列= ensg, symbol
        gdf.columns = ["gene_id", "gene_symbol"][: gdf.shape[1]]
        obs = pd.DataFrame(index=pd.Index(cells, name="barcode"))
        var = gdf.set_index("gene_id" if "gene_id" in gdf else gdf.columns[0])
        if "gene_symbol" in var:
            var["gene_symbols"] = var["gene_symbol"].values
        a = ad.AnnData(m, obs=obs, var=var)
        a.var_names_make_unique()
        a.obs["sample"] = d.name
        return a

    tri_dirs = []
    if all((input_path / n).exists() for n in ("matrix.mtx", "matrix.mtx.gz",
                                               "barcodes.tsv", "barcodes.tsv.gz")):
        tri_dirs = [input_path]
    else:
        for sub in sorted(p for p in input_path.iterdir() if p.is_dir()):
            if any((sub / n).exists() for n in ("matrix.mtx", "matrix.mtx.gz")) and \
               any((sub / n).exists() for n in ("barcodes.tsv", "barcodes.tsv.gz")):
                tri_dirs.append(sub)
    if not tri_dirs:
        raise SystemExit(f"{input_path}: 既不是 .h5ad，也不是（含多份）10X 三件套目录")
    parts = [_read_triplet(d) for d in tri_dirs]
    a = ad.concat(parts, join="outer", label=None, merge="same")
    dup = int(a.obs_names.duplicated().sum())
    if dup:  # 跨样本相同 barcode 是真实场景（如 GSE183320 127 例）：去重命名，否则下游 .loc 重排会爆炸
        a.obs_names_make_unique(join="-")
        _log(logf, "obs_names_make_unique", duplicates_fixed=dup)
    a.obs["sample"] = a.obs["sample"].astype(str)
    a.var["gene_symbols"] = a.var.get("gene_symbols", pd.Series(a.var_names, index=a.var_names))
    _log(logf, "load", kind="10x_triplets", n_samples=len(tri_dirs),
         samples=str([d.name for d in tri_dirs][:8]), shape=str(a.shape))
    return a


# ---------------------------------------------------------------- 主流程
def run_stage_a(input_path, out_dir, species, sample_col="", gene_symbol_col="",
                ensg_map="", group_col="", min_genes=200, max_pct_mt=20.0,
                min_cells=3, resolution=1.0, n_top_genes=2000, n_pcs=50,
                expected_doublet_rate=0.06, seed=20260929, no_scrublet=False,
                no_harmony=False, log=print):
    import scanpy as sc
    import harmonypy
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sc.settings.n_jobs = max(1, min(16, os.cpu_count() or 4))
    out = Path(out_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    logf = out / "stage_a_log.jsonl"

    a = load_input(Path(input_path), logf, sample_col=sample_col)
    a, gene_note = resolve_gene_symbols(a, species, logf, symbol_col=gene_symbol_col,
                                        ensg_map=ensg_map)
    if group_col and "=" in group_col:
        # 三件套形态无 obs 列：用 "样本名=组名;样本名=组名" 映射构造分组
        mp = dict(kv.split("=", 1) for kv in group_col.split(";") if "=" in kv)
        a.obs["group"] = a.obs["sample"].astype(str).map(lambda s: mp.get(s, s)).astype(str)
    elif group_col and group_col in a.obs.columns:
        a.obs["group"] = a.obs[group_col].astype(str)
    elif "disease" in a.obs.columns:
        a.obs["group"] = a.obs["disease"].astype(str)

    # raw counts 校验（只警告不拒收：全零/归一化输入会给出明确诊断）
    X = a.X
    frac_nonint = float(np.asarray((X[:300].toarray() % 1 != 0).mean()) if hasattr(X, "toarray")
                        else (X[:300] % 1 != 0).mean())
    if frac_nonint > 0.01:
        _log(logf, "warn", note=f"X 非整数比例 {frac_nonint:.3f} —— 疑似已归一化输入（README 要求 raw counts），继续但请自查")
    a.layers["counts"] = X.copy()

    # ---- QC 统计与过滤
    sc.pp.filter_cells(a, min_genes=0)
    a.var["mt"] = a.var["mt"].astype(bool)
    sc.pp.calculate_qc_metrics(a, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
    pre = {"n_cells": int(a.shape[0]), "n_genes": int(a.shape[1]),
           "median_genes": float(np.median(a.obs["n_genes_by_counts"])),
           "median_pct_mt": float(np.median(a.obs["pct_counts_mt"]))}
    keep = (a.obs["n_genes_by_counts"] >= min_genes) & (a.obs["pct_counts_mt"] <= max_pct_mt)
    # 基因至少出现在 min_cells 个细胞
    keep_g = np.asarray((a[keep.to_numpy()].X != 0).sum(axis=0)).ravel() >= min_cells
    dbl_call = np.zeros(a.shape[0], dtype=bool)
    dbl_score = np.full(a.shape[0], np.nan)
    if not no_scrublet:
        import scrublet as _sb  # noqa: F401  (走 scanpy 封装，与仓内实测一致)
        ac = a.copy()
        ac.X = ac.layers["counts"]
        sc.pp.scrublet(ac, batch_key="sample", expected_doublet_rate=expected_doublet_rate,
                       random_state=seed, verbose=False)
        dbl_score = ac.obs["doublet_score"].values
        dbl_call = ac.obs["predicted_doublet"].values.astype(bool)
        del ac
    a.obs["doublet_score"] = dbl_score
    a.obs["scrublet_call"] = dbl_call.astype(float)
    a.obs["flag_doublet"] = dbl_call
    a.obs["flag_high_mt"] = (a.obs["pct_counts_mt"] > 10).values
    keep2 = keep & (~pd.Series(dbl_call, index=a.obs_names))
    a_qc = a[keep2.to_numpy() if hasattr(keep2, "to_numpy") else keep2, keep_g].copy()
    post = {"n_cells": int(a_qc.shape[0]), "n_genes": int(a_qc.shape[1]),
            "median_genes": float(np.median(a_qc.obs["n_genes_by_counts"])),
            "median_pct_mt": float(np.median(a_qc.obs["pct_counts_mt"])),
            "removed_lowquality": int((~keep).sum()) if hasattr(keep, "__invert__") else None,
            "removed_doublets": int(dbl_call.sum()),
            "doublet_rate_kept": float(a_qc.obs["flag_doublet"].mean())}
    a = a_qc

    # ---- 标准化 / HVG / PCA（顺序与仓内实测锚点一致）
    a.layers["counts"] = a.X.copy()
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)
    sc.pp.highly_variable_genes(a, n_top_genes=n_top_genes, flavor="seurat")
    sc.pp.pca(a, n_comps=min(n_pcs, a.shape[0] - 1, a.shape[1] - 1), random_state=seed)

    n_samples = int(a.obs["sample"].nunique())
    group_present = bool("group" in a.obs.columns and a.obs["group"].nunique() >= 2)
    use_harmony = (n_samples >= 2) and not no_harmony
    a.uns["batch_correction"] = ("harmony" if use_harmony else
                                 ("disabled_by_flag" if not no_harmony else "none"))
    if use_harmony:
        Z = harmonypy.run_harmony(np.asarray(a.obsm["X_pca"]), a.obs, ["sample"],
                                  random_state=seed, verbose=False).Z_corr
        a.obsm["X_pca_harmony"] = Z.astype(np.float32) if Z.dtype != np.float32 else Z
        rep = "X_pca_harmony"
    else:
        rep = "X_pca"

    # ---- 双空间 UMAP + 聚类（聚类在判读空间 = harmony 空间，若启用）
    sc.pp.neighbors(a, n_neighbors=15, use_rep="X_pca", random_state=seed)
    sc.tl.umap(a, random_state=seed)
    a.obsm["X_umap_uncorrected"] = a.obsm["X_umap"].copy()
    sc.pp.neighbors(a, n_neighbors=15, use_rep=rep, random_state=seed)
    sc.tl.leiden(a, resolution=resolution, key_added="leiden", flavor="igraph",
                 n_iterations=2, directed=False, random_state=seed)
    sc.tl.umap(a, random_state=seed)
    a.obsm["X_umap"] = a.obsm["X_umap"].copy()
    if use_harmony:
        a.obsm["X_umap_harmony"] = a.obsm["X_umap"].copy()

    # ---- marker 表
    sc.tl.rank_genes_groups(a, "leiden", method="wilcoxon", n_genes=30)
    gr = a.uns["rank_genes_groups"]
    names_df = pd.DataFrame(gr["names"]); scores_df = pd.DataFrame(gr["scores"])
    padj_df = pd.DataFrame(gr["pvals_adj"]); lfc_df = pd.DataFrame(gr["logfoldchanges"])
    recs = []
    for c in names_df.columns:
        for k in range(len(names_df)):
            recs.append({"cluster": str(c), "rank": k + 1, "gene": names_df[c].iloc[k],
                         "score": float(scores_df[c].iloc[k]),
                         "pval_adj": float(padj_df[c].iloc[k]),
                         "logfc": float(lfc_df[c].iloc[k])})
    mdf = pd.DataFrame(recs)
    mdf.to_csv(out / "cluster_markers.csv", index=False)
    sizes = a.obs["leiden"].value_counts().sort_index()
    pd.DataFrame({"cluster": sizes.index.astype(str), "n_cells": sizes.values}) \
        .to_csv(out / "cluster_sizes.csv", index=False)

    # ---- 质控图（绝对路径保存，scanpy save= 相对 CWD 教训固化）
    a.obs["cluster"] = a.obs["leiden"].astype(str)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].hist(a.obs["pct_counts_mt"], bins=50, color="#c44")
    axes[0].axvline(max_pct_mt, ls="--", c="k"); axes[0].set_title("pct mito (after QC)")
    axes[0].set_xlabel("% MT")
    axes[1].hist(a.obs["n_genes_by_counts"], bins=50, color="#48c")
    axes[1].axvline(min_genes, ls="--", c="k"); axes[1].set_title("detected genes/cell (after QC)")
    fig.suptitle(f"QC filter: {pre['n_cells']} -> {post['n_cells']} cells "
                 f"(min_genes={min_genes}, max_mt={max_pct_mt}%)")
    ds = np.asarray(a.obs["doublet_score"], dtype=float)
    axes[2].hist(ds[~a.obs["flag_doublet"].values.astype(bool)], bins=50, alpha=0.6, label="singlet")
    axes[2].hist(ds[a.obs["flag_doublet"].values.astype(bool)], bins=50, alpha=0.6, label="doublet")
    axes[2].legend(); axes[2].set_title("Scrublet doublet score")
    plt.tight_layout(); fig.savefig(str(out / "figures" / "qc_filter_doublet.png"), dpi=110)
    plt.close("all")

    fig, axes = plt.subplots(1, (2 if use_harmony else 1), figsize=(7 * (2 if use_harmony else 1), 5.4))
    axes = np.atleast_1d(axes)
    axes[0].scatter(a.obsm["X_umap_uncorrected"][:, 0], a.obsm["X_umap_uncorrected"][:, 1],
                    c=pd.factorize(a.obs["sample"])[0], s=2.5, cmap="tab10")
    axes[0].set_title("UMAP before batch corr. (PCA, colored=sample)")
    if use_harmony:
        axes[1].scatter(a.obsm["X_umap_harmony"][:, 0], a.obsm["X_umap_harmony"][:, 1],
                        c=a.obs["cluster"].astype("category").cat.codes, s=2.5, cmap="tab20")
        axes[1].set_title("UMAP after Harmony (colored=leiden clusters)")
    plt.tight_layout(); fig.savefig(str(out / "figures" / "umap_before_after.png"), dpi=110)
    plt.close("all")
    fig, ax = plt.subplots(figsize=(1.6 + 0.55 * len(sizes), 4))
    ax.bar(sizes.index.astype(str), sizes.values, color="#5a5")
    ax.set_xlabel("cluster"); ax.set_ylabel("n_cells")
    plt.tight_layout(); fig.savefig(str(out / "figures" / "cluster_sizes.png"), dpi=110)
    plt.close("all")

    a.write(out / "processed.h5ad")
    metrics = {"input": str(input_path), "species": species, "gene_id": gene_note,
               "group_present": group_present,
               "qc_pre": pre, "qc_post": post,
               "thresholds": {"min_genes": min_genes, "max_pct_mt": max_pct_mt,
                              "min_cells": min_cells,
                              "expected_doublet_rate": expected_doublet_rate},
               "n_samples": n_samples, "samples": sorted(a.obs["sample"].unique().tolist()),
               "batch_correction": a.uns["batch_correction"], "resolution": resolution,
               "n_clusters": int(a.obs["cluster"].nunique()),
               "cluster_sizes": {str(k): int(v) for k, v in sizes.items()},
               "seed": seed}
    (out / "stage_a_metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False))
    _log(logf, "done", out=str(out / "processed.h5ad"), clusters=metrics["n_clusters"])
    return metrics


def main():
    ap = argparse.ArgumentParser(description="EyeKB pipeline 阶段 A（标准处理，零 LLM）")
    ap.add_argument("--input", required=True, help=".h5ad / 10X 三件套目录 / 多三件套父目录")
    ap.add_argument("--species", required=True, choices=["human", "mouse"])
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--sample-col", default="", help="h5ad 里样本列名（默认用 obs.sample 或输入名）")
    ap.add_argument("--group-col", default="", help="分组列名（对照/疾病等，供疾病先验比对启用）")
    ap.add_argument("--gene-symbol-col", default="", help="var 里符号列名（输入是 ENSG 时）")
    ap.add_argument("--ensg-map", default="", help="ENSG<TAB>SYMBOL 两列 TSV（离线映射）")
    ap.add_argument("--min-genes", type=int, default=200)
    ap.add_argument("--max-pct-mt", type=float, default=20.0)
    ap.add_argument("--min-cells", type=int, default=3)
    ap.add_argument("--resolution", type=float, default=1.0)
    ap.add_argument("--n-top-genes", type=int, default=2000)
    ap.add_argument("--expected-doublet-rate", type=float, default=0.06)
    ap.add_argument("--seed", type=int, default=20260929)
    ap.add_argument("--no-scrublet", action="store_true")
    ap.add_argument("--no-harmony", action="store_true")
    a = ap.parse_args()
    run_stage_a(a.input, a.out, a.species, sample_col=a.sample_col,
                group_col=a.group_col, gene_symbol_col=a.gene_symbol_col,
                ensg_map=a.ensg_map, min_genes=a.min_genes, max_pct_mt=a.max_pct_mt,
                min_cells=a.min_cells, resolution=a.resolution, n_top_genes=a.n_top_genes,
                expected_doublet_rate=a.expected_doublet_rate, seed=a.seed,
                no_scrublet=a.no_scrublet, no_harmony=a.no_harmony)


if __name__ == "__main__":
    main()
