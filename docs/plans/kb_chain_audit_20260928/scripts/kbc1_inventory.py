#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC1 全库链账盘点 (PRE_REG_kbchain_v1.0 §1-2 规则 R1-R5)
输出 out/CHAIN_INVENTORY.tsv + 计数摘要。零网络零 LLM。"""
import json, re, os, sys, csv

ROOT='/mnt/D/EyeKB'
PLAN=f'{ROOT}/plans/kb_chain_audit_20260928'
MK=f'{ROOT}/kb/markers'
PM=re.compile(r'PMID[:=]?\s*(\d{6,8})')
RETRACTED={'41349939'}  # _raggap_errata_v1.json 已撤证, 出框
INST=[]

def add(frame, surface, kind, path, cls, gene, pmid, note, title='', extra=''):
    INST.append(dict(frame=frame, surface=surface, kind=kind, path=path, cls=cls or '',
                     gene=gene or '', pmid=pmid, note=(note or '')[:300],
                     title=title, extra=extra))

# ---------- R1/R2/R3: kb/markers/*.json (非 _ 前缀) ----------
F1_FILES={'markers_v6_retina_repair.json','markers_v6_face_increment.json',
          'markers_v6_lacrimal_increment.json','markers_k9_ocs_increment.json'}
BLACK={'version','created','prereg_sha','card','sha'}  # 叙述字段黑名单

def scan_markers(fname):
    frame = 'F1' if fname in F1_FILES else 'F3'
    d=json.load(open(os.path.join(MK,fname),encoding='utf-8'))
    captured=set()  # (path,id) R1/R2 已捕获, R3 去重
    def walk(o, path, cls_hint, gene_hint):
        if isinstance(o, dict):
            g = o.get('gene') if isinstance(o.get('gene'),str) else gene_hint
            c = o.get('class') or o.get('cls') or o.get('term') or cls_hint
            if isinstance(g,str) and isinstance(o.get('evidence'),list):
                for i,e in enumerate(o['evidence']):
                    if isinstance(e,dict) and e.get('type')=='pmid':
                        m=PM.search(str(e.get('id','')))
                        if m:
                            captured.add((f'{path}/evidence[{i}]/id', m.group(1)))
                            add(frame,fname,'R1_evidence',f'{path}/evidence[{i}]',c,g,m.group(1),e.get('note',''))
            if o.get('type')=='pmid_context' and o.get('id'):
                m=PM.search(str(o['id']))
                if m and (f'{path}/id', m.group(1)) not in captured:
                    captured.add((f'{path}/id', m.group(1)))
                    add(frame,fname,'R2_prov_ctx',path,c,g or gene_hint,m.group(1),
                        o.get('note',''), extra=str(o.get('semantics','')))
            # R3: 字符串值内嵌 (evidence/id 已在 captured 中; 其余字段扫)
            for k,v in o.items():
                if isinstance(v,str) and k not in BLACK:
                    if k=='id' and (f'{path}/id',) :  # R1/R2 的 id 字段
                        pass
                    for m in PM.finditer(v):
                        if (f'{path}/{k}', m.group(1)) in captured: continue
                        add(frame,fname,'R3_note_embed',f'{path}/{k}',c,g,m.group(1),v[:200])
                # 键名即细胞类/基因 (provenance[cell][gene])
                nk = k if isinstance(k,str) else ''
                walk(v, f'{path}/{nk}', c if isinstance(o.get(k),(dict,list)) and k in ('provenance',) else (nk if _looks_class(nk,c) else c),
                     g or (nk if _looks_gene(nk) and k!='markers' and _parent_is_prov(path) else None))
        elif isinstance(o, list):
            for i,v in enumerate(o):
                walk(v, f'{path}[{i}]', cls_hint, gene_hint)
    # provenance 结构专用展开 (cell->gene->recs)
    prov = d.get('provenance')
    if isinstance(prov,dict):
        for cell,genes in prov.items():
            if not isinstance(genes,dict): continue
            for gene,recs in genes.items():
                if not isinstance(recs,list): continue
                for i,r in enumerate(recs):
                    if not isinstance(r,dict): continue
                    p=f'/provenance/{cell}/{gene}[{i}]'
                    if r.get('type')=='pmid_context':
                        if r.get('id'):
                            m=PM.search(str(r['id']))
                            if m:
                                captured.add((f'{p}/id', m.group(1)))
                                add(frame,fname,'R2_prov_ctx',p,cell,gene,m.group(1),r.get('note',''),
                                    extra=str(r.get('semantics',''))[:120])
                        else:
                            add(frame,fname,'R5_pcx_nopmid',p,cell,gene,'',r.get('query',''),
                                title='||'.join(t for t in (r.get('top_titles') or []) if t))
                    for k,v in r.items():
                        if isinstance(v,str) and k not in BLACK and k!='id':
                            for m in PM.finditer(v):
                                add(frame,fname,'R3_note_embed',f'{p}/{k}',cell,gene,m.group(1),v[:200])
    walk(d,'',None,None)
    return captured

CLS_WORDS=set('Endo Endo_Patho Pericyte SMC Fibroblast Myofibroblast Mono_Classical Mono_Nonclassical Mac_Tissue Mac_DAM_LAM Microglia APC_MHCII_high cDC1 cDC2 pDC T NK B Plasma Granulocyte Proliferating Keratocytes CornealEndothelium Endothelium Epithelium'.split())
def _looks_class(k, hint): return k in CLS_WORDS
def _looks_gene(k): return bool(re.fullmatch(r'[A-Z0-9\-]{2,12}', k)) and k not in ('Core','ID','Note')
def _parent_is_prov(path): return '/provenance/' in path

for f in sorted(os.listdir(MK)):
    if f.endswith('.json') and not f.startswith('_'):
        scan_markers(f)

# markers/*/detail 深层: 上面 walk 已覆盖任意深度 evidence; markers dict (gene 列表) 无 PMID 自然跳过

# ---------- R3 其余 kb 面: priors / baselines / literature_db notes ----------
def scan_text(frame, surface, fpath):
    txt=open(fpath,encoding='utf-8',errors='replace').read()
    for m in PM.finditer(txt):
        ln = txt.count('\n',0,m.start())+1
        ctx = txt[max(0,m.start()-160):m.end()+160].replace('\n',' ')
        add(frame,surface,'R3_text',f':{ln}','','',m.group(1),ctx[:250])

for base,frame,surf in [(f'{ROOT}/kb/priors','F3','priors'),(f'{ROOT}/kb/baselines','F3','baselines')]:
    for root,_,files in os.walk(base):
        for f in sorted(files):
            if f.endswith(('.json','.md','.tsv')) and 'concepts.tsv' not in f:
                scan_text(frame,surf,os.path.join(root,f))
scan_text('F3','litdb_notes',f'{ROOT}/kb/literature_db/KBADD_KERATOCYTE_NOTES_20260924.md')

# ---------- R4: vk_literature_index ----------
VKROW=re.compile(r'PMID(\d{6,8})\s*\((\d{4})\)\s*(.+?)\s*—\s*\*(.+?)\*\s*(\[[a-z,]+\])?')
vkpage=re.compile(r'PMID\d{6,8}')
for f in sorted(os.listdir(f'{ROOT}/kb/vk_literature_index')):
    if not f.endswith('.md'): continue
    txt=open(f'{ROOT}/kb/vk_literature_index/{f}',encoding='utf-8').read()
    for ln,line in enumerate(txt.splitlines(),1):
        m=VKROW.search(line)
        if m and m.group(1):
            add('F4','vk_index','R4_index',f'{f}:{ln}','','',m.group(1),
                f'year={m.group(2)} species={m.group(5)}', title=m.group(3).strip(), extra=m.group(4))
        else:
            m2=vkpage.search(line)
            if m2 and f!='INDEX.md':
                add('F4','vk_index','R4_index_malformed',f'{f}:{ln}','','',m2.group(0)[4:],
                    line[:200])

# ---------- R5: E2R 白名单 100 对 ----------
wl=json.load(open(f'{ROOT}/plans/e2r_s5audit_20260927/data/e2r_whitelist_S5b.json'))
S5B=set(wl['S5b'])
pcx={}
for l in open(f'{ROOT}/plans/e2r_s5audit_20260927/data/e2r_pcx_pairs.jsonl'):
    r=json.loads(l); pcx[f"{r['lib']}::{r['cls']}::{r['gene']}"]=r
res={}
for l in open(f'{ROOT}/plans/e2r_s5audit_20260927/data/e2r_title_resolution.jsonl'):
    r=json.loads(l); res[r['title']]=r
n_wl=0
for key in sorted(S5B):
    r=pcx.get(key)
    if not r: add('F2','e2r_whitelist','R5_whitelist_orphan',key,'','','', 'pair missing'); continue
    cls,gene=key.split('::')[1],key.split('::')[2]
    pms=[]; titles=[]
    for t in (r.get('title1'),r.get('title2')):
        if t and t in res and res[t].get('resolved_pmid'):
            rr=res[t]
            pms.append(rr['resolved_pmid']); titles.append(t)
    if not pms:
        add('F2','e2r_whitelist','R5_whitelist_unresolved',key,cls,gene,'',r.get('query',''),
            title='||'.join(x for x in (r.get('title1'),r.get('title2')) if x)); continue
    for pmid,t in zip(pms,titles):
        n_wl+=1
        add('F2','e2r_whitelist','R5_whitelist_pair',key,cls,gene,pmid,r.get('query',''),title=t)

# ---------- 汇总 ----------
os.makedirs(f'{PLAN}/out',exist_ok=True)
COLS=['frame','surface','kind','path','cls','gene','pmid','note','title','extra']
with open(f'{PLAN}/out/CHAIN_INVENTORY.tsv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=COLS,delimiter='\t'); w.writeheader()
    for r in INST: w.writerow({c:r[c] for c in COLS})

import collections
cnt=collections.Counter((r['frame'],r['kind']) for r in INST)
uniq=collections.Counter(r['frame'] for r in INST)
print('== 实例计数 by frame ==')
for k,v in sorted(cnt.items()): print(f'  {k}: {v}')
print('== 框合计 ==', dict(uniq))
for fr in ('F1','F2','F3','F4'):
    ids={r['pmid'] for r in INST if r['frame']==fr and r['pmid']}
    print(f'{fr}: instances={uniq[fr]} distinct_pmids={len(ids)}')
allids={r['pmid'] for r in INST if r['pmid']} - RETRACTED
print('TOTAL distinct fetch universe (excl retracted):', len(allids))
with open(f'{PLAN}/work_pmids.txt','w') as fh:
    fh.write('\n'.join(sorted(allids)))
print('retracted-in-frame hits (should be 0):', sum(1 for r in INST if r['pmid'] in RETRACTED))
