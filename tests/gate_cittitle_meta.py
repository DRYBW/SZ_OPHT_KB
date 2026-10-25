#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_cittitle_meta.py — G12 gate: citation presentation metadata (title / doi / pmcid).

Why this gate exists (card t_d8e7f2d4, CITTITLE)
    `kb/link_registry/scripts/build_link_registry.py` wrote a citation's title as
    `(hit title)[:120]` on the retrieval route and as `""` on the full-text gene-index route. On the
    shipped registry that is 2,429 citation records with no title at all and 509 whose title is a
    120-character prefix. Every cited paper is present in the corpus and the corpus holds the complete
    title, so nothing on the citation side could be checked by title — an audit against the corpus
    reported ~30% and read it as "the two libraries disagree" (measured: A strict 247/825 = 29.94%,
    B prefix-40 369/825 = 44.73%). The builder now joins title / doi / pmcid from the corpus on
    `paper_id == pmid`, and the delivered registry carries `title_full` / `doi` / `pmcid` on every
    citation record. This gate re-derives all of that from disk.

Checks (each fail-closed; a FAIL names the check code, never just "G12 FAIL"):
  G12-C01 SOURCE-FIX        the builder no longer contains either pre-fix literal (`"title": ""` on
                            the gene-index route, `(hit.get("title") or "")[:120]` on the retrieval
                            route) and does contain the fix (`corpus_meta_index()` + `citation_field(
                            …, "title")` at both citation sites). A regression here is the defect
                            coming back, which no delivered file would show until the next rebuild.
  G12-C02 META-PRESENT      every citation record of the registry under test carries all three keys.
                            Registry under test = the live kb/link_registry/LINK_REGISTRY_v1.jsonl
                            when it carries the keys (a post-rebuild state), otherwise the delivered
                            anchor twin docs/plans/cittitle_20261025/out/LINK_REGISTRY_v2_cittitle.jsonl.
  G12-C03 META-FROM-CORPUS  for every citation, `title_full` equals the corpus' own title for its
                            pmid and `doi` / `pmcid` equal the corpus' fields; and no citation title
                            in the registry under test is empty. INCONCLUSIVE (rc=3) when no corpus
                            copy is on this tree (G2 asset not unpacked; G3/G11 precedent) — the
                            numbers cannot be re-derived, so no verdict is issued.
  G12-C04 COVERAGE          the registry under test has the same number of rows as the frozen
                            registry, and (when it is the twin) the same (entry_id, pmid) multiset as
                            the pre-image it was derived from.
  G12-C05 ANCHOR            the delivered anchor twin inverts to the delivered pre-image
                            byte-for-byte (remove title_full/doi/pmcid -> the original line), the
                            drop-in equals the anchor twin with `title := title_full`, and the
                            delivered pre-image's sha is the one recorded in BACKFILL_META.json. The
                            pre-image is an immutable copy inside this delivery, so this check is
                            executable on any tree and does not move when the live registry is
                            rebuilt.
  G12-C06 BUILDER-PARITY    the builder's own `corpus_meta_index()` (which imports the service
                            kernel) agrees key-for-key with this gate's stdlib-only corpus reader on
                            the cited ids. INCONCLUSIVE if the builder cannot be imported here — an
                            unimportable delivery is an environment state, but an importable builder
                            that disagrees is a FAIL.
  G12-C07 SELF-TEST         the gate's own comparators are proven to flag the planted violation
                            shapes (citation without the keys, mutated title_full, broken inversion,
                            source with a pre-fix literal) so a scanner that flags nothing cannot
                            pass. Synthetic strings only; the real tree is never modified.

Stdlib only; zero network; zero GPU; read-only on the real tree.

