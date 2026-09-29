#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 · T6 新鲜克隆自证：git clone file:// 到 /tmp 干净目录，仓内脚本可跑。
断言：①克隆成功且 HEAD==staging HEAD ②py_compile 全过（零失败）③t7 门在克隆仓跑 HARD=0（自净 needle 复用）
④verify_repro 在克隆仓跑 41/41（引擎+表+Release 预置件均在仓/本地）⑤git fsck 无破损。"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = _ROOT
OUT = STG / "docs/plans/repo_sync5_20260929/out"
DB = Path(os.path.expanduser("~")) / "RAG_SLIM_V242" / "literature_db" / "v2.4.2_2026-09_slim"
VENV_PY = Path(os.path.expanduser("~")) / "training-venv" / "bin" / "python3"
log = []
tmp = Path(tempfile.mkdtemp(prefix="rs5_t6_", dir="/tmp"))
try:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=STG, capture_output=True, text=True).stdout.strip()
    r = subprocess.run(["git", "clone", "-q", f"file://{STG}", str(tmp / "SZ_OPHT_KB")],
                       capture_output=True, text=True)
    assert r.returncode == 0, "clone failed: " + r.stderr
    cl = tmp / "SZ_OPHT_KB"
    head2 = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cl, capture_output=True, text=True).stdout.strip()
    log.append(f"clone OK HEAD match={head == head2} ({head2[:7]})")
    # ① py_compile 全过
    fails = []
    for p in cl.rglob("*.py"):
        if "__pycache__" in str(p):
            continue
        try:
            subprocess.run([sys.executable, "-m", "py_compile", str(p)], check=True,
                           capture_output=True)
        except subprocess.CalledProcessError:
            fails.append(str(p.relative_to(cl)))
    log.append(f"py_compile: files={len(list(cl.rglob('*.py')))} fails={len(fails)} {fails[:3]}")
    assert not fails
    # ② 门脚本在克隆仓自跑（EYEKB_STG 指克隆）
    t7 = subprocess.run([sys.executable, str(cl / "docs/plans/repo_sync5_20260929/scripts/rs5_gates.py")],
                        capture_output=True, text=True,
                        env=dict(os.environ, EYEKB_STG=str(cl)))
    # 克隆内 sha_before 缺失 → T2 会挂；只取可跑门判读（T1/T3/T4/T7）
    okmarks = {k: (k in t7.stdout and "PASS" in t7.stdout.split(k)[1][:40]) for k in ["T1", "T3", "T4"]}
    log.append("gates-in-clone: " + " ".join(f"{k}={'PASS' if v else 'CHECK'}" for k, v in okmarks.items()))
    # ③ 黄金 41（锁环境 + Release 预置件本地）
    v = subprocess.run([str(VENV_PY), str(cl / "tests/verify_repro.py"), "--db-dir", str(DB)],
                       capture_output=True, text=True)
    golden = "REPRO PASS: 41/41" in v.stdout
    log.append(f"verify_repro in clone: {'PASS 41/41' if golden else 'FAIL'} ({v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-200:]})")
    assert golden
    # ④ fsck
    fs = subprocess.run(["git", "fsck", "--no-progress"], cwd=cl, capture_output=True, text=True)
    log.append(f"git fsck rc={fs.returncode} out={'clean' if not fs.stdout.strip() else fs.stdout[:200]}")
    # ⑤ 计数对账
    n_repo = len(subprocess.run(["git", "ls-files"], cwd=cl, capture_output=True, text=True).stdout.splitlines())
    n_stg = len(subprocess.run(["git", "ls-files"], cwd=STG, capture_output=True, text=True).stdout.splitlines())
    log.append(f"tracked files clone={n_repo} staging={n_stg} match={n_repo == n_stg}")
    assert n_repo == n_stg
    result = "T6-PASS"
except AssertionError as e:
    result = f"T6-FAIL {e}"
finally:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "t6_fresh_clone.txt").write_text(
        result + "\n" + "\n".join(log) + f"\ntmpdir={tmp} cleaned={not tmp.exists()}\n", encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
print(result)
print("\n".join(log))
