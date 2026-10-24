# REPORT — KB-REACH: the three registration/instrument defects found by CL56-ADOPT, closed

Card t_c19cd667 (board pi-briefing, assignee pi-bioinfo). Defects found and measured by card
t_fabddb85 (§6 of its REPORT); each was outside that card's scope. This card fixes them in the
smallest layer that owns each defect. Wave root (construction site):
`/mnt/D/EyeKB/plans/kbreach_fix_20261024/`; repository mirror: `docs/plans/kbreach_fix_20261024/`
of `/home/ubuntu/EYEKB_REPO` (the tree every command below runs against). English throughout, so
the mirror is verbatim the record. Zero downloads, zero network, zero GPU; commits are local, no push.

## 0. One line

`subtype_v14` can now answer through its explicit route (body fixed, registration re-taken), the
tool-panel identity device is green again with the drift attributed per call (baseline re-recorded
in the commit that carries the fix), and the frozen harness's qualified-`is_a` closure gap is
**registered as a stated instrument limit** — 686 qualified edges, 26/721 recorded clusters move
under a corrected closure, 14 move at family level — with the full list and the re-derivation entry
points in `docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md`.

## 1. Item 1 — `subtype_v14` is reachable through its explicit route

### 1.1 The defect, reproduced before any byte changed

```bash
cd /home/ubuntu/EYEKB_REPO && /usr/bin/python3 -c "import json;d=json.load(open('kb/markers/markers_v14_subtype_second_increment.json'));print('markers' in d, len(d.get('entries') or []))"
# -> False 16            (recorded in out/R1_REPRODUCE.json D1_body: markers_key_present=false)
```

The same reading via the shipped core (clean env child, `scripts/r1_reproduce.py` D1 block):
`n_ranked = 0`, `top = null`, inventory `cell_types` = 0 — the explicit route answers NOTHING while
registry row L1-31 says "reachable only by naming library=subtype_v14" (= reachable). Byte state:
sha256 75884fb7bd88e1ab7fd1652a26051046bff07dd0c6ee2972abfd7c8100f9f452, 37,576 bytes (== the
registered value of row L1-31 before this card).

### 1.2 The fix

`scripts/f1_fix_subtype_markers.py` derives the top-level `markers` block from the file's own
`entries` (`class_name -> markers`, insertion order and per-class gene order preserved) and inserts
it immediately before the `entries` key. Hard assertions before the write: 16 distinct class names;
every derived list non-empty; `panel_gene_union_unchanged = true` (per (class, gene) pair set equal);
the ONLY top-level key added is `markers`; per-class lists byte-equal to their entries after the
write. Result: sha256 f0978ceec6945db72184a400364d5b7537a9e78e25c59db6697c0de2aff468cb, 38,759
bytes (out/F1_FIX.json). Byte-exact pre-image kept at
`pre_images/markers_v14_subtype_second_increment.json.pre_kbreach` (sha256 == 75884fb7...).

No service-core byte changed in this commit: the loader already reads `db["markers"]` when present;
`_load_marker_dbs` needs no edit, so `mcp_server/eyekb_core.py` stays at its committed blob.

### 1.3 The default route is byte-identical before/after (measured, not asserted)

Reusing the CL-56 wave's replay machinery verbatim (`scripts/m2_replay_route.py` of
/mnt/D/EyeKB/plans/cl56_adopt_20261022/, against the recorded 721-window set):

| arm | windows | raw_md5 PRE | raw_md5 POST | canonical PRE | canonical POST | same? |
|---|---|---|---|---|---|---|
| clusters (721 recorded gene windows, default route) | 721 | 61ac177e309458a7832058a6cf95a286 | 61ac177e309458a7832058a6cf95a286 | 058004589e2b7f311c8517a05144ea60 | 058004589e2b7f311c8517a05144ea60 | yes |
| battery (page listing + class windows x species) | 238 | d7400a22b408ca3d8da62d03d9fdcadf | d7400a22b408ca3d8da62d03d9fdcadf | 59fa523a1f1824353cbb96307028e35b | 59fa523a1f1824353cbb96307028e35b | yes |
| explicit (every named library) | 15 | f1f3cc201f7b55b7655f63147b03faa7 | f1f3cc201f7b55b7655f63147b03faa7 | a8d87b8aaa5531b3676d24fda381d020 | a8d87b8aaa5531b3676d24fda381d020 | yes |

