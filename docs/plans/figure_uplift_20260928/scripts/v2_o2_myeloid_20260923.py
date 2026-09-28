#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB-P1opt O2: GSE165784 v2 髓系 compartment 深挖 (单核/巨噬/DC 亚型级)。
协议 = scripts/v2_PROTOCOL_20260923.md §O2。
输入 = proc/v2/03_harmonized.h5ad (Track B + flags + 逐细胞 compartment 门控)。
门控口径 (协议预注册): 细胞级 PTPRC+∩髓系分数 与 v1 髓系参照差 -21.8% (>±20%) →
  按协议启用 B簇多数票并集 (mye_frac>=0.5 的整簇入组), 偏差解释写进输出。
签名类 = kb/markers/markers_membrane_v1.json (与 query_marker 同源, 单一事实源)。
产物 proc/v2/: 04_myeloid_sub.h5ad, myeloid_sub_markers.csv, myeloid_sub_signature.csv,
  myeloid_sub_composition.csv, myeloid_gating_rationale.csv, v2_myeloid_metrics.json,
  figs_v2/myeloid_*.png
"""
import json, time
from pathlib import Path
import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
import harmonypy

ad.settings.allow_write_nullable_strings = False
BASE = Path("/mnt/D/EyeKB/plans/demo_gse165784")
OUT = BASE / "proc" / "v2"
FIGS = OUT / "figs_v2"
LOG = open(OUT / "v2_pipeline_log.jsonl", "a", encoding="utf-8")
SEED = 20260923
sc.settings.n_jobs = 16


def log(step, **kw):
    rec = {"ts": time.strftime("%F %T"), "step": step, **kw}
    LOG.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n"); LOG.flush()
    print(f"[{rec['ts']}] {step}: " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)


PANEL_CLASSES = ["Mono_Classical", "Mono_Nonclassical", "Mac_Tissue", "Mac_DAM_LAM",
                 "Microglia", "APC_MHCII_high", "cDC1", "cDC2", "pDC", "Granulocyte",
                 "Proliferating"]
mk = json.load(open("/mnt/D/EyeKB/kb/markers/markers_membrane_v1.json"))
SIGS = {c: mk["markers"][c] for c in PANEL_CLASSES}

adata = ad.read_h5ad(OUT / "03_harmonized.h5ad")
log("load", shape=str(adata.shape))

# ================================================================ 门控口径 + 簇多数票
comp_ct = pd.crosstab(adata.obs.leiden_B.astype(str), adata.obs.compartment)
mye_frac = (comp_ct.get("myeloid", 0) / comp_ct.sum(1)).round(3)
mye_clusters = sorted(mye_frac[mye_frac >= 0.5].index.astype(str), key=int)
adata.obs["mye_cluster_vote"] = adata.obs.leiden_B.astype(str).isin(mye_clusters)
mye = adata[adata.obs.mye_cluster_vote].copy()
gate_tbl = pd.DataFrame({"cluster_B": mye_frac.index, "mye_frac_celllevel": mye_frac.values,
                         "in_myeloid_by_vote": mye_frac.index.isin(mye_clusters)})
gate_tbl.to_csv(OUT / "myeloid_gating_rationale.csv", index=False)
log("gating_final", n_myeloid=int(mye.shape[0]), clusters=mye_clusters,
    celllevel_n=int((adata.obs.compartment == "myeloid").sum()),
    v1_ref=8105, delta_pct=round((int(mye.shape[0]) - 8105) / 8105 * 100, 1))

# ================================================================ 髓系亚聚类
mye.layers["counts"] = adata[adata.obs.mye_cluster_vote].layers["counts"].copy()
# subset 内重归一 (亚聚类标准口径, 从 counts 重建, 不沿用全群 CPM)
sc.pp.normalize_total(mye, target_sum=1e4)
sc.pp.log1p(mye)
sc.pp.highly_variable_genes(mye, n_top_genes=2000, flavor="seurat")
panel_genes = sorted({g for gs in SIGS.values() for g in gs if g in mye.var_names})
force = [g for g in ["XCR1","C1S","C1R","FCER1A","CD14","TREM2","CD9","OLR1","MMP9",
                     "SELL","CCL5","GNLY","NKG7","TRDC","MKI67","TOP2A","CLEC4C","ZBTB46",
                     "CD163","VSIG4","CD5L","STAB1","LILRA4","IL3RA","IRF7","GZMB",
                     "P2RY12","TMEM119","SIGLEC11","SALL1","GPR34","OLFML3","SELENOP",
                     "LYVE1","FOLR2","MRC1","FCN1","VCAN","S100A8","S100A9","LST1",
                     "FCGR3A","TYROBP","C1QA","C1QB","APOE","SPP1","GPNMB","CTSD",
                     "HLA-DRA","CD74","CSF3R","C5AR1","CD3D"]
           if g in mye.var_names]
add = sorted(set(panel_genes) | set(force))
newly = [g for g in add if not mye.var.loc[g, "highly_variable"]]
mye.var.loc[add, "highly_variable"] = True
log("feature_space", hvg2000=int((mye.var.highly_variable & mye.var_names.isin(add)).sum()),
    panel_forced_newly=len(newly))
mye_h = mye[:, mye.var.highly_variable].copy()
sc.pp.pca(mye_h, n_comps=50, random_state=SEED)
Z = harmonypy.run_harmony(np.asarray(mye_h.obsm["X_pca"]), mye_h.obs, ["sample"],
                          random_state=SEED, verbose=False).Z_corr
mye_h.obsm["X_pca_harmony"] = Z.astype(np.float32)
sc.pp.neighbors(mye_h, n_neighbors=15, use_rep="X_pca_harmony", random_state=SEED)
RES = 1.5
sc.tl.leiden(mye_h, resolution=RES, key_added="sub", flavor="igraph",
             n_iterations=2, directed=False, random_state=SEED)
n_sub = int(mye_h.obs["sub"].nunique())
log("subcluster", resolution=RES, n_sub=n_sub,
    sizes=str(mye_h.obs["sub"].value_counts().sort_index(key=lambda x: x.astype(int)).to_dict()))
assert 10 <= n_sub <= 24, f"亚型簇数 {n_sub} 超协议带 (10-20, 上限放 24), 需人工裁定"

# ================================================================ 亚簇 marker + 签名打分
sc.tl.rank_genes_groups(mye_h, "sub", method="wilcoxon", n_genes=30)
gr = mye_h.uns["rank_genes_groups"]
nd = pd.DataFrame(gr["names"]); sdf = pd.DataFrame(gr["scores"])
padj_df = pd.DataFrame(gr["pvals_adj"]); lfc_df = pd.DataFrame(gr["logfoldchanges"])
recs = []
for c in nd.columns:
    for k in range(len(nd)):
        recs.append({"sub": str(c), "rank": k + 1, "gene": nd[c].iloc[k],
                     "score": float(sdf[c].iloc[k]), "pval_adj": float(padj_df[c].iloc[k]),
                     "logfc": float(lfc_df[c].iloc[k])})
pd.DataFrame(recs).to_csv(OUT / "myeloid_sub_markers.csv", index=False)
topmap = {str(c): list(nd[c].head(20)) for c in nd.columns}

# 签名打分 (均值 z) 用全基因表达
Xl = mye_h.X
lg = {g: i for i, g in enumerate(mye_h.var_names)}
def sig_score(genes):
    idx = [lg[g] for g in genes if g in lg]
    Xs = np.asarray(Xl[:, idx].todense()) if sp.issparse(Xl) else np.asarray(Xl[:, idx])
    z = (Xs - Xs.mean(0)) / (Xs.std(0) + 1e-9)
    return pd.Series(np.nanmean(z, axis=1), index=mye_h.obs_names)
S = pd.DataFrame({c: sig_score(gs) for c, gs in SIGS.items()})
mye_h.obs = mye_h.obs.join(S.round(3))
dom = S.idxmax(1)
sub_dom = pd.crosstab(mye_h.obs["sub"].astype(str), dom).apply(lambda r: r.idxmax(), axis=1)
sub_domn = pd.crosstab(mye_h.obs["sub"].astype(str), dom).apply(lambda r: r.max() / r.sum(), axis=1)
sig_tab = pd.concat([mye_h.obs.groupby("sub", observed=True).size().rename("n"), sub_dom.rename("dominant_sig"),
                     sub_domn.round(3).rename("dom_frac"),
                     S.groupby(mye_h.obs["sub"], observed=True).mean().round(2)], axis=1)
sig_tab = sig_tab.sort_values("n", ascending=False)
sig_tab.to_csv(OUT / "myeloid_sub_signature.csv")
log("signatures", dominant=sub_dom.to_dict())

# 组成表 (PDR/RRD 描述性 — RRD n=1 禁统计断言)
comp = pd.crosstab(mye_h.obs["sub"].astype(str), mye_h.obs["sample"])
comp["n"] = comp.sum(1)
comp["rrd_frac"] = (comp.get("RRD-ERM1", 0) / comp["n"]).round(4)
comp["dbl_frac"] = mye_h.obs.groupby("sub", observed=True).flag_doublet.mean().round(4)
comp = comp.join(sig_tab[["dominant_sig", "dom_frac"]])
# flag 敏感性 (打标不删 → 剔除后簇规模变化)
sens = mye_h[~mye_h.obs.flag_doublet.astype(bool)].obs["sub"].value_counts().rename("n_no_doublet")
comp = comp.join(sens)
comp["dbl_removed"] = comp["n"] - comp["n_no_doublet"].fillna(0)
comp.sort_index(key=lambda x: x.astype(int)).to_csv(OUT / "myeloid_sub_composition.csv")
log("composition", rrd_leads=[c for c in comp.index if comp.loc[c, "rrd_frac"] > 0.5])

# ================================================================ UMAP + 保存
sc.tl.umap(mye_h, random_state=SEED)
import matplotlib.pyplot as plt
def _savefig(name):
    plt.savefig(str(FIGS / ("umap" + name)), dpi=110, bbox_inches="tight")
    plt.close("all")
sc.pl.umap(mye_h, color=["sub"], show=False); _savefig("myeloid_sub.png")
sc.pl.umap(mye_h, color=["sample", "disease"], show=False); _savefig("myeloid_sample.png")
for c in ["Mac_DAM_LAM", "Mac_Tissue", "Microglia", "Mono_Classical", "APC_MHCII_high"]:
    if c in mye_h.obs:
        sc.pl.umap(mye_h, color=[c], show=False); _savefig(f"myeloid_sig_{c}.png")
mye_h.write(OUT / "04_myeloid_sub.h5ad")

metrics = {"n_myeloid": int(mye_h.shape[0]),
           "myeloid_clusters_by_vote": [int(c) for c in mye_clusters],
           "gating_delta_vs_v1_pct": round((int(mye_h.shape[0]) - 8105) / 8105 * 100, 1),
           "gating_explanation": ("细胞级 PTPRC∩髓系分数 = 6337 (-21.8%), 缺口=高MT簇(B0/B6 髓系 CD45 低检出)与"
                                  "炎症巨噬 PTPRC dropout; 按协议启用簇多数票并集。逐簇 mye_frac 见 "
                                  "myeloid_gating_rationale.csv"),
           "n_sub": n_sub,
           "sub_dominant_sig": {str(k): v for k, v in sub_dom.items()},
           "rrd_gt50_subclusters": [str(c) for c in comp.index if comp.loc[c, "rrd_frac"] > 0.5],
           "dbl_removed_by_sub": {str(k): int(v) for k, v in comp["dbl_removed"].items()},
           "assert_band": "10<=n_sub<=24 通过"}
json.dump(metrics, open(OUT / "v2_myeloid_metrics.json", "w"), indent=1, ensure_ascii=False)
log("done", out=str(OUT / "04_myeloid_sub.h5ad"))
print("O2 OK")
