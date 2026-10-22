#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cell Ontology explanation layer for the EyeKB service (read-only, registered OFF by default).

What this module is for
-----------------------
The project used the Cell Ontology as a spelling normaliser: one library class to one CL term in a
sidecar, and nothing else. This module makes the ontology *navigable* inside the shipped service, so
a caller can ask what the graph actually says about two terms instead of being handed a curated
list. It answers four questions, and it answers them read-only:

    resolve_term(text)                 which CL term is this, and how sure is that resolution?
    get_ancestors(term)                what the graph says is above it, and along which path
    compare_terms(ours, theirs)        how do two terms relate, and how far may that be used?
    explain_class_mapping(our_class)   what backs the mapping this library ships for one class?

Two records that must never be collapsed
---------------------------------------
`is_a_relation` is **what the graph says**. `assessment` is **whether that answer holds under this
sample, this task granularity and this evidence**. A parent-child relation is not by itself a correct
answer, and a correct-but-coarse answer is a resolution limitation, not a biological error. Both
records are returned on every comparison, side by side, and neither is derived from the other.

The comparison verdict uses five report buckets, computed from the graph and nothing else:

    same_term                 canonically the same CL term (a naming difference only)
    ours_broader              our term is an ancestor of theirs
    ours_narrower             their term is an ancestor of ours
    confirmed_incompatible    explicit incompatibility evidence was supplied and is recorded
    not_supported_by_is_a     the graph does not support equivalence - and does NOT prove exclusion

"No ancestor relation" is not proof of biological mutual exclusion: multiple inheritance, incomplete
ontologies and cross-classification all produce it. `not_supported_by_is_a` is therefore never
counted as correct and never reported as a confirmed error; `confirmed_incompatible` is only reached
when the caller supplies explicit incompatibility evidence, which is recorded with the verdict.

Deterministic parsing of one fixed local snapshot only
------------------------------------------------------
Everything is read from the single snapshot named by
`kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json` (logical anchor, repo-relative path, sha256,
release string). No network, no second source, no mutation of a file: the module never writes
anything, and it refuses to answer from a snapshot whose hash does not match.

The parser handles, and reports rather than repairs: `alt_id`, obsolete terms with their unique
replacements (ambiguity goes to review), ambiguous synonyms (only a unique resolution is
auto-accepted, and the choice is never made in the direction that flatters a metric), multiple
inheritance, missing imports, same-label-different-concept, duplicate id blocks, and OWL restriction
expressions - which are recorded separately and are NEVER read as named-class `is_a` edges.

Stop line
---------
This module will not modify ontology semantics, will not prefer a favourable synonym, and will not
let an extremely broad ancestor blanket an answer: a relation that only reaches a blanket ancestor
(declared threshold, see ONT_LAYER_REGISTRY_v1.json) is reported as below the minimum reporting
granularity, so it cannot be counted as a usable coarse answer.

Discipline
----------
Stdlib only. No author-machine absolute paths: every asset is a logical address resolved through
the versioned manifest, relative to the repository root discovered from this file's own location.
Nothing here is an input to any score, weighting, ranking or confidence measure.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

# ---------------------------------------------------------------- constants

CL = "CL:"
MANIFEST_REL = "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json"
REGISTRY_REL = "kb/ontology/ONT_LAYER_REGISTRY_v1.json"
ALIGNMENT_REL = "kb/markers/markers_cl_alignment_v2_unified.json"

# Report buckets (the five the ruling fixes). is_a_relation and assessment are separate records.
SAME_TERM = "same_term"
OURS_BROADER = "ours_broader"
OURS_NARROWER = "ours_narrower"
CONFIRMED_INCOMPATIBLE = "confirmed_incompatible"
NOT_SUPPORTED = "not_supported_by_is_a"
BUCKETS = (SAME_TERM, OURS_BROADER, OURS_NARROWER, CONFIRMED_INCOMPATIBLE, NOT_SUPPORTED)

# is_a_relation vocabulary: what the graph says, in graph terms.
REL_SAME = "same_canonical_term"
REL_OURS_ANCESTOR = "ours_is_ancestor_of_theirs"
REL_THEIRS_ANCESTOR = "theirs_is_ancestor_of_ours"
REL_NONE = "no_ancestor_relation"
REL_UNRESOLVED = "unresolved"

# Assessment vocabulary (never derived from the bucket).
ASSESS_NOT_ASSESSED = "not_assessed"
ASSESS_SUPPORTED = "supported"
ASSESS_RESOLUTION_LIMITED = "resolution_limited"
ASSESS_EVIDENCE_INSUFFICIENT = "evidence_insufficient"
ASSESS_UNMAPPED = "unmapped"
ASSESS_UNDER_REVIEW = "under_review"
ASSESS_INCOMPATIBLE = "incompatible"

