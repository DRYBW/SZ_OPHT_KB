#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC4 分档误引率表 (PRE_REG §4): 抽检层=样本终判+Wilson 95%CI; 全检层=census。
终判合并: out/FINAL_adjudications.tsv (人工升级判读覆盖表, path+pmid 键) 缺省回退机械档。"""
import csv, json, math, collections, os

PLAN='/mnt/D/EyeKB/plans/kb_chain_audit_20260928'
MIS={'MISMATCH','CONFIRMED_MISQUOTE'}
def wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0,0.0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (p*100,max(0,(c-h))*100,min(1,(c+h))*100)

def load(p):
    if not os.path.exists(p): return []
    return list(csv.DictReader(open(p),delimiter='\t'))
inv=load(f'{PLAN}/out/S1_RESULTS.tsv')+load(f'{PLAN}/out/S2_F2_RESULTS.tsv')+\
    load(f'{PLAN}/out/S2_F3_RESULTS.tsv')+load(f'{PLAN}/out/S2_F4_RESULTS.tsv')
finals={}
for r in load(f'{PLAN}/out/FINAL_adjudications.tsv'):
    finals[(r['frame'],r['surface'],r['path'],r['pmid'])]=r
def fg(r):
    key=(r['frame'],r['surface'],r['path'],r['pmid'])
    if key in finals: return finals[key]['final_grade'], finals[key].get('note','')
    return r['grade'], ''
rows=[]
# 样本标记联接 (SAMPLE_S2_selection.tsv 为冻结抽样单)
skeys=set()
if os.path.exists(f'{PLAN}/out/SAMPLE_S2_selection.tsv'):
    for r in load(f'{PLAN}/out/SAMPLE_S2_selection.tsv'):
        skeys.add((r['frame'],r['surface'],r['path'],r['pmid']))
for r in inv:
    g,_=fg(r)
    r['s2_sample']='1' if (r['frame'],r['surface'],r['path'],r['pmid']) in skeys else r.get('s2_sample','0')
    rows.append({**r,'final':g})

out=[]
def addrow(layer,surface,kind_pop,n_pop,n_judged,k_mis,mode,extra=''):
    if n_judged:
        p,lo,hi=wilson(k_mis,n_judged)
    else: p=lo=hi=0.0
    out.append(dict(layer=layer,surface=surface,pop_n=n_pop,judged_n=n_judged,
                    misquote_n=k_mis,rate_pct=f'{p:.1f}',ci95_lo=f'{lo:.1f}',ci95_hi=f'{hi:.1f}',
                    mode=mode,note=extra))

# F1 census (排除 RETRACTED/NOT_CHECKABLE)
f1=[r for r in rows if r['frame']=='F1' and r['final'] not in ('RETRACTED','NOT_CHECKABLE')]
k=sum(1 for r in f1 if r['final'] in MIS)
addrow('S1','markers_v6/k9 evidence链','census-final',len(f1),len(f1),k,'full-inspection')
# F1 按文件
for surf in sorted(set(r['surface'] for r in f1)):
    sub=[r for r in f1 if r['surface']==surf]
    kk=sum(1 for r in sub if r['final'] in MIS)
    addrow('S1',surf,'census-final',len(sub),len(sub),kk,'full-inspection')
# F2
f2=[r for r in rows if r['frame']=='F2' and r['final']!='NOT_CHECKABLE']
k2=sum(1 for r in f2 if r['final'] in MIS)
addrow('S1','E2R白名单100对(link级)','census-final',len(f2),len(f2),k2,'full-inspection',
       '100对→%d条已解析链'%len(f2))
pairs=collections.defaultdict(set)
for r in f2:
    pairs[r['path']].add(r['final'])
pk=sum(1 for v in pairs.values() if v & MIS)
addrow('S1','E2R白名单(pair级)','census-final',len(pairs),len(pairs),pk,'full-inspection')
# F3/F4: 预注册口径 = 15% 样本终判; 附 census 机械
for fr,layer in (('F3','S2'),('F4','S2')):
    chk=[r for r in rows if r['frame']==fr and r['final'] not in ('NOT_CHECKABLE','RETRACTED')]
    smp=[r for r in chk if r.get('s2_sample')=='1']
    ks=sum(1 for r in smp if r['final'] in MIS)
    addrow(layer,fr+' 15%分层样本','sample-final+Wilson',len(chk),len(smp),ks,'sampling(seed=20260928)')
    kc=sum(1 for r in chk if r['final'] in MIS)
    addrow(layer,fr+' census机械档(补充)','census-mechanical',len(chk),len(chk),kc,'full-scan-supplement')
    # census 与 sample 偏离核对 (>10pp 必须解释 — 预注册条款)
    if smp and chk:
        ps=ks/len(smp); pc=kc/len(chk)
        if abs(ps-pc)>0.10:
            addrow(layer,fr+' ⚠ 偏离告警','','',0,0,'prereg-check',
                   f'sample {ps:.1%} vs census {pc:.1%} — 本卡须在 NOTE 解释')

with open(f'{PLAN}/out/RATE_TABLE.tsv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=['layer','surface','pop_n','judged_n','misquote_n','rate_pct','ci95_lo','ci95_hi','mode','note'] if 'kind_pop' not in out[0] else list(out[0].keys()),delimiter='\t')
    w.writeheader(); [w.writerow(r) for r in out]
print('== RATE_TABLE ==')
for r in out:
    print(f"{r['layer']:4} {r['surface'][:38]:40} pop={r['pop_n'] or '-':>6} n={r['judged_n'] or '-':>6} mis={r['misquote_n']:>4} rate={r['rate_pct']}% [{r['ci95_lo']},{r['ci95_hi']}] {r['mode']} {r['note'][:60]}")

# 撤证候选清单 (final MISMATCH 且带 kb 位置)
cand=[r for r in rows if r['final'] in MIS and r['frame'] in ('F1','F2','F3')]
with open(f'{PLAN}/out/ERRATUM_CANDIDATES.tsv','w',newline='') as fh:
    cols=['frame','surface','kind','path','cls','gene','pmid','note','title','rec_title','rec_journal','rec_year','channels','final','reason']
    w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t',extrasaction='ignore'); w.writeheader()
    for r in cand: w.writerow(r)
print('erratum candidates:',len(cand))
