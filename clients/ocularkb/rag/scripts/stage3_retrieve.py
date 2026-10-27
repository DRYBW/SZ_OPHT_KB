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
v2.1 changes (2026-10-01, KB11-B):
  - new --dev-stage / retrieve(dev_stage=) hard paper-level filter on the developmental axis:
    adult | fetal_developing | unknown; None/""/"any" = no filter (default behavior byte-identical).
    Label source = the dev-stage sidecar under kb/literature_db/ (read-only, dev_stage_final field;
    papers the sidecar does not cover are unknown). Aligned with the baseline KB2c development_stage
    two-axis convention: hard filter, no fallback — the adult bucket must not answer fetal questions;
    when the filtered pool is smaller than top_k the honest short list is returned; the unknown bucket
    stays queryable (never silently dropped).
v2.2 changes (2026-10-27, developmental-axis scope gate):
  - the default adult face (no stage argument / "any") excludes papers whose scope is fetal-only, so an
    adult-视网膜 literature face no longer carries fetal specialists (a fetal paper must never answer an
    adult question; when a stage IS given the gate stands down and everything stays reachable).
  - the gate reads ONE whole-library table (kb/literature_db/dev_stage_scope_fulltext_2026-10.jsonl),
    whose scope is judged per paper from the full text by a local model and carries an original-text
    quote per paper (evidence file kept local). It replaces the earlier per-wave supplement tables.
  - the excluded scope set is a declared constant (DEFAULT_EXCLUDE_SCOPES), overridable for a run via
    EYEKB_SCOPE_EXCLUDE ("fetal_only" | "fetal_only,developing_only" | "" = gate off). Shipped default =
    fetal_only + developing_only (PI ruling 2026-10-27): the adult face drops both fetal specialists and
    developing-model / organoid / iPSC-differentiation work. Responses report the excluded chunk count
    only while the gate is actually excluding.
  - gate table missing / malformed → zero exclusion (behavior degrades to pre-gate, never crashes).
v2.3 changes (2026-10-27, same-study collapse):
  - a preprint and its later published version of the SAME study no longer take two slots in one
    answer: the preprint is replaced by the published copy when both land in the same candidate
    window. DISPLAY-ONLY — the library keeps both records, no paper_id changes, no re-ranking beyond
    the freed slot, and the freed slot is refilled by the next paper the window had not shown, so an
    answer never gets shorter than it was. Responses report the collapse only when it happened.
  - switch: EYEKB_PREPRINT_DEDUP ("0" / "off" / "false" / "no" disables; absent = enabled).
  - the pair map is machine-built from the library by build_preprint_pairs.py and is never hand-edited.
    Only the high-confidence tiers are read (A identical titles, B one title a strict prefix of the
    other, C a common leading run of >= 50 normalised characters inside the year window), so a wrong
    pair cannot silently delete a genuine result; the ambiguous band lives in a separate review sheet.
  - map file missing / unreadable → zero collapsing (behaviour identical to v2.2).
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


def _resolve_data_file(env_var, rel_path, absolute_default):
    """Sidecar lookup with the same three levels as the model dir: env override > in-repo path >
    absolute path of the machine the pipeline was built on. Returns None when the file is absent
    anywhere — every caller treats None as 'no labels', i.e. zero behavioral change."""
    env = os.environ.get(env_var)
    if env and os.path.isfile(env):
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, os.pardir, os.pardir, os.pardir, os.pardir))
    cand = os.path.join(repo_root, rel_path)
    if os.path.isfile(cand):
        return cand
    return absolute_default if os.path.isfile(absolute_default) else None


_model = None
_df = None
_db_dir = None

# --- developmental axis (KB11-B + v2.2 scope gate) ---------------------------------------------
# Label sidecar for the dev_stage argument: paper_id -> dev_stage_final (adult / fetal_developing / unknown).
DEV_SIDECAR_REL = "kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl"
DEV_SIDECAR_ABS = "/mnt/D/EyeKB/kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl"

# Scope gate table — ONE table for the whole library (per-wave supplement tables retired 2026-10-27;
# the retired files are kept on disk, and restoring the old behavior is one list edit here).
# Columns used: paper_id, stage_scope ∈ {fetal_only, developing_only, adult_only, mixed, not_recorded}.
SCOPE_SIDECAR_REL = "kb/literature_db/dev_stage_scope_fulltext_2026-10.jsonl"
SCOPE_SIDECAR_ABS = "/mnt/D/EyeKB/kb/literature_db/dev_stage_scope_fulltext_2026-10.jsonl"

