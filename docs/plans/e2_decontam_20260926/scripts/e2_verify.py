#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2 复刻验收闸门（预注册 §1）：raw replica vs e1_scores_ON.tsv 逐 (cid,canon) 全等。
n/lit 必须 bit 级一致；shared_genes/alias 仅允许平票行序差异并逐处登记。不过闸 exit 2。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2_common import ROOT, R1

def load(path):
    per = {}
    for i, l in enumerate(open(path)):
        if i == 0:
            continue
        f = l.rstrip('\n').split('\t')
        per[(f[0], f[3])] = dict(n=int(f[4]), genes=f[5], alias=f[6], lit_n=int(f[7]), lit=f[8])
    return per

def main():
    e1 = load(f'{R1}/data/e1_scores_ON.tsv')
    mine = load(f'{ROOT}/data/e2_scores_raw_replica.tsv')
    log = []
    only_e1 = sorted(set(e1) - set(mine))
    only_mine = sorted(set(mine) - set(e1))
    dn = dl = dg = da = 0
    diff_rows = []
    for k in sorted(set(e1) & set(mine)):
        a, b = e1[k], mine[k]
        if a['n'] != b['n']:
            dn += 1; diff_rows.append(('N', k, a, b))
        if a['lit_n'] != b['lit_n']:
            dl += 1; diff_rows.append(('LITN', k, a, b))
        if set(x for x in a['genes'].split(';') if x) != set(x for x in b['genes'].split(';') if x):
            dg += 1; diff_rows.append(('GENES', k, a, b))
        if set(x for x in a['alias'].split(';') if x) != set(x for x in b['alias'].split(';') if x):
            da += 1; diff_rows.append(('ALIAS', k, a, b))
    log.append(f'rows: e1={len(e1)} replica={len(mine)}')
    log.append(f'only_in_e1={len(only_e1)} only_in_replica={len(only_mine)}')
    log.append(f'n_mismatch={dn} lit_n_mismatch={dl} genes_set_mismatch={dg} alias_set_mismatch={da}')
    for t in diff_rows[:20]:
        log.append('DIFF ' + repr(t))
    # 逐簇行集一致（每簇的 canon 集）
    ce1 = {}
    cm = {}
    for (c, k) in e1:
        ce1.setdefault(c, set()).add(k)
    for (c, k) in mine:
        cm.setdefault(c, set()).add(k)
    clus_diff = [c for c in set(ce1) | set(cm) if ce1.get(c, set()) != cm.get(c, set())]
    log.append(f'clusters_with_candidates: e1={len(ce1)} replica={len(cm)} per-cluster set diffs={len(clus_diff)}')
    for c in clus_diff[:10]:
        log.append(f'CLUSDIFF {c} e1-only={sorted(ce1.get(c,set())-cm.get(c,set()))} rep-only={sorted(cm.get(c,set())-ce1.get(c,set()))}')
    ok = (not only_e1) and (not only_mine) and dn == 0 and dl == 0 and dg == 0 and da == 0 and not clus_diff
    log.append('VERIFY_GATE: ' + ('PASS' if ok else 'FAIL'))
    open(f'{ROOT}/out/e2_verify_replica.tsv', 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log[-30:]))
    sys.exit(0 if ok else 2)

if __name__ == '__main__':
    main()
