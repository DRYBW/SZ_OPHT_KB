#!/usr/bin/env python3
"""G4 验收门：一条命令回答"你的批注管线和我们跑出的是不是同一个东西"。

前提（对应 VERIFY_CONTRACT G1/G2）：依赖按 requirements.repro.txt 安装；
文献语料为 Release slim 件（生产 fp32 原件已实测同锚）。
判据 = tests/G4_EXPECTED.json 三件锚（证据报告按时间戳/输出路径归一化后取
sha256，其余两件原始字节锚）。管线入口默认钉线程，请勿覆盖。

用法:  python tests/verify_pipeline.py [--work 输出目录]
退出码: 0=PASS(3/3)   1=FAIL（打印逐件 got/expected）   2=环境错误
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = json.loads((ROOT / "tests" / "G4_EXPECTED.json").read_text(encoding="utf-8"))


def raw_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_report_sha(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"生成时间[:：]\s*[\d\- :]+", "生成时间:=TS", t)
    t = re.sub(r"`[^`]*?/stage_a/", "`<RUN>/stage_a/", t)
    t = re.sub(r"(/tmp/[\w\-]+/|\$HOME/\S*?/pipeline/)", "<RUN>/", t)
    return hashlib.sha256(t.encode()).hexdigest()


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
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="g4_verify_"))
    cmd = [sys.executable, str(ROOT / "pipeline" / "run_pipeline.py"),
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
