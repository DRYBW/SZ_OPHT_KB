#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3 -- the default face: the kill switch restores the pre-flip default byte-for-byte, and the delta
the activation introduces is counted and attributed (card clauses A3 + A4, BRIIEF items 3 and 5).

Method (measurement, not assertion). Arms are replayed **at the same absolute path**, so every
path-carrying field of a response resolves identically and the only variables are the file's bytes and
the switch value:

  PARENT  the parent commit's `mcp_server/eyekb_core.py`, swapped IN PLACE, default route
          (`library="all"`, no `tissue` argument, no switch set) -- the shipped pre-flip face;
  KILL    the flipped core in place, `EYEKB_ACT_HOLEFILL=0`  -- must equal PARENT byte-for-byte;
  FLIP    the flipped core in place, switch unset             -- the activated face.

Three modes per arm: `clusters` (the 721 recorded cluster windows), `battery` (page listing +
`cell_type` mode over the 76 labelled classes x 3 species arguments) and `explicit` (every named
library, so a registration that is missing from the loader is visible as a refusal).

Pass `--pass final` AFTER a NO-GO revert: the activation is gone from the tree, so the arms collapse
to PARENT vs FINAL (the reverted tree), and the script writes `out/FINAL_STATE.json` proving that the
state left on disk reproduces the parent commit's default route byte-for-byte while the restored
registration is reachable by name.

Readings:
  * raw and canonical per-query md5 (raw = the response bytes in field order; canonical =
    sort_keys=True, the predecessor wave's reading, so the numbers are comparable);
  * the exact count of queries whose raw bytes moved (PARENT -> FLIP), with each moved query's
    before/after answer, its n_shared, its candidate count and whether the library's entry is present
    -- every moved query is attributed or reported as unexplained;
  * the repository's own tool-panel identity probe and the wave's standing default-face device
    `golden_721.py`, run under each arm.

The swap is guarded: the core's bytes are snapshotted first and restored in a `finally`, with the
sha256 re-verified afterwards. Writes out/DEFAULT_FACE.json (or out/FINAL_STATE.json).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
OUT = os.path.join(WAVE, "out")
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PROBE = os.path.join(REPO, "tests", "probe_tool_panel_identity.py")
AUDIT_DIR = os.path.join(HERE, "netaudit")
GOLDEN = "/mnt/D/EyeKB/plans/holefill_v12_20261021/golden_721.py"
PY = "/usr/bin/python3"
PROBE_PY = "/home/ubuntu/training-venv/bin/python3"
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_HOLEFILL", "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD",
            "EYEKB_S0_ENFORCE", "EYEKB_FALLBACK_WIDEN", "EYEKB_FALLBACK_WIDEN_DENY_TISSUES",
            "EYEKB_CL_KEY", "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")
LIB_BASENAME = "markers_v12_holefill_increment.json"
REGISTRATION_ENTRY = '"holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"'
_LIB_CLASSES = None


def lib_classes():
    """The library's own class names (read from I4), needed because its entries are emitted under the
    Cell Ontology label with no `holefill_v12::` prefix: their names collide with no shipped class, so
    they appear as ordinary canonical classes. Keying on the prefix mislabelled library takeovers --
    caught by `diag_top1_moves.py` before this card's ruling was written."""
    global _LIB_CLASSES
    if _LIB_CLASSES is None:
        inc = json.load(open(os.path.join(REPO, "kb", "markers",
                                          "markers_v12_holefill_increment.json")))
        _LIB_CLASSES = {str(k).casefold() for k in (inc.get("markers") or {})}
    return _LIB_CLASSES


def won_by_the_library(row):
    if str(row.get("top_lib") or "") == LIB_BASENAME:
        return True
    top = str(row.get("top") or "")
    if top.startswith("holefill_v12::"):
        return True
    return top.split("::")[-1].strip().casefold() in lib_classes()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(cmd, env=None, cwd=REPO):
    e = dict(os.environ)
    for k in SWITCHES:
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    # PINNED PYTHONPATH: every child here must import the REPOSITORY's dependencies from its own
    # interpreter; the worker sandbox can export a PYTHONPATH that shadows `mcp` and turns the
    # tool-panel probe into an inconclusive "cannot be driven" instead of a verdict. Only the audit
    # hook's own directory is inherited.
    e["PYTHONPATH"] = AUDIT_DIR
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd)


