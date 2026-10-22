#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n8 -- the wave's own gate. Every check is mechanical, fail-closed, and names its code.

Usage: python3 n8_gate.py [--inner-clone-check] [--json out/GATE.json]
  --inner-clone-check : this invocation runs INSIDE a clean clone; the clone-check record is
                        produced by the step that launched it, so N12 is reported as INFO here and
                        judged by the author-tree invocation.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

ALLOWED_CHANGED = {
    "mcp_server/eyekb_core.py",
    "kb/markers/markers_v13_onfibro_increment.json",
    "docs/W3_PIPELINE_REGISTRY.tsv",
}
WAVE_PREFIX = "docs/plans/noregr_20261022/"
# Files a CONCURRENT card was writing in this working tree while this wave ran. They are declared
# here with their owner so the check states who is responsible instead of either failing on someone
# else's work or silently ignoring a modified file. This card writes nothing outside WAVE_PREFIX and
# ALLOWED_CHANGED; the check asserts exactly that, and reports these as INFO.
FOREIGN_INFLIGHT = {
    "docs/plans/l5_ontlayer_20261022/scripts/09_clean_clone_chain.sh":
        "card l5_ontlayer_20261022 (its own clone-check script, modified in the working tree)",
    "docs/plans/l5_ontlayer_20261022/scripts/07_registry_rows.py":
        "card l5_ontlayer_20261022 (its own registry-row generator, modified in the working tree)",
}


