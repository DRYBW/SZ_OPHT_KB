#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC7 误引机制归因表: 对 20 条确诊误引, 量化
 A. 前缀同形度 (错号 vs 当日合法 idlist 各号的最长公共前缀)
 B. note↔账本文本呼应 (note 与当日命中题名的 token 重合)
 C. 痕迹类型 (in/off-ledger)
→ 分型: 数字变异型 / 搬运替换型 / 裸回填无账型"""
import csv, re, json, collections
PLAN='/mnt/D/EyeKB/plans/kb_chain_audit_20260928'
K7='/mnt/D/EyeKB/plans/kb7_v6_20260925'
cand=list(csv.DictReader(open(f'{PLAN}/out/ERRATUM_CANDIDATES.tsv'),delimiter='\t'))
xref={(r['surface'],r['path'],r['pmid']):r['xref_type'] for r in csv.DictReader(open(f'{PLAN}/out/LEDGER_XREF.tsv'),delimiter='\t')}
for r in cand: r['xref_type']=xref.get((r['surface'],r['path'],r['pmid']),'?')
# 当日 idlist per gene|cls
idlist={}
import os
for f in os.listdir(f'{K7}/out/efetch_kb7'):
    if f.endswith('.txt'):
        txt=open(f'{K7}/out/efetch_kb7/{f}',errors='replace').read(600)
        ml=re.search(r"PMIDS:\s*\[([^\]]*)\]",txt)
        if ml: idlist[f[:-4]]=re.findall(r'\d{6,9}',ml.group(1))
# W4a hits per gene|class
w4a=collections.defaultdict(list)
for r in csv.DictReader(open(f'{K7}/out/kb7_lit_hits.tsv'),delimiter='\t'):
    if r['pmid'] and r['pmid']!='-': w4a[f"{r['gene']}|{r['class']}"].append((r['pmid'],r['title']))
def lcp(a,b):
    n=0
    for x,y in zip(a,b):
        if x==y: n+=1
        else: break
    return n
STOP=set('the of and in for with on from by a an to are is was were study'.split())
def toks(s): return set(w for w in re.findall(r'[a-z0-9\-]{4,}',(s or '').lower()) if w not in STOP)
rows=[]
for r in cand:
    gene=r['gene']; cls=r['cls'] or ''
    # 找该基因当日所有检索记录 (efetch idlist 文件名含 gene; W4a 行含 gene)
    ids=set(); titles=[]
    for k,v in idlist.items():
        if k.startswith(gene+'|') or k.startswith(gene+'_') or k.split('_')[0]==gene:
            ids.update(v)
    for k,hits in w4a.items():
        if k.split('|')[0].upper()==gene.upper():
            for p,t in hits: ids.add(p); titles.append((p,t))
    best=max(((lcp(r['pmid'],i),i) for i in ids if i!=r['pmid']), default=(0,''))
    note_toks=toks(r['note'])
    echo=max(((len(note_toks&toks(t)),p) for p,t in titles), default=(0,'')) if note_toks else (0,'')
    rows.append({**r,'ledger_ids':' '.join(sorted(ids))[:120],'prefix_max':best[0],'prefix_with':best[1],
                 'note_echo_best':echo[1],'note_echo_n':echo[0]})
with open(f'{PLAN}/out/MISQUOTE_MECHANISM.tsv','w',newline='') as fh:
    cols=list(rows[0].keys())
    w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t'); w.writeheader(); [w.writerow(r) for r in rows]
for r in rows:
    print(f"{r['gene']:8}{r['pmid']} off={'off-ledger' if r['xref_type']=='off-ledger' else 'in-ledger ':11} prefix={r['prefix_max']}~{r['prefix_with']:10} note_echo={r['note_echo_n']:2}{'→'+r['note_echo_best'] if r['note_echo_best'] else '':>12}  {(r['title'] or '')[:36]}")