def drop_pyc():
    p = os.path.join(REPO, "mcp_server", "__pycache__")
    if os.path.isdir(p):
        for fn in os.listdir(p):
            if fn.startswith("eyekb_core"):
                os.remove(os.path.join(p, fn))


def replay(fmode, arm, tmp):
    p = sh([PY, os.path.join(HERE, "l3b_replay_route.py"), fmode,
            os.path.join(tmp, "%s_%s.json" % (arm, fmode))],
           env=ARMS[arm]["env"], cwd=WAVE)
    if p.returncode != 0:
        raise SystemExit("replay %s/%s failed: %s" % (arm, fmode, p.stderr[-3000:]))
    return json.load(open(os.path.join(tmp, "%s_%s.json" % (arm, fmode))))


def clean_chatter(text, tail=4000):
    """Drop environment chatter (progress bars, loader notes) so the recorded readout is
    reproducible: an earlier wave measured that the raw tail carried per-run throughput figures and
    made every artefact byte-differ after an identical re-run."""
    noise = ("it/s", "%|", "Batches:", "Loading weights", "Loading SentenceTransformer",
             "JAX version", "INFO ", "DB: ")
    keep = [l for l in (text or "").splitlines() if not any(n in l for n in noise)]
    return "\n".join(keep)[-tail:]


def probe(arm, baseline=False):
    cmd = [PROBE_PY, PROBE]
    if baseline:
        cmd += ["--baseline", os.path.join(REPO, "tests", "fixtures", "tool_panel_baseline.json")]
    p = sh(cmd, env=ARMS[arm]["env"])
    digests = {}
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.startswith('"legacy_panel"') or line.startswith('"full_panel"'):
            k, v = line.split(":", 1)
            digests[k.strip().strip('"')] = v.strip().strip(',').strip('"')
    return {"rc": p.returncode, "digests": digests,
            "stdout_tail": clean_chatter(p.stdout, tail=1500),
            "stdout_full": clean_chatter(p.stdout, tail=4000),
            "stderr_tail": clean_chatter(p.stderr, tail=500)}


def golden(arm, tmp):
    out = os.path.join(tmp, "golden_%s.json" % arm)
    p = sh([PY, GOLDEN, out], env=ARMS[arm]["env"])
    d = json.load(open(out)) if os.path.exists(out) else None
    return {"rc": p.returncode, "stats": (d or {}).get("stats"), "stderr_tail": p.stderr[-400:]}


ARMS = {}


def compare(a, b, fmode):
    diff = sorted(k for k in a["rows"] if a["rows"][k]["raw_md5"] != b["rows"][k]["raw_md5"])
    diff_c = sorted(k for k in a["rows"] if a["rows"][k]["canon_md5"] != b["rows"][k]["canon_md5"])
    return {"n_queries": a["n"], "identical_raw": not diff, "identical_canonical": not diff_c,
            "n_differing_raw": len(diff), "n_differing_canonical": len(diff_c),
            "differing": diff[:20],
            "raw_combined_md5_a": a["raw_combined_md5"], "raw_combined_md5_b": b["raw_combined_md5"],
            "canon_combined_md5_a": a["canon_combined_md5"],
            "canon_combined_md5_b": b["canon_combined_md5"]}


