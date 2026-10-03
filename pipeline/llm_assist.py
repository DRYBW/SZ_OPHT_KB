#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — optional LLM-assisted summarization (**off by default**, example implementation).

Discipline redlines:
- The main path (without --llm-assist) is zero LLM; this file is only invoked when explicitly enabled.
- The channel is entirely user-supplied: only environment variables are read (API key / base url / model name);
  the repository ships no real key, real URL, or account.
- LLM input = evidence already collected in Stage B; output = a reference narrative draft for the
  reviewer. It does **not change** any cluster's confidence grade and never produces a definite
  label; when unavailable it silently degrades and notes this in the report.
- If your data may not leave your country/institution, do not enable this switch.

Environment variables (example script; fill in for your own channel):
  OPENAI_API_KEY   your key (this file neither contains nor prints it)
  OPENAI_BASE_URL  OpenAI-compatible API root (defaults to https://api.openai.com/v1)
  OPENAI_MODEL     model name (defaults to gpt-4o-mini, placeholder example only)
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
    "You are a single-cell annotation review assistant. Below is the mechanical retrieval evidence "
    "from the five EyeKB knowledge-base tools for one cell cluster (marker-dictionary candidates, "
    "tissue-composition baseline comparison flags, literature PMIDs). Write the researcher a "
    "reference narrative draft in 3-4 English sentences: what the evidence points to, where doubt "
    "remains, and which item a human should review first. "
    "Never give a definite cell-type name as a conclusion; when evidence is insufficient you must "
    "explicitly recommend abstention/review. "
    "Output JSON: {\"note\": \"...\"}\nEvidence: "
)


def assist(per_cluster, out_dir):
    """Generate a reference narrative per cluster; any failure degrades to 'not enabled' without touching the main report."""
    key = os.environ.get("OPENAI_API_KEY", "")
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    meta = {"enabled": bool(key), "model": model if key else None,
            "base_url_set": bool(os.environ.get("OPENAI_BASE_URL")),
            "n_clusters_annotated": 0, "errors": []}
    if not key:
        meta["note"] = ("--llm-assist was requested but no API key environment variable "
                        "(OPENAI_API_KEY) is set; continuing on the default zero-LLM path")
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
                     "Authorization": f"Bearer {key}"},  # key stays in memory only: never written to disk or printed
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read().decode())
            note = body["choices"][0]["message"]["content"]
            c["llm_assist_note"] = ("[LLM draft · not a conclusion · human review required] "
                                    + str(json.loads(note).get("note", note))[:600])
            meta["n_clusters_annotated"] += 1
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
                ValueError, TimeoutError) as e:
            meta["errors"].append({"cluster": c["cluster"], "err": type(e).__name__})
            c["llm_assist_note"] = "[LLM assist unavailable; judge from mechanical evidence alone]"
        time.sleep(0.2)
    return meta
