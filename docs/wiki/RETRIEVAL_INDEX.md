# Retrieval Index (how to find things)

> RAG query commands + project document map. Updated: 2026-09-23

## 1. RAG literature queries (most used)

```bash
cd /mnt/D/OcularKB/ocularkb/rag
/home/ubuntu/.conda/envs/pipeline_env/bin/python scripts/stage3_retrieve.py \
  --cell-type "keratocyte" --species human --tissue cornea \
  --db-dir literature_db/v2.0_2026-09 --top-k 5
```

- Three-dimensional filtering: `--cell-type` (required) + `--species` (human/mouse, incl. both) + `--tissue` (11 tissue labels: retina/cornea/conjunctiva/sclera/trabecular_meshwork/iris/ciliary_body/lens/optic_nerve/RPE/choroid)
- `--db-dir` omitted = defaults to v1.0 (old-behavior compatibility); **for the active project, explicitly pass v2.0**
- Returns: PMID + journal year + species + literature snippet + marker genes + relevance
- Usage boundary (rewritten by PI decision 2026-09-26 as the "evidence-consumption discipline v2", see USER_DIRECTIVE_20260926_redline_rewrite.md): **consuming RAG/MCP evidence on the annotation/reading side = legitimate and the core design; the scoring/adjudication side (ground-truth matching, hit rate, consensus adjudication, any automated scoring/confidence weighting) is banned from consuming evidence sourced from the reading side** (red line, anti circular self-validation)

## 2. Document map (where this project's things live)

| Type | Path |
|---|---|
| Task brief (v2.0 expansion) | `ocularkb/rag/BRIEF_RAG_V2_PANOCCULAR_20260923.md` |
| Task brief (dataset inventory) | `plans/BRIEF_TISSUE_REFERENCE_INVENTORY_20260923.md` |
| QA/coverage/manifest | `ocularkb/rag/literature_db/v2.0_2026-09/` (QA_V2.md + manifest.yaml) |
| Pipeline scripts | `ocularkb/rag/scripts/` (stage1→stage4; the v2 suffix = artifacts of this iteration) |
| Engine-applicability statement | `plans/P1_decision_20260819/APPLICABILITY_STATEMENT.md` |
| Stage history (macro) | `/mnt/D/OcularKB/PROJECT_STATE.md` (project-level general ledger, complementary to this WIKI) |
| Human/mouse data tier table | `data/retina_human_mouse_tier.md` |

## 3. Literature index layer (folded in from the old vk; entry points)

- Overview: `ocularkb/vk/literature/INDEX.md` (v2.0 whole-eye navigation over 2,713 papers)
- 11 tissue pages: `tissue-*.md` in the same directory (created 2026-09-23; per-tissue literature overview)
- 17 topic pages: photoreceptor / amd / glaucoma / aging / models / metabolism etc. (created in the 2026-08 retina-library era; content still valid)
- Note: topic-page ↔ tissue-page cross links are the content of the v2.1 reinforcement card; currently the two page sets are each independently queryable

## 4. The correct order for marker lookups (discipline, do not invert)

1. Local knowledge bases: MarkerBase fingerprint library / curated marker JSON (`ocularkb/pilot/markers_v4.1_clean.json`) / local author-annotated reference atlases
2. Local RAG (retrieval commands above)
3. Only if neither has it, go to the web — and cross-species use must check species specificity (skill: celltype-marker-knowledge-base)

## 4b. Multi-library marker queries under kb/ (MCP query_marker library= routing)

- Default `library=all` = merge of the incumbent libraries (includes retina_v6/face_v6 in their activated state; lacrimal_v6/k9_ocs are **excluded from the default in every state**).
- **KB9 ocular-surface new entries (registered default OFF, 2026-09-28 PI D17)**: reachable only via explicit `library=k9_ocs` —
  `query_marker(cell_type="Melanocyte", library="k9_ocs")` / reverse lookup by genes / empty-argument roster (4 classes).
  Entry file `EyeKB/kb/markers/markers_k9_ocs_increment.json` (each entry carries a CL id + OLS back-verification + per-gene PMID chain);
  the block/applicability/assembly rules v2 sidecar sits in the same directory as `_k9_ocs_rules_overlay_v1.json` (consumed by reading the file directly; MCP does not load it).
  Lacrimal entries work the same way via `library=lacrimal_v6`. For the full activation-status table see DATA_ASSETS.md §8 / the ARCHITECTURE_REVIEW_20260924 supplement.

## 5. Chinese-language search tips

For whole-corpus grep use the `search_files` tool (ripgrep-backed); the pattern supports regex. Much of the corpus is still written in Chinese (e.g. the online WIKI originals and plan documents), so searching with the original Chinese terms (such as "覆盖弱" (weak coverage), "豁免" (exemption)) hits faster.
