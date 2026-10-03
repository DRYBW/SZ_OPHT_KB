# EyeKB / SZ_OPHT_KB — ophthalmology knowledge base: MCP · RAG · Wiki · Skill four-layer system (cloneable run mirror)

> **Repo characterization (PI corrected it on 2026-09-27)**: this repo = a **cloneable run mirror** of the EyeKB four-layer system — not a documentation backup, not a snapshot archive. Anyone who clones it and configures dependencies per this README can: ① start the MCP evidence service ② pull the Release to restore the RAG corpus ③ read the current project state in docs/wiki ④ reproduce the interpretation and evaluation workflows via docs/skills + docs/plans.
> The project itself: a second-tier ophthalmology literature knowledge base · evidence service (launched by PI decision 2026-09-23). Service version = `KB1v2-0.6-kbgov5` (consistent with `mcp_server/server.py`; the 0.5-k9reg→0.6-kbgov5 change = the B5 cross-species governance implementation from addendum-five queue ①, see the version notes).

## 5-minute quickstart (from zero to a retrieval result)

```bash
# 1) Clone + dependencies (Python 3.11+)
git clone <repo-url> && cd SZ_OPHT_KB
python3 -m venv .venv && . .venv/bin/activate
pip install "sentence-transformers>=3" pyarrow pandas numpy mcp

# 2) Pull the pre-built RAG corpus Release asset (fp16-slim derived asset, 379MB; retrieval ranking bit-for-bit identical to the fp32 original, see the asset's manifest)
#    GitHub web UI: Releases -> v2.4.2-rag-assets, download all files; or gh CLI:
gh release download v2.4.2-rag-assets --pattern '*'
cat EYEKB_RAG_v2.4.2_slim.tar.part_* > EYEKB_RAG_v2.4.2_slim.tar
sha256sum -c EYEKB_RAG_v2.4.2_slim.tar.sha256   # acceptance = the hashes; if anything is missing, do not untar
tar -xf EYEKB_RAG_v2.4.2_slim.tar               # yields literature_db/v2.4.2_2026-09_slim/

# 3) One command-line retrieval check (the engine auto-detects both fp32/fp16 embedding storages)
python clients/ocularkb/rag/scripts/stage3_retrieve.py \
  --cell-type "Muller glia" --tissue retina --db-dir literature_db/v2.4.2_2026-09_slim

# 4) Start the MCP stdio evidence service (stdio, no port opened; connects to any MCP client)
python mcp_server/server.py
#    search_literature with db="literature_db/v2.4.2_2026-09_slim" uses the latest library;
#    omitting db = the v2.0 default surface (same path as the pre-built asset, see docs/RAG_REBUILD.md)

# 5) Homogeneity acceptance (optional but strongly recommended): does this machine output the same distribution as the whole-repo anchors — one command answers
pip install -r requirements.repro.txt   # skip if you installed per the lock above
python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
#    REPRO PASS: 41/41 = homogeneous; on FAIL follow docs/VERIFY_CONTRACT.md §4 three-layer triage, modifying the criteria yourself is forbidden
```

Dependent model: `BAAI/bge-large-en-v1.5` (public HuggingFace weights, fetched automatically on first use; this repo contains no weights).

## Four-layer system map

| Layer | Content | Repo location |
|---|---|---|
| **MCP service layer** | stdio evidence service (5 tools) + call audit-trail layer + soft-flag layer | `mcp_server/` (server.py / eyekb_core.py / calllog.py / softflags.py) |
| **RAG literature layer** | whole-eye literature library (v2.0 live default: 174,616 chunks / 2,713 papers; v2.2–v2.4.2 see the pointer and the Release) | metadata `rag_snapshots/v2.3_2026-09/`; main library = Release `v2.3-rag-assets` (6 files); engine `clients/ocularkb/rag/scripts/stage3_retrieve.py` |
| **Wiki knowledge layer** | project current state / decisions / redlines / directive (sanitized mirror, incl. frozen hash anchors) | `docs/wiki/` (15 files, incl. PROTOCOL_VOTING_v2_C2b) |
| **Skill + interpretation layer** | two skill mirrors + interpretation protocol files + the full evidence chains of the 09-26/27/28 annotation-evidence reports | `docs/skills/` (annotation-eval-ops, knowledge-guided-cell-annotation, protocols/); `docs/plans/` (2260 files); knowledge assets `kb/` (104 files) |

## What the system produces (genuine demo outputs)

![EyeKB demo v2 interpretation output — UMAP of the myeloid subsets in the PDR vitreous membrane](figures/umap_myeloid_sub.png)

![QC view — compartment distribution + doublet labels](figures/umap_compartment_doublet.png)

