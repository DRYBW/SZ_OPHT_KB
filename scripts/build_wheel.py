#!/usr/bin/env python3
"""Build the distributable with the release identity record travelling inside it.

Why this exists: mcp_server/server.py resolves the release identity record at
<repo>/docs/RELEASE_IDENTITY.json. In an installed wheel there is no repository, so a wheel built
straight from the tree ships a service that answers release_id="unrecorded" and cannot say which
release of the knowledge base it is serving.

The record is never committed a second time. It is copied into the package for the duration of the
build and removed afterwards, in a finally block, so the working tree is left exactly as it was and
the identity hash never has to account for a copy of itself.

Usage:
    python3 scripts/build_wheel.py [--outdir dist]
"""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "RELEASE_IDENTITY.json"
STAGED = ROOT / "mcp_server" / "RELEASE_IDENTITY.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "dist"))
    a = ap.parse_args()
    out = Path(a.outdir)

    if not RECORD.exists():
        print(f"FATAL: {RECORD} missing; run scripts/release_identity.py first", file=sys.stderr)
        return 2
    if STAGED.exists():
        print(f"FATAL: {STAGED} already present; refusing to overwrite a tracked file", file=sys.stderr)
        return 2

    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    print(f"release_id      : {rec.get('release_id')}")
    print(f"taken_at_commit : {rec.get('taken_at_commit')}")
    print(f"record sha256   : {sha(RECORD)}")

    try:
        shutil.copyfile(RECORD, STAGED)
        if sha(STAGED) != sha(RECORD):
            print("FATAL: staged copy differs from the record", file=sys.stderr)
            return 2
        cmd = [sys.executable, "-m", "build", "--outdir", str(out)]
        print("running:", " ".join(cmd))
        rc = subprocess.call(cmd, cwd=str(ROOT))
        if rc != 0:
            return rc
    finally:
        if STAGED.exists():
            STAGED.unlink()
            print("staged copy removed from the working tree")

    wheels = sorted(out.glob("*.whl"))
    if not wheels:
        print("FATAL: no wheel produced", file=sys.stderr)
        return 2
    w = wheels[-1]
    import zipfile
    names = zipfile.ZipFile(w).namelist()
    inside = [n for n in names if n.endswith("RELEASE_IDENTITY.json")]
    print(f"wheel           : {w.name} ({w.stat().st_size/1e6:.2f} MB, {len(names)} entries)")
    print(f"identity inside : {inside if inside else 'MISSING'}")
    if not inside:
        print("FATAL: the wheel does not carry the release identity record", file=sys.stderr)
        return 2
    print("OK: the built wheel can identify its own release")
    return 0


if __name__ == "__main__":
    sys.exit(main())