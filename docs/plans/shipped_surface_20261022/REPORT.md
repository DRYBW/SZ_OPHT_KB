# Shipped-surface defects measured by the V3 card: what they are, which side was wrong, what changed

Card `t_19831068`. Raised by the developmental-lineage workstream (card `t_aa1b7f12`, commit
`08332e849a576bd1b8d081825baf23c911510e6c`), which measured two defects on the shipped surface while
probing it and did not repair them. This card repairs the two defects and nothing else: the V3
deliverable was not edited.

Everything below was measured on this machine, from committed bytes, with the commands printed next
to the readings. No number in this report is quoted from the card that raised it, an older report, or
a previous run: each one is reproduced here and is also extracted mechanically into
`out/REPORT_NUMBERS.tsv` by `scripts/g1_numbers.py` (47 rows, name / value / source artefact / how it
was obtained).

- Repository: `/home/ubuntu/EYEKB_REPO`, base commit `954aeae3656541a6af285452c17c613ab539d5de`
- Interpreter used for every service-side reading: `/home/ubuntu/training-venv/bin/python3`
  (python 3.14.4, pydantic 2.12.5)
- Zero downloads, zero network. All dumps were taken by driving `mcp_server/server.py` over stdio.
- Not pushed. One local commit, hash at the end of this file.

**Where the artefacts are.** Tables, logs, scripts and this report are committed under
`docs/plans/shipped_surface_20261022/`. The three 54-call dumps (1.4-2.5 MB each) are **not**
committed: they live in the declared local evidence root
`/mnt/D/EyeKB/plans/shipped_surface_20261022/out/`, listed in that root's `MANIFEST.sha256`. Where this
report writes `out/DUMP_*.json`, read `/mnt/D/EyeKB/plans/shipped_surface_20261022/out/DUMP_*.json`.
The 220 MB extracted base-commit tree the "before" dump was taken from is not retained either: it is
exactly `git archive 954aeae3656541a6af285452c17c613ab539d5de`, `scripts/d1_dump_pair.sh` recreates it
in seconds, and the dumps taken from it are retained, so nothing depends on a copy of a repository
inside the repository.

## How the evidence was taken

Two dumps of the same 54 calls, so that "before" is committed content rather than "whatever the work
tree happened to hold before the editor touched it":

```
bash docs/plans/shipped_surface_20261022/scripts/d1_dump_pair.sh <outdir> v2
#   before = git archive 954aeae extracted to out/tree_HEAD_954aeae/   -> out/DUMP_PRE_HEAD_v2.json
#   after  = /home/ubuntu/EYEKB_REPO (work tree carrying the fix)      -> out/DUMP_POST_WORKTREE_v3.json
```

Each dump holds, per call, the response text, the md5 of that text (with the repo path normalised to
`<REPO>`, as the panel probe does), the byte count, the MCP client's `is_error` flag and the parsed
payload. The 54 calls are the 12 panel calls plus `get_tissue_composition` driven once per
development-stage literal (14 literals x 3 species/tissue pairs = 42).

---

# Defect 1 — the recorded tool panel does not reproduce at HEAD

## What was measured

`tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json`, run inside the
committed HEAD tree (`out/tree_HEAD_954aeae/`), reproduces the card's reading exactly:

```
legacy_panel 9beb43df165f82e6a8de36391d7b29f1   (recorded 4813fca2f5c8c916a233f4825b200b19)
full_panel   5aa0fa546cdcd9e83e48ab390f3d7dcd   (recorded 097328b42ffdb736b6934fa1967ada37)
IDENTITY FAIL: legacy_panel, full_panel moved.   5 of 12 calls differ      (log: logs/e1_probe_headtree.log)
```

The probe keeps digests only, so "five calls differ" was split into its two causes with the raw dump
(`scripts/a3_attribute_mueller.py`, table `out/PANEL_ATTRIBUTION.tsv`, log `logs/e2_attribution.log`):

| cause | calls | measured |
|---|---|---|
| refused on arguments | 4 | `get_kb_page{"kind":"index"}` · `get_kb_page{"kind":"topic","name":"vascular"}` · `get_tissue_composition{"detail":true,...}` · `search_literature{"query":...,"top_k":3}` |
| answered differently | 1 | `explain_annotation{"cell_type":"Mueller cell"}` |
| unchanged | 7 | everything else |

