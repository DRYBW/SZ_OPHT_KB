#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — 可选 LLM 辅助摘要（**默认关闭**，示例实现）。

纪律红线：
- 主路径（不带 --llm-assist）零 LLM；本文件只有显式开启才会被调用。
- 通道完全由用户自备：只读取环境变量（API key / base url / model 名），
  仓内不写任何真实 key、真实 URL 或账号。
- LLM 输入 = 阶段 B 已采集的证据；输出 = 给判读者的参考叙述草稿，
  **不改变**任何簇的置信度分级，不产出确定标签；不可用时静默降级并在报告中注明。
- 若你的数据不能出境/出院，请不要开启本开关。

环境变量（示例脚本，按你自备通道填）:
  OPENAI_API_KEY   你的 key（本文件不包含也不打印）
  OPENAI_BASE_URL  兼容 OpenAI 协议的接口根地址（缺省 https://api.openai.com/v1）
  OPENAI_MODEL     模型名（缺省 gpt-4o-mini，仅占位示例）
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def _evidence_brief(c):
    qm = c["kb_marker"] or {}
    cr = qm.get("celltype_ranking") or []
    pmids = []
    for resp in (c["literature"].get("per_celltype") or {}).values():
        for h in (resp.get("results") or [])[:2]:
            if h.get("pmid"):
                pmids.append(str(h["pmid"]))
    return {
        "cluster": c["cluster"], "n_cells": c["n_cells"],
        "fraction_pct": c["fraction_pct"], "top_genes": c["top_genes"][:10],
        "marker_candidates": [x.get("cell_type") for x in cr[:3]],
        "composition_flag": c["tissue_composition"]["observed_vs_baseline"].get("flag"),
        "qc_grade": c["confidence"], "pmids": sorted(set(pmids))[:6],
    }


PROMPT = (
    "你是单细胞注释判读助手。下面是 EyeKB 知识库五工具对一个细胞簇的机械检索证据"
    "（marker 词典候选、组织组成基线对照旗标、文献 PMID）。请用 3-4 句中文给研究者写一份"
    "参考性叙述草稿：证据指向什么、哪里存疑、建议人工优先复核哪条。"
    "禁止给出确定细胞类型命名作为结论；证据不足时必须明说建议弃权/复核。"
    "输出 JSON: {\"note\": \"...\"}\n证据: "
)


def assist(per_cluster, out_dir):
    """逐簇生成参考叙述；任何一步失败都降级为'未启用'，不影响主报告。"""
    key = os.environ.get("OPENAI_API_KEY", "")
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    meta = {"enabled": bool(key), "model": model if key else None,
            "base_url_set": bool(os.environ.get("OPENAI_BASE_URL")),
            "n_clusters_annotated": 0, "errors": []}
    if not key:
        meta["note"] = ("--llm-assist 已开但环境未设 API key 变量（OPENAI_API_KEY），"
                        "按默认零 LLM 路径继续")
        return meta
    for c in per_cluster:
        payload = {"model": model, "temperature": 0,
                   "messages": [{"role": "user",
                                 "content": PROMPT + json.dumps(_evidence_brief(c),
                                                                ensure_ascii=False)}]}
        req = urllib.request.Request(
            base + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"},  # key 只在内存，不落盘不打印
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read().decode())
            note = body["choices"][0]["message"]["content"]
            c["llm_assist_note"] = ("[LLM 草稿·非结论·须人工复核] "
                                    + str(json.loads(note).get("note", note))[:600])
            meta["n_clusters_annotated"] += 1
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
                ValueError, TimeoutError) as e:
            meta["errors"].append({"cluster": c["cluster"], "err": type(e).__name__})
            c["llm_assist_note"] = "[LLM 辅助不可用，仅凭机械证据判读]"
        time.sleep(0.2)
    return meta
