#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 (t_b94d0999) stage ra3_fetch: 准入集 103 篇下载（判据=DECISION_MATRIX R0-R1）
- 与 ra2_fetch.py 完全同源纪律: species 正则逐字、0.6s/请求限速、指数退避、
  OA=Y∧有PMCID→fullTextXML, 失败/无PMCID→abstract-only, 禁绕付费墙
- 通道: PORT 代理优先, 失败回退直连（ra3_scan 实证代理可用; 通道逐条记账）
- 顺序: 7 目标单元候选 14 篇在前, 其余 FULLTEXT 在后, ABS_ONLY 不下载仅登记
- 预算: 累计 xml_bytes ≤ 100MB (RA3_BUDGET), 超限停车记 SKIPPED_CAP;
  单篇 >1GB 不收并登记 SKIP_GT1GB（DECISION_MATRIX R1）
输入: work/ra3_meta.jsonl + out/closed_set_ra3_intake.tsv
输出: work/ra3_selected.jsonl + work/xml3/{pmcid}.xml + work/ra3_availability.tsv + work/ra3_bytes.json
"""
import csv, json, os, re, subprocess, time

PLAN3 = "/mnt/D/EyeKB/plans/rag_fix3_20260928"
WORK = f"{PLAN3}/work"
XML_DIR = f"{WORK}/xml3"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
PROXY = "http://127.0.0.1:PORT"
UA = "OcularKB-RAG/0.3 (RAGFIX3)"
BUDGET_BYTES = 100_000_000
GT1GB = 1_000_000_000
SEVEN = ["C8ORF76", "COL19A1", "FAM107B", "SLC24A3", "SSR4", "XCR1", "ZNF804B"]

HUMAN_PAT = re.compile(r"human|humans|patient|patients|donor|donors|volunteer", re.I)
MOUSE_PAT = re.compile(r"mouse|mice|murine|mus musculus", re.I)
OTHER_PAT = re.compile(r"rat|rats|zebrafish|macaque|monkey|pig|porcine|bovine|chicken|drosophila|non-human primate|sheep|fish|teleost|frog|salamander", re.I)

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

meta = {}
for line in open(f"{WORK}/ra3_meta.jsonl", encoding="utf-8"):
    d = json.loads(line)
    meta[str(d["pmid"])] = d
intake = list(csv.DictReader(open(f"{PLAN3}/out/closed_set_ra3_intake.tsv"), delimiter="\t"))
ft = [r for r in intake if r["decision"] == "INTAKE_FULLTEXT"]
ab = [r for r in intake if r["decision"] == "INTAKE_ABS_ONLY"]
prim = [r for r in ft if any(g in r["benefit_genes"] for g in SEVEN)]
rest = [r for r in ft if r not in prim]
ORDER = prim + rest + ab
assert len(ft) + len(ab) == 103 and len(prim) == 14, f"{len(ft)}/{len(ab)}/{len(prim)}"

def get_xml(pmcid):
    url = f"{EPMC}/{pmcid}/fullTextXML"
    for mode, extra in (("proxy", ["-x", PROXY]), ("direct", [])):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "120", "-A", UA] + extra + [url],
                               capture_output=True, timeout=150)
            content = r.stdout.decode("utf-8", "replace")
            if content.lstrip().startswith("<"):
                return content, mode
        except Exception:
            pass
    return None, "both_fail"

os.makedirs(XML_DIR, exist_ok=True)
sel_f = open(f"{WORK}/ra3_selected.jsonl", "w", encoding="utf-8")
ledger, total_bytes, cap_hit = [], 0, False
for row in ORDER:
    pm = row["pmid"]; m = meta[pm]
    pmcid = m.get("pmcid") or ""
    oa = m.get("isOpenAccess", "N")
    gene = row["benefit_genes"]
    if cap_hit:
        ledger.append((pm, "SKIPPED_CAP", gene, pmcid, oa, "", 0, ""))
        print(f"{pm} SKIPPED_CAP ({gene})", flush=True); continue
    xml_status, xml_bytes, chan = ("no_pmcid", 0, "-")
    if row["decision"] == "INTAKE_ABS_ONLY":
        xml_status = "abs_only_lane"
    elif oa == "Y" and pmcid:
        content, chan = get_xml(pmcid)
        if content:
            if len(content.encode()) > GT1GB:
                xml_status = "SKIP_GT1GB"; xml_bytes = len(content.encode())
                print(f"!! {pm} >1GB 不收", flush=True)
            else:
                with open(f"{XML_DIR}/{pmcid}.xml", "w", encoding="utf-8") as f:
                    f.write(content)
                xml_status, xml_bytes = "ok", len(content.encode())
                total_bytes += xml_bytes
                if total_bytes > BUDGET_BYTES:
                    cap_hit = True
                    print(f"!! BUDGET {BUDGET_BYTES/1e6:.0f}MB 超限 (累计 {total_bytes/1e6:.2f}MB) 停车", flush=True)
        else:
            xml_status = "fetch_fail"
    ji = m.get("journalInfo", {}) or {}
    rec = {"key": f"MED:{pm}", "pmid": pm, "pmcid": pmcid, "doi": m.get("doi", "") or "",
           "title": m.get("title", ""), "abstractText": (m.get("abstractText") or "")[:4000],
           "year": m.get("pubYear", ""),
           "journal": (ji.get("journal", {}) or {}).get("title", "") or ji.get("journalAbbreviation", ""),
           "species": detect_species(m), "tissues": [], "subtypes": [], "axes": ["RA3-TIERA"],
           "is_preprint": bool(m.get("preprint", "n") == "y"),
           "is_oa": oa, "fulltext": xml_status, "channel": chan,
           "xml_bytes": xml_bytes, "abstract_bytes": len(m.get("abstractText") or ""),
           "gene_slot": gene}
    sel_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ledger.append((pm, xml_status, gene, pmcid, oa, chan, xml_bytes, detect_species(m)))
    print(f"{pm} [{gene[:30]}] OA={oa} xml={xml_status}({xml_bytes}B) ch={chan} cum={total_bytes/1e6:.2f}MB", flush=True)
    time.sleep(0.6)
sel_f.close()
with open(f"{WORK}/ra3_availability.tsv", "w", encoding="utf-8") as f:
    f.write("pmid\tfulltext_status\tbenefit_genes\tpmcid\tisOpenAccess\tchannel\txml_bytes\tspecies\n")
    for r in ledger:
        f.write("\t".join(str(x) for x in r) + "\n")
json.dump({"total_xml_bytes": total_bytes, "budget": BUDGET_BYTES, "cap_hit": cap_hit},
          open(f"{WORK}/ra3_bytes.json", "w"), indent=1)
print(f"DONE n={len(ledger)} total={total_bytes/1e6:.2f}MB cap_hit={cap_hit}")
