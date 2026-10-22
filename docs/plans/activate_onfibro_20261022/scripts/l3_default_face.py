#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3 -- the default face: the kill switch restores the pre-flip default byte-for-byte, and the
delta the activation itself introduces is counted and attributed (A3 + A4).

Method (measurement, not assertion). Three arms are replayed **at the same absolute path**, so
every path-carrying field of a response resolves identically and the only variables are the file's
bytes and the switch value:

  PARENT  the parent commit's `mcp_server/eyekb_core.py`, swapped IN PLACE, default route
          (`library="all"`, no `tissue` argument, no switch set) -- the shipped pre-flip face;
  KILL    the flipped core in place, `EYEKB_ACT_ONFIBRO=0`   -- must equal PARENT byte-for-byte;
  FLIP    the flipped core in place, switch unset            -- the activated face.

Two modes per arm: `clusters` (the 721 recorded cluster windows) and `battery` (page listing +
`cell_type` mode over the 76 labelled classes x 3 species arguments = 229 calls).

Readings:
  * raw and canonical per-query md5 (raw = the response bytes in field order; canonical =
    sort_keys=True, the predecessor wave's reading, so the numbers are comparable);
  * the exact count of queries whose raw bytes moved (PARENT -> FLIP), with each moved query's
    before/after answer, its n_shared, and whether the carrier entry is present -- every moved query
    is attributed or reported as unexplained;
  * the repository's own tool-panel identity probe run under PARENT / KILL / FLIP cores, plus
    `golden_721.py` (the standing default-face replay device) under PARENT and FLIP.

The swap is guarded: the flipped file's bytes are snapshotted first and restored in a `finally`,
with the sha256 re-verified afterwards. Writes out/DEFAULT_FACE.json.
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
            "EYEKB_ACT_ONFIBRO", "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE",
            "EYEKB_FALLBACK_WIDEN", "EYEKB_FALLBACK_WIDEN_DENY_TISSUES", "EYEKB_CL_KEY",
            "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(cmd, env=None, cwd=REPO):
    e = dict(os.environ)
    for k in SWITCHES:
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    # PINNED PYTHONPATH. Every child here must import the REPOSITORY's dependencies from its own
    # interpreter; the worker sandbox exports a PYTHONPATH that includes another venv's
    # site-packages, which shadows `mcp` and makes the probe report "cannot be driven" instead of a
    # verdict (measured 2026-10-22: the panel returned rc=3 for exactly that reason). Only the audit
    # hook's own directory is inherited, and nothing else.
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
    return {"rc": p.returncode, "digests": digests, "stdout_tail": p.stdout[-1500:],
            "stdout_full": p.stdout[-4000:], "stderr_tail": p.stderr[-500:]}


def golden(arm, tmp):
    out = os.path.join(tmp, "golden_%s.json" % arm)
    p = sh([PY, GOLDEN, out], env=ARMS[arm]["env"])
    d = json.load(open(out)) if os.path.exists(out) else None
    return {"rc": p.returncode, "stats": (d or {}).get("stats"),
            "stderr_tail": p.stderr[-400:]}


ARMS = {}


def main():
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    parent = sh(["git", "-C", REPO, "show", "HEAD:mcp_server/eyekb_core.py"])
    if parent.returncode != 0:
        raise SystemExit("cannot read the parent commit's core: %s" % parent.stderr)
    parent_bytes = parent.stdout.encode()
    pre = open(os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_activation"), "rb").read()
    doc = {"probe": "l3_default_face.py", "core_path": "mcp_server/eyekb_core.py",
           "child_env_policy": ("PYTHONPATH pinned to the audit-hook directory only (the worker "
                                "sandbox exports another venv's site-packages, which shadows `mcp` "
                                "and turns the tool-panel probe into an inconclusive rc=3); "
                                "PYTHONDONTWRITEBYTECODE=1; PYTHONHASHSEED=0; every service switch "
                                "cleared before the arm's own value is applied"),
           "parent_commit": sh(["git", "-C", REPO, "rev-parse", "HEAD"]).stdout.strip(),
           "flipped_core_sha256": cur_sha, "flipped_core_bytes": len(cur),
           "parent_core_sha256": sha(parent_bytes),
           "preimage_core_sha256": sha(pre),
           "parent_core_equals_kept_preimage": sha(parent_bytes) == sha(pre)}
    ARMS.update({
        "PARENT": {"env": {}, "core": "parent"},
        "KILL": {"env": {"EYEKB_ACT_ONFIBRO": "0"}, "core": "flipped"},
        "FLIP": {"env": {}, "core": "flipped"},
    })

    arms = {}
    try:
        # ---- PARENT: the parent commit's bytes in place
        with open(CORE, "wb") as f:
            f.write(parent_bytes)
        drop_pyc()
        doc["parent_core_verified_in_place"] = (sha(open(CORE, "rb").read()) == sha(parent_bytes))
        for fmode in ("clusters", "battery"):
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
    doc["flipped_core_verified_in_place"] = (doc["restored_core_sha256"] == cur_sha)

    for arm in ("KILL", "FLIP"):
        for fmode in ("clusters", "battery"):
            arms[arm + "_" + fmode] = replay(fmode, arm, tmp)
        doc[arm.lower() + "_probe"] = probe(arm)
        doc[arm.lower() + "_probe_with_baseline"] = probe(arm, baseline=True)
    doc["flip_golden"] = golden("FLIP", tmp)
    # the core that actually answered, per arm (the switch is the only other variable)
    doc["core_sha_seen_by_each_arm"] = {
        k: v["core_sha256"] for k, v in arms.items()}

    # ---- A3: the kill switch restores the pre-flip default byte-for-byte
    kill_cmp = {}
    for fmode in ("clusters", "battery"):
        a, b = arms["PARENT_" + fmode], arms["KILL_" + fmode]
        diff = [k for k in a["rows"] if a["rows"][k]["raw_md5"] != b["rows"][k]["raw_md5"]]
        diff_c = [k for k in a["rows"] if a["rows"][k]["canon_md5"] != b["rows"][k]["canon_md5"]]
        kill_cmp[fmode] = {
            "n_queries": a["n"], "identical_raw": not diff, "identical_canonical": not diff_c,
            "n_differing_raw": len(diff), "n_differing_canonical": len(diff_c),
            "differing": diff[:20],
            "raw_combined_md5_parent": a["raw_combined_md5"],
            "raw_combined_md5_kill": b["raw_combined_md5"],
            "canon_combined_md5_parent": a["canon_combined_md5"],
            "canon_combined_md5_kill": b["canon_combined_md5"],
            "switch_value_in_kill_arm": b["act_onfibro"]}
    doc["kill_switch_byte_identity"] = kill_cmp

    # ---- A4: the delta the activation introduces, counted and attributed
    # Two levels are reported separately, because they are different claims:
    #   * RANKING movement   -- the (top-1, n_shared, candidate count) tuple changed;
    #   * byte movement      -- the response bytes changed at all, which includes the disclosure
    #                           fields every response carries (provenance files/conflicts,
    #                           soft-flag notes).  A byte that moved while the ranking did not is
    #                           attributed as `disclosure-field-only`, not silently dropped and not
    #                           called a movement of an answer.
    delta = {}
    for fmode in ("clusters", "battery"):
        a, b = arms["PARENT_" + fmode], arms["FLIP_" + fmode]
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
                    "carrier_present_after": rb.get("carrier_present")}
            if not ranking_moved and rb.get("carrier_present"):
                item["attribution"] = "disclosure-field-only-and-carrier-named"
            elif not ranking_moved:
                item["attribution"] = "disclosure-field-only"
            elif rb.get("carrier_present") and ra.get("top") != rb.get("top"):
                item["attribution"] = "carrier-drives-top1-change"
            elif rb.get("carrier_present"):
                item["attribution"] = "carrier-in-candidate-list-top1-same"
            else:
                item["attribution"] = "unexplained"
            moved.append(item)
        delta[fmode] = {
            "n_queries": a["n"], "n_moved_raw": len(moved),
            "n_ranking_moved": sum(1 for m in moved if m["ranking_moved"]),
            "n_byte_moved_ranking_unchanged": sum(1 for m in moved if not m["ranking_moved"]),
            "n_unexplained": sum(1 for m in moved if m["attribution"] == "unexplained"),
            "attribution_census": {x: sum(1 for m in moved if m["attribution"] == x)
                                   for x in sorted({m["attribution"] for m in moved})},
            "moved": moved,
            "raw_combined_md5_before": a["raw_combined_md5"],
            "raw_combined_md5_after": b["raw_combined_md5"],
            "canon_combined_md5_before": a["canon_combined_md5"],
            "canon_combined_md5_after": b["canon_combined_md5"]}
    doc["activation_delta"] = delta

    # the moved cluster set (ranking level) vs the movement measured through the declared-tissue
    # route (l2)
    try:
        l2 = json.load(open(os.path.join(OUT, "FLIP_MEASUREMENT.json")))
        declared_keys = {"%s|%s" % (m["vol"], m["cluster"]) for m in l2["moved_clusters"]}
        default_keys = {m["query"] for m in delta["clusters"]["moved"] if m["ranking_moved"]}
        doc["moved_set_vs_declared_tissue_route"] = {
            "default_route_ranking_moved": len(default_keys),
            "declared_tissue_route_moved": len(declared_keys),
            "only_default_route": sorted(default_keys - declared_keys)[:40],
            "only_declared_tissue_route": sorted(declared_keys - default_keys)[:40],
            "in_both": len(default_keys & declared_keys),
            "note": ("the two routes differ by construction: the tissue-scope filter only acts when "
                     "the caller declares a tissue, so the default route has no narrowing to undo "
                     "and its ranking delta is the carrier's own movement under the default "
                     "declarations")}
    except Exception as e:                                   # noqa: BLE001
        doc["moved_set_vs_declared_tissue_route"] = {"error": repr(e)}

    # ---- tool-panel probes under the three arms
    lp = doc["parent_probe"]["digests"]
    doc["tool_panel"] = {
        "probe_file": "tests/probe_tool_panel_identity.py",
        "probe_file_byte_unchanged_vs_parent_commit": (
            sha(open(PROBE, "rb").read())
            == sha(sh(["git", "-C", REPO, "show", "HEAD:tests/probe_tool_panel_identity.py"]
                      ).stdout.encode())),
        "PARENT": {"rc": doc["parent_probe"]["rc"], "digests": lp},
        "KILL": {"rc": doc["kill_probe"]["rc"], "digests": doc["kill_probe"]["digests"]},
        "FLIP": {"rc": doc["flip_probe"]["rc"], "digests": doc["flip_probe"]["digests"]},
        "recorded_baseline": json.load(open(os.path.join(REPO, "tests", "fixtures",
                                                         "tool_panel_baseline.json"))),
    }
    tb = doc["tool_panel"]
    # per-call attribution straight from the probe's own report (it prints the differing calls)
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
        "FLIP": {"rc": doc["flip_probe_with_baseline"]["rc"],
                 "report": diff_calls("flip_probe_with_baseline")},
        "KILL": {"rc": doc["kill_probe_with_baseline"]["rc"],
                 "report": diff_calls("kill_probe_with_baseline")},
        "baseline_re_recorded": False,
        "reason_not_re_recorded": (
            "the coordinator's card asks for the movement to be reported explicitly rather than "
            "absorbed; re-recording the baseline is the owner's/coordinator's decision, so the "
            "fixture is left untouched and the probe stays RED at this commit, visibly"),
        "cause": ("the carrier is now a member of the default route, so every response that carries "
                  "the provenance/soft-flag disclosure fields now names its file and its entries. "
                  "The two legacy calls that moved carry those fields; their RANKINGS are unchanged "
                  "(out/FIELD_DIFF.json, per-path diff)"),
    }
    tb["legacy_panel_unchanged_parent_vs_flip"] = (lp.get("legacy_panel")
                                                   == doc["flip_probe"]["digests"].get("legacy_panel"))
    tb["full_panel_unchanged_parent_vs_flip"] = (lp.get("full_panel")
                                                 == doc["flip_probe"]["digests"].get("full_panel"))
    tb["legacy_panel_matches_recorded_baseline"] = (
        lp.get("legacy_panel") == tb["recorded_baseline"]["legacy_panel"])
    tb["compatibility_contract_item"] = (
        None if tb["legacy_panel_unchanged_parent_vs_flip"] else
        "the legacy five-tool panel MOVED (parent %s -> flip %s)" % (
            lp.get("legacy_panel"), doc["flip_probe"]["digests"].get("legacy_panel")))

    pg, fg = doc["parent_golden"], doc["flip_golden"]
    doc["golden_721"] = {
        "device": GOLDEN,
        "note": ("the standing default-face replay device: re-runs each recorded cluster and compares "
                 "the ranking with the 2026-10-18 recording; the OFF arm is the pre-flip reference, "
                 "the ON arm is today's default"),
        "PARENT": {"rc": pg["rc"], "stats": pg["stats"]},
        "FLIP": {"rc": fg["rc"], "stats": fg["stats"]}}

    ok = (doc["parent_core_equals_kept_preimage"] and doc["restored_matches_snapshot"]
          and doc["parent_core_verified_in_place"] and doc["flipped_core_verified_in_place"]
          and all(v["identical_raw"] and v["identical_canonical"] for v in kill_cmp.values())
          and all(v["n_unexplained"] == 0 for v in delta.values())
          and doc["tool_panel"]["probe_file_byte_unchanged_vs_parent_commit"]
          and doc["parent_probe"]["rc"] == 0 and doc["flip_probe"]["rc"] == 0
          # the parent arm must reproduce the recorded panel (no differing calls), and the
          # compatibility item must be present in this artefact if the panel moved
          and tb["per_call_attribution"]["PARENT"]["report"] == []
          and (tb["legacy_panel_unchanged_parent_vs_flip"]
               or tb["compatibility_contract_item"] is not None))
    doc["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(OUT, "DEFAULT_FACE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("   parent core == kept pre-image:", doc["parent_core_equals_kept_preimage"],
          "| restored == snapshot:", doc["restored_matches_snapshot"])
    for fmode, v in kill_cmp.items():
        print("   KILL vs PARENT %-8s n=%d raw-identical=%s canon-identical=%s (differing raw=%d)"
              % (fmode, v["n_queries"], v["identical_raw"], v["identical_canonical"],
                 v["n_differing_raw"]))
    for fmode, v in delta.items():
        print("   PARENT -> FLIP %-8s moved_raw=%d/%d  ranking_moved=%d  disclosure-only=%d  "
              "unexplained=%d" % (fmode, v["n_moved_raw"], v["n_queries"], v["n_ranking_moved"],
                                  v["n_byte_moved_ranking_unchanged"], v["n_unexplained"]))
        print("        attribution census:", v["attribution_census"])
    print("   compatibility item:", tb["compatibility_contract_item"])
    print("   probe report (FLIP):", tb["per_call_attribution"]["FLIP"]["report"],
          "rc", tb["per_call_attribution"]["FLIP"]["rc"])
    print("   legacy panel: parent=%s flip=%s unchanged=%s (baseline %s)"
          % (lp.get("legacy_panel"), doc["flip_probe"]["digests"].get("legacy_panel"),
             tb["legacy_panel_unchanged_parent_vs_flip"],
             tb["recorded_baseline"]["legacy_panel"]))
    print("   full panel : parent=%s flip=%s unchanged=%s"
          % (lp.get("full_panel"), doc["flip_probe"]["digests"].get("full_panel"),
             tb["full_panel_unchanged_parent_vs_flip"]))
    print("   golden_721 PARENT:", json.dumps(pg["stats"]["off"]) if pg["stats"] else None)
    print("   golden_721 FLIP  :", json.dumps(fg["stats"]["off"]) if fg["stats"] else None)
    print("   l3 verdict:", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())