## Which side was wrong: the panel

The panel's argument spellings were never the documented interface. Three independent records agree,
and all three are in the repository at the commits in question:

- `README.md`, "exact signatures" table: `get_kb_page` takes **`scope`** (with `name` required for
  `scope=topic|tissue`); `get_tissue_composition`'s `detail` is a **string** (`full` default /
  `answer`); `search_literature` has **`cell_type` as a required argument**. The panel passed
  `kind`, passed `true`, and omitted `cell_type`.
- The tool signatures in `mcp_server/server.py` (and the core functions in `mcp_server/eyekb_core.py`)
  match the README, not the panel.
- The refusals are emitted by the MCP layer's argument validation before the tool body runs, so those
  four calls never exercised the tools at all — they measured the validator's error text.

Two further measurements settle the question rather than leaving it to a reading of the docs:

1. **The mismatch predates the recording.** The four calls are refused identically at `a400315` (the
   commit that last touched the fixture), at `c4d04d9`, and at HEAD: 4/4 at each
   (`panel.refused_at_a400315 = 4/4`, `panel.refused_at_c4d04d9 = 4/4`). So the panel never matched any
   tracked build of this server on this machine.
2. **The recording came from a different validator version.** The refusal text embeds the validating
   library's own documentation URL, `pydantic.dev/2.12/`, which happens to be this machine's version.
   Rewriting *only* that version substring inside the four refusal texts and re-computing the panel
   digests with the probe's own digest function reproduces the recorded legacy panel exactly at target
   `2.13` (and at no other version tried: 2.10, 2.11, 2.12, 2.14, 2.15 all miss). At target `2.12` the
   same reconstruction returns precisely the values measured at HEAD. Reading: the baseline was
   recorded on an interpreter whose validator rendered the URL as `2.13`, and the four calls were
   already being refused then. `full_panel` cannot be reproduced by that substitution alone because it
   also contains the one call that moved for a content reason — which is defect 1b below.

## Defect 1b — the one answered move, attributed to its commit

`explain_annotation{"cell_type":"Mueller cell"}`:

| commit | md5 | note |
|---|---|---|
| recorded in the fixture (as committed at `a400315`) | `80e96deae5e28482099daee394db7de2` | matches at `a400315` |
| `c4d04d9` | `919fac6e91a67153a214870127407e13` | first commit where it moves |
| HEAD `954aeae` | `919fac6e91a67153a214870127407e13` | unchanged since |

Recursive leaf diff of the parsed payload, `a400315` -> HEAD: **11 fields, all of them
`entries[i].citations[j].tissues`, empty -> populated** (`retina`, `RPE,retina`). `c4d04d9` is
"evidence: attach the papers the corpus could already support" and is a descendant of `a400315`
(checked with `git merge-base --is-ancestor`). So this move is a legitimate content improvement whose
record was never refreshed — it is **not** caused by this card, and re-recording it is not
"making the check green": the alternative would be to keep a baseline that pins an answer the
repository deliberately improved.

## What changed

- `tests/probe_tool_panel_identity.py` — the panel now spells the documented signatures (`scope`, a
  string `detail`, the required `cell_type`). Two rules are now enforced rather than hoped for:
  *a refused call is a FAILURE, not an anchor* (the error text carries the validator's version, so a
  baseline containing one is not reproducible on another interpreter — it measures the MCP layer, not
  the tool), and *the run's interpreter is recorded and compared as an advisory* rather than silently
  changing what the digests mean. Exit codes: `0` match and no refusal, `1` a digest moved **or** a
  call was refused, `3` the server could not be driven at all (not a statement about the service).
- `tests/fixtures/tool_panel_baseline.json` — **deliberate re-record**, argued here and in the registry
  note for row L6-37. It now contains the documented spellings, no refused calls, the advertised tool
  list, and a `provenance` block (interpreter, python, pydantic).

Result, on the shipped bytes:

```
python3 tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json
legacy_panel e8e6c26351cd9a1d42fa2e7cb6a83f23
full_panel   3f1f52cb62915f5ad2801962aa523d36
n_calls 12   refused 0
interpreter /home/ubuntu/training-venv/bin/python3 (python 3.14.4, pydantic 2.12.5)
IDENTITY PASS: both panel digests match the baseline.        rc=0     (log: logs/e1_probe_worktree.log)
```

### Negative direction (stated, not omitted)

