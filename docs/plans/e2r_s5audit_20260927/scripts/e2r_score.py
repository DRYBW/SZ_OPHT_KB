#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R-3 打分：E2 复刻（raw/S1/S5 与 E2 冻结件逐行全等为闸）+ S5b/S5b_rel 新口径。
产物: data/e2r_scores_raw_replica.tsv, data/e2r_scores_{S1,S5,S5b,S5b_rel}.tsv, logs/score_log.txt
不 import 生产码；面板装载与打分按 E2 脚本拷贝改参（e2r_common.load_panel 同 e2_common 逐字逻辑）。"""
import json, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2r_common import (load_panel, gene_evidence, keep, canon, load_digest_rows,
                       top10_of, lit_of_cluster, MEMBERS, BSRC, ROOT)

VAR = sys.argv[1] if len(sys.argv) > 1 else 'ALL'

def main():
    log = []
    def P(*a):
        s = ' '.join(str(x) for x in a); log.append(s); print(s, flush=True)

    rows, dbs = load_panel()
    P(f'ON panel: {len(rows)} rows')
    # 预计算 (row_key, gene) -> evidence dict；每库/类只算一次
    ev_cache = {}
    for r in rows:
        for g in r['genes']:
            if (r['lib'], r['cls'], g) not in ev_cache:
                ev_cache[(r['lib'], r['cls'], g)] = gene_evidence(dbs, r['lib'], r['cls'], g)

    def kept_for(row, m, variant):
        if variant == 'raw':
            return row['genes']
        out = []
        gs = row['genes']
        gset = set()
        for g in gs:
            e = ev_cache[(row['lib'], row['cls'], g)]
            if keep(e, row['lib'], m, variant):
                out.append(g); gset.add(g)
        return out

    dig = load_digest_rows()
    assert len(dig) == 290
    variants = ['raw', 'S1', 'S5', 'S5b', 'S5b_rel'] if VAR == 'ALL' else ['raw', VAR]
    files = {}
    for v in variants:
        path = f'{ROOT}/data/e2r_scores_raw_replica.tsv' if v == 'raw' else f'{ROOT}/data/e2r_scores_{v}.tsv'
        f = open(path, 'w')
        f.write('\t'.join(['cluster_id', 'member', 'n_cells', 'cand_canon', 'n', 'shared_genes',
                           'alias_rows', 'lit_n', 'lit_pmids', 'lit_n_raw', 'n_raw_of_row']) + '\n')
        files[v] = f
    n_empty = {v: 0 for v in variants}

    for r in dig:
        cid, mem = r['cluster_id'], r['member']
        top = top10_of(r)
        raw_lit = lit_of_cluster(r)
        bsrc = BSRC.get(mem, set())
        # 注册序逐行算分（复刻 query_marker score dict 的插入序），再稳定 -n 排序 = 排名序
        scored = {v: [] for v in variants}
        for row in rows:
            ksets = {v: set(kept_for(row, mem, v)) for v in variants}
            for v in variants:
                sg = [g for g in top if g in ksets[v]]
                if sg:
                    scored[v].append((row, len(sg), sg))
        for v in variants:
            ranked = sorted(scored[v], key=lambda t: -t[1])  # 稳定排序 = 平票保注册序
            merged = {}
            for row, n, sg in ranked:  # 并类 = E1 collect 严格同规则（含平票别名序）
                c = canon(row['key'])
                if c not in merged or n > merged[c]['n']:
                    merged[c] = {'n': n, 'shared_genes': sg, 'alias': [row['key']]}
                else:
                    merged[c]['alias'].append(row['key'])
            for c, pm in raw_lit.items():  # lit-only 候选行（E1 extra_lit 同规则）
                if c not in merged and pm:
                    merged[c] = {'n': 0, 'shared_genes': [], 'alias': [c]}
            if not merged:
                n_empty[v] += 1
                continue
            for c, d in merged.items():  # lit 分数列（decon 视变体）
                pm = raw_lit.get(c, set())
                d['lit_n_raw'] = len(pm)
                d['lit_pm_raw'] = sorted(pm)
                if v in ('S1', 'S2', 'S4', 'S5', 'S5b', 'S5b_rel'):
                    d['lit_n'] = len(pm - bsrc)
                    d['lit_pm'] = sorted(pm - bsrc)
                else:
                    d['lit_n'] = len(pm)
                    d['lit_pm'] = sorted(pm)
            for c, d in sorted(merged.items(), key=lambda kv: (-kv[1]['n'], kv[0])):
                files[v].write('\t'.join([cid, mem, str(r.get('n_cells', '')), c, str(d['n']),
                                          ';'.join(d['shared_genes']), ';'.join(d['alias']),
                                          str(d['lit_n']), ';'.join(d['lit_pm']),
                                          str(d['lit_n_raw']), '']) + '\n')
    for v in variants:
        files[v].close()
        P(f'{v}: empty-ranking clusters={n_empty[v]}')
    open(f'{ROOT}/logs/score_log.txt', 'w').write('\n'.join(log) + f'\nran {datetime.datetime.now()}\n')
    print('E2_SCORE_DONE')

if __name__ == '__main__':
    main()
