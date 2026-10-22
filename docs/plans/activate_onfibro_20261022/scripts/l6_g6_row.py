#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l6 -- append the change-control instance row for the activation (27 columns, G6 rules R1-R8).

Because the flip changes default bytes on purpose, the change must be *introduced* legitimately:
twelve content cells (Q1-Q5 / M1-M3 / E1-E4) plus their evidence cells, three identity cells, every
content cell carrying an evidence cell with a resolvable anchor, the pre-registered criteria carrying
a sha anchor, the escape door naming its switch and its OFF byte identity, and the default-ON
behaviour change naming the precondition registration -- which is what R8 checks.

The row is appended; the file's earlier rows and its comment block are not touched.
"""
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
INST = os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv")
WAVE = "docs/plans/activate_onfibro_20261022"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    prereg_sha = sha256(os.path.join(REPO, WAVE, "PREREG_ACTIVATION_ONFIBRO_20261022.md"))
    core_sha = sha256(os.path.join(REPO, "mcp_server", "eyekb_core.py"))
    reg_sha = sha256(os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv"))
    rows = [l for l in open(INST, encoding="utf-8").read().split("\n")]
    hdr_i = [i for i, l in enumerate(rows) if l.startswith("change_id\t")][0]
    hdr = rows[hdr_i].split("\t")
    assert len(hdr) == 27, "instance header moved: %d columns" % len(hdr)
    existing = [l.split("\t")[0] for l in rows[hdr_i + 1:] if l.strip()]
    cid = "CHG-20261022-ONFIBRO-ACTIVATION"
    if cid in existing:
        print("row already present; nothing to do")
        return 0

    r = {}
    r["change_id"] = cid
    r["owner"] = ("Maintainer (repository delivery surface; activation card t_42df17c2, board "
                  "pi-briefing; PI-signed activation of the optic-nerve fibroblast carrier)")
    r["entry_point"] = "/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py"

    r["Q1"] = ("First-cause layer = L1 (the KB service loading point: the default-route library "
               "whitelist). The carrier library `onfibro_v13` was registered by card t_0c40c7b1 with "
               "an EMPTY whitelist, so the fibroblast family's only reachable carrier on the "
               "optic-nerve side was unreachable by any caller on the default route and a "
               "coarse-but-family-correct answer degraded to an abstention. Removing that layer's "
               "cause (the library becoming a member of the default route) removes the abstention. "
               "L0 (corpus), L2-L5 (vocabulary, generators, adjudication, contract) and L6 (gates) "
               "are untouched by this change.")
    r["Q1_evidence"] = (WAVE + "/PREREG_ACTIVATION_ONFIBRO_20261022.md:1 the pre-registration names "
                        "the layer and the decision; %s/REPORT.md:1 the measured effect" % WAVE)

    r["Q2"] = ("Layer to fix = L1 = the first-cause layer (equal, so the fix lands there; no "
               "downstream patch and no transitional artefact). The change is a wiring change inside "
               "the service core: ONFIBRO_DEFAULT_LIBS gains `onfibro_v13` and the surrounding "
               "comments/docstring state the activation; the carrier file itself is byte-unchanged. "
               "Everything else in this commit is registration: registry rows L1-11M / L1-30 / L6-01 "
               "/ L6-37, docs/VERIFY_CONTRACT.md §5.5, docs/RELEASE_IDENTITY.json, "
               "docs/RELEASE_MANIFEST_v1.json, docs/W3_MANIFEST.sha256, and this row.")
    r["Q2_evidence"] = (WAVE + "/out/FLIP.json:1 the diff census (2 hunks, both inside the ONFIBRO "
                        "region, 21 added / 10 removed lines, whitelist delta = ONFIBRO only); "
                        + WAVE + "/out/PREIMAGE.json:1 the pre-image of the pre-flip file")

    r["Q3"] = ("Blast radius per file x per reading, with the loss/negative term stated and not "
               "omitted: (1) the answers of the default route move on 45 of the 721 recorded "
               "clusters (cell-weighted +1.496pp consistent on the default route; +1.692pp under the "
               "recorded declarations; +1.618pp under the tester's declarations), no dataset's share "
               "falls on either route, and no cell moves down a grade (harm cells = 0); (2) every "
               "response that carries the provenance/soft-flag disclosure fields moves, because it "
               "now names the carrier's file and entries -- 676 of the 721 cluster queries move in "
               "bytes while their ranking does not; (3) the loss: the LEGACY TOOL-PANEL DIGEST MOVED "
               "and its baseline fixture was NOT re-recorded, so the panel probe is red at this "
               "commit (compatibility item, reported rather than absorbed); (4) rollback/negative: "
               "the switch EYEKB_ACT_ONFIBRO=0 restores the pre-flip default byte-for-byte and the "
               "commit can be reverted, so the change is not monotone in the shipped surface -- it "
               "is reversible at three levels; (5) does-not-move: the carrier file, the exclusion "
               "table, the score, the admission floor, the tie-break, every other library, "
               "tests/verify_repro.py, tests/verify_pipeline.py and the expectation files.")
    r["Q3_evidence"] = (WAVE + "/out/FLIP_MEASUREMENT.json:1 the four arm readings and the "
                        "45-cluster attribution; " + WAVE + "/out/DEFAULT_FACE.json:1 the "
                        "kill-switch byte identity (721/721 + 229/229) and the moved-query census; "
                        + WAVE + "/out/FIELD_DIFF.json:1 the per-path diff proving the disclosure "
                        "fields are what move on the non-ranking queries")

    r["Q4"] = ("Criteria frozen before the run (the file exists on disk with its sha recorded before "
               "any measurement): no dataset's cell-weighted consistent share may fall under either "
               "declaration set (PASS, not PASS_ATTRIBUTED, because this card activates rather than "
               "proposes); every moved cluster must be attributed with its truth label and its "
               "before/after answer; the kill switch must restore the pre-flip default byte-for-byte; "
               "gates G3-G8 green in a clean clone. Failure exit condition: any dataset falls, or any "
               "moved cluster is unexplained, or the kill switch is not byte-identical -> the "
               "activation is rolled back rather than reported.")
    r["Q4_evidence"] = (WAVE + "/PREREG_ACTIVATION_ONFIBRO_20261022.md:1 (§3.3 acceptance rule) "
                        "sha256 %s; frozen criteria file sha256 %s for the activated core"
                        % (prereg_sha, core_sha))

    r["Q5"] = ("Escape door: `EYEKB_ACT_ONFIBRO`. Unset/empty/anything other than {0,false,off,no} = "
               "the carrier is part of the default `all` route; the value {0,false,off,no} = OFF and "
               "is byte-identical to the pre-flip default, measured by replaying the recorded query "
               "set at the SAME absolute path against the parent commit's core: 721/721 cluster "
               "windows and 229/229 battery calls identical in raw and canonical bytes, so the OFF "
               "state is a complete rollback of the observable surface. A revert of the commit is "
               "the second route and the kept pre-image the third.")
    r["Q5_evidence"] = (WAVE + "/out/DEFAULT_FACE.json:1 kill_switch_byte_identity (identical_raw "
                        "true, n_differing_raw 0, both modes); " + WAVE +
                        "/pre_images/eyekb_core.py.pre_activation:1 the pre-flip bytes, sha256 "
                        "3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736")

    r["M1"] = ("Version artefacts: the carrier file is NOT edited in place (a wiring change, not a "
               "panel change) -- its sha is unchanged and its registry row keeps that sha; the "
               "service core is edited in place because it is the loading point, and its pre-flip "
               "bytes are kept as a pre-image (route 2 of the rollback) with the sha recorded; the "
               "new capability is not a new file, so no new version file is introduced.")
    r["M1_evidence"] = (WAVE + "/out/PREIMAGE.json:1 pre_image_sha256 == live_before_sha256; "
                        + WAVE + "/out/REGISTRY_UPDATE.json:1 the four re-taken rows with their "
                        "before/after values")

    r["M2"] = ("Impact list per file: changed = mcp_server/eyekb_core.py (the whitelist constant and "
               "its documentation); re-taken = docs/W3_PIPELINE_REGISTRY.tsv (rows L1-11M, L1-30, "
               "L6-01, L6-37), docs/VERIFY_CONTRACT.md (§5.5, the R8 precondition registration), "
               "docs/RELEASE_IDENTITY.json, docs/RELEASE_MANIFEST_v1.json, docs/W3_MANIFEST.sha256 "
               "(last), docs/CHANGE_CONTROL_G6_INSTANCE.tsv (this row), plus the new evidence root "
               "%s/. Not changed: kb/markers/markers_v13_onfibro_increment.json, the exclusion "
               "table, every other marker library, pipeline/**, clients/**, tests/verify_repro.py, "
               "tests/verify_pipeline.py, tests/REPRO_EXPECTED.json, tests/G4_EXPECTED.json, "
               "tests/probe_tool_panel_identity.py and tests/fixtures/tool_panel_baseline.json (left "
               "un-re-recorded on purpose)." % WAVE)
    r["M2_evidence"] = (WAVE + "/out/FLIP.json:1 whitelist_delta = {ONFIBRO_DEFAULT_LIBS: "
                        "[(), (onfibro_v13,)]} only; " + WAVE + "/out/REGISTRY_UPDATE.json:1 the "
                        "re-taken rows; registry ledger sha256 %s" % reg_sha)

    r["M3"] = ("Regression gate with runnable command and concrete threshold: `bash tests/run_gates.sh` "
               "must end gates=6 failed=0 (CHAIN PASS; G3 verify_repro 41/41, G4 three byte anchors, "
               "G5 registry 8/8, G6 change control 8/8, G7, G8), run inside a clean clone at the "
               "commit under test; `python3 " + WAVE + "/scripts/l2_flip_measure.py` must print "
               "verdict=PASS with datasets_falling=[] on the recorded, the tester and the default "
               "route arms; `python3 " + WAVE + "/scripts/l3_default_face.py` must print "
               "KILL-vs-PARENT raw-identical=True for 721/721 and 229/229 with n_unexplained=0. This "
               "row also carries the DEFAULT-ON change, whose gate precondition is registered in "
               "docs/VERIFY_CONTRACT.md §5.5 (G6-R8).")
    r["M3_evidence"] = (WAVE + "/out/REPO_GATES.log:1 the chain summary line; " + WAVE +
                        "/out/CLEAN_CLONE_CHECK.json:1 the clone commit, both chains' return codes "
                        "and the mirror-fidelity comparison; " + WAVE + "/out/GATE.json:1 this "
                        "wave's own gate verdict")

    r["E1"] = ("sha evidence taken fresh in this commit, none quoted from an earlier report: the "
               "activated core sha256 %s, the carrier file sha256 %s (unchanged), the registry "
               "sha256 %s, and the pre-registration sha256 %s -- all recomputed with `sha256sum` "
               "after the last write." % (core_sha, sha256(os.path.join(
                   REPO, "kb", "markers", "markers_v13_onfibro_increment.json")), reg_sha, prereg_sha))
    r["E1_evidence"] = (WAVE + "/out/MANIFEST.sha256:1 every artefact of this wave with its "
                        "sha256, verified with `sha256sum -c`; " + WAVE + "/out/REGISTRY_UPDATE.json:1 "
                        "the registry re-take with before/after sha values")

    r["E2"] = ("Rollback identity, two independent paths: path 1 -- the switch: with the activation in "
               "place, EYEKB_ACT_ONFIBRO=0 reproduces the pre-flip default byte-for-byte, measured "
               "against the parent commit's core at the same absolute path (721/721 + 229/229 "
               "identical raw and canonical); path 2 -- the bytes: the pre-flip core is kept as a "
               "pre-image with its sha recorded, so restoring `ONFIBRO_DEFAULT_LIBS = ()` is "
               "verifiable without git, and `git revert <commit>` is available as the third route. "
               "The default-ON behaviour change this row records is registered as a gate "
               "precondition in docs/VERIFY_CONTRACT.md §5.5 (R8).")
    r["E2_evidence"] = ("python3 " + WAVE + "/scripts/l3_default_face.py -> kill_switch_byte_identity "
                        "identical_raw=True (721/721, 229/229), differing raw=0; " + WAVE +
                        "/pre_images/eyekb_core.py.pre_activation sha256 "
                        "3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736")

    r["E3"] = ("Differential reading, negative column included, no gains-only reporting: overall "
               "cell-weighted consistent share 40.852% -> 42.544% (+1.692pp, recorded declarations), "
               "41.061% -> 42.679% (+1.618pp, tester declarations), and +1.496pp on the default "
               "route with no tissue argument; 45 clusters move, all attributed (13 carrier-gain, "
               "32 rank-shift, 0 unexpected, 0 takeover on another family); harm cells = 0; the "
               "negative column: the legacy tool-panel digest moved and its baseline is stale (no "
               "re-record), and 676 cluster queries move in bytes with unchanged rankings because of "
               "the disclosure fields. Nothing here is an accuracy claim: the reading is IN-SAMPLE "
               "on the volumes the carrier was selected on, and the carrier is a family-level coarse "
               "answer at the bar.")
    r["E3_evidence"] = (WAVE + "/out/FLIP_MEASUREMENT.json:1 moved_kinds, harm_cells and the "
                        "per-cluster table; " + WAVE + "/out/DEFAULT_FACE.json:1 the moved-query "
                        "census and the compatibility item")

    r["E4"] = ("Ledger registration: new row L1-30's authority text now states the activation, row "
               "L1-11M's sha/bytes/mtime and note are re-taken from live bytes, L6-01 is re-taken "
               "for the §5.5 precondition, and L6-37 records why the baseline fixture was left "
               "un-re-recorded; docs/GATE_INVENTORY_G5G6.tsv needs no new gate (no gate of the "
               "chain invokes the panel probe) and is left byte-unchanged. Time order: pre-registration "
               "first, flip second, measurements third, registrations fourth, manifest last.")
    r["E4_evidence"] = ("docs/W3_PIPELINE_REGISTRY.tsv:1 rows L1-11M / L1-30 / L6-01 / L6-37 as "
                        "re-taken by " + WAVE + "/scripts/l4_registry_rows.py; " + WAVE +
                        "/out/REGISTRY_UPDATE.json:1 the re-take readout; docs/W3_MANIFEST.sha256:1 "
                        "the registry checksum, re-frozen last")

    row = [r[h] for h in hdr]
    for h in hdr:
        assert r.get(h), "empty cell %s" % h
    # rebuild: keep the comment block + header + existing data rows, append the new row, drop the
    # trailing empty line
    kept = rows[:hdr_i + 1] + [l for l in rows[hdr_i + 1:] if l.strip()]
    out_txt = "\n".join(kept + ["\t".join(row)]) + "\n"
    assert out_txt.count("\n") == len(kept) + 1, "row count changed while serialising"
    tmp = INST + ".tmp-activate"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(out_txt)
    os.replace(tmp, INST)
    # read back: the cell count must still be 27
    back = [l for l in open(INST, encoding="utf-8").read().split("\n") if l.strip()]
    assert back[-1].split("\t")[0] == cid and len(back[-1].split("\t")) == 27

    doc = {"probe": "l6_g6_row.py", "instance": "docs/CHANGE_CONTROL_G6_INSTANCE.tsv",
           "change_id": cid, "columns": len(row),
           "rows_before": len([x for x in existing]), "rows_after": len(back) - hdr_i - 1,
           "instance_sha256": sha256(INST), "prereg_sha256": prereg_sha,
           "activated_core_sha256": core_sha, "registry_sha256": reg_sha,
           "verdict": "PASS"}
    json.dump(doc, open(os.path.join(OUT, "G6_ROW.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())