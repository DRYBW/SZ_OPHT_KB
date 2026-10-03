# Key Findings (read this first)

> Summary of red lines and frozen rulings. Mandatory reading for any session/agent taking over. Updates sync with the decision log.

## 1. RAG positioning (Claude5 frozen ruling established 2026-08-12; rewritten by PI decision 2026-09-26 as the "evidence-consumption discipline v2")

- RAG = **human-in-the-loop auxiliary citation module**: after annotation completes, attach literature evidence + PMIDs
- **Evidence-consumption discipline v2** (PI decision 2026-09-26, replacing the old "banned from scoring" clause; details in USER_DIRECTIVE_20260926_redline_rewrite.md): ① using RAG/MCP literature evidence on the annotation/independent-reading side = legitimate and the core of the system design; ② the scoring/adjudication side (ground-truth matching, hit rate, consensus adjudication, any automated scoring/confidence weighting/composite QC score) is **banned from consuming evidence sourced from the reading side**; ③ if an automated-scoring stack (GBDT/LLM-judge) is ever introduced, ② is the precondition red line and evidence features require separate PI approval
- Derived wording red line: coverage reports state facts about library content only; never write "improved annotation capability / more accurate scoring"

## 2. Annotation-engine applicability (frozen statement v1.2, APPLICABILITY_STATEMENT.md)

- **Species: human only** (cross-species testing is impossible — measured human/mouse HVG overlap 2/2000; GSE243413 ruled N/A)
- **Development stage: adult only** (fetal/immature cells get force-assigned to AC/MG; measured PRPC/NRPC misassigned 94%)
- **Development-axis separation red line (PI decision 2026-09-23)**: fetal/developing-stage and adult material **must not share entries even for the same tissue** — baselines/matrices/evaluation sets/RAG labels all carry development_stage as a first-class axis; fetal sets are always OOD_strict at the evaluation layer; fetal reference candidates (GSE268630 etc.) are held separately pending a future fetal pipeline. See /mnt/D/EyeKB/plans/USER_DIRECTIVE_20260923_dev_axis_separation.md
- Non-human species, fetal samples = sample-level OOD, must be judged from metadata; the engine does not backstop this itself
- Mouse model: **not built** (GSE243413 reference on disk; whether to build awaits the PI decision — see CURRENT_STATUS.md)

## 3. RAG v2.0 coverage facts (built 2026-09-23)

- 11 eye-tissue classes, multi-label: retina / cornea / conjunctiva / sclera / trabecular_meshwork / iris / ciliary_body / lens / optic_nerve / RPE / choroid
- 2,713 papers / 174,616 chunks; species distribution human 97,521 / mouse 37,625 / both 25,956 / other+unknown 13,514
- Three-dimensional retrieval filters live: `--species` + `--tissue` + cell_type_mentioned (script stage3_retrieve.py; the default library remains v1.0 so old invocations are unchanged)
- Known weak-coverage subtypes (QA ⚠️ flagged as-is, no padding): Schlemm's canal endothelium, scleral cartilage/smooth muscle, lens fiber/epithelium, iris smooth muscle, conjunctival epithelium, ONH-RGC etc. (full list in literature_db/v2.0_2026-09/QA_V2.md)
- Thin-tissue exemption records: sclera/iris year window relaxed to 2015+, impact factor downgraded to priority (traced in manifest.yaml — not a silent relaxation)

## 4. Marker data-retrieval discipline (skill: celltype-marker-knowledge-base, distilled 2026-08-22)

- **Check local knowledge bases for markers first (MarkerBase / curated marker JSON / local author-annotated reference atlases) before ever considering the web; never in reverse** (PI as-is: "these markers should already be in our knowledge base — don't search the web")
- Splitting merged labels (e.g. Macroglia → Müller/Astro): use local already-separated reference atlases for pairwise DE; one-vs-rest markers are unusable for similar classes
- Scoring combinations must **verify the separation direction within the source** (the AQP4 reversed-direction trap); mixed-phenotype rollups must stratify per-source (the GSE196235 Astro≈MG semantic-drift trap)
- When porting panels across species, always check: species specificity (the SNCG fish pan-expression 91.9% trap) + ortholog aliases (fish ohnolog double copies) + gene_name capitalization (lowercase in fish)

## 5. Engine and model status (updated 2026-09-24: v2_prod decision completed)

- v2_prod (10-class LR-HVG2000): **switched to the production default on 2026-09-16** (SWITCH_RECORD acceptance drift 0.02pp); after KB2's same-exam round showed it beating G1 on all three true external datasets (+5.1/+16.6/+12.2pp, all CIs exclude 0), the **PI decided to keep it** (USER_DIRECTIVE_20260924_v2prod_maintain.md); G1 retained via the `--model g1` fallback
- Its 8-fold CV 0.9885 **must not be used as evidence of model capability or as a paper headline** due to data saturation (2026-09-18 CEILING backfill ruling)
- scANVI: stage-D fair comparison 4/4 losses; stay with LR. The FM-channel (scGPT) plan passed review but the PI decided not to start it before M2

## 6. Development-axis red line (PI instruction 2026-09-23/24 consolidated, KB2c+KB3, never lifted)

- **Development-stage data is always held separately; at no tissue level do adult/fetal serve as each other's reference** (PI as-is: "the fetal ones and the adult ones are not comparable, even when it's one tissue").
- Execution status (KB3 t_5425a7ca, 2026-09-24): all 11 adult entries in kb/baselines carry the required `development_stage` field + reference-distribution bans; the first development-stage entry with real data, `retina__fetal_developing` (GSE268630 portal 226,506 cells + GSE138002 author-labeled fetal layer 88,013; schema `eyekb-baseline-development/1.0`, **invisible to adult MCP queries**; the ban on answering fetal questions from adult buckets unchanged); the disease matrix gained a `development_axis` column + a reserved ROP cell; RAG papers-level `dev_stage` sidecar (v2.2, 3,696 rows, title+abstract regex + manual spot-check of 30 papers) + `stage3_retrieve_v3.py --dev-stage` optional filter (default = old behavior unchanged).
- The engine-applicability statement is untouched: fetal is OOD to begin with (E4/E5 = OOD_strict); this clause additionally separates the **knowledge layer** = belt and braces.
- Prohibited: mapping developmental vocabulary such as PRPC/NRPC/RPCs into the adult 10 classes; backfilling developmental numbers into any adult entry; putting fetal/organoid material into adult disease cells.
- 2026-09-27 final scoring-line caliber: E1/E2 = Evidence-into-scoring adjudicated W2, offline audit only (abstention recall, limited to the retina surface; AUDIT_SOP_v1.0 finalized, zero wiring); red line ②'s operational definition is settled (the reading/evidence-gathering side may use label-derived rules but must carry a "development-set self-check" qualifier; the scoring/adjudication side may not — see the redline_rewrite addendum); the four-form RAG-for-single-cell-annotation verdict = A evidence surface usable / B free query under validation / C scoring banned / D externally corroborated (rag_anno_usability_20260927). Ballot rules v2 = C2b approved, effective going forward (history not rewritten).
