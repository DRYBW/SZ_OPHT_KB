#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K7: 火灾审计格二——混合面（眼表 33 + 视网膜抽 22）。
抽样冻结规则(PREREG §4): Q1/Q2/Q3/Q4/Q5b/Q7/Q8 各按 n_cells 降序 top3 = 21 + Q9 top1 = 22。
两臂: 无规则臂=ON 库+k9 新条直接参与 ranking（暴露潜在火）; KB9 规则臂=R1 镜像（face-only 条在视网膜材料剔除）。
同时输出 KB9 条核心基因 × 22 视网膜簇 top10 的基因级重叠格（真泄漏风险，规则拦不住也要披露）。"""
import json, os, sys, heapq

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
import eyekb_core as C

K9 = json.load(open(f'{ROOT}/build/markers_k9_ocs_increment.json'))
K9_NAMES = set((K9.get('new_terms') or {}).keys())
face33 = [json.loads(l) for l in open(f'{EV}/digest/face_q6/EV_DIGEST_SLIM_q6.jsonl', encoding='utf-8')]

rows = [json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl', encoding='utf-8')]
sel = []
for tag in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7', 'Q8']:
    rr = sorted([r for r in rows if r['member'] == tag], key=lambda r: -int(r['n_cells']))[:3]
    sel += rr
sel += sorted([r for r in rows if r['member'] == 'Q9'], key=lambda r: -int(r['n_cells']))[:1]
assert len(sel) == 22, len(sel)


def top10(r):
    return [(s or g) for g, s in zip(r['top_genes'][:10], (r.get('top_genes_sym') or [])[:10])]


def ranking_no_rules(genes):
    resp = C.query_marker(genes=genes, library='all')  # ON 态
    out = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (resp.get('celltype_ranking') or [])[:3]]
    # 注入 k9 条并合并排序（模拟"若注册且无 applicability"）
    gl = {str(g).upper() for g in genes}
    k9score = {cls: sum(1 for x in e.get('core', []) if str(x.get('gene', '')).upper() in gl) for cls, e in K9['new_terms'].items()}
    merged = out + [{'cell_type': cls, 'n_shared': n} for cls, n in k9score.items() if n]
    merged.sort(key=lambda x: -x['n_shared'])
    return merged[:3]


def ranking_kb9_rules(genes):
    # 视网膜材料: KB9 face-only 条剔除 = R1 镜像; 其余保持 ON 态原生 ranking
    resp = C.query_marker(genes=genes, library='all')
    out = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (resp.get('celltype_ranking') or [])[:3]]
    return [x for x in out if x['cell_type'] not in K9_NAMES]


frows = []
leak_any = 0
for r in sel:
    g = top10(r)
    nr = ranking_no_rules(g)
    rr = ranking_kb9_rules(g)
    leaked = [x['cell_type'] for x in nr if x['cell_type'] in K9_NAMES]
    if leaked:
        leak_any += 1
    frows.append({'cluster': r['cluster_id'], 'member': r['member'], 'n_cells': r['n_cells'],
                  'top10': ';'.join([str(s or x) for x, s in zip(r['top_genes'][:10], r.get('top_genes_sym') or [])]),
                  'ranking_no_rules': ' | '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in nr),
                  'ranking_with_rules': ' | '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in rr) or '(空)',
                  'k9_leak_no_rules': ','.join(leaked) or ''})
with open(f'{ROOT}/out/kb9_fire_audit_mixedface.tsv', 'w') as f:
    f.write('cluster\tmember\tn_cells\ttop10\tranking_no_rules\tranking_with_rules\tk9_leak_no_rules\n')
    for x in frows:
        f.write('\t'.join([str(x[k]) for k in ['cluster', 'member', 'n_cells', 'top10', 'ranking_no_rules', 'ranking_with_rules', 'k9_leak_no_rules']]) + '\n')

# 基因级重叠格: KB9 core 基因 × 22 簇 top10
ovl = []
for cls, e in K9['new_terms'].items():
    for c in e.get('core', []):
        g = str(c.get('gene', '')).upper()
        hits = [x['cluster_id'] for x in sel if any(str(s).upper() == g for s in (x.get('top_genes_sym') or []))]
        ovl.append({'term': cls, 'gene': g, 'n_retina_clusters_top10': len(hits), 'clusters': ','.join(hits[:22])})
json.dump(ovl, open(f'{ROOT}/out/kb9_fire_audit_mixedface_genegrid.json', 'w'), ensure_ascii=False, indent=1)

# 眼表侧: 33 簇在规则臂下 retina-only 条零进入（断言）
arms = json.load(open(f'{ROOT}/out/kb9_face_arms.json'))
RET_CLASSES = set()
for name, path, db in C._load_marker_dbs('all'):
    if name in ('retina', 'retina_interneuron', 'retina_v6'):
        RET_CLASSES |= set(db.get('markers', {}).keys())
        RET_CLASSES |= {f'{name}::{ct}' for ct in db.get('markers', {})}
bad = [cid for cid, rk in arms['armC_kb9'].items()
       if any(x['cell_type'] in RET_CLASSES or x['cell_type'].startswith(('retina::', 'retina_interneuron::', 'retina_v6::')) for x in rk)]
print('格二完成: 22 视网膜簇, 无规则臂 k9 泄漏簇数 =', leak_any)
print('眼表面 R1 剔除断言: 违规簇 =', bad if bad else '0 (PASS)')
json.dump({'retina_no_rules_leak_clusters': leak_any, 'ocs_r1_assert_violations': bad,
           'sample_rule': 'Q1-Q5b/Q7/Q8 top3 by n_cells + Q9 top1', 'n_ret': 22},
          open(f'{ROOT}/out/kb9_fire_audit_mixedface_summary.json', 'w'), ensure_ascii=False, indent=1)
