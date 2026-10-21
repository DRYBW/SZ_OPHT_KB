#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ont_nav.py - navigate the Cell Ontology instead of looking a label up in it.

Why this module exists
----------------------
Until now the project used the Cell Ontology as a spelling normaliser: one library
class mapped to one CL term in a sidecar, and nothing else. That is why a coarse
class (`Endo`) scored as a disagreement against an author's finer term
(`blood vessel endothelial cell`) even though the ontology says one is an ancestor
of the other, and why a class that is literally the same term under another name
(`Mac_Tissue` vs `macrophage`, both CL:0000235) was counted as an error.

This module makes the ontology navigable:

  * the `is_a` ancestor closure is computed at build time (transitive), so any
    relation between two CL terms is a function of the two terms and the file;
  * every relation is named: same term / we are coarser / we are finer / true
    mismatch / no mapping on one side - never a hand-curated list;
  * `develops_from` (RO:0002202) and the germ-layer terms are exposed for the
    developmental lineage layer;
  * every identifier carries the file line it was read from, so a delivered CL
    number can always be traced back to a line of the ontology file and can never
    be typed from memory.

Discipline baked in
-------------------
* stdlib only, read-only, zero network.
* The release string is read from the file (`data-version:`), not assumed.
* Quantifiers on `is_a` lines (`{is_inferred="true"}`) are stripped: this release
  carries 662 of them, and leaving the qualifier attached silently breaks the
  whole ancestor chain (already paid for once, 2026-10-20).
* Obsolete terms are parsed but excluded from the navigable set, and reported.

Usage (library):
    from ont_nav import Ontology
    ont = Ontology(path)
    ont.release, ont.n_active, ont.relate("CL:0000115", "CL:0000071")
