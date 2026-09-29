#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selfcheck_comp_v0.py — EXPECTED_COMPOSITION_v0 只读自检 (旗标不出结论)
卡: t_fa03e1d7 | 全程只读输入: kb/composition 面 + plans/evalset 冻结件 + demo 冻结件
口径: 旗标=提示复核≠注释错误; 健康公开集旗标率>20% = 面太窄 (反向质检内建条款)
"""
import json, csv, collections, pathlib, math

KB=pathlib.Path("<EYEKB>/kb/composition")
EV=pathlib.Path("<EYEKB>/plans/evalset")
DEMO=pathlib.Path("<EYEKB>/plans/demo_gse165784/proc/v2")
face=json.load(open(KB/"EXPECTED_COMPOSITION_v0.json"))
RP={r["cell_type"]:r for r in face["pages"]["retina_normal_adult_human"]["rows"] if r["low_pct"] is not None}
OP={r["cell_type"]:r for r in face["pages"]["ocular_surface_normal_adult_human"]["rows"] if r["low_pct"] is not None}
NULLR={r["cell_type"]:r for r in face["pages"]["retina_normal_adult_human"]["rows"] if r["low_pct"] is None}

def counts_from_clusters(tsv, col=-1, delim="\t"):
    c=collections.Counter()
    for i,line in enumerate(open(tsv,encoding="utf-8")):
        parts=line.rstrip("\n").split(delim)
        if i==0: continue
        c[parts[col]]+=1
    return c

# ---------------- 面外身份映射 (off-panel identity disclosure)
OFFPANEL={"Pericytes":"Pericyte_vascular","Endothelium":"Endo_vascular",
 "retinal ganglion cell":None,"unannotated":"off_face_unassigned","unspecified":"off_face_unassigned",
 "Other_mapped":"off_face_unassigned","glial cell":"off_face_unclassified_glia",
 "T cell":"off_face_immune","macrophage":"off_face_immune","dendritic cell":"off_face_immune",
 "B cell":"off_face_immune","vascular associated smooth muscle cell":"off_face_vascular_smc",
 "pericyte":"Pericyte_vascular","smooth muscle cell":"off_face_vascular_smc",
 "epithelial cell":None}

REMAP10={"retinal rod cell":"Rod","retinal cone cell":"Cone","amacrine cell":"AC",
 "retinal horizontal cell":"HC","Mueller cell":"MG","astrocyte":"Astro","microglial cell":"Micro",
 "retinal pigment epithelial cell":"RPE","retinal ganglion cell":"RGC"}
BC_PREFIX=("ON-bipolar","OFF-bipolar","retinal bipolar")
# 真值列已用短名的数据集 (Q1/Q2/Q3/Q4/Q7 truth col)
SHORTS={"Rod","Cone","BC","AC","HC","RGC","MG","Astro","Micro","RPE"}
Q2_ALIAS={"Bipolar":"BC","Muller":"MG","Amacrine":"AC","Microglia":"Micro","Astrocytes":"Astro",
 "Horizontal":"HC","Ganglion":"RGC","Pericytes":"OFF:Pericytes","Endothelium":"OFF:Endothelium",
 "Rod":"Rod","Cone":"Cone"}

def to10(raw):
    if raw in SHORTS: return raw
    if raw in Q2_ALIAS: return Q2_ALIAS[raw]
    if raw in REMAP10: return REMAP10[raw]
    if raw.startswith(BC_PREFIX): return "BC"
    rl=raw.lower()
    if "progenitor" in rl or "psc" in rl or "organoid" in rl: return "OFF:"+raw
    for pat,ct in [("ganglion","RGC"),("horizontal","HC"),("bipolar","BC"),("amacrine","AC"),
                   ("rod cell","Rod"),("cone cell","Cone"),("mueller","MG"),("müller","MG"),
                   ("microglia","Micro"),("astrocyt","Astro"),("pigment epithel","RPE")]:
        if pat in rl: return ct
    return ("OFF:"+raw)

def qdef_counts(name):
    d=json.load(open(EV/"defs"/f"{name}.json"))
    return d, d.get("classes",{})

targets=[]  # (dataset, page, composition_pct, meta)
def pctmap(counts):
    tot=sum(counts.values())
    return {k:100.0*v/tot for k,v in counts.items()}, tot

# Q1
c1=counts_from_clusters(EV/"clustering/Q1_clusters.tsv")
m1=json.load(open(EV/"defs/maps_Q1.json"))["map"]
r1=collections.Counter()
for k,v in c1.items(): r1[to10(m1.get(k,"OFF:"+k))]+=v
targets.append(("Q1_Lukowski2019","retina",r1,"E1 人正常成人视网膜 (作者注释真值); snRNA"))
# Q2
c2=counts_from_clusters(EV/"clustering/Q2_clusters.tsv")
m2=json.load(open(EV/"defs/maps_Q2.json"))["map"]
r2=collections.Counter()
for k,v in c2.items():
    mv=m2.get(k,"OFF:"+k)
    if mv=="OTHER":
        # maps_Q2 把 Pericytes/Endothelium 折进 OTHER — 还原身份供 off-face 披露
        r2["OFF:"+k]+=v
    else: r2[to10(mv if not mv.startswith("OFF:") else mv)]+=v
targets.append(("Q2_GSE155288","retina",r2,"E1 人正常成人视网膜 (作者注释真值)"))
# Q3/Q4/Q5b/Q7/Q8
for name,page,meta,conv in [
 ("Q3_def","retina","E1 人正常 (Smart-seq 类, mapped_10class 真值)",None),
 ("Q4_def","retina","E1 人正常但 CD73/CD90 分选设计 (mapped_10class)",None),
 ("Q5b_def","retina","E2 GSE226108=HRCA resub 域内参照 (cell_type→10 映射)",True),
 ("Q7_def","retina","E4 小鼠 GSE243413 — 物种外, 面不适用 (仅行为记录)",None),
 ("Q8_def","retina","E5 GSE268630 胎儿 — 发育轴外, 面不适用 (仅行为记录; def.classes 全类合计=226,506=全文件 ✓)",None)]:
    d,cls=qdef_counts(name)
    if conv:
        mm=d["map"]; rr=collections.Counter()
        for k,v in cls.items():
            rr[to10(mm.get(k,"OFF:"+k)) if mm.get(k)!="EXCL" else "OFF:"+k]+=v
    else:
        rr=collections.Counter()
        for k,v in cls.items(): rr[to10(k)]+=v
    targets.append((name.replace("_def",""),page,rr,meta))
# Q6 眼表
c6=counts_from_clusters(EV/"clustering/Q6_clusters.tsv")
sup=json.load(open(EV/"defs/Q6_def.json"))["super_map"]
inv={lab:sc for sc,labs in sup.items() for lab in labs}
r6=collections.Counter()
for k,v in c6.items(): r6[inv.get(k,"OFF:"+k)]+=v
targets.append(("Q6_D002_sub100k","ocular_surface",r6,"E3 眼表 (面构建同源=循环参照, 只 sanity)"))
# Q9 demo 共识注释
N={0:1752,1:948,2:1080,3:790,4:830,5:1008,6:433,7:372,8:250,9:354,10:687,11:314,12:163,13:705,14:61,15:270,16:52}
LAB={0:"Micro",12:"MG(候选)",13:"OFF:Mac_Tissue",8:"Pericyte_vascular",15:"Endo_vascular",
 1:"OFF:Mac_MHCII",2:"OFF:Mac_Inflam",3:"OFF:Mac_DC",4:"OFF:Mono_Nonclass",5:"OFF:Mac_DAMLAM",
 6:"OFF:Mac_RRD",7:"OFF:Myofibroblast",9:"OFF:Tcell",10:"OFF:Mono_Classical",11:"OFF:Proliferating",
 14:"OFF:Plasma",16:"OFF:pDC"}
r9=collections.Counter()
for cid,n in N.items(): r9[LAB[cid]]+=n
targets.append(("Q9_GSE165784_demo_v2","retina",r9,"E6 PDR/RRD 纤维血管膜 共识注释草稿 (疾病手术材料; usage_scope: 不得对照健康面验收; 展示旗标行为用)"))

OUTOF_SCOPE={"Q7":"species=mouse (面=human)",
 "Q8":"organism_stage=fetal/developing (D-1 红线: 发育材料不得对照成人面判分)"}
DISEASE={"Q9_GSE165784_demo_v2":"疾病手术材料 (usage_scope 禁当达标对照)"}
HEALTHY={"Q1_Lukowski2019","Q2_GSE155288","Q3","Q4","Q5b"}

flag_rows=[]; summary=[]
for ds,page,comp,meta in targets:
    P = RP if page=="retina" else OP
    tot=sum(comp.values())
    pcts={k:100.0*v/tot for k,v in comp.items()}
    flagged=[]
    for ct,row in P.items():
        pct=pcts.get(ct,0.0)
        kind="face_row"
        if pct<row["low_pct"]: flagged.append((ct,pct,"BELOW",row["low_pct"],row["high_pct"])); kind="FLAG"
        elif pct>row["high_pct"]: flagged.append((ct,pct,"ABOVE",row["low_pct"],row["high_pct"])); kind="FLAG"
        flag_rows.append(dict(dataset=ds,page=page,row=ct,pct=round(pct,2),
            low=row["low_pct"],high=row["high_pct"],status="FLAG_"+("BELOW" if pct<row['low_pct'] else "ABOVE") if kind=="FLAG" else "in_range",
            in_scope=("no" if ds in OUTOF_SCOPE or ds in DISEASE else "yes"),note=meta))
    offs={k:v for k,v in pcts.items() if k.startswith("OFF") or k in NULLR or k.endswith("(候选)")}
    n_flag=sum(1 for x in flagged)
    scope_ok = ds in HEALTHY
    flag_rate = (n_flag/len(P)*100.0) if P else 0
    # MG(候选) demo 特殊并入 MG 统计? 保持独立行展示
    summary.append(dict(dataset=ds,page=page,total_cells=tot,n_flagged=n_flag,
        face_rows=len(P),flag_pct=round(flag_rate,1),reverseQC=("TRIGGER(>20%)" if scope_ok and flag_rate>20 else ("not_counted(disease/发育/循环)" if ds in OUTOF_SCOPE or ds in DISEASE or ds=="Q6_D002_sub100k" else "under")),
        flagged=[f"{c} {p:.1f}% vs [{lo},{hi}]" for c,p,_,lo,hi in flagged],
        off_face=[f"{k.split(':',1)[-1]} {v:.1f}%" for k,v in sorted(offs.items(),key=lambda x:-x[1])][:10],
        meta=meta))
    for ct,p in sorted(offs.items(),key=lambda x:-x[1]):
        name=ct.split(":",1)[-1]
        nullrow=NULLR.get(ct)
        flag_rows.append(dict(dataset=ds,page=page,row="OFF_FACE::"+name,pct=round(p,2),
            low=None,high=None,status="off_face_identity",
            in_scope=("no" if ds in OUTOF_SCOPE or ds in DISEASE else "yes"),
            note=("面含该身份但无区间(no_evidence 披露行)" if nullrow else "面外身份 — unexpected 披露, 非注释错误")))

with open(KB/"selfcheck/flags.tsv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["dataset","page","row","pct","low","high","status","in_scope","note"],delimiter="\t")
    w.writeheader(); w.writerows(flag_rows)
json.dump(summary,open(KB/"selfcheck/summary.json","w"),ensure_ascii=False,indent=1)
print(f"{'dataset':22s} {'flag':>4s}{'face':>5s} {'rate%':>6s}  reverseQC")
for s in summary:
    print(f"{s['dataset']:22s} {s['n_flagged']:>4d}{s['face_rows']:>5d} {s['flag_pct']:>6.1f}  {s['reverseQC']}")
    print("      flags:", "; ".join(s["flagged"]) or "-")
