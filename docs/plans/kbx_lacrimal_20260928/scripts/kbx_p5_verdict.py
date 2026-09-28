#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P5: C2b 裁决 + 三门判分（PREREG_v2 §7.4/§7.5）。
rule_c2=本地复刻（tiep t1_revote.py sha d321e793… 逐字同语义，count_coarse=True）；
实现自测=构造样例逐断言 PASS 后才跑真票（§7.6）。
输入: annotation/ANN_{A,B,C}_kbx.jsonl + out/kbx_cluster_table_raw.tsv + face + crosswalk
输出: scoring/kbx_verdict.json + out/kbx_percluster_verdict.tsv"""
import json, os, sys, collections

ROOT = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
SEATS = ('A', 'B', 'C')
TERM_NAMES = {'Lacrimal_secretory_tearcell', 'Lacrimal_duct_epithelial', 'Lacrimal_myoepithelial'}

# ---------- crosswalk ----------
CW = {}
for i, line in enumerate(open(f'{ROOT}/out/KBX_LG_CROSSWALK.tsv', encoding='utf-8')):
    if i == 0 or line.startswith('#') or not line.strip() or line.startswith('seat_name'):
        continue
    p = line.rstrip('\n').split('\t')
    if len(p) >= 2:
        CW[p[0].lower()] = p[1]
def xwalk(name):
    if name is None:
        return None
    return CW.get(str(name).strip().lower(), 'no_counterpart')

# ---------- ballot (t1_revote 逐字语义) ----------
def norm_identity(ident):
    if ident is None:
        return None
    s = str(ident)
    if s.startswith('undetermined'):
        return 'UNDET'
    if s.startswith('coarse:'):
        return 'COARSE'
    return s

def parse_ballot(raw, grade):
    g = None if grade is None else str(grade).strip()
    ni = norm_identity(raw)
    if ni is None:
        return dict(kind='MISSING', label=None, coarse=None, grade=g)
    if ni == 'UNDET':
        return dict(kind='UNDET', label=None, coarse=None, grade=g)
    if ni == 'COARSE':
        return dict(kind='COARSE', label=None, coarse=str(raw)[len('coarse:'):], grade=g)
    return dict(kind='NAMED', label=ni, coarse=None, grade=g)

def rule_c2(bs, count_coarse=True):
    cnt = collections.Counter()
    for b in bs:
        if b['kind'] == 'NAMED':
            cnt[b['label']] += 1
        elif count_coarse and b['kind'] == 'COARSE' and b['coarse']:
            cnt[b['coarse']] += 1
    if not cnt:
        return None
    top, n = cnt.most_common(1)[0]
    return top if n >= 2 else None

def c2b_mode(bs):
    name = rule_c2(bs)
    if name is None:
        cnt = collections.Counter()
        for b in bs:
            if b['kind'] == 'NAMED':
                cnt[b['label']] += 1
            elif b['kind'] == 'COARSE' and b['coarse']:
                cnt[b['coarse']] += 1
        if not cnt:
            return None, 'abstain3'
        if len(cnt) == sum(1 for b in bs if b['kind'] in ('NAMED', 'COARSE')) == 3:
            return None, 'split3'
        return None, 'tie'
    return name, 'named'

# ---------- 自测样例（§7.6 先于真票） ----------
def selftest():
    B = lambda kind, **kw: dict(kind=kind, label=kw.get('label'), coarse=kw.get('coarse'), grade=kw.get('grade', 'B'))
    cases = [
        # 任意 grade 定名票入数：A 席 C 票也数
        ([B('NAMED', label='Acinar_cell', grade='C'), B('NAMED', label='Acinar_cell', grade='A'), B('UNDET')],
         ('Acinar_cell', 'named')),
        # coarse:X 计入 X
        ([B('NAMED', label='Ductal_cell', grade='B'), B('COARSE', coarse='Ductal_cell'), B('UNDET')],
         ('Ductal_cell', 'named')),
        # 残余平票=无名
        ([B('NAMED', label='Acinar_cell'), B('NAMED', label='Ductal_cell'), B('NAMED', label='Endothelial_cell')],
         (None, 'split3')),
        # 单席不定名
        ([B('NAMED', label='Immune_cell'), B('MISSING'), B('MISSING')], (None, 'tie')),
    ]
    for bs, exp in cases:
        got = c2b_mode(bs)
        assert got == exp, f'selftest FAIL {got} != {exp}'
    print('selftest 4/4 PASS')

# ---------- 真票裁决 ----------
def main():
    selftest()
    if '--selftest-only' in sys.argv:
        print('SELFTEST-ONLY done'); return
    face = [json.loads(l) for l in open(f'{ROOT}/face/EV_DIGEST_SLIM_kbx.jsonl', encoding='utf-8')]
    order = [r['cluster_id'] for r in face]
    ballots = {}
    for s in SEATS:
        fp = f'{ROOT}/annotation/ANN_{s}_kbx.jsonl'
        if not os.path.exists(fp):
            print(f'MISSING {fp} — abort'); sys.exit(2)
        for l in open(fp, encoding='utf-8'):
            r = json.loads(l)
            ballots.setdefault(r['cluster_id'], {})[s] = r
    import pandas as pd
    tab = pd.read_csv(f'{ROOT}/out/kbx_cluster_table_raw.tsv', sep='\t')
    tab = tab[(tab['resolution'] == 'main') & (tab['cluster'].str.startswith('TIS::'))]
    truth = {r['cluster']: (r['top_group'], bool(r['anchored']), bool(r['leak_flag']), int(r['n_cells']))
             for _, r in tab.iterrows()}

    per = []
    denom = hits = p2 = 0
    group_counts = collections.Counter()
    buckets = collections.Counter()
    for cid in order:
        bs_raw = ballots.get(cid, {})
        bs = [parse_ballot(bs_raw.get(s, {}).get('identity') if s in bs_raw else None,
                           bs_raw.get(s, {}).get('grade')) for s in SEATS]
        cname, mode = c2b_mode(bs)
        xname = xwalk(cname) if cname else None
        grp, anch, leak, ncells = truth.get(cid, (None, False, False, 0))
        in_p1 = anch and not leak
        # coarse no_counterpart 桶（§5.2）
        nc_abst = any(b['kind'] == 'COARSE' and b['coarse'] and xwalk(b['coarse']) == 'no_counterpart' for b in bs)
        rec = {'cluster_id': cid, 'n_cells': ncells, 'truth_group': grp, 'anchored': anch, 'leak_flag': leak,
               'in_P1_denom': in_p1, 'consensus_raw': cname, 'consensus_mode': mode, 'consensus_xwalk': xname,
               'hit': (in_p1 and xname == grp),
               'term_named': cname in TERM_NAMES,
               'nc_coarse': nc_abst,
               'votes': {s: (bs_raw.get(s, {}).get('identity'), bs_raw.get(s, {}).get('grade')) for s in SEATS}}
        if in_p1:
            denom += 1
            group_counts[grp] += 1
            if xname == grp:
                hits += 1
                buckets['hit'] += 1
            elif cname in TERM_NAMES and xname not in (None, 'no_counterpart') and xname != grp:
                p2 += 1
                rec['P2_term_pollution'] = True
                buckets['P2_term_pollution'] += 1
            elif cname is None:
                buckets['abstain_or_tie'] += 1
            elif xname == 'no_counterpart':
                buckets['no_counterpart_name'] += 1
            else:
                buckets['wrong_named_other'] += 1
        per.append(rec)
    floor_grp, floor_n = (group_counts.most_common(1) or [(None, 0)])[0]
    floor = round(floor_n / denom, 4) if denom else None
    p1 = round(hits / denom, 4) if denom else None
    ci = None
    if denom:
        from scipy.stats import beta
        lo = beta.ppf(0.025, hits, denom - hits + 1) if hits > 0 else 0.0
        hi = beta.ppf(0.975, hits + 1, denom - hits) if hits < denom else 1.0
        ci = [round(lo, 4), round(hi, 4)]
    out = {'rule': 'v2/C2b', 'n_face': len(order), 'P1_denom': denom, 'P1_hits': hits, 'P1': p1,
           'P1_CP95CI': ci, 'P1_line': 0.60,
           'P1_gate': 'PASS' if (p1 is not None and p1 >= 0.60) else ('FAIL' if p1 is not None else 'N/A'),
           'majority_floor': floor, 'majority_group': floor_grp, 'group_composition': dict(group_counts),
           'P2_term_pollution': p2, 'P2_gate': 'PASS' if p2 <= 1 else 'FAIL',
           'P3_buckets': dict(buckets),
           'prereg_note': 'P3 归因表=out/kbx_percluster_verdict.tsv'}
    pd.DataFrame(per).to_csv(f'{ROOT}/out/kbx_percluster_verdict.tsv', sep='\t', index=False)
    json.dump(out, open(f'{ROOT}/scoring/kbx_verdict.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
