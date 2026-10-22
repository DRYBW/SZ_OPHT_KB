# Pre-registration — ACTIVATION of the optic-nerve fibroblast carrier (`onfibro_v13`) on the default route

Date: 2026-10-22
Card: `t_42df17c2` ("L7 ACTIVATE onfibro_v13 on the default route"), board `pi-briefing`
Predecessor wave: `docs/plans/noregr_20261022/` (card `t_0c40c7b1`), which built the carrier, measured
it through the regression harness and left it **registered default-OFF with an empty whitelist**.

## 0. The decision, and what kind of record this is

The project owner authorised the activation in writing, verbatim: **"载体并进默认路由"** — merge the
carrier library `onfibro_v13` into the default route.

This document is the pre-registration of an **activation decision**. It is **not** an audit pass, and
it does not convert the withheld verdicts of earlier rounds into passes. It records: what is being
switched on, the acceptance rule that decides whether the switch-on stands or is rolled back, the
rollback path, and the disclosure that any number produced here is an **IN-SAMPLE** reading on the
same volumes the carrier was selected on — a harm-line/regression reading, **not a validation and not
an accuracy claim**.

Written before any measurement of the flipped state. No number below was chosen after seeing a
result; the only numbers in this document are ones already on disk from the predecessor wave, and
each is named with its source.

---

## 1. What is being changed, exactly

| item | before (commit 16349f6) | after (this card) |
|---|---|---|
| `ONFIBRO_DEFAULT_LIBS` in `mcp_server/eyekb_core.py` | `()` — empty by design | `("onfibro_v13",)` |
| the guarded append in `_load_marker_dbs` | appends nothing | appends `onfibro_v13` when the feature is on |
| `_onfibro_act_enabled()` | `{0,false,off,no}` = OFF, unset = ON (ON injected nothing) | **unchanged semantics, now consequential**: unset/other = ON = the carrier is part of `all`; `{0,false,off,no}` = OFF = byte-identical pre-flip default |
| the carrier file `kb/markers/markers_v13_onfibro_increment.json` | one entry, `Fibroblast`, CL:0000057, 12 genes | **byte-unchanged** (the flip is a wiring change, not a panel change) |
| the Cell Ontology term | CL:0000057 resolved against the in-repo release | unchanged; re-measured, not assumed |

Nothing else moves: no other library is activated, no other whitelist entry is added, no exclusion
row is withdrawn, no score term, admission floor (`n_shared >= 2`), margin or tie-break changes, and
no other KB body is edited.

## 2. Frozen inputs (read-only; every number traceable to one of these)

| # | Path | Role |
|---|---|---|
| I1 | `/mnt/D/EyeKB/plans/oss_check_20261019/dl/results/<vol>/annotation_evidence_report.json` (28 files) | the recorded per-cluster query (`top_genes`) and the ranking the shipped code produced on 2026-10-18 |
| I2 | `/mnt/D/EyeKB/plans/oss_check_20261019/ledger_v1/ledger_cluster_level.tsv` | recorded reference labels (`ref_cell_type`, `ref_family`) and `n_cells`, one row per cluster (721) |
| I3 | `/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py` | the shipped service core (the file the flip edits) |
| I4 | `/home/ubuntu/EYEKB_REPO/kb/markers/markers_v13_onfibro_increment.json` | the carrier under activation |
| I5 | `/home/ubuntu/EYEKB_REPO/kb/baselines/_tissue_class_crosswalk_v1.json` | the exclusion table (unchanged; the flip does not touch it) |
| I6 | `/home/ubuntu/EYEKB_REPO/kb/ontology/cl/releases/2026-06-08/cl-base.obo` + `kb/markers/markers_cl_alignment_v2_unified.json` | the Cell Ontology release and the KB-class → CL map |
| I7 | `/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/` | the predecessor wave: its pre-registration, its harness (`scripts/n3_harness.py`, `scripts/wave_common.py`), its four measured arms and its default-face device (`scripts/n6_default_face.py`, `scripts/n6b_replay_route.py`) — **the instrument reused here** |

