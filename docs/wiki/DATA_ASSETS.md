# Data Assets (marker-annotation project)

> All paths verified to exist. Updated: 2026-09-28 (+ KB9 ocular-surface new-entry registration section)

## 1. RAG literature library (literature_db, three versions coexisting)

| Version | Path | Content | Status |
|---|---|---|---|
| v1.0_2026-08 | `ocularkb/rag/literature_db/v1.0_2026-08/` | retina 684 papers / 46,363 chunks / bge-large-en-v1.5 | **frozen read-only** |
| v1.1_2026-08 | `ocularkb/rag/literature_db/v1.1_2026-08/` | retina supplement: 505 screened papers (not ingested at the time; its 32,789 chunks were back-computed in v2.0) | **frozen read-only** |
| **v2.0_2026-09** | `ocularkb/rag/literature_db/v2.0_2026-09/` | **whole eye, 11 tissues, 2,713 papers / 174,616 chunks** (= v1.0 inheritance + v1.1 back-computation + 95,464 from new tissues), chunks.parquet 776MB + manifest + QA + coverage report | **active** |

Companions: `QA_V2.md` (retina regression + per-tissue recall spot-checks + weak-coverage list), `build_stats.json`, manifest.yaml (contains the full per-tissue EPMC query strings).

## 2. Annotation engine and models

| Asset | Path | Notes |
|---|---|---|
| G1 LR (active) | `models/g1_hrca_main/` | full training on HRCA 3.17M cells; macro-F1 0.9969 |
| v2_prod | `models/v2_prod/v2_prod_model.pkl` | 10-class LR-HVG2000; 08-24 PASS, production not switched (SHA256 d38af37…) |
| scANVI pilot | `models/stageD_scanvi/` | for stage-D comparison only, not into production |
| P1 decision mechanism | `plans/P1_decision_20260819/` | marker reverse-exclusion gate + applicability statement v1.2 |
| Consumption API | `ocularkb/pilot/consume_p1.py` | any h5ad → P1 decision annotation (frozen caliber) |

## 3. Core datasets

| Dataset | Species | Use | Location/status |
|---|---|---|---|
| D001 HRCA | human | standard reference set (3.17M cells / 10 major classes) | fully downloaded |
| D002 OcularSurface | human | ocular-surface standard set (cornea/conjunctiva/sclera etc., 102 donors) | on disk, model not built |
| GSE243413 | mouse | mouse integrated atlas, 323K cells / 120 types (mouse-model candidate) | T2 tier on disk |
| Shekhar L4 | 13 species | cross-species annotation (ortholog-panel route) | `shekhar_annotated/` 13 h5ad |
| GSE226108 etc. | human | T2 tier | tier table `data/retina_human_mouse_tier.md` |

## 4. Script pipeline (ocularkb/rag/scripts/)

- stage1a/1b (EPMC retrieval + screening; the v2 versions add thin-tissue exemptions and noise disambiguation)
- stage2a/2b/2c (full-text download + XML parsing / chunking / embedding + merge; v2 is a 6-shard GPU pipeline)
- stage3_retrieve.py (retrieval interface: `--cell-type/--species/--tissue/--db-dir`; default library v1.0 for old-call compatibility)
- stage4_qa_recall.py + qa_v2.py (golden-set regression + per-tissue spot checks)
- embedding environment: `/home/ubuntu/.conda/envs/pipeline_env` (bge-large-en-v1.5 local)

## 5. Skills (discipline sedimentation)

- `sc-cell-annotation` (active in the default profile): annotation workflow + CyteType + the in-house own-CyteType route
- `celltype-marker-knowledge-base` (cold storage, can be enabled): marker data-retrieval discipline + discriminative signatures + cross-species pitfalls checklist

## 6. Literature index layer (folded in from the old vk)

`ocularkb/vk/literature/`: 11 tissue pages (tissue-*.md, created 2026-09-23 alongside v2.0) + 17 topic pages (photoreceptor/amd/glaucoma/aging/models etc., created in the 2026-08 retina-library era) + INDEX.md overview. Entry point: see RETRIEVAL_INDEX.md.

---

## 7. Adnexa datasets — lacrimal gland / lacrimal sac / meibomian gland (ingested 2026-09-25)

> Card `t_6fec256c` (AGENT_ROLE) | source: `USER_DIRECTIVE_20260925_eyekb_downstream_batch.md` Supplement 2
> (PI: "the MB-scale ones are fine, forget the GB ones" → only the 5 MB-scale items approved, measured total **133.73 MiB**, within the <1 GB red line)
> Retrieval precheck: `/mnt/D/EyeKB/plans/adnexa_scout_20260925/ADNEXA_SCOUT_LIST.md` (card t_e5f13ed1, zero downloads)
> Download ledger: `data/adnexa_download_20260925/ADNEXA_DOWN_DOWNLOAD_LEDGER.md` (per-file sha256)
> Routes and gaps: `data/adnexa_download_20260925/ADNEXA_DOWN_RAWTAR_ROUTE_AND_GAPS.md`

### 7.1 Tier registration (**computed from this library's own 6-dimension scoring card**, not the scout card's provisional estimate)

