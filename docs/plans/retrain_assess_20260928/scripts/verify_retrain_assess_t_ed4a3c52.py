#!/usr/bin/env python3
"""RETRAIN 四对象冲击评估——可复算验证脚本（t_ed4a3c52, 2026-09-28, 全程只读）。

复算内容：
  A) v2_prod: pkl sha 对 META；LILRB2 在 HVG-2000 特征列定位 + 各类系数
  B) mouse_prod_v1: SHA256SUMS 对账 + hvg_panel ENSMUSG 全行覆盖
  C) RAG v2.4: chunks.parquet 行数=230,426、闭集 64 PMID 精确分割 220,654+9,772、
     embedding 列 null=0/空=0/维数全 1024、新 lane 编码覆盖 9,772/9,772
  D) 撤证面: v6 面板内嵌 41349939 计数=1（core[13].evidence[1]）；errata/linkbackfill 命中计数

退出码 0 = 全部断言 PASS。
"""
import hashlib, json, sys
import numpy as np

FAIL = []
def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")
    if not cond: FAIL.append(name)

# ---- A) v2_prod ----
pkl = '/mnt/D/OcularKB/models/v2_prod/v2_prod_model.pkl'
sha = hashlib.sha256(open(pkl, 'rb').read()).hexdigest()
meta = json.load(open('/mnt/D/OcularKB/models/v2_prod/META.json'))
check('A1 v2_prod sha==META', sha == meta['sha256'], sha[:16])
import joblib
d = joblib.load(pkl)
cg = np.array(d['common_genes']); hi = np.array(d['hvg_idx'])
# 列序按 hvg_idx 原存储序（lr.coef_ 列与训练取列顺序一致），禁止排序
hvg = [str(x) for x in cg[hi]]
check('A2 LILRB2 in HVG-2000', 'LILRB2' in hvg, f"pos={hvg.index('LILRB2') if 'LILRB2' in hvg else None}")
pos = hvg.index('LILRB2')
coefs = d['lr'].coef_[:, pos]
classes = [str(c) for c in d.get('classes')]
print('     LILRB2 coef by class:', {c: round(float(v), 4) for c, v in zip(classes, coefs)})

# ---- B) mouse_prod_v1 ----
import subprocess
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS.txt'],
                   cwd='/mnt/D/OcularKB/models/mouse_prod_v1',
                   capture_output=True, text=True)
oks = r.stdout.count(': OK'); fails = r.stdout.count(': FAILED')
check('B1 mouse SHA256SUMS 全 OK', oks == 6 and fails == 0, f'{oks} OK / {fails} FAILED')
lines = open('/mnt/D/OcularKB/models/mouse_prod_v1/hvg_panel.csv').read().strip().splitlines()[1:]
check('B2 panel 2000 行全 ENSMUSG', len(lines) == 2000 and all('ENSMUSG' in l for l in lines),
      f'{len(lines)} rows')

# ---- C) RAG v2.4 ----
import pyarrow.parquet as pq
closed = {p.strip() for p in open('/mnt/D/EyeKB/plans/rag_fix_20260928/out/closed_set_pmids.txt')
          if p.strip() and not p.startswith('#')}
check('C0 闭集 64 PMID', len(closed) == 64, str(len(closed)))
t = pq.ParquetFile('/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09/chunks.parquet')\
      .read(columns=['paper_id', 'embedding'])
pid = t['paper_id'].to_pylist(); emb = t['embedding']; n = len(pid)
check('C1 行数 230,426', n == 230426, str(n))
new_mask = [str(p).split(':')[-1] in closed for p in pid]
n_new = sum(new_mask)
check('C2 分割 9,772+220,654', n_new == 9772 and n - n_new == 220654,
      f'new={n_new} inherited={n-n_new}')
nulls = sum(1 for e in emb if e is None)
empties = sum(1 for e in emb if e is not None and len(e) == 0)
check('C3 embedding null=0 空=0', nulls == 0 and empties == 0, f'null={nulls} empty={empties}')
lens = np.fromiter((len(e) for e in emb), dtype=np.int64, count=n)
check('C4 维数全 1024', set(lens.tolist()) == {1024}, str(dict(zip(*np.unique(lens, return_counts=True)))))
check('C5 新 lane 编码齐', all(len(e) == 1024 for e, m in zip(emb, new_mask) if m), f'{n_new}/{n_new}')

# ---- D) 撤证面 ----
txt = open('/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json').read()
check('D1 v6 面板内嵌 41349939=1（撤证前设计使然，再导出候选）', txt.count('41349939') == 1)
lk = open('/mnt/D/EyeKB/kb/markers/_raggap_c_linkbackfill_v1.json').read()
check('D2 linkbackfill 零误引 PMID', lk.count('41349939') == 0)
er = json.load(open('/mnt/D/EyeKB/kb/markers/_raggap_errata_v1.json'))
check('D3 errata INERT 且目标=core[13]/LILRB2',
      er['status'].startswith('INERT') and
      er['retractions'][0]['target_gene'] == 'LILRB2' and
      er['retractions'][0]['target_json_path'] == '/microglia_repair/core[13]')

print()
print('RESULT:', 'ALL PASS' if not FAIL else f'FAILED: {FAIL}')
sys.exit(0 if not FAIL else 1)
