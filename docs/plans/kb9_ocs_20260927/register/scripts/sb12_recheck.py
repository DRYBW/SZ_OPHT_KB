#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K1 v3: 数据驱动选基（只读 agg_kb6b_v1.npz；KB7-W2 冻结常量，PREREG §1.2）。
目标(author 池): Melanocyte←Melanocytes; Schwann←Schwann_M∪Schwann_N; Conj_suprabasal←Conj_suprabasal(KB7 阴性复核)。
火灾域: GROUP 其余组 + 同父兄弟 author 亚型。pool>=500 否决格; <500 记录不否决。
donor cons(逐邻组, 可算域=两侧均 MIND>=10 的 donor; ok=目标 CPM>=DR×邻组 CPM; 要求 min cons>=CONS_T)。
键语义照 KB7: da_keys=donorG*NA+author, dg_keys=donorG*NG+group, donorG=study*ND+donor。
输出 out/kb9_fire_audit.tsv 全格 + out/kb9_term_candidates.json + out/kb9_donor_cons.tsv
"""
import numpy as np, json, scipy.sparse as sp

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927/register/recheck_run'
AGG = '/mnt/D/EyeKB/plans/kb6b_face_20260925/out/agg_kb6b_v1.npz'
CPM_FLOOR, LFC_T, CONS_T, DR, MIND = 5.0, 1.0, 0.75, 2.0, 10
EPS = 1e-9; TOPN = 12; MINPOOL = 500

z = np.load(AGG, allow_pickle=True)
offs = json.loads(str(z['offs'])); cats = json.loads(str(z['layer_cats']))
grp = list(cats['GROUP']); auth = [str(a) for a in cats['AUTHOR']]
donors = list(cats['DONOR']); ND = len(donors)
SUM = z['SUM'].astype(np.float64); TOT = z['TOT'].astype(np.float64)
NC = z['NC'].astype(np.float64); DET = z['DET'].astype(np.float64)
SYM = z['symbol'].astype(str); FT = z['ftype'].astype(str)
NG, NA = len(grp), len(auth)
da_keys = z['da_keys'].astype(np.int64); dg_keys = z['dg_keys'].astype(np.int64)
da_d, da_a = da_keys // NA, da_keys % NA
dg_d, dg_g = dg_keys // NG, dg_keys % NG
maxD = int(max(da_d.max(), dg_d.max())) + 1

print('GROUP:', grp)
print('pools G:', dict(zip(grp, NC[:NG].astype(int))))
print('pools A:', dict(zip(auth, NC[offs['AUTHOR'][0]:offs['AUTHOR'][0] + NA].astype(int))))

usym = np.unique(SYM)
inv = np.searchsorted(usym, SYM)
Msym = sp.csr_matrix((np.ones(SYM.size), (inv, np.arange(SYM.size))), shape=(usym.size, SYM.size))
SUMs = np.asarray(SUM @ Msym.T); DETs = np.asarray(DET @ Msym.T)
def sl(name):
    o_, n_ = offs[name]; return slice(o_, o_ + n_)
CPMg_all = SUMs[sl('GROUP')] / np.maximum(TOT[sl('GROUP')][:, None], EPS) * 1e6
CPMa_all = SUMs[sl('AUTHOR')] / np.maximum(TOT[sl('AUTHOR')][:, None], EPS) * 1e6
NCg = NC[sl('GROUP')]; NCa = NC[sl('AUTHOR')]
detG = DETs[sl('GROUP')] / np.maximum(NCg[:, None], 1)
detA = DETs[sl('AUTHOR')] / np.maximum(NCa[:, None], 1)
SUMda = np.asarray(SUM[sl('DONORxAUTHOR')] @ Msym.T); TOTda = TOT[sl('DONORxAUTHOR')]; NCda_ = NC[sl('DONORxAUTHOR')]
SUMdg = np.asarray(SUM[sl('DONORxGROUP')] @ Msym.T); TOTdg = TOT[sl('DONORxGROUP')]; NCdg_ = NC[sl('DONORxGROUP')]
# donor 级稠密索引
da_of = {}
for k in range(len(da_a)):
    da_of.setdefault((int(da_d[k]), int(da_a[k])), k)
dg_of = {}
for k in range(len(dg_g)):
    dg_of.setdefault((int(dg_d[k]), int(dg_g[k])), k)

pc_any = {}
for s, ft in zip(SYM, FT):
    pc_any[s] = pc_any.get(s, False) or (ft == 'protein_coding')

# author→GROUP 父归属（KB7 细胞数对齐法）
Ma = np.zeros((NA, maxD)); Mgc = np.zeros((NG, maxD))
np.add.at(Ma, (da_a, da_d), NCda_); np.add.at(Mgc, (dg_g, dg_d), NCdg_)
score = Ma @ Mgc.T
auth2grp = [int(score[a].argmax()) for a in range(NA)]

TARGETS = {'Conj_suprabasal': ['Conj_suprabasal']}
# 父组冻结指定（细胞数实证: author Melanocytes 7209=GROUP Melanocytes 7209; Schwann_M+N 6059=GROUP Schwann;
# Conj_suprabasal→Epithelium 照 KB7 归属断言。score-argmax 启发式受大类支配偏置, 仅用于无同名组时参考）
FROZEN_PARENTS = {'Melanocyte': {'Melanocytes'}, 'Schwann': {'Schwann'}, 'Conj_suprabasal': {'Epithelium'},
  'Limbus_Fib': {'Fibroblast-stroma'}, 'LimScl_C1': {'Fibroblast-stroma'}, 'LimScl_C2': {'Fibroblast-stroma'}, 'Sclera_Fib': {'Fibroblast-stroma'}}

def pool_cpm(rows):
    w = NCa[rows]
    return (CPMa_all[rows] * w[:, None]).sum(0) / w.sum(), (detA[rows] * w[:, None]).sum(0) / w.sum(), w.sum()

def donor_stats(term, rows, si, nbrG, sibs_sel):
    """cons 精算域照 KB7: pool>=5000 的邻组 + pool 最大 3 兄弟亚型; donor 双侧 MIND>=10; ok=目标>=DR×邻"""
    min_cons, min_valid = None, None
    per = {}
    for nm, gi in nbrG:
        if NCg[gi] < 5000:
            continue
        ok = tot = 0
        for d in np.unique(dg_d):
            ks = [da_of.get((d, r)) for r in rows]
            ks = [k for k in ks if k is not None]
            if not ks:
                continue
            nc_t = sum(NCda_[k] for k in ks)
            cpm_t = sum(SUMda[k, si] for k in ks) / max(sum(TOTda[k] for k in ks), EPS)
            kg = dg_of.get((int(d), gi))
            if kg is None or nc_t < MIND or NCdg_[kg] < MIND:
                continue
            tot += 1
            cpm_n = SUMdg[kg, si] / max(TOTdg[kg], EPS)
            if cpm_t >= DR * cpm_n + 0.0:
                ok += 1
        cons = ok / tot if tot else None
        per[nm] = (cons, tot)
        if tot:
            if min_cons is None or cons < min_cons:
                min_cons, min_valid = cons, tot
    for nm, ai in sibs_sel:
        ok = tot = 0
        for d in np.unique(da_d):
            ks = [da_of.get((d, r)) for r in rows]
            ks = [k for k in ks if k is not None]
            kb_ = da_of.get((int(d), ai))
            if not ks or kb_ is None:
                continue
            nc_t = sum(NCda_[k] for k in ks)
            cpm_t = sum(SUMda[k, si] for k in ks) / max(sum(TOTda[k] for k in ks), EPS)
            if nc_t < MIND or NCda_[kb_] < MIND:
                continue
            tot += 1
            cpm_n = SUMda[kb_, si] / max(TOTda[kb_], EPS)
            if cpm_t >= DR * cpm_n + 0.0:
                ok += 1
        cons = ok / tot if tot else None
        per[nm] = (cons, tot)
        if tot:
            if min_cons is None or cons < min_cons:
                min_cons, min_valid = cons, tot
    return min_cons, min_valid, per

results = {}
consf = open(f'{ROOT}/out/kb9_donor_cons.tsv', 'w')
consf.write('term\tgene\tneighbor\tcons\tdonor_valid\n')
with open(f'{ROOT}/out/kb9_fire_audit.tsv', 'w') as fout:
    fout.write('term\tgene\tcpm_target\tdet_target\tpool_target\tneighbor\tnbr_level\tpool_nbr\tcpm_nbr\tlfc\tdonor_cons\tdonor_valid\tnbr_ok\n')
    for term, tas in TARGETS.items():
        rows = [auth.index(a) for a in tas]
        cpm_t, det_t, pool_t = pool_cpm(rows)
        parents = FROZEN_PARENTS[term]
        nbrG = [(g, grp.index(g)) for g in grp if g not in parents]
        nbrG_veto = [(g, i) for g, i in nbrG if NCg[i] >= MINPOOL]   # KB7: <500 记录不否决
        sibs = [(a, auth.index(a)) for a in auth if grp[auth2grp[auth.index(a)]] in parents and a not in tas]
        sibs_veto = [(a, i) for a, i in sibs if NCa[i] >= MINPOOL]
        cand = []
        for si in range(usym.size):
            g = str(usym[si])
            if not g or not pc_any.get(g, False):
                continue
            if cpm_t[si] < CPM_FLOOR or det_t[si] < 0.25:
                continue
            lfcs = [float(np.log2((cpm_t[si] + 1) / (CPMg_all[gi, si] + 1))) for _, gi in nbrG_veto]
            lfcs += [float(np.log2((cpm_t[si] + 1) / (CPMa_all[ai, si] + 1))) for _, ai in sibs_veto]
            if min(lfcs) >= LFC_T:
                cand.append((g, si, min(lfcs)))
        cand.sort(key=lambda x: -x[2])
        print(f'{term}: pool={int(pool_t)} parents={parents} lfc_pass={len(cand)}')
        results[term] = {'pool_cells': int(pool_t), 'parents': sorted(parents), 'lfc_fire_pass_genes': [], 'core': []}
        for g, si, mlfc in cand[:60]:  # 全量登记 lfc 过筛基因(含 cons 失败者, 诚实)
            sibs_sel = sorted([(a, i) for a, i in sibs if NCa[i] >= 500], key=lambda x: -NCa[x[1]])[:3]
            mc, mv, per = donor_stats(term, rows, si, nbrG, sibs_sel)
            cp = mc is not None and mc >= CONS_T
            rec = {'gene': g, 'cpm': round(float(cpm_t[si]), 1), 'det': round(float(det_t[si]), 3),
                   'min_lfc_fire': round(mlfc, 3), 'min_donor_cons': round(mc, 3) if mc is not None else None,
                   'donor_valid': mv, 'cons_pass': bool(cp)}
            results[term]['lfc_fire_pass_genes'].append(rec)
            if cp:
                results[term]['core'].append(g)
            for nm, gg in per.items():
                consf.write(f"{term}\t{g}\t{nm}\t{gg[0] if gg[0] is None else round(gg[0],3)}\t{gg[1]}\n")
            if g in [c[0] for c in cand[:TOPN]] or cp:
                for nm, gi in nbrG:
                    lfc = float(np.log2((cpm_t[si] + 1) / (CPMg_all[gi, si] + 1)))
                    veto = 'ok' if lfc >= LFC_T else ('FIRE' if NCg[gi] >= MINPOOL else 'small-record')
                    fout.write(f"{term}\t{g}\t{cpm_t[si]:.1f}\t{det_t[si]:.3f}\t{int(pool_t)}\t{nm}\tgroup\t{int(NCg[gi])}\t{CPMg_all[gi,si]:.2f}\t{lfc:.3f}\t{per.get(nm, ('', ''))[0] if per.get(nm) and per[nm][0] is not None else ''}\t{per.get(nm, ('', ''))[1] if per.get(nm) else ''}\t{veto}\n")
                for nm, ai in sibs:
                    lfc = float(np.log2((cpm_t[si] + 1) / (CPMa_all[ai, si] + 1)))
                    veto = 'ok' if lfc >= LFC_T else ('FIRE' if NCa[ai] >= MINPOOL else 'small-record')
                    fout.write(f"{term}\t{g}\t{cpm_t[si]:.1f}\t{det_t[si]:.3f}\t{int(pool_t)}\t{nm}\tauthor\t{int(NCa[ai])}\t{CPMa_all[ai,si]:.2f}\t{lfc:.3f}\t\t\t{veto}\n")
consf.close()
results['meta'] = {'constants': {'CPM_FLOOR': CPM_FLOOR, 'LFC_T': LFC_T, 'CONS_T': CONS_T, 'DR': DR, 'MIND': MIND, 'TOPN': TOPN, 'MINPOOL': MINPOOL},
                   'agg': AGG, 'agg_prereg_sha': str(z['prereg_sha']), 'agg_h5_sha': str(z['h5_sha'])}
json.dump(results, open(f'{ROOT}/out/kb9_term_candidates.json', 'w'), ensure_ascii=False, indent=1)
for t in TARGETS:
    print(t, 'core genes:', results[t]['core'][:20], f"(lfc pass {len(results[t]['lfc_fire_pass_genes'])})")
print('DONE')
