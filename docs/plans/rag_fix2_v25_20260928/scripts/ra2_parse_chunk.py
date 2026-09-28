#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 stage ra2_parse_chunk: work/xml2/*.xml + ra2_selected.jsonl -> work/chunks_ra2_raw.jsonl
- 与 ra_parse_chunk.py (t_d0bea5a6) 完全同构: 同一 stage2a_parse_xml_v2/stage2b_chunk_v2 纯函数,
  仅换路径与 axes=["RA2-TIERA"] (中间字段, merge 时按 v2.4 schema 列过滤, 不入 parquet)
- abstract-only: sections=[] tables=[] 只出 abstract chunk (ftstatus=0)
红线: 不写任何冻结版本目录
"""
import json, os, re, sys
import lxml.etree as etree

BASE = "/mnt/D/OcularKB/ocularkb/rag"
PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
sys.path.insert(0, f"{BASE}/scripts")
from stage2a_parse_xml_v2 import strip_ns, walk_secs, extract_tables
from stage2b_chunk_v2 import (MARKERS, detect_cell_types, detect_tissues,
                              count_tokens, chunk_paragraph)

XML_DIR = f"{PLAN2}/work/xml2"
SEL = f"{PLAN2}/work/ra2_selected.jsonl"
OUT = f"{PLAN2}/work/chunks_ra2_raw.jsonl"

def load_meta():
    m = {}
    for line in open(SEL, encoding="utf-8"):
        r = json.loads(line)
        key = r.get("pmcid") or f"PMID:{r['pmid']}"
        m[key] = r
    return m

def parse_xml(path, meta):
    tree = etree.parse(path)
    root = tree.getroot()
    t_el = root.find(".//title-group/article-title")
    title = " ".join(t_el.itertext()).strip() if t_el is not None else meta.get("title", "")
    sections = []
    for sec in root.iter():
        if strip_ns(sec.tag) == "sec":
            parent = sec.getparent()
            if parent is None or strip_ns(parent.tag) != "sec":
                sections.extend(walk_secs(sec))
    tables = extract_tables(root)
    abs_els = [el for el in root.iter() if strip_ns(el.tag) == "abstract"]
    abstract = " ".join(abs_els[0].itertext()).strip() if abs_els else meta.get("abstractText", "")
    return {"paper_id": meta["pmid"], "pmcid": meta.get("pmcid", ""),
            "title": title or meta.get("title", ""), "journal": meta.get("journal", ""),
            "year": meta.get("year", ""), "doi": meta.get("doi", ""),
            "species": meta.get("species", "unknown"), "tissues": meta.get("tissues", []),
            "subtypes": [], "axes": ["RA2-TIERA"], "if_metric": None,
            "is_preprint": int(bool(meta.get("is_preprint", False))),
            "abstract": abstract, "sections": sections, "tables": tables}

def abstract_only_rec(m):
    return {"paper_id": m["pmid"], "pmcid": m.get("pmcid", ""), "title": m.get("title", ""),
            "journal": m.get("journal", ""), "year": m.get("year", ""), "doi": m.get("doi", ""),
            "species": m.get("species", "unknown"), "tissues": m.get("tissues", []),
            "subtypes": [], "axes": ["RA2-TIERA"], "if_metric": None,
            "is_preprint": int(bool(m.get("is_preprint", False))),
            "abstract": m.get("abstractText", ""), "sections": [], "tables": []}

def main():
    meta_map = load_meta()
    papers, seen_ids = [], set()
    for fn in sorted(os.listdir(XML_DIR)):
        if not fn.endswith(".xml"):
            continue
        pmcid = fn[:-4]
        m = meta_map.get(pmcid)
        if m is None:
            print(f"SKIP orphan xml {pmcid}")
            continue
        try:
            p = parse_xml(os.path.join(XML_DIR, fn), m)
        except Exception as e:
            print(f"ERR {pmcid}: {e} -> fallback abstract-only")
            p = abstract_only_rec(m)
        if p["paper_id"] not in seen_ids:
            papers.append(p); seen_ids.add(p["paper_id"])
    for key, m in meta_map.items():
        if m["pmid"] in seen_ids:
            continue
        papers.append(abstract_only_rec(m)); seen_ids.add(m["pmid"])
    n_expected = sum(1 for _ in open(SEL, encoding="utf-8"))
    assert len(papers) == n_expected, f"expect {n_expected} papers, got {len(papers)}"

    marker_genes = set()
    for ct, genes in json.load(open(MARKERS)).get("markers_new", {}).items():
        marker_genes.update(genes)
    n_chunks = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for p in papers:
            paper_tissues = sorted(set(p.get("tissues", [])))
            paper_tissues = sorted((set(paper_tissues) | set(detect_tissues(
                (p.get("title", "") + " " + (p.get("abstract", "") or ""))))) - {"retina"})
            base = {"paper_id": str(p["paper_id"]), "pmcid": p["pmcid"], "title": p["title"],
                    "journal": p["journal"], "year": p["year"], "doi": p["doi"],
                    "species": p.get("species", "unknown"),
                    "tissue": paper_tissues[0] if paper_tissues else "unknown",
                    "tissue_labels_paper": paper_tissues,
                    "is_preprint": int(p.get("is_preprint", 0)), "axes": ["RA2-TIERA"]}

            def emit(chunk_type, section, text, extra=None):
                nonlocal n_chunks
                rec = dict(base)
                labels = sorted(set(paper_tissues) | set(detect_tissues(text)))
                rec.update({"chunk_type": chunk_type, "section": section, "text": text,
                            "n_tokens": count_tokens(text), "tissue_labels": labels,
                            "cell_type_mentioned": detect_cell_types(text),
                            "marker_genes": [g for g in marker_genes
                                             if re.search(r"\b" + g + r"\b", text, re.I)]})
                if extra:
                    rec.update(extra)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_chunks += 1

            if p.get("abstract"):
                for c in chunk_paragraph(p["abstract"], 800):
                    emit("abstract", "Abstract", c["text"])

            def walk(secs, path):
                for sec in secs:
                    heading = sec.get("heading", "")
                    full_path = (path + " > " + heading) if path else heading
                    sec_text = " ".join(sec.get("paragraphs", []))
                    if sec_text.strip():
                        for c in chunk_paragraph(sec_text, 800):
                            emit("paragraph", full_path, c["text"])
                    walk(sec.get("children", []), full_path)
            walk(p.get("sections", []), "")
            for t in p.get("tables", []):
                cap = t.get("caption", "")
                for ri, row in enumerate(t.get("rows", [])):
                    emit("table_row", f"Table: {cap[:100]}", " | ".join(row), extra={"row_idx": ri})

    import collections
    cnt = collections.Counter(); ftstatus = {}
    for line in open(OUT, encoding="utf-8"):
        r = json.loads(line)
        cnt[r["paper_id"]] += 1
        cur = ftstatus.get(r["paper_id"], 0)
        ftstatus[r["paper_id"]] = max(cur, 0 if r["chunk_type"] == "abstract" else 1)
    json.dump(dict(cnt), open(f"{PLAN2}/work/ra2_chunks_per_paper.json", "w"), indent=1)
    json.dump(ftstatus, open(f"{PLAN2}/work/ra2_ftstatus.json", "w"), indent=1)
    print(f"DONE: {len(cnt)} papers -> {n_chunks} chunks -> {OUT}")
    print("zero-chunk:", [m["pmid"] for m in meta_map.values() if cnt.get(m["pmid"], 0) == 0])
    for k, v in sorted(cnt.items()):
        print(f"  {k}: {v} chunks ft={ftstatus.get(k)}")

if __name__ == "__main__":
    main()
