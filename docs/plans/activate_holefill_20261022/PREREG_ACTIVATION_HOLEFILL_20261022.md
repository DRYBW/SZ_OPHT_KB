# Pre-registration — ACTIVATION of the literature hole-fill library (`holefill_v12`) on the default route

Date: 2026-10-22
Card: `t_be11fd4a` ("ACT-holefill — activate the literature hole-fill library on the default route
(owner-signed 2026-10-22)"), board `pi-briefing`
Predecessor wave: `docs/plans/holefill_v12_20261021/` (built and measured the library, registered it
**default OFF with no whitelist entry**) · precedent card: `docs/plans/activate_onfibro_20261022/`
(`t_42df17c2`, the one-day-old activation of `onfibro_v13`, whose instrument, acceptance shape,
kill-switch proof and re-registration list are reused here).

## 0. The decision, and what kind of record this is

The project owner was shown a two-item checklist — (1) enable the literature hole-fill library,
(2) adopt the 56 Cell-Ontology child-term candidates — and answered **"ok"** (2026-10-22).

This document is the pre-registration of an **owner-signed ACTIVATION decision**. It is **not an
audit pass**, it is **not** evidence that any accuracy claim is now true, and it does not convert any
withheld verdict of an earlier round into a pass. It records: what is being switched on, the
acceptance rule that decides whether the switch-on stands or is rolled back, the rollback path, and
the disclosure that every number produced here is an **IN-SAMPLE** reading on the same 28 public
volumes the library was selected against — a harm-line/regression reading, **not a validation and
not an accuracy claim**.

Written and on disk **before** any measurement of the flipped state. No number below was chosen
after seeing a result: every number in this document is already on disk from the predecessor wave
and is named with its source file.

## 1. What is being changed, exactly

| item | before (this card's base commit) | after (if the acceptance rule passes) |
|---|---|---|
| a whitelist for the new library in `mcp_server/eyekb_core.py` | absent — there is no `HOLEFILL_DEFAULT_LIBS` at all | `HOLEFILL_DEFAULT_LIBS = ("holefill_v12",)` |
| the guarded append in `_load_marker_dbs` (`library="all"`) | no branch | one branch: when the feature is on, `holefill_v12` is appended to the default `all` set |
| the kill switch | absent | `EYEKB_ACT_HOLEFILL` — `{0,false,off,no}` = OFF, unset/empty/anything else = ON (ACT-v6 discipline) |
| `kb/markers/markers_v12_holefill_increment.json` | 17 entries / 387 genes, registered default OFF | **byte-unchanged** (a wiring change, not a panel change) |
| the Cell Ontology terms | 17 entry names resolved against the in-repo CL release `2026-06-08` at build time | unchanged; re-checked, not assumed |

Nothing else moves: no other library is activated, no other whitelist gains an entry, no exclusion
row is withdrawn, **no admission floor / margin / tie-break / score / window is changed**, no other KB
body is edited. **No admission guard is added to the new library by this card**: the card's red line
is a knowledge-layer activation, and the measured behaviour of the raw merge is what the acceptance
rule below judges. (The `antseg_v10` eligibility guard is library-specific — it keys on that file's
basename — so it does not and will not act on this library.)

## 1b. A defect found BEFORE measuring, and the restoration this card must carry

**The library is not reachable by name on the shipped tree, and the registration row says it is.**

`MARKER_LIBS` in `mcp_server/eyekb_core.py` has **no entry for `holefill_v12`**. The predecessor
wave's own commit added one (`290cb984`, 2026-10-21 23:53, "+1 MARKER_LIBS line"), and a *later*
commit removed it as a side effect of appending a registration: commit **`0312016`** (2026-10-22
11:24, card `t_0c40c7b1`) replaced the dictionary's closing line

```
    "holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"}
```

with the `onfibro_v13` block — so the newly appended entry took the previous trailing entry's place
instead of following it. Reproduce with:

```
git show 290cb984 -- mcp_server/eyekb_core.py | grep 'holefill_v12": MARKER_DIR'   # the addition
git show 0312016 -- mcp_server/eyekb_core.py | grep '^-.*holefill_v12": MARKER_DIR' # the deletion
git show HEAD:mcp_server/eyekb_core.py | grep -c 'holefill_v12": MARKER_DIR'        # 0
/usr/bin/python3 -c "import sys;sys.path.insert(0,'mcp_server');import eyekb_core as c;print(sorted(c.MARKER_LIBS))"
```

Measured effect: `query_marker(library="holefill_v12")` raises
`ValueError: library must be one of … lensiris_v11|holefill_v12|onfibro_v13|all` — an error whose own
message names the library it refuses. Registry row **L1-26** states the opposite ("REGISTERED_DEFAULT_OFF
… reachable only via `library=holefill_v12`"), so the shipped record contradicts the shipped code. The
**default route is unaffected** (the library was never in a whitelist, and the dictionary entry is not
read on the `all` route), and nothing reported as a default-route reading changes.

Why this card carries the fix rather than deferring it: (i) the activation cannot be performed at all
without the entry — an entry appended to the whitelist while the library is unresolvable would be a
null; (ii) the card's own acceptance measurement is defined as the library's merge, which the missing
entry makes unmeasurable; (iii) restoring the entry is not "activating another library" — it restores
the registration the predecessor wave took and that row L1-26 still claims, and it leaves the default
route byte-identical (proven below, not asserted).

**Proof required of the restoration (recorded whatever the GO/NO-GO outcome):** with the entry
restored and the whitelist still empty in every state, the shipped default route must replay
**byte-for-byte identically** against the pre-restoration commit (`721/721` recorded cluster windows
and the full default battery, raw and canonical digests), `golden_721.py` must reproduce all 721
recorded rankings, and `library="holefill_v12"` must resolve to the 17 registered entries. The
restoration is recorded as a **defect fix with its evidence**, separately from the activation decision,
and the detection gap it exposes (no gate exercises explicit-route reachability against the
registration row; `golden_721` replays only the default route) is reported as a finding.

## 2. Frozen inputs (read-only; every number traceable to one of these)

| # | Path | Role |
|---|---|---|
| I1 | `/mnt/D/EyeKB/plans/oss_check_20261019/dl/results/<vol>/annotation_evidence_report.json` (28 files) | the recorded per-cluster query (`top_genes`) and the ranking the shipped code produced on 2026-10-18 |
| I2 | `/mnt/D/EyeKB/plans/oss_check_20261019/ledger_v1/ledger_cluster_level.tsv` | recorded reference labels (`ref_cell_type`, `ref_family`) and `n_cells`, one row per cluster (721) |
| I3 | `/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py` | the shipped service core (the file the flip edits) |
| I4 | `/home/ubuntu/EYEKB_REPO/kb/markers/markers_v12_holefill_increment.json` | the library under activation |
| I5 | `/home/ubuntu/EYEKB_REPO/kb/baselines/_tissue_class_crosswalk_v1.json` | the exclusion table (unchanged; the flip does not touch it) |
| I6 | `kb/ontology/cl/releases/2026-06-08/cl-base.obo` + `kb/markers/markers_cl_alignment_v2_unified.json` | the Cell Ontology release and the KB-class → CL map |
| I7 | `docs/plans/noregr_20261022/` | the predecessor harness: `scripts/n3_harness.py` + `scripts/wave_common.py` (rulers, replay engine, acceptance rule) — **the instrument reused here, unedited** |
| I8 | `docs/plans/holefill_v12_20261021/` | the wave that built the library: pre-registration, four measured arms, per-target readings, `out/golden_721_BEFORE.json` / `_AFTER.json`, `golden_721.py`, `measure_wave.py` |

Recorded set: **28 volumes / 721 clusters / 1,495,330 cells** (re-measured here, not assumed).

Interpreters: `/usr/bin/python3` for this wave's own scripts (stdlib only); `/home/ubuntu/training-venv/bin/python3`
for the repository's G3/G7 precondition and the tool-panel probe. Zero network, zero downloads:
`ledgers/net_audit.log` must carry hook load receipts > 0 and zero connecting/HTTP event lines.

## 3. Operationalisation

1. **Units.** The claim is judged on the recorded (volume, cluster) windows, **cell-weighted**,
   under the predecessor harness's four grades (`consistent` / `related` / `inconsistent` / `mixed`;
   `mixed` = the service returned no named candidate) and its Cell-Ontology reading
   (`same_cl` / `kb_coarser` / `kb_finer` / `truly_inconsistent` / `abstain` / `unmappable_*`).
2. **Three readings, all reported.** (i) the recorded volume declarations; (ii) the external tester's
   re-declarations (`CX16_tabula_sapiens_eye` → `ocular_surface`, `CX11_posterior_eye_atlas` →
   `ocular_surface`, as used by the predecessor card); (iii) the **default route itself** — the
   `library="all"` call with no `tissue` argument, which is the surface a default-route flip actually
   changes. A criterion that holds on one reading and fails on another is a failure.
3. **Before/after arms.** `before` = the tree without the whitelist member (the pre-flip default);
   `after` = the tree with it. On the flipped core the arms are separated by the switch
   (`EYEKB_ACT_HOLEFILL=0` vs unset) **and** by the measurement-only injection path
   (`inject: ["holefill_v12"]`), which the flip is proven to reproduce cluster by cluster.
4. **Attribution.** Every cluster whose ranking tuple `(top-1, n_shared, n_ranked)` moves is listed
   with its truth label (`ref_cell_type` / `ref_family`), its tissue, its cell count and its
   before/after answer, classified into pre-specified kinds:
   `library-gain` (the new top-1 is an entry of `holefill_v12`), `rank-shift` (top-1 unchanged, the
   candidate list moved), `unexpected` (top-1 changed to something that is **not** a `holefill_v12`
   entry). `unexpected` is never absorbed.
5. **The aggregate inconsistent share** is read twice: cell-weighted over all 721 clusters, and
   per dataset. It is the named failure mode of this class of change (the L1 precedent on record in
   `plans/INDEX.md` under `scorer_guard_20261020`: lowering abstention raised true contradictions
   from 17.95% to 29.32% and was ruled NO-GO). **Abstention falling is the intended effect of this
   library and is not a gain by itself.**

## 4. The acceptance rule (pre-registered; decides GO / NO-GO)

A **GO** requires **all four** of the following, measured on the flipped core, under **all three**
readings of §3.2:

- **(a) No dataset's cell-weighted `consistent` share falls.** For an activation, the predecessor's
  `PASS_ATTRIBUTED` is **not** sufficient: the verdict must be `PASS` on each reading. A fall on any
  dataset under any reading is a NO-GO (reported with its numbers).
- **(b) The aggregate cell-weighted `inconsistent` share must NOT rise** (overall, and on no dataset).
  A rise, however small, is a NO-GO: it is the failure mode named in §3.5, and it is not rescued by
  attribution.
- **(c) The movement must be attributable cluster by cluster**: every moved cluster classified into
  the pre-specified kinds of §3.4 with zero `unexpected`, and the count of moved clusters compared
  against the pre-registered expectation of §5.
- **(d) The kill switch must restore the pre-flip default byte-for-byte**, proven by replaying the
  recorded query set at the **same absolute path** (`721/721` cluster windows and the full default
  battery, raw and canonical digests identical).

The expectation is directional and is stated before the measurement: this library closes four
measured holes (§5), and it is a **merge into an unfiltered route** — the predecessor wave measured
exactly that merge as a net loss at cluster level (207 exact vs 190; **mismatch 100 → 134**), which
is why (b) exists as a separate criterion. If the measurement reproduces that pattern cell-weighted,
the answer is NO-GO, and a NO-GO reported with its numbers is a valid completion of this card.

## 5. Pre-registered expectations (all already on disk, from the predecessor wave)

From `docs/plans/holefill_v12_20261021/REPORT.md` §4/§5 (measured there with its own four arms; the
`MERGED` arm is the one this card's flip corresponds to):

| target of the library | pre-registered direction | predecessor reading (MERGED arm) |
|---|---|---|
| vascular endothelium (11 entries) | 0 → 11 truth clusters answered exactly (12 clusters / 20,420 cells) | 0 → 3 exact at the endothelium class, 11 in the single-library arm; blood-vessel partitions stay coarser |
| macrophage (4 entries) | 0 → 11 exact (16 clusters / 41,043 cells) | 7 exact under MERGED |
| rod panel 5 → 15 genes | clusters clearing ≥ 2 shared genes 11 → 21; exact 15 → 23 | 23 exact |
| RPE panel deepened | precise 11 → 14; the 6 RPE→melanocyte confusions stay 6 in every arm | 13 exact under MERGED |
| corpus-level negative arms | `NEW` alone and `GUARDED` both worse than BASE | exact **+17**, mismatch **+34** under MERGED |

The committed library body is unchanged by this card, so the arms must reproduce these directions on
the *shipped default route*; a divergence is reported, not smoothed.

## 6. Rollback path (pre-registered, mechanical)

1. **Kill switch (instant, no edit):** `EYEKB_ACT_HOLEFILL=0` restores the pre-flip default
   byte-for-byte; proven by replay at the same absolute path (§4d) with the pre-image verified
   identical to the parent commit's blob.
2. **Switch removal (one commit):** restore `HOLEFILL_DEFAULT_LIBS = ()` (the tuple the flip adds),
   which is the pre-flip behaviour with the switch in either state; the library stays registered and
   reachable by name only.
3. **Full revert:** `git revert` this card's commit; the pre-flip core is kept as a pre-image at
   `pre_images/eyekb_core.py.pre_activation` (sha256 recorded in `out/PREIMAGE.json`).

## 7. Red lines carried from the card

- Cell Ontology conformance: **every** entry name of the library must be resolvable against the
  in-repo snapshot; no fabricated term (re-checked in this card, not inherited).
- No other library activated; no whitelist entry beyond `holefill_v12`; no scoring / admission-floor
  / tie-break / window change.
- Zero downloads, zero network (audit hook receipts > 0, events = 0).
- English for everything that mirrors into the repository. Every number carries its command.
  `NOT_RUN` and missing preconditions are never reported as a pass.
- Commit locally; **DO NOT PUSH**; the commit hash is reported.

## 8. Resource discipline (binding)

`/home/ubuntu/Desktop/Hermes工作区/WORKSTATION_RULES_资源纪律_20260930.md` read first. One process RSS
is measured before choosing concurrency; heavy steps run under
`systemd-run --user -p MemoryMax=<measured+margin>G -p MemorySwapMax=2G`; concurrency ≤ min(8, cpu/2);
heartbeat every 30 min with the available reading; below 40 GiB nothing new starts.