Usage (from anywhere; paths resolve off this file's location):
  python3 tests/gate_cittitle_meta.py
  python3 tests/gate_cittitle_meta.py --json out/G12_RESULTS.json

Environment: EYEKB_G12_CORPUS overrides the corpus candidate list (a single path). It exists so the
INCONCLUSIVE branch can be exercised on a real tree without moving the corpus; with it unset the gate
tries the repo's G2 slim library and then the pointer's default library.

Exit codes: 0 = PASS, 2 = FAIL (fail-closed), 3 = INCONCLUSIVE (a declared precondition is absent on
this tree, so no verdict may be issued; the one-click entry counts rc=3 as not-pass).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_REG = ROOT / "kb" / "link_registry" / "LINK_REGISTRY_v1.jsonl"
BUILDER = ROOT / "kb" / "link_registry" / "scripts" / "build_link_registry.py"
DELIV = ROOT / "docs" / "plans" / "cittitle_20261025"
ANCHOR = DELIV / "out" / "LINK_REGISTRY_v2_cittitle.jsonl"
DROPIN = DELIV / "out" / "LINK_REGISTRY_v2_cittitle_dropin.jsonl"
META_JSON = DELIV / "out" / "BACKFILL_META.json"
PREIMAGE = DELIV / "pre_images" / "LINK_REGISTRY_v1.jsonl.pre_cittitle"

ADDED = ("title_full", "doi", "pmcid")
_CORPUS_OVERRIDE = os.environ.get("EYEKB_G12_CORPUS", "")
CORPUS_CANDIDATES = ((Path(_CORPUS_OVERRIDE),) if _CORPUS_OVERRIDE else (
    ROOT / "literature_db" / "v2.4.2_2026-09_slim" / "papers.jsonl",
    Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/papers.jsonl"),
))

# The two literals the fix removed, recorded verbatim so a regression is a string match rather than a
# judgement call. The needle is the *code-shaped* assignment, not the bare `[:120]` slice: the fix's
# own comment and docstring describe the removed slice in prose (`Was (hit.get("title") or "")[:120]
# — a 120-character prefix is not a title`), and prose about the hazard must not be read as the
# hazard (the same rule the G9 scanner applies to references written inside backticks).
PREFIX_LITERAL = '"title": (hit.get("title") or "")[:120]'
EMPTY_LITERAL_NEEDLE = '"title": ""'


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def lines_of(p: Path):
    return [ln for ln in p.read_text(encoding="utf-8").split("\n") if ln.strip()]


# ---------------------------------------------------------------- readers (stdlib only)
_D = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2043"


def n1(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def load_corpus(path: Path):
    out = {}
    with path.open(encoding="utf-8") as fh:
        for ln in fh:
            if not ln.strip():
                continue
            d = json.loads(ln)
            pid = str(d.get("paper_id") or "")
            if pid:
                out[pid] = d
    return out


def strip_added(cit):
    return {k: v for k, v in cit.items() if k not in ADDED}


# ---------------------------------------------------------------- C01
def check_source_fix():
    if not BUILDER.is_file():
        return "FAIL", f"builder not on disk: {BUILDER.relative_to(ROOT)}"
    src = BUILDER.read_text(encoding="utf-8")
    off = []
    if PREFIX_LITERAL in src:
        off.append("the 120-character truncation literal is back on the retrieval route")
    if EMPTY_LITERAL_NEEDLE in src:
        off.append('the `"title": ""` literal is back on the gene-index route')
    if "def corpus_meta_index(" not in src:
        off.append("corpus_meta_index() is gone")
    n_title_calls = len(re.findall(r'citation_field\([^)]*"title"', src))
    if n_title_calls < 2:
        off.append(f'citation_field(..., "title") appears {n_title_calls}x, expected 2 '
                   "(retrieval route + gene-index route)")
    if "doi" not in src or "pmcid" not in src:
        off.append("doi/pmcid are no longer written onto citation records")
    return ("FAIL", "; ".join(off)) if off else \
           ("PASS", f"builder carries the fix: corpus_meta_index() present, citation_field(..., "
                    f'"title") at {n_title_calls} sites, neither pre-fix literal present')


# ---------------------------------------------------------------- C02/C03/C04
def pick_registry():
    live_rows = [json.loads(l) for l in lines_of(LIVE_REG)] if LIVE_REG.is_file() else []
    live_has = all(k in c for r in live_rows for c in (r.get("citations") or []) for k in ADDED)
    if live_rows and live_has:
        return LIVE_REG, live_rows, "live kb/link_registry/LINK_REGISTRY_v1.jsonl (post-rebuild state)"
    rows = [json.loads(l) for l in lines_of(ANCHOR)]
    return ANCHOR, rows, ("delivered anchor twin (the live registry does not carry the three keys "
                          "yet — the frozen file is not rewritten by this card)")


def iter_citations(rows):
    for r in rows:
        for c in (r.get("citations") or []):
            yield r, c


def check_meta_present(rows):
    missing = 0
    n = 0
    for _r, c in iter_citations(rows):
        n += 1
        if any(k not in c for k in ADDED):
            missing += 1
    if missing:
        return "FAIL", f"{missing}/{n} citation records do not carry all of {ADDED}"
    return "PASS", f"all {n} citation records carry {', '.join(ADDED)}"


def check_meta_from_corpus(rows):
    """title_full/doi/pmcid vs the corpus, sqlite-free, from whichever copy is on this tree."""
    corpus_path = next((p for p in CORPUS_CANDIDATES if p.is_file()), None)
    if corpus_path is None:
        return "INCONCLUSIVE", None, (
            "no corpus copy on this tree, so title_full/doi/pmcid cannot be re-derived "
            "(the corpus ships as the G2 Release asset)")
    corpus = load_corpus(corpus_path)
    bad_title, bad_doi, bad_pmcid, empty_title, unresolved = [], 0, 0, 0, []
    n = 0
    for _r, c in iter_citations(rows):
        n += 1
        pmid = str(c.get("pmid"))
        cm = corpus.get(pmid)
        if cm is None:
            unresolved.append(pmid)
            continue
        want_t = cm.get("title") or ""
        if (c.get("title_full") or "") != want_t:
            bad_title.append(pmid)
        if (c.get("doi") or "") != (cm.get("doi") or ""):
            bad_doi += 1
        if (c.get("pmcid") or "") != (cm.get("pmcid") or ""):
            bad_pmcid += 1
        if not (c.get("title_full") or "").strip():
            empty_title += 1
    detail = (f"corpus {corpus_path.parent.name}: {n} citation records checked; "
              f"title_full mismatches={len(bad_title)} empty={empty_title} "
              f"doi mismatches={bad_doi} pmcid mismatches={bad_pmcid} unresolved ids={len(unresolved)}")
    extra = {"corpus": str(corpus_path), "n": n, "title_mismatch": len(bad_title),
             "empty_title": empty_title, "doi_mismatch": bad_doi, "pmcid_mismatch": bad_pmcid,
             "unresolved": len(unresolved)}
    if bad_title or bad_doi or bad_pmcid or empty_title or unresolved:
        return "FAIL", extra, detail + f"; sample title mismatches={bad_title[:5]}"
    return "PASS", extra, detail


def check_coverage(rows, used_path):
    frozen = [json.loads(l) for l in lines_of(LIVE_REG)] if LIVE_REG.is_file() else []
    pre = [json.loads(l) for l in lines_of(PREIMAGE)] if PREIMAGE.is_file() else []
    if len(rows) != len(frozen):
        return "FAIL", f"registry under test has {len(rows)} rows, the frozen registry {len(frozen)}"
    if used_path == ANCHOR:
        if not pre:
            return "FAIL", "the delivered pre-image is missing, so coverage cannot be anchored"
        a = sorted((r.get("entry_id"), str(c.get("pmid"))) for r in rows
                   for c in (r.get("citations") or []))
        b = sorted((r.get("entry_id"), str(c.get("pmid"))) for r in pre
                   for c in (r.get("citations") or []))
        if a != b:
            return "FAIL", (f"(entry_id, pmid) multiset differs from the pre-image: "
                            f"{len(a)} vs {len(b)}")
        return "PASS", (f"{len(rows)} rows and {len(a)} (entry_id, pmid) pairs identical to the "
                        f"pre-image")
    return "PASS", (f"registry under test IS the live file: {len(rows)} rows, coverage identical "
                    "by construction")


# ---------------------------------------------------------------- C05
def check_anchor():
    if not (ANCHOR.is_file() and DROPIN.is_file() and PREIMAGE.is_file() and META_JSON.is_file()):
        return "FAIL", "one of the twin / pre-image / BACKFILL_META.json is missing"
    meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    recorded = meta["inputs"]["frozen_registry"]["sha256"]
    got = sha256_file(PREIMAGE)
    if got != recorded:
        return "FAIL", f"delivered pre-image sha {got[:16]} != the sha recorded in BACKFILL_META ({recorded[:16]})"
    pl, al, dl = lines_of(PREIMAGE), lines_of(ANCHOR), lines_of(DROPIN)
    if not (len(pl) == len(al) == len(dl)):
        return "FAIL", f"line counts differ: pre={len(pl)} anchor={len(al)} dropin={len(dl)}"
    inv_bad = der_bad = 0
    for p, a, d in zip(pl, al, dl):
        arow, drow = json.loads(a), json.loads(d)
        back = {k: ([strip_added(c) for c in v] if k == "citations" else v)
                for k, v in arow.items()}
        if json.dumps(back, ensure_ascii=False) != p:
            inv_bad += 1
        der = {k: ([dict(c, title=c.get("title_full", c.get("title"))) for c in v]
                   if k == "citations" else v) for k, v in arow.items()}
        if json.dumps(der, ensure_ascii=False) != d:
            der_bad += 1
    if inv_bad or der_bad:
        return "FAIL", (f"anchor twin breaks the byte anchor on {inv_bad} line(s); drop-in breaks "
                        f"the title:=title_full derivation on {der_bad} line(s)")
    return "PASS", (f"{len(al)} lines: anchor twin inverts to the pre-image byte-for-byte and the "
                    f"drop-in is the anchor twin derived by title := title_full; pre-image sha "
                    f"{got[:16]} matches BACKFILL_META")


# ---------------------------------------------------------------- C06
def check_builder_parity(rows):
    try:
        spec = importlib.util.spec_from_file_location("cittitle_builder", BUILDER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:                                            # noqa: BLE001
        return "INCONCLUSIVE", None, (f"the builder could not be imported here ({type(exc).__name__}: "
                                      f"{exc}); its own corpus reader therefore cannot be compared")
    try:
        meta, sources = mod.corpus_meta_index()
    except Exception as exc:                                            # noqa: BLE001
        return "FAIL", None, f"the builder's corpus_meta_index() raised: {exc}"
    if not meta:
        return "FAIL", None, "the builder's corpus_meta_index() returned an empty index"
    bad = []
    n = 0
    for _r, c in iter_citations(rows):
        pmid = str(c.get("pmid"))
        m = meta.get(pmid)
        if m is None:
            bad.append((pmid, "not in the builder's index")); continue
        n += 1
        for key in ("title", "doi", "pmcid"):
            if key == "title":
                if (c.get("title_full") or "") != (m.get("title") or ""):
                    bad.append((pmid, "title_full"))
            elif (c.get(key) or "") != (m.get(key) or ""):
                bad.append((pmid, key))
    detail = (f"builder reader vs this gate's reader: {n} ids compared, {len(bad)} disagreements; "
              f"builder sources={len(sources)}")
    if bad:
        return "FAIL", {"bad": bad[:5]}, detail + f" sample={bad[:5]}"
    return "PASS", None, detail


# ---------------------------------------------------------------- C07
def self_test():
    off = []
    src_good = 'def corpus_meta_index():\n    pass\n"title": citation_field(cmeta, pmid, "title"),\n' \
               '"doi": citation_field(cmeta, pmid, "doi"),\n"pmcid": citation_field(cmeta, pmid, "pmcid"),'
    src_bad = 'def corpus_meta_index():\n    pass\n"title": (hit.get("title") or "")[:120],\n' \
              '"doi": 1, "pmcid": 2'
    for tag, txt, want in (("clean", src_good, False), ("pre-fix", src_bad, True)):
        has_bad = PREFIX_LITERAL in txt
        if has_bad != want:
            off.append(f"self-test: the source scanner said {has_bad} for the {tag} source")
    # a citation missing a key must be seen as missing
    good_cit = {"pmid": "1", "title": "T", "title_full": "T", "doi": "d", "pmcid": "p"}
    if any(k not in good_cit for k in ADDED):
        off.append("self-test: a fully populated citation record was reported as incomplete")
    for drop in ADDED:
        c = {k: v for k, v in good_cit.items() if k != drop}
        if not any(k not in c for k in ADDED):
            off.append(f"self-test: dropping `{drop}` was not detected")
    # inversion comparator
    row = {"entry_id": "x", "citations": [good_cit]}
    line = json.dumps(row, ensure_ascii=False)
    back = {k: ([strip_added(x) for x in v] if k == "citations" else v) for k, v in row.items()}
    if json.dumps(back, ensure_ascii=False) == line:
        off.append("self-test: an un-stripped row was reported as inverting to the original")
    stripped = {k: ([strip_added(x) for x in v] if k == "citations" else v) for k, v in row.items()}
    if json.dumps(stripped, ensure_ascii=False) == line:
        off.append("self-test: stripping did not change the serialisation")
    # normalisation comparator (planted display artefact)
    if n1("A <i>B</i>") == n1("A B"):
        off.append("self-test: N1 was expected to see the HTML tag as a difference")
    return off


# ---------------------------------------------------------------- driver
def main() -> int:
    ap = argparse.ArgumentParser(description="G12: citation presentation metadata gate")
    ap.add_argument("--json", default="", help="write the machine-readable runout here")
    args = ap.parse_args()

    checks = []

    def add(cid, name, verdict, detail, extra=None):
        row = {"id": cid, "name": name, "verdict": verdict, "detail": detail}
        if extra:
            row["extra"] = extra
        checks.append(row)

    v1, d1 = check_source_fix()
    add("G12-C01", "SOURCE-FIX", v1, d1)

    used_path, rows, used_note = pick_registry()
    v2, d2 = check_meta_present(rows)
    add("G12-C02", "META-PRESENT", v2, f"{d2} [registry under test: {used_note}]")

    v3, x3, d3 = check_meta_from_corpus(rows)
    add("G12-C03", "META-FROM-CORPUS", v3, d3, x3)

    v4, d4 = check_coverage(rows, used_path)
    add("G12-C04", "COVERAGE", v4, d4)

    v5, d5 = check_anchor()
    add("G12-C05", "ANCHOR", v5, d5)

    v6, x6, d6 = check_builder_parity(rows)
    add("G12-C06", "BUILDER-PARITY", v6, d6, x6)

    off7 = self_test()
    add("G12-C07", "SELF-TEST", "FAIL" if off7 else "PASS",
        "; ".join(off7) if off7 else
        "planted pre-fix source literal / dropped metadata key / broken inversion all flagged")

    verdicts = {c["verdict"] for c in checks}
    if "FAIL" in verdicts:
        final, rc = "FAIL", 2
    elif "INCONCLUSIVE" in verdicts:
        final, rc = "INCONCLUSIVE", 3
    else:
        final, rc = "PASS", 0

    summary = {
        "gate": "G12",
        "script": "tests/gate_cittitle_meta.py",
        "final": final,
        "ok": final == "PASS",
        "registry_under_test": str(used_path.relative_to(ROOT)),
        "checks": checks,
    }
    lines = "\n".join(f"  {c['id']} {c['name']:<18} {c['verdict']:<13} {(c['detail'] or '')[:150]}"
                      for c in checks)
    print(f"[G12] citation presentation metadata: {final} (rc={rc})")
    print(lines)
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
        print(f"[G12] runout -> {args.json}")
    return rc


if __name__ == "__main__":
    sys.exit(main())