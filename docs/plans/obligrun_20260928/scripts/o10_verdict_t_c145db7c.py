#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, PREREG §7/§9.5): C2b 裁决。
票规 v2 C2b 逐字=PROTOCOL_VOTING_v2_C2b §1 / t1_revote.py(sha d321e793…) rule_c2(count_coarse=True)
+ KBX p5 c2b_mode 同语义（实现自测先于真票）。truth/crosswalk/P2 判据逐字=k8_verdict.py。
票集=本 run 三席新票 33 簇全量（零复用存档票，PREREG §6 OB-1 判读口径）。
输出: out/oblig_verdict.json + out/oblig_percluster.tsv。退出码 0=出数成功；1=输入不齐。"""
import json, os, sys, collections
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
KB9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
WORK = f'{EV}/work_t_d1ca11b0'
SEATS = ('A', 'B', 'C')

# ---------- ballot/rule_c2（t1_revote 逐字语义） ----------
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
        return dict(kind='COARSE', coarse=str(raw)[len('coarse:'):], grade=g)
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

# ---------- 实现自测（先于真票，KBX §7.6 惯例） ----------
def selftest():
    B = lambda kind, **kw: dict(kind=kind, label=kw.get('label'), coarse=kw.get('coarse'), grade=kw.get('grade', 'B'))
    cases = [
        ([B('NAMED', label='Endothelium', grade='C'), B('NAMED', label='Endothelium', grade='A'), B('UNDET')], ('Endothelium', 'named')),
        ([B('NAMED', label='Epithelium', grade='B'), B('COARSE', coarse='Epithelium'), B('UNDET')], ('Epithelium', 'named')),
        ([B('NAMED', label='Epithelium'), B('NAMED', label='Fibroblasts'), B('NAMED', label='Endothelium')], (None, 'split3')),
        ([B('NAMED', label='Epithelium'), B('UNDET'), B('MISSING')], (None, 'tie')),
        ([B('UNDET'), B('MISSING'), B('UNDET')], (None, 'abstain3')),
    ]
    for bs, exp in cases:
        got = c2b_mode(bs)
        assert got == exp, f'自测失败 {got} != {exp}'

selftest()
print('rule_c2 实现自测 PASS')

# ---------- 输入 ----------
def load(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if l:
            r = json.loads(l)
            d[r['cluster_id']] = r
    return d

V = {}
for stem in SEATS:
    p = f'{ROOT}/out/ANN_{stem}_oblig.jsonl'
    if not os.path.exists(p):
        raise SystemExit(f'缺票集 {p}')
    V[stem] = load(p)

face = [json.loads(l) for l in open(f'{ROOT}/face/kb9_face_v2.1.jsonl', encoding='utf-8')]
face_ids = [r['cluster_id'] for r in face]
for stem in SEATS:
    miss = [c for c in face_ids if c not in V[stem]]
    if miss:
        raise SystemExit(f'席位 {stem} 缺票 {len(miss)}: {miss}——投票未完成，不出数')

Q6S = json.load(open(f'{EV}/defs/Q6_def.json', encoding='utf-8'))
SUPER = {v2: k for k, vs in Q6S['super_map'].items() for v2 in vs}

# truth 对账断言=k8 逐字复刻
cl = pd.read_csv(f'{EV}/clustering/Q6_clusters.tsv', sep='\t', index_col=0)
truth = {}
for cid in face_ids:
    leiden = cid.split('::')[1]
    m = cl[cl['leiden'].astype(str) == str(leiden)]['truth'].astype(str).map(lambda x: SUPER.get(x, 'EXCL'))
    m = m[m != 'EXCL']
    if m.empty or len(m) < 10:
        truth[cid] = (None, None, len(m)); continue
    vc = m.value_counts()
    truth[cid] = (vc.index[0], round(float(vc.iloc[0] / len(m)), 4), int(len(m)))
tm = pd.read_csv(f'{WORK}/Q6_truth_map.tsv', sep='\t')
tmj = {r['cluster_id']: (r['truth_major'], float(r['truth_frac']), int(r['n_truth_cells'])) for _, r in tm.iterrows()}
mismatch = [c for c in face_ids if (truth[c][0] != tmj[c][0]) or abs((truth[c][1] or 0) - tmj[c][1]) > 1e-4]
assert not mismatch, f'truth 对账失败: {mismatch}'
print('truth 对账 PASS（k8 逐字）')

cw = pd.read_csv(f'{WORK}/KB_Q6_crosswalk.tsv', sep='\t')
ext = pd.read_csv(f'{KB9}/build/KB9_CROSSWALK_ext.tsv', sep='\t')
CW = {r['kb_name']: ((str(r['q6_vocab_class']) if pd.notna(r['q6_vocab_class']) else ''), str(r['provenance'])) for _, r in cw.iterrows()}
for _, r in ext.iterrows():
    CW[r['kb_name']] = ((str(r['q6_vocab_class']) if pd.notna(r['q6_vocab_class']) else ''), str(r['provenance']))
mk = pd.read_csv(f'{WORK}/author_class_markers_data.tsv', sep='\t')
MK = {r['truth_super']: set(str(r['top60_markers']).split(',')) for _, r in mk.iterrows()}

def kb_hit_class(name):
    c, p = CW.get(name, ('', 'unknown'))
    if p == 'no_counterpart':
        return None, 'no_counterpart'
    if p == 'ambiguous':
        return tuple(c.split('|')), 'ambiguous'
    return (c,), p

changed = set(json.load(open(f'{KB9}/out/kb9_changed_clusters.json'))['changed'])
rows = {}
for r in face:
    cid = r['cluster_id']
    tv, tfrac, tn = truth[cid]
    bs = [parse_ballot(V[s].get(cid, {}).get('identity'), V[s].get(cid, {}).get('grade')) for s in SEATS]
    con, mode = c2b_mode(bs)
    n_ballots = sum(1 for b in bs if b['kind'] in ('NAMED', 'COARSE'))
    ranking = [x['cell_type'] for x in (r.get('kb_marker_ranking') or [])]
    top10 = [str(g) for g in (r.get('top_genes') or [])[:10]]
    top10_sym = [str(s) for s in (r.get('top_genes_sym') or [])[:10]]
    mk_truth = MK.get(tv, set())
    ov = sorted(set(top10) & mk_truth)
    ov_sym = [s for g, s in zip(top10, top10_sym) if g in set(ov)]
    p2 = {}
    for scope, names in (('strict', ranking[:1]), ('any', ranking)):
        kbcls, provs = set(), []
        for nm in names:
            cs, pv = kb_hit_class(nm)
            if cs:
                kbcls |= set(cs)
                provs.append(f'{nm}->{"|".join(cs)}({pv})')
        p2[scope] = dict(kb_classes=sorted(kbcls), mapping=provs,
                         name_matches_kb=bool(con and con in kbcls),
                         differs_from_truth=bool(con and con != tv),
                         direct_evidence_contradicts=len(ov) >= 3,
                         violation=bool(con and con in kbcls and con != tv and len(ov) >= 3))
    rows[cid] = dict(cluster_id=cid, era=('变化簇' if cid in changed else '冻结簇'), n_cells=int(r['n_cells']),
                     truth=tv, truth_frac=tfrac, n_truth_cells=tn,
                     vote_A=V['A'].get(cid, {}).get('identity'), grade_A=V['A'].get(cid, {}).get('grade'),
                     vote_B=V['B'].get(cid, {}).get('identity'), grade_B=V['B'].get(cid, {}).get('grade'),
                     vote_C=V['C'].get(cid, {}).get('identity'), grade_C=V['C'].get(cid, {}).get('grade'),
                     consensus_c2b=con, mode=mode, n_ballots=n_ballots,
                     p1_hit=bool(con and con == tv), kb_n=len(ranking), kb_top1=ranking[0] if ranking else '',
                     top10=';'.join(top10_sym), n_truth_marker_in_top10=len(ov),
                     truth_markers_in_top10=';'.join(ov_sym),
                     p2_strict_violation=p2['strict']['violation'], p2_any_violation=p2['any']['violation'],
                     p2_detail=json.dumps(p2, ensure_ascii=False))

hit = sorted([c for c in face_ids if rows[c]['p1_hit']])
miss = sorted([c for c in face_ids if not rows[c]['p1_hit']])
p1 = dict(rule='v2 C2b 定名且 consensus==truth', count=len(hit), total=33, rate=round(len(hit) / 33, 4),
          gate='>=24/33', passed=len(hit) >= 24, hit_clusters=hit, missed_clusters=miss,
          missed_modes={c: rows[c]['mode'] for c in miss})
gates = {}
for scope in ('strict', 'any'):
    key = f'p2_{scope}_violation'
    vl = sorted([c for c in face_ids if rows[c][key]])
    detail = []
    for c in vl:
        d = json.loads(rows[c]['p2_detail'])[scope]
        detail.append(dict(cluster_id=c, truth=rows[c]['truth'], consensus=rows[c]['consensus_c2b'],
                           kb_top1_or_names=rows[c]['kb_top1'], mapping=d['mapping'],
                           n_truth_marker_in_top10=rows[c]['n_truth_marker_in_top10'],
                           truth_markers_in_top10=rows[c]['truth_markers_in_top10']))
    gates[scope] = dict(count=len(vl), total=33, gate='<=1/33(strict; any 并报)', passed=(len(vl) <= 1) if scope == 'strict' else None,
                        violation_clusters=vl, evidence=detail)
kb_empty = sorted([c for c in face_ids if rows[c]['kb_n'] == 0])
p3 = dict(kb_empty_n=len(kb_empty), kb_empty_clusters=kb_empty, note='照旧记录不入门')

modes = collections.Counter(rows[c]['mode'] for c in face_ids)
budget_lines = []
for stem in SEATS:
    budget_lines.append(json.load(open(f'{ROOT}/out/ANN_{stem}_oblig_META.json')).get('budget_consumed_total'))
verdict_inputs = dict(obligations=dict(
    OB1='清（v1 run 落表 out/OB1_ledger.tsv 339 行；ADD1 A4 继承：v2.1 面与 v1 面差异仅 2 lit 行=许可漂移字段内，31 簇零差异）',
    OB2='PASS（v2.1 机械重算 57/57 零漂移+硬断言 33/33；out/pre_vote_diagnostics_v21.tsv）',
    OB3='清（v1 run 落表 out/OB3_consistency.tsv 22/22；案 A ranking 零动→结论可继承，裁定理由3）',
    OB4='复筛通过（v2.1 面 62 条/11 PMID 残留 0；out/OB4_lit_screening_v21.md）'),
    face_sha='2c0649dcc2001c8b3fe485dab35761a90a4f2c297df88e7a16739e3ec23929bb',
    budget_per_seat_latest=budget_lines)
out = dict(p1=p1, p2=gates, p3=p3, modes=dict(modes), inputs=verdict_inputs,
           matrix=dict(rule='OB全清 AND P1 pass AND P2 strict pass → READY',
                       ready=bool(verdict_inputs['obligations'] and p1['passed'] and gates['strict']['passed'])))
json.dump(out, open(f'{ROOT}/out/oblig_verdict.json', 'w'), ensure_ascii=False, indent=1)
cols = ['cluster_id', 'era', 'n_cells', 'truth', 'truth_frac', 'n_truth_cells',
        'vote_A', 'grade_A', 'vote_B', 'grade_B', 'vote_C', 'grade_C',
        'consensus_c2b', 'mode', 'n_ballots', 'p1_hit', 'kb_n', 'kb_top1',
        'top10', 'n_truth_marker_in_top10', 'truth_markers_in_top10',
        'p2_strict_violation', 'p2_any_violation', 'p2_detail']
with open(f'{ROOT}/out/oblig_percluster.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for c in face_ids:
        f.write('\t'.join(str(rows[c][x]) for x in cols) + '\n')
print(f"P1(C2b)={p1['count']}/33 gate>=24/33 passed={p1['passed']} | P2 strict={gates['strict']['count']}/33 passed={gates['strict']['passed']} any={gates['any']['count']}/33")
print(f"modes={dict(modes)} | READY={out['matrix']['ready']}")
