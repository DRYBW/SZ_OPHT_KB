#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 stage ra3_merge: v2.4.2 = v2.4.1 全量继承 (embedding 原样复制, 零重算, v2.4.1 字节不动)
+ RA3 备选104准入增量 103 篇 (闭集 out/closed_set_ra3_pmids.txt, 机械四检扫描账=work/ra3_scan_ledger.tsv)
Part A:   v2.4.1 parquet 231,707 chunks 原样 (文本/向量/全部列零改动)
Part RA3: work/chunks_ra3_raw.jsonl — embedding 新算 (CPU bge-large-en-v1.5 fp32 normalize=True,
          与 v2.2/2.3/2.4/2.4.1 增量同模型同精度)
输出: literature_db/v2.4.2_2026-09/{chunks.parquet, papers.jsonl, build_stats.json, manifest.yaml}
红线: v2.4/v2.4.1 全程只读 (基线 ledgers/SHA_PRE_inputs_20260928.txt); 新 paper_id 与 v2.4.1 零交集断言;
      不触 plans/evalset/; 禁 GPU (device="cpu" 硬编码)
运行: systemd-run --user -p MemoryMax=20G /home/ubuntu/.conda/envs/pipeline_env/bin/python ra3_merge.py
"""
import json, os, sys, time, hashlib
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
V241_DIR = f"{BASE}/literature_db/v2.4.1_2026-09"
V241_PARQUET = f"{V241_DIR}/chunks.parquet"
V241_PAPERS = f"{V241_DIR}/papers.jsonl"
PLAN3 = "/mnt/D/EyeKB/plans/rag_fix3_20260928"
CHUNKS_RA3 = f"{PLAN3}/work/chunks_ra3_raw.jsonl"
OUTDIR = f"{BASE}/literature_db/v2.4.2_2026-09"
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"
os.makedirs(OUTDIR, exist_ok=True)

EXPECTED_COLS_PREFIX = ["paper_id", "pmcid", "title", "journal", "year", "doi"]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def main():
    t_all = time.time()
    print("[A] 读 v2.4.1 parquet (继承 embedding)...", flush=True)
    dfA = pd.read_parquet(V241_PARQUET)
    nA = len(dfA)
    cols = list(dfA.columns)
    assert cols[:6] == EXPECTED_COLS_PREFIX, f"schema drift: {cols[:6]}"
    assert "is_preprint" in cols and "embedding" in cols and "full_text_available" in cols
    v241_pids = set(str(x) for x in dfA.paper_id.unique())
    print(f"    A: {nA} chunks, papers={dfA.paper_id.nunique()}, cols={len(cols)}", flush=True)
    assert nA == 231707, f"v2.4.1 inheritance count drift: {nA}"

    rowsRA3 = [json.loads(l) for l in open(CHUNKS_RA3, encoding="utf-8")]
    nRA3 = len(rowsRA3)
    ra3_pids = {str(r["paper_id"]) for r in rowsRA3}
    assert not (ra3_pids & v241_pids), f"paper_id overlap with v2.4.1: {ra3_pids & v241_pids}"
    print(f"[RA3] 新 chunks: {nRA3}, papers: {len(ra3_pids)}", flush=True)
    texts = [r["text"] for r in rowsRA3]

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_DIR, device="cpu")
    print("    模型就绪 bge-large-en-v1.5 (cpu, fp32, normalize=True)", flush=True)
    embRA3 = model.encode(texts, batch_size=64, normalize_embeddings=True,
                          show_progress_bar=False).astype(np.float32).reshape(nRA3, 1024)

    dfRA3 = pd.DataFrame([{c: r.get(c) for c in cols if c != "embedding"} for r in rowsRA3])
    dfRA3["embedding"] = [embRA3[i] for i in range(nRA3)]
    del embRA3
    ftmap = json.load(open(f"{PLAN3}/work/ra3_ftstatus.json"))
    dfRA3["full_text_available"] = [int(ftmap.get(str(r["paper_id"]), 1)) for r in rowsRA3]
    dfRA3 = dfRA3.reindex(columns=list(dfA.columns))

    df = pd.concat([dfA, dfRA3], ignore_index=True)
    out = f"{OUTDIR}/chunks.parquet"
    df.to_parquet(out, index=False)
    print(f"[5] SAVED {out}: {len(df)} rows, {os.path.getsize(out)/1e6:.1f} MB ({time.time()-t_all:.0f}s)", flush=True)

    nch = df.groupby("paper_id").size().to_dict()
    n_fta = df.groupby("paper_id")["full_text_available"].max().to_dict()
    seen_new = set()
    n_ghost = 0
    with open(f"{OUTDIR}/papers.jsonl", "w", encoding="utf-8") as f:
        for line in open(V241_PAPERS, encoding="utf-8"):
            p = json.loads(line)
            p["n_chunks"] = int(nch.get(str(p["paper_id"]), p.get("n_chunks", 0)))
            if p["n_chunks"] == 0:
                n_ghost += 1
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            seen_new.add(str(p["paper_id"]))
        for r in rowsRA3:
            pid = str(r["paper_id"])
            if pid in seen_new:
                continue
            seen_new.add(pid)
            f.write(json.dumps({
                "paper_id": pid, "pmcid": r.get("pmcid", ""), "title": r.get("title", ""),
                "journal": r.get("journal", ""), "year": r.get("year", ""), "doi": r.get("doi", ""),
                "species": r.get("species", "unknown"),
                "tissues": sorted(set(r.get("tissue_labels_paper") or [])),
                "source_version": "v2.4.2-ra3", "admission_lane": "ragfix3_backup104_scan",
                "fulltext_status": "full_text" if int(ftmap.get(pid, 1)) else "abstract_only",
                "is_preprint": int(r.get("is_preprint", 0)),
                "full_text_available": int(n_fta.get(pid, 1)),
                "n_chunks": int(nch.get(pid, 0)),
            }, ensure_ascii=False) + "\n")

    import collections
    per_ra3 = collections.Counter(str(r["paper_id"]) for r in rowsRA3)
    ft_absent_new = sum(1 for pid, v in ftmap.items() if int(v) == 0)
    stats = {"n_chunks": int(len(df)), "n_chunks_A_inherited_v241": int(nA),
             "n_chunks_RA3_new": int(nRA3),
             "n_papers": int(df.paper_id.nunique()),
             "n_papers_preprint": int(df[df.is_preprint == 1].paper_id.nunique()),
             "n_papers_fulltext_absent": int(df[df.full_text_available == 0].paper_id.nunique()),
             "ra3_per_paper": dict(per_ra3),
             "species": {k: int(v) for k, v in df.species.value_counts().items()},
             "parquet_MB": round(os.path.getsize(out) / 1e6, 1)}
    json.dump(stats, open(f"{OUTDIR}/build_stats.json", "w"), indent=1, ensure_ascii=False)

    n_lines = sum(1 for _ in open(f"{OUTDIR}/papers.jsonl"))
    closed = [l.strip() for l in open(f"{PLAN3}/out/closed_set_ra3_pmids.txt") if l.strip()]
    manifest = f"""version: v2.4.2_2026-09
