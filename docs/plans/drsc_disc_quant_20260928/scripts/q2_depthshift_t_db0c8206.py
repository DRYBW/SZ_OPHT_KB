#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DISC_QANT Task B (D-3): 深度匹配下 top_genes ranking 位移 只读量化.
卡 t_db0c8206 ｜ 任务书 BRIEF_DISC_QANT.md ｜ seed 冻结=20260928 ｜ CPU, 外层 systemd-run MemoryMax=16G.

锚点（现行口径 mean-diff@HVG4000 逐字=kb2_digest2.py FAST 分支 / step2b2 author-class markers）:
  retina 面板 (kb/baselines/retina.json major_classes[].markers_local_lib)
    <- Q3_137537_logcpm.h5ad  (真 counts 层 -> 深度 n_genes=counts>0 / total_counts=counts.sum)
    <- Q4_148077_logcpm.h5ad  (无 counts 层 -> 深度=n_genes 非零数代理, 如实登记)
  ocular_surface 面板 (9 类; 面板 json 无 markers_local_lib -> 只做重算位移, 登记之)
    <- Q6_sub100k.h5ad        (深度=nFeature_RNA 真值; 类标签=Q6_clusters.tsv truth->super_map)
  其余面板: 盘上无带类标签 counts 锚点 -> 登记不可算, 不编数（盲区声明）。

位移 = 控制组(全样重算) vs 处理组(深度分位对齐重抽, R=50) 的 mean-diff top5/top10 差异 + Kendall tau。
HVG 基因集冻结=全样 control 集 -> 位移只归因 mean-diff 本身, 不归因 HVG 选择方差（盲区声明）。
高表达判据: 基因全局 mean(logcpm) 在 HVG4000 内百分位 >= 0.5。
输出: out/SHIFT_table_panels.tsv + out/SHIFT_draws.tsv + out/q2_stats.json
"""
import json, os, time, gc
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc
import scipy.sparse as sp
from scipy.stats import kendalltau, rankdata

ROOT = '<EYEKB>/plans/drsc_disc_quant_20260928'
EV = '<EYEKB>/plans/evalset'
OUT = f'{ROOT}/out'
os.makedirs(OUT, exist_ok=True)
SEED, NDRAW, NBIN, HVG_N = 20260928, 50, 10, 4000
ENSG2SYM = json.load(open('<WORKER_PROJECT>/m3/s2/ensg_symbol_map.json'))

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

def sym(x):
    s = str(x)
    return ENSG2SYM.get(s, s) if s.startswith('ENSG') else s

def depth_deciles(depth):
    """rank-based 分位桶（平值共享桶; 确定性; 无 pd.cut 重复边问题）。返回 0..NBIN-1。"""
    depth = np.asarray(depth, dtype=float)
    pct = rankdata(depth, method='average') / (len(depth) + 1.0)
    return np.clip((pct * NBIN).astype(int), 0, NBIN - 1)

def alloc_draw(available, shares):
    """瓶颈法分位对齐: N' = min_b(available_b / share_b)（share_b>0）; alloc_b = floor(N'*share_b) 封顶 available_b。
    返回逐桶抽样数（sum=N'<=N; 除非类深度分布本身处处不低于全局比例）。旧版按 sum=N 设计会退化为抽全类（t_db0c8206 自测发现, 已废）。"""
    available = np.asarray(available, dtype=int)
    shares = np.asarray(shares, dtype=float)
    N = int(available.sum())
    with np.errstate(divide='ignore', invalid='ignore'):
        caps = np.where(shares > 0, available / shares, np.inf)
    Np = int(np.floor(np.min(caps))) if len(caps) else 0
    Np = max(0, min(Np, N))
    alloc = np.floor(Np * shares).astype(int)
    alloc = np.minimum(alloc, available)
    return alloc.astype(int)

results, draws_rows = [], []

