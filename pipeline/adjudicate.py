#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — optional second answer per cluster (**off by default**).

The default path calls no model: the curated marker libraries rank the cluster's genes and the
top candidate is the answer, reproducible byte for byte from disk. This module adds an OPTIONAL
second answer beside it, produced by a model that reads the literature already collected by
Stage B.

Two properties are deliberate and must not be relaxed:

1. **It never overwrites the library's answer.** The library answer stays where it was
   (`kb_marker`); this module writes `adjudication` beside it. A cluster therefore has two
   answers, and the report prints both. On this corpus the two are not separated globally
   (the paired interval for the difference crosses zero), so the system must not choose one on
   the user's behalf — the whole point of shipping both is that the choice is not ours to make.
2. **It is not a deterministic artefact.** The answer is a record of one channel at one date.
   Whatever produces it is named in the report with the number of runs and the vote rule, and
   no reading computed from it may be presented as reproducible.

Discipline:
- The main path (without `--adjudicate`) is zero LLM; this file is only invoked when enabled.
- The channel is entirely user-supplied and read from the environment only. The repository ships
  no key, no URL and no account. If the environment is incomplete, this degrades to "not
  enabled" and the report says so; nothing else changes.
- Input = evidence Stage B already collected. Output = one candidate name from the library's own
  candidate list, or an explicit abstention. The model is never given the truth labels, and it
  cannot invent a name outside the list.
- Abstention is a legal and expected output.

Environment variables (all optional, all user-supplied):
  EYEKB_ADJUDICATE=1   enable from the environment when the caller did not pass the flag
  OPENAI_API_KEY       your key (never read from disk by this file, never printed)
  OPENAI_BASE_URL      OpenAI-compatible API root (default https://api.openai.com/v1)
  OPENAI_MODEL         model name (default: whatever OPENAI_MODEL says; there is no default model
                       on purpose — a named model is a result, an unnamed one is not)
  EYEKB_ADJUDICATE_RUNS  number of independent runs per cluster (default 3)
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter

DEFAULT_BASE = "https://api.openai.com/v1"

PROMPT = (
    "You are adjudicating a single-cell annotation call. A curated marker library has already "
    "ranked candidates for this cluster from the cluster's marker genes; that ranking is given "
    "below together with the literature evidence the pipeline retrieved.\n"
    "Your task: state which single candidate the evidence best supports.\n"
    "Rules you must follow:\n"
    "  1. The answer must be EXACTLY one of the candidate names given below, copied character "
    "for character. Never invent a name that is not in the list.\n"
    "  2. If the evidence does not support any candidate well enough, answer ABSTAIN. Abstaining "
    "is a correct answer, not a failure.\n"
    "  3. Give a one-sentence reason quoting which evidence decided it.\n"
    'Output JSON only: {"answer": "...", "reason": "..."}\n'
)


def _brief(c):
    """The evidence for one cluster, as the model sees it. No truth, no labels, no author names."""
    qm = c.get("kb_marker") or {}
    rank = qm.get("celltype_ranking") or []
    cands = [x.get("cell_type") for x in rank if isinstance(x, dict) and x.get("cell_type")]
    pmids, snips = [], []
    per_ct = (c.get("literature") or {}).get("per_celltype") or {}
    # a query that could not run is stored as a plain string next to the answered ones; skip those
    for resp in (per_ct.values() if isinstance(per_ct, dict) else []):
        if not isinstance(resp, dict):
            continue
        for h in (resp.get("results") or [])[:2]:
            if not isinstance(h, dict):
                continue
            if h.get("pmid"):
                pmids.append(str(h["pmid"]))
            if h.get("snippet"):
                snips.append(str(h["snippet"])[:400])
    comp = (c.get("tissue_composition") or {}).get("observed_vs_baseline") or {}
    return {
        "cluster": c.get("cluster"),
        "n_cells": c.get("n_cells"),
        "top_genes": (c.get("top_genes") or [])[:30],
        "library_candidates": [
            {"name": x.get("cell_type"), "n_shared": x.get("n_shared"),
             "shared_genes": (x.get("shared_genes") or [])[:6]}
            for x in rank[:5] if isinstance(x, dict)
        ],
        "candidate_names": cands[:5],
        "composition_flag": comp.get("flag"),
        "literature_pmids": sorted(set(pmids))[:6],
        "literature_snippets": snips[:4],
    }


def _ask(key, base, model, brief, seed, max_tokens):
    payload = {
        "model": model,
        "temperature": 0,
        "seed": seed,
        "max_tokens": max_tokens,
        "messages": [{"role": "user",
                      "content": PROMPT + json.dumps(brief, ensure_ascii=False)}],
    }
    req = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 # the key lives in memory only: never written to disk, never printed
                 "Authorization": f"Bearer {key}"},
        method="POST")
    # Direct connection: an ambient HTTP proxy is a common cause of a channel that "works
    # elsewhere" failing here with a TLS or 4xx error, and the operator cannot see it in the
    # report. Bypassing the proxy environment makes the failure the channel's own.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=180) as r:
        body = json.loads(r.read().decode())
    txt = body["choices"][0]["message"].get("content") or ""
    # A reasoning model spends its budget on the reasoning channel first and can leave `content`
    # empty when the budget runs out; the JSON contract is then unmet and the run must be counted
    # as a failed run, not read as an abstention. Search both channels for the object before
    # giving up, and never guess an answer from free text.
    cand_txt = [txt, body["choices"][0]["message"].get("reasoning_content") or ""]
    for blob in cand_txt:
        if not blob:
            continue
        try:
            obj = json.loads(blob)
            if "answer" in obj:
                return (obj.get("answer"), obj.get("reason"))
        except ValueError:
            pass
        m = re.search(r'\{[^{}]*"answer"[^{}]*\}', blob, re.S)
        if m:
            try:
                obj = json.loads(m.group(0))
                return (obj.get("answer"), obj.get("reason"))
            except ValueError:
                continue
    return None, ("json_contract_unmet: " + (txt or "<empty content>")[:160])


