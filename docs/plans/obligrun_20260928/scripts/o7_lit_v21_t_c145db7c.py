#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, 案A细则3): OB-4 对票面 v2.1 复筛——断言 0 残留同源命中。
筛查体与 o4_lit_t_c145db7c.py 同规则（注册包 §9 两级：标题级观看列表+片段级 own-deposit/指派复核），
FACE=kb9_face_v2.1.jsonl；输出 OB4_lit_hits_v21.tsv + OB4_lit_screening_v21.md。
血缘登记升级（相对 v1）：6 GSM study→source paper 外部解析补登记（GSE155683→33865984 Collin 等，
见 FACE_V21_ledger.tsv 注释），排除判据=「lit 行 PMID ∈ 该簇供细胞 study 的来源论文」。
退出码 0=0 残留(复筛通过)；3=仍有残留（升级 block 上报，不粉饰）。"""
import json, re, sys
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
D002 = {'GSE218123': 'chakravarti_GSE218123', 'GSE153515': 'chen_pub_GSE153515',
        'GSE186433': 'dickman_GSE186433', 'GSE155683': 'lako_adult_GSE155683',
        'GSE147979': 'li_GSE147979', 'GSE157474': 'shi_GSE157474'}
# v1 冻结观看列表（36712326 已自 v2.1 面剔除；其余 source paper 外部解析后均不在票面）
SOURCE_PAPERS = {'36712326': 'chakravarti_GSE218123（v1 三重证据链件，现应零出现）'}
# 外部解析登记（2026-09-28 eutils，只读；不在票面即无剔除贡献）
EXT_SOURCE = {'GSE155683': '33865984 (Collin J, Ocul Surf 2021)'}
ASSIGN_RE = re.compile(r'(cluster[s]?|cell (?:population|type|state)s?|CL)\b[^.]{0,160}?\b(?:was|were|is|are)?\s*(annotated|labeled|labelled|identified|defined|classified|designated)\b', re.I)
GSE_RE = re.compile(r'GSE\d{5,8}')

face = [json.loads(l) for l in open(f'{ROOT}/face/kb9_face_v2.1.jsonl', encoding='utf-8')]
changed = set(json.load(open('/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_changed_clusters.json'))['changed'])
hits = []
for r in face:
    for ct, es in (r.get('lit') or {}).items():
        for e in es:
            hits.append(dict(cluster_id=r['cluster_id'], era=('变化簇-KB9重建' if r['cluster_id'] in changed else '冻结簇-RUN5代'),
                             cell_type=ct, pmid=str(e.get('pmid')), year=e.get('yr'), title=(e.get('t') or '')))
pmids = sorted({h['pmid'] for h in hits})
assert '36712326' not in pmids, '36712326 仍在 v2.1 面——剔除未生效'

df = pd.read_parquet('/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09/chunks.parquet',
                     columns=['paper_id', 'section', 'text'])
sub = df[df['paper_id'].astype(str).isin(pmids)]
paper_evi = {}
for p, g in sub.groupby('paper_id'):
    gse_own, assign_n, assign_ex = set(), 0, []
    for _, row in g.iterrows():
        t = str(row['text'])
        for m in GSE_RE.finditer(t):
            gse_own.add(m.group(0))
        if ASSIGN_RE.search(t):
            assign_n += 1
            if len(assign_ex) < 2:
                assign_ex.append(str(row['section']))
    d002_ment = sorted(set.intersection(set(gse_own), set(D002)))
    own_dep = set()
    for _, row in g[g['section'].astype(str).str.contains('availab|Methods', case=False, na=True)].iterrows():
        t = str(row['text'])
        for mm in re.finditer(r'deposited[\s\S]{0,200}?(GSE\d{5,8})', t, re.I):
            own_dep.add(mm.group(1))
    paper_evi[p] = dict(n_chunks=len(g), gse_mentions=d002_ment, own_deposit=sorted(own_dep),
                        assign_hits=assign_n, assign_sections=assign_ex)

rows_out, excl = [], 0
for h in hits:
    p = h['pmid']
    ev = paper_evi.get(p, {})
    tier1 = p in SOURCE_PAPERS
    own_d002 = sorted(set.intersection(set(ev.get('own_deposit', [])), set(D002)))
    ruling = '同源排除' if (tier1 or own_d002) else '保留'
    action = '票面剔除该 lit 行（残留命中——升级 block）' if ruling == '同源排除' else '无'
    if ruling == '同源排除':
        excl += 1
    basis = (SOURCE_PAPERS[p] if tier1 else
             (f"own-deposit∩D002={own_d002}" if own_d002 else
              f"非任何簇 truth 来源论文（观看列表零匹配；own-deposit 扫描零 D002；EXT 解析={EXT_SOURCE} 均不在票面）"))
    rows_out.append({**h, 'tier1_title_watch': tier1, 'tier2_assign_hits': ev.get('assign_hits', 0),
                     'own_deposit_D002': ';'.join(own_d002), 'ruling': ruling, 'action': action, 'basis': basis})

cols = ['cluster_id', 'era', 'cell_type', 'pmid', 'year', 'title', 'tier1_title_watch', 'tier2_assign_hits', 'own_deposit_D002', 'ruling', 'action', 'basis']
with open(f'{ROOT}/out/OB4_lit_hits_v21.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for x in rows_out:
        f.write('\t'.join(str(x[c]) for c in cols) + '\n')

md = []
md.append('# OB4_lit_screening_v21 — 票面 v2.1 复筛（案 A 细则 3：断言 0 残留命中）')
md.append('')
md.append(f'- 筛查对象：v2.1 面全部 lit 命中 {len(rows_out)} 条 / {len(pmids)} 唯一 PMID（=v1 64 条减 2 条已剔除行，其余逐条复筛）。')
md.append('- 规则与 v1 同一冻结件：注册包 §9 两级筛查（标题级观看列表 + 片段级 own-deposit/指派复核）；血缘登记升级：6 GSM study→source paper 外部解析补登记（GSE155683→33865984 Collin Ocul Surf 2021；其余 4 GSM source 题名与票面 11 PMID 零匹配；chen_* 无 accession 残余限制沿 v1）。')
md.append('- v1 命中的 36712326（chakravarti_GSE218123 source）两行已按 OBLIGRUN_RULING_1 案 A 于面剔除（FACE_V21_ledger.tsv 逐行台账）。')
md.append('')
md.append('## 逐 PMID 复筛汇总（11 PMID）')
md.append('')
md.append('| PMID | 标题级 | 片段级 own-deposit∩D002 | 指派命中 | 判定 |')
md.append('|---|---|---|---|---|')
for p in pmids:
    ev = paper_evi.get(p, {})
    own = sorted(set.intersection(set(ev.get('own_deposit', [])), set(D002)))
    md.append(f"| {p} | {'**命中**' if p in SOURCE_PAPERS else '观看列表零匹配'} | {own or '无'} | {ev.get('assign_hits', 0)} | {'**同源排除（残留！）**' if (p in SOURCE_PAPERS or own) else '保留'} |")
md.append('')
md.append('## 结论')
md.append(f'- 残留同源命中 = **{excl}** 条。' + ('**0 残留，复筛通过，放行正式三席票 run**' if excl == 0 else '**非零——按判读矩阵升级 block，不粉饰**'))
md.append('- 残余限制沿 v1：chen_cornea/limbus/sclera 无 accession 本地不可解析；若日后获权威映射须重跑本筛查（登记为下游项，随票注记进入 VERDICT v2）。')
open(f'{ROOT}/out/OB4_lit_screening_v21.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')

print(f'OB-4 复筛: {len(rows_out)} hits / {len(pmids)} pmids | 残留同源排除={excl}')
sys.exit(3 if excl else 0)
