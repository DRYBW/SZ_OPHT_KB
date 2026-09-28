#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1M3-IMPL (t_e0f94d4f, PREREG_H1M3 §1): 判读 runner 定名链组件——H1 判序锚实装。

- 票形解析逐字沿 tiep t1_revote.py / RUNNER_WATCHLIST H3 语义；
- C2b 计票/tie-弃权处理逐字沿 obligrun o10_verdict_t_c145db7c.py（rule_c2/c2b_mode，票规 v2 决策件）；
- C4 计票逐字沿 grade_anchor grade_h1_counterfactual.py（facev21_verdict 语义，v1=C4 现行基线）；
- H1 判序锚（GRADE_ANCHOR §3-H1）：具名票 grade≥B 协议下限；档位谓词族 S/M/M2/M3/X 逐字沿锚件 VARIANTS；
  推荐档 H1-M3 = identity_evidence=='pass' ∨ resolution=='pass'（technical 三门不参与，3A 同构）；
  模式 B（本波实装默认）= NAMED∧C∧过门 → 生效 grade 下限化 B + anchor_applied 旗；
  模式 A（PREREG 可声明档）= NAMED∧C 一律拒收（冻结票重放中=剔除出计票，不生成 anchor_applied）；
  未过门的 NAMED∧C：模式 B 不升（namedC_noanchor 旗，C4 不入数、C2b 按已批准 v2 规则照入——
  H1 治 grade 语义漂移，不改写票规计票语义，锚件 §22）。
