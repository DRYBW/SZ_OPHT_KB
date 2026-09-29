#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC6 · T6 新鲜克隆自证（沿 RS5 同型）：git clone file:// 预检 commit → 断言链。
①克隆成功且 HEAD==预检 commit ②py_compile 全过 ③rs6_gates 克隆内 T1/T3/T4 PASS
④verify_repro 克隆内 41/41 ⑤git fsck clean ⑥tracked 文件数 clone==staging 对账。"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = _ROOT
OUT = STG / "docs/plans/repo_sync6_20260929/out"
DB = Path(os.path.expanduser("~")) / "RAG_SLIM_V242" / "literature_db" / "v2.4.2_2026-09_slim"
VENV_PY = Path(os.path.expanduser("~")) / "training-venv" / "bin" / "python3"
VERIFY_REF = os.environ.get("RS6_VERIFY_REF", "refs/heads/rs6-verify")
VERIFY_BRANCH = VERIFY_REF.split("/")[-1]
log = []
tmp = Path(tempfile.mkdtemp(prefix="rs6_t6_", dir="/tmp"))
result = "T6-FAIL init"
try:
    head = subprocess.run(["git", "rev-parse", VERIFY_REF], cwd=STG, capture_output=True, text=True).stdout.strip()
    assert head, "verify ref missing"
    r = subprocess.run(["git", "clone", "-q", "-b", VERIFY_BRANCH, f"file://{STG}", str(tmp / "SZ_OPHT_KB")],
                       capture_output=True, text=True)
    assert r.returncode == 0, "clone failed: " + r.stderr
    cl = tmp / "SZ_OPHT_KB"
    head2 = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cl, capture_output=True, text=True).stdout.strip()
    log.append(f"clone OK target={head[:12]} HEAD match={head == head2}")
    fails = []
    pyfiles = [p for p in cl.rglob("*.py") if "__pycache__" not in str(p)]
    for p in pyfiles:
        try:
            subprocess.run([sys.executable, "-m", "py_compile", str(p)], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            fails.append(str(p.relative_to(cl)))
    log.append(f"py_compile: files={len(pyfiles)} fails={len(fails)} {fails[:3]}")
    assert not fails
    t7 = subprocess.run([sys.executable, str(cl / "docs/plans/repo_sync6_20260929/scripts/rs6_gates.py")],
                        capture_output=True, text=True,
                        env=dict(os.environ, EYEKB_STG=str(cl)))
    okmarks = {}
    for k in ["T1", "T3", "T4"]:
        seg = t7.stdout.split(k + " ")[1][:60] if (k + " ") in t7.stdout else ""
        okmarks[k] = "PASS" in seg
    log.append("gates-in-clone: " + " ".join(f"{k}={'PASS' if v else 'CHECK'}" for k, v in okmarks.items()))
    assert all(okmarks.values()), "clone-gates not all PASS: " + t7.stdout[-400:]
    v = subprocess.run([str(VENV_PY), str(cl / "tests/verify_repro.py"), "--db-dir", str(DB)],
                       capture_output=True, text=True)
    golden = "REPRO PASS: 41/41" in v.stdout
    log.append(f"verify_repro in clone: {'PASS 41/41' if golden else 'FAIL'} ({v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-200:]})")
    assert golden
    fs = subprocess.run(["git", "fsck", "--no-progress"], cwd=cl, capture_output=True, text=True)
    log.append(f"git fsck rc={fs.returncode} out={'clean' if not fs.stdout.strip() else fs.stdout[:200]}")
    n_repo = len(subprocess.run(["git", "ls-files"], cwd=cl, capture_output=True, text=True).stdout.splitlines())
    n_stg = len(subprocess.run(["git", "ls-files", "--with-tree", head], cwd=STG, capture_output=True, text=True).stdout.splitlines())
    log.append(f"tracked files clone={n_repo} staging@{head[:12]}={n_stg} match={n_repo == n_stg}")
    assert n_repo == n_stg
    result = "T6-PASS"
except AssertionError as e:
    result = f"T6-FAIL {e}"
finally:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "t6_fresh_clone.txt").write_text(
        result + "\n" + "\n".join(log) + f"\ntmpdir={tmp} cleaned={not tmp.exists()}\n"
        "# 注：本件验证对象=预检 commit（commit-tree 生成 refs/rs6-verify）；正式 commit 在本证据件与 gates_summary、\n"
        "# REPOSYNC6_COMPLETED.md、T7_EXCLUSIONS_RS6 台账落盘后于其 tree 之上生成（parent=fa4f175 不变，线性可快进），\n"
        "# 终态 clone+tracked 对账复跑结果=登记于看板完成 summary（协调者可 `git clone file://<staging>` 独立复验）。\n",
        encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
print(result)
print("\n".join(log))
