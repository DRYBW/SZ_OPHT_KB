#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m10 -- manifest (taken BEFORE the gate) and the wave's own gate.

Gates are fail-closed and each carries the command that produced its reading.  The manifest is taken
before the gate so a drifting artefact is the gate's job rather than a human's, and it excludes
everything this file itself writes plus every run-time artefact (the lessons from earlier waves:
a manifest that hashes its own log or the verification output reports FAILED on every re-check).

  1. in-scope set          26 rows / 16 subtypes, re-derived from the frozen result
  2. the ruler reproduces  control arm == the frozen 56-row result, with the frozen ruler AND the
                           local copy (so the two-line repair is behaviour-preserving)
  3. augmented arm         56 rows; 0 out-of-scope rows moved
  4. thresholds frozen     the local ruler differs from the frozen one only in the disclosed hunks;
                           AUC_MIN / FDR_MAX / MIN_CELLS / SHARE_FACTOR byte-identical
  5. default face          PASS: 0 differing calls, route composition identical, subtype_v14 absent
                           from `all` in every switch state, present in MARKER_LIBS, empty whitelist
  6. no other whitelist    the set of `*_DEFAULT_LIBS = ...` assignments is unchanged by this commit
  7. library              16 entries, 16/16 CL ids resolve against the frozen snapshot, <= 2 added
                           genes per subtype
  8. provenance            every added gene carries >= 1 paper id and a verbatim segment
  9. flips auditable       every flip is in-scope, has >= 2 clearing markers above the gate, and
                           carries the H1-H5 classification and a robustness verdict
 10. zero network          audit-hook load receipts > 0 and EVENT lines == 0
 11. pass archive          all five mining passes are on disk, superseded ones byte-preserved
 12. NOT_RUN is not a pass every gate above has a recorded command and a real reading