生效制=向前（协议 v1.3 §9 落款后新预注册 run 起用）；历史冻结判读不回改；打分栈（E 系）与本组件无交集。
"""
import collections

NAMED, COARSE, UNDET, MISSING = 'NAMED', 'COARSE', 'UNDET', 'MISSING'

# ---------------- 票形解析（t1_revote/o10 逐字语义） ----------------
def norm_identity(ident):
    if ident is None:
        return None
    s = str(ident)
    if s.startswith('undetermined'):
        return 'UNDET'
    if s.startswith('coarse:'):
        return 'COARSE'
    return s

def parse_ballot(raw_identity, grade, gates=None):
    g = None if grade is None else str(grade).strip()
    ni = norm_identity(raw_identity)
    gt = gates or {}
    b = dict(kind=MISSING, label=None, coarse=None, grade=g,
             ie=str(gt.get('identity_evidence', '') or ''),
             res=str(gt.get('resolution', '') or ''),
             tech=str(gt.get('technical', '') or ''),
             raw_identity=raw_identity)
    if ni is None:
        return b
    if ni == 'UNDET':
        b['kind'] = UNDET
        return b
    if ni == 'COARSE':
        b['kind'] = COARSE
        b['coarse'] = str(raw_identity)[len('coarse:'):]
        return b
    b['kind'] = NAMED
    b['label'] = ni
    return b

# ---------------- H1 档位谓词（grade_anchor VARIANTS 逐字） ----------------
def _ie(b): return b['ie']
def _res(b): return b['res']
def _tech(b): return b['tech']

TIERS = {
    'none': lambda b: False,
    'S':    lambda b: _ie(b) == 'pass' and _res(b) == 'pass' and _tech(b) in ('pass', 'na', ''),
    'M':    lambda b: _ie(b) != 'fail' and _res(b) != 'fail' and _tech(b) != 'fail',
    'M2':   lambda b: (_ie(b) == 'pass' or _res(b) == 'pass') and _tech(b) != 'fail',
    'M3':   lambda b: (_ie(b) == 'pass' or _res(b) == 'pass'),
    'X':    lambda b: True,
}

def apply_h1_anchor(b, tier='M3', mode='B'):
    """返回该票的生效票（新 dict）：eff_grade + 旗标。非 NAMED∧C 形态一律原样（合法弃权/粗判不触）。"""
    o = dict(b)
    o['eff_grade'] = b['grade']
    o['anchor_applied'] = False
    o['namedC_noanchor'] = False
    o['rejected'] = False
    illegal = (b['kind'] == NAMED and str(b['grade']) == 'C')
    if not illegal or tier == 'none':
        return o
    if mode == 'A':
        # 模式 A（强）：具名∧C=非法票形，一律拒收回炉；冻结票重放=剔除出计票
        o['rejected'] = True
        return o
    # 模式 B（弱，本波实装默认）：档位过门→自动下限 B；不过门→保持 C 记旗
    if TIERS[tier](b):
        o['eff_grade'] = 'B'
        o['anchor_applied'] = True
    else:
        o['namedC_noanchor'] = True
    return o

# ---------------- C4 计票（grade_h1_counterfactual ballot/c4 逐字语义，用 eff_grade） ----------------
def c4_ballot(b):
    if b['kind'] in (UNDET, COARSE, MISSING) or b['label'] in (None, '') or b.get('rejected'):
        return None
    if str(b.get('eff_grade', b['grade'])) not in ('A', 'B'):
        return None
    return b['label']

def c4_count(bs):
    votes = [x for x in (c4_ballot(b) for b in bs) if x]
    if not votes:
        return None, 'abstain3'
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority'
    if len(cnt) == len(votes) == 3:
        return None, 'split3'
    return None, 'tie'

# ---------------- C2b 计票（o10_verdict rule_c2/c2b_mode 逐字；grade 不参与→锚不扰动） ----------------
def rule_c2(bs, count_coarse=True):
    cnt = collections.Counter()
    for b in bs:
        if b.get('rejected'):
            continue
        if b['kind'] == NAMED:
            cnt[b['label']] += 1
        elif count_coarse and b['kind'] == COARSE and b['coarse']:
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
            if b.get('rejected'):
                continue
            if b['kind'] == NAMED:
                cnt[b['label']] += 1
            elif b['kind'] == COARSE and b['coarse']:
                cnt[b['coarse']] += 1
        if not cnt:
            return None, 'abstain3'
        if len(cnt) == sum(1 for b in bs if b['kind'] in (NAMED, COARSE) and not b.get('rejected')) == 3:
            return None, 'split3'
        return None, 'tie'
    return name, 'named'

def consensus(bs, rule='C2b'):
    f = c2b_mode if rule == 'C2b' else c4_count
    return f(bs)

# ---------------- 输入适配器 ----------------
def from_matrix_row(r):
    """ballot_matrix.tsv 行（dict-like，gate_* 列；identity_norm 已归一）。
    矩阵 identity_norm∈{UNDET,COARSE,MISSING,''}=已归一 kind；具名票 label=identity_norm。"""
    ni = r['identity_norm']
    ni = '' if ni is None else str(ni)
    kind = r['kind']
    b = dict(kind=MISSING, label=None, coarse=None, grade=str(r['grade']),
             ie=str(r['gate_identity_evidence'] or '') if r['gate_identity_evidence'] is not None else '',
             res=str(r['gate_resolution'] or '') if r['gate_resolution'] is not None else '',
             tech=str(r['gate_technical'] or '') if r['gate_technical'] is not None else '',
             raw_identity=r['identity'])
    if kind == NAMED:
        b['kind'], b['label'] = NAMED, (ni if ni not in ('', 'nan', 'None') else None)
        if b['label'] is None:
            b['kind'] = MISSING
    elif kind == COARSE:
        b['kind'] = COARSE
        s = str(r['identity'])
        b['coarse'] = s[len('coarse:'):] if s.startswith('coarse:') else None
    elif kind == UNDET:
        b['kind'] = UNDET
    return b

def from_ann_row(rec):
    """ANN_*.jsonl 票记录（identity/grade/gates{identity_evidence,resolution,technical}）。"""
    return parse_ballot(rec.get('identity'), rec.get('grade'), rec.get('gates') or {})

# ---------------- 自测（先于真实输入，KBX/o10 惯例） ----------------
def selftest():
    B = lambda kind, **kw: dict(kind=kind, label=kw.get('label'), coarse=kw.get('coarse'),
                                grade=kw.get('grade', 'B'), ie=kw.get('ie', ''), res=kw.get('res', ''),
                                tech=kw.get('tech', ''), raw_identity=kw.get('raw'))
    G = dict(ie='pass', res='pass', tech='na')
    # 1) NAMED∧C 过门 → 下限化 B + 旗
    p = apply_h1_anchor(B(NAMED, label='Epithelium', grade='C', **G), 'M3', 'B')
    assert p['eff_grade'] == 'B' and p['anchor_applied'] and not p['namedC_noanchor']
    # 2) NAMED∧C 未过门（ie/res 皆 unresolved，RUN5 Q6::31 B 席通胀案形态）→ 不升
    q = apply_h1_anchor(B(NAMED, label='Pericytes', grade='C', ie='unresolved', res='unresolved', tech='na'), 'M3', 'B')
    assert q['eff_grade'] == 'C' and not q['anchor_applied'] and q['namedC_noanchor']
    # 2b) 同票在 H1-X 档会升（通胀机制复现：M3 挡、X 不挡）
    qx = apply_h1_anchor(B(NAMED, label='Pericytes', grade='C', ie='unresolved', res='unresolved', tech='na'), 'X', 'B')
    assert qx['anchor_applied']
    # 3) COARSE∧C / UNDET∧C 合法形态不触锚
    for b0 in (B(COARSE, coarse='Epithelium', grade='C', **G), B(UNDET, grade='C')):
        p = apply_h1_anchor(b0, 'M3', 'B')
        assert not p['anchor_applied'] and p['eff_grade'] == 'C'
    # 4) tier=none 全不触
    p = apply_h1_anchor(B(NAMED, label='X', grade='C', **G), 'none', 'B')
    assert p['eff_grade'] == 'C' and not p['anchor_applied']
    # 5) 模式 A 一律拒收
    p = apply_h1_anchor(B(NAMED, label='X', grade='C', **G), 'M3', 'A')
    assert p['rejected'] and c4_ballot(p) is None
    # 6) C4：锚后升票入数、未升 C 弃
    bs = [apply_h1_anchor(b0, 'M3', 'B') for b0 in
          (B(NAMED, label='Fibroblasts', grade='C', ie='pass', res='unresolved', tech='na'),
           B(NAMED, label='Fibroblasts', grade='B', **G),
           B(UNDET))]
    assert c4_count(bs) == ('Fibroblasts', 'majority')
    # H1-X 档（纯一致性锚）会升通胀案票→假多数（RUN5 Q6::31 机制复现）；H1-M3 门条件挡下→维持 tie
    assert c4_count([apply_h1_anchor(b0, 'X', 'B') for b0 in
                     (B(NAMED, label='Pericytes', grade='C', ie='unresolved', res='unresolved', tech='na'),
                      B(NAMED, label='Pericytes', grade='B', **G), B(UNDET))]) == ('Pericytes', 'majority')
    assert c4_count([apply_h1_anchor(b0, 'M3', 'B') for b0 in
                     (B(NAMED, label='Pericytes', grade='C', ie='unresolved', res='unresolved', tech='na'),
                      B(NAMED, label='Pericytes', grade='B', **G), B(UNDET))]) == (None, 'tie')
    # 7) C2b 语义五用例（o10 selftest 逐字）
    cases = [
        ([B(NAMED, label='Endothelium', grade='C'), B(NAMED, label='Endothelium', grade='A'), B(UNDET)], ('Endothelium', 'named')),
        ([B(NAMED, label='Epithelium', grade='B'), B(COARSE, coarse='Epithelium'), B(UNDET)], ('Epithelium', 'named')),
        ([B(NAMED, label='Epithelium'), B(NAMED, label='Fibroblasts'), B(NAMED, label='Endothelium')], (None, 'split3')),
        ([B(NAMED, label='Epithelium'), B(UNDET), B(MISSING)], (None, 'tie')),
        ([B(UNDET), B(MISSING), B(UNDET)], (None, 'abstain3')),
    ]
    for bs0, exp in cases:
        assert c2b_mode(bs0) == exp, f'C2b 自测失败 {c2b_mode(bs0)} != {exp}'
    # 8) C2b 结构吸收：NAMED 票 grade 下限化不改共识（锚件 §4 预言的组件级断言）
    import random
    rng = random.Random(7)
    lab = ['Epithelium', 'Fibroblasts', 'Immune Cells', None]
    for _ in range(500):
        bs0 = []
        for _i in range(3):
            l = rng.choice(lab)
            if l is None:
                bs0.append(B(rng.choice([UNDET, MISSING])))
            else:
                bs0.append(B(NAMED, label=l, grade=rng.choice(['A', 'B', 'C']), **G))
        bs1 = [apply_h1_anchor(x, 'M3', 'B') for x in bs0]
        assert c2b_mode(bs0) == c2b_mode(bs1), 'C2b 吸收性断言失败'
    print('h1m3_runner selftest PASS (8 组)')

if __name__ == '__main__':
    selftest()
