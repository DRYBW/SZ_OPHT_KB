# Pre-registration -- no-regression audit of the tissue exclusion table, the optic-nerve fibroblast carrier, and the "accuracy must not fall" machine gate

Date: 2026-10-22
Card: `t_0c40c7b1` ("L6 no-regression"), board `pi-briefing`
Owner requirement being operationalised: *everything we ship must improve accuracy or at least not
lower it; if it falls anywhere, find exactly where.*

**Disclosure (ordering).** The card mandates reproducing the source-of-truth finding *before*
anything else, and read-only inventory of the tree. That reproduction plus read-only file
inventory happened before this document was written. Everything **new** this card decides -- the
carrier fix, the all-tissue sweep, the harness ruler, the acceptance gate, the default-face
identity claim -- is pre-registered below, with the pre-registered judgement written before any of
those measurements was run. No number in this document was chosen after seeing a result.

---

## 1. Questions

Q1 (the known drop). Is `CX15_optic_nerve_all` 44.40% -> 41.87% (cell-weighted, -2.53pp) wholly
attributable to one cluster, one row and one mechanism -- the exclusion of
`Limbus_Sclera_fibroblast_C1` for `optic_nerve` removing a family's only reachable carrier?

Q2 (the general defect). Does the same pattern -- *a tissue excludes a foreign-specific class while
the legitimate carrier for that family in that tissue is too thin to answer, so an abstention
replaces a coarse-but-family-correct answer* -- occur on any other (`tissue`, exclusion row) pair
inside the recorded 28-volume / 721-cluster set? And what is the **all-tissue** harm line of the
exclusion rows, as opposed to the retina-only harm line they were signed off on?

Q3 (the gate). Can "does not lower accuracy" be made machine-checked over the recorded set, such
that a change whose cell-weighted consistent share falls on any dataset cannot be reported complete
without a named cluster + named cause + named row/panel recorded in the artefact?

---

## 2. Frozen inputs (read-only; every number traceable to one of these)

| # | Path | Role |
|---|---|---|
| I1 | `/mnt/D/EyeKB/plans/oss_check_20261019/dl/results/<vol>/annotation_evidence_report.json` (28 files) | the recorded per-cluster `top_genes` query and the ranking as produced by the shipped code on 2026-10-18 |
| I2 | `/mnt/D/EyeKB/plans/oss_check_20261019/ledger_v1/ledger_cluster_level.tsv` | recorded reference labels (`ref_cell_type`, `ref_family`) and the recorded prediction/grade, one row per cluster (721 rows) |
| I3 | `/home/ubuntu/EYEKB_REPO/kb/baselines/_tissue_class_crosswalk_v1.json` | the exclusion table under audit (12 tissues) |
| I4 | `/home/ubuntu/EYEKB_REPO/kb/markers/*.json` | the marker libraries (panel content; `markers_membrane_v1.json` carries the generic `Fibroblast`) |
| I5 | `/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py` | the shipped service core (`query_marker`, the tissue-scope filter, the increment guard) |
| I6 | `/home/ubuntu/EYEKB_REPO/kb/ontology/cl/releases/2026-06-08/cl-base.obo` + `/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json` | the Cell Ontology release and the KB class -> CL map, for the ontology ruler |
| I7 | `/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/tissue_scope/{GATE_A3.json,gate_a3_no_collateral.py,REPORT_TISSUE_SCOPE_v2.0_DEFAULT_ON.md}` | the *previous* harm-line measurement and its ruler, which this card audits |
| I8 | `/mnt/D/EyeKB/plans/zjy_feedback_20261021/from_oss/cross_dataset_summary.csv` | the external tester's 28-volume re-evaluation (per-dataset consistent/related/inconsistent/mixed + cells) |
| I9 | `/mnt/D/EyeKB/plans/pi_asks_20261021/probe_opticnerve_scope_ab.py` | the source-of-truth probe reproduced in step 1 |

Interpreters: `/home/ubuntu/training-venv/bin/python3` reads this repository's `numpy`/`pydantic`.
`/usr/bin/python3` is used for the wave's own scripts where they are dependency-free (the wave's
scripts import only the stdlib + the repo).