_P_ID = re.compile(r"^id:\s*(\S+)")
_P_NAME = re.compile(r"^name:\s*(.+)$")
_P_SYN = re.compile(r'^synonym:\s*"((?:[^"\\]|\\.)*)"\s*(?:(\w+)\s*)?')
_P_IS_A = re.compile(r"^is_a:\s*(\S+)")
_P_REL = re.compile(r"^relationship:\s*(\S+)\s+(\S+)")
_P_INTER = re.compile(r"^intersection_of:\s*(\S+)(?:\s+(\S+))?")
_P_ALT = re.compile(r"^alt_id:\s*(\S+)")
_P_REPLACED = re.compile(r"^replaced_by:\s*(\S+)")
_P_CONSIDER = re.compile(r"^consider:\s*(\S+)")
_P_IMPORT = re.compile(r"^import:\s*(.+)$")
_P_DATA_VER = re.compile(r"^data-version:\s*(.+)$")
_P_FORMAT_VER = re.compile(r"^format-version:\s*(.+)$")
_P_ONTOLOGY = re.compile(r"^ontology:\s*(.+)$")
_P_OBSOLETE = "is_obsolete: true"


def norm_label(s) -> str:
    """Label normalisation for resolution. Deliberately conservative: case, whitespace runs,
    hyphens/underscores and the Mueller/Muller spelling. No stemming, no fuzzy matching - a false
    'this label is that CL term' is worse than a miss, and a near-match must never be preferred
    because it improves a metric."""
    if s is None:
        return ""
    s = str(s).lower().strip()
    s = s.replace("müller", "muller").replace("mueller", "muller")
    s = s.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- anchors


def repo_root(start: Path | None = None) -> Path:
    """The repository root, discovered by walking up from this file: the first directory that
    holds both `kb/` and `mcp_server/`. No absolute path is written down anywhere, so the same
    code resolves its assets in a clone that sits anywhere, under any directory name."""
    here = (start or Path(__file__)).resolve()
    for d in [here] + list(here.parents):
        if (d / "kb").is_dir() and (d / "mcp_server").is_dir():
            return d
    raise FileNotFoundError("repository root (a directory holding kb/ and mcp_server/) not found")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_manifest(asset_root: Path | None = None) -> dict:
    root = asset_root or repo_root()
    p = root / MANIFEST_REL
    if not p.is_file():
        return {"schema": None, "anchors": [], "_manifest_path": str(MANIFEST_REL),
                "_status": "MANIFEST_MISSING"}
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:                                    # a broken manifest is a defect
        return {"schema": None, "anchors": [], "_manifest_path": str(MANIFEST_REL),
                "_status": f"MANIFEST_UNREADABLE:{type(e).__name__}"}
    m["_manifest_path"] = str(MANIFEST_REL)
    m["_status"] = "OK"
    return m


def resolve_anchor(anchor: str, asset_root: Path | None = None) -> dict:
    """Resolve one logical address to bytes on disk and verify its content hash.

    Returned status is one of:
      RESOLVED               the file exists and its sha256 equals the recorded one
      ANCHOR_UNKNOWN         the manifest lists no such address (a defect: name it, do not guess)
      ANCHOR_MISSING         the manifest lists it and the file is absent (a defect, NOT an env
                             error: a mandatory delivered asset is missing from the delivery)
      ANCHOR_HASH_MISMATCH   the bytes are not the recorded bytes
      MANIFEST_MISSING       the manifest itself is absent or unreadable
    A path that escapes the repository root is refused rather than resolved.
    """
    root = (asset_root or repo_root()).resolve()
    man = load_manifest(asset_root)
    out = {"anchor": anchor, "status": None, "path": None, "sha256_recorded": None,
           "sha256_actual": None, "bytes": None, "release": None, "manifest": man.get("_manifest_path")}
    if man.get("_status") != "OK":
        out["status"] = "MANIFEST_MISSING"
        return out
    rec = next((a for a in man.get("anchors", []) if a.get("anchor_id") == anchor), None)
    if rec is None:
        out["status"] = "ANCHOR_UNKNOWN"
        return out
    out["sha256_recorded"] = rec.get("sha256")
    out["release"] = rec.get("release")
    rel = rec.get("path") or ""
    p = (root / rel).resolve()
    if not str(p).startswith(str(root) + "/") and p != root:
        out["status"] = "ANCHOR_UNKNOWN"
        out["path"] = rel
        return out
    out["path"] = rel
    if not p.is_file():
        out["status"] = "ANCHOR_MISSING"
        return out
    got = sha256_file(p)
    out["sha256_actual"] = got
    out["bytes"] = p.stat().st_size
    out["status"] = "RESOLVED" if got == rec.get("sha256") else "ANCHOR_HASH_MISMATCH"
    return out


