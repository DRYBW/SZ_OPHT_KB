# KB9REG-SB sandbox rerun of KB7-W2 (原样判据, 仅输出重定向; 只判不改)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB7-W2: B1 眼表细分词条基因计算（只读 agg_kb6b_v1.npz；KB6b 冻结常量复刻）。
口径: 空间内 CPM, floor 5, lfc>=1(火灾域全格), cons>=0.75(可算域, SD=study,donor 标签键, DR=2, MIND=10)。
目标(7): 结膜上皮分层 Conj_basal/Conj_suprabasal/Conj_superficial; 纤维细分 Limbus Fibroblasts/
         Limbus/Sclera Fibroblasts - C1/ - C2 / Sclera Fibroblasts。
火灾域: 其余 9 互斥组(pool>=500, 排除父组) + 同父兄弟亚型(pool>=500; <500 记录不否决)。
cons 精算域: pool 最大 3 兄弟 + pool>=5000 组。
输出 out/kb7_face_fullaudit.tsv, kb7_face_summary.tsv, kb7_face_dominant_study.tsv。
"""
import numpy as np, json

ROOT='/mnt/D/EyeKB/plans/kb9_ocs_20260927/register/recheck_kb7_cf'; OUTD=f'{ROOT}/out'
AGG='/mnt/D/EyeKB/plans/kb6b_face_20260925/out/agg_kb6b_v1.npz'
CPM_FLOOR, LFC_T, CONS_T, DR, MIND = 5.0, 1.0, 0.75, 2.0, 10
EPS=1e-9
TOPN=12; MINPOOL=500; BIGPOOL=5000

z=np.load(AGG, allow_pickle=True)
offs=json.loads(str(z['offs'])); cats=json.loads(str(z['layer_cats']))
grp_cats=list(cats['GROUP']); auth_cats=[str(a) for a in cats['AUTHOR']]
studies=[str(s) for s in cats['STUDY']]; donors=cats['DONOR']; ND=len(donors)
SUM=z['SUM'].astype(np.float64); TOT=z['TOT'].astype(np.float64); NC=z['NC'].astype(np.float64)
DET=z['DET'].astype(np.float64); SYM=z['symbol'].astype(str); BIOT=z['biotype'].astype(str)
NG,NA=len(grp_cats),len(auth_cats)
da_keys=z['da_keys'].astype(np.int64); dg_keys=z['dg_keys'].astype(np.int64); sg_keys=z['sg_keys'].astype(np.int64)
da_d,da_a = da_keys//NA, da_keys%NA
dg_d,dg_g = dg_keys//NG, dg_keys%NG
sg_s,sg_g = sg_keys//NG, sg_keys%NG
da_study=(da_d//ND).astype(int); dg_study=(dg_d//ND).astype(int)
usym=np.unique(SYM); sym2col={s:i for i,s in enumerate(usym)}
def sl(name):
    o_,n_=offs[name]; return slice(o_,o_+n_)
# ---- symbol 列空间 ----
import scipy.sparse as sp
inv=np.searchsorted(usym,SYM)
Msym=sp.csr_matrix((np.ones(SYM.size),(inv,np.arange(SYM.size))),shape=(usym.size,SYM.size))
SUMs=np.asarray(SUM@Msym.T); DETs=np.asarray(DET@Msym.T)
CPMg=SUMs[sl('GROUP')]/np.maximum(TOT[sl('GROUP')][:,None],EPS)*1e6
CPMa=SUMs[sl('AUTHOR')]/np.maximum(TOT[sl('AUTHOR')][:,None],EPS)*1e6
CPMdg=np.asarray(SUM[sl('DONORxGROUP')]@Msym.T)/np.maximum(TOT[sl('DONORxGROUP')][:,None],EPS)*1e6
CPMda=np.asarray(SUM[sl('DONORxAUTHOR')]@Msym.T)/np.maximum(TOT[sl('DONORxAUTHOR')][:,None],EPS)*1e6
CPMsg=np.asarray(SUM[sl('STUDYxGROUP')]@Msym.T)/np.maximum(TOT[sl('STUDYxGROUP')][:,None],EPS)*1e6
NCg=NC[sl('GROUP')]; NCa=NC[sl('AUTHOR')]; NCda=NC[sl('DONORxAUTHOR')]; NCdg=NC[sl('DONORxGROUP')]
detA=DETs[10:10+NA]/np.maximum(NCa[:,None],1)
bt_by_sym={}
for s,bt in zip(SYM,BIOT): bt_by_sym.setdefault(s,set()).add(bt)
def is_nc(s):
    bts=bt_by_sym.get(s,set())
    return bool(bts) and all(('RNA' in x or 'pseudo' in x or 'ncRNA'==x) for x in bts)

# ---- author -> 父组 (SD 细胞数对齐) ----
maxSD=int(max(da_d.max(),dg_d.max()))+1
Ma=np.zeros((NA,maxSD)); Mgc=np.zeros((NG,maxSD))
np.add.at(Ma,(da_a,da_d),NCda); np.add.at(Mgc,(dg_g,dg_d),NCdg)
score=Ma@Mgc.T
auth2grp=[int(x) for x in score.argmax(axis=1)]  # COUNTERFACTUAL: only parent assignment fixed
# 归属断言只对 7 目标做 (Corneal_Endo 等小组 donor 行 MIND 过滤导致对齐分偏低, 不影响目标集)

TARGETS=['Conj_basal','Conj_suprabasal','Conj_superficial',
         'Limbus Fibroblasts','Limbus/Sclera Fibroblasts - C1','Limbus/Sclera Fibroblasts - C2','Sclera Fibroblasts']
fha=open(f'{OUTD}/kb7_face_fullaudit.tsv','w')
fha.write('entry\tgene\tcpm_target\tdet_target\tneighbor\tnbr_level\tpool\tcpm_nbr\tlfc\tcons\tcons_donors\tnbr_ok\n')
fsm=open(f'{OUTD}/kb7_face_summary.tsv','w')
fsm.write('entry\tn_floor\tn_fullpass\trank\tgene\tbiotype\tcpm\tdet\tmin_lfc_fire\tn_fail_small_sib\tmin_cons\tverflag_nonchen_studies\tverflag_parent_group\n')
fdm=open(f'{OUTD}/kb7_face_dominant_study.tsv','w')
fdm.write('entry\tpool\tdominant_study\tstudy_cellcount\n')
nonchen=np.array(['chen' not in s for s in studies])

for T in TARGETS:
    aT=auth_cats.index(T); gT=auth2grp[aT]
    row=CPMa[aT]; poolT=int(NCa[aT])
    rowsT=np.where(da_a==aT)[0]
    stc={}
    for st,c in zip(da_study[rowsT],NCda[rowsT]): stc[studies[st]]=stc.get(studies[st],0)+int(c)
    domst=max(stc,key=stc.get)
    fdm.write(f"{T}\t{poolT}\t{domst}\t{';'.join(f'{k}={v}' for k,v in sorted(stc.items(),key=lambda x:-x[1]))}\n")
    sib_all=[a for a in range(NA) if auth2grp[a]==gT and a!=aT]
    sib_in=[a for a in sib_all if NCa[a]>=MINPOOL]; sib_small=[a for a in sib_all if NCa[a]<MINPOOL]
    otherG=[g for g in range(NG) if g!=gT and NCg[g]>=MINPOOL]
    cands=np.where(row>=CPM_FLOOR)[0]
    if len(cands)==0: print(T,'no candidates'); continue
    lfG=np.log2((row[cands]+EPS)/(CPMg[np.ix_(otherG,cands)]+EPS))       # (nG,nc)
    lfS=np.log2((row[cands]+EPS)/(CPMa[np.ix_(sib_in,cands)]+EPS)) if sib_in else np.zeros((0,len(cands)))
    lfX=np.log2((row[cands]+EPS)/(CPMa[np.ix_(sib_small,cands)]+EPS)) if sib_small else np.zeros((0,len(cands)))
    fire=np.vstack([lfG,lfS]); okfire=(fire>=LFC_T).all(0)
    # ---- donor cons: top3 兄弟 + >=BIGPOOL 组 ----
    ref_sibs=sorted(sib_in,key=lambda a:-NCa[a])[:3]
    ref_bigG=[g for g in otherG if NCg[g]>=BIGPOOL]
    okT=NCda[rowsT]>=MIND; rT=rowsT[okT]; kT=da_d[rT]; A=CPMda[np.ix_(rT,cands)]
    consM=[]; consName=[]; consNd=[]
    for a in ref_sibs:
        rr=np.where(da_a==a)[0]; rr=rr[NCda[rr]>=MIND]
        consNd.append((a,'sub',rr)); 
    for g in ref_bigG: consNd.append((g,'grp',np.where((dg_g==g)&(NCdg>=MIND))[0]))
    for idx_,lvl,rr in consNd:
        if len(rr)==0: consM.append(np.full(len(cands),np.nan)); consName.append('skip'); consNd.append(0); continue
        kk=(da_d if lvl=='sub' else dg_d)[rr]; B=(CPMda if lvl=='sub' else CPMdg)[np.ix_(rr,cands)]
        mapT={v:i for i,v in enumerate(kT)}
        pairs=[(mapT[x],i) for i,x in enumerate(kk) if x in mapT]
        if len(pairs)<MIND:
            consM.append(np.full(len(cands),np.nan)); consName.append((auth_cats[idx_] if lvl=='sub' else grp_cats[idx_])+f'(n{len(pairs)})'); continue
        ai=np.array([p[0] for p in pairs]); bi=np.array([p[1] for p in pairs])
        consM.append((A[ai]>=DR*B[bi]).mean(0))
        consName.append(auth_cats[idx_] if lvl=='sub' else grp_cats[idx_]+':grp')
    consM=np.vstack(consM)
    with np.errstate(invalid='ignore'):
        minc=np.nanmin(consM,axis=0)
    okcons=np.where(np.isnan(minc),True,minc>=CONS_T)
    idx=np.where(okfire&okcons)[0]
    mlb=fire[:,idx].min(0)
    order=idx[np.argsort(-mlb)]
    # verflag: 父组在全部 study 的行 + 非 chen study 中该 gene CPM>=1 数
    rows_parentG=np.where(sg_g==gT)[0]
    for rk,ci in enumerate(order[:TOPN],1):
        g=usym[cands[ci]]
        col=inv[cands[ci]] if False else None
        pg=CPMsg[rows_parentG]  # studies x (cands)
        vfcnt=int(((pg[nonchen][:,ci])>=1.0).sum())
        vgname='; '.join(f'{studies[st]}:{pg[st,ci]:.0f}' for st in np.where(nonchen)[0] if pg[st,ci]>=0.5)[:180]
        nsm=int((lfX[:,ci]<LFC_T).sum()) if lfX.size else 0
        mc=minc[ci]
        fsm.write(f"{T}\t{len(cands)}\t{len(idx)}\t{rk}\t{g}\t{'ncRNA' if is_nc(g) else 'coding'}\t{row[cands[ci]]:.1f}\t{detA[aT,cands[ci]]:.3f}\t{mlb[np.where(order==ci)[0][0]]:.3f}\t{nsm}\t{'skip' if np.isnan(mc) else format(mc,'.3f')}\t{vfcnt}\t{vgname}\n")
        for gi,gg in enumerate(otherG):
            cname=grp_cats[gg]
            cq=[i for i,nm in enumerate(consName) if nm==cname+':grp']
            cons='' if not cq else ('skip' if np.isnan(consM[cq[0],ci]) else f"{consM[cq[0],ci]:.3f}")
            ndq=''
            fha.write(f"{T}\t{g}\t{row[cands[ci]]:.1f}\t{detA[aT,cands[ci]]:.3f}\t{cname}\tgroup\t{int(NCg[gg])}\t{CPMg[gg,cands[ci]]:.2f}\t{lfG[gi,ci]:.3f}\t{cons}\t\t{'ok' if lfG[gi,ci]>=LFC_T else 'fail'}\n")
        for ai_,aa in enumerate(sib_in):
            cname=auth_cats[aa]
            cq=[i for i,nm in enumerate(consName) if nm==cname]
            cons='' if not cq else ('skip' if np.isnan(consM[cq[0],ci]) else f"{consM[cq[0],ci]:.3f}")
            fha.write(f"{T}\t{g}\t{row[cands[ci]]:.1f}\t{detA[aT,cands[ci]]:.3f}\t{cname}\tsibling\t{int(NCa[aa])}\t{CPMa[aa,cands[ci]]:.2f}\t{lfS[ai_,ci]:.3f}\t{cons}\t\t{'ok' if lfS[ai_,ci]>=LFC_T else 'fail'}\n")
        for ai_,aa in enumerate(sib_small):
            fha.write(f"{T}\t{g}\t{row[cands[ci]]:.1f}\t{detA[aT,cands[ci]]:.3f}\t{auth_cats[aa]}\tsibling_small\t{int(NCa[aa])}\t{CPMa[aa,cands[ci]]:.2f}\t{lfX[ai_,ci]:.3f}\tskip\t\t{'ok' if lfX[ai_,ci]>=LFC_T else 'fail'}\n")
    print(f"{T}: pool={poolT} floor={len(cands)} fullpass+cons={len(idx)} top={ [usym[cands[c]] for c in order[:8]] }", flush=True)
fha.close(); fsm.close(); fdm.close()
print('KB7-W2 done')
