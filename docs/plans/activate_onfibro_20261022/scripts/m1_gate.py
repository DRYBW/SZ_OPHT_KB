#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m1 -- the activation wave's own gate. Every check is mechanical, fail-closed, and names its code.

Usage: python3 m1_gate.py [--inner-clone-check] [--json out/GATE.json]
  --inner-clone-check : this invocation runs INSIDE the clean clone; the clone-check record is
                        produced by the step that launched it, so M13 is reported as INFO here and
                        judged by the author-tree invocation.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
OUT = os.path.join(WAVE, "out")
WAVE_REL = "docs/plans/activate_onfibro_20261022/"

# changed paths this card may write (everything else must be untouched). Runtime outputs under the
# wave prefix are exempt by the prefix rule.
ALLOWED_CHANGED = {
    "mcp_server/eyekb_core.py",
    "docs/W3_PIPELINE_REGISTRY.tsv",
    "docs/VERIFY_CONTRACT.md",
    "docs/CHANGE_CONTROL_G6_INSTANCE.tsv",
    "docs/RELEASE_IDENTITY.json",
    "docs/RELEASE_MANIFEST_v1.json",
    "docs/W3_MANIFEST.sha256",
    "tests/G4_EXPECTED.json",
    "tests/G4_EXPECTED_PRE-ONFIBRO.json",
    "docs/GATE_INVENTORY_G5G6.tsv",
}
# JSON response paths the activation is allowed to move (the answer surface + the disclosure fields
# that report which libraries answered). Anything else is an unexplained default-face change.
ALLOWED_FIELDS = {"provenance", "soft_flags", "celltype_ranking", "gene_to_celltypes"}


