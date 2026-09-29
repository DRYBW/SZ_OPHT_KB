#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s4_recompute_flags_t_37a35220.py — OB-3 分层反向质检复算
规则(预注册 PHASE0 §3): R0=v0 池化区间(复现 SELFFLAG 数字自校对); R1=数据集级路由层;
R2=单元级(供者/样本×匹配层)敏感性. 20% 线不动.
真值输入=evalset 冻结件 + 成员 h5ad obs 真值列 (作者级; 非自家聚类).
"""
import json, csv, collections, math, pathlib
import pandas as pd

EV = pathlib.Path("/mnt/D/EyeKB/plans/evalset")
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
face0 = json.load(open("/mnt/D/EyeKB/kb/composition/EXPECTED_COMPOSITION_v0.json"))
RP = {r["cell_type"]: r for r in face0["pages"]["retina_normal_adult_human"]["rows"] if r["low_pct"] is not None}
LAY = json.load(open(OUT / "retina_conditional_intervals.json"))["layers"]
def lay_rows(lid):
    return {("Astro" if c == "Astrocyte" else "Micro" if c == "Microglia" else c): r
            for c, r in LAY[lid]["classes"].items() if r["support_gate_pass"]}
RC = {lid: lay_rows(lid) for lid in LAY}

# ---- 真值组装 (selfcheck_comp_v0.py 同源映射表, 冻结件只读)
SHORTS = {"Rod","Cone","BC","AC","HC","RGC","MG","Astro","Micro","RPE"}
REMAP10 = {"retinal rod cell":"Rod","retinal cone cell":"Cone","amacrine cell":"AC",
 "retinal horizontal cell":"HC","Mueller cell":"MG","astrocyte":"Astro","microglial cell":"Micro",
 "retinal pigment epithelial cell":"RPE","retinal ganglion cell":"RGC"}
BCP = ("ON-bipolar","OFF-bipolar","retinal bipolar")
Q2_ALIAS = {"Bipolar":"BC","Muller":"MG","Amacrine":"AC","Microglia":"Micro","Astrocytes":"Astro",
 "Horizontal":"HC","Ganglion":"RGC","Rod":"Rod","Cone":"Cone"}
def to10(raw):
    if raw in SHORTS: return raw
    if raw in Q2_ALIAS: return Q2_ALIAS[raw]
    if raw in REMAP10: return REMAP10[raw]
    if raw.startswith(BCP): return "BC"
    rl = raw.lower()
    for pat, ct in [("ganglion","RGC"),("horizontal","HC"),("bipolar","BC"),("amacrine","AC"),
                    ("rod cell","Rod"),("cone cell","Cone"),("mueller","MG"),("müller","MG"),
                    ("microglia","Micro"),("astrocyt","Astro"),("pigment epithel","RPE")]:
        if pat in rl: return ct
    return None  # off-face

M1 = json.load(open(EV/"defs/maps_Q1.json"))["map"]
M2 = json.load(open(EV/"defs/maps_Q2.json"))["map"]
M5 = json.load(open(EV/"defs/Q5b_def.json"))["map"]

def unitize(rows):  # rows: (dataset, unit, raw_label)
    d = collections.defaultdict(collections.Counter)
    for ds, unit, raw in rows: d[(ds, unit)][to10(raw) or "OFF"] += 1
    return d

import anndata as ad
obs_rows = []
a = ad.read_h5ad("/mnt/D/OcularKB/data/GSE137400/lukowski2019_retina.h5ad", backed="r")
for don, raw in zip(a.obs["donor_id"].astype(str), a.obs["author_cell_type"].astype(str)):
    obs_rows.append(("Q1_Lukowski2019", don, M1.get(raw, raw)))
a.file.close()
a = ad.read_h5ad("/mnt/D/OcularKB/data/GSE155288/GSE155288_annotated.h5ad", backed="r")
for don, reg, raw in zip(a.obs["donor"].astype(str), a.obs["region"].astype(str), a.obs["author_cell_type"].astype(str)):
    obs_rows.append(("Q2_GSE155288", don + "_" + reg, M2.get(raw, raw)))
a.file.close()
a = ad.read_h5ad(EV/"data/Q3_137537_logcpm.h5ad", backed="r")
for ind, tis, cl in zip(a.obs["individual"].astype(str), a.obs["tissue"].astype(str), a.obs["mapped_10class"].astype(str)):
    obs_rows.append(("Q3", ind + "_" + ("central" if tis.startswith("MR") else "peripheral"), cl))
a.file.close()
a = ad.read_h5ad(EV/"data/Q4_148077_logcpm.h5ad", backed="r")
for don, cl in zip(a.obs["donor_id"].astype(str), a.obs["mapped_10class"].astype(str)):
    obs_rows.append(("Q4", don, cl))
a.file.close()
# Q5b: 全量 412,419 (7 源文件 obs; 单元=sample group × enrichment; 与 SELFFLAG 同源)
import glob
tot5b = 0
for f in sorted(glob.glob("/mnt/D/OcularKB/data/GSE226108_cellxgene/*.h5ad")):
    a = ad.read_h5ad(f, backed="r")
    g = a.obs[["group", "suspension_enrichment_factors", "cell_type"]]
    a.file.close()
    tot5b += len(g)
    for grp, enr, ct in zip(g["group"].astype(str), g["suspension_enrichment_factors"].astype(str), g["cell_type"].astype(str)):
        obs_rows.append(("Q5b", grp + "|" + enr, M5.get(ct, ct)))
assert tot5b == 412419, tot5b

UN = unitize(obs_rows)
# 数据集级组成 (池)
DS = {}
for (ds, u), c in UN.items():
    DS.setdefault(ds, collections.Counter()).update(c)

# ---- R2 单元路由 (机械): NeuN/targeted→RC4; region central→RC2 / peripheral→RC3; 未知→RC1
def route_unit(ds, unit):
    if ds == "Q5b":
        if unit.endswith("|NeuN"): return "RC4_sorted_or_targeted"
        if "_fovea" in unit or "_macular" in unit: return "RC2_unsorted_central"
        if "_per" in unit: return "RC3_unsorted_peripheral"
        return "RC1_unsorted_allregion"
    if ds == "Q4": return "RC4_sorted_or_targeted"
    if "central" in unit or unit.endswith("_M"): return "RC2_unsorted_central"
    if "peripheral" in unit or unit.endswith("_P"): return "RC3_unsorted_peripheral"
    return "RC1_unsorted_allregion"
# ---- R1 数据集路由 (PHASE0 §3 预注册)
R1ROUTE = {"Q1_Lukowski2019":"RC1_unsorted_allregion","Q2_GSE155288":"RC1_unsorted_allregion",
           "Q3":"RC1_unsorted_allregion","Q4":"RC4_sorted_or_targeted","Q5b":"RC1_unsorted_allregion"}
HEALTHY = ["Q1_Lukowski2019","Q2_GSE155288","Q3","Q4","Q5b"]
UNIT_DET = {}
EXP_R0 = {"Q1_Lukowski2019":4,"Q2_GSE155288":4,"Q3":3,"Q4":2,"Q5b":0}  # SELFFLAG §1 复现门

def flagset(P, comp):
    tot = sum(comp.values())
    out = []
    for ct, row in P.items():
        pct = 100.0 * comp.get(ct, 0) / tot
        lo = row["low_pct"] if "low_pct" in row else row["low"]
        hi = row["high_pct"] if "high_pct" in row else row["high"]
        st = "FLAG_BELOW" if pct < lo else ("FLAG_ABOVE" if pct > hi else "in_range")
        out.append((ct, round(pct, 2), lo, hi, st))
    return out

rows = []
summary = []
for ds in HEALTHY:
    comp = DS[ds]
    r0 = flagset(RP, comp)
    n0 = sum(1 for *_, s in r0 if s.startswith("FLAG"))
    ok = (n0 == EXP_R0[ds])
    summary.append(dict(dataset=ds, rule="R0_v0_pooled", n_face_rows=len(RP), n_flagged=n0,
                        flag_pct=round(100*n0/len(RP), 1), reverseQC=("TRIGGER" if 100*n0/len(RP) > 20 else "under"),
                        reproduce_SELFFLAG=("PASS" if ok else f"MISMATCH exp={EXP_R0[ds]}")))
    for ct, pct, lo, hi, st in r0:
        rows.append(dict(dataset=ds, rule="R0_v0_pooled", layer="v0_any_design", row=ct, pct=pct, low=lo, high=hi, status=st))
    P = RC[R1ROUTE[ds]]
    r1 = flagset(P, comp)
    n1 = sum(1 for *_, s in r1 if s.startswith("FLAG"))
    summary.append(dict(dataset=ds, rule=f"R1_routed[{R1ROUTE[ds].split('_')[0]}]", n_face_rows=len(P), n_flagged=n1,
                        flag_pct=round(100*n1/len(P), 1), reverseQC=("TRIGGER" if 100*n1/len(P) > 20 else "under"),
                        reproduce_SELFFLAG="n/a"))
    for ct, pct, lo, hi, st in r1:
        rows.append(dict(dataset=ds, rule=f"R1_routed[{R1ROUTE[ds].split('_')[0]}]", layer=R1ROUTE[ds], row=ct, pct=pct, low=lo, high=hi, status=st))
    # R2 单元级
    per_unit, hi_units = [], 0
    for (d2, u), c in sorted(UN.items()):
        if d2 != ds: continue
        lid = route_unit(ds, u)
        rr = flagset(RC[lid], c)
        nf = sum(1 for *_, s in rr if s.startswith("FLAG"))
        rate = 100*nf/len(RC[lid])
        per_unit.append((u, lid, nf, rate, [(x[0], x[1], x[4]) for x in rr if x[4].startswith("FLAG")]))
        hi_units += (rate > 20)
    mean_rate = sum(x[3] for x in per_unit)/len(per_unit)
    summary.append(dict(dataset=ds, rule="R2_unit_level(sensitivity)", n_face_rows=len(RC['RC1_unsorted_allregion']),
                        n_flagged=hi_units, flag_pct=round(mean_rate, 1),
                        reverseQC=(f"{hi_units}/{len(per_unit)} units>20%"), reproduce_SELFFLAG="n/a"))
    for u, lid, nf, rate, det in per_unit:
        rows.append(dict(dataset=ds, rule="R2_unit_level(sensitivity)", layer=lid + "|unit=" + u,
                         row="UNIT_SUMMARY", pct=round(rate, 1), low=None, high=None,
                         status=f"{nf}/10 flagged: " + ";".join(f"{a_}={b_}({c_})" for a_, b_, c_ in det)))
    UNIT_DET[ds] = per_unit
pd.DataFrame(summary).to_csv(OUT / "stratified_recompute_summary.tsv", sep="\t", index=False)
pd.DataFrame(rows).to_csv(OUT / "stratified_recompute_rows.tsv", sep="\t", index=False)
print(pd.DataFrame(summary).to_string(index=False))
with open(OUT / "logs/s4_unit_detail.json", "w") as f:
    json.dump(UNIT_DET, f, ensure_ascii=False, indent=1)
print("done s4")
