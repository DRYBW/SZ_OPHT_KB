#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTEST 路径 grep 自检（PREREG §8.2）：runner/verdict 硬编码路径审计。
写路径白名单 = plans/btest_20260927/**（+ /mnt/D/EyeKB/logs/mcp_trace 服务端 calllog 追加，
属正常服务副作用）；读路径白名单 = §11 冻结件 + mcp_server + OcularKB rag/models（只读）。
输出 logs/path_grep.txt；任何越界写入路径即 rc=1。"""
import re, sys

ROOT = '/mnt/D/EyeKB/plans/btest_20260927'
files = [f'{ROOT}/scripts/btest_runner.py', f'{ROOT}/scripts/btest_verdict.py',
         f'{ROOT}/scripts/btest_input_sha_check.py', f'{ROOT}/BTEST_PREREG_v1.0.md']
WRITE_PAT = re.compile(r"(open\(|\.write|to_csv|json\.dump\(|makedirs|os\.mkdir|shutil\.copy)", re.I)
PATH_PAT = re.compile(r"/mnt/D/[^\s'\"`\)]+|~/[^\s'\"`\)]+")
OUT = f'{ROOT}/logs/path_grep.txt'
lines = []
viol = []
for fp in files:
    for i, l in enumerate(open(fp, encoding='utf-8'), 1):
        for m in PATH_PAT.finditer(l):
            p = m.group(0)
            lines.append(f'{fp}:{i}: {p}')
            is_write = bool(WRITE_PAT.search(l)) or 'TRACE_DIR' in l
            allowed = (p.startswith('/mnt/D/EyeKB/plans/btest_20260927') or
                       p.startswith('/mnt/D/EyeKB/logs/mcp_trace'))
            if is_write and not allowed:
                # open() 读冻结件属读；仅对写出方向路径做白名单（w/a 模式或 dump/to_csv/makedirs）
                if re.search(r"open\([^)]*['\"][war]", l) or 'to_csv' in l or 'json.dump(' in l or 'makedirs' in l:
                    viol.append(f'{fp}:{i}: WRITE OUTSIDE WHITELIST: {p}')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
    f.write(f'\nchecked_lines={len(lines)} violations={len(viol)}\n')
    for v in viol:
        f.write(v + '\n')
print(f'WROTE {OUT} refs={len(lines)} violations={len(viol)}')
for v in viol:
    print(v)
sys.exit(1 if viol else 0)
