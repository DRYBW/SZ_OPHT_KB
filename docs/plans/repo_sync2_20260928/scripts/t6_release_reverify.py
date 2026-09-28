#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC2 t_719dd225 · T6 — Release v2.3 六件本地重验（零触碰：不下载不上传不改动）
1) 本地 EYEKB_RAG_v2.3.tar 按打包字节边界(4×201326592+176371712)重切 5 卷，逐卷 sha256 对 GitHub Release API digest；
2) tar 全文件 sha 对本地台账 EYEKB_RAG_v2.3.tar.sha256（=Release 附件 .sha256 内容，附件本体 digest 同步核对）；
3) 资产清单=6 件、尺寸面复核。零子进程零网络（API 元数据预先只读拉取存档）。"""
import hashlib
import json
from pathlib import Path

TAR = Path("/home/ubuntu/EYEKB_RAG_v2.3.tar")
LEDGER = Path("/home/ubuntu/EYEKB_RAG_v2.3.tar.sha256")
API = Path("/home/ubuntu/EyeKB_reposync2_work/release_v23_assets.json")
OUT = Path("/home/ubuntu/EYEKB_REPO_STAGING_20260928/docs/plans/repo_sync2_20260928/out/t6_release_reverify.txt")
SIZES = [201326592, 201326592, 201326592, 201326592, 176371712]
CHUNK = 1 << 24


def sha_slice(path, start, length=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(start)
        left = length if length is not None else -1
        while left != 0:
            b = f.read(CHUNK if left < 0 else min(CHUNK, left))
            if not b:
                break
            h.update(b)
            left -= len(b)
    return h.hexdigest()


assets = {a["name"]: a for a in json.loads(API.read_text(encoding="utf-8"))}
lines = []
total = TAR.stat().st_size
assert sum(SIZES) == total, f"tar size {total} != sum(SIZES) {sum(SIZES)}"
lines.append(f"tar bytes={total} == sum(5 part sizes) OK")

ok = True
off = 0
for i, sz in enumerate(SIZES):
    name = f"EYEKB_RAG_v2.3.tar.part_0{i}"
    got = sha_slice(TAR, off, sz)
    want = assets[name]["digest"].removeprefix("sha256:")
    same = got == want
    ok &= same
    lines.append(f"{name}: local-slice-sha={got} github-asset-digest={want} {'MATCH' if same else 'MISMATCH'} size={sz}=={assets[name]['size']}:{sz == assets[name]['size']}")
    off += sz

full = sha_slice(TAR, 0)
led_hash = LEDGER.read_text().split()[0]
same2 = full == led_hash
ok &= same2
lines.append(f"merged-tar recompute={full}")
lines.append(f"local ledger (.tar.sha256 首行)={led_hash} {'MATCH' if same2 else 'MISMATCH'}")
# .tar.sha256 附件本体 digest（GitHub 侧对台账文件的哈希）对台账文件本地重算
led_local = hashlib.sha256(LEDGER.read_bytes()).hexdigest()
asset_led = assets["EYEKB_RAG_v2.3.tar.sha256"]["digest"].removeprefix("sha256:")
same3 = led_local == asset_led
ok &= same3
lines.append(f".tar.sha256 附件本体: local={led_local} github-digest={asset_led} {'MATCH' if same3 else 'MISMATCH'}")
lines.append(f"assets-count={len(assets)} (expect 6)")
ok &= len(assets) == 6
lines.append("T6 语义: 本地 tar 重切 5 卷逐卷==Release 附件 digest ⇒ 本地合并态与 Release 分卷合并态逐字节同一；Release 零触碰。")
verdict = "PASS" if ok else "FAIL"
lines.append(f"T6={verdict}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