Scoring reuses `registry/ocularkb_tier_scoring.py` (annotation 25 / scale 15 / donor 10 / raw+license 15 / completeness 20, depth 15 PENDING not counted; max 85; T1≥70 / T2≥55 / T3≥40 / T4<40).
Inputs: `registry/adnexa_tier_scoring_20260925.csv|json`; script `data/adnexa_download_20260925/step13_tier_scoring.py`.

| accession | tissue/modality | measured scale | donors | s_ann | s_scale | s_donor | s_raw_lic | s_integ | total | **tier (computed)** | scout-card provisional tier | ingest status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **GSE164403** | Lacrimal gland (tissue + organoid) / scRNA (SORT-seq plate) | 3K | 5 | 12.5 | 4 | 8 | 14.7 | 20 | **59.2** | **T2-high** | T1 | **ingested + h5ad assembled** |
| **GSE252058** | Lacrimal sac (PANDO disease) / scRNA (BD Rhapsody) | 3×10K | 5 | 12.5 | 7 | 8 | 11.5 | 20 | **59.0** | **T2-high** | T2 | **ingested** (not assembled, route registered) |
| **GSE174653** | Lacrimal gland-like organoid (iPSC) / scRNA (10x) | not checked | 1 | 12.5 | 0 | 3 | 14.7 | 20 | **50.2** | **T3-mid** | T2 | **ingested** (cell-level unavailable) |
| **GSE17822** | Meibomian gland (tarsal plate of eyelid) / microarray (Illumina HT-12 v3) | not checked | 12 | 12.5 | 0 | 10 | 9.1 | 20 | **51.6** | **T3-mid** | T3 | **ingested** (bulk, not assembled) |
| **GSE288952** | Meibomian gland epithelial cell line (IHMGEC) / bulk RNA-seq | not checked | 1 | 12.5 | 0 | 3 | 11.5 | 20 | **47.0** | **T3-mid** | T3 | **ingested** (bulk, not assembled) |

**⚠ Tier-caliber divergence (must stay on record, to prevent downstream mis-citation)**: the tiers given by the scout card `ADNEXA_SCOUT_LIST.md` (GSE164403=T1) are a **provisional judgment based on "scientific uniqueness"**; this library's 6-dimension scoring card computes **T2-high (59.2)** —
mainly due to the scoring card's **scale-dimension penalty** (3,071 cells <1e4 earns only 4/15) and **annotation-dimension penalty** (no cell-type labels deposited in GEO, earning only 12.5/25). The two are **not contradictory**:
"the only true human lacrimal atlas" = high scientific uniqueness (scout-card view); "small scale + no author cell labels" = limited training value (scoring-card view).
**Downstream citations must state which caliber was used.**

### 7.2 Per-dataset registration

| accession | platform/samples | cell count | author cell-type labels | raw data | landing path |
|---|---|---|---|---|---|
| **GSE164403** | GPL18573 NextSeq 500; 8 GSM (4 tissue + 4 organoid), SORT-seq 384-well plate | **3,071** (1,536 tissue + 1,535 organoid) | ❌ **not deposited** (paper self-reports 18 clusters) | SRP300792 | `data/GSE164403/` (`GSE164403_annotated.h5ad` 44.85 MiB + `raw/` 4 files) |
| **GSE252058** | GPL24676; 5 GSM (BD Rhapsody), lacrimal sac PANDO | 29,352 raw barcodes (authors self-report 25,791 past QC) | ❌ not deposited (paper self-reports 11 classes) | PRJNA1057236 | `data/GSE252058/raw/` (RAW.tar 15 entries + filelist) |
| **GSE174653** | GPL24676; 3 GSM (10x), hiPSC lacrimal-gland-like organoids D0/D10/D20 | **PENDING (no cell-level matrix in GEO)** | ❌ none | SRP320381 | `data/GSE174653/raw/` (RAW.tar 3 entries + 1 cluster-mean file) |
| **GSE17822** | GPL6947 Illumina HT-12 v3; 12 GSM (6 normal + 6 MGD) | n/a (bulk array) | n/a | none (RAW.tar holds only BGX annotations) | `data/GSE17822/raw/` (RAW.tar 1 entry + non_normalized matrix) |
| **GSE288952** | GPL21697; 19 GSM, IHMGEC cell line Krox20 | n/a (bulk) | n/a | PRJNA1220084 | `data/GSE288952/raw/` (RAW.tar 1 entry + 3 comparison tables) |

### 7.3 GSE164403 assembled h5ad (this library's first adnexa cell-level h5ad)

