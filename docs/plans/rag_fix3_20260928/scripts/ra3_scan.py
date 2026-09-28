#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 (t_b94d0999) stage ra3_scan: 104 备选池机械扫描（零 LLM，判据=out/DECISION_MATRIX_RAGFIX3.md R0）
- V1 题录可核性 = EPMC EXT_ID:{pmid} AND SRC:MED core 单篇回查 ∧ 标题前缀逐字比对（沿 ra2_fetch C2 判据）
- V2 在库查重 = pmid ∈ v2.4.1 paper_id ∨ live DOI ∈ v2.4.1 doi 集（大小写不敏感）
- V3 自引排除 = HRCA_EXCL ∪ {41349939} ∪ closed64 ∪ RA2_17（沿 RA2 C3）
- V4 OA 实测 = live isOpenAccess/pmcid + curl -sI HEAD fullTextXML 状态码（HEAD 无 Content-Length，体积由 fetch 段 GET 实测）
- 网络: PORT 代理优先，失败回退直连（通道逐条记录）；0.6s/请求限速；指数退避沿 ra2_fetch
输出: work/ra3_scan_ledger.tsv + work/ra3_meta.jsonl + out/closed_set_ra3_intake.tsv + out/RA3_SCAN_SUMMARY.json
"""
import csv, json, os, re, subprocess, sys, time, urllib.parse, urllib.error

PLAN3 = "/mnt/D/EyeKB/plans/rag_fix3_20260928"
WORK = f"{PLAN3}/work"
P1 = "/mnt/D/EyeKB/plans/rag_fix_20260928"
P2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
V241_PAPERS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09/papers.jsonl"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
PROXY = "http://127.0.0.1:PORT"
UA = "OcularKB-RAG/0.3 (RAGFIX3)"

HRCA_EXCL = {"41578023", "32555229", "34691611", "37388908", "32946783", "39117640"}
ERRATA = {"41349939"}
closed64 = set(l.strip() for l in open(f"{P1}/out/closed_set_pmids.txt") if l.strip())
ra2_17 = set(l.strip() for l in open(f"{P2}/out/closed_set_ra2_pmids.txt") if l.strip())

lib_pids, lib_dois = set(), set()
for line in open(V241_PAPERS, encoding="utf-8"):
    d = json.loads(line)
    lib_pids.add(str(d["paper_id"]))
    if d.get("doi"):
        lib_dois.add(str(d["doi"]).lower())

def http_json(url, tries=6):
    """代理优先→直连回退; 返回 (data, channel)"""
    last = None
    for att in range(tries):
        for mode in ("proxy", "direct"):
            cmd = ["curl", "-s", "--max-time", "60", "-A", UA]
            if mode == "proxy":
                cmd += ["-x", PROXY]
            cmd += [url]
            try:
                out = subprocess.run(cmd, capture_output=True, timeout=90).stdout
                data = json.loads(out)
                if "hitCount" not in data:
                    raise RuntimeError("partial response")
                return data, mode
            except Exception as e:
                last = e
        print(f"  retry {att+1}: {last}", flush=True)
        time.sleep(5 * (att + 1))
    raise RuntimeError(f"scan fetch failed: {url[:90]} ({last})")

def head_oa(pmcid):
    url = f"{EPMC}/{pmcid}/fullTextXML"
    for mode, cmd_extra in ((("proxy", ["-x", PROXY])), ("direct", [])):
        try:
            r = subprocess.run(["curl", "-sI", "--max-time", "45", "-A", UA] + cmd_extra + [url],
                               capture_output=True, timeout=60)
            txt = r.stdout.decode("utf-8", "replace")
            m = re.findall(r"HTTP/[\d.]+ (\d{3})", txt)
            if m:
                return m[-1], mode   # 最终状态码（代理 CONNECT 行在前）
        except Exception:
            pass
    return "ERR", "both_fail"

rows = list(csv.reader(open(f"{WORK}/backup104_raw.tsv"), delimiter="\t"))
assert len([r for r in rows if r[1].isdigit()]) == 104, f"expect 104, got {len(rows)}"

ledger, meta_f = [], open(f"{WORK}/ra3_meta.jsonl", "w", encoding="utf-8")
n_done = 0
for chk, pmid, year, oa_tab, genes_col, title_tab in rows:
    n_done += 1
    wl_title = " ".join(title_tab.split()).lower()
    # V3/V2 本地检先做（省网络）
    if pmid in HRCA_EXCL:
        ledger.append((pmid, genes_col, "REJECT_HRCA_SELF_CIT", "", "", "", "", "", oa_tab)); continue
    if pmid in ERRATA:
        ledger.append((pmid, genes_col, "REJECT_ERRATA_LILRB2", "", "", "", "", "", oa_tab)); continue
    if pmid in closed64 or pmid in ra2_17 or pmid in lib_pids:
        ledger.append((pmid, genes_col, "REJECT_IN_LIBRARY_DOUBLECOUNT", "", "", "", "", "", oa_tab)); continue
    # V1 EPMC 回查
    url = EPMC + "/search?" + urllib.parse.urlencode(
        {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core", "pageSize": "1"})
    try:
        d, chan = http_json(url)
    except RuntimeError as e:
        ledger.append((pmid, genes_col, "REJECT_FETCH_FAIL", "", "", "", "", "", oa_tab)); print(f"{pmid} FETCH_FAIL", flush=True); continue
    res = d["resultList"]["result"]
    if not res:
        ledger.append((pmid, genes_col, "REJECT_VERIFY_NOHIT", "", "", "", chan, "", oa_tab)); print(f"{pmid} NOHIT", flush=True)
        time.sleep(0.6); continue
    r = res[0]
    title_live = " ".join((r.get("title") or "").split()).lower()
    if not title_live.startswith(wl_title[:60].rstrip(".")):
        if wl_title not in title_live:
            ledger.append((pmid, genes_col, "REJECT_TITLE_MISMATCH", "", "", "", chan, "", oa_tab))
            print(f"{pmid} TITLE_MISMATCH live={title_live[:50]!r}", flush=True); time.sleep(0.6); continue
    # V2b DOI 查重
    doi = (r.get("doi") or "").lower()
    if doi and doi in lib_dois:
        ledger.append((pmid, genes_col, "REJECT_DOI_IN_LIBRARY", r.get("pmcid", "") or "", doi[:30], "PASS", chan, "", oa_tab))
        print(f"{pmid} DOI_DUP {doi}", flush=True); time.sleep(0.6); continue
    # V4 OA 实测
    pmcid = r.get("pmcid") or ""
    oa_live = r.get("isOpenAccess", "N")
    head_code, head_chan = ("-", "-") if not (oa_live == "Y" and pmcid) else head_oa(pmcid)
    if oa_live == "Y" and pmcid and head_code == "200":
        decision = "INTAKE_FULLTEXT"
    elif head_code in ("403", "404", "ERR", "-") or oa_live != "Y" or not pmcid:
        decision = "INTAKE_ABS_ONLY"
    else:
        decision = "INTAKE_ABS_ONLY"
    meta_f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ledger.append((pmid, genes_col, decision, pmcid, doi[:30], head_code, f"v1={chan},v4={head_chan}",
                   r.get("pubYear", ""), oa_tab))
    if n_done % 10 == 0:
        print(f"[{n_done}/104] last={pmid} {decision}", flush=True)
    time.sleep(0.6)
meta_f.close()

with open(f"{WORK}/ra3_scan_ledger.tsv", "w", encoding="utf-8") as f:
    f.write("pmid\tbenefit_genes\tdecision\tpmcid\tdoi\thead_code\tchannel\tpubyear_live\toa_table\n")
    for row in ledger:
        f.write("\t".join(str(x) for x in row) + "\n")

from collections import Counter
cnt = Counter(r[2] for r in ledger)
intake = [r for r in ledger if r[2].startswith("INTAKE")]
with open(f"{PLAN3}/out/closed_set_ra3_intake.tsv", "w", encoding="utf-8") as f:
    f.write("pmid\tbenefit_genes\tdecision\tpmcid\tdoi\thead_code\n")
    for r in intake:
        f.write("\t".join(str(x) for x in r[:6]) + "\n")
open(f"{PLAN3}/out/closed_set_ra3_pmids.txt", "w").write("\n".join(r[0] for r in intake) + "\n")
summary = {"n_scanned": len(ledger), "decisions": dict(cnt),
           "n_intake": len(intake), "n_intake_fulltext": sum(1 for r in intake if r[2] == "INTAKE_FULLTEXT"),
           "n_intake_abs_only": sum(1 for r in intake if r[2] == "INTAKE_ABS_ONLY"),
           "intake_covering_7units": {g: [r[0] for r in intake for x in [g + "("] if (x + r[1]).count(g + "(")]
                                       for g in ["C8ORF76", "COL19A1", "FAM107B", "SLC24A3", "SSR4", "XCR1", "ZNF804B"]}}
json.dump(summary, open(f"{PLAN3}/out/RA3_SCAN_SUMMARY.json", "w"), indent=1, ensure_ascii=False)
print("SUMMARY", json.dumps(summary["decisions"], ensure_ascii=False))
print(f"intake={len(intake)} (fulltext={summary['n_intake_fulltext']} abs_only={summary['n_intake_abs_only']})")
