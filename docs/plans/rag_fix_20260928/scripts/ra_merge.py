#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 (RAGFIX D19) stage ra_merge: v2.4 = v2.3 全量继承 (embedding 原样复制, 零重算)
+ RAGGAP-A 增量 64 篇 (闭集; ⛔41349939 排除走勘误件)
Part A:  v2.3 parquet 220,654 chunks 原样 (文本/向量/全部列零改动)
Part RA: work/chunks_ra_raw.jsonl — embedding 新算 (CPU bge-large-en-v1.5 fp32, normalize=True,
         与 d0/kc 增量同模型同精度, 与 v2.3 manifest embedding_provenance 口径一致)
输出: literature_db/v2.4_2026-09/{chunks.parquet, papers.jsonl, build_stats.json, manifest.yaml}
红线: v2.3/v2.2/v2.1/v2.0/v1.x 全程只读 (基线 ledgers/SHA_PRE_inputs_20260928.txt,
      收尾复核=零改动证明); 不触 plans/evalset/
运行: systemd-run --user -p MemoryMax=20G /home/ubuntu/.conda/envs/pipeline_env/bin/python ra_merge.py
"""
import json, os, sys, time, hashlib
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
V23_DIR = f"{BASE}/literature_db/v2.3_2026-09"
V23_PARQUET = f"{V23_DIR}/chunks.parquet"
V23_PAPERS = f"{V23_DIR}/papers.jsonl"
PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
CHUNKS_RA = f"{PLAN}/work/chunks_ra_raw.jsonl"
OUTDIR = f"{BASE}/literature_db/v2.4_2026-09"
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
    print("[A] 读 v2.3 parquet (继承 embedding)...", flush=True)
    dfA = pd.read_parquet(V23_PARQUET)
    nA = len(dfA)
    cols = list(dfA.columns)
    assert cols[:6] == EXPECTED_COLS_PREFIX, f"schema drift: {cols[:6]}"
    assert "is_preprint" in cols and "embedding" in cols and "full_text_available" in cols, f"missing cols: {cols}"
    print(f"    A: {nA} chunks, papers={dfA.paper_id.nunique()}, cols={len(cols)}", flush=True)

    # ---- Part RA ----
    rowsRA = [json.loads(l) for l in open(CHUNKS_RA, encoding="utf-8")]
    nRA = len(rowsRA)
    print(f"[RA] 新 chunks: {nRA}", flush=True)
    texts = [r["text"] for r in rowsRA]

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_DIR, device="cpu")
    print("    模型就绪 bge-large-en-v1.5 (cpu, fp32, normalize=True)", flush=True)
    embRA = model.encode(texts, batch_size=64, normalize_embeddings=True,
                         show_progress_bar=False).astype(np.float32).reshape(nRA, 1024)

    dfRA = pd.DataFrame([{c: r.get(c) for c in cols if c != "embedding"} for r in rowsRA])
    dfRA["embedding"] = [embRA[i] for i in range(nRA)]
    del embRA
    ftmap = json.load(open(f"{PLAN}/work/ra_ftstatus.json"))
    dfRA["full_text_available"] = [int(ftmap.get(str(r["paper_id"]), 1)) for r in rowsRA]
    dfRA = dfRA.reindex(columns=list(dfA.columns))

    df = pd.concat([dfA, dfRA], ignore_index=True)
    out = f"{OUTDIR}/chunks.parquet"
    df.to_parquet(out, index=False)
    print(f"[5] SAVED {out}: {len(df)} rows, {os.path.getsize(out)/1e6:.1f} MB ({time.time()-t_all:.0f}s)", flush=True)

    # ---- papers.jsonl: v2.3 原样 (n_chunks 重算) + 64 新论文 ----
    sel = {}
    for line in open(f"{PLAN}/work/ra_selected.jsonl", encoding="utf-8"):
        r = json.loads(line)
        sel[str(r["pmid"])] = r
    nch = df.groupby("paper_id").size().to_dict()
    n_fta = df.groupby("paper_id")["full_text_available"].max().to_dict()
    with open(f"{OUTDIR}/papers.jsonl", "w", encoding="utf-8") as f:
        for line in open(V23_PAPERS, encoding="utf-8"):
            p = json.loads(line)
            p["n_chunks"] = int(nch.get(str(p["paper_id"]), p.get("n_chunks", 0)))
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
        seen = set()
        for r in rowsRA:
            pid = str(r["paper_id"])
            if pid in seen:
                continue
            seen.add(pid)
            s = sel.get(pid, {})
            f.write(json.dumps({
                "paper_id": pid, "pmcid": r.get("pmcid", ""), "title": r.get("title", ""),
                "journal": r.get("journal", ""), "year": r.get("year", ""), "doi": r.get("doi", ""),
                "species": r.get("species", "unknown"),
                "tissues": sorted(set(r.get("tissue_labels_paper") or [])),
                "source_version": "v2.4-ra", "admission_lane": "raggap_tier_a_eyekb",
                "fulltext_status": "full_text" if int(ftmap.get(pid, 1)) else "abstract_only",
                "is_preprint": int(r.get("is_preprint", 0)),
                "full_text_available": int(n_fta.get(pid, 1)),
                "n_chunks": int(nch.get(pid, 0)),
            }, ensure_ascii=False) + "\n")

    # ---- stats ----
    import collections
    per_ra = collections.Counter(r["paper_id"] for r in rowsRA)
    stats = {"n_chunks": int(len(df)), "n_chunks_A_inherited_v23": int(nA),
             "n_chunks_RA_new": int(nRA),
             "n_papers": int(df.paper_id.nunique()),
             "n_papers_preprint": int(df[df.is_preprint == 1].paper_id.nunique()),
             "n_papers_fulltext_absent": int(df[df.full_text_available == 0].paper_id.nunique()),
             "ra_per_paper": dict(per_ra),
             "species": df.species.value_counts().to_dict(),
             "parquet_MB": round(os.path.getsize(out) / 1e6, 1)}
    json.dump(stats, open(f"{OUTDIR}/build_stats.json", "w"), indent=1, ensure_ascii=False)

    # ---- manifest.yaml (手写, 与 v2.3 先例同结构) ----
    closed = [l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip()]
    led = {}
    for i, line in enumerate(open(f"{PLAN}/work/ra_availability.tsv")):
        if i == 0:
            continue
        parts = line.rstrip("\n").split("\t")
        led[parts[0]] = parts
    xml_bytes = {p: int(v[5]) for p, v in led.items()}
    manifest = f"""version: v2.4_2026-09
