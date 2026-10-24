# -*- coding: utf-8 -*-
"""registry_update.py -- re-take row L1-31 from live bytes and append the two change-control
instance rows for this wave. Byte-discipline: the file is handled as raw TSV via split/ '/'
'.join on '\t'; every cell text asserted tab-free and newline-free; all other bytes unchanged.
Idempotent at the row level (a second run aborts on an already-present change_id)."""
import hashlib
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs/W3_PIPELINE_REGISTRY.tsv")
G6 = os.path.join(REPO, "docs/CHANGE_CONTROL_G6_INSTANCE.tsv")

# ---------------- L1-31 re-take from live bytes (idempotent: skips if already re-taken) ----------------
lib = os.path.join(REPO, "kb/markers/markers_v14_subtype_second_increment.json")
st = os.stat(lib)
sha_now = hashlib.sha256(open(lib, "rb").read()).hexdigest()
bytes_now = st.st_size
import datetime
mtime_now = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

lines = open(REG, encoding="utf-8").read().split("\n")
target_idx = None
for i, ln in enumerate(lines):
    cols = ln.split("\t")
    if len(cols) > 2 and cols[1] == "L1-31":
        target_idx = i
        before_cols = cols
        break
assert target_idx is not None, "row L1-31 not found"
assert len(before_cols) == 17, len(before_cols)
sha_before, bytes_before, mtime_before = before_cols[10], before_cols[11], before_cols[12]
l131_already = (sha_before == sha_now and "2026-10-24 card t_c19cd667 (KB-REACH)" in before_cols[14])
if not l131_already:
    NOTE = (" | 2026-10-24 card t_c19cd667 (KB-REACH): the file body carried 16 entries but no "
            "top-level `markers` key, and _load_marker_dbs feeds db[markers] to the ranking, so "
            "library=subtype_v14 answered an EMPTY ranking (n_ranked=0) while this row said reachable "
            "by name (defect found and measured by card t_fabddb85 section 6.1). Fixed by deriving the "
            "top-level markers block from the file's own 16 entries (class_name -> markers, inserted "
            "immediately before `entries`), with zero panel-gene change asserted (per-class gene lists "
            "byte-equal 16/16, union unchanged; out/F1_FIX.json). Default-route byte identity measured, "
            "not asserted: 721/721 recorded cluster windows + 238/238 battery calls + 15/15 explicit "
            "calls identical raw and canonical before/after (out/PRE_*.json vs out/POST_*.json). "
            "Explicit-route reply now: inventory lists the 16 classes (was 0); best recorded window "
            "CX02_adult_retina#7 ranks 0 -> 6 candidates (top ON-bipolar cell); full 721-window census "
            "max=6/16 (out/R2B_CENSUS.json) -- the brief's n_ranked=16 literal is unreachable on the "
            "recorded set and is reported as a measured non-result. sha/bytes/mtime re-taken from live "
            "bytes in the same commit. The derivation-only edit is inside this row's never-edited-in-"
            "place gate as a registration-layer fix: panel genes bit-identical, entries fragment "
            "untouched, byte-exact pre-image kept at docs/plans/kbreach_fix_20261024/pre_images/"
            "markers_v14_subtype_second_increment.json.pre_kbreach (sha256 75884fb7bd88e1ab7fd1652a26051"
            "046bff07dd0c6ee2972abfd7c8100f9f452).")
    note_new = before_cols[14] + NOTE
    cols = list(before_cols)
    cols[10] = sha_now
    cols[11] = str(bytes_now)
    cols[12] = mtime_now
    cols[14] = note_new
    for c in cols:
        assert "\t" not in c and "\n" not in c, "cell text would break TSV discipline"
    lines[target_idx] = "\t".join(cols)
    with open(REG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    lines2 = open(REG, encoding="utf-8").read().split("\n")
    assert len(lines2) == len(lines)
    diffs = [i for i, (a, b) in enumerate(zip(lines, lines2)) if a != b]
    assert diffs == [], diffs
else:
    print("L1-31 already re-taken (idempotent skip)")

# ---------------- G6 instance rows (2) ----------------
COMMON_MIRROR = "docs/plans/kbreach_fix_20261024"
row1 = [
    "CHG-20261024-KBREACH-SUBTYPE14-BODY",
    "Maintainer (repository delivery surface; card t_c19cd667, board pi-briefing; the defect was found and measured by card t_fabddb85 section 6.1 and is outside that card's scope)",
    "/home/ubuntu/EYEKB_REPO/kb/markers/markers_v14_subtype_second_increment.json",
    ("First-cause layer = L1 (the release-file body). The shipped file carries 16 entries but no "
     "top-level `markers` key; mcp_server/eyekb_core.py `_load_marker_dbs` feeds db[markers] to the "
     "ranking, so query_marker(library=subtype_v14) answers an EMPTY ranking (n_ranked=0, "
     "out/DEFAULT_FACE.json of card t_fabddb85: explicit_route_reachability.subtype_v14) while row "
     "L1-31 tells the reader the library is reachable by name."),
    ("%s/out/R1_REPRODUCE.json:1 the pre-fix reading (markers_key_present false, n_ranked 0, "
     "inventory 0); %s/out/DEFAULT_FACE.json of /mnt/D/EyeKB/plans/cl56_adopt_20261022/:1 the "
     "explicit-route row the defect was found from" % (COMMON_MIRROR, "/mnt/D/EyeKB/plans/cl56_adopt_20261022")),
    ("Layer to fix = L1, the first-cause layer itself, no downstream patch and no transitional "
     "artefact. The top-level `markers` block is DERIVED from the file's own entries "
     "(class_name -> markers list, insertion order and per-class gene order preserved), inserted "
     "immediately before `entries`; no service-core edit was needed or made -- the core file is "
     "byte-unchanged in this commit."),
    ("%s/out/F1_FIX.json:1 the derivation record with every assertion (16 distinct class names, "
     "per-class gene lists byte-equal, panel_gene_union_unchanged true, only key added = markers); "
     "git show HEAD: no diff under mcp_server/" % COMMON_MIRROR),
    ("Blast radius measured on both routes. Default route: byte-identical before/after - "
     "721/721 recorded cluster windows, 238/238 battery calls, 15/15 explicit calls, raw and "
     "canonical, 0 differing rows in both readings. Explicit route: only reachable by naming "
     "library=subtype_v14; the empty whitelist (SUBTYPE_DEFAULT_LIBS) is untouched, so `all` cannot "
     "see the new block in any switch state."),
    ("%s/out/PRE_clusters.json vs %s/out/POST_clusters.json (raw_md5 61ac177e309458a7832058a6cf95a286"
     " = canon 058004589e2b7f311c8517a05144ea60, row-level n_differing_raw 0); same for "
     "PRE/POST_battery.json (d7400a22b408ca3d8da62d03d9fdcadf / 59fa523a1f1824353cbb96307028e35b) and "
     "PRE/POST_explicit.json (f1f3cc201f7b55b7655f63147b03faa7 / a8d87b8aaa5531b3676d24fda381d020)"
     % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Criteria frozen before the fix ran (this card body): (i) default-route replay byte-identical "
     "before/after; (ii) the release file answers through its explicit route (measured readouts "
     "stated under E3); (iii) panel genes unchanged (assertion, before any write); (iv) row L1-31 "
     "re-taken from live bytes in the same commit."),
    ("%s/out/R1_REPRODUCE.json:1 (D1c coverage oracle computed before any byte change); "
     "%s/out/F1_FIX.json:1 (the frozen assertion set); docs/W3_PIPELINE_REGISTRY.tsv:1 row L1-31 "
     "re-taken column sha256/bytes/mtime" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Escape door unchanged: EYEKB_ACT_SUBTYPE cannot inject subtype_v14 into `all` in any state "
     "(SUBTYPE_DEFAULT_LIBS = () in mcp_server/eyekb_core.py); rollback = restore the byte-exact "
     "pre-image, verified by sha256, then the PRE replay digests reproduce."),
    ("%s/pre_images/markers_v14_subtype_second_increment.json.pre_kbreach:1 sha256 "
     "75884fb7bd88e1ab7fd1652a26051046bff07dd0c6ee2972abfd7c8100f9f452 (== the registered row sha "
     "before this commit); mcp_server/eyekb_core.py:1003 SUBTYPE_DEFAULT_LIBS = () unchanged"
     % COMMON_MIRROR),
    ("Version artefacts: the release file is edited in place ONLY to add the derived registration "
     "block; the entries fragment is untouched (panel genes bit-identical, asserted before the "
     "write); the file's own version string is untouched (v14.0-subtype-second-marker-20261022). "
     "This sits inside row L1-31's never-edited-in-place gate as a registration-layer fix and is "
     "declared there; a new file name was rejected because the defect IS the registration record, "
     "not the panel content, and the L1-31 row points at this exact path."),
    ("%s/out/F1_FIX.json:1 (bytes 37576 -> 38759, insertion position, indent style); "
     "docs/W3_PIPELINE_REGISTRY.tsv:1 row L1-31 notes column, 2026-10-24 clause" % COMMON_MIRROR),
    ("Impact list per file: changed = kb/markers/markers_v14_subtype_second_increment.json "
     "(37576 -> 38759 bytes) and its registry row re-take; added = docs/HARNESS_LIMIT_QUALIFIED_ISA_"
     "20261024.md, docs/plans/kbreach_fix_20261024/ (mirror of this wave: REPORT.md, scripts/, out/, "
     "pre_images/); docs/RELEASE_IDENTITY.json re-taken; docs/W3_MANIFEST.sha256 re-frozen last; the "
     "tool-panel baseline re-record is a separate row of this wave (CHG-20261024-KBREACH-TOOLPANEL-"
     "BASELINE)."),
    ("%s/out/F1_FIX.json:1; %s/out/R2B_CENSUS.json:1; %s/out/R3_CLOSURE_READING.json:1; "
     "git status --porcelain of the commit" % (COMMON_MIRROR, COMMON_MIRROR, COMMON_MIRROR)),
    ("Regression gate: a clean clone of the commit must pass `bash tests/run_gates.sh` ending "
     "`gates=8 failed=0 (CHAIN PASS)` (G3 41/41 retrieval, G4 three byte anchors, G5 registry, G6 "
     "change control, G7 ontology anchors, G8 portability, G9 pre-image immutability, G10 switch "
     "coverage); the identity device must pass `tests/probe_tool_panel_identity.py --baseline "
     "tests/fixtures/tool_panel_baseline.json` with exit 0."),
    ("%s/out/CLONE_REPO_GATES.log:1 the chain summary line of this commit's clean-clone run; "
     "%s/out/PROBE_AFTER_RERECORD.log:1 IDENTITY PASS + rc=0" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("sha evidence taken fresh in this commit, none quoted from an earlier report: file sha256 after "
     "f0978ceec6945db72184a400364d5b7537a9e78e25c59db6697c0de2aff468cb (bytes 38759, mtime %s); "
     "sha256 before 75884fb7bd88e1ab7fd1652a26051046bff07dd0c6ee2972abfd7c8100f9f452 (bytes 37576, "
     "mtime 2026-10-22 21:28:06, == the registered value this commit replaces)." % mtime_now),
    ("%s/out/F1_FIX.json:1 both hashes with their byte counts; docs/W3_PIPELINE_REGISTRY.tsv:1 the "
     "re-taken L1-31 row carries exactly these two values" % COMMON_MIRROR),
    ("Rollback identity: restore the pre-image bytes (byte-exact, sha-verified) -> the release file "
     "returns to sha256 75884fb7... and the replay re-run reproduces the PRE digests; the registry "
     "row reverts by removing this commit's clause. No switch, no destructive step."),
    ("%s/pre_images/markers_v14_subtype_second_increment.json.pre_kbreach:1 (the kept pre-image); "
     "%s/out/PRE_clusters.json:1 (the PRE digests the rollback must reproduce)"
     % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Differential reading, negative column included: the fix makes the explicit route ANSWER, and "
     "the answer is window-dependent by design - 576/721 recorded windows still rank 0 candidates "
     "(no marker overlap with the panel), the best recorded window ranks 6/16 (CX02_adult_retina#7, "
     "top ON-bipolar cell, n_cells 2398); the card brief's acceptance literal n_ranked=16 for a "
     "recorded probe window is UNREACHABLE on the recorded set (full census over all 721 windows) "
     "and is reported as a measured non-result, not rounded to PASS; no window gained a new best "
     "candidate outside its own marker overlap."),
    ("%s/out/R2B_CENSUS.json:1 census_by_n_ranked {0:576, 1:59, 2:42, 3:9, 5:31, 6:4} and the best "
     "window; %s/out/D1_after rowdiff_* all 0 differences; %s/out/R1_REPRODUCE.json:1 the same "
     "oracle computed BEFORE the fix (static, best=6, same window)" % (COMMON_MIRROR, COMMON_MIRROR, COMMON_MIRROR)),
    ("Ledger registration: docs/W3_PIPELINE_REGISTRY.tsv row L1-31 re-taken from live bytes in this "
     "commit (sha256/bytes/mtime + the 2026-10-24 notes clause); docs/CHANGE_CONTROL_G6_INSTANCE.tsv "
     "gains this row and the tool-panel baseline row; docs/W3_MANIFEST.sha256 re-frozen last after "
     "the registry is final; docs/RELEASE_IDENTITY.json re-taken after every byte change landed."),
    ("docs/W3_PIPELINE_REGISTRY.tsv:1 row L1-31; docs/CHANGE_CONTROL_G6_INSTANCE.tsv:1 rows "
     "CHG-20261024-KBREACH-SUBTYPE14-BODY and CHG-20261024-KBREACH-TOOLPANEL-BASELINE; "
     "docs/W3_MANIFEST.sha256:1 re-frozen last; docs/RELEASE_IDENTITY.json:1 re-taken"),
]

row2 = [
    "CHG-20261024-KBREACH-TOOLPANEL-BASELINE",
    "Maintainer (repository identity device; card t_c19cd667; the response drift itself was introduced by card t_42df17c2 activating onfibro_v13 on the default route, and that card's own L1-11M note left the device RED by design stating the baseline was NOT re-recorded)",
    "/home/ubuntu/EYEKB_REPO/tests/probe_tool_panel_identity.py",
    ("First-cause layer = L6 (the identity device) over an L1 answer change: the two moved calls "
     "differ ONLY in the response's provenance field - provenance.files gains the activated "
     "onfibro_v13 line and provenance.conflicts gains the onfibro_v13::Fibroblast alias. The "
     "semantic surface is identical between the baseline commit and HEAD (markers keys, "
     "celltype_ranking order, n_shared_first 5)."),
    ("%s/out/D2_FIELD_DIFF.json:1 the field-level diff (n_differing 2 of 12; both limited to "
     "provenance); %s/out/DUMP_435bb92.json:1 vs %s/out/DUMP_HEAD.json:1 the two full-response "
     "dumps (12/12 calls, per-call md5 of the 435bb92 arm == the approved fixture bytes)"
     % (COMMON_MIRROR, COMMON_MIRROR, COMMON_MIRROR)),
    ("Layer to fix = L6 re-record, executed in the commit that makes the device green again, with "
     "the per-call attribution recorded here as the device's own instruction requires; no service "
     "bytes change for this row (tests/probe_tool_panel_identity.py byte-unchanged)."),
    ("%s/out/D2_FIELD_DIFF.json:1 semantic_summary blocks for both moved calls (ranking identical; "
     "identical fields detail/found/markers/mode)" % COMMON_MIRROR),
    ("Blast radius: 12/12 panel calls driven, 0 refused; 10/12 call digests byte-identical across "
     "435bb92 and HEAD before the re-record; after the re-record the probe exits 0 against the new "
     "fixture; shipped route bytes are untouched by this row (the default-route replay of this "
     "commit is byte-identical, see row CHG-20261024-KBREACH-SUBTYPE14-BODY)."),
    ("%s/out/R1_REPRODUCE.json:1 (D2_probe_baseline rc=1, moved_calls = the two calls); "
     "%s/out/PROBE_AFTER_RERECORD.log:1 rc=0 IDENTITY PASS after the re-record"
     % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Criteria frozen before the re-record: attribution first (field-level, both commits replayed), "
     "then re-record with the SAME interpreter family the fixture provenance declares "
     "(/home/ubuntu/training-venv/bin/python3, python 3.14.4, pydantic 2.12.5), then probe --baseline "
     "must exit 0."),
    ("%s/out/DUMP_435bb92.json:1 provenance (python 3.14.4 / pydantic 2.12.5) matching "
     "tests/fixtures/tool_panel_baseline.json provenance before the re-record" % COMMON_MIRROR),
    ("Escape door: none required; the PRE fixture bytes are kept verbatim "
     "(sha256 ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87) and restoring them "
     "returns the probe to its recorded RED state (the defect state this commit closes)."),
    ("%s/pre_images/tool_panel_baseline.json.pre_rerecord:1 sha256 "
     "ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87; %s/out/R1_REPRODUCE.json:1 "
     "the RED reading this rollback reproduces" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Version artefacts: the fixture is re-recorded through the probe's own --record pipeline; the "
     "fixture's self-carried digests after re-record: legacy_panel 47e42230a8f7256b4ae9a78d4ff628d3 "
     "(== the post-activation legacy digest card t_42df17c2 recorded in row L1-11M notes), "
     "full_panel f97ff8ad2507f4d69a0e6e57406c2de1; tools/probe file and PANEL list byte-unchanged."),
    ("%s/out/PROBE_AFTER_RERECORD.log:1 the run that recorded the fixture and the digests; "
     "tests/fixtures/tool_panel_baseline.json:1 the self-carried provenance block"
     % COMMON_MIRROR),
    ("Impact list per file: changed = tests/fixtures/tool_panel_baseline.json only (this row); "
     "unchanged = tests/probe_tool_panel_identity.py, the PANEL args, the README signatures; the "
     "subtype_v14 body fix of this wave changed 0 of the 12 call digests (measured: the digests "
     "before and after the body fix are identical to the byte)."),
    ("%s/out/DUMP_HEAD.json:1 per_call_md5 (post-body-fix tree, 12/12, 0 refused) vs the digests "
     "printed by %s/out/PROBE_AFTER_RERECORD.log:1" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Regression gate: `tests/probe_tool_panel_identity.py --baseline "
     "tests/fixtures/tool_panel_baseline.json` exits 0 (IDENTITY PASS) in the working tree and the "
     "clean-clone gate run of this commit; the full chain `bash tests/run_gates.sh` ends gates=8 "
     "failed=0."),
    ("%s/out/PROBE_AFTER_RERECORD.log:1 rc=0; %s/out/CLONE_REPO_GATES.log:1 the clean-clone chain "
     "summary" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("sha evidence taken fresh: fixture sha256 before ce6416126252663ff8be794fe985500a284876c3d15b2"
     "420359656c1bb4afd87 (the pre-re-record bytes, == fixture as recorded at 435bb92); fixture "
     "after-sha carried in the commit's git diff; both dumps' 12 per-call md5s inside "
     "%s/out/DUMP_435bb92.json and DUMP_HEAD.json." % COMMON_MIRROR),
    ("%s/out/DUMP_435bb92.json:1; %s/out/DUMP_HEAD.json:1; "
     "%s/pre_images/tool_panel_baseline.json.pre_rerecord:1" % (COMMON_MIRROR, COMMON_MIRROR, COMMON_MIRROR)),
    ("Rollback identity: restore the PRE fixture bytes (sha-verified); the probe then fails again "
     "with IDENTITY FAIL on exactly the two attributed calls - the recorded, reproducible defect "
     "state. No other file participates in this row."),
    ("%s/pre_images/tool_panel_baseline.json.pre_rerecord:1; %s/out/R1_REPRODUCE.json:1 the rc=1 "
     "state the rollback reproduces" % (COMMON_MIRROR, COMMON_MIRROR)),
    ("Differential reading, negative column included: the re-record is NOT a whitewash - the two "
     "moved calls keep moving their provenance field today whenever a new default-route library "
     "activates; the device's green state now names the single commit-level cause (onfibro_v13 "
     "activation, t_42df17c2) and records that the 2026-10-22 registrations (subtype_v14 t_7509a1a2, "
     "holefill_v12 t_be11fd4a, cl56_v15 t_fabddb85) contribute NOTHING to either moved call (those "
     "libraries are explicit-route-only and absent from provenance.files at both commits)."),
    ("%s/out/D2_FIELD_DIFF.json:1 provenance.files library sets at both commits (435bb92 7 libs, "
     "HEAD 8 libs, delta = onfibro_v13 only)" % COMMON_MIRROR),
    ("Ledger registration: this row plus CHG-20261024-KBREACH-SUBTYPE14-BODY in "
     "docs/CHANGE_CONTROL_G6_INSTANCE.tsv; docs/W3_MANIFEST.sha256 re-frozen last."),
    ("docs/CHANGE_CONTROL_G6_INSTANCE.tsv:1 the two CHG-20261024-KBREACH rows; "
     "docs/W3_MANIFEST.sha256:1 re-frozen last"),
]

g6_lines = open(G6, encoding="utf-8").read().split("\n")
existing = "\n".join(g6_lines)
assert "CHG-20261024-KBREACH-SUBTYPE14-BODY" not in existing, "row already present (idempotency stop)"
with open(G6, "w", encoding="utf-8") as f:
    f.write("\n".join(g6_lines) + "\n" + "\t".join(row1) + "\n" + "\t".join(row2) + "\n")

doc = {"probe": "registry_update.py",
       "L1-31": {"sha_before": sha_before, "sha_after": sha_now,
                 "bytes": [bytes_before, bytes_now], "mtime": [mtime_before, mtime_now]},
       "G6_rows_added": 2}
with open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps(doc, ensure_ascii=False, indent=1))