# Default excluded scopes on the adult face. PI ruling 2026-10-27 ("排"): the adult face excludes
# fetal-only AND developing-only papers — an adult retina literature face must not be padded with
# fetal material or with developing-model work (E14.5 / P0-P14 / hiPSC differentiation / organoid).
# Overridable per run via EYEKB_SCOPE_EXCLUDE ("fetal_only" to walk it back, "" to switch the gate off).
DEFAULT_EXCLUDE_SCOPES = ("fetal_only", "developing_only")
# stage_scope -> developmental-axis class (used by the stage argument so that stage=fetal reaches everything).
# fetal_only / developing_only / mixed all carry fetal-developmental material -> fetal_developing; the mapping
# for the classes the earlier gate already knew (mixed -> fetal_developing, etc.) is kept verbatim on purpose,
# so adding the whole-library table does not silently shrink anyone's stage=fetal pool.
SCOPE_TO_DEV = {"fetal_only": "fetal_developing", "developing_only": "fetal_developing",
                "mixed": "fetal_developing", "adult_only": "adult", "not_recorded": "unknown"}

_dev_cache = {"key": None, "map": {}}
_scope_cache = {"key": None, "map": {}}


def _exclude_scopes():
    """Declared default, overridable per run via EYEKB_SCOPE_EXCLUDE ("" disables the gate)."""
    env = os.environ.get("EYEKB_SCOPE_EXCLUDE")
    if env is None:
        return DEFAULT_EXCLUDE_SCOPES
    return tuple(s.strip().lower() for s in env.split(",") if s.strip())


def _dev_sidecar():
    return _resolve_data_file("EYEKB_DEV_SIDECAR", DEV_SIDECAR_REL, DEV_SIDECAR_ABS)


def _scope_sidecar():
    return _resolve_data_file("EYEKB_SCOPE_SIDECAR", SCOPE_SIDECAR_REL, SCOPE_SIDECAR_ABS)


def _dev_map():
    """paper_id(str) -> dev_stage_final(lower). Sidecar missing / bad row -> empty map (all unknown)."""
    p = _dev_sidecar()
    if not p:
        return {}
    st = os.stat(p)
    key = (p, st.st_mtime, st.st_size)
    if _dev_cache["key"] != key:
        m = {}
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if "paper_id" not in d:
                    continue
                m[str(d["paper_id"])] = str(d.get("dev_stage_final") or "unknown").lower()
        _dev_cache["key"] = key
        _dev_cache["map"] = m
    return _dev_cache["map"]


def _scope_map():
    """paper_id(str) -> stage_scope(lower). Sidecar missing / bad row -> empty map (zero exclusion)."""
    p = _scope_sidecar()
    if not p:
        return {}
    st = os.stat(p)
    key = (p, st.st_mtime, st.st_size)
    if _scope_cache["key"] != key:
        m = {}
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if "paper_id" not in d:
                    continue          # header/meta line
                m.setdefault(str(d["paper_id"]), str(d.get("stage_scope") or "not_recorded").lower())
        _scope_cache["key"] = key
        _scope_cache["map"] = m
    return _scope_cache["map"]


# --- same-study collapse: a preprint and its later published version (v2.3, 2026-10-27) ----------
# Ruling 2026-10-27: when one study sits in the library twice -- as a preprint and as its
# peer-reviewed version -- an answer should spend only ONE slot on it, and the published version is
# the copy kept. DISPLAY-ONLY: both records stay in the library, no paper_id changes, no re-ranking;
# the response body states what was collapsed, and only the slots that were actually at stake change.
# Switch: EYEKB_PREPRINT_DEDUP ("0" / "off" / "false" / "no" disables it; absent = enabled).
# This is one line to walk back.
# The map is rebuilt from the library itself by plans/lit_gapfill_20261026/build_preprint_pairs.py
# and is never hand-edited: pairs in tiers A (titles identical), B (one title is a strict prefix of
# the other) and C (a common leading run of >=50 normalised characters inside the year window) are
# active; anything below that stays in a separate review sheet and is NOT read here.
PAIR_MAP_REL = "kb/literature_db/preprint_published_map_v1.jsonl"
PAIR_MAP_ABS = "/mnt/D/EyeKB/kb/literature_db/preprint_published_map_v1.jsonl"
ACTIVE_PAIR_TIERS = ("A", "B", "C")
_pair_cache = {"key": None, "map": {}}


def _preprint_dedup_on():
    env = os.environ.get("EYEKB_PREPRINT_DEDUP")
    if env is None:
        return True
    return env.strip().lower() not in ("0", "off", "false", "no")


