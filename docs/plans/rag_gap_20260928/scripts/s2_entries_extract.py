#!/usr/bin/env python3
"""RAGGAP step 2 — 词条×逐基因×证据链 抽取（全 KB marker 库 + KB9 build 件）。
两种形态:
  (A) {"gene": G, "evidence": [ ... ]}      —— v6/face/lacrimal/k9 core+marker_blocks
  (B) provenance[entry][gene] = [ev,...]    —— v5 / membrane 溯源层
产出 out/kb_entries_genes.tsv: library, entry, gene, pmids(cited), pmid_context, has_canonical, has_data_driven
"""
import json, os, re

KB = '/mnt/D/EyeKB/kb/markers'
K9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927/build/markers_k9_ocs_increment.json'
OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'

PM_RE = re.compile(r'PMID[:\s]*(\d{6,9})')

def ev_collect(evs):
    """evidence list -> dict(pmids set, ctx set, canonical bool, data bool, other notes)"""
    r = dict(pmids=set(), ctx=set(), canonical=False, data=False)
    for e in evs or []:
        if isinstance(e, dict):
            t = e.get('type', '')
            if t == 'pmid' and e.get('id'):
                m = PM_RE.search(str(e['id']))
                if m: r['pmids'].add(m.group(1))
            elif t == 'pmid_context' and e.get('id'):
                m = PM_RE.search(str(e['id']))
                if m: r['ctx'].add(m.group(1))
            elif t == 'canonical':
                r['canonical'] = True
            elif t == 'data_driven':
                r['data'] = True
            # canonical note 里也可能内嵌 PMID (v5 provenance "HRCA v1 正文点名 (PMID:41578023)")
            for blob in (str(e.get('note','')), str(e.get('query',''))):
                for m in PM_RE.finditer(blob):
                    r['ctx'].add(m.group(1))
    return r

rows = []  # (library, entry, gene, ev)

def walk(o, lib, entry_path):
    """形态 A 的通用递归"""
    if isinstance(o, dict):
        if 'gene' in o and isinstance(o.get('gene'), str) and 'evidence' in o:
            rows.append((lib, entry_path, o['gene'].strip().upper(), ev_collect(o['evidence'])))
        for k, v in o.items():
            if k in ('version','created','card','prereg_sha','scope','note','data_note_ambient','data_note_acinar_zymogen_gap'):
                continue
            child_entry = entry_path
            if isinstance(v, dict) and k and not k.startswith('_'):
                # 容器键若是类名（大写/驼峰开头且值含 core/evidence/stats）视为词条层
                child_entry = f"{entry_path}::{k}" if entry_path else k
            walk(v, lib, child_entry)
    elif isinstance(o, list):
        for v in o: walk(v, lib, entry_path)

FILES = [
    ('retina_v4.1', f'{KB}/markers_v4.1_clean.json'),
    ('retina_v5',   f'{KB}/markers_v5_retina_interneuron.json'),
    ('membrane_v1', f'{KB}/markers_membrane_v1.json'),
    ('retina_v6',   f'{KB}/markers_v6_retina_repair.json'),
    ('face_v6',     f'{KB}/markers_v6_face_increment.json'),
    ('lacrimal_v6', f'{KB}/markers_v6_lacrimal_increment.json'),
    ('kb9',         K9),
]

for lib, path in FILES:
    if not os.path.exists(path):
        print('MISSING', path); continue
    d = json.load(open(path))
    # 普通列表词条: {markers|panels: {class: [genes]}}
    for container in ('markers',):   # panels=面板→类名映射，非基因
        c = d.get(container)
        if isinstance(c, dict):
            for entry, genes in c.items():
                if isinstance(genes, list) and genes and all(isinstance(x, str) for x in genes):
                    for g in genes:
                        rows.append((lib, entry, g.strip().upper(),
                                     dict(pmids=set(), ctx=set(), canonical=False, data=False)))
    # 形态 B: provenance[entry][gene]
    prov = d.get('provenance') or d.get('ols_evidence') or {}
    if isinstance(prov, dict):
        for entry, genes in prov.items():
            if not isinstance(genes, dict): continue
            for g, evs in genes.items():
                if isinstance(evs, list):
                    rows.append((lib + ':prov', entry, g.strip().upper(), ev_collect(evs)))
    # 形态 A: 全文档递归 (markers / *_increment / marker_blocks / new_terms / panels)
    # 排除 provenance 避免双计
    d2 = {k: v for k, v in d.items() if k not in ('provenance', 'ols_evidence')}
    walk(d2, lib, '')

# 去重: 同 (lib, entry, gene) 合并
merged = {}
for lib, entry, g, ev in rows:
    key = (lib, entry, g)
    if key in merged:
        merged[key]['pmids'] |= ev['pmids']; merged[key]['ctx'] |= ev['ctx']
        merged[key]['canonical'] |= ev['canonical']; merged[key]['data'] |= ev['data']
    else:
        merged[key] = ev

with open(os.path.join(OUT, 'kb_entries_genes.tsv'), 'w') as w:
    w.write('library\tentry\tgene\tcited_pmids\tpmid_context\thas_canonical\thas_data_driven\n')
    for (lib, entry, g), ev in sorted(merged.items()):
        w.write(f"{lib}\t{entry}\t{g}\t{','.join(sorted(ev['pmids']))}\t{','.join(sorted(ev['ctx']))}\t{1 if ev['canonical'] else 0}\t{1 if ev['data'] else 0}\n")

libs = {}
for (lib, entry, g) in merged: libs.setdefault(lib, set()).add(entry)
for lib in sorted(libs): print(lib, 'entries:', len(libs[lib]), 'rows:', sum(1 for k in merged if k[0]==lib))
print('total gene-rows:', len(merged), '| distinct genes:', len({g for (_,_,g) in merged}))
