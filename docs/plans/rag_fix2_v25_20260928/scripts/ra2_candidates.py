#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 (t_6848d3de) stage ra2_candidates: 16 基因候选检索 + 三条件题录核验 + 白名单
判据=BRIEF_RAGFIX2.md §3 (冻结):
  检索: EPMC REST '"SYM" AND CTX词族 AND SPECIES:"HUMAN"' pageSize=75 (词族逐字=RAGGAP s5);
        登记别名另跑同口径查询。symbol 引号查询命中=EPMC 全文域含 symbol (gate text 路强先验);
        别名查询命中仅作题录线索, 可兑现仍须 sym∈摘要 或 OA全文+sym 在检索域。
  C1 三档: T1=sym∈标题∧ctx∈标题; T2=sym∈标题∧ctx∈摘要; T3=ctx∈标题∧sym∈摘要;
          别名档 T1a/T2a/T3a 同构; 链路口=kb自引 PMID ∧ ctx∈标题 (语义一致)。
  C2 PMID 可核: EXT_ID 单篇回查 (链路口内做; 检索候选选入后在 fetch 台账再核一次)。
  C3 ∉HRCA_EXCL ∪ v2.4在库 ∪ closed64 ∪ 本白名单已选(防双计)。
  可兑现: fulltext(oa=Y∧pmcid∧sym∈摘要∨qsrc=sym) > abstract_token(sym∈摘要) > chain; 全无→不入围。
输出: work/ra2_candidates_raw.json + out/RA2_candidate_ledger.tsv
     + out/RA2_WHITELIST.tsv + out/closed_set_ra2_pmids.txt
