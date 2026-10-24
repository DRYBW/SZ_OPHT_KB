# -*- coding: utf-8 -*-
"""ont_closure_probe.py -- the Cell-Ontology reading under a closure that keeps the qualified `is_a` edges.

Why this exists (finding, not a fix)
------------------------------------
The frozen harness (`plans/noregr_20261022/scripts/wave_common.py`, `Rulers._load_obo`) parses an
`is_a` line as `v.split("!")[0].strip()`, which leaves the trailing qualifier in place. In the pinned
release `2026-06-08` **662 `is_a` lines carry `{is_inferred="true"}`**, so those parent edges never
enter the closure: the harness's `anc()`, its `related()` and its `cl_grade()` miss most of the
coarser/finer relations, and a granularity difference is read as `truly_inconsistent`.

The predecessor waves recorded the opposite convention: the CL-depth wave's gate A3 audited a closure
with the qualifier stripped, and its four-way relation reads (`we_are_coarser`) rely on exactly those
edges. So the harness under-counts relatedness relative to the project's own ontology authority.

This module does NOT edit the frozen harness. It recomputes the same reading with the qualifier
stripped, so both arms can be compared under one corrected ruler and the size of the instrument
difference is visible. The harness reading stays the primary one (comparability with the cards that
reused it); this is reported beside it.

Zero writes, zero network.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter

REPO = "/home/ubuntu/EYEKB_REPO"
CL_MAP = os.path.join(REPO, "kb/markers/markers_cl_alignment_v2_unified.json")
CL_OBO = os.path.join(REPO, "kb/ontology/cl/releases/2026-06-08/cl-base.obo")

_CACHE = {}


def _load():
    if _CACHE:
        return _CACHE
    terms, cur = {}, None
    n_qualified = 0
    with open(CL_OBO, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                cur = {}
                continue
            if line.startswith("[") and line.endswith("]"):
                cur = None
                continue
            if cur is None or ":" not in line:
                continue
            k, v = line.split(":", 1)
            v = v.strip()
            if k == "id":
                cur["id"] = v
                terms[v] = cur
            elif k == "name":
                cur["name"] = v
            elif k == "is_obsolete":
                cur["obsolete"] = (v == "true")
            elif k == "is_a":
                raw = v.split("!")[0].strip()
                if "{" in raw:
                    n_qualified += 1
                cur.setdefault("is_a", []).append(raw.split("{")[0].strip())
    active = {k: v for k, v in terms.items() if not v.get("obsolete")}
    label_cl = {}
    for lbl, rec in json.load(open(CL_MAP, encoding="utf-8"))["labels"].items():
        if rec.get("cl_id"):
            label_cl[str(lbl).split("::")[-1].strip().casefold()] = rec["cl_id"]
    cllabel_cl = {}
    for cid, t in active.items():
        nm = (t.get("name") or "").strip().casefold()
        if nm:
            cllabel_cl.setdefault(nm, cid)
    _CACHE.update({"terms": active, "label_cl": label_cl, "cllabel_cl": cllabel_cl,
                   "n_qualified_is_a_lines": n_qualified,
                   "obo_sha256": hashlib.sha256(open(CL_OBO, "rb").read()).hexdigest()})
    return _CACHE


def _anc(cid, terms):
    seen, stack = set(), [cid]
    while stack:
        x = stack.pop()
        t = terms.get(x)
        if not t:
            continue
        for p in (t.get("is_a") or []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen


def cl_grade(pred_label, ref_label):
    d = _load()
    a = d["label_cl"].get(str(pred_label).split("::")[-1].strip().casefold()) if pred_label else None
    b = d["cllabel_cl"].get(str(ref_label).strip().casefold())
    if not pred_label:
        return "abstain"
    if not a:
        return "unmappable_pred"
    if not b:
        return "unmappable_truth"
    if a == b:
        return "same_cl"
    if a in _anc(b, d["terms"]):
        return "kb_coarser"
    if b in _anc(a, d["terms"]):
        return "kb_finer"
    return "truly_inconsistent"


def corrected_cl_counts(calls, graded, keys=None):
    keys = list(graded) if keys is None else keys
    by = {(c["vol"], c["cluster"]): c for c in calls}
    return dict(Counter(cl_grade(graded[k]["top"], by[k]["ref_cell_type"]) for k in keys))


def instrument_difference():
    d = _load()
    return {"obo_sha256": d["obo_sha256"], "qualified_is_a_lines_in_the_release": d["n_qualified_is_a_lines"],
            "note": "the frozen harness keeps the qualifier on these lines, so the parents they name "
                    "never enter its closure"}


if __name__ == "__main__":
    print(json.dumps(instrument_difference(), indent=1))