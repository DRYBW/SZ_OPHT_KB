# SUBDIVISION READINESS — per-parent resolution audit, and what a split costs

Date: 2026-10-22 · Card: `t_74ef13aa` · Pre-registration: `PREREG_SUBDIVISION_READINESS_20261022.md` (written before any measurement) + operational annexes A / A-amendments / A-amendments2 / A-amendments3
· Frozen target: `plans/retina_deep_20261020/REPORT_EyeKB_成果报告_v2.0.md` (addendum A appended, pre-existing bytes unchanged)
· Nothing activated; no whitelist entry; no download; no network

## One line

The dictionary ships **76** parent classes; over the fixed CL snapshot they carry **923** `is_a` descendant entries (**652** distinct terms). Graded against the ruling's release thresholds, **8** (parent, child) pairs are subdivision-available now, **3** are knowledge-subdividable only, **121** need the parent panel deepened first, **641** are not subdividable, and **150** are not subdivision questions at all (already a shipped class, or on the developmental / system axis). **595** of the 923 pairs fail for the plainest reason there is: the child name never occurs in the literature we hold. Every pair that *did* clear the bar is nevertheless a **net loss** if read as "replace the parent": gain **1** clusters against loss **297** on the recorded 721-cluster set. RPE is a **leaf term with zero descendants**, so RPE vs melanocyte is delivered as a sibling **confusion-pair evidence package**, not as a thicker panel.

## 1. What was asked, and what this wave added

