#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB-P1opt O1+O3: GSE165784 v2 — Harmony batch 整合双轨重聚类 + Scrublet/质量打标。
协议 = scripts/v2_PROTOCOL_20260923.md。输入 proc/01_qc.h5ad (X=raw counts)。
产物 (全部新目录 proc/v2/, v1 零改动):
  03_harmonized.h5ad  obs: sample/disease/leiden_v1_trackA/leiden_harmony_B/
                       scrublet_score/scrublet_call/flag_doublet/flag_high_mt/
                       flag_suspect_cluster/compartment
  track_ab_crosstab.csv / track_ab_marker_jaccard.csv / cluster_composition_B.csv
  cluster_markers_harmony.csv (Track B top30 wilcoxon + mean_expr, 与 v1 同构)
  figs_v2/umap_trackA.png umap_trackB.png umap_sampleB.png umap_scrublet.png
  v2_metrics.json (ARI/Jaccard/组成漂移/Scrublet 汇总, 供 EVAL)
CPU-only; seed 20260923; 中间产物保留。
"""
import json, time
from pathlib import Path
import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
import harmonypy
import scrublet as sb
from sklearn.metrics import adjusted_rand_score

ad.settings.allow_write_nullable_strings = False

BASE = Path("/mnt/D/EyeKB/plans/demo_gse165784")
PROC, OUT = BASE / "proc", BASE / "proc" / "v2"
OUT.mkdir(exist_ok=True)
FIGS = OUT / "figs_v2"; FIGS.mkdir(exist_ok=True)
LOG = open(OUT / "v2_pipeline_log.jsonl", "a", encoding="utf-8")
SEED = 20260923
sc.settings.n_jobs = 16


def log(step, **kw):
    rec = {"ts": time.strftime("%F %T"), "step": step, **kw}
    LOG.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n"); LOG.flush()
    print(f"[{rec['ts']}] {step}: " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)


def marker_table(adata, key, out_csv, topn=30):
    sc.tl.rank_genes_groups(adata, key, method="wilcoxon", n_genes=topn)
    gr = adata.uns["rank_genes_groups"]
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
    allg = sorted(mdf.gene.unique())
    expr = pd.DataFrame(index=allg)
    for c in names_df.columns:
        sub = adata[adata.obs[key].astype(str) == str(c)]
        col = {}
        for g in allg:
            if g in adata.var_names:
                x = sub[:, g].X
                col[g] = float(np.asarray(x.todense()).mean() if sp.issparse(x) else x.mean())
        expr[f"mean_{c}"] = pd.Series(col)
    melted = expr.stack().rename("mean_expr").reset_index()
    melted.columns = ["gene", "cluster_col", "mean_expr"]
    melted["cluster"] = melted.cluster_col.str.replace("mean_", "", regex=False)
    mdf = mdf.merge(melted[["gene", "cluster", "mean_expr"]], on=["gene", "cluster"], how="left")
    mdf.to_csv(out_csv, index=False)
    # 返回 {cluster: top-N genes}
    return {str(c): list(names_df[c].head(30)) for c in names_df.columns}


# ================================================================ 载入 + 标准化
adata = ad.read_h5ad(PROC / "01_qc.h5ad")
log("load", shape=str(adata.shape))
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
sc.pp.pca(adata, n_comps=50, random_state=SEED)

# ---- Track A: v1 真实标签直接继承 (比"重跑复现"更忠实; 重跑仅作复现性观察)
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca", random_state=SEED)
sc.tl.leiden(adata, resolution=1.0, key_added="leiden_A_rerun", flavor="igraph",
             n_iterations=2, directed=False, random_state=SEED)
v1 = ad.read_h5ad(PROC / "02_clustered.h5ad")
assert set(v1.obs_names) == set(adata.obs_names), "v1 与 01_qc 细胞集不一致!"
adata.obs["leiden_A"] = v1.obs["leiden"].reindex(adata.obs_names).astype(str).values
ari_repro = adjusted_rand_score(adata.obs.leiden_A, adata.obs.leiden_A_rerun)
log("trackA", n_clusters=int(adata.obs.leiden_A.nunique()), ari_rerun_vs_v1=round(float(ari_repro), 4),
    note="TrackA=v1真实标签; rerun仅复现性观察(BLAS浮点非确定)")
del v1

# ---- Track B: Harmony (batch=sample) 整合
Z = harmonypy.run_harmony(np.asarray(adata.obsm["X_pca"]), adata.obs, ["sample"],
                          random_state=SEED, verbose=False).Z_corr
adata.obsm["X_pca_harmony"] = Z.astype(np.float32) if Z.dtype != np.float32 else Z
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca_harmony", random_state=SEED)
sc.tl.leiden(adata, resolution=1.0, key_added="leiden_B", flavor="igraph",
             n_iterations=2, directed=False, random_state=SEED)
log("trackB", n_clusters=int(adata.obs.leiden_B.nunique()),
    sizes=str(adata.obs.leiden_B.value_counts().sort_index().to_dict()))

# UMAP (各轨自己的邻域图 → 忠实反映其聚类空间)
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca", random_state=SEED)
sc.tl.umap(adata, random_state=SEED); adata.obsm["X_umap_A"] = adata.obsm["X_umap"].copy()
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca_harmony", random_state=SEED)
sc.tl.umap(adata, random_state=SEED); adata.obsm["X_umap_B"] = adata.obsm["X_umap"].copy()
# 图必须绝对路径保存 (scanpy 1.12 save= 相对 CWD 落过 ~/figures, 教训固化)
import matplotlib.pyplot as plt
def _savefig(name):
    plt.savefig(str(FIGS / name), dpi=110, bbox_inches="tight")
    plt.close("all")
tmp = adata.copy()
tmp.obsm["X_umap"] = tmp.obsm["X_umap_A"]
sc.pl.umap(tmp, color=["leiden_A"], show=False); _savefig("umap_trackA.png")
sc.pl.umap(tmp, color=["sample", "disease"], show=False); _savefig("umap_sampleA.png")
tmp.obsm["X_umap"] = tmp.obsm["X_umap_B"]
sc.pl.umap(tmp, color=["leiden_B"], show=False); _savefig("umap_trackB.png")
sc.pl.umap(tmp, color=["sample", "disease"], show=False); _savefig("umap_sampleB.png")
del tmp

# ================================================================ O3: Scrublet 逐样本 + 质量 flag
# scanpy 1.12 封装: 吃 adata.X (counts), 固定写 obs['doublet_score'/'predicted_doublet'];
# 用 counts 副本跑, batch_key=sample 逐样本; 本地 scrublet 裸 API 不稳不再直用
ac = adata.copy()
ac.X = ac.layers["counts"]
sc.pp.scrublet(ac, batch_key="sample", expected_doublet_rate=0.06,
               random_state=SEED, verbose=False)
adata.obs["scrublet_score"] = ac.obs["doublet_score"].values
adata.obs["scrublet_call"] = ac.obs["predicted_doublet"].astype(float).values
del ac
per_sample = {}
for s in adata.obs["sample"].cat.categories if hasattr(adata.obs["sample"], "cat") else adata.obs["sample"].unique():
    m = adata.obs["sample"] == s
    per_sample[str(s)] = {"n": int(m.sum()), "n_doublet": int(adata.obs.loc[m, "scrublet_call"].sum()),
                          "rate": round(float(adata.obs.loc[m, "scrublet_call"].mean()), 4)}
    log("scrublet", sample=str(s), **per_sample[str(s)])
adata.obs["flag_doublet"] = adata.obs["scrublet_call"].astype(bool)
adata.obs["flag_high_mt"] = adata.obs["pct_counts_mt"] >= 10

# ================================================================ 双轨 marker 一致性
topA = marker_table(adata, "leiden_A", OUT / "cluster_markers_trackA.csv")
topB = marker_table(adata, "leiden_B", OUT / "cluster_markers_harmony.csv")
ct = pd.crosstab(adata.obs.leiden_A.astype(str), adata.obs.leiden_B.astype(str))
ct.to_csv(OUT / "track_ab_crosstab.csv")
rows = []
for b in ct.columns:
    nb = int(ct[b].sum())
    a_dom = ct[b].idxmax(); share = float(ct[b].max()) / max(nb, 1)
    ja, jb = set(topA[a_dom]), set(topB[b])
    jac = len(ja & jb) / max(len(ja | jb), 1)
    rows.append({"cluster_B": b, "n_B": nb, "dominant_A": a_dom, "share_from_dominant_A": round(share, 3),
                 "jaccard_top30": round(jac, 3)})
cons = pd.DataFrame(rows).sort_values("cluster_B", key=lambda x: x.astype(int))
cons.to_csv(OUT / "track_ab_marker_jaccard.csv", index=False)
log("consistency", median_jaccard=float(np.median(cons.jaccard_top30)),
    low_jaccard=list(cons[cons.jaccard_top30 < 0.2].cluster_B))

# 组成表 (Track B) — RRD 混杂检查
comp = pd.crosstab(adata.obs.leiden_B.astype(str), adata.obs["sample"])
comp["n"] = comp.sum(1); comp["rrd_frac"] = (comp.get("RRD-ERM1", 0) / comp["n"]).round(4)
comp["pdr_frac"] = (1 - comp["rrd_frac"]).round(4)
comp.sort_index(key=lambda x: x.astype(int)).to_csv(OUT / "cluster_composition_B.csv")
log("composition", rrd_global=round(float((adata.obs["sample"] == "RRD-ERM1").mean()), 4))

# ================================================================ 髓系门控 (O2 用)
def panel_score(genes):
    gs = [g for g in genes if g in adata.var_names]
    X = adata[:, gs].X
    X = np.asarray(X.todense()) if sp.issparse(X) else np.asarray(X)
    z = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return z.mean(1)

MYE = ["TYROBP", "C1QA", "C1QB", "FCN1", "VCAN", "S100A8", "S100A9", "LYZ", "CD74",
       "MRC1", "CTSS", "AIF1", "FCGR3A"]
LYM = ["CD3D", "CD3E", "CD2", "TRAC", "IL7R", "MS4A1", "CD79A", "MZB1", "JCHAIN"]
ptprc = np.asarray((adata[:, "PTPRC"].X > 0).todense()).ravel()
adata.obs["score_mye"] = panel_score(MYE)
adata.obs["score_lym"] = panel_score(LYM)
adata.obs["compartment"] = "other"
adata.obs.loc[ptprc & (adata.obs.score_mye > adata.obs.score_lym), "compartment"] = "myeloid"
adata.obs.loc[ptprc & (adata.obs.score_lym >= adata.obs.score_mye), "compartment"] = "lymphoid"
n_mye = int((adata.obs.compartment == "myeloid").sum())
log("gating", myeloid=n_mye, lymphoid=int((adata.obs.compartment == "lymphoid").sum()),
    v1_ref=8105, delta_pct=round((n_mye - 8105) / 8105 * 100, 1))

# suspect cluster flag: Track B 簇级 MT/核糖体 z>2
ribo = [g for g in adata.var_names if str(g).startswith(("RPL", "RPS"))]
Xr = adata[:, ribo].X; Xr = np.asarray(Xr.todense()) if sp.issparse(Xr) else np.asarray(Xr)
adata.obs["pct_ribo"] = np.asarray((Xr.sum(1) / np.clip(np.asarray(adata.layers["counts"].sum(1)).ravel(), 1, None) * 100)).ravel()
cl = adata.obs.groupby("leiden_B", observed=True).agg(mt=("pct_counts_mt", "mean"),
                                                      rb=("pct_ribo", "mean"),
                                                      dbl=("flag_doublet", "mean"), n=("leiden_B", "size"))
z = (cl - cl.mean()) / (cl.std(ddof=0) + 1e-9)
sus = set(cl.index[(z[["mt", "rb"]].max(1) > 2) | (z["dbl"] > 2)])
adata.obs["flag_suspect_cluster"] = adata.obs.leiden_B.astype(str).isin([str(c) for c in sus])
log("suspect_clusters", sus=sorted([str(c) for c in sus]))
cl.to_csv(OUT / "cluster_quality_summary.csv")

adata.write(OUT / "03_harmonized.h5ad")
tmp = adata.copy(); tmp.obsm["X_umap"] = tmp.obsm["X_umap_B"]
sc.pl.umap(tmp, color=["compartment", "flag_doublet"], show=False)
_savefig("umap_compartment_doublet.png")
del tmp

metrics = {
    "n_cells": int(adata.shape[0]),
    "trackA_clusters": int(adata.obs.leiden_A.nunique()),
    "trackB_clusters": int(adata.obs.leiden_B.nunique()),
    "ari_trackA_vs_v1": round(float(ari_repro), 4),
    "median_jaccard_AB": float(np.median(cons.jaccard_top30)),
    "low_jaccard_clusters": list(cons[cons.jaccard_top30 < 0.2].cluster_B.astype(str)),
    "rrd_frac_global": round(float((adata.obs["sample"] == "RRD-ERM1").mean()), 4),
    "clusters_rrd_gt95pct_trackA": [c for c in adata.obs.leiden_A.astype(str).unique()
        if float((adata.obs[adata.obs.leiden_A.astype(str) == c]["sample"] == "RRD-ERM1").mean()) > 0.95],
    "clusters_rrd_gt95pct_trackB": [c for c in adata.obs.leiden_B.astype(str).unique()
        if float((adata.obs[adata.obs.leiden_B.astype(str) == c]["sample"] == "RRD-ERM1").mean()) > 0.95],
    "scrublet_per_sample": per_sample,
    "doublet_total": int(adata.obs.flag_doublet.sum()),
    "doublet_rate": round(float(adata.obs.flag_doublet.mean()), 4),
    "flag_high_mt": int(adata.obs.flag_high_mt.sum()),
    "suspect_clusters": sorted([str(c) for c in sus]),
    "myeloid_n": n_mye,
}
json.dump(metrics, open(OUT / "v2_metrics.json", "w"), indent=1, ensure_ascii=False)
log("done", out=str(OUT / "03_harmonized.h5ad"))
print("O1O3 OK")
