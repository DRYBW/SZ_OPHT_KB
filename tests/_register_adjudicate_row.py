#!/usr/bin/env python3
"""Register the optional second-answer layer and refresh two drifted rows.

Re-run safe: it recomputes the sha/bytes/mtime from disk every time, and it will not add a
second L3-06 row.
"""
import hashlib
import os
import time

P = "docs/W3_PIPELINE_REGISTRY.tsv"
NEWVER = "v(2026-10-29 ADJUDICATE-LAYER 可选第二答案层)"


def meta(rel):
    b = open(rel, "rb").read()
    return (hashlib.sha256(b).hexdigest(), str(len(b)),
            time.strftime("%F %T", time.localtime(os.path.getmtime(rel))))


rows = [l.rstrip("\n").split("\t") for l in open(P, encoding="utf-8")]
hdr = rows[0]
I = {c: i for i, c in enumerate(hdr)}
n = 0
for r in rows[1:]:
    if len(r) < len(hdr):
        continue
    if r[I["item_id"]] in ("L2-01", "L2-03"):
        sha, b, m = meta(r[I["path"]])
        r[I["sha256"]], r[I["bytes"]], r[I["mtime"]], r[I["version"]] = sha, b, m, NEWVER
        n += 1

if not any(len(r) > 1 and r[I["item_id"]] == "L3-06" for r in rows[1:]):
    tpl = [r for r in rows[1:] if len(r) >= len(hdr) and r[I["item_id"]] == "L3-04"][0]
    new = list(tpl)
    new[I["item_id"]] = "L3-06"
    new[I["item_name"]] = "可选第二答案层（模型判读·不改库答案·默认关）"
    new[I["category"]] = "判读版本 D(辅助)"
    new[I["path"]] = "pipeline/adjudicate.py"
    new[I["version"]] = NEWVER
    new[I["authority"]] = "AUTHORITATIVE(辅助，默认关)"
    new[I["change_gate"]] = ("只经镜像仓版本件；零 LLM 默认（--adjudicate 或 EYEKB_ADJUDICATE=1 "
                             "才生效，需用户自带 OPENAI_* 通道）")
    sha, b, m = meta("pipeline/adjudicate.py")
    new[I["sha256"]], new[I["bytes"]], new[I["mtime"]] = sha, b, m
    new[I["state"]] = "ON_DISK"
    new[I["evidence"]] = (f"盘上实测：{b} B；两答案并列政策=库答案永不覆盖（adjudication 与 "
                          "kb_marker 分列）；该列非确定性，报告必须带模型名与运行日期；"
                          "无通道时静默降级只报库答案；默认路径不出现 adjudication 键")
    rows.append(new)
    print("appended L3-06")
else:
    print("L3-06 already present, not duplicated")

open(P, "w", encoding="utf-8").write("\n".join("\t".join(r) for r in rows) + "\n")
print(f"refreshed rows: {n} | total ledger rows: {len(rows) - 1}")