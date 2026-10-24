# REPORT — CL-56 child-term adoption: adopted into the naming layer, ruled NO-GO for the default route

Card: `t_fabddb85` ("CL56-ADOPT"), board `pi-briefing`, executed by `pi-chief`.
Brief: `plans/cl56_adopt_20261022/BRIEF_ADOPT_CL56_20261022.md` (verbatim in the card body).
Pre-registration: `PREREG_ADOPT_CL56_20261022.md` (on disk before any measurement; sha256 recorded in
`out/REGISTRY_ROWS.json`).
Wave directory: `plans/cl56_adopt_20261022/` (construction site) → mirrored to
`docs/plans/cl56_adopt_20261022/` (review layer) in the same commit.

## One line

The three child-term pairs that clear the pre-registered scope rule **are adopted into the naming layer**
— the terms now exist in the KB label → Cell-Ontology map, and a registered-but-default-OFF marker
increment can name them — but merging that increment into the default route **fails the pre-registered
acceptance rule** (cell-weighted `consistent` 42.544% → 37.371%, −5.173pp; `inconsistent` 19.843% →
29.609%, +9.766pp; 12 of 28 datasets fall), so the brief's clause 5 applies: **the increment stays
registered default OFF and the shipped default route stays byte-identical** (721/721 recorded cluster
windows and 238/238 battery calls, raw and canonical, against the pre-card commit). A NO-GO with numbers
is the outcome.

## 1. What kind of record this is

The project owner was shown a two-item checklist — (1) enable the literature hole-fill library,
(2) adopt the 56 Cell-Ontology child-term candidates — and answered **"ok"** (2026-10-22). This card
executes item (2) **as an owner-signed adoption decision**, not as an audit pass, not as a validation,
and not as an accuracy claim. Every reading below is **IN-SAMPLE**: the panels were selected and measured
on the same 28 public volumes.

**Disclosure of ordering.** `PREREG_ADOPT_CL56_20261022.md` was written and on disk before any
measurement of the merged state; it fixes the scope rule (§4), the acceptance rule (§5), the rollback path
(§7) and the directional expectations (§6). The scope list it produced (`out/SCOPE.json`) was computed by
applying the rule as written, and the rule did not move afterwards. What already existed on disk when the
pre-registration was written is listed in its §0b: the predecessor waves' frozen artefacts, a read-only
reading of the *shipped* tree (`out/RECON_BEFORE_SCOPE.json`), and the input manifest.

## 2. What was built

Two halves, both inside the L1 layer (the KB loading point and the naming layer it reads).

### 2.1 The naming layer gains the terms

`kb/markers/markers_cl_alignment_v2_unified.json` goes v1.1 → **v1.2 with additive rows only**
(76 → 79 labels). Three rows, each `status: mapped`, `cl_id` = the frozen snapshot's own term,
`libraries: ["cl56_v15"]`:

| label | CL id | snapshot label |
|---|---|---|
| `rod bipolar cell` | CL:0000751 | rod bipolar cell |
| `keratocyte` | CL:0002363 | keratocyte |
| `S cone cell` | CL:0003050 | S cone cell |

No existing row is edited or removed; the file's own `supersedes_note` carries the reason. This half is
what the standing directive `docs/wiki/USER_DIRECTIVE_20260924_cell_ontology_naming.md` §1 asks for (a new
entry records the CL term it names), and it is the fix the predecessor activation card asked for: it
measured that an entry name the map cannot resolve is graded `unmappable_pred` and read as an
inconsistency — 70 of 90 takeovers in that card. Measured here: `unmappable_pred` stays at 15 clusters
before and after, i.e. the adopted names resolve (they would otherwise be 3 more).

### 2.2 The naming increment, registered default OFF

`kb/markers/markers_v15_cl56_increment.json` — `v15.0-cl56-child-term-adoption-20261024`, 3 entries /
126 genes, `cl56_v15`, whitelist `CL56_DEFAULT_LIBS = ()` (empty by design), switch `EYEKB_ACT_CL56`.

| our class | adopted child term | CL id | genes | demand clusters | demand cells |
|---|---|---|---:|---:|---:|
| `BC` | rod bipolar cell | CL:0000751 | 44 | 8 | 23,484 |
| `Fibroblast` | keratocyte | CL:0002363 | 60 | 3 | 11,836 |
| `Cone` | S cone cell | CL:0003050 | 22 | 3 | 3,685 |