Row-level re-check (scripts/r2_after_fix.py): `n_differing_raw = 0` and `n_differing_canonical = 0`
in all three arms — including the `lib:subtype_v14` row, whose query window shares no gene with the
panel, so the empty ranking is byte-identical by construction. Commands:
`/usr/bin/python3 scripts/m2_replay_route.py <mode> out/PRE_<mode>.json` before, `.../POST_<mode>.json`
after; `scripts/r2_after_fix.py` compares row by row.

### 1.4 The explicit route now answers (acceptance readings, and one measured non-result)

All readings from the shipped core in a clean-env child:

1. Class inventory: `core.query_marker(library="subtype_v14")` -> mode=list, `cell_types` = 16
   (was 0). The body now exposes all 16 entries.
2. Best recorded window: `query_marker(genes=<window>, library="subtype_v14")` over
   CX02_adult_retina#7 (2,398 cells, 10 genes) -> **n_ranked 0 -> 6**, top = ON-bipolar cell
   (out/R2B_CENSUS.json `best_window`).
3. Full census over ALL 721 recorded windows (out/R2B_CENSUS.json `census_by_n_ranked`):
   `{0: 576, 1: 59, 2: 42, 3: 9, 5: 31, 6: 4}` — the maximum anywhere in the recorded set is 6/16.

**Measured non-result, reported rather than rounded to PASS:** the card brief's acceptance literal
"one command shows `n_ranked = 16` for a recorded probe window" is unreachable on the recorded set —
no recorded window's gene set overlaps all 16 panels (the 16 windows hit at most 6; the explicit
probe window of the CL-56 machinery — the largest recorded cluster, CX02_adult_retina#4, 12,902
cells — overlaps ZERO of the 16 panels, which is exactly why the pre-fix `n_ranked=0` and the
post-fix explicit-row bytes are identical there). The reachable, honest statement of "the 16 entries
are ranked" is the inventory reading (16/16 classes listed) plus per-window rankings wherever any
gene is shared. Static oracle over all 721 windows BEFORE the fix agrees with the service census
AFTER (max hit = 6, same window; scripts/r1_reproduce.py D1c).

### 1.5 The registration surface, re-taken in the same commit

`docs/W3_PIPELINE_REGISTRY.tsv` row L1-31: sha256 -> f0978ceec6945db72184a400364d5b7537a9e78e25c59db6697c0de2aff468cb,
bytes -> 38,759, mtime -> 2026-10-24 17:06:30 (live bytes), plus a dated notes clause that records
the defect, the fix, the replay identity, the census numbers and why the derivation-only edit sits
inside the row's "never edited in place" gate as a registration-layer fix (panel genes bit-identical;
the entries fragment is untouched). Change-control row `CHG-20261024-KBREACH-SUBTYPE14-BODY`
(documented below).

## 2. Item 2 — the tool-panel identity device is green again, with per-call attribution

### 2.1 The RED state, reproduced

```bash
cd /home/ubuntu/EYEKB_REPO && HOME=/home/ubuntu EYEKB_PROBE_PY=/home/ubuntu/training-venv/bin/python3 \
  /home/ubuntu/training-venv/bin/python3 tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json
# -> IDENTITY FAIL: legacy_panel, full_panel moved.     rc=1
#    different: query_marker:{"cell_type": "MG"}
#    different: query_marker:{"genes": ["TMEM119", ...]}
```
(out/R1_REPRODUCE.json `D2_probe_baseline`: returncode 1, the two moved calls.)

### 2.2 Per-call field attribution (both commits replayed, full responses stored)

A clone of the baseline commit 435bb92 and HEAD were each driven through the same 12-call panel with
the SAME interpreter the fixture's provenance declares (scripts/dump_panel.py; the 435bb92 arm's
per-call md5s match the approved fixture byte-for-byte, 12/12 — the dump caliber IS the fixture
caliber). Field-level diff (scripts/d2_field_diff.py -> out/D2_FIELD_DIFF.json):

- n_calls compared 12; n_differing 2; refused 0.
- BOTH moved calls differ in exactly ONE field: `provenance`.
  - `provenance.files` gains `onfibro_v13` (7 libs -> 8 libs).
  - `provenance.conflicts` gains `{"class": "Fibroblast", "alias": "onfibro_v13::Fibroblast"}`.
- Semantic surface identical in both calls: `markers` keys, `celltype_ranking` order
  (Microglia, HC, Mono_Nonclassical, Mac_Tissue, retina_interneuron::HC) and `n_shared_first = 5`.

