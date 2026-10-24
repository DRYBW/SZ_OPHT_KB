# Pre-registration — ADOPTION of the corpus-supported Cell-Ontology child terms into the naming layer (`cl56_v15`)

Date: 2026-10-22 (written) · executed 2026-10-24
Card: `t_fabddb85` ("CL56-ADOPT"), board `pi-briefing`, assignee `pi-chief`
Brief: `plans/cl56_adopt_20261022/BRIEF_ADOPT_CL56_20261022.md` (verbatim in the card body)
Predecessors whose instruments and floors are reused, unedited:
`plans/cl_depth_devlineage_20261021/` (built the candidates) ·
`plans/subdivision_readiness_20261022/` (pre-registered the floors this wave's scope rule cites) ·
`plans/noregr_20261022/` (the harness: rulers, replay engine, acceptance gate) ·
`plans/activate_holefill_20261022/` (the activation card's shape: pre-registration → default-OFF build →
measurement → GO/NO-GO → kill-switch proof → re-registration → clean-clone gates).

## 0. The decision, and what kind of record this is

The project owner was shown a two-item checklist — (1) enable the literature hole-fill library,
(2) adopt the 56 Cell-Ontology child-term candidates — and answered **"ok"** (2026-10-22). This document
pre-registers the **owner-signed adoption decision** for item (2). It is **not an audit pass**, not a
validation, and not an accuracy claim. It records: what is being adopted, at what granularity, which
pairs are in scope, the acceptance rule that decides whether the adoption stands or is rolled back, the
rollback path, and the disclosure that every number produced here is an **IN-SAMPLE** reading on the same
28 public volumes the panels were selected against — a harm-line/regression reading, not a validation.

### 0b. Ordering disclosure — what was on disk before this file was written

| artefact | why it exists before this file |
|---|---|
| `out/INPUT_MANIFEST.json` (54 inputs, sha256 each) | read-only freeze of every input, run first so this document can name inputs by hash (`scripts/f0_freeze_inputs.py`) |
| `out/RECON_BEFORE_SCOPE.json` + `logs/r0_recon.log` | a **read-only** reading of the SHIPPED tree (no overlay, no increment) over the recorded set, taken to establish the starting point (`scripts/r0_recon.py`) |
| the two predecessor waves' frozen artefacts | built on 2026-10-21/22, before this card was even dispatched |

**Disclosed honestly**: the shipped tree's *before* reading and the predecessor waves' *readiness* readings
(the pre-registered floors, the demand/gain/keep/loss table) were on disk when this document was written.
What had **not** been produced in any form: an after-arm (post-adoption) reading, the increment itself,
the scope list this document fixes, and the panels it will carry. No threshold, no scope condition and no
acceptance clause below was set or moved with reference to a post-adoption result. The scope list is fixed
in §4 and is computed mechanically from the frozen inputs by the rule as written; the rule was written
before the list was produced and does not move after it.

## 1. What is being changed, exactly

| item | before (base commit `c06aac2`) | after (only if the acceptance rule passes) |
|---|---|---|
| a new naming increment, `kb/markers/markers_v15_cl56_increment.json` | absent | present, registered **default OFF** |
| a dictionary entry for it in `mcp_server/eyekb_core.py` (`MARKER_LIBS`) | absent | one entry, `"cl56_v15"` |
| its whitelist tuple in `mcp_server/eyekb_core.py` | absent | `CL56_DEFAULT_LIBS = ()` first (empty), `("cl56_v15",)` only after a GO |
| the `all`-route append branch in `_load_marker_dbs` | absent | one branch, guarded by the switch |
| the kill switch | absent | `EYEKB_ACT_CL56` — `{0,false,off,no}` = OFF, unset/empty/anything else = ON (ACT-v6 discipline) |
| the KB label → Cell Ontology map `kb/markers/markers_cl_alignment_v2_unified.json` | 76 labels, covering the libraries up to `antseg_v10` | the adopted child terms added, one `mapped` row each (`cl_id` + the snapshot's own label + the entry as provenance) — **the naming layer itself**. No existing row is edited or removed; one version bump + `supersedes_note` |
| the marker bodies, the score, the admission floor (`n_shared >= 2`), the margin, the tie-break, the window, every other library | — | **byte-unchanged** |

Nothing else moves. No other library is activated, no other whitelist gains an entry, no exclusion row is
withdrawn, and no scoring parameter is touched.

**Why the label map is part of the adoption, and not an extra.** The naming layer is the pair
(entry name, `cl_id`) recorded per the standing directive `docs/wiki/USER_DIRECTIVE_20260924_cell_ontology_naming.md`
§1: a new entry must carry the CL term it names. The predecessor activation card measured the cost of not
doing it: 16 of `holefill_v12`'s 17 Cell-Ontology entry names were unresolvable to the shipped map, so the
judge graded 70 of 90 takeovers `unmappable_pred` and read them as inconsistencies — an artefact of the map,
not of the panels. Its own close-out asks for the map to be fixed "before retrying the library". An adopted
name that the judge cannot map is not an adoption; it is the same defect again.

## 2. Frozen inputs (read-only; every number traceable to one of these)

Hashes: `out/INPUT_MANIFEST.json` (54 rows). The load-bearing ones:

| # | Path | sha256 (16 hex) | Role |
|---|---|---|---|
| I1 | `/mnt/D/EyeKB/plans/oss_check_20261019/dl/results/<vol>/annotation_evidence_report.json` (28) | see manifest | the recorded per-cluster query window (`top_genes`) and the ranking the shipped code produced on 2026-10-18 |
| I2 | `…/oss_check_20261019/ledger_v1/ledger_cluster_level.tsv` | `9e2a0844ad639e0b` | recorded reference labels + `n_cells`, one row per cluster (721) |
| I3 | `/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py` | `be4e91c311bb77f1` | the shipped service core (the file the wiring edits) |
| I4 | `…/kb/markers/markers_cl_alignment_v2_unified.json` | `48051cdae915b82e` | the KB label → CL map (the naming layer) |
| I5 | `…/kb/ontology/cl/releases/2026-06-08/cl-base.obo` | `c6274fb65cdf740b` | the frozen Cell Ontology snapshot (3,531 `[Term]` blocks / 3,335 active) |
| I6 | `…/plans/cl_depth_devlineage_20261021/out/CHILD_TERM_CANDIDATES.json` | `52802c68200a719d` | the 56 (parent, child) candidates, 25 with corpus support |
| I7 | `…/cl_depth_devlineage_20261021/out/GRANULARITY_FOURWAY_721.tsv` | `f66ba000cac34f50` | the per-cluster four-way relation reading (721 rows) |
| I8 | `…/plans/subdivision_readiness_20261022/out/pair_table.json` | `48077ed8fc0f4ab8` | the 923 readiness rows: tiers, and per pair the **discriminating positive genes** (parent-shared removed) |
| I9 | `…/subdivision_readiness_20261022/out/cost_table.json` + `PREREG_SUBDIVISION_READINESS_20261022.md` | `c3a0421ea039f0cf` / `eef74a506c102501` | demand/gain/keep/loss per pair, and **the pre-registered floors** (§4c cites them) |
| I10 | `…/plans/noregr_20261022/scripts/wave_common.py` + `n3_harness.py` + `PREREG_NOREGRESSION_20261022.md` | `f8226dc4aefc799a` / `9f55a8ccbd202196` / `131f5a422842e392` | **the harness, reused unedited**: R_fam (four grades), R_cl (ontology relations), the replay engine, the acceptance gate |
| I11 | `…/plans/antseg_fill_20261020/out/gene_vocab.json` | `b423511f2df1bdc2` | the assay gene vocabulary (the panel's measurability floor) |
| I12 | `/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet` | not re-mined | the served corpus; identity only — this wave mines nothing new from it |

Recorded set: **28 volumes / 721 clusters / 1,495,330 cells** (re-measured here, not assumed).

Interpreters: `/usr/bin/python3` for this wave's own scripts and for the repo import (measured: it imports
`eyekb_core` cleanly). Zero network, zero downloads: `ledgers/net_audit.log` must carry hook-load receipts
> 0 and zero connection-class events.

## 3. Operationalisation

1. **Units.** The claim is judged on the recorded `(volume, cluster)` windows, **cell-weighted**, under the
   harness's four grades (`consistent` / `related` / `inconsistent` / `mixed`; `mixed` = the service
   returned no named candidate) and its Cell-Ontology reading
   (`same_cl` / `kb_coarser` / `kb_finer` / `truly_inconsistent` / `abstain` / `unmappable_*`).
2. **Three readings, all reported.** (i) the recorded volume declarations; (ii) the external tester's
   re-declarations (`CX16_tabula_sapiens_eye` → `ocular_surface`, `CX11_posterior_eye_atlas` → `ocular_surface`,
   as used by the predecessor card); (iii) the **default route itself** — the `library="all"` call with no
   `tissue` argument, the surface a default-route flip actually changes. A criterion that holds on one
   reading and fails on another is a failure.
3. **Before/after arms.** `before` = the tree without the whitelist member; `after` = the tree with it
   (measurement-only `inject: ["cl56_v15"]` before any flip). Once flipped, the arms are separated **both**
   by the switch (`EYEKB_ACT_CL56=0` vs unset) **and** by the injection path, and the flip is proven to
   reproduce the injection arm cluster by cluster.
4. **Attribution.** Every cluster whose ranking tuple `(top-1, n_shared, n_ranked)` moves is listed with its
   truth label (`ref_cell_type` / `ref_family`), its volume, its tissue, its cell count and its before/after
   answer, classified into pre-specified kinds: `adopted-name-gain` (the new top-1 is an entry of `cl56_v15`),
   `rank-shift` (top-1 unchanged, the candidate list moved), `unexpected` (top-1 changed to something that is
   **not** a `cl56_v15` entry). `unexpected` is never absorbed.
5. **The aggregate `inconsistent` share** is read twice: cell-weighted over all 721 clusters, and per dataset.
   It is the named failure mode of this class of change (the L1 precedent on record in `plans/INDEX.md` under
   `scorer_guard_20261020`: abstention 23.25% → 5.55% while contradictions 17.95% → 29.32%, ruled NO-GO).
   **Abstention falling is not a gain by itself.**
6. **This measures naming agreement against author labels, not recognition ability.** An ontology-consistent
   name is not evidence of a better call. Said once here and once in the report.

## 4. Scope rule (pre-registered; fixed before the list was computed; not widened after results)

Adopt a `(our class → child CL term)` pair only if (a), (b) and (c) all hold.

**(a) Ontology.** The child term exists in the frozen snapshot I5, is not obsolete, and is a **strict**
`is_a` descendant of our current class's CL term under the snapshot's own ancestor closure (computed from
I5's `is_a` lines with `{is_inferred=…}` qualifiers stripped, as the predecessor wave's gate A3 does).
Refusals are recorded with their reason.

**(b) Naming support.** The pair is one of the **25 corpus-supported pairs** of I6 (the held corpus states
the term or one of its synonyms, with a phrase and a locator — measured by that wave, not re-derived here;
`corpus_support_status` ∈ {`corpus_states_the_term` (16), `corpus_states_a_synonym_only` (9)}).
The 31 pairs with `no_corpus_hit` are **out of this adoption** and are reported as a pending list: an
unsupported name adopted on our own say-so is exactly the fabrication this project forbids. Widening later
is a new pre-registration, not an amendment after the fact.

**(c) Scorable at the pre-registered floor.** The card's clause (c) ("the pair has enough cells to be
scorable at the pre-registered floor") is operationalised here as three mechanical conditions, all read from
the frozen inputs, and the operationalisation is **stated because the clause is ambiguous** — it is resolved
towards the predecessor wave's own floors, never towards a laxer one:

| id | condition | source of the floor |
|---|---|---|
| c1 | ≥ 1 recorded cluster (I2) whose fixed reference `ref_cell_type` is literally the child term — the demand unit that can move a cell-weighted reading | the unit of measurement (§3.1) |
| c2 | the entry built for the pair carries **≥ 2 discriminating positive genes** (≥2 distinct studies as markers in the child's own context, parent-shared genes removed, restricted to I11's assay vocabulary) | `subdivision_readiness` T-GENES and invariant 5 ("single-gene admission = 0") |
| c3 | at least one demand cluster's recorded window (I1) shares **≥ 2** genes with that panel — i.e. the name is producible at all inside the shipped interface | `subdivision_readiness` T-OBS ("≥2 discriminating genes observable inside the shipped top-marker window") |

**Panel source (fixed here, before the build).** For an adopted pair, the entry's genes are **exactly** the
pair's `discriminating_genes` list from I8, restricted to I11 and deduplicated. No gene is proposed by this
card, none is taken from an evaluation label, and **none is copied from another library's panel** — a child
entry must not carry the parent's identity genes (that would tie it with the parent and rename everything the
parent answers). Genes removed by the vocabulary restriction are listed, not silently dropped.