| Item | Value |
|---|---|
| Path | `/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad` |
| Shape | 3,071 cells × 39,009 genes (1,536 tissue + 1,535 organoid) |
| X caliber | author's original near-integer counts (**not log, not library-size normalized**; measured per-cell library size 1–135,835, CV=1.45) |
| layers | `counts_int32` = round(X) integer counts (**9,192,701/9,192,701 consistent with round(X); 0 mismatches in integer recovery between float32 and float64**) |
| obs | cell_id / sample_id / gsm / source_type / patient_number / author_sort / culture_condition / passage_number / day_in_culture / total_counts / n_genes_by_counts / pct_counts_mt / author_empty_well |
| var | var_names = de-duplicated symbols (8 repeated symbols get `__dup2` suffixes); feature_name / gene_symbol / gene_biotype / gene_id_original (originally `SYMBOL__biotype`) |
| Verification | readback V1–V6 all PASS; **5/5 random cells' total_counts/n_genes recomputed independently from the gz CSV text, exact match** |
| Gap | author cell-type cluster labels not deposited ⇒ the entry layer must source them separately (paper supplementary material / own clustering) |

### 7.4 Existing hard gaps in adnexa data (unchanged this round, registered for reference)

- **Human meibomian-gland tissue single-cell atlas = 0**: across all of GEO the only human MG tissue entries are GSE17822 (array) / GSE201490 (miRNA TLDA) / GSE250294 (AAL-sorted subsets, not an MG atlas); the only human MG single-cell source is **SRP497138 (SRA-only, 171.7 GB, not approved)**.
- **CELLxGENE's 2,235 datasets carry zero `meibomian gland` tissue labels**; HCA Azul organ=lacrimal/meibomian/eyelid all have 0 projects.
- The lacrimal sac (GSE252058) is a **tear-drainage structure, not the lacrimal gland proper**, and is entirely PANDO disease material ⇒ **usable only as a disease reference line; merging into the normal lacrimal baseline is prohibited** (baselines discipline).
- GSE174653 is unavailable at cell level (GEO stores cluster means only); obtaining cell level needs FASTQ + aligner + an 11 GB reference — **requires separate PI approval**.

### 7.5 Intermediate artifacts (all retained)

```
data/adnexa_download_20260925/
├── step1_download.py … step13_tier_scoring.py   # 14 scripts (incl. dbg_csv*.py debug artifacts)
├── logs/                                        # step1/5/7/7b/8/11/13 run logs
├── metadata/                                    # series+gsm SOFT text for the 5 GSEs
├── download_ledger.json                         # per-file expected/measured bytes + sha256 + tar entries
├── rawtar_reconcile.json                        # filelist↔tar reconciliation
├── GSE164403_assemble_report.json / _verify.json
├── GSE164403_counts_qc_overview.txt (+4 tsv)     # grouped count tables + QC overview
├── GSE164403_qc_threshold_probe.json            # reverse-inference of the "916 pass QC" threshold (44 near-value groups ⇒ not uniquely determinable)
├── ADNEXA_DOWN_DOWNLOAD_LEDGER.md               # ① download ledger
└── ADNEXA_DOWN_RAWTAR_ROUTE_AND_GAPS.md         # ③ routes and toolchain gaps
```

## 8. kb/ marker-entry library (EyeKB `mcp_server` query_marker multi-library surface)

Active default `all` = retina(v4.1)+membrane+retina_interneuron(v5) (the OFF fallback state) + retina_v6+face_v6 (the ACT 09-26 activated default state); lacrimal_v6 / k9_ocs are **excluded from the default in every state** (reachable only via explicit library= routing).

| Library (library=) | File | Version | Content | Status |
|---|---|---|---|---|
| retina / membrane / retina_interneuron | `EyeKB/kb/markers/` v4.1/v1/v5 | — | the three incumbent libraries | default ON |
| retina_v6 / face_v6 | same as above | v6.0 | KB7 repaired panels | activated (EYEKB_ACT_V6, rollback-able) |
| lacrimal_v6 | `markers_v6_lacrimal_increment.json` | v6.0-lacrimal | KB8 lacrimal, 3 entries | registered default OFF (PI A3 not switched for now) |
| **k9_ocs** | `markers_k9_ocs_increment.json` | **k9.0-ocs-registered-v1** | **KB9 case-B, 4 new ocular-surface entries**: Melanocyte(CL:0000148, 10 genes)/Schwann(CL:0002573, 4)/Conj_epithelium_suprabasal(CL:1000432 borrowed parent entry + layer, 3)/Limbus_Sclera_fibroblast_C1(CL:0000057 attached to parent entry + subtype, 3); each entry carries its CL id + OLS back-verification + per-gene PMID chain (the §0 development-set qualifier statement travels with the file) | **registered default OFF** (t_4bb75b26, PI D17; activation = obligation run + separate PI approval) |

Sidecar companions (inert data, not loaded by the MCP runtime): `_k9_ocs_rules_overlay_v1.json` = R1 per-entry scope table 34 rows + R2/R3 block tables 283 rows (kept 225/block 28/R1_drop 30) + effective gene set + assembly rules v2 (AV2-1..5) + crosswalk_ext 11 rows + A09 mapping snapshot 38 rows + A03 same-source registration table + A19 exemption table + C2b comparison note + §10-6 pre-activation obligation table.
Underlying evidence files (read-only archive, diffable): `EyeKB/plans/kb9_ocs_20260927/{build,out,register,ledgers}/`; execution self-attestation: `plans/kb9_ocs_20260927/exec/` (pre/post sha record table + 42-probe full equality + GOLDEN41/KB2C regressions).
