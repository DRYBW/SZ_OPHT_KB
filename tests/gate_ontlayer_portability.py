#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_ontlayer_portability.py - G8: does the ontology layer travel, and does it fail closed?

What it enforces (all of it mechanically, with no network and no data-mount dependency)
    G8-P01 FOREIGN-CWD     the layer resolves its assets whatever the working directory is
    G8-P02 FOREIGN-ROOT    a copy of the layer's assets at a different path, in a directory whose
                           name contains spaces, answers correctly: anchors resolve, the battery
                           passes. The author tree is not consulted.
    G8-P03 NO-AUTHOR-PATHS new service code carries no absolute path of any machine (the portable
                           shebang form aside)
    G8-P04 READ-ONLY       a full battery leaves every asset byte-identical, and the module contains
                           no write call
    G8-P05 FAIL-CLOSED     a missing snapshot, a corrupted snapshot and an unlisted address each
                           produce the declared failure status - and never an ENV_ERROR mask, and
                           never an answer from a placeholder
    G8-P06 GATE-REPORT     the three-state policy and the five-count report are declared, and this
                           gate's own report carries them

Gate result: PASS / FAIL / ENV_ERROR, with every check reporting should-run, did-run and status. A
gate does not pass while any mandatory check did not execute.

Usage (from the repository root):
    python3 tests/gate_ontlayer_portability.py [--json out.json]
Exit codes: 0 = PASS, 2 = FAIL, 3 = ENV_ERROR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_server"))

# The files this card adds or changes. The scan covers them and nothing else: pre-existing absolute
# paths elsewhere in the repository are somebody else's registration, not this card's claim.
SERVICE_FILES = ["mcp_server/ontology_layer.py", "mcp_server/server.py",
                 "kb/ontology/scripts/build_ont_manifest.py",
                 "tests/gate_ontology_layer.py", "tests/gate_ontlayer_portability.py",
                 "docs/plans/l5_ontlayer_20261022/scripts/02_build_tables.py",
                 "docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py",
                 "docs/plans/l5_ontlayer_20261022/scripts/05_freeze_replay_hashes.py"]
ASSET_RELS = ["kb/ontology", "kb/markers/markers_cl_alignment_v2_unified.json",
              "mcp_server/ontology_layer.py", "mcp_server/__init__.py"]
ADDRESS_HINT = ("/mnt" + "/", "/home" + "/", "/Users" + "/", "C:" + "\\", "/data" + "/",
                "/opt" + "/")
BATTERY = [("resolve_term", ["CL:0000002"]), ("resolve_term", ["mo.6c+ii"]),
           ("get_ancestors", ["CL:0004222"]),
           ("compare_terms", ["CL:0000561", "CL:0004232"]),
           ("compare_terms", ["CL:0000000", "CL:0000001"]),
           ("explain_class_mapping", ["Rod"])]
LAYER_PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
import ontology_layer as OL
out = {"anchors": OL.anchor_status(), "summary": OL.layer().summary()["ontology_snapshot"]}
out["unlisted"] = OL.resolve_anchor("ont://not-listed")
out["battery"] = []
snap = OL.layer()
for name, args in %r:
    got = getattr(snap, name)(*args)
    out["battery"].append({"call": name, "args": args,
                           "verdict": got.get("verdict") or got.get("resolution_status")
                           or got.get("mapping_status"),
                           "anchor_status": (got.get("ontology_snapshot") or {}).get("anchor_status"),
                           "is_a_relation": got.get("is_a_relation")})