def main():
    final_pass = "--pass" in sys.argv and "final" in sys.argv
    tag = "final" if final_pass else "flip"
    out_path = os.path.join(OUT, "FINAL_STATE.json" if final_pass else "DEFAULT_FACE.json")
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    src = cur.decode("utf-8")
    activation_present = "_holefill_act_enabled" in src
    ref = json.load(open(os.path.join(OUT, "PREIMAGE.json")))["base_commit"]
    parent = sh(["git", "-C", REPO, "show", "%s:mcp_server/eyekb_core.py" % ref])
    if parent.returncode != 0:
        raise SystemExit("cannot read the pre-flip commit's core: %s" % parent.stderr)
    parent_bytes = parent.stdout.encode()
    pre = open(os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_activation"), "rb").read()
    sys.path.insert(0, HERE)
    import l0b_restore_registration as R        # the restoration's own anchors, reused not retyped
    parent_src = parent_bytes.decode("utf-8")
    pre_src = pre.decode("utf-8")
    doc = {"probe": "l3_default_face.py", "pass": tag, "core_path": "mcp_server/eyekb_core.py",
           "pre_flip_reference_commit": ref,
           "pre_flip_reference_note": ("pinned to the commit recorded by this card's pre-image, not to "
                                       "HEAD, so a post-commit re-run still compares the shipped "
                                       "default against the pre-flip default"),
           "child_env_policy": ("PYTHONPATH pinned to the audit-hook directory only; "
                                "PYTHONDONTWRITEBYTECODE=1; PYTHONHASHSEED=0; every service switch "
                                "cleared before the arm's own value is applied"),
           "activation_present_in_the_tree": activation_present,
           "current_core_sha256": cur_sha, "current_core_bytes": len(cur),
           "current_core_equals_pre_image": cur_sha == sha(pre),
           "parent_core_sha256": sha(parent_bytes), "preimage_core_sha256": sha(pre),
           "parent_core_equals_kept_preimage": sha(parent_bytes) == sha(pre),
           "pre_image_equals_parent_plus_restoration": (pre_src.replace(R.INSERT, R.ANCHOR)
                                                        == parent_src),
           "pre_image_relationship_note": (
               "the kept pre-image is the PRE-ACTIVATION state, which already carries this card's "
               "l0b restoration of the dropped `holefill_v12` registration; undoing exactly that "
               "restoration must reproduce the parent commit's blob (checked above), and the "
               "restoration's own neutrality on the default route is proven in out/RESTORE.json"),
           "registration_entry_present": REGISTRATION_ENTRY in src}
    if activation_present:
        ARMS.update({"PARENT": {"env": {}, "core": "parent"},
                     "KILL": {"env": {"EYEKB_ACT_HOLEFILL": "0"}, "core": "current"},
                     "FLIP": {"env": {}, "core": "current"}})
    else:
        ARMS.update({"PARENT": {"env": {}, "core": "parent"},
                     "FINAL": {"env": {}, "core": "current"}})

    arms = {}
    try:
        with open(CORE, "wb") as f:
            f.write(parent_bytes)
        drop_pyc()
        doc["parent_core_verified_in_place"] = (sha(open(CORE, "rb").read()) == sha(parent_bytes))
        for fmode in ("clusters", "battery", "explicit"):
            arms["PARENT_" + fmode] = replay(fmode, "PARENT", tmp)
        doc["parent_probe"] = probe("PARENT")
        doc["parent_probe_with_baseline"] = probe("PARENT", baseline=True)
        doc["parent_golden"] = golden("PARENT", tmp)
    finally:
        with open(CORE, "wb") as f:
            f.write(cur)
        drop_pyc()
        doc["restored_core_sha256"] = sha(open(CORE, "rb").read())
        doc["restored_matches_snapshot"] = (doc["restored_core_sha256"] == cur_sha)
    doc["current_core_verified_in_place"] = doc["restored_matches_snapshot"]

    for arm in [a for a in ARMS if a != "PARENT"]:
        for fmode in ("clusters", "battery", "explicit"):
            arms[arm + "_" + fmode] = replay(fmode, arm, tmp)
        doc[arm.lower() + "_probe"] = probe(arm)
        doc[arm.lower() + "_probe_with_baseline"] = probe(arm, baseline=True)
    if activation_present:
        doc["flip_golden"] = golden("FLIP", tmp)
    else:
        doc["final_golden"] = golden("FINAL", tmp)
    doc["core_sha_seen_by_each_arm"] = {k: v["core_sha256"] for k, v in arms.items()}

    # ---- clause (d): the OFF state (or the reverted tree) reproduces the parent commit
    kill_cmp = {}
    for fmode in ("clusters", "battery"):
        a = arms["PARENT_" + fmode]
        b = arms["KILL_" + fmode] if activation_present else arms["FINAL_" + fmode]
        kill_cmp[fmode] = compare(a, b, fmode)
    doc["preflip_byte_identity"] = kill_cmp

    # ---- the activation's own delta, counted and attributed
    delta = {}
    for fmode in ("clusters", "battery", "explicit"):
        a = arms["PARENT_" + fmode]
        b = arms["FLIP_" + fmode] if activation_present else arms["FINAL_" + fmode]
        moved = []
        for k in a["rows"]:
            ra, rb = a["rows"][k], b["rows"][k]
            if ra["raw_md5"] == rb["raw_md5"]:
                continue
            ranking_moved = (ra.get("top"), ra.get("n_shared"), ra.get("n_ranked")) != \
                            (rb.get("top"), rb.get("n_shared"), rb.get("n_ranked"))
            item = {"query": k, "before_top": ra.get("top"), "after_top": rb.get("top"),
                    "before_n_shared": ra.get("n_shared"), "after_n_shared": rb.get("n_shared"),
                    "before_n_ranked": ra.get("n_ranked"), "after_n_ranked": rb.get("n_ranked"),
                    "ranking_moved": ranking_moved,
                    "lib_present_after": rb.get("lib_present")}
            if not ranking_moved:
                item["attribution"] = ("disclosure-field-only-naming-the-library"
                                       if rb.get("lib_present") else "disclosure-field-only")
            elif not item["query"].startswith("lib:") and rb.get("top") != ra.get("top"):
                # the top-1 answer itself changed; whether the library caused it is a separate
                # question, answered by which class won -- never absorbed into "moved by the library"
                item["attribution"] = ("top1-changed-to-a-library-entry"
                                       if won_by_the_library(rb)
                                       else "top1-changed-to-another-class")
            elif rb.get("lib_present"):
                item["attribution"] = "library-in-candidate-list-top1-same"
            elif item["query"].startswith("lib:"):
                item["attribution"] = "explicit-route-row-moved"
            else:
                item["attribution"] = "unexplained"
            moved.append(item)
        delta[fmode] = {"n_queries": a["n"], "n_moved_raw": len(moved),
                        "n_ranking_moved": sum(1 for m in moved if m["ranking_moved"]),
                        "n_byte_moved_ranking_unchanged": sum(1 for m in moved
                                                              if not m["ranking_moved"]),
                        "n_unexplained": sum(1 for m in moved
                                             if m["attribution"] == "unexplained"),
                        "attribution_census": {x: sum(1 for m in moved if m["attribution"] == x)
                                               for x in sorted({m["attribution"] for m in moved})},
                        "moved": moved,
                        "raw_combined_md5_before": a["raw_combined_md5"],
                        "raw_combined_md5_after": b["raw_combined_md5"],
                        "canon_combined_md5_before": a["canon_combined_md5"],
                        "canon_combined_md5_after": b["canon_combined_md5"]}
    doc["activation_delta"] = delta

    try:
        l2 = json.load(open(os.path.join(OUT, "FLIP_MEASUREMENT.json")))
        declared_keys = {"%s|%s" % (m["vol"], m["cluster"]) for m in l2["moved_clusters"]}
        default_keys = {m["query"] for m in delta["clusters"]["moved"] if m["ranking_moved"]}
        doc["moved_set_vs_declared_tissue_route"] = {
            "default_route_ranking_moved": len(default_keys),
            "declared_tissue_route_moved": len(declared_keys),
            "only_default_route": sorted(default_keys - declared_keys)[:40],
            "only_declared_tissue_route": sorted(declared_keys - default_keys)[:40],
            "in_both": len(default_keys & declared_keys)}
    except Exception as e:                                   # noqa: BLE001
        doc["moved_set_vs_declared_tissue_route"] = {"error": repr(e)}

    # ---- tool-panel probes
    lp = doc["parent_probe"]["digests"]
    oa = "flip" if activation_present else "final"
    doc["tool_panel"] = {
        "probe_file": "tests/probe_tool_panel_identity.py",
        "probe_file_byte_unchanged_vs_parent_commit": (
            sha(open(PROBE, "rb").read())
            == sha(sh(["git", "-C", REPO, "show", "%s:tests/probe_tool_panel_identity.py"
                       % ref]).stdout.encode())),
        "PARENT": {"rc": doc["parent_probe"]["rc"], "digests": lp},
        "OTHER_ARM": {"name": oa.upper(), "rc": doc[oa + "_probe"]["rc"],
                      "digests": doc[oa + "_probe"]["digests"]},
        "recorded_baseline": json.load(open(os.path.join(REPO, "tests", "fixtures",
                                                         "tool_panel_baseline.json")))}
    tb = doc["tool_panel"]

    def diff_calls(key):
        lines = []
        for ln in (doc[key]["stdout_full"] if "stdout_full" in doc[key]
                   else doc[key]["stdout_tail"]).splitlines():
            s = ln.strip()
            if s.startswith("different:") or s.startswith("IDENTITY FAIL") or s.startswith("refused:"):
                lines.append(s)
        return lines
    tb["per_call_attribution"] = {
        "PARENT": {"rc": doc["parent_probe_with_baseline"]["rc"],
                   "report": diff_calls("parent_probe_with_baseline")},
        "OTHER_ARM": {"name": oa.upper(), "rc": doc[oa + "_probe_with_baseline"]["rc"],
                      "report": diff_calls(oa + "_probe_with_baseline")},
        "baseline_re_recorded": False,
        "reason_not_re_recorded": ("the card asks for a moved legacy panel to be reported, not "
                                   "absorbed; re-recording the baseline is the owner's decision, so "
                                   "the fixture is left untouched and the probe's state at this "
                                   "commit is shown as measured")}
    tb["legacy_panel_unchanged_parent_vs_other"] = (
        lp.get("legacy_panel") == doc[oa + "_probe"]["digests"].get("legacy_panel"))
    tb["full_panel_unchanged_parent_vs_other"] = (
        lp.get("full_panel") == doc[oa + "_probe"]["digests"].get("full_panel"))
    tb["legacy_panel_matches_recorded_baseline"] = (
        lp.get("legacy_panel") == tb["recorded_baseline"]["legacy_panel"])
    # The recorded fixture (e8e6c263...) predates the `onfibro_v13` activation, which reported that it
    # moved it and deliberately left the fixture un-re-recorded. So the PARENT arm of THIS card is
    # expected to disagree with the fixture already; what must be shown is that the disagreement is
    # inherited rather than this card's. Evidence: the PARENT digests equal the digests the preceding
    # activation wave recorded for its own activated face.
    try:
        prev = json.load(open(os.path.join(REPO, "docs", "plans", "activate_onfibro_20261022",
                                           "out", "DEFAULT_FACE.json")))
        prev_digests = prev["flip_probe"]["digests"]
    except Exception as e:                                   # noqa: BLE001
        prev, prev_digests = None, {"error": repr(e)}
    tb["inherited_panel_staleness"] = {
        "recorded_fixture_legacy_panel": tb["recorded_baseline"]["legacy_panel"],
        "parent_arm_legacy_panel": lp.get("legacy_panel"),
        "predecessor_activation_wave_activated_face": prev_digests,
        "parent_arm_equals_predecessor_activated_face":
            prev_digests == lp if prev_digests and "error" not in prev_digests else None,
        "reading": ("the fixture is already stale at this card's parent commit for the reason the "
                    "predecessor activation recorded (it moved the panel and declined to "
                    "re-record); this card's own compatibility item is the FURTHER move below")}
    tb["parent_panel_equals_predecessor_activated_face"] = (
        tb["inherited_panel_staleness"]["parent_arm_equals_predecessor_activated_face"])
    tb["compatibility_contract_item"] = (
        None if tb["legacy_panel_unchanged_parent_vs_other"] else
        "the legacy five-tool panel MOVED (parent %s -> %s %s)" % (
            lp.get("legacy_panel"), oa.upper(), doc[oa + "_probe"]["digests"].get("legacy_panel")))

    pg = doc["parent_golden"]
    og = doc["flip_golden"] if activation_present else doc["final_golden"]
    doc["golden_721"] = {"device": GOLDEN,
                         "note": ("the standing default-face replay device: re-runs each recorded "
                                  "cluster and compares the ranking with the 2026-10-18 recording"),
                         "PARENT": {"rc": pg["rc"], "stats": pg["stats"]},
                         "OTHER_ARM": {"name": oa.upper(), "rc": og["rc"], "stats": og["stats"]}}
    doc["golden_parent_equals_other_arm"] = (pg["stats"] == og["stats"])

    parent_report_ok = (tb["per_call_attribution"]["PARENT"]["report"] == []
                        or tb.get("parent_panel_equals_predecessor_activated_face") is True)
    ok = (doc["pre_image_equals_parent_plus_restoration"] and doc["restored_matches_snapshot"]
          and doc["parent_core_verified_in_place"] and doc["current_core_verified_in_place"]
          and doc["registration_entry_present"]
          and all(v["identical_raw"] and v["identical_canonical"] for v in kill_cmp.values())
          and all(v["n_unexplained"] == 0 for v in delta.values())
          and (doc["golden_parent_equals_other_arm"] if final_pass else True)
          and doc["tool_panel"]["probe_file_byte_unchanged_vs_parent_commit"]
          and doc["parent_probe"]["rc"] == 0
          and doc[oa + "_probe"]["rc"] == 0
          and parent_report_ok
          and (tb["legacy_panel_unchanged_parent_vs_other"]
               or tb["compatibility_contract_item"] is not None))
    doc["parent_panel_report_is_inherited_or_clean"] = parent_report_ok
    doc["verdict"] = "PASS" if ok else "FAIL"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("pass                 :", tag, "| activation present in tree:", activation_present)
    print("parent core == kept pre-image:", doc["parent_core_equals_kept_preimage"],
          "| restored == snapshot:", doc["restored_matches_snapshot"],
          "| current == pre-image:", doc["current_core_equals_pre_image"])
    for fmode, v in kill_cmp.items():
        print("   PARENT vs %-5s %-8s n=%d raw-identical=%s canon-identical=%s (differing raw=%d)"
              % ("KILL" if activation_present else "FINAL", fmode, v["n_queries"],
                 v["identical_raw"], v["identical_canonical"], v["n_differing_raw"]))
    for fmode, v in delta.items():
        print("   PARENT -> %-5s %-8s moved_raw=%d/%d  ranking_moved=%d  disclosure-only=%d  "
              "unexplained=%d" % (oa.upper(), fmode, v["n_moved_raw"], v["n_queries"],
                                  v["n_ranking_moved"], v["n_byte_moved_ranking_unchanged"],
                                  v["n_unexplained"]))
        print("        attribution census:", v["attribution_census"])
    print("   compatibility item:", tb["compatibility_contract_item"])
    print("   legacy panel: parent=%s other=%s unchanged=%s (baseline %s)"
          % (lp.get("legacy_panel"), doc[oa + "_probe"]["digests"].get("legacy_panel"),
             tb["legacy_panel_unchanged_parent_vs_other"],
             tb["recorded_baseline"]["legacy_panel"]))
    print("   golden_721 PARENT:", json.dumps(pg["stats"]))
    print("   golden_721 %-5s :" % oa.upper(), json.dumps(og["stats"]))
    print("   l3 verdict          :", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())