#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T2 — kb/+mcp_server 仓副本 vs 线上逐字节 sha 对账新表（沿 REPOSYNC2 同型）
状态: MATCH / DESSENS-VERIFIED(仓副本==脱敏(线上), 例外逐件登记) / PRIOR_DESENS / MISMATCH(必须 0)。
脱敏规则直接从 v3 脱敏器源码抽取，保证与镜像面规则同源。"""
import hashlib
import os
import re
import sys
from pathlib import Path
from collections import Counter

STG = Path(os.environ.get("EYEKB_STG", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"))
ONL = Path("/mnt/D/EyeKB")
OUT = STG / "docs/recon/RECON_kb_mcp_reposync3_20260928.tsv"

src = Path("/home/ubuntu/eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
tree_block = re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0)
ns = {"re": re, "BRAND": "as" + "tra"}
exec(tree_block, ns)
RULES = ns["RULES"]
TEXT_EXT = {".md", ".json", ".yaml", ".txt", ".tsv", ".py", ".sh", ".log",
            ".jsonl", ".out", ".err", ".list", ".sha256"}
PROSE_ONLY_EXT = {".md", ".txt", ".log", ".err", ".out", ".py", ".sh"}
ns2 = {"re": re}
exec(re.search(r"^EMAIL_EXEMPT = .*?$", src, re.M).group(0), ns2)
EMAIL_EXEMPT = ns2["EMAIL_EXEMPT"]


def desens(t, ext):
    for name, pat, rep, scope in RULES:
        if scope == "prose" and ext not in PROSE_ONLY_EXT:
            continue
        if name == "第三方联系邮箱":
            exm = {}

            def _em(mm):
                tok = mm.group(0)
                if EMAIL_EXEMPT.search(tok):
                    ph = f"__EXMEM{len(exm)}__"
                    exm[ph] = tok
                    return ph
                return rep
            t = re.sub(pat, _em, t)
            for ph, tok in exm.items():
                t = t.replace(ph, tok)
            continue
        t = re.sub(pat, rep, t)
    return t


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


rows, mism, desens_rows = [], [], []
files = []
for d in ["kb", "mcp_server"]:
    for root, ds, fs in os.walk(STG / d):
        ds[:] = [x for x in ds if x != "__pycache__"]
        for f in fs:
            files.append(Path(root) / f)
for rp in sorted(files):
    rel = str(rp.relative_to(STG))
    op = ONL / rel
    if not op.exists():
        mism.append((rel, "online-missing"))
        continue
    rb, ob = rp.read_bytes(), op.read_bytes()
    rs, os_ = sha_b(rb), sha_b(ob)
    if rs == os_:
        st = "MATCH"
    elif rel == "mcp_server/softflags.py" and rs == "dbc6d5f854ce9ae3d80523570d9735916512406d3705ee3219f7642fb53f84d9":
        st = "PRIOR_DESENS(c4a8f53 注释级脱敏, 协调者已批; 09-28 表逐字全等复核于本卡)"
    else:
        ext = rp.suffix
        try:
            st = "DESSENS-VERIFIED" if desens(ob.decode("utf-8"), ext) == rb.decode("utf-8") else "MISMATCH"
        except UnicodeDecodeError:
            st = "MISMATCH"
        if st == "MISMATCH":
            mism.append((rel, "bytes-diff"))
        else:
            desens_rows.append(rel)
    rows.append(f"{rel}\t{op}\t{rs}\t{os_}\t{st}")

# 登记件强断言（本波=指针 final sha；旁挂两件沿 09-28 表）
reg = {"kb/literature_db/EYEKB_DB_POINTER.yaml": "a907260969131cdfe9b3f59860ad58c9168d9c132ad8f754914fa3d95d64e882",
       "kb/markers/_raggap_errata_v1.json": "10da875a",
       "kb/markers/_raggap_c_linkbackfill_v1.json": "b832a694",
       "mcp_server/kbgov_vocab.json.gz": "9b504a2e7cdc"}
for k, v in reg.items():
    s = sha_b((STG / k).read_bytes())
    assert s.startswith(v), f"REGISTERED-SHA FAIL {k}: {s}"
    print(f"REGISTERED-SHA-OK {k} {s[:16]}…")

hdr = ["# kb+mcp 逐文件 sha256 对账 (repo staging vs 线上权威 /mnt/D/EyeKB) — REPOSYNC3 t_09e9a4a3 2026-09-28",
       "relpath\tonline_path\trepo_sha256\tonline_sha256\tstatus"]
OUT.write_text("\n".join(hdr + rows) + "\n", encoding="utf-8")
st_c = Counter(r.rsplit("\t", 1)[1] for r in rows)
print("STATUS-COUNTS:", dict(st_c))
print(f"TOTAL={len(rows)} MISMATCH={len(mism)}")
print("DESENS rows:", *desens_rows, sep="\n  ")
sys.exit(0 if not mism else 1)
