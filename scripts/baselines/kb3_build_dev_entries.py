#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W1: 发育期独立条目 retina__fetal_developing 渲染 (JSON+MD)。

铁律实现 (PI: 胎儿≠成人即使同组织):
  - schema=eyekb-baseline-development/1.0 → MCP _load_priors 只收 startswith
    "eyekb-baseline/" 的成人条, 本条对成人查询不可见, 禁成人桶代答路径不变 (_fetal_concept_response)。
  - 数据源=作者/portal **已发布标签**直方图 (聚合脚本 kb3_fetal_agg.py), 现役成人引擎零参与。
  - development_stage=fetal_developing; GSE138002 内 4 个样本面按 sample 前缀硬拆,
    adult_Adult / organoid_Day 段**不进条目主体**, 只存隔离记录 (organoid 按裁定 Q1 unknown+旗标)。
素材: plans/kb3_evidence/fetal_agg_20260924.json (本脚本断言校验, 数字不手抄)。
"""
import json
from pathlib import Path

AGG = Path("/mnt/D/EyeKB/plans/kb3_evidence/fetal_agg_20260924.json")
KB = Path("/mnt/D/EyeKB/kb/baselines")
OUT_DIR = KB
PROH = ("KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 "
        "—— 同一组织胎儿≠成人, adult/fetal 不互为参照。")

agg = json.loads(AGG.read_text(encoding="utf-8"))
A = agg["GSE268630_portal"]
B = agg["GSE138002_final_author_labels"]
C = agg["GSE234963"]

# ---- 断言 (素材完整性; 失败即停禁产出半成品条) ----
assert A["cells_total"] == sum(A["majorclass_hist"].values()) == 226506, "268630 直方图失配"
assert B["cells_final_total"] == 118555
lay = B["layers"]
lay.setdefault("other", {"n_cells": 0, "celltype_pct": {}, "samples": []})
assert sum(v["n_cells"] for v in lay.values()) == B["cells_final_total"], "138002 分层漏细胞"
assert "Hgw9" in lay["fetal_Hgw"]["samples"] and "Hgw27" in lay["fetal_Hgw"]["samples"]
assert set(lay["adult_Adult"]["samples"]) == {"Adult"}
assert all(s.endswith("_Day") for s in lay["organoid_Day"]["samples"])

FETAL = lay["fetal_Hgw"]
POST = lay["postnatal_Hpnd"]
# fetal 词表 → 成人 10 类词表零映射: 保留原词 (发育词表是独立本体, 翻译=混池前兆)
entry = {
    "schema": "eyekb-baseline-development/1.0",
    "entry_id": "baseline_human_retina__fetal_developing__kb3",
    "tissue": "retina",
    "species": "human",
    "title": "组成参考 (发育期): 人胎视网膜 fetal_developing (作者/portal 标签聚合, KB3 独立条)",
    "status": "development_annotated_aggregate",
    "generated": "2026-09-24",
    "generator": "kb3_build_dev_entries.py (KB3 t_5425a7ca) ← kb3_fetal_agg.py 实测素材",
    "card": "t_5425a7ca",
    "development_stage": "fetal_developing",
    "development_stage_prohibition": PROH,
    "stage_axis": {
        "field": "development_stage",
        "levels": ["adult", "fetal_developing", "postnatal_neonatal",
                   "mixed_not_separable", "unknown"],
        "note": ("KB3 枚举 (任务书 W1)。本条=发育期条, 与 adult 主档 (retina.json, "
                 "organism_stage=adult) 身份永久分离; 引用本条数字禁止回填任何 adult 条, 反之亦然。"),
    },
    "nature": ("发育期**组成参考**条目: 数字=数据集作者/CELLxGENE portal 已发布细胞标签的**直接计数聚合**, "
               "非现役成人引擎推断 (引擎对 fetal 必须弃权, E4/E5 OOD_严格 冻结件); 供者级 median/IQR 口径未建 "
               "(fetal 参考管线任务未启动, KB2c 裁定 Q5), 本条为标签分布级参考。"),
    "usage_scope": ("胎/发育期视网膜材料的身份参考 + OOD 行为对照锚 (E5 同源数据); "
                    "不得当组成达标线; 不得与 adult 主档互为参照 (PI 红线); 禁入一切打分 (Astra T2 全域继承)。"),
    "evidence_grades": {"A": "portal/作者发布标签的直接计数 (文件路径+聚合脚本可溯源)"},
    "anchors": [
        {"acc": "GSE268630", "role": "primary_portal", "tier": "fetal",
         "file": "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad",
         "cells": 226506, "donors": 14,
         "stage_range": "11w2d–23w4d post-fertilization (portal development_stage 14 档, 全档列表见 "
                        "plans/kb3_evidence/fetal_agg_20260924.json)",
         "tissue_note": "macula lutea 119,111 + peripheral 100,532 + retina(未标部位) 6,863",
         "provenance": "CELLxGENE portal 注释 (author_cell_type/majorclass 列)"},
        {"acc": "GSE138002", "role": "secondary_author_labels", "tier": "fetal+postnatal 混面已拆",
         "file": "/mnt/D/OcularKB/data/GSE138002/GSE138002_Final_barcodes.csv.gz",
         "cells_final_total": 118555,
         "layer_split": {k: v["n_cells"] for k, v in lay.items()},
         "fetal_layer_cells": FETAL["n_cells"],
         "fetal_layer_samples": FETAL["samples"],
         "stage_range_note": "任务书写 GW9-19; 实测 portal 终版含 Hgw9–Hgw27 + Hpnd8 + Adult + 类器官 Days"
                             " —— 混内容按样本面前缀硬拆, 非 fetal 面不入本条主体",
         "provenance": "作者发布标签列 umap2_CellType (GEO suppl Final_barcodes)"},
        {"acc": "GSE234963", "role": "data_card_only", "tier": "fetal_RPC",
         "cells": C["cells"], "registry": C["registry"], "files": C["files"],
         "composition": None,
         "note": "obs 无标签列 (实测 24×h5ad obs 全空) + GEO 无独立标签文件 (registry 复核一致) "
                 "→ 只立数据卡, 组成待 fetal 参考管线/作者标签获取后回填; 无据不建 (KB3 纪律3)。"}],
    "portal_majorclass_reference": {
        "cells": A["cells_total"], "donors": A["n_donors"],
        "pct": A["majorclass_pct"], "hist": A["majorclass_hist"],
        "vocabulary_note": "PRPC=photoreceptor progenitor, NRPC=neural retina progenitor —— "
                           "发育专用类, **无成人 10 类对应物**, 禁映射进 adult 词表 (本体隔离)。"},
    "author_labels_fetal_layer(GSE138002)": {
        "cells": FETAL["n_cells"], "samples": FETAL["samples"],
        "pct_by_celltype": FETAL["celltype_pct"],
        "vocabulary_note": "RPCs/Neurogenic Cells/BC.Photo_Precurs/AC.HC_Precurs 等前体词表同上 —— 禁成人化翻译。"},
    "postnatal_neonatal_layer(GSE138002)": {
        "cells": POST["n_cells"], "samples": POST["samples"],
        "pct_by_celltype": POST["celltype_pct"],
        "development_stage": "postnatal_neonatal",
        "note": "单列分层: 新生≠胎≠成人 (KB3 枚举第三值在此有据); 与胎层不互并。"},
    "excluded_layers": {
        "adult_Adult": {"cells": lay["adult_Adult"]["n_cells"],
                        "disposition": "禁并入本发育条 (adult 对照材料归 adult 侧口径, 但 11.6K 细胞 "
                                       "非 D001 体系 — 不单建条目, 登记隔离)"},
        "organoid_Day": {"cells": lay["organoid_Day"]["n_cells"], "samples": lay["organoid_Day"]["samples"],
                         "disposition": "organoid → unknown+旗标 (KB2c 裁定 Q1: 类器官≠胎儿组织≠成人); "
                                        "只列不并入任何发育/成人条"},
        "other": {"cells": lay["other"]["n_cells"], "disposition": "非发育命名样本面 → 隔离"}},
    "cross_source_note": ("两锚点词表不同 (portal majorclass 9 类 vs 作者 12+ 类) —— 本条并列展示, "
                          "不合成单一分布 (Astra T6 不合成口径的发育轴继承)。"),
    "flags": {"engine_applicability": "现役判读引擎=成人域, 对本条材料必须弃权; 本条数字不得被用作"
                                        "引擎对 fetal 输出'对错'的评分基准 (E5 仅行为描述)。",
              "not_donor_level": "供者级区间口径未建 (fetal 管线另批), 引用时须带本旗。"},
    "caveats": [
        "标签分布=发表注释的转录组面; GSE268630 同时含 multiome ATAC 面 GSM 矩阵 (未并入本条)。",
        "GSE138002 'Final' 为作者清洗后集合 (118,555/全 138,672), All_barcodes 面无标签列, 聚合以 Final 为准。",
        "本条=发育期**独立文件**; KB2c 概念条 fetal_development_transitions 仍是入口占位, 二者并存: "
        "概念条答'有哪些候选', 本条答'胎视网膜标签分布实测是什么'。"],
    "sources": [
        {"sid": "S1", "kind": "portal_dataset", "acc": "GSE268630",
         "path": A and "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad"},
        {"sid": "S2", "kind": "geo_supplementary", "acc": "GSE138002",
         "path": "/mnt/D/OcularKB/data/GSE138002/GSE138002_Final_barcodes.csv.gz"},
        {"sid": "S3", "kind": "registry", "row": "OA-D009/OA-D010",
         "path": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv"},
        {"sid": "S4", "kind": "eval_anchor", "note": "E5=Q8_GSE268630 (评估侧同数据, 行为隔离在先, "
                                                     "本条为其 KB 侧配套)"},
    ],
    "identity_signature": None,  # 填充后于下方计算 (只覆盖本条主体, 与成人条签名体系互不相干)
}


def sha256_obj(obj):
    import hashlib
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


entry["identity_signature"] = {
    entry["entry_id"]: sha256_obj({k: entry[k] for k in
                                   ("portal_majorclass_reference",
                                    "author_labels_fetal_layer(GSE138002)",
                                    "postnatal_neonatal_layer(GSE138002)", "excluded_layers")})}

(OUT_DIR / "retina__fetal_developing.json").write_text(
    json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- MD 渲染 ----------------
L = [f"# {entry['title']}", ""]
L.append(f"> schema: `{entry['schema']}` | entry_id: `{entry['entry_id']}` | 状态: {entry['status']} "
         f"| **development_stage={entry['development_stage']}** | 生成: {entry['generated']} | 卡片: {entry['card']}")
L.append(f"> ⚠ {PROH}")
L.append(f"> 本文件由 `/mnt/D/EyeKB/scripts/baselines/kb3_build_dev_entries.py` 从素材 "
         f"`plans/kb3_evidence/fetal_agg_20260924.json` 渲染 —— 改内容改聚合脚本+素材, 手改 MD 会被覆盖。")
L.append("")
L.append(f"**性质**: {entry['nature']}")
L.append("")
L.append(f"**用途口径**: {entry['usage_scope']}")
L.append("")
L.append("## 锚点与可得性核实 (KB3 纪律3: 无据不建)")
L.append("")
L.append("| 锚点 | 角色 | 细胞 | 层级 | 盘上证据 |")
L.append("|---|---|---|---|---|")
L.append(f"| GSE268630 | portal 主锚 | {A['cells_total']:,} (14 donor) | 11w2d–23w4d 全胎期 | "
         f"gse268630_cellxgene.h5ad 实测 (本仓 E5 冻结件同文件) |")
L.append(f"| GSE138002 | 作者标签副锚 | Final {B['cells_final_total']:,} (胎层 {FETAL['n_cells']:,}) | "
         f"Hgw9–Hgw27 实测 (任务书 GW9-19 偏窄) | Final_barcodes.csv.gz umap2_CellType |")
L.append(f"| GSE234963 | **只立数据卡** | 176,849 (24 样本) | ~7.5–21 PCW | obs 无标签列 实测 → 组成待回填 |")
L.append("")
L.append("## 发育期标签分布 — GSE268630 (portal majorclass, 全池直计)")
L.append("")
L.append("| majorclass | % | n_cells |")
L.append("|---|---|---|")
for k, v in A["majorclass_hist"].items():
    L.append(f"| {k} | {A['majorclass_pct'][k]} | {v:,} |")
L.append("")
L.append(f"> 部位面: macula lutea 119,111 / peripheral 100,532 / 未标 6,863; "
         f"PRPC/NRPC 为发育专有无成人对应 —— **禁映射进成人 10 类词表**。")
L.append("")
L.append("## 发育期标签分布 — GSE138002 胎网层 (作者 umap2_CellType)")
L.append("")
L.append("| celltype | % |  | 样本面 | Hgw9–Hgw27 (17 unit) |")
L.append("|---|---|---|---|---|")
for k, v in FETAL["celltype_pct"].items():
    L.append(f"| {k} | {v} | | | |")
L.append("")
L.append("## 新生层 (GSE138002 Hpnd8) — development_stage=postnatal_neonatal (第三值在此有据)")
L.append("")
for k, v in POST["celltype_pct"].items():
    L.append(f"- {k}: {v}%")
L.append("")
L.append("## 排除层 (禁并入, 只登记)")
L.append("")
L.append(f"- **Adult 面** ({lay['adult_Adult']['n_cells']:,} 细胞): 成人对照材料 → 发育条不纳; "
         f"亦非 D001 体系, 不单建 adult 条 (隔离记录)。")
L.append(f"- **类器官 Days 面** ({lay['organoid_Day']['n_cells']:,} 细胞, "
         f"{sorted(lay['organoid_Day']['samples'])}): organoid→unknown+旗标 (裁定 Q1)。")
if lay["other"]["n_cells"]:
    L.append(f"- **other 面** ({lay['other']['n_cells']} 细胞): 隔离。")
L.append("")
L.append("## 跨源口径声明")
L.append("")
L.append(entry["cross_source_note"])
L.append("")
L.append(f"⚑ **{entry['flags']['engine_applicability']}**")
L.append(f"⚑ {entry['flags']['not_donor_level']}")
L.append("")
L.append("## caveats")
for c in entry["caveats"]:
    L.append(f"- {c}")
L.append("")
L.append(f"身份签名: `{json.dumps(entry['identity_signature'], ensure_ascii=False)}`")
(OUT_DIR / "retina__fetal_developing.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------- 索引登记 (baselines.json development_entries 键, additive) ----------------
IDX = KB / "baselines.json"
idx = json.loads(IDX.read_text(encoding="utf-8"))
rec = {"entry_id": entry["entry_id"], "file": "retina__fetal_developing.md",
       "tissue": "retina", "development_stage": "fetal_developing",
       "anchors": [c["acc"] for c in entry["anchors"]], "status": entry["status"],
       "schema": entry["schema"], "note": "发育期独立条 (MCP 成人查询不可见; 概念条并存)"}
ex = [x for x in idx.get("development_entries", []) if x.get("entry_id") != rec["entry_id"]]
idx["development_entries"] = ex + [rec]
IDX.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- 概念条指针 (additive 尾注, 候选数组不动) ----------------
pm = KB / "fetal_development_transitions.md"
t = pm.read_text(encoding="utf-8")
mark = "KB3 已建首个发育期实数据参考条"
if mark not in t:
    t += ("\n> **KB3 进展 (2026-09-24)**: 首个发育期实数据参考条已独立立档 = `retina__fetal_developing.md` "
          "(GSE268630 portal + GSE138002 作者标签聚合; GSE234963 数据卡)。本概念条继续作为候选总表与 "
          "MCP fetal 查询入口 —— 两者并存互不覆盖; \"需 fetal 参考管线\"声明对**引擎判读**仍有效, "
          "本条数字仅为已发布标签分布参考, 非引擎管线产物。\n")
    pm.write_text(t, encoding="utf-8")
pj = KB / "fetal_development_transitions.json"
d = json.loads(pj.read_text(encoding="utf-8"))
if "kb3_first_entry_pointer" not in d:
    d["kb3_first_entry_pointer"] = {
        "file": "retina__fetal_developing.json", "entry_id": entry["entry_id"],
        "card": "t_5425a7ca", "date": "2026-09-24",
        "note": "概念条=候选总表/查询入口; 该文件=已发布标签分布参考条 (首个发育期实数据条目)。并存。"}
    pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

print("WROTE retina__fetal_developing.json/md + index + concept pointer")
print(json.dumps({"fetal_268630": A["majorclass_pct"],
                  "fetal_138002_cells": FETAL["n_cells"]}, ensure_ascii=False))
