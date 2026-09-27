#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E3 主管线：S1 复刻→G0/G1 复现闸→两臂弃权带检验(R1/R2)→改良臂叠加层(R3)→判读落表。
判据=E3_PREREG_v1.0.md (sha 23105aff) + e3_rules.json (sha f00b3e7f)，2026-09-27 09:14:11 落纸先于跑数。
不 import 生产码；席位票全读存档；零 LLM、零网络、零生产写。G0/G1 任一失败 exit 2 禁出结论。"""
import json, csv, os, sys, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e2common import (load_panel, gene_evidence, keep, canon, load_digest_rows,
                      top10_of, lit_of_cluster, MEMBERS, BSRC)

ROOT = '/mnt/D/EyeKB/plans/e3_rescue_20260927'
EVR = '/mnt/D/EyeKB/plans/evalset'
R1D = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'
R2D = '/mnt/D/EyeKB/plans/e2_decontam_20260926'
F21 = '/mnt/D/EyeKB/plans/face_v21_20260926'
RET_MEMBERS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7']
M = json.load(open(f'{R1D}/e1_class_map.json'))['map']
E2_OBS = {'F-RET': (85, 48, 41), 'F-3SEAT': (14, 7, 5)}  # G1 逐值断言目标（E2 冻结 observation_addendum）

LOG = []
def P(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s, flush=True)

def bail(code, msg):
    P('REPLICATION_GATE_FAIL:', msg)
    open(f'{ROOT}/logs/pipeline_log.txt', 'w').write('\n'.join(LOG) + f'\nran {datetime.datetime.now()} EXIT={code}\n')
    sys.exit(code)

def mapped_label(c, panel):
    e = M.get(c)
    if not e:
        return None
    v = e.get(panel)
    if v is None:
        return None
    if v.startswith('AMBIG['):
        return ('AMBIG', set(x.strip() for x in v[6:-1].split(',')))
    return v

def panel_of(cid):
    return 'ocular' if cid.startswith('Q6') else 'retina'

# ---------- STEP 1: S1 打分复刻（e2_score.py 同构循环，仅 S1 变体） ----------
rows, dbs = load_panel()
P(f'ON panel rows={len(rows)}')
ev_cache = {}
for r in rows:
    for g in r['genes']:
        if (r['lib'], r['cls'], g) not in ev_cache:
            ev_cache[(r['lib'], r['cls'], g)] = gene_evidence(dbs, r['lib'], r['cls'], g)

dig = load_digest_rows()
assert len(dig) == 290, f'digest rows {len(dig)} != 290'
per = defaultdict(list)  # cid -> [cand dict] in frozen write order
out = open(f'{ROOT}/data/e3_scores_S1_replica.tsv', 'w')
out.write('\t'.join(['cluster_id', 'member', 'n_cells', 'cand_canon', 'n', 'shared_genes',
                     'alias_rows', 'lit_n', 'lit_pmids', 'lit_n_raw', 'n_raw_of_row']) + '\n')
for r in dig:
    cid, mem = r['cluster_id'], r['member']
    top = top10_of(r)
    raw_lit = lit_of_cluster(r)
    bsrc = BSRC.get(mem, set())
    scored = []
    for row in rows:
        kept = [g for g in row['genes'] if keep(ev_cache[(row['lib'], row['cls'], g)], row['lib'], mem, 'S1')]
        sg = [g for g in top if g in set(kept)]
        if sg:
            scored.append((row, len(sg), sg))
    ranked = sorted(scored, key=lambda t: -t[1])  # 稳定排序=平票保注册序
    merged = {}
    for row, n, sg in ranked:
        c = canon(row['key'])
        if c not in merged or n > merged[c]['n']:
            merged[c] = {'n': n, 'shared_genes': sg, 'alias': [row['key']]}
        else:
            merged[c]['alias'].append(row['key'])
    for c, pm in raw_lit.items():
        if c not in merged and pm:
            merged[c] = {'n': 0, 'shared_genes': [], 'alias': [c]}
    for c, d in merged.items():
        pm = raw_lit.get(c, set())
        d['lit_n_raw'] = len(pm); d['lit_pm_raw'] = sorted(pm)
        d['lit_n'] = len(pm - bsrc); d['lit_pm'] = sorted(pm - bsrc)
    for c, d in sorted(merged.items(), key=lambda kv: (-kv[1]['n'], kv[0])):
        rec = {'canon': c, 'n': d['n'], 'genes': ';'.join(d['shared_genes']),
               'alias': ';'.join(d['alias']), 'lit_n': d['lit_n'], 'lit_pm': ';'.join(d['lit_pm']),
               'lit_n_raw': d['lit_n_raw']}
        per[cid].append(rec)
        out.write('\t'.join([cid, mem, str(r.get('n_cells', '')), c, str(d['n']),
                             ';'.join(d['shared_genes']), ';'.join(d['alias']),
                             str(d['lit_n']), ';'.join(d['lit_pm']), str(d['lit_n_raw']), '']) + '\n')
out.close()
P(f'replica score rows={sum(len(v) for v in per.values())} clusters={len(per)}')

# ---------- STEP 2: G0 复现闸（对 E2 冻结 S1 表逐值） ----------
frozen = defaultdict(dict)
nf = 0
with open(f'{R2D}/data/e2_scores_S1.tsv') as f:
    for i, l in enumerate(f):
        if i == 0:
            continue
        fl = l.rstrip('\n').split('\t'); nf += 1
        frozen[fl[0]][fl[3]] = {'n': int(fl[4]), 'genes': set(x for x in fl[5].split(';') if x),
                                'alias': fl[6], 'lit_n': int(fl[7]), 'lit_pm': fl[8], 'lit_n_raw': int(fl[9])}
diffs = []
nr = 0
for cid, cands in per.items():
    for rc in cands:
        nr += 1
        fr = frozen.get(cid, {}).get(rc['canon'])
        if fr is None:
            diffs.append(f'{cid}/{rc["canon"]}: replica-only'); continue
        if rc['n'] != fr['n'] or rc['lit_n'] != fr['lit_n'] or rc['lit_n_raw'] != fr['lit_n_raw'] \
           or set(x for x in rc['genes'].split(';') if x) != fr['genes'] \
           or rc['lit_pm'] != fr['lit_pm'] or rc['alias'] != fr['alias']:
            diffs.append(f'{cid}/{rc["canon"]}: value diff')
for cid in frozen:
    for c in frozen[cid]:
        if not any(x['canon'] == c for x in per.get(cid, [])):
            diffs.append(f'{cid}/{c}: frozen-only')
P(f'G0: frozen_rows={nf} replica_rows={nr} diffs={len(diffs)}')
if diffs or nf != nr:
    bail(2, f'G0 failed ({len(diffs)} diffs), e.g. ' + '; '.join(diffs[:5]))
open(f'{ROOT}/out/e3_G0_replica_check.tsv', 'w').write(
    'check\tvalue\nfrozen_rows\t%d\nreplica_rows\t%d\ndiffs\t0\nresult\tPASS\n' % (nf, nr))

# ---------- STEP 3: 面/带构建（存档票直读） ----------
rows3 = list(csv.DictReader(open(f'{EVR}/scoring/run3_object_B_table_v1.1.tsv'), delimiter='\t'))
r3 = {x['cluster_id']: x for x in rows3}
def ab_consensus(x):
    a, b = x['ann_A'], x['ann_B']
    if a and b and a == b and not a.startswith(('undetermined', 'coarse:')):
        return a
    return None
flip = list(csv.DictReader(open(f'{F21}/out/per_cluster_flip_table_facev21.tsv'), delimiter='\t'))
def v21_consensus(x):
    return x['v21_consensus'] if x['v21_mode'] == 'majority' and x['v21_consensus'] and x['v21_consensus'] != 'nan' else None
run5 = list(csv.DictReader(open(f'{EVR}/scoring/run5_truth_table.tsv'), delimiter='\t'))
r5 = {x['cluster_id']: x for x in run5}
def r5_consensus(x):
    c = x['consensus']
    return c if c and c != 'nan' else None

f_ret = [x['cluster_id'] for x in rows3 if x['truth'] and x['member'] in RET_MEMBERS]
flip_ret = {x['cluster_id']: x for x in flip if x['truth'] and x['truth'] != 'nan'
            and x['cluster_id'].split('::')[0] in RET_MEMBERS}
f_ocs = [x['cluster_id'] for x in run5]
f3 = list(flip_ret) + list(f_ocs)
truth_of = {}
for cid in set(f_ret) | set(f_ocs) | set(flip_ret):
    truth_of[cid] = (r3[cid]['truth'] if cid in r3 and r3[cid]['truth']
                     else (r5[cid]['truth'] if cid in r5 and r5[cid]['truth'] else None))
for x in flip:
    if x['cluster_id'] in flip_ret:
        truth_of[x['cluster_id']] = x['truth']
member_of = {cid: cid.split('::')[0] for cid in truth_of}

def cons_of(cid, face):
    if face == 'F-RET':
        return ab_consensus(r3[cid]) if cid in r3 else None
    if cid in flip_ret:
        return v21_consensus(flip_ret[cid])
    if cid in r5:
        return r5_consensus(r5[cid])
    return None
band_ret = [c for c in f_ret if truth_of.get(c) and not cons_of(c, 'F-RET')]
band_f3 = [c for c in f3 if truth_of.get(c) and not cons_of(c, 'F-3SEAT')]
P(f'faces: F-RET={len(f_ret)} band={len(band_ret)} | F-3SEAT={len(f3)} (flip={len(flip_ret)}+run5={len(f_ocs)}) band={len(band_f3)}')

# ---------- STEP 4: 两臂定义 ----------
def incumbent_named(cid):
    cands = per.get(cid) or []
    if not cands:
        return None, 'no_candidate', None
    rank = sorted(cands, key=lambda c: (-c['n'], c['canon']))
    top = rank[0]
    lab = mapped_label(top['canon'], panel_of(cid))
    if isinstance(lab, str):
        return lab, 'named', top
    return None, ('AMBIG' if lab is not None else 'nomap'), top

def improved_named(cid):
    if member_of[cid] == 'Q7':
        return None, 'Q7_stripped', None
    cands = per.get(cid) or []
    if not cands:
        return None, 'no_candidate', None
    rank = sorted(cands, key=lambda c: (-c['n'], c['canon']))
    maxn = rank[0]['n']
    layer = [c for c in rank if c['n'] == maxn]
    if maxn <= 1:
        return None, f'weak_hit(maxn={maxn})', rank[0]
    if len(layer) >= 2:
        return None, f'conflict(n={maxn},k={len(layer)})', layer[0]
    top = layer[0]
    lab = mapped_label(top['canon'], panel_of(cid))
    if isinstance(lab, str):
        return lab, 'named', top
    return None, ('AMBIG' if lab is not None else 'nomap'), top

def band_table(cids, fname):
    lines = ['\t'.join(['cluster_id', 'member', 'truth', 'arm', 'named_label', 'top1_canon',
                        'n_shared', 'shared_genes', 'lit_n', 'cand_count', 'abstain_reason', 'correct'])]
    stats = {}
    for armf, armn in ((incumbent_named, 'incumbent'), (improved_named, 'improved')):
        named = correct = 0
        for cid in cids:
            t = truth_of[cid]
            lab, reason, top = armf(cid)
            cc = len(per.get(cid) or [])
            if lab:
                named += 1
                correct += 1 if lab == t else 0
            lines.append('\t'.join([cid, member_of[cid], t, armn, lab or '',
                                    top['canon'] if top else '', str(top['n']) if top else '',
                                    top['genes'] if top else '', str(top['lit_n']) if top else '',
                                    str(cc), reason, '1' if lab and lab == t else ('0' if lab else '')]))
        stats[armn] = dict(band=len(cids), named=named, correct=correct,
                           precision=round(100.0 * correct / named, 2) if named else None)
    open(f'{ROOT}/out/e3_band_rows_{fname}.tsv', 'w').write('\n'.join(lines) + '\n')
    return stats

st_ret = band_table(band_ret, 'FRET')
st_f3 = band_table(band_f3, 'F3SEAT')
P('F-RET arms:', json.dumps(st_ret, ensure_ascii=False))
P('F-3SEAT arms:', json.dumps(st_f3, ensure_ascii=False))

# G1：现役臂逐值==E2 冻结观察
for fname, s in (('F-RET', st_ret['incumbent']), ('F-3SEAT', st_f3['incumbent'])):
    eb, en, ec = E2_OBS[fname]
    if not (s['band'] == eb and s['named'] == en and s['correct'] == ec):
        bail(2, f'G1 failed on {fname}: replica=({s["band"]},{s["named"]},{s["correct"]}) e2_frozen=({eb},{en},{ec})')
P('G1 PASS: 现役臂带计数与 E2 observation_addendum 逐值一致')

# ---------- STEP 5: 门判读 ----------
i = st_ret['incumbent']
r1_prec = 100.0 * i['correct'] / i['named'] if i['named'] else 0.0
r1 = dict(named=i['named'], correct=i['correct'], precision_pct=round(r1_prec, 2),
          prec_ge_80=r1_prec >= 80.0, named_ge_40=i['named'] >= 40)
r1['PASS'] = r1['prec_ge_80'] and r1['named_ge_40']
j = st_f3['incumbent']
r2_prec = 100.0 * j['correct'] / j['named'] if j['named'] else 0.0
r2 = dict(named=j['named'], correct=j['correct'], precision_pct=round(r2_prec, 2),
          named_ge_15=j['named'] >= 15, prec_ge_70=r2_prec >= 70.0)
r2['PASS'] = r2['named_ge_15'] and r2['prec_ge_70']
P('R1:', json.dumps(r1)); P('R2:', json.dumps(r2))

# R3：改良臂精确率地板 + E1 §5 案例表状态
r3_face = {}
for fname, st in (('F-RET', st_ret), ('F-3SEAT', st_f3)):
    inc, imp = st['incumbent'], st['improved']
    if imp['named'] == 0:
        ok = False; pr = None
    else:
        pr = 100.0 * imp['correct'] / imp['named']
        ip = 100.0 * inc['correct'] / inc['named'] if inc['named'] else 0.0
        ok = pr >= ip - 1e-9
    r3_face[fname] = dict(inc_named=inc['named'], inc_prec=inc['precision'],
                          imp_named=imp['named'], imp_correct=imp['correct'],
                          imp_prec=round(pr, 2) if pr is not None else None,
                          floor_met=ok)
cases = list(csv.DictReader(open(f'{R1D}/out/e1_divergence_cases.tsv'), delimiter='\t'))
clines = ['\t'.join(['cluster_id', 'truth', 'e1_raw_top1', 'e1_raw_n', 'consensus',
                     'incumbent_S1_named', 'incumbent_hit', 'improved_named', 'improved_reason',
                     'status'])]
case_rows = []
for x in cases:
    cid = x['cluster_id']
    inc_lab, _, _ = incumbent_named(cid)
    imp_lab, imp_reason, _ = improved_named(cid)
    if inc_lab == x['truth']:
        status = 'incumbent_already_correct'
    elif imp_lab == x['truth']:
        status = 'repaired'
    elif imp_lab:
        status = f'not_repaired(still_wrong:{imp_lab})'
    else:
        status = f'not_repaired(abstained:{imp_reason})'
    case_rows.append(dict(cid=cid, truth=x['truth'], incumbent=inc_lab or '', improved=imp_lab or '', status=status))
    clines.append('\t'.join([cid, x['truth'], x['ev_top1'], x['n_shared'], x['consensus'],
                             inc_lab or '', '1' if inc_lab == x['truth'] else '0',
                             imp_lab or '', imp_reason, status]))
open(f'{ROOT}/out/e3_r3_cases.tsv', 'w').write('\n'.join(clines) + '\n')
q222 = [c for c in case_rows if c['cid'] == 'Q2::22'][0]
floor_all = all(v['floor_met'] for v in r3_face.values())
r3 = dict(face_floors=r3_face, floor_all_faces=floor_all,
          q2_22_status=q222['status'], cases_recorded=len(case_rows),
          PASS=floor_all)  # 案例条款=修复或如实记录，恒满足记录义务；地板=硬判据
P('R3:', json.dumps(r3, ensure_ascii=False))

# 判读矩阵行
if r1['PASS'] and r2['PASS']:
    line = '双面成立：辅助工具 F-RET+F-3SEAT 双过，SOP 草案交 PI 阅（不接线）'
elif r1['PASS']:
    line = '限视网膜面成立（R1 PASS/R2 FAIL）：SOP 标注泛化边界'
else:
    line = '观测数字未过正式化检验（R1 FAIL）：SOP 不产出，E2 观察性附加勘正注记（本卡目录侧登记）'
P('DECISION:', line)

# ---------- STEP 6: 两臂对比表 + metrics json ----------
cmp_lines = ['\t'.join(['face', 'arm', 'band_rows', 'named', 'correct', 'precision_pct'])]
for fname, st in (('F-RET', st_ret), ('F-3SEAT', st_f3)):
    for armn in ('incumbent', 'improved'):
        s = st[armn]
        cmp_lines.append('\t'.join([fname, armn, str(s['band']), str(s['named']), str(s['correct']),
                                    str(s['precision'] if s['precision'] is not None else 'NA')]))
open(f'{ROOT}/out/e3_arm_compare.tsv', 'w').write('\n'.join(cmp_lines) + '\n')

json.dump(dict(
    replication=dict(G0='PASS', G1='PASS', G2='see sha_ledger_POST_inputs.txt'),
    arms=dict(F_RET=st_ret, F_3SEAT=st_f3),
    gates=dict(R1=r1, R2=r2, R3=r3),
    decision_matrix_line=line,
    faces=dict(F_RET=len(f_ret), band_F_RET=len(band_ret), F_3SEAT=len(f3), band_F_3SEAT=len(band_f3)),
    tool_spec=dict(scoring='S1 decon ①top1 (e2_decon_rules sha 34928582)',
                   improved_overlays=['3A: no-op passthrough', 'Q7: strip ranking -> abstain',
                                      'C: weak(maxn<=1) no-name; strong-layer tie -> conflict no-name']),
), open(f'{ROOT}/out/e3_metrics.json', 'w'), ensure_ascii=False, indent=1)
open(f'{ROOT}/logs/pipeline_log.txt', 'w').write('\n'.join(LOG) + f'\nran {datetime.datetime.now()} EXIT=0\n')
print('E3_PIPELINE_DONE')
