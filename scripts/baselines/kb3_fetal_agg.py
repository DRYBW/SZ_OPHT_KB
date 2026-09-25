#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W1: 发育期锚点数据标签聚合 (只读源, 产出 retina__fetal_developing 条目素材)。

源 1 GSE268630 portal h5ad: obs[majorclass, cell_type, development_stage, donor_id, tissue]
    → 全细胞标签直方图 (portal 作者注释, 非现役引擎推断)。
源 2 GSE138002 Final_barcodes.csv.gz: col[umap2_CellType, sample]
    → 按样本面拆层: Hgw*=胎网(收录), Hpnd8*=新生, Adult=成人对照, *_Day=类器官 (后三类只列不并入)。
源 3 GSE234963: 无公开标签 (obs 空) → 只出数据卡。
纪律: 本脚本不实算组成分类 (无 fetal 参考管线), 仅聚合**作者/portal 已发布标签**的分布 ——
      "只写有据条目"的"据"= 官方注释标签本身。
产物: plans/kb3_evidence/fetal_agg_20260924.json
"""
import gzip
import json
import re
from collections import Counter
from pathlib import Path

import h5py
import numpy as np

OUT = Path("/mnt/D/EyeKB/plans/kb3_evidence")
OUT.mkdir(exist_ok=True)
H268 = "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad"
H138 = "/mnt/D/OcularKB/data/GSE138002/GSE138002_Final_barcodes.csv.gz"


def cat_col(f, name):
    g = f["obs/" + name]
    if isinstance(g, h5py.Dataset):
        return [s.decode() for s in g[:]]
    codes = g["codes"][:]
    cats = [c.decode() for c in g["categories"][:]]
    return [cats[c] if c >= 0 else "" for c in codes]


# ---- 源1: GSE268630 ----
res268 = {}
with h5py.File(H268, "r") as f:
    n = f["obs/_index"].shape[0]
    mc = Counter(cat_col(f, "majorclass"))
    ds = Counter(cat_col(f, "development_stage"))
    dt = Counter(cat_col(f, "tissue"))
    donors = set(cat_col(f, "donor_id"))
    ct = Counter(cat_col(f, "cell_type"))
res268 = {"cells_total": int(n), "n_donors": len(donors),
          "majorclass_hist": dict(mc.most_common()),
          "majorclass_pct": {k: round(100 * v / n, 2) for k, v in mc.most_common()},
          "development_stage_hist": dict(ds.most_common()),
          "tissue_hist": dict(dt.most_common()),
          "cell_type_hist_top30": dict(ct.most_common(30))}

# ---- 源2: GSE138002 Final (作者注释) ----
strata = {"fetal_Hgw": Counter(), "postnatal_Hpnd": Counter(),
          "adult_Adult": Counter(), "organoid_Day": Counter()}
samp = {"fetal_Hgw": set(), "postnatal_Hpnd": set(),
        "adult_Adult": set(), "organoid_Day": set()}
gw_re = re.compile(r"Hp?gw(\d+)")
with gzip.open(H138, "rt") as fh:
    header = fh.readline().rstrip("\n\r").split(";")
    i_s, i_c = header.index('"sample"'), header.index('"umap2_CellType"')
    total = 0
    for ln in fh:
        p = ln.rstrip("\n\r").split(";")
        if len(p) <= i_c:
            continue
        s, c = p[i_s].strip('"'), p[i_c].strip('"')
        total += 1
        if s.startswith("Hpnd"):
            key = "postnatal_Hpnd"
        elif s.startswith("Hgw"):
            key = "fetal_Hgw"
        elif s == "Adult":
            key = "adult_Adult"
        elif s.endswith("_Day"):
            key = "organoid_Day"
        else:
            key = "other"
            strata.setdefault("other", Counter())[c] += 1
            continue
        strata[key][c] += 1
        samp[key].add(s)
res138 = {"cells_final_total": total, "fetal_gw_range": "Hgw9-Hgw27 (任务书写 GW9-19, 实测含至 GW27)",
          "layers": {k: {"n_cells": int(sum(v.values())),
                         "celltype_pct": {c: round(100 * x / max(1, sum(v.values())), 2)
                                          for c, x in v.most_common()},
                      "samples": sorted(samp.get(k, []))}
                   for k, v in strata.items()}}
kb = json.dumps({"GSE268630_portal": res268, "GSE138002_final_author_labels": res138,
                 "GSE234963": {"cells": "176,849 (24 h5ad, obs 无标签列 — 实测 iloc 全空)",
                               "composition": None,
                               "registry": "OA-D009 Human fetal retinal progenitor, ~7.5-21 PCW, "
                                           "24 samples/13 time points (SRA PRJNA983820)",
                               "files": "/mnt/D/OcularKB/data/backlog_h5ad/GSE234963_*.h5ad + "
                                        "/mnt/D/OcularKB/data/GSE234963/GSE234963_RAW.tar"},
                 }, ensure_ascii=False, indent=1)
(OUT / "fetal_agg_20260924.json").write_text(kb, encoding="utf-8")
print(kb[:3000])
print("... saved", OUT / "fetal_agg_20260924.json")
