#!/usr/bin/env python3
"""G4 验收门：一条命令回答"你的批注管线和我们跑出的是不是同一个东西"。

前提（对应 VERIFY_CONTRACT G1/G2）：依赖按 requirements.repro.txt 安装；
文献语料为 Release slim 件（生产 fp32 原件已实测同锚）。
判据 = tests/G4_EXPECTED.json 三件锚（证据报告按时间戳/输出路径归一化后取
sha256，其余两件原始字节锚）。管线入口默认钉线程，请勿覆盖。

解释器 = 契约的一部分（KB10d，2026-10-01）：本门驱动管线用的解释器**钉在
pipeline_env**（`EYEKB_G4_PY` 可覆盖，见下），不继承调用方 `sys.executable`。
原因：`stage_a/processed.h5ad` 的字节取决于 anndata/numpy/scipy/sklearn 的
浮点写入路径。实测同代码同 fixture：pipeline_env(scanpy 1.11.5/anndata
0.11.4/numpy 2.2.6/scipy 1.15.3/sklearn 1.7.2) → 锚 `dbc657…`；training-venv
(scanpy 1.12.2/anndata 0.12.19/numpy 2.4.6) → `f7a461…`；离线 venv
(anndata 0.13.2) → `10cfbe…`（三例差异集中在 X_pca/X_umap/var/dispersions
的 float32 末位；obs/leiden/counts 层全同）。继承调用方解释器 = 跨 venv 必
假 FAIL。钉的解释器缺失/不可执行 = 环境错误（rc=2 并打印修法），**不静默
回退到当前解释器**。

用法:  python tests/verify_pipeline.py [--work 输出目录]
       EYEKB_G4_PY=/path/to/python python tests/verify_pipeline.py   # 显式覆盖
       本门自身仅用标准库，可由任意 python3 启动（3.10+）。
退出码: 0=PASS(3/3)   1=FAIL（打印逐件 got/expected）   2=环境错误
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = json.loads((ROOT / "tests" / "G4_EXPECTED.json").read_text(encoding="utf-8"))

# 解释器钉：默认值 = 生成 G4 锚的解释器；EYEKB_G4_PY 可覆盖（唯一回退口）。
PY_ENV = "EYEKB_G4_PY"
PY_PINNED = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"


def raw_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_report_sha(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"生成时间[:：]\s*[\d\- :]+", "生成时间:=TS", t)
    t = re.sub(r"`[^`]*?/stage_a/", "`<RUN>/stage_a/", t)
    t = re.sub(r"(/tmp/[\w\-]+/|\$HOME/\S*?/pipeline/)", "<RUN>/", t)
    return hashlib.sha256(t.encode()).hexdigest()


def resolve_python():
    """解析并实测 G4 管线解释器。返回 (path, src, ver)；path=None 表示环境错误。"""
    env = os.environ.get(PY_ENV, "").strip()
    cand, src = (env, f"环境变量 {PY_ENV}") if env else (PY_PINNED, "契约默认值")
    if not (Path(cand).is_file() and os.access(cand, os.X_OK)):
        print(f"ENV ERROR: G4 解释器不可用（来源={src}）: {cand}")
        print("  本门判据锚定在 pipeline_env（见 docs/VERIFY_CONTRACT.md G4）；"
              "解释器缺失/不可执行即环境错误，")
        print("  不静默改用当前解释器——那必然产生假 FAIL。")
        print(f"  修法: 准备等价环境后 `export {PY_ENV}=/path/to/python` 再跑。")
        return None, src, None
    try:
        r = subprocess.run([cand, "-c", "import sys;print('%d.%d'%sys.version_info[:2])"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"ENV ERROR: G4 解释器实跑失败（来源={src}）: {cand} ({type(e).__name__}: {e})")
        return None, src, None
    if r.returncode != 0:
        print(f"ENV ERROR: G4 解释器实跑 rc={r.returncode}（来源={src}）: {cand}")
        print(r.stderr[-400:])
        return None, src, None
    return cand, src, r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="")
    a = ap.parse_args()
    fixture = ROOT / EXP["fixture"]
    if not fixture.is_file():
        print("ENV ERROR: fixture 缺失:", fixture)
        return 2
    if raw_sha(fixture) != EXP["fixture_sha256"]:
        print("FAIL: fixture 本体与锚不符（仓库内容漂移）")
        return 1
    PY, src, pyver = resolve_python()
    if PY is None:
        return 2
    print(f"[g4] 解释器: {PY} (python {pyver}, 来源: {src})")
    if PY != PY_PINNED:
        print(f"[g4] 注意: 解释器非契约默认（{PY_PINNED}）——G4 锚来自契约默认环境，"
              "非默认解释器若出现差异不算新发现。")
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="g4_verify_"))
    cmd = [PY, str(ROOT / "pipeline" / "run_pipeline.py"),
           "--out", str(work), "--seed", EXP["seed"],
           "--input", str(fixture), "--species", "human",
           "--tissue", "fibrovascular_membrane"]
    print("[g4] 运行管线（约 1-2 分钟，零联网）...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ENV ERROR: run_pipeline rc=", r.returncode)
        print(r.stderr[-800:])
        return 2
    checks = [
        ("stage_a/processed.h5ad", lambda p: raw_sha(p)),
        ("decisions_template.csv", lambda p: raw_sha(p)),
        ("annotation_evidence_report.md", lambda p: norm_report_sha(p)),
    ]
    nfail = 0
    for name, fn in checks:
        key = name + ("__normalized" if "report" in name else "")
        target = EXP["anchors"][key]
        got = fn(work / name)
        ok = (got == target)
        nfail += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + key)
        if not ok:
            print("   got:     ", got)
            print("   expected:", target)
    print(f"\nG4 {'PASS: 3/3 逐位一致' if nfail == 0 else f'FAIL: {nfail}/3 不一致'}")
    print("（时间戳与输出路径不参与判据，其余逐字节；详见 VERIFY_CONTRACT G4）")
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
