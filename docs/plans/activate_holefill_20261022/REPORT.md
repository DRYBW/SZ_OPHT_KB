# Activation report — the literature hole-fill library (`holefill_v12`) on the default route

Card: `t_be11fd4a` (ACT-holefill) · board `pi-briefing` · 2026-10-22
Pre-registration: `PREREG_ACTIVATION_HOLEFILL_20261022.md` (sha256 `79ef237cbac7dcf94435d4d05c837fafaed372ba5dd6e7eebe4be62a7e49451c`,
written and on disk before any measurement of the flipped state — ordering recorded in `out/PREIMAGE.json`).
Precedent reused: `docs/plans/activate_onfibro_20261022/` (the one-day-old `onfibro_v13` activation) — instrument,
acceptance shape, kill-switch proof, delta census and gate discipline.
Interpreter: `/usr/bin/python3` for this wave's scripts (stdlib only); `/home/ubuntu/training-venv/bin/python3`
for the repository's tool-panel probe. Zero network, zero downloads (audit-hook receipts in
`ledgers/net_audit.log`, event lines = 0).

**This card did NOT activate the library. The acceptance rule failed, and a NO-GO reported with its
numbers is the outcome the card pre-registered as valid.**

---

## 0. One-line answers

1. **The activation was measured, not argued, and it fails the pre-registered rule.** Over the recorded
   28 volumes / 721 clusters / 1,495,330 cells, cell-weighted: the `consistent` share falls
   **42.544 % → 39.230 % (−3.314 pp)** (recorded declarations), **−3.316 pp** (the external tester's
   re-declarations) and **43.228 % → 39.853 % (−3.375 pp)** on the default route itself; **14 of 28
   datasets fall**, and the aggregate `inconsistent` share **rises +12.725 pp / +12.986 pp / +13.063 pp**
   — the exact failure mode the rule was written against (the L1 precedent: abstention 23.25 % → 5.55 %
   came with contradictions 17.95 % → 29.32 % and was ruled NO-GO).
2. **The movement is fully attributed**: 255 clusters move (636,656 cells), **92 of them change their top-1
   answer to a library entry** and 163 move at the ranking-tuple level with the same top-1; **0 unexplained**.
   The flipped default reproduces the measurement-only injection arm on **721/721** clusters, so the wiring
   change is the only change.
3. **The kill switch passes**: with the flip in place, `EYEKB_ACT_HOLEFILL=0` reproduces the parent commit's
   core on **721/721** recorded cluster windows and **229/229** battery calls, raw and canonical, at the same
   absolute path. The same measurement proves this card's registration restoration is default-neutral.
4. **The instrument cannot read the library's own answers as such, and that does not change the verdict.**
   The frozen KB→CL map carries the 76 shipped class names; **16 of the library's 17 entry names are the Cell
   Ontology labels themselves and are absent from it**, so 70 of the 90 takeovers were graded
   `unmappable_pred`. Re-read with a resolver that falls back to each entry's own `cl_id`, `same_cl` rises
   **39.707 % → 42.261 %** *and* `truly_inconsistent` rises **21.024 % → 24.973 %** (46 of the 90 takeovers
   land on a cluster whose author class is a genuinely different class). Criterion (b) fails under **both**
   rulers: the refusal is not a labelling artefact. **No criterion was weakened to make a gate agree.**
5. **The library's registration line was missing from the shipped tree, and this card had to restore it to be
   able to measure anything at all.** Commit `0312016` (card `t_0c40c7b1`) had dropped the
   `"holefill_v12"` entry from `MARKER_LIBS` as a side effect of appending the next registration, so
   `library="holefill_v12"` raised `ValueError` while registry row **L1-26** claimed it was reachable by
   name. Restored, and the restoration is proven neutral: default route **721/721 + 229/229 byte-identical**,
   `golden_721` 721/721 in both switch arms, and the explicit route now resolves (`out/RESTORE.json`).
6. **A concurrent card edited the same file in the same window** (see §7): the final working-tree state is a
   three-party merge — shipped bytes + this card's restoration + that card's own registration, with this
   card's activation wiring **removed** — proven to replay the parent commit's default route byte-for-byte.
