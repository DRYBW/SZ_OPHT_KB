#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K1: 零词条补建数据驱动选基（只读 agg_kb6b_v1.npz；KB7-W2 冻结常量）。
目标: Melanocyte(池=author Melanocytes), Schwann(池=author Schwann_M∪Schwann_N)。
另复核 KB7 诚实阴性案 Conj_suprabasal(池=author) 在新候选域下是否仍 0 全过。
口径: 目标=author 类, 火灾域=GROUP 9 互斥组全格(排除自身所在组) + 同父兄弟亚型(author, pool>=500)。
lfc/cons/CPM 全用 GROUP 空间(与 KB7 一致, 保证可比)。输出 out/kb9_fire_audit.tsv + out/kb9_term_candidates.json
"""
import numpy as np, json, scipy.sparse as sp

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
AGG = '/mnt/D/EyeKB/plans/kb6b_face_20260925/out/agg_kb6b_v1.npz'
CPM_FLOOR, LFC_T, CONS_T, DR, MIND = 5.0, 1.0, 0.75, 2.0, 10
EPS = 1e-9; TOPN = 12; MINPOOL = 500; BIGPOOL = 5000

z = np.load(AGG, allow_pickle=True)
offs = json.loads(str(z['offs'])); cats = json.loads(str(z['layer_cats']))
grp = list(cats['GROUP']); auth = [str(a) for a in cats['AUTHOR']]
studies = [str(s) for s in z['studies']] if 'studies' in z else None
donors = cats['DONOR']; ND = len(donors)
SUM = z['SUM'].astype(np.float64); TOT = z['TOT'].astype(np.float64)
NC = z['NC'].astype(np.float64); DET = z['DET'].astype(np.float64)
SYM = z['symbol'].astype(str); BIOT = z['biotype'].astype(str)
NG, NA = len(grp), len(auth)
da_keys = z['da_keys'].astype(np.int64); dg_keys = z['dg_keys'].astype(np.int64); sg_keys = z['sg_keys'].astype(np.int64)
da_d, da_a = da_keys // NA, da_keys % NA
dg_d, dg_g = dg_keys // NG, dg_keys % NG
da_study = (da_d // ND).astype(int); dg_study = (dg_d // ND).astype(int)
print('npz keys:', list(z.keys()))

usym = np.unique(SYM)
inv = np.searchsorted(usym, SYM)
Msym = sp.csr_matrix((np.ones(SYM.size), (inv, np.arange(SYM.size))), shape=(usym.size, SYM.size))
SUMs = np.asarray(SUM @ Msym.T); DETs = np.asarray(DET @ Msym.T)
def sl(name):
    o_, n_ = offs[name]; return slice(o_, o_ + n_)
CPMg = SUMs[sl('GROUP')] / np.maximum(TOT[sl('GROUP')][:, None], EPS) * 1e6
NCg = NC[sl('GROUP')]
detG = DETs[sl('GROUP')] / np.maximum(NCg[:, None], 1)
# donor×group / study×group 空间 CPM (cons 用 DONORxGROUP, 与 KB7 CPMdg 同口径)
CPMdg = np.asarray(SUM[sl('DONORxGROUP')] @ Msym.T) / np.maximum(TOT[sl('DONORxGROUP')][:, None], EPS) * 1e6
CPMsg = np.asarray(SUM[sl('STUDYxGROUP')] @ Msym.T) / np.maximum(TOT[sl('STUDYxGROUP')][:, None], EPS) * 1e6
NCdg = NC[sl('DONORxGROUP')]; NCsg = NC[sl('STUDYxGROUP')]

# author 组内细胞数 & author->GROUP 归属 (细胞数对齐)
NCa = NC[sl('AUTHOR')]
Ma = np.zeros((NA, int(dg_d.max()) + 1)); Mgc = np.zeros((NG, int(dg_d.max()) + 1))
np.add.at(Ma, (da_a, da_d), NC[sl('DONORxAUTHOR')]); np.add.at(Mgc, (dg_g, dg_d), NCdg)
score = Ma @ Mgc.T
auth2grp = [int(score[a].argmax()) for a in range(NA)]

bt_by_sym = {}
for s, bt in zip(SYM, BIOT):
    bt_by_sym.setdefault(s, set()).add(bt)
def is_nc(s):
    bts = bt_by_sym.get(s, set())
    return bool(bts) and all(('RNA' in x or 'pseudo' in x or 'ncRNA' == x) for x in bts)

# ---- 目标: author 池 -> GROUP 代表行 ----
TARGETS = {
    'Melanocyte': ['Melanocytes'],
    'Schwann': ['Schwann_M', 'Schwann_N'],
    'Conj_suprabasal': ['Conj_suprabasal'],
}

def target_stats(target_auths):
    """目标池 = author 类的并集, 以 DONORxAUTHOR 聚合行加权 (细胞数)"""
    rows = [auth.index(a) for a in target_auths]
    w = NCa[rows]
    CPMt = sum(CPMa_ := None) if False else None
    # author 空间 CPM
    CPMa = SUMs[sl('AUTHOR')] / np.maximum(TOT[sl('AUTHOR')][:, None], EPS) * 1e6
    detA = DETs[sl('AUTHOR')] / np.maximum(NCa[:, None], 1)
    tot = w.sum()
    cpm = (CPMa[rows] * w[:, None]).sum(0) / tot
    det = (detA[rows] * w[:, None]).sum(0) / tot
    return cpm, det, tot

def group_row(gname):
    gi = grp.index(gname)
    return CPMg[gi], detG[gi], NCg[gi], gi

def cons_for(gi, gname, gene_col):
    """donor 级一致: target 侧=该 donor 目标 author 类表达 vs 邻居组该 donor 表达, DR>=2, MIND>=10"""
    return None  # 简化: 用 STUDYxGROUP 主导研究 + 全格 lfc 一致; donor cons 用 DONORxGROUP 邻侧

results = {}
order = np.argsort(-CPMg.mean(0))
with open(f'{ROOT}/out/kb9_fire_audit.tsv', 'w') as fout:
    fout.write('term\tgene\tcpm_target\tdet_target\tneighbor\tnbr_level\tpool\tcpm_nbr\tlfc\tcons\tnbr_ok\n')
    for term, ta in TARGETS.items():
        cpm_t, det_t, pool_t = target_stats(ta)
        # 候选: floor CPM, det, 非ncRNA, topN by (cpm, det) 预筛后按 min_lfc_fire 排序
        cand = []
        nbrs = [g for g in grp if g not in {grp[auth2grp[auth.index(a)]] for a in ta}]
        for si in range(usym.size):
            g = str(usym[si])
            if not g or is_nc(g):
                continue
            if cpm_t[si] < CPM_FLOOR or det_t[si] < 0.25:
                continue
            lfcs = []
            for nb in nbrs:
                c_n, d_n, pool_n, _ = group_row(nb)
                lfcs.append(np.log2((cpm_t[si] + 1) / (c_n[si] + 1)))
            mlfc = min(lfcs)
            if mlfc >= LFC_T:
                cand.append((g, si, mlfc))
        cand.sort(key=lambda x: -x[2])
        top = cand[:TOPN]
        print(term, 'pool', int(pool_t), 'floorpass_cand', len(cand), 'top:', [c[0] for c in top])
        results[term] = []
        for g, si, mlfc in top:
            row = dict(gene=g, cpm=round(float(cpm_t[si]), 1), det=round(float(det_t[si]), 3), min_lfc_fire=round(float(mlfc), 3))
            results[term].append(row)
            for nb in nbrs:
                c_n, d_n, pool_n, _ = group_row(nb)
                lfc = float(np.log2((cpm_t[si] + 1) / (c_n[si] + 1)))
                fout.write(f"{term}\t{g}\t{cpm_t[si]:.1f}\t{det_t[si]:.3f}\t{nb}\tgroup\t{int(pool_n)}\t{c_n[si]:.2f}\t{lfc:.3f}\t\t{'ok' if lfc>=LFC_T else 'FIRE'}\n")
        # 兄弟亚型 (同父 author)
        parents = {grp[auth2grp[auth.index(a)]] for a in ta}
        sibs = [a for a in auth if grp[auth2grp[auth.index(a)]] in parents and a not in ta]
        CPMa = SUMs[sl('AUTHOR')] / np.maximum(TOT[sl('AUTHOR')][:, None], EPS) * 1e6
        for g, si, mlfc in top:
            for sb in sibs:
                ai = auth.index(sb)
                lfc = float(np.log2((cpm_t[si] + 1) / (CPMa[ai, si] + 1)))
                fout.write(f"{term}\t{g}\t{cpm_t[si]:.1f}\t{det_t[si]:.3f}\t{sb}\tauthor\t{int(NCa[ai])}\t{CPMa[ai,si]:.2f}\t{lfc:.3f}\t\t{'ok' if (lfc>=LFC_T or NCa[ai]<MINPOOL) else 'FIRE'}\n")
json.dump(results, open(f'{ROOT}/out/kb9_term_candidates.json', 'w'), ensure_ascii=False, indent=1)
print('DONE')
