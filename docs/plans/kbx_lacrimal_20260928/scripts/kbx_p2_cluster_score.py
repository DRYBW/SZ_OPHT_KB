#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P2 v2: 建卷（两池 Leiden 主档 res=1.0 + 敏感性档 {0.8,1.2}）+ 等权细胞检测率群分数
+ 检测一致性门（0.7 ∧ 2x）+ 锚定/泄漏/前置条件判定。
判据件 KBX_PREREG_v2.md §2/§3/§4/§8。主考试分母=组织池；类器官=描述性附录（不投票）。
冻结常量：SEED=20260928 RES=1.0 DET_FLOOR_CP10K=5.0 CONS_T=0.7 RATIO_T=2.0 NC_MIN=30
MIN_T1=3 AMB_CV=0.3 AMB_MED=2000（CP10K 口径） MAX_SHARE=0.40。"""
import json, os, hashlib
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc

ad.settings.allow_write_nullable_strings = False
BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
H5 = '/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad'
H5_SHA = '5e6d753d0c10d1c5ac23e50b5b0150741ce0341654ad65cd68a2a72368a73399'
KB_CORE = {'LACRT', 'SCGB1D1', 'SCGB2A1', 'CST4', 'CST1', 'MUC7', 'PRR27'}
SEED = 20260928
RESOLUTIONS = {'main': 1.0, 'sens08': 0.8, 'sens12': 1.2}
DET_FLOOR = 5.0
CONS_T, RATIO_T, NC_MIN, MIN_T1 = 0.7, 2.0, 30, 3
AMB_CV, AMB_MED, MAX_SHARE = 0.3, 2000.0, 0.40

assert hashlib.sha256(open(H5, 'rb').read()).hexdigest() == H5_SHA, 'h5ad sha mismatch'
os.makedirs(f'{BASE}/logs', exist_ok=True)
log = open(f'{BASE}/logs/kbx_p2_cluster.log', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()

main_groups = json.load(open(f'{BASE}/ledgers/KBX_PANEL_MAIN_groups.json'))
main_groups = {g: v for g, v in main_groups.items()}
P('panel(main) raw:', {g: len(v) for g, v in main_groups.items()})

a = ad.read_h5ad(H5)
assert a.shape == (3071, 39009)
empty = a.obs['author_empty_well'].astype(str).str.lower().isin(['true'])
a = a[~empty].copy()
P('after empty-well exclusion', a.shape)

def cluster_pool(sub, res, seed):
    s = sub.copy()
    s.X = s.layers['counts_int32'].astype('float32')
    sc.pp.normalize_total(s, target_sum=1e4)
    sc.pp.log1p(s)
    sc.pp.highly_variable_genes(s, n_top_genes=min(2000, s.n_vars), flavor='seurat')
    h = s[:, s.var['highly_variable']].copy()
    sc.pp.pca(h, n_comps=50, random_state=seed)
    sc.pp.neighbors(h, n_neighbors=15, use_rep='X_pca', random_state=seed)
    sc.tl.leiden(h, resolution=res, flavor='igraph', random_state=seed, key_added='leiden')
    s.obs['clus'] = h.obs['leiden'].astype(str).values
    return s

def cp10k_layer(sub):
    """未取 log 的 CP10K 检测层（dense float32）：counts→normalize_total(1e4)。
    稀疏按行缩放必须 diags@X（记忆坑：csr.multiply 2D 静默错位）。"""
    import scipy.sparse as sp
    C = sub.layers['counts_int32']
    if sp.issparse(C):
        C = C.tocsr().astype(np.float64)
        lib = np.asarray(C.sum(axis=1)).ravel()
        lib[lib == 0] = 1
        X = sp.diags(1e4 / lib) @ C
        return np.asarray(X.todense(), dtype=np.float32)
    C = np.asarray(C, dtype=np.float64)
    lib = C.sum(axis=1)
    lib[lib == 0] = 1
    return np.asarray(C / lib[:, None] * 1e4, dtype=np.float32)

def group_score_table(sub, groups, panel_genes):
    """等权细胞检测率：d(c,g,gene)=frac cells CP10K>=5；群分数=截尾均值（n>=4 去首尾各1；n==3 中位；n<3 群不可用）。"""
    X = cp10k_layer(sub)
    vn = np.array(list(map(str, sub.var_names)))
    pos = {g: int(np.where(vn == g)[0][0]) for g in panel_genes if (vn == g).any()}
    cid = sub.obs['clus'].values
    clusters = sorted(np.unique(cid), key=lambda x: int(x))
    rows = []
    for c in clusters:
        m = cid == c
        n = int(m.sum())
        dets = {g: {gene: float((X[m][:, pos[gene]] >= DET_FLOOR).mean()) for gene in gs if gene in pos}
                for g, gs in groups.items()}
        rec = {'cluster': f'{c}', 'n_cells': n}
        for g, dd in dets.items():
            vals = sorted(dd.values(), reverse=True)
            k = len(vals)
            if k >= 4:
                sc_ = float(np.mean(vals[1:-1]))
            elif k == 3:
                sc_ = float(vals[1])
            else:
                sc_ = np.nan  # 群不可用（MIN_T1 未达，面板级已过滤，保险）
            rec[f'score_{g}'] = sc_
        rec['det_frac'] = json.dumps({g: {k2: round(v2, 3) for k2, v2 in d.items()} for g, d in dets.items()})
        rows.append(rec)
    return pd.DataFrame(rows)

def leak_check(groups, amb_excluded):
    rows = []
    for g, gs in groups.items():
        avail = [x for x in gs if x not in amb_excluded]
        ov = len(set(avail) & KB_CORE) / max(len(avail), 1)
        rows.append({'group': g, 'n_panel': len(avail), 'overlap_genes': '|'.join(sorted(set(avail) & KB_CORE)),
                     'overlap_frac': round(ov, 3), 'leak_flag': bool(ov > 0.5)})
    return pd.DataFrame(rows)

def anchor_decide(stab, groups_keys, amb_excluded):
    out = []
    avail_groups = [g for g in groups_keys if not all(pd.isna(stab[f'score_{g}']))]
    for _, r in stab.iterrows():
        scs = {g: float(r[f'score_{g}']) for g in avail_groups if not pd.isna(r[f'score_{g}'])}
        if not scs:
            out.append({'top_group': '', 'score_top': np.nan, 'score_second': np.nan, 'anchored': False,
                        'anchor_reason': 'no_available_group'}); continue
        srt = sorted(scs.items(), key=lambda kv: (-kv[1], kv[0]))
        top, sv = srt[0]; second = srt[1][1] if len(srt) > 1 else 0.0
        tie = len(srt) > 1 and abs(srt[0][1] - srt[1][1]) < 1e-12
        ok = (sv >= CONS_T) and ((second == 0) or (sv >= RATIO_T * second)) and (not tie) and int(r['n_cells']) >= NC_MIN
        reason = 'ok' if ok else ('tie' if tie else ('cons<0.7' if sv < CONS_T else ('ratio<2x' if sv < RATIO_T * second else 'n_cells<30')))
        out.append({'top_group': top, 'score_top': round(sv, 3), 'score_second': round(second, 3),
                    'anchored': bool(ok), 'anchor_reason': reason})
    return pd.DataFrame(out)

results = {}
for res_name, res in RESOLUTIONS.items():
    for pool in ['tissue', 'organoid']:
        sub = a[a.obs['source_type'].astype(str) == pool].copy()
        sub = cluster_pool(sub, res, SEED)
        prefix = 'TIS' if pool == 'tissue' else 'ORG'
        sub.obs['kbx_cluster'] = [f'{prefix}::{c}' for c in sub.obs['clus']]
        panel_genes = sorted({x for gs in main_groups.values() for x in gs})
        stab = group_score_table(sub, main_groups, panel_genes)
        if res_name == 'main':
            # ambient 过滤：主档组织池 n>=30 簇的池内伪 bulk CPM（簇 counts 求和÷池总计数×1e6）
            X = cp10k_layer(sub)
            cid = sub.obs['clus'].values
            keep = [c for c in np.unique(cid) if (cid == c).sum() >= NC_MIN]
            C_pool = sub.layers['counts_int32'].tocsr().astype('float64')
            pool_total = float(C_pool.sum())
            pb = {c: np.asarray(C_pool[cid == c].sum(axis=0)).ravel() / pool_total * 1e6 for c in keep}
            vn = np.array(list(map(str, sub.var_names)))
            amb = []
            for g in panel_genes:
                if not (vn == g).any():
                    continue
                j = int(np.where(vn == g)[0][0])
                vals = np.array([pb[c][j] for c in keep])
                lv = np.log2(vals + 1)
                cv = float(lv.std() / lv.mean()) if lv.mean() > 0 else 0.0
                if vals.size >= 4 and cv <= AMB_CV and float(np.median(vals)) >= AMB_MED:
                    amb.append(g)
            P(f'[main] ambient-excluded: {amb}')
            json.dump(amb, open(f'{BASE}/out/kbx_ambient_excluded.json', 'w'))
            groups_f = {g: [x for x in gs if x not in amb] for g, gs in main_groups.items()}
            groups_f = {g: v for g, v in groups_f.items() if len(v) >= MIN_T1}
            P(f'[main] groups after filter (>= {MIN_T1} T1 genes):', {g: len(v) for g, v in groups_f.items()})
            results['groups_f'] = groups_f
            stab = group_score_table(sub, groups_f, panel_genes)
        prefix = 'TIS' if pool == 'tissue' else 'ORG'
        stab['cluster'] = [f'{prefix}::{c}' for c in sorted(np.unique(sub.obs['clus'].values), key=lambda x: int(x))]
        stab = stab.merge(sub.obs.groupby('kbx_cluster').agg(
            donors=('patient_number', lambda x: '|'.join(f'{k}:{v}' for k, v in pd.Series(x).astype(str).value_counts().items())),
            sorts=('author_sort', lambda x: '|'.join(f'{k}:{v}' for k, v in pd.Series(x).astype(str).value_counts().items())),
        ).reset_index().rename(columns={'kbx_cluster': 'cluster'}), on='cluster', how='left')
        anch = anchor_decide(stab, list(results['groups_f'].keys()) if 'groups_f' in results else list(main_groups.keys()),
                             json.load(open(f'{BASE}/out/kbx_ambient_excluded.json')) if os.path.exists(f'{BASE}/out/kbx_ambient_excluded.json') else [])
        tab = pd.concat([stab.drop(columns=[c for c in ['top_group','score_top','score_second','anchored','anchor_reason'] if c in stab.columns]),
                         anch], axis=1)
        tab['pool'], tab['resolution'] = pool, res_name
        results[(res_name, pool)] = tab
        if res_name == 'main':
            sub.write_h5ad(f'{BASE}/out/kbx_clustered_{pool}.h5ad')

groups_f = results['groups_f']
leaks = leak_check(groups_f, json.load(open(f'{BASE}/out/kbx_ambient_excluded.json')))
leaks.to_csv(f'{BASE}/out/kbx_leak_overlap.tsv', sep='\t', index=False)
P('\nleak table:\n', leaks.to_string(index=False))

mt = results[('main', 'tissue')]
mo = results[('main', 'organoid')]
alltabs = pd.concat([mt, mo] + [results[(r, p)] for r in ['sens08', 'sens12'] for p in ['tissue', 'organoid']], ignore_index=True)
alltabs.to_csv(f'{BASE}/out/kbx_cluster_table_raw.tsv', sep='\t', index=False)

face = mt[mt['n_cells'] >= NC_MIN]
qual = face[(face['anchored']) & (~face['top_group'].isin(leaks[leaks['leak_flag']]['group']))]
P(f'\n=== MAIN (res=1.0) tissue clusters n>=30: {len(face)} ; anchored={int(face["anchored"].sum())} ; qualified(non-leak)={len(qual)}')
P(qual[['cluster', 'n_cells', 'top_group', 'score_top', 'score_second']].to_string(index=False))
counts = qual['top_group'].value_counts()
share = (counts.max() / len(qual)) if len(qual) else 0
P('group composition:', dict(counts), f'max_share={share:.3f}')
leak_groups = set(leaks[leaks['leak_flag']]['group'])
def qual_count(r, p):
    t = results[(r, p)]
    sel = t[(t['n_cells'] >= NC_MIN) & (t['anchored']) & (~t['top_group'].isin(leak_groups))]
    return int(len(sel))
pre = {'qual_anchors': int(len(qual)), 'max_share': float(share),
       'precondition_pass': bool(len(qual) >= 8 and share <= MAX_SHARE),
       'sens_anchors': {f'{r}_{p}': qual_count(r, p) for r in ['sens08', 'sens12'] for p in ['tissue', 'organoid']}}
json.dump(pre, open(f'{BASE}/ledgers/KBX_ANCHOR_COUNT.txt', 'w'), indent=1)
P('\nPRECONDITIONS:', json.dumps(pre, ensure_ascii=False))
P('DONE')
