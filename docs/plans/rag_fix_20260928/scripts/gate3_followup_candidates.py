#!/usr/bin/env python3
"""gate3 残差 25 单元的追加轮候选表 (供 PI 勾选; 本卡不下任何一篇)
- 16 mismatch 基因: top_pmids 取 s5 检查表, EPMC 现查 OA/PMCID
- 8 备选104已含: 直接标"备选轮"
- LILRB2: 无候选, 维持缺口 (撤证设计)
"""
import csv, json, re, time, urllib.request, urllib.parse
RAGGAP="/mnt/D/EyeKB/plans/rag_gap_20260928"
PLAN="/mnt/D/EyeKB/plans/rag_fix_20260928"
OP=urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA={"User-Agent":"OcularKB-RAG/0.3"}
E="https://www.ebi.ac.uk/europepmc/webservices/rest"

mismatch=["ATP8B4","CALD1","CDH8","CST1","CST4","FAM135A","FBXL7","FCER1G","GPR143","GRM5",
          "LMOD1","LRRTM3","MUC7","PTPRK","SAMSN1","SHISA6"]
rows=[]
for f in ["epmc_gene_check.tsv","epmc_gene_check_extra.tsv"]:
    with open(f"{RAGGAP}/out/{f}",encoding="utf-8") as fh:
        for r in csv.DictReader(fh,delimiter="\t"):
            rows.append(r)
by={}
for r in rows:
    key=(r["gene"].upper(), r["ctx"])
    if r["gene"].upper() in mismatch and key not in by:
        by[key]=r
closed=set(l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip())
out=[]
for (g,ctx),r in sorted(by.items()):
    tops=[p for p in (r.get("top_pmids") or "").split(",") if p][:3]
    rec={"gene":g,"ctx":ctx,"n_eye_hits":r.get("n_eye_hits"),"top_candidates":tops,"oa":[],"already_in":[]}
    for p in tops:
        if p in closed:
            rec["already_in"].append(p); continue
        try:
            u=E+"/search?"+urllib.parse.urlencode({"query":f"EXT_ID:{p} AND SRC:MED","format":"json","pageSize":"1"})
            d=json.loads(OP.open(urllib.request.Request(u,headers=UA),timeout=45).read())
            r0=d["resultList"]["result"][0] if d["resultList"]["result"] else {}
            rec["oa"].append({"pmid":p,"isOpenAccess":r0.get("isOpenAccess"),"pmcid":r0.get("pmcid")})
            time.sleep(0.6)
        except Exception as e:
            rec["oa"].append({"pmid":p,"error":repr(e)[:60]})
    out.append(rec)
with open(f"{PLAN}/out/GATE3_FOLLOWUP_candidate_table.md","w") as f:
    f.write("# gate3 残差追加轮候选（本卡零下载, 供 PI 勾选）\n\n")
    f.write("| gene | ctx | EPMC 眼命中 | top 候选 PMID | OA 状态 | 已在闭集 |\n|---|---|---|---|---|---|\n")
    for rec in out:
        oa="; ".join(f"{o.get('pmid')}:{o.get('isOpenAccess','?')}" for o in rec["oa"])
        f.write(f"| {rec['gene']} | {rec['ctx']} | {rec['n_eye_hits']} | "
                f"{','.join(rec['top_candidates'])} | {oa} | {','.join(rec['already_in']) or '-'} |\n")
    f.write("\n另 8 单元 ('C8ORF76/COL19A1/CPNE5/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B') 备选104表已含,\n")
    f.write("走既有 TIER_A_approval_list.md 备选勾选即可; LILRB2 单元维持缺口 (撤证设计, 无诚实候选)。\n")
json.dump(out,open(f"{PLAN}/out/GATE3_FOLLOWUP_candidate_table.json","w"),indent=1,ensure_ascii=False)
print("followup table written:",len(out),"genes")
