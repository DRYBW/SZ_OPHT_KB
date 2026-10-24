#!/usr/bin/env python3
"""FAIRX4A manifest builder (repo-side, verifiable with `sha256sum -c MANIFEST.sha256`).

Run LAST, after every deliverable has stopped changing. Never hashes itself.
In-repo files -> canonical "<sha>  <relpath>" lines.
Large artifacts kept outside git -> '#'-prefixed informational lines (sha + absolute path),
so `sha256sum -c` ignores them instead of reporting "improperly formatted".
"""
import hashlib, os

DST = "/home/ubuntu/EYEKB_REPO/docs/plans/fairex4a_20261024"
MAN = os.path.join(DST, "MANIFEST.sha256")
LARGE = [
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/E_x4a.npy",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/E_x4a_r2.npy",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/E_ref_hra006282.npy",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/E_ref_hra006282_S2.npy",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/q5_x4a_hvg5000.h5ad",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/ref_hra006282.h5ad",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/ref_hra006282_S2.h5ad",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/work/hvg5000_genes.txt",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/out/pred_A1b_scgpt_x4a_rerun.tsv",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/out/pred_A1b_scgpt_x4a_run2_raw.tsv",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/out/pred_A1b_scgpt_x4a_refswap_raw.tsv",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/out/pred_A1b_scgpt_x4a_refswap_run2_raw.tsv",
    "/mnt/D/EyeKB/plans/fairex4a_20261024/out/pred_A1b_scgpt_x4a_refswap_S2_raw.tsv",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


lines = [
    "# FAIRX4A manifest — verify from this directory:  sha256sum -c MANIFEST.sha256",
    "# Excluded by design: this manifest itself; nothing else is written at verify time.",
    "# Lines starting with '#' are informational and ignored by sha256sum -c.",
    "# LARGE ARTIFACTS (kept outside git, sha256 + absolute path):",
]
for p in LARGE:
    if os.path.exists(p):
        lines.append(f"# LARGE {sha(p)}  {p}")
    else:
        lines.append(f"# LARGE MISSING  {p}")
lines.append("#")
rels = []
for root, dirs, files in os.walk(DST):
    dirs[:] = [d for d in dirs if d != ".git"]
    for fn in sorted(files):
        p = os.path.join(root, fn)
        if p == MAN:
            continue
        rels.append(os.path.relpath(p, DST))
rels.sort()
for rel in rels:
    lines.append(f"{sha(os.path.join(DST, rel))}  {rel}")
with open(MAN, "w") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"MANIFEST_OK files={len(rels)} large={sum(1 for p in LARGE if os.path.exists(p))} -> {MAN}")