7. **The reading is IN-SAMPLE.** The library was selected on the same 28 public volumes it was measured on:
   this is a coverage/harm reading, not a validation, not an independent test, and not an accuracy claim.

---

## 1. The decision, and what kind of record this is

The project owner was shown a two-item checklist — (1) enable the literature hole-fill library,
(2) adopt the 56 Cell-Ontology child-term candidates — and answered **"ok"** (2026-10-22). Recorded here
**as an owner-signed activation decision**, not as an audit pass and not as evidence that any accuracy
claim is now true.

The pre-registration (`PREREG_ACTIVATION_HOLEFILL_20261022.md`, §4) fixed the acceptance rule before any
measurement: **(a)** no dataset's cell-weighted `consistent` share may fall (`PASS` required; the
predecessor's `PASS_ATTRIBUTED` is not sufficient for an activation), **(b)** the aggregate `inconsistent`
share must not rise, **(c)** every moved cluster must be attributed cluster by cluster with zero
`unexpected`, **(d)** the kill switch must restore the pre-flip default byte-for-byte. A GO requires all
four under **all three** readings (recorded declarations, the tester's re-declarations, and the default
route with no `tissue` argument).

## 2. What was changed, and what was measured

| | |
|---|---|
| library under decision | `kb/markers/markers_v12_holefill_increment.json` — 17 entries / 387 genes, **byte-unchanged** by this card |
| the flip | `HOLEFILL_DEFAULT_LIBS = ("holefill_v12",)` + `_holefill_act_enabled()` + one guarded append in `_load_marker_dbs`, switch `EYEKB_ACT_HOLEFILL` |
| the flip's own record | `out/FLIP.json`: pre-image `95aa15be1f9e25a9…` → flipped `bd45c6b93ec73cd6…`, 37 added / 0 removed lines, 2 hunks; undoing the two declared replacements reproduces the pre-image **byte-for-byte** (`inverse_replace_restores_pre_image = true`), the only whitelist that changed is `HOLEFILL_DEFAULT_LIBS`, and the imported module reports `library="all"` **with** `holefill_v12` when the feature is on and **without** it when off |
| the flip's end state | **removed** (NO-GO). The library stays registered default-off and reachable by name only |
| Cell Ontology conformance (red line) | `out/CL_CONFORMANCE.json`: **17/17 entry names resolve to their declared CL ids against the in-repo release `2026-06-08`**; no fabricated term |
| zero network | audit hook loaded, `ledgers/net_audit.log` event lines = 0 |
| no scoring change | no threshold, admission floor, tie-break or window touched; no other library activated; no whitelist entry beyond `holefill_v12` (this flip added one constant that exists only for this library and removed it again) |

## 3. The measurement (instrument reused, unedited)

`docs/plans/noregr_20261022/scripts/n3_harness.py` + `wave_common.py`, reused byte-for-byte with **one declared
extension**: the harness's switch-hygiene tuple gained the name `EYEKB_ACT_HOLEFILL` (the newest switch in the
service), so an arm's value cannot leak into the next arm. No rule, ruler, grade or threshold changed.

### 3.1 Overall, cell-weighted (`out/FLIP_MEASUREMENT.json`, arm F1 = recorded declarations)

| grade | before % | after % | delta pp |
|---|---:|---:|---:|
| consistent | 42.544 | 39.230 | **−3.314** |
| related | 16.936 | 13.030 | −3.906 |
| inconsistent | 19.843 | 32.568 | **+12.725** |
| mixed (no named answer) | 20.676 | 15.172 | −5.504 |

Abstention falls (the intended effect) and contradictions rise much faster — the L1 pattern, reproduced.

### 3.2 The three readings, and the datasets that fall

| reading | `consistent` delta | `inconsistent` delta | verdict (a) |
|---|---:|---:|---|
| F1 recorded declarations | **−3.314 pp** | **+12.725 pp** | FAIL |
| F2 tester re-declarations (`CX16`, `CX11` → `ocular_surface`) | **−3.316 pp** | **+12.986 pp** | FAIL |
| D default route (no `tissue` argument) | 43.228 → 39.853 (**−3.375 pp**) | 24.205 → 37.268 (**+13.063 pp**) | FAIL |

