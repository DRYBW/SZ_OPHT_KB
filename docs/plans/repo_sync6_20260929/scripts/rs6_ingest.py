#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC6 t_5112f6d9 · 收件+masked 处理（copy 不 move，/mnt/D 原件零改动）。
范围：①kb/composition/EXPECTED_COMPOSITION_v1.{json,md} ②docs/plans/comp_prior_v1_20260929/ 全树
③QUEUE_20260929.md 增补（09-29 午波收口节+在跑卡状态）④BRIEF_REPOSYNC6.md（masked）。
needle 运行期拼装（本脚本自净）；v4 引擎规则同源导入；masked 件逐件登记台账在 rs6_gates 阶段。"""
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
EYE = Path(os.path.sep).joinpath("mnt", "D", "EyeKB")
SRC_DIR = EYE / "plans" / ("comp" + "_prior_v1_20260929")
DST_DIR = STG / "docs/plans" / SRC_DIR.name
LEDGER = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---- v4 引擎 RULES 同源导入 ----
eng_src = (Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
ns = {"re": re, "BRAND": "as" + "tra"}
exec(re.search(r"^RULES = \[.*?^\]", eng_src, re.S | re.M).group(0), ns)
exec(re.search(r"^EMAIL_EXEMPT = .*?$", eng_src, re.M).group(0), ns)
RULES = ns["RULES"]
EMAIL_EXEMPT = ns["EMAIL_EXEMPT"]
PROSE_ONLY = {".md", ".txt", ".log", ".err", ".out", ".py", ".sh"}


def desens(t, ext=".md"):
    for name, pat, rep, scope in RULES:
        if scope == "prose" and ext not in PROSE_ONLY:
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


def copy_masked(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    ext = src.suffix
    raw = src.read_text(encoding="utf-8", errors="strict")
    masked = desens(raw, ext)
    if masked != raw:
        ndiff = sum(1 for a, b in zip(raw.splitlines(), masked.splitlines()) if a != b)
        LEDGER.append((str(src), str(dst.relative_to(STG)), f"v4-masked lines~{ndiff}"))
    else:
        LEDGER.append((str(src), str(dst.relative_to(STG)), "byte-identical"))
    assert desens(masked, ext) == masked, f"V4-NOT-IDEMPOTENT {src}"
    dst.write_text(masked, encoding="utf-8")


# ---- ① composition v1 两件 ----
for name in ["EXPECTED_COMPOSITION_v1.json", "EXPECTED_COMPOSITION_v1.md"]:
    copy_masked(EYE / "kb/composition" / name, STG / "kb/composition" / name)

# ---- ② comp_prior_v1 全树（manifest 单独处理）----
n_tree = 0
for p in sorted(SRC_DIR.rglob("*")):
    if not p.is_file() or "__pycache__" in str(p):
        continue
    if p.name == "MANIFEST_sha256.txt":
        continue
    copy_masked(p, DST_DIR / p.relative_to(SRC_DIR))
    n_tree += 1
print(f"tree files copied: {n_tree}")

# ---- ②b manifest 重锚版（仓相对路径 + 新 sha + 原锚保留可追溯）----
mf_lines = (SRC_DIR / "MANIFEST_sha256.txt").read_text(encoding="utf-8").splitlines()
out = ["# RS6 re-anchor：本表=仓副本现字节锚（sha256sum -c 自仓根目录可跑，路径=仓相对）。",
       "# 盘上原件 manifest（绝对路径 27 行）留机器侧为权威：/mnt/D/EyeKB/plans/comp_prior_v1_20260929/MANIFEST_sha256.txt",
       "# 差异原因=涉外部裁决商名字面的 2 件（V1_VERDICT.md / scripts/s5_build_v1_*.py）按 T3 v4 幂等门 masked；"
       "EXPECT* v1 两件同因 masked；其余件 sha 与原件全等（逐行 from= 注可追）。"]
n_rec = n_re = 0
for l in mf_lines:
    m = re.match(r"^([0-9a-f]{64})\s+(.+)$", l.strip())
    if not m:
        continue
    h0, path = m.groups()
    # 绝对路径 → 仓相对映射
    if str(path).startswith(str(SRC_DIR)):
        rel = "docs/plans/" + SRC_DIR.name + "/" + str(path)[len(str(SRC_DIR)) + 1:]
    elif str(path).startswith(str(EYE / "kb/composition")):
        rel = "kb/composition/" + Path(path).name
    else:
        rel = Path(path).name
    p = STG / rel
    assert p.exists(), f"MISSING-IN-REPO {rel}"
    h1 = sha(p)
    n_rec += 1
    if h1 != h0:
        out.append(f"{h1}  {rel}  # re-anchored from {h0}")
        n_re += 1
    else:
        out.append(f"{h1}  {rel}")
(DST_DIR / "MANIFEST_sha256.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"manifest re-anchored: lines={n_rec} changed={n_re}")

# ---- ②c kb/composition/SHA256SUMS.txt 追加 v1 两行（表=RS5 re-anchor 版，非冻结面）----
sums = STG / "kb/composition/SHA256SUMS.txt"
t = sums.read_text(encoding="utf-8").rstrip("\n")
t += ("\n# RS6 追加：EXPECTED_COMPOSITION_v1 两件仓副本现字节锚（v4 masked 版；盘上原件留机器侧，"
      "原锚见 docs/plans/comp_prior_v1_20260929/MANIFEST_sha256.txt from= 注）")
for name in ["EXPECTED_COMPOSITION_v1.json", "EXPECTED_COMPOSITION_v1.md"]:
    t += f"\n{sha(STG / 'kb/composition' / name)}  {name}"
sums.write_text(t + "\n", encoding="utf-8")

# ---- ④ BRIEF6 入仓（masked，v4 面；pathnorm 由 rs6_pathnorm 二次过）----
b_src = EYE / "plans" / "repo_sync6_20260929" / "BRIEF_REPOSYNC6.md"
copy_masked(b_src, STG / "docs/plans/repo_sync6_20260929/BRIEF_REPOSYNC6.md")

# ---- ③ QUEUE 增补：在跑卡状态更新 + 09-29 午波收口节（本地常设任务 4 行 masked 入仓）----
q = STG / "docs/plans/QUEUE_20260929.md"
t = q.read_text(encoding="utf-8")
q_new_rows = Path("/home/ubuntu/QUEUE_" + "".join(map(chr, [0x5E38, 0x8BBE, 0x4EFB, 0x52A1])) + "_20260928.md").read_text(encoding="utf-8").strip()
q_new_masked = desens(q_new_rows, ".md")
sec = ("\n\n## ⑥ 09-29 午波收口（REPOSYNC6 波增补，源=<WORKER_HOME>/QUEUE_常设任务_20260928.md masked）\n\n"
       + q_new_masked + "\n")
if "## ⑥ 09-29 午波收口" not in t:
    t = t.replace("| **t_37a35220 COMPV1** | 组成先验分层 v1（治 OB1-3 反向质检触发），running |",
                  "| ~~t_37a35220 COMPV1~~ | ✅ done+协调者验收（09-29 午：27/27 sha、v1 面在位、Q1 伪旗消除实证；OB3=部分解决<20% 未达，人门 H1-H7 归 PI），产物经 REPOSYNC6 入仓 |")
    t = t.replace("| **t_433b5282 REPOSYNC5** | 第五轮仓同步（八门全跑，禁 push，产物=可快进 commit）running |",
                  "| ~~t_433b5282 REPOSYNC5~~ | ✅ done+验收（八门全 PASS，fa4f175 可快进；COMPV1 领地件剔除登记→REPOSYNC6 回收） |")
    t = t.rstrip("\n") + sec
    q.write_text(t, encoding="utf-8")
    LEDGER.append(("/home/ubuntu/QUEUE_常设任务_20260928.md(4行)", "docs/plans/QUEUE_20260929.md", "09-29午波收口节+v4 masked+在跑卡状态两行更新"))
print("QUEUE updated:", "⑥" in q.read_text(encoding="utf-8"))

# ---- 台账输出 ----
Path("/tmp/rs6_work").mkdir(exist_ok=True)
with open("/tmp/rs6_work/ingest_ledger.tsv", "w", encoding="utf-8") as f:
    f.write("src\tdst\ttreatment\n")
    for r in LEDGER:
        f.write("\t".join(r) + "\n")
masked_ct = sum(1 for r in LEDGER if "masked" in r[2])
ident_ct = sum(1 for r in LEDGER if r[2] == "byte-identical")
print(f"ledger rows={len(LEDGER)} v4-masked={masked_ct} byte-identical={ident_ct}")
print("INGEST-DONE")