**What a pair failing (c) is.** Not adopted, with its reason recorded (`c1_no_demand_cluster`,
`c2_below_two_discriminating_genes`, `c3_panel_not_observable_in_window`). No panel is invented for it and no
entry is written for it.

**Two things this adoption must not do**, per the brief: it must not invent a term the author never used for
those cells (every adopted entry's name is the snapshot's own preferred name for the child term, and the
author's own label for the demand clusters is checked to be literally that name, reported in §5d), and it
must not merge two of our classes (each entry carries only its own discriminating genes; the parent entry is
untouched and stays in the route).

`we_are_finer_pairs` (I6, 8 pairs where **our** term is finer than the author's) is a **different question**
and is not folded into this adoption.

## 5. The acceptance rule (pre-registered; decides GO / NO-GO)

A **GO** requires **all four**, measured on the merged arm, under **all three** readings of §3.2:

- **(a) No dataset's cell-weighted `consistent` share falls.** For an adoption, the predecessor's
  `PASS_ATTRIBUTED` is **not** sufficient: the verdict must be `PASS` on each reading. A fall on any dataset
  under any reading is a NO-GO, reported with its numbers.
- **(b) The aggregate cell-weighted `inconsistent` share must NOT rise** (overall, and on no dataset). A rise,
  however small, is a NO-GO: it is the failure mode named in §3.5 and it is not rescued by attribution.
- **(c) The movement must be attributable cluster by cluster**, every moved cluster classified into the
  pre-specified kinds of §3.4 with zero `unexpected`, and the count of moved clusters compared against the
  pre-registered expectation of §6.
- **(d) The finer name must be the author's own label for those adopted clusters.** Reported per adopted
  cluster: the truth label and the before/after answer; any adopted cluster whose truth label is not exactly
  the adopted name is reported as such (and, if the reading in §4(b) was carried by a synonym, it is named as
  a synonym-carried adoption rather than restated as the author's label).
- **(e) The kill switch must restore the pre-flip default byte-for-byte** (carried from the predecessor's
  clause (d), which is the same requirement), proven by replaying the recorded query set at the **same
  absolute path** (`721/721` cluster windows and the full default battery, raw and canonical digests identical).

## 6. Pre-registered expectations (all already on disk before this file)

| # | expectation | on-disk basis |
|---|---|---|
| E1 | The scope list is **a small subset of the 25**, not all of them: the predecessor wave measured that most of these child panels are thin against the shipped parent panels | `subdivision_readiness` cost table: for these pairs `gain_clusters` is 0 except `Cone → S cone cell` (1), against `loss_clusters` of 4–111; all 11 of its T1/T1k splits together: **gain 1, loss 297** |
| E2 | The **named mechanism is narrow** and is stated as such: clusters the family-level regex called inconsistent because they were finer than our class. The measurable gain is therefore at the **ontology reading** (`kb_coarser` → `same_cl`), and at **abstention → a named candidate** where the child panel is observable | §3.4/§3.5; the four-way reading of I7 (150 `we_are_coarser` clusters) |
| E3 | Where an adopted name does win, the **family** grade of a currently-`consistent` cluster can move `consistent` → `related`, because the frozen family ruler maps the author-side families (`cb`, `muscle`, …) to our coarse labels and does not know the finer term | the family ruler is the harness's R_fam (I10), frozen; the scope subset's before reading is `out/RECON_BEFORE_SCOPE.json` |
| E4 | The **named risk** is clause (b): if an adopted name cannot be mapped by the shipped label map, the judge grades it `unmappable_pred` and an abstention becomes an inconsistency — the exact shape the predecessor activation card measured | the activation card's own finding (16 of 17 entry names unresolvable) and the §1 fix |
| E5 | **A NO-GO is a valid outcome** and this card completes with the numbers if the rule fails | the brief, item 5 |

Nothing above is a prediction of a *pass*. E3 and E4 are the reasons the acceptance rule's clauses (a) and (b)
exist as separate criteria, and the answer may well be NO-GO.

## 7. Rollback path (pre-registered, mechanical)

1. **Kill switch (instant, no edit):** `EYEKB_ACT_CL56=0` restores the pre-flip default byte-for-byte; proven
   by replay at the same absolute path (§5e), with the pre-image verified identical to the parent blob.
2. **Switch removal (one commit):** restore `CL56_DEFAULT_LIBS = ()`, which is the pre-flip behaviour with the
   switch in either state; the increment stays registered and reachable by name only.
3. **Full revert:** `git revert` this card's commit. The pre-flip core is kept as a pre-image at
   `pre_images/eyekb_core.py.pre_cl56`, and the pre-flip label map at
   `pre_images/markers_cl_alignment_v2_unified.json.pre_cl56`; both sha256 recorded in `out/PREIMAGE.json`.
4. Independent of 1–3: the label-map extension is itself revertible on its own (one file, additive rows only).

## 8. Red lines carried from the card

- Cell Ontology conformance against the frozen snapshot I5; no fabricated term, no term the author never used
  for those cells.
- No scoring / admission-floor / tie-break / window change; no other library activated; no whitelist entry
  beyond this increment.
- `we_are_finer_pairs` is not folded into this adoption.
- Zero downloads, zero network (audit hook receipts > 0, events = 0).
- English for everything that mirrors into the repository. Every number carries the command that produced it.
  `NOT_RUN` and missing preconditions are never reported as pass.
- Commit locally; **DO NOT PUSH**. The commit hash is reported.

## 9. Resource discipline (binding)

`/home/ubuntu/Desktop/Hermes工作区/WORKSTATION_RULES_资源纪律_20260930.md` read first. One process's RSS is
measured before choosing concurrency; heavy steps run under
`systemd-run --user --scope -p MemoryMax=<measured+margin>G -p MemorySwapMax=2G`; concurrency ≤ min(8, cpu/2);
heartbeat every 30 min with the available reading; below 40 GiB nothing new starts.