#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 既有 PMID 链随机抽 20 条 EPMC 题录复核 (误引率落账)
- 总体 = 全部 kb/markers/*.json (含 :prov 结构) 中 evidence type=pmid 的 (file, entry_path, gene, PMID) 实例
  排除: 勘误件已撤证的 41349939 实例 (已在 _raggap_errata_v1.json); 本卡新增的 r1 链不属"既有" (未回写词条)
- 抽样 = random.Random(20260928).sample (种子预注册=本卡号)
- 复核 = EPMC EXT_ID 题录逐字; 机械一致性三档:
    CONSISTENT = 题录存在 且 (标题含该基因符号 或 标题/期刊含眼科语境词族)
    UNCLEAR    = 题录存在, 标题无基因符号且无眼科词族 (通用文献可作机制/方法证据, 不判误引, 落账人工可查)
    MISMATCH   = 题录不存在 或 标题与该词条语境完全异域 (泌尿/肿瘤等非眼且基因也不在题录 = 误引候选)
- 发现新误引: 只登记到输出 (扩范围修=禁止, 任务书红线)
输出: out/PMID_CHAIN_SAMPLE20.tsv + .json
"""
import json, os, re, random, time, urllib.request, urllib.parse

KB = "/mnt/D/EyeKB/kb/markers"
PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "OcularKB-RAG/0.3"}
PM_RE = re.compile(r"PMID[:\s]*(\d{6,9})")
FILES = [f for f in os.listdir(KB) if f.endswith(".json") and not f.startswith("_")]

EYE_PAT = re.compile(r"retin|ocular|eye|lens|corne|glaucoma|cataract|uvea|macula|"
                     r"photoreceptor|ganglion|microglia|Müller|muller|amacrine|bipolar cell|"
                     r"RPE|vitreous|sclera|choroid|conjunctl|lacrimal|tear", re.I)
GENERIC_OK = re.compile(r"single.cell|atlas|transcriptom|proteom|macrophage|immune|dendritic|"
                        r"review|method|protocol", re.I)


def harvest():
    inst = []
    def walk(o, path, fname):
        if isinstance(o, dict):
            g = o.get("gene") if isinstance(o.get("gene"), str) else None
            if g and isinstance(o.get("evidence"), list):
                for e in o["evidence"]:
                    if isinstance(e, dict) and e.get("type") == "pmid" and e.get("id"):
                        m = PM_RE.search(str(e["id"]))
                        if m:
                            inst.append({"file": fname, "path": path, "gene": g.upper(),
                                         "pmid": m.group(1), "note": e.get("note", "")})
            for k, v in o.items():
                walk(v, f"{path}/{k}", fname)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]", fname)
    for f in sorted(FILES):
        walk(json.load(open(os.path.join(KB, f), encoding="utf-8")), "", f)
    return inst


def epmc_rec(pmid, tries=5):
    url = EPMC + "/search?" + urllib.parse.urlencode(
        {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core", "pageSize": "1"})
    for i in range(tries):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            res = d.get("resultList", {}).get("result", [])
            if not res:
                return {"found": False}
            r0 = res[0]
            return {"found": True, "title": r0.get("title", ""),
                    "journal": ((r0.get("journalInfo") or {}).get("journal") or {}).get("title", ""),
                    "pubyear": r0.get("pubYear", "")}
        except Exception:
            time.sleep(4 * (i + 1))
    return {"found": None, "error": "epmc_unreachable"}


def main():
    inst = harvest()
    pop = [x for x in inst if x["pmid"] != "41349939"]
    print(f"total pmid-evidence instances={len(inst)}, population(excl retracted)={len(pop)}, "
          f"distinct files={len(set(x['file'] for x in pop))}")
    rng = random.Random(20260928)
    sample = rng.sample(pop, 20)
    rows, n_con, n_unc, n_mis = [], 0, 0, 0
    for s in sample:
        time.sleep(0.6)
        rec = epmc_rec(s["pmid"])
        if rec.get("found") is None:
            verdict = "EPMC_UNREACHABLE"
        elif not rec.get("found"):
            verdict = "NOT_IN_EPMC(登记, 可能 PubMed-only, 不计误引—按 §6.4 通道注记另查)"
        else:
            title = rec["title"]
            gene_in = bool(re.search(r"\b" + re.escape(s["gene"]) + r"\b", title, re.I))
            eye_in = bool(EYE_PAT.search(title + " " + rec.get("journal", "")))
            gen_ok = bool(GENERIC_OK.search(title))
            if gene_in or eye_in:
                verdict = "CONSISTENT"
            elif gen_ok:
                verdict = "UNCLEAR"
            else:
                verdict = "MISMATCH"
        if verdict == "CONSISTENT":
            n_con += 1
        elif verdict == "UNCLEAR":
            n_unc += 1
        elif verdict == "MISMATCH":
            n_mis += 1
        rows.append({**s, "epmc": rec, "verdict": verdict})
        print(f"{s['file']}::..{s['path'][-40:]} {s['gene']} PMID:{s['pmid']} → {verdict}")
    os.makedirs(f"{PLAN}/out", exist_ok=True)
    with open(f"{PLAN}/out/PMID_CHAIN_SAMPLE20.tsv", "w") as f:
        f.write("file\tgene\tpmid\tverdict\tepmc_title\tjournal\tpubyear\tpath\n")
        for r in rows:
            f.write(f"{r['file']}\t{r['gene']}\t{r['pmid']}\t{r['verdict']}\t"
                    f"{(r['epmc'].get('title') or '').replace(chr(9),' ')}\t"
                    f"{(r['epmc'].get('journal') or '').replace(chr(9),' ')}\t"
                    f"{r['epmc'].get('pubyear','')}\t{r['path']}\n")
    json.dump({"seed": 20260928, "population_n": len(pop), "sample_n": 20,
               "counts": {"CONSISTENT": n_con, "UNCLEAR": n_unc, "MISMATCH": n_mis},
               "mismatch_rate": n_mis / 20, "rows": rows},
              open(f"{PLAN}/out/PMID_CHAIN_SAMPLE20.json", "w"), indent=1, ensure_ascii=False)
    print(f"DONE consistent={n_con} unclear={n_unc} mismatch={n_mis} rate={n_mis/20:.0%}")


if __name__ == "__main__":
    main()
