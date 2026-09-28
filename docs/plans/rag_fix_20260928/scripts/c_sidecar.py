#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 C 档索引旁挂 (两路径, 按 TIER_C_index_backlog.md 定义执行, 不动语料正文/面板核心字节)

路径1 链回填旁挂:
  输入 = RAGGAP out/tier_C_backlog.tsv 830 行 (gene, lib_entry, c_grade, ctx_papers, link_candidate_pmids)
  验证 = 候选 PMID 在 v2.3 继承库 (v2.4 的 A 部分) 有 chunk (papers.jsonl n_chunks>0)
  产物 = kb/markers/_raggap_c_linkbackfill_v1.json  (INERT_REGISTERED_DATA, 默认 OFF;
         下划线前缀不入加载 glob, 仿 _k9_ocs_rules_overlay_v1.json 先例)
  应用规则 (激活时): 按 library+entry+gene 定位 {gene, evidence} 节点, 向 evidence 追加
        {"type":"pmid","id":"PMID:<X>","in_corpus":true,"note":"RAGGAP-C backfill (t_d0bea5a6)"}
        已含该 PMID 的不重复追加 (KB1v2d 先例格式)。本卡不改词条本体字节。

路径2 面板字段扩展旁挂 (marker 共现面):
  v2.1 起 chunk.marker_genes 列仅 40 基因 QA 面板 → search_literature 共现面缺词条基因。
  本卡产出「chunk 级扩展共现」旁挂表: 对 402 词条基因表 (RAGGAP kb_entries_genes.tsv) 用
  与现役完全同源的词边界大小写不敏感 token 匹配扫 v2.4 全部 chunk text, 输出
  row_idx → extra_genes (面板外但词条内的命中基因)。不动 v2.4 parquet 任何字节;
  激活=未来版本按 v2.2 先例只重算该列元数据 (embedding 零重算), 或消费方读旁挂表合并视图。

