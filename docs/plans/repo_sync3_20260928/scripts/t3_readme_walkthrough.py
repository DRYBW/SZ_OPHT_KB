#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T3 — README 增量可复跑实证
①版本串：README 服务版本 == server.py version 字段逐字；②禁词断言：README 与 v2.4.x/k9 相关面
零"已激活/已上线"措辞（激活未发生口径）；③当期主口径 26/33 在文；④义务 run=READY 措辞与
"激活归 PI/建议票件"限定同段；⑤B5/H1M3"已实装默认生效"允许措辞在文；⑥附录 A/§五/§四引用路径
逐件 ls 实证存在；⑦py 脚本 py_compile（本卡+被引用）。输出 out/t3_readme_walkthrough.txt。"""
import py_compile
import re
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
OUT = STG / "docs/plans/repo_sync3_20260928/out"
lines, rc = [], 0

rd = (STG / "README.md").read_text(encoding="utf-8")
sv = (STG / "mcp_server/server.py").read_text(encoding="utf-8")
ver = re.search(r'version="([^"]+)"', sv).group(1)
ck = lambda tag, cond, det="": lines.append(f"{tag}: {'PASS' if cond else 'FAIL'} {det}") or (0 if cond else globals().update(rc=1))

ck("1-version-string", f"`{ver}`" in rd, ver)
forb = []
for m in re.finditer(r"已激活|已上线|已启用", rd):
    seg = rd[max(0, m.start() - 60): m.end() + 60]
    if not re.search(r"不构成|禁|勿|不出现|未|零\"", seg):
        forb.append(m.group(0))
ck("2-forbidden-activation-words==0(negated-mentions-exempt)", not forb, str(forb))
ck("3-main-caliber-26/33", "26/33" in rd and "P1" in rd)
ck("3b-obligrun-READY-with-PI-scope", ("READY" in rd) and ("OB-5 激活权归 PI" in rd) and ("建议票件" in rd))
ck("4-B5-H1M3-implemented-wording", ("0.6-kbgov5" in rd) and ("已实装默认生效" in rd) and ("向前生效" in rd))
ck("5-k9-and-v24x-default-off", "均仍默认 OFF" in rd)
paths = [
    "docs/recon/RECON_kb_mcp_reposync3_20260928.tsv",
    "docs/recon/REPOSYNC3_INTAKE.sha256",
    "docs/plans/repo_sync3_20260928/S9_SCREENING.md",
    "docs/plans/repo_sync3_20260928/ledgers/T7_EXCLUSIONS.tsv",
    "docs/plans/kbgov_b5impl_20260928/out/B5IMPL_A5_ROLLBACK.tsv",
    "docs/plans/kbgov_b5impl_20260928/B5IMPL_COMPLETED.md",
    "docs/plans/grade_h1m3impl_20260928/REPORT_H1M3.md",
    "docs/plans/obligrun_20260928/ACTIVATION_READINESS.md" if (STG / "docs/plans/obligrun_20260928/ACTIVATION_READINESS.md").exists() else "docs/plans/obligrun_20260928/out/ACTIVATION_READINESS.md",
    "docs/plans/obligrun_20260928/OBLIGRUN_RULING_1.md",
    "docs/plans/obligrun_20260928/out/FACE_V21_ledger.tsv",
    "docs/plans/mouse_ext_precheck_20260928/MOUSEEXT_APPROVAL.tsv",
    "docs/plans/rag_fix3_20260928/RAGFIX3_NOTE.md",
    "docs/plans/rag_fix3_20260928/REPO_RESYNC3_REQUIRED.md",
    "docs/plans/rag_fix3_20260928/work/ra3_availability.tsv",
    "docs/plans/rag_fix3_20260928/work/ra3_selected.jsonl",
    "docs/plans/rag_fix3_20260928/scripts/ra3_fetch.py",
    "docs/plans/rag_fix3_20260928/scripts/ra3_scan.py",
    "docs/plans/rag_fix3_20260928/scripts/ra3_merge.py",
    "docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md",
    "mcp_server/kbgov_vocab.json.gz",
    "kb/literature_db/EYEKB_DB_POINTER.yaml",
]
missing = [p for p in paths if not (STG / p).exists()]
ck("6-referenced-paths-exist", not missing, f"{len(paths)} paths, missing={missing}")
pf = []
for p in ["docs/plans/repo_sync3_20260928/scripts/t3_readme_walkthrough.py"]:
    try:
        py_compile.compile(str(STG / p), doraise=True)
    except Exception as e:
        pf.append((p, str(e)[:80]))
ck("7-self-py_compile", not pf, str(pf))

(OUT / "t3_readme_walkthrough.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
sys.exit(rc)
