#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB 镜像仓同质化验收器（VERIFY 契约 G3）。
本机跑出的检索结果是否与仓锚点同分布？一条命令回答。

用法（仓根目录）：
  python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
判据：41 例 top5 PMID 序列与 tests/REPRO_EXPECTED.json 逐位全等。
退出码 0=PASS(同质) 1=FAIL(打印逐例差异与三层排查顺序)。
依赖=requirements.repro.txt；引擎=clients/ocularkb/rag/scripts/stage3_retrieve.py（双格式分支）。
"""
import argparse, json, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-dir", default=os.path.join(ROOT, "literature_db", "v2.4.2_2026-09_slim"))
    ap.add_argument("--expected", default=os.path.join(ROOT, "tests", "REPRO_EXPECTED.json"))
    a = ap.parse_args()

    if not os.path.isdir(a.db_dir):
        print("FAIL: 找不到语料目录", a.db_dir)
        print("排查顺序: G2 先做——从 Release 下载预置件并 sha256sum -c（见 README 5 分钟跑通 步骤2）。重建路径产物不作数（契约 G2）。")
        return 1

    spec = importlib.util.spec_from_file_location(
        "s3", os.path.join(ROOT, "clients", "ocularkb", "rag", "scripts", "stage3_retrieve.py"))
    s3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s3)

    exp = json.load(open(a.expected, encoding="utf-8"))["results"]
    mis, n = [], 0
    for c in exp:
        r = s3.retrieve(c["cell_type"], species=c.get("species"), top_k=5,
                        tissue=c.get("tissue"), db_dir=a.db_dir)
        hits = r["results"] if isinstance(r, dict) and "results" in r else r
        got = [str(h.get("pmid")) for h in hits[:5]]
        n += 1
        if got != [str(p) for p in c["top_pmids"]]:
            mis.append({"case": f'{c["cell_type"]}/{c.get("species")}/{c.get("tissue")}',
                        "expected": c["top_pmids"], "got": got})
    ok = not mis
    print(f"REPRO {'PASS' if ok else 'FAIL'}: {n-len(mis)}/{n} 例 top5 逐位全等")
    if mis:
        print(json.dumps(mis[:10], ensure_ascii=False, indent=1))
        print("排查顺序: G2 预置件 sha 是否对上 -> G1 依赖版本是否按 requirements.repro.txt -> 模型是否 BAAI/bge-large-en-v1.5。")
        print("勿改判据勿调参凑数：漂移本身就是要报的信息（docs/VERIFY_CONTRACT.md §4）。")
    return 0 if ok else 1

sys.exit(main())
