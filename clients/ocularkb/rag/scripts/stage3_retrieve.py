#!/usr/bin/env python3
"""OcularKB RAG Stage 3: 检索接口 retrieve_references()
用法:
  python stage3_retrieve.py --cell-type "Rod Bipolar Cell" --species human --top-k 5
  python stage3_retrieve.py --query "Muller glia marker genes" --species mouse
  # v2.0 全眼库 (推荐): 加 --db-dir 指向 v2.0 + --tissue 过滤
  python stage3_retrieve.py --cell-type "corneal endothelium" --tissue cornea --db-dir <...>/v2.0_2026-09
输出: 文献片段 + marker 共现 + PMID (可溯源)
v2.0 变更 (2026-09-23, OCB-RAG2):
  - 新增 --db-dir (默认仍为 v1.0_2026-08 → 旧调用行为不变) 与 --tissue 过滤
  - 三维过滤 species+tissue+cell_type (Claude5 审核要求落地); 各维过滤后不足 top_k*3 回退全量
  - tissue 过滤命中 tissue_labels 多标签列 (任一命中); v1.0 库无该列时忽略该参数并告警
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
DEFAULT_DB_DIR = f"{BASE}/literature_db/v1.0_2026-08"
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"

_model = None
_df = None
_db_dir = None

def load(db_dir=None):
    global _model, _df, _db_dir
    if _df is None or (db_dir and _db_dir != db_dir):
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_DIR, device="cpu")  # GPU 留科研 (与 stage2c 一致)
        _df = pd.read_parquet(f"{db_dir}/chunks.parquet")
        _db_dir = db_dir
        print(f"库: {db_dir} | {len(_df)} chunks, {_df['species'].nunique()} species", file=sys.stderr)
    return _model, _df

# 细胞类型 → cell_type_mentioned 词表映射 (chunking 时提取的元数据)
CT_MAP = {
    "rod": ["Rod"],
    "cone": ["Cone"],
    "retinal pigment epithelium": ["RPE"],
    "rpe": ["RPE"],
    "muller glia": ["MG"],
    "muller cell": ["MG"],
    "astrocyte": ["Astro"],
    "microglia": ["Micro"],
    "retinal ganglion cell": ["RGC"],
    "ganglion cell": ["RGC"],
    "bipolar cell": ["BC"],
    "rod bipolar cell": ["BC"],
    "horizontal cell": ["HC"],
    "amacrine cell": ["AC"],
    # --- v2.0 全眼组织细胞类型 ---
    "corneal epithelial": ["CornealEpithelial"],
    "corneal epithelium": ["CornealEpithelial"],
    "corneal endothelial": ["CornealEndothelial"],
    "corneal endothelium": ["CornealEndothelial"],
    "keratocyte": ["CornealEpithelial"],
    "limbal stem cell": ["CornealEpithelial"],
    "conjunctival epithelial": ["ConjunctivalEpithelial"],
    "goblet cell": ["Goblet"],
    "trabecular meshwork cell": ["TMcell"],
    "tm cell": ["TMcell"],
    "schlemm": ["SchlemmEndo"],
    "ciliary epithelial": ["CiliaryEpithelial"],
    "ciliary epithelium": ["CiliaryEpithelial"],
    "lens epithelial": ["LensEpithelial"],
    "lens fiber": ["LensEpithelial"],
    "iris smooth muscle": ["IrisSMC"],
    "iris sphincter": ["IrisSMC"],
    "oligodendrocyte": ["Oligodendrocyte"],
    "schwann cell": ["Schwann"],
    "choriocapillaris": ["Choriocapillaris"],
    "choroidal endothelial": ["Choriocapillaris", "Endo"],
    "endothelial cell": ["Endo"],
    "pericyte": ["Pericyte"],
    "fibroblast": ["Fibroblast"],
}

def _ct_filter_keys(cell_type: str):
    """把查询细胞类型名映射到 cell_type_mentioned 词表键 (大小写不敏感)"""
    k = cell_type.strip().lower()
    if k in CT_MAP:
        return CT_MAP[k]
    # 模糊匹配: 包含关系
    for key, vals in CT_MAP.items():
        if key in k or k in key:
            return vals
    return None

def retrieve(cell_type: str, species: str = None, top_k: int = 5, query: str = None,
             tissue: str = None, db_dir: str = None):
    model, df = load(db_dir or DEFAULT_DB_DIR)
    if query is None:
        query = f"{cell_type} marker genes {tissue or 'retina'} single cell RNA sequencing"
    emb = model.encode([query], normalize_embeddings=True)[0]
    emb_matrix = np.stack(df["embedding"].values)
    sims = emb_matrix @ emb
    df = df.assign(_sim=sims)
    if species:
        df = df[df["species"].isin([species, "both"])]
    # tissue 多标签过滤 (v2.0 列; 任一命中; 不足 top_k*3 回退)
    if tissue:
        if "tissue_labels" not in df.columns:
            print("WARN: 当前库无 tissue_labels 列, --tissue 忽略", file=sys.stderr)
        else:
            df_t = df[df["tissue_labels"].apply(
                lambda labs: labs is not None and tissue in labs)]
            if len(df_t) >= top_k * 3:
                df = df_t
    # cell_type_mentioned 元数据过滤 (Claude5 审核要求: 检索过滤 species+tissue/cell_type)
    ct_keys = _ct_filter_keys(cell_type)
    if ct_keys is not None:
        df_ct = df[df["cell_type_mentioned"].apply(
            lambda ctm: ctm is not None and any(k in ctm for k in ct_keys))]
        # 过滤后不足 top_k*3 时回退到全量 (避免漏检)
        if len(df_ct) >= top_k * 3:
            df = df_ct
    df = df.sort_values("_sim", ascending=False).head(top_k * 3)
    # 按 paper 去重, 每篇最多 2 条
    out, seen_papers = [], set()
    for _, r in df.iterrows():
        if r["paper_id"] in seen_papers:
            continue
        seen_papers.add(r["paper_id"])
        ctm = r.get("cell_type_mentioned")
        mg = r.get("marker_genes")
        out.append({
            "pmid": r["paper_id"],
            "title": r["title"],
            "journal": r["journal"],
            "year": r["year"],
            "species": r["species"],
            "tissue_labels": list(r["tissue_labels"]) if r.get("tissue_labels") is not None else [r.get("tissue", "unknown")],
            "section": r["section"],
            "snippet": r["text"][:500],
            "_full_text": r["text"],  # 完整 chunk 文本 (质检 marker 匹配用)
            "cell_type_mentioned": list(ctm) if ctm is not None and len(ctm) else [],
            "marker_genes": list(mg) if mg is not None and len(mg) else [],
            "relevance_score": round(float(r["_sim"]), 4),
        })
        if len(out) >= top_k:
            break
    return {"query": query, "species": species, "tissue": tissue, "results": out}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell-type", default="Rod Bipolar Cell")
    ap.add_argument("--species", default=None)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--query", default=None)
    ap.add_argument("--tissue", default=None)
    ap.add_argument("--db-dir", default=None, help=f"chunks.parquet 所在目录 (默认 {DEFAULT_DB_DIR})")
    args = ap.parse_args()
    res = retrieve(args.cell_type, args.species, args.top_k, args.query,
                   tissue=args.tissue, db_dir=args.db_dir)
    print(json.dumps(res, ensure_ascii=False, indent=1))
