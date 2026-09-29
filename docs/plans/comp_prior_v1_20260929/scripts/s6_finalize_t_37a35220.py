#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s6_finalize_t_37a35220.py — 零触碰自证(后 sha)+ MANIFEST_sha256.txt"""
import subprocess, pathlib, hashlib, datetime
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
pre = (OUT / "logs/SHA_BASELINE_pre_20260929.txt").read_text().strip().splitlines()
lines = [ln.split() for ln in pre if ln.strip()]
# 台账生成时分两段 cd: 前14条根=kb/composition, 其余根=plans/evalset (相对路径还原)
R = ["/mnt/D/EyeKB/kb/composition/"]*14 + ["/mnt/D/EyeKB/plans/evalset/"]*(len(lines)-14)
bad = []
for (h, rel), root in zip(lines, R):
    path = root + rel
    cur = hashlib.sha256(open(path, "rb").read()).hexdigest() if pathlib.Path(path).exists() else None
    if cur != h: bad.append((path, "MISSING" if cur is None else "CHANGED"))
print("PRE-entry:", len(lines), "VIOLATIONS:", len(bad), bad)
(OUT / "logs/SHA_POST_verify.txt").write_text(
    f"verified {datetime.datetime.now().isoformat()} entries={len(lines)} violations={len(bad)} {bad}\n")
# stat 快照对照 (大文件)
post_stat = subprocess.run(
    ["stat", "-c", "%n|%s|%y"] + [l.split("|")[0] for l in (OUT / "logs/STAT_BASELINE_pre_20260929.txt").read_text().splitlines()],
    capture_output=True, text=True).stdout
same = post_stat.strip() == (OUT / "logs/STAT_BASELINE_pre_20260929.txt").read_text().strip()
print("STAT snapshot identical:", same)
(OUT / "logs/STAT_POST_verify.txt").write_text(post_stat)
# MANIFEST
mani = []
for p in sorted(OUT.rglob("*")) + sorted(pathlib.Path("/mnt/D/EyeKB/kb/composition").glob("EXPECTED_COMPOSITION_v1.*")):
    if p.is_file():
        mani.append(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p))
(OUT / "MANIFEST_sha256.txt").write_text("\n".join(mani) + "\n")
print("manifest entries:", len(mani))