Recorded set: **28 volumes / 721 clusters / 1,495,330 cells** (the predecessor wave measured this
shape; it is re-measured, not assumed).

Interpreters: `/usr/bin/python3` for this wave's own scripts (stdlib only); `/home/ubuntu/training-venv/bin/python3`
for the repository's G3/G7 precondition and for `tests/probe_tool_panel_identity.py`.
Zero network, zero downloads: `ledgers/net_audit.log` must carry hook load receipts > 0 and zero
connecting/HTTP event lines.

## 3. Operationalisation

### 3.1 The arms (a "change" is a declared replay overlay; nothing is edited by the harness)

| arm | meaning |
|---|---|
| `PRE` | the **parent commit's** core bytes swapped in place at the same absolute path, default route (`library="all"`, no `tissue` argument, no switch set) — the shipped pre-flip face |
| `KILL` | the **flipped** core in place, `EYEKB_ACT_ONFIBRO=0` — must be byte-identical to `PRE` |
| `FLIP` | the **flipped** core in place, switch unset (the new default) — the activated face |
| `CTRL-INJECT` | the flipped core, feature OFF, with the predecessor wave's measurement-only injection overlay (`inject:["onfibro_v13"]`) — the arm the predecessor wave measured as R2/R3; the flipped default must reproduce it |

The kill-switch comparison (`PRE` vs `KILL`) and the delta count (`PRE` vs `FLIP`) are both taken
**at the same absolute path in the same working tree**, so every path-carrying field of a response is
identical and the only variable is the file's bytes plus the switch value.

### 3.2 Rulers (inherited unchanged from the predecessor wave; applied identically to every arm)

`ref_family` = I2 `ref_family`, never recomputed. Four cell-weighted grades — `consistent` (family
match), `related` (same cell under another name, or a coarser/finer CL term), `inconsistent`, `mixed`
(abstention) — plus the independent Cell Ontology reading (`same_cl` / `kb_coarser` / `kb_finer` /
`truly_inconsistent` / `abstain`). Declaration sets: the **recorded** declarations (primary) and the
external tester's re-declarations (`CX16_tabula_sapiens_eye`, `CX11_posterior_eye_atlas` →
`ocular_surface`; secondary). Both are reported; neither is smoothed into the other.

### 3.3 The acceptance rule (pre-registered; a fall is a rollback, not an attribution)

> **A1 — no dataset falls.** Over the recorded 28 volumes × 721 clusters, cell-weighted, the flip may
> not lower the `consistent` share of **any** dataset, under **either** declaration set. Because this
> card *activates* rather than proposes, the predecessor's `PASS_ATTRIBUTED` verdict is **not
> sufficient here**: the verdict must be `PASS`. Any fall ⇒ the activation does not stand; the flip is
> reverted through the rollback path in §5 and the fall is reported cluster by cluster, cell-weighted,
> with the named cause.

> **A2 — the movement is attributable cluster by cluster.** Every cluster whose ranking moves must be
> listed with its truth label (`ref_cell_type` / `ref_family`), its `n_cells`, and its before/after
> answer (`top` + `n_shared` + library). Each moved cluster must be classifiable as one of:
> `carrier-gain` (a fibroblast-family coarse answer appears, or the carrier entry moves a candidate the
> family owns), `rank-shift` (top-1 unchanged, only the candidate list shifted), or **`unexpected`** —
> and an `unexpected` entry is a **compatibility item that is reported explicitly, never absorbed**.

> **A3 — the kill switch restores the pre-flip default byte-for-byte.** With the flip in place,
> `EYEKB_ACT_ONFIBRO=0` must reproduce the pre-flip default **byte-for-byte**, proved by replaying the
> recorded query set at the **same absolute path** and comparing raw response bytes (`PRE` vs `KILL`),
> for both the 721 cluster windows and the battery arm (page listing + `cell_type` mode over the 76
> labelled classes × 3 species arguments). Canonical hashes are reported alongside the raw ones so the
> reading is comparable with the predecessor wave's.

