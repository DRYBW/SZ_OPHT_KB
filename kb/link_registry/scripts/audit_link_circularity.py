#!/usr/bin/env python3
"""Dry run: how many registry entries keep a page if the registry's own output is not counted.

The registry's rendered appendix lists every label, so it matches almost every entry. Using it as
the page evidence for an entry is circular — the page is generated from the registry itself. This
script measures what the linkage looks like when pages under kb/link_registry/ are excluded, so the
two readings can be reported side by side instead of quietly counting the circular one.

No files are written. Usage: python3 audit_link_circularity.py [registry.jsonl]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KB = HERE.parent.parent
REG = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "LINK_REGISTRY_v1.jsonl"
OWN_OUTPUT = "link_registry/"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def page_texts(exclude_own):
    out = {}
    for p in sorted(KB.glob("**/*.md")):
        rel = str(p.relative_to(KB))
        if exclude_own and rel.startswith(OWN_OUTPUT):
            continue
        out[rel] = p.read_text(encoding="utf-8", errors="ignore").lower()
    return out


def spans_of(pages):
    """Joins of two and three consecutive word tokens, separators removed (spelling variants)."""
    out = {}
    for rel, txt in pages.items():
        toks = re.split(r"[^a-z0-9]+", txt)
        s = set()
        for i in range(len(toks) - 1):
            if toks[i] and toks[i + 1]:
                s.add(toks[i] + toks[i + 1])
                if i + 2 < len(toks) and toks[i + 2]:
                    s.add(toks[i] + toks[i + 1] + toks[i + 2])
        out[rel] = s
    return out


def matches(cls, pages, spans):
    """Same three-tier rule as build_link_registry.py: exact spelling, variant, then loose word."""
    phrase = cls.replace("_", " ").lower()
    rx = re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])")
    loose = [re.compile(r"(?<![a-z0-9])" + re.escape(w.lower()) + r"(?![a-z0-9])")
             for w in re.split(r"[_\s]+", cls) if len(w) >= 5]
    ln = norm(cls)
    hits = []
    for rel, txt in pages.items():
        if rx.search(txt) or (len(ln) > 3 and ln in spans[rel]) \
                or any(lx.search(txt) for lx in loose):
            hits.append(rel)
    return hits


def main():
    rows = [json.loads(l) for l in REG.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if "error" not in r and r.get("source_kind") == "marker_library"]

    pages_any = page_texts(exclude_own=False)
    pages_indep = page_texts(exclude_own=True)
    spans_any = spans_of(pages_any)
    spans_indep = spans_of(pages_indep)

    reach, indep, own_only = [], [], []
    for r in rows:
        m_any = matches(r["cell_type"], pages_any, spans_any)
        m_indep = matches(r["cell_type"], pages_indep, spans_indep)
        if m_any:
            reach.append(r["entry_id"])
        if m_indep:
            indep.append(r["entry_id"])
        elif m_any:
            own_only.append(r["entry_id"])

    print(f"entries: {len(rows)}")
    print(f"A. reachable at all            : {len(reach)}/{len(rows)}")
    print(f"B. reachable excluding the registry's own rendered appendix: {len(indep)}/{len(rows)}")
    print(f"   of which rely only on that appendix: {len(own_only)}")
    for e in own_only:
        print("   appendix-only page:", e)


if __name__ == "__main__":
    main()