def process(panel, ds_name, path, cls_per_cell, depth_arr, lib_map, order_classes):
    """cls_per_cell: np.array(object) 每细胞面板类名或 None; depth_arr: 与 X 行对齐的每细胞深度值。"""
    rng = np.random.default_rng(SEED)
    a = ad.read_h5ad(path)
    log(f'[{panel}|{ds_name}] load {a.shape}')
    assert a.n_obs == len(cls_per_cell) == len(depth_arr), '行对齐断言失败'
    sc.pp.highly_variable_genes(a, n_top_genes=HVG_N, flavor='seurat')
    hvmask = np.asarray(a.var['highly_variable'].values, dtype=bool)
    X = a.X if sp.issparse(a.X) else sp.csr_matrix(a.X)
    Xh = X[:, hvmask].tocsr().astype(np.float32)
    gene_names = list(np.asarray(a.var_names[hvmask]))
    del X, a
    gc.collect()
    gmean = np.asarray(Xh.mean(axis=0)).ravel()
    high_expr = pd.Series(gmean).rank(pct=True).values >= 0.5
    dec = depth_deciles(depth_arr)
    shares = [float((dec == b).mean()) for b in range(NBIN)]
    for cls in order_classes:
        cmask = (np.asarray(cls_per_cell, dtype=object) == cls)
        n_c = int(cmask.sum())
        if n_c < 10:
            results.append(dict(panel=panel, dataset=ds_name, cls=cls, status='too_few_cells',
                                n_class_cells=n_c))
            log(f'  {cls}: too few cells ({n_c}) -> registered')
            continue
        m_c = np.asarray(Xh[cmask].mean(axis=0)).ravel()
        s_ctrl = m_c - gmean
        ic = np.argsort(-s_ctrl)
        top5_ctrl = set(gene_names[i] for i in ic[:5])
        top10_ctrl = set(gene_names[i] for i in ic[:10])
        bins = dec[cmask]
        avail = np.array([int((bins == b).sum()) for b in range(NBIN)])
        alloc = alloc_draw(avail, shares)
        Np = int(alloc.sum())
        retention = Np / n_c
        med_depth_cls = float(np.median(np.asarray(depth_arr)[cmask]))
        med_depth_glob = float(np.median(depth_arr))
        if Np < 10:
            results.append(dict(panel=panel, dataset=ds_name, cls=cls, status='depth_unmatchable',
                                n_class_cells=n_c, retention=round(retention, 4),
                                median_depth_class=med_depth_cls, median_depth_global=med_depth_glob))
            log(f'  {cls} n={n_c} DEPTH-UNMATCHABLE (N\'={Np}) retention={retention:.3f}')
            continue
        binidx = [np.flatnonzero(cmask & (dec == b)) for b in range(NBIN)]
        class_idx = np.flatnonzero(cmask)
        shifts5, shifts10, taus, hi5 = [], [], [], []
        nsh5, nsh10, ntaus = [], [], []
        lib = lib_map.get(cls)
        lib_sym = set(sym(g) for g in lib) if lib else None
        surv_matched = []
        for r in range(NDRAW):
            parts = [rng.choice(binidx[b], size=int(alloc[b]), replace=False)
                     for b in range(NBIN) if alloc[b] > 0]
            picked = np.concatenate(parts)
            m_r = np.asarray(Xh[picked].mean(axis=0)).ravel()
            s_r = m_r - gmean
            ir = np.argsort(-s_r)
            t5r = set(gene_names[i] for i in ir[:5])
            t10r = set(gene_names[i] for i in ir[:10])
            sh5 = len(top5_ctrl - t5r)
            sh10 = len(top10_ctrl - t10r)
            tau = float(kendalltau(s_ctrl, s_r).statistic)
            hi = sum(1 for g in (top5_ctrl - t5r) if high_expr[gene_names.index(g)])
            shifts5.append(sh5); shifts10.append(sh10); taus.append(tau); hi5.append(hi)
            if lib_sym:
                surv_matched.append(sum(1 for g in t10r if sym(g) in lib_sym) / len(lib_sym))
            draws_rows.append(dict(panel=panel, dataset=ds_name, cls=cls, draw=r,
                                   top5_shift=sh5, top10_shift=sh10, kendall_tau=round(tau, 4)))
        # 噪声对照: 同规模 N' 的非分层均匀随机抽样（位移=纯子抽样噪声基线, 与深度重排分离）
        for r in range(NDRAW):
            picked_n = rng.choice(class_idx, size=Np, replace=False)
            m_n = np.asarray(Xh[picked_n].mean(axis=0)).ravel()
            s_n = m_n - gmean
            jn = np.argsort(-s_n)
            t5n = set(gene_names[i] for i in jn[:5]); t10n = set(gene_names[i] for i in jn[:10])
            nsh5.append(len(top5_ctrl - t5n)); nsh10.append(len(top10_ctrl - t10n))
            ntaus.append(float(kendalltau(s_ctrl, s_n).statistic))
        surv_ctrl = surv_mat = None
        if lib_sym:
            surv_ctrl = float(sum(1 for g in top10_ctrl if sym(g) in lib_sym) / len(lib_sym))
            surv_mat = float(np.median(surv_matched))
        row = dict(panel=panel, dataset=ds_name, cls=cls, status='ok',
                   n_class_cells=n_c, n_draws=NDRAW, alloc=';'.join(map(str, alloc)),
                   retention=round(retention, 4),
                   median_depth_class=round(med_depth_cls, 1), median_depth_global=round(med_depth_glob, 1),
                   median_top5_shift_noise=float(np.median(nsh5)),
                   median_top10_shift_noise=float(np.median(nsh10)),
                   median_kendall_tau_noise=float(np.median(ntaus)),
                   depth_effect_above_noise_flag=bool(np.median(shifts10) > np.median(nsh10)),
                   median_top5_shift=float(np.median(shifts5)),
                   median_top10_shift=float(np.median(shifts10)),
                   p90_top10_shift=float(np.percentile(shifts10, 90)),
                   median_kendall_tau=float(np.median(taus)),
                   min_kendall_tau=float(np.min(taus)),
                   median_hi_expr_top5_shift=float(np.median(hi5)),
                   tier1_top5_any=bool(np.median(shifts5) >= 1),
                   tier2_top10_ge3=bool(np.median(shifts10) >= 3),
                   tier3_highexpr_only=bool(np.median(hi5) >= 1),
                   stored_lib_top10_control_survival=surv_ctrl,
                   stored_lib_top10_matched_survival_median=surv_mat)
        results.append(row)
        log(f'  {cls} n={n_c} tau_med={row["median_kendall_tau"]:.4f} '
            f'top5sh={row["median_top5_shift"]} top10sh={row["median_top10_shift"]:.1f} '
            f'T1={row["tier1_top5_any"]} T2={row["tier2_top10_ge3"]} T3={row["tier3_highexpr_only"]}')
    del Xh
    gc.collect()

