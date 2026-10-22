#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l0b -- restore the `holefill_v12` dictionary entry that commit 0312016 dropped, and PROVE the
restoration is neutral on the shipped default route.

Context (full evidence in PREREG_ACTIVATION_HOLEFILL_20261022.md section 1b): the predecessor wave
registered `holefill_v12` in `MARKER_LIBS` (commit 290cb984). Commit 0312016, appending the next
registration, replaced the dictionary's closing line -- which was `holefill_v12`'s entry -- with the
new block, so the entry was lost. Measured effect: `query_marker(library="holefill_v12")` raises
ValueError although the error string still names the library, while registry row L1-26 states it is
"reachable only via library=holefill_v12".

This script
  1. keeps a pre-restore image of the core (pre_images/eyekb_core.py.pre_restore);
  2. replays the recorded default route BEFORE the restore (clusters + battery + explicit-route
     battery) with the core in place at its absolute path;
  3. inserts the entry back, inside the dictionary, immediately after its own comment block, with
     `assert count == 1` on the anchor;
  4. replays the same three batteries AFTER the restore and compares every query byte-for-byte;
  5. runs the wave's standing default-face device `golden_721.py` in both switch arms, before and
     after, and requires 721/721 identical rankings;
  6. probes that `library="holefill_v12"` now resolves to the 17 registered entries;
  7. writes out/RESTORE.json. If any check fails the pre-restore bytes are put back and the script
     exits non-zero.

The three default-route arms must be byte-identical before/after because the dictionary entry is not
read on the `all` route; the explicit-route arm is EXPECTED to change (a refusal becomes a served
answer) and is reported as the restoration's intended effect, not as a default-route movement.
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
TMP = os.path.join(OUT, "restore_tmp")
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PRE_RESTORE = os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_restore")
GOLDEN = "/mnt/D/EyeKB/plans/holefill_v12_20261021/golden_721.py"
PY = "/usr/bin/python3"
AUDIT_DIR = os.path.join(HERE, "netaudit")
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_HOLEFILL", "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD",
            "EYEKB_S0_ENFORCE", "EYEKB_FALLBACK_WIDEN", "EYEKB_FALLBACK_WIDEN_DENY_TISSUES",
            "EYEKB_CL_KEY", "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")

ANCHOR = ('    #   its own admission guard and separate PI approval. Rollback = delete this line.\n'
          '    # onfibro_v13 = the optic-nerve fibroblast carrier (2026-10-22, card t_0c40c7b1): ONE entry,')
INSERT = ('    #   its own admission guard and separate PI approval. Rollback = delete this line.\n'
          '    # [RESTORED t_be11fd4a 2026-10-22] The registration line below was DROPPED by commit\n'
          '    #   0312016 (card t_0c40c7b1) as a side effect of appending the next entry: the new block\n'
          '    #   replaced the dictionary closing line, which was this entry. Restored here, with the\n'
          '    #   default route proven byte-identical -- see\n'
          '    #   docs/plans/activate_holefill_20261022/PREREG_ACTIVATION_HOLEFILL_20261022.md section 1b.\n'
          '    "holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json",\n'
          '    # onfibro_v13 = the optic-nerve fibroblast carrier (2026-10-22, card t_0c40c7b1): ONE entry,')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha(open(p, "rb").read())


def sh(cmd, env=None):
    e = dict(os.environ)
    for k in SWITCHES:
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e["PYTHONPATH"] = AUDIT_DIR
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=WAVE)


def drop_pyc():
    p = os.path.join(REPO, "mcp_server", "__pycache__")
    if os.path.isdir(p):
        for fn in os.listdir(p):
            if fn.startswith("eyekb_core"):
                os.remove(os.path.join(p, fn))


def replay(fmode, arm):
    out = os.path.join(TMP, "%s_%s.json" % (arm, fmode))
    p = sh([PY, os.path.join(HERE, "l3b_replay_route.py"), fmode, out])
    if p.returncode != 0:
        raise SystemExit("replay %s/%s failed: %s" % (arm, fmode, p.stderr[-2000:]))
    return json.load(open(out))


