#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINKKEY manifest 生成器（必须在所有交付件写完*之后*跑，且为最后一次写入）。

纪律（均来自本室已固化的 manifest 三连坑）:
  * 清单不含自身（文件不可能含自身哈希）
  * 信息性行一律 '#' 前缀（否则 sha256sum -c 报 lines improperly formatted）
  * 运行期写入件（run_time.log 等）显式排除
  * 输出为 canonical 两空格格式： '<sha256>' + '  ' + <path>
  * 本脚本 stdout 只到终端，不 tee 进本目录
"""
import hashlib, os

OUT = "/mnt/D/EyeKB/plans/consistency_20261024/LINKKEY_out"
MANIFEST = "MANIFEST.sha256"
# 运行期/自指/非交付件 → 排除（并写明理由）
EXCLUDE = {
    MANIFEST: "清单自身",
    "run_time.log": "运行期写入件（/usr/bin/time 输出），每次重跑都变",
    "MANIFEST_CHECK.txt": "运行期自检输出，每次重跑都变",
}
INPUTS = [
    "/mnt/D/EyeKB/plans/kbreach_fix_20261024/clone_check/kb/link_registry/LINK_REGISTRY_v1.jsonl",
    "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    lines = ["# LINKKEY v1 MANIFEST — 逐件 sha256（canonical 两空格格式，可在本目录直接 sha256sum -c）",
             "# 生成: LINKKEY_out/make_manifest.py；清单不含自身；运行期写入件已排除（理由见脚本 EXCLUDE）",
             "# 排除: " + "; ".join(f"{k}={v}" for k, v in EXCLUDE.items())]
    pairs = []
    for fn in sorted(os.listdir(OUT)):
        if fn in EXCLUDE:
            continue
        p = os.path.join(OUT, fn)
        if os.path.isfile(p):
            pairs.append((sha(p), fn))
    for p in INPUTS:
        pairs.append((sha(p), p))
    body = [f"{h}  {n}" for h, n in pairs]
    with open(os.path.join(OUT, MANIFEST), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n" + "\n".join(body) + "\n")
    print(f"entries={len(pairs)} (self-hashed files={len(pairs)-len(INPUTS)}, inputs={len(INPUTS)})")
    for h, n in pairs:
        print(f"  {h[:16]}  {os.path.basename(n)}")


if __name__ == "__main__":
    main()