**14 datasets fall** under the recorded declarations (`CX01_retina_snRNA`, `CX02_adult_retina`,
`CX03_retina_multiome`, `CX04_cowan_fovea`, `CX04_cowan_organoid`, `CX04_cowan_periphery`,
`CX09_voigt_RPE_choroid`, `CX10_hiPSC_RPE`, `CX12_ocular_surface_snRNA`, `CX13_central_cornea`,
`CX16_tabula_sapiens_eye`, `PRE_GSE268630`, `PRE_OA-D001`, `PRE_OA-D068`), the worst being
`CX04_cowan_periphery` 54.239 % → 13.140 % with `inconsistent` **+62.469 pp**.
**25 datasets** show a rising `inconsistent` share. The control arm F3 (measurement-only injection) reports
the same numbers, and the flipped default reproduces that arm **721/721**.

### 3.3 Attribution (clause c — this clause passes)

255 clusters / 636,656 cells move: **90 library takeovers** (`Rod → retinal rod cell`, `Endo → endothelial
cell`, `→ macrophage`, `RPE → retinal pigment epithelial cell`, `Mac_Tissue → macrophage`, `MG → macrophage`,
…), **163 rank shifts** with the top-1 unchanged, **0 unexplained**. `l2`'s first classifier keyed on a
`holefill_v12::` name prefix and therefore mislabelled all 90 takeovers as `unexpected`; a diagnostic run
(`scripts/diag_top1_moves.py`, `out/DIAG_TOP1_MOVES.json`) caught it **before the ruling was written** and the
classifier now resolves ownership from the response's `library` field and the library's own class list. The
corrected reading is reported here; the mis-classification is documented rather than quietly fixed.

Takeover quality against the author's own label (frozen judge): `unmappable_pred` 70, `same_cl` 7,
`truly_inconsistent` 13. **Harm line** (reported whether or not a criterion trips): **117,006 cells moved down
a grade (7.8 %)**, 34 clusters graded down, e.g. `CX02_adult_retina c4` (12,902 cells, truth *retinal rod
cell*) `Rod → retinal rod cell`, graded `consistent → inconsistent`; `CX10_hiPSC_RPE c0` (6,299 cells)
`RPE → retinal pigment epithelial cell`.

### 3.4 The four pre-registered directions, as measured

| target | pre-registered direction | measured on the shipped route | predecessor wave |
|---|---|---|---|
| rod panel 5 → 15 genes | clusters clearing the ≥2 shared-gene bar 11 → 21 | **11 → 21 (+10)** — reproduced exactly | 11 → 21 |
| macrophage (4 entries) | truth clusters answered exactly 0 → 11 | 6 → 8 under the frozen judge; under the library-aware judge the answer set is `macrophage` ×7, `Microglia` ×1, `Astro` ×2 … | MERGED 7 exact |
| vascular endothelium (11 entries) | 0 → 11 exact | 10 → 7 under the frozen judge (most `Endo`/`endothelial cell` takeovers are graded `unmappable`), library-aware 10 → 10 | MERGED 3 exact |
| RPE panel deepened | precise 11 → 14, the 6 RPE→melanocyte confusions unchanged | 10 → 12 library-aware; the RPE→melanocyte confusion is still present | MERGED 13 exact |

So one of the four directions is reproduced **exactly** (the rod panel), and the others are directionally
partial — the library does close holes; it also displaces answers elsewhere, and on this route the second
effect is larger.

### 3.5 The instrument finding (why the refusal is not a labelling artefact)

`kb/markers/markers_cl_alignment_v2_unified.json` maps the **76 shipped class names** to CL ids
(`Rod → CL:0000604`, `RPE → CL:0002586`, …). The library names its entries by the **Cell Ontology label
itself** (`retinal rod cell`, `retinal pigment epithelial cell`, `macrophage`, …) — 16 of its 17 names are
absent from that map, and the ranking rows carry no CL id. The frozen judge therefore resolves every such
answer as `unmappable_pred` / family `other` = `inconsistent`, even where the class it names is the correct
one. `scripts/diag_labelmap_gap.py` re-reads the same two arms with a resolver that falls back to each
entry's own `cl_id` (read from the OBO file at build time):

