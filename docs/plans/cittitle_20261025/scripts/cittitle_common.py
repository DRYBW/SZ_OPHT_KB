#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cittitle_common.py — shared rules for the CITTITLE card (t_d8e7f2d4).

Stdlib only. Nothing here writes: the backfill, the counterfactual measurement and the independent
verifier all import these definitions so there is exactly one statement of (a) how a corpus is read as
`paper_id -> {title, doi, pmcid}`, (b) how a title is normalised for matching, and (c) how the three
added citation keys are placed inside a citation record while keeping the original key order.

Why a second copy of the corpus reader exists at all: `build_link_registry.corpus_meta_index()` lives
in a module that imports the service kernel (`mcp_server/eyekb_core`), while the delivered measurement
artifacts must be recomputable from bare stdlib (G11 precedent: gates are stdlib-only). The two
implementations are the same rule written twice, and `tests/gate_cittitle_meta.py` G12-C05 asserts the
two agree key-for-key on the live corpus — so a drift between them is a FAIL, not a silent split.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path

# The three keys added to every citation record. `title_full` is the paper's complete title; it is
# named separately from `title` so the frozen registry's own bytes for `title` can be preserved
# (the anchor twin) while a consumer still has an unambiguous full-length field to read.
ADDED_KEYS = ("title_full", "doi", "pmcid")
TITLE_FIELD = "title"
LEGACY_TRUNCATION = 120   # the pre-fix cap in build_link_registry.py: `[:120]`

CORPUS_META_FIELDS = ("title", "doi", "pmcid", "is_preprint", "journal", "year")

REG = "LINK_REGISTRY_v1.jsonl"

# ------------------------------------------------------------------ corpus reader


def load_corpus_meta(papers_jsonl) -> dict:
    """paper_id -> {title, doi, pmcid, is_preprint} read from one corpus `papers.jsonl`."""
    out = {}
    p = Path(papers_jsonl)
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            d = json.loads(line)
            pid = str(d.get("paper_id") or d.get("pmid") or "")
            if not pid:
                continue
            out[pid] = {k: ("" if d.get(k) is None else d.get(k)) for k in CORPUS_META_FIELDS}
    return out


# ------------------------------------------------------------------ title normalisation


def norm_title(s: str) -> str:
    """NFKC, lower-case, non-alphanumerics folded to single spaces (the LINKKEY convention)."""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


#: A corpus title can carry a presentation artefact that is not a disagreement: an HTML tag
#: (`<i>PRRX1</i>`, `<sup>+</sup>`), an HTML entity (`&lt;i&gt;PRRX1&lt;/i&gt;` — 41 corpus titles do),
#: a Unicode dash that NFKC does not fold to ASCII (U+2010 `‐`, U+2013 `–`), or a doubled space.
#: The retrieval route carried the pure-text form of these while `papers.jsonl` carries the marked-up
#: form, so an N1-only comparison files them as "the libraries disagree". Normalisation N2 removes the
#: artefact: strip tags, unescape entities, then fold dashes and whitespace.
_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2043"
_TAG_RE = re.compile(r"<[^>]+>")


def strip_display_marks(s: str) -> str:
    s = html.unescape(s or "")
    s = _TAG_RE.sub(" ", s)
    s = html.unescape(s)                      # a doubly-escaped entity (`&amp;lt;i&amp;gt;`) comes out
    for d in _DASHES:
        s = s.replace(d, "-")
    return re.sub(r"\s+", " ", s).strip()


def norm_title_display(s: str) -> str:
    """`norm_title` after `strip_display_marks` — the N2 normalisation."""
    return norm_title(strip_display_marks(s))


# Backwards-compatible alias: the N2 arm was first written for HTML entities only.
norm_title_unescaped = norm_title_display


def title_state(t: str) -> str:
    """The pre-fix defect state of one citation title field, as measured on the frozen registry."""
    t = t or ""
    if not t.strip():
        return "EMPTY_CITED"
    if len(t) == LEGACY_TRUNCATION:
        return "TRUNCATED_120"
    return "OK"


def tables_equal(a: str, b: str, unescape: bool = False) -> bool:
    f = norm_title_unescaped if unescape else norm_title
    return bool(f(a)) and f(a) == f(b)


def tables_prefix_equal(a: str, b: str, n: int = 40, unescape: bool = False) -> bool:
    f = norm_title_unescaped if unescape else norm_title
    na, nb = f(a), f(b)
    return bool(na) and na[:n] == nb[:n]


# ------------------------------------------------------------------ citation augmentation


def augment_citation(cit: dict, meta: dict, title_mode: str = "anchor") -> dict:
    """Return the citation with `title_full` / `doi` / `pmcid` inserted immediately after `title`.

    Inserting at that position (rather than appending) is what makes the transform invertible in the
    unit of bytes: removing the three keys restores the original key order exactly. `title_mode`:
      anchor — `title` is left byte-identical to the frozen record (audit anchor);
      repair — `title` is replaced by the complete title (drop-in for consumers that read `title`).
    """
    pmid = str(cit.get("pmid") or "")
    m = meta.get(pmid) or {}
    full = m.get("title") or ""
    out = {}
    placed = False
    for k, v in cit.items():
        if k == TITLE_FIELD:
            out[TITLE_FIELD] = full if title_mode == "repair" else v
            out["title_full"] = full
            out["doi"] = m.get("doi", "")
            out["pmcid"] = m.get("pmcid", "")
            placed = True
        else:
            out[k] = v
    if not placed:               # defensive: a citation without `title` must not be silently left bare
        raise KeyError(f"citation record has no `{TITLE_FIELD}` key: pmid={pmid}")
    return out


def augment_row(row: dict, meta: dict, title_mode: str = "anchor") -> dict:
    """Apply `augment_citation` to every citation of one registry row, preserving row key order."""
    out = {}
    for k, v in row.items():
        if k == "citations" and isinstance(v, list):
            out[k] = [augment_citation(c, meta, title_mode) for c in v]
        else:
            out[k] = v
    return out


def strip_added(cit: dict) -> dict:
    """Inverse of `augment_citation` for the anchor twin: drop the three added keys."""
    return {k: v for k, v in cit.items() if k not in ADDED_KEYS}


def derive_dropin(cit: dict) -> dict:
    """The repair-mode citation, derived from the anchor twin as `title := title_full`.

    Deriving it (rather than writing it independently) is what makes the drop-in's provenance a
    byte-level fact: `dumps(derive_dropin(c))` must equal the drop-in line exactly, and the anchor
    twin remains the artefact that inverts to the frozen registry byte-for-byte. The drop-in itself
    is deliberately NOT invertible on its own — `title` was overwritten, so the pre-fix value is not
    in it — and claiming otherwise would be a false anchor.
    """
    if "title_full" not in cit:
        raise KeyError("derive_dropin needs the anchor twin's `title_full`")
    return {**cit, TITLE_FIELD: cit["title_full"]}


def dumps(obj) -> str:
    """The exact serialisation the shipped builder uses (`json.dumps(r, ensure_ascii=False)`)."""
    return json.dumps(obj, ensure_ascii=False)