Each entry carries **only** that pair's discriminating positive genes (parent-shared genes removed, the
predecessor readiness wave's T-GENES construction), so a child entry cannot re-state the parent's identity
genes and cannot merge two of our classes. No gene in this card is proposed by this card: the panel source
is `plans/subdivision_readiness_20261022/out/pair_table.json` field `discriminating_genes`.

### 2.3 The scope rule, applied (25 → 3)

The rule was pre-registered as the card states it — (a) a true `is_a` descendant in the frozen snapshot,
(b) one of the 25 corpus-supported pairs, (c) scorable at the pre-registered floor. Because clause (c) is
ambiguous in the brief, it was operationalised **before** the list was computed as three mechanical
conditions resolved towards the predecessor wave's own floors, never towards a laxer one (PREREG §4c):
(c1) ≥1 recorded cluster whose reference label is literally the term; (c2) ≥2 discriminating positive genes
in the assay vocabulary (T-GENES, "single-gene admission = 0"); (c3) ≥1 demand cluster whose recorded
window shares ≥2 genes with that panel (T-OBS).

```bash
/usr/bin/python3 scripts/s1_scope.py     # out/SCOPE.json, out/SCOPE.tsv
```

```
corpus-supported pairs: 25 | adopted: 3 (14 clusters / 39005 cells) | pending: 22 | no-corpus-hit: 31 out of scope
```

The 22 pending pairs and the reason each failed (`out/SCOPE.json`, `out/SCOPE.tsv`):

| reason | pairs |
|---|---:|
| `c2_below_two_discriminating_genes` (+ `c3`) | 18 |
| `c3_panel_not_observable_in_window` only | 4 |

The decisive one is c2/c3: for 18 of the 22 the predecessor readiness wave found **no discriminating
positive gene at all** for the child term (the corpus mentions the term but never attaches a marker to
it), and for 4 more the genes exist but none appears in a demand cluster's recorded top-10 window. Adopting
those would mean inventing a panel, which the brief forbids; they are listed, not adopted. The 31 pairs
with no corpus hit are out of this adoption for the reason the brief gives (an unsupported name adopted on
our own say-so is the fabrication this project forbids).

