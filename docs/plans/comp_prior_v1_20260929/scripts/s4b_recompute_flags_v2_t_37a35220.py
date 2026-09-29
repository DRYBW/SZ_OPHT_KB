#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s4b_recompute_flags_v2_t_37a35220.py — OB-3 复算 v2: 四规则 + 残差归因交叉表
R0 v0池化(复现门) | R1A 层区间仅A级(预注册主口径) | R1B 层区间=v0公式完整包络(层iqr替换donor_iqr项; 后验敏感性, 标注清楚)
R2A/R2B 单元级敏感性 | 判定<20%只看 R1A(预注册)。
"""
import json, collections, math, pathlib
import pandas as pd
import anndata as ad

EV = pathlib.Path("/mnt/D/EyeKB/plans/evalset")
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
face0 = json.load(open("/mnt/D/EyeKB/kb/composition/EXPECTED_COMPOSITION_v0.json"))
RP0 = {r["cell_type"]: r for r in face0["pages"]["retina_normal_adult_human"]["rows"] if r["low_pct"] is not None}
LAY = json.load(open(OUT / "retina_conditional_intervals.json"))["layers"]

def norm(c): return {"Astro": "Astrocyte", "Micro": "Microglia"}.get(c, c)
RC_A, RC_B = {}, {}
for lid, L in LAY.items():
    a_rows, b_rows = {}, {}
    for c, r in L["classes"].items():
        if not r["support_gate_pass"]: continue
        ct = "Astro" if c == "Astrocyte" else "Micro" if c == "Microglia" else c
        a_rows[ct] = dict(low_pct=r["low_pct"], high_pct=r["high_pct"])
        srcs_lo = [r["iqr_pct"][0]]; srcs_hi = [r["iqr_pct"][1]]
        v0 = RP0.get(ct)
        if v0:
            if v0.get("c_prior_v1"):
                srcs_lo.append(v0["c_prior_v1"]["expected_range_pct"][0])
                srcs_hi.append(v0["c_prior_v1"]["expected_range_pct"][1])
            for la in v0.get("literature_anchors", []):
                if la.get("kind") == "fold":
                    d, val = la["bound"]
                    (srcs_lo if d == "low" else srcs_hi).append(val)
        b_rows[ct] = dict(low_pct=math.floor(min(srcs_lo)), high_pct=math.ceil(max(srcs_hi)))
    RC_A[lid], RC_B[lid] = a_rows, b_rows

# ---------- 真值组装 (同 s4) ----------
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
    return None
M1 = json.load(open(EV/"defs/maps_Q1.json"))["map"]
M2 = json.load(open(EV/"defs/maps_Q2.json"))["map"]
M5 = json.load(open(EV/"defs/Q5b_def.json"))["map"]
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
    obs_rows.append(("Q3", ind + ("_central" if tis.startswith("MR") else "_peripheral"), cl))
a.file.close()
a = ad.read_h5ad(EV/"data/Q4_148077_logcpm.h5ad", backed="r")
for don, cl in zip(a.obs["donor_id"].astype(str), a.obs["mapped_10class"].astype(str)):
    obs_rows.append(("Q4", don, cl))
a.file.close()
import glob
for f in sorted(glob.glob("/mnt/D/OcularKB/data/GSE226108_cellxgene/*.h5ad")):
    a = ad.read_h5ad(f, backed="r")
    g = a.obs[["group", "suspension_enrichment_factors", "cell_type"]]
    a.file.close()
    for grp, enr, ct in zip(g["group"].astype(str), g["suspension_enrichment_factors"].astype(str), g["cell_type"].astype(str)):
        obs_rows.append(("Q5b", grp + "|" + enr, M5.get(ct, ct)))
UN = collections.defaultdict(collections.Counter)
for ds, unit, raw in obs_rows: UN[(ds, unit)][to10(raw) or "OFF"] += 1
DS = {}
for (ds, u), c in UN.items(): DS.setdefault(ds, collections.Counter()).update(c)

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
R1ROUTE = {"Q1_Lukowski2019":"RC1_unsorted_allregion","Q2_GSE155288":"RC1_unsorted_allregion",
           "Q3":"RC1_unsorted_allregion","Q4":"RC4_sorted_or_targeted","Q5b":"RC1_unsorted_allregion"}
HEALTHY = ["Q1_Lukowski2019","Q2_GSE155288","Q3","Q4","Q5b"]
PLAT = {"Q1_Lukowski2019":"cell","Q2_GSE155288":"cell","Q3":"cell(smart-seq)","Q4":"cell(sorted)","Q5b":"nucleus"}
EXP_R0 = {"Q1_Lukowski2019":4,"Q2_GSE155288":4,"Q3":3,"Q4":2,"Q5b":0}

def flags(P, comp):
    tot = sum(comp.values()); out = {}
    for ct, row in P.items():
        pct = 100.0 * comp.get(ct, 0) / tot
        out[ct] = (pct, "FLAG" if (pct < row["low_pct"] or pct > row["high_pct"]) else "ok")
    return out

rows, xtab = [], []
for ds in HEALTHY:
    comp = DS[ds]
    f0 = flags(RP0, comp)
    lidA = R1ROUTE[ds]
    fa = flags(RC_A[lidA], comp); fb = flags(RC_B[lidA], comp)
    n0, na, nb = sum(1 for _, s in f0.values() if s == "FLAG"), sum(1 for _, s in fa.values() if s == "FLAG"), sum(1 for _, s in fb.values() if s == "FLAG")
    assert n0 == EXP_R0[ds], (ds, n0)
    rows.append(dict(dataset=ds, rule="R0_v0_pooled", layer="v0", n=len(RP0), flagged=n0, rate=round(100*n0/len(RP0), 1)))
    rows.append(dict(dataset=ds, rule="R1A_layer_Aonly(PREREG_HEADLINE)", layer=lidA, n=len(RC_A[lidA]), flagged=na, rate=round(100*na/len(RC_A[lidA]), 1)))
    rows.append(dict(dataset=ds, rule="R1B_layer_envelope(post-hoc-sens)", layer=lidA, n=len(RC_B[lidA]), flagged=nb, rate=round(100*nb/len(RC_B[lidA]), 1)))
    # 单元级
    ua = ub = nu = 0; ra = rb = 0.0
    for (d2, u), c in sorted(UN.items()):
        if d2 != ds: continue
        lid = route_unit(ds, u)
        xa = flags(RC_A[lid], c); xb = flags(RC_B[lid], c)
        na_u = sum(1 for _, s in xa.values() if s == "FLAG"); nb_u = sum(1 for _, s in xb.values() if s == "FLAG")
        nu += 1; ua += na_u; ub += nb_u
        ra += 100*na_u/len(xa); rb += 100*nb_u/len(xb)
        rows.append(dict(dataset=ds, rule="R2_unit|A", layer=lid + "|unit=" + u, n=len(xa), flagged=na_u, rate=round(100*na_u/len(xa), 1)))
        rows.append(dict(dataset=ds, rule="R2_unit|B", layer=lid + "|unit=" + u, n=len(xb), flagged=nb_u, rate=round(100*nb_u/len(xb), 1)))
    rows.append(dict(dataset=ds, rule="R2_MEAN(A-interval)", layer=f"{nu} units", n=10, flagged=round(ua/nu, 2), rate=round(ra/nu, 1)))
    rows.append(dict(dataset=ds, rule="R2_MEAN(B-interval)", layer=f"{nu} units", n=10, flagged=round(ub/nu, 2), rate=round(rb/nu, 1)))
    # 逐行交叉表 (归因原料)
    for ct in RP0:
        s0 = f0.get(ct, (None, "absent"))[1]; sa = fa.get(ct, (None, "absent"))[1]; sb = fb.get(ct, (None, "absent"))[1]
        if sa != s0 or sb != s0 or s0 == "FLAG":
            verdict = ("RESOLVED_by_layering" if s0 == "FLAG" and sa != "FLAG" else
                       "NEWFLAG_under_strict_layer" if s0 != "FLAG" and sa == "FLAG" else
                       "PERSISTS_all_rules" if s0 == sa == "FLAG" else "R1B_only_fix" if s0 == "FLAG" and sa == "FLAG" and sb != "FLAG" else "ok")
            xtab.append(dict(dataset=ds, platform=PLAT[ds], row=ct,
                             pct_v0=round(f0.get(ct, (0,))[0], 2), v0=s0, A=sa, B=sb, verdict=verdict))
pd.DataFrame(rows).to_csv(OUT / "stratified_recompute_rows_v2.tsv", sep="\t", index=False)
xt = pd.DataFrame(xtab)
xt.to_csv(OUT / "residual_attribution_xtab.tsv", sep="\t", index=False)
summ = [r for r in rows if r["rule"].startswith(("R0", "R1A", "R1B", "R2_MEAN"))]
print(pd.DataFrame(summ).to_string(index=False))
print("==== xtab verdict counts by dataset×verdict ====")
print(xt.groupby(["dataset", "verdict"]).size().to_string())
print("done s4b")
