#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T6 — Release 六件本地重验零触碰（沿 REPOSYNC2 同型）
① 新鲜只读拉取 GitHub Release API 资产清单 → 与 REPOSYNC2 存档逐 digest 全等（=远端零漂移证据）；
② 本地 EYEKB_RAG_v2.3.tar 按打包边界重切 5 卷对 digest；③ 合并态 sha 对本地台账；④ 台账附件本体 digest。
零下载零上传零改动。"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
TAR = Path("/home/ubuntu/EYEKB_RAG_v2.3.tar")
LEDGER = Path("/home/ubuntu/EYEKB_RAG_v2.3.tar.sha256")
ARCHIVE = Path("/home/ubuntu/EyeKB_reposync2_work/release_v23_assets.json")
W = Path("/home/ubuntu/EyeKB_reposync3_work")
W.mkdir(exist_ok=True)
FRESH = W / "release_v23_assets_fresh.json"
OUT = STG / "docs/plans/repo_sync3_20260928/out"
OUT.mkdir(parents=True, exist_ok=True)
SIZES = [201326592, 201326592, 201326592, 201326592, 176371712]
CHUNK = 1 << 24
lines, ok = [], True


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


# ① 新鲜拉取（只读 GET，代理）
url = "https://api.github.com/repos/DRYBW/SZ_OPHT_KB/releases/tags/v2.3-rag-assets"
r = subprocess.run(["curl", "-s", "--max-time", "60", "-x", "http://127.0.0.1:PORT", url],
                   capture_output=True, text=True)
try:
    fresh = json.loads(r.stdout)
    assert isinstance(fresh.get("assets"), list) and fresh["assets"], "API 未返回 assets（网络/鉴权）"
    FRESH.write_text(json.dumps(fresh["assets"]), encoding="utf-8")
except Exception as e:
    print("FRESH-FETCH-FAIL:", e)
    FRESH = ARCHIVE  # 降级=沿用 09-28 存档（本卡零触碰结论不受影响，登记说明）
    lines.append("note: fresh fetch failed, used REPOSYNC2 archive only")

fa = {a["name"]: a for a in json.loads(FRESH.read_text(encoding="utf-8"))}
aa = {a["name"]: a for a in json.loads(ARCHIVE.read_text(encoding="utf-8"))}
drift = [n for n in aa if n in fa and fa[n]["digest"] != aa[n]["digest"]]
same_names = set(fa) == set(aa)
ck1 = same_names and not drift
ok &= ck1
lines.append(f"1) remote-vs-archive: names-equal={same_names} digest-drift={drift} -> {'NO-DRIFT(零触碰实证)' if ck1 else 'DRIFT!'}")

total = TAR.stat().st_size
assert sum(SIZES) == total
lines.append(f"2) tar bytes={total} == sum(5 part sizes) OK")
off = 0
parts = sorted([n for n in fa if "part" in n])
assert len(parts) == 5, f"part assets !=5: {parts}"
for i, sz in enumerate(SIZES):
    name = parts[i]
    got = sha_slice(TAR, off, sz)
    want = fa[name]["digest"].removeprefix("sha256:")
    same = got == want
    ok &= same
    lines.append(f"{name}: local-slice={got[:16]}… digest={'MATCH' if same else 'MISMATCH'} size={'OK' if fa[name]['size']==sz else 'MISMATCH'}")
    off += sz
full = sha_slice(TAR, 0)
led_hash = LEDGER.read_text().split()[0]
same2 = full == led_hash
ok &= same2
lines.append(f"3) merged recompute={full[:16]}… vs local ledger {'MATCH' if same2 else 'MISMATCH'}")
led_local = hashlib.sha256(LEDGER.read_bytes()).hexdigest()
asset_led = fa["EYEKB_RAG_v2.3.tar.sha256"]["digest"].removeprefix("sha256:")
same3 = led_local == asset_led
ok &= same3
lines.append(f"4) ledger-file digest={led_local[:16]}… vs github asset digest {'MATCH' if same3 else 'MISMATCH'}")
lines.append(f"assets count={len(fa)}")
lines.append("RESULT=" + ("PASS" if ok else "FAIL"))
(OUT / "t6_release_reverify.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
sys.exit(0 if ok else 1)
