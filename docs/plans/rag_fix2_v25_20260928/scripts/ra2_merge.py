#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 stage ra2_merge: v2.4.1 = v2.4 全量继承 (embedding 原样复制, 零重算, v2.4 字节不动)
+ RA2 白名单增量 17 篇 (闭集 out/closed_set_ra2_pmids.txt, 三条件题录核验件=RA2_WHITELIST.tsv)
Part A:  v2.4 parquet 230,426 chunks 原样 (文本/向量/全部列零改动)
Part RA2: work/chunks_ra2_raw.jsonl — embedding 新算 (CPU bge-large-en-v1.5 fp32 normalize=True,
          与 v2.2/2.3/2.4 增量同模型同精度)
输出: literature_db/v2.4.1_2026-09/{chunks.parquet, papers.jsonl, build_stats.json, manifest.yaml}
红线: v2.0-v2.4 全程只读 (基线 ledgers/SHA_PRE_inputs_20260928.txt, 收尾复核=零改动证明);
      新 paper_id 与 v2.4 零交集断言; 不触 plans/evalset/
运行: systemd-run --user -p MemoryMax=20G /home/ubuntu/.conda/envs/pipeline_env/bin/python ra2_merge.py
"""
import json, os, sys, time, hashlib
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
V24_DIR = f"{BASE}/literature_db/v2.4_2026-09"
V24_PARQUET = f"{V24_DIR}/chunks.parquet"
V24_PAPERS = f"{V24_DIR}/papers.jsonl"
PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
CHUNKS_RA2 = f"{PLAN2}/work/chunks_ra2_raw.jsonl"
OUTDIR = f"{BASE}/literature_db/v2.4.1_2026-09"
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
    print("[A] 读 v2.4 parquet (继承 embedding)...", flush=True)
    dfA = pd.read_parquet(V24_PARQUET)
    nA = len(dfA)
    cols = list(dfA.columns)
    assert cols[:6] == EXPECTED_COLS_PREFIX, f"schema drift: {cols[:6]}"
    assert "is_preprint" in cols and "embedding" in cols and "full_text_available" in cols
    v24_pids = set(str(x) for x in dfA.paper_id.unique())
    print(f"    A: {nA} chunks, papers={dfA.paper_id.nunique()}, cols={len(cols)}", flush=True)

    rowsRA2 = [json.loads(l) for l in open(CHUNKS_RA2, encoding="utf-8")]
    nRA2 = len(rowsRA2)
    ra2_pids = {str(r["paper_id"]) for r in rowsRA2}
    assert not (ra2_pids & v24_pids), f"paper_id overlap with v2.4: {ra2_pids & v24_pids}"
    print(f"[RA2] 新 chunks: {nRA2}, papers: {len(ra2_pids)}", flush=True)
    texts = [r["text"] for r in rowsRA2]

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_DIR, device="cpu")
    print("    模型就绪 bge-large-en-v1.5 (cpu, fp32, normalize=True)", flush=True)
    embRA2 = model.encode(texts, batch_size=64, normalize_embeddings=True,
                          show_progress_bar=False).astype(np.float32).reshape(nRA2, 1024)

    dfRA2 = pd.DataFrame([{c: r.get(c) for c in cols if c != "embedding"} for r in rowsRA2])
    dfRA2["embedding"] = [embRA2[i] for i in range(nRA2)]
    del embRA2
    ftmap = json.load(open(f"{PLAN2}/work/ra2_ftstatus.json"))
    dfRA2["full_text_available"] = [int(ftmap.get(str(r["paper_id"]), 1)) for r in rowsRA2]
    dfRA2 = dfRA2.reindex(columns=list(dfA.columns))

    df = pd.concat([dfA, dfRA2], ignore_index=True)
    out = f"{OUTDIR}/chunks.parquet"
    df.to_parquet(out, index=False)
    print(f"[5] SAVED {out}: {len(df)} rows, {os.path.getsize(out)/1e6:.1f} MB ({time.time()-t_all:.0f}s)", flush=True)

    sel = {}
    for line in open(f"{PLAN2}/work/ra2_selected.jsonl", encoding="utf-8"):
        r = json.loads(line)
        sel[str(r["pmid"])] = r
    nch = df.groupby("paper_id").size().to_dict()
    n_fta = df.groupby("paper_id")["full_text_available"].max().to_dict()
    with open(f"{OUTDIR}/papers.jsonl", "w", encoding="utf-8") as f:
        for line in open(V24_PAPERS, encoding="utf-8"):
            p = json.loads(line)
            p["n_chunks"] = int(nch.get(str(p["paper_id"]), p.get("n_chunks", 0)))
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
        seen = set()
        for r in rowsRA2:
            pid = str(r["paper_id"])
            if pid in seen:
                continue
            seen.add(pid)
            f.write(json.dumps({
                "paper_id": pid, "pmcid": r.get("pmcid", ""), "title": r.get("title", ""),
                "journal": r.get("journal", ""), "year": r.get("year", ""), "doi": r.get("doi", ""),
                "species": r.get("species", "unknown"),
                "tissues": sorted(set(r.get("tissue_labels_paper") or [])),
                "source_version": "v2.4.1-ra2", "admission_lane": "ragfix2_v25_whitelist",
                "fulltext_status": "full_text" if int(ftmap.get(pid, 1)) else "abstract_only",
                "is_preprint": int(r.get("is_preprint", 0)),
                "full_text_available": int(n_fta.get(pid, 1)),
                "n_chunks": int(nch.get(pid, 0)),
            }, ensure_ascii=False) + "\n")

    import collections
    per_ra2 = collections.Counter(str(r["paper_id"]) for r in rowsRA2)
    stats = {"n_chunks": int(len(df)), "n_chunks_A_inherited_v24": int(nA),
             "n_chunks_RA2_new": int(nRA2),
             "n_papers": int(df.paper_id.nunique()),
             "n_papers_preprint": int(df[df.is_preprint == 1].paper_id.nunique()),
             "n_papers_fulltext_absent": int(df[df.full_text_available == 0].paper_id.nunique()),
             "ra2_per_paper": dict(per_ra2),
             "species": df.species.value_counts().to_dict(),
             "parquet_MB": round(os.path.getsize(out) / 1e6, 1)}
    json.dump(stats, open(f"{OUTDIR}/build_stats.json", "w"), indent=1, ensure_ascii=False)

    closed = [l.strip() for l in open(f"{PLAN2}/out/closed_set_ra2_pmids.txt") if l.strip()]
    manifest = f"""version: v2.4.1_2026-09
