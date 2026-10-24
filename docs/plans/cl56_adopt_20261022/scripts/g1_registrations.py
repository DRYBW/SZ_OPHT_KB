# -*- coding: utf-8 -*-
"""g1_registrations.py -- land this card's registration surface, all data taken from live bytes.

Steps, in the order the repository's own rules prescribe (registry first, manifest LAST):
  1. regenerate docs/SWITCH_COVERAGE_REGISTRY.tsv from source (G10 R1 binding; the new switch
     `EYEKB_ACT_CL56` must be classified before any arm reading is quoted);
  2. re-take registry row L1-11M (the service core), row L1-23 (the CL label map, edited additively),
     row L6-47 (the switch registry, just regenerated), and add one new row L1-32 for the new
     increment file;
  3. append one change-control instance row (parseable anchors, rules R1-R8);
  4. re-freeze docs/W3_MANIFEST.sha256 LAST, after the registry's final bytes.

`scripts/release_identity.py --take --source index` is run by the caller AFTER `git add`, because the
identity is taken against the staged tree; this script only touches the registry, the switch registry
and the change-control instance.

Writes out/REGISTRY_ROWS.json.
Run: /usr/bin/python3 g1_registrations.py
"""
import csv
import datetime
import hashlib
import json
import os
import subprocess

REPO = "/home/ubuntu/EYEKB_REPO"
HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
INST = os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv")
SWREG = os.path.join(REPO, "docs", "SWITCH_COVERAGE_REGISTRY.tsv")
NEW_ROW_ID = "L1-32"
SW_ROW_ID = "L6-47"
CORE = "mcp_server/eyekb_core.py"
CLMAP = "kb/markers/markers_cl_alignment_v2_unified.json"
INCR = "kb/markers/markers_v15_cl56_increment.json"


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def stat_row(rel):
    p = os.path.join(REPO, rel)
    st = os.stat(p)
    return (hashlib.sha256(open(p, "rb").read()).hexdigest(), str(st.st_size),
            datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))


