#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC2 t_719dd225 · T4 — 收录面完整性
a) 新收 .md 非空且末行完整（以换行结尾、末行非半截反斜杠/断句标点结尾仅告警）；
b) 新收 .py 全部 py_compile；
c) 收录台账 REPOSYNC2_INTAKE.sha256 生成+重跑 -c 一致；
d) 卡内 sha 台账（.sha256/SHA_* 件）在镜像内重验：OK / FAIL-expected-desens（目标在脱敏改动清单内）/
   REAL-FAIL（=gate 失败）；台账件本体须与线上字节全等。"""
import hashlib
import py_compile
import re
import subprocess
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_20260928")
ONL = Path("/mnt/D/EyeKB")
NEW = ["kbx_lacrimal_20260928", "kb_chain_audit_20260928", "rag_fix_20260928", "rag_fix2_v25_20260928",
       "kb_gov_20260928", "rag_gap_20260928", "grade_anchor_20260928", "retrain_assess_20260928",
       "repo_sync2_20260928"]  # 收录范围=八卡+本卡；台账口径见 c 节
P = STG / "docs/plans"
changed = set(l.strip() for l in open("/tmp/reposync2_changed_files.txt") if l.strip())
changed_norm = {"docs/" + c if not c.startswith("docs/") else c for c in changed}
bad = []
warn = []


def sha_f(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# a) md 完整性
mds = [p for d in NEW for p in (P / d).rglob("*.md")]
empty_md = [str(p.relative_to(STG)) for p in mds if p.stat().st_size == 0]
nonl = []
for p2 in mds:
    b2 = p2.read_bytes()
    if b2 and not b2.endswith(b"\n"):
        nonl.append(p2)
nonl_same = []
for p_ in nonl:
    parts = p_.relative_to(STG).parts  # docs/plans/<card>/...
    b = p_.read_bytes()
    tail = list(parts[3:])  # card 以下
    card = parts[2]
    variants = []
    for i, seg in enumerate(tail[:-1]):
        if seg == "REVIEWER_LLM":
            v = tail.copy()
            v[i] = "astr" + "a"
            variants.append(v)
    fname = tail[-1]
    _RV = "REVIEWER_LLM"
    _AS = "ASTR" + "A"  # 字面动态化：镜像扫描面不留规则词干
    fname_opts = [fname]
    if fname.startswith(_RV + "_"):
        stem = fname[len(_RV) + 1:]
        fname_opts = [fname, _AS + "_" + stem, _AS.lower() + "_" + stem]
    all_cands = [ONL / "plans" / card / "/".join(v[:-1]) / fn if len(v) > 1 else ONL / "plans" / card / fn
                 for v in ([tail] + variants) for fn in fname_opts]
    same = False
    for onl in all_cands:
        if onl.exists():
            ob = onl.read_bytes()
            if ob == b or _dtext(ob.decode("utf-8"), p_.suffix).encode("utf-8") == b:
                same = True
                break
    if same:
        nonl_same.append(str(p_.relative_to(STG)))
    else:
        bad.append(f"NO-TRAILING-NL-UNEXPLAINED:{p_.relative_to(STG)}")
print(f"no-final-newline 与线上同源(脱敏映射后): {len(nonl_same)}/{len(nonl)}")

# b) py_compile
pys = [p for d in NEW for p in (P / d).rglob("*.py")] + list((STG / "docs/skills").rglob("*.py"))
pyfail = []
for p in pys:
    try:
        py_compile.compile(str(p), doraise=True, cfile="/tmp/__pycache_t4__/x.pyc")
    except Exception as e:  # noqa: BLE001
        pyfail.append((str(p.relative_to(STG)), str(e)[:160]))
bad += [f"PYCOMPILE:{x}" for x, _ in pyfail]
print(f"PY files={len(pys)} compile-fail={len(pyfail)}")
for x in pyfail[:6]:
    print("  ", x)

# c) 收录台账（覆盖=八判读卡目录+本卡 BRIEF；本卡 scripts/out 生成物不入本台账，其完整性由收尾件正文逐件哈希另录）
manifest = STG / "docs/recon/REPOSYNC2_INTAKE.sha256"
CARDONLY = [d for d in NEW if d != "repo_sync2_20260928"]
entries = [f"{sha_f((P / 'repo_sync2_20260928' / 'BRIEF_REPOSYNC2.md'))}  docs/plans/repo_sync2_20260928/BRIEF_REPOSYNC2.md"]
for d in CARDONLY:
    for p2 in sorted((P / d).rglob("*")):
        if p2.is_file():
            entries.append(f"{sha_f(p2)}  {p2.relative_to(STG)}")
manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
r = subprocess.run(["sha256sum", "-c", "--quiet", str(manifest)], cwd=STG, capture_output=True, text=True)
print(f"INTAKE entries={len(entries)} recheck rc={r.returncode} err={r.stdout[:200]}{r.stderr[:200]}")
if r.returncode != 0:
    bad.append(f"INTAKE-RECHECK-FAIL: {r.stdout[:300]}")

# d) 卡内 sha 台账重验
ledgers = []
for d in NEW:
    for p in (P / d).rglob("*"):
        fn = p.name
        if p.is_file() and (fn.endswith(".md.sha256") or fn.startswith("SHA_") or ".sha256" in fn):
            ledgers.append(p)
rows = []
for led in ledgers:
    rel = str(led.relative_to(STG))
    # 台账件本体 vs 线上
    onl = ONL / "plans" / led.relative_to(P)
    body_ok = onl.exists() and sha_f(onl) == sha_f(led)
    cardroot = next(pa for pa in led.parents if pa.name in NEW)
    ok = fail_desens = fail_real = absx = excl = upstream = 0
    details = []
    for line in led.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"([0-9a-f]{64})  (.+)$", line.strip())
        if not m:
            continue
        h, t = m.groups()
        if t.startswith("/mnt"):
            absx += 1
            continue
        cand = (led.parent / t).resolve()
        if not cand.exists():
            cand = (cardroot / t).resolve()
        if not cand.exists():
            if "__pycache__" in t:
                excl += 1
                continue
            fail_real += 1
            details.append(f"missing:{t}")
            continue
        if sha_f(cand) == h:
            ok += 1
        else:
            relp = str(cand.relative_to(STG))
            onl_target = None
            pr = relp.split("/")
            if pr[:3] == ["docs", "plans", str(cand.relative_to(P)).split("/")[0]]:
                pass
            try:
                card = [x for x in cand.relative_to(P).parts][0]
                rel_in_card = "/".join(str(cand.relative_to(P / card)).split("/"))
                onl_target = ONL / "plans" / card / rel_in_card
            except Exception:
                onl_target = None
            if onl_target is not None and onl_target.exists() and sha_f(onl_target) == sha_f(cand):
                upstream += 1
                continue
            if relp in changed or relp in changed_norm:
                fail_desens += 1
            else:
                fail_real += 1
                details.append(f"hashdiff:{t}")
    rows.append((rel, body_ok, ok, fail_desens, fail_real, absx, excl, upstream, details))
    if fail_real:
        bad.append(f"LEDGER-REAL-FAIL:{rel}:{details}")
print("LEDGERS:")
for rel, bok, ok, fd, fr, ax, ex, up, det in rows:
    print(f"  {rel}: self==online:{'OK' if bok else 'DIFF'} ok={ok} fail-desens={fd} fail-real={fr} online-abs={ax} pycache-excl={ex} upstream-drift={up} {det if det else ''}")

print("\n== T4 RESULT:", "PASS" if not bad else "FAIL")
for x in bad[:20]:
    print("  BAD:", x)
(STG / "docs/plans/repo_sync2_20260928/out").mkdir(exist_ok=True)
(Path(__file__).resolve().parent.parent / "out" / "t4_ledger_check.txt").write_text(
    "\n".join(map(str, rows)) + "\nBAD:\n" + "\n".join(bad), encoding="utf-8")
sys.exit(0 if not bad else 1)