created: '2026-09-28'
description: >
  v2.4.1 = v2.4 全量继承 (230,426 chunks 原样零重算) + RAGFIX2 门③追补轮 RA2 白名单增量 17 篇
  (卡 t_6848d3de D21, 上游=RAGFIX_DECISION_1 P1=B 批 v2.5 追加轮; 执行方案=BRIEF_RAGFIX2.md §3
  三条件题录核验: 题录含断言词 ∧ PMID 可核 ∧ 非 HRCA 自引∧不在库防重蹈)。16 个 RAGGAP 清单
  从未配文基因 (was_S2_ctx_mismatch 型) 重跑候选检索: 10 基因兑现 (chain 3: CST1/CST4/MUC7
  回填 kb 自引 PMID; text 7: CALD1[backup顶岗]/CDH8/FCER1G/GPR143/GRM5/PTPRK/SAMSN1),
  6 基因诚实维持 none (ATP8B4/FAM135A/FBXL7/LMOD1/LRRTM3/SHISA6, 无满足三条件+可兑现候选)。
  候选闭集 104 备选 8 单元与 LILRB2 撤证缺口不在本增量面 (另案)。
  下载闭集=白名单本身 (out/closed_set_ra2_pmids.txt, 2.34MB ≤ 6MB 上限, 零清单外下载, 未绕付费墙)。
inheritance:
  v2.4: >-
    literature_db/v2.4_2026-09/chunks.parquet {nA} chunks 原样继承 (文本/向量/全部列零改动)
  v2.4_frozen_sha256: {{"v2.4 chunks.parquet": "{sha(V24_PARQUET)}", "v2.4 papers.jsonl": "{sha(V24_PAPERS)}", "v2.4 manifest.yaml": "{sha(V24_DIR + "/manifest.yaml")}"}}
  baseline_recorded_at: {PLAN2}/ledgers/SHA_PRE_inputs_20260928.txt (开卡快照; 收尾复核=零改动证明)
chunker_provenance:
  code: stage2a_parse_xml_v2 + stage2b_chunk_v2 (与 v2.1-2.4 完全同源纯函数, 零改动复用)
  note: 卡内 scripts/ra2_parse_chunk.py 逐行同构 ra_parse_chunk.py (t_d0bea5a6)
increment_lane:
  name: ragfix2_v25_whitelist (t_6848d3de, 三条件核验白名单闭集, 非检索式裸回填)
  n_papers: {len(per_ra2)}
  closed_set: {PLAN2}/out/closed_set_ra2_pmids.txt
  whitelist_ledger: {PLAN2}/out/RA2_WHITELIST.tsv (逐篇 tier/feas/slot/题录)
  token_verification: {PLAN2}/out/RA2_token_verification.tsv (词边界 token 终裁, T4 下载复核判据)
  download_ledger: {PLAN2}/work/ra2_availability.tsv (逐 PMID C2 复核+成败+体积)
  download_total_xml_MB: 2.34
  abstract_only_pmids: {sorted([p for p, v in ftmap.items() if int(v) == 0])}
  backup_substitutions: [CALD1: 39195219(primary,token miss) -> 33028893(backup,token hit)]
embedding_provenance:
  model: bge-large-en-v1.5 ({MODEL_DIR}, fp32, normalize=True)
  device: cpu (与 v2.2/2.3/2.4 增量同模型同精度)
counts:
  n_chunks: {stats['n_chunks']}
  n_papers: {stats['n_papers']}  # = parquet unique paper_id
  papers_jsonl_lines: {len(open(f'{OUTDIR}/papers.jsonl').readlines())}
  papers_jsonl_zero_chunk_ghosts: 15  # 历史遗留, 自 v2.4 原样继承
  n_papers_preprint: {stats['n_papers_preprint']}
  n_papers_fulltext_absent: {stats['n_papers_fulltext_absent']}
  parquet_MB: {stats['parquet_MB']}
redlines:
  v2.4_zero_change_verified: 见 {PLAN2}/ledgers/SHA_POST_verify_20260928.txt (收尾复核)
  v2.3_v2.2_v2.1_v2.0_v1x_untouched: true (全程只读)
  evalset_untouched: true
  mcp_default_db_unchanged: true (EYEKB_DB_POINTER default=v2.0 未动; v2.4.1 仅注册)
"""
    open(f"{OUTDIR}/manifest.yaml", "w", encoding="utf-8").write(manifest)
    print("DONE", json.dumps({k: stats[k] for k in ("n_chunks", "n_papers",
          "n_papers_preprint", "n_papers_fulltext_absent", "parquet_MB")}), flush=True)

if __name__ == "__main__":
    main()