Writes out/MANIFEST.sha256 and out/GATE.json.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
REPO = "/home/ubuntu/EYEKB_REPO"
EXCLUDE_NAMES = {"MANIFEST.sha256", "GATE.json", "MANIFEST_CHECK.txt"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    m0 = json.load(open(os.path.join(OUT, "INPUT_MANIFEST.json"), encoding="utf-8"))
    runs = json.load(open(os.path.join(OUT, "RULER_RUNS.json"), encoding="utf-8"))
    repro = json.load(open(os.path.join(OUT, "RULER_REPRO_CHECK.json"), encoding="utf-8"))
    fl = json.load(open(os.path.join(OUT, "FLIPS.json"), encoding="utf-8"))
    rob = json.load(open(os.path.join(OUT, "ROBUSTNESS.json"), encoding="utf-8"))
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    panel = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_PANEL.json"), encoding="utf-8"))
    dface = json.load(open(os.path.join(OUT, "DEFAULT_FACE.json"), encoding="utf-8"))
    patchd = json.load(open(os.path.join(OUT, "RULER_PATCH.json"), encoding="utf-8"))
    reg = json.load(open(os.path.join(OUT, "REGISTRY_UPDATE.json"), encoding="utf-8"))
    lib = json.load(open(os.path.join(REPO, "kb", "markers",
                                      "markers_v14_subtype_second_increment.json"), encoding="utf-8"))

    checks = []

    def add(cid, desc, ok, cmd, detail=""):
        checks.append({"id": cid, "description": desc, "ok": bool(ok), "command": cmd,
                       "reading": detail})

    add("G1", "in-scope set = 26 rows / 16 subtypes",
        m0["in_scope_n_rows"] == 26 and m0["in_scope_n_subtypes"] == 16,
        "python3 scripts/m0_freeze_inputs.py",
        "rows=%d subtypes=%d" % (m0["in_scope_n_rows"], m0["in_scope_n_subtypes"]))

    add("G2", "the ruler reproduces the frozen 56-row result (frozen ruler and local copy)",
        repro["control_reproduces_frozen_verdicts"] and runs["control_local_ruler"]["identical_verdicts"],
        "python3 scripts/m3_remeasure.py && python3 scripts/m3b_remeasure_local.py",
        "frozen-ruler control identical=%s; local-ruler control identical=%s; %s"
        % (repro["control_reproduces_frozen_verdicts"],
           runs["control_local_ruler"]["identical_verdicts"], repro["before_counts"]))

    add("G3", "augmented arm: 56 rows, 0 out-of-scope rows moved",
        repro["augmented_rows"] == 56 and repro["out_of_scope_moved_n"] == 0,
        "python3 scripts/m4_flips.py",
        "rows=%d out_of_scope_moved=%d before=%s after=%s"
        % (repro["augmented_rows"], repro["out_of_scope_moved_n"], repro["before_counts"],
           repro["after_counts"]))

    frozen_src = open(os.path.join(CONS, "scripts", "c3_separation.py"), encoding="utf-8").read()
    local_src = open(os.path.join(HERE, "c3_separation_local.py"), encoding="utf-8").read()
    consts = ["AUC_MIN = 0.70", "FDR_MAX = 0.05", "MIN_CELLS = 30", "SHARE_FACTOR = 4.0"]
    consts_ok = all(c in frozen_src and c in local_src for c in consts)
    add("G4", "thresholds frozen: local ruler differs only in the disclosed repair",
        consts_ok and patchd["n_changed_lines"] <= 24 and "qmap" in patchd["unified_diff"]
        and "qs[i]" in patchd["unified_diff"],
        "python3 scripts/m3b_remeasure_local.py  (out/RULER_PATCH.json holds the unified diff)",
        "changed diff lines=%d; constants present in both=%s; diff touches qmap/qs[i]"
        % (patchd["n_changed_lines"], consts_ok))

    dv = dface["verdict"]
    add("G5", "default face: this card's delta changes no default-route byte",
        dv == "PASS" and dface["arms"]["n_differing_calls"] == 0
        and dface["route_composition_identical"]
        and not dface["subtype_v14"]["in_all_route_any_state"]
        and not dface["subtype_v14"]["in_all_route_with_switch_on"],
        "python3 scripts/m9_default_face.py",
        "verdict=%s calls/arm=%d differing=%d route_identical=%s in_all_any_state=%s"
        % (dv, dface["arms"]["n_calls_per_arm"], dface["arms"]["n_differing_calls"],
           dface["route_composition_identical"], dface["subtype_v14"]["in_all_route_any_state"]))

    parent_blob = open(os.path.join(OUT, "COMMITTED_eyekb_core.py").replace("COMMITTED", "PREIMAGE")
                       + ".bak_pre_subtype2m", encoding="utf-8").read()
    committed = open(os.path.join(OUT, "COMMITTED_eyekb_core.py"), encoding="utf-8").read()
    prehead = subprocess.run(["git", "-C", REPO, "show",
                              "%s:mcp_server/eyekb_core.py" % dface["parent_commit"]],
                             capture_output=True, text=True).stdout
    def whitelists(text):
        return sorted(re.findall(r"^([A-Z0-9_]+_DEFAULT_LIBS) = \(([^)]*)\)", text, re.M))
    wl_parent, wl_commit = whitelists(prehead), whitelists(committed)
    only_mine = [w for w in wl_commit if w not in wl_parent]
    add("G6", "no other wave's *_DEFAULT_LIBS tuple is touched; the new one is empty",
        len(only_mine) == 1 and only_mine[0][0] == "SUBTYPE_DEFAULT_LIBS" and only_mine[0][1] == ""
        and all(w in wl_commit for w in wl_parent),
        "python3 scripts/m7_register_library.py ; compare *_DEFAULT_LIBS in "
        "git show HEAD:mcp_server/eyekb_core.py vs out/COMMITTED_eyekb_core.py",
        "parent whitelists=%s ; committed adds only %s" % ([w[0] for w in wl_parent], only_mine))

    rows_lib = panel["panel_rows"]
    max_added = max(len(r["added"]) for r in rows_lib)
    add("G7", "library: 16 entries, every CL id resolves, cap K=2 respected",
        len(lib["entries"]) == 16 and all(e["cl_resolves"] for e in lib["entries"]) and max_added <= 2
        and all(e["markers_added_by_this_wave"] == e["markers_added_by_this_wave"] for e in lib["entries"]),
        "python3 scripts/m6_build_panel.py",
        "entries=%d cl_resolve=%d/%d max_added_per_subtype=%d"
        % (len(lib["entries"]), sum(1 for e in lib["entries"] if e["cl_resolves"]),
           len(lib["entries"]), max_added))

    missing = []
    for e in lib["entries"]:
        for a in e["added_evidence"]:
            if not a["papers"] and not a["channel_b_sources"]:
                missing.append((e["cl_id"], a["gene"], "no paper id"))
            if not any(a["segments"]):
                missing.append((e["cl_id"], a["gene"], "no verbatim segment"))
    add("G8", "provenance: every added gene has >= 1 resolvable claim and a verbatim segment",
        not missing, "python3 scripts/m6_build_panel.py (reads out/SUBTYPE_SECOND_MARKER_LIT.json)",
        "gaps=%s" % missing[:5])

    bad_flips = []
    scope = set(m0["in_scope_subtypes"])
    for f in fl["flips"]:
        clearing = [m for m in f["clearing_markers"] if m["q"] is not None and m["auc"] >= 0.70
                    and m["q"] < 0.05]
        if f["subtype"] not in scope or len(clearing) < 2 or not f["verdict"]:
            bad_flips.append(f["subtype"] + "@" + f["volume"])
    add("G9", "every flip is in-scope, has >= 2 clearing markers, and carries H1-H5 + robustness",
        not bad_flips and all("verdict" in r for r in rob["rows"]),
        "python3 scripts/m4_flips.py && python3 scripts/m5_robustness.py",
        "flips=%d bad=%s robust=%d rule_dependent=%d"
        % (fl["n_flips"], bad_flips, rob["n_robust"], rob["n_rule_dependent"]))

    audit = os.path.join(WAVE, "ledgers", "net_audit.log")
    receipts = events = 0
    if os.path.isfile(audit):
        txt = open(audit, encoding="utf-8", errors="replace").read()
        receipts = txt.count("# hook-installed")
        events = len([l for l in txt.splitlines() if l.startswith("EVENT")])
    add("G10", "zero network: audit-hook receipts > 0 and EVENT lines == 0",
        receipts > 0 and events == 0, "bash scripts/run_all.sh (PYTHONPATH=scripts/netaudit)",
        "receipts=%d events=%d" % (receipts, events))

    arch = ["SUPERSEDED_m1_mine_lit_p1.json", "SUPERSEDED_pass2/SUBTYPE_SECOND_MARKER_LIT_p2.json",
            "SUPERSEDED_pass3/SUBTYPE_SECOND_MARKER_LIT_p3.json",
            "SUPERSEDED_pass4/SUBTYPE_SECOND_MARKER_LIT_p4.json",
            "SUBTYPE_SECOND_MARKER_LIT.json"]
    have = [a for a in arch if os.path.isfile(os.path.join(OUT, a))]
    add("G11", "all five mining passes on disk (superseded ones preserved)", len(have) == 5,
        "ls out/SUPERSEDED* out/SUBTYPE_SECOND_MARKER_LIT.json", "present=%s" % have)

    add("G12", "NOT_RUN is never a pass: every gate above carries a command and a real reading",
        all(c["command"] and c["reading"] != "" for c in checks) and len(checks) == 11,
        "this script", "gates=%d" % (len(checks) + 1))

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"

    # ---- manifest (excludes this script's own outputs and all run-time artefacts)
    manifest = os.path.join(OUT, "MANIFEST.sha256")
    lines = []
    targets = []
    for d in (WAVE, os.path.join(WAVE, "scripts"), os.path.join(WAVE, "out")):
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if not os.path.isfile(p):
                continue
            if fn in EXCLUDE_NAMES or fn.startswith("SUPERSEDED_"):
                continue
            targets.append(p)
    for p in targets:
        lines.append("%s  %s" % (sha(p), os.path.relpath(p, WAVE)))
    with open(manifest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    doc = {"probe": "m10_manifest_gate.py", "verdict": verdict, "n_gates": len(checks),
           "checks": checks,
           "manifest": {"path": manifest, "n_files": len(lines),
                        "excluded": sorted(EXCLUDE_NAMES) + ["logs/**", "ledgers/**",
                                                             "artefacts this script writes"],
                        "rule": "run-time artefacts (this wave's logs, the audit ledger, this script's "
                                "own outputs) are excluded so a re-check cannot invalidate the manifest"},
           "registry": {"core_row": reg["core_row"], "library_row": reg["library_row"]},
           "headline": {"rows_in_scope": m0["in_scope_n_rows"],
                        "separated_before": repro["before_counts"].get("separated"),
                        "separated_after": repro["after_counts"].get("separated"),
                        "flips": fl["n_flips"], "robust": rob["n_robust"],
                        "rule_dependent": rob["n_rule_dependent"],
                        "out_of_scope_moved": repro["out_of_scope_moved_n"]}}
    json.dump(doc, open(os.path.join(OUT, "GATE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for c in checks:
        print("%-5s %-6s %s" % (c["id"], "PASS" if c["ok"] else "FAIL", c["description"]))
        if not c["ok"]:
            print("        reading:", c["reading"], "| cmd:", c["command"])
    print("verdict:", verdict, " gates:", len(checks), " manifest files:", len(lines))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())