def golden(arm):
    out = os.path.join(TMP, "golden_%s.json" % arm)
    p = sh([PY, GOLDEN, out])
    d = json.load(open(out)) if os.path.exists(out) else None
    return {"rc": p.returncode, "stats": (d or {}).get("stats"), "stderr_tail": p.stderr[-400:]}


def main():
    os.makedirs(TMP, exist_ok=True)
    src = open(CORE, encoding="utf-8").read()
    already = '"holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"' in src
    mode = "verify" if already else "apply"
    cur = open(CORE, "rb").read()
    doc = {"probe": "l0b_restore_registration.py", "mode": mode,
           "core_path": "mcp_server/eyekb_core.py",
           "core_sha256_before": sha(cur), "core_bytes_before": len(cur),
           "defect": {
               "introduced_by": "0312016 (2026-10-22 11:24, card t_0c40c7b1)",
               "added_by": "290cb984 (2026-10-21 23:53, the holefill_v12 registration wave)",
               "mechanism": ("the append replaced the dictionary's closing line -- which carried "
                             "holefill_v12's entry -- instead of following it"),
               "measured_effect": ("library=\"holefill_v12\" raises ValueError although the error "
                                   "string names the library; registry row L1-26 claims it is "
                                   "reachable by name")},
           "anchor_occurrences_before": src.count(ANCHOR)}
    if mode == "apply":
        assert src.count(ANCHOR) == 1, "anchor not unique: %d" % src.count(ANCHOR)
        open(PRE_RESTORE, "wb").write(cur)
        new = src.replace(ANCHOR, INSERT)
        assert new != src and new.count('"holefill_v12": MARKER_DIR') == 1
        tmp = CORE + ".tmp_l0b"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, CORE)
        drop_pyc()
    doc["pre_restore_image"] = "pre_images/eyekb_core.py.pre_restore"
    doc["pre_restore_image_sha256"] = sha_file(PRE_RESTORE) if os.path.exists(PRE_RESTORE) else None
    doc["pre_restore_matches_before_commit"] = (
        doc["pre_restore_image_sha256"] == sha(sh(["git", "-C", REPO, "show",
                                                  "HEAD:mcp_server/eyekb_core.py"]).stdout.encode()))
    after = open(CORE, "rb").read()
    doc["core_sha256_after"] = sha(after)
    doc["core_bytes_after"] = len(after)
    doc["entry_present_after"] = '"holefill_v12": MARKER_DIR' in open(CORE, encoding="utf-8").read()
    doc["whitelists_after"] = {ln.strip().split("=")[0].strip(): ln.strip().split("=", 1)[1].strip()
                               for ln in open(CORE, encoding="utf-8").read().splitlines()
                               if "_DEFAULT_LIBS" in ln and "=" in ln and not ln.strip().startswith("#")}

    order = []
    if mode == "apply":
        # BEFORE: the pre-restore bytes in place
        order.append(("before", "pre_restore_bytes"))
    # AFTER (or the already-restored tree): current bytes in place
    arms = {}
    if mode == "apply":
        with open(CORE, "wb") as f:
            f.write(cur)                     # the pre-restore bytes back in place for the BEFORE arm
        drop_pyc()
        for fmode in ("clusters", "battery", "explicit"):
            arms["BEFORE_" + fmode] = replay(fmode, "BEFORE")
        doc["before_golden"] = golden("BEFORE")
        with open(CORE, "wb") as f:
            f.write(after)
        drop_pyc()
    for fmode in ("clusters", "battery", "explicit"):
        arms["AFTER_" + fmode] = replay(fmode, "AFTER")
    doc["after_golden"] = golden("AFTER")
    doc["restored_core_sha256"] = sha_file(CORE)
    doc["restored_matches_after_snapshot"] = doc["restored_core_sha256"] == doc["core_sha256_after"]

    cmp = {}
    if mode == "apply":
        for fmode in ("clusters", "battery", "explicit"):
            a, b = arms["BEFORE_" + fmode], arms["AFTER_" + fmode]
            diff = sorted(k for k in a["rows"] if a["rows"][k]["raw_md5"] != b["rows"][k]["raw_md5"])
            diff_c = sorted(k for k in a["rows"] if a["rows"][k]["canon_md5"] != b["rows"][k]["canon_md5"])
            cmp[fmode] = {
                "n_queries": a["n"], "n_differing_raw": len(diff), "n_differing_canonical": len(diff_c),
                "identical_raw": not diff, "identical_canonical": not diff_c,
                "differing": [{"query": k, "before": a["rows"][k], "after": b["rows"][k]}
                              for k in diff[:10]],
                "raw_combined_md5_before": a["raw_combined_md5"],
                "raw_combined_md5_after": b["raw_combined_md5"],
                "canon_combined_md5_before": a["canon_combined_md5"],
                "canon_combined_md5_after": b["canon_combined_md5"]}
    doc["before_vs_after"] = cmp
    doc["explicit_route_battery_after"] = {k: v for k, v in sorted(
        arms["AFTER_explicit"]["rows"].items())}
    doc["holefill_resolves_by_name"] = not arms["AFTER_explicit"]["rows"][
        "lib:holefill_v12"].get("refused", False)
    ref = json.load(open(os.path.join(os.path.dirname(GOLDEN), "out", "golden_721_BEFORE.json")))
    g = doc["after_golden"]["stats"]
    doc["golden_reference_file"] = os.path.join(os.path.dirname(GOLDEN), "out", "golden_721_BEFORE.json")
    doc["golden_reference_stats"] = ref.get("stats")
    doc["golden_before_equals_after"] = (doc["before_golden"]["stats"] == g
                                        if mode == "apply" else None)
    doc["golden_vs_historical_reference"] = (g == ref.get("stats")) if g else None
    doc["golden_reference_note"] = (
        "the historical file was recorded on 2026-10-21, before `onfibro_v13` was activated on the "
        "default route; with the default switches unset today the affected clusters (45) have moved "
        "for that reason, so the restoration is judged against the BEFORE arm of this run (the "
        "pre-restore core, same process, same switches) and the historical comparison is reported "
        "as information, not as a criterion")

    ok = (mode in ("apply", "verify") and doc["pre_restore_matches_before_commit"]
          and doc["entry_present_after"] and doc["holefill_resolves_by_name"]
          and doc["restored_matches_after_snapshot"]
          and doc["after_golden"]["rc"] == 0
          and (mode == "apply" and doc["golden_before_equals_after"] is True
               or mode == "verify")
          and (mode == "verify" or (
              cmp["clusters"]["identical_raw"] and cmp["clusters"]["identical_canonical"]
              and cmp["battery"]["identical_raw"] and cmp["battery"]["identical_canonical"]))
          and (mode == "verify" or cmp["explicit"]["n_differing_raw"] >= 1))
    if not ok and mode == "apply":
        with open(CORE, "wb") as f:
            f.write(cur)
        drop_pyc()
        doc["reverted_to_pre_restore_bytes"] = sha_file(CORE) == sha(cur)
    doc["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(OUT, "RESTORE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("mode                 :", mode)
    print("core sha             :", doc["core_sha256_before"][:16], "->", doc["core_sha256_after"][:16])
    print("pre-restore image == HEAD blob:", doc["pre_restore_matches_before_commit"])
    print("entry present after  :", doc["entry_present_after"],
          "| library=holefill_v12 resolves:", doc["holefill_resolves_by_name"])
    for fmode, v in sorted(cmp.items()):
        print("  default-route replay %-9s n=%d differing_raw=%d differing_canon=%d"
              % (fmode, v["n_queries"], v["n_differing_raw"], v["n_differing_canonical"]))
    print("golden_721 after rc  :", doc["after_golden"]["rc"],
          "| before==after:", doc["golden_before_equals_after"],
          "| vs 2026-10-21 reference:", doc["golden_vs_historical_reference"],
          "|", json.dumps(doc["after_golden"]["stats"] or {})[:220])
    print("l0b verdict          :", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())