| reading | `same_cl` | `truly_inconsistent` | `unmappable_pred` |
|---|---:|---:|---:|
| recorded declarations, OFF → ON | 39.707 % → **42.261 %** | 21.024 % → **24.973 %** | 1.560 % → 0.933 % |
| default route, OFF → ON | 32.988 % → **35.826 %** | 25.209 % → **29.697 %** | 1.370 % → 0.743 % |

Under that instrument the library's gains are real (+2.55 pp `same_cl`) **and** so are the contradictions
(+3.95 pp), with 46 of the 90 takeovers landing on a cluster whose author class is genuinely different. Both
rulers fail clause (b); the pre-registered ruler decides, and the second reading is reported so the owner can
see that the refusal is not an artefact of a stale label map. **Updating that map is item (2) of the same
owner checklist and is deliberately not part of this card.**

## 4. The kill switch, byte for byte (clause d — passes)

Measured by swapping the parent commit's core **in place** at the same absolute path and replaying the
recorded query set (`out/DEFAULT_FACE.json`):

| arm pair | mode | queries | raw bytes identical | canonical identical |
|---|---|---:|---|---|
| PARENT vs **KILL** (`EYEKB_ACT_HOLEFILL=0`) | clusters | 721 | **true** | true |
| PARENT vs **KILL** | battery | 229 | **true** | true |

Combined digests: clusters raw `53b045972102086ac085a5649bd8859e` in both arms; battery raw
`56fd4a1c0c451f39e5d630869fae327a` in both. The same comparison also proves this card's **registration
restoration is default-neutral** (the parent commit does not carry it; the killed flip does).

## 5. The change is the only change, and the delta is characterised (card item 5)

| arm pair | queries | raw bytes moved | ranking moved | attribution census |
|---|---:|---:|---:|---|
| PARENT → FLIP, clusters | 721 | **721** | 255 | disclosure-field-only 466, library-in-candidate-list (top-1 same) 163, **top-1 changed to a library entry 92**, unexplained **0** |
| PARENT → FLIP, battery | 229 | 228 | 0 | disclosure-field-only 228 |
| PARENT → FLIP, explicit route | 13 | 1 | 1 | explicit-route row now served (`holefill_v12`) |

`out/FIELD_DIFF.json` names the response fields that move (ranking, provenance/disclosure blocks,
soft-flag notes) on representative queries, so “721 moved” is an attributed number rather than a count.

**Compatibility-contract item (reported, not absorbed):** the legacy five-tool panel digest moves
`47e42230a8f7256b4ae9a78d4ff628d3` → `06bb857eac0052133421a56138afbe83` on the two `query_marker` calls whose
**rankings are unchanged**. The recorded fixture (`e8e6c26351cd9a1d42fa2e7cb6a83f23`) was **not** re-recorded,
so the probe is red at this commit. Note the fixture was **already stale at the parent commit** — the digest
the PARENT arm reports equals exactly the digest the preceding `onfibro_v13` activation recorded for its own
activated face (`out/DEFAULT_FACE.json: tool_panel.inherited_panel_staleness.parent_arm_equals_predecessor_activated_face = true`),
so the movement this card would have added is the *further* move, not the inherited one.

## 6. The defect this card found, and the restoration it carries

`MARKER_LIBS` had **no `holefill_v12` entry**: commit `0312016` (card `t_0c40c7b1`) replaced the dictionary's
closing line — which was that entry — with the block registering the next library, instead of following it.
Measured consequence: `query_marker(library="holefill_v12")` raised `ValueError: library must be one of retina|membrane|retina_interneuron|retina_v6|face_v6|
lacrimal_v6|k9_ocs|retina_v7|retina_dev|antseg_v10|lensiris_v11|holefill_v12|onfibro_v13|all` — an error whose own message names the library it refuses — while
registry row **L1-26** states it is “reachable only via `library=holefill_v12`”. Without the entry the
activation could not be performed or measured at all (an entry appended to a whitelist whose library is
unresolvable is a null), so the restoration is part of this card.