The existing scheme and the frozen final report were not to be changed; a subdivision/subtype report was to be
appended to the end of that report. That is what happened: addendum A (Chinese, the report's own language) is
now in place, and everything above it is byte-identical.

| property | measurement |
|---|---|
| pre-append sha256 | `63a9f7bd4751df4122a45e89cb0737bbf9dd84a295caeecfdd4b1691703f9a8b` (16745 bytes) |
| addendum size | 24401 bytes |
| prefix 0..16745 re-hashed after the append | `63a9f7bd4751df4122a45e89cb0737bbf9dd84a295caeecfdd4b1691703f9a8b` |
| prefix identical to the pre-image | **True** |
| line diff | added 281, removed 0, modified 0 |
| pre-image copy kept | `REPORT_EyeKB_成果报告_v2.0.md.pre_addendum` |
| one-pager companion | added 13 lines, removed 0, prefix identical True |

## 2. Method, and the discipline that was kept

The ruling's block C was honoured literally: this wave **audits resolution, it does not split panels**.
Thresholds were written to disk before measurement and did not move afterwards:

| threshold | value |
|---|---|
| T-GENES | ≥ 2 discriminating positive genes against the nearest sibling |
| T-SOURCES | ≥ 2 independent sources, ≥ 1 giving adjacent-type contrast |
| T-CONTEXT | species / tissue / stage / system declared and satisfied |
| T-NONEG | no inference from "not in the top-10" |
| T-OBS | ≥ 2 discriminating genes inside the shipped top-marker window |
| T-STATE | state-programme share of discriminating genes < 0.50 |
| T-MATERIAL | ≥ 1 independent, non-evaluation local material |

Operations were fixed in `PREREG_ANNEX_A_OPERATIONS_20261022.md`, then corrected three times — each correction
written down with what had been observed on disk first, and **no threshold moved**:

| annex | what was observed first | what was corrected |
|---|---|---|
| A4-b | singular-only matching hit 1,277 chunks; 40 of 78 observed names gain chunks on a plural | occurrence test accepts a regular plural |
| A3-b | library scope prose gave uneven tissue sets (two libraries yielded none) | the shipped `_tissue_class_crosswalk_v1.json` is the first source |
| A7-b | the state reference as a *set* saturated (state fraction 1.0000 on 26/26 strong pairs) | state test became a **ratio** (≥0.75 of mentioning chunks in state context) |
| A11-b/A12 | progenitor parent's closure returned `monocyte`, `hematopoietic stem cell` | progenitor-like parents go on the developmental axis; thin evidence is T2 before any continuum reading |
| A11-c | `Fibroblast` came back 64/64 `developmental_axis` | the token `blast` was matching inside "fi**blast**" — matched on word boundaries instead (135 pairs returned to the audit) |

The first readiness pass (built with the two defective operations) is preserved unmodified at `out/firstpass/`,
so the supersession is checkable rather than asserted.

## 3. Result — the per-parent table

Machine-readable: `out/subdivision_readiness.tsv` / `.json` (76 rows, one per shipped parent class),
`out/pair_table.tsv` / `.json` (923 rows, one per (parent, candidate child) pair).

| tier | pairs | meaning |
|---|---:|---|
| T1 subdivision available now | 8 | every threshold cleared, including independent non-evaluation material |
| T1k knowledge-subdividable only | 3 | thresholds cleared except T-MATERIAL (ruling: 知识上可细分 ≠ 本接口上已验证) |
| T2 needs the parent panel deepened | 121 | occurs in context, but the evidence is too thin to separate |
| T3 not subdividable | 641 | ontology-thin, leaf, never mentioned, outside context, state-programme-only, or continuum |
| excluded | 150 | already a shipped class, or on the developmental / system axis |

| reason (fixed enum) | pairs |
|---|---:|
| `never_mentioned` | 595 |
| `developmental_axis` | 128 |
| `needs_deeper_panel_genes` | 119 |
| `outside_declared_context` | 43 |
| `system_axis_organoid_or_ipsc` | 14 |
| `available_now` | 8 |
| `already_shipped_as_own_class` | 8 |
| `knowledge_subdividable_only` | 3 |
| `spectrum_only` | 2 |
| `needs_wider_window` | 2 |
| `state_programme_only` | 1 |

| scope class | pairs |
|---|---:|
| `in_scope_adult_celltype` | 773 |
| `developmental_axis` | 128 |
| `system_axis_organoid_or_ipsc` | 14 |
| `already_shipped_as_own_class` | 8 |

Eight parents reached `subtype_suggested`: AC, Astro, Cone, Endo, Endo_Arterial, Endo_Patho, Fibroblast, RGC.

Two readings worth the PI's attention more than the labels themselves:

1. **The ontology's fine names are mostly not in the literature we hold.** 595 of 923 pairs die there. That is a fact about the corpus's naming habits, not about the
   biology, and it is the single largest limitation of this audit.
2. **The `is_a` closure is not a subdivision menu.** It returns `monocyte is_a progenitor cell` (a direct edge) and
   `corneal endothelial cell is_a endothelial cell` — real ontology statements that are not subtype questions
   here. Both are named in the table instead of being silently dropped.

## 4. Output shape (specification and dry run only)

Per the ruling §C2 the emission is `parent_candidates` + `subtype_suggestions_by_parent` + `resolution_status` +
`review_reasons`; parents are always preserved, subtypes compete only inside their parent branch, `parent_only`
and `subtype_ambiguous` are legitimate outputs, and no automatic final label is ever emitted.

| resolution_status | parents |
|---|---:|
| `parent_only` | 53 |
| `parent_abstain` | 15 |
| `subtype_suggested` | 8 |

Dry run: `out/output_shape_emission.json` (76 parents). Checked mechanically: parent candidates
present for every parent; suggestions nested under their own parent; status values inside the four legal values;
no single-gene admission; no parent-shared gene presented as child evidence; no default-route change.

## 5. Confusion pair — RPE vs melanocyte

RPE (`CL:0002586`) is a **leaf** in the fixed snapshot: 0 `is_a` descendants. It cannot be subdivided at all,
and the pair with melanocyte is a **same-level sibling confusion**, measured as such. Deliverable is the
six-element evidence package (`out/confusion_rpe_melanocyte.json`):

| element | measurement |
|---|---|
| ① shared support | shipped-panel overlap **0** genes; literature-positive on both sides **209** genes; slices: RPE 8477 chunks / 1405 papers vs melanocyte 553 / 210 |
| ② discriminating positive evidence | RPE-only **658** (unfiltered 1051), melanocyte-only **73** (unfiltered 118); papers giving adjacent-type contrast **49** |
| ③ state programmes | RPE-only share **0.234**, melanocyte-only **0.0822**, shared block **0.0957** |
| ④ information the interface lacks | only **141** of the RPE-only genes appear anywhere in the 721-cluster window (vs 27 on the other side) |
| ⑤ keep several candidates | **5** clusters rank both sides |
| ⑥ abstention | **179** clusters have no candidate at all |

Recorded reading on the fixed reference: 37 RPE-truth clusters and 55 melanocyte-truth clusters; **6** RPE-truth clusters are answered melanocyte in BOTH arms, so the deepened panel does not move it. The leading RPE-only genes in the literature
are dominated by disease programme genes, which is why element ③ reads the way it does. **The answer to this pair
is the parent plus a named confusion reason — not a thicker positive panel.**

## 6. What a subdivision would cost the parent

Same definitions as the predecessor wave's price table (holefill v12 §5), re-measured on the recorded set:

| parent | child | tier | demand | gain | keep | loss | costly |
|---|---|---|---:|---:|---:|---:|:--:|
| Cone | M cone cell | T1k | 0 | 0 | 4 | 13 | yes |
| Cone | S cone cell | T1 | 3 | 1 | 13 | 4 | yes |
| AC | glycinergic amacrine cell | T1 | 17 | 0 | 0 | 70 | yes |
| AC | starburst amacrine cell | T1 | 3 | 0 | 1 | 69 | yes |
| RGC | intrinsically photosensitive retinal ganglion cell | T1 | 0 | 0 | 7 | 12 | yes |
| RGC | retinal ganglion cell C1 | T1k | 0 | 0 | 0 | 19 | yes |
| Astro | retinal astrocyte | T1 | 2 | 0 | 0 | 8 | yes |
| Endo | endothelial cell of vascular tree | T1 | 3 | 0 | 4 | 25 | yes |
| Endo_Patho | endothelial cell of vascular tree | T1 | 3 | 0 | 1 | 28 | yes |
| Fibroblast | embryonic fibroblast | T1k | 0 | 0 | 0 | 20 | yes |
| Endo_Arterial | endothelial cell of vascular tree | T1 | 3 | 0 | 0 | 29 | yes |

**All 11 T1/T1k splits together: gain 1 clusters, loss 297 clusters.** Every branch this audit found subdividable is a loss if read as "the child replaces the parent" — the
literature child panels are thinner than the shipped parent panels and drop below the ≥2 shared-gene bar before
they can win anything. This is the same shape the predecessor wave measured for the bipolar splits, and it is
why this wave delivers a **knowledge asset and a resolution audit**, not a build order.

## 7. Red lines, with evidence

| red line | evidence |
|---|---|
| report and scheme byte-identical | prefix re-hash identical; added 281 / removed 0 / modified 0; pre-image kept (`out/append_proof.json`) |
| zero downloads, zero network | audit hook loaded **26** times across the chain; connection-class events **0**; the only socket events are **0** `socket.__new__` (unbound socket, fd=-1 — construction, not a connection) |
| discovery vs evaluation sources separated | searchable accessions from the volumes: ['GSE199013', 'GSE268630']; the 22 cellxgene-hosted volumes have no local accession handle → their overlap is `NOT_RUN` with the reason stated, **never 0** |
| nothing activated | no change to any shipped marker body, no threshold, no default switch, and the wave's commit contains only `docs/plans/subdivision_readiness_20261022/` |
| default route byte-identical, replayed not argued | OFFl 721/721 recorded rankings reproduced (differ 0); ON 721/721 (differ 0) |
| gate chain green in a CLEAN CLONE | G4 PASS: 3/3 byte-identical；G3 verify_repro (41-query retrieval anchor) rc=0 pass；G4 verify_pipeline (three byte anchors) rc=0 pass；G5 gate_registry (registry surface enforced) rc=0 pass；G6 gate_change_control (eight machine rules) rc=0 pass；gates=4 failed=0 (CHAIN PASS) |
| NOT_RUN never reported as pass | 2 unopenable material files listed by path; the disease thin layer carries no gene list (0 genes extracted) and that arm is declared void in §5 rather than counted as 0 evidence |

The gate chain was run from a clean clone of HEAD in a path containing a space, with a different working
directory and no author directory — the portability conditions the ruling's engineering ruling ③ asks for.
G3 needed `EYEKB_G3_PY` (the interpreter that has the locked embedding stack) and `EYEKB_MODEL_DIR`; with them it
reports `REPRO PASS: 41/41` rather than the inconclusive fallback the predecessor wave had to record.

## 8. Defects found in this wave's own work, recorded

1. **State reference saturating** (fixed by A7-b): in the superseded first pass, **32** pairs carried a
   state fraction of exactly 1.0 — a set-valued reference that contained every discriminating gene. Replaced by a
   ratio at a 0.75 cutoff, calibrated on disk (MKI67 1.0, TOP2A 1.0, RBPMS 0.4824, POU4F1 0.2368). Recomputed from `out/firstpass/pair_table.json`.
2. **`blast` matching inside `fibroblast`** (fixed by A11-c): **135** pairs were wrongly put on the
   developmental axis. After the fix that axis holds 128 pairs and the in-scope count goes
   638 → 773. This is the most consequential defect found, and it was found by looking at
   why a parent with many candidate children reported none. Counts parsed from `logs/m_readiness_v2.log` and
   `logs/m_readiness_v4.log`.
3. **Tier ordering** (fixed by A12): **136** pairs were labelled `spectrum_only` purely for having no
   evidence at all, recomputed from `out/firstpass/pair_table.json`.
4. **Preferred-name-only recall** (fixed by A4-b): the singular-only reading measured nomenclature, not evidence.
5. **RPE slice contaminated by the bare cell abbreviation** in the first confusion run: the slice matched the
   abbreviation wherever it appeared, so the side-only difference was dominated by slice size rather than by
   biology. Slices are now name phrases and a specificity floor was added; the unfiltered counts are kept
   beside the filtered ones rather than dropped. The superseded run's own log was overwritten by later runs,
   so its reading is **not quoted here** — an unverifiable number is worse than a description of the defect.

## 9. Repo changes and commit

Committed: this wave's English artefacts under `docs/plans/subdivision_readiness_20261022/` — and nothing else.
The author tree carries another card's uncommitted work (`docs/plans/l5_ontlayer_20261022/`,
`mcp_server/ontology_layer.py`, `mcp_server/server.py`, `kb/ontology/…`, `tests/run_gates.sh` and others); none of
it is in this commit, and the gate chain reading above was taken from a clean clone of HEAD precisely so it does
not measure that work. Not pushed — push is a separate reserved step.