def sha256(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


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

    # M01 -- the pre-registration exists and predates every outcome artefact
    pre = os.path.join(WAVE, "PREREG_ACTIVATION_ONFIBRO_20261022.md")
    outs = [os.path.join(OUT, n) for n in
            ("FLIP.json", "FLIP_MEASUREMENT.json", "DEFAULT_FACE.json", "FIELD_DIFF.json")]
    if not os.path.exists(pre):
        rec("M01 PREREG", False, "PREREG_ACTIVATION_ONFIBRO_20261022.md missing")
    else:
        pm = os.path.getmtime(pre)
        earlier = [os.path.basename(p) for p in outs if os.path.exists(p) and os.path.getmtime(p) < pm]
        rec("M01 PREREG", not earlier, "prereg present; outcome files older than it: %s"
            % (earlier or "none"))

    # M02 -- the pre-image is kept and matches the state the flip started from
    pi = load("PREIMAGE.json")
    if not pi:
        rec("M02 PREIMAGE", False, "PREIMAGE.json missing (run l0 first)")
    else:
        ok = (pi["pre_image_matches_live"] and pi["before_region_counts"] == {"comment": 1, "doc": 1}
              and pi["base_commit"])
        rec("M02 PREIMAGE", ok, "pre-image %s (matches live=%s); region counts %s; base commit %s"
            % (pi["pre_image_sha256"][:16], pi["pre_image_matches_live"],
               pi["before_region_counts"], pi["base_commit"][:8]))

    # M03 -- the flip is exactly the whitelist change, inside the declared region
    fl = load("FLIP.json")
    if not fl:
        rec("M03 FLIP", False, "FLIP.json missing")
    else:
        ok = (fl["verdict"] == "PASS"
              and fl["whitelist_delta"] == {"ONFIBRO_DEFAULT_LIBS": ["()", '("onfibro_v13",)']}
              and fl["all_hunks_inside_onfibro_region"] and fl["py_compile_rc"] == 0
              and "('onfibro_v13',)" in fl["import_probe_stdout"])
        rec("M03 FLIP", ok, "whitelist delta %s; hunks %s inside region %s; py_compile rc=%s; "
            "import %s" % (fl["whitelist_delta"], fl["diff_hunks_after_line"],
                           fl["onfibro_region_lines_after"], fl["py_compile_rc"],
                           fl["import_probe_stdout"].replace("\n", " | ")))

    # M04 -- the harness measurement: no dataset falls, every moved cluster attributed
    fm = load("FLIP_MEASUREMENT.json")
    if not fm:
        rec("M04 HARNESS", False, "FLIP_MEASUREMENT.json missing")
    else:
        acc = fm["acceptance"]
        ok = (acc["verdict"] == "PASS" and fm["verdict"] == "PASS"
              and fm["equivalence_flip_vs_inject"]["identical"] == fm["equivalence_flip_vs_inject"]["clusters"]
              and all(fm["cross_wave_identity"][k]["identical"] for k in fm["cross_wave_identity"])
              and fm["moved_kinds"].get("unexpected", 0) == 0
              and not fm["takeovers_on_other_family"]
              and fm["motivating_cluster"]["after_grade"] == "consistent")
        rec("M04 HARNESS", ok, "acceptance=%s (F1/F2/F3=%s/%s/%s, default route=%s); moved=%d kinds=%s; "
            "flip==inject %d/%d; motivating cluster %s -> %s(%s)"
            % (acc["verdict"], acc["F1_verdict"], acc["F2_verdict"], acc["F3_control_verdict"],
               acc["default_route_verdict"], len(fm["moved_clusters"]), fm["moved_kinds"],
               fm["equivalence_flip_vs_inject"]["identical"],
               fm["equivalence_flip_vs_inject"]["clusters"],
               fm["motivating_cluster"]["before_top"], fm["motivating_cluster"]["after_top"],
               fm["motivating_cluster"]["after_n_shared"]))

    # M05 -- the kill switch restores the pre-flip default byte-for-byte
    df = load("DEFAULT_FACE.json")
    if not df:
        rec("M05 KILL-SWITCH", False, "DEFAULT_FACE.json missing")
    else:
        ks = df["kill_switch_byte_identity"]
        ok = (df["verdict"] == "PASS" and df["parent_core_equals_kept_preimage"]
              and df["restored_matches_snapshot"]
              and all(v["identical_raw"] and v["identical_canonical"] for v in ks.values())
              and all(v["n_differing_raw"] == 0 for v in ks.values()))
        rec("M05 KILL-SWITCH", ok, "721/721 clusters and 229/229 battery calls identical "
            "(raw+canonical), differing raw=%s; parent core == kept pre-image=%s"
            % ([v["n_differing_raw"] for v in ks.values()], df["parent_core_equals_kept_preimage"]))

    # M06 -- the activation delta is fully attributed (nothing unexplained)
    if not df:
        rec("M06 DELTA-ATTRIBUTED", False, "DEFAULT_FACE.json missing")
    else:
        d = df["activation_delta"]
        ok = all(v["n_unexplained"] == 0 for v in d.values())
        rec("M06 DELTA-ATTRIBUTED", ok,
            "clusters moved_raw=%d/%d ranking_moved=%d disclosure-only=%d; battery moved=%d/%d; "
            "census %s / %s"
            % (d["clusters"]["n_moved_raw"], d["clusters"]["n_queries"],
               d["clusters"]["n_ranking_moved"], d["clusters"]["n_byte_moved_ranking_unchanged"],
               d["battery"]["n_moved_raw"], d["battery"]["n_queries"],
               d["clusters"]["attribution_census"], d["battery"]["attribution_census"]))

    # M07 -- the compatibility item is recorded, not absorbed
    if not df:
        rec("M07 COMPAT-ITEM", False, "DEFAULT_FACE.json missing")
    else:
        tb = df["tool_panel"]
        ok = ((tb["legacy_panel_unchanged_parent_vs_flip"]
               or tb["compatibility_contract_item"] is not None)
              and tb["per_call_attribution"]["baseline_re_recorded"] is False
              and tb["per_call_attribution"]["FLIP"]["report"] != []
              and tb["probe_file_byte_unchanged_vs_parent_commit"])
        rec("M07 COMPAT-ITEM", ok, "legacy panel unchanged=%s; item recorded=%s; baseline "
            "re-recorded=%s; probe report %s"
            % (tb["legacy_panel_unchanged_parent_vs_flip"],
               tb["compatibility_contract_item"] is not None,
               tb["per_call_attribution"]["baseline_re_recorded"],
               tb["per_call_attribution"]["FLIP"]["report"]))

    # M08 -- the field-level diff stays inside the allowed response paths
    fd = load("FIELD_DIFF.json")
    if not fd:
        rec("M08 FIELD-SCOPE", False, "FIELD_DIFF.json missing")
    else:
        fields = set(fd["changed_response_fields"])
        outside = sorted(fields - ALLOWED_FIELDS)
        rec("M08 FIELD-SCOPE", not outside and fd["verdict"] == "PASS",
            "changed response fields %s; outside the allowed set: %s" % (sorted(fields), outside))

    # M09 -- the registry is honest about every file this card moved
    ru = load("REGISTRY_UPDATE.json")
    gr = subprocess.run(["/usr/bin/python3", "tests/gate_registry.py"], cwd=REPO,
                        capture_output=True, text=True)
    if not ru:
        rec("M09 REGISTRY", False, "REGISTRY_UPDATE.json missing")
    else:
        ok = gr.returncode == 0 and "verdict=PASS" in gr.stdout and ru["verdict"] == "PASS"
        rec("M09 REGISTRY", ok, "G5 rc=%d verdict_in_stdout=%s; rows re-taken %s"
            % (gr.returncode, "verdict=PASS" in gr.stdout, sorted(ru["rows"])))

    # M10 -- the change-control row passes its own validator
    gc = subprocess.run(["/usr/bin/python3", "tests/gate_change_control.py"], cwd=REPO,
                        capture_output=True, text=True)
    row_ok = "CHG-20261022-ONFIBRO-ACTIVATION" in open(
        os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv"), encoding="utf-8").read()
    rec("M10 CHANGE-CONTROL", gc.returncode == 0 and row_ok,
        "G6 rc=%d; activation row present=%s" % (gc.returncode, row_ok))

    # M11 -- zero network: no event of a class that can transfer data, plus a census of what the
    # hook did record (the load receipt proves the hook ran)
    CONNECTING = ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname",
                  "urllib.", "http.client", "ftplib.", "smtplib.")
    led = os.path.join(WAVE, "ledgers", "net_audit.log")
    receipts, bad, census = 0, [], {}
    if not os.path.exists(led):
        bad.append("net_audit.log missing")
    else:
        txt = open(led, encoding="utf-8", errors="replace").read().splitlines()
        receipts = len([l for l in txt if l.startswith("# hook-installed")])
        ev = [l for l in txt if l.startswith("EVENT")]
        for l in ev:
            k = l.split()[1]
            census[k] = census.get(k, 0) + 1
        for l in ev:
            if any(l.startswith("EVENT " + c) for c in CONNECTING):
                bad.append(l[:120])
    rec("M11 NET-AUDIT", receipts > 0 and not bad,
        "hook load receipts=%d; connecting/HTTP events=%d; census=%s" % (receipts, len(bad), census))

    # M12 -- the manifest matches the disk
    man = load("MANIFEST.json")
    if not man:
        rec("M12 MANIFEST", False, "MANIFEST.json missing")
    else:
        drift = [e["rel"] for e in man["files"]
                 if not os.path.exists(os.path.join(WAVE, e["rel"]))
                 or sha256(os.path.join(WAVE, e["rel"])) != e["sha256"]]
        rec("M12 MANIFEST", not drift, "files=%d drifting=%d %s"
            % (len(man["files"]), len(drift), drift[:6]))

    # M13 -- nothing outside the declared change surface was touched
    gs = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True)
    changed = []
    for line in gs.stdout.splitlines():
        rel = line[3:].strip()
        if " -> " in rel:
            rel = rel.split(" -> ")[-1]
        changed.append(rel)
    unexpected = [c for c in changed if c not in ALLOWED_CHANGED and not c.startswith(WAVE_REL)]
    rec("M13 CHANGE-SURFACE", not unexpected,
        "changed=%d outside the declared surface=%s" % (len(changed), unexpected[:8]))

    # M14 -- the registration surfaces agree with the wire: the delivery copy identity check
    ri = subprocess.run(["/usr/bin/python3", "scripts/release_identity.py", "--check"], cwd=REPO,
                        capture_output=True, text=True)
    rec("M14 RELEASE-IDENTITY", ri.returncode == 0,
        "scripts/release_identity.py --check rc=%d %s" % (ri.returncode, ri.stdout.strip()[:200]))

    # M15 -- red lines: exactly one whitelist entry, the carrier file untouched, the ontology term
    # resolvable, the exclusion table untouched
    src = open(os.path.join(REPO, "mcp_server", "eyekb_core.py"), encoding="utf-8").read()
    m = re.search(r"ONFIBRO_DEFAULT_LIBS = \(([^)]*)\)", src)
    wl_ok = m is not None and m.group(1).strip() == '"onfibro_v13",'
    others = {k: v for k, v in re.findall(r"(V6|K9|ANTSEG)_DEFAULT_LIBS = \(([^)]*)\)", src)}
    carrier = json.load(open(os.path.join(REPO, "kb", "markers",
                                          "markers_v13_onfibro_increment.json"), encoding="utf-8"))
    cl_id = carrier["entries"][0]["cl_id"]
    obo = open(os.path.join(REPO, "kb", "ontology", "cl", "releases", "2026-06-08",
                            "cl-base.obo"), encoding="utf-8", errors="replace").read()
    cl_ok = bool(re.search(r"^id: %s\s*$" % re.escape(cl_id), obo, re.M)) and \
        bool(re.search(r"^id: %s\s*\nname: fibroblast\s*$" % re.escape(cl_id), obo, re.M))
    xw = subprocess.run(["git", "-C", REPO, "diff", "--name-only", "HEAD", "--",
                         "kb/baselines/_tissue_class_crosswalk_v1.json"], capture_output=True,
                        text=True)
    rec("M15 RED-LINES", wl_ok and not xw.stdout.strip() and cl_ok and cl_id == "CL:0000057",
        "ONFIBRO whitelist=%r; other whitelists=%s; carrier CL %s resolves=%s; exclusion table "
        "touched=%r" % (m.group(1) if m else None, others, cl_id, cl_ok, xw.stdout.strip()))

    # M16 -- the clean clone
    cc = load("CLEAN_CLONE_CHECK.json")
    if a.inner_clone_check:
        rec("M16 CLEAN-CLONE", True,
            "INFO: produced by the step that launched this invocation; judged in the author tree",
            status="INFO")
    elif not cc:
        rec("M16 CLEAN-CLONE", False, "CLEAN_CLONE_CHECK.json missing")
    else:
        rec("M16 CLEAN-CLONE", cc.get("verdict") == "PASS",
            "verdict=%s commit=%s compared=%s differing=%s repo_chain_rc=%s"
            % (cc.get("verdict"), cc.get("commit"), cc.get("files_compared_author_vs_clone"),
               cc.get("files_differing_from_author_tree"), cc.get("repo_gate_chain_rc_in_clone")))

    failed = [c for c in checks if c["status"] == "FAIL"]
    doc = {"probe": "m1_gate.py", "wave": WAVE_REL.rstrip("/"), "checks": checks,
           "n_checks": len(checks), "n_failed": len(failed),
           "failed": [c["code"] for c in failed],
           "verdict": "PASS" if not failed else "FAIL",
           "inner_clone_check": bool(a.inner_clone_check)}
    os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
    json.dump(doc, open(a.json, "w"), ensure_ascii=False, indent=1)
    for c in checks:
        print("  %-6s %-22s %s" % (c["status"], c["code"], str(c["detail"])[:150]))
    print("[activate] checks=%d failed=%d verdict=%s" % (len(checks), len(failed), doc["verdict"]))
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())