#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门1 = 复算门（PREREG_H1M3 §2）：9 归档 × H1-M3(模式B) 反事实，经 h1m3_runner 实装组件重放，
与 grade_anchor/data/counterfactual_summary.json（冻结锚件，SHA_PRE 台账在册）逐档一致。
零 LLM、零网络；R2 集合比较按内容不按迭代序（锚件列表序=其进程 set 迭代序，哈希随机化不可复现，
内容集合全等即为一致——已在 REPORT 声明）。任一不一致=停卡上报，禁就地改锚。"""
import sys, json, collections
import pandas as pd

sys.path.insert(0, '/mnt/D/EyeKB/plans/grade_h1m3impl_20260928/scripts')
from h1m3_runner_t_e0f94d4f import from_matrix_row, apply_h1_anchor, c4_count, consensus

OUT = '/mnt/D/EyeKB/plans/grade_h1m3impl_20260928'
ANCHOR = '/mnt/D/EyeKB/plans/grade_anchor_20260928'
EVAL = '/mnt/D/EyeKB/plans/evalset'

M = pd.read_csv(f'{ANCHOR}/data/ballot_matrix.tsv', sep='\t', keep_default_na=False, na_values=[''])
M['grade'] = M['grade'].astype(str)
REF = {(r['archive']): r for r in json.load(open(f'{ANCHOR}/data/counterfactual_summary.json'))
       if r['variant'] == 'H1-M3'}
ARCHIVES = ['RUN4-r', 'RUN7RG', 'FACEV21', 'BTEST-run1', 'BTEST-run2', 'RUN5', 'RUN6A', 'RUN6B', 'KB9']
assert set(ARCHIVES) == set(REF), '归档清单与锚件不符'

TARGETS = json.load(open(f'{EVAL}/RUN4_TARGETS_v1.1.json'))
HOT, CTL = set(TARGETS['hotspots_22']), set(TARGETS['controls_23'])
r3 = pd.read_csv(f'{EVAL}/scoring/run3_object_B_table_v1.1.tsv', sep='\t').set_index('cluster_id')
DOUBLE_OK = {cid: bool(r3.loc[cid, 'matchA'] == True and r3.loc[cid, 'matchB'] == True)
             for cid in CTL if cid in r3.index}

def run_archive(arch):
    sub = M[(M['archive'] == arch) & (M['missing'] == 0)]
    cids = sorted(sub['cluster_id'].unique())
    truth = {cid: sub[sub['cluster_id'] == cid]['truth'].iloc[0] for cid in cids}
    base_res, cf_res, promoted = {}, {}, []
    for cid in cids:
        g = sub[sub['cluster_id'] == cid]
        bb, cb = [], []
        for _, r in g.iterrows():
            b0 = from_matrix_row(r)
            bb.append(b0)
            b1 = apply_h1_anchor(b0, 'M3', 'B')
            if b1['anchor_applied']:
                promoted.append(dict(cluster_id=cid, seat=r['seat'], model=r['model'],
                                     name=b0['label'], truth=r['truth'],
                                     hit=int(b0['label'] == r['truth'] and pd.notna(r['truth']))))
            cb.append(b1)
        base_res[cid] = c4_count(bb)[0]
        cf_res[cid] = c4_count(cb)[0]
    trans, detail = collections.Counter(), []
    for cid in cids:
        b, c, t = base_res.get(cid), cf_res.get(cid), truth.get(cid)
        if pd.isna(t):
            t = None
        if b == c:
            trans['unchanged'] += 1
            continue
        if t is None:
            trans[f'changed_noTruth({b}->{c})'] += 1
            continue
        if c == t and b != t:
            key = 'rectified_from_none' if (b is None or str(b) in ('', 'nan')) else 'rectified_from_wrong'
        elif (b is not None and str(b) == t) and c != t:
            key = 'regression_to_none' if (c is None or str(c) in ('', 'nan')) else 'regression_to_wrong'
        elif (b is None or str(b) in ('', 'nan')) and c not in (None, '', 'nan') and c != t:
            key = 'new_error_from_none'
        else:
            key = 'wrong_rename_or_other'
        trans[key] += 1
        detail.append(dict(cid=cid, kind=key, base=b, cf=c, truth=t))
    named_base = sum(1 for v in base_res.values() if v and str(v) not in ('', 'nan', 'None'))
    named_cf = sum(1 for v in cf_res.values() if v and str(v) not in ('', 'nan', 'None'))
    r1 = dict(base=None, cf=None)
    r2 = dict(base=None, cf=None)
    if arch not in ('RUN5', 'RUN6A', 'RUN6B', 'KB9'):
        def hits(res):
            return sum(1 for cid in HOT if cid in res and res[cid] == truth.get(cid))
        def errs(res):
            out = []
            for cid in CTL:
                if cid in res and DOUBLE_OK.get(cid) and truth.get(cid) is not None:
                    if not (res[cid] and str(res[cid]) == str(truth.get(cid))):
                        out.append(cid)
            return sorted(out)
        r1 = dict(base=hits(base_res), cf=hits(cf_res))
        r2 = dict(base=errs(base_res), cf=errs(cf_res))
    return dict(archive=arch, variant='H1-M3', n_clusters=len(cids), n_promoted=len(promoted),
                promoted_name_hit_rate=(round(float(sum(p['hit'] for p in promoted) / len(promoted)), 3)
                                        if promoted else None),
                transitions=dict(trans), named_base=named_base, named_cf=named_cf,
                R1=r1, R2=dict(base=r2['base'], cf=sorted(r2['cf']) if r2['cf'] is not None else None))

rows, all_match, TOTAL = [], True, dict(promoted=0, rectified=0, newerr=0, regress=0)
FIELDS = ['n_clusters', 'n_promoted', 'promoted_name_hit_rate', 'transitions', 'named_base', 'named_cf']
for arch in ARCHIVES:
    got = run_archive(arch)
    ref = REF[arch]
    diffs = [f for f in FIELDS if got[f] != ref[f]]
    if got['R1'] != ref['R1']:
        diffs.append('R1')
    for k in ('base', 'cf'):
        gv, rv = got['R2'][k], ref['R2'][k]
        if (None if gv is None else sorted(gv)) != (None if rv is None else sorted(rv)):
            diffs.append(f'R2.{k}')
    match = not diffs
    all_match &= match
    t = got['transitions']
    TOTAL['promoted'] += got['n_promoted']
    TOTAL['rectified'] += t.get('rectified_from_none', 0) + t.get('rectified_from_wrong', 0)
    TOTAL['newerr'] += t.get('new_error_from_none', 0) + t.get('wrong_rename_or_other', 0)
    TOTAL['regress'] += t.get('regression_to_none', 0) + t.get('regression_to_wrong', 0)
    rows.append(dict(archive=arch, match=match, diffs=';'.join(diffs) or '',
                     n_promoted=got['n_promoted'], hit=got['promoted_name_hit_rate'],
                     transitions=json.dumps(got['transitions'], ensure_ascii=False, sort_keys=True),
                     ref_transitions=json.dumps(ref['transitions'], ensure_ascii=False, sort_keys=True),
                     named=f"{got['named_base']}->{got['named_cf']}",
                     R1=f"{got['R1']['base']}->{got['R1']['cf']}",
                     R2cf=json.dumps(got['R2']['cf'], sort_keys=True)))
    print(f"{arch:12s} match={match} {'OK' if match else 'DIFF: ' + ','.join(diffs)}")

# 锚件汇总预期复核（GRADE_ANCHOR §3 网格 + §4：升24/正确91.7%/翻正7/新错0/回归0）
expect = dict(promoted=24, rectified=7, newerr=0, regress=0)
head_ok = all(TOTAL[k] == v for k, v in expect.items())
pd.DataFrame(rows).to_csv(f'{OUT}/out/g1_perarchive.tsv', sep='\t', index=False)
verdict = dict(gate='G1 复算门（9 归档 × H1-M3 模式B via h1m3_runner）',
               per_archive_all_match=bool(all_match), headcounts=TOTAL, expected_headcounts=expect,
               headcounts_match_anchor_doc=bool(head_ok),
               promoted_hit_rate=round(22 / 24, 3),
               PASS=bool(all_match and head_ok), ts=json.dumps(__import__('datetime').datetime.now().isoformat()))
# 升票隐藏名正确率（锚件 24 票中正确名计数=91.7%→22/24）复核
PROM = []
for arch in ARCHIVES:
    sub = M[(M['archive'] == arch) & (M['missing'] == 0)]
    for _, r in sub.iterrows():
        b0 = from_matrix_row(r)
        if b0['kind'] == 'NAMED' and b0['grade'] == 'C' and apply_h1_anchor(b0, 'M3', 'B')['anchor_applied']:
            PROM.append(int(b0['label'] == r['truth'] and pd.notna(r['truth'])))
verdict['promoted_votes'] = len(PROM)
verdict['promoted_name_correct'] = sum(PROM)
verdict['promoted_hit_rate_measured'] = round(sum(PROM) / len(PROM), 3) if PROM else None
verdict['hit_rate_match_anchor'] = verdict['promoted_name_correct'] == 22
verdict['PASS'] = bool(all_match and head_ok and verdict['hit_rate_match_anchor'])
json.dump(verdict, open(f'{OUT}/out/g1_verdict.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(verdict, ensure_ascii=False, indent=1))
sys.exit(0 if verdict['PASS'] else 2)