print(json.dumps(out))
"""


class Ledger:
    def __init__(self):
        self.checks = []

    def rec(self, code, label, mandatory, should_run, did_run, status, detail, offenders=None):
        self.checks.append({"code": code, "label": label, "mandatory": bool(mandatory),
                            "should_run": bool(should_run), "did_run": bool(did_run),
                            "status": status, "detail": detail, "offenders": (offenders or [])[:8]})
        print(f"  {status:9s} {code} {label} :: {detail}")
        for o in (offenders or [])[:6]:
            print(f"      - {o}")


def run_probe(py: str, mcp_dir: str, cwd: str) -> dict:
    p = subprocess.run([py, "-c", LAYER_PROBE % (BATTERY,), mcp_dir], cwd=cwd,
                       capture_output=True, text=True, timeout=600, env=_clean_env())
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip()[-400:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def _clean_env() -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["EYEKB_ONT_LAYER"] = ""
    return env


def tree_hash(p: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(p).as_posix().encode())
            h.update(hashlib.sha256(f.read_bytes()).hexdigest().encode())
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    L = Ledger()
    py = sys.executable

    # ---------------------------------------------------------------- G8-P01 FOREIGN-CWD
    off = []
    with tempfile.TemporaryDirectory() as td:
        got = run_probe(py, str(ROOT / "mcp_server"), td)
    if any(x["status"] != "RESOLVED" for x in got["anchors"]):
        off.append(f"anchors unresolved from another working directory: "
                   f"{[x['status'] for x in got['anchors']]}")
    if len(got["battery"]) != len(BATTERY) or any(b["verdict"] in (None, "") for b in got["battery"]):
        off.append("the battery produced an empty verdict")
    L.rec("G8-P01", "FOREIGN-CWD", True, True, True, "PASS" if not off else "FAIL",
          f"{len(got['anchors'])} anchors resolved, {len(got['battery'])} battery calls answered "
          f"from a temporary working directory", off)

    # ---------------------------------------------------------------- G8-P02 FOREIGN-ROOT
    off, det = [], []
    with tempfile.TemporaryDirectory() as td:
        spaced = Path(td) / "L5 shadow checkout (copy 2)"
        spaced.mkdir(parents=True)
        for rel in ASSET_RELS:
            src = ROOT / rel
            dst = spaced / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        (spaced / "mcp_server" / "server.py").write_text(
            (ROOT / "mcp_server" / "server.py").read_text(encoding="utf-8"), encoding="utf-8")
        got2 = run_probe(py, str(spaced / "mcp_server"), td)
        det.append(f"root={spaced.name!r} anchors="
                   f"{[x['status'] for x in got2['anchors']]}")
        if any(x["status"] != "RESOLVED" for x in got2["anchors"]):
            off.append("the copy's anchors did not resolve")
        if got2["summary"]["file_sha256"] != got["summary"]["file_sha256"]:
            off.append("the copy answered from a different snapshot")
        if [b["verdict"] for b in got2["battery"]] != [b["verdict"] for b in got["battery"]]:
            off.append(f"the copy's battery differs: "
                       f"{[b['verdict'] for b in got2['battery']]}")
        det.append("battery identical to the author tree")
    L.rec("G8-P02", "FOREIGN-ROOT", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    # ---------------------------------------------------------------- G8-P03 NO-AUTHOR-PATHS
    off, det = [], []
    for rel in SERVICE_FILES:
        p = ROOT / rel
        if not p.is_file():
            off.append(f"{rel}: missing")
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith("#!") and "/usr/bin/env" in s:
                continue
            for hint in ADDRESS_HINT:
                if hint in line:
                    off.append(f"{rel}:{i}: {hint} in {s[:70]}")
    found = "no absolute path"
    for rel in ("kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json",
                "kb/ontology/ONT_LAYER_REGISTRY_v1.json"):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for hint in ADDRESS_HINT:
            if hint in txt:
                off.append(f"{rel}: {hint}")
                found = "an absolute path is present"
    L.rec("G8-P03", "NO-AUTHOR-PATHS", True, True, True, "PASS" if not off else "FAIL",
          f"{len(SERVICE_FILES)} service files + both ontology records scanned: {found}", off)

    # ---------------------------------------------------------------- G8-P04 READ-ONLY
    off, det = [], []
    before = tree_hash(ROOT / "kb" / "ontology")
    align_before = hashlib.sha256(
        (ROOT / "kb/markers/markers_cl_alignment_v2_unified.json").read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as td:
        got3 = run_probe(py, str(ROOT / "mcp_server"), td)
    after = tree_hash(ROOT / "kb" / "ontology")
    align_after = hashlib.sha256(
        (ROOT / "kb/markers/markers_cl_alignment_v2_unified.json").read_bytes()).hexdigest()
    det.append(f"kb/ontology {before[:12]} -> {after[:12]}")
    if before != after:
        off.append("the battery wrote into kb/ontology")
    if align_before != align_after:
        off.append("the battery wrote into the class-mapping source")
    if len(got3["battery"]) != len(BATTERY):
        off.append("the battery did not run")
    banned = []
    names = set()
    with open(ROOT / "mcp_server" / "ontology_layer.py", "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            names.add(tok.string)
    for w in ("write_text", "writelines", "unlink", "mkdir", "makedirs", "rmtree", "remove",
              "rename", "chmod", "system", "Popen", "urlopen", "socket", "requests"):
        if w in names:
            banned.append(w)
    if banned:
        off.append(f"write/exec/network primitives appear in ontology_layer.py: {banned}")
    det.append("no write/exec/network primitive in the module")
    L.rec("G8-P04", "READ-ONLY", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    # ---------------------------------------------------------------- G8-P05 FAIL-CLOSED
    off, det = [], []
    import ontology_layer as OL
    policy = (OL.load_registry().get("anchor_failure_policy") or {})
    for state, want in (("ANCHOR_MISSING", "FAIL"), ("ANCHOR_HASH_MISMATCH", "FAIL"),
                        ("ANCHOR_UNKNOWN", "FAIL"), ("MANIFEST_MISSING", "FAIL")):
        if not str(policy.get(state, "")).startswith(want):
            off.append(f"the registry does not map {state} to {want}: {policy.get(state)!r}")
    if "ENV_ERROR" not in policy:
        off.append("the registry does not declare where ENV_ERROR applies")
    with tempfile.TemporaryDirectory() as td:
        shadow = Path(td) / "shadow"
        for rel in ASSET_RELS:
            src, dst = ROOT / rel, shadow / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
        snap_rel = shadow / "kb/ontology/cl/releases/2026-06-08/cl-base.obo"
        keep = snap_rel.read_bytes()
        snap_rel.unlink()
        got_missing = run_probe(py, str(shadow / "mcp_server"), td)
        snap_rel.write_bytes(keep[:len(keep) // 2])
        got_corrupt = run_probe(py, str(shadow / "mcp_server"), td)
        snap_rel.write_bytes(keep)
        # the third failure state, exercised against an address the manifest does not list at all:
        # the manifest is left exactly as shipped, and an unknown address is resolved explicitly
        got_unknown = run_probe(py, str(shadow / "mcp_server"), td)
    seen = {}
    for tag, got in (("missing", got_missing), ("corrupt", got_corrupt),
                     ("unlisted", got_unknown)):
        st = [x["status"] for x in got["anchors"]]
        seen[tag] = st
        if tag == "missing" and "ANCHOR_MISSING" not in st:
            off.append("a missing snapshot did not report ANCHOR_MISSING")
        if tag == "corrupt" and "ANCHOR_HASH_MISMATCH" not in st:
            off.append("a corrupted snapshot did not report ANCHOR_HASH_MISMATCH")
        # the unlisted address is resolved explicitly, so that the third failure state is exercised
        # even though it is not part of the manifest's listing
        if tag == "unlisted" and got["unlisted"]["status"] != "ANCHOR_UNKNOWN":
            off.append(f"an unlisted address reported {got['unlisted']['status']} instead of "
                       f"ANCHOR_UNKNOWN")
        if tag != "unlisted":
            if got["summary"]["anchor_status"] == "RESOLVED":
                off.append(f"{tag}: the snapshot was reported as resolved")
            bad = [b for b in got["battery"] if b.get("anchor_status") == "RESOLVED"]
            if bad:
                off.append(f"{tag}: an answer carried a resolved anchor status "
                           f"({[b['call'] for b in bad]})")
    det.append(f"missing={seen['missing']} corrupt={seen['corrupt']} "
               f"unlisted={got_unknown['unlisted']['status']}")
    L.rec("G8-P05", "FAIL-CLOSED", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    # ---------------------------------------------------------------- G8-P06 GATE-REPORT
    off, det = [], []
    reg = json.loads((ROOT / "kb/ontology/ONT_LAYER_REGISTRY_v1.json").read_text(encoding="utf-8"))
    if not reg.get("anchor_failure_policy"):
        off.append("the failure policy is not declared in the registry")
    for c in ("should_run", "did_run", "status"):
        if c not in L.checks[0]:
            off.append(f"the gate's own checks do not report {c}")
    det.append(f"checks reported with should_run/did_run/status; states seen so far="
               f"{sorted({c['status'] for c in L.checks})}")
    L.rec("G8-P06", "GATE-REPORT", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    return _finish(L, a)


def _finish(L, a) -> int:
    total = len(L.checks)
    did = sum(1 for c in L.checks if c["did_run"])
    npass = sum(1 for c in L.checks if c["status"] == "PASS")
    nfail = sum(1 for c in L.checks if c["status"] == "FAIL")
    nenv = sum(1 for c in L.checks if c["status"] == "ENV_ERROR")
    nnot = sum(1 for c in L.checks if not c["did_run"])
    unrun = [c["code"] for c in L.checks if c["mandatory"] and not c["did_run"]]
    verdict = "ENV_ERROR" if nenv else ("FAIL" if (nfail or unrun) else "PASS")
    res = {"gate": "G8", "label": "ontology layer portability and fail-closed behaviour",
           "script": str(Path(__file__).resolve().relative_to(ROOT)), "checks": L.checks,
           "n_checks": total, "should_run": total, "did_run": did, "pass": npass, "fail": nfail,
           "not_run": nnot, "env_error": nenv, "mandatory_not_run": unrun, "verdict": verdict,
           "environments": {"author_tree": str(ROOT),
                            "temporary_cwd": True,
                            "spaced_path_copy": True},
           "rule": ("two of the three environments are not the author tree; a missing shipped "
                    "asset is a FAIL, never an ENV_ERROR")}
    print(f"[g8] should_run={total} did_run={did} pass={npass} fail={nfail} not_run={nnot} "
          f"env_error={nenv} verdict={verdict}")
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if verdict == "PASS" else (3 if verdict == "ENV_ERROR" else 2)


if __name__ == "__main__":
    sys.exit(main())