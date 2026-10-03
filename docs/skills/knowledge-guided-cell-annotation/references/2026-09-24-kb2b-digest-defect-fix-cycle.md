# KB2b digest silent-defect fix, full cycle (2026-09-24; double-blind evaluation evidence-surface rebuild instance)

## Timeline and defect

1. The KB2 first-round evaluation card t_854ba6e6 produced EV_DIGEST_SLIM.jsonl (45-cluster evidence cards, frozen sha 9e67eb50…), serving as the sole evidence surface for the double-blind readers.
2. The second reader (AGENT_ROLE, card t_0188c99f), while validating the input, found that **40/45 clusters had empty top_genes** (only the five Q9 clusters had values), refused to fabricate "abstentions" on empty evidence, and filed a blocking report — a model of correct behavior.
3. Root cause (its forensics localized the exact line): `kb2_digest2.py`'s `member_clusters()` reads the clustering TSV via pandas, where the `leiden` column is int64 → selected cluster IDs are int; while the group-mean dict keys, having gone through `.astype(str)`, are str. `if c not in gm: out[c]=[]` is always true → **silently returns empty lists, no exception, no log**. The log tail "Q1..Q9 genes done / GENES PART DONE" looked entirely normal — the empty-value path was not inside a FAIL branch.

## Fix cycle (executed by the project maintainer per the blocking report's section-3 proposals)

1. **Version the old artifacts**: the four items `cluster_selection/genes_part/EV_DIGEST_SLIM/script` were copied as `*_r1_defective.*`, and their sha256 appended to `digest/ERRATA_SOURCE_FIX_SHA_LOG.txt` (never silently overwrite in place).
2. **Minimal patch**: only 2 spots — `astype(str)` unification + the fallback `c=str(c)` + a WARN log added to that branch (so this class of defect is never silent again). Executed exactly per the blocking report's proposal, no improvisation.
3. **Environment probe (key new step)**: the first rerun picked pipeline_env (anndata 0.11.4) and died on the Q9 read — the newer h5ad's `/uns/log1p` null encoding has no reader in the old anndata. Correct procedure: enumerate the key library versions of every conda env (`python -c "import anndata; print(version)"`), then do a low-cost backed test-read of **every data source** before launching any long run. Measured: scrnaseq/eyescgpt/r-env (anndata 0.13.2) all pass.
4. **After the rerun, first verify "frozen selection unchanged"**: the fix does not alter the rng consumption order ⇒ same exam. Per member, convert the old and new selections to str and compare lists — accepted only after 9/9 IDENTICAL (changing the engine must not change the questions).
5. **Acceptance line** (line by line per the blocking report): genes_part 45/45 non-empty ✓; the nine members' selection keys all str ✓; SLIM 45/45 non-empty ✓; kb_marker_ranking recomputed (16/45 with hits; low hit counts are themselves information) ✓; log 0 WARN 0 FAIL ✓.
6. **New artifacts' shas logged**, canonical filenames unchanged (downstream references do not rename); defective old artifacts kept permanently.
7. **Reopen the reading slot**: a contaminated reader is never reused (it self-reported that reading the clustering TSV exposed 2 barcode ground truths, plus it had read forensics material) — a fresh clean card (t_7c1630fc) was opened, its task brief carrying the blinding red-line checklist + territory declaration + card-recording discipline.

## Blinding red-line checklist (template elements of a clean annotation-evidence-report task brief)

- Allowed to read: only the digest (specified sha) + the reading instructions file.
- Forbidden to read: clustering/ (contains per-cell truth columns), defs/, engine/, scoring/, result reports, any ERRATA/forensics artifacts, the other reader's artifacts (ANN_A_*), defective old artifacts, the project WIKI.
- External retrieval forbidden (first round has lit as a placeholder; both readers on the identical evidence surface).
- undetermined is a legitimate output; forcing labels just to fill the table is forbidden.
- Output path / row count / cluster_id set correspond one-to-one with the digest; project-maintainer acceptance = counts + set comparison + schema enumeration + spot-check of 3 rows' why against the evidence.

## Human PI reading slot (slot A)

- On the same evidence surface, the "clinical expert vs AI" agreement rate fits the KB's human-in-the-loop positioning better than two AIs judging each other; the PI works through MSG_PLATFORM batch reading packages: each batch = one member's 5 clusters (top genes + KB hits + KB ranking + n_cells), answered in plain language as "identity + grade A/B/C + a one-line basis"; the project maintainer transcribes faithfully to JSONL without editing.
- Slot filenames stay scorer-compatible (kb2_bscore.py hard-codes ANN_A_AGENT_ROLE.jsonl/ANN_B_second.jsonl): when the slot's source person changes, the filename stays and the README/task brief declares the actual reader's identity.
- Before issuing evidence cards, self-check for leakage: no truth, no engine predictions, no second reader's opinions; KB rankings must be labeled "a retrieval by-product, not a confidence score".

## One-sentence lesson

Scripts that auto-assemble "evidence cards for humans/models to read" MUST carry **row-level non-empty assertions** as a frozen pre-acceptance gate; silent nulls plus an all-normal log = the most dangerous defect shape, and reader-side input acceptance (empty values block immediately) is the last line of defense — and the one that actually held.