> **A4 — the change is the only change.** The default-face delta (`PRE` vs `FLIP`) must contain
> **nothing but the intended movement**: the exact count of recorded queries whose raw response bytes
> moved is reported, and every moved query must be one whose ranking moved and whose movement is
> classified as `carrier-gain` (or `rank-shift` with the carrier entry named). The repository's
> tool-panel probes are run under both cores: the legacy five-tool panel digests must be unchanged; **if
> the legacy panel moves, that is recorded as a compatibility-contract item, not absorbed**.

> **A5 — re-registration in the same commit.** Because this changes default bytes on purpose, the
> affected registrations are re-taken in the same commit: carrier row **L1-30**, the service-core
> delivery row **L1-11M**, `docs/RELEASE_IDENTITY.json` (+ `docs/RELEASE_MANIFEST_v1.json`), a **new
> 27-column change-control instance row** carrying parseable anchors per G6 rule R2 (and the G6
> precondition registration required by rule R8), and `docs/W3_MANIFEST.sha256` **LAST**. Any other
> registry row the gates report as drifted is re-taken too; none is dispensed wholesale.

> **A6 — gates green in a clean clone.** G3 / G4 / G5 / G6 / G7 / G8 must be green in the author tree
> **and again inside a clean clone** of the commit under test. If a frozen identity anchor moves (the
> G4 three byte anchors, or a 906-/740-request default-face baseline), it is re-anchored **with the
> reason recorded and the pre-image kept**; **no criterion is weakened to make a gate pass**.

> **A7 — red lines.** The carrier's entry name stays resolvable against the in-repo snapshot
> (CL:0000057 `fibroblast`) — measured, not assumed; no other KB body changes; no other library
> activated; no other whitelist entry; no score / admission-floor / tie-break change (the carrier is a
> **class carrier**, not a scoring change); zero network (receipts > 0, connecting events = 0).

> **A8 — disclosure inside the artefact.** The report states in its own body that the reading is
> IN-SAMPLE on the volumes the carrier was selected on, that the carrier is a family-level (coarse)
> answer, that it clears the ≥2 shared-gene bar only *at* the bar, and that no accuracy claim is made.

### 3.4 Pre-registered expectation (written before measuring)

Expected: `FLIP` reproduces the predecessor wave's R2/R3 arms — overall `consistent` **+1.69pp
(recorded declarations) / +1.62pp (tester declarations)**, 45 clusters moving, and the motivating
cluster `CX15_optic_nerve_all` c31 (1,822 cells, truth `fibroblast`) returning to a family-consistent
answer at `n_shared=2`; no dataset falling. **If a dataset falls, or if the flip's movement differs
from the injection arm's, that is reported as a refutation of this expectation**, not smoothed over.

## 4. Rollback path (three independent routes, all pre-registered)

1. **Switch (fastest, no commit needed):** `EYEKB_ACT_ONFIBRO=0` restores the pre-flip default —
   claimed byte-for-byte and proved by A3's same-path replay, not asserted.
2. **Registration form:** restoring `ONFIBRO_DEFAULT_LIBS = ()` and the pre-flip comment block
   returns the file to the registered pre-flip state; the pre-image of the pre-flip file is kept at
   `docs/plans/activate_onfibro_20261022/pre_images/eyekb_core.py.pre_activation` with its sha256
   recorded, so the restore is verifiable without git.
3. **Commit-level:** `git revert <this commit>`; the pre-flip blobs remain the committed objects at
   16349f6.

## 5. What this card will NOT do

1. It will not change the carrier's panel, the exclusion table, the score, the admission floor
   (`n_shared >= 2`), the margin or the tie-break.
2. It will not activate any other library and will not add any other whitelist entry.
3. It will not present the in-sample reading as a validation, and will not claim accuracy.
4. It will not weaken a gate criterion, and will not re-anchor a frozen identity anchor without
   recording the reason and keeping the pre-image.
5. It will not push. Commit locally only; the commit hash is reported.
6. It will not treat `NOT_RUN` or a missing precondition as a pass.

## 6. Reporting

Every number carries the command that produced it. `NOT_RUN` is reported as `NOT_RUN`. Disconfirming
results are reported as such. English for everything that mirrors into the repository.