- The upper figure (cover) = the EyeKB demo v2 interpretation output for dataset GSE165784 (PDR vitreous membrane, scRNA): harmonypy batch integration + Scrublet doublet QC + myeloid-subset deep dive (Microglia/Macrophage/Mono/DAM-LAM refinement), with KB entries participating in the interpretation; the lower figure = the QC view (compartment distribution + doublet labelling, label without removal). The generation scripts accompany the figures in `docs/plans/figure_uplift_20260928/scripts/` (per-file sha ledger in `docs/recon/RECON_figures_20260928.tsv`).
- The demo's nature follows the WIKI policy: labels = agent proposals + KB evidence, final only after per-cluster PI confirmation; both figures show how the system works and constitute no therapeutic or clinical conclusions. The old v1 figures (umap_cluster/umap_sample) moved to `figures/v1_legacy/`, kept as audit trail only, no longer referenced by this README.

## 1. MCP service layer: running it after clone

### 1.1 Dependencies

The service itself needs only **Python ≥3.10 + `mcp` (stdio server SDK, lab-tested at v2.0.0) + numpy + pandas + pyarrow**; retrieval embedding additionally needs `sentence-transformers` (CPU inference suffices; GPUs reserved for research).

```bash
python -m venv .venv && . .venv/bin/activate
pip install mcp numpy pandas pyarrow sentence-transformers
```

Embedding model = the public HuggingFace model **bge-large-en-v1.5** (weights do not enter the repo):

```bash
huggingface-cli download BAAI/bge-large-en-v1.5 --local-dir ./models/bge-large-en-v1.5
```

Then point `MODEL_DIR` and `BASE` at the top of `clients/ocularkb/rag/scripts/stage3_retrieve.py` to your local paths (the engine is a verbatim copy from OcularKB and defaults to the lab working disk).

**Related-environment note (whenever interpretation/evaluation scripts touch h5ad)**: this lab reads eval-set h5ad files in the scrnaseq environment (**anndata 0.13.2**, backed raw mode verified readable); **pipeline_env (anndata 0.11.4) is incompatible with this group's matrices** (nullable-string columns load as object dtype and crash downstream; declared an unusable environment; if you insist on writing h5ad with 0.11+, `anndata.settings.allow_write_nullable_strings=False` is required). The pure MCP service and the docs recomputation scripts do not depend on anndata.

### 1.2 stdio registration sample (any MCP client)

```json
{
  "mcpServers": {
    "eyekb": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/SZ_OPHT_KB/mcp_server/server.py"]
    }
  }
}
```

Inside `server.py`, `kb_root` resolves relative to the file's own location, so `kb/` is readable straight after clone; only `search_literature` needs the RAG library path pointed at the restored literature_db (see §2 and `kb/literature_db/EYEKB_DB_POINTER.yaml`). Local stdio, no network port opened (SSE/remote is P3, unauthorized).

### 1.3 env switch matrix

