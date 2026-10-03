# MCP-RAG-Wiki-Skill Architecture Review and Roadmap (2026-09-24)

> Maintained by: the project maintainer | Nature: architecture-level current-state snapshot + next-step plan (for the PI to prioritize)
> Basis: the 2026-09-24 full-chain archaeology (taken stock after KB2's two evaluation rounds completed); the upper-layer doctrine lives in skill `knowledge-guided-cell-annotation`.

## 0. The architecture in one sentence

**A four-layer interlocked "ophthalmic single-cell annotation knowledge infrastructure"**: the Skill (reading discipline/protocol) dictates how to read → MCP (tool layer) provides the unified data-retrieval interface → RAG (literature evidence layer) supplies evidence + PMIDs → Wiki (project hub) stores conclusions and decisions. Production annotation runs human-in-loop (AI draft + PI adjudication); quality is verified by the KB2 double-blind evaluation loop.

```
[PI clinical adjudication]  ← the apex of the human-in-loop circle (ground truth sits with the PI)
     ↕
[Skill] reading protocol: two-dimensional doctrine / three gates / vocabulary / development-axis red lines
     ↕
[MCP] eyekb 5 tools: query_marker / search_literature / get_tissue_composition
                / get_disease_prior / get_kb_page   (stdio, golden regression 41/41)
     ↕                    ↘
[RAG] literature evidence     [knowledge entries] kb/baselines (11 tissues + development axis) + kb/markers
  v2.1→v2.2 switched to default 09-24 (220,571 ch)   + preprint axis (filterable) / QA per marker with PMID
  (v2.2 = D0 anchor-literature targeted channel; switch evidence SWITCH_V22_RECORD.md)   + disease matrix (PDR first cell + development_axis; keratocyte backfill 09-24 completed)
     ↕
[Wiki] the six-piece core set (INDEX / KEY_FINDINGS / DATA_ASSETS / DECISION_LOG / CURRENT_STATUS / RETRIEVAL_INDEX)
     ↕
[KB2 evaluation loop] double-blind independent reading (RUN1/RUN2 completed) → quantifies reading agreement + automatically exposes KB gaps (already demonstrated: the keratocyte vocabulary gap)
```

## 1. Layer-by-layer current state

### RAG (literature evidence layer)
- **Active v2.2_2026-09 (the retrieval default library, switched 09-24 t_27d3ba2c)**: 220,571 chunks / 3,681 papers; 11 tissues + preprint axis (filterable) + QA per marker with PMID; retrieval stage3_retrieve_v3 supports `--tissue/--preprint/--dev-stage` (default now points at v2.2; golden regression 10/10 no degradation + D0 detectability self-check, evidence scripts/SWITCH_V22_RECORD.md; the MCP search_literature default is still v2.0, switch awaiting decision on a separate card)
- **v2.2_2026-09 (built 09-23 late night)**: full inheritance of v2.1 + the **D0 anchor-literature targeted channel** (7 papers 196 chunks, per-paper exception registered; incl. the GSE165784 original abstract-only) + a `full_text_available` column
- papers-level dev_stage sidecar (3,696 rows, regex + manual spot check of 30)
- **Gaps**: ① ~~v2.2 not wired as the retrieval default library~~ (✅ 09-24 t_27d3ba2c: the ocularkb retrieval script default has switched to v2.2, the GSE165784 original main anchor is measured detectable at rank-1; the MCP-side default switch awaits the user's decision) ② the RAG master papers table has no organism_stage column (currently bridged by the sidecar) ③ the three-field evidence model required by REVIEWER_LLM (inclusion_reason five classes + claim_relation + evidence_context) **not yet implemented** ④ adnexa ingestion pending decision (lacrimal 170 / meibomian 220 / orbital fat 126 / extraocular muscle 46 OA papers)

### MCP (tool-service layer)
- All 5 tools in place; get_tissue_composition already carries development_stage (adult main entries / adult_pool controls / fetal transition-state concept entries, KB2c caliber); golden regression 41/41; stdio opens no port (red line maintained)
- **Gaps**: ① query_marker does not recognize ENSG (demonstrated this round; the collector-side dual columns are fixed; the tool side keeps the current design "callers pass symbols", spelled out in the docstring) ② search_literature's dev-stage filter depends on the RAG sidecar and is not passed through inside the tool ③ the disease-state / membrane-class marker panels are still thin (the PDR membrane demo proved 0 coverage in the healthy library; backfill in progress)

### Wiki (project hub)
- The six-piece core set runs normally; CURRENT_STATUS / KEY_FINDINGS updated today (stale items in the engine-status section fixed: the v2_prod keep-decision booked)
- **Gap**: DECISION_LOG.md does not yet include today's three decisions (v2_prod keep / dual-column schema / keratocyte backfill) — to be added

### Skill (procedural knowledge)
- `knowledge-guided-cell-annotation` (the main skill of the reading system): doctrine + three-layer knowledge entries + REVIEWER_LLM adjudication + development-axis red lines + double-blind evaluation operations + pitfalls; the KB2 defect cycle has been added to references — **in sync with the actual system**
- `celltype-marker-knowledge-base` (marker data-retrieval discipline, 2026-08-22, another profile): no cross-references with the main skill
- **Gaps**: the main skill's instance-assets section has not been updated with the RUN1/RUN2 evaluation results; the relationship between the two skills is undeclared

## 2. Cross-layer break points (sorted by harm)

### Addendum 2026-09-28 (t_4bb75b26 KB9REG-EXEC): current state of the marker-entry library layer (lacrimal / ocular-surface new-entry status)
| Library | Content | Status |
|---|---|---|
| retina_v6 + face_v6 | KB7 repaired panels (retina 10 classes + ocular-surface stroma) | **activated** (ACT t_5d5853c9 09-26, included in the default all; env-rollbackable) |
| lacrimal_v6 | KB8 lacrimal 3 entries (secretory / duct / myoepithelial warning) | **registered default OFF** (PI A3 not switched for now — the lacrimal efficacy first exam KBX is running; revisit once numbers are in) |
| **k9_ocs** | **KB9 case B, 4 new ocular-surface entries** (Melanocyte/Schwann/Conj_suprabasal/Limbus_Sclera_fib_C1; closes the structural zero-entry gap on the ocular surface) | **registered default OFF** (PI D17 09-28 approved registration; before activation the §10-6 obligation run is required: AV2-5(c) historical ON gate + A07 diagnostics-table first run + 22-retina-cluster consistency re-check + lit same-source exclusion archive, plus separate PI approval) |
| Companions for the new ocular-surface entries | block/applicability rules + assembly rules v2 sidecar `_k9_ocs_rules_overlay_v1.json` (inert data file, not loaded at runtime) | registered in the store; consumption surface = evaluation/reading runs read the files directly |

| # | Break point | Harm | Fix |
|---|---|---|---|
| 1 | The three-field evidence model is not implemented | "auditable evidence" is the project mainline set by REVIEWER_LLM; entries currently carry only PMIDs, no claim-level relations (supporting/refuting/qualifying) | Start with per-claim verification of the D0 key assertions; a whole-library rollout is prohibited |
| 2 | ~~RAG v2.2 not wired~~ (✅ 09-24 t_27d3ba2c: retrieval-script default switched + regression self-check PASS; the MCP default switch awaits decision on a separate card) | Evaluations/demos citing D0 anchor literature (the GSE165784 original) cannot retrieve it | Switch the retrieval default library to v2.2 + golden-regression self-check |
| 3 | The last mile of human-in-loop is not walked | demos stop at the draft; the "PI confirms → writes back to obs → diff table" finalization loop has not been walked on a real sample | Take the PDR membrane demo v2 through one cycle (about 30 minutes of PI participation) |
| 4 | The organism_stage master column has not entered RAG | the sidecar is a bridge; cross-library queries fork | add the column at the next rebuild (decision first) |
| 5 | The two skills are unrelated | future sessions may load only one of them | add cross-references to both (minutes-level) |
| 6 | The disease-state marker panel is thin | local hit rates are low on PDR membrane-class samples | roll it out alongside the disease spectrum (the doctrine already has this route; avoid one big-bang effort) |

## 3. Next-step plan

### P0 (mechanical, dispatchable immediately)
1. ~~The KEY_FINDINGS engine section is stale~~ (✅ fixed today)
2. Switch the RAG retrieval default library to v2.2 + 41/41 regression self-check (small card) (✅ 09-24 t_27d3ba2c done: stage3_retrieve_v3 default switched to v2.2, golden regression 10/10 under the same caliber with no degradation + the seven D0 papers detectable; evidence scripts/SWITCH_V22_RECORD.md. Note: the MCP search_literature default is still v2.0; switching it is a service-behavior change, awaiting the user's decision on a separate card)
3. Keratocyte backfill card completion acceptance (t_e1febb8e running)
4. Cross-reference declarations for the two skills + add the two evaluation rounds' results to the main skill's instance assets (minutes-level, done directly by the project maintainer)
5. DECISION_LOG.md: add today's three decisions

### P1 (1-2 day scale, suggested for the next wave)
6. **Implement the three-field evidence model**: first verify the key assertions of the seven D0 papers claim by claim (inclusion_reason + claim_relation + evidence_context); talk about scaling only after the template is produced
7. **First walk of the human-in-loop finalization loop**: PDR membrane demo v2 draft → PI confirms/re-rules → write back to obs → v2→v3 diff table (needs about 30 minutes of PI participation)
8. Decide the organism_stage master-column plan (sidecar promoted to master vs keep sidecar + query-layer aggregation)

### P2 (awaiting decisions)
9. Adnexa ingestion of the four tissues (volumes already reported)
10. Mouse annotation model (GSE243413 323K cells on disk; OWN_MOUSE_DR_DATASET benefits directly)
11. RUN3 direction (expand the exam / real human double-blind / change the reader architecture)
12. M1 data-paper assembly (registry/fingerprint library/verification chain ready; workspace/figures/body text missing)

### Explicitly not doing (red lines already in the doctrine)
- Widening the disease layer in one push; human-mouse alignment (on hold); any shortcut other than the fetal bucket answering fetal questions; putting RAG/priors into engine scoring
