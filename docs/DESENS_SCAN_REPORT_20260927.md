# Sanitization double-scan report — 2026-09-27 REPOSYNC

Scope: docs/wiki (14 files) + docs/skills (two skill mirrors + 3 protocols files) + docs/plans (interpretation layer, 1439 files) + mcp_server (4 code files).
The rule triples share their source with the current project-github-export checklist (R01–R16 codenames in the table below); surfaces newly covered this round: second-hand channel-vendor endpoint strings, third-party author emails, local proxy ports, internal agent role names.
**This report reproduces no channel-vendor name / adjudicator name / endpoint string** — rules are referred to only by codename plus semantic description; the full mapping stays in the local sanitizer script and the git commit message (outside the repo).

## Rule codename table (hit counts)

| Codename | Semantics | Label | Hits |
|---|---|---|---|
| R01 | Own DR sample identifiers | OWN_MOUSE_DR_DATASET | 2 |
| R02 | IM conversation-ID prefix shapes | CONTACT_ID | 0 |
| R03 | Workstation hostnames | HOST | 0 |
| R04 | Channel vendor A (Chinese nickname) and its endpoints/bare aliases ("token-plan" style strings) | LLM_CHANNEL | 44 |
| R05 | Channel vendor B (.fan/.fun dual-domain family) | LLM_CHANNEL | 2 |
| R06 | Channel vendor C (nickname + numeric endpoint) | LLM_CHANNEL | 14 |
| R07 | Channel vendor D (intern domain) | LLM_CHANNEL | 2 |
| R08 | External adjudication LLM aliases (incl. adjudicator A's `$_`-prefixed filenames; word boundary prevents collateral hits on substrings like "astrocyte") | REVIEWER_LLM | 353 |
| R09 | IM platform names (WeCom family) | MSG_PLATFORM | 7 |
| R10 | Secret-shape catch-all (sk-/github_pat_/gh*_/PRIVATE KEY) | REDACTED_SECRET | **0** |
| R11 | Local LLM stack name | LOCAL_LLM | 1 |
| R12 | Internal agent role/profile names | AGENT_ROLE | 29 |
| R13 | Third-party contact emails (corresponding authors, inside API caches) | CONTACT_EMAIL | 259 |
| R14 | Internal service ports (prose-type files only) | PORT | 1 |
| R15 | Local proxy ports (prose-type files only; numeric evidence surfaces in tsv/json/jsonl are not touched, to avoid breaking recomputable numbers) | PORT | 4 |
| R16 | Session-identifier shapes (session/conversation/chat/trace id) | SESSION_ID | **0** |

## Filename scan (21 renames + 1 directory)

- 1 reference file of the knowledge-guided skill: filename contained channel-vendor A wording → `<…>-llm-channel.md` (realigns with the same-named file in the 09-25 first-export repo; content refreshed to the 09-26 version)
- 17 five-round review-submission files of kb9_ocs_20260927 (PROMPT/REPLY/send.log): adjudicator prefix in filenames → `REVIEWER_LLM_*`; in-text references replaced in sync, so after renaming each reference corresponds one-to-one with a filename
- kb9 script whose original name contained the R08 stem → `REVIEWER_LLM_xhigh.py`; the 6 out/recheck audit-trail files follow the same rule
- Directory `docs/plans/sync_<profile-name>_scSOP_20260927` → `sync_scSOP_20260927` (profile names do not land in directory names)

## Zero-hit fallbacks (redline recheck)

- Secret shapes (R10): **0**; IM chat_id (R02): **0**; hostnames (R03): **0**; session identifiers (R16): **0** (ballot archives' toolcalls measured to carry only ts+tool+args+result summary, no session fields)
- Patient/DR-derived data: 0 csv/percell/patient files inside the mirror surface; >5MB large tables and raw fetch-cache directories were kept out of the mirror entirely (sizes and regeneration path in the main README appendix)
- PI verbatim: PI quotations in directives/briefs are kept word-for-word (sanitization replaces only account/channel/email patterns; no sentences were deleted)

## Idempotency verification

Second full-rule scan after replacement: 0 hits, 0 renames (no label re-matches any rule pattern).

## Frozen hash-anchor exception register (important)

- 2 lines in `docs/plans/btest_20260927/BTEST_PREREG_v1.0.md` were sanitized under R04/R12 (card-attribution and channel wording).
- Its sidecar `BTEST_PREREG_v1.0.md.sha256` was **left as-is, not rewritten**: the hash anchors the live original (`/mnt/D/EyeKB/plans/...`, sha256 confirmed matching). A preregistration anchor must not be rewritten by the mirroring side.
- Consequently, running `sha256sum -c` inside this mirror is **expected to FAIL** for that file — this is a sanitization difference, not tampering. Original integrity is judged against the live disk / evidence bundle.
