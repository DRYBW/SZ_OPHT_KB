#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Freeze a service baseline by content fingerprint.

One command rebuilds the whole frozen set, and re-running it in the same checkout returns the same
bytes:

    python3 docs/plans/l5_ontlayer_20261022/scripts/01_baseline_freeze.py \\
        --service-python <interpreter that can import the service>

What is frozen
    code                 every file of the declared service surface, by sha256, repository-relative
    release identity     the recorded identity of the checkout being frozen
    default configuration the observed value of every declared behaviour toggle, with the meaning of
                         its off state
    active libraries     the interpreter, the package versions it actually resolves, and the marker
                         library set the shipped loader builds by default
    scoring / guard      the declared constants that decide scoring, guards and stage routing, read
                         out of the shipped module in that interpreter
    recorded requests    the raw response of every call in the recorded request set, kept as md5 +
                         byte count per call (the full texts stay in the evidence root)
    panel identity       the live reading of the repository's own panel probe, with the recorded
                         baseline it is compared against

What a frozen set is named after
    The baseline revision. The file is `BASELINE_FREEZE_<rev12>.json`, so freezing a second revision
    never overwrites the first, and `BASELINE_FREEZE.json` is a pointer naming the frozen baseline.
    Re-run with `--revision <rev>` in a checkout of that revision to reproduce the same bytes.

What is deliberately NOT in it
    timestamps, mtimes, commit ids and the working directory: they move without a byte of the
    service moving. The frozen set is byte-reproducible as a result - run it twice and diff.

Exit codes: 0 = frozen; 2 = the checkout does not match the revision asked for (nothing written);
            3 = the repository or the interpreter could not be used.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents)
            if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
OUT = ROOT / "docs/plans/l5_ontlayer_20261022/out"
SERVICE_SURFACE_PREFIXES = ("mcp_server/", "kb/markers/", "kb/baselines/", "kb/priors/",
                            "kb/ontology/", "kb/literature_db/", "kb/vk_literature_index/",
                            "tests/", "scripts/", "clients/", "literature_db/",
                            "docs/RELEASE_IDENTITY.json", "docs/RELEASE_MANIFEST_v1.json")
TOGGLES = {
    "EYEKB_ACT_V6": "unset = the v6 activation behaviour of the release",
    "EYEKB_ACT_ANTSEG": "0/false/off/no = the pre-flip default (anterior-segment activation off)",
    "EYEKB_KBGOV_B5": "unset = the release default for the vocabulary-governance rule B5",
    "EYEKB_CN_REWRITE": "0/off/false/no = Chinese query rewrite off (pre-2026-10-05 behaviour)",
    "EYEKB_SPECIES_ROUTE": "unset = OFF (the byte-exact pre-wiring species route)",
    "EYEKB_ONT_LAYER": "unset/empty = no ontology tool advertised (the capability is registered OFF)",
    "EYEKB_ABSTAIN_REASON": "unset = no abstention-reason key in the response",
    "EYEKB_FALLBACK_WIDEN": "unset = no fallback widening",
    "EYEKB_STATE_GUARD": "unset = the release default for the soft-flag state guard",
    "EYEKB_DB_DIR": "unset = resolve the corpus through the pointer file, then the repository copy",
}
GUARD_CONSTANTS = ["KBGOV_T_FROZEN", "KBGOV_AMBIG", "STAGE_TIERS", "STAGE_FOLD",
                   "STAGE_ACCEPTED_LITERALS", "STAGE_UNRECOGNISED_RULE", "ANTSEG_DEFAULT_LIBS",
                   "ANTSEG_MIN_SHARED", "ANTSEG_MARGIN", "MARKER_LIBS", "DEFAULT_DB_DIR"]
PACKAGES = ["mcp", "pydantic", "numpy", "pandas", "pyarrow", "PyYAML",
            "sentence-transformers"]


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def normalise(value, root: Path):
    if isinstance(value, str):
        return value.replace(str(root), "<REPO>")
    if isinstance(value, list):
        return [normalise(v, root) for v in value]
    if isinstance(value, dict):
        return {k: normalise(v, root) for k, v in value.items()}
    return value


def git(args, root=ROOT, timeout=300) -> str:
    p = subprocess.run(["git", "-C", str(root)] + args, capture_output=True, text=True,
                       timeout=timeout)
    return p.stdout.strip() if p.returncode == 0 else ""


