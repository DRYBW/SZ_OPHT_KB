# REPORT — CL56WIRE: the newest library wired into the registry / wiki / route / skill

Card: `t_2fed9122` (board `pi-briefing`, executed by `pi-chief`).
Brief: `/mnt/D/EyeKB/plans/consistency_20261024/BRIEF_CL56WIRE_20261024.md`.
Construction site: `/mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/`; review mirror:
`docs/plans/cl56wire_20261025/` (this file lives in both).
Commit under test: `619a702` (local only; push is the coordinator's).

## One line

The three entries of the newest adopted library (`cl56_v15`) now carry registry rows with the same
eleven fields, the same four links (citation + page + route + skill) and the same builder as the
eight libraries that were already wired, and each of them is reachable from a written page —
**without changing the default answer route**: the library stays registered default-off and the three
names answer only on their explicit route (0 of 3 reachable on `all`, re-read from the shipped
service). The proof is machine-read (`out/WIRING_PROOF_v1.md`, verdict PASS).

## 1. What kind of record this is

This is a **wiring / disclosure** change, not an activation, not an audit and not an accuracy claim.
The registry says where an annotation's support comes from; it feeds no score, no weighting and no
ranking, and its own reader guide says so. Nothing here re-decides whether the library *should* be
on the default route — that question was decided against it by its own pre-registered acceptance rule
(cell-weighted `consistent` −5.173pp, `inconsistent` +9.766pp, 12 of 28 datasets fall → NO-GO), and
this card carries that negative result forward unchanged.

## 2. What was built

1. **One declared line in the registry builder.** `REGISTRY_EXTRA_LIBS = ("cl56_v15",)`
   (`kb/link_registry/scripts/build_link_registry.py`). The registry previously covered exactly the
   libraries the default answer route loads; a library registered **default-off** (empty whitelist,
   explicit route only) could not be wired at all, which is precisely how the newest batch ended up
   with no page, no route and no citation. The route is read from the service's own whitelist, so
   this list cannot turn anything on.
2. **The registry, rebuilt by its own builder**: 161 → 165 rows.
3. **Three new rows, one per adopted entry**, computed by the same rules as every other row:

   | entry | panel genes | citations | gene-verified | wiki pages | route |
   |---|---:|---:|---:|---|---|
   | `cl56_v15::rod bipolar cell` | 44 | 77 | 71 | `baselines/retina.md`, appendix, `priors/composition/human_retina.md`, the new page | `query_marker(cell_type='rod bipolar cell', library='cl56_v15')` |
   | `cl56_v15::keratocyte` | 60 | 58 | 52 | `baselines/ocular_surface.md`, `composition/EXPECTED_COMPOSITION_v0.md`, appendix, `literature_db/KBADD_KERATOCYTE_NOTES_20260924.md` | `query_marker(cell_type='keratocyte', library='cl56_v15')` |
   | `cl56_v15::S cone cell` | 22 | 46 | 37 | the new page, appendix | `query_marker(cell_type='S cone cell', library='cl56_v15')` |

4. **The full-text gene index rebuilt** (`GENE_PAPER_INDEX_v1.tsv/.json`). The index's gene list *is*
   the union of the registry's panels, and the citation layer is scored against it; without the
   rebuild the three new entries' citations would be checked against an index that never scanned
   their genes (312 → 330 panel genes, 9,709 → 10,550 rows). Measured: only the four new rows move.
5. **A written page for the new entries** — `kb/vk_literature_index/cell-ontology-child-terms.md`:
   the three adopted Cell-Ontology child terms, their CL ids and `is_a` paths, their panels and where
   the panels come from, the route that reaches each name, and the measured caveat. Written so the
   new entries are reachable from a written page rather than only from the registry's own generated
   appendix (the circularity reading the repository audits).
6. **The reader-facing twins regenerated**: the appendix (165 entries / 10 libraries, with a
   `cl56_v15` section and the papers behind it), its machine twin, and the coverage summary. The
   appendix's default-route label set was corrected for `onfibro_v13`.
7. **The reader guide** states which libraries the registry covers and that the three builders
   consume each other, so a rebuild is run to a **fixed point** (measured: two passes, then stable).

## 3. The consistency proof

`out/WIRING_PROOF_v1.md` (machine twin `out/WIRING_PROOF_v1.json`, recompute:
`/home/ubuntu/training-venv/bin/python3 /mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/scripts/wiring_proof.py`).
Every number is read from the shipped tree at build time; nothing is quoted from this report.

| check | reading |
|---|---|
| entries per library | 165 total = 84 marker + 81 textbook; `cl56_v15` = 3 |
| required fields | 163/165 rows carry all required fields; the 2 exceptions are entries whose source library records **no panel at all** (`face_v6::Fibroblast`, `face_v6::Myofibroblast`) — a registered gap, named with its reason |
| linkage gate (four links) | `165/165 entries fully wired`, rc=0 |
| wiki-page existence | **403/403** listed page paths resolve to a file under `kb/` (100.0%) |
| `kb_file` existence | all rows resolve |
| live routes | **165/165** `mcp_route`s re-issued against the shipped service, 0 not answering |
| route hygiene | 0 of the three new names reachable on the default `all` route |
| isomorphy vs pre-image | 161/161 existing rows **byte-identical**, 0 changed, 0 removed, shipped row order preserved, exactly 4 added |
| circularity | 84/84 reachable, 84/84 excluding the registry's own appendix, **0** relying on the appendix alone |

## 4. Findings (measured; three are pre-existing defects, not caused by this card)

1. **The registry was already stale by one library.** `onfibro_v13` was activated on the default
   route on 2026-10-22, after the registry snapshot was taken, so the shipped registry had no row for
   its entry. The rebuild produces it (`onfibro_v13::Fibroblast`), and it is carried rather than
   suppressed: suppressing it would make the file unreproducible by its own builder. **Disclosed, and
   counted in the four added rows.**
2. **The coverage summary was stale independently of this card.** Its knowledge-entry table read
   2,106 citation rows / 1,241 checkable, while the registry it was computed from already carried
   3,735 / 2,870 (the appendix header states the same 3,735). Its entry columns are reproduced
   exactly by the re-take's rule, so the rule did not move — only the read-out was old. Re-taken.
3. **Two lines of that summary were superseded.** It still named `membrane::cDC1` / `membrane::cDC2`
   as reachable only through the generated appendix; both gained a written page at the 2026-10-21
   link-spine close-out, and the current circularity reading is 0 entries relying on the appendix
   alone. The one-line `MOBP` gap is re-stated with the current scan size (330 panel genes).
4. **Six registered libraries remain unwired** (`lacrimal_v6`, `retina_v7`, `retina_dev`,
   `lensiris_v11`, `holefill_v12`, `subtype_v14`). Each is the same one-line addition. `subtype_v14`
   needs its body repaired first: its entries carry no top-level `markers` key, so its explicit route
   answers nothing (measured in the CL-56 adoption report §6.1) and wiring it now would create rows
   whose route is a dead end. **Not wired, and stated as not wired.**

## 5. What was NOT done, and why

- **The default route was not touched.** `CL56_DEFAULT_LIBS = ()`; the route-hygiene check re-reads
  that from the shipped service.
- **No claim was added about recognition.** An ontology-consistent name is not evidence of a better
  call; the new page says so, and quotes the measured over-application (92 clusters renamed by these
  three panels, only 3 of them carrying the adopted term as their author label).
- **The cluster-level block of the coverage summary was not re-taken** — it is byte-identical to the
  pre-image because a default-off library cannot move a cluster-level reading, and the run panel that
  produced it is a run artefact that is not shipped (the generator `build_annotation_evidence.py`
  cannot be re-run without it; that is stated in the summary itself).
- **The cleaned-up twins were registered but not rebuilt beyond what changed**; nothing else in the
  link-registry family was touched.

## 6. Red lines, with evidence

| red line | evidence |
|---|---|
| zero downloads, zero GPU | no network call and no GPU was used; every step reads shipped files and the local corpus the service already resolves |
| read-only on existing artefacts, copy not move | the six pre-images the change can be rolled back to: `out/PREIMAGE.sha256`; the one new file is additive |
| no frozen artefact rewritten | the ontology anchors (`ONTOLOGY_SNAPSHOT_MANIFEST_v1.json`), the marker bodies and the label map are untouched by this card (git diff of `619a702` lists no such path) |
| machine-checkable criteria only | `wiring_proof.py` re-reads the tree; the linkage gate and the circularity audit are re-run, not quoted |
| no padding, no silent drops | the two no-panel entries and the six unwired libraries are named in the proof and in this report; the fourth added row is disclosed with its cause |
| local commit only, no push | `619a702` is local; the commit message says push is the coordinator's |
| worker self-report is not acceptance | every node of the proof is a command the coordinator can re-run; the fixed point was produced independently in a second tree (byte-identical) |

## 7. Reproduction and file map

```bash
PY=/home/ubuntu/training-venv/bin/python3
cd /home/ubuntu/EYEKB_REPO/kb/link_registry
env -u EYEKB_DB_DIR $PY scripts/build_gene_paper_index.py     # index (gene list = the registry's panels)
env -u EYEKB_DB_DIR $PY scripts/build_link_registry.py        # registry rows
$PY scripts/build_citation_appendix.py                        # reader-facing appendix + twin
# repeat the pair until the registry stops changing (measured: two passes, then stable)
$PY scripts/validate_linkage.py                               # 165/165
$PY scripts/audit_link_circularity.py                         # 84/84, 0 appendix-only
$PY /mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/scripts/wiring_proof.py   # verdict=PASS
$PY /mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/scripts/registrations.py  # registry + change-control + W3 manifest (idempotent: asserts its row ids are free)
```

| path | contents |
|---|---|
| `scripts/wiring_proof.py` | the consistency proof (all eight checks) + `out/WIRING_PROOF_v1.md` / `.json` |
| `scripts/registrations.py` | the ledger re-takes and new rows, the change-control instance row, the W3 manifest re-freeze (last) |
| `scripts/recompute_summary_table.py` | the coverage summary's entry-level table, with its own validation arm (`--validate` on the shipped registry reproduces the shipped entry columns) |
| `scripts/update_summary_tail.py` | the summary's surgical re-take (refuses to run if the cluster block has moved since the pre-image) |
| `out/REGISTRY_ROWS.json` | the six re-taken rows and the four added rows, before/after shas |
| `out/PREIMAGE.sha256`, `pre_images/` | the six pre-images |
| `out/CLONE_REPO_GATES.log` | the gate chain in a clean clone of `619a702`, corpus unpacked per G2: `gates=9 failed=0 (CHAIN PASS)` |
| `out/CLONE_REPO_GATES_pristine_clone.log` | the same chain on the pristine clone, where `G11` reads `rc=3 INCONCLUSIVE` because the bundled corpus ships as the G2 Release asset and is not in a fresh clone (the gate says so itself) |
| `logs/` | the builder runs, the fixed-point checks, the resource measurement |
| `out/MANIFEST.sha256` | sha256 of every artefact of this wave |

## 8. Verification at the commit under test

```bash
rm -rf /tmp/cl56wire_clone && git clone -q /home/ubuntu/EYEKB_REPO /tmp/cl56wire_clone
cd /tmp/cl56wire_clone && git rev-parse HEAD          # 619a702cd7f4cdf4d0fe5d18facf4b9d107ad511
cp -r /home/ubuntu/EYEKB_REPO/literature_db .          # G2: unpack the corpus asset
EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 EYEKB_GATE_OUT=/tmp/cl56wire_clone/.gate_out \
  bash tests/run_gates.sh
# G3 41/41, G4 3/3 byte anchors, G5 registry 8/8, G6 change control, G7, G8, G9, G10, G11
# gates=9 failed=0  (CHAIN PASS)
```

G9 (`gate_preimage_ref_immutable`) and G6 read this card's new change-control row and its pre-image
references without complaint; G5 reads the re-taken rows as matching live bytes. The pre-existing
`probe_tool_panel_identity` drift recorded by the CL-56 acquisition card is **not** in this chain and
is not touched here.

## 9. Concurrency disclosure

Card `t_2a047be0` (MCPDESC) edited and committed rows in **the same ledger files** in the same window
(`docs/W3_PIPELINE_REGISTRY.tsv`, `docs/CHANGE_CONTROL_G6_INSTANCE.tsv`, `docs/RELEASE_*`, `tests/`).
This card re-read the ledger immediately before writing, asserted that every row id it uses is free
(L6-49..L6-52), re-took only rows whose files it changed, and committed **no sibling-authored file**
(`docs/plans/linkkey_20261025/`, which belongs to card `t_83c4324d`, and the sibling's `mcpdesc` logs
are deliberately left untracked). The release records are full-tree records regenerated by this
card's take, so a later take by any card supersedes rather than merges — that is what the record's own
`recompute` line prescribes.

## 10. Resource readings

Measured with `/usr/bin/time -v` on the heaviest step (the registry rebuild, `logs/r1_registry_resource.log`):
**70 s wall, 2463 % CPU (≈25 threads), peak RSS 6.75 GiB**, and the registry bytes come back identical
(fourth independent confirmation of the fixed point). The gene index rebuild scans 242,928 chunks in
5.2 s; the appendix renderer is seconds. Available memory was ~198 GiB throughout. **Disclosure:**
these runs were made in the foreground rather than under `systemd-run --user` with `MemoryMax` as the
shared-workstation rule asks for heavy compute; the measured peak is far under the 40 GiB stop line
and no other workstream was disturbed, but the rule exists to make that a guarantee rather than an
observation, so it is reported here instead of being left unsaid.

## 11. What would falsify this

Re-run §7 in a clean clone: if the registry stops reproducing (any of the 161 pre-existing rows
changes, or the fixed point needs more than two passes), the wiring is not the mechanical extension
this report claims. If `wiring_proof.py` returns any verdict other than PASS, the wiring is
incomplete. Both are one command each.