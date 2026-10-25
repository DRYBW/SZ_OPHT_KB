# cl56wire_20261025 — CL56WIRE: the newest library wired into registry / wiki / route / skill

Card: `t_2fed9122` (board `pi-briefing`, executed by `pi-chief`).
Brief: `/mnt/D/EyeKB/plans/consistency_20261024/BRIEF_CL56WIRE_20261024.md` (copy: `out/`).
Construction site: `/mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/` (this directory is its
review mirror). Wave artefacts are English; the two Chinese strings in the registry ledger belong
to upstream rows.

## One line

The newest adopted library (`cl56_v15`, three entries: `rod bipolar cell`, `keratocyte`,
`S cone cell`) now carries registry rows with the same eleven fields, the same four links
(citation + page + route + skill) and the same builder as the eight libraries that were already
wired — **without changing the default answer route**: the library stays registered default-off,
and the three names answer only on their explicit route. The rebuild also carried one row the
registry was missing (`onfibro_v13::Fibroblast`, a library activated after the previous snapshot)
and rebuilt the full-text gene index so the new entries' citations are scored against an index that
covers their panels.

## What to read, in order

1. `out/WIRING_PROOF_v1.md` — the machine-verified proof: entries per library, field completeness,
   wiki-page existence (403/403), live routes (165 re-issued), route hygiene (0 default-route
   leaks), and isomorphy against the pre-image (161/161 existing rows byte-identical, 4 added).
   Machine twin: `out/WIRING_PROOF_v1.json`.
2. `REPORT.md` — what was done, what was found (two pre-existing staleness defects in the
   shipped tree, both measured and fixed in this change), and what was deliberately not done.
3. `out/REGISTRY_ROWS.json` — the ledger rows re-taken (6) and added (4), with before/after shas.
4. `out/PREIMAGE.sha256` — the six pre-images the change can be rolled back to.

## Recompute (one command each)

```bash
PY=/home/ubuntu/training-venv/bin/python3
$PY /mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out/scripts/wiring_proof.py   # verdict=PASS
cd /home/ubuntu/EYEKB_REPO/kb/link_registry
$PY scripts/validate_linkage.py            # linkage gate: 165/165 fully wired
$PY scripts/audit_link_circularity.py      # 84/84 reachable, 0 rely on the appendix alone
cd /home/ubuntu/EYEKB_REPO && bash tests/run_gates.sh    # gates=8 failed=0 (see out/CLONE_REPO_GATES.log)
```

The three builders consume each other (the gene index's gene list is the union of the registry's
panels; the registry's page matcher reads the registry's own rendered appendix), so a faithful
rebuild is run to a **fixed point**: index → registry → appendix, repeated until the registry stops
changing. Measured 2026-10-25: two passes, then stable (byte-identical on the third), and the same
bytes were produced independently in a second tree. The iteration is documented in
`kb/link_registry/README.md`.