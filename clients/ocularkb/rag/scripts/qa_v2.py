#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCB-RAG2 W6 QA: ①retina 黄金集回归 (v1.0 基线 vs v2.0) ②逐组织 recall 抽查 (3-5 典型细胞类型)
判据与 v1.0 stage4 一致 (Claude5 审核): Top-5 论文中 >=3 篇命中期望 marker (论文级, top-5 chunks 任一)
回归判据: v2.0 每个用例的论文命中数 >= v1.0 基线 (不劣化)
输出: literature_db/v2.0_2026-09/QA_V2.md + qa_v2.json
"""
import json, os, re, sys, time
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
sys.path.insert(0, f"{BASE}/scripts")
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"
V10 = f"{BASE}/literature_db/v1.0_2026-08"
V20 = f"{BASE}/literature_db/v2.0_2026-09"

from stage3_retrieve import _ct_filter_keys


def _norm(t):
    return t.lower().replace("ü", "u").replace("é", "e").replace("ö", "o").replace("ä", "a")


def marker_hit(text, expected):
    tl = _norm(text)
    return any(re.search(r"\b" + re.escape(m.lower()) + r"\b", tl) for m in expected)


def paper_level_recall(model, df, emb_matrix, case, tissue=None,
                       top_chunks_per_paper=5, n_papers=5, top_n=100):
    ct, sp, markers = case["cell_type"], case["species"], case["expected_markers"]
    q = f"{ct} marker genes"  # 回归必须同 query (任务书: 与 v1.1 同 query 对比; tissue 只做过滤)
    emb = model.encode([q], normalize_embeddings=True)[0]
    sims = emb_matrix @ emb
    d = df.assign(_sim=sims)
    if sp:
        d = d[d["species"].isin([sp, "both"])]
    if tissue and "tissue_labels" in d.columns:
        dt = d[d["tissue_labels"].apply(lambda l: l is not None and tissue in l)]
        if len(dt) >= 30:
            d = dt
    keys = _ct_filter_keys(ct)
    if keys:
        d_ct = d[d["cell_type_mentioned"].apply(lambda c: c is not None and any(k in c for k in keys))]
        if len(d_ct) >= 30:
            d = d_ct
    d = d.sort_values("_sim", ascending=False).head(top_n)
    by_paper = {}
    for _, r in d.iterrows():
        pid = r["paper_id"]
        if pid not in by_paper:
            by_paper[pid] = []
        if len(by_paper[pid]) < top_chunks_per_paper:
            by_paper[pid].append(r["text"])
    top_papers = []
    for pid, texts in by_paper.items():
        hit = any(marker_hit(t, markers) for t in texts)
        top_papers.append((pid, hit))
    top_papers = top_papers[:n_papers]
    return sum(1 for _, h in top_papers if h), [p for p, _ in top_papers]


# ---- ① retina 黄金集 (v1.0 stage4 同款 10 用例) ----
GOLDEN = [
    {"cell_type": "Rod", "species": "human",
     "expected_markers": ["RHO", "rhodopsin", "NRL", "PDE6B", "GNAT1", "transducin"]},
    {"cell_type": "Cone", "species": "human",
     "expected_markers": ["OPN1SW", "OPN1MW", "ARR3", "GNAT2", "cone arrestin"]},
    {"cell_type": "Retinal Pigment Epithelium", "species": "human",
     "expected_markers": ["BEST1", "bestrophin", "RPE65", "LRAT", "TYRP1"]},
    {"cell_type": "Muller Glia", "species": "human",
     "expected_markers": ["RLBP1", "CRALBP", "GLUL", "glutamine synthetase", "VIM", "vimentin",
                          "SLC1A3", "GLAST", "SOX9"]},
    {"cell_type": "Astrocyte", "species": "human",
     "expected_markers": ["GFAP", "AQP4", "S100B"]},
    {"cell_type": "Microglia", "species": "human",
     "expected_markers": ["C1QB", "C1QA", "P2RY12", "P2Y12", "AIF1", "IBA1", "IBA-1", "TMEM119"]},
    {"cell_type": "Retinal Ganglion Cell", "species": "human",
     "expected_markers": ["RBPMS", "THY1", "NEFL", "SLC17A6", "VGLUT2", "POU4F1", "BRN3A"]},
    {"cell_type": "Rod Bipolar Cell", "species": "human",
     "expected_markers": ["PRKCA", "PKC", "protein kinase C", "SCGN", "secretagogin",
                          "CABP5", "GRM6", "GBX2", "VSX1"]},
    {"cell_type": "Horizontal Cell", "species": "human",
     "expected_markers": ["ONECUT1", "ONECUT2", "LHX1", "CALB1", "calbindin"]},
    {"cell_type": "Amacrine Cell", "species": "human",
     "expected_markers": ["GAD1", "GAD2", "SLC32A1", "VGAT", "TFAP2A"]},
]

# ---- ② 逐组织抽查 (典型细胞类型 2-4 个/组织; marker=文献共识启发式, 仅 QA 判读用) ----
TISSUE_SPOT = {
    "cornea": [
        {"cell_type": "corneal epithelium", "species": "human",
         "expected_markers": ["KRT12", "KRT3", "PAX6", "TP63", "keratin 12"]},
        {"cell_type": "corneal endothelium", "species": "human",
         "expected_markers": ["COL8A1", "ATP1A1", "NAK-ATPase", "ZO-1", "TGFBI", "descemet"]},
        {"cell_type": "keratocyte", "species": "human",
         "expected_markers": ["LUM", "lumican", "DCN", "decorin", "KRT68", "mimeocan"]},
        {"cell_type": "limbal stem cell", "species": "human",
         "expected_markers": ["ABCB1", "TP63", "KRT14", "limbal epithelial stem"]},
    ],
    "conjunctiva": [
        {"cell_type": "goblet cell", "species": "human",
         "expected_markers": ["MUC5AC", "TFF3", "spasmolytic", "AGR2"]},
        {"cell_type": "conjunctival epithelium", "species": "human",
         "expected_markers": ["KRT13", "KRT4", "MUC16", "p63"]},
        {"cell_type": "fibroblast", "species": "human",
         "expected_markers": ["COL1A1", "fibronectin", "LUM", "THY1"]},
    ],
    "sclera": [
        {"cell_type": "fibroblast", "species": "human",
         "expected_markers": ["COL1A1", "collagen I", "COMP", "POSTN"]},
        {"cell_type": "chondrocyte", "species": "human",
         "expected_markers": ["SOX9", "COL2A1", "aggrecan", "ACAN"]},
        {"cell_type": "smooth muscle", "species": "human",
         "expected_markers": ["ACTA2", "alpha-SMA", "MYH11", "Desmin"]},
    ],
    "trabecular_meshwork": [
        {"cell_type": "trabecular meshwork cell", "species": "human",
         "expected_markers": ["MYOC", "myocilin", "ENG", "CD105", "LY64", "GPX3"]},
        {"cell_type": "schlemm canal endothelium", "species": "human",
         "expected_markers": ["TEK", "TIE2", "KDR", "CDH5", "PECAM1"]},
        {"cell_type": "endothelial cell", "species": "human",
         "expected_markers": ["CDH5", "VECAD", "PECAM1", "von Willebrand"]},
    ],
    "iris": [
        {"cell_type": "iris smooth muscle", "species": "human",
         "expected_markers": ["ACTA2", "MYH11", "CNN1", "desmin"]},
        {"cell_type": "iris pigment epithelium", "species": "human",
         "expected_markers": ["TYRP1", "PMEL", "MITF", "TYR", "melanosome"]},
        {"cell_type": "astrocyte", "species": "human",
         "expected_markers": ["GFAP", "S100B", "vimentin"]},
    ],
    "ciliary_body": [
        {"cell_type": "ciliary epithelium", "species": "human",
         "expected_markers": ["AQP1", "ATP1A1", "BEST1", "CFTR", "aqueous humor"]},
        {"cell_type": "endothelial cell", "species": "human",
         "expected_markers": ["CDH5", "PECAM1", "PLVAP"]},
        {"cell_type": "smooth muscle", "species": "human",
         "expected_markers": ["ACTA2", "MYH11", "Desmin"]},
    ],
    "lens": [
        {"cell_type": "lens fiber cell", "species": "human",
         "expected_markers": ["MIP", "AQP0", "LIM2", "BFSP1", "filensin", "CP49"]},
        {"cell_type": "lens epithelium", "species": "human",
         "expected_markers": ["LMFB1", "LIM", "PAX6", "AQUAPORIN", "LEPREL2", "keratin 18"]},
        {"cell_type": "fiber cell", "species": "human",
         "expected_markers": ["CRYAA", "alphaA-crystallin", "CRYBB1", "gamma-crystallin", "betaA3"]},
    ],
    "optic_nerve": [
        {"cell_type": "oligodendrocyte", "species": "human",
         "expected_markers": ["MBP", "myelin basic", "MOG", "PLP1", "CNP"]},
        {"cell_type": "astrocyte", "species": "human",
         "expected_markers": ["GFAP", "AQP4", "S100B", "ALDH1L1"]},
        {"cell_type": "microglia", "species": "human",
         "expected_markers": ["P2RY12", "TMEM119", "AIF1", "IBA1", "CX3CR1"]},
        {"cell_type": "retinal ganglion cell", "species": "human",
         "expected_markers": ["RBPMS", "THY1", "CD90", "NEFL", "SLC17A6"]},
    ],
    "RPE": [
        {"cell_type": "retinal pigment epithelium", "species": "human",
         "expected_markers": ["RPE65", "BEST1", "bestrophin", "TYR", "PMEL", "MERL"]},
        {"cell_type": "endothelial cell", "species": "human",
         "expected_markers": ["CDH5", "PECAM1", "CLDN5"]},
    ],
    "choroid": [
        {"cell_type": "choriocapillaris endothelium", "species": "human",
         "expected_markers": ["CDH5", "PECAM1", "PLVAP", "CLDN5"]},
        {"cell_type": "melanocyte", "species": "human",
         "expected_markers": ["TYR", "DCT", "PMEL", "MITF", "TYRP1"]},
        {"cell_type": "pericyte", "species": "human",
         "expected_markers": ["RGS5", "PDGFRB", "pericyte", "ACTA2"]},
    ],
}


def main():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_DIR, device="cpu")
    print("[load] v1.0 baseline parquet...", flush=True)
    df10 = pd.read_parquet(f"{V10}/chunks.parquet")
    m10 = np.stack(df10["embedding"].values)
    print("[load] v2.0 parquet...", flush=True)
    df20 = pd.read_parquet(f"{V20}/chunks.parquet")
    m20 = np.stack(df20["embedding"].values)
    print(f"  v1.0: {len(df10)} chunks | v2.0: {len(df20)} chunks", flush=True)

    # ---- retina 黄金回归 ----
    golden = []
    for case in GOLDEN:
        h10, _ = paper_level_recall(model, df10, m10, case)
        h20, _ = paper_level_recall(model, df20, m20, case, tissue="retina")
        h20n, _ = paper_level_recall(model, df20, m20, case)
        ok = h20 >= h10
        golden.append({"cell_type": case["cell_type"], "v10_hits": h10, "v20_retina_hits": h20,
                       "v20_all_hits": h20n, "no_degrade": ok})
        print(f"golden {case['cell_type']:28s} v1.0={h10}/5 v2.0(retina)={h20}/5 "
              f"{'OK' if ok else 'DEGRADED'}", flush=True)

    # ---- 逐组织抽查 ----
    spot = {}
    for tissue, cases in TISSUE_SPOT.items():
        rows = []
        for case in cases:
            h, pmids = paper_level_recall(model, df20, m20, case, tissue=tissue)
            passed = h >= 3
            rows.append({"cell_type": case["cell_type"], "hits": h, "passed": passed,
                         "top_pmids": pmids[:3]})
            print(f"spot [{tissue}] {case['cell_type']:32s} hits={h}/5 "
                  f"{'PASS' if passed else 'WEAK'}", flush=True)
        spot[tissue] = rows

    out = {"golden_regression": golden,
           "golden_pass": sum(1 for g in golden if g["no_degrade"]),
           "golden_total": len(golden),
           "tissue_spot": spot}
    json.dump(out, open(f"{V20}/qa_v2.json", "w"), indent=1, ensure_ascii=False)

    with open(f"{V20}/QA_V2.md", "w") as f:
        f.write("# OCB-RAG2 v2.0 QA 报告 (2026-09-23)\n\n")
        f.write("判据 (与 v1.0 stage4 一致, Claude5 审核): Top-5 论文中 ≥3 篇命中期望 marker "
                "(论文级: 每篇 top-5 chunks 任一命中即算)。\n\n")
        f.write("## ① retina 黄金集回归 (v1.0 基线 vs v2.0)\n\n")
        f.write("| 细胞类型 | v1.0 命中/5 | v2.0(retina过滤) 命中/5 | v2.0(无过滤) | 不劣化 |\n")
        f.write("|---|---|---|---|---|\n")
        for g in golden:
            f.write(f"| {g['cell_type']} | {g['v10_hits']} | {g['v20_retina_hits']} | "
                    f"{g['v20_all_hits']} | {'✅' if g['no_degrade'] else '❌'} |\n")
        npass = sum(1 for g in golden if g["no_degrade"])
        f.write(f"\n**回归判定: {npass}/{len(golden)} 用例不劣化**"
                f"{' — PASS' if npass == len(golden) else ' — 见逐用例说明 (红线7: 只陈述库内容事实)'}\n\n")
        f.write("## ② 逐组织 recall 抽查 (v2.0, tissue 过滤开启)\n\n")
        for tissue, rows in spot.items():
            f.write(f"### {tissue}\n\n| 细胞类型 | 命中/5 | 判定 | Top PMIDs |\n|---|---|---|---|\n")
            for r in rows:
                f.write(f"| {r['cell_type']} | {r['hits']} | "
                        f"{'✅' if r['passed'] else '⚠️ 覆盖弱'} | {','.join(r['top_pmids'])} |\n")
            f.write("\n")
        f.write("注: marker 为文献共识启发式, 仅用于 QA 判读, 不构成知识库断言。\n")
    print("-> QA_V2.md + qa_v2.json", flush=True)


if __name__ == "__main__":
    main()