- Both recorded panel digests change. A reader diffing the fixture sees a different file; the reason is
  in this report and in the L6-37 registry note, not left to be inferred from a green check.
- The probe is now **stricter**: a future change to a tool signature turns the gate red (`rc=1`) instead
  of silently pinning an error string. That is a new way to fail, and it is intended.
- The old baseline is not deleted: its bytes remain the committed blob at `954aeae`
  (`sha256 c95ae8ade83a8bd90140d600117bc3a042687722ff275464d3c3432269fd9c2e`).

---

# Defect 2 — an unrecognised stage literal returned the adult baseline

## What was measured (before)

`get_tissue_composition(species="human", tissue="retina", development_stage="organoid")` on the
committed HEAD tree: md5 **`53a3565cc92b8eca6462f24d6b77b10d`**, byte-identical to the same call with
`development_stage="adult"` (and with `""`) — the card's quoted digest, reproduced here.

The whole surface was then measured instead of the one literal the card named: 3 species/tissue pairs
x 14 literals (`out/STAGE_SURFACE_BEFORE_AFTER.tsv`, log `logs/d1_stage_surface.log`). At HEAD, the
seven spellings that are not contract tier names — `organoid`, `ORGANOID`, `organoid_Day30`,
`adult_or_unspecified`, `fetel`, `neonatal`, `any` — all reached the adult baseline on human retina, and
`postnatal` folded to `developing` without saying so. The query path was the outlier: the builder side
has implemented the contract since KB2c (`scripts/baselines/build_baselines.py:139`:
`if "organoid" in s: return "unknown", "organoid → unknown + flag (adjudication Q1 mapping)"`), and
every baseline JSON carries a `stage_axis.unknown_rule` that says the same thing. The tool's own
docstring said `organoid -> unknown+flag` while the code fell through. **Shipped bytes contradicted
shipped documentation; the code was the side that was wrong.**

## What changed

`mcp_server/eyekb_core.py` — the literal is now *resolved* before anything is answered:

- `""` and `any` -> the adult main file (`any` is a documented synonym and carries a fold block);
- `fetal` / `developing`, and `postnatal` (which folds to `developing`) -> the developmental transition
  entry;
- `unknown` -> the unknown tier;
- **every other literal** (organoid, organoid_Day30, `ORGANOID`, a typo, `adult_or_unspecified`) ->
  the unknown tier, and it says so.

The disclosure block (`stage_literal`) names the requested literal, whether the spelling is recognised,
the tier it reached, the accepted spellings and the rule it came from. It is attached on **every** path
the query can take after the literal is resolved — the developmental-transition answer, the
unknown-tier answer, the "no unknown-tier entry for this pair" disclosure, the final composition
answer, the compact/`answer` view — and on the "no matching composition entry" error as well, so the
case where nothing answered is still the case where the caller can see that its literal was folded
rather than matched. `mcp_server/server.py` (tool docstring) and `README.md` (signature table plus a
paragraph) state the same rule in the shipped text.

## Acceptance, measured on all 42 rows (not just `organoid`)

`scripts/c3_acceptance.py` states the card's acceptance line as four assertions and runs them over the
whole surface (`out/STAGE_ACCEPTANCE.tsv`, log `logs/e3_acceptance.log`):

- **A1** every literal that is not a contract tier name carries a `stage_literal` block echoing the
  requested literal verbatim (case preserved);
- **A2** the flag distinguishes a documented fold (`stage_literal_folded`: `any`, `postnatal`) from an
  unrecognised literal (`unrecognised_development_stage_literal`), and names the tier reached;
- **A3** the five tier names plus the empty default carry no block — the disclosure is not sprayed onto
  ordinary calls;
- **A4** no unrecognised literal is answered with the adult composition.

```
rows=42  assertions FAIL=0      responses that changed versus the pre-change dump: 24 of 42
```

The three pairs the card's own probe did not cover:

