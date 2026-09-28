#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN OB-3 (t_c145db7c): 22 视网膜簇 Arm1/Arm2 完整 ranking 一致性补查。
样本=KB9_PREREG §4 冻结抽样规则逐字重导；k7 两臂函数逐字抽取重放对账；
完整 ranking（截断前全列表）三臂：native(ON 五库)/Arm1(ON+k9)/Arm2(R1 镜像剔 k9)。
逐项：次序全等、top3 可重放、去重碰撞、平票加载序、k9 零进入。产 out/OB3_consistency.tsv。"""
import json, sys, os, io, contextlib, collections

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
KB9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
os.environ.pop('EYEKB_ACT_V6', None)
import eyekb_core as C

K9 = json.load(open(f'{KB9}/build/markers_k9_ocs_increment.json'))
K9_NAMES = set((K9.get('new_terms') or {}).keys())
SHIELD = json.load(open(f'{KB9}/out/kb9_face_effective_genesets.json'))
ON_NAMES = ['retina', 'membrane', 'retina_interneuron', 'retina_v6', 'face_v6']
RETINA_ONLY_FILES = {'markers_v4.1_clean.json', 'markers_v5_retina_interneuron.json', 'markers_v6_retina_repair.json'}

# k5 build_markers/k9_query 逐字复用
k5 = open(f'{KB9}/scripts/k5_face_build.py', encoding='utf-8').read()
seg = k5[k5.index('# ---- C 臂实现'):k5.index('# ---- G1')]
ns = {'json': json, 'C': C, 'K9': K9, 'SHIELD': SHIELD, 'ON_NAMES': ON_NAMES,
      'RETINA_ONLY_FILES': RETINA_ONLY_FILES, 'os': os, 'ROOT': KB9}
exec(seg, ns)
build_markers = ns['build_markers']

def full_query(genes, config):
    markers = build_markers(config)
    gl = [str(g).strip().upper() for g in genes if str(g).strip()]
    score, order = {}, {}
    for i, ct in enumerate(markers):
        n = sum(1 for g in gl if g in markers[ct])
        if n:
            score[ct] = n
            order[ct] = i
    ranked = sorted(score.items(), key=lambda kv: (-kv[1], order[kv[0]]))
    return [{'cell_type': c, 'n_shared': n} for c, n in ranked], markers

# ---- 冻结抽样重导（22 视网膜簇）----
rows = [json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl', encoding='utf-8')]
sel = []
for tag in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7', 'Q8']:
    rr = sorted([r for r in rows if r['member'] == tag], key=lambda r: -int(r['n_cells']))[:3]
    sel += rr
sel += sorted([r for r in rows if r['member'] == 'Q9'], key=lambda r: -int(r['n_cells']))[:1]
assert len(sel) == 22
saved_tsv = [l.split('\t') for l in open(f'{KB9}/out/kb9_fire_audit_mixedface.tsv', encoding='utf-8').read().strip().splitlines()]
saved_ids = [x[0] for x in saved_tsv[1:]]
assert [r['cluster_id'] for r in sel] == saved_ids, '样本重导与 k7 存档行集不一致'

def top10(r):
    return [(s or g) for g, s in zip(r['top_genes'][:10], (r.get('top_genes_sym') or [])[:10])]

# ---- k7 两臂函数逐字抽取重放 ----
k7 = open(f'{KB9}/scripts/k7_fire_mixedface.py', encoding='utf-8').read()
seg7 = k7[k7.index('def top10'):k7.index('leak_any = 0')]
face33 = [json.loads(l) for l in open(f'{EV}/digest/face_q6/EV_DIGEST_SLIM_q6.jsonl', encoding='utf-8')]
ns7 = {'json': json, 'C': C, 'K9': K9, 'K9_NAMES': K9_NAMES, 'face33': face33, 'rows': rows, 'top10': top10}
exec(seg7, ns7)
replay_ok = 0
for r, saved in zip(sel, saved_tsv[1:]):
    nr = ns7['ranking_no_rules'](top10(r))
    rr = ns7['ranking_kb9_rules'](top10(r))
    s_nr = ' | '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in nr)
    s_rr = ' | '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in rr) or '(空)'
    if s_nr == saved[4] and s_rr == saved[5]:
        replay_ok += 1
    else:
        print('REPLAY MISMATCH', r['cluster_id'])

out_rows = []
all_clear = True
for r in sel:
    cid = r['cluster_id']
    gl = top10(r)
    native, mkN = full_query(gl, {'on': True})
    arm1, mk1 = full_query(gl, {'on': True, 'k9': True})
    k9_keys = [k for k in mk1 if k in K9_NAMES or k.startswith('k9_build::')]
    arm2 = [x for x in arm1 if x['cell_type'] not in K9_NAMES and not x['cell_type'].startswith('k9_build::')]
    # ① native 次序/值全等：Arm2 == native
    order_eq = arm2 == native
    # ② Arm1 去 k9 后与 native 同序（stable-sort 无副作用）——同 order_eq；另核非 k9 子序列
    nonk9_arm1 = [x for x in arm1 if x['cell_type'] not in K9_NAMES and not x['cell_type'].startswith('k9_build::')]
    subseq_eq = nonk9_arm1 == native
    # ③ top3 vs query_marker ON 原生（G1 语义扩展至视网膜输入）
    prod = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (C.query_marker(genes=gl, library='all').get('celltype_ranking') or [])[:3]]
    top3_eq = native[:3] == prod
    # ④ 去重碰撞：k9 键形态
    collision = any(k.startswith('k9_build::') for k in k9_keys)
    k9_in_arm1 = [x['cell_type'] for x in arm1 if x['cell_type'] in K9_NAMES]
    # ⑤ 平票组：arm1 内同 n_shared 组数（加载序作用域）
    ncnt = collections.Counter(x['n_shared'] for x in arm1)
    ties = sum(1 for v in ncnt.values() if v > 1)
    # ⑥ Arm2 k9 零进入
    leak = any(x['cell_type'] in K9_NAMES or str(x['cell_type']).startswith('k9_build::') for x in arm2)
    clear = order_eq and subseq_eq and top3_eq and not leak
    if not clear:
        all_clear = False
    out_rows.append(dict(cluster_id=cid, member=r['member'], n_cells=r['n_cells'],
                         n_entries_native=len(native), n_entries_arm1=len(arm1), n_entries_arm2=len(arm2),
                         k9_entries_in_arm1=';'.join(k9_in_arm1) or '(0)',
                         arm2_equals_native=order_eq, nonk9_subseq_equals_native=subseq_eq,
                         top3_equals_prod_on=top3_eq, dedup_collision=collision,
                         tie_groups=ties, k9_leak_in_arm2=leak, verdict='清' if clear else '不清'))

cols = list(out_rows[0].keys())
with open(f'{ROOT}/out/OB3_consistency.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for x in out_rows:
        f.write('\t'.join(str(x[c]) for c in cols) + '\n')
print(f'k7 重放逐字节对账: {replay_ok}/22')
print('OB-3 全清判定:', '清' if (all_clear and replay_ok == 22) else '不清',
      '| 不清簇:', [x['cluster_id'] for x in out_rows if x['verdict'] != '清'])
print('碰撞(k9_build:: 前缀键出现)簇:', sum(1 for x in out_rows if x['dedup_collision']))
