#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBC3 机械判级 + 分层 15% 抽检选取 (PRE_REG_kbchain_v1.0 §3-§4)。零 LLM。
输入: out/CHAIN_INVENTORY.tsv + ledgers/recs_merged.json
输出: out/S1_RESULTS.tsv out/S2_F3_RESULTS.tsv out/S2_F4_RESULTS.tsv
      out/SAMPLE_S2_selection.tsv out/ESCALATION_rows.tsv ledgers/SAMPLE_FREEZE.json"""
import json, csv, re, math, random, collections, html

PLAN='/mnt/D/EyeKB/plans/kb_chain_audit_20260928'
rows=list(csv.DictReader(open(f'{PLAN}/out/CHAIN_INVENTORY.tsv'),delimiter='\t'))
recs=json.load(open(f'{PLAN}/ledgers/recs_merged.json'))
SEED=20260928

EYE=re.compile(r'retin|ocular|eye|lens|corne|glaucoma|cataract|uvea|macula|photoreceptor|'
    r'ganglion|microglia|m[ü]ller glia|muller|amacrine|bipolar cell|RPE|vitreous|sclera|'
    r'choroid|conjunctiv|lacrimal|tear|retinal|ocular surface',re.I)
GENERIC=re.compile(r'single.cell|atlas|transcriptom|proteom|macrophage|immune|dendritic|review|'
    r'method|protocol|cell type|annotation',re.I)
CLASS_TERMS={
 'AC':r'\bamacrine','Astro':r'\bastrocyt|\bastroglia','BC':r'\bbipolar','HC':r'\bhorizontal',
 'MG':r'm[üi]ller|radial glia','Microglia':r'\bmicroglia|\bmicroglial|microgl',
 'RPE':r'retinal pigment epithel|\bRPE\b','RGC':r'ganglion cell|\bRGC','Pericyte':r'\bpericyte',
 'SMC':r'smooth muscle','ConjEpithelium':r'conjunctiv','Melanocyte':r'melanocyte|melanoma|uveal',
 'Endo':r'endotheli','Epithelium':r'epitheli','Fibroblast':r'fibroblast|stroma',
 'Cone':r'\bcone|opsin','Rod':r'\brod\b|photoreceptor','Keratocytes':r'keratocyte|corneal',
 'Neuron':r'neuron|neuronal','Glia':r'glia','Immune':r'immune|macrophage|lymphocyte',
}
def class_rx(cls):
    for k,v in CLASS_TERMS.items():
        if cls and k.lower() in cls.lower(): return v
    return None
STOP=set('the of and in for with on from by a an to are is was were study studies cells cell using'.split())
def toks(s): return set(w for w in re.findall(r'[a-z0-9\-]{4,}',(s or '').lower()) if w not in STOP)
def norm(t): return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',html.unescape(t or '').lower())).strip()
def rt_clean(t):
    s=norm(t)
    s=re.sub(r'^(19|20)\d{2}\s+','',s)          # 年份前缀剥离 (E2R PREREG v1.2 同款机修)
    s=re.sub(r'\s+(sup|sub|italicref)$','',s)
    s=re.sub(r'\b(sup|sub)\b','',s)             # <sup> 等标记残留
    return re.sub(r'\s+',' ',s).strip()
def rt_match(a,b):
    a,b=rt_clean(a),rt_clean(b)
    if not a or not b: return False
    if a==b: return True
    m=min(len(a),len(b))
    if m>=30 and (a[:m]==b[:m] or a.startswith(b) or b.startswith(a)): return True
    ta,tb=set(a.split()),set(b.split())
    return len(ta&tb)/max(1,len(ta|tb))>=0.70

def year_bucket(y):
    y=str(y or '')
    m=re.search(r'(19|20)\d{2}',y)
    if not m: return 'unk'
    yr=int(m.group(0))
    if yr<2020: return '<2020'
    if yr<=2022: return '2020-22'
    if yr==2023: return '2023'
    if yr==2024: return '2024'
    return '2025+'

out=[]
RETRACTED={'41349939'}  # _raggap_errata_v1 已撤证, 出分母 (PRE_REG §1)
for r in rows:
    # 机修: 从 path 恢复 class 上下文 (提取器实现缺陷修复; 判据词族表不动)
    if not r['cls']:
        mpath=re.search(r'/(?:new_terms|marker_blocks|subtype_anchor_layer|stromal_repair|'
                        r'lacrimal_increment|lacrimal_[a-z_]+|anchor_layer|increment|core|'
                        r'superficial_repair|basal_repair)/([^/\[]+)',r['path'])
        if mpath: r['cls']=mpath.group(1)
    if r['pmid'] in RETRACTED:
        r2={**r,'rec_title':'','rec_journal':'','rec_year':'','channels':'','grade':'RETRACTED',
            'c1':0,'c2':0,'eye':0,'cls_hit':0,'note_echo':0,'diverge':0,
            'reason':'已由 _raggap_errata_v1.json 撤证, 出框','yb':'unk'}
        out.append(r2); continue
    pmid=r['pmid']; rec=recs.get(pmid) if pmid else None
    title=(rec or {}).get('title',''); journal=(rec or {}).get('journal','')
    year=str((rec or {}).get('pubdate','') or '')
    ch=','.join((rec or {}).get('channels',[]))
    gene=r['gene'].upper(); cls=r['cls']
    blob=title+' '+journal
    c1 = bool(rec and title.strip())
    c2 = bool(gene) and bool(re.search(r'\b'+re.escape(gene)+r'\b',blob,re.I))
    eye = bool(EYE.search(blob))
    crx=class_rx(cls)
    cclass = bool(crx) and bool(re.search(crx,blob,re.I))
    note=r['note']
    # note 呼应
    ntoks=toks(note); htoks=toks(blob)
    echo=len(ntoks & htoks)
    diverge=False
    if len(ntoks)>=5 and echo==0 and c1:
        diverge=True
    gen = bool(GENERIC.search(blob))
    kind=r['kind']
    if kind=='R4_index':
        if not c1: grade='MISMATCH'; reason='C1 fail (PMID 不可解析)'
        elif rt_match(r['title'], title): grade='GOOD'; reason='C1+存储题名与题录 rt 全等/前缀'
        elif toks(r['title']) and not (toks(r['title'])&toks(title)):
            grade='MISMATCH'; reason='PMID 存在但题录≠存储题名 (ID-题名错位)'
        else:
            grade='SUSPECT'; reason='题名部分重合需人工'
    elif kind=='R5_pcx_nopmid':
        grade='NOT_CHECKABLE'; reason='pmid_context 无 PMID 字段 (存储缺陷面, E2R 发现①)'
    elif kind=='R4_index_malformed':
        grade='NOT_CHECKABLE'; reason='索引行格式异常, 登记'
    elif kind=='R5_whitelist_pair':
        rt = rt_match(r['title'], title) if r['title'] else False
        if not c1: grade='MISMATCH'; reason='C1 fail (反解 PMID 不可解析)'
        elif not rt: grade='MISMATCH'; reason='反解 PMID 题录≠E2R 存储题名 (round-trip 断)'
        elif c2 or cclass or eye: grade='GOOD'; reason=f'round-trip 全等 + {"gene" if c2 else ("class" if cclass else "eye")}'
        elif gen: grade='SUSPECT'; reason='可解但题录语境不特异(generic)'
        else: grade='SUSPECT'; reason='可解但题录与断言词面无关联'
    else:  # R1/R2/R3 (F1/F3)
        if kind=='R2_prov_ctx' and '非该基因的逐条引用' in r['extra']:
            c2=False  # 类级语境链, 基因词面豁免 (预注册豁免)
            if not c1: grade='MISMATCH'; reason='C1 fail'
            elif eye or cclass: grade='GOOD'; reason='C1+类语境(眼/类词)命中(基因豁免)'
            elif gen: grade='SUSPECT'; reason='类语境链但题录 generic'
            else: grade='MISMATCH'; reason='类级语境断言但题录完全异域'
        elif not c1:
            grade='MISMATCH'; reason='C1 fail (双通道均无记录)'
        elif c2 or eye:
            if diverge and not c2: grade='SUSPECT'; reason='题录眼语境但 note 零呼应(DIVERGE 旗)'
            else: grade='GOOD'; reason=f'C1+{"基因词面" if c2 else "眼科语境"}'
        elif gen: grade='SUSPECT'; reason='generic 方法/图谱类可作旁证, 不判误引'
        else: grade='MISMATCH'; reason='题录异域且无基因/语境词 = 误引候选'
    out.append({**r,'rec_title':title[:180],'rec_journal':journal[:80],'rec_year':year[:8],
                'channels':ch,'grade':grade,'c1':int(c1),'c2':int(bool(c2)),'eye':int(eye),
                'cls_hit':int(bool(cclass)),'note_echo':echo,'diverge':int(diverge),
                'reason':reason,'yb':year_bucket(year)})

# ---------- S1/S2 输出 ----------
def wr(path,rs):
    cols=['frame','surface','kind','path','cls','gene','pmid','note','title','extra',
          'rec_title','rec_journal','rec_year','channels','grade','c1','c2','eye','cls_hit',
          'note_echo','diverge','reason','yb']
    with open(path,'w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t'); w.writeheader()
        for r in rs: w.writerow({c:r.get(c,'') for c in cols})
wr(f'{PLAN}/out/S1_RESULTS.tsv',[r for r in out if r['frame']=='F1'])
wr(f'{PLAN}/out/S2_F2_RESULTS.tsv',[r for r in out if r['frame']=='F2'])   # F2 也随 S1 全检
wr(f'{PLAN}/out/S2_F3_RESULTS.tsv',[r for r in out if r['frame']=='F3'])
wr(f'{PLAN}/out/S2_F4_RESULTS.tsv',[r for r in out if r['frame']=='F4'])

# ---------- 分层 15% 抽检 (F3/F4, 仅可核实例) ----------
chk=[r for r in out if r['frame'] in ('F3','F4') and r['grade'] not in ('NOT_CHECKABLE','RETRACTED')]
strata=collections.defaultdict(list)
for r in chk:
    strata[(r['frame'],r['surface'],r['yb'])].append(r)
rng=random.Random(SEED)
sel=[]; freeze={}
for key in sorted(strata):
    members=strata[key]
    # 基因多样性优先: 按 gene/cls 打散后轮抽
    order=members[:]; rng.shuffle(order)
    seen_g=set(); pref=[]; rest=[]
    for r in order:
        g=(r['gene'] or r['cls'])
        if g and g not in seen_g: seen_g.add(g); pref.append(r)
        else: rest.append(r)
    draws=pref+rest
    n=max(1,math.ceil(0.15*len(members)))
    chosen=draws[:n]
    for r in chosen: r['s2_sample']=1
    sel+=chosen
    freeze['|'.join(key)]={'layer_n':len(members),'drawn':n}
for r in chk:
    r.setdefault('s2_sample',0)
print(f'S2 checkable={len(chk)} sampled={len(sel)} strata={len(strata)}')
with open(f'{PLAN}/out/SAMPLE_S2_selection.tsv','w',newline='') as fh:
    cols=list(sel[0].keys()); w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t'); w.writeheader()
    for r in sel: w.writerow(r)
json.dump({'seed':SEED,'strata':freeze,'sampled_n':len(sel),'checkable_n':len(chk)},
          open(f'{PLAN}/ledgers/SAMPLE_FREEZE.json','w'),indent=1)

# ---------- 升级判读队列: 全部 MISMATCH + 全部 DIVERGE + 全部 SUSPECT(F1/F2/F3 无条件; F4 仅样本) ----------
def in_esc(r):
    if r['grade']=='MISMATCH': return True
    if r.get('diverge')==1: return True
    if r['grade']=='SUSPECT':
        if r['frame'] in ('F1','F2','F3'): return True
        if r.get('s2_sample')==1: return True
    return False
esc=[r for r in out if in_esc(r)]
with open(f'{PLAN}/out/ESCALATION_rows.tsv','w',newline='') as fh:
    cols=['frame','surface','kind','path','cls','gene','pmid','note','title','rec_title','rec_journal','rec_year','channels','grade','reason','s2_sample']
    w=csv.DictWriter(fh,fieldnames=cols,delimiter='\t',extrasaction='ignore'); w.writeheader()
    for r in esc: w.writerow(r)
print('escalation rows:',len(esc))
gc=collections.Counter((r['frame'],r['grade']) for r in out)
for k,v in sorted(gc.items()): print(k,v)
# 更新各 RESULTS 带 s2_sample 标记
wr(f'{PLAN}/out/S2_F3_RESULTS.tsv',[r for r in out if r['frame']=='F3'])
wr(f'{PLAN}/out/S2_F4_RESULTS.tsv',[r for r in out if r['frame']=='F4'])
print('KBC3 done')
