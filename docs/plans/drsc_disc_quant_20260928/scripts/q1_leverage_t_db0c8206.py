#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DISC_QANT Task A (D-2): leave-one-donor-out 翻否杠杆 只读量化.
卡 t_db0c8206 ｜ 任务书 <EYEKB>/plans/drsc_disc_quant_20260928/BRIEF_DISC_QANT.md
双口径: (1) 冻结票面=obligrun v2.1 三席票(99票) (2) 评估卷=RUN5 冻结三席票(同33簇).
票规 v2 C2b 逐字复刻 o10_verdict_t_c145db7c.py (rule_c2/c2b_mode/parse_ballot) —— 球门零移动零改算, 票不重投.
truth 逐字复刻 o10 (SUPER 折叠 + EXCL 剔除 + n>=10 + value_counts.index[0]); 另记并列(tie)态供取严口径.
输出: LEVERAGE_table_units.tsv (口径x簇xdonor) + LEVERAGE_summary.tsv + PANEL_LOO_donors.tsv + q1_stats.json
领地: 只读冻结件; 只写本卡目录. CPU only.
"""
import json, os, sys, collections
import pandas as pd

ROOT = '<EYEKB>/plans/drsc_disc_quant_20260928'
OBLIG = '<EYEKB>/plans/obligrun_20260928'
EV = '<EYEKB>/plans/evalset'
WORK = f'{EV}/work_t_d1ca11b0'
OUT = f'{ROOT}/out'
os.makedirs(OUT, exist_ok=True)
SEATS = ('A', 'B', 'C')

# ---------- C2b 实现（o10_verdict_t_c145db7c.py 逐字复刻） ----------
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
print('rule_c2 自测 PASS（o10 逐字）', flush=True)

# ---------- 输入（只读） ----------
def load_ballots(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if l:
            r = json.loads(l)
            d[r['cluster_id']] = r
    return d

SCOPES = {
    '票面v2.1(oblig)': [f'{OBLIG}/out/ANN_{s}_oblig.jsonl' for s in SEATS],
    '评估卷(RUN5)':    [f'{EV}/annotation/ANN_{s}_run5.jsonl' for s in SEATS],
}
V = {}
for sc, paths in SCOPES.items():
    V[sc] = [load_ballots(p) for p in paths]

face = [json.loads(l) for l in open(f'{OBLIG}/face/kb9_face_v2.1.jsonl', encoding='utf-8')]
face_ids = [r['cluster_id'] for r in face]
assert len(face_ids) == 33

Q6S = json.load(open(f'{EV}/defs/Q6_def.json', encoding='utf-8'))
SUPER = {v2: k for k, vs in Q6S['super_map'].items() for v2 in vs}

cl = pd.read_csv(f'{EV}/clustering/Q6_clusters.tsv', sep='\t', index_col=0)
cl['leiden'] = cl['leiden'].astype(str)
cl['donor'] = cl['donor'].astype(str)
cl['super'] = cl['truth'].astype(str).map(lambda x: SUPER.get(x, 'EXCL'))

# ---------- consensus（票不重投；named 集对 donor 删除不变，逐簇记录） ----------
def consensus_of(scope, cid):
    bs = [parse_ballot(v.get(cid, {}).get('identity'), v.get(cid, {}).get('grade')) for v in V[scope]]
    return c2b_mode(bs)

# ---------- truth 计算（全样 + 删 donor 后） ----------
def truth_calc(sub, tie_strict=True):
    """sub: DataFrame(含 'super')。返回 (truth_pandas, tie_flag, n_pool)
    truth_pandas = value_counts.index[0]（o10 逐字）; tie=True 表示并列（取严口径下判翻否时用 strict 规则）。"""
    m = sub['super']
    m = m[m != 'EXCL']
    n = int(len(m))
    if n < 10:
        return None, False, n
    vc = m.value_counts()
    top = int(vc.iloc[0])
    n_top = int((vc == top).sum())
    return str(vc.index[0]), (n_top > 1), n

def truth_full(cid):
    leiden = cid.split('::')[1]
    sub = cl[cl['leiden'] == leiden]
    return truth_calc(sub)

# ---- 冻结对账断言: 全样 truth == Q6_truth_map; oblig P1==冻结 verdict ----
tm = pd.read_csv(f'{WORK}/Q6_truth_map.tsv', sep='\t')
tmj = {r['cluster_id']: (r['truth_major'], float(r['truth_frac']), int(r['n_truth_cells'])) for _, r in tm.iterrows()}
tf = {c: truth_full(c) for c in face_ids}
mis = [c for c in face_ids if tf[c][0] != tmj[c][0]]
assert not mis, f'truth 对账失败: {mis}'
print('truth 全样对账 PASS（=o10/k8 口径）', flush=True)

hit0 = {}
for sc in SCOPES:
    hs = []
    for cid in face_ids:
        con, mode = consensus_of(sc, cid)
        tv, tie, n = tf[cid]
        if con and con == tv:
            hs.append(cid)
    hit0[sc] = set(hs)
ob_hit_frozen = set(json.load(open(f'{OBLIG}/out/oblig_verdict.json'))['p1']['hit_clusters'])
assert hit0['票面v2.1(oblig)'] == ob_hit_frozen, 'oblig P1 复算 != 冻结 verdict（禁回改，须停卡）'
print(f"票面v2.1 复算 P1={len(hit0['票面v2.1(oblig)'])}/33 与冻结件逐簇一致; 评估卷(RUN5) C2b 复算 P1={len(hit0['评估卷(RUN5)'])}/33", flush=True)

# ---------- 逐单元 donor LOO（只对 hit 单元, 任务书口径） ----------
rows = []
for sc in SCOPES:
    for cid in sorted(hit0[sc], key=lambda c: int(c.split('::')[1])):
        leiden = cid.split('::')[1]
        sub = cl[cl['leiden'] == leiden]
        con, mode = consensus_of(sc, cid)
        tv0, tie0, n0 = tf[cid]
        hit0f = (con == tv0)
        donors = sorted(sub['donor'].unique())
        for d in donors:
            rest = sub[sub['donor'] != d]
            tv1, tie1, n1 = truth_calc(rest)
            # strict 口径: 并列(tie) → truth 视未定（None）
            tv1_strict = None if tie1 else tv1
            hit_loose = bool(con and con == tv1)
            # 取严口径: 删除后 truth 并列 → 判未定（None），不猜 index[0]
            hit_strict = bool(con and con == tv1_strict)
            flip_type = ''
            if hit0f and not hit_strict:
                flip_type = ('unit_dies' if n1 == 0 else
                             'shrink_out' if n1 < 10 else
                             'tie_undetermined' if tie1 else 'label_flip')
            rows.append(dict(scope=sc, cluster_id=cid, n_cells_unit=int(len(sub)), truth=tv0, consensus=con,
                             hit=hit0f, donor=d, donor_cells=int((sub['donor'] == d).sum()),
                             n_after=n1, truth_after=tv1, tie_after=tie1,
                             hit_after_loose=hit_loose, hit_after_strict=hit_strict,
                             flip_strict=bool(hit0f and not hit_strict), flip_loose=bool(hit0f and not hit_loose),
                             flip_type=flip_type))
lev = pd.DataFrame(rows)
lev.to_csv(f'{OUT}/LEVERAGE_table_units.tsv', sep='\t', index=False)
print(f'杠杆表 {len(lev)} 行 → LEVERAGE_table_units.tsv', flush=True)

# ---------- 逐单元汇总 ----------
summ = []
for sc in SCOPES:
    for cid in sorted(hit0[sc], key=lambda c: int(c.split('::')[1])):
        g = lev[(lev.scope == sc) & (lev.cluster_id == cid)]
        n_donors = len(g)
        n_flip = int(g.flip_strict.sum())
        n_flip_loose = int(g.flip_loose.sum())
        dom = g.loc[g.donor_cells.idxmax()]
        flip_share = g.loc[g.flip_strict, 'donor_cells'].max() if n_flip else 0
        summ.append(dict(scope=sc, cluster_id=cid, n_donors=n_donors,
                         unit_size=int(g.n_cells_unit.iloc[0]),
                         dominant_donor=dom.donor, dominant_share=round(float(dom.donor_cells) / float(g.n_cells_unit.iloc[0]), 4),
                         n_flip_donors_strict=n_flip, n_flip_donors_loose=n_flip_loose,
                         single_donor_flip_strict=bool(n_flip >= 1), single_donor_flip_loose=bool(n_flip_loose >= 1),
                         flip_donor_share_pct=round(100.0 * float(flip_share) / float(g.n_cells_unit.iloc[0]), 2) if n_flip else 0.0,
                         flip_types=';'.join(sorted(set(g.loc[g.flip_strict, 'flip_type']))) if n_flip else ''))
sm = pd.DataFrame(summ)
sm.to_csv(f'{OUT}/LEVERAGE_summary.tsv', sep='\t', index=False)

# ---------- 面板级 LOO（每 donor 从全 33 簇删, 重算 truth → 新 P1） ----------
pan = []
all_donors = sorted(cl['donor'].unique())
for sc in SCOPES:
    cons = {cid: consensus_of(sc, cid) for cid in face_ids}
    for d in all_donors:
        cnt = 0
        flipped_units = []
        for cid in face_ids:
            leiden = cid.split('::')[1]
            sub = cl[(cl['leiden'] == leiden) & (cl['donor'] != d)]
            tv1, tie1, n1 = truth_calc(sub)
            tv1 = None if tie1 else tv1
            con, mode = cons[cid]
            hit = bool(con and con == tv1)
            if hit:
                cnt += 1
            if cid in hit0[sc] and not hit:
                flipped_units.append(cid)
        pan.append(dict(scope=sc, donor=d, donor_cells_total=int((cl['donor'] == d).sum()),
                        p1_after=cnt, p1_before=len(hit0[sc]),
                        gate_breaks=bool(cnt < 24), flipped_units=';'.join(sorted(flipped_units, key=lambda c: int(c.split('::')[1])))))
pn = pd.DataFrame(pan)
pn.to_csv(f'{OUT}/PANEL_LOO_donors.tsv', sep='\t', index=False)
print('面板级 LOO → PANEL_LOO_donors.tsv', flush=True)

# ---------- 分布统计 + 三档实测 ----------
stats = {}
for sc in SCOPES:
    g = sm[sm.scope == sc]
    n_hit = len(g)
    nf = int(g.single_donor_flip_strict.sum())
    nfl = int(g.single_donor_flip_loose.sum())
    p = pn[pn.scope == sc]
    stats[sc] = dict(
        hit_units=n_hit,
        units_flip_strict=nf, units_flip_loose=nfl,
        pct_flip_strict=round(100.0 * nf / n_hit, 2), pct_flip_loose=round(100.0 * nfl / n_hit, 2),
        flip_type_hist=dict(collections.Counter(t for s in g.flip_types if s for t in s.split(';'))),
        n_donors_per_unit_med=int(g.n_donors.median()),
        panel_gatebreak_donors=list(p.loc[p.gate_breaks, 'donor']),
        panel_min_p1=int(p.p1_after.min()), panel_p1_before=n_hit,
        # 三档实测
        tier1_flag_units=nf,                      # 单 donor 翻转即旗标(单元级)
        tier2_panel_alarm=bool(100.0 * nf / n_hit >= 20.0), tier2_flag_units=n_hit if 100.0 * nf / n_hit >= 20.0 else 0,  # ≥20%单元翻转→面板警戒
        tier3_flag_units=0,                       # 仅记录不门控
    )
json.dump(stats, open(f'{OUT}/q1_stats.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(stats, ensure_ascii=False, indent=1), flush=True)
print('Q1 DONE', flush=True)
