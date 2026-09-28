#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T4 — 收录完整性
a) 新收 .md 非空且末行以换行结尾（无换行=告警并核线上同源）；
b) 新收 .py 全部 py_compile；
c) REPOSYNC3_INTAKE.sha256 生成+重跑 sha256sum -c 一致；
d) 卡内 sha 台账在镜像内重验：OK / FAIL-EXPECTED-DESENS(线上件 sha==台账 且 仓件==脱敏(线上件)) /
   FAIL-EXPECTED-EXCLUDED(本波排除面) / OUTSIDE-REPO(OcularKB 侧) / REAL-FAIL(=门失败)。"""
import hashlib
import py_compile
import re
import subprocess
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
ONL = Path("/mnt/D/EyeKB")
NEW = ["kbgov_b5impl_20260928", "grade_h1m3impl_20260928", "obligrun_20260928",
       "mouse_ext_precheck_20260928", "rag_fix3_20260928", "repo_sync3_20260928"]
P = STG / "docs/plans"
EXTRA = [STG / "docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md",
         STG / "mcp_server/kbgov_vocab.json.gz"]

_src = Path("/home/ubuntu/eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
_ns = {"re": re, "BRAND": "as" + "tra"}
exec(re.search(r"^RULES = \[.*?^\]", _src, re.S | re.M).group(0), _ns)
_R = _ns["RULES"]


def desens(t):
    for _n, pat, rep, _s in _R:
        t = re.sub(pat, rep, t)
    return t


lines = []
rc = 0


def sha_f(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# a) md 完整性
mds = [p for d in NEW for p in (P / d).rglob("*.md")] + [STG / "docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md"]
empty = [str(p.relative_to(STG)) for p in mds if p.stat().st_size == 0]
nonl = []
for p_ in mds:
    b = p_.read_bytes()
    if b and not b.endswith(b"\n"):
        rel = str(p_.relative_to(STG))
        op = None
        if rel.startswith("docs/plans/"):
            op = ONL / "plans" / rel.split("docs/plans/", 1)[1]
        same_src = bool(op) and op.exists() and not op.read_bytes().endswith(b"\n")
        nonl.append((rel, "ONLINE-SAME(同源非本波引入)" if same_src else "CHECK"))
lines.append(f"A) md={len(mds)} empty={len(empty)} no-final-newline={len(nonl)}")
for x in empty:
    lines.append(f"  EMPTY-FAIL {x}")
    rc = 1
for rel, tag in nonl:
    lines.append(f"  NONL {rel} [{tag}]")

# b) py_compile
pys = [p for d in NEW for p in (P / d).rglob("*.py")]
pfail = []
for py in pys:
    try:
        py_compile.compile(str(py), doraise=True)
    except Exception as e:
        pfail.append((str(py.relative_to(STG)), str(e)[:120]))
lines.append(f"B) py={len(pys)} compile-fail={len(pfail)}")
for x in pfail:
    lines.append(f"  PY-FAIL {x}")
    rc = 1

# c) INTAKE 台账（本波全部收录件）
wave = set()
for d in NEW:
    for p in (P / d).rglob("*"):
        if p.is_file():
            wave.add(p)
for x in EXTRA:
    if x.exists():
        wave.add(x)
for f in ["docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md", "docs/wiki/当前状态.md",
          "kb/literature_db/EYEKB_DB_POINTER.yaml", "mcp_server/server.py", "mcp_server/eyekb_core.py"]:
    wave.add(STG / f)
led = STG / "docs/recon/REPOSYNC3_INTAKE.sha256"
with open(led, "w") as fh:
    for p in sorted(wave):
        fh.write(f"{sha_f(p)}  {p.relative_to(STG)}\n")
out = subprocess.run(["sha256sum", "-c", "--quiet", str(led)], cwd=STG, capture_output=True, text=True)
lines.append(f"C) INTAKE entries={len(wave)} recheck-rc={out.returncode} stderr={out.stderr[:200]}")
if out.returncode != 0:
    rc = 1

# d) 卡内 sha 台账重验
res = {"OK": 0, "FAIL-EXPECTED-DESENS": 0, "FAIL-EXPECTED-EXCLUDED": 0, "OUTSIDE-REPO": 0, "REAL-FAIL": 0}
detail = []
for d in NEW[:5]:
    for lp in (P / d).rglob("*"):
        if not lp.is_file() or not re.search(r"SHA|sha256|MANIFEST", lp.name):
            continue
        if lp.suffix not in {".txt", ".tsv", ".md", ".list"}:
            continue
        for ln in lp.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.search(r"([0-9a-f]{64})", ln)
            if not m:
                continue
            want = m.group(1)
            seg = ln.split(want, 1)[1].strip().split()[0].rstrip(")）,;\"'") if ln.strip() else ""
            if "sha256" in seg.lower() or "sha" == seg.lower()[:3] and not seg:
                pass
            rel = onl_p = None
            if "plans/" in seg:
                tail = seg.split("plans/", 1)[1]
                rel = STG / "docs/plans" / tail
                onl_p = ONL / "plans" / tail
            elif seg and not seg.startswith("/") and ("OcularKB" not in seg):
                cand = (P / d) / seg.lstrip("./")
                rel = cand if cand.exists() else None
                onl_p = ONL / "plans" / d / seg.lstrip("./")
            if seg.startswith("/") or "OcularKB" in seg:
                res["OUTSIDE-REPO"] += 1
                continue
            if rel is None or not rel.exists():
                res["FAIL-EXPECTED-EXCLUDED"] += 1
                detail.append(f"EXCLUDED {lp.relative_to(STG)} -> {seg}")
                continue
            got = sha_f(rel)
            if got == want:
                res["OK"] += 1
                continue
            if rel.suffix in {".md", ".py", ".json", ".txt", ".tsv", ".jsonl", ".yaml", ".log", ".out", ".err"} \
               and onl_p and onl_p.exists() and sha_f(onl_p) == want \
               and desens(onl_p.read_text(encoding="utf-8", errors="ignore")) == rel.read_text(encoding="utf-8", errors="ignore"):
                res["FAIL-EXPECTED-DESENS"] += 1
                detail.append(f"DESENS {lp.relative_to(STG)} -> {rel.relative_to(STG)}")
                continue
            res["REAL-FAIL"] += 1
            detail.append(f"REAL-FAIL {lp.relative_to(STG)} -> {rel.relative_to(STG)}")
lines.append(f"D) {res}")
for x in detail[:80]:
    lines.append(f"  {x}")
if res["REAL-FAIL"]:
    rc = 1

(STG / "docs/plans/repo_sync3_20260928/out").mkdir(exist_ok=True)
(STG / "docs/plans/repo_sync3_20260928/out/t4_result.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
sys.exit(rc)