created: '2026-09-28'
description: >
  v2.4.2 = v2.4.1 全量继承 (231,707 chunks 原样零重算) + RAGFIX3 备选104批处置增量 103 篇
  {nRA3} chunks (卡 t_b94d0999, 上游=USER_DIRECTIVE_20260928 追加五 PI 整链授权; 执行方案=
  BRIEF_RAGFIX3.md §1 机械四检零 LLM 扫描: V1 题录可核(EPMC EXT_ID 单篇回查∧标题前缀逐字) ∧
  V2 不在库(paper_id∪doi 查重) ∧ V3 非 HRCA 自引∪撤证∪closed64∪RA2_17 防双计 ∧ V4 OA 实测
  (curl -sI HEAD; HEAD 无 Content-Length→体积由 GET 实测=DECISION_MATRIX 预注册注记))。
  扫描账: 104 行→准入 103 (93 FULLTEXT + 10 ABS_ONLY 沿 RA2 先例入库), 拒 1 (40171795=RA2 白名单
  成员防双计)。下载账 19.33MB ≤ 100MB 波次预算, 零清单外下载, 零付费墙触碰, 无 >1GB 拒收项,
  无 SKIPPED_CAP。7 目标单元兑现 6 (COL19A1/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B), C8ORF76 诚实
  MISS (两候选全文无词边界 token); 副产品兑现 FAM135A/LMOD1/LILRB2(text 路) 见 RAGFIX3_NOTE。
