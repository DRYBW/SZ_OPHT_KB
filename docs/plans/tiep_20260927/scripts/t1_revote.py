#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TIEP-t1: 平票/弃权反事实重投票（全机械，零LLM，零网络）。

五面票档: RUN3(2席) / RUN4-r(3席) / RUN5(3席) / FACEV21(3席) / KB9(3席有效合并票)。
规则:
  C4  = 现行三票多数制基线(票=定名&grade∈{A,B}; ≥2同名定名; 否则 tie/split3/abstain3) —— 逐字复刻 k8_verdict.py/run4r_verdict.py, 硬对账已发布 consensus/mode, 不符即退出。
  C1  = grade 加权票: 定名票(任意grade)按 w(grade) 求和取严格最大; 权重档网格敏感性 (wA=1.0 固定, wB∈{.6,.7,.8,.9}, wC∈{.1..6}); 默认档 (1.0,0.8,0.4)。
  C2a = tie 法定人数(仅定名票, 任意grade): ≥2席同标签即定名; coarse/undet 不入数。
  C2b = C2a 基础上 coarse:X 计入标签 X 的法定人数 ("第三席粗判不弃全"的宽读法)。
  C3a = C4 真平票(tie/split3 且并列标签≥2)时用 E2 S1 证据分 (n_shared_decon, 经 e1_class_map 映射, 同类取max, AMBIG 行不给分) 具名破平; S1 并列=不具名。
  C3b = C3a + 单有效票(tie@1)时若该标签 S1≥1 则具名确认。