created: '2026-09-28'
description: >
  v2.4 全量继承 v2.3，并新增 RAGGAP A 档必补清单 64 篇 (EyeKB-RAG 执行卡 t_d0bea5a6 D19,
  上游=RAGGAP 盘点卡 t_922cdfa0 TIER_A_approval_list.md 必补表 ☐ 行闭集; PI 放行
  =USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加二 D19 "该补文献的补文献该补rag的补")。
  备选 104 篇本轮不下 (清单留账)。⛔ PMID 41349939 (retina_v6 microglia_repair LILRB2 链误引,
  EPMC 逐字复核=泌尿科论文) 不入库, 走旁挂勘误件撤证
  (kb/markers/_raggap_errata_v1.json)。EPMC OA 全文优先 (fullTextXML), 全文不可得篇
  abstract-only 入库 (fulltext_status=abstract_only, chunk 级 full_text_available=0)——
  仅提供摘要中可核验的证据, 不代表已取得或核验正文; 禁绕付费墙。
  PMID 42777860 为 EPMC MEDLINE 未收录新上线文献 (Ocul Surf 2026-09-23, NCBI eutils 实证存在),
  走 PubMed 摘要补录通道 (source=PUBMED_ONLY)。
inheritance:
  v2.3: >-
    literature_db/v2.3_2026-09/chunks.parquet {nA} chunks 原样继承
    (文本/向量/全部列零改动; v2.3 已含 full_text_available 列, 本版无 schema 变更)
  v2.3_frozen_sha256: {{"v2.3 chunks.parquet": "{sha(V23_PARQUET)}", "v2.3 papers.jsonl": "{sha(V23_PAPERS)}", "v2.3 manifest.yaml": "{sha(V23_DIR + "/manifest.yaml")}", "v2.2 chunks.parquet": "e8d71734301da265e4814c2d788216c9b305dc390872d5565375283187c39eac", "v2.1 chunks.parquet": "a371a860b10a4a6d94e5596e76cd45fc6f95fbb25aacb927d25f500d26937004", "v2.0 chunks.parquet": "f8bb3ef25fef31a633c78a4121746dddaec57ed31cb94dd77654be91c92047f5"}}
  baseline_recorded_at: {PLAN}/ledgers/SHA_PRE_inputs_20260928.txt (开卡前快照; 收尾复核一致=零改动证明)
