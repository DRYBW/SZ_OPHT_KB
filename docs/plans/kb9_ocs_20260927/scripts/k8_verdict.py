#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K8: 自检裁决（run5_verdict.py 判据逐字复用；只改路径与票集来源）。
票集: 变化簇=本次三席新票(ANN_X_k9), 无变化簇=RUN5 存档票(ANN_X_run5) —— 每簇三票同一证据状态。
球门: P1>=24/33, P2 strict/any <=1/33 —— 与 RUN5 完全一致, 不降。
crosswalk: 冻结件 + build/KB9_CROSSWALK_ext.tsv (追加行)。"""
import json, hashlib, collections
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
WORK = f'{EV}/work_t_d1ca11b0'

face = [json.loads(l) for l in open(f'{ROOT}/build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl', encoding='utf-8')]
face_ids = [r['cluster_id'] for r in face]
Q6S = json.load(open(f'{EV}/defs/Q6_def.json', encoding='utf-8'))
SUPER = {v2: k for k, vs in Q6S['super_map'].items() for v2 in vs}

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

cw = pd.read_csv(f'{WORK}/KB_Q6_crosswalk.tsv', sep='\t')
ext = pd.read_csv(f'{ROOT}/build/KB9_CROSSWALK_ext.tsv', sep='\t')
CW = {r['kb_name']: ((str(r['q6_vocab_class']) if pd.notna(r['q6_vocab_class']) else ''), str(r['provenance'])) for _, r in cw.iterrows()}
for _, r in ext.iterrows():
    CW[r['kb_name']] = ((str(r['q6_vocab_class']) if pd.notna(r['q6_vocab_class']) else ''), str(r['provenance']))

mk = pd.read_csv(f'{WORK}/author_class_markers_data.tsv', sep='\t')
MK = {r['truth_super']: set(str(r['top60_markers']).split(',')) for _, r in mk.iterrows()}

changed = set(json.load(open(f'{ROOT}/out/kb9_changed_clusters.json'))['changed'])


def load(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if l:
            r = json.loads(l)
            d[r['cluster_id']] = r
    return d


V = {}
for stem in ('A', 'B', 'C'):
    arch = load(f'{EV}/annotation/ANN_{stem}_run5.jsonl')
    newp = f'{ROOT}/out/ANN_{stem}_k9.jsonl'
    new = load(newp) if pd.notna(newp) and __import__('os').path.exists(newp) else {}
    merged = {}
    for cid in face_ids:
        if cid in changed:
            if cid not in new:
                raise SystemExit(f'缺失新票 {stem}:{cid} — 投票未完成')
            merged[cid] = new[cid]
        else:
            merged[cid] = arch[cid]
    V[stem] = merged


def norm_identity(ident):
    if ident is None:
        return None
    if str(ident).startswith('undetermined'):
        return 'UNDET'
    if str(ident).startswith('coarse:'):
        return 'COARSE'
    return ident


def ballot(r):
    if not r:
        return None
    ni = norm_identity(r.get('identity'))
    if ni in (None, 'UNDET', 'COARSE'):
        return None
    if str(r.get('grade')) not in ('A', 'B'):
        return None
    return ni


def consensus(cid):
    votes = [b for b in (ballot(V['A'].get(cid)), ballot(V['B'].get(cid)), ballot(V['C'].get(cid))) if b]
    if not votes:
        return None, 'abstain3', 0
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority', len(votes)
    if len(cnt) == len(votes) and len(votes) == 3:
        return None, 'split3', 3
    return None, 'tie', len(votes)


def kb_hit_class(name):
    c, p = CW.get(name, ('', 'unknown'))
    if p == 'no_counterpart':
        return None, 'no_counterpart'
    if p == 'ambiguous':
        return tuple(c.split('|')), 'ambiguous'
    return (c,), p


rows = {}
ensg = json.load(open('/home/ubuntu/rp_project/m3/s2/ensg_symbol_map.json'))
for r in face:
    cid = r['cluster_id']
    tv, tfrac, tn = truth[cid]
    con, mode, nv = consensus(cid)
    ranking = [x['cell_type'] for x in (r.get('kb_marker_ranking') or [])]
    kb_top1 = ranking[0] if ranking else ''
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
    rows[cid] = dict(cluster_id=cid, n_cells=int(r['n_cells']), truth=tv, truth_frac=tfrac, n_truth_cells=tn,
                     vote_A=V['A'].get(cid, {}).get('identity'), vote_B=V['B'].get(cid, {}).get('identity'),
                     vote_C=V['C'].get(cid, {}).get('identity'),
                     grade_A=V['A'].get(cid, {}).get('grade'), grade_B=V['B'].get(cid, {}).get('grade'),
                     grade_C=V['C'].get(cid, {}).get('grade'),
                     consensus=con, mode=mode, n_ballots=nv,
                     p1_hit=bool(con and con == tv), kb_n=len(ranking), kb_top1=kb_top1, kb_names='|'.join(ranking),
                     top10=';'.join(top10_sym), top10_ensg=';'.join(top10),
                     n_truth_marker_in_top10=len(ov), truth_markers_in_top10=';'.join(ov_sym),
                     p2_strict_violation=p2['strict']['violation'], p2_any_violation=p2['any']['violation'],
                     p2_detail=json.dumps(p2, ensure_ascii=False), revoted=cid in changed)

hit = sorted([c for c in face_ids if rows[c]['p1_hit']])
miss = sorted([c for c in face_ids if not rows[c]['p1_hit']])
p1 = dict(count=len(hit), total=33, rate=round(len(hit) / 33, 4), gate='>=24/33', passed=len(hit) >= 24,
          hit_clusters=hit, missed_clusters=miss, missed_modes={c: rows[c]['mode'] for c in miss})
for scope in ('strict', 'any'):
    key = f'p2_{scope}_violation'
    vl = sorted([c for c in face_ids if rows[c][key]])
    detail = []
    for c in vl:
        d = json.loads(rows[c]['p2_detail'])[scope]
        detail.append(dict(cluster_id=c, truth=rows[c]['truth'], consensus=rows[c]['consensus'],
                           kb_names=rows[c]['kb_names'], mapping=d['mapping'],
                           n_truth_marker_in_top10=rows[c]['n_truth_marker_in_top10'],
                           truth_markers_in_top10=rows[c]['truth_markers_in_top10'], top10=rows[c]['top10']))
    p2o = dict(count=len(vl), total=33, gate='<=1/33', passed=len(vl) <= 1, violation_clusters=vl, evidence=detail)
    if scope == 'strict':
        p2_strict = p2o
    else:
        p2_any = p2o
kb_empty = sorted([c for c in face_ids if rows[c]['kb_n'] == 0])
p3 = dict(kb_empty_n=len(kb_empty), kb_empty_clusters=kb_empty)

verdict = dict(card='t_6df5b739', run='KB9-selfcheck', prereg='KB9_PREREG.md',
               prereg_sha256=hashlib.sha256(open(f'{ROOT}/KB9_PREREG.md', 'rb').read()).hexdigest(),
               run5_prereg_sha256=hashlib.sha256(open(f'{EV}/RUN5_FACE_PREREG.md', 'rb').read()).hexdigest(),
               face='build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl',
               face_sha256=hashlib.sha256(open(f'{ROOT}/build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl', 'rb').read()).hexdigest(),
               votes=dict(A='qwen3.8-max', B='glm-5.1', C='deepseek-v3.2',
                          mix='25 changed re-voted + 8 archived RUN5 ballots reused'),
               P1=p1, P2_strict=p2_strict, P2_any=p2_any, P3=p3,
               verdict=dict(P1='PASS' if p1['passed'] else 'FAIL',
                            P2='PASS' if p2_any['passed'] else 'FAIL',
                            overall='PASS' if (p1['passed'] and p2_any['passed']) else 'FAIL'),
               rows=rows)
json.dump(verdict, open(f'{ROOT}/out/kb9_verdict.json', 'w'), ensure_ascii=False, indent=1)
cols = ['cluster_id', 'n_cells', 'truth', 'truth_frac', 'vote_A', 'vote_B', 'vote_C', 'grade_A', 'grade_B', 'grade_C',
        'consensus', 'mode', 'p1_hit', 'kb_n', 'kb_top1', 'kb_names', 'top10', 'n_truth_marker_in_top10',
        'p2_strict_violation', 'p2_any_violation', 'revoted']
pd.DataFrame([rows[c] for c in face_ids])[cols].to_csv(f'{ROOT}/out/kb9_truth_table.tsv', sep='\t', index=False)
print(f"[P1] {p1['count']}/33 (gate>=24) {verdict['verdict']['P1']}")
print(f"     miss: {miss}")
print(f"[P2 strict] {p2_strict['count']}/33 {p2_strict['violation_clusters']} | [any] {p2_any['count']}/33 {p2_any['violation_clusters']}")
print(f"[P3] kb空 {p3['kb_empty_n']}/33")
print('overall:', verdict['verdict']['overall'])
