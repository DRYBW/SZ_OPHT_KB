#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E1-1 分数采集：直调 eyekb_core.query_marker（与 MCP 同一代码路径，server 不启不停不改）。
ON（默认 60 类，主口径）/ OFF（EYEKB_ACT_V6=0，43 类敏感性）两态 × 290 簇。
产物: data/e1_scores_{ON,OFF}.tsv, data/e1_leak_table.tsv, logs/collect_log.txt
冻结件只读；本脚本不写 kb/、mcp_server/、生产评分链任何文件。"""
import json, os, sys, io, datetime

ROOT = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'
EV = '/mnt/D/EyeKB/plans/evalset'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')

def canon(c):
    return c.split('::')[-1] if '::' in c else c

def main():
    log = []
    def P(*a):
        s = ' '.join(str(x) for x in a)
        log.append(s); print(s, flush=True)

    rows = [json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl')]
    assert len(rows) == 290, len(rows)
    cmap = json.load(open(f'{ROOT}/e1_class_map.json'))['map']
    lineage = json.load(open(f'{ROOT}/e1_leak_lineage.json'))

    # corpus membership (v2.0 = search_literature default db)
    corpus = set()
    for l in open('/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09/papers.jsonl'):
        corpus.add(str(json.loads(l).get('paper_id')))
    src = {m: set(v.get('source_pmids') or []) for m, v in lineage['members'].items()}
    channel = {}
    for m in src:
        s = src[m]
        if not s:
            channel[m] = 'unresolved' if m not in ('Q9',) else 'n/a'
        else:
            channel[m] = 'open' if (s & corpus) else 'closed'
    P('channel:', channel)

    import eyekb_core as ec
    states = {}
    raw_top3 = {}  # OFF 态别名级 top3（一致性自检验 OFF 原行为，不经并类）
    for state, envval in (('ON', None), ('OFF', '0')):
        if envval is None:
            os.environ.pop('EYEKB_ACT_V6', None)
        else:
            os.environ['EYEKB_ACT_V6'] = envval
        classes = ec.query_marker()['cell_types']
        states[state] = len(classes)
        P(f'state {state}: n_classes={len(classes)}')
        out = open(f'{ROOT}/data/e1_scores_{state}.tsv', 'w')
        out.write('\t'.join(['cluster_id', 'member', 'n_cells', 'cand_canon', 'n_shared',
                             'shared_genes', 'alias_rows', 'lit_papers_n', 'lit_pmids']) + '\n')
        n_empty = 0
        for r in rows:
            cid, mem = r['cluster_id'], r['member']
            syms = r.get('top_genes_sym') or []
            genes = r.get('top_genes') or []
            # 建卷原规则 (kb2_mcp_v2.py L54): symbol 优先, 空则回退原 ID, 取前 10
            top = [(s or g) for g, s in zip(genes, syms)][:10]
            resp = ec.query_marker(genes=top)
            rank = resp.get('celltype_ranking') or []
            # canonical merge, max n_shared
            merged = {}
            for x in rank:
                c = canon(x['cell_type'])
                n = int(x['n_shared'])
                if c not in merged or n > merged[c]['n_shared']:
                    merged[c] = {'n_shared': n, 'shared_genes': x.get('shared_genes') or [],
                                 'alias': [x['cell_type']]}
                else:
                    merged[c]['alias'].append(x['cell_type'])
            if state == 'OFF':
                raw_top3[cid] = [(x['cell_type'], int(x['n_shared'])) for x in rank[:3]]
            # lit per canonical (unique pmids)
            litm = {}
            for k, ents in (r.get('lit') or {}).items():
                c = canon(k)
                pms = set()
                for e in ents or []:
                    pm = str(e.get('pmid') or '').strip()
                    if pm and pm.lower() != 'none':
                        pms.add(pm)
                litm[c] = litm.get(c, set()) | pms
            # candidate universe = merged ∪ lit keys; assert lit ⊆ merged
            extra_lit = [c for c in litm if c not in merged and litm[c]]
            if extra_lit:
                P('WARN lit-cand-without-marker', cid, extra_lit)
                for c in extra_lit:
                    merged[c] = {'n_shared': 0, 'shared_genes': [], 'alias': [c]}
            if not merged:
                n_empty += 1
                continue
            for c, d in sorted(merged.items(), key=lambda kv: (-kv[1]['n_shared'], kv[0])):
                pms = sorted(litm.get(c, set()))
                out.write('\t'.join([cid, mem, str(r.get('n_cells', '')), c, str(d['n_shared']),
                                     ';'.join(d['shared_genes']), ';'.join(d['alias']),
                                     str(len(pms)), ';'.join(pms)]) + '\n')
        out.close()
        P(f'{state}: clusters_with_empty_ranking={n_empty}')

    # OFF 一致性自检: 别名级重算 top3 vs digest 存档 kb_marker_ranking (建卷 OFF 时代)
    mismatch = 0; checked = 0
    for r in rows:
        arch = [(x['cell_type'], int(x['n_shared'])) for x in (r.get('kb_marker_ranking') or [])]
        if not arch: continue
        checked += 1
        mine = raw_top3.get(r['cluster_id'], [])
        if sorted(arch, key=lambda t: (-t[1], t[0])) != sorted(mine, key=lambda t: (-t[1], t[0])):
            mismatch += 1
            if mismatch <= 5: P('OFF-MISMATCH', r['cluster_id'], 'arch=', arch, 'mine=', mine)
    P(f'OFF-consistency: checked={checked} mismatch={mismatch}')

    # 泄漏审计表
    lk = open(f'{ROOT}/data/e1_leak_table.tsv', 'w')
    lk.write('\t'.join(['cluster_id', 'member', 'channel', 'lit_total_papers', 'cited_pmids',
                        'lit_cites_source', 'evidence_self_reference', 'marker_channel_ref']) + '\n')
    mref = {'Q5b': 'strong(HRCA-derived panels)', 'Q6': 'strong(D002-borne face panels)',
            'Q3': 'weak(HRCA constituent)', 'Q4': 'weak(HRCA constituent)'}
    for r in rows:
        cid, mem = r['cluster_id'], r['member']
        pms = set()
        for k, ents in (r.get('lit') or {}).items():
            for e in ents or []:
                pm = str(e.get('pmid') or '').strip()
                if pm and pm.lower() != 'none': pms.add(pm)
        ch = channel[mem]
        cites = sorted(pms & src[mem]) if src[mem] else []
        if not pms:
            sr = '无'
        elif ch in ('open', 'closed'):
            sr = '有' if cites else '无'
        elif ch == 'n/a':
            sr = '无'
        else:
            sr = '不可判'
        lk.write('\t'.join([cid, mem, ch, str(len(pms)), ';'.join(sorted(pms)),
                            ';'.join(cites), sr, mref.get(mem, 'none')]) + '\n')
    open(f'{ROOT}/logs/collect_log.txt', 'w').write('\n'.join(log) + f'\nwrote_at {datetime.datetime.now()}\n')
    print('E1_COLLECT_DONE')

if __name__ == '__main__':
    os.environ.pop('EYEKB_ACT_V6', None)
    main()
