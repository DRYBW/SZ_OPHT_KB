# Activation-prerequisite obligation run record — 2026-09-28 (OBLIGRUN / B5IMPL / H1M3 / RAGFIX3 / MOUSEEXT / REPOSYNC3)

## OBLIGRUN two-round chain (plans/obligrun_20260928/)

Timeline: BRIEF (reading-matrix preregistration) → run1: OB-1 clear (339-row record table; RUN5 requests deterministically re-rendered byte-for-byte equivalent 21/21, standing in for the unarchived originals) / OB-2 PASS (diagnostic table 57 rows × 11 columns; hard assertion post_shield top3==ballot face 33/33) / OB-3 clear (22/22) / **OB-4 not clear → ballot-face void branch** → blocked with 0 ballots. Project maintainer RULING_1 = option A → comment pointing the way + unblock to resume in place → run2 all green, done.

Final numbers: **P1(C2b)=26/33** (named 28; the 7 missed clusters all fall in the Fibroblasts/Pericytes lineage band: 5 unnamed + 2 named-but-wrong), **P2 strict=0/33**, ballot budget 99/150 with zero missing ballots, face_sha identical across the three seats. VERDICT_OBLIGRUN_v2.md = READY; ACTIVATION_READINESS.md = advisory ballot (activation still rests with the PI via OB-5); the voided v1 is kept as a trail artifact, never altered, cross-referenced.

Key artifacts: PREREG_OBLIGRUN.md (sha bfd8836d) / PREREG_OBLIGRUN_ADD1.md (option-A addendum section, sha 92c2a538) / OBLIGRUN_RULING_1.md / face/kb9_face_v2.1.jsonl (sha 2c0649dc) / out/FACE_V21_ledger.tsv (31 clusters, full rows byte-identical) / pre_vote_diagnostics_v21.tsv (delta_vs_v1 column) / OB4_lit_screening_v21.md (0 residue).

The triple paper-evidence recipe that option A hit (reusable as a same-source criterion template): ① the paper's Data Availability declares its own GSE accession; ② the GEO series title matches the paper title as-is; ③ the evaluation object's obs.study × GSM directly-read cell counts agree. chen_* has no accession and cannot be resolved = residual limitation registered as-is (if an authoritative mapping is obtained, rerun the screening).

## Project-maintainer recompute-script pitfalls (verify recipe)

- Naive three-seat majority: treats `coarse:Fibroblasts` as an independent label → named=31; under C2b semantics, normalizing `coarse:X`≡`X` → named=28; **the hit set in both versions is exactly equal to the runner script's 26 clusters** → judged PASS. Fields: an ANN row = cluster_id/identity/level/grade/gates/flag/why.
- The truth table lives in the kb9 build directory, out/kb9_truth_table.tsv (columns include current-period fields such as consensus/p1_hit; the recompute uses only the truth column to prevent circularity).

## B5IMPL (plans/kbgov_b5impl_20260928/)

B5 = mouse-derived input (title_frac convention + the three signals Gm\d+/.*Rik$/m_only, frozen threshold T=0.4) → celltype_ranking=[] + all unranked_candidates retained + no_named_ranking_for; AMBIG{GLUL,VIM,CLU} co-expression only gets a no_naming_claim annotation, never an order deletion. Human input sees zero intervention; the three cell_type/list-mode tools see zero perturbation (governed surface = genes-mode). All five gates PASS (defect cases 7/7, human-side displacement 0.0% across 230 clusters, mouse side 59/59 all rejected, GOLDEN 41/41 identical when off, 42-probe fallback byte-identical, read-only with zero writes). Fail-soft: a missing lexicon automatically degrades to legacy (empirically identical to the OFF state).
**Known residual risk**: genuine mouse title-case input sent upstream would be falsely rejected (misdetections=0 on this data, but no guarantee) → case-by-case calllog review at T+7; if false rejections >0, report to the PI and switch to the B4 tier (suspected = annotate only, never refuse to answer) — changing tiers = a change of methodological criteria and MUST be approved by the PI; the same wiring applies at env granularity, no fork.
Project-maintainer live-probe tri-state script: production code started via training-venv stdio; HUM KERA/ALDH3A1 (named, human_assumed), MOUSE Thy1+Grin3a (suspected → refusal), Gm3339 group (confirmed → refusal); B5=0 control restores legacy.

## H1M3 (plans/grade_h1m3impl_20260928/)

Reading protocol v1.3 §9 = H1-M3 naming eligibility `ie=pass ∨ res=pass` (the three technical gates do not participate), **prospective effect** (from runs preregistered after the sign-off date); the counterfactual recompute against the 9 archives is identical to the anchor artifacts (raised 24 / flipped correct 7 / new errors 0 / regressions 0); an H1-M3 sensitivity comparison on the 99 ballots of the OBLIGRUN v2.1 surface gives delta=0 and is kept in a separate column (the headline 26/33 is not retroactively altered). The runner script self-reported a transcription typo in the hand-copied PREREG table for RUN6A, "23→23" (true value 24→24) → ERRATA_PREREG incremental artifact: the criterion's comparison object is the frozen json anchor file, not the hand-copied table, so gate validity is entirely unaffected — the hand-copied-table single-cell typo + errata-artifact pattern is reusable.

## RAGFIX3 three gates (v2.4.2 = 242,928 chunks / 3,869 papers)

Gate ③ 87/92 = 94.6%, the first breach of 80% (original denominator, original threshold, original criterion; 78→87 monotone with zero regressions); 104 rows → 103 admitted, 1 rejected (double counting prevented); of the 7 target units, 6 delivered + C8ORF76 honest MISS (full text in the corpus but no word-boundary token) + 3 side products; downloads 19.33MB, within the ≤100MB budget, nothing >1GB; the CPU embedding chain (viable under the no-GPU clause).

## MOUSEEXT — the heavy tier is judged dead (plans/mouse_ext_precheck_20260928/)

Row-level forensics on the 7 candidates admits none, with one open case: GSE137400/81905 = mother series of the training pool (GSM-level smoking guns: 10/10, 6/6 containment); GSE255520 = re-profiled training cells (admitting = circular); GSE63472 = P14 developmental domain + labels not in GEO; GSE150703/184933 = developmental/perturbation domains without labels; the sole open case GSE201402 (already on disk, 1.3GB, zero downloads; 7/10 classes but panel coverage 50.25% < 90% — the frozen assertion awaits further checks). **Lesson phrasing: meeting the labeling bar ≠ meeting the independence bar**; public resources cannot supplement a true second external set — the 08-26 limitation note on F1 is confirmed beyond doubt.

## REPOSYNC3 eight gates + expired GitHub credentials (push channel)

T1-T8 all passed (including the first run of the T7 own-data token scan = HARD 0 / masked exceptions — 2 items registered; the T8 §9 three-version corpus screen = 36712326 has been in the corpus since v2.0, not introduced by this wave, own-deposit + attributed-phrasing review on file; ra3's 103 papers have zero intersection with the watch list). With the four local commits staged (11f9649→73e9cd3→1f547f3→cf254ab, clean tree on main), the **push stalled = the gh token had silently expired** (hosts.yml an empty shell, cached token returns 401, SSH key not registered) → rescued by the project maintainer's device-code flow (recipe in research-repo-publish): curl device/code (**the `Accept: application/json` header MUST be sent, otherwise the response is form-encoded — parse both formats as a fallback**) → send user_code to the PI → poll for the token → push automatically. During network anomalies, pgrep / a full `ps` sweep of /proc hangs (some process in D state) while single commands such as echo/date work fine — diagnose with targeted commands, never with full-table scans.