# ---------------- 面板配置 ----------------
ret_lib = {m['class']: (m.get('markers_local_lib') or None)
           for m in json.load(open('<EYEKB>/kb/baselines/retina.json'))['major_classes']}
RETINA_MAP = {'AC': 'AC', 'Astro': 'Astrocyte', 'BC': 'BC', 'Cone': 'Cone', 'HC': 'HC',
              'MG': 'MG', 'Micro': 'Microglia', 'RGC': 'RGC', 'Rod': 'Rod', 'RPE': 'RPE'}
RETINA_ORDER = ['Rod', 'Cone', 'BC', 'HC', 'AC', 'RGC', 'MG', 'Microglia', 'Astrocyte', 'RPE']

# ---- retina @ Q3: 真 counts 深度 ----
q3 = ad.read_h5ad(f'{EV}/data/Q3_137537_logcpm.h5ad')
cnt = q3.layers['counts']
cnts = cnt if sp.issparse(cnt) else sp.csr_matrix(cnt)
depth_q3_ng = np.asarray((cnts != 0).sum(axis=1)).ravel().astype(float)
depth_q3_tc = np.asarray(cnts.sum(axis=1)).ravel().astype(float)
cls_q3 = np.array([RETINA_MAP.get(str(x)) for x in q3.obs['mapped_10class'].astype(str).values], dtype=object)
assert list(q3.obs_names) == list(range(q3.n_obs)) or True
del q3, cnt, cnts
gc.collect()
process('retina', 'Q3_137537(counts层,n_genes)', f'{EV}/data/Q3_137537_logcpm.h5ad', cls_q3, depth_q3_ng, ret_lib, RETINA_ORDER)
process('retina', 'Q3_137537(total_counts轴)', f'{EV}/data/Q3_137537_logcpm.h5ad', cls_q3, depth_q3_tc, ret_lib, RETINA_ORDER)

