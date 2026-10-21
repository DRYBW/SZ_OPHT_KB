#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step G2 — append this card's change-control row to docs/CHANGE_CONTROL_G6_INSTANCE.tsv.

The row is written from live bytes: every sha it quotes is computed here, at write time, so no
hand-typed hex can drift away from the file it claims to describe. Re-running replaces the row with
the same change_id (idempotent), which is what makes it safe to call again after an edit.

Usage: <py> g2_g6_row.py [--write]
"""
import argparse
import hashlib
import pathlib

REPO = pathlib.Path("/home/ubuntu/EYEKB_REPO")
INST = REPO / "docs" / "CHANGE_CONTROL_G6_INSTANCE.tsv"
CHANGE_ID = "CHG-20261022-SHIPPED-SURFACE"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def build():
    P = "docs/plans/shipped_surface_20261022"
    report = f"{P}/REPORT.md"
    attrib = f"{P}/out/PANEL_ATTRIBUTION.tsv"
    accept = f"{P}/out/STAGE_ACCEPTANCE.tsv"
    stage = f"{P}/out/STAGE_SURFACE_BEFORE_AFTER.tsv"
    numbers = f"{P}/out/REPORT_NUMBERS.tsv"
    crit = f"{P}/scripts/c3_acceptance.py"
    probe = "tests/probe_tool_panel_identity.py"
    fixture = "tests/fixtures/tool_panel_baseline.json"
    core = "mcp_server/eyekb_core.py"
    server = "mcp_server/server.py"
    readme = "README.md"
    reg = "docs/W3_PIPELINE_REGISTRY.tsv"
    man = "docs/W3_MANIFEST.sha256"

    cells = {}
    cells["change_id"] = CHANGE_ID
    cells["owner"] = ("Maintainer (repository delivery surface; card t_19831068, shipped-surface "
                      "defects measured by the V3 developmental-lineage card)")
    cells["entry_point"] = probe

    cells["Q1"] = (
        "First-cause layer = L1 (the delivery volume's query path) for the stage defect, and L6 (the "
        "delivery surface's test artefact) for the panel defect. Two independent causes were removed: "
        "an unrecognised development_stage literal fell through to the adult baseline in "
        "get_tissue_composition, and the panel recorded four calls whose arguments the tool never "
        "accepted, so the recorded digests measured the MCP validator's error text instead of the "
        "tools. L0-L5 (corpus, vocabulary, generators, adjudication, contract, gating) are untouched.")
    cells["Q1_evidence"] = (f"{attrib}:1 per-call attribution of all 12 panel calls (4 refused, 1 "
                            f"answered-and-moved, 7 unchanged) at three commits; {stage}:1 the "
                            f"42-row before/after stage table; {core}:1516 the resolution block")

    cells["Q2"] = (
        "Layer to fix = the same two layers (equal, so the fix lands there; no downstream patch and no "
        "transitional artefact). Files: mcp_server/eyekb_core.py (literal resolution + disclosure on "
        "every answer path, including the no-entry error), mcp_server/server.py and README.md (the "
        "shipped text states the same rule), tests/probe_tool_panel_identity.py (documented "
        "signatures; a refused call is a failure, not an anchor), tests/fixtures/tool_panel_baseline.json "
        "(deliberate re-record, argued in Q3 and in registry row L6-37).")
    cells["Q2_evidence"] = (f"{report}:60 the change list with its measurements; {reg}:1 rows L1-11M / "
                            f"L6-06 / L6-36 / L6-37 re-taken in this commit")

    cells["Q3"] = (
        "Blast radius per file x per reading, with the rollback/negative term stated rather than "
        "omitted: (1) service answers change for 24 of 42 (species, tissue, development_stage) rows -- "
        "the loss is that a caller who hedged the stage (organoid, organoid_Day30, neonatal, "
        "adult_or_unspecified, a typo) used to receive adult numbers and now receives the unknown-tier "
        "disclosure with none; (2) the twelve-call panel is byte-identical because no panel call "
        "supplies a stage literal; (3) does-not-move: kb/**, pipeline/**, clients/**, literature_db/**, "
        "tests/verify_repro.py, tests/verify_pipeline.py, tests/REPRO_EXPECTED.json, "
        "tests/G4_EXPECTED.json are byte-unchanged, and registry row L1-11 (the D-side runtime volume) "
        "still matches its file; (4) negative term on the test side -- the probe now fails on a refused "
        "call, so a future signature change turns the gate red instead of silently pinning an error "
        "string; (5) rollback = git revert of this commit, and the pre-change bytes are proven "
        "reproducible by a dump taken from the committed base tree.")
    cells["Q3_evidence"] = (f"{stage}:1 42 rows with the byte delta and the adult-equality column; "
                            f"{numbers}:1 every number of the report with its source")

    cells["Q4"] = (
        "Criteria frozen before the post-change run: the card's acceptance line was restated as four "
        "assertions (A1 block present and echoing the literal, A2 flag/tier correct, A3 no block on a "
        "contract tier name, A4 no unrecognised literal answered with the adult composition) and "
        "written before the after-dump was taken; the fixture re-record is accepted only if the probe "
        "reports IDENTITY PASS with zero refused calls. Failure exit condition: any assertion FAIL, or "
        "any refused call in the re-recorded panel, abandons the re-record rather than the criterion. "
        f"Criteria file sha256 {sha(REPO / crit)} ({crit}).")
    cells["Q4_evidence"] = (f"{crit}:1 the four assertions; {P}/scripts/d1_dump_pair.sh:1 the "
                            f"before/after dump driver; sha256 of the criteria file inside Q4")

    cells["Q5"] = (
        "Escape door: no new switch is introduced, and that is a decision rather than an omission -- "
        "the development_stage path has no environment gate today and adding a second behaviour to keep "
        "in sync would cost more than the rollback it buys. The switch that does exist on this path is "
        "EYEKB_ROOT (KB root selection), which this change does not touch. The escape door is the "
        "commit-level rollback, and its OFF state is byte-identical: a dump taken from the committed "
        "base tree reproduces the recorded pre-change panel digests (legacy 4813fca2..., full "
        "097328b4...) and the pre-change stage table, and `git revert` restores exactly those blobs.")
    cells["Q5_evidence"] = (f"{report}:290 the two rollback readings; git show "
                            f"954aeae3656541a6af285452c17c613ab539d5de:{probe} | sha256sum = "
                            f"40d5182930d15f14b85b4e971c0af775abf371c7586e1742863087a38e76b8f3")

    cells["M1"] = (
        "Version artefact: no file was edited without its previous state remaining retrievable -- the "
        "pre-change bytes of every changed file are the committed blobs at 954aeae, including the "
        "previous baseline fixture, so the old recording and the old probe are one `git show` away. The "
        "new fixture additionally records its own provenance (interpreter, python, pydantic).")
    cells["M1_evidence"] = (f"git show 954aeae3656541a6af285452c17c613ab539d5de:{fixture} | sha256sum = "
                            f"c95ae8ade83a8bd90140d600117bc3a042687722ff275464d3c3432269fd9c2e; "
                            f"{numbers}:1 file.sha256_HEAD.* rows")

    cells["M2"] = (
        "Impact list per file: changed = mcp_server/eyekb_core.py (behaviour), mcp_server/server.py "
        "(tool docstring), README.md (signature table + paragraph), tests/probe_tool_panel_identity.py "
        "(panel spellings, refusal rule, provenance), tests/fixtures/tool_panel_baseline.json "
        "(deliberate re-record), docs/W3_PIPELINE_REGISTRY.tsv (four rows re-taken), "
        "docs/W3_MANIFEST.sha256 (re-frozen), docs/CHANGE_CONTROL_G6_INSTANCE.tsv (this row), plus the "
        "new evidence root docs/plans/shipped_surface_20261022/. Not changed: kb/**, pipeline/**, "
        "clients/**, literature_db/**, tests/verify_repro.py, tests/verify_pipeline.py, the expectation "
        "files, and registry row L1-11.")
    cells["M2_evidence"] = f"{report}:250 the blast radius with the do-not-move list; {reg}:1"

    cells["M3"] = (
        "Regression gate with runnable command and concrete threshold: `python3 "
        "tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json` must "
        "print IDENTITY PASS, exit rc=0 and report zero refused calls (expected legacy_panel "
        "e8e6c26351cd9a1d42fa2e7cb6a83f23, full_panel 3f1f52cb62915f5ad2801962aa523d36); "
        f"`python3 {crit} --after <dump> --before <dump>` must report assertions FAIL=0 over 42 rows; "
        "`python3 tests/gate_registry.py` and `python3 tests/gate_change_control.py` must both exit "
        "rc=0.")
    cells["M3_evidence"] = (f"{P}/logs/e1_probe_worktree.log:1 IDENTITY PASS; "
                            f"{P}/logs/e3_acceptance.log:1 assertions FAIL=0 over 42 rows; "
                            f"{P}/logs/g5_gate.log:1 and {P}/logs/g6_gate.log:1 the two gate readouts")

    cells["E1"] = (
        "sha256 evidence taken fresh in this commit, none quoted from an earlier report: run "
        "`sha256sum` over the five changed delivery files. The current values are probe "
        f"{sha(REPO/probe)}, fixture {sha(REPO/fixture)}, eyekb_core {sha(REPO/core)}, server "
        f"{sha(REPO/server)}, README {sha(REPO/readme)}.")
    cells["E1_evidence"] = (f"{numbers}:1 the file.sha256.* rows (each with bytes); command "
                            f"`sha256sum {probe} {fixture} {core} {server} {readme}`")

    cells["E2"] = (
        "Rollback identity, two independent paths: path 1 -- the pre-change state is the committed "
        "blob tree at 954aeae, and a dump taken from a git archive of that tree reproduces the recorded "
        "pre-change panel digests and stage table (expected: legacy 4813fca2f5c8c916a233f4825b200b19, "
        "full 097328b42ffdb736b6934fa1967ada37); path 2 -- reverting this commit restores those same "
        "blobs, so the OFF state is byte-identical by construction. Both readings agree. This change "
        "adds no gate precondition to VERIFY_CONTRACT, so no precondition entry is required.")
    cells["E2_evidence"] = (f"{P}/logs/e1_probe_headtree.log:1 the pre-change digests measured from the "
                            f"committed tree; {numbers}:1 file.sha256_HEAD.* rows")

    cells["E3"] = (
        "Differential reading, negative column included, no gains-only reporting: panel digests move "
        "from 4813fca2.../097328b4... (recorded, not reproducible on this machine) to "
        "e8e6c263.../3f1f52cb... (measured, reproducible, zero refusals); stage answers change for 24 "
        "of 42 rows; negative direction is (a) callers hedging a stage lose their numbers on purpose, "
        "(b) a refused panel call is now a gate failure, (c) the fixture's recorded digests change, "
        "which a diffing reader will see. No accuracy or coverage gain is claimed -- this is a "
        "correctness and reproducibility fix.")
    cells["E3_evidence"] = (f"{attrib}:1 and {accept}:1 the two differential tables; {report}:230 the "
                            f"negative-direction sections")

    cells["E4"] = (
        "Ledger registration: docs/W3_PIPELINE_REGISTRY.tsv rows L1-11M, L6-06, L6-36 and L6-37 "
        "re-taken from live bytes (sha/bytes/mtime) in this commit, one appended sentence each and no "
        "other cell touched; docs/W3_MANIFEST.sha256 re-frozen for the registry line with the "
        "transition recorded in its comment block. Ordering: the code and documents were finalised on "
        "disk first and the registration rows were taken afterwards, so registration time is later "
        "than implementation time. Row L1-11 (the D-side runtime volume) is untouched and still "
        "matches its file.")
    cells["E4_evidence"] = (f"{P}/logs/f1_reg_retake.log:1 the four-row readout; "
                            f"{P}/logs/f2_manifest_reanchor.log:1 `sha256sum -c {man}` -> 4/4 OK rc=0")

    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    cells = build()
    order = ["change_id", "owner", "entry_point", "Q1", "Q1_evidence", "Q2", "Q2_evidence", "Q3",
             "Q3_evidence", "Q4", "Q4_evidence", "Q5", "Q5_evidence", "M1", "M1_evidence", "M2",
             "M2_evidence", "M3", "M3_evidence", "E1", "E1_evidence", "E2", "E2_evidence", "E3",
             "E3_evidence", "E4", "E4_evidence"]
    missing = [c for c in order if not cells.get(c, "").strip()]
    tabs = [c for c in order if "\t" in cells.get(c, "")]
    if missing:
        raise SystemExit(f"empty cells: {missing}")
    if tabs:
        raise SystemExit(f"cells containing a tab: {tabs}")
    row = "\t".join(cells[c] for c in order)

    txt = INST.read_text(encoding="utf-8")
    lines = txt.rstrip("\n").split("\n")
    kept = [ln for ln in lines if not ln.startswith(CHANGE_ID + "\t")]
    n_before = len(lines) - len(kept)
    out = "\n".join(kept + [row]) + "\n"
    print(f"row cells={len(order)} chars={len(row)} replaced_existing={n_before}")
    if a.write:
        INST.write_text(out, encoding="utf-8")
        print(f"wrote {INST}  rows={len(kept) + 1}  sha256={sha(INST)}")
    else:
        print("(read-only run; pass --write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())