import json, csv
from collections import Counter

EV = '/mnt/D/EyeKB/plans/evalset'
R1 = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'

# digest structure
rows = [json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl')]
print('digest rows:', len(rows))
r0 = rows[0]
print('digest keys:', list(r0.keys()))
lit = r0.get('lit') or {}
print('lit sample keys:', list(lit.keys())[:4])
k0 = next(iter(lit), None)
if k0:
    print('lit entry sample:', json.dumps(lit[k0], ensure_ascii=False)[:400])
print('top_genes len:', len(r0.get('top_genes') or []), '| sym sample:', (r0.get('top_genes_sym') or [])[:5])
# how many candidates in lit per cluster typical
nc = Counter(len(r.get('lit') or {}) for r in rows)
print('lit cand-count distribution:', dict(sorted(nc.items())[:8]))

# ON scores sample
print('--- e1_scores_ON.tsv head:')
for i, l in enumerate(open(f'{R1}/data/e1_scores_ON.tsv')):
    if i > 6: break
    print('  ', l.rstrip()[:150])

# sensitivity grid existing values
print('--- e1_sensitivity_grid.tsv:')
for l in open(f'{R1}/out/e1_sensitivity_grid.tsv'):
    f = l.split('\t')
    if f[0] in ('axis', 'marker_channel') or (f[0] == 'ambig'):
        print('  ', l.rstrip()[:120])

# truth region table key rows
print('--- e1_truth_region_table F-RET rows:')
for i, l in enumerate(open(f'{R1}/out/e1_truth_region_table.tsv')):
    f = l.rstrip('\n').split('\t')
    if i == 0 or (f and f[0] in ('F-RET', 'F-3SEAT') and f[1] in ('全部', '无泄漏')):
        print('  ', l.rstrip()[:200])

# flip table cols
flip = list(csv.DictReader(open('/mnt/D/EyeKB/plans/face_v21_20260926/out/per_cluster_flip_table_facev21.tsv'), delimiter='\t'))
print('--- flip cols:', list(flip[0].keys()))
print('   flip n:', len(flip), '| members:', Counter(x['cluster_id'].split('::')[0] for x in flip))
run5 = list(csv.DictReader(open(f'{EV}/scoring/run5_truth_table.tsv'), delimiter='\t'))
print('--- run5 cols:', list(run5[0].keys()))
print('   run5 n:', len(run5))
