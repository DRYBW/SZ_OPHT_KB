#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINKKEY — 引用侧 ↔ 语料侧 共同连接键 (t_83c4324d)

只读盘上件，零下载 / 零 GPU / 零网络。
输入（均只读；流式逐行读，不整文件载入）:
  CITED  : 引用侧 registry (brief 的分母 803 篇所对应的那份)
  CORPUS : 语料随件 papers.jsonl  (= v2.6-dev_2026-10, rows=3917 / pmcid=3680, 与 brief 实测数一致)
输出（本目录）:
  CONNECT_KEY_v1.tsv    803 行：每个被引 pmid 的对照
  UNMATCHED_v1.tsv      逐条未对上 + reason 非空（两种题名口径）
  CORPUS_TOUCH_v1.tsv   3917 行：语料全量两档 + pmid 可用性
  REGISTRY_SOURCES_v1.tsv  候选引用侧 registry 盘点（口径差异留证）
  MANIFEST.sha256       输入+输出的哈希清单（不含自身）

口径（三档并报，禁只报高的）:
  A 严格   : 规范化题名全等
  B 放宽   : 规范化题名前 40 字前缀（DOI/PMCID 键在引用侧结构性缺失，实测 0 条可用 → 不参与）
  C 标识键 : pmid ↔ 语料 paper_id
