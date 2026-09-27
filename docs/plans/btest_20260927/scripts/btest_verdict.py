#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTEST 裁决（判据件 BTEST_PREREG_v1.0.md §2/§5/§6/§7/§4.4）。
顺序硬约束：先稳定性门（§5），不过门 → 只出诊断报告，禁 A/B 判读。
C4 = kb2_bscore_v4_truthfix exec-head 逐字复用（与 facev21_verdict 同实现源）。
C2b = TIEP t1_revote.py rule_c2(count_coarse=True) 语义逐字复用 + 与 TIEP 已发布
revote_matrix(face=FACEV21) name_C2b 列逐簇对账（不等即中止，双实现交叉验证）。
主判读票 = run1（钉死）；run2 仅稳定性样本，其 R1/R2/保全为诊断列。"""
import json, collections, sys, datetime, pandas as pd

ROOT = '/mnt/D/EyeKB/plans/btest_20260927'
EVAL = '/mnt/D/EyeKB/plans/evalset'
F21 = '/mnt/D/EyeKB/plans/face_v21_20260926'
TIEP = '/mnt/D/EyeKB/plans/tiep_20260927'

src = open(f'{EVAL}/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py').read()
head = src.split('def summarize')[0]
ns = {'__name__': 'ctx'}
exec(compile(head, 'h', 'exec'), ns)
truth_major, norm_identity, load = ns['truth_major'], ns['norm_identity'], ns['load']

T = json.load(open(f'{EVAL}/RUN4_TARGETS_v1.1.json'))
hot, ctl = set(T['hotspots_22']), set(T['controls_23'])
assert len(hot) == 22 and len(ctl) == 23
hs = pd.read_csv(f'{EVAL}/scoring/run3_M4_hotspots_v1.1.tsv', sep='\t')
assert set(hs[hs['high_purity'] == True]['cluster_id']) == hot, '§1 靶断言失败'
r3 = pd.read_csv(f'{EVAL}/scoring/run3_object_B_table_v1.1.tsv', sep='\t').set_index('cluster_id')
fv = json.load(open(f'{F21}/scoring/FACEV21_VERDICT.json'))
frows = fv['rows']
base = json.load(open(f'{EVAL}/scoring/run4r_verdict.json'))
brows = base['rows']


def ballot(r):  # C4 有效票（facev21_verdict 逐字同）
    if not r:
        return None
    ni = norm_identity(None, r.get('identity'))
    if ni in (None, 'UNDET', 'COARSE'):
        return None
    if str(r.get('grade')) not in ('A', 'B'):
        return None
    return ni


def consensus(A_, B_, C_, cid):  # C4（facev21_verdict 逐字同）
    votes = [b for b in (ballot(A_.get(cid)), ballot(B_.get(cid)), ballot(C_.get(cid))) if b]
    if not votes:
        return None, 'abstain3', 0
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority', len(votes)
    if len(cnt) == len(votes) and len(votes) == 3:
        return None, 'split3', 3
    return None, 'tie', len(votes)


def parse_tiep(raw, grade):  # TIEP t1_revote.py parse_ballot 逐字语义
    g = None if grade is None else str(grade).strip()
    s = '' if raw is None else str(raw)
    if raw is None:
        ni = None
    elif s.startswith('undetermined'):
        ni = 'UNDET'
    elif s.startswith('coarse:'):
        ni = 'COARSE'
    else:
        ni = s
    if ni is None:
        return dict(kind='MISSING', label=None, coarse=None, grade=g)
    if ni == 'UNDET':
        return dict(kind='UNDET', label=None, coarse=None, grade=g)
    if ni == 'COARSE':
        return dict(kind='COARSE', label=None, coarse=s[len('coarse:'):], grade=g)
    return dict(kind='NAMED', label=ni, coarse=None, grade=g)


def rule_c2(bs):  # TIEP rule_c2(count_coarse=True) 逐字
    cnt = collections.Counter()
    for b in bs:
        if b['kind'] == 'NAMED':
            cnt[b['label']] += 1
        elif b['kind'] == 'COARSE' and b['coarse']:
            cnt[b['coarse']] += 1
    if not cnt:
        return None
    top, n = cnt.most_common(1)[0]
    return top if n >= 2 else None


def c2b_consensus(dicts, cid):
    bs = [parse_tiep(d.get(cid, {}).get('identity'), d.get(cid, {}).get('grade')) for d in dicts]
    return rule_c2(bs)


def r2_flips(namefun):
    out = []
    for cid in sorted(ctl):
        dbl = bool(r3.loc[cid, 'matchA'] == True and r3.loc[cid, 'matchB'] == True) if cid in r3.index else False
        if dbl and not namefun(cid):
            out.append(cid)
    return out


# ---------- 载入四套票档 ----------
seats = {}
for run in ('run1', 'run2'):
    A = load(f'{ROOT}/annotation/ANN_A_btest_{run}.jsonl')
    B = load(f'{ROOT}/annotation/ANN_B_btest_{run}.jsonl')
    C = load(f'{ROOT}/annotation/ANN_C_btest_{run}.jsonl')
    for nm, d in (('A', A), ('B', B), (('C'), C)):
        assert len(d) == 45, f'{run} 席位 {nm} 行数 {len(d)} != 45'
    seats[run] = (A, B, C)
FA = load(f'{F21}/annotation/ANN_A_facev21.jsonl')
FB = load(f'{F21}/annotation/ANN_B_facev21.jsonl')
FC = load(f'{F21}/annotation/ANN_C_facev21.jsonl')

# ---------- 交叉验证闸门（双实现对账） ----------
gate = []
for cid in sorted(hot | ctl):
    con, mode, nv = consensus(FA, FB, FC, cid)
    r = frows[cid]
    assert (con or None) == (r['consensus'] or None) and mode == r['mode'], f'FACEV21 C4 复刻不符 {cid}'
    gate.append(cid)
tmat = pd.read_csv(f'{TIEP}/out/revote_matrix.tsv', sep='\t')
tmat21 = tmat[tmat['face'] == 'FACEV21'].set_index('cid')
for cid in sorted(hot | ctl):
    mine = c2b_consensus([FA, FB, FC], cid)
    pub = tmat21.loc[cid, 'name_C2b']
    pub = None if pd.isna(pub) else str(pub)
    assert (mine or None) == (pub or None), f'FACEV21 C2b 与 TIEP 已发布件不符 {cid}: {mine} vs {pub}'
r1_cnt = sum(1 for cid in hot if frows[cid]['consensus'] and frows[cid]['consensus'] == frows[cid]['truth'])
assert r1_cnt == fv['R1']['count'] == 19, f'FACEV21 R1 复算 {r1_cnt} != 19'
print(f'[GATE PASS] FACEV21 C4 复刻 45/45 一致；C2b 与 TIEP 发布件对账 45/45 一致；R1 锚点 19/22 复现')

# ---------- 逐簇计算（两 run × C4/C2b + A 侧参照） ----------
rows = {}
for cid in sorted(hot | ctl):
    tag, cl = cid.split('::')
    tm = truth_major(tag, cl, alpha=False)
    ta = tm[0] if tm else None
    rec = {'truth': ta,
           'r3_double_ok': bool(r3.loc[cid, 'matchA'] == True and r3.loc[cid, 'matchB'] == True) if cid in r3.index else False,
           'role': 'hotspot' if cid in hot else 'control'}
    for run in ('run1', 'run2'):
        A, B, C = seats[run]
        con, mode, nv = consensus(A, B, C, cid)
        rec[f'c4_{run}'] = con
        rec[f'mode_{run}'] = mode
        for s, d in (('a', A), ('b', B), ('c', C)):
            rec[f'{s}_{run}'] = d.get(cid, {}).get('identity')
            rec[f'{s}g_{run}'] = d.get(cid, {}).get('grade')
        rec[f'c2b_{run}'] = c2b_consensus([A, B, C], cid)
    rec['c4_A'] = frows[cid]['consensus']
    rec['c2b_A'] = tmat21.loc[cid, 'name_C2b'] if not pd.isna(tmat21.loc[cid, 'name_C2b']) else None
    rec['A_a'] = frows[cid]['a']; rec['A_b'] = frows[cid]['b']; rec['A_c'] = frows[cid]['c']
    rows[cid] = rec


def hit(name, truth):
    return bool(name) and name == truth


# ---------- §5 稳定性门 ----------
agree = [c for c in rows if (rows[c]['c4_run1'] or None) == (rows[c]['c4_run2'] or None)]
rate = len(agree) / 45
gate_pass = rate >= 0.90  # =≥41/45
mismatch = [dict(cluster_id=c, truth=rows[c]['truth'],
                 run1_name=rows[c]['c4_run1'], run1_mode=rows[c]['mode_run1'],
                 run2_name=rows[c]['c4_run2'], run2_mode=rows[c]['mode_run2'],
                 a1=rows[c]['a_run1'], b1=rows[c]['b_run1'], c1=rows[c]['c_run1'],
                 a2=rows[c]['a_run2'], b2=rows[c]['b_run2'], c2=rows[c]['c_run2']) for c in sorted(rows)
            if (rows[c]['c4_run1'] or None) != (rows[c]['c4_run2'] or None)]
seat_level = {}
for s in ('a', 'b', 'c'):
    n = sum(1 for c in rows if str(rows[c][f'{s}_run1']) == str(rows[c][f'{s}_run2']))
    seat_level[f'{s}_identity_agree'] = f'{n}/45'
c2b_agree = sum(1 for c in rows if (rows[c]['c2b_run1'] or None) == (rows[c]['c2b_run2'] or None))

# ---------- §2/§7 主判读（仅门过后执行；run1 C4） ----------
PRESERVE = ['Q4::15', 'Q5b::13']
if gate_pass:
    hot_ok = sorted([c for c in hot if hit(rows[c]['c4_run1'], rows[c]['truth'])])
    flips = [c for c in r2_flips(lambda cid: hit(rows[cid]['c4_run1'], rows[cid]['truth']))]
    pres_ok = all(hit(rows[c]['c4_run1'], rows[c]['truth']) for c in PRESERVE)
    r1, r2n = len(hot_ok), len(flips)
    if r2n > 1 or r1 < 15:
        band = 'B不达（维持A唯一形态）'
    elif r1 >= 19 and pres_ok:
        band = 'PASS（B 不劣于 A）'
    else:
        band = '部分成立'
    verdict = dict(stability_gate=dict(agree=f'{len(agree)}/45', rate=round(rate, 4), gate='>=90% (>=41/45)', passed=True),
                   R1=dict(count=r1, gate='>=19 PASS带 / 15-18 部分带', clusters=hot_ok),
                   R2=dict(count=r2n, gate='<=1', clusters=flips),
                   preservation={c: dict(truth=rows[c]['truth'], consensus=rows[c]['c4_run1'], ok=hit(rows[c]['c4_run1'], rows[c]['truth'])) for c in PRESERVE},
                   band=band)
    # run2 诊断列
    r1_diag = sum(1 for c in hot if hit(rows[c]['c4_run2'], rows[c]['truth']))
    flips_diag = r2_flips(lambda cid: hit(rows[cid]['c4_run2'], rows[cid]['truth']))
    verdict['run2_diagnostic'] = dict(R1=r1_diag, R2=len(flips_diag),
                                      preservation_ok=all(hit(rows[c]['c4_run2'], rows[c]['truth']) for c in PRESERVE),
                                      flips=flips_diag)
else:
    verdict = dict(stability_gate=dict(agree=f'{len(agree)}/45', rate=round(rate, 4), gate='>=90% (>=41/45)', passed=False),
                   band='稳定性门不过 → 不判、先治非确定性（禁 A/B 对比判读）')

# ---------- §6 C2b 并列读（run1/run2 票 + A 侧参照；零额外票，不进门禁） ----------
side = {}
for label, key in (('B_run1', 'c2b_run1'), ('B_run2', 'c2b_run2'), ('A_FACEV21', 'c2b_A')):
    n1 = sum(1 for c in hot if hit(rows[c][key], rows[c]['truth']))
    fl = [c for c in sorted(ctl) if rows[c]['r3_double_ok'] and not hit(rows[c][key], rows[c]['truth'])]
    pr = {c: dict(name=rows[c][key], ok=hit(rows[c][key], rows[c]['truth'])) for c in PRESERVE}
    named = sum(1 for c in rows if rows[c][key])
    side[label] = dict(R1=n1, R2_flips=fl, R2_count=len(fl), preservation=pr, named=f'{named}/45')
c4_ref = {}
for label, key in (('B_run1', 'c4_run1'), ('B_run2', 'c4_run2'), ('A_FACEV21', 'c4_A')):
    n1 = sum(1 for c in hot if hit(rows[c][key], rows[c]['truth']))
    fl = [c for c in sorted(ctl) if rows[c]['r3_double_ok'] and not hit(rows[c][key], rows[c]['truth'])]
    named = sum(1 for c in rows if rows[c][key])
    c4_ref[label] = dict(R1=n1, R2_count=len(fl), named=f'{named}/45')

# ---------- calllog 非空硬断言（服务端独立留痕 × 逐簇时间窗） ----------
import glob
traces = []
for f in glob.glob('/mnt/D/EyeKB/logs/mcp_trace/calls_*.jsonl'):
    for l in open(f, encoding='utf-8'):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get('tag') == 'btest_d9':
            traces.append(d)


def ts2dt(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


audit_rows = []
for run in ('run1', 'run2'):
    for stem in ('A', 'B', 'C'):
        try:
            meta = json.load(open(f'{ROOT}/annotation/ANN_{stem}_btest_{run}_META.json'))
        except FileNotFoundError:
            audit_rows.append(dict(run=run, seat=stem, cluster='(missing)', server_calls=None, ok=False))
            continue
        pid = meta.get('runner_pid')
        cost = {}
        for l in open(f'{ROOT}/logs/cost_{run}_{stem}.jsonl', encoding='utf-8'):
            r0 = json.loads(l)
            cost[r0['cid']] = r0
        for cid, rec in sorted(cost.items()):
            t0, t1 = ts2dt(rec['start_ts']), ts2dt(rec['end_ts'])
            nserver = sum(1 for d in traces if d.get('pid') == pid
                          and t0 - datetime.timedelta(seconds=5) <= ts2dt(d['ts']) <= t1 + datetime.timedelta(seconds=5))
            audit_rows.append(dict(run=run, seat=stem, cluster=cid, server_calls=nserver,
                                   runner_exec_calls=rec.get('n_exec_tools', 0),
                                   ok=bool(nserver >= 1)))

# ---------- 成本汇总（§4.4/§8） ----------
cost_sum = []
for run in ('run1', 'run2'):
    for stem in ('A', 'B', 'C'):
        try:
            recs = {}
            for l in open(f'{ROOT}/logs/cost_{run}_{stem}.jsonl', encoding='utf-8'):
                r0 = json.loads(l)
                recs[r0['cid']] = r0
        except FileNotFoundError:
            continue
        vals = list(recs.values())
        by_tool = collections.Counter()
        for v in vals:
            by_tool.update(v.get('tools') or {})
        cost_sum.append(dict(run=run, seat=stem, n_clusters=len(vals),
                             api_calls=sum(v['api_calls'] for v in vals),
                             tool_calls=sum(v['tool_calls'] for v in vals),
                             tool_calls_exec=sum(v.get('n_exec_tools', 0) for v in vals),
                             tools_by_name=json.dumps(dict(by_tool), ensure_ascii=False),
                             wall_s_total=round(sum(v['wall_s'] for v in vals), 1),
                             wall_s_mean=round(sum(v['wall_s'] for v in vals) / max(1, len(vals)), 1),
                             prompt_tokens=sum(v['prompt_tokens'] for v in vals),
                             completion_tokens=sum(v['completion_tokens'] for v in vals),
                             reminders=sum(v['reminders'] for v in vals),
                             forced_final=sum(1 for v in vals if v['forced_final'])))
a_cost = []
for stem in ('A', 'B', 'C'):
    m = json.load(open(f'{F21}/annotation/ANN_{stem}_facev21_META.json'))
    a_cost.append(dict(seat=stem, mode='A(EV_DIGEST 5簇/批)', batches=9,
                       prompt_tokens=m['usage']['prompt_tokens'], completion_tokens=m['usage']['completion_tokens']))

# ---------- 逐簇表 + 与 FACEV21/RUN4-r 对照 ----------
recs_out = []
for cid in sorted(hot | ctl):
    r = rows[cid]
    b, fr = brows.get(cid), frows[cid]
    def st(prev):
        po = bool(prev) and prev == r['truth']
        ro = hit(r['c4_run1'], r['truth'])
        return ('still_right' if po and ro else 'newly_fixed' if ro and not po
                else 'lost' if po and not ro else 'still_wrong')
    recs_out.append(dict(cluster_id=cid, role=r['role'], truth=r['truth'],
                         b_run1_a=r['a_run1'], b_run1_b=r['b_run1'], b_run1_c=r['c_run1'],
                         b_run1_mode=r['mode_run1'], b_run1_consensus=r['c4_run1'],
                         b_run2_consensus=r['c4_run2'], b_c2b_run1=r['c2b_run1'], b_c2b_run2=r['c2b_run2'],
                         a_consensus=fr['consensus'], a_c2b=r['c2b_A'],
                         r4r_consensus=b.get('consensus'), r3_double_ok=r['r3_double_ok'],
                         st_vs_facev21=st(fr['consensus']), st_vs_run4r=st(b.get('consensus')),
                         b1_why=(seats['run1'][0].get(cid, {}).get('why') or '')))
flip = pd.DataFrame(recs_out)
flip.to_csv(f'{ROOT}/out/per_cluster_table_btest.tsv', sep='\t', index=False)
pd.DataFrame(mismatch).to_csv(f'{ROOT}/out/stability_mismatches.tsv', sep='\t', index=False)
pd.DataFrame(audit_rows).to_csv(f'{ROOT}/out/calllog_audit.tsv', sep='\t', index=False)
pd.DataFrame(cost_sum).to_csv(f'{ROOT}/out/cost_summary.tsv', sep='\t', index=False)

out = dict(prereg_sha256=json.load(open(f'{ROOT}/annotation/ANN_A_btest_run1_META.json'))['prereg_sha256'],
           gates_check=dict(facev21_c4_replication='PASS', c2b_tiep_crosscheck='PASS', r1_anchor_19='PASS'),
           verdict=verdict,
           parallel_read_C2b=side, reference_C4=c4_ref,
           seat_level_stability=seat_level, c2b_stability_agree=f'{c2b_agree}/45',
           calllog_audit=dict(total_server_trace_lines=len(traces),
                              clusters_audited=len(audit_rows),
                              clusters_with_zero_server_calls=[dict(r=a['run'], s=a['seat'], c=a['cluster']) for a in audit_rows if not a['ok']]),
           cost_b_arm=cost_sum, cost_a_reference=a_cost,
           baselines=dict(RUN4r_R1p=base['R1p']['count'], FACEV21_R1=fv['R1']['count'],
                          FACEV21_R2=fv['R2']['count'], FACEV21_verdict_pass=fv['verdict_pass']),
           rows=rows)
json.dump(out, open(f'{ROOT}/scoring/BTEST_VERDICT.json', 'w'), ensure_ascii=False, indent=1, default=str)

print(f"[稳定性门] run1 vs run2 C4 共识一致 {len(agree)}/45 rate={rate:.3f} pass={gate_pass}")
print(f"[席位级] {json.dumps(seat_level)} C2b一致 {c2b_agree}/45")
if gate_pass:
    print(f"[主判读 run1 C4] R1={verdict['R1']['count']}/22 R2={verdict['R2']['count']}/23 保全={all(v['ok'] for v in verdict['preservation'].values())} → {verdict['band']}")
    print(f"[run2 诊断列] {json.dumps(verdict['run2_diagnostic'], ensure_ascii=False)}")
    print(f"[C2b 并列读] {json.dumps({k: dict(R1=v['R1'], R2=v['R2_count']) for k, v in side.items()}, ensure_ascii=False)}")
zero = out['calllog_audit']['clusters_with_zero_server_calls']
print(f"[calllog 审计] trace 行={len(traces)} 零留痕簇={len(zero)} {zero[:5]}")
print('[成本] ' + json.dumps(cost_sum, ensure_ascii=False))
print('WROTE scoring/BTEST_VERDICT.json + out/{per_cluster_table_btest,stability_mismatches,calllog_audit,cost_summary}.tsv')