红线: 不写 v2.0-2.3 / markers_*.json 本体 / panels_v5.json; 全部产物=新文件。
"""
import json, os, re, sys, time, hashlib

PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
RAGGAP = "/mnt/D/EyeKB/plans/rag_gap_20260928"
V23_PAPERS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.3_2026-09/papers.jsonl"
OUTSIDE = f"{PLAN}/out"
os.makedirs(OUTSIDE, exist_ok=True)
os.makedirs(f"{PLAN}/work", exist_ok=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------- 路径 1 ----------------
def path1():
    # 库内 chunked 论文集合 (v2.3 继承面 = C 档候选的来源面)
    in_corpus = {}
    for line in open(V23_PAPERS, encoding="utf-8"):
        d = json.loads(line)
        in_corpus[str(d["paper_id"])] = int(d.get("n_chunks", 0))
    rows = []
    with open(f"{RAGGAP}/out/tier_C_backlog.tsv", encoding="utf-8") as f:
        header = f.readline()  # RAGGAP 已知表头逐字拆分 bug (数据行列序: gene,entry,c_grade,ctx_papers,candidates)
        for line in f:
            parts = line.rstrip("\r\n").split("\t")
            if len(parts) < 5 or parts[0] == "g":
                continue
            gene, entry, grade, ctx, cands = parts[0], parts[1], parts[2], parts[3], parts[4]
            lib = entry.split("/", 1)[0] if "/" in entry else ""
            pm = [p.strip() for p in cands.split(",") if p.strip()]
            ver = {p: ("in_corpus" if in_corpus.get(p, 0) > 0 else
                       ("ghost" if p in in_corpus else "absent")) for p in pm}
            rows.append({"gene": gene, "library": lib, "entry": entry, "c_grade": grade,
                         "ctx_papers": int(ctx) if ctx.isdigit() else None,
                         "candidate_pmids": pm,
                         "candidate_status_v23": ver,
                         "verified_in_corpus_n": sum(1 for v in ver.values() if v == "in_corpus")})
    assert len(rows) == 830, f"C rows {len(rows)} != 830"
    strong = sum(1 for r in rows if r["c_grade"] == "C_strong")
    mid = sum(1 for r in rows if r["c_grade"] == "C_mid")
    zero_ver = sum(1 for r in rows if r["verified_in_corpus_n"] == 0)
    sidecar = {
        "schema": "eyekb-raggap-c-linkbackfill/1.0",
        "version": "c-linkbackfill-registered-v1",
        "registered_at": time.strftime("%F %T"),
        "card": "t_d0bea5a6 (RAGFIX D19)",
        "upstream": f"{RAGGAP}/out/tier_C_backlog.tsv (sha256={sha(RAGGAP + '/out/tier_C_backlog.tsv')})",
        "status": "INERT_REGISTERED_DATA — 非可查询库：不在 MARKER_LIBS、不在任何加载 glob、"
                  "MCP 运行时不读本件。注册=数据落库留档，非行为变更；激活另需 PI 批。",
        "apply_rule": "按 library+entry+gene 在词条 JSON 定位 {gene, evidence} 节点, 向 evidence "
                      "追加 {\"type\":\"pmid\",\"id\":\"PMID:<X>\",\"in_corpus\":true,"
                      "\"note\":\"RAGGAP-C backfill (t_d0bea5a6)\"}; 已含该 PMID 不重复追加 "
                      "(KB1v2d 先例格式); 本件不自动改词条本体。",
        "caveats": [
            "候选=词边界 token 匹配 (元数据级近似), 基因提及≠该文支持该基因作该语境 marker; "
            "激活前需逐行语境抽检 (RAGGAP §5 局限原样继承)",
            f"{zero_ver} 行候选在 v2.3 全部不可证 in_corpus (ghost/absent), 回填价值=弱, 已逐候选标注状态",
        ],
        "counts": {"rows": len(rows), "C_strong": strong, "C_mid": mid,
                   "fully_unverified_rows": zero_ver},
        "rows": rows,
    }
    dst = "/mnt/D/EyeKB/kb/markers/_raggap_c_linkbackfill_v1.json"
    json.dump(sidecar, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[path1] {dst}: rows={len(rows)} strong={strong} mid={mid} unverified_rows={zero_ver}")
    # 行级明细 TSV (plans 侧账)
    with open(f"{OUTSIDE}/C_path1_rows_detail.tsv", "w") as w:
        w.write("gene\tlibrary\tentry\tc_grade\tctx_papers\tcandidates\tverified_n\tall_status\n")
        for r in rows:
            w.write(f"{r['gene']}\t{r['library']}\t{r['entry']}\t{r['c_grade']}\t{r['ctx_papers']}\t"
                    f"{','.join(r['candidate_pmids'])}\t{r['verified_in_corpus_n']}\t"
                    f"{json.dumps(r['candidate_status_v23'])}\n")


# ---------------- 路径 2 ----------------
def path2():
    vocab = set()
    with open(f"{RAGGAP}/out/kb_entries_genes.tsv", encoding="utf-8") as f:
        header = f.readline().rstrip("\r\n").split("\t")
        gi = header.index("gene")
        for line in f:
            g = line.rstrip("\r\n").split("\t")[gi].strip().upper()
            if re.fullmatch(r"[A-Z0-9\-]{2,20}", g):
                vocab.add(g)
    print(f"[path2] vocab genes = {len(vocab)}")
    pat = re.compile(r"\b(" + "|".join(sorted(vocab, key=len, reverse=True)) + r")\b", re.I)
    import pandas as pd
    df = pd.read_parquet("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09/chunks.parquet",
                         columns=["paper_id", "text", "marker_genes"])
    # 现面板基因 (来自面板列并集) 也要从 extra 排除口径=面板内不算 extra
    panel = set()
    def _aslist(mg):
        if mg is None:
            return []
        try:
            return list(mg)
        except TypeError:
            return []
    for mg in df["marker_genes"].head(50000):
        panel.update(g.upper() for g in _aslist(mg))
    t0 = time.time()
    n_rows_with_extra = 0
    genes_with_cooccur = set()
    with open(f"{OUTSIDE}/C_path2_panel_expansion.tsv", "w") as w:
        w.write("row_idx\tpaper_id\textra_genes\n")
        for i, (pid, text, mg) in enumerate(zip(df["paper_id"], df["text"], df["marker_genes"])):
            hits = {m.group(0).upper() for m in pat.finditer(text)} if text else set()
            extra = sorted(hits - {g.upper() for g in _aslist(mg)})
            if extra:
                w.write(f"{i}\t{pid}\t{';'.join(extra)}\n")
                n_rows_with_extra += 1
                genes_with_cooccur.update(extra)
            if i % 50000 == 0:
                print(f"  scan {i}/{len(df)} ({time.time()-t0:.0f}s)", flush=True)
    n_chunks_total = int(len(df))
    del df
    summ = {"vocab_genes": len(vocab), "panel_genes_observed": len(panel),
            "chunks_total": n_chunks_total,
            "rows_with_extra": n_rows_with_extra,
            "extra_genes_with_cooccurrence": len(genes_with_cooccur),
            "extra_genes_no_cooccurrence": sorted(vocab - genes_with_cooccur - panel),
            "note": "row_idx=v2.4 chunks.parquet 0-based 行序 (继承段=v2.3 原序, 增量段追加在后); "
                    "本表不改 parquet 任何字节; 激活=未来版本重算 marker_genes 列 (v2.2 先例) 或消费方合并读"}
    json.dump(summ, open(f"{OUTSIDE}/C_path2_summary.json", "w"), indent=1, ensure_ascii=False)
    print(f"[path2] rows_with_extra={n_rows_with_extra} genes_cooccur={len(genes_with_cooccur)} "
          f"no_cooccur={len(summ['extra_genes_no_cooccurrence'])} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    path1()
    if "--p2" in sys.argv:
        path2()