Zero network, zero downloads (audit hook, `EVENT` lines must be 0, load receipts must be > 0).

---

## 3. Operationalisation

### 3.1 The recorded set

`SET` = every ordered pair `(volume, cluster)` that has BOTH a set of `top_genes` in I1 and a truth
row in I2. The card's "28 volumes x 721 clusters": the count is measured, not assumed (721 is
asserted by I2; the intersection is what is actually used and will be reported).

Each element carries: the exact recorded gene list, the volume's declared `tissue` and `species`
(from I1 `inputs`), the recorded reference `ref_cell_type` / `ref_family`, and `n_cells` (for
cell-weighting).

### 3.2 The change model (what "a change" means to the harness)

The harness never edits anything. A "change" is a *declared replay overlay* applied inside the
harness process only:

| overlay | meaning |
|---|---|
| `env:VAR=VAL` (repeatable) | set an environment switch for the replayed calls |
| `inject:<library>` | measurement-only merge of a registered-but-OFF marker library into the `all` route (loader monkeypatch inside the harness process, exactly the `holefill_v12` wave's `MERGED` arm) |
| `excl:withdraw=<tissue>:<class>` | withdraw one exclusion row at replay time |
| `excl:withdraw-all-new` | withdraw every row added by the `antseg_fill_20261020` increment |

The harness's own pre-image (its script sha256) and the sha256 of I1/I2 are recorded in every run
metadata, so any reported number can be recomputed from the frozen inputs.

### 3.3 Rulers (frozen here, applied identically to every arm)

`ref_family(cluster)` = I2 `ref_family` (recorded truth, never recomputed).

`fam_of(label)` for a predicted KB class label, in order:
1. I2-derived lookup: the recorded `pred_family` for that base label where the label occurs in I2
   (measured from the recording, not invented);
2. else the frozen crosswalk `/mnt/D/EyeKB/plans/oss_check_20261019/kb_family_crosswalk_v2.json`
   inverted, but only where exactly one family claims the label;
3. else `other`.
The ruler's own agreement with I2's recorded `pred_family` column is reported; disagreement is
disclosed as a ruler difference, not counted against any product.

`cl_of(label)` = I6 map (`markers_cl_alignment_v2_unified.json`), plus the `cl_id` carried by the
v10 increment entries; ancestors computed from the in-repo `cl-base.obo`.

**R_fam (primary; this is the card's "consistent share")** -- four cell-weighted grades:

| grade | rule |
|---|---|
| `consistent` | a candidate was returned and `fam_of(top1) == ref_family` |
| `related` | a candidate was returned, `fam_of(top1) != ref_family`, and `cl_of(top1)` and `cl_of(ref_cell_type)` are equal or in an ancestor/descendant relation (same cell under another name, or a coarser/finer ontology term) |
| `inconsistent` | a candidate was returned and neither of the above |
| `mixed` | no candidate was returned (abstention) |

**R_cl (secondary)** -- per cluster: `same_cl` / `kb_coarser` / `kb_finer` / `truly_inconsistent` /
`abstain` / `unmappable`.

Cell-weighted shares are `sum(n_cells of clusters in grade) / sum(n_cells)`, per dataset and overall.

### 3.4 Derived readings

* per-dataset and per-cluster ranking deltas: `top1`, `n_shared`, `n_ranked` before vs after;
* cells moved in each direction (a 4x4 grade transition matrix, cell-weighted);
* the "carrier-loss" signature: `before != None` and `after == None` and the before top-1's base
  class is in the tissue's `excluded_classes`.

---

## 4. Pre-registered judgements (written before measuring)

**G1 (Q1) -- the known drop is reproduced, one cluster, one row, one mechanism.** PASS iff a
replay that flips only `EYEKB_TISSUE_SCOPE` changes the top-1 of exactly one `optic_nerve` cluster
whose truth family is `fibro`, that cluster holds `n_cells` cells with
`n_cells / 71997 == 2.53% +/- 0.01pp`, and the removed candidate is the crosswalk's
`Limbus_Sclera_fibroblast_C1` row. Also recorded: the shared-gene count between the cluster's
window and the generic `Fibroblast` panel, which the source-of-truth narrative states as 1; **that
count is measured, and a value other than 1 is reported as a correction to the narrative, not
forced to 1.**

**G2 (Q2) -- the sweep.** For every (tissue, exclusion row) pair of I3, report the number of
recorded clusters for which that row participates in a carrier loss (3.4). PASS (the audit is
complete) iff every exclusion row of all 12 tissues is enumerated with its implicated-cluster count
and its implicated cluster set, including rows with count 0. A row is *registered as a live defect*
iff it removes a family's only reachable carrier for at least one recorded cluster whose
pre-withdrawal answer was family-consistent.

**G3 (Q2) -- the corrected all-tissue harm line.** Recompute the harm line of the withdrawal-ON
change over ALL tissues using R_fam, and contrast it with the previously recorded harm line (I7,
which used a family ruler derived from the raw KB class name). PASS iff the corrected line is
reported per tissue with cell-weighted consistent shares before and after, and every cluster whose
grade fell is named with its previous and new answer. **Pre-registered expectation: the
previously recorded "collateral 0" is falsified**, because I7's ruler scores a coarse-but-correct
foreign-named answer as already-wrong, and at least one such cluster (CX15/c31) is recorded as
family-consistent in I2 (`fam_eq_raw=True`). If the corrected line is also zero harm, that is
reported as a *refutation of this expectation*, i.e. the card's premise is wrong -- it will not be
smoothed over.

**G4 (Q1 fix) -- the carrier fix works and does not lower anything.** The fix is a new, registered
default-OFF marker library carrying a legitimate carrier for the fibroblast family on the optic
nerve side. PASS iff, with the library merged (overlay `inject:`), (a) `CX15_optic_nerve_all`
cluster 31 returns a family-consistent answer, (b) no dataset's cell-weighted `consistent` share
falls relative to the same-arm baseline, and (c) any cluster whose top-1 changes is listed. The
class name of every new entry must resolve to a Cell Ontology term (measured against I6). **New
panels are registered default-OFF with an empty whitelist** -- activating a default face is a
separate PI decision and is explicitly NOT made here.

**G5 (red line) -- the default face is byte-identical.** PASS iff, on the recorded query set
replayed at the SAME absolute path with the fix registered, the response bytes of the default route
(no `tissue` argument, no new switch set) are identical before and after the change to the shipped
code, and the repo's legacy tool-panel identity probe (`tests/probe_tool_panel_identity.py`) is
unchanged and still passes.

**G6 (Q3) -- the gate is mechanical.** PASS iff the harness, given (arm_before, arm_after), returns
FAIL whenever any dataset's cell-weighted `consistent` share falls and the run's attribution file
does not name, for that dataset, a cluster + a cause + a row/panel; and returns PASS (with the
attribution restated in the artefact) when it does. The acceptance rule is implemented as code in
the harness, not as a sentence in a report. The harness's own pre-image is stored so its numbers
are re-derivable.

**G7 -- the gate is not vacuous.** PASS iff the harness's acceptance rule is exercised twice in the
same run: once on a synthetic input containing an unattributed drop (must FAIL) and once on the
same input with the attribution supplied (must PASS). A gate that only ever passes is not evidence.

---

## 5. What this card will NOT do

1. It will not withdraw the `optic_nerve` exclusion row (that would put a limbal/scleral identity
   into the optic nerve); the row stays, with provenance, row-by-row withdrawable.
2. It will not change the score, the admission floor (`n_shared >= 2`), the margin, or any
   tie-break. The harness is measurement only.
3. It will not activate any new panel, and it will not change the default response bytes.
4. It will not push. Commit locally only; the commit hash is reported.
5. It will not treat `NOT_RUN` or a missing precondition as a pass.

## 6. Reporting

Every number in the report carries the command that produced it. Disconfirming results are
reported as such. English for anything mirroring into the repository.