#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB7-G1: KB5 离线自检门 v6 重跑 (PREREG §8 关1)。
S2a: 现役 v4.1 重算 == 冻结 digest (零扰动前置)。
S1 : 文件A markers_v6_retina_repair.json 内存 swap 为 retina 库 -> 22 热点簇 truth∈top3, 球门 >=15/22。
禁触任何代码/文件 (只 in-memory 替换 core.MARKER_LIBS)。判 0 FAIL 输出。"""
import json, sys
from pathlib import Path
sys.path.insert(0,'/mnt/D/EyeKB/mcp_server')
import eyekb_core as core

ROOT='/mnt/D/EyeKB/plans/evalset'
V6A=Path('/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json')
V41=Path('/mnt/D/EyeKB/kb/markers/markers_v4.1_clean.json')
TABLE=f'{ROOT}/scoring/run3_object_B_table_v1.1.tsv'
DIGEST=f'{ROOT}/digest/EV_DIGEST_SLIM_v3full.jsonl'
GATE=15; NCLUSTERS=22

def hotspot_list():
    rows=[l.rstrip('\n').split('\t') for l in open(TABLE)][1:]
    hdr=open(TABLE).readline().rstrip().split('\t')
    ix={h:i for i,h in enumerate(hdr)}
    out=[]
    for r in rows:
        if (r[ix['member']] in {'Q1','Q2','Q3','Q4','Q5b','Q7'}
            and r[ix['ident_equal']]=='True' and r[ix['matchA']]=='False' and r[ix['matchB']]=='False'
            and r[ix['truth_frac']] and r[ix['truth_frac']]!='nan'
            and float(r[ix['truth_frac']])>=0.7):
            out.append({'cluster_id':r[ix['cluster_id']],'truth':r[ix['truth']]})
    return out

def load_digest():
    d={}
    for l in open(DIGEST):
        r=json.loads(l); d[r['cluster_id']]=r
    return d

def query_list(rec):
    return [(s or g) for g,s in zip(rec['top_genes'],rec.get('top_genes_sym') or rec['top_genes'])][:10]

def rank_with(lib,genes):
    # digest 宇宙 = v3full 采集时点: retina + membrane 两库, retina_interneuron 库彼时未接线
    # (was 含 Mac_DAM_LAM/Pericyte 无前缀, 无 retina_interneuron:: 前缀类——4 簇抽样实证, 见运行日志)
    old=dict(core.MARKER_LIBS)
    try:
        core.MARKER_LIBS['retina']=lib
        from pathlib import Path as _P
        core.MARKER_LIBS['retina_interneuron']=_P('/nonexistent/kb7_digest_universe_off.json')
        return core.query_marker(genes=genes)['celltype_ranking']
    finally:
        core.MARKER_LIBS.clear(); core.MARKER_LIBS.update(old)

hs=hotspot_list(); dg=load_digest()
assert len(hs)==NCLUSTERS, f'应 22 簇, 实得 {len(hs)}'
assert all(h['cluster_id'] in dg for h in hs), '热点簇缺 digest'
lib6=json.loads(V6A.read_text())
lib41=json.loads(V41.read_text())
# 结构对等断言 (KB5 S2b 同型): 类名集全等; 未修类逐位等
assert set(lib6['markers'])==set(lib41['markers'])
for c in ['Rod','Cone','Micro']:
    assert lib6['markers'][c]==lib41['markers'][c], f'{c} 照抄类被改动'
assert set(lib41['markers']['RGC']) <= set(lib6['markers']['RGC']), 'RGC 只增不删 (观察名单转正)——违 S2b 惯例'
# S2a 零扰动
bad=0
for cid,rec in dg.items():
    now=[(x['cell_type'],x['n_shared']) for x in rank_with(V41,query_list(rec))[:3]]
    was=[(x['cell_type'],x['n_shared']) for x in rec['kb_marker_ranking']]
    if now!=was: bad+=1; print('S2a MISMATCH',cid)
print(f'S2a 现役库重算==冻结digest: {"PASS" if bad==0 else f"FAIL {bad}"}')
assert bad==0
# S1 v6
n_ok=0; rows=[]
for h in hs:
    rec=dg[h['cluster_id']]; q=query_list(rec)
    new=[(x['cell_type'],x['n_shared']) for x in rank_with(V6A,q)[:3]]
    b=h['truth'] in [x[0] for x in new]
    n_ok+=b; rows.append((h['cluster_id'],h['truth'],new,b))
with open('/mnt/D/EyeKB/plans/kbgov_b5impl_20260928/out/b506a_g1_hotspot_rerun.tsv','w') as fh:
    fh.write('cluster_id\ttruth\tv6_top3\thit\n')
    for r in rows: fh.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\n")
print(f'S1 v6 truth∈top3 = {n_ok}/22 | 球门 >={GATE} -> ' + ('PASS' if n_ok>=GATE else 'FAIL'))
sys.exit(0 if (bad==0 and n_ok>=GATE) else 1)
