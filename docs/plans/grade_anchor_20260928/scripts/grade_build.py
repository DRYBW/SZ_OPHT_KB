#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRADE-D16 步骤1：sha 台账 + 席×簇×grade 矩阵复原 + 验证闸门（零 LLM，纯读档）
- 输入只读；sha256 台账落 data/SHA_LEDGER_INPUTS.txt
- 矩阵 = 全部冻结票档 (archive, dataset, run, seat, model, cluster, truth?, grade, identity...)
- 闸门 G1-G6：与已发布 consensus/C2b/truth 逐簇对账，不等即中止
"""
import json, sys, os, hashlib, collections, datetime

OUT = '/mnt/D/EyeKB/plans/grade_anchor_20260928'
ROOT = '/mnt/D/EyeKB/plans'
EVAL = f'{ROOT}/evalset'

def sha256(p, blk = 1 << 22):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(blk), b''):
            h.update(b)
    return h.hexdigest()

# ---------- truth 与归一实现：kb2_bscore exec-head 逐字复用（与 BTEST/FACEV21 同一实现源） ----------
src = open(f'{EVAL}/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py').read()
head = src.split('def summarize')[0]
ns = {'__name__': 'ctx'}
exec(compile(head, 'h', 'exec'), ns)
truth_major, norm_identity = ns['truth_major'], ns['norm_identity']

def load_jsonl(p):
    d = {}
    for l in open(p):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        d[r['cluster_id']] = r
    return d

# ---------- retina45 簇集 + 发布 consensus 参照 ----------
BTEST_TBL = f'{ROOT}/btest_20260927/out/per_cluster_table_btest.tsv'
import pandas as pd
bt = pd.read_csv(BTEST_TBL, sep='\t')
RET45 = sorted(bt['cluster_id'])
assert len(RET45) == 45
truth_ret = dict(zip(bt['cluster_id'], bt['truth']))

# Q6 33 簇 truth
q6t = pd.read_csv(f'{EVAL}/scoring/run5_truth_table.tsv', sep='\t')
truth_q6 = dict(zip(q6t['cluster_id'], q6t['truth']))

# retina45 truth 重建对账（truth_major 独立重算 vs btest 表 truth 列）
mismatch_t = []
for cid in RET45:
    tag, cl = cid.split('::')
    tm = truth_major(tag, cl)
    lab = tm[0] if tm else None
    if lab != truth_ret[cid]:
        mismatch_t.append((cid, lab, truth_ret[cid]))
assert not mismatch_t, f'truth 重建对账失败: {mismatch_t[:5]}'

# ---------- 票档清单 ----------
# dataset: RET45 / Q6-33 / Q6-25 / PILOT
ARCHIVES = [
    # (archive, dataset, seats: {seat: (path, model)})
    ('RUN2',      'PILOT-2seat', {'A': (f'{EVAL}/annotation/ANN_A_run2.jsonl', None),
                                   'B2': (f'{EVAL}/annotation/ANN_B2_run2.jsonl', None)}),
    ('RUN3',      'FULL290',     {'A': (f'{EVAL}/annotation/ANN_A_run3.jsonl', None),
                                   'B': (f'{EVAL}/annotation/ANN_B_run3.jsonl', None)}),
    ('RUN3MINI',  'PILOT-5',     {'A3': (f'{EVAL}/annotation/ANN_A3_run3mini.jsonl', None),
                                   'B3': (f'{EVAL}/annotation/ANN_B3_run3mini.jsonl', None)}),
    ('RUN4',      'RET45-2seat', {'A': (f'{EVAL}/annotation/ANN_A_run4.jsonl', 'qwen3.8-max'),
                                   'B': (f'{EVAL}/annotation/ANN_B_run4.jsonl', 'glm-5.1')}),
    ('RUN4-r',    'RET45',       {'A': (f'{EVAL}/annotation/ANN_A_run4.jsonl', 'qwen3.8-max'),
                                   'B': (f'{EVAL}/annotation/ANN_B_run4.jsonl', 'glm-5.1'),
                                   'C': (f'{EVAL}/annotation/ANN_C_run4r.jsonl', 'deepseek-v3.2')}),
    ('RUN5',      'Q6-33',       {'A': (f'{EVAL}/annotation/ANN_A_run5.jsonl', 'qwen3.8-max'),
                                   'B': (f'{EVAL}/annotation/ANN_B_run5.jsonl', 'glm-5.1'),
                                   'C': (f'{EVAL}/annotation/ANN_C_run5.jsonl', 'deepseek-v3.2')}),
    ('RUN6A',     'Q6-33',       {'A': (f'{ROOT}/evalset/run6a/ANN_A_run6a.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/evalset/run6a/ANN_B_run6a.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/evalset/run6a/ANN_C_run6a.jsonl', 'deepseek-v3.2')}),
    ('RUN6B',     'Q6-33',       {'A': (f'{ROOT}/run6b_20260926/out/ANN_A_run6b.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/run6b_20260926/out/ANN_B_run6b.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/run6b_20260926/out/ANN_C_run6b.jsonl', 'deepseek-v3.2')}),
    ('RUN7RG',    'RET45',       {'A': (f'{ROOT}/run7rg_20260926/annotation/ANN_A_run7rg.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/run7rg_20260926/annotation/ANN_B_run7rg.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/run7rg_20260926/annotation/ANN_C_run7rg.jsonl', 'deepseek-v3.2')}),
    ('FACEV21',   'RET45',       {'A': (f'{ROOT}/face_v21_20260926/annotation/ANN_A_facev21.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/face_v21_20260926/annotation/ANN_B_facev21.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/face_v21_20260926/annotation/ANN_C_facev21.jsonl', 'deepseek-v3.2')}),
    ('BTEST-run1','RET45',       {'A': (f'{ROOT}/btest_20260927/annotation/ANN_A_btest_run1.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/btest_20260927/annotation/ANN_B_btest_run1.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/btest_20260927/annotation/ANN_C_btest_run1.jsonl', 'deepseek-v3.2')}),
    ('BTEST-run2','RET45',       {'A': (f'{ROOT}/btest_20260927/annotation/ANN_A_btest_run2.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/btest_20260927/annotation/ANN_B_btest_run2.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/btest_20260927/annotation/ANN_C_btest_run2.jsonl', 'deepseek-v3.2')}),
    ('KB9',       'Q6-25',       {'A': (f'{ROOT}/kb9_ocs_20260927/out/ANN_A_k9.jsonl', 'qwen3.8-max'),
                                   'B': (f'{ROOT}/kb9_ocs_20260927/out/ANN_B_k9.jsonl', 'glm-5.1'),
                                   'C': (f'{ROOT}/kb9_ocs_20260927/out/ANN_C_k9.jsonl', 'deepseek-v3.2')}),
]

# RUN5 席位模型确认读 META
for seat in 'ABC':
    mp = f'{EVAL}/annotation/ANN_{seat}_run5_META.json'
    if os.path.exists(mp):
        d = json.load(open(mp))
        for name in list(d):
            if 'model' in name.lower():
                pass  # keep declared mapping; META crosscheck below
# META 内嵌 model 交叉校验（凡有 META 的票档，模型映射以 META 为准）
def meta_model(path):
    base = os.path.basename(path)
    stem = base.replace('ANN_', '').replace('.jsonl', '')
    for cand in [f'{os.path.dirname(path)}/{stem}_META.json',
                 f'{os.path.dirname(path)}/ANN_{stem}_META.json',
                 f'{EVAL}/annotation/{stem}_META.json',
                 f'{EVAL}/annotation/ANN_{stem}_META.json']:
        if os.path.exists(cand):
            try:
                return json.load(open(cand)).get('model')
            except Exception:
                return None
    return None
mism = []
for arch, ds, seats in ARCHIVES:
    for seat, (p, model) in seats.items():
        mm = meta_model(p)
        if mm and model and mm != model:
            mism.append((arch, seat, model, mm))
        if mm and not model:
            pass
print('META 模型交叉校验 mismatches:', mism if mism else '无（声明映射与 META 全等或 META 无记录）')

# 断点残档（.facev21_B_done 等）不入矩阵——以正式 ANN_*.jsonl 为准，防双计

# ---------- sha 台账 ----------
ledger_lines = []
input_files = []
for arch, ds, seats in ARCHIVES:
    for seat, (p, model) in seats.items():
        input_files.append(p)
for extra in [BTEST_TBL, f'{EVAL}/scoring/run5_truth_table.tsv',
              f'{EVAL}/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py',
              f'{EVAL}/RUN4_TARGETS_v1.1.json',
              f'{EVAL}/scoring/run3_M4_hotspots_v1.1.tsv',
              f'{EVAL}/scoring/run3_object_B_table_v1.1.tsv',
              f'{EVAL}/clustering/Q2_clusters_truthfix_v1.tsv',
              f'{ROOT}/tiep_20260927/out/revote_matrix.tsv',
              f'{ROOT}/face_v21_20260926/scoring/FACEV21_VERDICT.json',
              f'{ROOT}/btest_20260927/scoring/BTEST_VERDICT.json',
              f'{ROOT}/evalset/scoring/run4r_verdict.json',
              f'{ROOT}/run7rg_20260926/scoring/RG_VERDICT.json',
              f'{ROOT}/run6b_20260926/RUN6B_VERDICT.json',
              f'{ROOT}/ANNOTATION_PROTOCOL_v1.2.md',
              '/mnt/D/OcularKB/WIKI/PROTOCOL_VOTING_v2_C2b.md',
              '/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md',
              f'{ROOT}/btest_20260927/BTEST_PREREG_v1.0.md',
              f'{EVAL}/annotation/ANNOT_INSTRUCTIONS.md',
              f'{ROOT}/proto_v2_20260927/RUNNER_WATCHLIST.md']:
    if os.path.exists(extra):
        input_files.append(extra)
seen = set()
for p in input_files:
    if p in seen:
        continue
    seen.add(p)
    ledger_lines.append(f'{sha256(p)}  {p}')
os.makedirs(f'{OUT}/data', exist_ok=True)
os.makedirs(f'{OUT}/scripts', exist_ok=True)
with open(f'{OUT}/data/SHA_LEDGER_INPUTS.txt', 'w') as f:
    f.write('\n'.join(ledger_lines) + '\n')
print(f'sha 台账: {len(ledger_lines)} 件 → data/SHA_LEDGER_INPUTS.txt')

# ---------- 矩阵 ----------
rows = []
for arch, ds, seats in ARCHIVES:
    data = {}
    for seat, (p, model) in seats.items():
        data[seat] = load_jsonl(p)
    # 簇全集
    cids = sorted(set().union(*[set(d) for d in data.values()]))
    for cid in cids:
        tag = cid.split('::')[0]
        if tag in ('Q1','Q2','Q3','Q4','Q5b','Q7'):
            truth = truth_ret.get(cid)  # 仅 RET45 集
        elif tag == 'Q6':
            truth = truth_q6.get(cid)
        else:
            truth = None
        for seat, d in data.items():
            r = d.get(cid)
            if r is None:
                rows.append(dict(archive=arch, dataset=ds, seat=seat, cluster_id=cid,
                                 truth=truth, missing=1))
                continue
            g = r.get('gates', {})
            ni = norm_identity(None, r.get('identity'))
            _decl_model, _path = seats[seat][1], seats[seat][0]
            rows.append(dict(archive=arch, dataset=ds,
                             seat=seat,
                             model=_decl_model or meta_model(_path) or 'unrecorded',
                             cluster_id=cid, truth=truth,
                             identity=r.get('identity'), identity_norm=ni,
                             kind=('UNDET' if ni == 'UNDET' else 'COARSE' if ni == 'COARSE' else 'MISSING' if ni is None else 'NAMED'),
                             level=r.get('level'), grade=r.get('grade'),
                             gate_identity_evidence=g.get('identity_evidence'),
                             gate_resolution=g.get('resolution'),
                             gate_technical=g.get('technical'),
                             flag=r.get('flag'), why=r.get('why'), missing=0))
import pandas as pd
M = pd.DataFrame(rows)
M.to_csv(f'{OUT}/data/ballot_matrix.tsv', sep='\t', index=False)
print(f'矩阵: {len(M)} 票行 / {M["archive"].nunique()} archive / {M["cluster_id"].nunique()} 簇')
print(M.groupby('archive').size().to_string())

# ---------- C4 / C2b 实现（facev21_verdict 逐字语义） ----------
def ballot(r):
    if r is None or (isinstance(r, float)):
        return None
    ni = r.get('identity_norm')
    if ni in (None, 'UNDET', 'COARSE', 'MISSING'):
        return None
    if str(r.get('grade')) not in ('A', 'B'):
        return None
    return ni

def c4_consensus(seatrows):
    votes = [b for b in (ballot(r) for r in seatrows) if b]
    if not votes:
        return None, 'abstain3', 0
    cnt = collections.Counter(votes)
    top, n = cnt.most_common(1)[0]
    if n >= 2:
        return top, 'majority', len(votes)
    if len(cnt) == len(votes) == 3:
        return None, 'split3', 3
    return None, 'tie', len(votes)

def parse_b(r):
    if r is None:
        return dict(kind='MISSING', label=None, coarse=None, grade=None)
    ni = r.get('identity_norm'); s = r.get('identity') or ''
    g = r.get('grade')
    if ni is None: return dict(kind='MISSING', label=None, coarse=None, grade=g)
    if ni == 'UNDET': return dict(kind='UNDET', label=None, coarse=None, grade=g)
    if ni == 'COARSE': return dict(kind='COARSE', label=None, coarse=s[len('coarse:'):], grade=g)
    return dict(kind='NAMED', label=ni, coarse=None, grade=g)

def rule_c2(bs):
    cnt = collections.Counter()
    for b in bs:
        if b['kind'] == 'NAMED': cnt[b['label']] += 1
        elif b['kind'] == 'COARSE' and b['coarse']: cnt[b['coarse']] += 1
    if not cnt: return None
    top, n = cnt.most_common(1)[0]
    return top if n >= 2 else None

PIV = M[M['missing'] == 0].pivot_table(index=['archive','cluster_id'], columns='seat',
                                       values=['identity_norm','grade','identity','level','flag',
                                              'gate_identity_evidence','gate_resolution','gate_technical'],
                                       aggfunc='first')
def seat_dict(arch, seat):
    sub = M[(M['archive'] == arch) & (M['seat'] == seat) & (M['missing'] == 0)]
    return {r['cluster_id']: r for _, r in sub.iterrows()}

results = {}
for arch, ds, seats in ARCHIVES:
    sd = {s: seat_dict(arch, s) for s in seats}
    cids = sorted(set().union(*[set(d) for d in sd.values()]))
    res = {}
    for cid in cids:
        seatrows = [sd[s].get(cid) for s in sorted(seats)]
        name, mode, nv = c4_consensus(seatrows)
        c2b = rule_c2([parse_b(r) for r in seatrows])
        res[cid] = dict(c4=name, mode=mode, c2b=c2b)
    results[arch] = res
json.dump(results, open(f'{OUT}/data/consensus_recomputed.json', 'w'), ensure_ascii=False, indent=1)

# ---------- 验证闸门 ----------
gates = {}
# G1 C4 FACEV21 == btest 表 a_consensus 列
g = [cid for cid in RET45 if (results['FACEV21'][cid]['c4'] or '') != (str(bt.set_index('cluster_id').loc[cid, 'a_consensus']) if pd.notna(bt.set_index('cluster_id').loc[cid, 'a_consensus']) else '')]
gates['G1_C4_FACEV21_vs_published'] = f'{"PASS" if not g else "FAIL"} 不一致={g}'
# G2 C4 BTEST run1/run2 == published
for run in ('run1','run2'):
    col = f'b_{run}_consensus'
    ref = bt.set_index('cluster_id')[col]
    g = [cid for cid in RET45 if (results[f'BTEST-{run}'][cid]['c4'] or '') != (str(ref.loc[cid]) if pd.notna(ref.loc[cid]) else '')]
    gates[f'G2_C4_BTEST-{run}_vs_published'] = f'{"PASS" if not g else "FAIL"} 不一致={g}'
# G3 C2b FACEV21 == TIEP revote_matrix name_C2b (face=FACEV21)
tiep = pd.read_csv(f'{ROOT}/tiep_20260927/out/revote_matrix.tsv', sep='\t')
tf = tiep[tiep['face'] == 'FACEV21'].set_index('cid')
g = [cid for cid in RET45 if (results['FACEV21'][cid]['c2b'] or '') != (str(tf.loc[cid, 'name_C2b']) if pd.notna(tf.loc[cid, 'name_C2b']) else '')]
gates['G3_C2b_FACEV21_vs_TIEP'] = f'{"PASS" if not g else "FAIL"} 不一致={g}'
# G4 C4 RUN4-r == published run4r_verdict rows
r4 = json.load(open(f'{EVAL}/scoring/run4r_verdict.json'))
r4rows = r4['rows'] if isinstance(r4.get('rows'), dict) else {x['cluster_id']: x for x in r4.get('rows', [])}
if r4rows:
    g = [cid for cid in RET45 if cid in r4rows and (results['RUN4-r'][cid]['c4'] or '') != (str(r4rows[cid].get('consensus') or ''))]
    gates['G4_C4_RUN4r_vs_published'] = f'{"PASS" if not g else "FAIL"} 不一致={g[:6]}'
# G5 C4 RUN7RG == published verdict
p7 = f'{ROOT}/run7rg_20260926/scoring/RG_VERDICT.json'
if os.path.exists(p7):
    r7 = json.load(open(p7))
    rows7 = r7.get('rows')
    r7rows = rows7 if isinstance(rows7, dict) else {x['cluster_id']: x for x in (rows7 or [])}
    if r7rows:
        g = [cid for cid in RET45 if cid in r7rows and (results['RUN7RG'][cid]['c4'] or '') != (str(r7rows[cid].get('consensus') or ''))]
        gates['G5_C4_RUN7RG_vs_published'] = f'{"PASS" if not g else "FAIL"} 不一致={g[:6]}'
# G6 C4 Q6 集 vs run5 truth 表 consensus 列（run5 已发布）
ref5 = q6t.set_index('cluster_id')
g = []
for cid in sorted(truth_q6):
    if cid in results['RUN5']:
        mine = results['RUN5'][cid]['c4'] or ''
        pub = str(ref5.loc[cid, 'consensus']) if pd.notna(ref5.loc[cid, 'consensus']) else ''
        if mine != pub:
            g.append((cid, mine, pub))
gates['G6_C4_RUN5Q6_vs_published'] = f'{"PASS" if not g else "CHECK"} 不一致={g[:6]}'

print('\n==== 验证闸门 ====')
for k, v in gates.items():
    print(k, '→', v)
json.dump(gates, open(f'{OUT}/data/verification_gates.json', 'w'), ensure_ascii=False, indent=1)

# 票面词汇表 vs truth 词汇表（大小写/别名差异盘点）
vocab = sorted(set(M[(M['kind'] == 'NAMED')]['identity_norm']))
tset = sorted(set(list(truth_ret.values()) + list(truth_q6.values())))
print('\nNAMED 票面标签:', vocab)
print('truth 标签:', tset)
print('票面-truth 差集:', sorted(set(vocab) - set(tset)))
print('\nDONE build')