Single-cause attribution: card t_42df17c2 (default-route activation of `onfibro_v13`). Its own
L1-11M note recorded the legacy digest move (e8e6c263..., 10 calls) and deliberately left the
baseline un-re-recorded ("RED by design"), deferring the re-record. The 2026-10-22 registrations
(subtype_v14 t_7509a1a2, holefill_v12 t_be11fd4a, cl56_v15 t_fabddb85) contribute NOTHING to either
moved call — explicit-route-only libraries are absent from `provenance.files` at both commits.

### 2.3 Re-record, in the commit that makes the device green

```bash
cd /home/ubuntu/EYEKB_REPO && HOME=/home/ubuntu EYEKB_PROBE_PY=/home/ubuntu/training-venv/bin/python3 \
  /home/ubuntu/training-venv/bin/python3 tests/probe_tool_panel_identity.py --record tests/fixtures/tool_panel_baseline.json
# recorded baseline -> tests/fixtures/tool_panel_baseline.json   (legacy_panel 47e42230a8f7256b4ae9a78d4ff628d3, full f97ff8ad2507f4d69a0e6e57406c2de1)
... --baseline tests/fixtures/tool_panel_baseline.json
# -> IDENTITY PASS: both panel digests match the baseline.   rc=0
```
(out/PROBE_AFTER_RERECORD.log carries both runs + rc; legacy digest == the post-activation value
t_42df17c2 recorded in L1-11M notes — the re-record contains EXACTLY the attributed drift, nothing
else.) PRE fixture bytes kept at
`pre_images/tool_panel_baseline.json.pre_rerecord` (sha256 ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87,
== the fixture as recorded at 435bb92). The subtype_v14 body fix moved 0 of the 12 digests (the
printing run right after the fix printed the same 47e42230... legacy digest).

Change-control row `CHG-20261024-KBREACH-TOOLPANEL-BASELINE` records per-call attribution
(field-level), the owning card, the rollback path, and the interpreter identity.

## 3. Item 3 — the frozen harness's closure gap, REGISTERED as an instrument limit

Choice and reason: the harness lives at `docs/plans/noregr_20261022/scripts/wave_common.py`, whose
bytes are pinned by that wave's own `out/MANIFEST.json` / `out/MANIFEST.sha256` and whose ruler
several cards' recorded readings declare comparability with. A byte edit — even a default-OFF
declared switch — invalidates those pins and re-opens recorded numbers that this card does not own.
The card brief offers exactly this second path; it is taken: **the gap is registered in
`docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md`** with the parse site, the counts, the full affected
list, and the re-derivation entry points. The harness bytes are untouched (`git diff` in the wave
commit shows no change under docs/plans/noregr_20261022/).

### 3.1 The measured numbers (all re-derived on this tree, commands inside the note)

- Qualified `is_a` lines in the pinned release `kb/ontology/cl/releases/2026-06-08/cl-base.obo`
  (sha256 c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7):
  **686** carry any `{...}` qualifier (the card brief's number; of them 679 are `{is_inferred="true"}`,
  7 carry `evidence=...` instead) out of 4,880 `is_a` lines. Command: r1_reproduce.py D3 block.
- Service-replay caliber (the CLOSURE_INSTRUMENT_DIFFERENCE caliber of t_fabddb85; top source =
  `W.replay(calls, {"EYEKB_ACT_CL56": "1"}, label="kbreach_sens_before")`), 721 recorded clusters:
  kb_coarser 116 -> **129**, truly_inconsistent 176 -> **150**, kb_finer 5 -> **18**; same_cl 244,
  abstain 165, unmappable_pred 15 unchanged in both rulers. **26 clusters change grade** — 13 as
  truly_inconsistent -> kb_coarser, 13 as truly_inconsistent -> kb_finer (full 26-row table in the
  note; out/R3_CLOSURE_READING.json `A_replay_top`). Family level (R_fam): related 88 -> 102,
  inconsistent 171 -> 157, consistent 297/297, mixed 165/165 — **14 clusters are graded inconsistent
  by the harness and related by a qualifier-stripping closure**; every directional move is
  inconsistent -> related. Command: `/usr/bin/python3 scripts/r3_closure.py`.
- Second opinion with the ledger's recorded top labels (no service call): 27/721 change
  (out/R3_CLOSURE_READING.json `B_ledger_top`); the difference vs 26 traces to the ledger's top
  labels predating the current shipped service state, not to a ruler disagreement.

