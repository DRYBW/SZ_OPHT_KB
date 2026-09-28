#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 (RAGFIX D19) stage ra_fetch: A 档闭集 64 篇定向抓取 (metadata + fullTextXML)
- 与 stage_kc_fetch/stage_d0_fetch 完全同源纪律: ProxyHandler({}) 强制直连、0.6s/请求限速、
  指数退避重试 (残缺 JSON 视为失败重试); species 正则同源
- 闭集=本目录 out/closed_set_pmids.txt (64 PMID, 由 TIER_A_approval_list.md 必补表 ☐ 行逐行提取;
  ⛔41349939 已排除=误引撤证对象, 走勘误件不入库; 备选 104 篇本轮不下)
- PI 放行: USER_DIRECTIVE 追加二 D19 (A 档总量 ≤~85MB 在 <1GB 免批纪律内)
- 全文可得性按语料管线规则: 有 PMCID → 试 fullTextXML; 失败/无 PMCID → abstract-only
- 42777860 特例 (RAGGAP §6.4): EPMC MEDLINE 未收录 → NCBI eutils esummary/efetch 摘要补录,
  台账标 source=PUBMED_ONLY
输出: work/ra_meta.jsonl + work/ra_selected.jsonl + work/xml/{pmcid}.xml
     + work/ra_availability.tsv (逐 PMID 台账: 成败+体积)