def service_surface(root: Path):
    """Files of the declared surface, hashed from the checkout. Absent paths are recorded as absent
    rather than dropped, so a surface that shrank is visible."""
    files, absent = {}, []
    for prefix in SERVICE_SURFACE_PREFIXES:
        p = root / prefix
        if p.is_file():
            files[prefix] = sha256_of(p)
        elif p.is_dir():
            n = 0
            for f in sorted(p.rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
                    files[str(f.relative_to(root))] = sha256_of(f)
                    n += 1
            if n == 0:
                absent.append(prefix)
        else:
            absent.append(prefix)
    return files, absent


def introspect(py: str, code: str, root: Path):
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    p = subprocess.run([py, "-c", code], cwd=str(root), env=env, capture_output=True, text=True,
                       timeout=900)
    if p.returncode != 0:
        return {"_status": "FAILED", "_stderr": p.stderr.strip()[-500:]}
    return json.loads(p.stdout.strip().splitlines()[-1])


def drive_replay(root: Path, py: str) -> dict:
    """Run the recorded request set in this checkout, through the module that the card ships."""
    spec = importlib.util.spec_from_file_location(
        "l5_replay", root / "docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.SERVER = root / "mcp_server" / "server.py"
    run = asyncio.run(mod.drive())
    out = {}
    for k, v in run["calls"].items():
        out[k] = {"md5": v["md5"], "bytes": v["bytes"],
                  "md5_normalised": hashlib.md5(
                      v["text"].replace(str(root), "<REPO>").encode()).hexdigest()}
    out["_tools"] = run["tools"]
    out["_refused"] = run["refused"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--service-python", default=os.environ.get("EYEKB_G7_PY")
                    or os.environ.get("EYEKB_G3_PY") or sys.executable)
    ap.add_argument("--revision", default="", help="the revision being frozen (default: HEAD)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    head = git(["rev-parse", "HEAD"])
    if not head:
        print("CANNOT FREEZE: this is not a git checkout, so no revision can be named.")
        return 3
    rev = a.revision or head
    rev_full = git(["rev-parse", rev]) or rev
    if a.revision and rev_full != head:
        print(f"CANNOT FREEZE: asked for {rev_full[:12]} but this checkout is at {head[:12]}. "
              f"A baseline is frozen in a checkout of the revision it describes; nothing was "
              f"written.")
        return 2

    surface, absent = service_surface(ROOT)
    rec_path = ROOT / "docs/RELEASE_IDENTITY.json"
    identity = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.is_file() else None
    id_check = git(["status", "--porcelain"]) == ""
    core = f'''
import json, sys
sys.path.insert(0, "mcp_server")
import eyekb_core as c

def norm(v):
    """Deterministic rendering: a set's iteration order depends on the interpreter's hash seed, so
    every container is rendered as a sorted, typed record. Without this the frozen set changes
    between two runs of the same code on the same bytes - which is exactly what a fingerprint must
    not do."""
    if isinstance(v, (set, frozenset)):
        return {{"type": type(v).__name__, "items": sorted(str(x) for x in v)}}
    if isinstance(v, dict):
        return {{"type": "dict", "items": [[str(k), norm(x)] for k, x in sorted(v.items(), key=lambda kv: str(kv[0]))]}}
    if isinstance(v, (list, tuple)):
        return {{"type": type(v).__name__, "items": [norm(x) for x in v]}}
    if v is None:
        return None
    return str(v)

out = {{"constants": {{}}, "packages": {{}}}}
for name in {GUARD_CONSTANTS!r}:
    out["constants"][name] = norm(getattr(c, name, None))
import importlib.metadata as md
for pkg in {PACKAGES!r}:
    try:
        out["packages"][pkg] = md.version(pkg)
    except Exception:
        out["packages"][pkg] = None
import platform
out["python"] = platform.python_version()
out["interpreter"] = sys.executable
print(json.dumps(out))
'''
    got = introspect(a.service_python, core, ROOT)
    responses = drive_replay(ROOT, a.service_python)

    fixture = json.loads((ROOT / "tests/fixtures/tool_panel_baseline.json").read_text(encoding="utf-8"))
    probe = subprocess.run([a.service_python, str(ROOT / "tests/probe_tool_panel_identity.py"),
                            "--baseline", str(ROOT / "tests/fixtures/tool_panel_baseline.json")],
                           cwd=str(ROOT), capture_output=True, text=True, timeout=900,
                           env={**{k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
                                "EYEKB_ONT_LAYER": ""})
    live = {}
    for line in probe.stdout.splitlines():
        s = line.strip()
        if s.startswith('"legacy_panel"') or s.startswith('"full_panel"'):
            k, _, v = s.partition(":")
            live[k.strip('"')] = v.strip().strip('",')
    panel_ok = (probe.returncode == 0 and live
                and live.get("legacy_panel") == fixture.get("legacy_panel")
                and live.get("full_panel") == fixture.get("full_panel"))

    frozen = {
        "schema": "eyekb-baseline-freeze/1.0",
        "card": "L5 baseline freeze + read-only Cell Ontology explanation layer",
        "baseline_revision": rev_full,
        "baseline_revision_short": rev_full[:12],
        "rebuild_command": ("python3 docs/plans/l5_ontlayer_20261022/scripts/01_baseline_freeze.py "
                            "--service-python <interpreter> --revision " + rev_full[:12]),
        "checkout": {"worktree_clean": id_check,
                     "note": "recorded so a reader knows whether the fingerprint is a commit or a "
                             "working tree; the working-directory path itself is deliberately absent"},
        "release_identity": normalise(identity, ROOT) if identity else None,
        "code_fingerprint": {
            "coverage": {"prefixes": list(SERVICE_SURFACE_PREFIXES),
                         "rule": "every file under these prefixes, sha256, repository-relative"},
            "n_files": len(surface),
            "surface_digest": hashlib.sha256(
                "".join(f"{p}  {h}\n" for p, h in sorted(surface.items())).encode()).hexdigest(),
            "declared_but_absent": absent,
            "files": surface,
        },
        "default_configuration": {
            "toggles": {k: {"observed": os.environ.get(k), "off_state_meaning": v}
                        for k, v in TOGGLES.items()},
            "note": "observed = the raw value in this process's environment; null = unset = release "
                    "default",
        },
        "active_libraries": {
            "interpreter": normalise(got.get("interpreter") or a.service_python, ROOT),
            "python": got.get("python"),
            "packages": got.get("packages"),
            "marker_libraries": normalise((got.get("constants") or {}).get("MARKER_LIBS"), ROOT),
            "note": ("packages are the versions this interpreter actually resolves; "
                     "marker_libraries is the set the shipped loader builds by default, as a sorted "
                     "record"),
        },
        "scoring_and_guard_configuration": {
            "constants": normalise(got.get("constants"), ROOT),
            "source": ("mcp_server/eyekb_core.py, read out of the shipped module in the same "
                       "interpreter that would serve a request (absent -> null, never omitted)"),
        },
        "recorded_request_set": {
            "coverage": "the 12-call tool panel + a 42-call development-stage sweep + 1 identity call",
            "n_calls": len([k for k in responses if not k.startswith("_")]),
            "tools": responses.get("_tools"),
            "refused": responses.get("_refused"),
            "responses": {k: v for k, v in responses.items() if not k.startswith("_")},
            "digest_rule": ("md5 = the raw response bytes of this checkout; md5_normalised = the "
                            "same text with this checkout's path replaced by <REPO>. 27 of the 55 "
                            "answers echo the install path, so raw digests are comparable only "
                            "between runs at the SAME absolute path (which is where the "
                            "byte-identity comparison of this card was taken), while the "
                            "normalised digests are comparable between checkouts and are what "
                            "this baseline is stated in"),
            "note": "the raw texts themselves stay in the evidence root of the card",
        },
        "panel_identity": {
            "probe": "tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json",
            "live": live,
            "recorded": {"legacy_panel": fixture.get("legacy_panel"),
                         "full_panel": fixture.get("full_panel")},
            "probe_rc": probe.returncode,
            "verdict": ("IDENTITY PASS" if panel_ok else
                        "NOT CONFIRMED - read the probe output before citing this baseline"),
        },
        "volatile_fields_excluded": ["timestamps", "mtimes", "working directory", "environment dump"],
    }

    blob = json.dumps(frozen, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    target = out / f"BASELINE_FREEZE_{rev_full[:12]}.json"
    same = target.is_file() and target.read_text(encoding="utf-8") == blob
    target.write_text(blob, encoding="utf-8")
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    (out / f"BASELINE_FREEZE_{rev_full[:12]}.sha256").write_text(
        f"{digest}  {target.name}\n", encoding="utf-8")
    pointer = {"schema": "eyekb-baseline-freeze-pointer/1.0",
               "frozen_baseline": target.name,
               "sha256": digest,
               "baseline_revision": rev_full,
               "n_calls": frozen["recorded_request_set"]["n_calls"],
               "panel_verdict": frozen["panel_identity"]["verdict"],
               "rule": ("the frozen baseline of this card. Rebuild it in a checkout of "
                        "baseline_revision with the command recorded inside it; the file is named "
                        "after the revision so freezing another revision cannot overwrite it.")}
    (out / "BASELINE_FREEZE.json").write_text(
        json.dumps(pointer, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    shown = target.relative_to(ROOT) if str(target).startswith(str(ROOT)) else target
    print(f"frozen -> {shown}  sha256={digest}")
    print(f"re-run identical to the file that was already there: {same}")
    print(json.dumps({"baseline_revision": rev_full[:12],
                      "release_id": (identity or {}).get("release_id"),
                      "service_files": len(surface), "declared_but_absent": absent,
                      "packages": got.get("packages"),
                      "panel_verdict": frozen["panel_identity"]["verdict"],
                      "probe_rc": probe.returncode},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())