#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2-2/3/4/5 指标：干净效果量（两口径并列）、W 矩阵机械绑定、旗标 ROC、水分账、敏感性 S1-S6。
口径 = E2_PREREG_v1.0.md（sha 6ade3ca2）。先过 E1 锚点复现断言，不过则 exit 2 禁出结论。"""
import json, csv, os, sys, datetime
from collections import defaultdict

ROOT = '/mnt/D/EyeKB/plans/e2_decontam_20260926'
EV = '/mnt/D/EyeKB/plans/evalset'
R1 = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'
RET_MEMBERS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7']
M = json.load(open(f'{R1}/e1_class_map.json'))['map']

def load_scores(path):
    per = defaultdict(list)
    for i, l in enumerate(open(path)):
        if i == 0:
            continue
        f = l.rstrip('\n').split('\t')
        per[f[0]].append({'canon': f[3], 'n': int(f[4]), 'genes': f[5], 'alias': f[6],
                          'lit_n': int(f[7]), 'lit_pm': f[8], 'lit_n_raw': int(f[9])})
    return per

def mapped_label(canon, panel):
    e = M.get(canon)
    if not e:
        return None
    v = e.get(panel)
    if v is None:
        return None
    if v.startswith('AMBIG['):
        return ('AMBIG', set(x.strip() for x in v[6:-1].split(',')))
    return v

def rank(cands, kind):
    if not cands:
        return []
    if kind == 1:
        return sorted(cands, key=lambda c: (-c['n'], c['canon']))
    if kind == 2:
        return sorted(cands, key=lambda c: (-c['lit_n'], c['canon']))
    mx = max(c['n'] for c in cands) or 1
    return sorted(cands, key=lambda c: (-(0.5 * c['n'] / mx + 0.5 * min(c['lit_n'], 4) / 4), -c['n'], c['canon']))

def top1(per, cid, panel, kind=1):
    cands = per.get(cid)
    if not cands:
        return None, None
    c = rank(cands, kind)[0]
    lab = mapped_label(c['canon'], panel)
    return (lab if isinstance(lab, str) else None), c

def top3set(per, cid, panel, kind=1):
    out = set()
    for c in rank(per.get(cid) or [], kind)[:3]:
        lab = mapped_label(c['canon'], panel)
        if isinstance(lab, str):
            out.add(lab)
    return out

def macro_f1(pairs):
    classes = sorted({t for _, t in pairs if t})
    f1s = []
    for c in classes:
        tp = sum(1 for p, t in pairs if p == c and t == c)
        fp = sum(1 for p, t in pairs if p == c and t != c)
        fn = sum(1 for p, t in pairs if p != c and t == c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return sum(f1s) / len(f1s) if f1s else None

def pct(h, n):
    return round(100.0 * h / n, 2) if n else None

def panel_of(cid):
    return 'ocular' if cid.startswith('Q6') else 'retina'

def main():
    log = []
    def P(*a):
        s = ' '.join(str(x) for x in a); log.append(s); print(s, flush=True)

    per = {v: load_scores(f'{ROOT}/data/e2_scores_{"raw_replica" if v=="raw" else v}.tsv')
           for v in ('raw', 'S1', 'S2', 'S4', 'S5', 'S6')}
    leak = {f[0]: f[6] for i, f in enumerate((l.rstrip('\n').split('\t') for l in open(f'{R1}/data/e1_leak_table.tsv'))) if i > 0}
    rows3 = list(csv.DictReader(open(f'{EV}/scoring/run3_object_B_table_v1.1.tsv'), delimiter='\t'))
    r3 = {x['cluster_id']: x for x in rows3}
    flip = list(csv.DictReader(open('/mnt/D/EyeKB/plans/face_v21_20260926/out/per_cluster_flip_table_facev21.tsv'), delimiter='\t'))
    run5 = list(csv.DictReader(open(f'{EV}/scoring/run5_truth_table.tsv'), delimiter='\t'))
    r5 = {x['cluster_id']: x for x in run5}

    def ab_consensus(x):
        a, b = x['ann_A'], x['ann_B']
        if a and b and a == b and not a.startswith(('undetermined', 'coarse:')):
            return a
        return None
    def v21_consensus(x):
        return x['v21_consensus'] if x['v21_mode'] == 'majority' and x['v21_consensus'] and x['v21_consensus'] != 'nan' else None
    def r5_consensus(x):
        c = x['consensus']
        return c if c and c != 'nan' else None

    f_ret = [x['cluster_id'] for x in rows3 if x['truth'] and x['member'] in RET_MEMBERS]
    f_ocs = [x['cluster_id'] for x in run5]
    flip_ret = {x['cluster_id']: x for x in flip if x['truth'] and x['truth'] != 'nan'
                and x['cluster_id'].split('::')[0] in RET_MEMBERS}
    f3 = list(flip_ret) + list(f_ocs)
    truth_of = {}
    for cid in set(f_ret) | set(f_ocs) | set(flip_ret):
        truth_of[cid] = (r3[cid]['truth'] if cid in r3 and r3[cid]['truth']
                         else (r5[cid]['truth'] if cid in r5 and r5[cid]['truth'] else None))
    for x in flip:
        if x['cluster_id'] in flip_ret:
            truth_of[x['cluster_id']] = x['truth']
    P(f'faces F-RET={len(f_ret)} F-OCS={len(f_ocs)} F-3SEAT={len(f3)}')

    def cons_of(cid, face=None):
        """F-RET 严格用 AB 两席共识（预注册 §3 主替换基线）；F-3SEAT/F-OCS 用三席存档。"""
        if face == 'F-RET':
            return ab_consensus(r3[cid]) if cid in r3 else None
        if cid in flip_ret:
            return v21_consensus(flip_ret[cid])
        if cid in r5:
            return r5_consensus(r5[cid])
        if cid in r3:
            return ab_consensus(r3[cid])
        return None

    # ---- 证据打分器
    def ev_pack(cids, v, kind):
        hit = cov = 0; pairs = []; nolab = 0
        for cid in cids:
            t = truth_of.get(cid)
            if not t:
                continue
            lab, c = top1(per[v], cid, panel_of(cid), kind)
            hit += 1 if lab == t else 0
            cov += 1 if t in top3set(per[v], cid, panel_of(cid), kind) else 0
            if lab is None:
                nolab += 1
            pairs.append((lab, t))
        return dict(hit=hit, n=len(pairs), cov3=cov, nolab=nolab,
                    f1=round(macro_f1(pairs), 4) if pairs else None)

    def ev_cond(cids, v, kind, bl):
        """(deprecated; kept for row-compare reuse) c2 口径辅助。"""
        sub = [c for c in cids if truth_of.get(c) and cons_of(c, 'F-3SEAT')]
        e = ev_pack(sub, v, kind)
        bh = sum(1 for c in sub if cons_of(c, 'F-3SEAT') == truth_of[c])
        return e, dict(hit=bh, n=len(sub))

    def base_ret(cids):
        rows = [r3[c] for c in cids if c in r3]
        a = sum(1 for x in rows if x['matchA'] == 'True')
        b = sum(1 for x in rows if x['matchB'] == 'True')
        ch = sum(1 for x in rows if ab_consensus(x) and ab_consensus(x) == x['truth'])
        return dict(A=dict(hit=a, n=len(rows)), B=dict(hit=b, n=len(rows)),
                    ABcons=dict(hit=ch, n=len(rows)))

    def base3(cids):
        hit = 0; n = 0
        for cid in cids:
            cs = cons_of(cid)
            t = truth_of.get(cid)
            if t is None:
                continue
            n += 1
            if cs and cs == t:
                hit += 1
        return dict(cons3=dict(hit=hit, n=n))

    def seat_rows_hit(cids, key):
        hit = 0
        for cid in cids:
            if cid in r5:
                pass
        return hit

    # ---- E1 锚点复现（raw 列）
    anchors = {}
    nl155 = [c for c in f_ret if leak.get(c) == '无']
    p_all1 = ev_pack(f_ret, 'raw', 1); p_all3 = ev_pack(f_ret, 'raw', 3)
    p_nl1 = ev_pack(nl155, 'raw', 1); p_nl3 = ev_pack(nl155, 'raw', 3)
    brn = base_ret(nl155)
    anchors['FRET_all_ev1'] = pct(p_all1['hit'], len(f_ret))
    anchors['FRET_noleak_ev1'] = pct(p_nl1['hit'], len(nl155))
    anchors['FRET_noleak_ev3'] = pct(p_nl3['hit'], len(nl155))
    anchors['d_vs_AB_noleak'] = round(100.0 * p_nl1['hit'] / p_nl1['n'] - 100.0 * brn['ABcons']['hit'] / brn['ABcons']['n'], 2)
    anchors['d_vs_B_noleak'] = round(100.0 * p_nl1['hit'] / p_nl1['n'] - 100.0 * brn['B']['hit'] / brn['B']['n'], 2)
    p3all = ev_pack(f3, 'raw', 1)
    b3all = base3(f3)
    anchors['F3_all_ev1'] = pct(p3all['hit'], len(f3))
    anchors['F3_all_cons3'] = pct(b3all['cons3']['hit'], b3all['cons3']['n'])
    P('anchors:', json.dumps(anchors))
    want = dict(FRET_all_ev1=72.45, FRET_noleak_ev1=67.74, FRET_noleak_ev3=68.39,
                d_vs_AB_noleak=16.77, d_vs_B_noleak=3.23, F3_all_ev1=60.26, F3_all_cons3=80.77)
    # Δ 类锚点容差 0.01（E1 以未舍入 pct 相减再舍入，两位小数直减有半分钱差）
    fail = {k: (v, want[k]) for k, v in anchors.items()
            if abs(v - want[k]) > (0.011 if k.startswith('d_') else 0.005)}
    if fail:
        P('ANCHOR FAIL:', fail)
        open(f'{ROOT}/logs/metrics_log.txt', 'w').write('\n'.join(log))
        sys.exit(2)
    P('ANCHOR PASS: raw 列全部复现 E1 冻结值')

    # ---- 主表：面 x 子集 x 两口径 x raw/S1 x ①/③
    tab = open(f'{ROOT}/out/e2_truth_region_table_decon.tsv', 'w')
    tab.write('\t'.join(['face', 'subset', 'caliber', 'n', 'ev1_raw', 'ev3_raw', 'ev1_S1', 'ev3_S1',
                         'base_A', 'base_B', 'base_ABcons_or_3seat', 'S1_nolabel', 'notes']) + '\n')
    out_m = {}
    def face_metrics(fname, fcids):
        res = {}
        for sname, sub in (('全部', None), ('无泄漏', '无')):
            cids = [c for c in fcids if sub is None or leak.get(c) == sub]
            c1 = dict(n=len(cids))
            for v in ('raw', 'S1'):
                for kind, kn in ((1, 'ev1'), (3, 'ev3')):
                    e = ev_pack(cids, v, kind)
                    c1[f'{v}_{kn}'] = pct(e['hit'], e['n'])
                    c1[f'{v}_{kn}_abs'] = dict(hit=e['hit'], n=e['n'])
                    c1[f'{v}_{kn}_f1'] = e['f1']
                    c1[f'{v}_{kn}_cov3'] = pct(e['cov3'], e['n'])
                    if v == 'S1' and kind == 1:
                        c1['S1_nolabel'] = e['nolab']
            if fname == 'F-RET':
                bl = base_ret(cids)
                c1['A'] = pct(bl['A']['hit'], bl['A']['n'])
                c1['B'] = pct(bl['B']['hit'], bl['B']['n'])
                c1['B_abs'] = bl['B']
                c1['ABcons'] = pct(bl['ABcons']['hit'], bl['ABcons']['n'])
                c1['ABcons_abs'] = bl['ABcons']
            else:
                b3 = base3(cids)
                c1['cons'] = pct(b3['cons3']['hit'], b3['cons3']['n'])
                c1['cons_abs'] = b3['cons3']
            res[sname] = {'c1': c1}
            # c2: 基线已定义子集（F-RET 严格 AB；其余三席多数）
            subd = [c for c in cids if truth_of.get(c) and cons_of(c, fname)]
            e1r = ev_pack(subd, 'raw', 1); e1s = ev_pack(subd, 'S1', 1)
            e3s = ev_pack(subd, 'S1', 3)
            bh = sum(1 for c in subd if cons_of(c, fname) == truth_of[c])
            res[sname]['c2'] = dict(n=len(subd), ev1_raw=pct(e1r['hit'], len(subd)),
                                    ev1_S1=pct(e1s['hit'], len(subd)), ev3_S1=pct(e3s['hit'], len(subd)),
                                    base=pct(bh, len(subd)), base_abs=dict(hit=bh, n=len(subd)),
                                    S1_nolabel=e1s['nolab'])
            tab.write('\t'.join([fname, sname, 'c1', str(c1['n'])] +
                                [str(c1.get(f'{v}_{k}', '')) for v in ('raw', 'S1') for k in ('ev1', 'ev3')] +
                                [str(c1.get('A', c1.get('cons', ''))), str(c1.get('B', '')),
                                 str(c1.get('ABcons', c1.get('cons', ''))), str(c1.get('S1_nolabel', '')),
                                 'circular-Q6 sanity only' if fname == 'F-OCS' else '']) + '\n')
            c2 = res[sname]['c2']
            tab.write('\t'.join([fname, sname, 'c2', str(c2['n']), str(c2['ev1_raw']), '', str(c2['ev1_S1']),
                                 str(c2['ev3_S1']), '', '', str(c2['base']), str(c2['S1_nolabel']), '']) + '\n')
        return res
    out_m['F-RET'] = face_metrics('F-RET', f_ret)
    out_m['F-3SEAT'] = face_metrics('F-3SEAT', f3)
    out_m['F-OCS'] = face_metrics('F-OCS', f_ocs)
    tab.close()

    def flag_roc(cids, mode, face):
        rows = []
        subs = [c for c in cids if truth_of.get(c) and cons_of(c, face)]
        n_undef = sum(1 for c in cids if truth_of.get(c) and not cons_of(c, face))
        for theta in (0, 1, 2, 3, 4):
            tp = fp = fn = tn = 0
            for cid in subs:
                t = truth_of[cid]
                cs = cons_of(cid, face)
                lab, topc = top1(per['S1'], cid, panel_of(cid), 1)
                cons_wrong = (cs != t)
                flagged = False
                if lab is not None and lab != cs:
                    nc = 0
                    for cd in per['S1'].get(cid) or []:
                        ml = mapped_label(cd['canon'], panel_of(cid))
                        if ml == cs:
                            nc = max(nc, cd['n'])
                    flagged = (topc['n'] - nc) >= theta
                if cons_wrong and flagged:
                    tp += 1
                elif cons_wrong:
                    fn += 1
                elif flagged:
                    fp += 1
                else:
                    tn += 1
            sens = pct(tp, tp + fn); spec = pct(tn, tn + fp); prec = pct(tp, tp + fp)
            rows.append(dict(mode=mode, theta=theta, rows=len(subs), undef_rows=n_undef,
                             cons_err=tp + fn, tp=tp, fp=fp, fn=fn, tn=tn,
                             sens=sens, spec=spec, prec=prec,
                             flag_rate=pct(tp + fp, len(subs))))
        return rows

    # ---- W 矩阵机械绑定（预注册 §5：主读 = ev_S1①@F-RET全部@c1 vs ABcons；③并报；否决列 vs 最强单席 B）
    fr = out_m['F-RET']['全部']['c1']
    d1 = round(fr['S1_ev1'] - fr['ABcons'], 2)
    d3 = round(fr['S1_ev3'] - fr['ABcons'], 2)
    d1B = round(fr['S1_ev1'] - fr['B'], 2)
    def wtier(delta):
        if delta > 5.0:
            return 'W1线'
        if delta > 0.0:
            return 'W2线'
        return 'W3线'
    op = flag_roc(f_ret, 'AB', 'F-RET')
    ops2 = flag_roc(f3, '3S', 'F-3SEAT')
    usable = any(o['spec'] >= 80.0 and o['sens'] >= 30.0 for o in op)
    tiers = {wtier(d1), wtier(d3)}
    cross = len(tiers) > 1
    if d1 <= 0 and d3 <= 0:
        w_raw = 'W3'
    elif cross:
        w_raw = '边界案(跨档)'
    elif 'W1线' in tiers:
        w_raw = 'W1候选' if usable else 'W2(无可用工作点)'
        if w_raw == 'W1候选' and d1B < 5.0:
            w_raw = 'W2(否决条款:vs B<+5pp)'
    else:
        w_raw = 'W2'
    w_final = {'W1候选': 'W1'}  # 只有机械全过才 W1
    W = w_raw if w_raw not in w_final else w_final[w_raw]
    gate = dict(delta_primary_ev1=d1, delta_ev3=d3, delta_vs_B=d1B,
                usable_operating_point=usable, tier_1=wtier(d1), tier_3=wtier(d3),
                cross_tier=cross, verdict_line=W,
                note='①③分档不同=跨档边界案交PI(E1先例); W1需可用工作点+否决条款')
    P('GATE:', json.dumps(gate, ensure_ascii=False))

    rop = open(f'{ROOT}/out/e2_flag_operating_points.tsv', 'w')
    rop.write('\t'.join(['mode', 'theta', 'rows', 'undef_cons_rows', 'cons_err', 'tp', 'fp', 'fn', 'tn',
                         'sens_pct', 'spec_pct', 'prec_pct', 'flag_rate_pct']) + '\n')
    for r in op + ops2:
        rop.write('\t'.join(str(r[k]) for k in ['mode', 'theta', 'rows', 'undef_rows', 'cons_err', 'tp',
                                                'fp', 'fn', 'tn', 'sens', 'spec', 'prec', 'flag_rate']) + '\n')
    rop.close()

    # ---- 逐行对照表
    rc = open(f'{ROOT}/out/e2_row_compare.tsv', 'w')
    rc.write('\t'.join(['cluster_id', 'member', 'truth', 'leak', 'axis_member',
                        'ev1_raw_top1', 'ev1_raw_hit', 'ev1_S1_top1', 'ev1_S1_hit', 'n_raw', 'n_S1',
                        'ev3_raw_hit', 'ev3_S1_hit', 'lit_raw', 'lit_S1', 'A_hit', 'B_hit', 'cons_label',
                        'cons_hit']) + '\n')
    allc = [x['cluster_id'] for x in rows3] + [x['cluster_id'] for x in run5 if x['cluster_id'] not in {y['cluster_id'] for y in rows3}]
    axis_m = {'Q3', 'Q4', 'Q5b', 'Q6'}
    for cid in allc:
        mem = cid.split('::')[0]
        t = truth_of.get(cid)
        def one(v, kind):
            lab, c = top1(per[v], cid, panel_of(cid), kind)
            return lab, (c['n'] if c else 0)
        lr, nr = one('raw', 1); ls, ns = one('S1', 1)
        l3r, _ = one('raw', 3); l3s, _ = one('S1', 3)
        cn = cons_of(cid)
        x3 = r3.get(cid, {})
        rc.write('\t'.join([cid, mem, t or '', leak.get(cid, ''), 'Y' if mem in axis_m else '',
                            lr or '', ('1' if t and lr == t else ('' if not t else '0')),
                            ls or '', ('1' if t and ls == t else ('' if not t else '0')),
                            str(nr), str(ns),
                            ('1' if t and l3r == t else ('' if not t else '0')),
                            ('1' if t and l3s == t else ('' if not t else '0')),
                            str(sum(cd['lit_n_raw'] for cd in per['raw'].get(cid) or [])),
                            str(sum(cd['lit_n'] for cd in per['S1'].get(cid) or [])),
                            ('1' if x3.get('matchA') == 'True' else ('0' if x3 and t else '')),
                            ('1' if x3.get('matchB') == 'True' else ('0' if x3 and t else '')),
                            cn or '', ('1' if t and cn == t else ('' if not t else '0'))]) + '\n')
    rc.close()

    # ---- 水分账 A（簇侧）+ 宇宙塌缩统计
    wa = open(f'{ROOT}/out/e2_homology_water.tsv', 'w')
    wa.write('\t'.join(['member/rows', 'n_truth', 'ev1_raw_pct', 'ev1_S1_pct', 'water_pp',
                        'median_cands_raw', 'median_cands_S1']) + '\n')
    import statistics as stx
    def med(v, cids):
        xs = [len([cd for cd in per[v].get(c) or [] if cd['n'] > 0]) for c in cids]
        return stx.median(xs) if xs else None
    for mem in ('Q3', 'Q4', 'Q5b', 'Q6'):
        cids = [c for c in set(f_ret + f3) if c.startswith(mem + '::') and truth_of.get(c)]
        e0 = ev_pack(cids, 'raw', 1); e1x = ev_pack(cids, 'S1', 1)
        a = pct(e0['hit'], e0['n']); b = pct(e1x['hit'], e1x['n'])
        wa.write('\t'.join([mem, str(e0['n']), str(a), str(b), str(round(a - b, 2)),
                            str(med('raw', cids)), str(med('S1', cids))]) + '\n')
    lk13 = [c for c in set(f_ret + f3) if truth_of.get(c) and leak.get(c) == '有']
    e0 = ev_pack(lk13, 'raw', 1); e1x = ev_pack(lk13, 'S1', 1)
    a = pct(e0['hit'], e0['n']); b = pct(e1x['hit'], e1x['n'])
    wa.write('\t'.join(['lit有泄漏13行', str(e0['n']), str(a), str(b), str(round(a - b, 2)), '', '']) + '\n')
    fr196 = ev_pack(f_ret, 'S1', 1)
    wa.write('\t'.join(['面板候选宇宙(F-RET@196)', '', str(stx.median([len([cd for cd in per['raw'].get(c) or [] if cd['n'] > 0]) for c in f_ret])),
                        str(stx.median([len([cd for cd in per['S1'].get(c) or [] if cd['n'] > 0]) for c in f_ret])),
                        '', '', '']) + '\n')
    wa.close()

    # ---- 面板侧水分 B：行级三层表（build_matrix 产物）+ 汇总
    pw = open(f'{ROOT}/out/e2_panel_water.tsv', 'w')
    pw.write('# from data/e2_matrix_rows_summary.tsv; axis 成员见 e2_decon_rules.json\n')
    pw.write(open(f'{ROOT}/data/e2_matrix_rows_summary.tsv').read())
    pw.close()

    # ---- 历史登记 C
    hist = open(f'{ROOT}/out/e2_history_register.tsv', 'w')
    hist.write('\t'.join(['E1 冻结件数字', '值', '本卡修正/解读', '']) + '\n')
    nl = nl155
    e0 = ev_pack(nl, 'raw', 1); e1x = ev_pack(nl, 'S1', 1)
    e0b = ev_pack(nl, 'raw', 3); e1b = ev_pack(nl, 'S1', 3)
    hist.write('\t'.join(['E1_VERDICT §1 F-RET 无泄漏① 67.74%', '67.74', str(round(100*e1x['hit']/e1x['n'], 2)), 'S1 干净列']) + '\n')
    hist.write('\t'.join(['E1_VERDICT §1 F-RET 无泄漏③ 68.39%', '68.39', str(round(100*e1b['hit']/e1b['n'], 2)), 'S1 干净列']) + '\n')
    hist.write('\t'.join(['E1 F-A Q5b 无泄漏列命中 93.0% (43行)', '93.0', '', '被面板同源垫高']) + '\n')
    hist.write('\t'.join(['E1 矩阵 Δ(无泄漏① vs ABcons) +16.77pp', '+16.77', str(d1) + '(全196干净列主读)', '见 W 绑定']) + '\n')
    hist.write('注：本表只登记不改历史冻结件；供 RUN 系列口径修订输入\n')
    hist.close()

    # ---- 敏感性 S2-S6 网格（F-RET 主面两子集 + F-3SEAT）
    sg = open(f'{ROOT}/out/e2_sensitivity_grid.tsv', 'w')
    sg.write('\t'.join(['variant', 'face', 'subset', 'n', 'ev1_top1', 'ev3_top1', 'note']) + '\n')
    for v in ('S1', 'S2', 'S4', 'S5', 'S6', 'raw'):
        for fname, fcids in (('F-RET', f_ret), ('F-3SEAT', f3)):
            for sname, sub in (('全部', None), ('无泄漏', '无')):
                cids = [c for c in fcids if sub is None or leak.get(c) == sub]
                e1x = ev_pack(cids, v, 1); e3x = ev_pack(cids, v, 3)
                sg.write('\t'.join([v, fname, sname, str(e1x['n']), str(pct(e1x['hit'], e1x['n'])),
                                    str(pct(e3x['hit'], e3x['n'])),
                                    'nolab=' + str(e1x['nolab'])]) + '\n')
    # S3 = E1 点名单行剔除复算（raw 分）
    f_ret_m = [c for c in f_ret if not c.startswith('Q5b') and leak.get(c) == '无']
    e3x = ev_pack(f_ret_m, 'raw', 1)
    brm = base_ret(f_ret_m)
    sg.write('\t'.join(['S3_rowdrop_Q5b', 'F-RET', '无泄漏', str(e3x['n']), str(pct(e3x['hit'], e3x['n'])),
                        '', 'E1 锚 58.04; ABcons=' + str(pct(brm['ABcons']['hit'], brm['ABcons']['n']))
                        + '; B=' + str(pct(brm['B']['hit'], brm['B']['n']))]) + '\n')
    sg.close()

    # ---- 分类目分层（F-RET，raw vs S1）
    cls = open(f'{ROOT}/out/e2_by_class_decon.tsv', 'w')
    cls.write('\t'.join(['face', 'truth_class', 'n', 'raw1_hit', 'S1_hit', 'S5_hit', 'S1_nolab']) + '\n')
    for fname, fcids in (('F-RET', f_ret), ('F-3SEAT', f3)):
        ag = defaultdict(lambda: dict(n=0, r=0, s=0, l=0, nl=0))
        for cid in fcids:
            t = truth_of.get(cid)
            if not t:
                continue
            g = ag[t]; g['n'] += 1
            lr, _ = top1(per['raw'], cid, panel_of(cid), 1)
            ls, _ = top1(per['S1'], cid, panel_of(cid), 1)
            l3, _ = top1(per['S5'], cid, panel_of(cid), 1)
            g['r'] += 1 if lr == t else 0
            g['s'] += 1 if ls == t else 0
            g['l'] += 1 if l3 == t else 0
            g['nl'] += 1 if lr is None and ls is None else 0
        for t, g in sorted(ag.items()):
            cls.write('\t'.join([fname, t, str(g['n']), str(g['r']), str(g['s']), str(g['l']), str(g['nl'])]) + '\n')
    cls.close()

    # ---- 观察性附加（非判读门，事后描述，E1 F-B 同型）：弃权覆盖
    # F-RET 上 AB 共识未定义（=判读弃权/无共识）的行，去同源证据能给出具名标签/且给对的数量
    obs = {}
    for fname, fcids, fmode in (('F-RET', f_ret, 'F-RET'), ('F-3SEAT', f3, 'F-3SEAT')):
        und = [c for c in fcids if truth_of.get(c) and not cons_of(c, fname)]
        labd = hit = 0
        for cid in und:
            lab, _ = top1(per['S1'], cid, panel_of(cid), 1)
            if lab:
                labd += 1
                if lab == truth_of[cid]:
                    hit += 1
        obs[fname + '_cons_undef_rows'] = len(und)
        obs[fname + '_S1_labels_given'] = labd
        obs[fname + '_S1_labels_correct'] = hit
        cov = ev_pack(fcids, 'S1', 1)
        obs[fname + '_S1_cov3'] = pct(cov['cov3'], cov['n'])
        obs[fname + '_S1_f1'] = cov['f1']
    P('OBS(附加):', json.dumps(obs))

    json.dump(dict(anchors=anchors, metrics=out_m, gate=gate,
                   observation_addendum=obs,
                   flag_roc=dict(F_RET=op, F_3SEAT=ops2),
                   faces=dict(F_RET=len(f_ret), F_3SEAT=len(f3), F_OCS=len(f_ocs))),
              open(f'{ROOT}/out/e2_metrics.json', 'w'), ensure_ascii=False, indent=1)
    open(f'{ROOT}/logs/metrics_log.txt', 'w').write('\n'.join(log) + f'\nran {datetime.datetime.now()}\n')
    print('E2_METRICS_DONE')

if __name__ == '__main__':
    main()