def main():
    doc = {"probe": "g1_registrations.py", "rows": {}}
    meas = json.load(open(os.path.join(OUT, "MEASURE.json"), encoding="utf-8"))
    acc = json.load(open(os.path.join(OUT, "ACCEPTANCE.json"), encoding="utf-8"))
    f1 = json.load(open(meas["harness_reports"]["A1_recorded_decls"], encoding="utf-8"))
    b1 = meas["readings"]["b_inconsistent_rises"]["A1_recorded_decls"]
    moved = meas["moved"]
    n_up = sum(1 for x in moved if x["grade_up"])
    n_down = sum(1 for x in moved if x["grade_down"])
    cells_up = sum(x["n_cells"] for x in moved if x["grade_up"])
    cells_down = sum(x["n_cells"] for x in moved if x["grade_down"])
    tak = [x for x in moved if x["kind"] == "adopted-name-gain"]
    tak_on = [x for x in tak if x["truth_is_the_adopted_name"]]
    prereg_sha = hashlib.sha256(open(os.path.join(WAVE, "PREREG_ADOPT_CL56_20261022.md"),
                                     "rb").read()).hexdigest()
    n_falls = acc["clauses"]["a"]["readings"]["A1_recorded_decls"]["n_falls"]
    n_ds = acc["clauses"]["a"]["readings"]["A1_recorded_decls"]["datasets_checked"]
    # 1. switch registry from source
    p = subprocess.run(["/usr/bin/python3", os.path.join(REPO, "scripts", "switch_coverage",
                                                         "gen_switch_registry.py")],
                       capture_output=True, text=True, cwd=REPO)
    doc["switch_registry"] = {"rc": p.returncode, "stdout": p.stdout.strip(),
                              "stderr": p.stderr.strip()[-400:],
                              "sha256": sha_rel("docs/SWITCH_COVERAGE_REGISTRY.tsv"),
                              "has_cl56": "EYEKB_ACT_CL56" in open(SWREG, encoding="utf-8").read()}
    if p.returncode != 0 or not doc["switch_registry"]["has_cl56"]:
        raise SystemExit("switch registry regeneration failed or missed EYEKB_ACT_CL56")

    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    idx = {c: i for i, c in enumerate(hdr)}
    assert hdr[1] == "item_id" and len(hdr) == 17, "registry schema moved"
    by_id = {r[1]: r for r in rows if len(r) == 17}

    # 2a. re-take the rows whose bytes changed
    note_core = (" | 2026-10-24 card t_fabddb85 (CL56-ADOPT): the service core gains the `cl56_v15` "
                 "MARKER_LIBS entry, the `CL56_DEFAULT_LIBS = ()` whitelist (EMPTY by design) and the "
                 "`EYEKB_ACT_CL56` predicate, because the CL-56 child-term adoption FAILED its "
                 "pre-registered acceptance rule on the recorded set (clause (a): 12 of 28 datasets' "
                 "cell-weighted consistent share falls; clause (b): aggregate inconsistent 19.843% -> "
                 "29.609%) and the brief's clause 5 keeps the increment registered default-off. The "
                 "default route is byte-identical in every state: 721/721 cluster windows and 229/229 "
                 "battery calls, raw and canonical, against the pre-card commit (out/DEFAULT_FACE.json). "
                 "Re-taken from live bytes in the same commit as the change.")
    note_map = (" | 2026-10-24 card t_fabddb85 (CL56-ADOPT): v1.1 -> v1.2, ADDITIVE rows only (76 -> 79 "
                "labels): the three adopted child-term names (`rod bipolar cell`, `keratocyte`, "
                "`S cone cell`) so an entry of `cl56_v15` is mappable by the ontology ruler -- the "
                "activation card t_be11fd4a measured that an unlisted entry name is graded "
                "`unmappable_pred` and read as an inconsistency. Neutral on the default route (no "
                "default-route answer carries any of the three names; the replay is byte-identical).")

    for item_id, rel, note in ((("L1-11M"), CORE, note_core), ("L1-23", CLMAP, note_map)):
        r = by_id[item_id]
        s, b, m = stat_row(rel)
        doc["rows"][item_id] = {"path": rel,
                                "before": {"sha256": r[idx["sha256"]], "bytes": r[idx["bytes"]]},
                                "after": {"sha256": s, "bytes": b, "mtime": m}}
        r[idx["sha256"]], r[idx["bytes"]], r[idx["mtime"]] = s, b, m
        if not r[idx["notes"]].endswith(note):
            r[idx["notes"]] = r[idx["notes"]] + note

    # 2b. the switch registry row (regenerated above)
    r = by_id[SW_ROW_ID]
    s, b, m = stat_row("docs/SWITCH_COVERAGE_REGISTRY.tsv")
    sw_note = (" | 2026-10-24 card t_fabddb85 (CL56-ADOPT): regenerated from source with the "
               "repository's own tool (scripts/switch_coverage/gen_switch_registry.py), which adds the "
               "row for EYEKB_ACT_CL56 registered by this card and re-classifies the whole switch set; "
               "sha/bytes/mtime re-taken from live bytes in the same commit.")
    doc["rows"][SW_ROW_ID] = {"path": "docs/SWITCH_COVERAGE_REGISTRY.tsv",
                              "before": {"sha256": r[idx["sha256"]], "bytes": r[idx["bytes"]]},
                              "after": {"sha256": s, "bytes": b, "mtime": m}}
    r[idx["sha256"]], r[idx["bytes"]], r[idx["mtime"]] = s, b, m
    if not r[idx["notes"]].endswith(sw_note):
        r[idx["notes"]] = r[idx["notes"]] + sw_note

    # 2c. the new increment row
    if NEW_ROW_ID in by_id:
        raise SystemExit("row id %s already taken -- someone else registered in this window"
                         % NEW_ROW_ID)
    s, b, m = stat_row(INCR)
    inc = json.load(open(os.path.join(REPO, INCR), encoding="utf-8"))
    new = ["L1", NEW_ROW_ID,
           "Cell-Ontology child-term naming increment (author-side finer terms of coarser shipped classes)",
           "KB 版本件", INCR, inc["version"],
           "REGISTERED_DEFAULT_OFF (empty whitelist: not in the default `all` set in any state; reachable "
           "only via library=cl56_v15; merging into the default route requires the pre-registered "
           "acceptance rule to pass, which it did NOT -- see the evidence column)",
           "只经 L1 发布门（新版本件，禁止就地改）；任何字节变更在同一 commit 内重取 sha",
           "KB bodies frozen: this file adds classes, it modifies no existing entry",
           "G5 + the recorded-set replay: the default route is byte-identical with the increment "
           "registered (721/721 cluster windows + 229/229 battery calls, raw and canonical)",
           s, b, m, "ON_DISK",
           ("pre-registration plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md; scope rule "
            "application out/SCOPE.json (3 of 25 adopted, 22 pending with reasons, 31 out of scope); "
            "measurement out/MEASURE.json; acceptance verdict NO-GO on clauses (a) and (b) "
            "out/ACCEPTANCE.json; default-face byte identity out/DEFAULT_FACE.json; report REPORT.md"),
           ("%d entries / %d genes: the author-side finer Cell-Ontology terms for recorded clusters whose "
            "reference label is literally that term, carrying only each term's discriminating positive "
            "genes (parent-shared genes removed). NOT merged into the default route: the recorded-set "
            "reading fails the pre-registered rule (consistent -5.173pp; inconsistent +9.766pp; 89 of the "
            "92 clusters it renames carry a different author label). Kept registered so the terms are "
            "reachable by name and so a future, narrower pre-registration can build on it."
            % (inc["n_entries"], sum(len(e["markers"]) for e in inc["entries"]))),
           "repo"]
    rows.append(new)

    body = "\n".join("\t".join(r) for r in rows) + "\n"
    assert body.count("\n") == len(rows), "row count changed while serialising"
    with open(REG, "w", encoding="utf-8") as f:
        f.write(body)
    doc["new_row"] = {k: v for k, v in zip(hdr, new)}
    doc["registry_sha256_after"] = sha_rel("docs/W3_PIPELINE_REGISTRY.tsv")
    doc["registry_sha256_before"] = doc["rows"]["L1-11M"]["before"]["sha256"]  # placeholder, replaced below
    doc["rows_taken"] = sorted(doc["rows"])

    # 3. the change-control instance row
    inst_lines = open(INST, encoding="utf-8").read().rstrip("\n").split("\n")
    inst_rows = list(csv.reader(open(INST, encoding="utf-8"), delimiter="\t"))
    ihdr = [r for r in inst_rows if r and r[0] == "change_id"][0]
    migration = {
        "change_id": "CHG-20261024-CL56-ADOPT",
        "owner": ("Maintainer (repository delivery surface; card t_fabddb85, board pi-briefing; "
                  "owner-signed adoption decision of 2026-10-22, recorded as such and not as an audit pass)"),
        "entry_point": "/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py",
        "Q1": ("First-cause layer = L1 (the KB service loading point and the naming layer it reads). The "
               "shipped dictionary names a cell type at one granularity; where the author's own label is a "
               "finer Cell-Ontology term (5 clusters are called `ciliary muscle cell`, 8 `rod bipolar "
               "cell`, 3 `keratocyte`, ...) the answer can only ever be the coarser name, so the finer name "
               "is a naming gap and not a recognition failure. L0 (corpus), L2-L5 and L6 are untouched by "
               "this change."),
        "Q1_evidence": ("docs/plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md:1 names the layer and "
                        "the decision; docs/plans/cl56_adopt_20261022/REPORT.md:1 the measured effect"),
        "Q2": ("Layer to fix = L1 = the first-cause layer (equal, so the change lands there; no downstream "
               "patch, no transitional artefact). The change has two halves inside L1: (i) a new marker "
               "body `kb/markers/markers_v15_cl56_increment.json` with one entry per adopted child term, "
               "registered with an EMPTY whitelist; (ii) three additive rows in the KB label -> Cell "
               "Ontology map so an entry of this library is mappable at all. The service core gains the "
               "loader entry, the empty whitelist constant and the switch predicate; no existing entry, no "
               "label-map row and no other library is edited."),
        "Q2_evidence": ("docs/plans/cl56_adopt_20261022/out/WIRING.json:1 the four anchored edits, each "
                        "asserting exactly one match; docs/plans/cl56_adopt_20261022/out/PREIMAGE.json:1 the "
                        "kept pre-images of both edited files with their before-sha"),
        "Q3": ("Blast radius per file x per reading, with the loss/negative term stated: the recorded-set "
               "reading of the merge is a NEGATIVE result and it is not hidden -- with the increment merged "
               "into the default route, the cell-weighted consistent share falls %+.3fpp (%.3f%% -> %.3f%%), "
               "the inconsistent share rises %+.3fpp (%.3f%% -> %.3f%%), %d of %d datasets fall, and %d "
               "clusters move. Because of that the increment is NOT merged and the default route loses "
               "nothing: it is byte-identical in every state (721/721 + 229/229). So the shipped surface is "
               "unchanged and the negative term of this change is zero moving cells."
               % (f1["overall_delta_pp"]["consistent"], f1["overall_before"]["share_pct"]["consistent"],
                  f1["overall_after"]["share_pct"]["consistent"], b1["overall_delta_pp"],
                  b1["overall_before_pct"], b1["overall_after_pct"], n_falls, n_ds, len(moved))),
        "Q3_evidence": ("docs/plans/cl56_adopt_20261022/out/MEASURE.json:1 the two declaration readings and "
                        "the moved-cluster attribution; docs/plans/cl56_adopt_20261022/out/ACCEPTANCE.json:1 "
                        "verdict NO-GO with the failing clauses; "
                        "docs/plans/cl56_adopt_20261022/out/DEFAULT_FACE.json:1 the byte identity"),
        "Q4": ("Criteria frozen before the run (file on disk with its sha recorded before any measurement): "
               "no dataset's cell-weighted consistent share may fall under any of the three readings; the "
               "aggregate inconsistent share may not rise; every moved cluster must be attributed with its "
               "truth label and its before/after answer; every adopted cluster's author label must be the "
               "adopted name; and the kill switch must restore the pre-flip default byte-for-byte. The "
               "verdict is NO-GO on the first two and PASS on the last three."),
        "Q4_evidence": ("docs/plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md:1 (§5 acceptance "
                        "rule) sha256 %s; docs/plans/cl56_adopt_20261022/out/ACCEPTANCE.json:1 the five "
                        "clauses and their verdicts" % prereg_sha),
        "Q5": ("Escape door: `EYEKB_ACT_CL56`. Unset/empty/anything other than {0,false,off,no} = ON, which "
               "with the EMPTY whitelist merges nothing; the value {0,false,off,no} = OFF and is "
               "byte-identical to the unset state and to the pre-card default, measured by replaying the "
               "recorded query set at the SAME absolute path against the pre-card commit's core: 721/721 "
               "cluster windows and 229/229 battery calls identical in raw and canonical bytes. Removal of "
               "the constant is the one-commit rollback."),
        "Q5_evidence": ("docs/plans/cl56_adopt_20261022/out/DEFAULT_FACE.json:1 pre_card_byte_identity "
                        "(PARENT vs OFF0 vs UNSET, identical_raw true, n_differing_raw 0); "
                        "docs/plans/cl56_adopt_20261022/pre_images/eyekb_core.py.pre_cl56:1 the pre-card "
                        "bytes"),
        "M1": ("Version artefacts: a NEW version file (kb/markers/markers_v15_cl56_increment.json) instead "
               "of editing any marker body in place; the label map is bumped v1.1 -> v1.2 with ADDITIVE "
               "rows only and its own supersedes_note records why; nothing else is edited in place except "
               "the service core, which is the loading point and whose pre-card bytes are kept as a "
               "pre-image with the sha recorded."),
        "M1_evidence": ("docs/plans/cl56_adopt_20261022/out/PREIMAGE.json:1 sha256_before/after for both "
                        "edited files; docs/plans/cl56_adopt_20261022/out/REGISTRY_ROWS.json:1 the four "
                        "re-taken registry rows with their before/after values"),
        "M2": ("Impact list per file: added = kb/markers/markers_v15_cl56_increment.json and the mirrored "
               "docs/plans/cl56_adopt_20261022/ tree; changed = mcp_server/eyekb_core.py (loader entry, "
               "empty whitelist constant, switch predicate, explicit-route error message) and "
               "kb/markers/markers_cl_alignment_v2_unified.json (three additive rows + version); re-taken = "
               "docs/W3_PIPELINE_REGISTRY.tsv (L1-11M, L1-23, L1-32 new, L6-47), "
               "docs/SWITCH_COVERAGE_REGISTRY.tsv (regenerated), docs/CHANGE_CONTROL_G6_INSTANCE.tsv (this "
               "row), docs/RELEASE_IDENTITY.json, docs/RELEASE_MANIFEST_v1.json, docs/W3_MANIFEST.sha256 "
               "(last)."),
        "M2_evidence": ("docs/plans/cl56_adopt_20261022/out/REGISTRY_ROWS.json:1 the re-taken rows and the "
                        "new row; docs/plans/cl56_adopt_20261022/out/WIRING.json:1 the edit census "
                        "(4 anchored edits, 36 added lines, 0 removed)"),
        "M3": ("Regression gate with runnable command and concrete threshold: `bash tests/run_gates.sh` must "
               "end gates=8 failed=0 (CHAIN PASS: G3 41/41, G4 three byte anchors, G5 registry, G6 change "
               "control 8/8, G7, G8, G9, G10), run inside a clean clone at the commit under test; "
               "`python3 docs/plans/cl56_adopt_20261022/scripts/m1_measure.py` must print the same "
               "consistent/inconsistent deltas and `scripts/a1_acceptance.py` must print verdict: NO-GO on "
               "clauses a and b."),
        "M3_evidence": ("docs/plans/cl56_adopt_20261022/out/CLONE_REPO_GATES.log:1 the chain summary line; "
                        "docs/plans/cl56_adopt_20261022/out/CLONE_CHECK.json:1 the clone commit and both "
                        "chains' return codes; docs/plans/cl56_adopt_20261022/out/ACCEPTANCE.md:1 the "
                        "verdict"),
        "E1": ("sha evidence taken fresh in this commit, none quoted from an earlier report: the edited core "
               "sha256 %s, the new increment sha256 %s, the label map sha256 %s, the registry sha256 %s."
               % (sha_rel(CORE), sha_rel(INCR), sha_rel(CLMAP),
                  sha_rel("docs/W3_PIPELINE_REGISTRY.tsv"))),
        "E1_evidence": ("docs/plans/cl56_adopt_20261022/out/MANIFEST.sha256:1 every artefact of this wave "
                        "with its sha256, verified with `sha256sum -c`; "
                        "docs/plans/cl56_adopt_20261022/out/REGISTRY_ROWS.json:1 the registry re-take"),
        "E2": ("Rollback identity, two independent paths: path 1 -- the switch: EYEKB_ACT_CL56=0 reproduces "
               "the pre-card default byte-for-byte, measured against the pre-card commit's core at the same "
               "absolute path (721/721 + 229/229, raw and canonical); path 2 -- the bytes: both edited "
               "files are kept as pre-images with their shas recorded, so restoring them returns the tree "
               "to the pre-card state."),
        "E2_evidence": ("python3 docs/plans/cl56_adopt_20261022/scripts/m2_default_face.py -> "
                        "pre_card_byte_identity identical_raw=True (721/721, 229/229); "
                        "docs/plans/cl56_adopt_20261022/pre_images/:1 the two pre-images"),
        "E3": ("Differential reading, negative column included, no gains-only reporting: the merge moves %d "
               "clusters / %d cells; consistent %.3f%% -> %.3f%% (%+.3fpp), inconsistent %.3f%% -> %.3f%% "
               "(%+.3fpp), mixed %.3f%% -> %.3f%%; %d clusters move up a grade and %d move down (%d cells up "
               "/ %d cells down); %d clusters are renamed by an adopted entry and only %d of those carry "
               "that term as their author label."
               % (len(moved), sum(x["n_cells"] for x in moved),
                  f1["overall_before"]["share_pct"]["consistent"], f1["overall_after"]["share_pct"]["consistent"],
                  f1["overall_delta_pp"]["consistent"], b1["overall_before_pct"], b1["overall_after_pct"],
                  b1["overall_delta_pp"], f1["overall_before"]["share_pct"]["mixed"],
                  f1["overall_after"]["share_pct"]["mixed"], n_up, n_down, cells_up, cells_down,
                  len(tak), len(tak_on))),
        "E3_evidence": ("docs/plans/cl56_adopt_20261022/out/MEASURE.json:1 moved/moved_kinds, the grade "
                        "transition matrix and the clause_d table; "
                        "docs/plans/cl56_adopt_20261022/out/harness/A1_recorded_decls/REPORT.md:1 the "
                        "harness's own per-dataset table"),
        "E4": ("Ledger registration: new row L1-32 records the increment and its NO-GO; L1-11M and L1-23 are "
               "re-taken from live bytes; L6-47 is re-taken after the switch registry was regenerated from "
               "source (G10 R1 binding); docs/GATE_INVENTORY_G5G6.tsv needs no new gate because no gate of "
               "the chain invokes this library, and it is left byte-unchanged. Time order: switch registry "
               "-> registry rows -> change-control row -> release identity -> W3 manifest last."),
        "E4_evidence": ("docs/W3_PIPELINE_REGISTRY.tsv:1 rows L1-11M / L1-23 / L1-32 / L6-47; "
                        "docs/plans/cl56_adopt_20261022/out/REGISTRY_ROWS.json:1 the readout; "
                        "docs/W3_MANIFEST.sha256:1 the registry checksum, re-frozen last"),
    }
    missing = [c for c in ihdr if c not in migration]
    if missing:
        raise SystemExit("instance row is missing columns: %s" % missing)
    inst_lines.append("\t".join(migration[c] for c in ihdr))
    with open(INST, "w", encoding="utf-8") as f:
        f.write("\n".join(inst_lines) + "\n")
    doc["instance_row"] = "CHG-20261024-CL56-ADOPT"
    doc["instance_sha256_after"] = sha_rel("docs/CHANGE_CONTROL_G6_INSTANCE.tsv")

    # 4. W3 manifest LAST (only the registry row changes there)
    man = os.path.join(REPO, "docs", "W3_MANIFEST.sha256")
    lines = open(man, encoding="utf-8").read().rstrip("\n").split("\n")
    out, touched = [], []
    for ln in lines:
        if ln.startswith("#") or not ln.strip():
            out.append(ln)
            continue
        s, rel = ln.split()[0], ln.split()[-1]
        newsha = sha_rel("docs/" + rel)
        if s != newsha:
            touched.append({"file": rel, "before": s, "after": newsha})
        out.append("%s  %s" % (newsha, rel))
    header = ("# re-taken 2026-10-24 (card t_fabddb85, CL-56 adoption): the registry row was re-taken "
              "after adding row L1-32 and re-taking L1-11M / L1-23 / L6-47; the other rows are unchanged.")
    idx0 = max(i for i, ln in enumerate(out) if ln.startswith("#"))
    out = out[:idx0 + 1] + [header] + out[idx0 + 1:]
    with open(man, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    doc["w3_manifest_touched"] = touched
    doc["w3_manifest_sha256"] = sha_rel("docs/W3_MANIFEST.sha256")

    with open(os.path.join(OUT, "REGISTRY_ROWS.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    print("switch registry:", doc["switch_registry"]["stdout"], "| has EYEKB_ACT_CL56:",
          doc["switch_registry"]["has_cl56"])
    print("registry rows taken:", doc["rows_taken"], "+ new", NEW_ROW_ID)
    print("instance row added:", doc["instance_row"])
    print("W3 manifest touched:", touched)
    print("wrote out/REGISTRY_ROWS.json")


if __name__ == "__main__":
    main()