| Variable | unset / other value | ∈ {0,false,off,no} (strip+casefold) | Semantics |
|---|---|---|---|
| `EYEKB_ACT_V6` | **ON**: query_marker defaults to `library=all`, merging in retina_v6 + face_v6 (same-name classes disambiguated via `<library>::<class>` aliases) | OFF: falls back to the three live libraries; the off-state response is byte-for-byte identical to the pre baseline (A5 machine-readable acceptance) | KB7 red-entry remediation-panel activation switch (PI approved activation 2026-09-26; lacrimal_v6 **enters the default in no state**, explicit queries only — PI A3: not switched yet) |
| `EYEKB_MCP_SOFTFLAGS` | **ON**: responses carry `soft_flags` (two flavours: flag#1 rod-BC parameter parallel groups / flag#2 mural TOP3 boundary reminder) | OFF: the `soft_flags` key does not appear at all | soft re-review cue layer (third state = key absent from the response; consumers treat it as default) |
| `EYEKB_MCP_TRACE_TAG` | audit-trail record tag empty (real traffic) | self-set string | self-test traffic tagging; the OBS-2 statistics tool excludes tagged records by default |
| (no env, hard-coded OFF) | `library=k9_ocs` reachable only by explicit query (KB9 plan-B ocular surface, 4 new entries, registration default OFF) | enters the default `all` in no state | KB9REG-EXEC t_4bb75b26 (PI D17 registration approval 2026-09-28; activation requires the §10-6 obligation run + separate PI approval; lacrimal_v6 likewise keeps its A3 registered state) |

Three-tool contract + the two KB1v2 interpretation-layer tools:

- `search_literature(cell_type, species?, tissue?, top_k?, query?, db?)` → chunks + PMID + journal year + marker co-occurrence + relevance (v2.0 adds the inclusion_reasons/claim_relation/evidence_context three-field join)
- `get_kb_page(scope=index|topic|tissue, name)` → VK index page verbatim (whitelisted paths prevent traversal)
- `query_marker(genes?|cell_type?, library?)` → local authoritative marker hits (the local-first-then-online rule, mechanized)
- `get_tissue_composition(species, tissue, disease?, development_stage?)` → donor-level composition baseline (KB2c developmental axis, two tiers: adult_only primary tier + adult_pool reference tier; fetal/developing returns transition-state concept entries; answering by proxy from the adult bucket is forbidden)
- `get_disease_prior(disease, tissue?)` → thin-layer entries of the disease×tissue matrix (identity hierarchy + state axis + sampling-material mismatch warning)

### 1.4 Call audit-trail layer (calllog.py, OBS-1)

Adds logging only, zero behavior change: every tool response is written to `logs/mcp_trace/calls_YYYY-MM-DD.jsonl` (line-atomic writes via O_APPEND; >200MB continues into `.partN`; no auto-deletion). Record = tool name / inputs (query strings are domain information, not personal-sensitive data) / **structural summary** of the response (flag_id and category names, not the full notes or chunk bodies) / env state / process uuid + pid + host. The observation-window statistical basis: see `docs/plans/obs_followup` (the 09-26 card) and the WIKI current-state page.

## 2. RAG layer: restoring the corpus from the Release (v2.3)

The 937MB main library exceeds GitHub's single-file wall, so it ships as **split volumes in Release `v2.3-rag-assets`** (5×192MB parts + `.tar.sha256`, 6 files total):

```bash
gh release download v2.3-rag-assets --repo <owner>/SZ_OPHT_KB --pattern '*'
cat EYEKB_RAG_v2.3.tar.part_* > EYEKB_RAG_v2.3.tar
sha256sum -c EYEKB_RAG_v2.3.tar.sha256          # acceptance = byte counts and hashes; if anything is missing, do not untar
tar -xf EYEKB_RAG_v2.3.tar                       # yields literature_db/v2.3_2026-09/{chunks.parquet,papers.jsonl,manifest.yaml,build_stats.json}
```

Then point `kb/literature_db/EYEKB_DB_POINTER.yaml`'s `default` at the unpacked directory (current default = v2.0; v2.2/v2.3 marked latest pending PI's switch decision — **do not change unilaterally**; since 09-28 the pointer additionally carries the **v2.4 / v2.4.1 / v2.4.2 blocks = frozen read-only staging, MCP/stage3 default unswitched, v2.0 unchanged**, see the "version notes" below). The in-repo `rag_snapshots/v2.3_2026-09/` stores the three metadata files (papers.jsonl/manifest.yaml/build_stats.json, byte-identical to the live v2.3 directory); the fuller three-path rebuild guide (unpacking the pre-built asset / rebuilding from the bibliography / fallback without the literature layer) is in `docs/RAG_REBUILD.md`.