Proof of neutrality (`out/RESTORE.json`, `scripts/l0b_restore_registration.py`):

| check | result |
|---|---|
| pre-restore image equals the parent commit's blob | **true** (`e74c73c6c2ef04d1…`) |
| default route, pre-restore vs restored | clusters **721/721**, battery **229/229** byte-identical (raw and canonical) |
| explicit route | 13 rows, **exactly 1** moves: `lib:holefill_v12` stops being a refusal (the intended effect) |
| `golden_721.py`, both switch arms | before == after; the 45-cluster difference to the 2026-10-18 recording is the preceding `onfibro_v13` activation, reported as information, not used as a criterion |
| `library="holefill_v12"` resolves to the 17 registered entries | **true** |

**Detection gap, reported as a finding:** no gate exercises explicit-route reachability against the
registration row, and `golden_721` replays only the default route — which is why a dropped registration line
survived two cards, four gate chains and a release identity.

## 7. A concurrent card edited the same file (recorded, not hidden)

Card `t_7509a1a2` (the second-marker subtype registration) edits `mcp_server/eyekb_core.py` in the same
working tree; the dispatch queue had flagged that file as the conflict point, and two writers did meet on it.
What was measured (`out/COLLISION_AND_CLOSEOUT.json`, `out/collision/`):

* the sibling's registration was taken **on top of this card's flipped core** (its own pre-image sha
  `bd45c6b93ec73cd6…` is this card's flip) — so its baseline silently contained this card's activation;
* its append **dropped the `onfibro_v13` registration line** by the same mechanism as the defect above, and
  `library="all"` raised `KeyError: 'onfibro_v13'` in the working tree while that state stood;
* this card's measurement window, by putting its own core in place, overwrote the sibling's most recent
  uncommitted write (sha `fb6c0408…`), which is **not recoverable** — recorded as this card's footprint. The
  sibling's *recorded* registration state (`9f0a34c1…`) was independently reproduced from its own script plus
  its pre-image, sha for sha, so the shared-file edit is fully understood rather than guessed;
* the sibling's own script was later amended to **echo the anchor line** and it records why (its comment cites
  the measured `KeyError`) — that self-correction was found while closing this card out and is reported as
  such;
* the final working-tree state is a **three-party merge** (`sha be4e91c3…`): the parent commit's bytes + this
  card's registration restoration + the sibling's registration (rebuilt from its own script, `onfibro_v13`
  preserved) − **this card's activation wiring**. Verified: it compiles, all **14** named libraries resolve,
  `library="all"` answers, `holefill_v12` is reachable by name, and the default route replays the parent
  commit byte-for-byte (clusters 721/721, battery 229/229).
* the sibling card was told, on its own card, not to write the core from its pre-registration buffer (it
  carries this card's NO-GO'd activation), and that its registration is already present in the tree.

## 8. Registrations, and the commits

Three local commits (no push; the coordinator pushes after verification):

| commit | content |
|---|---|
| `b2f2e47` | the measurement record: pre-registration, scripts, every reading, the collision record, and registry row **L1-26** carrying the decision, the numbers, the instrument finding and the restoration (exactly one registry line changed) |
| `b30c124` | the landed restoration: the six lines restoring `holefill_v12`'s `MARKER_LIBS` entry + registry row **L1-11M** re-taken from live bytes + `docs/SWITCH_COVERAGE_REGISTRY.tsv` regenerated from source + `docs/W3_MANIFEST.sha256` re-frozen last + `docs/RELEASE_IDENTITY.json` / `RELEASE_MANIFEST_v1.json` re-taken against the index |
| `54fc328` | follow-up: the switch registry's **own** registry row (`L6-47`) re-taken (regenerating it invalidated the row that registers it), W3 manifest re-frozen after it, identity re-taken (`release_id c874b80592be`, 4,166 files, `--check` IDENTITY MATCH) |