红线: 不写 v2.0-2.3 目录 (冻结只读); 下载仅限闭集, 任何清单外一篇不下; 不触 plans/evalset/
"""
import json, os, time, urllib.request, urllib.parse, urllib.error

PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
WORK = f"{PLAN}/work"
XML_DIR = f"{WORK}/xml"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "OcularKB-RAG/0.3"}

PMIDS = [l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip()]
assert len(PMIDS) == 64 and len(set(PMIDS)) == 64, f"closed set size {len(PMIDS)} != 64"

# species 检测 — 与 stage_kc_fetch/stage_d0_fetch/stage1b_v3 完全同源的正则
import re
HUMAN_PAT = re.compile(r"human|humans|patient|patients|donor|donors|volunteer", re.I)
MOUSE_PAT = re.compile(r"mouse|mice|murine|mus musculus", re.I)
OTHER_PAT = re.compile(r"rat|rats|zebrafish|macaque|monkey|pig|porcine|bovine|chicken|drosophila|non-human primate", re.I)


def detect_species(row):
    text = (row.get("title", "") + " " + (row.get("abstractText", "") or "")).lower()
    me = row.get("meshHeadingList", []) or []
    mesh = json.dumps(me).lower()
    h = bool(HUMAN_PAT.search(text)) or "human" in mesh or "humans" in mesh
    m = bool(MOUSE_PAT.search(text)) or "mice" in mesh or "mouse" in mesh
    o = bool(OTHER_PAT.search(text))
    if h and m: return "both"
    if h: return "human"
    if m: return "mouse"
    if o: return "other"
    return "unknown"


def get_json(url, tries=7):
    req = urllib.request.Request(url, headers=UA)
    last = None
    for attempt in range(tries):
        try:
            with OPENER.open(req, timeout=120) as resp:
                data = json.loads(resp.read())
            if "hitCount" not in data:
                raise RuntimeError("partial response: missing hitCount")
            return data
        except Exception as e:
            last = e
            print(f"  retry {attempt+1}: {e}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"fetch failed: {url[:90]} ({last})")


def get_xml(pmcid, tries=5):
    url = f"{EPMC}/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers=UA)
    out = f"{XML_DIR}/{pmcid}.xml"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return "cached", os.path.getsize(out)
    last = None
    for attempt in range(tries):
        try:
            with OPENER.open(req, timeout=90) as resp:
                content = resp.read().decode("utf-8", "replace")
            if content.lstrip().startswith("<"):
                with open(out, "w", encoding="utf-8") as f:
                    f.write(content)
                return "ok", len(content)
            raise RuntimeError("non-XML body")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):  # 非 OA: fullTextXML 不可得, 不重试 (禁绕付费墙)
                return f"http{e.code}", 0
            last = e
            time.sleep(4 * (attempt + 1))
        except Exception as e:
            last = e
            time.sleep(4 * (attempt + 1))
    return f"ERR:{last}", 0


def pubmed_abstract(pmid, tries=5):
    """eutils 摘要补录 (EPMC 未收录 PMID 专用通道, RAGGAP §6.4)"""
    url = (EUTILS + "/efetch.cgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"}))
    req = urllib.request.Request(url, headers={"User-Agent": "OcularKB-RAG/0.3"})
    last = None
    for attempt in range(tries):
        try:
            with OPENER.open(req, timeout=90) as resp:
                txt = resp.read().decode("utf-8", "replace")
            if len(txt.strip()) > 200:
                return txt
            raise RuntimeError("empty abstract body")
        except Exception as e:
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"eutils failed {pmid}: {last}")


def journal_of(row):
    ji = row.get("journalInfo", {}) or {}
    j = ji.get("journal", {}) or {}
    return j.get("title", "") or ji.get("journalAbbreviation", "")


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(XML_DIR, exist_ok=True)
    meta_f = open(f"{WORK}/ra_meta.jsonl", "w", encoding="utf-8")
    sel_f = open(f"{WORK}/ra_selected.jsonl", "w", encoding="utf-8")
    ledger = []
    for pm in PMIDS:
        url = EPMC + "/search?" + urllib.parse.urlencode(
            {"query": f"EXT_ID:{pm} AND SRC:MED", "format": "json",
             "resultType": "core", "pageSize": "1"})
        d = get_json(url)
        res = d.get("resultList", {}).get("result", [])
        if not res:
            # EPMC 未收录 → PubMed eutils 摘要补录通道 (42777860 型)
            try:
                abst = pubmed_abstract(pm)
            except Exception as e:
                ledger.append((pm, "NOT_FOUND", "", "", "eutils_err", 0, 0, ""))
                print(f"{pm} NOT_FOUND_BOTH {e}", flush=True)
                time.sleep(0.6)
                continue
            url2 = EUTILS + "/esummary.cgi?" + urllib.parse.urlencode(
                {"db": "pubmed", "id": pm, "version": 1.0, "retmode": "json"})
            title, year, journal = "", "", ""
            try:
                sd = json.loads(OPENER.open(urllib.request.Request(url2, headers=UA), timeout=60).read())
                r0 = (sd.get("result") or {}).get(pm) or {}
                title = " ".join((r0.get("title") or "").split())
                year = (r0.get("pubdate") or "")[:4]
                journal = r0.get("fulljournalname", "") or r0.get("source", "")
            except Exception:
                pass
            rec = {"key": f"PUBMED:{pm}", "pmid": pm, "pmcid": "", "doi": "",
                   "title": title, "abstractText": abst[:4000], "year": year,
                   "journal": journal, "species": detect_species({"title": title, "abstractText": abst}),
                   "tissues": [], "subtypes": [], "axes": ["RA-TIERA"],
                   "is_preprint": False, "is_oa": "N", "fulltext": "pubmed_abstract_only",
                   "xml_bytes": 0, "abstract_bytes": len(abst)}
            sel_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            ledger.append((pm, "PUBMED_ONLY", "", "N", "pubmed_abstract_only",
                           0, len(abst), rec["species"]))
            print(f"{pm} PUBMED_ONLY abstract-only bytes={len(abst)}", flush=True)
            time.sleep(0.6)
            continue
        r = res[0]
        meta_f.write(json.dumps(r, ensure_ascii=False) + "\n")
        pmcid = r.get("pmcid") or ""
        oa = r.get("isOpenAccess", "N")
        xml_status, xml_bytes = get_xml(pmcid) if pmcid else ("no_pmcid", 0)
        sp = detect_species(r)
        rec = {
            "key": f"MED:{pm}", "pmid": pm, "pmcid": pmcid,
            "doi": r.get("doi", "") or "", "title": r.get("title", ""),
            "abstractText": (r.get("abstractText") or "")[:4000],
            "year": r.get("pubYear", ""), "journal": journal_of(r),
            "species": sp, "tissues": [], "subtypes": [], "axes": ["RA-TIERA"],
            "is_preprint": bool(r.get("preprint", "n") == "y"),
            "is_oa": oa, "fulltext": xml_status,
            "xml_bytes": xml_bytes, "abstract_bytes": len(r.get("abstractText") or ""),
        }
        sel_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ledger.append((pm, "MED", pmcid, oa, xml_status, xml_bytes,
                       rec["abstract_bytes"], sp))
        print(f"{pm} OA={oa} pmcid={pmcid or '-'} xml={xml_status}({xml_bytes}B) "
              f"preprint={rec['is_preprint']} species={sp}", flush=True)
        time.sleep(0.6)
    meta_f.close(); sel_f.close()
    with open(f"{WORK}/ra_availability.tsv", "w") as f:
        f.write("pmid\tsource\tpmcid\tisOpenAccess\tfulltext_status\txml_bytes\tabstract_bytes\tspecies\n")
        for row in ledger:
            f.write("\t".join(str(x) for x in row) + "\n")
    tot = sum(r[5] for r in ledger)
    print(f"DONE n={len(ledger)} total_xml_bytes={tot/1e6:.1f}MB", flush=True)


if __name__ == "__main__":
    main()
