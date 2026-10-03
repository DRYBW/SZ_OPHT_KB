# USER_DIRECTIVE_20260928_eyekb_improve_wave — EyeKB improvement wave (released by PI "keep pushing EyeKB forward")

PI instruction: keep pushing eyekb forward (2026-09-28). The PI has explicitly stated that the three items — KB9 registration approval, the obligation run, and the full B A/B — are "no hurry"; this wave is **entirely offline/candidate/analytical in nature: zero registration, zero wiring, zero activation**, and does not move the above three items.

| # | Card | Nature | Why worth doing |
|---|---|---|---|
| D13 | KBX lacrimal efficacy first exam | build the exam paper + first test (the **first formal run** of ballot rules v2 C2b) | the lacrimal entries were finished but never had an exam paper (the root cause of the A3 logged item); the exam paper = the on-disk GSE164403 author labels, zero downloads |
| D14 | KB-GOV cross-species ranking governance candidate | library-side defuse design + mechanical A/B at the evidence layer | BTEST nailed the lesion (mouse-cluster AC/RGC artifact flowing back, Calb1/Grin3a false hits); only a library-side fix leaves form B any chance of revival |
| D15 | PME3 residual 44 keys, triple sweep + storage-repair plan | data-engineering wrap-up | after two batches, 44 weak/none remain; E2R found the structural defect that pmid_context never stores the PMID — a repair design is owed |
| D16 | GRADE grading-order drift-anchor analysis | ballot counterfactual + protocol candidate | the BTEST Q5b::35-type case of "the correct name discarded by grade drift"; seat grade discipline is the weakest link in the voting chain |

Discipline: each card's artifacts land in its own plans/ directory; kb/, mcp_server/, evalset, and the production scoring chain stay read-only throughout with a sha record table; the pre-registration sha goes on paper first; LLM ballots are used only in D13 (LLM_CHANNEL, three seats with identical parameters, cap 120 ballots, exceed → block); D14/D15/D16 are zero-LLM. All "register/wire/activate/implement" actions = candidate package + awaiting the PI; nothing of the sort executes in this wave.

## Supplement 1 (2026-09-27 evening; PI "fine — for missing literature add literature, for missing rag fill rag, for missing wiki fill wiki")
PI approvals: ① execute the KB9 registration (case B: write the versioned overlay into kb/, register the routing but **default OFF, not activated** — activation still requires the §10-6 obligation run + separate PI approval; the PI has explicitly deferred the obligation run / full B); ② the three-layer gaps are released under "if missing, fill", but **for filling RAG, first produce a zero-download gap inventory, then seek approval per that list** (prevents blindly rebuilding to burn compute / triggering a big download).
- D17 KB9REG-EXEC: put case B's four entries + rules into a kb/ sidecar overlay (baseline bytes untouched, copy not move); route registered, default OFF; also backfill the new entries' companion literature chains / knowledge-base pages / retrieval-index entries (making "add literature + add wiki" real).
- D18 RAG-GAP: whole-corpus RAG coverage-gap inventory (zero downloads); produce the approval list of "which primary literatures are missing, at what volume, which tiers to refill"; actual rebuild/download awaits the PI approving per the list.
- "Add literature": PME3 is running (44-key triple sweep); the KB9 new entries' literature chains are folded into D17.

