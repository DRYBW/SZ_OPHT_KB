# Sanitization double-scan report — REPOSYNC2 (09-28 improvement-wave intake surface)

Generating card: t_719dd225 (REPOSYNC2). Rule triples = the current project-github-export checklist + the surfaces added on 09-27; this wave **added no new rules**, but **added a CJK-boundary-hardened word-form recheck** (see the "Boundary hardening" section).
Discipline carried over from the 09-27 version: this report reproduces no channel-vendor name / adjudicator name / endpoint string / email literal — rules are referred to only by codename (mapping table = `docs/plans/repo_sync2_20260928/scripts/DESENS_RULES_codename.md`).

## Scan surfaces

- Newly taken this wave: `docs/plans/{kbx_lacrimal_20260928, kb_chain_audit_20260928, rag_fix_20260928, rag_fix2_v25_20260928, kb_gov_20260928, rag_gap_20260928, grade_anchor_20260928, retrain_assess_20260928, repo_sync2_20260928}` — 768 files in total (ledger `docs/recon/REPOSYNC2_INTAKE.sha256`)
- `docs/wiki/` (15 files, incl. the newly taken USER_DIRECTIVE_20260928 directive)
- `docs/skills/` (both skill mirrors refreshed in lockstep)
- `mcp_server/` (zero-change surface, re-checked with the double scan)
- Excluded surface (byte-mirror policy, no sanitization): `kb/`, `clients/`, `scripts/`, `tests/`, `evals/`, `rag_snapshots/`, `figures/` — their hits are listed file by file under "legacy registered, not touched" in `docs/plans/repo_sync2_20260928/out/t5_inventory_register.txt`.

## Filename double-scan

- 3 files renamed (v3 engine, automatic):
  - `rag_fix_20260928/scripts/<R08 stem>_followup_probes.py` → `REVIEWER_LLM_followup_probes.py`
  - `rag_fix_20260928/out/<R08 stem>_GATE3_ADJUDICATION_reply.md` → `REVIEWER_LLM_GATE3_ADJUDICATION_reply.md`
  - `knowledge-guided-cell-annotation/references/2026-09-24-kb2-run-ledger-and-<R04 stem>-channel.md` → `…-and-llm-channel.md` (restored to an existing in-repo filename; git treats it as a content update on the same path)
- 1 directory renamed (manual, following the 09-27 precedent "no stems in directory names"): `kbx_lacrimal_20260928/<R08 stem>/` → `kbx_lacrimal_20260928/REVIEWER_LLM/` (the review-submission filenames inside carry no stem; after in-text references were replaced in sync, paths correspond character-for-character to the directory name).

## Rule hit statistics (content replacements counted, from the apply log)

| Codename | Semantics | Hits |
|---|---|---|
| R13 | Third-party contact emails | 3,704 |
| R04 | Channel vendor A family | 129 |
| R08 | External adjudication LLM aliases | 99 |
| R12 | Internal agent profile names | 23 |
| R09 | IM platform names | 7 |
| R06 | Channel vendor C | 3 |
| R01 | Own sample identifiers | 2 |
| R07 | Channel vendor D | 2 |
| R15 | Local proxy ports (prose-type files only) | 2 |
| R11 | Local LLM stack name | 1 |
| R14 | Internal service ports (prose-type files only) | 1 |
| R02/R03/R10/R16 | chat_id / hostnames / secret shapes / session identifiers | **0** |

355 files with hits; 352 files with actual content changes (2 rename-then-content-change files overlap in both counts); numeric evidence surfaces (tsv/json/jsonl) received no numeric changes whatsoever beyond the R13/R04/R08/R12 string replacements; R14/R15 are active on prose files only, to avoid breaking recomputable numbers.

## Boundary hardening (new action introduced in this document)

The current `\bastra\b`-style word boundaries fail when adjacent to CJK characters (Python `\w` includes Han characters) — a blind spot in the 09-27 legacy rules. This document re-scanned **all included files** with the hardened word form `(?<![A-Za-z])<stem>(?![A-Za-z])`:
- Included surface (docs new wave + wiki + skills + mcp_server): **0 hits**, besides files that already existed before this document was generated;
- The only non-zero on the docs surface = one occurrence of the R04 literal inside the rule-description self-reference of `DESENS_SCAN_REPORT_20260927.md` (09-27 legacy; registered, left unmodified);
- Policy-surface legacy (kb/scripts/tests, byte-mirrored): 3,610 occurrences, registered file by file (see the "Excluded surface" pointer above).
Recommended handling (for the PI / project maintainers to adjudicate, beyond this document's authority): a) fold the hardened word form into the rule engine (prevents recurrence in future waves); b) if the kb/ surface is also required clean, that conflicts with the T2 byte-exact reconciliation discipline — mirroring-policy priority must be adjudicated first.
Details: `docs/plans/repo_sync2_20260928/out/t5_final_scan.txt`.

## Frozen hash-anchor exception register (expected `sha256sum -c` results inside this wave's mirror)

| Ledger file | Expectation | Reason |
|---|---|---|
| `kb_gov_20260928/KBGOV_PREREG_v1.{0,1}.md.sha256` | **PASS** (2/2) | Preregistration files were not hit by any rule |
| `kb_gov_20260928/SHA_MANIFEST.txt` | 31 OK + 1 line unverifiable | 1 line anchors `__pycache__/*.pyc` (not mirrored per precedent; the live anchor remains valid) |
| `kb_chain_audit_20260928/ledgers/SHA_DELIVERABLES.txt` | 43 OK + 79 lines expected-FAIL | Targets were sanitized under R13/R04/R08 (author emails inside epmc batch caches, etc.) |
| `rag_fix2_v25_20260928/ledgers/SHA_DELIVERABLES_20260928.txt` | 27 OK + 5 lines expected-FAIL | Same pattern (incl. reference lines to renamed files) |
| the four `rag_fix_20260928/ledgers/SHA_*` files | All anchor live absolute paths | Unverifiable inside the mirror; live-disk integrity governs (09-27 policy) |
| `retrain_assess_20260928/ledgers/SHA_SELF_20260928.txt` | 3 OK + 1 line expected-FAIL | The self-anchored RETRAIN_VERDICT.md was sanitized under R08 |
| `rag_gap_20260928/ledgers/SHA_DELIVERABLES.txt` | 20 OK + 1 line of **upstream drift** | REPORT_RAGGAP.md on the live side already disagrees with its own ledger (ee7b6933… ≠ 42b79838…) — not mirror corruption; see open item 1 of the closeout document |
| `grade_anchor_20260928/data/SHA_LEDGER_INPUTS.txt` / the PRE/POST verifications | All absolute paths | Live disk governs |

Machine-checkable detail = `docs/plans/repo_sync2_20260928/out/t4_ledger_check.txt`.
The sidecars of preregistration-frozen files were **not rewritten** (the mirroring side has no authority to rewrite anchors, per the 09-27 discipline).

## Idempotency verification

Full-rule rescan by the v3 engine after replacement: **0 renames, 0 rule hits, 0 hit files** (raw machine-side output kept in /tmp; in-repo evidence = this file + out/t5_final_scan.txt).

## Release zero-touch statement

The six files of Release `v2.3-rag-assets` were not downloaded, not uploaded, not modified; reverification only re-split the existing local tar and compared the parts against the API digests (evidence `docs/plans/repo_sync2_20260928/out/t6_release_reverify.txt`).
