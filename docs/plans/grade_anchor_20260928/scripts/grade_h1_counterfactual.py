#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRADE-D16 步骤3：H1 判序锚反事实重算（零 LLM，同型案全库）
H1 三档操作化（对 NAMED∧grade==C 票施 grade 下限 B）：
- H1-S 严格：gates identity_evidence=pass ∧ resolution=pass ∧ technical∈{pass,na} 才升
- H1-M 中间：identity_evidence≠fail ∧ resolution≠fail ∧ technical≠fail 即升
- H1-X 一致性锚：NAMED∧C 一律升（协议不允许"具名+C"存在——要C必须改投 coarse:X/undet）
输出：各 archive 的翻转分类账 + R1/R2（视网膜45）+ grade 通胀风险计数。
"""
import json, pandas as pd, numpy as np, collections

OUT = '/mnt/D/EyeKB/plans/grade_anchor_20260928'
EVAL = '/mnt/D/EyeKB/plans/evalset'
M = pd.read_csv(f'{OUT}/data/ballot_matrix.tsv', sep='\t', keep_default_na=False, na_values=[''])
M['grade'] = M['grade'].astype(str)

# C4 实现（facev21_verdict 逐字语义）
def ballot(ni, g):
    if ni in (None, 'UNDET', 'COARSE', 'MISSING', ''):
        return None
    if str(g) not in ('A', 'B'):
        return None
    return ni

def c4(seatballs):
    votes = [b for b in seatballs if b]
    if not votes:
        return None, 'abstain3'
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority'
    if len(cnt) == len(votes) == 3:
        return None, 'split3'
    return None, 'tie'

VARIANTS = {
    'H1-S': lambda r: r['gate_identity_evidence'] == 'pass' and r['gate_resolution'] == 'pass' and str(r['gate_technical']) in ('pass', 'na', ''),
    'H1-M': lambda r: r['gate_identity_evidence'] != 'fail' and r['gate_resolution'] != 'fail' and str(r['gate_technical']) != 'fail',
    'H1-M2': lambda r: (r['gate_identity_evidence'] == 'pass' or r['gate_resolution'] == 'pass') and str(r['gate_technical']) != 'fail',
    'H1-M3': lambda r: (r['gate_identity_evidence'] == 'pass' or r['gate_resolution'] == 'pass'),
    'H1-X': lambda r: True,
}

ARCHIVES = ['RUN4-r', 'RUN7RG', 'FACEV21', 'BTEST-run1', 'BTEST-run2', 'RUN5', 'RUN6A', 'RUN6B', 'KB9']
TARGETS = json.load(open(f'{EVAL}/RUN4_TARGETS_v1.1.json'))
HOT, CTL = set(TARGETS['hotspots_22']), set(TARGETS['controls_23'])
r3 = pd.read_csv(f'{EVAL}/scoring/run3_object_B_table_v1.1.tsv', sep='\t').set_index('cluster_id')
DOUBLE_OK = {cid: bool(r3.loc[cid, 'matchA'] == True and r3.loc[cid, 'matchB'] == True)
             for cid in CTL if cid in r3.index}

def promote(row, vfun):
    """返回该票生效 grade（H1 后）"""
    if row['kind'] == 'NAMED' and row['grade'] == 'C' and vfun(row):
        return 'B'
    return row['grade']

def run_archive(arch, variant, vfun):
    sub = M[(M['archive'] == arch) & (M['missing'] == 0)]
    cids = sorted(sub['cluster_id'].unique())
    truth = {cid: sub[sub['cluster_id'] == cid]['truth'].iloc[0] for cid in cids}
    base_res, cf_res, promoted = {}, {}, []
    seats = sorted(sub['seat'].unique())
    for cid in cids:
        g = sub[sub['cluster_id'] == cid]
        base_b, cf_b = [], []
        for _, r in g.iterrows():
            base_b.append(ballot(r['identity_norm'] if pd.notna(r['identity_norm']) else None, r['grade']))
            g2 = promote(r, vfun)
            if g2 != r['grade']:
                promoted.append(dict(cluster_id=cid, seat=r['seat'], model=r['model'],
                                     name=r['identity_norm'], truth=r['truth'],
                                     hit=int(r['identity_norm'] == r['truth']),
                                     gate_ie=r['gate_identity_evidence'], gate_res=r['gate_resolution'],
                                     gate_tech=r['gate_technical'], flag=r['flag']))
            cf_b.append(ballot(r['identity_norm'] if pd.notna(r['identity_norm']) else None, g2))
        base_res[cid] = c4(base_b)[0]
        cf_res[cid] = c4(cf_b)[0]
    # 转移分类
    trans = collections.Counter()
    detail = []
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
            trans[key] += 1
            detail.append(dict(cid=cid, kind=key, base=b, cf=c, truth=t))
        elif (b is not None and str(b) == t) and c != t:
            key = 'regression_to_none' if (c is None or str(c) in ('', 'nan')) else 'regression_to_wrong'
            trans[key] += 1
            detail.append(dict(cid=cid, kind=key, base=b, cf=c, truth=t))
        elif (b is None or str(b) in ('', 'nan')) and c not in (None, '', 'nan') and c != t:
            trans['new_error_from_none'] += 1
            detail.append(dict(cid=cid, kind='new_error_from_none', base=b, cf=c, truth=t))
        else:
            trans['wrong_rename_or_other'] += 1
            detail.append(dict(cid=cid, kind='wrong_rename_or_other', base=b, cf=c, truth=t))
    named_base = sum(1 for v in base_res.values() if v and str(v) not in ('', 'nan', 'None'))
    named_cf = sum(1 for v in cf_res.values() if v and str(v) not in ('', 'nan', 'None'))
    # 视网膜 R1/R2
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
            return out
        r1 = dict(base=hits(base_res), cf=hits(cf_res))
        r2 = dict(base=errs(base_res), cf=errs(cf_res))
    return dict(archive=arch, variant=variant, n_clusters=len(cids),
                n_promoted=len(promoted),
                promoted_name_hit_rate=round(float(np.mean([p['hit'] for p in promoted])), 3) if promoted else None,
                transitions=dict(trans), named_base=named_base, named_cf=named_cf,
                R1=r1, R2=dict(base=r2['base'], cf=r2['cf']))

ALL, PROM, DETAIL = [], [], []
for arch in ARCHIVES:
    for vname, vfun in VARIANTS.items():
        res = run_archive(arch, vname, vfun)
        ALL.append(res)
        sub = M[(M['archive'] == arch) & (M['missing'] == 0)]
        for cid in sorted(sub['cluster_id'].unique()):
            for _, r in sub[sub['cluster_id'] == cid].iterrows():
                if r['kind'] == 'NAMED' and r['grade'] == 'C' and vfun(r):
                    PROM.append(dict(archive=arch, variant=vname, cluster_id=cid, seat=r['seat'],
                                     model=r['model'], name=r['identity_norm'], truth=r['truth'],
                                     hit=int(r['identity_norm'] == r['truth'])))

A = pd.DataFrame(ALL)
A.to_json(f'{OUT}/data/counterfactual_summary.json', orient='records', force_ascii=False, indent=1)
pd.DataFrame(PROM).to_csv(f'{OUT}/data/counterfactual_promoted.tsv', sep='\t', index=False)
print(A[['archive', 'variant', 'n_promoted', 'promoted_name_hit_rate', 'transitions', 'named_base', 'named_cf', 'R1', 'R2']].to_string(index=False))

# C2b 吸收性验证：H1 生效前后 C2b 共识应零变化（v2 已计任意 grade 具名票）
def parse_b(r):
    ni = r['identity_norm']; s = r['identity']
    if ni in (None, ''): return ('MISSING', None)
    if ni == 'UNDET': return ('UNDET', None)
    if ni == 'COARSE': return ('COARSE', s[len('coarse:'):])
    return ('NAMED', ni)
def rule_c2(bs):
    cnt = collections.Counter()
    for k, lab in bs:
        if k == 'NAMED': cnt[lab] += 1
        elif k == 'COARSE' and lab: cnt[lab] += 1
    if not cnt: return None
    top, n = cnt.most_common(1)[0]
    return top if n >= 2 else None
c2b_delta = 0
for arch in ARCHIVES:
    sub = M[(M['archive'] == arch) & (M['missing'] == 0)]
    for cid in sorted(sub['cluster_id'].unique()):
        g = sub[sub['cluster_id'] == cid]
        b0 = rule_c2([parse_b(r) for _, r in g.iterrows()])
        # grade 下限化不改变 kind/label → C2b 恒等（结构验证）
        b1 = rule_c2([parse_b(r) for _, r in g.iterrows()])
        c2b_delta += int(b0 != b1)
print('\nC2b 吸收性（grade 下限不改变 C2b 共识）: delta =', c2b_delta, '(结构恒等，H1 增量=0 under C2b)')
print('\nDONE h1 counterfactual')
