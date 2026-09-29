#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s1_retina_strata_t_37a35220.py — retina 条件层重聚合（只读 obs，A 级）
输入: /mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad (backed obs)
输出: comp_prior_v1_20260929/retina_strata_units.tsv + retina_conditional_intervals.json
口径: 单元=donor×tissue×enrichment, adult-only(排除 baselines 7 供者), 供者级分布法与 baselines 同式
"""
import anndata as ad, json, pandas as pd, numpy as np, pathlib, math

OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
BR = json.load(open("/mnt/D/EyeKB/kb/baselines/retina.json"))
EXCL = set(e["donor_id"] for e in BR["excluded_nonadult_units"])
TARGET_STUDIES = {"Chen_rgc", "Shekhar_GSE237204"}  # baselines caveat 设计声明=靶向层

a = ad.read_h5ad("/mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad", backed="r")
obs = a.obs[["donor_id", "tissue", "suspension_enrichment_factors", "study_name", "majorclass"]].copy()
a.file.close()
obs = obs[~obs["donor_id"].isin(EXCL)]
for c in ["donor_id", "tissue", "suspension_enrichment_factors", "study_name", "majorclass"]:
    obs[c] = obs[c].astype(str)
obs["enrichment"] = np.where(obs["suspension_enrichment_factors"].isin(["na", "NeuN"]),
                             obs["suspension_enrichment_factors"], "na")
# 路由维: design_layer = sorted_or_targeted (NeuN FACS ∪ 靶向研究) / unsorted
obs["design_layer"] = np.where((obs["enrichment"] == "NeuN") | obs["study_name"].isin(TARGET_STUDIES),
                               "sorted_or_targeted", "unsorted")
obs["region"] = np.where(obs["tissue"] == "peripheral region of retina", "peripheral", "central")
# 单元 = donor × tissue × enrichment (tissue 原4值全保留供审计; 聚合用 region)
obs["unit"] = obs["donor_id"] + "|" + obs["tissue"] + "|" + obs["enrichment"]

ct = pd.crosstab(obs["unit"], obs["majorclass"])
tot = ct.sum(axis=1)
ct = ct[tot > 0]
pct = 100.0 * ct.div(tot, axis=0)
meta = obs.drop_duplicates("unit").set_index("unit")[["donor_id", "tissue", "region", "enrichment",
                                                        "design_layer", "study_name"]]
units = meta.join(pct.round(4)).reset_index()
units["n_cells"] = tot.reindex(units["unit"]).values
units.to_csv(OUT / "retina_strata_units.tsv", sep="\t", index=False)
print("units:", len(units), "adult-only, 排除供者:", len(EXCL))

def iqr_stats(s):
    return dict(n_units=int(s.shape[0]),
                median_pct=round(float(s.median()), 2),
                iqr_pct=[round(float(s.quantile(.25)), 2), round(float(s.quantile(.75)), 2)],
                range_pct=[round(float(s.min()), 2), round(float(s.max()), 2)])

CLASSES = sorted(set(obs["majorclass"].unique()))
layers = {}
defs = {
 "RC1_unsorted_allregion": (units["design_layer"] == "unsorted"),
 "RC2_unsorted_central": (units["design_layer"] == "unsorted") & (units["region"] == "central"),
 "RC3_unsorted_peripheral": (units["design_layer"] == "unsorted") & (units["region"] == "peripheral"),
 "RC4_sorted_or_targeted": (units["design_layer"] == "sorted_or_targeted"),
}
for lid, mask in defs.items():
    sub = units[mask]
    rows = {}
    for c in CLASSES:
        st = iqr_stats(sub[c])
        gate = st["n_units"] >= 5
        rows[c] = dict(**st, support_gate_pass=bool(gate))
        if gate:
            rows[c]["low_pct"] = math.floor(st["iqr_pct"][0])
            rows[c]["high_pct"] = math.ceil(st["iqr_pct"][1])
        else:
            rows[c]["low_pct"] = rows[c]["high_pct"] = None  # 支撑门不过 → 由组装步回落父层
    layers[lid] = dict(unit_def=str(mask.name if hasattr(mask, "name") else lid),
                       n_units=int(mask.sum()), classes=rows)
json.dump(dict(card="t_37a35220", adult_rule="排除 baselines/retina.json excluded_nonadult_units (KB2c)",
               unit_key="donor_id × tissue × enrichment",
               target_studies_per_baselines_caveat=sorted(TARGET_STUDIES),
               interval_rule="low=floor(stratum_iqr_low) high=ceil(stratum_iqr_high) mid=median; 仅A级设计层来源; 单元数<5回落父层",
               layers=layers),
          open(OUT / "retina_conditional_intervals.json", "w"), ensure_ascii=False, indent=1)

# 自校对: RC1 应≈baselines 主档口径但 baselines 把 Shekhar 留在 naive —— 双变体并报
alt = defs["RC1_unsorted_allregion"] & (units["study_name"] != "Shekhar_GSE237204")
sub = units[alt]
chk = {c: iqr_stats(sub[c])["iqr_pct"] for c in ("Rod", "AC", "RGC", "MG", "BC")}
print("RC1-minus-Shekhar iqr:", json.dumps(chk))
print("RC1 n_units:", defs["RC1_unsorted_allregion"].sum(),
      "RC2:", defs["RC2_unsorted_central"].sum(), "RC3:", defs["RC3_unsorted_peripheral"].sum(),
      "RC4:", defs["RC4_sorted_or_targeted"].sum())
print("done")
