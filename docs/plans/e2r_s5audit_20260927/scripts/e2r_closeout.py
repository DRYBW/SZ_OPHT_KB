#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R-5 收口组装：三口径对比表 + 判读矩阵机械执行 + 历史登记表同源副本(append 一行)
+ 虚构/不可解析清单（KB 数据质量发现）。全部写本卡目录，不回写 E2。"""
import json, csv

ROOT = '/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
E2 = '/mnt/D/EyeKB/plans/e2_decontam_20260926'

met = json.load(open(f'{ROOT}/out/e2r_metrics.json'))
summ = json.load(open(f'{ROOT}/out/e2r_identity_summary.json'))
grid = list(csv.DictReader(open(f'{ROOT}/out/e2r_sensitivity_grid.tsv'), delimiter='\t'))
water = list(csv.DictReader(open(f'{ROOT}/out/e2r_homology_water.tsv'), delimiter='\t'))

def g(v, face, subset):
    r = [x for x in grid if x['variant'] == v and x['face'] == face and x['subset'] == subset]
    return r[0] if r else None

q5 = [x for x in water if x['member/rows'] == 'Q5b'][0]
VARS = ['raw', 'S1', 'S5b', 'S5b_rel', 'S5']
tab = ['\t'.join(['caliber', 'F-RET@196①', 'F-RET无泄漏①', 'F-3SEAT①', 'Q5b@43行①', 'Q5b水分pp',
                  'Q5b水分区间锚'])]
for v in VARS:
    a = g(v, 'F-RET', '全部'); b = g(v, 'F-RET', '无泄漏'); c = g(v, 'F-3SEAT', '全部')
    q5pct = {'raw': q5['ev1_raw'], 'S1': q5['ev1_S1'], 'S5b': q5['ev1_S5b'],
             'S5b_rel': q5['ev1_S5b_rel'], 'S5': q5['ev1_S5']}[v]
    wat = {'raw': '0', 'S1': q5['water_S1_pp'], 'S5b': q5['water_S5b_pp'],
           'S5b_rel': q5['water_S5b_rel_pp'], 'S5': q5['water_S5_pp']}[v]
    anchor = {'S1': 'E2 冻结 32.55 ✓', 'raw': '基准'}.get(v, '')
    tab.append('\t'.join([v, a['ev1_top1'], b['ev1_top1'], c['ev1_top1'], q5pct, wat, anchor]))
open(f'{ROOT}/out/e2r_three_caliber_table.tsv', 'w').write('\n'.join(tab) + '\n')

# 判读矩阵机械执行
gate = summ['gate']
row1 = gate['verifiable_rate_ge50'] and gate['non_hrca_self_majority'] and not gate['mass_offtopic']
row2 = (not gate['verifiable_rate_ge50']) or gate['mass_offtopic']
matrix = 'ROW1_S5b_established' if (row1 and not row2) else ('ROW2_keep_strict' if (row2 and not row1) else 'AMBIGUOUS_report')
# S5 行 E2 声明复核（水分读数塌向 0 的实测值）
w_s5 = float(q5['water_S5_pp']); w_s5b = float(q5['water_S5b_pp']); w_s5b_rel = float(q5['water_S5b_rel_pp'])
verdict = dict(matrix_row=matrix, gate=gate, stats=summ['stats'],
               q5b_water=dict(S1=float(q5['water_S1_pp']), S5b=w_s5b, S5b_rel=w_s5b_rel, S5=w_s5),
               interval_note='水分读数区间按三口径升序报，W 档零改动', ran_from='e2r_metrics.json+identity_summary')
json.dump(verdict, open(f'{ROOT}/out/e2r_matrix_verdict.json', 'w'), ensure_ascii=False, indent=1)

# 历史登记同源副本 + append 一行（不回写 E2）
base = open(f'{E2}/out/e2_history_register.tsv').read().rstrip('\n').split('\n')
q5b_row = (f'E2 §5 S5 口径尾账收口（E2R）\tS1=32.55/S5b={w_s5b}/S5b_rel={w_s5b_rel}/S5={w_s5}\t'
           f'判读矩阵={matrix}\t三口径区间详见 e2r_three_caliber_table.tsv')
open(f'{ROOT}/out/e2r_history_register.tsv', 'w').write('\n'.join(base + [q5b_row]) + '\n')

# 虚构/不可解析清单（数据质量发现）
verds = list(csv.DictReader(open(f'{ROOT}/data/e2r_pair_verdicts.tsv'), delimiter='\t'))
pairs = [json.loads(l) for l in open(f'{ROOT}/data/e2r_pcx_pairs.jsonl')]
pm = {(p['cls'], p['gene']): p for p in pairs}
res = {}
for l in open(f'{ROOT}/data/e2r_title_resolution.jsonl'):
    d = json.loads(l); res[d['title']] = d
bad = ['\t'.join(['cls', 'gene', 'n_hits', 'status', 'title', 'fail_reason'])]
for v in verds:
    p = pm[(v['cls'], v['gene'])]
    if v['status'] in ('unverifiable', 'self_only', 'creditable'):
        for slot in ('title1', 'title2'):
            t = p[slot]
            r = res.get(t, {})
            if not t:
                bad.append('\t'.join([v['cls'], v['gene'], v['n_hits'], v['status'], '<空标题>', 'empty_title']))
            elif not r.get('verifiable') or (v['status'] == 'self_only' and r.get('hrca_self')) \
                 or (v['status'] == 'creditable' and not r.get('hrca_self', False)):
                fr = r.get('fail_reason') or ('hrca_self' if r.get('hrca_self') else ('offtopic' if v['status'] == 'creditable' else ''))
                if v['status'] == 'unverifiable' and r.get('fail_reason'):
                    bad.append('\t'.join([v['cls'], v['gene'], v['n_hits'], v['status'], t[:100], fr]))
                elif v['status'] == 'self_only' and r.get('hrca_self'):
                    bad.append('\t'.join([v['cls'], v['gene'], v['n_hits'], v['status'], t[:100], 'hrca_self_only']))
                elif v['status'] == 'creditable':
                    bad.append('\t'.join([v['cls'], v['gene'], v['n_hits'], v['status'], t[:100], 'offtopic(非自引但题不含基因/类词)']))
open(f'{ROOT}/out/e2r_quality_findings.tsv', 'w').write('\n'.join(bad) + '\n')

print(open(f'{ROOT}/out/e2r_three_caliber_table.tsv').read())
print(json.dumps(verdict['matrix_row'] and {'matrix': matrix, 'q5b_water': verdict['q5b_water'],
                                            'stats': summ['stats'], 'gate': gate}, ensure_ascii=False))
print('E2R_CLOSEOUT_DONE')
