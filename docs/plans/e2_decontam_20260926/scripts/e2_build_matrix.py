#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2-1 证据矩阵构建：gene x panel x PMID 全矩阵（可复算规则产物）。
产物: data/e2_gene_panel_pmid.tsv + data/e2_matrix_rows_summary.tsv + logs/matrix_log.txt"""
import json, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2_common import (load_panel, gene_evidence, keep, MEMBERS, v41_p04_sets, ROOT)

def main():
    log = []
    def P(*a):
        s = ' '.join(str(x) for x in a); log.append(s); print(s, flush=True)
    rows, dbs = load_panel()
    P(f'ON rows registered: {len(rows)} classes={len({r["key"] for r in rows})}')
    _, _, warn = v41_p04_sets(dbs)
    for w in warn:
        P('WARN', w)
    out = open(f'{ROOT}/data/e2_gene_panel_pmid.tsv', 'w')
    hdr = (['library', 'class_raw', 'gene', 'explicit_pmids', 'hrca', 'mem', 'face', 'p04', 'pcx_ext',
            'axis_members'] + [f'keep_S1_{m}' for m in MEMBERS]
           + ['keep_S2_Q5b', 'keep_S4_Q5b', 'keep_S5_Q5b'])
    out.write('\t'.join(hdr) + '\n')
    ext = iax = nor = 0
    per_row = []
    for r in rows:
        re_ = ri = rn = 0
        for g in r['genes']:
            e = gene_evidence(dbs, r['lib'], r['cls'], g)
            if e['S']:
                ext += 1; re_ += 1
            elif e['axis']:
                iax += 1; ri += 1
            else:
                nor += 1; rn += 1
            keeps1 = [str(1 if keep(e, r['lib'], m, 'S1') else 0) for m in MEMBERS]
            out.write('\t'.join([r['lib'], r['cls'], g, ';'.join(sorted(e['S'])),
                                 'Y' if e['hrca'] else '', 'Y' if e['mem'] else '',
                                 'Y' if e['face'] else '', 'Y' if e['p04'] else '',
                                 'Y' if e['pcx'] else '', ';'.join(sorted(e['axis']))]
                                + keeps1
                                + [str(1 if keep(e, r['lib'], 'Q5b', 'S2') else 0),
                                   str(1 if keep(e, r['lib'], 'Q5b', 'S4') else 0),
                                   str(1 if keep(e, r['lib'], 'Q5b', 'S5') else 0)]) + '\n')
        per_row.append((r['lib'], r['cls'], len(r['genes']), re_, ri, rn))
    out.close()
    st = open(f'{ROOT}/data/e2_matrix_rows_summary.tsv', 'w')
    st.write('\t'.join(['library', 'class', 'n_genes', 'external_chain', 'internal_axis_only', 'no_record']) + '\n')
    for t in per_row:
        st.write('\t'.join(map(str, t)) + '\n')
    st.close()
    P(f'gene x panel pairs={ext+iax+nor}: external_chain={ext} internal_axis_only={iax} no_record={nor}')
    open(f'{ROOT}/logs/matrix_log.txt', 'w').write('\n'.join(log) + f'\nran {datetime.datetime.now()}\n')
    print('E2_MATRIX_DONE')

if __name__ == '__main__':
    main()
