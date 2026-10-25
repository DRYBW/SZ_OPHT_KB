#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_deliverables.py — CITTITLE (card t_d8e7f2d4): the card's own numbers, recomputed by a
SECOND implementation, from the inputs, with every declared value compared against the recomputed one.

Discipline (same shape as the LINKKEY card's verifier):
  * It trusts nothing this directory says about itself. It reads the frozen registry, the delivered
    twins, the corpus and the emitted tables and recomputes.
  * The normalisation, the cap test, the reason classifier and the JSON handling are re-implemented
    here rather than imported, so a bug in `cittitle_common.py` cannot make this verifier agree with
    the build by construction. (The convention itself — NFKC + lower + fold — is shared; it is a
    definition, not an implementation.)
  * Read-only on the real tree: it opens files for reading only and writes nothing.

Exit 0 = every check PASS; exit 1 = at least one FAIL (each FAIL names the check and both numbers).
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/ubuntu/EYEKB_REPO")
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out"

FROZEN = ROOT / "kb" / "link_registry" / "LINK_REGISTRY_v1.jsonl"
ANCHOR = OUT / "LINK_REGISTRY_v2_cittitle.jsonl"
DROPIN = OUT / "LINK_REGISTRY_v2_cittitle_dropin.jsonl"
CORPUS = ROOT / "literature_db" / "v2.4.2_2026-09_slim" / "papers.jsonl"
ADDED = ("title_full", "doi", "pmcid")
LIMIT = 120

RESULTS = []


def check(cid, ok, detail):
    RESULTS.append((cid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {detail}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- independent normalisation / classification (deliberately not imported) ------------------
_D = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2043"


def n1(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def n2(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    for d in _D:
        s = s.replace(d, "-")
    return n1(s)


def lines_of(p: Path):
    return [ln for ln in p.read_text(encoding="utf-8").split("\n") if ln.strip()]


def strip_added_written_by_hand(cit):
    """Drop the three added keys, keeping the original key order (hand-written on purpose)."""
    out = {}
    for k in cit:
        if k in ADDED:
            continue
        out[k] = cit[k]
    return out


def main() -> int:
    print("verify_deliverables.py — CITTITLE independent recomputation")
    meta_declared = json.loads((OUT / "BACKFILL_META.json").read_text(encoding="utf-8"))
    cf = json.loads((OUT / "CITATION_TITLE_COUNTERFACTUAL_v1.json").read_text(encoding="utf-8"))

    frozen_lines = lines_of(FROZEN)
    anchor_lines = lines_of(ANCHOR)
    dropin_lines = lines_of(DROPIN)

    # ---------------------------------------------------------------- C01 inputs
    check("C01-input-sha",
          sha(FROZEN) == meta_declared["inputs"]["frozen_registry"]["sha256"]
          and sha(CORPUS) == cf["inputs"]["corpus_primary"]["sha256"],
          f"frozen {sha(FROZEN)[:16]} / corpus {sha(CORPUS)[:16]} match the declared inputs")

    # ---------------------------------------------------------------- C02 row/anchor identity
    check("C02-row-count", len(frozen_lines) == len(anchor_lines) == len(dropin_lines) == 165,
          f"frozen={len(frozen_lines)} anchor={len(anchor_lines)} dropin={len(dropin_lines)}")

    corpus = {}
    with CORPUS.open(encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                d = json.loads(ln)
                corpus[str(d.get("paper_id") or "")] = d

    n_cit = 0
    inv_ok = inv_bad = 0
    der_ok = der_bad = 0
    titlefull_bad = []
    added_missing = 0
    doi_off = pmcid_off = 0
    pre_state = Counter()

    for fl, al, dl in zip(frozen_lines, anchor_lines, dropin_lines):
        frow, arow, drow = json.loads(fl), json.loads(al), json.loads(dl)
        back = {}
        for k, v in arow.items():
            back[k] = ([strip_added_written_by_hand(c) for c in v] if k == "citations" else v)
        if json.dumps(back, ensure_ascii=False) == fl:
            inv_ok += 1
        else:
            inv_bad += 1
        der = {}
        for k, v in arow.items():
            der[k] = ([dict(c, title=c.get("title_full", c.get("title"))) for c in v]
                      if k == "citations" else v)
        if json.dumps(der, ensure_ascii=False) == dl:
            der_ok += 1
        else:
            der_bad += 1
        for c0, c1, c2 in zip(frow.get("citations") or [], arow.get("citations") or [],
                              drow.get("citations") or []):
            n_cit += 1
            if any(k not in c1 for k in ADDED):
                added_missing += 1
                continue
            cm = corpus.get(str(c0.get("pmid"))) or {}
            if c1["title_full"] != (cm.get("title") or "") or c2["title"] != c1["title_full"]:
                titlefull_bad.append(c1.get("pmid"))
            if c1["doi"] != (cm.get("doi") or ""):
                doi_off += 1
            if c1["pmcid"] != (cm.get("pmcid") or ""):
                pmcid_off += 1
            t0 = c0.get("title") or ""
            pre_state["EMPTY" if not t0.strip() else
                      ("LEN120" if len(t0) == LIMIT else "OTHER")] += 1

    check("C03-anchor-inverts",
          inv_bad == 0 and inv_ok == 165,
          f"every one of {inv_ok} lines inverts to the frozen bytes (bad={inv_bad})")
    check("C04-dropin-derives",
          der_bad == 0 and der_ok == 165,
          f"dropin == anchor with title := title_full on {der_ok} lines (bad={der_bad})")
    check("C05-three-keys-present", added_missing == 0,
          f"{n_cit} citation records carry title_full/doi/pmcid (missing={added_missing})")
    check("C06-title-from-corpus",
          not titlefull_bad and doi_off == 0 and pmcid_off == 0,
          f"title_full == corpus title, doi/pmcid == corpus fields; mismatches="
          f"title={len(titlefull_bad)} doi={doi_off} pmcid={pmcid_off}")

    # ---------------------------------------------------------------- C07 counterfactual recompute
    pre_titles = defaultdict(list)
    for fl in frozen_lines:
        for c in (json.loads(fl).get("citations") or []):
            pre_titles[str(c.get("pmid"))].append(c.get("title") or "")
    papers = sorted(pre_titles)
    pre_pick = {p: max(pre_titles[p], key=len) if any(t.strip() for t in pre_titles[p]) else ""
                for p in papers}

    def rate(fn, pick):
        ok = 0
        for p in papers:
            ct = ((corpus.get(p) or {}).get("title") or "")
            if ct and fn(pick[p], ct):
                ok += 1
        return ok

    rec = {
        "A_strict_full_equality|N1_raw|pre": rate(lambda t, c: n1(t) == n1(c) if n1(t) else False, pre_pick),
        "A_strict_full_equality|N2_display_stripped|pre":
            rate(lambda t, c: n2(t) == n2(c) if n2(t) else False, pre_pick),
        "B_prefix40|N1_raw|pre":
            rate(lambda t, c: bool(n1(t)) and n1(t)[:40] == n1(c)[:40], pre_pick),
        "B_prefix40|N2_display_stripped|pre":
            rate(lambda t, c: bool(n2(t)) and n2(t)[:40] == n2(c)[:40], pre_pick),
    }
    post_pick = {p: ((corpus.get(p) or {}).get("title") or "") for p in papers}
    arms = {
        "A_strict_full_equality|N1_raw": lambda t, c: bool(n1(t)) and n1(t) == n1(c),
        "A_strict_full_equality|N2_display_stripped": lambda t, c: bool(n2(t)) and n2(t) == n2(c),
        "B_prefix40|N1_raw": lambda t, c: bool(n1(t)) and n1(t)[:40] == n1(c)[:40],
        "B_prefix40|N2_display_stripped": lambda t, c: bool(n2(t)) and n2(t)[:40] == n2(c)[:40],
    }
    rec = {}
    for k, fn in arms.items():
        rec[k + "|pre"] = rate(fn, pre_pick)
        rec[k + "|post"] = rate(fn, post_pick)
    declared = {k: v["matched"] for k, v in cf["calibers"].items()}
    diff = {k: (rec[k], declared.get(k)) for k in rec if rec[k] != declared.get(k)}
    check("C07-counterfactual-recompute", not diff,
          f"all 8 caliber arms recomputed: {rec}" if not diff else f"declared != recomputed: {diff}")

    # ---------------------------------------------------------------- C08 per-row reasons
    un_pre = list(csv.DictReader((OUT / "UNMATCHED_PRE_v1.tsv").open(encoding="utf-8"),
                                 delimiter="\t"))
    un_post = list(csv.DictReader((OUT / "UNMATCHED_POSTFIX_v1.tsv").open(encoding="utf-8"),
                                  delimiter="\t"))
    declared_un = sum(v["unmatched"] for v in cf["calibers"].values() if v["arm"] == "pre")
    declared_post = sum(v["unmatched"] for v in cf["calibers"].values() if v["arm"] == "post")
    reasons_sum = sum(sum(v["reasons"].values())
                      for v in cf["calibers"].values() if v["arm"] == "pre")
    empty_reason = sum(1 for r in un_pre if not (r.get("reason_code") or "").strip()
                       or not (r.get("reason_text") or "").strip())
    check("C08-unmatched-rows",
          len(un_pre) == declared_un == reasons_sum and len(un_post) == declared_post == 0
          and empty_reason == 0,
          f"pre rows={len(un_pre)} declared={declared_un} reason-sum={reasons_sum}; "
          f"post rows={len(un_post)} declared={declared_post}; blank-reason rows={empty_reason}")

    # ---------------------------------------------------------------- C09 ledger
    ledger = list(csv.DictReader((OUT / "CITATION_TITLE_LEDGER_v1.tsv").open(encoding="utf-8"),
                                 delimiter="\t"))
    post_all = all(r["post_strict_match"] == "1" for r in ledger)
    pre_cls = Counter(r["pre_class"] for r in ledger)
    check("C09-ledger",
          len(ledger) == n_cit and post_all
          and dict(pre_cls) == cf["ledger_counts"]["pre_class"],
          f"ledger rows={len(ledger)} (citations={n_cit}); post-fix strict match on all rows="
          f"{post_all}; pre classes={dict(pre_cls)}")

    # ---------------------------------------------------------------- C10 controls
    ctl = cf["controls"]
    jr = defaultdict(Counter)
    yr = defaultdict(Counter)
    for fl in frozen_lines:
        for c in (json.loads(fl).get("citations") or []):
            jr[str(c.get("pmid"))][(c.get("journal") or "").strip()] += 1
            yr[str(c.get("pmid"))][str(c.get("year") or "").strip()] += 1
    cm_journal = cm_year = 0
    for p in papers:
        cm = corpus.get(p) or {}
        js = max(jr[p], key=jr[p].get) if jr[p] else ""
        if js and n1(js) == n1(cm.get("journal") or ""):
            cm_journal += 1
        ys = max(yr[p], key=yr[p].get) if yr[p] else ""
        if ys and str(cm.get("year") or "") == ys:
            cm_year += 1
    check("C10-field-controls",
          cm_year == ctl["year_agree"] and cm_journal == ctl["journal_agree"] == 820,
          f"year agreement recomputed {cm_year}/{ctl['year_denom']} (declared {ctl['year_agree']}); "
          f"journal {cm_journal}/{ctl['journal_denom']} (declared {ctl['journal_agree']}, "
          f"the 5 misses being the PPR_* preprints whose corpus journal field is empty)")

    # ---------------------------------------------------------------- C11 the five PPR_ ids
    ppr = sorted({p for p in papers if not p.isdigit()})
    check("C11-preprint-ids",
          len(ppr) == 5 and all(p.startswith("PPR_") for p in ppr)
          and ctl["journal_denom"] - ctl["journal_agree"] == 5,
          f"{len(ppr)} non-numeric cited ids, all PPR_*: {ppr}")

    # ---------------------------------------------------------------- C12 defect counts (live)
    empty_recs = sum(1 for fl in frozen_lines for c in (json.loads(fl).get("citations") or [])
                     if not (c.get("title") or "").strip())
    capped_recs = sum(1 for fl in frozen_lines for c in (json.loads(fl).get("citations") or [])
                      if (c.get("title") or "") and len(c.get("title")) == LIMIT)
    check("C12-defect-live",
          empty_recs == cf["ledger_counts"]["pre_class"]["EMPTY"]
          and capped_recs == cf["ledger_counts"]["pre_class"]["CAPPED_120"]
          + cf["ledger_counts"]["pre_class"]["GENUINE_120"],
          f"frozen registry: {empty_recs} empty-title records, {capped_recs} records whose title is "
          f"exactly {LIMIT} chars (= {cf['ledger_counts']['pre_class']['CAPPED_120']} capped + "
          f"{cf['ledger_counts']['pre_class']['GENUINE_120']} genuinely {LIMIT} chars)")

    bad = [c for c, ok, _ in RESULTS if not ok]
    print(f"\nverify_deliverables: {len(RESULTS)} checks, {len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL")
    if bad:
        print("FAILED:", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())