def _pair_map():
    """preprint_id(str) -> published_id(str). Map file missing / unreadable -> empty map, i.e. the
    response is exactly what it was before this feature existed."""
    p = _resolve_data_file("EYEKB_PAIR_MAP", PAIR_MAP_REL, PAIR_MAP_ABS)
    if not p:
        return {}
    st = os.stat(p)
    key = (p, st.st_mtime, st.st_size)
    if _pair_cache["key"] != key:
        m = {}
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                pid, vid = d.get("preprint_id"), d.get("published_id")
                if pid and vid and str(d.get("tier")) in ACTIVE_PAIR_TIERS:
                    m[str(pid)] = str(vid)
        _pair_cache["key"] = key
        _pair_cache["map"] = m
    return _pair_cache["map"]


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
# Metadata filter masks, computed once per (db, column, value) over the full frame and reused by
# index. The two metadata filters used to run a Python-level .apply() over ~170k rows on every
# call, which cost more than the embedding and the matrix product together. The predicates below
# are copied verbatim from the call sites they replace, so the selected rows are identical.
_META_MASK = {}


def _cached_mask(db_key, kind, arg, full_df):
    key = (db_key, kind, arg)
    mask = _META_MASK.get(key)
    if mask is None:
        if kind == "tissue":
            mask = full_df["tissue_labels"].apply(
                lambda labs: labs is not None and arg in labs)
        elif kind == "cell_type":
            mask = full_df["cell_type_mentioned"].apply(
                lambda ctm: ctm is not None and any(k in ctm for k in arg))
        else:
            raise ValueError(f"unknown mask kind: {kind!r}")
        _META_MASK[key] = mask
    return mask


def _apply_cached_mask(df, db_key, kind, arg, full_df):
    """Select rows of df using a mask computed on full_df: same rows, same order."""
    mask = _cached_mask(db_key, kind, arg, full_df)
    return df.loc[mask.reindex(df.index, fill_value=False).to_numpy(dtype=bool)]


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

def _flag(row, col):
    """Corpus provenance flag for a result row: True/False, or None when the column is absent
    (libraries older than v2.1) or the value is NaN. Never raises on a missing column."""
    try:
        v = row[col]
    except (KeyError, IndexError):
        return None
    if v is None:
        return None
    if isinstance(v, float) and v != v:      # NaN
        return None
    return bool(v)


