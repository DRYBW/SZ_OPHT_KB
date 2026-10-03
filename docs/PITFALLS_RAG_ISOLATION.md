# docs/PITFALLS_RAG_ISOLATION.md — Structured known-issues entries and the RAG-corpus isolation statement

**Status**: BINDING (filed on the authority of the "Prohibited Actions" text issued with the
architecture-review ruling; 2026-09-30 REV-1 = the astra formally reviewed and approved
disk version, superseding the first edition of the same morning)
**Applies to**: `pipeline/pitfalls/pages/*.json` (atomic-claim contract), the upstream
known-issues manuscript (`/mnt/D/EyeKB/kb/known_issues/`, read-only file outside the repo)
and any of its text fields

## Prohibitions (permanent)

1. No text from known-issues — the claim contract's failure_mode /
   observable_signature / mitigation, nor the manuscript's issue / why_it_bites
   long-form fields — **may ever enter the RAG corpus**. The build scripts of any
   RAG index/activation pipeline (the live v2.1, the staged v2.4.2, and all future
   versions) must explicitly exclude `pipeline/pitfalls/` and the known-issues
   manuscript directory; when new corpus sources are added, this prohibition must be
   re-checked for dilution.
2. **WIRE locks the live RAG v2.1 library throughout**: wiring known-issues into other
   surfaces is not grounds for any RAG version switch or activation; the staged v2.4.2
   must not be activated as a side effect (its own acceptance gates have not fully
   passed; its activation goes through an independent process). This batch changed no
   service-side or dictionary-side files (`mcp_server/`, `kb/`, `clients/` git diff =
   empty; machine-checked under acceptance gate G6).
3. The sample pre-check engine (`pipeline/s0_check.py`) and the interpretation evidence
   surface (stage A/B evidence-collection functions, the evidence-summary documents fed
   to blinded review) are **forbidden to read** known-issues text. Consumption = shadow
   semantics: risk flags and re-review requests are injected into the human reading
   surface (flag table in the report header + two columns in decisions), with **no
   automatic rewrite of grading/ballots/naming** (automatic naming changes are always
   =0); entry free text is not injected before blinded review, and entries with
   `answer_dependency≠none` open only after interpretation (in run artifacts that text
   = REDACTED).
4. Machine-check criteria (two; rerun after any wiring change):
   - `plans/wire_p1_20260930/scripts/firewall_grep.py <run-dir>`:
     layer A = grep 163+ natural-language fingerprints of the manuscript against the
     interpretation evidence surface → 0 hits;
     layer B = post_decision entry free text in any run artifact → 0 hits
     (blinded-review contamination scan).
   - `pipeline/pitfalls/build_claims.py --check` + `tests/test_s0_gate.py`
     T4-T6: AST-level read prohibition for interpretation-surface modules +
     contract/link/field integrity + no override/cap strings.

## Rationale

The blinded-review protocol and the frozen exam set are EyeKB's core methodological
assets; the legitimacy of the 94.7% concordance regression depends on
"interpretation sees only evidence, never answer-side text". known-issues entries
record known pitfalls of specific datasets (including sample-level information);
once they enter the retrieval corpus or any surface visible to the blinded reviewer
they constitute evaluation-set information leakage — the review termination condition
is "one blinded-review answer leak = termination of the whole expansion".

## Exceptions and exit

None. If known-issues ever need to participate in retrieval, a new review must be
convened and this statement revised first.
