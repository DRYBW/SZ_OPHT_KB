#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s2_ocular_surface_t_37a35220.py — OB-2: 眼表面 类型×区域 分层区间 + Q6 分区域重算
区间来源=baselines/ocular_surface.json.strata (A 级盘上现成, 零重聚合)
Q6 组成=Q6_sub100k.h5ad obs(tissue, majorclass, donor_id) 只读
"""
import anndata as ad, json, math, pandas as pd, pathlib

OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
BO = json.load(open("/mnt/D/EyeKB/kb/baselines/ocular_surface.json"))
EXCL = set(e["donor_id"] for e in BO["excluded_nonadult_units"])

# ---- 1. 类型×区域 区间 (支撑门>=5 adult 单元, 与 retina 侧同一机械门)
intervals = {}
for s in BO["strata"]:
    tg = s["tissue_group"]
    n_u = s.get("n_units_adult_only", 0)
    dl = s.get("donor_level_adult_only", {})
    rows = {}
    for c, st in dl.items():
        gate = n_u >= 5
        rows[c] = dict(n_units=n_u, median_pct=st["median_pct"], iqr_pct=st["iqr_pct"],
                       range_pct=st["range_pct"], support_gate_pass=bool(gate),
                       low_pct=(math.floor(st["iqr_pct"][0]) if gate else None),
                       high_pct=(math.ceil(st["iqr_pct"][1]) if gate else None))
    intervals[tg] = rows
json.dump(dict(card="t_37a35220", source="kb/baselines/ocular_surface.json strata (A级)",
               support_gate="n_units_adult_only>=5 否则 any_region 父行回落",
               interval_rule="low=floor(stratum_iqr_low) high=ceil(stratum_iqr_high)",
               region_semantics="行=类型×tissue_group; 禁跨区套用 (category_note 进面语义)",
               groups=intervals),
          open(OUT / "os_conditional_intervals.json", "w"), ensure_ascii=False, indent=1)
print("OS groups:", {k: v[next(iter(v))]["n_units"] for k, v in intervals.items()})

# ---- 2. Q6 分区域重算
T2G = {"cornea": "cornea", "corneal epithelium": "cornea", "substantia propria of cornea": "cornea",
       "corneo-scleral junction": "corneo-scleral junction (limbus 区)",
       "sclera": "sclera", "tunica fibrosa of eyeball": "sclera",
       "ocular surface region": "ocular surface region (混合)",
       "corneal endothelium": "corneal endothelium (单独层, 仅 404 细胞)"}
a = ad.read_h5ad("/mnt/D/EyeKB/plans/evalset/data/Q6_sub100k.h5ad", backed="r")
obs = a.obs[["tissue", "majorclass", "donor_id"]].copy()
a.file.close()
obs = obs[~obs["donor_id"].isin(EXCL)]           # adult-only 与主档同口径
obs["group"] = obs["tissue"].map(T2G)
assert obs["group"].notna().all(), sorted(obs.loc[obs["group"].isna(), "tissue"].unique())
res = []
for g, sub in obs.groupby("group"):
    vc = sub["majorclass"].value_counts()
    tot = int(vc.sum())
    n_u = sub["donor_id"].nunique()
    gate_g = tot >= 500 and g in intervals and intervals[g][next(iter(intervals[g]))]["support_gate_pass"]
    for c, n in vc.items():
        pct = round(100.0 * n / tot, 2)
        if gate_g:
            row = intervals[g][c]
            st = "FLAG_BELOW" if pct < row["low_pct"] else ("FLAG_ABOVE" if pct > row["high_pct"] else "in_range")
            lo, hi = row["low_pct"], row["high_pct"]
        else:
            st, lo, hi = "not_evaluated_small_support" if tot < 500 else "support_gate_fail_region", None, None
        res.append(dict(region=g, n_cells=tot, n_units=n_u, cell_type=c, pct=pct,
                        low=lo, high=hi, status=st))
# any_region (v0 mixed) 对照行: 用 v0 面区间重跑同 adult-only 全池
V0 = json.load(open("/mnt/D/EyeKB/kb/composition/EXPECTED_COMPOSITION_v0.json"))
V0OP = {r["cell_type"]: r for r in V0["pages"]["ocular_surface_normal_adult_human"]["rows"] if r["low_pct"] is not None}
vc = obs["majorclass"].value_counts(); tot = int(vc.sum())
anyreg = []
for c, n in vc.items():
    pct = round(100.0 * n / tot, 2)
    r = V0OP.get(c)
    if r:
        st = "FLAG_BELOW" if pct < r["low_pct"] else ("FLAG_ABOVE" if pct > r["high_pct"] else "in_range")
    else:
        st = "off_face"
    anyreg.append(dict(region="ANY(v0 mixed, adult-only)", n_cells=tot, n_units=obs["donor_id"].nunique(),
                       cell_type=c, pct=pct, low=(r["low_pct"] if r else None), high=(r["high_pct"] if r else None), status=st))
pd.DataFrame(res + anyreg).to_csv(OUT / "q6_recompute_os.tsv", sep="\t", index=False)
nf = {}
for rr in res + anyreg:
    g = rr["region"]; nf.setdefault(g, [0, 0])
    if rr["status"] in ("FLAG_BELOW", "FLAG_ABOVE"): nf[g][0] += 1
    if rr["status"] != "not_evaluated_small_support": nf[g][1] += 1
print("Q6 adult-only by region:", json.dumps(nf, ensure_ascii=False))
print("done s2")