def retrieve(cell_type: str, species: str = None, top_k: int = 5, query: str = None,
             tissue: str = None, db_dir: str = None, dev_stage: str = None):
    model, df_full = load(db_dir or DEFAULT_DB_DIR)
    df = df_full
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
    # --- developmental axis -------------------------------------------------------------------
    want = (dev_stage or "").strip().lower()
    # (1) scope gate on the default adult face. A fetal specialist paper must not answer an adult
    #     question; when a stage IS named the gate stands down so that stage reaches everything.
    scope_excluded_chunks = None
    if want in ("", "any"):
        _ex = _exclude_scopes()
        _sm = _scope_map() if _ex else {}
        if _sm:
            _mask = df["paper_id"].map(lambda p: _sm.get(str(p)) in _ex)
            _n = int(_mask.sum())
            if _n:
                df = df[~_mask]
                scope_excluded_chunks = _n
    # (2) explicit stage argument: paper-level hard filter, no fallback.
    dev_pool = None
    if want and want != "any":
        dm = _dev_map()
        _so = _scope_map()

        def _devlab(p):
            s = _so.get(str(p))
            if s:
                return SCOPE_TO_DEV.get(s, "unknown")
            return dm.get(str(p), "unknown")
        df = df[df["paper_id"].map(_devlab) == want]
        dev_pool = int(len(df))
        print(f"dev_stage={want} hard-filtered pool={dev_pool} "
              f"(sidecar={os.path.basename(_dev_sidecar() or '-')}+scope{len(_so)})", file=sys.stderr)
    # tissue multi-label filter (v2.0 column; any-label match; fall back when fewer than top_k*3 remain)
    if tissue:
        if "tissue_labels" not in df.columns:
            print("WARN: current library has no tissue_labels column; --tissue ignored", file=sys.stderr)
        else:
            df_t = _apply_cached_mask(df, db_key, "tissue", tissue, df_full)
            if len(df_t) >= top_k * 3:
                df = df_t
    # cell_type_mentioned metadata filter (Claude5 review requirement: retrieval filters species+tissue/cell_type)
    ct_keys = _ct_filter_keys(cell_type)
    if ct_keys is not None:
        df_ct = _apply_cached_mask(df, db_key, "cell_type", tuple(ct_keys), df_full)
        # fall back to the full set when fewer than top_k*3 remain after filtering (avoid misses)
        if len(df_ct) >= top_k * 3:
            df = df_ct
    if model is None:
        df_sorted = df.sort_values("_sim", ascending=False, kind="stable")
    else:
        df_sorted = df.sort_values("_sim", ascending=False)
    # --- same-study collapse (display-only, v2.3) -------------------------------------------------
    # A preprint is dropped ONLY when its published twin sits in this same candidate window -- that is
    # the case where one study would occupy two of the caller's slots. When the twin is not in the
    # window, the preprint is the only copy of that study here and stays.
    # Refilling is by PAPER, not by row: the window is top_k*3 rows, which after the one-entry-per-
    # paper rule is often only 8-10 distinct papers, so the next row is usually another block of a
    # paper already present. Each dropped preprint is therefore replaced by the next paper that the
    # window has not shown yet, and the (rare) cascade repeats until it settles.
    pool_n = top_k * 3
    df = df_sorted.head(pool_n)
    collapsed = 0
    pm = _pair_map() if _preprint_dedup_on() else {}
    if pm:
        seen_paper = set(df["paper_id"].astype(str))
        tail_limit = pool_n + 400          # bounded scan for the replacement papers
        for _ in range(6):
            ids_now = set(df["paper_id"].astype(str))
            drop = {p for p, v in pm.items() if p in ids_now and v in ids_now}
            if not drop:
                break
            df = df[~df["paper_id"].astype(str).isin(drop)]
            collapsed += len(drop)
            tail = df_sorted.iloc[pool_n:tail_limit]
            tail = tail[~tail["paper_id"].astype(str).isin(seen_paper | drop)]
            tail = tail.drop_duplicates("paper_id").head(len(drop))
            if tail.empty:
                break
            seen_paper |= set(tail["paper_id"].astype(str))
            df = pd.concat([df, tail], axis=0)
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
            # Provenance flags that were in the corpus but not surfaced to callers (2026-10-27):
            # a top slot occupied by a preprint or by an abstract-only record was indistinguishable
            # from a full-text peer-reviewed paper in the response body. Disclosure only — no ranking
            # change; both columns exist in every library from v2.1 on and are absent in older ones.
            "is_preprint": _flag(r, "is_preprint"),
            "full_text_available": _flag(r, "full_text_available"),
            "_full_text": r["text"],  # full chunk text (for QC marker matching)
            "cell_type_mentioned": list(ctm) if ctm is not None and len(ctm) else [],
            "marker_genes": list(mg) if mg is not None and len(mg) else [],
            "relevance_score": round(float(r["_sim"]), 4),
        })
        if len(out) >= top_k:
            break
    res = {"query": query, "species": species, "tissue": tissue,
           "retrieval_mode": retrieval_mode,
           "degraded": retrieval_mode == "lexical_fallback",
           "note": ("pure-lexical fallback retrieval (zero model): ranking differs from the official dense_bge version; "
                    "place the bge-large-en-v1.5 model directory to get the official ranking"
                    if retrieval_mode == "lexical_fallback" else None),
           "results": out}
    if want and want != "any":              # key appears only while the filter is active
        res["dev_stage"] = want
        res["dev_stage_pool"] = dev_pool
    if scope_excluded_chunks:               # appears only while the gate is actually excluding
        res["adult_face_scope_excluded_chunks"] = scope_excluded_chunks
        res["adult_face_scope_excluded_scopes"] = list(_exclude_scopes())
    if collapsed:                           # appears only when a slot was actually collapsed
        res["same_study_collapsed"] = collapsed
        res["same_study_collapsed_note"] = (
            "a preprint was replaced by its published version of the same study, so the study takes "
            "one slot instead of two; the library still holds both records "
            "(EYEKB_PREPRINT_DEDUP=0 turns this off)")
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell-type", default="Rod Bipolar Cell")
    ap.add_argument("--species", default=None)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--query", default=None)
    ap.add_argument("--tissue", default=None)
    ap.add_argument("--db-dir", default=None, help=f"directory containing chunks.parquet (default {DEFAULT_DB_DIR})")
    ap.add_argument("--dev-stage", default="any",
                    choices=["adult", "fetal_developing", "unknown", "any"],
                    help="developmental-axis hard filter (any = no filter, the default)")
    args = ap.parse_args()
    res = retrieve(args.cell_type, args.species, args.top_k, args.query,
                   tissue=args.tissue, db_dir=args.db_dir,
                   dev_stage=None if args.dev_stage == "any" else args.dev_stage)
    print(json.dumps(res, ensure_ascii=False, indent=1))