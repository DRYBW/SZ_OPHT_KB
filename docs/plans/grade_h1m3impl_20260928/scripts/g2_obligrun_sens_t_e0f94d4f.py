#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门2 = 回归门（PREREG_H1M3 §3）：OBLIGRUN v2 票面（kb9_face_v2.1，99 票=33簇×3席）
经 h1m3_runner 实装组件重算 P1 敏感性对照。
(a) 基线复现 C2b∘none：逐簇 consensus/mode 必须与 obligrun 发布件 oblig_percluster.tsv 全等 + P1=26/33；
(b) 敏感性主列 C2b∘M3(模式B)：P1 单独成列报数（冻结预期=26/33，delta 如实登记；主口径当期 26/33 不动、
    不回改 verdict 件）；named∧C 13 票清点（预期 anchor_applied=11 / namedC_noanchor=2）；
(c) 参考列（非主口径）：C4∘none / C4∘M3 同 99 票 P1 与定名数。
零 LLM、零写入 obligrun 目录（只读）。"""
import sys, json
import pandas as pd

sys.path.insert(0, '/mnt/D/EyeKB/plans/grade_h1m3impl_20260928/scripts')
from h1m3_runner_t_e0f94d4f import (from_ann_row, apply_h1_anchor, c4_count, c2b_mode, NAMED)

OUT = '/mnt/D/EyeKB/plans/grade_h1m3impl_20260928'
ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
SEATS = ('A', 'B', 'C')

V = {}
SEATMODEL = {}
for s in SEATS:
    SEATMODEL[s] = json.load(open(f'{ROOT}/out/ANN_{s}_oblig_META.json')).get('model', s)
    V[s] = {}
    for l in open(f'{ROOT}/out/ANN_{s}_oblig.jsonl', encoding='utf-8'):
        if l.strip():
            V[s][json.loads(l)['cluster_id']] = json.loads(l)

pc = pd.read_csv(f'{ROOT}/out/oblig_percluster.tsv', sep='\t', keep_default_na=False, na_values=[''])
face_ids = list(pc['cluster_id'])
assert len(face_ids) == 33 and all(len(V[s]) == 33 for s in SEATS)
ov = json.load(open(f'{ROOT}/out/oblig_verdict.json'))
truth = {r['cluster_id']: (r['truth'] if r['truth'] not in ('', None, 'None', 'nan') else None) for _, r in pc.iterrows()}
frozen = {r['cluster_id']: (r['consensus_c2b'] if r['consensus_c2b'] not in ('', None, 'None', 'nan') else None,
                             r['mode']) for _, r in pc.iterrows()}

def bs_of(cid, tier, mode='B'):
    out = []
    for s in SEATS:
        b = from_ann_row(V[s][cid])
        out.append(b if tier == 'none' else apply_h1_anchor(b, tier, mode))
    return out

rows, flags = {}, []
for cid in face_ids:
    bs0 = bs_of(cid, 'none')
    bs3 = [apply_h1_anchor(b, 'M3', 'B') for b in bs0]
    cons2b_0, mode2b_0 = c2b_mode(bs0)
    cons2b_3, mode2b_3 = c2b_mode(bs3)
    cons4_0, m4_0 = c4_count(bs0)
    cons4_3, m4_3 = c4_count(bs3)
    tv = truth[cid]
    rows[cid] = dict(cluster_id=cid, truth=tv,
                     vote_A=V['A'][cid]['identity'], grade_A=V['A'][cid]['grade'],
                     vote_B=V['B'][cid]['identity'], grade_B=V['B'][cid]['grade'],
                     vote_C=V['C'][cid]['identity'], grade_C=V['C'][cid]['grade'],
                     cons_c2b=cons2b_0, mode_c2b=mode2b_0,
                     cons_c2b_m3=cons2b_3, mode_c2b_m3=mode2b_3,
                     cons_c4=cons4_0, mode_c4=m4_0,
                     cons_c4_m3=cons4_3, mode_c4_m3=m4_3,
                     p1_c2b=bool(cons2b_0 == tv), p1_c2b_m3=bool(cons2b_3 == tv),
                     p1_c4=bool(cons4_0 == tv), p1_c4_m3=bool(cons4_3 == tv))
    for s in SEATS:
        b = from_ann_row(V[s][cid])
        if b['kind'] == NAMED and str(b['grade']) == 'C':
            a = apply_h1_anchor(b, 'M3', 'B')
            flags.append(dict(cluster_id=cid, seat=s, model=SEATMODEL[s],
                              name=b['label'], truth=tv,
                              gate_ie=b['ie'], gate_res=b['res'], gate_tech=b['tech'],
                              anchor_applied=a['anchor_applied'], namedC_noanchor=a['namedC_noanchor'],
                              counted_c2b=True))  # C2b 计任意 grade 具名票（v2 语义）
    # sanity：基线复现逐簇
    assert (cons2b_0, mode2b_0) == frozen[cid], f'基线复现失败 {cid}: {(cons2b_0, mode2b_0)} != {frozen[cid]}'

def p1(col):
    hits = sorted([c for c in face_ids if rows[c][col]])
    return dict(count=len(hits), total=33, clusters=hits)

cols = dict(p1_c2b=p1('p1_c2b'), p1_c2b_m3=p1('p1_c2b_m3'), p1_c4=p1('p1_c4'), p1_c4_m3=p1('p1_c4_m3'))
named2b = sum(1 for c in face_ids if rows[c]['cons_c2b'] is not None)
named2b_m3 = sum(1 for c in face_ids if rows[c]['cons_c2b_m3'] is not None)
named4 = sum(1 for c in face_ids if rows[c]['cons_c4'] is not None)
named4_m3 = sum(1 for c in face_ids if rows[c]['cons_c4_m3'] is not None)
diff_2b = [c for c in face_ids if rows[c]['cons_c2b'] != rows[c]['cons_c2b_m3']]
anchor_votes = sum(1 for f in flags if f['anchor_applied'])
noanchor_votes = sum(1 for f in flags if f['namedC_noanchor'])

verdict = dict(
    gate='G2 回归门（OBLIGRUN v2 99 票 × H1-M3 敏感性，h1m3_runner 实装组件）',
    baseline_reproduction=dict(percluster_consensus_mode='33/33 逐簇全等（assert 通过）',
                               p1_c2b=f"{cols['p1_c2b']['count']}/33", expected='26/33',
                               matches_published=cols['p1_c2b']['count'] == 26 and
                               cols['p1_c2b']['clusters'] == sorted(ov['p1']['hit_clusters'])),
    sensitivity_main_column=dict(rule='C2b ∘ H1-M3(模式B)', p1=f"{cols['p1_c2b_m3']['count']}/33",
                                 expected_frozen='26/33（锚件 §4 C2b 吸收性=结构恒等）',
                                 delta_vs_main=cols['p1_c2b_m3']['count'] - 26,
                                 percluster_consensus_diff=len(diff_2b), diff_clusters=diff_2b,
                                 main_caliber_note='主口径当期 26/33 不动、verdict 件不回改（PREREG §3）'),
    ballot_inventory=dict(namedC_votes=len(flags), anchor_applied=anchor_votes,
                          namedC_noanchor=noanchor_votes,
                          expected_frozen='named∧C=13（A0/B4/C9）、升=11、不升=2（B席 Q6::2/Q6::30）',
                          matches_expected=(len(flags), anchor_votes, noanchor_votes) == (13, 11, 2)),
    reference_columns=dict(rule='C4 口径=参考列（非主口径、不进任何球门）',
                           p1_c4=f"{cols['p1_c4']['count']}/33", named_c4=named4,
                           p1_c4_m3=f"{cols['p1_c4_m3']['count']}/33", named_c4_m3=named4_m3,
                           anchor_gain_c4_named=named4_m3 - named4),
    named_counts_c2b=dict(base=named2b, m3=named2b_m3),
    PASS=None)
# 参考列不设 PASS 断言（只登记，见 reference_columns），防"换了规则又赢了"归因混淆
verdict['PASS'] = bool(verdict['baseline_reproduction']['matches_published']
                       and cols['p1_c2b_m3']['count'] == 26 and len(diff_2b) == 0
                       and verdict['ballot_inventory']['matches_expected'])
json.dump(dict(columns=cols, detail=verdict), open(f'{OUT}/out/g2_p1_columns.json', 'w'), ensure_ascii=False, indent=1)
pd.DataFrame([rows[c] for c in face_ids]).to_csv(f'{OUT}/out/g2_percluster.tsv', sep='\t', index=False)
pd.DataFrame(flags).to_csv(f'{OUT}/out/g2_ballot_flags.tsv', sep='\t', index=False)
print(json.dumps(verdict, ensure_ascii=False, indent=1))
sys.exit(0 if verdict['PASS'] else 2)