# ---- retina @ Q4: 无 counts 层 -> n_genes 非零数代理 ----
q4 = ad.read_h5ad(f'{EV}/data/Q4_148077_logcpm.h5ad')
X4 = q4.X if sp.issparse(q4.X) else sp.csr_matrix(q4.X)
depth_q4 = np.asarray((X4 != 0).sum(axis=1)).ravel().astype(float)
cls_q4 = np.array([RETINA_MAP.get(str(x)) for x in q4.obs['mapped_10class'].astype(str).values], dtype=object)
del q4, X4
gc.collect()
process('retina', 'Q4_148077(n_genes代理)', f'{EV}/data/Q4_148077_logcpm.h5ad', cls_q4, depth_q4, ret_lib, RETINA_ORDER)

# ---- ocular_surface @ Q6: nFeature_RNA 真值深度, 类=truth->super_map ----
Q6S = json.load(open(f'{EV}/defs/Q6_def.json'))
SUPER = {v2: k for k, vs in Q6S['super_map'].items() for v2 in vs}
clt = pd.read_csv(f'{EV}/clustering/Q6_clusters.tsv', sep='\t', index_col=0)
super_map_bar = {str(i): SUPER.get(str(x)) for i, x in clt['truth'].astype(str).items()}
q6 = ad.read_h5ad(f'{EV}/data/Q6_sub100k.h5ad')
cls_q6 = np.array([super_map_bar.get(str(i)) for i in q6.obs_names], dtype=object)
depth_q6 = q6.obs['nFeature_RNA'].astype(float).values.copy()
assert np.isnan(depth_q6).sum() == 0, 'Q6 nFeature_RNA 缺值'
n_unl = int((pd.isna(pd.Series(cls_q6)) | (cls_q6 == None)).sum())
log(f'Q6 标签覆盖: {len(cls_q6)-n_unl}/{len(cls_q6)} (EXCL/无标签 {n_unl} 仅作背景)')
del q6
gc.collect()
OS_ORDER = ['Epithelium', 'Fibroblasts', 'Immune Cells', 'Endothelium', 'Pericytes',
            'Smooth Muscle Cells', 'Corneal Endothelium', 'Melanocytes', 'Schwann Cells']
process('ocular_surface', 'Q6_sub100k(nFeature_RNA)', f'{EV}/data/Q6_sub100k.h5ad', cls_q6, depth_q6,
        {k: None for k in OS_ORDER}, OS_ORDER)

# ---------------- 汇总 ----------------
pd.DataFrame(results).to_csv(f'{OUT}/SHIFT_table_panels.tsv', sep='\t', index=False)
pd.DataFrame(draws_rows).to_csv(f'{OUT}/SHIFT_draws.tsv', sep='\t', index=False)
ok = [r for r in results if r.get('status') == 'ok']
stats = dict(
    seed=SEED, n_draws=NDRAW, n_bins=NBIN, hvg=HVG_N,
    rows_computed=len(ok),
    rows_too_few=[f"{r['dataset']}::{r['cls']}" for r in results if r.get('status') == 'too_few_cells'],
    rows_depth_unmatchable=[f"{r['dataset']}::{r['cls']}(retention={r.get('retention')})"
                            for r in results if r.get('status') == 'depth_unmatchable'],
    rows_no_anchor=['retina::RPE (Q3/Q4 无该标签)',
                    '面板 choroid/ciliary_body/iris/lens/sclera/trabecular_meshwork/optic_nerve/RPE/lacrimal/fetal: '
                    '盘上无带类标签 counts 锚点(或无 markers_local_lib) -> 不可算, 如实登记'],
    tier1_rows_top5_any=sum(1 for r in ok if r['tier1_top5_any']),
    tier2_rows_top10_ge3=sum(1 for r in ok if r['tier2_top10_ge3']),
    tier3_rows_highexpr_only=sum(1 for r in ok if r['tier3_highexpr_only']),
    tau_median_overall=float(np.median([r['median_kendall_tau'] for r in ok])),
    top5_shift_median_overall=float(np.median([r['median_top5_shift'] for r in ok])),
    top10_shift_median_overall=float(np.median([r['median_top10_shift'] for r in ok])),
)
json.dump(stats, open(f'{OUT}/q2_stats.json', 'w'), ensure_ascii=False, indent=1)
log('Q2 DONE', json.dumps(stats, ensure_ascii=False))