See `COMMIT.txt` for the hash.

## 10. Commands run, and what each cost

| step | wall | peak RSS (MB) | memory-capped |
|---|---|---:|:--:|
| `golden_721_v2.log` | 0:06.01 | 151.4 | yes |
| `m_confusion.log` | 0:31.19 | 830.2 | yes |
| `m_confusion_v2.log` | 0:27.23 | 830.2 | yes |
| `m_cost.log` | 0:01.19 | 31.9 | yes |
| `m_cost_v4.log` | 0:01.19 | 30.9 | yes |
| `m_material.log` | 13:47.62 | 16321.4 | yes |
| `m_observe.log` | 0:00.17 | 22.6 | yes |
| `m_readiness.log` | 0:00.88 | 24.2 | yes |
| `m_readiness_v2.log` | 0:00.93 | 25.2 | yes |
| `m_readiness_v4.log` | 0:00.92 | 25.2 | yes |
| `m_report.log` | 0:00.07 | 24.3 | yes |
| `m_scan.log` | 2:43.69 | 948.0 | yes |
| `m_scan_v2.log` | 2:47.03 | 953.9 | yes |
| `m_state.log` | 0:35.79 | 596.9 | yes |
| `m_state2.log` | 0:21.76 | 502.7 | yes |
| `r_recon.log` | 0:04.05 | 26.5 | yes |

