#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E1-2/3/4/5 指标计算（全部读 e1_collect_scores.py 产物，不触 LLM/服务）。
输出 out/e1_truth_region_table.tsv, out/e1_by_class_table.tsv, out/e1_no_truth_agreement.tsv,
     out/e1_divergence_cases.tsv, out/e1_sensitivity_grid.tsv, out/e1_metrics.json, logs/metrics_log.txt
口径 = E1_PREREG_v1.0.md（sha 252b0fbb…），执行端不代裁。"""
import json, csv, math
from collections import defaultdict

ROOT = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'
EV = '/mnt/D/EyeKB/plans/evalset'
RET_MEMBERS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7']

CMAP = json.load(open(f'{ROOT}/e1_class_map.json'))
M = CMAP['map']

def load_scores(path):
    per = defaultdict(list)
    for i, l in enumerate(open(path)):
        if i == 0: continue
        f = l.rstrip('\n').split('\t')
        per[f[0]].append({'canon': f[3], 'n': int(f[4]), 'genes': f[5], 'alias': f[6],
                          'lit_n': int(f[7]), 'lit_pm': f[8]})
    return per

def mapped_label(canon, panel):
    """panel: 'retina'|'ocular' -> label or None or ('AMBIG', set)"""
    e = M.get(canon)
    if not e: return None
    v = e.get(panel)
    if v is None: return None
    if v.startswith('AMBIG['):
        return ('AMBIG', set(x.strip() for x in v[6:-1].split(',')))
    return v

def rank_candidates(cands, kind):
    if kind == 1:
        return sorted(cands, key=lambda c: (-c['n'], c['canon']))
    if kind == 2:
        return sorted(cands, key=lambda c: (-c['lit_n'], c['canon']))
    mx = max(c['n'] for c in cands) or 1
    return sorted(cands, key=lambda c: (-(0.5 * c['n'] / mx + 0.5 * min(c['lit_n'], 4) / 4), -c['n'], c['canon']))

def top1_label(per, cid, panel, kind=1, ambig_lenient=False, truth=None):
    cands = per.get(cid)
    if not cands: return None
    c = rank_candidates(cands, kind)[0]
    lab = mapped_label(c['canon'], panel)
    if isinstance(lab, tuple):
        if ambig_lenient and truth and truth in lab[1]: return truth
        return None
    return lab

def top3_labels(per, cid, panel, kind=1, ambig_lenient=False, truth=None):
    cands = per.get(cid)
    if not cands: return set()
    out = set()
    for c in rank_candidates(cands, kind)[:3]:
        lab = mapped_label(c['canon'], panel)
        if isinstance(lab, tuple):
            if ambig_lenient: out |= lab[1]
            continue
        if lab: out.add(lab)
    return out

def macro_f1(pairs):
    """pairs: list[(pred_label_or_None, truth_label)] -> macro F1 over truth classes"""
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

def _f1r(pairs):
    v = macro_f1(pairs)
    return round(v, 4) if v is not None else None

def pct(h, n): return round(100.0 * h / n, 2) if n else None

def main():
    log = []
    def P(*a):
        s = ' '.join(str(x) for x in a); log.append(s); print(s, flush=True)

    ON = load_scores(f'{ROOT}/data/e1_scores_ON.tsv')
    OFF = load_scores(f'{ROOT}/data/e1_scores_OFF.tsv')
    leak = {f[0]: {'self_ref': f[6], 'mref': f[7], 'cites': f[5], 'channel': f[2]}
            for i, f in enumerate((l.rstrip('\n').split('\t') for l in open(f'{ROOT}/data/e1_leak_table.tsv'))) if i > 0}

    # ---- 行级底表
    rows3 = list(csv.DictReader(open(f'{EV}/scoring/run3_object_B_table_v1.1.tsv'), delimiter='\t'))
    r3 = {x['cluster_id']: x for x in rows3}
    flip = list(csv.DictReader(open('/mnt/D/EyeKB/plans/face_v21_20260926/out/per_cluster_flip_table_facev21.tsv'), delimiter='\t'))
    run5 = list(csv.DictReader(open(f'{EV}/scoring/run5_truth_table.tsv'), delimiter='\t'))
    r5 = {x['cluster_id']: x for x in run5}

    def ab_consensus(x):
        a, b = x['ann_A'], x['ann_B']
        if a and b and a == b and not a.startswith(('undetermined', 'coarse:')): return a
        return None
    def v21_consensus(x):
        return x['v21_consensus'] if x['v21_mode'] == 'majority' and x['v21_consensus'] and x['v21_consensus'] != 'nan' else None
    def r4r_consensus(x):
        return x['r4r_consensus'] if x.get('r4r_mode') == 'majority' and x['r4r_consensus'] and x['r4r_consensus'] != 'nan' else None
    def r5_consensus(x):
        c = x['consensus']
        return c if c and c != 'nan' else None

    # ---- 面定义（行清单）
    f_ret = [x['cluster_id'] for x in rows3 if x['truth'] and x['member'] in RET_MEMBERS]
    f_ocs = [x['cluster_id'] for x in run5]
    flip_ret = {x['cluster_id']: x for x in flip if x['truth'] and x['truth'] != 'nan' and x['cluster_id'].split('::')[0] in RET_MEMBERS}
    f3_keys = list(flip_ret) + [c for c in f_ocs]  # 三席面 = FACEV21 retina(45-核对=全部retina成员) ∪ RUN5 Q6(33, 循环注记)
    truth_of = {cid: (r3[cid]['truth'] if cid in r3 and r3[cid]['truth'] else
                      (r5[cid]['truth'] if cid in r5 else None)) for cid in set(f_ret) | set(f_ocs) | set(flip_ret)}
    for x in flip: 
        if x['cluster_id'] in flip_ret: truth_of[x['cluster_id']] = x['truth']
    P(f'faces: F-RET={len(f_ret)} F-OCS={len(f_ocs)} F-3SEAT={len(f3_keys)} (flip-retina={len(flip_ret)})')

    # ---- 泄漏分裂
    byref = defaultdict(list)
    for cid in set(f_ret) | set(f_ocs) | set(flip_ret):
        byref[leak.get(cid, {}).get('self_ref', '不可判')].append(cid)
    P('leak split all-truth-rows:', {k: len(v) for k, v in byref.items()})
    # per-member leak summary
    memb = defaultdict(lambda: defaultdict(int))
    for cid, k in leak.items():
        memb[cid.split('::')[0]][k['self_ref']] += 1
    for m_ in sorted(memb): P('  leak', m_, dict(memb[m_]))

    # ---- 指标表
    out_rows = []
    def scorer_pack(face_cids, ev_per, ambig_lenient=False):
        """returns dict of scorer -> (hits, n, pairs, cov3, f1)"""
        res = {}
        def ev(kind):
            hits = []; cov = []; pairs = []
            for cid in face_cids:
                panel = 'ocular' if cid.startswith('Q6') else 'retina'
                t = truth_of.get(cid)
                if not t: continue
                p = top1_label(ev_per, cid, panel, kind=kind, ambig_lenient=ambig_lenient, truth=t)
                hits.append(1 if p == t else 0)
                cov.append(1 if t in top3_labels(ev_per, cid, panel, kind=kind, ambig_lenient=ambig_lenient, truth=t) else 0)
                pairs.append((p, t))
            return dict(hit=sum(hits), n=len(hits), cov3=sum(cov), f1=round(macro_f1(pairs), 4) if pairs else None)
        res['ev1_ON'] = ev(1); res['ev2_ON'] = ev(2); res['ev3_ON'] = ev(3); res['ev1_OFF'] = ev(1) if ambig_lenient else None
        return res

    def baseline_ret(cids):
        rows = [r3[c] for c in cids if c in r3]
        a = sum(1 for x in rows if x['matchA'] == 'True'); b = sum(1 for x in rows if x['matchB'] == 'True')
        cons = [x for x in rows if ab_consensus(x)]; c_hit = sum(1 for x in cons if ab_consensus(x) == x['truth'])
        n = len(rows)
        pairsA = [(x['ann_A'] if x['ann_A'] and not x['ann_A'].startswith(('undetermined', 'coarse:')) else None, x['truth']) for x in rows]
        pairsB = [(x['ann_B'] if x['ann_B'] and not x['ann_B'].startswith(('undetermined', 'coarse:')) else None, x['truth']) for x in rows]
        pairsC = [(ab_consensus(x), x['truth']) for x in rows]
        return dict(A=dict(hit=a, n=n, f1=_f1r(pairsA)),
                    B=dict(hit=b, n=n, f1=_f1r(pairsB)),
                    ABcons=dict(hit=c_hit, n=n, cond_hit=c_hit, cond_n=len(cons), f1=_f1r(pairsC)))

    def baseline_3seat(cids):
        rows = [flip_ret[c] if c in flip_ret else r5[c] for c in cids]
        hit45 = 0; hit5 = 0; n = 0; pairs45 = []; pairs5 = []
        for x in rows:
            cid = x['cluster_id']
            if cid in flip_ret:
                c = v21_consensus(x); t = x['truth']
                hit45 += 1 if (c and c == t) else 0
                pairs45.append((c, t))
            else:
                c = r5_consensus(x); t = x['truth']
                hit5 += 1 if (c and c == t) else 0
                pairs5.append((c, t))
            n += 1
        allp = pairs45 + pairs5
        return dict(v21_ret=dict(hit=hit45, n=len(pairs45), f1=_f1r(pairs45)),
                    r5_ocs=dict(hit=hit5, n=len(pairs5), f1=_f1r(pairs5)),
                    union=dict(hit=hit45 + hit5, n=n, f1=_f1r(allp)))

    def r5_singles(cids):
        rows = [r5[c] for c in cids if c in r5]
        out = {}
        for s in ('A', 'B', 'C'):
            hit = sum(1 for x in rows if x[f'vote_{s}'] and x[f'vote_{s}'] != 'nan'
                      and not x[f'vote_{s}'].startswith(('undetermined', 'coarse')) and x[f'vote_{s}'] == x['truth'])
            out[f'single_{s}'] = dict(hit=hit, n=len(rows))
        return out

    # 主表: face x subset
    faces = {'F-RET': f_ret, 'F-OCS': f_ocs, 'F-3SEAT': f3_keys}
    subsets = {'全部': None, '无泄漏': '无', '有泄漏': '有', '不可判': '不可判'}
    main_tab = open(f'{ROOT}/out/e1_truth_region_table.tsv', 'w')
    main_tab.write('\t'.join(['face', 'subset', 'n', 'ev1_top1', 'ev1_top3cov', 'ev1_f1',
                              'ev2_top1', 'ev2_f1', 'ev3_top1', 'ev3_top3cov', 'ev3_f1',
                              'base_A', 'base_B', 'base_ABcons', 'base_3seat', 'notes']) + '\n')
    metrics = {}
    for fname, fcids in faces.items():
        metrics[fname] = {}
        for sname, sval in subsets.items():
            cids = [c for c in fcids if (sval is None or leak.get(c, {}).get('self_ref') == sval)]
            if not cids:
                continue
            ep = scorer_pack(cids, ON)
            base = {}
            if fname == 'F-RET':
                bl = baseline_ret(cids); base = dict(A=bl['A'], B=bl['B'], ABcons=bl['ABcons'])
            if fname in ('F-3SEAT', 'F-OCS'):
                b3 = baseline_3seat([c for c in cids if c in flip_ret or c in r5])
                base['3seat'] = b3['union']
                if fname == 'F-OCS': base.update(r5_singles(cids))
            row = [fname, sname, str(len(cids)),
                   str(pct(ep['ev1_ON']['hit'], len(cids))), str(pct(ep['ev1_ON']['cov3'], len(cids))), str(ep['ev1_ON']['f1']),
                   str(pct(ep['ev2_ON']['hit'], len(cids))), str(ep['ev2_ON']['f1']),
                   str(pct(ep['ev3_ON']['hit'], len(cids))), str(pct(ep['ev3_ON']['cov3'], len(cids))), str(ep['ev3_ON']['f1']),
                   str(pct(base.get('A', {}).get('hit'), base.get('A', {}).get('n'))),
                   str(pct(base.get('B', {}).get('hit'), base.get('B', {}).get('n'))),
                   str(pct(base.get('ABcons', {}).get('hit'), base.get('ABcons', {}).get('n'))),
                   str(pct(base.get('3seat', {}).get('hit'), base.get('3seat', {}).get('n'))),
                   'circular-Q6 sanity only' if fname == 'F-OCS' else '']
            main_tab.write('\t'.join(row) + '\n')
            metrics[fname][sname] = dict(n=len(cids), ev1=ep['ev1_ON'], ev2=ep['ev2_ON'], ev3=ep['ev3_ON'], base=base)
        P(fname, '->', {k: round(v['ev1']['hit'] / v['n'], 3) if v['n'] else None for k, v in metrics[fname].items()})
    main_tab.close()

    # ---- 判读矩阵（扣泄漏列，基线同分母）
    def tier(delta):
        if delta is None: return None
        if delta >= 5.0: return 'V1'
        if delta <= -5.0: return 'V3'
        return 'V2'
    matrix = {}
    for fname, blkey, blsub in (('F-RET', 'ABcons', '无泄漏'), ('F-3SEAT', '3seat', '无泄漏')):
        mm = metrics.get(fname, {}).get(blsub)
        if not mm or not mm['n']: continue
        bl = mm['base'].get(blkey)
        if not bl: continue
        bl_pct = 100.0 * bl['hit'] / bl['n']
        for kind in ('ev1', 'ev3'):
            ev_pct = 100.0 * mm[kind]['hit'] / mm['n']
            d = round(ev_pct - bl_pct, 2)
            matrix[f'{fname}:{kind}:{blkey}@{blsub}'] = dict(evidence=round(ev_pct, 2), baseline=round(bl_pct, 2),
                                                             delta_pp=d, tier=tier(d), n=mm['n'])
    # 副：F-3SEAT 泄漏=全部 与 F-RET vs B 单席
    mm = metrics.get('F-3SEAT', {}).get('全部')
    if mm and mm['base'].get('3seat'):
        d = round(100.0 * mm['ev1']['hit'] / mm['n'] - 100.0 * mm['base']['3seat']['hit'] / mm['base']['3seat']['n'], 2)
        matrix['F-3SEAT:ev1:3seat@全部'] = dict(delta_pp=d, tier=tier(d), n=mm['n'])
    mm = metrics.get('F-RET', {}).get('无泄漏')
    if mm and mm['base'].get('B'):
        d = round(100.0 * mm['ev1']['hit'] / mm['n'] - 100.0 * mm['base']['B']['hit'] / mm['base']['B']['n'], 2)
        matrix['F-RET:ev1:B@无泄漏'] = dict(delta_pp=d, tier=tier(d), n=mm['n'])
    # 泄漏列差（>10pp => 背答案主导条款）
    le = metrics.get('F-RET', {})
    if le.get('有泄漏') and le.get('无泄漏'):
        a = 100.0 * le['有泄漏']['ev1']['hit'] / le['有泄漏']['n']
        b = 100.0 * le['无泄漏']['ev1']['hit'] / le['无泄漏']['n']
        matrix['leak_column_gap_F-RET'] = dict(with_leak=round(a, 2), without=round(b, 2), gap_pp=round(a - b, 2))
    le3 = metrics.get('F-3SEAT', {})
    if le3.get('有泄漏') and le3.get('无泄漏'):
        a = 100.0 * le3['有泄漏']['ev1']['hit'] / le3['有泄漏']['n']
        b = 100.0 * le3['无泄漏']['ev1']['hit'] / le3['无泄漏']['n']
        matrix['leak_column_gap_F-3SEAT'] = dict(with_leak=round(a, 2), without=round(b, 2), gap_pp=round(a - b, 2))
    P('MATRIX:'); [P(' ', k, v) for k, v in matrix.items()]

    # ---- 分类目分层（F-RET 全部 & F-OCS）
    cls_tab = open(f'{ROOT}/out/e1_by_class_table.tsv', 'w')
    cls_tab.write('\t'.join(['face', 'truth_class', 'n', 'ev1_hit', 'ev3_hit', 'A_hit', 'B_hit', 'ABcons_hit', 'ev1_top1_dist']) + '\n')
    for fname, fcids, blmode in (('F-RET', f_ret, 'AB'), ('F-OCS', f_ocs, 'R5')):
        agg = defaultdict(lambda: dict(n=0, e1=0, e3=0, a=0, b=0, c=0, dist=defaultdict(int)))
        for cid in fcids:
            t = truth_of.get(cid)
            if not t: continue
            panel = 'ocular' if fname == 'F-OCS' else 'retina'
            g = agg[t]; g['n'] += 1
            if top1_label(ON, cid, panel, 1) == t: g['e1'] += 1
            if top1_label(ON, cid, panel, 3) == t: g['e3'] += 1
            p1 = top1_label(ON, cid, panel, 1)
            if p1: g['dist'][p1] += 1
            x = r3.get(cid)
            if blmode == 'AB' and x:
                g['a'] += 1 if x['matchA'] == 'True' else 0
                g['b'] += 1 if x['matchB'] == 'True' else 0
                g['c'] += 1 if ab_consensus(x) == t else 0
            if blmode == 'R5' and cid in r5:
                y = r5[cid]; g['c'] += 1 if r5_consensus(y) == t else 0
                g['a'] += 1 if y.get('vote_A') == t else 0
                g['b'] += 1 if y.get('vote_B') == t else 0
        for t, g in sorted(agg.items()):
            cls_tab.write('\t'.join([fname, t, str(g['n']), str(g['e1']), str(g['e3']), str(g['a']), str(g['b']), str(g['c']),
                                     ';'.join(f'{k}:{v}' for k, v in sorted(g['dist'].items(), key=lambda kv: -kv[1]))]) + '\n')
    cls_tab.close()

    # ---- E1-4 无真值区
    nt = [x for x in rows3 if not x['truth']]
    agree_n = 0; agree_h = 0
    nt_tab = open(f'{ROOT}/out/e1_no_truth_agreement.tsv', 'w')
    nt_tab.write('\t'.join(['cluster_id', 'member', 'n_cells', 'ev1_top1_canon', 'ev1_mapped', 'panel_consensus', 'agree']) + '\n')
    for x in nt:
        cid = x['cluster_id']
        cands = ON.get(cid) or []
        t1 = rank_candidates(cands, 1)[0]['canon'] if cands else None
        panel = 'ocular' if cid.startswith('Q6') else 'retina'
        lab = mapped_label(t1, panel) if t1 else None
        lab = lab if isinstance(lab, str) else None
        cons = ab_consensus(x)
        if cons and lab:
            agree_n += 1; agree_h += 1 if lab == cons else 0
        nt_tab.write('\t'.join([cid, x['member'], x['n_cells'], t1 or '', lab or '', cons or '',
                                ('Y' if lab == cons else 'N') if (cons and lab) else 'na']) + '\n')
    nt_tab.close()
    P(f'E1-4 no-truth: rows={len(nt)} both-defined={agree_n} agree={agree_h}')

    # ---- E1-5 分歧案例
    div = []
    for cid in list(dict.fromkeys(f_ret + f_ocs)):
        t = truth_of.get(cid)
        if not t: continue
        panel = 'ocular' if cid.startswith('Q6') else 'retina'
        cands = ON.get(cid)
        if not cands: continue
        c = rank_candidates(cands, 1)[0]
        lab = mapped_label(c['canon'], panel)
        if isinstance(lab, tuple) or not lab: continue
        cons = v21_consensus(flip_ret[cid]) if cid in flip_ret else (r5_consensus(r5[cid]) if cid in r5 else (ab_consensus(r3.get(cid, {})) if cid in r3 else None))
        if cons and cons != lab:
            nshared_cons = next((q['n'] for q in cands if q['canon'] == cons), None)
            div.append(dict(cid=cid, truth=t, ev=c['canon'], n=c['n'], cons=cons,
                            dn=(c['n'] - (nshared_cons or 0)), n_cons=nshared_cons))
    div.sort(key=lambda d: (-abs(d['dn']), -d['n'], d['cid']))
    must = [d for d in div if d['cid'] == 'Q2::22']
    picked = ([must[0]] if must else []) + [d for d in div if d['cid'] != 'Q2::22'][:5 - (1 if must else 0)]
    dg = open(f'{ROOT}/out/e1_divergence_cases.tsv', 'w')
    dg.write('\t'.join(['cluster_id', 'truth', 'ev_top1', 'n_shared', 'consensus', 'cons_n_shared', 'delta_n', 'q2_22_mandatory', 'top_genes', 'lit']) + '\n')
    dig = {json.loads(l)['cluster_id']: json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl')}
    for d in picked:
        g = dig.get(d['cid'], {})
        genes = ','.join([s or x for s, x in zip(g.get('top_genes_sym', [])[:10], g.get('top_genes', [])[:10])])
        litj = json.dumps(g.get('lit', {}), ensure_ascii=False)[:300]
        dg.write('\t'.join([d['cid'], d['truth'], d['ev'], str(d['n']), d['cons'], str(d['n_cons']),
                            str(d['dn']), 'Y' if d['cid'] == 'Q2::22' else '', genes, litj]) + '\n')
    dg.close()
    P('E1-5 divergence candidates:', len(div), 'Q2::22 in div:', bool(must))

    # ---- 敏感性网格（不进结论）
    grid = open(f'{ROOT}/out/e1_sensitivity_grid.tsv', 'w')
    grid.write('\t'.join(['axis', 'setting', 'face', 'n', 'top1_pct', 'top3cov_pct', 'macro_f1']) + '\n')
    def wrow(axis, setting, cids, per, kind='w', w=0.5, lenient=False):
        hits = []; cov = []; pairs = []
        for cid in cids:
            t = truth_of.get(cid)
            if not t: continue
            panel = 'ocular' if cid.startswith('Q6') else 'retina'
            if kind == 'w':
                cands = per.get(cid)
                if not cands: p = None
                else:
                    mx = max(c['n'] for c in cands) or 1
                    o = sorted(cands, key=lambda c: (-(w * c['n'] / mx + (1 - w) * min(c['lit_n'], 4) / 4), -c['n'], c['canon']))
                    p = mapped_label(o[0]['canon'], panel); p = p if isinstance(p, str) else (t if (lenient and isinstance(p, tuple) and p[1] and t in p[1]) else None)
            elif kind == 'off1':
                p = top1_label(per, cid, panel, 1, lenient, t)
            else:
                p = top1_label(per, cid, panel, kind, lenient, t)
            hits.append(1 if p == t else 0)
            cov.append(1 if t in top3_labels(per, cid, panel, 1 if kind == 'off1' else kind, lenient, t) else 0)
            pairs.append((p, t))
        grid.write('\t'.join([axis, setting, str(len(pairs)), str(pct(sum(hits), len(pairs))), str(pct(sum(cov), len(pairs))),
                              str(round(macro_f1(pairs), 4) if pairs else '')]) + '\n')
    for fname, fcids in (('F-RET', f_ret), ('F-3SEAT', f3_keys)):
        cids_nl = [c for c in fcids if leak.get(c, {}).get('self_ref') == '无']
        for wi in range(11):
            wrow('weight_w', f'w={wi/10:.1f}', cids_nl, ON, kind='w', w=wi / 10)
        wrow('state', 'OFF-①', cids_nl, OFF, kind='off1')
        wrow('ambig', 'lenient-①', cids_nl, ON, kind=1, lenient=True)
        wrow('ambig', 'lenient-③', cids_nl, ON, kind=3, lenient=True)
        wrow('lit_granularity', 'presence-proxy-note=count-only-built', cids_nl, ON, kind=2)
    # marker 通道强自参照成员剔除重算（Q5b 剔出 F-RET；Q6 即 F-OCS 全剔）
    f_ret_m = [c for c in f_ret if not c.startswith('Q5b') and leak.get(c, {}).get('self_ref') == '无']
    wrow('marker_channel', 'F-RET minus Q5b ①', f_ret_m, ON, kind=1)
    wrow('marker_channel', 'F-RET minus Q5b ③', f_ret_m, ON, kind=3)
    grid.close()

    json.dump(dict(metrics=metrics, matrix=matrix,
                   faces=dict(F_RET=len(f_ret), F_OCS=len(f_ocs), F_3SEAT=len(f3_keys)),
                   leak_rows={k: len(v) for k, v in byref.items()}),
              open(f'{ROOT}/out/e1_metrics.json', 'w'), ensure_ascii=False, indent=1)
    import datetime
    open(f'{ROOT}/logs/metrics_log.txt', 'w').write('\n'.join(log) + f'\nran {datetime.datetime.now()}\n')
    print('E1_METRICS_DONE')

if __name__ == '__main__':
    main()