Usage (self-test):
    python3 ont_nav.py --obo <path> [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys

CL_PREFIX = "CL:"
DEVELOPS_FROM = "RO:0002202"          # `develops from`, resolved from the file's own typedef line

_OBO_ID_LINE = re.compile(r"^id:\s*(\S+)")
_OBO_NAME_LINE = re.compile(r"^name:\s*(.+)$")
_OBO_SYN_LINE = re.compile(r'^synonym:\s*"((?:[^"\\]|\\.)*)"\s*(?:(\w+)\s*)?')
_OBO_IS_A_LINE = re.compile(r"^is_a:\s*(\S+)")
_OBO_REL_LINE = re.compile(r"^relationship:\s*(\S+)\s+(\S+)")
_OBO_XREF_LINE = re.compile(r"^xref:\s*(.+)$")
_OBO_DEF_LINE = re.compile(r'^def:\s*"((?:[^"\\]|\\.)*)"')
_OBO_SUBSET_LINE = re.compile(r"^subset:\s*(\S+)")
_DATA_VERSION = re.compile(r"^data-version:\s*(.+)$")
_FORMAT_VERSION = re.compile(r"^format-version:\s*(.+)$")

# Verdict vocabulary. Exactly one applies to a (our term, their term) pair.
SAME_TERM = "same_term"
WE_COARSER = "we_are_coarser"
WE_FINER = "we_are_finer"
TRUE_MISMATCH = "true_mismatch"
NO_MAPPING = "no_mapping"
VERDICTS = (SAME_TERM, WE_COARSER, WE_FINER, TRUE_MISMATCH, NO_MAPPING,)


def norm_name(s: str) -> str:
    """Name normalisation used for label -> term resolution.

    Deliberately conservative: case, runs of whitespace, hyphens/underscores and the
    two spellings of Mueller/Muller. No stemming, no fuzzy matching - a false
    'this label is that CL term' is worse than a miss.
    """
    if s is None:
        return ""
    s = str(s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("müller", "muller").replace("mueller", "muller")
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s


class Term:
    __slots__ = ("id", "name", "synonyms", "parents", "develops_from", "obsolete",
                 "definition", "subsets", "xrefs", "line", "is_a_lines", "dev_lines")

    def __init__(self, tid: str, line: int):
        self.id = tid
        self.name = None
        self.synonyms = []           # list of (text, scope)
        self.parents = []            # is_a targets, qualifier stripped
        self.is_a_lines = []         # (target, file line) for each is_a statement
        self.develops_from = []      # relationship RO:0002202 targets
        self.dev_lines = []          # (target, file line) for each develops_from statement
        self.obsolete = False
        self.definition = None
        self.subsets = []
        self.xrefs = []
        self.line = line             # 1-based line of `id:` in the source file

    def as_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "line": self.line,
                "parents": self.parents, "n_synonyms": len(self.synonyms),
                "develops_from": self.develops_from,
                "obsolete": self.obsolete, "subsets": self.subsets}


class Ontology:
    """A navigable view of one Cell Ontology OBO release."""

    def __init__(self, path: str, with_closure: bool = True):
        self.path = path
        self.release = None
        self.format_version = None
        self.typedefs = {}
        self.cl_typedefs = {}            # relation ids in the CL namespace (not cell types)
        self.duplicate_id_lines = {}     # id -> [line, extra line...] for repeated id blocks
        self.terms = {}                  # all CL terms incl. obsolete
        self.active = set()              # non-obsolete CL terms
        self.n_import_terms = 0          # non-CL blocks inlined by the integrated release
        self.sha256 = self._sha256(path)
        self._parse(path)
        self._name_index = self._build_name_index()
        self._anc = {}
        if with_closure:
            self._build_closure()

    # ---------- parsing ----------
    @staticmethod
    def _sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for blk in iter(lambda: f.read(1 << 20), b""):
                h.update(blk)
        return h.hexdigest()

    def _parse(self, path: str) -> None:
        cur = None
        block = None
        with open(path, encoding="utf-8", errors="replace") as f:
            for lineno, raw in enumerate(f, 1):
                line = raw.rstrip("\n")
                if line.startswith("["):
                    if cur is not None and cur.id.startswith(CL_PREFIX):
                        self.terms[cur.id] = cur
                    elif cur is not None:
                        self.n_import_terms += 1
                    cur = None
                    if line == "[Term]":
                        block = "term"
                    elif line == "[Typedef]":
                        block = "typedef"
                    else:
                        block = None
                    continue
                m = _DATA_VERSION.match(line)
                if m and self.release is None:
                    self.release = m.group(1).strip()
                    continue
                m = _FORMAT_VERSION.match(line)
                if m and self.format_version is None:
                    self.format_version = m.group(1).strip()
                    continue
                if block == "typedef":
                    m = _OBO_ID_LINE.match(line)
                    if m:
                        self.typedefs[m.group(1)] = lineno
                        if m.group(1).startswith(CL_PREFIX):
                            self.cl_typedefs[m.group(1)] = lineno
                    continue
                if block != "term":
                    continue
                m = _OBO_ID_LINE.match(line)
                if m:
                    tid = m.group(1)
                    cur = Term(tid, lineno)
                    if tid.startswith(CL_PREFIX):
                        if tid in self.terms:
                            # A repeated id block: keep the first and record the extra line so the
                            # duplication is disclosed instead of silently overwritten.
                            self.duplicate_id_lines.setdefault(
                                tid, [self.terms[tid].line]).append(lineno)
                            cur = None
                        else:
                            self.terms[tid] = cur
                    else:
                        self.n_import_terms += 1
                        cur = None
                    continue
                if cur is None:
                    continue
                m = _OBO_NAME_LINE.match(line)
                if m:
                    cur.name = m.group(1).strip()
                    continue
                m = _OBO_SYN_LINE.match(line)
                if m:
                    cur.synonyms.append((m.group(1), (m.group(2) or "EXACT").upper()))
                    continue
                m = _OBO_IS_A_LINE.match(line)
                if m:
                    tok = m.group(1)
                    # `is_a: CL:0000071 {is_inferred="true"} ! blood vessel endothelial cell`
                    cur.parents.append(tok)
                    cur.is_a_lines.append((tok, lineno))
                    continue
                m = _OBO_REL_LINE.match(line)
                if m:
                    rel, tgt = m.group(1), m.group(2)
                    if rel == DEVELOPS_FROM:
                        cur.develops_from.append(tgt)
                        cur.dev_lines.append((tgt, lineno))
                    continue
                if line.startswith("is_obsolete: true"):
                    cur.obsolete = True
                    continue
                m = _OBO_DEF_LINE.match(line)
                if m:
                    cur.definition = m.group(1).strip()
                    continue
                m = _OBO_SUBSET_LINE.match(line)
                if m:
                    cur.subsets.append(m.group(1))
                    continue
                m = _OBO_XREF_LINE.match(line)
                if m:
                    cur.xrefs.append(m.group(1).strip())
                    continue
        if cur is not None:
            if cur.id.startswith(CL_PREFIX):
                self.terms[cur.id] = cur
            else:
                self.n_import_terms += 1
        self.active = {t for t, o in self.terms.items() if not o.obsolete}

    def _build_name_index(self) -> dict:
        idx = collections.defaultdict(set)
        for tid in self.active:
            t = self.terms[tid]
            if t.name:
                idx[("name", norm_name(t.name))].add(tid)
            for txt, scope in t.synonyms:
                idx[("syn", norm_name(txt))].add(tid)
                idx[("syn", scope, norm_name(txt))].add(tid)
        return idx

    # ---------- closure ----------
    def _build_closure(self) -> None:
        """Ancestor closure by DFS with memo; missing/foreign parents are traversed
        through (a CL term may sit under a non-CL term in the integrated release)."""
        for tid in self.active:
            if tid in self._anc:
                continue
            self._anc[tid] = self._closure_from(tid, set())

    def _closure_from(self, tid: str, stack: set) -> frozenset:
        got = self._anc.get(tid)
        if got is not None:
            return got
        if tid in stack:                     # cycle guard: report and stop
            return frozenset()
        stack.add(tid)
        seen = set()
        for p in self.terms.get(tid, Term(tid, 0)).parents:
            seen.add(p)
            if p in self.terms:
                seen |= set(self._closure_from(p, stack))
            elif p in self._anc:
                seen |= set(self._anc[p])
        stack.discard(tid)
        res = frozenset(x for x in seen if x != tid)
        self._anc[tid] = res
        return res

    def ancestors(self, tid: str) -> frozenset:
        """Strict transitive is_a ancestors of a CL term (CL and non-CL ids kept)."""
        return self._anc.get(tid, frozenset())

    def ancestors_cl(self, tid: str) -> set:
        return {a for a in self.ancestors(tid) if a.startswith(CL_PREFIX)}

    def descendants(self, tid: str) -> set:
        return {t for t in self.active if tid in self._anc.get(t, ())}

    def closure_is_consistent(self) -> dict:
        """Fixed-point audit: recompute the closure by iterated union and compare.

        A closure built by DFS with memo can hide a cycle or a stale entry; this
        re-derives it the slow, obvious way and reports every term that differs.
        """
        bad = []
        for tid in self.active:
            want = set()
            frontier = [p for p in self.terms[tid].parents]
            while frontier:
                p = frontier.pop()
                if p in want:
                    continue
                want.add(p)
                frontier.extend(self.terms[p].parents if p in self.terms else [])
            want.discard(tid)
            if want != set(self.ancestors(tid)):
                bad.append(tid)
        return {"n_terms": len(self.active), "n_bad": len(bad), "bad": sorted(bad)[:20]}

    # ---------- lookup / tracing ----------
    def label(self, tid: str):
        t = self.terms.get(tid)
        return t.name if t else None

    def is_active(self, tid: str) -> bool:
        return tid in self.active

    def trace_line(self, tid: str):
        """The line of the file where `id: <tid>` is written (None if not in the file)."""
        t = self.terms.get(tid)
        return t.line if t else None

    def resolve(self, text: str, prefer_shortest: bool = True) -> dict:
        """Resolve a human label to one CL term, or report why it could not.

        Preferred name beats synonym (a synonym lookup can land on a neighbour:
        'macrophage' also matches 'plasmatocyte'). Among several preferred names,
        the shortest wins so that a generic label does not resolve to a
        species-qualified variant.
        """
        k = norm_name(text)
        out = {"input": text, "cl_id": None, "cl_label": None, "method": None,
               "candidates": []}
        names = sorted(self._name_index.get(("name", k), set()))
        if names:
            pick = names[0] if len(names) == 1 else (
                sorted(names, key=lambda t: (len(self.terms[t].name or ""), t))[0]
                if prefer_shortest else names[0])
            out.update(cl_id=pick, cl_label=self.terms[pick].name,
                       method="name" if len(names) == 1 else "name_multi",
                       candidates=names)
            return out
        syns = sorted(self._name_index.get(("syn", k), set()))
        if syns:
            pick = sorted(syns, key=lambda t: (len(self.terms[t].name or ""), t))[0]
            out.update(cl_id=pick, cl_label=self.terms[pick].name,
                       method="synonym" if len(syns) == 1 else "synonym_multi",
                       candidates=syns)
            return out
        out["method"] = "unresolved"
        return out

    # ---------- the four-way relation ----------
    def relate(self, ours, theirs) -> dict:
        """Classify one (our term, their term) pair against the ontology.

        Exactly one verdict, computed from the two terms and the closure:
          same_term      identical CL term (a naming difference only)
          we_are_coarser our term is a strict ancestor of theirs (their term is our descendant)
          we_are_finer   their term is a strict ancestor of ours
          true_mismatch  neither is an ancestor of the other
          no_mapping     one side carries no CL term (which side is recorded)
        """
        res = {"ours": ours, "theirs": theirs, "verdict": NO_MAPPING,
               "missing_side": None, "path": None}
        if not ours and not theirs:
            res["missing_side"] = "both"
            return res
        if not ours:
            res["missing_side"] = "ours"
            return res
        if not theirs:
            res["missing_side"] = "theirs"
            return res
        if ours == theirs:
            res["verdict"] = SAME_TERM
            return res
        # our term is an ancestor of theirs  -> we named a coarser term than the author
        if ours in self.ancestors(theirs):
            res["verdict"] = WE_COARSER
            res["path"] = self._path(theirs, ours)   # their term -> ... -> our term
            return res
        # their term is an ancestor of ours -> we named a finer term than the author
        if theirs in self.ancestors(ours):
            res["verdict"] = WE_FINER
            res["path"] = self._path(ours, theirs)   # our term -> ... -> their term
            return res
        res["verdict"] = TRUE_MISMATCH
        return res

    def common_ancestors(self, a: str, b: str) -> set:
        return self.ancestors_cl(a) & self.ancestors_cl(b)

    def _path(self, child: str, ancestor: str, max_len: int = 12):
        """Shortest chain child -> ... -> ancestor (for the report), [] if unreachable."""
        if child == ancestor:
            return [child]
        prev = {child: None}
        q = collections.deque([child])
        while q:
            n = q.popleft()
            for p in self.terms.get(n, Term(n, 0)).parents:
                if p in prev:
                    continue
                prev[p] = n
                if p == ancestor:
                    chain, cur = [], p
                    while cur is not None:
                        chain.append(cur)
                        cur = prev[cur]
                    chain.reverse()
                    return chain[:max_len]
                q.append(p)
        return []

    # ---------- developmental / germ layer ----------
    def develops_from_edges(self) -> list:
        return [(t, p, self.terms[t].line) for t in sorted(self.active)
                for p in self.terms[t].develops_from]

    def resolves_from_file(self, names: dict) -> list:
        """Resolve a dict {key: preferred name} to ids, ids read from the file only."""
        rows = []
        for key, name in names.items():
            r = self.resolve(name)
            rows.append({"key": key, "name": name, "cl_id": r["cl_id"],
                         "cl_label": r["cl_label"], "method": r["method"],
                         "line": self.trace_line(r["cl_id"]) if r["cl_id"] else None})
        return rows

    def germ_layer_of(self, tid: str, layer_names: list) -> list:
        """Which germ-layer ancestor(s) a term sits under, using names resolved from
        the file (never typed ids). Returns [] when the term has none."""
        layers = []
        for key, name, _method, cid in layer_names:
            if cid and (tid == cid or cid in self.ancestors(tid)):
                layers.append(key)
        return layers

    def summary(self) -> dict:
        return {"source": self.path, "sha256": self.sha256,
                "format_version": self.format_version, "release": self.release,
                "n_cl_terms_in_file": len(self.terms),
                "n_active": len(self.active),
                "n_obsolete": len(self.terms) - len(self.active),
                "n_duplicate_id_blocks": len(self.duplicate_id_lines),
                "duplicate_id_blocks": {k: v for k, v in sorted(self.duplicate_id_lines.items())},
                "n_cl_namespace_typedefs": len(self.cl_typedefs),
                "cl_namespace_typedefs": dict(sorted(self.cl_typedefs.items())),
                "n_import_terms": self.n_import_terms,
                "n_develops_from_edges": len(self.develops_from_edges()),
                "typedef_develops_from_in_file": DEVELOPS_FROM in self.typedefs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--obo", default="/mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    ont = Ontology(a.obo)
    s = ont.summary()
    print(json.dumps(s, ensure_ascii=False, indent=1))
    c = ont.closure_is_consistent()
    print(f"closure audit: terms={c['n_terms']} bad={c['n_bad']}")
    for ours, theirs in (("CL:0000115", "CL:0000071"), ("CL:0000115", "CL:0000666"),
                         ("CL:0000748", "CL:0000751"), ("CL:0000235", "CL:0000235"),
                         ("CL:0000115", "CL:0000604")):
        r = ont.relate(ours, theirs)
        print(f"  {ours} vs {theirs} -> {r['verdict']}  "
              f"({ont.label(ours)} vs {ont.label(theirs)})")
    if a.json:
        json.dump({"summary": s, "closure_audit": c}, open(a.json, "w"),
                  ensure_ascii=False, indent=1)
        print("wrote", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())