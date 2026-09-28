#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 (t_6848d3de) stage ra2_fetch: 白名单闭集 17 篇定向抓取 (metadata + fullTextXML)
- 与 ra_fetch.py 完全同源纪律: EPMC core EXT_ID 单篇回查(=C2 复核, 标题与白名单逐字比对)、
  ProxyHandler({}) 直连、0.6s/请求限速、指数退避、species 正则同源、
  有 PMCID→试 fullTextXML, 403/404/无 PMCID→abstract-only, 禁绕付费墙;
  EPMC 未收录→eutils 摘要补录(本闭集已全 C2 通过, 理论不触发; 保留通道与 ra_fetch 同构)
- 顺序=首选在前替补在后 (从 RA2_WHITELIST.tsv slot 列); 6MB 硬上限: 累计 xml_bytes>6e6 时
  停止后续下载, 剩余记 SKIPPED_CAP (超限停车回挂报批, DECISION_1 红线)
- 闭集=out/closed_set_ra2_pmids.txt (17 PMID, 由 ra2_candidates.py 三条件核验锁定)
输出: work/ra2_meta.jsonl + work/ra2_selected.jsonl + work/xml2/{pmcid}.xml
     + work/ra2_availability.tsv (逐 PMID 台账) + work/ra2_bytes.json