"""
import json, re, time, urllib.request, urllib.parse, csv

PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
P1 = "/mnt/D/EyeKB/plans/rag_fix_20260928"
V24 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09"
E = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OP = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "OcularKB-RAG/0.3 (RAGFIX2 whitelist)"}

CTX = {
    'retina': '(retina OR retinal OR photoreceptor OR macula OR "retinal pigment")',
    'membrane': '(eye OR ocular OR retinal OR choroid OR "optic nerve")',
    'face': '(cornea OR corneal OR conjunctiva OR conjunctival OR "ocular surface" OR limbal)',
    'lacrimal': '(lacrimal OR tear OR "dry eye" OR meibomian)',
    'kb9': '(ocular OR eye OR conjunctiva OR cornea OR "ocular surface")',
}
CTX_TERMS = {
    'retina': [r'retina\w*', r'photoreceptor\w*', r'macula\w*', r'retinal\s+pigment\w*'],
    'membrane': [r'\beye\b', r'ocular\w*', r'retina\w*', r'choroid\w*', r'optic\s+nerve'],
    'face': [r'corneal?', r'conjunctival', r'ocular\s+surface', r'limbal', r'sclera'],
    'lacrimal': [r'lacrimal', r'\btears?\b', r'dry\s+eye', r'meibomian'],
    'kb9': [r'ocular\w*', r'\beye\b', r'conjunctival?', r'corneal?'],
}
# 检索别名词组 (EPMC 引号查询用) 与 标题/摘要判别正则分开
ALIAS_SEARCH = {
    'CST1': ['cystatin', 'cystatins'], 'CST4': ['cystatin', 'cystatins'],
    'FCER1G': ['Fc epsilon RI', 'IgE receptor'],
    'GRM5': ['mGluR5', 'metabotropic glutamate receptor 5'],
    'GPR143': ['OA1'],
    'CALD1': ['caldesmon'], 'LMOD1': ['leiomodin'],
}
ALIAS_RE = {
    'CST1': [r'cystatins?'], 'CST4': [r'cystatins?'],
    'MUC7': [r'mucins?\b(?:\s*\d| proteins?)?'],
    'FCER1G': [r'fce\s?ri\w*', r'fc\s?epsilon\s?ri\w*', r'ige\s+receptor\w*'],
    'GRM5': [r'mglur5', r'metabotropic\s+glutamate\s+receptor\s*(?:subtype\s*)?5'],
    'GPR143': [r'\boa1\b'],
    'CALD1': [r'caldesmon'], 'LMOD1': [r'leiomodin'],
}
HRCA_EXCL = {"41578023", "32555229", "34691611", "37388908", "32946783", "39117640"}
GENES = ["ATP8B4", "CALD1", "CDH8", "CST1", "CST4", "FAM135A", "FBXL7", "FCER1G",
         "GPR143", "GRM5", "LMOD1", "LRRTM3", "MUC7", "PTPRK", "SAMSN1", "SHISA6"]
ORDER = {"T1": 0, "T1a": 1, "T2": 2, "T2a": 3, "T3": 4, "T3a": 5, "T4": 6, "T4a": 7}

def epmc(query, pageSize=75):
    url = E + "?" + urllib.parse.urlencode({"query": query, "format": "json",
                                            "pageSize": pageSize, "resultType": "core"})
    for att in range(4):
        try:
            with OP.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            if "hitCount" not in d:
                raise RuntimeError("partial: no hitCount")
            return d
        except Exception as e:
            print(f"  RETRY {att+1} {e}", flush=True)
            time.sleep(3 + att * 4)
    return None

def tb(tok):
    return re.compile(r"\b(?:" + tok + r")\b", re.I)

def main():
    closed64 = {l.strip() for l in open(f"{P1}/out/closed_set_pmids.txt") if l.strip()}
    corpus = {str(json.loads(l)["paper_id"]) for l in open(f"{V24}/papers.jsonl", encoding="utf-8")}
    units = {r["gene"]: r for r in csv.DictReader(open(f"{P1}/out/GATE3_residual_units.tsv"), delimiter="\t")}
    assert set(units) >= set(GENES)

    ledger, picks, used = [], {}, set()
    for g in GENES:
        u = units[g]
        ctx = u["ctx"]
        cited = [p for p in (u["cited"] or "").split(",") if p]
        sym_re = tb(g)
        alias_res = [tb(t) for t in ALIAS_RE.get(g, [])]
        ctx_res = [tb(t) for t in CTX_TERMS[ctx]]
        inT = lambda t, rl: any(rx.search(t) for rx in rl)

        # ---- 1) 链路口: kb 自引 PMID ----
        chain_cands = []
        for pm in cited:
            if pm in closed64 or pm in HRCA_EXCL:
                chain_cands.append(dict(pmid=pm, route="chain", verdict="EXCLUDED",
                                        reason="in closed64/HRCA"))
                continue
            d = epmc(f"EXT_ID:{pm} AND SRC:MED", pageSize=1)
            time.sleep(0.5)
            res = (d or {}).get("resultList", {}).get("result", [])
            if not res:
                chain_cands.append(dict(pmid=pm, route="chain", verdict="C2_FAIL",
                                        reason="EPMC MED 无此 PMID"))
                continue
            h = res[0]
            t = " ".join((h.get("title") or "").split())
            a = " ".join((h.get("abstractText") or "").split())
            ok = inT(t, ctx_res) or bool(sym_re.search(t))
            chain_cands.append(dict(pmid=pm, route="chain", title=t[:160], title_full=t,
                                    abstract_head=a[:500], oa=h.get("isOpenAccess"),
                                    pmcid=h.get("pmcid"), year=h.get("pubYear"),
                                    journal=h.get("journalTitle"),
                                    c1_ctx_in_title=ok, token_sym_abs=bool(sym_re.search(a)),
                                    verdict="CHAIN_VERIFIED" if ok else "CHAIN_CTX_FAIL",
                                    reason="" if ok else "题录与断言眼语境不一致"))
        # ---- 2) 检索候选 (symbol 查询 + 别名查询) ----
        search_cands, seen = [], set()
        for q, qsrc in ([(f'"{g}" AND {CTX[ctx]} AND SPECIES:"HUMAN"', "sym")] +
                        [(f'"{al}" AND {CTX[ctx]} AND SPECIES:"HUMAN"', "alias")
                         for al in ALIAS_SEARCH.get(g, [])]):
            d = epmc(q, pageSize=75)
            time.sleep(0.5)
            if not d:
                continue
            for h in d.get("resultList", {}).get("result", []):
                pm = str(h.get("pmid") or "")
                if not pm or pm in seen:
                    continue
                seen.add(pm)
                if pm in closed64 or pm in corpus or pm in used or pm in HRCA_EXCL:
                    continue
                t = " ".join((h.get("title") or "").split())
                a = " ".join((h.get("abstractText") or "").split())
                sym_t, sym_a = bool(sym_re.search(t)), bool(sym_re.search(a))
                ali_t = inT(t, alias_res)
                ctx_t, ctx_a = inT(t, ctx_res), inT(a, ctx_res)
                oa = h.get("isOpenAccess") == "Y"
                pmcid = h.get("pmcid") or ""
                inE = h.get("inEPMC") == "Y"
                if sym_t and ctx_t: tier = "T1"
                elif sym_t and ctx_a: tier = "T2"
                elif ctx_t and sym_a: tier = "T3"
                elif qsrc == "alias" and ali_t and ctx_t: tier = "T1a"
                elif qsrc == "alias" and ali_t and ctx_a: tier = "T2a"
                elif qsrc == "alias" and ctx_t and inT(a, alias_res): tier = "T3a"
                elif qsrc == "sym" and ctx_t: tier = "T4"   # 语境断言词∈标题 ∧ symbol 经 EPMC 引号检索命中全文域(下载后 token 终裁)
                elif qsrc == "alias" and ctx_t: tier = "T4a" # 别名断言∈检索域 ∧ 语境∈标题 (正文含 symbol 待下载复核)
                else:
                    continue
                # 可兑现性: fulltext(oa∧pmcid; sym路须 qsrc=sym∨sym_a∨inEPMC; alias路须 inEPMC=Y 且下载后 token 复核)
                # abstract_token: sym∈摘要; 全无 → 出局
                feas = None
                if tier == "T4":
                    feas = "fulltext" if (oa and pmcid and (sym_a or inE)) else ("abstract_token" if sym_a else None)
                elif tier == "T4a":
                    feas = "fulltext" if (oa and pmcid and inE and not sym_a) else ("abstract_token" if sym_a else ("fulltext" if (oa and pmcid) else None))
                elif oa and pmcid and (qsrc == "sym" or sym_a):
                    feas = "fulltext"
                elif sym_a:
                    feas = "abstract_token"
                if feas is None:
                    search_cands.append(dict(pmid=pm, tier=tier, qsrc=qsrc, title=t[:160],
                                             oa=h.get("isOpenAccess"), pmcid=pmcid,
                                             verdict="NOT_FEASIBLE",
                                             reason="sym 不在摘要且非检索域 symbol 命中全文路"))
                    continue
                search_cands.append(dict(pmid=pm, tier=tier, qsrc=qsrc, feas=feas,
                                         title=t[:160], title_full=t, abstract_head=a[:500],
                                         oa=h.get("isOpenAccess"), pmcid=pmcid,
                                         year=h.get("pubYear"), journal=h.get("journalTitle"),
                                         preprint=(h.get("preprint") == "y"),
                                         inEPMC=h.get("inEPMC"), verdict="CANDIDATE"))
        # ---- 3) 选取: 首选+替补 (替补仅在首选下载复核失败时顶岗, 同属锁定闭集) ----
        ok_chain = [c for c in chain_cands if c["verdict"] == "CHAIN_VERIFIED"
                    and (c.get("pmcid") or c.get("abstract_head"))
                    and c["pmid"] not in closed64 and c["pmid"] not in corpus and c["pmid"] not in used]
        cand = [c for c in search_cands if c["verdict"] == "CANDIDATE"]
        cand.sort(key=lambda c: (ORDER.get(c["tier"], 9),
                                 0 if c["feas"] == "fulltext" else 1,
                                 1 if c.get("preprint") else 0,
                                 -int(str(c.get("year") or 0))))
        pool = (("chain", ok_chain) if ok_chain else ("search", cand))
        pick = pool[1][0] if pool[1] else None
        route = pool[0] if pool[1] else None
        backup = None
        if pick:
            used.add(pick["pmid"])
            for c in pool[1][1:]:
                if c["pmid"] not in used and c["pmid"] not in closed64 and c["pmid"] not in corpus:
                    backup = c
                    used.add(backup["pmid"])
                    break
        picks[g] = dict(ctx=ctx, rows=int(u["rows"]), cited=cited, chain=chain_cands,
                        candidates=cand[:15], pick=pick, backup=backup, route=route)
        print(f"{g}({ctx}): chain_ok={len(ok_chain)} cand={len(cand)} -> "
              f"{(pick['pmid'] + '/' + (pick.get('tier') or route)) if pick else 'NONE(honest)'}"
              f"{' +' + backup['pmid'] if backup else ''}", flush=True)
        for c in chain_cands + search_cands:
            ledger.append(dict(gene=g, ctx=ctx,
                               **{k: v for k, v in c.items() if k not in ("abstract_head", "title_full")}))

    json.dump(picks, open(f"{PLAN2}/work/ra2_candidates_raw.json", "w"), indent=1, ensure_ascii=False)
    with open(f"{PLAN2}/out/RA2_candidate_ledger.tsv", "w", newline="") as f:
        keys = ["gene", "ctx", "pmid", "route", "tier", "qsrc", "feas", "title", "oa", "pmcid",
                "year", "journal", "preprint", "c1_ctx_in_title", "token_sym_abs", "verdict", "reason"]
        wr = csv.DictWriter(f, fieldnames=keys, delimiter="\t", extrasaction="ignore")
        wr.writeheader(); wr.writerows(ledger)
    wl = []
    for g in GENES:
        p = picks[g]
        c = p["pick"]
        if not c:
            wl.append(dict(gene=g, ctx=p["ctx"], pmid="", tier="NONE", feas="", oa="",
                           title="(honest none: 无三条件+可兑现合格候选)", note="maintain_none"))
        else:
            wl.append(dict(gene=g, ctx=p["ctx"], pmid=c["pmid"], tier=c.get("tier") or p["route"],
                           feas=c.get("feas", "chain"), oa=c.get("oa", ""),
                           title=c.get("title", "")[:150], slot="primary",
                           note="kb_cited_chain" if p["route"] == "chain" else f"qsrc={c.get('qsrc')}"))
            b = p.get("backup")
            if b:
                wl.append(dict(gene=g, ctx=p["ctx"], pmid=b["pmid"], tier=b.get("tier") or p["route"],
                               feas=b.get("feas", "chain"), oa=b.get("oa", ""),
                               title=b.get("title", "")[:150], slot="backup",
                               note="替补:仅首选下载复核失败时顶岗"))
    with open(f"{PLAN2}/out/RA2_WHITELIST.tsv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["gene", "ctx", "pmid", "tier", "feas", "oa", "title", "slot", "note"],
                            delimiter="\t")
        wr.writeheader(); wr.writerows(wl)
    pm = sorted({w["pmid"] for w in wl if w["pmid"]})
    open(f"{PLAN2}/out/closed_set_ra2_pmids.txt", "w").write("\n".join(pm) + "\n")
    print(f"\nWHITELIST: {len(pm)} papers, none_genes={[w['gene'] for w in wl if not w['pmid']]}")

if __name__ == "__main__":
    main()