What was committed, and why it changed shape during the card: the activation was **refused**, so there is
no default-ON behaviour to register and no change-control instance row to add — but the **defect fix had to
land** (a dropped registration line that made a registry row untrue, in a file whose only live writer by
then was this card, and which would otherwise have been lost the way the sibling card's uncommitted bytes
were). That made the core a changed file, so the rows and identity records the change invalidates were
re-taken in the same commits, in the repository's own order (registry rows → switch registry → W3 manifest
→ identity).

The library is **not activated**: `holefill_v12` stays `REGISTERED_DEFAULT_OFF`, reachable by name only, and
the shipped default route is byte-identical to the parent commit's (§7).

## 9. Gates — the repository's own chain, in a clean clone

`tests/run_gates.sh` in a **clean clone at commit `54fc328`** (the corpus is not distributed inside the
clone, so `EYEKB_CORPUS` is pointed at the laboratory's copy; the clone's tree is not modified):

```
G3 verify_repro (41-query retrieval anchor)             rc=0 pass
G4 verify_pipeline (three byte anchors)                 rc=0 pass
G5 gate_registry (registry surface enforced)            rc=0 pass
G6 gate_change_control (eight machine rules)            rc=0 pass
G7 gate_ontology_layer (read-only ontology layer)       rc=0 pass
G8 gate_ontlayer_portability (portability/fail-closed)  rc=0 pass
G9 gate_preimage_ref_immutable (immutable refs)         rc=0 pass
G10 gate_switch_coverage (registry in sync; arms)       rc=0 pass
gates=8 failed=0  (CHAIN PASS)
```

Readout stored at `out/CLONE_REPO_GATES.log`, parsed into `out/CLONE_CHECK.json`. The reachability finding
of §6 stays open as a *proposal*, not as a weakened criterion: no gate was relaxed, and the two red
readouts of the intermediate commit (`b2f2e47`: G3 rc=1 for a corpus precondition missing from the clone,
G10 R1 rc=1 for the registry drift inherited from the sibling card's commit) are kept in
`out/CLONE_REPO_GATES_commit_b2f2e47.log` with their attribution, rather than deleted.

## 10. Artefacts

```
PREREG_ACTIVATION_HOLEFILL_20261022.md   the pre-registration (before any measurement)
REPORT.md                                this report
scripts/l0b_restore_registration.py      the registration restoration + its neutrality proof
scripts/l0_preimage.py                   the pre-flip pre-image and ordering record
scripts/l1_flip_apply.py                 the flip (apply / verify / revert), its region census and probe
scripts/l2_flip_measure.py               the measurement: three readings, four criteria, attribution
scripts/diag_top1_moves.py               why the top-1 answers moved (caught a classifier defect)
scripts/diag_labelmap_gap.py             the instrument finding: what the frozen judge cannot read
scripts/l3_default_face.py               the kill switch, the delta census, the tool-panel probes
scripts/l3b_replay_route.py              the same-path replay device (clusters / battery / explicit)
scripts/l3c_field_diff.py                which response fields move
scripts/l6_collision_closeout.py         the concurrent-card collision and the final working-tree state
scripts/l7_registry_note.py              the registry row update (one line)
scripts/cl_conformance_probe.py          the Cell Ontology red line
out/*.json, out/collision/               every reading, with the commands that produced them
logs/, ledgers/net_audit.log             run logs and the zero-network receipts
```

## 11. What the owner is asked to decide (not decided here)

1. **The library stays default-off.** The activation is refused on measurement, and the refusal holds under
   both the pre-registered ruler and a ruler that knows the library's own CL ids.
2. **The label-map gap is the thing to fix first** if this library is to be tried again: until
   `markers_cl_alignment_v2_unified.json` carries (or bridges to) the Cell Ontology labels the library uses,
   every judge — ours and anyone else's — will read its correct answers as contradictions. That is item (2) of
   the same checklist, and it edits the file this card's sibling card also edits.
3. **The `MARKER_LIBS` append mechanism needs a guard** (two cards in one day dropped a registration line by
   appending over the dictionary's closing line, and neither gate chain noticed). A one-line gate — every
   library named in a `*_DEFAULT_LIBS` constant must exist in `MARKER_LIBS`, and every registered row must be
   reachable by name — would have caught both.