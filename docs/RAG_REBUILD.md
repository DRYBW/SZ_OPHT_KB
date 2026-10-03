# RAG literature library: repo contents / rebuild / pre-built Release asset

## In the repo (metadata + engine; recomputable and traceable)
- rag_snapshots/v2.3_2026-09/: papers.jsonl (manifest of 3700 papers: PMID/DOI/title) + manifest.yaml + build_stats.json — the library's "complete bibliography"
- kb/literature_db/EYEKB_DB_POINTER.yaml: library-version pointer (chunk counts / roles / adjudication policy)
- kb/literature_db/evidence_meta_*.jsonl: per-paper inclusion-reason sidecars (EyeKB's own)
- clients/ocularkb/rag/scripts/stage3_retrieve.py: retrieval engine (used by MCP search_literature; already included in this repo)

## Not in the repo (size wall)
chunks.parquet ≈ 935 MB, a single file over GitHub's 100MB hard limit. Two acquisition paths:
1. **Pre-built Release asset (recommended)**: the EYEKB_RAG_v2.3.tar attachment of this repo's private Release (≈937MB, sha256 in the release note); unpack to any directory and point the `path` field of EYEKB_DB_POINTER.yaml at it
2. **Full rebuild**: refetch full text from PMC OA per the papers.jsonl manifest → chunk → re-embed with the public HuggingFace model bge-large-en-v1.5 (cpu). The pipeline lives on the OcularKB project side (stage1 fetch/stage2 chunk); byte-for-byte identity is not promised (embedding-version-sensitive), but retrieval behavior is equivalent
   **⚠ Homogeneity-contract note (2026-09-28, docs/VERIFY_CONTRACT.md G2)**: this path is exploratory behavior — rebuild output **must not serve as reproduction results, must not be reported labelled as "repo-system output", and must not flow back into the anchors**; for reproduction only the pre-built Release asset + a verify_repro PASS counts.

## Service wiring (one step)
In a Python 3.11+ environment install sentence-transformers/pyarrow/pandas and the mcp sdk; start `python mcp_server/server.py` (stdio, no port opened); search_literature reads the pointer automatically.

## Corpus-boundary prohibition (2026-09-30 wiring batch)
known-issues structured pages and their text fields **may never enter this RAG corpus / any index-build input** — full statement and machine-check criteria in `docs/PITFALLS_RAG_ISOLATION.md`.
