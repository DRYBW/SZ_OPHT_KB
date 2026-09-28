#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRADE-D16 步骤2：漂移量化（零 LLM，纯矩阵计算）
- 各席 grade 分布 + 时序漂移
- BTEST run1/run2 同席成对漂移
- 正确名被降 C 全库扫（Q5b::35 型案逐案登记 + 可救性标记）
- 席位 grade-C 率 vs 命中率相关（过度保守 vs 随机噪声判据）
"""
import json, pandas as pd, numpy as np, collections

OUT = '/mnt/D/EyeKB/plans/grade_anchor_20260928'
M = pd.read_csv(f'{OUT}/data/ballot_matrix.tsv', sep='\t', keep_default_na=False, na_values=[''])
CON = json.load(open(f'{OUT}/data/consensus_recomputed.json'))

# Q6 细粒度票面 ≡ super truth 等价表（辅助列，strict 口径为主）
SUPER_EQ = {'Keratocytes': 'Fibroblasts', 'Mac_DAM_LAM': 'Immune Cells', 'Mac_Tissue': 'Immune Cells',
            'pDC': 'Immune Cells', 'APC_MHCII_high': 'Immune Cells', 'Conj_epithelium_basal': 'Epithelium'}
M['truth_strict'] = (M['kind'] == 'NAMED') & (M['identity_norm'] == M['truth'])
M['truth_eq'] = M['truth_strict'] | ((M['kind'] == 'NAMED') & M['identity_norm'].map(SUPER_EQ).eq(M['truth']))

DATASETS_TRUTH = {'RET45', 'Q6-33', 'Q6-25', 'RUN45-2seat'}
def has_truth(ds, cid):
    tag = cid.split('::')[0]
    return tag in ('Q1','Q2','Q3','Q4','Q5b','Q7') or tag == 'Q6'

# ---------- 1) 席×archive grade 分布 ----------
rows = []
for (arch, seat, model), g in M[M['missing'] == 0].groupby(['archive', 'seat', 'model']):
    n = len(g)
    k = g['kind'].value_counts()
    gr = g['grade'].astype(str).value_counts()
    tv = g[g['truth'].notna() & (g['kind'] == 'NAMED')]
    valid = g[g['truth'].notna() & (g['kind'] == 'NAMED') & g['grade'].isin(['A', 'B'])]
    namedC = g[g['truth'].notna() & (g['kind'] == 'NAMED') & (g['grade'] == 'C')]
    rows.append(dict(archive=arch, seat=seat, model=model, n=n,
                     gradeA=gr.get('A', 0), gradeB=gr.get('B', 0), gradeC=gr.get('C', 0),
                     pC=round(gr.get('C', 0) / n, 3),
                     pC_named=round(len(namedC) / max(len(tv), 1), 3),      # 具名票中被降C率
                     undet=k.get('UNDET', 0), coarse=k.get('COARSE', 0), named=k.get('NAMED', 0),
                     hit_rate_valid=round(valid['truth_strict'].mean(), 3) if len(valid) else None,
                     hidden_acc_namedC=round(namedC['truth_strict'].mean(), 3) if len(namedC) else None,
                     n_namedC=len(namedC)))
D = pd.DataFrame(rows)
D.to_csv(f'{OUT}/data/seat_grade_dist.tsv', sep='\t', index=False)

# ---------- 2) BTEST 成对漂移 ----------
pair = []
for seat in 'ABC':
    r1 = M[(M['archive'] == 'BTEST-run1') & (M['seat'] == seat)].set_index('cluster_id')
    r2 = M[(M['archive'] == 'BTEST-run2') & (M['seat'] == seat)].set_index('cluster_id')
    cids = sorted(set(r1.index) & set(r2.index))
    gf = sum(1 for c in cids if str(r1.loc[c, 'grade']) != str(r2.loc[c, 'grade']))
    idf = sum(1 for c in cids if str(r1.loc[c, 'identity_norm']) != str(r2.loc[c, 'identity_norm']))
    dcC = sum(1 for c in cids if r1.loc[c, 'grade'] == 'C' and r2.loc[c, 'grade'] != 'C')
    ic2C = sum(1 for c in cids if r1.loc[c, 'grade'] != 'C' and r2.loc[c, 'grade'] == 'C')
    pair.append(dict(seat=seat, n=len(cids), grade_flip=gf, grade_flip_rate=round(gf/len(cids), 3),
                     ident_flip=idf, ident_flip_rate=round(idf/len(cids), 3),
                     C_in_run2=ic2C, C_out_run2=dcC))
P = pd.DataFrame(pair)
P.to_csv(f'{OUT}/data/btest_run_pair_drift.tsv', sep='\t', index=False)

# ---------- 3) 正确名被降 C 全库扫 ----------
dem = M[(M['missing'] == 0) & (M['kind'] == 'NAMED') & (M['grade'].astype(str) == 'C') &
        M['truth'].notna() & M['truth_strict']].copy()
# 附加：该票在 C4 下被弃，本簇基线共识是什么；只升这一票能否翻正（可救性）
recs = []
for _, r in dem.iterrows():
    arch, cid = r['archive'], r['cluster_id']
    base = CON[arch][cid]
    # 同 archive 其他席有效票（grade A/B NAMED）同名计数
    others = M[(M['archive'] == arch) & (M['cluster_id'] == cid) & (M['seat'] != r['seat']) &
               (M['missing'] == 0)]
    same_valid = int(((others['kind'] == 'NAMED') & others['grade'].isin(['A', 'B']) &
                      (others['identity_norm'] == r['identity_norm'])).sum())
    recs.append(dict(archive=arch, seat=r['seat'], model=r['model'], cluster_id=cid,
                     truth=r['truth'], base_c4=base['c4'], base_mode=base['mode'],
                     rescue_1ballot=int(base['c4'] in (None, '') and same_valid >= 1),
                     same_valid_others=same_valid,
                     gate_identity_evidence=r['gate_identity_evidence'],
                     gate_resolution=r['gate_resolution'], gate_technical=r['gate_technical'],
                     flag=r['flag'], why=r['why']))
DEM = pd.DataFrame(recs)
DEM.to_csv(f'{OUT}/data/correct_name_demoted_C.tsv', sep='\t', index=False)

# 具名∧gradeC 全量（含错名降C，用于"过度保守 vs 随机噪声"）
namedC = M[(M['missing'] == 0) & (M['kind'] == 'NAMED') & (M['grade'].astype(str) == 'C')].copy()
namedC['is_truth'] = namedC['truth_strict']
namedC.to_csv(f'{OUT}/data/named_gradeC_all.tsv', sep='\t', index=False)

# ---------- 4) 席级相关：降C率 vs 命中率 ----------
DD = D[D['model'] != 'unrecorded'].copy()
DD = DD[DD['archive'].isin(['RUN4-r','RUN5','RUN6A','RUN6B','RUN7RG','FACEV21','BTEST-run1','BTEST-run2','KB9'])]
x = DD['pC_named'].values; y = DD['hit_rate_valid'].values
def spearman(a, b):
    ra = pd.Series(a).rank().values; rb = pd.Series(b).rank().values
    return float(np.corrcoef(ra, rb)[0, 1])
rho = spearman(x, y)
# 全席全簇 C 率（含 undet 的总 C 率）版本
x2 = DD['pC'].values
rho2 = spearman(x2, y)
# 三席内部（每 archive 内 A/B/C 三点）相关均值
rho_model = {}
for m, g in DD.groupby('model'):
    rho_model[m] = dict(n=int(len(g)), mean_pC=round(g['pC'].mean(), 3),
                        mean_pC_named=round(g['pC_named'].mean(), 3),
                        mean_hit=round(np.nanmean(g['hit_rate_valid']), 3),
                        mean_hidden_acc=round(np.nanmean(g['hidden_acc_namedC']), 3))
CORR = dict(spearman_pC_named_vs_hit=round(rho, 3), n_units=int(len(DD)),
            spearman_pC_total_vs_hit=round(rho2, 3),
            by_model=rho_model)
json.dump(CORR, open(f'{OUT}/data/seat_corr.json', 'w'), ensure_ascii=False, indent=1)

# ---------- 5) 时序漂移（C 率随 run 时间） ----------
TIME = {'RUN2': '2026-09-23', 'RUN3': '2026-09-24', 'RUN3MINI': '2026-09-24', 'RUN4': '2026-09-24',
        'RUN4-r': '2026-09-24', 'RUN5': '2026-09-25', 'RUN6A': '2026-09-26', 'RUN6B': '2026-09-26',
        'RUN7RG': '2026-09-26', 'FACEV21': '2026-09-26', 'KB9': '2026-09-27',
        'BTEST-run1': '2026-09-27', 'BTEST-run2': '2026-09-27'}
D['date'] = D['archive'].map(TIME)
TS = D[D['model'].isin(['qwen3.8-max', 'glm-5.1', 'deepseek-v3.2'])].sort_values(['model', 'date', 'archive'])
TS[['model', 'date', 'archive', 'seat', 'pC', 'pC_named', 'hit_rate_valid', 'hidden_acc_namedC', 'n_namedC']].to_csv(
    f'{OUT}/data/gradeC_rate_timeseries.tsv', sep='\t', index=False)

print('==== 席×archive grade 分布（LLM 三席系） ====')
print(D.to_string(index=False))
print('\n==== BTEST 成对漂移 ====')
print(P.to_string(index=False))
print('\n==== 正确名被降C 全库扫: %d 案 ====' % len(DEM))
if len(DEM):
    print(DEM.groupby(['archive', 'seat']).size().to_string())
    print(DEM.to_string(index=False)[:3000])
print('\n==== 具名∧gradeC 全量: %d 票，其中隐藏名==truth 占 %.1f%% ====' % (
    len(namedC), 100 * namedC['is_truth'].mean()))
print('按席 (model): ')
print(namedC.groupby('model')['is_truth'].agg(['size', 'mean']).round(3).to_string())
print('\n==== 相关 ====')
print(json.dumps(CORR, ensure_ascii=False, indent=1))
print('\nDONE drift')