`we_are_finer_pairs` (8 pairs where **our** term is finer than the author's) is a different question and is
**not** folded in, recorded in the increment's own body.

## 3. The measurement

Instrument: the predecessor harness, **reused unedited** — `plans/noregr_20261022/scripts/wave_common.py`
(sha256 `f8226dc4aefc799a…`) and `n3_harness.py` (`9f55a8ccbd202196…`). One declared addition: the
harness's switch-hygiene tuple predates `EYEKB_ACT_CL56`, so `wave_common.SWITCHES` was extended with that
single name inside the measuring process (`out/MEASURE.json` → `harness.switch_hygiene_declared_extension`).
No ruler, grade, threshold or rule was changed.

```bash
/usr/bin/python3 scripts/m1_measure.py       # out/MEASURE.json + out/harness/**
/usr/bin/python3 scripts/a1_acceptance.py    # out/ACCEPTANCE.json / .md
/usr/bin/python3 scripts/s2_sensitivity.py   # out/SENSITIVITY.json (instrument sensitivity)
/usr/bin/python3 scripts/m2_default_face.py  # out/DEFAULT_FACE.json (byte identity)
```

Three readings, all reported: the recorded volume declarations, the external tester's re-declarations
(`CX16_tabula_sapiens_eye` → `ocular_surface`, `CX11_posterior_eye_atlas` → `ocular_surface`, as the
predecessor card used), and the **default route itself** (no `tissue` argument — the surface a flip
changes).

### 3.1 The registered-set reading, whole recording (721 clusters / 1,495,330 cells), cell-weighted

| grade | before % | after % | delta pp | clusters before → after |
|---|---:|---:|---:|---|
| consistent | 42.544 | 37.371 | **−5.173** | 297 → 276 |
| related | 16.936 | 17.915 | +0.979 | 88 → 90 |
| inconsistent | 19.843 | 29.609 | **+9.766** | 171 → 235 |
| mixed (abstention) | 20.676 | 15.105 | −5.571 | 165 → 120 |

Abstention falls — and **that is not a gain by itself** (the L1 precedent: abstention 23.25% → 5.55% came
with contradictions 17.95% → 29.32% and was ruled NO-GO). 311 clusters / 681,726 cells move; 50 clusters
move up a grade and 30 move down (96,714 cells up, 88,114 cells down). The tester-declaration reading
gives the same shape (−5.173pp / +9.784pp).

### 3.2 Per dataset — 12 of 28 fall

| dataset | consistent before → after | delta pp |
|---|---:|---:|
| PRE_OA-D068 | 53.785 → 18.923 | **−34.862** |
| CX04_cowan_organoid | 90.134 → 60.127 | −30.007 |
| CX04_cowan_periphery | 54.239 → 37.269 | −16.970 |
| CX12_ocular_surface_snRNA | 35.997 → 20.816 | −15.181 |
| CX02_adult_retina | 72.376 → 57.278 | −15.098 |
| CX04_cowan_fovea | 67.772 → 56.720 | −11.052 |
| CX03_retina_multiome | 36.842 → 27.695 | −9.147 |
| PRE_OA-D001 | 74.970 → 66.089 | −8.881 |
| PRE_OA-D002 | 35.879 → 30.913 | −4.966 |
| PRE_GSE199013 | 43.376 → 40.821 | −2.555 |
| CX13_TM_corneal_scleral | 41.306 → 40.450 | −0.856 |
| CX13_central_cornea | 6.629 → 6.386 | −0.243 |

(The other 16 datasets do not fall; the full per-dataset table is
`out/harness/A1_recorded_decls/REPORT.md`.)

### 3.3 Attribution — every move classified, none unexplained

311 moved clusters, `adopted-name-gain` 92 / `rank-shift` 219 / **`unexpected` 0**. The 92 renames:

| adopted entry | clusters renamed | cells | of those, clusters whose author label **is** that term |
|---|---:|---:|---:|
| rod bipolar cell | 45 | 88,453 | **0** |
| keratocyte | 27 | 43,293 | 2 |
| S cone cell | 20 | 74,563 | 1 |
| **total** | **92** | **206,309** | **3** |

Grade transitions of the 92 renames: `consistent→inconsistent` 17, `mixed→inconsistent` 44,
`consistent→related` 5, `inconsistent→inconsistent` 11, `inconsistent→related` 4, `related→inconsistent` 8,
`inconsistent→consistent` 1, `consistent→consistent` 1, `mixed→related` 1.

### 3.4 The ontology reading

Whole recording (clusters): `same_cl` 244 → 220, `kb_coarser` 116 → 114, `truly_inconsistent` 176 → 241,
`abstain` 165 → 120, `kb_finer` 5 → 11, `unmappable_pred` 15 → 15.

The 14 adopted demand clusters (the only place the pre-registered clause (d) looks):
`kb_coarser` 12 → 10, `same_cl` 0 → **3**, `abstain` 2 → 1. So the expected narrow mechanism is visible
exactly there — and it accounts for **14 clusters**, while the broad panels act on 311.

**This measures naming agreement against author labels, not recognition ability.** An ontology-consistent
name is not evidence of a better call; a cluster named `S cone cell` because it shares 22 genes with a
literature panel is not thereby an S cone.

## 4. The pre-registered acceptance rule, applied

| clause | requirement | verdict | measured |
|---|---|---|---|
| (a) | no dataset's cell-weighted `consistent` share falls, on each reading | **FAIL** | 12 of 28 fall under the recorded declarations, 12 under the tester's, 12 on the default route; worst −34.862pp |
| (b) | the aggregate `inconsistent` share must not rise (overall and on no dataset) | **FAIL** | 19.843% → 29.609% (+9.766pp); 18 datasets rise |
| (c) | every move attributable, zero `unexpected` | **PASS** | 311 moves: 92 adopted-name-gain + 219 rank-shift, 0 unexplained |
| (d) | the finer name is the author's own label for those adopted clusters, and any adopted cluster where it is not is reported | **PASS** | 14/14 demand clusters carry the name as their author label, 0 violations; reported beside it: only 3 of the 92 renames land on such a cluster |
| (e) | the kill switch restores the pre-flip default byte-for-byte | **PASS** | PARENT vs `EYEKB_ACT_CL56=0` vs unset: 721/721 cluster windows and 238/238 battery calls identical, raw **and** canonical |

**Verdict: NO-GO.** Failing clauses: (a), (b). Per clause 5 of the brief: no merge into the default route;
the increment stays registered default-off; the card completes with the numbers.

The verdict is **not instrument-dependent**: re-read under a corrected ontology closure
(`out/SENSITIVITY.json`), consistent is the same −5.173pp and inconsistent the same +9.766pp, with the
same 12 falls and 18 risings — only the *levels* shift (`inconsistent` 17.000% instead of 19.843% at
baseline), because the frozen harness's closure misses the release's qualified `is_a` edges (§6.3).

## 5. Why it failed, stated plainly

Three mechanisms, each measured:

1. **Over-application (the dominant one).** The child panels are not narrow enough to be child-specific.
   The `keratocyte` panel is 60 genes and reads like a generic stromal/mesenchymal set (`COL1A1`, `COL1A2`,
   `COL3A1`, `DCN`, `FN1`, `GFAP`, `CD68`, `CD14` …); the `rod bipolar cell` panel is 44 genes. Loaded into
   an unfiltered route they clear the ≥2 shared-gene bar on clusters nobody called that: **89 of the 92
   renames are clusters whose author label is a different term**. The readiness wave predicted exactly this
   shape (its `gain_clusters` was 0 for these pairs against `loss_clusters` of 4–111; all 11 of its T1/T1k
   splits together: gain 1, loss 297), and this card reproduces it cell-weighted on the shipped route.
2. **The family ruler does not know the adopted names.** R_fam's `consistent` requires
   `fam_of(answer) == ref_family`, and `fam_of` reads the frozen recording + the frozen family crosswalk —
   neither carries a label that did not exist when they were frozen. So a rename reads `related` (through
   the ontology) or `inconsistent`, never `consistent`: `consistent→related` 11,722 cells,
   `consistent→inconsistent` 66,646 cells. Under this ruler a pure rename can only lower clause (a), which
   is why clause (a) was written as an absolute bar in the pre-registration.
3. **Abstention falling is not a gain.** 45 clusters left `mixed`; 44 of them landed in `inconsistent`
   because the name that answered them is not the author's term. This is the L1 precedent's exact shape.

## 6. Findings about the instrument and about earlier registrations

Reported, not fixed — none of the three is this card's scope, and all three are measured.

### 6.1 `subtype_v14` is registered but its body cannot answer anything

`kb/markers/markers_v14_subtype_second_increment.json` (card `t_7509a1a2`) carries 16 `entries` but **no
top-level `markers` key**, and `_load_marker_dbs` feeds `db["markers"]` to the ranking. Measured with the
explicit-route battery (`out/DEFAULT_FACE.json` → `explicit_route_reachability`):
`query_marker(library="subtype_v14")` returns `n_ranked = 0` — an empty ranking, not a refusal — on the
pre-card commit and on this card's tree alike. Its registry row says the library is reachable by name.
This is the same class of defect the activation card `t_be11fd4a` found for `holefill_v12` (registration
says reachable, shipped code says otherwise), one layer deeper: the entry exists and the file loads, but
there is nothing to rank.

```bash
/usr/bin/python3 -c "import json;d=json.load(open('/home/ubuntu/EYEKB_REPO/kb/markers/markers_v14_subtype_second_increment.json'));print('markers' in d, len(d.get('entries') or []))"
# False 16
```

### 6.2 The tool-panel identity device is already red on the pre-card commit

`tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json` reports
`IDENTITY FAIL: legacy_panel, full_panel moved` on the **pre-card** core (`PARENT` arm), with the pristine
label map restored, and on the current tree alike; the two moved calls are
`query_marker:{"cell_type": "MG"}` and `query_marker:{"genes": ["TMEM119", …]}`. The baseline fixture was
last recorded at commit `435bb92`; the drift is therefore pre-existing, not introduced here, and this card
does not re-record it (the device's own instruction — "re-record the baseline in the same commit and say so
in the change record" — belongs to whoever moved those responses).

### 6.3 The frozen harness's ancestor closure drops 686 qualified `is_a` edges

`Rulers._load_obo` parses `is_a` as `v.split("!")[0].strip()`, which leaves the trailing qualifier — e.g.
`is_a: CL:0000192 {is_inferred="true"}` — inside the parent id, so that edge never enters the closure. The
pinned release carries **686** such lines (3335 active terms). Measured on the shipped tree
(`out/CLOSURE_INSTRUMENT_DIFFERENCE.json`): **26 of the 721 recorded clusters** are read
`truly_inconsistent` by the harness and `kb_coarser`/`kb_finer` by a closure that strips the qualifier —
`kb_coarser` 116 → 129, `kb_finer` 5 → 18, `truly_inconsistent` 176 → 150. Because R_fam's `related()`
calls the same closure, those clusters are also graded `inconsistent` instead of `related`. The
predecessor waves used the opposite convention (the CL-depth wave's gate A3 and its four-way relation
reads rely on exactly those edges), so the harness under-counts relatedness relative to the project's own
ontology authority. This card does not edit the frozen harness; it re-reads both arms under each ruler and
shows the ruling does not depend on the difference (§4).

### 6.4 The additive label-map rows moved a frozen ontology anchor — re-anchored, not waived

`kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json` pins the sha256 of
`kb/markers/markers_cl_alignment_v2_unified.json` (the ontology layer resolves its assets through that
manifest and refuses to answer on a hash mismatch). Adding three rows to the map therefore turned
G7-C01 red: `repo://kb/markers/markers_cl_alignment_v2_unified.json: ANCHOR_HASH_MISMATCH`, and G8
(portability) inherits it. The anchor was **re-taken in the same commit** with the repository's own tool —
`python3 kb/ontology/scripts/build_ont_manifest.py --take` — which reported the three declared assets and
refreshed exactly one recorded value:

```
kb/ontology/cl/releases/2026-06-08/cl-base.obo             3757082 bytes  c6274fb65cdf740b…  (unchanged)
kb/ontology/ONT_LAYER_REGISTRY_v1.json                        6437 bytes  f0ee9e4c72a5dac9…  (unchanged)
kb/markers/markers_cl_alignment_v2_unified.json              21506 bytes  b68fe013f1bfc693…  (re-taken)
re-taken: 1 recorded value(s) refreshed
```

Nothing else moved: the ontology snapshot and the capability registry are byte-identical, so the
"read-only, registered OFF" property of the ontology layer is untouched, and the pre-card bytes of the map
are kept as a pre-image (`pre_images/markers_cl_alignment_v2_unified.json.pre_cl56`,
sha256 `48051cdae915b82e…`). Re-anchoring is recorded here rather than waived: no gate criterion was
weakened, and the gate chain is re-run from a clean clone of the commit that carries the re-anchor.

## 7. What is left on disk, and what it costs

| item | state | cost on the shipped default route |
|---|---|---|
| `kb/markers/markers_v15_cl56_increment.json` | registered, `REGISTERED_DEFAULT_OFF`, empty whitelist, reachable as `library="cl56_v15"` | **none** — not in the `all` route in any state |
| `markers_cl_alignment_v2_unified.json` v1.2 | 3 additive rows | **none** — no default-route answer carries those names; the replay is byte-identical |
| `mcp_server/eyekb_core.py` | `MARKER_LIBS` entry + `CL56_DEFAULT_LIBS = ()` + `_cl56_act_enabled()` + explicit-route error message | **none** — 721/721 + 238/238 identical, raw and canonical, against the pre-card commit |

Rollback, three mechanical paths: (1) `EYEKB_ACT_CL56=0` (proven byte-identical, §4e); (2) restore
`CL56_DEFAULT_LIBS = ()` — already the shipped value, so the switch is a no-op in every state; (3)
`git revert` this commit, with both edited files kept as pre-images in `pre_images/` (shas in
`out/PREIMAGE.json`). The label-map rows revert on their own (one file, additive).

## 8. Red lines, with evidence

| red line | evidence |
|---|---|
| Cell-Ontology conformance against the frozen snapshot `2026-06-08` | every adopted term read from the snapshot with its own `id`/`name` and its `is_a` path; `out/SCOPE.json` → `a_snapshot_label`, `a_is_descendant`, `a_depth`; the gate chain's G7 re-reads the snapshot (`terms=3531 active=3335`) |
| no fabricated term, no term the author never used for *those* cells | the 14 demand clusters all carry the name as their author label (clause (d)); the 92 renames that go beyond them are counted and attributed, and are the reason the rule failed |
| no scoring / admission-floor / tie-break / window change; no other library activated; no whitelist entry beyond this increment | `out/WIRING.json` (4 anchored edits, 0 lines removed from any rule); `CL56_DEFAULT_LIBS = ()`; `docs/SWITCH_COVERAGE_REGISTRY.tsv` regenerated from source |
| `we_are_finer_pairs` not folded in | recorded in the increment body and in PREREG §4 |
| zero downloads, zero network | `ledgers/NET_AUDIT_SUMMARY.txt`: hook-load receipts > 0, connection-class events **0** (only unbound-socket construction, `gethostname`, and loopback `bind` with no peer) |
| English for everything mirrored into the repository | this report and every mirrored artefact; two Chinese strings remain only inside verbatim upstream registry cells |
| every number carries its command; NOT_RUN is never a pass | every table above is produced by a script named in §3; nothing is reported as PASS that was not run |
| commit locally, do not push | see §10 |

## 9. What did not work, and what is unresolved

1. **The adoption does not survive contact with the recorded set.** The panels the pre-registered floor
   admits are too broad to be child-specific. A narrower adoption would need a new pre-registration with a
   panel-specificity condition (for instance: an entry may not take over a cluster whose reference is
   outside its own parent's subtree, or a ceiling on renames outside the demand set). That is a new
   pre-registration, not an amendment — the brief says so explicitly.
2. **18 of the 22 pending pairs have no discriminating gene in the corpus at all.** The limit is the
   literature's marker vocabulary, not this pipeline; `out/SCOPE.json` names each one.
3. **The `keratocyte` pair is `already_shipped_as_own_class` in the readiness wave** (membrane_v1 carries
   `Keratocytes`, CL:0002363). It is in scope here because the CL-56 question is naming, and the shipped
   entry is a different label with a 3-gene panel that does not answer those clusters — but the overlap is
   real and a future adoption should decide whether the right move is a rename of the shipped entry rather
   than a second entry.
4. **The 31 unfetched candidates and the 8 `we_are_finer_pairs` remain untouched** by design.
5. **This card's own `m1` reading is a single instrument.** Its numbers were re-read under a second ruler
   (§4) and did not move; they were not re-read under a second *harness*.

## 10. Reproduction and file map

```bash
cd /mnt/D/EyeKB/plans/cl56_adopt_20261022
/usr/bin/python3 scripts/f0_freeze_inputs.py      # 54 inputs, sha256 each
/usr/bin/python3 scripts/r0_recon.py              # the shipped tree's starting point
/usr/bin/python3 scripts/s1_scope.py              # the pre-registered scope rule, applied
/usr/bin/python3 scripts/b1_build_increment.py    # the increment + the label-map rows
/usr/bin/python3 scripts/w1_wire.py               # the four anchored service-core edits
/usr/bin/python3 scripts/m1_measure.py            # the recorded-set measurement
/usr/bin/python3 scripts/a1_acceptance.py         # the pre-registered acceptance rule
/usr/bin/python3 scripts/s2_sensitivity.py        # instrument sensitivity
/usr/bin/python3 scripts/m2_default_face.py       # byte identity of the default route
/usr/bin/python3 scripts/g1_registrations.py      # registry, switch registry, change control, W3 manifest
```

| path | contents |
|---|---|
| `PREREG_ADOPT_CL56_20261022.md` | the pre-registration (scope rule, acceptance rule, rollback, expectations) |
| `scripts/f0_freeze_inputs.py`, `out/INPUT_MANIFEST.json` | read-only freeze of all 54 inputs with sha256 |
| `scripts/r0_recon.py`, `out/RECON_BEFORE_SCOPE.json` | the shipped tree's reading of the 93 in-scope clusters, before anything was built |
| `scripts/s1_scope.py`, `out/SCOPE.json` / `.tsv` | the scope rule applied: 3 adopted, 22 pending with reasons, 31 out of scope |
| `scripts/b1_build_increment.py`, `out/BUILD.json`, `out/PREIMAGE.json` | the increment file and the pre-images of both edited files |
| `scripts/b1b_map_only.py` | re-applies only the naming-map rows (idempotent, pre-image asserting) |
| `scripts/w1_wire.py`, `out/WIRING.json` | the four anchored service-core edits with their match counts |
| `scripts/m1_measure.py`, `out/MEASURE.json`, `out/harness/**` | the measurement: three readings, moved-cluster attribution, clause-(d) table |
| `scripts/a1_acceptance.py`, `out/ACCEPTANCE.json` / `.md` | the acceptance rule applied, clause by clause |
| `scripts/s2_sensitivity.py`, `out/SENSITIVITY.json` | the ruling re-read under a corrected ontology closure |
| `scripts/m2_default_face.py`, `out/DEFAULT_FACE.json` | the byte identity of the default route and the explicit-route reachability |
| `scripts/ont_closure_probe.py`, `out/CLOSURE_INSTRUMENT_DIFFERENCE.json` | the frozen closure's qualified-`is_a` gap, measured |
| `scripts/g1_registrations.py`, `out/REGISTRY_ROWS.json` | the registry rows, the change-control row, the W3 manifest |
| `discipline/net_audit/sitecustomize.py`, `ledgers/NET_AUDIT_SUMMARY.txt` | the zero-network audit hook and its census |
| `out/MANIFEST.sha256` | sha256 of every delivered artefact of this wave |

## 11. Verification at the commit under test

```bash
rm -rf /tmp/cl56_clone2 && git clone -q /home/ubuntu/EYEKB_REPO /tmp/cl56_clone2
cd /tmp/cl56_clone2 && git rev-parse HEAD        # 141862305ef24a0a632c89c3b26d1c40a482f1e1
EYEKB_CORPUS=/home/ubuntu/EYEKB_REPO/literature_db/v2.4.2_2026-09_slim \
EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 \
EYEKB_GATE_OUT=/tmp/cl56_clone2/.gate_out bash tests/run_gates.sh
# gates=8 failed=0  (CHAIN PASS)
```

| gate | reading | rc |
|---|---|---|
| G3 verify_repro (41-query retrieval anchor) | `REPRO PASS: 41/41` | 0 |
| G4 verify_pipeline (three byte anchors) | `G4 PASS: 3/3 byte-identical` | 0 |
| G5 gate_registry (registry surface enforced) | rows=141 gates=10, checks 8/8 | 0 |
| G6 gate_change_control (eight machine rules) | 8 rules, 0 problems (the new instance row parses; R1–R8 all satisfied) | 0 |
| G7 gate_ontology_layer | 9/9 checks (C01 anchors resolved after the re-anchor of §6.4) | 0 |
| G8 gate_ontlayer_portability | 6/6 checks, foreign cwd / foreign root / no author paths | 0 |
| G9 gate_preimage_ref_immutable | violations = 0 (the pre/post-image reference is the fixed sha `c06aac2…`) | 0 |
| G10 gate_switch_coverage | R1 registry matches source, R2 18 reports / 0 violations | 0 |

Two commits carry the work: `da4c412` (the adoption, the measurement, the NO-GO and the registrations)
and `1418623` (the ontology-manifest re-anchor of §6.4). Everything after those is a record-only commit
under `docs/plans/cl56_adopt_20261022/`.

Mirror fidelity, measured (`out/CLONE_CHECK.json`): 56 files compared between the construction site and
`docs/plans/cl56_adopt_20261022/`, 55 byte-identical, 1 declared difference — `ledgers/net_audit.log`, the
append-only audit log, which is excluded from the wave manifest for the same reason. The repository's
release identity checks: `IDENTITY MATCH: the record matches the shipped bytes`; the W3 manifest verifies
(`sha256sum -c docs/W3_MANIFEST.sha256` → 4/4 OK).

## 12. Resource readings

Measured with `resource.getrusage` inside the measuring process and from the scripts' own stdout
(`out/MEASURE.json` → `peak_rss_mb`, `elapsed_s`): the measurement arm pair is the heaviest step at
**193–199 MB peak RSS / 23–24 s** across the two chain runs; the byte-identity device swaps the core in
place three times and stays under the same envelope; `available` memory was ~199 GiB throughout, far above
the 40 GiB stop line in the shared workstation rules, so nothing was parked and no other workstream was
disturbed. No step needed more than one core; nothing ran concurrently.

The zero-network audit hook loaded **31** times across the chain (child processes included) and recorded
**0** connection-class events — the only socket events are unbound-socket construction, `gethostname`, and
loopback binds with no peer (`ledgers/NET_AUDIT_SUMMARY.txt`, `ledgers/net_audit.log`).