"""
import json, re, os, sys, csv, hashlib, unicodedata, collections, difflib

OUT = "/mnt/D/EyeKB/plans/consistency_20261024/LINKKEY_out"
CITED = "/mnt/D/EyeKB/plans/kbreach_fix_20261024/clone_check/kb/link_registry/LINK_REGISTRY_v1.jsonl"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"
REG_CANDIDATES = [
    ("authoritative_repo", "/home/ubuntu/EYEKB_REPO/kb/link_registry/LINK_REGISTRY_v1.jsonl"),
    ("workspace_mnt_D_eyekb", "/mnt/D/EyeKB/kb/link_registry/LINK_REGISTRY_v1.jsonl"),
    ("clone_check", CITED),
    ("clone_check2", "/mnt/D/EyeKB/plans/kbreach_fix_20261024/clone_check2/kb/link_registry/LINK_REGISTRY_v1.jsonl"),
    ("userjourney_clone", "/mnt/D/EyeKB/plans/user_journey_drsc_20261022/clone/SZ_OPHT_KB/kb/link_registry/LINK_REGISTRY_v1.jsonl"),
]
# 语料稳健性交叉：仓件随件 slim（结论对语料选择免疫的机器证据）
CORPUS_ROBUSTNESS = "/home/ubuntu/EYEKB_REPO/literature_db/v2.4.2_2026-09_slim/papers.jsonl"
# 构造性事实的两个源码锚点（题名截断 / 空题名 / pmid 即 paper_id）
SRC_ANCHORS = {
    "registry_pmid_from_paper_id": "EYEKB_REPO/kb/link_registry/scripts/build_link_registry.py:201",
    "registry_title_truncated_120": "EYEKB_REPO/kb/link_registry/scripts/build_link_registry.py:211",
    "registry_geneindex_title_empty": "EYEKB_REPO/kb/link_registry/scripts/build_link_registry.py:278",
    "retriever_pmid_is_paper_id": "EYEKB_REPO/clients/ocularkb/rag/scripts/stage3_retrieve.py:237",
    "corpus_paper_id_is_pmid": "/mnt/D/OcularKB/ocularkb/rag/scripts/stage1b_v11.py:229 (OcularKB 树；构建脚本未随仓)",
}
os.makedirs(OUT, exist_ok=True)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def norm_title(t):
    """规范化题名：NFKC → lower → 非字母数字折叠为单空格。"""
    if not t:
        return ""
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


# ---------------------------------------------------------------- 引用侧
def load_cited(path):
    cited = {}
    n_cit = 0
    with open(path, encoding="utf-8") as f:          # 流式
        for line in f:
            e = json.loads(line)
            for c in (e.get("citations") or []):
                n_cit += 1
                p = str(c.get("pmid") or "").strip()
                if not p:
                    continue
                r = cited.get(p)
                if r is None:
                    r = cited[p] = {
                        "pmid": p, "titles": [], "journals": [], "years": [],
                        "n_citations": 0, "entries": [], "has_doi": False,
                        "has_pmcid": False, "empty_title_cits": 0,
                        "raw_title_lens": [],
                    }
                r["n_citations"] += 1
                eid = e.get("entry_id")
                if eid and eid not in r["entries"]:
                    r["entries"].append(eid)
                t = c.get("title") or ""
                if t:
                    r["titles"].append(t)
                    r["raw_title_lens"].append(len(t))
                else:
                    r["empty_title_cits"] += 1
                if c.get("journal"):
                    r["journals"].append(c["journal"])
                if c.get("year"):
                    r["years"].append(str(c["year"]))
                if c.get("doi"):
                    r["has_doi"] = True
                if c.get("pmcid"):
                    r["has_pmcid"] = True
    return cited, n_cit


# ---------------------------------------------------------------- 语料侧
def load_corpus(path):
    rows = []
    with open(path, encoding="utf-8") as f:          # 流式
        for line in f:
            d = json.loads(line)
            rows.append({
                "paper_id": str(d.get("paper_id") or "").strip(),
                "pmcid": (d.get("pmcid") or "").strip(),
                "doi": (d.get("doi") or "").strip(),
                "title": d.get("title") or "",
                "journal": d.get("journal") or "",
                "year": str(d.get("year") or ""),
                "n_chunks": int(d.get("n_chunks") or 0),
                "is_preprint": int(d.get("is_preprint") or 0),
                "title_norm": norm_title(d.get("title") or ""),
            })
    return rows


def main():
    cited, n_cit_total = load_cited(CITED)
    corpus = load_corpus(CORPUS)
    by_id = {r["paper_id"]: r for r in corpus}
    corpus_norms = collections.defaultdict(list)
    for r in corpus:
        if r["title_norm"]:
            corpus_norms[r["title_norm"]].append(r["paper_id"])
    corpus_prefix40 = collections.defaultdict(list)
    for r in corpus:
        if r["title_norm"]:
            corpus_prefix40[r["title_norm"][:40]].append(r["paper_id"])

    pmids = sorted(cited)

    # ---------------- 主匹配：标识键 pmid ↔ paper_id
    conn_rows = []
    unmatched_rows = []          # (pmid, caliber, ...)
    reason_counter = collections.Counter()
    bucket_counter = collections.Counter()
    corpus_cited = collections.defaultdict(lambda: {"n_citations": 0, "entries": set()})

    for p in pmids:
        r = cited[p]
        cr = by_id.get(p)
        # 引用侧题名代表值：取最长的一条（截断只在 build 侧发生，长者为信息量最大者）
        ct_raw = max(r["titles"], key=len) if r["titles"] else ""
        ct_norm = norm_title(ct_raw)
        key_used = "pmid" if cr else ""
        level = "exact" if cr else "unmatched"

        # ---- 题名口径（与主键独立，仅供并报）
        strict = bool(ct_norm) and bool(cr) and (ct_norm in corpus_norms)
        pre40 = bool(ct_norm) and bool(cr) and (ct_norm[:40] in corpus_prefix40)
        title_level = "normalized" if strict else ("fuzzy" if pre40 else "none")

        sim = ""
        y_match = j_match = ""
        reason_code = reason_text = ""
        if cr:
            if ct_norm and cr["title_norm"]:
                sim = round(difflib.SequenceMatcher(None, ct_norm, cr["title_norm"]).ratio(), 4)
            if r["years"] and cr["year"]:
                y_match = "yes" if cr["year"] in r["years"] else "no"
            if r["journals"] and cr["journal"]:
                j_match = "yes" if cr["journal"] in r["journals"] else "no"

        # ---- 未对上（按题名口径）逐条原因分类（两口径各一行）
        def classify():
            """返回 (reason_code, reason_text, bucket)；bucket 按固定优先级唯一归属。"""
            if not ct_raw:
                return ("TITLE_EMPTY_CITED",
                        "引用记录无题名（该篇经 gene-index 路径加入，build_link_registry.py:246 置空）",
                        "其他")
            if not cr:
                return ("PAPER_ABSENT_FROM_CORPUS",
                        "语料 papers.jsonl 无此 paper_id（本条口径下唯一可归入「语料无此文」的形态）",
                        "语料无此文")
            if not cr["title_norm"]:
                return ("TITLE_EMPTY_CORPUS", "语料侧题名为空", "其他")
            if str(p).startswith("PPR_"):
                return ("PREPRINT_ID", "引用侧 id 为预印本 PPR 标识", "预印本或全文缺")
            if cr["n_chunks"] == 0:
                return ("FULLTEXT_MISSING_ZERO_CHUNK",
                        "语料该篇 n_chunks=0（幽灵条目：有元数据无正文）", "预印本或全文缺")
            if len(ct_raw) == 120:
                return ("TITLE_TRUNCATED_120",
                        "引用侧题名被 build_link_registry.py:175 截到 120 字符，与全题名规范化后非全等",
                        "标题写法差异")
            if sim != "" and sim >= 0.95:
                return ("TITLE_PUNCT_CASE", f"题名写法差异（标点/大小写/空白规范化差异，sim={sim}）",
                        "标题写法差异")
            if sim != "" and sim >= 0.70:
                return ("TITLE_REWRITTEN", f"题名写法差异（改写/缩写，sim={sim}）", "标题写法差异")
            return ("TITLE_DIVERGENT", f"题名写法差异（差异过大 sim={sim}，需人工核）", "标题写法差异")

        if not strict:
            reason_code, reason_text, bucket = classify()
            unmatched_rows.append({
                "pmid": p, "caliber": "A_strict_title_exact",
                "cited_title": ct_raw, "corpus_title": (cr or {}).get("title", ""),
                "corpus_paper_id": (cr or {}).get("paper_id", ""), "title_sim": sim,
                "reason_code": reason_code, "reason_text": reason_text,
                "bucket": bucket, "reachable_by_pmid": "yes" if cr else "no",
            })
            reason_counter[reason_code] += 1
            bucket_counter[bucket] += 1
        if not pre40:
            rc2, rt2, b2 = classify()
            unmatched_rows.append({
                "pmid": p, "caliber": "B_relaxed_title_prefix40",
                "cited_title": ct_raw, "corpus_title": (cr or {}).get("title", ""),
                "corpus_paper_id": (cr or {}).get("paper_id", ""), "title_sim": sim,
                "reason_code": rc2, "reason_text": rt2,
                "bucket": b2, "reachable_by_pmid": "yes" if cr else "no",
            })

        if cr:
            corpus_cited[p]["n_citations"] += r["n_citations"]
            corpus_cited[p]["entries"].update(r["entries"])

        conn_rows.append({
            "pmid": p,
            "key_used": key_used or "",
            "corpus_paper_id": (cr or {}).get("paper_id", ""),
            "match_level": level,
            "title": ct_raw,
            "year": ",".join(sorted(set(r["years"]))),
            "journal": "; ".join(sorted(set(r["journals"]))),
            "corpus_title": (cr or {}).get("title", ""),
            "corpus_pmcid": (cr or {}).get("pmcid", ""),
            "corpus_doi": (cr or {}).get("doi", ""),
            "corpus_n_chunks": (cr or {}).get("n_chunks", ""),
            "corpus_is_preprint": (cr or {}).get("is_preprint", ""),
            "n_citations": r["n_citations"],
            "n_entries": len(r["entries"]),
            "cited_by_entries": "|".join(sorted(r["entries"])),
            "id_is_numeric_pmid": "yes" if str(p).isdigit() else "no",
            "caliber_A_strict_title": "hit" if strict else "miss",
            "caliber_B_title_prefix40": "hit" if pre40 else "miss",
            "title_key_level": title_level,
            "title_sim_vs_corpus": sim,
            "year_agree": y_match,
            "journal_agree": j_match,
            "cited_side_has_doi": "yes" if r["has_doi"] else "no",
            "cited_side_has_pmcid": "yes" if r["has_pmcid"] else "no",
        })

    # ---------------- 反向：语料全量两档
    touch_rows = []
    for r in corpus:
        ci = corpus_cited.get(r["paper_id"])
        touch_rows.append({
            "corpus_paper_id": r["paper_id"],
            "pmid_available": "yes" if r["paper_id"].isdigit() else "no",
            "pmid": r["paper_id"] if r["paper_id"].isdigit() else "",
            "pmcid": r["pmcid"],
            "doi": r["doi"],
            "title": r["title"],
            "year": r["year"],
            "journal": r["journal"],
            "is_preprint": r["is_preprint"],
            "n_chunks": r["n_chunks"],
            "touch_class": "CITED_AS_EVIDENCE" if ci else "NOT_CITED",
            "n_citations": ci["n_citations"] if ci else 0,
            "n_entries": len(ci["entries"]) if ci else 0,
            "cited_by_entries": "|".join(sorted(ci["entries"])) if ci else "",
        })

    # ---------------- 候选 registry 盘点
    reg_rows = []
    for name, path in REG_CANDIDATES:
        if not os.path.exists(path):
            reg_rows.append({"name": name, "path": path, "exists": "no"})
            continue
        es = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                es.append(json.loads(line))
        pm = set()
        cits = 0
        empty = 0
        for e in es:
            for c in (e.get("citations") or []):
                cits += 1
                if c.get("pmid"):
                    pm.add(str(c["pmid"]))
                if not (c.get("title") or ""):
                    empty += 1
        reg_rows.append({
            "name": name, "path": path, "exists": "yes",
            "entries": len(es), "citations": cits, "unique_pmid": len(pm),
            "empty_title_citations": empty,
            "sha256": sha256_file(path),
            "matches_brief_denominator_803": "yes" if len(pm) == 803 else "no",
        })

    # ---------------- 写盘
    def sanitize(v):
        """行内不可含 \r\n\t —— 否则 TSV 的物理行数 ≠ 逻辑行数，协调者的 awk/grep 逐行核对会误报
        （实测：未清洗时 UNMATCHED 逻辑 1003 行被读成 1009 物理行）。"""
        if isinstance(v, str):
            return v.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        return v

    def write_tsv(fn, rows, cols):
        with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: sanitize(v) for k, v in r.items()})
        return len(rows)

    n1 = write_tsv("CONNECT_KEY_v1.tsv", conn_rows, list(conn_rows[0].keys()))
    n2 = write_tsv("UNMATCHED_v1.tsv", unmatched_rows,
                   ["pmid", "caliber", "cited_title", "corpus_title", "corpus_paper_id",
                    "title_sim", "reason_code", "reason_text", "bucket", "reachable_by_pmid"])
    n3 = write_tsv("CORPUS_TOUCH_v1.tsv", touch_rows, list(touch_rows[0].keys()))
    n4 = write_tsv("REGISTRY_SOURCES_v1.tsv", reg_rows, list(reg_rows[0].keys()))

    # ---------------- 统计
    N = len(pmids)
    hitA = sum(1 for r in conn_rows if r["caliber_A_strict_title"] == "hit")
    hitB = sum(1 for r in conn_rows if r["caliber_B_title_prefix40"] == "hit")
    hitC = sum(1 for r in conn_rows if r["match_level"] == "exact")
    cited_corpus = sum(1 for r in touch_rows if r["touch_class"] == "CITED_AS_EVIDENCE")
    cited_ids = set(pmids)
    corpus_id_set = set(by_id)
    absent = [p for p in pmids if p not in corpus_id_set]

    # ---- 语料稳健性交叉：换用仓件随件 slim 重算三档（结论对语料选择免疫的机器证据）
    rob = {"primary_corpus": CORPUS, "rows_primary": len(corpus),
           "A_hit": hitA, "B_hit": hitB, "C_hit": hitC}
    if os.path.exists(CORPUS_ROBUSTNESS):
        alt = load_corpus(CORPUS_ROBUSTNESS)
        alt_ids = {r["paper_id"] for r in alt}
        alt_tn, alt_pf = set(), set()
        for r in alt:
            if r["title_norm"]:
                alt_tn.add(r["title_norm"])
                alt_pf.add(r["title_norm"][:40])
        a = b = c2 = 0
        for p in pmids:
            ct = max(cited[p]["titles"], key=len) if cited[p]["titles"] else ""
            n = norm_title(ct)
            if p in alt_ids:
                c2 += 1
            if n and n in alt_tn:
                a += 1
            if n and n[:40] in alt_pf:
                b += 1
        rob.update({"alt_corpus": CORPUS_ROBUSTNESS, "rows_alt": len(alt),
                    "alt_sha256": sha256_file(CORPUS_ROBUSTNESS),
                    "A_hit_alt": a, "B_hit_alt": b, "C_hit_alt": c2,
                    "identical": (a == hitA and b == hitB and c2 == hitC)})
    sims = [r["title_sim_vs_corpus"] for r in conn_rows if r["title_sim_vs_corpus"] != ""]
    zero_chunk_among_matched = sum(1 for r in conn_rows if r["corpus_n_chunks"] == 0)
    doi_avail = sum(1 for r in conn_rows if r["cited_side_has_doi"] == "yes")
    pmcid_avail = sum(1 for r in conn_rows if r["cited_side_has_pmcid"] == "yes")
    yj = [(r["year_agree"], r["journal_agree"]) for r in conn_rows if r["year_agree"]]
    year_yes = sum(1 for y, j in yj if y == "yes")
    jr = [(y, j) for y, j in yj if j]
    jour_yes = sum(1 for y, j in jr if j == "yes")

    stats = {
        "cited_unique_pmid": N,
        "cited_total_citations": n_cit_total,
        "corpus_rows": len(corpus),
        "corpus_unique_paper_id": len(corpus_id_set),
        "caliber_A_strict_title": {"hit": hitA, "denom": N, "pct": round(hitA / N * 100, 2)},
        "caliber_B_relaxed_title_prefix40": {"hit": hitB, "denom": N, "pct": round(hitB / N * 100, 2)},
        "caliber_C_identifier_pmid": {"hit": hitC, "denom": N, "pct": round(hitC / N * 100, 2)},
        "doi_key_available_on_cited_side": doi_avail,
        "pmcid_key_available_on_cited_side": pmcid_avail,
        "cited_absent_from_corpus": len(absent),
        "corpus_rows_cited_as_evidence": cited_corpus,
        "corpus_rows_not_cited": len(corpus) - cited_corpus,
        "title_sim_vs_corpus": {
            "n": len(sims),
            "min": min(sims) if sims else None,
            "median": sorted(sims)[len(sims) // 2] if sims else None,
            "mean": round(sum(sims) / len(sims), 4) if sims else None,
            "lt_0.90": sum(1 for s in sims if s < 0.90),
        },
        "year_agree": {"yes": year_yes, "denom": len(yj)},
        "journal_agree": {"yes": jour_yes, "denom": len(jr)},
        "corpus_robustness": rob,
        "matched_rows_with_zero_chunks": zero_chunk_among_matched,
        "unmatched_rows_reason_counts": dict(reason_counter),
        "unmatched_rows_bucket_counts": dict(bucket_counter),
        "rows_written": {"CONNECT_KEY_v1.tsv": n1, "UNMATCHED_v1.tsv": n2,
                         "CORPUS_TOUCH_v1.tsv": n3, "REGISTRY_SOURCES_v1.tsv": n4},
        "source_anchors": SRC_ANCHORS,
        "inputs": {"cited_registry": CITED, "corpus": CORPUS,
                   "cited_sha256": sha256_file(CITED), "corpus_sha256": sha256_file(CORPUS)},
        "ts_note": "all rates are machine-recomputed from the two on-disk files named above",
    }
    with open(os.path.join(OUT, "LINKKEY_STATS_v1.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2, sort_keys=True)

    # 原因明细抽样（供口径说明引用；截断型/改写型各 5 条）
    sample = {}
    for code in ("TITLE_TRUNCATED_120", "TITLE_REWRITTEN", "TITLE_EMPTY_CITED", "TITLE_PUNCT_CASE"):
        ex = [r for r in unmatched_rows if r["reason_code"] == code and r["caliber"] == "A_strict_title_exact"][:5]
        sample[code] = [{"pmid": r["pmid"], "cited_title": r["cited_title"][:90],
                         "corpus_title": r["corpus_title"][:90], "sim": r["title_sim"]} for r in ex]
    with open(os.path.join(OUT, "LINKKEY_REASON_SAMPLES_v1.json"), "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2, sort_keys=True)

    print(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True))
    print("\n[OK] data outputs written; manifest is generated separately by make_manifest.py "
          "(must run after CALIBER_NOTE/README exist)")


if __name__ == "__main__":
    main()