**Release asset discipline (09-27 REPOSYNC verified)**: since the 09-25 packaging, the live v2.3 corpus side is unchanged (chunks.parquet/papers.jsonl/manifest.yaml/build_stats.json mtimes all ≤09-25 08:19; papers.jsonl and manifest.yaml hash-reconcile equal to rag_snapshots). The six Release files are **neither re-uploaded nor modified**; if corpus drift is ever found, report it honestly and cut a new tag rather than overwriting. (09-28 REPOSYNC2 local reverification: the re-split tar's five parts match the Release attachment digests part by part, and the merged sha matches the ledger — six files, complete, zero drift; see `docs/plans/repo_sync2_20260928/out/t6_release_reverify.txt`.)

### Version notes — 09-28 improvement wave (REPOSYNC2)

- **RAG pointer, v2.4 / v2.4.1 blocks** (`kb/literature_db/EYEKB_DB_POINTER.yaml`, final sha256=c7f2e0f7…, reconciled character-for-character against the registration document):
  - v2.4 = v2.3 fully inherited, zero recomputation + RAGGAP tier-A 64 papers (230,426 chunks / 3,749 unique papers; card t_d0bea5a6 D19).
  - v2.4.1 = v2.4 fully inherited, zero recomputation + RAGFIX2 whitelisted closed set of 17 papers (231,707 chunks / 3,766 unique papers; card t_6848d3de D21).
  - **Both blocks are frozen read-only staging: the MCP/stage3 default has NOT been switched (v2.0 unchanged); this repo surface does not constitute "activated" semantics**; switching authority lies with the PI. The main libraries themselves (1.02–1.03 GB class) live on the OcularKB side and are not in this repo (per the Release large-file discipline).
  - Gate numbering chain (repo-surface wording, verbatim from the registration document): v2.4 gate ③ (tier-A coverage) 72.8% < 80% — **FAIL recorded honestly**; after the RAGFIX2 backfill, v2.4.1 gate ③ on the original denominator 92 / original threshold 80% / original criterion recomputes to 78/92 = **84.8% PASS, superseding v2.4's status as the "latest deliverable"**; gate ① (golden 41/41 regression queries exactly identical in off state) and gate ② (strict retina gate) both PASS for the two versions. v2.4→v2.4.1 monotonicity check: 67 items, zero regressions.
- **Two INERT sidecars under kb/markers/** (byte mirrors, sha identical to the registration document): `_raggap_errata_v1.json` (LILRB2 evidence retraction + sample20 mis-citation registration, 10da875a…) and `_raggap_c_linkbackfill_v1.json` (tier-C 830-row index backfill, default OFF, b832a694…). **Neither file is referenced by any mcp_server code path** (REPOSYNC2 T1 static assertion `raggap-inerts-unwired` on record).
- **KBX lacrimal quantitative first exam (t_0fb07fd6), characterization recorded as-is**: the O3 downgrade = **exam instrument invalid** (after the external-literature Tier1 panel rebuild, 4/7 groups are panel_unavailable), not an entry losing on the merits; A3 lacrimal_v6 keeps its registered default OFF, no switch; the lacrimal quantitative first exam is booked as "awaiting new data" (KBX_RULING_1 / KBX_VERDICT).
- **KBCHAIN whole-library citation-chain audit (t_3a35a2cc)**: chain ledger 8,531 instances fully checked + 15% sampled; confirmed that mis-citations concentrate in the decision-table transcription channel (all evidence-collection files taken into the repo; zero writes on the kb/ surface).
- **RETRAIN four-target impact assessment (t_ed4a3c52)**: conclusion = **zero retraining** (answered from the ledger: v2_prod / mouse_prod_v1 / RAG embeddings / panel-derived assets all read none of the surfaces changed here); the assessment products are read-only in nature.
- **KBGOV / PME3 / GRADE three lines** (`kb_gov_20260928/`, the third batch of `panel_pmid_20260927/` (follow-along sha recheck if there is any increment), `grade_anchor_20260928/`): candidate and analysis nature; **zero registration, zero wiring, zero activation**.
- docs/plans/ gained eight card directories plus this closeout card's directory; docs/wiki fully refreshed to the live state (newly added USER_DIRECTIVE_20260928 improvement-wave directive); docs/skills mirrors refreshed in lockstep. Intake/exclusion list and six-gate test results = `docs/plans/repo_sync2_20260928/REPOSYNC2_COMPLETED.md`.

### Version notes — 09-28 addenda five/six wave (REPOSYNC3)

- **B5 production-code implementation (addendum-five queue ①, implemented and active by default)**: `mcp_server/server.py` version `KB1v2-0.5-k9reg → KB1v2-0.6-kbgov5`; `eyekb_core.py` gains the KBGOV governance layer; the frozen vocabulary `kbgov_vocab.json.gz` ships alongside the code (sha 9b504a2e…, reconciliation = REPOSYNC3 T2 table MATCH). query_marker genes-mode cross-species governance default ON: mouse-origin inputs (confirmed∨suspected) have named rankings cleared to `unranked_candidates` + `no_named_ranking_for`; pure co-expression hits for AMBIG{GLUL,VIM,CLU} carry a `no_naming_claim` annotation (ranking untouched); human input gets zero intervention; env `EYEKB_KBGOV_B5=0|false|off|no` rolls the whole feature back to the pre baseline byte-for-byte in all states (A5-style rollback self-proof = `docs/plans/kbgov_b5impl_20260928/out/B5IMPL_A5_ROLLBACK.tsv`). Criteria frozen from KBGOV_CANDIDATE §G1–§G3; all five acceptance gates PASS, see the task's `B5IMPL_COMPLETED.md`. Limitation recorded as-is: title-case human gene symbols sent upstream carry a false-rejection risk → T+7 observation window; if >0, falling back to the B4 behavior requires separate PI approval.
- **H1M3 ordering-anchor implementation (addendum-five queue ②, effective prospectively)**: `docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md` adds the codified §9 ordering anchor (§0–§8 inherited verbatim; historical v1.1/v1.2 files untouched in-repo); the interpretation-runner naming-chain components land in `docs/plans/grade_h1m3impl_20260928/` (9 archived recomputation gates identical, OBLIGRUN sensitivity control delta=0).
- **RAG pointer, v2.4.2 block** (`kb/literature_db/EYEKB_DB_POINTER.yaml`, final sha256=a9072609…, the assertion that the appended prefix is byte-for-byte unchanged passed): v2.4.2 = v2.4.1 fully inherited, zero recomputation + RAGFIX3 scan-passed 103 papers / 11,221 chunks (242,928 chunks / 3,869 unique papers; card t_b94d0999). Gate ③ on the original denominator 92 / original threshold 80% / original criterion recomputes = **87/92 = 94.6% PASS** (zero movement of criteria; the 78→87 monotonicity check covers all 78 v2.4.1 items, zero regressions; the 5 residual items are registered as-is, lowering the bar retroactively is forbidden); gate ① golden 41/41 regression queries exactly identical in off state + zero verbatim drift in top5; gate ② retina gate not degraded. **Still frozen read-only staging: the MCP/stage3 default has not been switched, v2.0 unchanged**; the main library (1.076 GB) lives on the OcularKB side, not in this repo.
- **Obligation run and activation wording (the current master caliber, fixed)**: OBLIGRUN (t_c145db7c, the obligation body of registration package §10-6) VERDICT=**READY** — P1 **26/33** (goalpost ≥24, never lowered) / P2 0/33, four-piece set OB1–4 fully cleared; **the master figure for the 33 clusters = 26/33** (activation has not occurred; OB-5 activation authority rests with the PI, `ACTIVATION_READINESS.md` is an advisory ballot only; k9_ocs and all v2.4.x remain default OFF, and any "started/enabled" style phrasing is banned as a misreading). Same-source ballot exclusion follows RULING_1 (the v2.1 sanitized-surface hit set is exactly 2 rows, machine recomputation identical).
- **MOUSEEXT mouse-version heavy-redownload precheck (t_f2bd45ce)**: line-level approval-request list with zero downloads (15 candidate rows: 13 not taken / 1 pending a further check / rows awaiting the PI's tick for >1GB = **0 rows**); net conclusion = the heavy redownload will most likely not backfill a genuine second external F1 — the ceiling is nailed down. No download action occurred.
- **T7 own-data token permanent gate, first run (addendum six)**: intake-surface scan across eight categories of own identifiers = zero HARD residue; the two normative texts themselves (this document's task brief / the WIKI addendum-six clause original) contain literal token enumerations → the repo keeps masked versions, registered file by file in `docs/plans/repo_sync3_20260928/ledgers/T7_EXCLUSIONS.tsv` (live originals stay machine-side); 32 literature-generic-name-level ADVISORY items may remain, each individually reviewed (per the PI directive's original wording).
- **T8 §9 corpus same-provenance screening, pre-inventory (inventory only, no library changes)**: lineage-hit list for the three corpus versions v2.4/v2.4.1/v2.4.2 × registry truth = `docs/plans/repo_sync3_20260928/S9_SCREENING.md`.
- docs/plans/ gained five card directories (`kbgov_b5impl_20260928/` `grade_h1m3impl_20260928/` `obligrun_20260928/` `mouse_ext_precheck_20260928/` `rag_fix3_20260928/`) plus this document's directory; docs/wiki fully refreshed to the live state (USER_DIRECTIVE_20260928 addenda four/five/six taken in, addendum six masked); docs/skills protocols layer gained v1.3. Intake/exclusion and eight-gate results = `docs/plans/repo_sync3_20260928/REPOSYNC3_COMPLETED.md`.

### Version notes — 09-28 night / 09-29 wave (REPOSYNC5)

- New kb-layer composition-prior surface `kb/composition/` (EXPECTED_COMPOSITION_v0 = per-cell-type proportion ranges for the normal adult eye, every row tagged with a PMID, derived only from the on-disk registry ledger / literature index; derivation from our own clusters is forbidden; **default OFF, unwired**; the self-check emits only the flag list COMP_SELFFLAG_20260928.md).
- New plans surface: `seurat_probe_20260928` (dual-track probe deliverables: report + three numbers + tables + scripts; the big data/ files not taken, see appendix A), `drsc_disc_quant_20260928` (read-only quantification of donor leverage + depth shift, checkbox table handed to the PI), `comp_prior_20260928` (two task briefs: DISC-COMP / COMPV1), `QUEUE_20260929.md` (in-flight work state machine), `SYNC_NOTE_20260928_drsc_labels.md` (cross-window message, masked).
- WIKI surface: directive addendum eight (the PI's standing autonomous-progression order) taken in masked; current-state / INDEX increments; new page PROJECT_REVIEW_20260928 (added at the time under a Chinese-named file; renamed to this slug in the 2026-10-03 English migration; a panoramic handoff document in `docs/wiki/`).
- Gate system: all eight gates pass = this wave REPOSYNC5 (T3 v4 idempotent scan=0 / T4 T7 permanent gate HARD=0 / T5 golden-41 bit-for-bit / T6 fresh clone / T2 frozen surface 154 files identical before/after); evidence = `docs/plans/repo_sync5_20260929/`.
- Territory isolation: outputs of COMPV1 (an in-flight card), `kb/composition/*v1*` and `plans/comp_prior_v1_*`, are uniformly not taken (any mtime-sweep hit triggers removal, registered as "awaiting the next round").

## 3. Wiki layer

`docs/wiki/` = the sanitized mirror of OcularKB/WIKI (current state / decision log / conclusions quick-reference / INDEX / redline and directive chain, incl. the PROTOCOL_VOTING_v2_C2b.md voting-rules v2 decision document). Policy: the **only** difference between mirrored files and live files = sanitization label replacement (see `docs/DESENS_SCAN_REPORT_20260927.md`); PI quotations kept verbatim, zero hits on account patterns.

## 4. Skill + interpretation layer: entry points for recomputing evaluations

- **Protocol files** (required reading for annotation interpretation; the four-phase "freeze first, then compare"): `docs/skills/protocols/ANNOTATION_PROTOCOL_v1.1.md` / `v1.2.md` (the authoritative text for the interpretation-layer workflow; the operational definition of redline ② is in the added section of the WIKI redline-rewrite file) + `PROTOCOL_VOTING_v2_C2b.md` (the voting-rules v2 decision document: effective for preregistered runs once signed off; historical rulings are not retroactively amended).
- **Skill mirrors**: `docs/skills/annotation-eval-ops/` (the complete Run1–Run7+ ballot ledgers and power conclusions, incl. the run6b-run7rg efficiency reference), `docs/skills/knowledge-guided-cell-annotation/` (KB interpretation-layer design and repair cycles).
- **The full evidence chain of the annotation-evidence reports** `docs/plans/` (per-card from 09-26/27; VERDICT/PREREG/interpretation tables/ballot archives/scripts taken in pairs):
  - `evidence_scoring_20260926/` (E1 scoring experiment completed) · `e2_decontam_20260926/` (the E2 decontamination leg) · `e3_rescue_20260927/` (the E3 rescue leg + `AUDIT_SOP_v1.0.md`, the full-rerun audit SOP)
  - `e2r_s5audit_20260927/` (E2-R S5 row-by-row audit) · `btest_20260927/` (free-query A/B validation: PREREG + ballot archives annotation/*.jsonl + toolcalls + interpretation tables)
  - `tiep_20260927/` (counterfactual evaluation of the tie/abstention protocol) · `panel_pmid_20260927/` + `batch2/` (PME/PME2 evidence-chain backfill, two batches: 338-key ledger + pme_accounts.tsv)
  - `kb9_ocs_20260927/` (KB9 ocular-surface registration package: five rounds of external-review prompts/replies with a full audit trail + BUILD_REPORT + REGISTER_PACKAGE v2) · `proto_v2_20260927/` (landing point of the voting-rules v2 decision document) · `rag_anno_usability_20260927/` · `sync_scSOP_20260927/` · `repo_sync_20260927/` (the task brief for this mirror sync)
  - **09-28 improvement wave (REPOSYNC2 intake)**: `kbx_lacrimal_20260928/` (lacrimal quantitative first exam: PREREG v2 + interpretations + ballot desk + REVIEWER_LLM review submissions; the two cluster-level h5ad files excluded, see appendix A) · `kb_chain_audit_20260928/` (whole-library citation-chain audit evidence surface, incl. the 31MB epmc batch ledger taken in full) · `rag_fix_20260928/` (RAGFIX v2.4 three gates + errata; the 9MB raw fetch cache excluded, see appendix A) · `rag_fix2_v25_20260928/` (v2.4.1 whitelisted closed set + gate-③ backfill, taken in full) · `kb_gov_20260928/` · `rag_gap_20260928/` (three-tier approval-request list) · `grade_anchor_20260928/` · `retrain_assess_20260928/` · `repo_sync2_20260928/` (the task brief for this document + six-gate test outputs + closeout file)
  - **09-28 addenda five/six wave (REPOSYNC3 intake)**: `kbgov_b5impl_20260928/` (B5 implementation five gates + A5 rollback ledger + vocabulary reconciliation, taken in full) · `grade_h1m3impl_20260928/` (H1M3 interpretation runner + 9 recomputation gates + errata file) · `obligrun_20260928/` (obligation-run four-piece set + 99 three-seat ballots + RULING_1 + PREREG addendum + ballot sheet v2.1 + VERDICT v2; the 3 hidden completion-marker files not taken, per the 09-28 hidden-file precedent) · `mouse_ext_precheck_20260928/` (zero-download precheck approval-request list + SHA_MANIFEST) · `rag_fix3_20260928/` (interpretation-matrix preregistration + four mechanical checks + three-gate ledger + the recomputation evidence surface of the 93 OA source XMLs, taken in full; the 12MB raw fetch cache excluded, see appendix A) · `repo_sync3_20260928/` (masked version of this document's task brief + eight-gate scripts/evidence + REPOSYNC3_COMPLETED.md + S9_SCREENING.md)
  - Recomputation for each card = enter that task's `scripts/`; input pointers are in the header notes of its PREREG/NOTE; numeric evidence surfaces (tsv/json/jsonl) carry no numeric changes whatsoever.
- **Hash-anchor exceptions**: `btest/BTEST_PREREG_v1.0.md.sha256` anchors the live original (sanitization inside the mirror makes `sha256sum -c` expected FAIL); see the "frozen hash-anchor exception register" in the sanitization report. Same-type exceptions from the 09-28 waves, registered file by file = `docs/DESENS_SCAN_REPORT_REPOSYNC2_20260928.md` (key files: the RETRAIN_VERDICT.md line of `retrain_assess_20260928/ledgers/SHA_SELF_20260928.txt`; the lines in the SHA_DELIVERABLES of the `kb_chain_audit_20260928` and `rag_fix2_v25_20260928` cards that point at sanitized-renamed files / text surfaces; the `rag_fix_20260928` card's ledger body itself contains channel wording and was sanitized; additionally, the drift between `rag_gap_20260928/REPORT_RAGGAP.md` and the live ledger itself is covered in the open-items section of the closeout file).

## 5. Reconciliation tables (mirror ↔ live)

`docs/recon/RECON_kb_mcp_20260927.tsv`: kb/ 100 files + mcp_server 4 files, per-file sha256 against the live manifest — **104/104 MATCH** (at the 09-27 REPOSYNC point in time); clients/scripts/evals/figures aggregated IDENTICAL across the four directories (appendix sheet of the same table). Documentation/interpretation-layer mirrors are sanitized copies and are not reconciled byte-for-byte (difference = label replacement; per-file hit statistics in the sanitization report).

- **09-28 REPOSYNC2 new table**: `docs/recon/RECON_kb_mcp_reposync2_20260928.tsv` (kb/ 104 + mcp_server 4 = 108 files, incl. this wave's 2 new INERT sidecars and the pointer's v2.4/v2.4.1 blocks): **103 MATCH + 4 DESSENS-VERIFIED (mirror = sanitization(live), verifiable byte-for-byte: two k9 json files + the server/core code) + 1 PRIOR_DESENS (softflags.py c4a8f53, comment-level sanitization, maintainer-confirmed; the repo sha is exactly identical character-for-character to the 09-28 table)**; MISMATCH = 0.
- **09-28 REPOSYNC3 new table**: `docs/recon/RECON_kb_mcp_reposync3_20260928.tsv` (kb/ 104 + mcp_server 5 = 109 files, incl. this wave's new kbgov_vocab.json.gz data asset and the pointer v2.4.2 block): **104 MATCH + 4 DESSENS-VERIFIED (two k9 json files + the server/core code = B5 increments layered onto the sanitized surface; repo file == sanitization_v4(live), verifiable byte-for-byte) + 1 PRIOR_DESENS**; MISMATCH = 0; the strong assertions on the four registered shas all pass (a9072609/b832a694/10da875a/9b504a2e). Rule source = sanitizer v4 (v3 + adjudicator-name CJK adjacency-boundary hardening, implementing the REPOSYNC2 §6-2 recommendation).
- **Intake ledgers**: `docs/recon/REPOSYNC2_INTAKE.sha256` (eight annotation-evidence reports, 767 files + this document's BRIEF) · `docs/recon/REPOSYNC3_INTAKE.sha256` (addenda five/six, 379 files = five cards + this document + protocol v1.3 + vocab + pointer + two substantively drifted wiki files + two mcp files; rerunning `sha256sum -c` is consistent).

## Discipline redlines (invariants)

1. **No evidence-service output in scoring** (redline-rewrite v2 clause): any classifier/model scoring pipeline is forbidden to consume this service's output to generate scores; `soft_flags.notes` is an optional re-review cue only.
2. **Local stdio; no network ports.**
3. **Copy, never move**: zero changes to upstream OcularKB; read-only references.
4. All citations carry a PMID for traceability; annotation products default = draft pending PI confirmation (human-in-the-loop).
5. Interpretation-layer use must go through ANNOTATION_PROTOCOL (freeze first, then compare); baseline/disease entries = identity reference + background contrast + QC flag, **never a composition pass-line**.

---

## Appendix A — Large tables not mirrored, and how to regenerate them

| Surface | Size | Content | Regeneration |
|---|---|---|---|
| `EyeKB/plans/panel_pmid_20260927/ledgers/raw/` | 111MB / 280 files | raw PubMed efetch response cache | run `docs/plans/panel_pmid_20260927/scripts/` (efetch fetch scripts); input = the in-repo PMID list tsv (shas in the same card's ledgers/*.tsv ledger rows) |
| `EyeKB/plans/panel_pmid_20260927/batch2/ledgers/raw2/` | 59MB / 103 files | second-pass efetch cache | same via `batch2/scripts/` (PME2 batch) |
| `EyeKB/plans/evalset/` (outside the repo) | 21GB class | frozen exam set (incl. h5ad / per-cell prediction tables) | **never enters the repo** (patient/project-derived-data redline); recovery requires OcularKB working-disk access |
| `EyeKB/plans/kbx_lacrimal_20260928/out/kbx_clustered_organoid.h5ad` + `kbx_clustered_tissue.h5ad` | 105MB + 53MB | KBX lacrimal cluster-level h5ad (expression-layer derived assets) | run `docs/plans/kbx_lacrimal_20260928/scripts/kbx_p2_cluster_score.py`; input = `GSE164403/GSE164403_annotated.h5ad` (sha 5e6d753d…, OcularKB working disk, not in the repo); parameter family frozen in `KBX_PREREG_v2.md` (seed random_state=20260928, scanpy 1.12.2, leiden flavor=igraph res=1.0); ledgers = the same card's `ledgers/KBX_CLUSTER_TABLE*` and `out/KBX_LG_CROSSWALK.tsv` |
| `EyeKB/plans/rag_fix_20260928/work/chunks_ra_raw.jsonl` | 9.0MB | raw fetch cache of RAGFIX tier-A 64 papers | run `docs/plans/rag_fix_20260928/scripts/ra_fetch.py` (closed set = `out/closed_set_pmids.txt`, 64 PMIDs; endpoints and retries in the script header; input list = in-repo `docs/plans/rag_gap_20260928/TIER_A_approval_list.md`); output reconciliation = the same card's `work/ra_fetch.log` + `work/ra_availability.tsv` (in the repo) |
| `OcularKB-side v2.4 / v2.4.1 main libraries` | 1.02GB / 1.03GB | RAG incremental main libraries (MCP/stage3 unswitched) | not in the repo (default ruling of the two registration documents + large-file discipline); rebuild path = Release v2.3 base + per-card `scripts/` incremental chain (`docs/plans/rag_fix_20260928/`, `rag_fix2_v25_20260928/`); library state and sha ledgers are authoritative in the per-block manifest rows of `kb/literature_db/EYEKB_DB_POINTER.yaml` |
| `OcularKB-side v2.4.2 main library` | 1.076GB | RAG incremental main library: v2.4.1 fully inherited + ra3 103 papers / 11,221 chunks (MCP/stage3 unswitched) | not in the repo (default ruling of the registration document + large-file discipline; rag_snapshots, per the standing default, does not take the v2.4.x metadata three-file set); rebuild path = Release v2.3 base + the `rag_fix_20260928`→`rag_fix2_v25_20260928`→`rag_fix3_20260928` incremental chain (`ra3_scan.py` closed-set determination + `ra3_fetch.py` OA download [zero off-list, zero paywalled; list = in-repo `work/ra3_availability.tsv`] + `ra3_merge.py`); library state is authoritative in the pointer's v2.4.2-block manifest row |
| `EyeKB/plans/rag_fix3_20260928/work/chunks_ra3_raw.jsonl` | 12MB | raw fetch cache of RA3 103 papers (rule: anything >10MB gets questioned first) | run `docs/plans/rag_fix3_20260928/scripts/ra3_fetch.py` (input = in-repo `work/ra3_selected.jsonl` closed set of 103 PMIDs; reconciliation = `work/ra3_fetch.log` + `work/ra3_bytes.json` + `work/xml3/` — the 93 source XMLs are in the repo) |

Cache surfaces already mirrored (small volume, audit value outweighs size): `e2r/ledgers/api/` 3.6MB, `panel_pmid/ledgers/raw_uniprot/` 0.57MB, `kb9/ledgers/epmc_raw*`, `ols_evidence_kb9/` <1MB.

- SEURATPROBE data files (on the `/mnt/D` side, `plans/seurat_probe_20260928/data/`, mtx/rds totaling ~4.6GB; >50MB not taken): regeneration = in-repo `docs/plans/seurat_probe_20260928/scripts/export_counts.py` + `export_ds1_sub.py` + `export_ds2_fix.py` (exported from the registry standard set; the on-disk source files stay machine-side); size anchors = the SIZE-ONLY / DATA-EXCLUDED lines of the in-repo `MANIFEST_SEURATPROBE.sha256` and `out/t0_large_files_excluded.tsv` (REPOSYNC5 registration).

## Appendix B — Sanitization and mirroring policy

- Rule triples = the current project-github-export skill list (channel-vendor names → LLM_CHANNEL; adjudicator names → REVIEWER_LLM; IM platform → MSG_PLATFORM; agent roles → AGENT_ROLE; hostnames → HOST; ports → PORT (prose-type files only); secret shapes → REDACTED_SECRET (catch-all, measured zero hits); third-party author emails → CONTACT_EMAIL).
- Filename + content double scan; 21 renames + 1 directory; second scan after replacement, zero hits (idempotent).
- From 09-28 REPOSYNC3 the rule source upgraded to sanitizer v4 (v3 retained verbatim + one adjudicator-name CJK adjacency-boundary hardening — closing the REPOSYNC2 §6-2 known blind spot); idempotent on existing repo files (proof of zero extra changes = the 2 hit files are both from this wave's new intake). Addendum six also added the T7 permanent gate = an eight-category own-identifier token scan (needles assembled entirely at runtime; the normative texts and the scanner's own source carry zero literals, i.e. no self-matching).
- Some sentences read stiffly because of the labels — this repo sacrifices readability for safety (the PI's informed choice); for close in-group reading, use the working-disk originals.

## Maintenance

- Re-sync checklist for the next structural change = the final section of `docs/REPOSYNC_NOTE_20260927.md` (for inheritance by future closeout documents).
- This README and the mirror were produced by the 2026-09-27 REPOSYNC (task brief `docs/plans/repo_sync_20260927/BRIEF_REPOSYNC.md`).