chunker_provenance:
  code: stage2a_parse_xml_v2 (XML 解析纯函数) + stage2b_chunk_v2 (切块/组织/细胞类型词表, 零改动复用)
  note: 口径与现役 v2.1-2.3 完全一致; 卡内 scripts/ra_parse_chunk.py 逐行同构 stage_kc_parse_chunk.py
increment_lane:
  name: raggap_tier_a_eyekb (t_d0bea5a6, parent=RAGGAP t_922cdfa0 报批清单,
    PI 勾选=必补表全 ☐ 闭集 64 篇, 备选/免补/⛔ 一律不下; 非检索式准入)
  n_papers: {len(per_ra)}
  closed_set: {PLAN}/out/closed_set_pmids.txt
  download_ledger: {PLAN}/work/ra_availability.tsv (逐 PMID 成败+体积)
  download_total_xml_MB: {sum(xml_bytes.values())/1e6:.1f}
  abstract_only_pmids: {sorted([p for p, v in ftmap.items() if int(v) == 0])}
  pubmed_only_pmids: ["42777860"]
  errata_excluded_pmids: ["41349939"]
embedding_provenance:
  model: bge-large-en-v1.5 ({MODEL_DIR}, fp32, normalize=True)
  device: cpu (本机纪律 GPU 留科研; 与 v2.2/v2.3 增量的 CPU fp32 路径同模型同精度)
counts:
  n_chunks: {stats['n_chunks']}
  n_papers: {stats['n_papers']}  # = parquet unique paper_id (与 v2.1/v2.2/v2.3 报数口径一致)
  papers_jsonl_lines: {len(open(f'{OUTDIR}/papers.jsonl').readlines())}
  papers_jsonl_zero_chunk_ghosts: 15  # 历史遗留, 自 v2.3 原样继承, 非本卡引入; 本卡 {len(per_ra)} 篇零chunk数={sum(1 for p in closed if per_ra.get(p,0)==0)}
  n_papers_preprint: {stats['n_papers_preprint']}
  n_papers_fulltext_absent: {stats['n_papers_fulltext_absent']}
  parquet_MB: {stats['parquet_MB']}
redlines:
  v2.3_zero_change_verified: 见 ledgers/SHA_POST_*.txt (收尾复核)
  v2.2_v2.1_v2.0_v1x_untouched: true (本卡全程只读)
  evalset_untouched: true (plans/evalset/ 禁触红线, 全程未写入)
  mcp_default_db_unchanged: true (EYEKB_DB_POINTER v2.0 default 未切; v2.4=latest-raggap 注册, OFF 态)
"""
    open(f"{OUTDIR}/manifest.yaml", "w", encoding="utf-8").write(manifest)
    print("DONE", json.dumps({k: stats[k] for k in ("n_chunks", "n_papers", "n_papers_preprint",
                                                    "n_papers_fulltext_absent", "parquet_MB")}), flush=True)


if __name__ == "__main__":
    main()
