#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC2 双通道题录取数 (PRE_REG §3 C1): NCBI eutils esummary 批量(180/req, 主) +
EPMC EXT_ID 批量(40/req, 副)。断点续跑: 已完成批次跳过。原始响应全留 ledgers/batches/。"""
import json, os, sys, time, urllib.request, urllib.parse

PLAN='/mnt/D/EyeKB/plans/kb_chain_audit_20260928'
LED=f'{PLAN}/ledgers'
os.makedirs(f'{LED}/batches',exist_ok=True)
PMIDS=[l.strip() for l in open(f'{PLAN}/work_pmids.txt') if l.strip()]
NOPROXY=urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA={'User-Agent':'EyeKB-KBCHAIN/1.0 (research; metadata-only)'}

def http(url, tries=5, sleep0=5):
    for a in range(tries):
        try:
            with NOPROXY.open(urllib.request.Request(url,headers=UA),timeout=90) as r:
                return r.read().decode('utf-8','replace')
        except Exception as e:
            print(f'  retry{a} {e}',file=sys.stderr); time.sleep(sleep0*(a+1))
    return ''

# ---------- pass 1: esummary ----------
done_es=set()
for f in os.listdir(f'{LED}/batches'):
    if f.startswith('esummary_') and f.endswith('.json'):
        done_es.update(int(x) for x in f[len('esummary_'):-len('.json')].split('_'))
B=180
chunks=[(i//B, PMIDS[i:i+B]) for i in range(0,len(PMIDS),B)]
es_map={}
# 先载入历史批
for idx,_ in chunks:
    fp=f'{LED}/batches/esummary_{idx}.json'
    if os.path.exists(fp):
        try:
            d=json.load(open(fp))
            res=d.get('result',{})
            for uid,v in res.items():
                if uid in ('uids','version','header','esummaryresult'): continue
                es_map[uid]={'title':v.get('title') or v.get('sorttitle') or '',
                             'journal':v.get('fulljournalname') or v.get('source') or '',
                             'pubdate':v.get('pubdate') or '',
                             'doi':next((a.get('value') for a in (v.get('articleids') or []) if a.get('key')=='doi'),''),
                             'channels':['eutils']}
        except Exception: pass
for idx,grp in chunks:
    if idx in done_es: continue
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&version=0.3&id='+','.join(grp)
    body=http(url)
    if not body:
        print(f'esummary batch {idx} FAILED',file=sys.stderr); continue
    fp=f'{LED}/batches/esummary_{idx}.json'
    open(fp,'w').write(body)
    try: d=json.loads(body)
    except Exception: print(f'batch {idx} unparsable',file=sys.stderr); continue
    res=d.get('result',{})
    for uid in grp:
        v=res.get(uid)
        if isinstance(v,dict):
            es_map[uid]={'title':v.get('title') or '',
                         'journal':v.get('fulljournalname') or v.get('source') or '',
                         'pubdate':v.get('pubdate') or '',
                         'doi':next((a.get('value') for a in (v.get('articleids') or []) if a.get('key')=='doi'),''),
                         'channels':['eutils']}
    print(f'[esummary] batch {idx} ok, mapped={len(es_map)}',flush=True)
    json.dump(es_map,open(f'{LED}/raw_eutils.jsonl.tmp','w'))
    time.sleep(0.5)
json.dump(es_map,open(f'{LED}/raw_eutils_map.json','w'),ensure_ascii=False)
print(f'PASS1 done: {len(es_map)}/{len(PMIDS)} eutils-resolved',flush=True)

# ---------- pass 2: EPMC 全量 (交叉通道) ----------
def epmc_batch(grp):
    q='(' + ' OR '.join(f'EXT_ID:{p}' for p in grp) + ') AND SRC:MED'
    url=('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+
         urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':str(min(100,len(grp)*2))}))
    body=http(url)
    recs={}
    if body:
        try:
            for r0 in json.loads(body).get('resultList',{}).get('result',[]) or []:
                pid=str(r0.get('pmid') or r0.get('pubid') or '')
                if not pid: continue
                recs[pid]={'title':r0.get('title',''),
                           'journal':((r0.get('journalInfo') or {}).get('journal') or {}).get('title',''),
                           'pubyear':r0.get('pubYear',''),
                           'doi':r0.get('doi',''),
                           'channels':['epmc']}
        except Exception as e: print('epmc parse err',e,file=sys.stderr)
    return recs, body

done_ep=set()
for f in os.listdir(f'{LED}/batches'):
    if f.startswith('epmc_') and f.endswith('.json'):
        done_ep.add(int(f[len('epmc_'):-len('.json')]))
ep_map={}
B2=40
chunks2=[(i//B2, PMIDS[i:i+B2]) for i in range(0,len(PMIDS),B2)]
for idx,_ in chunks2:
    fp=f'{LED}/batches/epmc_{idx}.json'
    if os.path.exists(fp):
        try:
            d=json.load(open(fp))
            for r0 in d.get('resultList',{}).get('result',[]) or []:
                pid=str(r0.get('pmid') or '')
                if pid:
                    ep_map[pid]={'title':r0.get('title',''),
                                 'journal':((r0.get('journalInfo') or {}).get('journal') or {}).get('title',''),
                                 'pubyear':r0.get('pubYear',''),'doi':r0.get('doi',''),'channels':['epmc']}
        except Exception: pass
for idx,grp in chunks2:
    if idx in done_ep: continue
    recs,body=epmc_batch(grp)
    if body:
        try: open(f'{LED}/batches/epmc_{idx}.json','w').write(body)
        except Exception: pass
        ep_map.update(recs)
        print(f'[epmc] batch {idx} ok, mapped={len(ep_map)}',flush=True)
    else:
        print(f'[epmc] batch {idx} FAILED',file=sys.stderr)
    time.sleep(0.8)
json.dump(ep_map,open(f'{LED}/raw_epmc_map.json','w'),ensure_ascii=False)

# ---------- merge ----------
merged={}
for pid in PMIDS:
    a=es_map.get(pid); b=ep_map.get(pid)
    m={}
    if a: m.update(a)
    if b:
        m.setdefault('title',b['title']); m.setdefault('journal',b['journal'])
        ch=set(m.get('channels',[]))|{'epmc'}; m['channels']=sorted(ch)
        if not m.get('pubdate'): m['pubdate']=b.get('pubyear','')
    if m: merged[pid]=m
json.dump(merged,open(f'{LED}/recs_merged.json','w'),ensure_ascii=False)
miss=[p for p in PMIDS if p not in merged]
print(f'PASS2 done: epmc={len(ep_map)}, merged={len(merged)}, unresolved={len(miss)}')
open(f'{LED}/unresolved_pmids.txt','w').write('\n'.join(miss))