Heavy steps ran under `systemd-run --user --scope -p MemoryMax=… -p MemorySwapMax=2G`. Measured peak RSS is
0.02–16.7 GB: the 16.7 GB reading is the local-material scan (`m_material.py`, 474 candidate
h5ad headers opened backed='r'), which is the only step that came near its cap. Available memory stayed around
205 GiB throughout — well above the 40 GiB stop line in the shared workstation rules, so nothing was parked and
no other workstream was disturbed.

## 11. Artefacts

```
PREREG_SUBDIVISION_READINESS_20261022.md       thresholds + output shape, written before measurement
PREREG_ANNEX_A_OPERATIONS_20261022.md          the operations (corpus, candidates, context, genes, state, window)
PREREG_ANNEX_A_AMENDMENTS_20261022.md          plural recall + shipped crosswalk as first context source
PREREG_ANNEX_A_AMENDMENTS2_20261022.md         state ratio + tier ordering + progenitor parents
PREREG_ANNEX_A_AMENDMENTS3_20261022.md         the 'blast inside fibroblast' fix
scripts/                                       11 scripts, one per measured step, plus the gate replay
discipline/net_audit/sitecustomize.py          the zero-network audit hook
out/subdivision_readiness.tsv / .json          the 76-row per-parent table
out/pair_table.tsv / .json                     the 923 (parent, child) rows, full detail
out/output_shape_emission.json                 the two-level emission dry run
out/cost_table.tsv / .json                     demand / gain / keep / loss per pair
out/confusion_rpe_melanocyte.json              the six-element evidence package
out/O_observable_window.json                   the current window (721 recorded top-10 lists)
out/O_state_ratio.json / O_state_reference.json the state programme reference and ratios
out/M_non_evaluation_material.json             474 candidates, 472 opened, 2 NOT_RUN
out/S0..S5_*.json                              library contexts, parents, occurrence, genes, contrast
out/R0..R4_*.json                              ontology snapshot sha, depth, volume provenance, machine inventory
out/golden_721_replay.json                     the default-route replay
out/append_proof.json / append_proof_onepager.json  the append-only proofs
out/firstpass/                                 the superseded first readiness pass, kept unmodified
logs/                                          every run's log, the command log, and the gate readouts
```