| pair | `organoid` before | `organoid` after |
|---|---|---|
| human / retina | `baseline_human_retina`, organism_stage `adult`, **no flag** | `no_unknown_stage_entry` (disclosure only), flag `unrecognised_development_stage_literal` |
| human / RPE | `baseline_human_RPE`, organism_stage `unknown`, no flag | same entry, now with the flag (this pair's adult baseline *is* the unknown-tier source — a source with no age column — so the defect did not express itself as adult numbers here) |
| mouse / retina | "no matching composition entry", no flag | same error, now with the flag (this species/tissue pair has no entry at all; the answer lends no adult numbers, for any literal) |

### Negative direction (stated, not omitted)

- 24 of 42 (pair, literal) answers change. A caller who passed a hedge word — `organoid`,
  `organoid_Day30`, `neonatal`, `adult_or_unspecified`, a typo — used to receive numbers and now
  receives the unknown-tier disclosure with no numbers and a pointer to
  `kb/baselines/_STAGE_DISCLOSURE.md`. That is the intended loss: the numbers it used to receive
  belonged to a different developmental stage.
- `any` and `postnatal` move by gaining the block only (+310 B and +297 B respectively; no row, no
  interval, no name changes).
- The twelve-call panel is byte-identical before and after, because no panel call supplies a stage
  literal: the change is confined to the stage axis.
- A caller relying on the old fall-through to obtain adult numbers by misspelling a literal loses that
  behaviour. There is no switch to restore it (see "Escape door").

---

# Residuals and criterion notes

1. **`kb/markers/markers_v8_dev_retina.json` exists only on the data mount.** Measured:
   `/mnt/D/EyeKB/kb/markers/markers_v8_dev_retina.json`, 37,960 B,
   sha256 `40d23beaa523704b1de20e6d52220736e7d89f08f967a049b742b4cd06907e56` (matches the card's
   value); no copy under `kb/markers/` in the repository; yet `kb/markers/_concept_kind_sidecar_v1.json`
   (in the repository) references it by name. The V3 stage scripts already fall back to the mount path,
   so nothing this card did depends on it. **Not repaired here**: putting a `kb/markers/` body into the
   repository is a data-plane change with its own registration duty, and the kb/markers copies are in
   another card's scope (`t_c3a3f145`, item 2). Registered as a residual rather than a fix.
2. **Criterion note (not a product defect).** An earlier pass of `c3_acceptance.py` graded the padded
   literal `' fetal '` as unrecognised and reported three A1/A2 failures. The server documents one
   normalisation (trim, lowercase) and applies it; the assertions now classify the same way. Recorded
   here because the first reading was a defect in the criterion, not in the shipped behaviour.
3. **Criterion note on the G6 escape-door rule.** The change-control gate's rule R7 expects a change to
   name an `EYEKB_*` switch as its escape door. This change deliberately adds **no** switch: there is no
   environment gate on the stage path today, and adding a second behaviour to keep in sync would be a
   larger liability than the rollback it buys. The escape door is the commit-level rollback, and its
   identity is measured (below). The row says so plainly rather than inventing a switch to satisfy a
   pattern.
4. **`same_as_adult` is only informative where an adult answer exists.** For mouse retina every literal,
   `adult` included, returns the same "no matching composition entry" error, so "identical to the adult
   response" is trivially true and meaningless there. The acceptance table carries a separate
   `adult_is_composition` column so the two situations cannot be confused, and A4 uses it.

---

# Bookkeeping in the same commit

- `docs/W3_PIPELINE_REGISTRY.tsv` — four rows re-taken from live bytes (sha/bytes/mtime) with one
  appended sentence each, no other cell touched:
  `L1-11M` (`mcp_server/eyekb_core.py`), `L6-06` (`README.md`), `L6-36`
  (`tests/probe_tool_panel_identity.py`), `L6-37` (`tests/fixtures/tool_panel_baseline.json`).
  Readout: `logs/f1_reg_retake.log`.
- `docs/W3_MANIFEST.sha256` — re-frozen for the registry line with the transition recorded in its
  comment block; `sha256sum -c W3_MANIFEST.sha256` inside `docs/` -> **4/4 OK, rc=0**
  (`logs/f2_manifest_reanchor.log`).
- `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` — one new row, `CHG-20261022-SHIPPED-SURFACE`, arguing the
  re-record (cause, layer, blast radius, pre-registered criteria, escape door, sha evidence, rollback
  identity, differential reading including the negative column, ledger registration).
- `docs/W3_PIPELINE_REGISTRY.tsv` row L1-11 (the D-side runtime volume,
  `/mnt/D/EyeKB/mcp_server/eyekb_core.py`) is **not** touched and still matches its file
  (`feff1e12fd8109c4...`): this card changes the repository-side delivery volume only. Per the standing
  ruling (PI t_830ff5f9) the two volumes are separate and are not force-synced; the D-side copy was not
  deployed to, and its row remains accurate.
- Gates: `python3 tests/gate_registry.py` (G5) and `python3 tests/gate_change_control.py` (G6) both
  re-run green after the bookkeeping (readouts `logs/g5_gate.log`, `logs/g6_gate.log`). G3 and G4 do
  not read any file this card changed (`tests/verify_repro.py` loads
  `clients/ocularkb/rag/scripts/stage3_retrieve.py`; G4's anchors are pipeline artefacts), so they are
  unchanged by construction.

# Escape door / rollback identity (two independent readings)

1. **Committed-bytes path.** The pre-change state is the committed blob tree at `954aeae`. A dump taken
   from a `git archive` of that tree reproduces the recorded pre-change panel digests
   (`legacy_panel 4813fca2f5c8c916a233f4825b200b19`, `full_panel 097328b42ffdb736b6934fa1967ada37`)
   and the pre-change stage table (`out/DUMP_PRE_HEAD_v2.json`, `out/STAGE_SURFACE_BEFORE_AFTER.tsv`).
2. **Revert path.** `git revert <this commit>` restores exactly those blobs, so the OFF state is
   byte-identical by construction; the per-file pre-change sha256 values are in
   `out/REPORT_NUMBERS.tsv` (`file.sha256_HEAD.*`).

Both readings agree. Nothing was edited in place without its previous state remaining retrievable from
git history.

# Reproduce everything

```
cd /home/ubuntu/EYEKB_REPO
PY=/home/ubuntu/training-venv/bin/python3
P=docs/plans/shipped_surface_20261022

bash $P/scripts/d1_dump_pair.sh /tmp/ss_repro v2   # before/after dumps (regenerated, not quoted)
$PY $P/scripts/a3_attribute_mueller.py --pre /tmp/ss_repro/DUMP_PRE_HEAD_v2.json \
    --hist /tmp/ss_verify/dump_a400315.json /tmp/ss_verify/dump_c4d04d9.json \
    --baseline-head /tmp/ss_repro/tree_HEAD_954aeae/tests/fixtures/tool_panel_baseline.json \
    --out /tmp/ss_repro/PANEL_ATTRIBUTION.tsv                          # defect 1 attribution
$PY $P/scripts/c2_stage_surface.py --before /tmp/ss_repro/DUMP_PRE_HEAD_v2.json \
    --after /mnt/D/EyeKB/plans/shipped_surface_20261022/out/DUMP_POST_WORKTREE_v3.json \
    --out /tmp/ss_repro/STAGE.tsv                                              # before/after table
$PY $P/scripts/c3_acceptance.py \
    --after /mnt/D/EyeKB/plans/shipped_surface_20261022/out/DUMP_POST_WORKTREE_v3.json \
    --before /tmp/ss_repro/DUMP_PRE_HEAD_v2.json --out /tmp/ss_repro/ACCEPT.tsv # 42-row acceptance
$PY tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json  # IDENTITY PASS
$PY $P/scripts/g1_numbers.py --out /tmp/ss_repro/NUMBERS.tsv            # every number in this report
( cd docs && sha256sum -c W3_MANIFEST.sha256 )                          # 4/4 OK
$PY tests/gate_registry.py ; $PY tests/gate_change_control.py           # G5, G6
```

`$PY $P/scripts/b1_bisect.sh /tmp/ss_verify $PY a400315 c4d04d9` regenerates the two historical dumps
that pin the answered move to a commit (they are kept in `out/PANEL_ATTRIBUTION.tsv` by digest).

# Artefacts

| path | what it is |
|---|---|
| `out/DUMP_PRE_HEAD_v2.json` (local evidence root) | 54-call dump of the committed HEAD tree (before) |
| `out/DUMP_POST_WORKTREE_v2.json`, `out/DUMP_POST_WORKTREE_v3.json` (local evidence root) | the same 54 calls on the work tree (v3 = after the error-path disclosure) |
| `out/PANEL_ATTRIBUTION.tsv` | per-call attribution: recorded / a400315 / c4d04d9 / HEAD / verdict |
| `out/STAGE_SURFACE_BEFORE_AFTER.tsv` | 42 rows: entry, stage, flag, adult-equality, byte delta, before and after |
| `out/STAGE_ACCEPTANCE.tsv` | the same 42 rows judged by A1-A4 |
| `out/REPORT_NUMBERS.tsv` | every number in this report with its source and how it was obtained |
| `scripts/` | `a1_dump_panel.py` (dump), `a3_attribute_mueller.py` (attribution, used for every number above), `b1_bisect.sh` (commit-bisect driver), `c1_apply_stage_fix.py` (the applied text), `c2_stage_surface.py` (before/after table), `c3_acceptance.py` (acceptance), `g1_numbers.py` (number extraction), `reg_retake.py` (registry rows), `f2_manifest_reanchor.py` (manifest) |
| `logs/` | the raw output of every step above |

**Provenance of the artefacts.** This card ran twice: the first attempt (`run 3300`) crashed at
01:43:26 after writing `scripts/a1..c2` and `logs/a2..c2`; nothing had been committed, so its work
product sat unverified in the work tree. This attempt (`run 3302`) re-derived every reading from
committed bytes (`d1_dump_pair.sh`, `a3_attribute_mueller.py`, `c2`, `c3`, `g1`), re-ran the panel
probe in both trees, extended the fix to the error path, and wrote the bookkeeping. Files from the
first attempt that are still in `logs/` (`a2_attribute.log`, `b2..b6`) are kept as the earlier
attribution route; where they disagree with `a3` the reading in this report is the one reproduced in
`logs/e2_attribution.log` — specifically, `a2_attribute.log` prints `recorded <none>` for every call
because its dump keys and the fixture's keys were built by different dump generations, which is why the
attribution was redone with a key normaliser rather than trusted.

Commit: see `COMMIT.txt` in this directory (written after the commit, and therefore not inside the
manifest).

---

# Late addition (written before the commit, same card)

- **The local evidence root now carries the manifest this report refers to:**
  `/mnt/D/EyeKB/plans/shipped_surface_20261022/out/MANIFEST.sha256`.
  `cd /mnt/D/EyeKB/plans/shipped_surface_20261022/out && sha256sum -c MANIFEST.sha256` -> **4/4 OK,
  rc=0**. Besides the three 54-call dumps named above it lists `PANEL_AT_HEAD.json`, the twelve-call
  panel dump of the first attempt (run 3300): kept because every intermediate artefact is retained, and
  it is that attempt's reading — where it disagrees with this report, the reading in this report is the
  one reproduced in `logs/e2_attribution.log`. The manifest itself is excluded from its own coverage.
- **Nothing in this report depends on the first attempt's uncommitted work product.** It was re-derived
  from committed bytes in the second attempt (see "Provenance of the artefacts"). At the end of this
  run, the delivered readings were re-measured one more time on the frozen tree: the panel probe
  `IDENTITY PASS` with zero refused calls, `W3_MANIFEST.sha256` 4/4 OK, G5 and G6 both rc=0,
  `c3_acceptance.py` and `g1_numbers.py` regenerating `out/STAGE_ACCEPTANCE.tsv` and
  `out/REPORT_NUMBERS.tsv` byte-identically from the retained dumps.
- **Commit structure.** The fix is one commit; `COMMIT.txt` names it and is itself committed in a
  second, record-only commit, so the working tree is left clean and a reader can see that nothing was
  left uncommitted. Neither this file nor `COMMIT.txt` can contain the hash of the commit that contains
  them; that is why the hash lives in `COMMIT.txt`.
- **Residual 1, re-checked rather than inherited.** The card allowed the missing
  `kb/markers/markers_v8_dev_retina.json` to be left alone "unless cheap". It is left alone, and the
  reason is measured: the repository's own development-panel code path reads a different file
  (`mcp_server/eyekb_core.py:934`, `DEV_PANEL_FILE = MARKER_DIR / "markers_v9_dev_retina.json"`), the v8
  file is consumed by the developmental-lineage line's scripts through a declared mount fallback
  (`docs/plans/devlineage_20261021/stages/scripts/03_robustness_probe.py:57-61`, which names both the
  repository path and `/mnt/D/EyeKB/kb/markers/` and reports when neither is present), and the only
  in-repository reference to it is the sidecar `kb/markers/_concept_kind_sidecar_v1.json:397`. Copying it
  in would add a marker-library body to the shipped `kb/markers/` directory and therefore carry its own
  registration duty, so it stays a residual of the lineage card's scope rather than a fix here.