## Supplement 3 (2026-09-28; PI: "fine, as long as it runs on this machine" + "after you're done, check whether a retrain is needed, then update github")
- D20 KBCHAIN whole-library citation-chain misquotation audit = GO (RAGFIX's 20-paper sample confirmed 6 = 30%, triggering full scoping; the blocked question P2 is settled here).
- D21 RAGFIX2 gate-③ supplementary round = GO (reassembly of the 16 "list-never-had-text" genes via whitelist + v2.4.1 + recompute; the 8 covered only by backup candidates are not touched — that belongs to the separate "approve the 104 backup batch" case).
- D22 RETRAIN impact assessment = GO (four objects: v2_prod / mouse edition / RAG embeddings / panel-derived artifacts; read-only, zero retraining; answer the PI's "retrain or not" with an object-by-object reconciliation rather than a feeling).
- D23 GitHub = queue item: after D20/D21/D22 are in and the project maintainer has re-reviewed the whole chain, do the **second round of repo sync** (overlay / credential-revocation notes / v2.4.1 index ledger / audit and assessment artifacts / README version notes); reuse the test gate (tested green before push); whether the Release assets move to v2.4.x depends on corpus state — the sync card evaluates and reports separately.
- KBX status sync: done (the O3 downgrade = the exam paper is invalid, not the entries judged losers; the lacrimal quantitative first exam stays logged as "awaiting new data"). RAGFIX: done (v2.4 staged, not activated; gate ③ FAIL recorded as-is; the REVIEWER_LLM independent ruling points the same way).

## Supplement 4 (2026-09-28; PI "approved")
The PI's reply to the single "awaiting your approval" item on the 11:25 status board is **approved** = **release to start the §10-6 obligation run** (prerequisite for KB9 k9_ocs activation):
- Execute OB-1..OB-4 (AV2-5(c) historical ON-state gate reconciliation / A07 pre_vote_diagnostics first run / Arm1-Arm2 ranking-consistency supplementary check over the 22 retina clusters / lit same-source exclusion screening archived) + the formal three-seat ballot run on the KB9 surface (ballot rules v2 C2b declared in the pre-registration; gate P1>=24/33 not lowered; P2 regression protection per the registration-package caliber).
- **This approval does not include activation**: the OB-5 permanent gate stands — after the obligation run + all gates pass and the ACTIVATION_READINESS report is produced, the activation switch remains the PI's separate approval; this run is zero-wiring, zero-activation, zero default switching; kb/, mcp_server/, evalset read-only.
- LLM ballots = LLM_CHANNEL three seats with identical parameters (enable_thinking:false), cap 150 ballots, exceed → block; the historical C4 P1=22/33 FAIL record is not rewritten (the C2b effective-going-forward regime).
- Task brief = <EYEKB>/plans/obligrun_20260928/BRIEF_OBLIGRUN.md; the execution card is recorded separately.

## Supplement 5 (2026-09-28; PI whole-chain authorization: "except downloads over 1G that need my approval, everything else just push forward")
From this supplement on, the project maintainer proceeds autonomously and settles the books afterwards. **Only two classes of gates still need the PI's explicit call**: ① >1GB downloads (approval list, line by line with volumes); ② the named permanent gates the PI has already stated (e.g. OB-5: KB9/v2.4.1 production activation = separate approval).
- **Proceed immediately**: RAGFIX3-104-backup-batch (v2.4.2 increment, zero-download or MB-scale) / mouse heavy-tier external-set zero-download precheck + approval list (for the PI to tick rows).
- **Auto-continue after OBLIGRUN completes (territory avoidance)**: KBGOV-B5 implementation (sink cross-species ranking governance to the library side; pass the test gate + rollbackable + re-verify zero displacement on the human side) / GRADE-H1M3 implementation (seat grade discipline; the flipped-correct-7 / new-errors-0 caliber) — both cards landing = wiring-level fixes, with regression gates and observation clauses; activation-class actions reported separately.
- **De-prioritized, not dropped**: the full B-form A/B (the PI once said "no hurry" → queued after the above implementations; ballot-budget caps follow the block regime).
- The mouse mid tier was already built on 09-25 (t_917f8709, the v2 revision on record); the board's "mouse edition awaiting the call" was a stale entry and is corrected.

## Supplement 6 (2026-09-28; PI red line on sensitive data entering the repo, long-term effective)
PI order: **no in-house data of any kind enters the SZ_OPHT_KB repo**, derivative results included. Named exclusions: OWN_MOUSE_DR_DATASET mouse data, vitreous protein/metabolism (the vitreous proteomics project series), the [comorbidity-project codename] cell-attribution line, [stage codename]/T-ATLAS patient-derived readings, patient sample numbers. **Binding on all subsequent repo-sync cards (REPOSYNC3 onward) and RAGFIX/audit cards**:
- Before inclusion, pass the "in-house data token scan" ([sample-number prefix]/[project-number prefix]/[drug name]/[comorbidity-project codename]/[stage codename]/[internal field name]/patient sample number); a hit means exclusion — do not desensitize-and-include (distinct from generic public-literature terms at the STZ/FLT1/DR2 level — those are public literature/KB content, not this project's patient data, and may stay).
- Repo character = a four-layer mirror of public datasets + public literature + system code/knowledge base/evaluation; **the sources and patient/animal in-house data stay physically isolated**; the OcularKB master library (v2.4/v2.4.x, 1GB-class) does not enter the repo — only metadata + kernel + bibliography (Release channel discussed separately).
- The current main=ea40bea was personally token-verified line by line by the project maintainer: 0 hits on the above sensitive items, compliant. This becomes a new push-precondition gate for every future sync/audit card.

## Supplement 7 (late night 2026-09-28; PI decisions: Seurat dual-track probe + drsc five disciplines codified)

### A. SEURATPROBE (PI as-is: "fine, but why do you keep staring at GSE165784/GSE160306? We have plenty of already-annotated standard datasets — what's the point of these two un-annotated ones?" + "you can add conditional logic — if the machine can't support seurat, just take the other path; use your judgment")
- **Data-plane caliber correction (a long-term rule effective immediately)**: for any "engine-comparison / methodology-probe" task, the ground-truth reference is **the per-cell author-level-annotated standard datasets in <STORE>/registry** (after the runner script's Phase-0 measures the obs columns + value distributions, pick ≥2, adult ocular tissue, ≤200k cells per set); **it is forbidden to use our own consensus annotation (the GSE165784 demo etc.) as the answer** — that is validating our own reading with our own reading; circular.
- **Approach decided = dual-track parallel + agreement auto-passes + disagreements go to the PI** (the project maintainer's recommended option among the three proposals got the PI's "fine"); no "system self-selects the engine" (single-ticket-ization was rejected).
- **Downgrade clause (pre-registered reading)**: install Seurat+SingleR in a new conda environment (don't touch system R; R package downloads expected ≤1GB — if measured >1GB, stop the card and seek approval); only if the 20k-cell pilot holds RSS≤20G and a single chain ≤15min does the full-scale probe GO; any criterion missed → NO-GO closure, the incumbent scanpy single track stands unchanged, and the NO-GO numbers land on disk as-is.
- The probe produces three numbers: cross-engine per-cell agreement (ARI/NMI + confusion matrix) / the SingleR re-decision list versus the existing surface, with per-item literature support / the disagreement-cluster list + a second-vote-promotion GO-NO-GO recommendation (a recommendation only, no decision made on anyone's behalf).

### B. drsc five disciplines codified (PI as-is "make sure it lands"; adopting the project maintainer's reading "good results = good discipline")
- **D-1 composition prior enters the gate** -> build the EXPECTED_COMPOSITION_v0 new surface (per-cell-type proportion ranges for the normal adult eye, one PMID per row, derived only from the registry record tables / literature index; deriving from our own clustering is forbidden; default OFF, no wiring; the self-check only emits a flag list): card DISC-COMP.
- **D-2 donor-level adjudication + D-3 depth/complexity controls** -> first the read-only quantification: over the 99 ballots on the frozen ballot surface and the existing exam sets, replay the leave-one-donor-out rejection leverage + measure top_genes displacement under depth-matched sampling; produce the "how many would be flagged if the two gates went live" checkbox sheet + recommended threshold tiers: card DISC-QANT. Gates not lowered, protocol unchanged, thresholds await the PI's tick.
- **D-4 dual-track discipline formalized (effective immediately from this directive, applies going forward)**: for any vocabulary-library/RAG-library-surface change, the efficacy readout must pass the "no-prior A vs with-prior B" dual track; **improvement counts only on the designed targets, not across the board**; negative readings such as empty rates / coverage displacement are listed as-is. Prior iterations are not retroactively judged.
- **D-5 narrowing first**: keep the status quo and codify it — every card's pre-registered primary test is unique, and no amount of iteration merges primary tests.
- Territories: three mutually exclusive directories (seurat_probe/drsc_disc_quant/comp_prior, one layer each), all CPU, systemd-run MemoryMax-managed, heartbeats carrying available, zero touch on the kb/mcp_server/evalset frozen surfaces (DISC-COMP only creates the kb/composition/ directory; no existing file is touched).

## Supplement 8 (early hours 2026-09-29): the PI's standing autonomous-progression order

PI as-is: **"watch it closely, keep it spinning; don't make me keep nodding — push it forward yourself"**. Character = a **standing rule**, distinct from per-iteration authorization; effective long-term until the PI withdraws it.

**Retained gates (still require the PI personally; everything else is autonomous + booked afterwards)**:
1. >1GB downloads, line-by-line approval (the existing iron rule unchanged)
2. PI-personal items: QANT threshold-tier ticks; any "activation/wiring switch" (k9_ocs, v2.4.x default switching, putting the composition surface live); demo/paper-body-text class
3. GitHub push/Release class, i.e. externally irreversible actions: ride along when an authorization window opens; **do not request a device-code scan just for pure bookkeeping commits**

**Pre-authorized by this very section (launch per list, no further asking)**:
- SEURATPROBE completes → project-maintainer acceptance (verify the probe's numbers + read the downgrade clause) → book it; the "second-vote promotion" recommendation part goes to the PI; the rest auto-continues
- SEURATPROBE completes and load drops below <40 → auto-dispatch **COMPV1** (composition-prior layering v1, treating the DISC_COMP reverse quality-check obligations OB-1/OB-2/OB-3; zero downloads, v0 frozen artifacts untouched, new directory versioned, wiring stays OFF, activation still the PI's)
- The unpushed local commit (1febfee, Release receipt) pushes automatically at the next authorization window
- The already-scheduled crons (A2 ballot-tracking weekly 10-03; B5 false-rejection review 10-05) fire as usual; do not disturb the PI unless an anomaly appears


> [Repo-surface note] In this file, literal own-identifier tokens have been masked per the T7 permanent gate (categories = sample-number form / project-number form / Chinese drug names / comorbidity-project codename / project English name / stage codename / internal field names / patient sample IDs). The online originals stay on the machine side; the per-file ledger = docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv. This note is a sync-card disposition trail and does not alter the normative meaning of the PI's clauses.