每规则报: 净翻正/翻错、命名面变化、对已发布门控结论(R1p/R1/P1/R2/P2/保全)的影响、全部差集清单(禁静默改判)。
输出全部落 /mnt/D/EyeKB/plans/tiep_20260927/out/ 。
"""
import json, collections, itertools, sys
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/tiep_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
SEATS = ('A', 'B', 'C')
GRADES = ('A', 'B', 'C')
W_DEFAULT = {'A': 1.0, 'B': 0.8, 'C': 0.4}

# ---------- ballot parsing ----------
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
    """-> dict(kind, label, coarse_label, grade)"""
    g = None if grade is None else str(grade).strip()
    ni = norm_identity(raw)
    if ni is None:
        return dict(kind='MISSING', label=None, coarse=None, grade=g)
    if ni == 'UNDET':
        return dict(kind='UNDET', label=None, coarse=None, grade=g)
    if ni == 'COARSE':
        return dict(kind='COARSE', label=None, coarse=str(raw)[len('coarse:'):], grade=g)
    return dict(kind='NAMED', label=ni, coarse=None, grade=g)

def c4_consensus(bs):
    """现行票规则逐字复刻 (k8_verdict/run4r_verdict consensus())."""
    votes = [b['label'] for b in bs if b['kind'] == 'NAMED' and b['grade'] in ('A', 'B')]
    if not votes:
        return None, 'abstain3', 0
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority', len(votes)
    if len(cnt) == len(votes) and len(votes) == 3:
        return None, 'split3', 3
    return None, 'tie', len(votes)

def tie_submode(bs):
    """tie 细分: 有效票数(定名&gradeAB)"""
    v = [b['label'] for b in bs if b['kind'] == 'NAMED' and b['grade'] in ('A', 'B')]
    if not v:
        return 'abstain3'
    cnt = collections.Counter(v)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return 'majority'
    if len(cnt) == len(v) == 3:
        return 'split3'
    return f'tie@{len(v)}'

# ---------- rules ----------
def rule_c1(bs, w):
    sc = collections.defaultdict(float)
    for b in bs:
        if b['kind'] == 'NAMED' and b['grade'] in w:
            sc[b['label']] += w[b['grade']]
    if not sc:
        return None
    mx = max(sc.values())
    winners = [k for k, v in sc.items() if abs(v - mx) < 1e-9]
    return winners[0] if len(winners) == 1 else None

def rule_c2(bs, count_coarse):
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

def c4_tied_labels(bs):
    v = [b['label'] for b in bs if b['kind'] == 'NAMED' and b['grade'] in ('A', 'B')]
    if not v:
        return []
    cnt = collections.Counter(v)
    mx = max(cnt.values())
    if mx >= 2:
        return []  # majority named, no tie
    tied = sorted([k for k, n in cnt.items() if n == mx])
    return tied if len(tied) >= 2 else []

def c4_sole_label(bs):
    v = [b['label'] for b in bs if b['kind'] == 'NAMED' and b['grade'] in ('A', 'B')]
    if len(v) == 1:
        return v[0]
    return None

# ---------- load faces ----------
def load_faces():
    faces = {}  # face -> list of dict(cid, member, truth, grade_ok, ballots[3], pub_consensus, pub_mode, extra)
    # --- RUN3 (2 seats, from v1.1 truthfixed table) ---
    t3 = pd.read_csv(f'{EV}/scoring/run3_object_B_table_v1.1.tsv', sep='\t')
    rows3 = []
    for _, r in t3.iterrows():
        bs = [parse_ballot(r['ann_A'], r['grade_A']), parse_ballot(r['ann_B'], r['grade_B']),
              parse_ballot(None, None)]
        tr = None if pd.isna(r['truth']) or str(r['truth']).strip() == '' else str(r['truth'])
        rows3.append(dict(cid=r['cluster_id'], member=r['member'], truth=tr, ballots=bs,
                          pub=None, pub_mode=None))
    faces['RUN3'] = rows3
    # --- RUN4-r (3 seats; grades joined from ANN jsonl, labels cross-checked vs published rows) ---
    def jload(p):
        d = {}
        for l in open(p, encoding='utf-8'):
            l = l.strip()
            if l:
                r = json.loads(l)
                d[r['cluster_id']] = r
        return d
    A4 = jload(f'{EV}/annotation/ANN_A_run4.jsonl')
    B4 = jload(f'{EV}/annotation/ANN_B_run4.jsonl')
    C4j = jload(f'{EV}/annotation/ANN_C_run4r.jsonl')
    v4r = json.load(open(f'{EV}/scoring/run4r_verdict.json'))['rows']
    T = json.load(open(f'{EV}/RUN4_TARGETS_v1.1.json'))
    hot, ctl = set(T['hotspots_22']), set(T['controls_23'])
    src4 = {'A': A4, 'B': B4, 'C': C4j}
    rows4 = []
    for cid, r in v4r.items():
        bs = []
        for s in SEATS:
            rec = src4[s].get(cid) or {}
            raw, g = rec.get('identity'), rec.get('grade')
            pub_raw = r[s.lower()]
            if str(raw) != str(pub_raw):
                sys.exit(f'[FAIL] run4r 票面 join 不一致 {cid}:{s}: jsonl={raw} verdict={pub_raw}')
            bs.append(parse_ballot(raw, g))
        rows4.append(dict(cid=cid, member=cid.split('::')[0], truth=r['truth'], ballots=bs,
                          pub=r['consensus'], pub_mode=r['mode'], r3_double_ok=r['r3_double_ok'],
                          grp='hot' if cid in hot else 'ctl'))
    faces['RUN4-r'] = rows4
    # --- RUN5 / FACEV21 / KB9: rows carry everything ---
    specs = [
        ('RUN5', f'{EV}/scoring/run5_verdict.json', 'vote_', 'grade_'),
        ('KB9', '/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_verdict.json', 'vote_', 'grade_'),
        ('FACEV21', '/mnt/D/EyeKB/plans/face_v21_20260926/scoring/FACEV21_VERDICT.json', '', '_grade'),
    ]
    hotsets = {'RUN4-r': (hot, ctl)}
    for face, path, vpfx, gpfx in specs:
        vd = json.load(open(path))
        rows = vd['rows']
        keymap = {'RUN5': ('vote_A', 'vote_B', 'vote_C', 'grade_A', 'grade_B', 'grade_C'),
                  'KB9': ('vote_A', 'vote_B', 'vote_C', 'grade_A', 'grade_B', 'grade_C'),
                  'FACEV21': ('a', 'b', 'c', 'a_grade', 'b_grade', 'c_grade')}[face]
        out_rows = []
        for cid, r in rows.items():
            bs = [parse_ballot(r[keymap[i]], r[keymap[i + 3]]) for i in range(3)]
            d = dict(cid=cid, member=cid.split('::')[0], truth=r['truth'], ballots=bs,
                     pub=r['consensus'], pub_mode=r['mode'])
            if face == 'FACEV21':
                d['r3_double_ok'] = r['r3_double_ok']
                d['grp'] = 'hot' if cid in hot else ('ctl' if cid in ctl else '?')
            if face in ('RUN5', 'KB9'):
                p2 = json.loads(r['p2_detail'])
                d['kb_classes_strict'] = set(p2['strict']['kb_classes'])
                d['kb_classes_any'] = set(p2['any']['kb_classes'])
                d['n_truth_marker'] = r['n_truth_marker_in_top10']
            out_rows.append(d)
        faces[face] = out_rows
    return faces, dict(hot=hot, ctl=ctl)

# ---------- S1 evidence (E2 decon) ----------
def load_s1():
    clsm = json.load(open('/mnt/D/EyeKB/plans/evidence_scoring_20260926/e1_class_map.json'))['map']
    s1 = collections.defaultdict(lambda: collections.defaultdict(int))  # cid -> label -> max n
    unmapped = collections.Counter()
    df = pd.read_csv('/mnt/D/EyeKB/plans/e2_decontam_20260926/data/e2_scores_S1.tsv', sep='\t')
    for _, r in df.iterrows():
        cid, member, cand, n = r['cluster_id'], r['member'], str(r['cand_canon']), int(r['n'])
        base = cand.split('::')[-1]
        ent = clsm.get(cand) or clsm.get(base)
        if ent is None:
            unmapped[cand] += 1
            continue
        vocab = 'ocular' if member == 'Q6' else 'retina'
        tgt = ent.get(vocab)
        if not isinstance(tgt, str) or tgt.startswith('AMBIG['):
            if isinstance(tgt, str):
                unmapped[f'{cand}(AMBIG)'] += 1
            continue
        s1[cid][tgt] = max(s1[cid][tgt], n)
    return s1, unmapped

def s1_score(s1, cid, label):
    return s1.get(cid, {}).get(label, 0)

def rule_c3(bs, s1map, cid, allow_sole=False):
    con, mode, nv = c4_consensus(bs)
    if con:
        return con
    tied = c4_tied_labels(bs)
    if len(tied) >= 2:
        sc = {L: s1_score(s1map, cid, L) for L in tied}
        mx = max(sc.values())
        winners = [k for k, v in sc.items() if v == mx]
        if len(winners) == 1 and mx > 0:
            return winners[0]
        return None
    if allow_sole:
        sole = c4_sole_label(bs)
        if sole and s1_score(s1map, cid, sole) >= 1:
            return sole
    return None

# ---------- hit / flip ----------
def hit_of(name, truth):
    if truth is None:
        return None
    return bool(name) and name == truth

def flip_class(c4n, rn, truth):
    h4 = hit_of(c4n, truth)
    hr = hit_of(rn, truth)
    if c4n == rn:
        return 'unchanged'
    if h4 is None:
        return 'unjudgeable(truth缺失)'
    if c4n is None and rn is not None:
        return 'FIXED(翻正)' if hr else 'BROKEN(新错名)'
    if c4n is not None and rn is None:
        return 'LOST_NAME'
    # named -> different name
    if h4 and not hr:
        return 'OVERTURN-GOOD(改翻已对名!!)'
    if (not h4) and hr:
        return 'FIXED_BY_RENAME'
    return 'RENAME-still-wrong'

def main():
    faces, tgt = load_faces()
    s1map, unmapped = load_s1()

    # ===== 自检闸门 1: C4 逐字复刻 == 已发布 consensus/mode（四面三席）=====
    fails = []
    for face, rows in faces.items():
        for r in rows:
            if r['pub'] is None and r.get('pub_mode') is None and face == 'RUN3':
                continue
            con, mode, nv = c4_consensus(r['ballots'][:3])
            pub = r['pub'] if r['pub'] is not None else None
            if (con or None) != (pub if isinstance(pub, str) else None) or mode != r['pub_mode']:
                fails.append((face, r['cid'], con, r['pub'], mode, r['pub_mode']))
    if fails:
        print('[FAIL] C4 复刻与已发布对账不符:')
        for f in fails[:20]:
            print(' ', f)
        sys.exit(1)
    print(f'[GATE1 PASS] C4 复刻对账: 4 三席面全部行 consensus/mode 与已发布件逐行一致 '
          f'(RUN4-r {len(faces["RUN4-r"])} / RUN5 {len(faces["RUN5"])} / FACEV21 {len(faces["FACEV21"])} / KB9 {len(faces["KB9"])})')

    # ===== 自检闸门 2: 已发布 P1/R1 计数复现 =====
    anchors = {'RUN5': 21, 'KB9': 22}
    for face, anchor in anchors.items():
        cnt = sum(1 for r in faces[face] if hit_of(c4_consensus(r['ballots'])[0], r['truth']))
        assert cnt == anchor, f'[FAIL] {face} P1 复算 {cnt} != 已发布 {anchor}'
    v4r = json.load(open(f'{EV}/scoring/run4r_verdict.json'))
    cnt = sum(1 for r in faces['RUN4-r'] if r['grp'] == 'hot' and hit_of(c4_consensus(r['ballots'])[0], r['truth']))
    assert cnt == v4r['R1p']['count'], f'[FAIL] RUN4-r R1p 复算 {cnt} != {v4r["R1p"]["count"]}'
    fv = json.load(open('/mnt/D/EyeKB/plans/face_v21_20260926/scoring/FACEV21_VERDICT.json'))
    cnt = sum(1 for r in faces['FACEV21'] if r['grp'] == 'hot' and hit_of(c4_consensus(r['ballots'])[0], r['truth']))
    assert cnt == fv['R1']['count'], f'[FAIL] FACEV21 R1 复算 {cnt} != {fv["R1"]["count"]}'
    print(f'[GATE2 PASS] 已发布计数锚点复现: RUN5 P1=21/33, KB9 P1=22/33, RUN4-r R1p=15/22, FACEV21 R1=19/22 (gate ≥15) 全等')

    # ===== 盘点 =====
    inv, inv_detail = [], []
    for face, rows in faces.items():
        modes = collections.Counter()
        grades = collections.Counter()
        seat_grades = {s: collections.Counter() for s in SEATS}
        lost_hits = []
        n_truth = 0
        for r in rows:
            con, mode, nv = c4_consensus(r['ballots'])
            sm = tie_submode(r['ballots']) if mode in ('tie', 'split3', 'abstain3') else mode
            modes[sm] += 1
            for i, b in enumerate(r['ballots']):
                if b['grade'] in GRADES:
                    seat_grades[SEATS[i]][b['grade']] += 1
                    grades[b['grade']] += 1
            if not con and r['truth'] and hit_of(con, r['truth']) is False:
                n_truth += 1
                # 盘上被弃/未定名票里是否已含真值标签（grade-A/B 定名票 或 coarse/gradeC 票携带真值）
                carry = [('AB' if (b['kind'] == 'NAMED' and b['grade'] in ('A', 'B'))
                          else 'G' if b['kind'] == 'NAMED'
                          else 'C' if b['kind'] == 'COARSE' and b['coarse'] == r['truth']
                          else None) for b in r['ballots']]
                carry = [x for b, x in zip(r['ballots'], carry) if x]
                if carry:
                    lost_hits.append((r['cid'], ''.join(c for c in carry)))
        inv.append(dict(face=face, n_rows=len(rows),
                        n_truth_rows=sum(1 for r in rows if r['truth']),
                        majority=modes.get('majority', 0), tie1=modes.get('tie@1', 0),
                        tie2=modes.get('tie@2', 0), split3=modes.get('split3', 0), abstain3=modes.get('abstain3', 0),
                        grade_A=grades['A'], grade_B=grades['B'], grade_C=grades['C'],
                        n_truth_carrying_unnamed=len(lost_hits),
                        lost_hits=';'.join(f'{c}({g})' for c, g in lost_hits)))
        for r in rows:
            con, mode, nv = c4_consensus(r['ballots'])
            if mode in ('tie', 'split3', 'abstain3'):
                inv_detail.append(dict(face=face, cid=r['cid'], truth=r['truth'], mode=tie_submode(r['ballots']),
                                        **{f'label_{s}': r['ballots'][i]['label'] or (f'coarse:{r["ballots"][i]["coarse"]}' if r['ballots'][i]['kind'] == 'COARSE' else ('undetermined' if r['ballots'][i]['kind'] == 'UNDET' else ''))
                                           for i, s in enumerate(SEATS)},
                                        **{f'grade_{s}': r['ballots'][i]['grade'] for i, s in enumerate(SEATS)}))
    pd.DataFrame(inv).to_csv(f'{ROOT}/out/inventory_summary.tsv', sep='\t', index=False)
    pd.DataFrame(inv_detail).sort_values(['face', 'cid']).to_csv(f'{ROOT}/out/inventory_tie_detail.tsv', sep='\t', index=False)
    print('\n[盘点] 各面 C4 模式下 tie/弃权 发生面:')
    print(pd.DataFrame(inv).to_string(index=False))

    # ===== 反事实重投票 =====
    grid = [{'A': 1.0, 'B': wb, 'C': wc} for wb in (0.6, 0.7, 0.8, 0.9) for wc in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)]
    RULES = {'C1_default': ('C1', W_DEFAULT), 'C2a': ('C2', False), 'C2b': ('C2', True),
             'C3a': ('C3', False), 'C3b': ('C3', True), 'C4': ('C4', None)}
    matrix, flips, diffs = [], [], []
    for face, rows in faces.items():
        for r in rows:
            c4n, c4m, _ = c4_consensus(r['ballots'])
            names = {}
            for rn_, (kind, arg) in RULES.items():
                if kind == 'C4':
                    names[rn_] = c4n
                elif kind == 'C1':
                    names[rn_] = rule_c1(r['ballots'], arg)
                elif kind == 'C2':
                    names[rn_] = rule_c2(r['ballots'], arg)
                else:
                    names[rn_] = rule_c3(r['ballots'], s1map, r['cid'], allow_sole=arg)
            tied = c4_tied_labels(r['ballots'])
            s1s = {L: s1_score(s1map, r['cid'], L) for L in tied} if tied else None
            sole = c4_sole_label(r['ballots'])
            matrix.append(dict(face=face, cid=r['cid'], member=r['member'], truth=r['truth'],
                               c4_name=c4n, c4_mode=c4m, **{f'name_{k}': v for k, v in names.items()},
                               s1_tied_scores=json.dumps(s1s, ensure_ascii=False) if s1s else '',
                               s1_sole=(s1_score(s1map, r['cid'], sole) if sole else '')))
            for rn_, nm in names.items():
                if rn_ == 'C4':
                    continue
                fc = flip_class(c4n, nm, r['truth'])
                if fc != 'unchanged':
                    diffs.append(dict(face=face, cid=r['cid'], rule=rn_, truth=r['truth'],
                                      c4_name=c4n, new_name=nm, flip_class=fc,
                                      was_published_hit=bool(hit_of(c4n, r['truth'])),
                                      becomes_hit=bool(hit_of(nm, r['truth']))))
        # gate impact per rule
        for gname, (kind, arg) in RULES.items():
            def nm_of(r):
                if kind == 'C4':
                    return c4_consensus(r['ballots'])[0]
                if kind == 'C1':
                    return rule_c1(r['ballots'], arg)
                if kind == 'C2':
                    return rule_c2(r['ballots'], arg)
                return rule_c3(r['ballots'], s1map, r['cid'], allow_sole=arg)
            named = sum(1 for r in rows if nm_of(r))
            fixed = broken = over = 0
            for r in rows:
                c4n = c4_consensus(r['ballots'])[0]
                fc = flip_class(c4n, nm_of(r), r['truth'])
                if fc in ('FIXED(翻正)', 'FIXED_BY_RENAME'):
                    fixed += 1
                elif fc == 'BROKEN(新错名)':
                    broken += 1
                elif fc.startswith('OVERTURN'):
                    over += 1
            d = dict(face=face, rule=gname, named_c4=sum(1 for r in rows if c4_consensus(r['ballots'])[0]),
                     named_new=named, fixed=fixed, broken=broken, overturn=over, net=fixed - broken)
            # gate recompute
            if face == 'RUN4-r':
                d['R1p_new'] = sum(1 for r in rows if r['grp'] == 'hot' and hit_of(nm_of(r), r['truth']))
                d['R1p_gate'] = '>=15'
                d['R2p_new'] = sum(1 for r in rows if r['grp'] == 'ctl' and r['r3_double_ok'] and not hit_of(nm_of(r), r['truth']))
                d['R2p_gate'] = '<=1'
            elif face == 'FACEV21':
                d['R1_new'] = sum(1 for r in rows if r['grp'] == 'hot' and hit_of(nm_of(r), r['truth']))
                d['R1_gate'] = '>=15'
                d['R2_new'] = sum(1 for r in rows if r['grp'] == 'ctl' and r['r3_double_ok'] and not hit_of(nm_of(r), r['truth']))
                d['R2_gate'] = '<=1'
                p = {r['cid']: nm_of(r) for r in rows if r['cid'] in ('Q4::15', 'Q5b::13')}
                d['preserve_new'] = all(p[k] == next(r['truth'] for r in rows if r['cid'] == k) for k in p)
            elif face in ('RUN5', 'KB9'):
                d['P1_new'] = sum(1 for r in rows if hit_of(nm_of(r), r['truth']))
                d['P1_gate'] = '>=24/33'
                # P2 violation: name in kb_classes(any/strict) & name!=truth & marker>=3
                for scope in ('strict', 'any'):
                    vl = sum(1 for r in rows
                             if nm_of(r) and r[f'kb_classes_{scope}'] and nm_of(r) in r[f'kb_classes_{scope}']
                             and nm_of(r) != r['truth'] and r['n_truth_marker'] >= 3)
                    d[f'P2_{scope}_new'] = vl
                d['P2_gate'] = '<=1/33'
            else:  # RUN3
                den = max(1, sum(1 for r in rows if r['truth']))
                d['acc_new'] = round(sum(1 for r in rows if hit_of(nm_of(r), r['truth'])) / den, 4)
                d['acc_c4'] = round(sum(1 for r in rows if hit_of(c4_consensus(r['ballots'])[0], r['truth'])) / den, 4)
            flips.append(d)
    pd.DataFrame(matrix).to_csv(f'{ROOT}/out/revote_matrix.tsv', sep='\t', index=False)
    fdf = pd.DataFrame(flips)
    fdf.to_csv(f'{ROOT}/out/flips_by_rule.tsv', sep='\t', index=False)
    pd.DataFrame(diffs).to_csv(f'{ROOT}/out/diff_pass_conclusions.tsv', sep='\t', index=False)
    print('\n[规则×面 汇总]')
    print(fdf.to_string(index=False))
    print(f'\n[差集清单行数] {len(diffs)} -> out/diff_pass_conclusions.tsv')

    # ===== C1 权重网格 =====
    grow = []
    for w in grid:
        for face, rows in faces.items():
            fixed = broken = over = named = 0
            for r in rows:
                c4n = c4_consensus(r['ballots'])[0]
                nm = rule_c1(r['ballots'], w)
                if nm:
                    named += 1
                fc = flip_class(c4n, nm, r['truth'])
                if fc in ('FIXED(翻正)', 'FIXED_BY_RENAME'):
                    fixed += 1
                elif fc == 'BROKEN(新错名)':
                    broken += 1
                elif fc.startswith('OVERTURN'):
                    over += 1
            grow.append(dict(wA=1.0, wB=w['B'], wC=w['C'], face=face, named=named,
                             fixed=fixed, broken=broken, overturn=over, net=fixed - broken))
    gdf = pd.DataFrame(grow)
    gdf.to_csv(f'{ROOT}/out/c1_weight_grid.tsv', sep='\t', index=False)
    print('\n[C1 权重网格 全局面合计] (wA=1.0)')
    print(gdf.groupby(['wB', 'wC'])[['fixed', 'broken', 'overturn', 'net']].sum().to_string())

    # KB9 gate per rule explicit
    kb9 = fdf[fdf.face == 'KB9']
    print('\n[KB9 门控影响 (>=24/33)]')
    print(kb9[['rule', 'named_new', 'fixed', 'broken', 'P1_new', 'P1_gate']].to_string(index=False))

    # unmapped S1 candidates register
    with open(f'{ROOT}/out/s1_unmapped_candidates.txt', 'w', encoding='utf-8') as f:
        for k, v in sorted(unmapped.items()):
            f.write(f'{k}\t{v}\n')
    print(f'\n[S1 映射] 未映射/AMBIG 候选类 {len(unmapped)} 种 -> out/s1_unmapped_candidates.txt')

    # machine summary
    summary = dict(gates=dict(c4_replication='PASS', count_anchors='PASS'),
                   inventory=inv, flips=flips,
                   s1_unmapped=dict(unmapped),
                   diff_rows=len(diffs))
    json.dump(summary, open(f'{ROOT}/out/tiep_counts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n[DONE] out/ 全件已落盘')

if __name__ == '__main__':
    main()