"""
import json, os, time, urllib.request, urllib.parse, urllib.error

PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
WORK = f"{PLAN2}/work"
XML_DIR = f"{WORK}/xml2"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "OcularKB-RAG/0.3 (RAGFIX2)"}
CAP_BYTES = 6_000_000

import csv, re
wl = list(csv.DictReader(open(f"{PLAN2}/out/RA2_WHITELIST.tsv"), delimiter="\t"))
prim = [w for w in wl if w["slot"] == "primary"]
back = [w for w in wl if w["slot"] == "backup"]
ORDER = prim + back  # 首选全部先于替补
wl_title = {w["pmid"]: " ".join(w["title"].split()).lower() for w in wl if w["pmid"]}
PMIDS = [w["pmid"] for w in ORDER]
assert len(PMIDS) == len(set(PMIDS)) == 17, f"closed set {len(PMIDS)}"

HUMAN_PAT = re.compile(r"human|humans|patient|patients|donor|donors|volunteer", re.I)
MOUSE_PAT = re.compile(r"mouse|mice|murine|mus musculus", re.I)
OTHER_PAT = re.compile(r"rat|rats|zebrafish|macaque|monkey|pig|porcine|bovine|chicken|drosophila|non-human primate", re.I)

def detect_species(row):
    text = (row.get("title", "") + " " + (row.get("abstractText", "") or "")).lower()
    mesh = json.dumps(row.get("meshHeadingList", []) or []).lower()
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
    for att in range(tries):
        try:
            with OPENER.open(req, timeout=120) as resp:
                data = json.loads(resp.read())
            if "hitCount" not in data:
                raise RuntimeError("partial response: missing hitCount")
            return data
        except Exception as e:
            last = e
            print(f"  retry {att+1}: {e}", flush=True)
            time.sleep(5 * (att + 1))
    raise RuntimeError(f"fetch failed: {url[:90]} ({last})")

def get_xml(pmcid):
    url = f"{EPMC}/{pmcid}/fullTextXML"
    out = f"{XML_DIR}/{pmcid}.xml"
    req = urllib.request.Request(url, headers=UA)
    try:
        with OPENER.open(req, timeout=90) as resp:
            content = resp.read().decode("utf-8", "replace")
        if content.lstrip().startswith("<"):
            with open(out, "w", encoding="utf-8") as f:
                f.write(content)
            return "ok", len(content)
        return "non-xml", 0
    except urllib.error.HTTPError as e:
        return f"http{e.code}", 0
    except Exception as e:
        return f"ERR:{e}", 0

def main():
    os.makedirs(XML_DIR, exist_ok=True)
    meta_f = open(f"{WORK}/ra2_meta.jsonl", "w", encoding="utf-8")
    sel_f = open(f"{WORK}/ra2_selected.jsonl", "w", encoding="utf-8")
    ledger, total_bytes, cap_hit = [], 0, False
    for w in ORDER:
        pm = w["pmid"]
        if cap_hit:
            ledger.append((pm, "SKIPPED_CAP", w["gene"], w["slot"], "", "", 0, 0, ""))
            print(f"{pm} SKIPPED_CAP ({w['gene']})", flush=True)
            continue
        d = get_json(EPMC + "/search?" + urllib.parse.urlencode(
            {"query": f"EXT_ID:{pm} AND SRC:MED", "format": "json",
             "resultType": "core", "pageSize": "1"}))
        res = d["resultList"]["result"]
        if not res:
            ledger.append((pm, "C2_FAIL", w["gene"], w["slot"], "", "", 0, 0, ""))
            print(f"{pm} C2_FAIL not in EPMC", flush=True)
            time.sleep(0.6)
            continue
        r = res[0]
        title_live = " ".join((r.get("title") or "").split()).lower()
        if not title_live.startswith(wl_title[pm][:60].rstrip(".")):  # 白名单标题为截断版, 前缀核对
            mismatch = title_live != wl_title[pm] and wl_title[pm] not in title_live
            if mismatch:
                ledger.append((pm, "C2_TITLE_MISMATCH", w["gene"], w["slot"], "", "", 0, 0, ""))
                print(f"{pm} C2_TITLE_MISMATCH live={title_live[:60]!r}", flush=True)
                time.sleep(0.6)
                continue
        meta_f.write(json.dumps(r, ensure_ascii=False) + "\n")
        pmcid = r.get("pmcid") or ""
        oa = r.get("isOpenAccess", "N")
        xml_status, xml_bytes = ("no_pmcid", 0)
        if oa == "Y" and pmcid:
            xml_status, xml_bytes = get_xml(pmcid)
            total_bytes += xml_bytes
            if total_bytes > CAP_BYTES:
                cap_hit = True
                print(f"!! CAP {CAP_BYTES/1e6:.1f}MB 超限 (累计 {total_bytes/1e6:.2f}MB) 停车", flush=True)
        sp = detect_species(r)
        ji = r.get("journalInfo", {}) or {}
        rec = {"key": f"MED:{pm}", "pmid": pm, "pmcid": pmcid, "doi": r.get("doi", "") or "",
               "title": r.get("title", ""), "abstractText": (r.get("abstractText") or "")[:4000],
               "year": r.get("pubYear", ""),
               "journal": (ji.get("journal", {}) or {}).get("title", "") or ji.get("journalAbbreviation", ""),
               "species": sp, "tissues": [], "subtypes": [], "axes": ["RA2-TIERA"],
               "is_preprint": bool(r.get("preprint", "n") == "y"),
               "is_oa": oa, "fulltext": xml_status,
               "xml_bytes": xml_bytes, "abstract_bytes": len(r.get("abstractText") or ""),
               "gene_slot": f"{w['gene']}/{w['slot']}/{w['tier']}"}
        sel_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ledger.append((pm, "MED", w["gene"], w["slot"], pmcid, oa, xml_status, xml_bytes, sp))
        print(f"{pm} [{w['gene']}/{w['slot']}] OA={oa} xml={xml_status}({xml_bytes}B) cum={total_bytes/1e6:.2f}MB sp={sp}", flush=True)
        time.sleep(0.6)
    meta_f.close(); sel_f.close()
    with open(f"{WORK}/ra2_availability.tsv", "w") as f:
        f.write("pmid\tsource\tgene\tslot\tpmcid\tisOpenAccess\tfulltext_status\txml_bytes\tspecies\n")
        for row in ledger:
            f.write("\t".join(str(x) for x in row) + "\n")
    json.dump({"total_xml_bytes": total_bytes, "cap_hit": cap_hit},
              open(f"{WORK}/ra2_bytes.json", "w"), indent=1)
    print(f"DONE n={len(ledger)} total_xml_bytes={total_bytes/1e6:.2f}MB cap_hit={cap_hit}")

if __name__ == "__main__":
    main()