def _vote(answers, allowed):
    """Majority over runs; None when every run abstained or no label reached 2 votes."""
    norm = []
    for a in answers:
        if not a:
            norm.append(None)
            continue
        a = str(a).strip()
        if a.upper() == "ABSTAIN":
            norm.append("ABSTAIN")
            continue
        norm.append(a if a in allowed else None)   # a name outside the list is not an answer
    real = [x for x in norm if x and x != "ABSTAIN"]
    if not real:
        return ("ABSTAIN" if any(x == "ABSTAIN" for x in norm) else None), Counter(norm)
    label, n = Counter(real).most_common(1)[0]
    if n * 2 <= len(norm):
        return None, Counter(norm)
    return label, Counter(norm)


def adjudicate(per_cluster, out_dir, runs=None):
    """Add a second answer beside the library answer. Never modifies the library answer."""
    key = os.environ.get("OPENAI_API_KEY", "")
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "")
    runs = int(runs or os.environ.get("EYEKB_ADJUDICATE_RUNS") or 3)
    meta = {
        "enabled": bool(key and model),
        "layer": "optional second answer; the library answer is unchanged",
        "model": model or None,
        "runs_per_cluster": runs,
        "vote": "majority; an answer outside the library's candidate list is discarded; "
                "ABSTAIN is a legal output",
        "n_clusters_answered": 0, "n_clusters_abstained": 0, "n_no_majority": 0,
        "errors": [],
        "reproducibility": "NOT reproducible: this is a record of one channel at one date; "
                           "no reading from this column may be reported as deterministic",
    }
    if not (key and model):
        meta["note"] = ("--adjudicate was requested but the channel is incomplete "
                        "(OPENAI_API_KEY and OPENAI_MODEL must both be set); continuing on the "
                        "default zero-LLM path and reporting only the library answer")
        return meta
    for c in per_cluster:
        brief = _brief(c)
        allowed = set(brief["candidate_names"])
        got, reasons, errs = [], [], []
        mt = int(os.environ.get("EYEKB_ADJUDICATE_MAX_TOKENS") or 2048)
        for k in range(runs):
            try:
                ans, reason = _ask(key, base, model, brief, seed=42 + k, max_tokens=mt)
                got.append(ans)
                if reason:
                    reasons.append(str(reason)[:200])
            except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
                    ValueError, TimeoutError) as e:
                errs.append(type(e).__name__)
            time.sleep(0.2)
        if errs:
            meta["errors"].append({"cluster": brief["cluster"], "err": sorted(set(errs))})
        label, tally = _vote(got, allowed)
        c["adjudication"] = {
            "answer": label,
            "abstained": label == "ABSTAIN",
            "runs": runs,
            "run_answers": [str(x) if x is not None else None for x in got],
            "votes": dict(tally),
            "reason": (reasons[0] if reasons else None),
            "model": model,
            "library_answer_unchanged": True,
        }
        if label in (None, "ABSTAIN"):
            meta["n_clusters_abstained"] += 1
            if label is None:
                meta["n_no_majority"] += 1
        else:
            meta["n_clusters_answered"] += 1
    return meta