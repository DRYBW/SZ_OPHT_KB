#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC5 建链期账本交叉核对 (PRE_REG §5b): 每条 S1(F1/F2) 错配/存疑/确诊链的 PMID
是否在当日检索账本中留有合法命中痕迹。痕迹源(全部只读):
  T1 kb7 efetch idlist (out/efetch_kb7/*.txt 的 PMIDS 行)
  T2 kb7 W4a hits (kb7_lit_hits.tsv 行级)
  T3 kb9 PMID_LEDGER.tsv (pmids 列) + ledgers/epmc_raw_v2/*.json (原始响应)
  T4 E2R title_resolution.jsonl (resolved_pmid)
  T5 RAGFIX work/ra_availability.tsv (09-28 新闭集 64)
分型: in-ledger(PMID在当日命中账本内=错位配对/搬运型) vs off-ledger(无痕迹=检索串扰/裸回填型)
输出 out/LEDGER_XREF.tsv (对 F1 全量 + F2 错配行 + 全部确诊误引)"""
import json, re, csv, os, collections

PLAN='/mnt/D/EyeKB/plans/kb_chain_audit_20260928'
K7='/mnt/D/EyeKB/plans/kb7_v6_20260925'
K9='/mnt/D/EyeKB/plans/kb9_ocs_20260927'
E2R='/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
RA='/mnt/D/EyeKB/plans/rag_fix_20260928'
PM=re.compile(r'\b(\d{6,9})\b')

# 痕迹库: pmid -> [sources]
led=collections.defaultdict(set)
for f in os.listdir(f'{K7}/out/efetch_kb7'):
    if f.endswith('.txt'):
        txt=open(f'{K7}/out/efetch_kb7/{f}',encoding='utf-8',errors='replace').read(600)
        ml=re.search(r"PMIDS:\s*\[([^\]]*)\]",txt)
        if ml:
            for p in re.findall(r'\d{6,9}',ml.group(1)):
                led[p].add(f'T1_kb7_efetch:{f[:-4]}')
for r in csv.DictReader(open(f'{K7}/out/kb7_lit_hits.tsv'),delimiter='\t'):
    if r['pmid'] and r['pmid']!='-':
        led[r['pmid']].add(f"T2_kb7_W4a:{r['gene']}|{r['class']}")
for r in csv.DictReader(open(f'{K9}/ledgers/PMID_LEDGER.tsv'),delimiter='\t'):
    for p in (r.get('pmids') or '').split(','):
        if p.strip(): led[p.strip()].add(f"T3_kb9_ledger:{r['term']}|{r['gene']}")
for root,_,files in os.walk(f'{K9}/ledgers/epmc_raw_v2'):
    for f in files:
        m2=re.match(r'(.+?)__(.+?)\.json',f)
        if not m2: continue
        try: d=json.load(open(os.path.join(root,f)))
        except Exception: continue
        s=json.dumps(d)
        for mm in re.finditer(r'"pmid"\s*:\s*"?(\d{6,9})',s):
            led[mm.group(1)].add(f"T3b_kb9_epmc_raw:{m2.group(1)}|{m2.group(2)}")
for l in open(f'{E2R}/data/e2r_title_resolution.jsonl'):
    r=json.loads(l)
    if r.get('resolved_pmid'): led[r['resolved_pmid']].add(f"T4_e2r_resolved:{(r.get('title') or '')[:40]}")
if os.path.exists(f'{RA}/work/ra_availability.tsv'):
    for r in csv.DictReader(open(f'{RA}/work/ra_availability.tsv'),delimiter='\t'):
        pid=(r.get('pmid') or r.get('PMID') or '').strip()
        if pid: led[pid].add('T5_ragfix_closed64')
# E1 起点账: sample20 已确诊名单 (用于标注)
CONF=set()
try:
    for r in json.load(open(f'{RA}/out/PMID_CHAIN_SAMPLE20_FINAL_ADJUDICATION.json'))['rows']:
        if r['adjudication'] in ('CONFIRMED_MISQUOTE','SUSPECT'): CONF.add(r['pmid'])
except Exception: pass

inv=list(csv.DictReader(open(f'{PLAN}/out/CHAIN_INVENTORY.tsv'),delimiter='\t'))
out=[]
for r in inv:
    if r['frame'] not in ('F1','F2'): continue
    if r['pmid'] and r['pmid'] in led:
        srcs='; '.join(sorted(led[r['pmid']]))[:300]; typ='in-ledger'
    elif r['pmid']:
        srcs=''; typ='off-ledger'
    else:
        srcs=''; typ='no-pmid'
    out.append({**r,'xref_type':typ,'xref_sources':srcs,
                'prior_confirmed':int(r['pmid'] in CONF)})
with open(f'{PLAN}/out/LEDGER_XREF.tsv','w',newline='') as fh:
    cols=list(out[0].keys()); w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t'); w.writeheader(); [w.writerow(r) for r in out]
c=collections.Counter((r['frame'],r['xref_type']) for r in out)
print('F1/F2 账本痕迹分布:',dict(c))
print('痕迹库覆盖 pmid 数:',len(led))
