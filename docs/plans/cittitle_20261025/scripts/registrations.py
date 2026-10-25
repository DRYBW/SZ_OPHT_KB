#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""registrations.py — CITTITLE (card t_d8e7f2d4): register this card's surface on the repository's
own ledgers, from live bytes only (sha/bytes/mtime are taken from disk, never from a report).

Order matters and is asserted: registry rows -> change-control row -> gate inventory row, then (after
the caller has `git add`ed) the release identity, then docs/W3_MANIFEST.sha256 last of all.

Every mutation is fail-closed and idempotent: the cell being replaced is located by its item id and
its *old* value is asserted before being written, and each new row is refused if its id already
exists. Nothing is edited with a regex over the whole file.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import io
import os
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
DOCS = REPO / "docs"
W3 = DOCS / "W3_PIPELINE_REGISTRY.tsv"
G6 = DOCS / "CHANGE_CONTROL_G6_INSTANCE.tsv"
GINV = DOCS / "GATE_INVENTORY_G5G6.tsv"
CONTRACT = DOCS / "VERIFY_CONTRACT.md"

DELIV = "docs/plans/cittitle_20261025"

# ------------------------------------------------------------------ live measurements


def stat3(p: Path):
    b = p.read_bytes()
    return (hashlib.sha256(b).hexdigest(), len(b),
            datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"))


def sha(p: Path) -> str:
    return stat3(p)[0]


# ------------------------------------------------------------------ A. gate inventory

G12_ROW = [
    "G12",
    "citation presentation metadata gate (every citation record's title/doi/pmcid equals the corpus "
    "for its pmid; the delivered registry inverts byte-for-byte to its pre-image)",
    "python3 tests/gate_cittitle_meta.py --json <out>/G12_RESULTS.json",
    "tests/gate_cittitle_meta.py",
    "",                     # live sha filled below
    "repo side (card t_d8e7f2d4, board pi-briefing; citation-key defect line)",
    "docs/VERIFY_CONTRACT.md \u00a75.7",
    "reverse-control battery on the real tree + corpus-absent INCONCLUSIVE "
    "(docs/plans/cittitle_20261025/out/G12_CONTROLS.json: CLEAN / SOURCE-REGRESSION / TITLE-DRIFT / "
    "ANCHOR-BREAK / COVERAGE-DROP / CORPUS-ABSENT)",
    "ACTIVE",
    "-",
    "New gate (card t_d8e7f2d4, 2026-10-25): seven fail-closed checks G12-C01..C07, stdlib only, "
    "exit 0/2/3 (INCONCLUSIVE = no corpus copy on this tree, the G3/G11 precedent). Reason: the "
    "builder wrote `(hit title)[:120]` on the retrieval route and `\"\"` on the full-text gene-index "
    "route, so 2,429 of the shipped registry's 3,993 citation records had no title and 509 had a "
    "120-character prefix of one; every cited paper is in the corpus and the corpus holds the "
    "complete title, so nothing on disk could catch the drift and a title-keyed audit read it as "
    "\"the two libraries disagree\" (A strict 247/825 = 29.94%). EYEKB_G12_CORPUS overrides the "
    "corpus candidate list (used to exercise the INCONCLUSIVE branch). First registration, sha "
    "taken from live bytes in the same commit.",
]


def add_gate_inventory():
    lines = GINV.read_text(encoding="utf-8").split("\n")
    row = list(G12_ROW)
    row[4] = sha(REPO / "tests" / "gate_cittitle_meta.py")
    for ln in lines:
        if ln.startswith("G12\t"):
            cells = ln.split("\t")
            if cells[4] == row[4]:
                print("  G12 already registered with the live sha; not appended again")
                return row[4]
            cells[4] = row[4]
            GINV.write_text("\n".join(lines), encoding="utf-8")     # unreachable in practice
            raise SystemExit("G12 registered with a stale sha; fix the row by hand")
    # insert before the trailing empty line
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append("\t".join(row))
    GINV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return row[4]


# ------------------------------------------------------------------ B. W3 registry

REG_ROWS = [
    # (item_id, item_name, category, path, version, authority, change_gate, freeze_gate,
    #  regression_gate, state, evidence, notes, surface)
    ("L6-53", "Citation presentation metadata gate (G12)", "Delivery tooling",
     "tests/gate_cittitle_meta.py", "v1 (2026-10-25 first registration)",
     "AUTHORITATIVE(check tool)",
     "Same commit as the change (VERIFY_CONTRACT \u00a75)",
     "Not frozen (re-derivable from the registry and the shipped corpus)",
     "Invoked by tests/run_gates.sh; registered in docs/GATE_INVENTORY_G5G6.tsv as G12",
     "ON_DISK",
     "\u76d8\u4e0a\u5b9e\u6d4b\uff1apython3 tests/gate_cittitle_meta.py -> rc=0, seven checks "
     "G12-C01..C07 PASS; reverse-control battery out/G12_CONTROLS.json verdict=PASS (six cases, "
     "planted on the real tree then restored byte-identical)",
     "Seven fail-closed checks; stdlib only; exit 0/2/3. Guards the citation title/doi/pmcid lane "
     "that carried no usable title before card t_d8e7f2d4.",
     "repo"),
    ("L6-54", "One-click gate chain entry (G3..G12)", "Delivery tooling",
     "tests/run_gates.sh", "v12 (2026-10-25 G12 wired in; card t_d8e7f2d4)",
     "AUTHORITATIVE(check tool)",
     "Same commit as the change (VERIFY_CONTRACT \u00a75)",
     "Not frozen (the chain is re-run, not compared)",
     "Runs every registered gate; G5-C07 requires each invoked gate script to be registered",
     "ON_DISK",
     "\u76d8\u4e0a\u5b9e\u6d4b\uff1a/bin/bash tests/run_gates.sh (see "
     "docs/plans/cittitle_20261025/logs/run_gates_after.log)",
     "Entry point only: it judges nothing itself and reports each gate's rc. G12 appended after G11; "
     "the earlier gates' invocations are byte-unchanged.",
     "repo"),
    ("L6-55", "Link registry v2, anchor twin (citation presentation metadata)", "Delivery data",
     DELIV + "/out/LINK_REGISTRY_v2_cittitle.jsonl", "v2 (2026-10-25; card t_d8e7f2d4)",
     "AUTHORITATIVE(delivery artefact)",
     "New version number + new file; the frozen LINK_REGISTRY_v1.jsonl is NOT rewritten",
     "Byte-anchored to pre_images/LINK_REGISTRY_v1.jsonl.pre_cittitle (remove title_full/doi/pmcid "
     "-> the original line, every line)",
     "python3 docs/plans/cittitle_20261025/scripts/verify_deliverables.py (rc=0) / G12-C05",
     "ON_DISK",
     "\u76d8\u4e0a\u5b9e\u6d4b\uff1a165 rows, 3,993 citation records, every one carrying "
     "title_full/doi/pmcid; title_full == corpus title for every pmid; sha256 in "
     "out/BACKFILL_META.json and out/MANIFEST.sha256",
     "The pre-fix registry is kept byte-identical (sha a04be771\u2026) beside it; promotion of this "
     "twin into kb/link_registry/ is the coordinator's call and is registered as NOT done here.",
     "repo"),
    ("L6-56", "Link registry v2, drop-in variant (title repaired in place)", "Delivery data",
     DELIV + "/out/LINK_REGISTRY_v2_cittitle_dropin.jsonl", "v2 (2026-10-25; card t_d8e7f2d4)",
     "AUTHORITATIVE(delivery artefact)",
     "New version number + new file; the frozen LINK_REGISTRY_v1.jsonl is NOT rewritten",
     "Derived from the anchor twin by title := title_full (asserted byte-for-byte, every line)",
     "python3 docs/plans/cittitle_20261025/scripts/verify_deliverables.py (C04) / G12-C05",
     "ON_DISK",
     "\u76d8\u4e0a\u5b9e\u6d4b\uff1a165 rows, 3,993 citation records; 0 empty titles; 32 records "
     "read as length 120 because those papers' real titles are 120 characters long",
     "What the patched builder emits: a consumer that reads `title` gets the complete title. The "
     "anchor twin remains the file that inverts to the frozen bytes.",
     "repo"),
    ("L6-57", "Citation presentation metadata: defect, fix and counterfactual (spec)", "Delivery document",
     DELIV + "/out/CITATION_META_SPEC_v1.md", "v1 (2026-10-25 first registration)",
     "AUTHORITATIVE(delivery artefact)",
     "Same commit as the change (VERIFY_CONTRACT \u00a75)",
     "Not frozen (regenerated from the delivered read-outs)",
     "Recompute: scripts/backfill_citation_meta.py + scripts/counterfactual_titles.py + "
     "scripts/verify_deliverables.py",
     "ON_DISK",
     "\u76d8\u4e0a\u5b9e\u6d4b\uff1athe before/after table, the per-row reason breakdown, the three "
     "non-circular controls and the reconciliation of the brief's numbers all come from the "
     "delivered JSON/TSV, not from prose",
     "Carries the honest boundary: the post-fix 100% is same-source by construction and is NOT "
     "evidence that the two libraries agree.",
     "repo"),
]

RETAKES = {
    "L6-01": ("docs/VERIFY_CONTRACT.md",
              "v8 (2026-10-25 \u52a0 \u00a75.7 \u5f15\u6587\u5c55\u793a\u5143\u6570\u636e\u4e0e G12 \u95e8\uff1b"
              "\u5361 t_d8e7f2d4)",
              "Same commit as the change (VERIFY_CONTRACT \u00a75)",
              "\u00a75.7 was appended for the citation presentation metadata defect and the gate that "
              "now re-derives it (G12); no earlier section is edited."),
    "L6-22": ("kb/link_registry/scripts/build_link_registry.py",
              "v2 (2026-10-25 citation presentation metadata; card t_d8e7f2d4)",
              "Same commit as the change (VERIFY_CONTRACT \u00a75)",
              "Adds corpus_meta_index() / citation_field() and writes the complete title plus "
              "doi/pmcid on both citation routes; removes the 120-character cap and the empty-title "
              "literal. The frozen registry this card does not rebuild is untouched "
              "(sha a04be771\u2026); a rebuild now carries the three fields."),
}


def csv_rows(p: Path):
    """Read with a naive tab split — the same way the gates read these files.

    `tests/gate_change_control.py:254` and `tests/gate_registry.py:109` both do
    `ln.split("\t")`, so this ledger must stay plain, unquoted TSV: routing it through
    `csv.reader`/`csv.writer` here would introduce quoting that the gates would then read as part of
    the cell text (and a round-trip through csv would be silently lossy for cells containing `"`).
    """
    with p.open(encoding="utf-8") as fh:
        return [ln.split("\t") for ln in fh.read().split("\n") if ln != ""]


def write_rows(p: Path, rows):
    for r in rows:
        for cell in r:
            assert "\t" not in cell and "\n" not in cell and "\r" not in cell, \
                "a ledger cell may not contain a tab or a newline (the gates split on tab and line)"
    with p.open("w", encoding="utf-8") as fh:
        fh.write("\n".join("\t".join(r) for r in rows) + "\n")


def update_w3():
    rows = csv_rows(W3)
    head = rows[0]
    assert head[1] == "item_id", head[:5]
    idx = {r[1]: i for i, r in enumerate(rows) if len(r) > 2 and r[0] == "L6"}
    existing = {r[1] for r in rows if len(r) > 2}
    log = []
    for item_id, col in RETAKES.items():
        path, version, gate, note = col
        p = REPO / path
        sha256, nbytes, mt = stat3(p)
        i = idx[item_id]
        old = rows[i][10]
        assert rows[i][4] == path, (item_id, rows[i][4])
        if old == sha256:
            log.append(f"re-take {item_id} {path}: already live ({sha256[:16]}); skipped")
            continue
        rows[i][5] = version
        rows[i][7] = gate
        rows[i][10], rows[i][11], rows[i][12] = sha256, str(nbytes), mt
        rows[i][13] = "ON_DISK"
        rows[i][15] = (rows[i][15].rstrip() + "  |  " + note) if rows[i][15].strip() else note
        log.append(f"re-take {item_id} {path}: {old[:16]} -> {sha256[:16]} ({nbytes} B)")
    for item_id, name, cat, path, version, auth, gate, freeze, reggate, state, ev, notes, surf in REG_ROWS:
        if item_id in existing:
            log.append(f"add     {item_id} {path}: already present; skipped")
            continue
        p = REPO / path
        sha256, nbytes, mt = stat3(p)
        rows.append(["L6", item_id, name, cat, path, version, auth, gate, freeze, reggate,
                     sha256, str(nbytes), mt, state, ev, notes, surf])
        log.append(f"add     {item_id} {path}: {sha256[:16]} ({nbytes} B)")
    write_rows(W3, rows)
    return log


# ------------------------------------------------------------------ C. change control

CONTENT = [
    # Q1 first-cause layer
    ("Q1", "First-cause layer = L6 (the delivery/disclosure surface: the link registry that ties an "
           "entry to a page, a route, a citation and a skill entry point). The citation records "
           "carried a `pmid` but no usable title key - 2,429 of the shipped registry's 3,993 records "
           "had `title: \"\"` (written by the builder's full-text gene-index route) and 509 had a "
           "120-character prefix of the corpus title (the retrieval route's `[:120]` cap). Remove the "
           "two causes and the symptom disappears; L0-L5 (volumes, vocabularies, generators, "
           "read-outs, contracts) are untouched by this card. (card t_d8e7f2d4)",
     DELIV + "/out/CITATION_META_SPEC_v1.md:1 names the two source lines and the live counts; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/"
     "build_link_registry.py.pre_cittitle:232 the pre-fix cap; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/"
     "build_link_registry.py.pre_cittitle:299 the empty-title literal"),
    # Q2 layer to fix
    ("Q2", "Layer to fix = L6 = the first-cause layer (equal, so the change lands there; no downstream "
           "patch, no transitional file). Two additions and two rewrites in the builder: (i) "
           "corpus_meta_index() reads the shipped corpus into `paper_id -> {title, doi, pmcid, "
           "is_preprint}` following the same resolution chain the citations themselves come from "
           "(EYEKB_DB_DIR -> eyekb_core._default_db_dir() -> the in-repo G2 slim library); (ii) "
           "citation_field() takes a corpus field with the retrieval hit as fallback; (iii) the "
           "retrieval route writes the complete title and doi/pmcid; (iv) the gene-index route does "
           "the same instead of `\"\"`. No marker body, no label map, no scoring rule and no default "
           "route is edited (card t_d8e7f2d4)",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/CITATION_META_SPEC_v1.md:1 section 2 "
     "lists the four edits; /home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/BACKFILL_META.json"
     ":1 the live join counts (825/825 cited ids resolved from a single corpus copy)"),
    # Q3 blast radius with the negative term (R5)
    ("Q3", "Blast radius per file x per reading, with the negative term stated. The registry lane "
           "moves and only it: the frozen LINK_REGISTRY_v1.jsonl is NOT rewritten (sha a04be771... "
           "unchanged, 165 rows, 3,993 citation records, verified byte-identical against the "
           "delivered pre-image), and the two new registry files are new paths. Negative term "
           "(rollback clause, stated rather than hidden): this card does NOT fix the shipped file - "
           "any consumer reading kb/link_registry/LINK_REGISTRY_v1.jsonl today still sees the "
           "defect, and promotion of the twin is deliberately left to the coordinator; the "
           "post-fix 100% title match is a same-source construction and is therefore NOT evidence "
           "that the two libraries agree, so no claim of that kind is made; 5 cited ids are "
           "preprints whose corpus journal field is empty (a disclosed difference, not repaired); "
           "and a rebuild of the registry is now required before the live file carries the fields. "
           "Rollback: drop the two new files and restore the builder pre-image (sha in "
           "pre_images/PREIMAGE.sha256); nothing else changed.",
     DELIV + "/out/CITATION_META_SPEC_v1.md:1 section 5 lists what this card does not claim; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/PREIMAGE.sha256:1 the eight "
     "pre-images with their shas"),
    # Q4 pre-registered criteria with a sha anchor (R6)
    ("Q4", "Criteria frozen before the run, in the brief and in the card's own spec: (1) the builder "
           "carries title/doi/pmcid backfilled from the corpus on paper_id == pmid, with the title "
           "not truncated; (2) the shipped registry stays byte-verifiable except for the three added "
           "columns; (3) the before/after title match rate is reported in both calibers (strict and "
           "40-character prefix) and the higher one is never reported alone; (4) every unmatched row "
           "carries a non-empty reason; (5) zero download, read-only corpus, default route "
           "unchanged, no push, frozen artefacts not rewritten, all numbers read live. Failure exit: "
           "if the anchor twin does not invert to the pre-image byte-for-byte, or any cited id fails "
           "to resolve, the run stops instead of shipping a partly-titled registry (the script exits "
           "2). No criterion was moved after seeing a number.",
     "sha256 3714be04ff1fdfe46b9d4d095b64fc9405ec755b39ad19090388658853176743 is the frozen brief "
     "(BRIEF_CITTITLE_20261025.md as delivered); the pre-registered inputs are pinned in "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/PREIMAGE.sha256:1 and the "
     "declared corpus sha is in out/BACKFILL_META.json:1"),
    # Q5 escape door (R7)
    ("Q5", "Escape door: EYEKB_G12_CORPUS, the new gate's corpus override - unset (OFF) it resolves "
           "the corpus through the repository's own chain (the G2 slim library, then the pointer's "
           "default library), which is the pre-card behaviour of every other gate and changes no "
           "service path; a missing corpus is INCONCLUSIVE (rc=3) and no verdict is issued, measured "
           "with EYEKB_G12_CORPUS=/nonexistent/papers.jsonl -> rc=3. This card adds no switch to the "
           "service: the default answer route's inputs (EYEKB_DB_DIR, the pointer's role:default "
           "entry, search_literature) are untouched, so the OFF state is byte-identical to the "
           "pre-card default. The builder's own change is additive on a disclosure surface: "
           "pre-existing citation keys keep their values and their order in the anchor twin, and "
           "removing the three added keys reproduces every frozen line byte-for-byte.",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/G12_CONTROLS.json:1 the "
     "CORPUS-ABSENT case (rc=3) and the CLEAN case (rc=0); "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/BACKFILL_META.json:1 the inversion "
     "block asserted per line"),
    # M1 version artefacts
    ("M1", "Version artefacts: every edited shipped file is kept as a pre-image with its sha recorded "
           "(eight pre-images: the frozen registry, the builder, the one-click entry, the gate "
           "inventory, the ownership ledger, the change-control instance, the contract, the W3 "
           "manifest); the new files are new paths, not edits of existing ones "
           "(tests/gate_cittitle_meta.py and the delivery tree under docs/plans/cittitle_20261025/); "
           "no frozen artefact is rewritten in place and no expected anchor is moved.",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/PREIMAGE.sha256:1 the eight "
     "pre-images with their shas; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/BACKFILL_META.json:1 the frozen "
     "registry sha the twins were derived from"),
    # M2 impact list
    ("M2", "Impact list per file: added = tests/gate_cittitle_meta.py, "
           "docs/plans/cittitle_20261025/ (out/, scripts/, logs/, pre_images/), and six rows in the "
           "ownership ledger (L6-53..L6-57 plus the entry-point row); changed = "
           "kb/link_registry/scripts/build_link_registry.py, tests/run_gates.sh (G12 appended), "
           "docs/VERIFY_CONTRACT.md (sect 5.7 appended), docs/GATE_INVENTORY_G5G6.tsv (G12 row), "
           "docs/CHANGE_CONTROL_G6_INSTANCE.tsv (this row), docs/W3_PIPELINE_REGISTRY.tsv (rows "
           "re-taken and added), docs/RELEASE_IDENTITY.json + docs/RELEASE_MANIFEST_v1.json "
           "(re-taken), docs/W3_MANIFEST.sha256 (re-frozen last); unchanged = kb/link_registry/"
           "LINK_REGISTRY_v1.jsonl, kb/link_registry/README.md, kb/link_registry/out/**, "
           "mcp_server/**, clients/**, pipeline/**, literature_db/** (all read-only).",
     "/home/ubuntu/EYEKB_REPO/docs/W3_PIPELINE_REGISTRY.tsv:1 the re-taken and added rows; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/MANIFEST.sha256:1 every delivered "
     "artefact with its sha256"),
    # M3 regression gate (R2-CONCRETE: command + expected read-out)
    ("M3", "Regression gate with a runnable command and a concrete expected read-out: from the repo "
           "root, `python3 tests/gate_cittitle_meta.py` must exit rc=0 with seven checks "
           "G12-C01..C07 PASS; `python3 docs/plans/cittitle_20261025/scripts/verify_deliverables.py` "
           "must print 12 checks, 12 PASS, 0 FAIL and exit 0; "
           "`python3 docs/plans/cittitle_20261025/scripts/g12_controls.py` must print "
           "verdict=PASS with six cases and restored byte-identical True; and `/bin/bash "
           "tests/run_gates.sh` must run G3..G12 with no gate failing (see the recorded read-out "
           "for the environment's rc=3 on G3, which is an interpreter precondition and not a "
           "repository verdict). This change is default-ON on a disclosure surface, so its "
           "precondition is registered in docs/VERIFY_CONTRACT.md sect 5.7 and enforced by G12 "
           "(R8).",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/logs/g12_after.log:1 the seven-check "
     "read-out rc=0; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/logs/p3_verify.log:1 '12 checks, 12 PASS, "
     "0 FAIL'; /home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/G12_CONTROLS.json:1 "
     "verdict=PASS"),
    # E1 sha evidence (R2-CONCRETE)
    ("E1", "sha evidence taken fresh in this commit, none quoted from an earlier report: the frozen "
           "registry a04be7711131225129ed6a8f6d3cb08862216c9187307a8a2b663b7bdd15e9cf (unchanged), "
           "the anchor twin 0d49ee04dc0a940d183ad887af592b1be39c59c71621a0df5816cef94198b549, the "
           "drop-in ba5e71b5b19b4a55..., the declared corpus "
           "7883f8db5bb235ecee95efa39c22129bb33b9d898af0817e3be647239fae5cea, and the new gate's "
           "sha as registered in docs/GATE_INVENTORY_G5G6.tsv.",
     "sha256 0d49ee04dc0a940d183ad887af592b1be39c59c71621a0df5816cef94198b549 is the anchor twin "
     "in /home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/BACKFILL_META.json:1; every "
     "delivered artefact's sha is listed in "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/MANIFEST.sha256:1 and verified with "
     "sha256sum -c"),
    # E2 rollback identity (R2-CONCRETE)
    ("E2", "Rollback identity, two independent paths: path 1, the bytes - the eight pre-images "
           "(shas in pre_images/PREIMAGE.sha256) restore every edited shipped file, and the two new "
           "registry files plus the gate and the delivery tree are additive, so `git revert` of the "
           "commit returns the pre-card tree; path 2, the switch - with EYEKB_G12_CORPUS unset the "
           "gate resolves the corpus through the repository's own chain and the service's default "
           "route is untouched, so the OFF state reproduces the pre-card behaviour and the "
           "pre-existing citation keys keep their exact values and order (removing the three added "
           "keys reproduces every frozen line byte-for-byte).",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/pre_images/PREIMAGE.sha256:1 the eight "
     "pre-images; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/G12_CONTROLS.json:1 the battery "
     "restored every planted file byte-identical (restored_byte_identical true)"),
    # E3 differential reading incl. negatives
    ("E3", "Differential reading with the negative column included, no gains-only reporting: citation "
           "records carrying a usable full title 1,053/3,993 -> 3,993/3,993; distinct cited papers "
           "matched under the strict caliber 247/825 (29.94%) -> 825/825, under the 40-character "
           "prefix caliber 369/825 (44.73%) -> 825/825; unmatched rows with a reason 2,066 -> 0; a "
           "new gate adds 7 checks to the one-click entry (9 gates -> 10; 10 -> 11 with the entry "
           "row counted separately). Negative column: nothing on the default answer route improves "
           "(0 route readings move), the frozen registry is not repaired so a consumer of that file "
           "sees no change, the two preprints' journal difference is disclosed rather than fixed, and "
           "the post-fix 100% is a same-source construction and is explicitly NOT claimed as "
           "independent agreement.",
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/CITATION_TITLE_COUNTERFACTUAL_v1.json"
     ":1 the eight caliber arms and the three non-circular controls; "
     "/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/out/CITATION_TITLE_LEDGER_v1.tsv:1 the "
     "per-record before/after ledger"),
    # E4 ledger registration + time order
    ("E4", "Ledger registration and time order: rows L6-01 (contract) and L6-22 (builder) re-taken "
           "from live bytes, rows L6-53..L6-57 added for the gate, the one-click entry, the two "
           "registry twins and the spec; G12 registered in docs/GATE_INVENTORY_G5G6.tsv with its live "
           "sha (G5-C07 requires every gate script invoked by the chain to be registered); this row "
           "written after re-reading the instance file; docs/W3_MANIFEST.sha256 re-frozen LAST and "
           "docs/RELEASE_IDENTITY.json + docs/RELEASE_MANIFEST_v1.json re-taken after `git add`. "
           "Concurrency disclosure: no other card was writing these files in this window (checked "
           "with git status before each write).",
     "/home/ubuntu/EYEKB_REPO/docs/W3_PIPELINE_REGISTRY.tsv:1 the five added rows and the two "
     "re-taken rows with live shas; "
     "/home/ubuntu/EYEKB_REPO/docs/GATE_INVENTORY_G5G6.tsv:1 the G12 row; "
     "/home/ubuntu/EYEKB_REPO/docs/W3_MANIFEST.sha256:1 the registry checksum, re-frozen last"),
]


def append_g6():
    rows = csv_rows(G6)
    # The file opens with a header block of `#` comment lines (the ledger's own provenance notes), so
    # the column header is located by its first cell rather than assumed to be row 0.
    hidx = next(i for i, r in enumerate(rows) if r and r[0] == "change_id")
    head = rows[hidx]
    assert len(head) == 27, len(head)
    cid = "CHG-20261025-CITTITLE"
    if any(r and r[0] == cid for r in rows):
        print(f"  {cid} already present; not appended again")
        return cid
    cells = {}
    for key, content, ev in CONTENT:
        cells[key] = content
        cells[key + "_evidence"] = ev
    row = [cid,
           "Maintainer (repository delivery surface; card t_d8e7f2d4, board pi-briefing; executed as "
           "the citation-key defect brief BRIEF_CITTITLE_20261025.md, not as an audit pass)",
           "/home/ubuntu/EYEKB_REPO/kb/link_registry/scripts/build_link_registry.py"]
    for k in ("Q1", "Q2", "Q3", "Q4", "Q5", "M1", "M2", "M3", "E1", "E2", "E3", "E4"):
        row += [cells[k], cells[k + "_evidence"]]
    assert len(row) == 27, len(row)
    while rows and not rows[-1]:
        rows.pop()
    rows.append(row)
    write_rows(G6, rows)
    return cid


# ------------------------------------------------------------------ D. contract

SECTION_57 = """
### §5.7 Citation presentation metadata on the link registry (card t_d8e7f2d4, 2026-10-25)

**Defect registered.** Every citation record in `kb/link_registry/LINK_REGISTRY_v1.jsonl` carries a
`pmid` and a `title`, and the title was unusable as a key: `kb/link_registry/scripts/
build_link_registry.py` wrote `(hit title)[:120]` on the retrieval route and `""` on the full-text
gene-index route. Measured on the shipped file: of 3,993 citation records, 2,429 have no title at all
and 509 carry a 120-character prefix of one (511 read as length 120, of which 2 are papers whose real
title is 120 characters long). All 825 cited papers are present in the corpus and the corpus holds the
complete title, so nothing on disk could catch the drift — and a title-keyed audit against the corpus
reported 247/825 (29.94%) strict, 369/825 (44.73%) prefix-40, which reads as "the two libraries
disagree" when in fact **zero** of the failures are a genuine title difference: 455 papers had no
citation-side title, 122 had a clipped one, 1 differed only by HTML/Unicode display marks.

**Fix (same commit as this contract line).** The builder gains `corpus_meta_index()` (reads the
shipped corpus into `paper_id -> {title, doi, pmcid, is_preprint}` through the same resolution chain
the citations come from: `EYEKB_DB_DIR` → `eyekb_core._default_db_dir()` → the in-repo G2 slim
library; read-only, no route change) and `citation_field()`, and writes the **complete** title plus
`doi` / `pmcid` on both citation routes. The frozen registry is deliberately **not** rewritten: the
repaired registry ships as a new file beside it, `docs/plans/cittitle_20261025/out/
LINK_REGISTRY_v2_cittitle.jsonl` (anchor twin: remove the three added keys and every line equals the
frozen file byte-for-byte) with `…_dropin.jsonl` derived from it by `title := title_full`.

**Machine gate.** G12 = `tests/gate_cittitle_meta.py`, wired into `tests/run_gates.sh` and registered
in `docs/GATE_INVENTORY_G5G6.tsv`. Seven fail-closed checks (G12-C01..C07; see the gate's own header):
the builder carries the fix and neither pre-fix literal is back; every citation record of the registry
under test carries the three fields; those fields equal the corpus for its `pmid`; coverage matches the
frozen registry and the pre-image; the anchor twin inverts to the pre-image and the drop-in derives
from it, both byte-for-byte; the builder's own corpus reader agrees with the gate's independent
reader; and a planted-shape self-test proves the comparators are not vacuous. Exit 0 / 2 (FAIL) / 3
(INCONCLUSIVE — no corpus copy on this tree; the G3/G11 precedent, counted as not-pass by the chain).
`EYEKB_G12_CORPUS` overrides the corpus candidate list and exists so the INCONCLUSIVE branch can be
exercised on a real tree without moving the corpus.

**Reverse controls measured on the real tree (docs/plans/cittitle_20261025/).** The battery plants
each shape, runs the gate, then restores and re-hashes: CLEAN rc=0; a pre-fix `[:120]` literal planted
back into the builder rc=2 with G12-C01 naming it; a mutated `title_full` rc=2 (G12-C03, plus the
consequential G12-C05/C06 incoherence); a mutated pre-existing citation key rc=2 (G12-C05); a dropped
row rc=2 (G12-C04); a missing corpus rc=3 (G12-C03). All planted files came back byte-identical
(`out/G12_CONTROLS.json`).

**Scope note (registered, not silently dropped).** The two registry files stay in the card's delivery
tree; promoting either into `kb/link_registry/` — which would move the knowledge-bundle identity — is
the coordinator's decision, and this card neither performs nor implies it. The builder change means a
rebuild now carries the three fields; until such a rebuild, a consumer of the frozen file still sees
the defect. The post-fix match rate is 825/825 **by construction** (same-source join) and is recorded
as such, never as evidence that the two libraries agree; the non-circular readings are the same
comparison against two other corpus copies, the journal/year field controls on the same join, and the
243 already-complete citation titles (written by the frozen builder, not by this card) matching the
corpus 243/243.
"""


def append_contract():
    txt = CONTRACT.read_text(encoding="utf-8")
    if "\u00a75.7 " in txt:
        print("  sect 5.7 already present; not appended again")
        return
    assert "\u00a75.6 \n" in txt or "\u00a75.6" in txt
    CONTRACT.write_text(txt.rstrip("\n") + "\n" + SECTION_57, encoding="utf-8")




# ------------------------------------------------------------------ E. second pass (found by G5/G6)

def retake_gate_inventory_contract():
    """Re-take the G2 row's sha: its entry point IS docs/VERIFY_CONTRACT.md, which sect 5.7 changed.

    Found by running the ownership gate after the first pass: `G5-C05 ... G2:VERIFY_CONTRACT.md
    registered=00c8dc51... live=e2b35ac7...`. A gate inventory entry point that is a repository file
    is registered with its live sha, so editing the file obliges the row to be re-taken.
    """
    lines = GINV.read_text(encoding="utf-8").split("\n")
    live = sha(CONTRACT)
    done = 0
    for i, ln in enumerate(lines):
        cells = ln.split("\t")
        if len(cells) < 11 or cells[0].startswith("#"):
            continue
        # the gate inventory's identity column for a file-anchored gate is the SCRIPT PATH
        # (header: gate_id, gate_name, entry_point, script_path, sha256, ...) — G2's entry_point is
        # the Release-asset download command, its script_path is the contract file
        if cells[3] == "docs/VERIFY_CONTRACT.md":
            if cells[4] == live:
                print(f"  {cells[0]}: contract sha already live ({live[:16]}); skipped")
                continue
            old = cells[4]
            cells[4] = live
            cells[10] = (cells[10].rstrip() + "  |  2026-10-25 re-taken in the same commit as "
                         "sect 5.7 appended (citation presentation metadata, card t_d8e7f2d4); "
                         f"sha {old[:16]} -> {live[:16]}.")
            lines[i] = "\t".join(cells)
            done += 1
    assert done <= 1
    if done:
        GINV.write_text("\n".join(lines), encoding="utf-8")
    print(f"  gate inventory: {done} contract row re-taken")
    return live


G6_E2_NEW = (
    "Rollback identity, two independent paths, each with a runnable command and an expected "
    "read-out. Path 1, the bytes: `sha256sum -c pre_images/PREIMAGE.sha256` from "
    "docs/plans/cittitle_20261025 must report 8/8 OK, and `git revert <the commit named in "
    "COMMIT.txt>` returns the pre-card tree because the two registry twins, the gate and the "
    "delivery tree are additive. Path 2, the switch: with EYEKB_G12_CORPUS unset "
    "`python3 tests/gate_cittitle_meta.py` must exit rc=0 and resolve the corpus through the "
    "repository's own chain, while the service's default route is untouched - expected read-out: "
    "the CLEAN and CORPUS-ABSENT lines of out/G12_CONTROLS.json (rc=0 and rc=3 respectively) with "
    "restored_byte_identical true, and the anchor twin still inverting to the pre-image: "
    "`python3 scripts/verify_deliverables.py` must print 12 checks, 12 PASS, 0 FAIL and exit 0."
)


def fix_g6_e2():
    """Give E2 an executable command + expected read-out (G6-R2-CONCRETE) and repair the two path
    anchors that pointed at out/MANIFEST.sha256 before it existed (G6-R2-PORTABLE)."""
    rows = csv_rows(G6)
    hidx = next(i for i, r in enumerate(rows) if r and r[0] == "change_id")
    keys = rows[hidx]
    e2 = keys.index("E2_evidence")
    changed = 0
    for r in rows:
        if not r or r[0] != "CHG-20261025-CITTITLE":
            continue
        if r[e2] != G6_E2_NEW:
            r[e2] = G6_E2_NEW
            changed += 1
    write_rows(G6, rows)
    print(f"  G6 E2_evidence rewritten: {changed}")
    return changed



def main():
    # Order: the contract edit lands first so the ownership-ledger row (L6-01) re-takes the
    # post-edit sha — a row re-taken before its file is edited would register a stale sha and G5-C05
    # would report drift against the very commit that made it.
    print("== contract ==")
    append_contract()
    print("  sect 5.7 appended; contract sha", sha(CONTRACT)[:16])
    print("== gate inventory ==")
    print("G12 sha", add_gate_inventory())
    print("== W3 registry ==")
    for ln in update_w3():
        print("  " + ln)
    print("== change control ==")
    print(" ", append_g6())
    fix_g6_e2()
    print("== second pass (what G5/G6 found) ==")
    retake_gate_inventory_contract()
    print("\nnext: git add, then scripts/release_identity.py --take, then w3_manifest (LAST)")
    return 0


if __name__ == "__main__":
    sys.exit(main())