# REPOSYNC_NOTE — SZ_OPHT_KB whole-repo alignment to the "cloneable four-layer system" (2026-09-27)

Task brief: `docs/plans/repo_sync_20260927/BRIEF_REPOSYNC.md` (PI's corrected characterization: this repo = a cloneable-run mirror of the four-layer system, not a documentation backup).
Execution used the staging-copy method: the working copy `/home/ubuntu/EYEKB_REPO` first fetched and reconciled against the remote (main level with origin/main, clean) → a job copy `EYEKB_REPO_STAGING_20260927` was built alongside → layered commits and push. The live `/mnt/D/EyeKB` and `/mnt/D/OcularKB` stayed read-only with zero writes throughout.

## 1. Five gap blocks → handling

| # | Gap (evidenced) | Handling |
|---|---|---|
| 1 | `mcp_server/server.py` stuck at KB1v2-**0.3**-kb7wire (live: 0.4-actv6); `eyekb_core.py` behind by 1764B; `calllog.py` (audit-trail layer) missing as a whole file | Three files synced from live (byte-level identical, reconciliation table MATCH); softflags.py was already identical and untouched |
| 2 | `docs/skills` held only 2 mirrors, outdated at 09-26 versions; the interpretation-protocol file ANNOTATION_PROTOCOL and the voting-rules v2 decision document were not mirrored | Both skills fully refreshed (annotation-eval-ops gained the run6b-run7rg efficiency reference, SKILL.md to the 09-27 version; knowledge-guided to the 09-26 22:26 version); new `docs/skills/protocols/`: ANNOTATION_PROTOCOL_v1.1/v1.2 + PROTOCOL_VOTING_v2_C2b.md |
| 3 | WIKI mirror stopped at the evening of 09-26: INDEX / current-state / conclusions-quick-reference missing for the 09-26 late-night → 09-27 range, scoring_wave directive (incl. addenda 1/2), the redline addendum section (operational definitions), PROTOCOL_VOTING_v2_C2b, AUDIT_SOP not mirrored | All 14 files fully refreshed (12 stale updates + 2 additions: scoring_wave/PROTOCOL_VOTING; the redline addendum section entered the repo with the redline_rewrite update; AUDIT_SOP_v1.0's body lives in the E3 card directory and entered with the interpretation layer at `docs/plans/e3_rescue_20260927/AUDIT_SOP_v1.0.md`) |
| 4 | Zero mirror of the 09-27 annotation-evidence reporting layer | `docs/plans/` took 12 card directories, **1439 files / 9.6MB**: evidence_scoring, e2_decontam, e3_rescue, e2r_s5audit, btest, tiep, panel_pmid (+batch2), kb9_ocs, proto_v2, rag_anno_usability, sync_scSOP, repo_sync. Policy = all md/json/tsv interpretation files in + ballot archives annotation/*.jsonl in + scripts/ chains in + small ledgers in; the two big raw fetch-cache surfaces (111MB+59MB) excluded and registered in appendix A; single files >5MB, npz/h5ad, .bak, and hidden sentinel files excluded |
| 5 | README had no "clone and run" path | Rewritten as a four-layer run guide: dependencies (incl. the scrnaseq-env anndata 0.13.2 note and the pipeline_env incompatibility declaration), stdio registration sample, env-switch matrix (EYEKB_ACT_V6 / softflags tri-state / TRACE_TAG), Release v2.3 split-volume download & merge + sha256 verification commands, evaluation recomputation entries (per-card scripts/ pointers), reconciliation and sanitization policy, appendices A/B |

## 2. Reconciliation tables

- `docs/recon/RECON_kb_mcp_20260927.tsv`: kb/ 100 files + mcp_server 4 files, per-file sha256 against live → **104/104 MATCH, 0 MISMATCH**.
- `docs/recon/RECON_other_dirs_20260927.tsv`: clients/scripts/evals/figures aggregated IDENTICAL.
- Documentation/interpretation-layer mirrors are sanitized copies and are not reconciled byte-for-byte (difference surface = label replacement; per-rule statistics in `docs/DESENS_SCAN_REPORT_20260927.md`).
- The six Release assets verified untouched (live v2.3 corpus mtime ≤09-25 08:19; papers.jsonl/manifest.yaml byte-equal to rag_snapshots, build_stats consistent); no re-upload, no tag change.

## 3. Sanitization double-scan hit statistics (details in the in-repo report)

Rule hits: REVIEWER_LLM 353 / CONTACT_EMAIL 259 / LLM_CHANNEL 44+14+2+2 / AGENT_ROLE 29 / MSG_PLATFORM 7 / PORT 4+1 (prose-type files only) / OWN_MOUSE_DR_DATASET 2 / LOCAL_LLM 1.
Zero-hit fallbacks: secret shapes 0, IM chat_id 0, hostnames 0, session identifiers 0 (ballot archives' toolcalls measured to carry no session field). Renames: 21 files + 1 directory. Second scan after replacement idempotent (0 hits).
Key exception: the BTEST_PREREG sidecar hash anchor retains the live original (`sha256sum -c` inside the mirror expected FAIL, not tampering).

## 4. Carry-overs and the "re-sync checklist after the next structural change" (for inheritance by future closeout documents)

1. **Code surface**: any change to server/eyekb_core/calllog/softflags → rerun the reconciliation table and overwrite `docs/recon/`; if code headers gain channel/host wording, pass the sanitization rules first, then commit.
2. **WIKI**: new/renamed files → full re-refresh of `docs/wiki/` (.bak skip rule retained); redline/directive addenda travel with their parent files.
3. **Interpretation layer**: new task directories → take into `docs/plans/` per this document's policy (md/json/tsv + annotation/*.jsonl + scripts; ledgers raw surfaces >5MB go to appendix A only, not in-repo); the .sha256 sidecars of preregistration-frozen files **must never be rewritten by the mirroring side**.
4. **RAG corpus changes** → new Release tag (do not overwrite v2.3-rag-assets) + `rag_snapshots/` three-file refresh + README §2 command updates.
5. **Pointer decision pending**: `EYEKB_DB_POINTER.yaml` default is still v2.0 (v2.2/v2.3 marked latest) — sync the pointer and README once PI decides to switch.
6. **calllog TRACE_DIR hardcoded** to `/mnt/D/EyeKB/logs/mcp_trace`: for off-host deployment, adjust per README §1.4 (audit-trail failure falls back silently, no service impact).
7. **git identity** is still the placeholder `EyeKB <eyekb@local>` (set by the 09-25/26 first export, consistent across history); switching to a real GitHub identity means amend = history rewrite, a separate action only after PI decides.
8. **stage3_retrieve engine paths**: MODEL_DIR/BASE point at the lab working disk — clone users must localize (documented in the README); if the upstream OcularKB engine upgrades, sync under the "verbatim copy" discipline.
9. **Local large-file wall**: keep the working tree at "repo body <50MB" (currently ~35MB including the interpretation layer); if new interpretation surfaces approach the cap → prefer splitting into a Release rather than committing.