def load(rel):
    p = os.path.join(OUT, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inner-clone-check", action="store_true")
    ap.add_argument("--json", default=os.path.join(OUT, "GATE.json"))
    a = ap.parse_args()
    checks = []

    def rec(code, ok, detail, status=None):
        checks.append({"code": code, "status": status or ("PASS" if ok else "FAIL"),
                       "ok": bool(ok), "detail": detail})

    # N01 -- pre-registration exists and predates every outcome artefact
    pre = os.path.join(WAVE, "PREREG_NOREGRESSION_20261022.md")
    outs = [os.path.join(OUT, n) for n in ("REPRODUCE.json", "SWEEP_EXCLUSIONS.json",
                                           "carrier_panel.json", "FIX_MEASUREMENT.json",
                                           "DEFAULT_FACE.json")]
    if not os.path.exists(pre):
        rec("N01 PREREG", False, "PREREG_NOREGRESSION_20261022.md missing")
    else:
        pm = os.path.getmtime(pre)
        later = [os.path.basename(p) for p in outs if os.path.exists(p)
                 and os.path.getmtime(p) < pm]
        rec("N01 PREREG", not later,
            "prereg present; outcome files older than it: %s" % (later or "none"))

    # N02 -- the frozen inputs: recorded set shape
    m = load("INPUT_MANIFEST.json")
    if not m:
        rec("N02 INPUTS", False, "INPUT_MANIFEST.json missing (run n0 first)")
    else:
        rs = m["recorded_set"]
        rec("N02 INPUTS", rs["volumes"] == 28 and rs["clusters"] == 721 and not m["missing"],
            "volumes=%d clusters=%d cells=%d missing_inputs=%d recordings_hashed=%d"
            % (rs["volumes"], rs["clusters"], rs["cells"], len(m["missing"]),
               len(m["recordings"])))

    # N03 -- G1 reproduction
    d = load("REPRODUCE.json")
    if not d:
        rec("N03 REPRODUCE", False, "REPRODUCE.json missing")
    else:
        cl = d["G1_single_carrier_loss"]
        ar = d["drop_arithmetic"]
        row = [x for x in d["scope_ab"]["changed"] if x["cluster"] == "31"]
        ok = (cl["n_limbus_sclera_fibroblast_losses"] == 1
              and row and row[0]["on_top"] is None
              and abs(ar["carrier_loss_share_of_volume_pct"] - 2.531) < 0.002
              and abs(ar["delta_pp"] + 2.531) < 0.002
              and d["source_of_truth_probe"]["rc"] == 0)
        rec("N03 REPRODUCE", ok,
            "carrier losses=%d (row Limbus_Sclera_fibroblast_C1); share=%.3f%% delta=%.3fpp; "
            "probe rc=%s" % (cl["n_limbus_sclera_fibroblast_losses"],
                             ar["carrier_loss_share_of_volume_pct"], ar["delta_pp"],
                             d["source_of_truth_probe"]["rc"]))

    # N04 -- the sweep enumerated every row of every tissue
    s = load("SWEEP_EXCLUSIONS.json")
    if not s:
        rec("N04 SWEEP", False, "SWEEP_EXCLUSIONS.json missing")
    else:
        A = s["A_row_audit"]
        zero_enumerated = all("n_carrier_loss" in r for r in A["rows"])
        rec("N04 SWEEP", A["n_tissues"] == 12 and zero_enumerated,
            "tissues=%d rows=%d live_defects=%d (rows with count 0 are enumerated too)"
            % (A["n_tissues"], A["n_rows"], A["n_live_defects"]))

    # N05 -- the harness's acceptance rule can fail, not only pass
    st = load("harness/SELFTEST_ACCEPTANCE_RULE.json")
    if not st:
        rec("N05 HARNESS-SELFTEST", False, "SELFTEST_ACCEPTANCE_RULE.json missing")
    else:
        rec("N05 HARNESS-SELFTEST", st["verdict"] == "PASS" and len(st["cases"]) == 3,
            "cases=%s verdict=%s" % ([(c["case"], c["verdict"]) for c in st["cases"]],
                                     st["verdict"]))

    # N06 -- G4: the fix recovers the cluster and lowers nothing
    f = load("FIX_MEASUREMENT.json")
    if not f:
        rec("N06 FIX", False, "FIX_MEASUREMENT.json missing")
    else:
        g = f["G4"]
        mc = f["runs"]["R2_fix_recorded_decls"]["motivating_cluster"]
        rec("N06 FIX", g["verdict"] == "PASS" and mc["after_grade"] == "consistent",
            "G4=%s; motivating cluster %s(%s) -> %s(%s) [%s -> %s]; overall consistent delta "
            "%+.3fpp (recorded decls) / %+.3fpp (tester decls)"
            % (g["verdict"], mc["before_top"], mc["before_n_shared"], mc["after_top"],
               mc["after_n_shared"], mc["before_grade"], mc["after_grade"],
               g["net_overall_delta_pp_recorded_decls"],
               g["net_overall_delta_pp_tester_decls"]))

    # N07 -- the default face
    df = load("DEFAULT_FACE.json")
    if not df:
        rec("N07 DEFAULT-FACE", False, "DEFAULT_FACE.json missing")
    else:
        ok = (df["verdict"] == "PASS" and df["restored_matches_snapshot"]
              and all(v["identical"] for v in df["arms"].values())
              and df["legacy_tool_panel_probe"]["byte_unchanged_vs_parent_commit"]
              and df["legacy_tool_panel_probe"]["digests_identical"])
        rec("N07 DEFAULT-FACE", ok,
            "clusters n=%d identical=%s; battery n=%d identical=%s; probe digests identical=%s; "
            "core restored=%s"
            % (df["arms"]["clusters"]["n_queries"], df["arms"]["clusters"]["identical"],
               df["arms"]["battery"]["n_queries"], df["arms"]["battery"]["identical"],
               df["legacy_tool_panel_probe"]["digests_identical"], df["restored_matches_snapshot"]))

    # N08 -- zero network.  The criterion is deliberately stated as: no event of a class that can
    # transfer data, plus a full census of everything the hook did record.  Claiming a literal
    # "events = 0" would be false: the hook is a socket-layer hook, so it also sees local socket
    # objects, gethostname and loopback binds, none of which move a byte off the machine.
    CONNECTING = ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname",
                  "urllib.", "http.client", "ftplib.", "smtplib.")
    census, bad, receipts = {}, [], 0
    for name in ("net_audit_full_chain.log", "net_audit_repogates.log"):
        led = os.path.join(WAVE, "ledgers", name)
        if not os.path.exists(led):
            bad.append(name + ":missing")
            continue
        txt = open(led, encoding="utf-8", errors="replace").read().splitlines()
        receipts += len([l for l in txt if l.startswith("# hook-installed")])
        ev = [l for l in txt if l.startswith("EVENT")]
        cen = {}
        for l in ev:
            k = l.split()[1]
            cen[k] = cen.get(k, 0) + 1
        census[name] = {"receipt_lines": len([l for l in txt
                                              if l.startswith("# hook-installed")]),
                        "event_lines": len(ev), "event_classes": cen}
        for l in ev:
            if any(l.startswith("EVENT " + c) for c in CONNECTING):
                bad.append(l[:120])
    rec("N08 NET-AUDIT", receipts > 0 and not bad,
        "hook load receipts=%d; connecting/HTTP events=%d; census=%s"
        % (receipts, len(bad), census))

    # N09 -- the manifest matches the disk
    man = load("MANIFEST.json")
    if not man:
        rec("N09 MANIFEST", False, "MANIFEST.json missing")
    else:
        bad = []
        for e in man["files"]:
            p = os.path.join(WAVE, e["rel"])
            if not os.path.exists(p) or W.sha256_file(p) != e["sha256"]:
                bad.append(e["rel"])
        rec("N09 MANIFEST", not bad, "files=%d drifting=%d %s"
            % (len(man["files"]), len(bad), bad[:6]))

    # N10 -- nothing outside the declared change surface was touched
    gs = subprocess.run(["git", "-C", W.REPO, "status", "--porcelain"],
                        capture_output=True, text=True)
    changed = []
    for line in gs.stdout.splitlines():
        rel = line[3:].strip()
        if " -> " in rel:
            rel = rel.split(" -> ")[-1]
        changed.append(rel)
    unexpected = [c for c in changed
                  if c not in ALLOWED_CHANGED and not c.startswith(WAVE_PREFIX)
                  and c not in FOREIGN_INFLIGHT]
    foreign = [c for c in changed if c in FOREIGN_INFLIGHT]
    rec("N10 CHANGE-SURFACE", not unexpected,
        "changed=%d unexpected=%s (foreign in-flight, declared and not owned by this card: %s)"
        % (len(changed), unexpected[:8],
           [(c, FOREIGN_INFLIGHT[c]) for c in foreign]))

    # N11 -- the registry is honest about the two files this card touches
    gr = subprocess.run(["/usr/bin/python3", "tests/gate_registry.py"], cwd=W.REPO,
                        capture_output=True, text=True)
    reg_ok = gr.returncode == 0 and "verdict=PASS" in gr.stdout
    reg_row = json.load(open(os.path.join(OUT, "REGISTRY_UPDATE.json")))
    iid = reg_row.get("new_row", {}).get("item_id")
    reg_txt = open(os.path.join(W.REPO, "docs", "W3_PIPELINE_REGISTRY.tsv"),
                   encoding="utf-8", errors="replace").read()
    n_iid = sum(1 for l in reg_txt.splitlines() if l.split("\t")[1:2] == [str(iid)])
    rec("N11 REGISTRY", reg_ok and iid and n_iid == 1,
        "G5 rc=%d verdict_in_stdout=%s; new row %s appears as an item_id %d time(s)"
        % (gr.returncode, reg_ok, iid, n_iid))

    # N12 -- the clean clone
    cc = load("CLEAN_CLONE_CHECK.json")
    if a.inner_clone_check:
        rec("N12 CLEAN-CLONE", True,
            "INFO: produced by the step that launched this invocation; judged in the author tree",
            status="INFO")
    elif not cc:
        rec("N12 CLEAN-CLONE", False, "CLEAN_CLONE_CHECK.json missing")
    else:
        rec("N12 CLEAN-CLONE", cc.get("verdict") == "PASS",
            "verdict=%s commit=%s files_compared=%s differing=%s"
            % (cc.get("verdict"), cc.get("commit"), cc.get("files_compared_author_vs_clone"),
               cc.get("files_differing_from_author_tree")))

    # N13 -- the harness pre-image is recorded in every harness run
    pre_ok, missing = True, []
    for k in ("R1_narrowing_recorded_decls", "R2_fix_recorded_decls", "R3_fix_tester_decls",
              "R4_narrowing_plus_fix_tester_decls", "selftest_unattributed",
              "selftest_attributed", "selftest_noop"):
        p = os.path.join(OUT, "harness", k, "REPORT.json")
        if not os.path.exists(p):
            pre_ok = False
            missing.append(k)
            continue
        d2 = json.load(open(p))
        hp = d2.get("harness_preimage") or {}
        if not hp.get("files") or not hp.get("inputs"):
            pre_ok = False
            missing.append(k + ":no-preimage")
    rec("N13 HARNESS-PREIMAGE", pre_ok, "runs without a pre-image: %s" % (missing or "none"))

    # N14 -- red lines: nothing activated
    src = open(os.path.join(W.REPO, "mcp_server", "eyekb_core.py"), encoding="utf-8").read()
    ok14 = ("ONFIBRO_DEFAULT_LIBS = ()" in src
            and 'ONFIBRO_DEFAULT_LIBS)' in src)
    import re as _re
    m14 = _re.search(r"ONFIBRO_DEFAULT_LIBS = \(([^)]*)\)", src)
    rec("N14 RED-LINES", ok14 and m14 is not None and m14.group(1).strip() == "",
        "ONFIBRO whitelist is empty (%r); new library is explicit-route-only"
        % (m14.group(1) if m14 else None))

    failed = [c for c in checks if c["status"] == "FAIL"]
    verdict = "PASS" if not failed else "FAIL"
    doc = {"probe": "n8_gate.py", "wave": os.path.relpath(WAVE, W.REPO),
           "checks": checks, "n_checks": len(checks), "n_failed": len(failed),
           "failed": [c["code"] for c in failed], "verdict": verdict,
           "inner_clone_check": bool(a.inner_clone_check)}
    os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
    json.dump(doc, open(a.json, "w"), ensure_ascii=False, indent=1)
    for c in checks:
        print("  %-9s %-22s %s" % (c["status"], c["code"], c["detail"]))
    print("[noregr] checks=%d failed=%d verdict=%s" % (len(checks), len(failed), verdict))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())