def load_registry(asset_root: Path | None = None) -> dict:
    root = asset_root or repo_root()
    p = root / REGISTRY_REL
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------- the snapshot


class Term:
    __slots__ = ("id", "name", "line", "parents", "is_a_lines", "synonyms", "alt_ids",
                 "obsolete", "replaced_by", "consider", "relationships", "restrictions",
                 "duplicate_lines", "subsets")

    def __init__(self, tid: str, line: int):
        self.id = tid
        self.name = None
        self.line = line
        self.parents = []            # is_a targets, quantifier stripped
        self.is_a_lines = []         # (target, file line)
        self.synonyms = []           # (text, scope)
        self.alt_ids = []            # (alt id, file line)
        self.obsolete = False
        self.replaced_by = []        # (target, file line)
        self.consider = []
        self.relationships = []      # (relation id, target, file line)
        self.restrictions = []       # (property id, target, file line) from intersection_of
        self.duplicate_lines = []
        self.subsets = []


class OntologySnapshot:
    """One parsed, hash-verified Cell Ontology release. Read-only: nothing is written anywhere."""

    def __init__(self, asset_root: Path | None = None,
                 anchor: str = "ont://cl/releases/2026-06-08"):
        self.asset_root = (asset_root or repo_root()).resolve()
        self.anchor = resolve_anchor(anchor, self.asset_root)
        self.registry = load_registry(self.asset_root)
        self.blanket_threshold = int(
            (self.registry.get("granularity_rules") or {}).get("blanket_ancestor_descendants", 200))
        self.terms: dict[str, Term] = {}
        self.active: set[str] = set()
        self.alt_index: dict[str, str] = {}
        self.n_import_term_blocks = 0
        self.imports_declared: list[str] = []
        self.release = None
        self.format_version = None
        self.ontology_id = None
        self.file_sha256 = self.anchor.get("sha256_actual")
        self._anc: dict[str, frozenset] = {}
        self._desc: dict[str, frozenset] = {}
        self._name_index: dict = {}
        self._syn_index: dict = {}
        self.n_duplicate_id_blocks = 0
        self.cycles: list[str] = []
        if self.anchor.get("status") == "RESOLVED":
            self._parse(self.asset_root / self.anchor["path"])
            self._build_indexes()
            self._build_closure()

    # ---- parsing

    def _parse(self, path: Path) -> None:
        block = None
        cur: Term | None = None
        with open(path, encoding="utf-8", errors="replace") as f:
            for lineno, raw in enumerate(f, 1):
                line = raw.rstrip("\n")
                if line.startswith("["):
                    self._close(cur, block)
                    cur = None
                    block = {"[Term]": "term", "[Typedef]": "typedef"}.get(line)
                    continue
                m = _P_DATA_VER.match(line)
                if m and self.release is None:
                    self.release = m.group(1).strip()
                    continue
                m = _P_FORMAT_VER.match(line)
                if m and self.format_version is None:
                    self.format_version = m.group(1).strip()
                    continue
                m = _P_ONTOLOGY.match(line)
                if m and self.ontology_id is None:
                    self.ontology_id = m.group(1).strip()
                    continue
                m = _P_IMPORT.match(line)
                if m and self.release is None:            # header imports only
                    self.imports_declared.append(m.group(1).strip())
                    continue
                if block != "term":
                    continue
                m = _P_ID.match(line)
                if m:
                    self._close(cur, block)
                    tid = m.group(1)
                    if tid in self.terms:                 # duplicate id block: disclosed, not merged
                        t = self.terms[tid]
                        t.duplicate_lines.append(lineno)
                        self.n_duplicate_id_blocks += 1
                        cur = None
                    elif tid.startswith(CL):
                        cur = Term(tid, lineno)
                    else:
                        self.n_import_term_blocks += 1
                        cur = None
                    continue
                if cur is None:
                    continue
                m = _P_NAME.match(line)
                if m:
                    cur.name = m.group(1).strip()
                    continue
                m = _P_SYN.match(line)
                if m:
                    cur.synonyms.append((m.group(1), (m.group(2) or "EXACT").upper()))
                    continue
                m = _P_IS_A.match(line)
                if m:
                    # `is_a: CL:0000071 {is_inferred="true"} ! label` - strip the quantifier, or the
                    # whole ancestor chain silently breaks.
                    cur.parents.append(m.group(1))
                    cur.is_a_lines.append((m.group(1), lineno))
                    continue
                m = _P_ALT.match(line)
                if m:
                    cur.alt_ids.append((m.group(1), lineno))
                    continue
                if line.startswith(_P_OBSOLETE):
                    cur.obsolete = True
                    continue
                m = _P_REPLACED.match(line)
                if m:
                    cur.replaced_by.append((m.group(1), lineno))
                    continue
                m = _P_CONSIDER.match(line)
                if m:
                    cur.consider.append((m.group(1), lineno))
                    continue
                m = _P_REL.match(line)
                if m:
                    cur.relationships.append((m.group(1), m.group(2), lineno))
                    continue
                m = _P_INTER.match(line)
                if m:
                    # An OWL restriction / equivalence expression. Recorded in its own list: it is
                    # NOT a named-class is_a edge, and reading it as one would invent ancestry.
                    cur.restrictions.append((m.group(1), m.group(2) or "", lineno))
                    continue
        self._close(cur, block)
        self.active = {t for t, o in self.terms.items() if not o.obsolete}
        for tid, t in self.terms.items():
            for alt, _ln in t.alt_ids:
                self.alt_index.setdefault(alt, tid)

    def _close(self, cur, block) -> None:
        if cur is not None and block == "term" and cur.id.startswith(CL):
            self.terms[cur.id] = cur

    def _build_indexes(self) -> None:
        names: dict[str, set] = collections.defaultdict(set)
        syns: dict[str, set] = collections.defaultdict(set)
        for tid in self.active:
            t = self.terms[tid]
            if t.name:
                names[norm_label(t.name)].add(tid)
            for txt, scope in t.synonyms:
                if scope == "EXACT":
                    syns[norm_label(txt)].add(tid)
        self._name_index = names
        self._syn_index = syns

    # ---- closure

    def _build_closure(self) -> None:
        for tid in self.active:
            self._closure(tid, set())
        # reverse closure (descendants) for the granularity rule
        for tid in self.active:
            self._desc[tid] = frozenset(
                t for t in self.active if tid in self._anc.get(t, ()))

    def _closure(self, tid: str, stack: set) -> frozenset:
        got = self._anc.get(tid)
        if got is not None:
            return got
        if tid in stack:
            if tid not in self.cycles:
                self.cycles.append(tid)
            return frozenset()
        stack.add(tid)
        seen: set = set()
        for p in self.terms.get(tid, Term(tid, 0)).parents:
            seen.add(p)
            if p in self.terms:
                seen |= set(self._closure(p, stack))
        stack.discard(tid)
        res = frozenset(x for x in seen if x != tid)
        self._anc[tid] = res
        return res

    def ancestors_cl(self, tid: str) -> set[str]:
        return {a for a in self._anc.get(tid, frozenset()) if a.startswith(CL)}

    def descendants_cl(self, tid: str) -> frozenset:
        return self._desc.get(tid, frozenset())

    def label(self, tid: str):
        t = self.terms.get(tid)
        return t.name if t else None

    def line_of(self, tid: str):
        t = self.terms.get(tid)
        return t.line if t else None

    def is_blanket(self, tid: str) -> bool:
        """An 'extremely broad' ancestor: this many active CL descendants or more. Such a term may
        not blanket an answer, per the stop line."""
        return len(self.descendants_cl(tid)) >= self.blanket_threshold

    def depth(self, tid: str) -> int:
        if tid not in self.terms or not self._anc.get(tid):
            return 0
        return max(1 + self.depth(p) for p in self.terms[tid].parents if p in self.terms) \
            if self.terms[tid].parents else 0

    def path(self, child: str, ancestor: str, max_len: int = 12) -> list[str]:
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

    # ---- the record every answer carries

    def snapshot_record(self) -> dict:
        return {"anchor": self.anchor.get("anchor"),
                "anchor_status": self.anchor.get("status"),
                "path": self.anchor.get("path"),
                "file_sha256": self.anchor.get("sha256_actual"),
                "release": self.release,
                "release_field": "data-version",
                "parser_version": (load_manifest(self.asset_root).get("parser_version")),
                "n_cl_terms": len(self.terms),
                "n_active": len(self.active),
                "n_obsolete": len(self.terms) - len(self.active)}

    # ---- resolve_term

    def resolve_term(self, text) -> dict:
        """Which CL term is this? Resolution status is explicit, and a non-unique match is NEVER
        resolved by preference: ambiguity goes to review."""
        rec = {"query": text, "canonical_id": None, "preferred_label": None,
               "obsolete_status": None, "resolution_status": None, "resolution_method": None,
               "candidates": [], "alternatives": [], "replacement": None,
               "unresolved_reason": None, "requires_review": False,
               "is_a_relation": None,
               "assessment": {"status": ASSESS_NOT_ASSESSED, "basis": [],
                              "unresolved_reason": "no sample, task granularity or evidence context "
                                                   "was supplied with this call"},
               "ontology_snapshot": self.snapshot_record()}
        if self.anchor.get("status") != "RESOLVED":
            rec.update(resolution_status="snapshot_unavailable",
                       unresolved_reason=f"ontology anchor {self.anchor.get('status')}")
            rec["assessment"]["status"] = ASSESS_UNMAPPED
            return rec
        if text is None or not str(text).strip():
            rec.update(resolution_status="unresolved", unresolved_reason="empty input")
            return rec
        raw = str(text).strip()

        # 1) an identifier, primary or alternate
        if raw.upper().startswith("CL:") or raw in self.alt_index:
            tid = raw if raw.startswith(CL) else self.alt_index.get(raw)
            if raw in self.alt_index and raw not in self.terms:
                return self._fill(rec, self.alt_index[raw], "alt_id", "unique_alt_id",
                                  candidates=[raw])
            if tid in self.terms:
                return self._fill(rec, tid, "id", "unique_id", candidates=[tid])

        # 2) a preferred name
        key = norm_label(raw)
        by_name = sorted(self._name_index.get(key, ()))
        if len(by_name) == 1:
            return self._fill(rec, by_name[0], "name", "unique_name", candidates=by_name)
        if len(by_name) > 1:
            rec.update(candidates=by_name, alternatives=by_name, resolution_status="ambiguous",
                       resolution_method="name",
                       unresolved_reason="same preferred label on more than one CL term "
                                         "(same label, different concept)",
                       requires_review=True)
            return rec

        # 3) a synonym - exact scope only, and only when it resolves to exactly one term
        by_syn = sorted(self._syn_index.get(key, ()))
        if len(by_syn) == 1:
            return self._fill(rec, by_syn[0], "synonym", "unique_synonym", candidates=by_syn)
        if len(by_syn) > 1:
            rec.update(candidates=by_syn, alternatives=by_syn, resolution_status="ambiguous",
                       resolution_method="synonym",
                       unresolved_reason="an exact synonym of more than one CL term; the ambiguity "
                                         "is left to review and is not resolved towards any "
                                         "particular answer",
                       requires_review=True)
            return rec

        # 4) an obsolete label whose term has exactly one declared replacement
        obs = [tid for tid in self.terms
               if self.terms[tid].obsolete and self.terms[tid].name
               and norm_label(self.terms[tid].name) == key]
        if len(obs) == 1:
            tid = obs[0]
            repl = sorted({r for r, _ln in self.terms[tid].replaced_by})
            if len(repl) == 1:
                rec.update(canonical_id=tid, preferred_label=self.terms[tid].name,
                           obsolete_status="obsolete", resolution_status="obsolete_replaced",
                           resolution_method="unique_replacement", candidates=[tid],
                           replacement={"replaced_by": repl[0],
                                        "replaced_by_label": self.label(repl[0]),
                                        "line": self.line_of(repl[0])})
                rec["assessment"]["status"] = ASSESS_UNDER_REVIEW
                rec["assessment"]["basis"] = [
                    "the term is obsolete: the replacement is reported, not silently substituted"]
                return rec
            rec.update(candidates=[tid], alternatives=repl, canonical_id=tid,
                       preferred_label=self.terms[tid].name, obsolete_status="obsolete",
                       resolution_status="ambiguous", resolution_method="replacement",
                       unresolved_reason="obsolete term with no unique replacement "
                                         f"({len(repl)} replaced_by, {len(self.terms[tid].consider)} consider)",
                       requires_review=True)
            return rec

        rec.update(resolution_status="unresolved",
                   unresolved_reason="label not found in this snapshot by preferred name, exact "
                                     "synonym or alternate identifier")
        return rec

    def _fill(self, rec, tid, method, status, candidates):
        t = self.terms[tid]
        rec.update(canonical_id=tid, preferred_label=t.name, resolution_method=method,
                   resolution_status=status, candidates=candidates,
                   obsolete_status="obsolete" if t.obsolete else "active")
        if t.obsolete:
            repl = sorted({r for r, _ln in t.replaced_by})
            rec["resolution_status"] = "obsolete_" + status
            rec["replacement"] = ({"replaced_by": repl[0], "replaced_by_label": self.label(repl[0])}
                                  if len(repl) == 1 else {"replaced_by": None,
                                                          "candidates": repl})
            rec["requires_review"] = len(repl) != 1
            rec["assessment"]["status"] = ASSESS_UNDER_REVIEW
            rec["assessment"]["basis"] = ["resolved to an obsolete term"]
        return rec

    # ---- get_ancestors

    def get_ancestors(self, term, max_depth: int = 0) -> dict:
        r = self.resolve_term(term)
        out = {"query": term, "canonical_id": r["canonical_id"],
               "preferred_label": r["preferred_label"],
               "resolution_status": r["resolution_status"],
               "unresolved_reason": r["unresolved_reason"],
               "ancestors": [], "n_ancestors": 0, "n_across_cl": 0,
               "max_depth": None, "blanket_ancestors": [], "requires_review": r["requires_review"],
               "is_a_relation": None,
               "assessment": {"status": ASSESS_NOT_ASSESSED,
                              "unresolved_reason": "ancestry alone does not assess an answer"},
               "ontology_snapshot": self.snapshot_record()}
        tid = r["canonical_id"]
        if not tid:
            out["assessment"]["status"] = ASSESS_UNMAPPED
            return out
        rows = []
        for a in sorted(self.ancestors_cl(tid)):
            d = max(1, self._levels(tid, a))
            if max_depth and d > int(max_depth):
                continue
            rows.append({"id": a, "label": self.label(a), "levels_above": d,
                         "line": self.line_of(a),
                         "path": self.path(tid, a),
                         "is_blanket_ancestor": self.is_blanket(a),
                         "n_descendants": len(self.descendants_cl(a))})
        rows.sort(key=lambda x: (x["levels_above"], x["id"]))
        out.update(ancestors=rows, n_ancestors=len(rows),
                   n_across_cl=sum(1 for a in self._anc.get(tid, ()) if not a.startswith(CL)),
                   max_depth=max([x["levels_above"] for x in rows], default=0),
                   blanket_ancestors=[x["id"] for x in rows if x["is_blanket_ancestor"]])
        return out

    def _levels(self, child: str, ancestor: str) -> int:
        p = self.path(child, ancestor)
        return len(p) - 1 if p else 0

    # ---- compare_terms

    def compare_terms(self, ours, theirs, evidence_source: str = "",
                      evidence_assertion: str = "", context: str = "") -> dict:
        """Classify one (our term, their term) pair. The graph verdict and the assessment of the
        answer are two separate records; neither is derived from the other."""
        ro, rt = self.resolve_term(ours), self.resolve_term(theirs)
        rec = {"ours": {"input": ours, "canonical_id": ro["canonical_id"],
                        "label": ro["preferred_label"],
                        "resolution_status": ro["resolution_status"],
                        "unresolved_reason": ro["unresolved_reason"]},
               "theirs": {"input": theirs, "canonical_id": rt["canonical_id"],
                          "label": rt["preferred_label"],
                          "resolution_status": rt["resolution_status"],
                          "unresolved_reason": rt["unresolved_reason"]},
               "verdict": None, "is_a_relation": None, "ancestor_path": None,
               "levels_crossed": None, "unresolved_reason": None,
               "incompatibility_evidence": None, "context": context or None,
               "is_a_relation_note": None,
               "assessment": {"status": ASSESS_NOT_ASSESSED, "min_report_granularity_met": None,
                              "basis": [], "unresolved_reason": None},
               "ontology_snapshot": self.snapshot_record()}
        a, b = ro["canonical_id"], rt["canonical_id"]
        if self.anchor.get("status") != "RESOLVED":
            rec.update(verdict=NOT_SUPPORTED, is_a_relation=REL_UNRESOLVED,
                       unresolved_reason=f"ontology anchor {self.anchor.get('status')}")
            rec["assessment"]["status"] = ASSESS_UNMAPPED
            return rec
        if not a or not b:
            side = "both" if not a and not b else ("ours" if not a else "theirs")
            rec.update(verdict=NOT_SUPPORTED, is_a_relation=REL_UNRESOLVED,
                       unresolved_reason=f"{side} could not be uniquely resolved: "
                                         + (ro["unresolved_reason"] if side in ("ours", "both") else
                                            rt["unresolved_reason"]))
            rec["assessment"].update(status=ASSESS_UNMAPPED,
                                     unresolved_reason="one side carries no unique CL term, so the "
                                                       "graph can say nothing about the pair")
            return rec
        if a == b:
            rec.update(verdict=SAME_TERM, is_a_relation=REL_SAME, ancestor_path=[a],
                       levels_crossed=0)
            rec["assessment"].update(status=ASSESS_SUPPORTED, min_report_granularity_met=True,
                                     basis=["the two sides are the same canonical CL term"])
            return rec
        if a in self.ancestors_cl(b):
            rec.update(verdict=OURS_BROADER, is_a_relation=REL_OURS_ANCESTOR,
                       ancestor_path=self.path(b, a), levels_crossed=self._levels(b, a))
            blanket = self.is_blanket(a)
            rec["assessment"].update(
                min_report_granularity_met=not blanket,
                status=ASSESS_RESOLUTION_LIMITED if blanket else ASSESS_SUPPORTED,
                basis=["our term is an ancestor of the reference term, so the answer is coarser "
                       "than the reference; a coarse answer is a resolution limitation",
                       f"descendants of our term = {len(self.descendants_cl(a))}, blanket "
                       f"threshold = {self.blanket_threshold}"],
                unresolved_reason=("the only relation runs through an extremely broad ancestor, "
                                   "which does not meet the minimum reporting granularity"
                                   if blanket else None))
            return rec
        if b in self.ancestors_cl(a):
            rec.update(verdict=OURS_NARROWER, is_a_relation=REL_THEIRS_ANCESTOR,
                       ancestor_path=self.path(a, b), levels_crossed=self._levels(a, b))
            rec["assessment"].update(
                status=ASSESS_EVIDENCE_INSUFFICIENT, min_report_granularity_met=True,
                basis=["our term is finer than the reference term; the extra resolution is not "
                       "verified by the reference, so it earns nothing automatically"],
                unresolved_reason="the finer answer is unverified against the reference term")
            return rec
        # no ancestor relation in either direction
        shared = sorted(self.ancestors_cl(a) & self.ancestors_cl(b))
        rec["is_a_relation_note"] = ("a shared ancestor is not equivalence"
                                     + (f" (nearest shared ancestor candidate(s): {', '.join(shared[:3])})"
                                        if shared else ""))
        if evidence_source or evidence_assertion:
            rec.update(verdict=CONFIRMED_INCOMPATIBLE, is_a_relation=REL_NONE,
                       incompatibility_evidence={"source": evidence_source,
                                                 "assertion": evidence_assertion,
                                                 "recorded": True})
            rec["assessment"].update(status=ASSESS_INCOMPATIBLE,
                                     min_report_granularity_met=True,
                                     basis=["explicit incompatibility evidence was supplied and is "
                                            "recorded with the verdict; the graph alone never "
                                            "establishes exclusion"])
            return rec
        rec.update(verdict=NOT_SUPPORTED, is_a_relation=REL_NONE,
                   unresolved_reason="no ancestor relation in either direction; this is NOT proof of "
                                     "biological mutual exclusion and is not reported as a confirmed "
                                     "error")
        rec["assessment"].update(
            status=ASSESS_EVIDENCE_INSUFFICIENT, min_report_granularity_met=None,
            basis=["the snapshot contains no relation between the two terms; multiple inheritance, "
                   "an incomplete ontology or cross-classification all produce this state"],
            unresolved_reason="excluding either term would need explicit incompatibility evidence, "
                              "which was not supplied")
        return rec

    # ---- explain_class_mapping

    def explain_class_mapping(self, internal_class_id, reference_term: str = "") -> dict:
        """What backs the mapping this library ships for one of our classes?"""
        src = self.asset_root / ALIGNMENT_REL
        out = {"query": internal_class_id, "mapping_source": ALIGNMENT_REL,
               "mapping_source_sha256": sha256_file(src) if src.is_file() else None,
               "internal_class_id": None, "canonical_id": None, "cl_label": None,
               "mapping_status": None, "mapping_reason": None, "libraries": [],
               "qualifier": None, "graph_says": None, "comparison": None,
               "is_a_relation": None, "ancestor_path": None, "unresolved_reason": None,
               "assessment": {"status": ASSESS_NOT_ASSESSED, "basis": [],
                              "unresolved_reason": "no sample, task granularity or evidence context"},
               "ontology_snapshot": self.snapshot_record()}
        entry = None
        if src.is_file():
            try:
                align = json.loads(src.read_text(encoding="utf-8"))
                labels = align.get("labels") or {}
                entry = labels.get(str(internal_class_id))
                if entry is None:                       # case-insensitive, still unique-only
                    hits = [k for k in labels if norm_label(k) == norm_label(internal_class_id)]
                    entry = labels[hits[0]] if len(hits) == 1 else None
                    if len(hits) > 1:
                        out.update(mapping_status="ambiguous",
                                   mapping_reason="more than one shipped class matches this name",
                                   unresolved_reason=f"candidates: {sorted(hits)}",
                                   requires_review=True)
                        out["assessment"]["status"] = ASSESS_UNDER_REVIEW
                        return out
            except Exception as e:
                out.update(mapping_status="source_unreadable",
                           unresolved_reason=f"{ALIGNMENT_REL} unreadable: {type(e).__name__}")
                return out
        if entry is None:
            out.update(mapping_status="not_mapped",
                       unresolved_reason="this class carries no shipped CL mapping; nothing is "
                                         "invented for it here")
            out["assessment"].update(status=ASSESS_UNMAPPED,
                                     unresolved_reason="no mapping on our side")
            return out
        tid = entry.get("cl_id")
        out.update(internal_class_id=str(internal_class_id), canonical_id=tid,
                   cl_label=entry.get("cl_label"), mapping_status=entry.get("status"),
                   mapping_reason=entry.get("reason"), libraries=entry.get("libraries") or [],
                   qualifier=entry.get("qualifier"))
        if tid and tid in self.terms:
            out["graph_says"] = {"in_snapshot": True, "line": self.line_of(tid),
                                 "n_ancestors_cl": len(self.ancestors_cl(tid)),
                                 "n_descendants_cl": len(self.descendants_cl(tid)),
                                 "n_parents": len(self.terms[tid].parents),
                                 "multiple_inheritance": len(self.terms[tid].parents) > 1,
                                 "develops_from": sorted(
                                     {t for r, t, _ln in self.terms[tid].relationships
                                      if r == "RO:0002202"})}
            out["is_a_relation"] = None
            out["assessment"].update(
                status=ASSESS_SUPPORTED if entry.get("status") == "mapped" else ASSESS_UNDER_REVIEW,
                basis=["the shipped mapping points at a term present in this snapshot",
                       f"the mapping source is recorded by hash ({ALIGNMENT_REL})"])
        elif tid:
            out["graph_says"] = {"in_snapshot": False}
            out.update(unresolved_reason="the shipped mapping names a term that is not in this "
                                         "snapshot; recorded, not repaired")
            out["assessment"].update(status=ASSESS_EVIDENCE_INSUFFICIENT,
                                     basis=["mapping present, term absent from the fixed snapshot"])
        else:
            out.update(unresolved_reason="the shipped mapping carries no CL id for this class")
            out["assessment"].update(status=ASSESS_UNMAPPED)
        if reference_term:
            cmp_ = self.compare_terms(tid or internal_class_id, reference_term)
            out["comparison"] = cmp_
            out["is_a_relation"] = cmp_["is_a_relation"]
            out["ancestor_path"] = cmp_["ancestor_path"]
        return out

    # ---- self description

    def summary(self) -> dict:
        rel_cases = {
            "term": self.terms["CL:0000000"].name if "CL:0000000" in self.terms else None,
            "n_total": len(self.terms),
        }
        return {"ontology_snapshot": self.snapshot_record(),
                "anchor_status": self.anchor.get("status"),
                "release": self.release, "format_version": self.format_version,
                "ontology_id": self.ontology_id,
                "n_terms_in_file": len(self.terms),
                "n_active": len(self.active),
                "n_obsolete": sum(1 for t in self.terms.values() if t.obsolete),
                "n_alt_ids": sum(len(t.alt_ids) for t in self.terms.values()),
                "n_obsolete_with_unique_replacement": sum(
                    1 for t in self.terms.values()
                    if t.obsolete and len({r for r, _l in t.replaced_by}) == 1),
                "n_obsolete_with_ambiguous_replacement": sum(
                    1 for t in self.terms.values()
                    if t.obsolete and len({r for r, _l in t.replaced_by}) > 1),
                "n_consider_only": sum(1 for t in self.terms.values()
                                       if t.obsolete and not t.replaced_by and t.consider),
                "n_is_a_edges_cl_to_cl": sum(
                    1 for t in self.terms.values() for p in t.parents if p.startswith(CL)),
                "n_is_a_edges_to_outside": sum(
                    1 for t in self.terms.values() for p in t.parents if not p.startswith(CL)),
                "n_dangling_parents": sum(
                    1 for t in self.terms.values() for p in t.parents if p not in self.terms),
                "n_restriction_expressions": sum(len(t.restrictions) for t in self.terms.values()),
                "n_multiple_inheritance": sum(1 for t in self.active
                                              if len(self.terms[t].parents) > 1),
                "n_duplicate_id_blocks": self.n_duplicate_id_blocks,
                "n_import_term_blocks": self.n_import_term_blocks,
                "declared_imports_in_header": len(self.imports_declared),
                "same_label_different_concept": sorted(
                    k for k, v in self._name_index.items() if len(v) > 1),
                "ambiguous_exact_synonyms": sorted(
                    k for k, v in self._syn_index.items() if len(v) > 1),
                "cycles": self.cycles,
                "blanket_ancestor_threshold": self.blanket_threshold,
                "n_blanket_ancestors": sum(1 for t in self.active if self.is_blanket(t)),
                "rel_cases": rel_cases}


# ---------------------------------------------------------------- module-level convenience

_CACHE: dict = {}


def layer(asset_root=None) -> OntologySnapshot:
    key = str((Path(asset_root).resolve() if asset_root else repo_root()))
    if key not in _CACHE:
        _CACHE[key] = OntologySnapshot(Path(asset_root) if asset_root else None)
    return _CACHE[key]


def anchor_status(asset_root=None) -> list[dict]:
    """Every anchor in the manifest with its resolution status - the record a gate reads."""
    root = (Path(asset_root).resolve() if asset_root else repo_root())
    man = load_manifest(root if asset_root else None)
    return [resolve_anchor(a.get("anchor_id"), root) for a in man.get("anchors", [])]


def _main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Ontology explanation layer self-check")
    ap.add_argument("--asset-root", default="")
    a = ap.parse_args()
    root = Path(a.asset_root) if a.asset_root else None
    snap = layer(root)
    out = snap.summary()
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    # The self-check prints; it writes nothing. This module contains no write call at all, which is
    # what makes "the capability reads and nothing else" checkable rather than asserted.
    return 0 if snap.anchor.get("status") == "RESOLVED" else 2


if __name__ == "__main__":
    import sys
    sys.exit(_main())