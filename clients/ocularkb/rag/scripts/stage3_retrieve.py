#!/usr/bin/env python3
"""OcularKB RAG Stage 3: retrieval interface retrieve_references()
Usage:
  python stage3_retrieve.py --cell-type "Rod Bipolar Cell" --species human --top-k 5
  python stage3_retrieve.py --query "Muller glia marker genes" --species mouse
  # v2.0 whole-eye library (recommended): add --db-dir pointing to v2.0 + --tissue filtering
  python stage3_retrieve.py --cell-type "corneal endothelium" --tissue cornea --db-dir <...>/v2.0_2026-09
Output: literature snippets + marker co-occurrence + PMID (traceable)
v2.0 changes (2026-09-23, OCB-RAG2):
  - new --db-dir (default stays v1.0_2026-08 → old call behavior unchanged) and --tissue filtering
  - three-dimensional filtering species+tissue+cell_type (landed per Claude5 review requirements); when a
    dimension leaves fewer than top_k*3 hits, fall back to the full set
  - the tissue filter hits the tissue_labels multi-label column (any-label match); on a v1.0 library without
    that column the parameter is ignored with a warning
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
DEFAULT_DB_DIR = f"{BASE}/literature_db/v1.0_2026-08"
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"

# 2026-09-29 model made optional (PI: "can we do without that model?"):
#   three-level model-directory lookup EYEKB_MODEL_DIR(env) > in-repo models/bge-large-en-v1.5 > old absolute path;
#   when none is available, retrieval falls back to pure lexical matching (lexical_fallback, the response body
#   explicitly marks the degradation); the dense main path and the golden-41 criteria are bit-for-bit unchanged
#   whenever the model is available.
def _resolve_model_dir():
    env = os.environ.get("EYEKB_MODEL_DIR")
    if env:
        return env if os.path.isdir(env) else None
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, os.pardir, os.pardir, os.pardir, os.pardir))
    for cand in (os.path.join(repo_root, "models", "bge-large-en-v1.5"), MODEL_DIR):
        if os.path.isdir(cand):
            return cand
    return None

_model = None
_df = None
_db_dir = None

def load(db_dir=None):
    global _model, _df, _db_dir
    if _df is None or (db_dir and _db_dir != db_dir):
        import os.path as _p
        if not _p.isfile(_p.join(db_dir or DEFAULT_DB_DIR, "chunks.parquet")):
            raise SystemExit(
                "ERROR: literature database not found. Download the corpus from Releases, unpack it, "
                "and point --db-dir at the unpacked directory (see README '5-minute quickstart' steps 2-3).")
        md = _resolve_model_dir()
        if md:
            try:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(md, device="cpu")  # GPU reserved for research (consistent with stage2c)
            except Exception as e:
                print(f"WARN: embedding model unavailable ({type(e).__name__}), "
                      "literature retrieval degraded to pure lexical_fallback (ranking differs from the official dense version)",
                      file=sys.stderr)
                _model = None
        else:
            print("INFO: bge-large-en-v1.5 model directory not found (set it via EYEKB_MODEL_DIR or the "
                  "in-repo models/ path); literature retrieval uses pure lexical_fallback — works with zero models.",
                  file=sys.stderr)
            _model = None
        _df = pd.read_parquet(f"{db_dir}/chunks.parquet")
        _db_dir = db_dir
        print(f"DB: {db_dir} | {len(_df)} chunks, {_df['species'].nunique()} species", file=sys.stderr)
    return _model, _df

# cell type -> cell_type_mentioned vocabulary mapping (metadata extracted at chunking time)
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
    # --- v2.0 whole-eye-tissue cell types ---
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
    """Map a query cell-type name to cell_type_mentioned vocabulary keys (case-insensitive)"""
    k = cell_type.strip().lower()
    if k in CT_MAP:
        return CT_MAP[k]
    # fuzzy match: containment
    for key, vals in CT_MAP.items():
        if key in k or k in key:
            return vals
    return None

_EMB_CACHE = {}
_LEX_HAY = {}

def _lexical_scores(df, query, db_dir):
    """Zero-model pure-lexical relevance: token coverage (full text + title) + weighted hits on structured metadata.
    Deterministic, no randomness: on tied scores, rows keep the stable parquet original order; recomputable."""
    import re
    toks = sorted({t for t in re.findall(r"[a-z0-9][a-z0-9\-]{1,}", query.lower())})
    if not toks:
        return np.zeros(len(df), dtype=np.float32)
    key = (db_dir, len(df))
    if key not in _LEX_HAY:
        title = df["title"].fillna("").str.lower()
        text = df["text"].fillna("").str.lower()
        genes = df["marker_genes"].fillna("").astype(str).str.lower() if df["marker_genes"].dtype == object else pd.Series([""] * len(df))
        _LEX_HAY[key] = (text, title, genes)
    text, title, genes = _LEX_HAY[key]
    ctm = df["cell_type_mentioned"].fillna("").astype(str).str.lower()
    scores = np.zeros(len(df), dtype=np.float32)
    for t in toks:
        scores += text.str.contains(t, regex=False).to_numpy(dtype=np.float32) * 1.0
        scores += title.str.contains(t, regex=False).to_numpy(dtype=np.float32) * 3.0
        scores += genes.str.contains(t, regex=False).to_numpy(dtype=np.float32) * 2.0
        scores += ctm.str.contains(t, regex=False).to_numpy(dtype=np.float32) * 2.0
    return scores / len(toks)

def retrieve(cell_type: str, species: str = None, top_k: int = 5, query: str = None,
             tissue: str = None, db_dir: str = None):
    model, df = load(db_dir or DEFAULT_DB_DIR)
    if query is None:
        query = f"{cell_type} marker genes {tissue or 'retina'} single cell RNA sequencing"
    db_key = db_dir or DEFAULT_DB_DIR
    if model is None:
        retrieval_mode = "lexical_fallback"
        df = df.assign(_sim=_lexical_scores(df, query, db_key))
    else:
        retrieval_mode = "dense_bge"
        emb = model.encode([query], normalize_embeddings=True)[0]
        # fp16-slim compatibility branch (2026-09-28, REPOSYNC4): the embedding column supports both
        # float32-list and float16 little-endian binary storage; fp32 libraries behave bit-identically
        # to the historical version (golden-41 reconciliation).
        if db_key in _EMB_CACHE:
            emb_matrix = _EMB_CACHE[db_key]
        else:
            first = df["embedding"].iloc[0]
            if isinstance(first, (bytes, bytearray, memoryview)):
                emb_matrix = np.stack([np.frombuffer(bytes(c), dtype="<f2").astype(np.float32)
                                       for c in df["embedding"].values])
            else:
                emb_matrix = np.stack(df["embedding"].values)
            _EMB_CACHE[db_key] = emb_matrix
        df = df.assign(_sim=emb_matrix @ emb)
    if species:
        df = df[df["species"].isin([species, "both"])]
    # tissue multi-label filter (v2.0 column; any-label match; fall back when fewer than top_k*3 remain)
    if tissue:
        if "tissue_labels" not in df.columns:
            print("WARN: current library has no tissue_labels column; --tissue ignored", file=sys.stderr)
        else:
            df_t = df[df["tissue_labels"].apply(
                lambda labs: labs is not None and tissue in labs)]
            if len(df_t) >= top_k * 3:
                df = df_t
    # cell_type_mentioned metadata filter (Claude5 review requirement: retrieval filters species+tissue/cell_type)
    ct_keys = _ct_filter_keys(cell_type)
    if ct_keys is not None:
        df_ct = df[df["cell_type_mentioned"].apply(
            lambda ctm: ctm is not None and any(k in ctm for k in ct_keys))]
        # fall back to the full set when fewer than top_k*3 remain after filtering (avoid misses)
        if len(df_ct) >= top_k * 3:
            df = df_ct
    if model is None:
        df = df.sort_values("_sim", ascending=False, kind="stable").head(top_k * 3)
    else:
        df = df.sort_values("_sim", ascending=False).head(top_k * 3)
    # dedupe by paper, at most 2 entries per paper
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
            "_full_text": r["text"],  # full chunk text (for QC marker matching)
            "cell_type_mentioned": list(ctm) if ctm is not None and len(ctm) else [],
            "marker_genes": list(mg) if mg is not None and len(mg) else [],
            "relevance_score": round(float(r["_sim"]), 4),
        })
        if len(out) >= top_k:
            break
    return {"query": query, "species": species, "tissue": tissue,
            "retrieval_mode": retrieval_mode,
            "degraded": retrieval_mode == "lexical_fallback",
            "note": ("pure-lexical fallback retrieval (zero model): ranking differs from the official dense_bge version; "
                     "place the bge-large-en-v1.5 model directory to get the official ranking"
                     if retrieval_mode == "lexical_fallback" else None),
            "results": out}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell-type", default="Rod Bipolar Cell")
    ap.add_argument("--species", default=None)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--query", default=None)
    ap.add_argument("--tissue", default=None)
    ap.add_argument("--db-dir", default=None, help=f"directory containing chunks.parquet (default {DEFAULT_DB_DIR})")
    args = ap.parse_args()
    res = retrieve(args.cell_type, args.species, args.top_k, args.query,
                   tissue=args.tissue, db_dir=args.db_dir)
    print(json.dumps(res, ensure_ascii=False, indent=1))