The recorded harness counts 116/244/176/5/165/15 reproduce the CL-56 numbers EXACTLY (both sides
re-derived, none carried over by trust), so every earlier card's reading made with this harness
stays comparable among itself; the note states the standing instruction for future waves (read both
rulers; never cite a relatedness deficit measured on the harness closure alone for qualified-parent
terms).

## 4. Acceptance-line accounting (per the card's Goal section)

| # | card brief | status | closing evidence |
|---|---|---|---|
| 1a | markers block written, no panel gene changed | **CLEAR** | out/F1_FIX.json (assertions), pre-image byte-equal |
| 1b | default-route replay byte-identical | **CLEAR (measured)** | three arms, 0 differing rows, raw+canonical, §1.3 |
| 1c | "one command shows n_ranked=16 for a recorded probe window" | **NOT CLEARABLE AS WRITTEN (measured)** | full 721-window census max=6/16 (out/R2B_CENSUS.json); the explicit probe window overlaps 0 panels; closing readings = inventory 16/16 + best window 0->6 (§1.4) |
| 1d | row L1-31 re-taken | **CLEAR** | same-commit re-take, §1.5 |
| 2 | device green OR drift recorded as intended | **CLEAR (both halves)** | probe rc=0 after on-record re-record AND per-call attribution + change-control row (§2) |
| 3 | switch OR registered limit with the affected count | **CLEAR (registered limit)** | docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md: 686 / 26/721 / 14, full lists, re-derivation commands (§3) |

## 5. Boundary compliance

- `subtype_v14` was NOT merged into the default route and NO whitelist flipped (loader untouched;
  `SUBTYPE_DEFAULT_LIBS = ()` unchanged; explicit route only).
- CL-56's NO-GO, holefill_v12's NO-GO, the onfibro activation: not re-argued, not re-measured.
- Zero downloads, zero network, zero GPU: all work is file edits + local Python/git; the MCP drives
  in §2 are local stdio to the in-repo server.
- Commits local, no push (§7).

## 6. Change control + registration surface (standard surface, in commit order)

1. `kb/markers/markers_v14_subtype_second_increment.json` — the derivation-only byte change (37,576
   -> 38,759 bytes).
2. `docs/W3_PIPELINE_REGISTRY.tsv` — row L1-31 re-taken (1 line +/- 1; every other byte unchanged).
3. `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` — +2 rows (SUBTYPE14-BODY, TOOLPANEL-BASELINE);
   `tests/gate_change_control.py` -> all R1-R8 PASS, rc=0 (in the working tree and re-run in the
   clean-clone gate).
4. `tests/fixtures/tool_panel_baseline.json` — re-recorded (PRE bytes kept as pre-image).
5. `docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md` — new (generated table-driven from
   out/R3_CLOSURE_READING.json + out/R1_REPRODUCE.json; scripts/gen_limit_doc.py).
6. `docs/plans/kbreach_fix_20261024/` — this REPORT + scripts/ + out/ + pre_images/ (the wave mirror).
7. `docs/RELEASE_IDENTITY.json` — re-taken from the staged tree AFTER all byte changes
   (`python3 scripts/release_identity.py --take --source index`), then committed.
8. `docs/W3_MANIFEST.sha256` — re-frozen LAST (registry row sha changed; dated header line appended).

## 7. Commits + clean-clone gate

Recorded in docs/plans/kbreach_fix_20261024/COMMIT.txt after the commit lands; the clean-clone
verification is:

```bash
rm -rf /tmp/kbreach_clone && git clone -q /home/ubuntu/EYEKB_REPO /tmp/kbreach_clone
cd /tmp/kbreach_clone && EYEKB_CORPUS=/home/ubuntu/EYEKB_REPO/literature_db/v2.4.2_2026-09_slim \
  EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 EYEKB_GATE_OUT=/tmp/kbreach_clone/.gate_out \
  bash tests/run_gates.sh
# required tail: gates=8 failed=0
```

(The readout line and the commit hash are stamped into COMMIT.txt and out/CLONE_REPO_GATES.log at
the end of this wave.)

## 8. What did not clear, and why (one line)

`n_ranked = 16 for a recorded probe window` — no recorded window can rank 16/16 (max 6 in the full
census); the acceptance literal is a measured non-result and the reachable readings that prove the
body answers are recorded in §1.4. Everything else in the card's Goal is either CLEAR or its stated
alternative was chosen deliberately (item 3 ).