inheritance:
  v2.4.1: >-
    literature_db/v2.4.1_2026-09/chunks.parquet {nA} chunks 原样继承 (文本/向量/全部列零改动)
  v2.4.1_frozen_sha256: {{"v2.4.1 chunks.parquet": "{sha(V241_PARQUET)}", "v2.4.1 papers.jsonl": "{sha(V241_PAPERS)}", "v2.4.1 manifest.yaml": "{sha(V241_DIR + '/manifest.yaml')}"}}
  baseline_recorded_at: {PLAN3}/ledgers/SHA_PRE_inputs_20260928.txt (开卡快照; 收尾复核=零改动证明)
chunker_provenance:
  code: stage2a_parse_xml_v2 + stage2b_chunk_v2 (与 v2.1-2.4.1 完全同源纯函数, 零改动复用)
  note: 卡内 scripts/ra3_parse_chunk.py 逐行同构 ra2_parse_chunk.py (t_6848d3de); 1 篇 XML 不合规
    (PMC13587881, lxml 属性缺陷) fallback abstract-only 如实登记
increment_lane:
  name: ragfix3_backup104_scan (t_b94d0999, 机械四检扫描闭集, 零 LLM, 非检索式裸回填)
  n_papers: {len(per_ra3)}
  closed_set: {PLAN3}/out/closed_set_ra3_pmids.txt ({len(closed)} PMID)
  scan_ledger: {PLAN3}/work/ra3_scan_ledger.tsv (逐 PMID 四检判决+通道+HEAD 码)
  download_ledger: {PLAN3}/work/ra3_availability.tsv (逐 PMID 成败+体积+物种)
  decision_matrix: {PLAN3}/out/DECISION_MATRIX_RAGFIX3.md (预注册 sha=b3787101187ceba27bdf9357662b6be501b0c6165e1d103015eb979982d80836)
  download_total_xml_MB: 19.33 (≤100MB 波次预算; 通道=PORT 代理优先/直连回退, 逐条记账)
  abstract_only_pmids: {sorted([p for p, v in ftmap.items() if int(v) == 0])}
embedding_provenance:
  model: bge-large-en-v1.5 ({MODEL_DIR}, fp32, normalize=True)
  device: cpu (与 v2.2/2.3/2.4/2.4.1 增量同模型同精度; 本卡禁 GPU 铁律)
counts:
  n_chunks: {stats['n_chunks']}
  n_papers: {stats['n_papers']}  # = parquet unique paper_id
  papers_jsonl_lines: {n_lines}
  papers_jsonl_zero_chunk_ghosts: {n_ghost}  # 历史遗留, 自 v2.4.1 原样继承
  n_papers_preprint: {stats['n_papers_preprint']}
  n_papers_fulltext_absent: {stats['n_papers_fulltext_absent']}  # v2.4.1 面 245 + RA3 abstract_only {ft_absent_new}
  parquet_MB: {stats['parquet_MB']}
redlines:
  v2.4.1_zero_change_verified: 见 {PLAN3}/ledgers/SHA_POST_verify_20260928.txt (收尾复核)
  v2.4_v2.3_v2.2_v2.1_v2.0_v1x_untouched: true (全程只读)
  evalset_untouched: true
  mcp_default_db_unchanged: true (EYEKB_DB_POINTER default=v2.0 未动; v2.4.2 仅注册)
"""
    open(f"{OUTDIR}/manifest.yaml", "w", encoding="utf-8").write(manifest)
    print("DONE", json.dumps({k: stats[k] for k in ("n_chunks", "n_papers",
          "n_papers_preprint", "n_papers_fulltext_absent", "parquet_MB")}), flush=True)

if __name__ == "__main__":
    main()
