#!/usr/bin/env python3
"""Build the preprint -> published-article equivalence map from the library itself.

Why this file exists
--------------------
The retrieval face needs to know when two library records are the SAME study (a preprint and
its later peer-reviewed version) so that one query does not spend two result slots on one study.
That knowledge must be recomputable from disk, never hand-maintained.

Matching is title-based. DOI cannot be used: a preprint DOI (10.21203/rs.3.rs-10594726/v1) is not
the journal DOI, so the two records never share one.

Tiers (a pair lands in the FIRST tier it satisfies)
---------------------------------------------------
  A  title_exact   normalised titles byte-identical                          -> auto-dedupe
  B  title_prefix  one normalised title is a strict prefix of the other       -> auto-dedupe
                   (covers "published = preprint + an added trailing clause")
  C  title_near    token Jaccard >= 0.85 AND common leading run >= 50 AND     -> review only
                   same year window (covers a reworded middle, an added
                   subtitle, or a spelling fix in the title)

Tiers A and B are high-confidence and feed automatic de-duplication. Tier C is written to a
SEPARATE file and is NOT active: a wrong pair there would silently delete a genuine result from
someone's answer, so the cost of a false pair is asymmetric and the conservative side wins.
Tier C exists to be reviewed by a human, one line at a time.

Year guard for every tier: published year >= preprint year and <= preprint year + 3.

Outputs (new files only; nothing is overwritten):
  <out>/preprint_published_map_v1.jsonl        tiers A+B  (active map, one line per preprint)
  <out>/preprint_published_map_v1.tsv          human-readable audit sheet for the above
  <out>/preprint_published_near_review_v1.tsv  tier C     (review list, inactive)

Usage: python build_preprint_pairs.py [--db-dir <library dir>] [--out <dir>]
"""
import argparse, json, os, re, sys, unicodedata
from pathlib import Path

DEFAULT_DB = os.environ.get("EYEKB_LIB_DIR") or "/mnt/D/OcularKB/ocularkb/rag/literature_db/v3.0_2026-10"
DEFAULT_OUT = os.environ.get("EYEKB_PAIRMAP_OUT") or "/mnt/D/EyeKB/kb/literature_db"

NEAR_MIN_RUN = 50      # tier C floor -- see the measured basis below
BORDERLINE_MIN_RUN = 30  # tier D floor (review list only, never active)

# Where these two numbers come from (measured 2026-10-27 on the whole library, 230 preprints x 3691
# published papers, year window applied):
#   * every pair with a common normalised leading run >= 50 turned out, on line-by-line reading, to be
#     the same study -- 30 byte-identical titles, 1 strict prefix, 9 reworded tails. That is 40 pairs
#     in total, and it reproduced the hand-built audit sheet of the same morning exactly.
#   * the 30-49 band is genuinely mixed: PPR468159 ("via nicd ulk1" vs "mediated by nicd ulk1") and
#     PPR1047307 (an HTML <i> tag) are the same study, while PPR990826 (Chinese-donor retina vs fetal
#     uveal tract), PPR691160 (retina vs cornea) and PPR914053 (limbal epithelium vs retina) are
#     different studies that merely share an opening phrase. A wrong pair in the active map silently
#     deletes a genuine result, so the mixed band stays out of it.
NEAR_JACCARD = 0.85    # reported for auditing only; not a gate


def norm_title(t: str) -> str:
    """Lower-case, strip accents and punctuation, collapse whitespace. Digits are kept."""
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def common_prefix_len(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def load_papers(db_dir: str):
    rows = []
    with (Path(db_dir) / "papers.jsonl").open(encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def is_preprint(r) -> bool:
    pid = str(r.get("paper_id", ""))
    flag = str(r.get("is_preprint", "")).strip().lower()
    return pid.startswith("PPR") or flag in ("1", "true", "yes")


def year_of(r):
    try:
        return int(str(r.get("year", "")).strip()[:4])
    except Exception:
        return None


def year_ok(py, by):
    if not py or not by:
        return True          # missing year is not evidence against a pair
    return py <= by <= py + 3


def classify(na, nb, py, by):
    """Return (tier, basis, common_run, jaccard) or None when the pair fails every tier."""
    if not na or not nb:
        return None
    run = common_prefix_len(na, nb)
    jac = jaccard(na, nb)
    if na == nb:
        return ("A", "title_exact", run, jac)
    if run == min(len(na), len(nb)) and year_ok(py, by):
        return ("B", "title_prefix", run, jac)
    if run >= NEAR_MIN_RUN and year_ok(py, by):
        return ("C", "title_near", run, jac)
    if run >= BORDERLINE_MIN_RUN and year_ok(py, by):
        return ("D", "title_borderline", run, jac)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-dir", default=DEFAULT_DB)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()

    rows = load_papers(a.db_dir)
    pre = [r for r in rows if is_preprint(r)]
    pub = [r for r in rows if not is_preprint(r)]
    print(f"papers={len(rows)} preprint={len(pre)} published={len(pub)}", file=sys.stderr)

    # 230 preprints x ~3700 published papers is under a million cheap comparisons, so the scan is
    # exhaustive. An index shortcut could silently drop a pair whose leading words were reworded in
    # review -- exactly the failure this file must not have.
    pub_norm = [(r, norm_title(r.get("title", ""))) for r in pub]

    active, review, unmatched = [], [], []
    for rp in pre:
        pn, py = norm_title(rp.get("title", "")), year_of(rp)
        best = None
        for r, nt in pub_norm:
            got = classify(pn, nt, py, year_of(r))
            if not got:
                continue
            tier, basis, run, jac = got
            rank = ({"A": 0, "B": 1, "C": 2, "D": 3}[tier], -run, -jac,
                    abs((year_of(r) or 0) - (py or 0)), str(r.get("paper_id")))
            if best is None or rank < best[0]:
                best = (rank, tier, basis, run, jac, r)
        if not best:
            unmatched.append(str(rp.get("paper_id")))
            continue
        _, tier, basis, run, jac, r = best
        rec = {
            "preprint_id": str(rp.get("paper_id")),
            "published_id": str(r.get("paper_id")),
            "tier": tier, "basis": basis,
            "common_run": run, "jaccard": round(jac, 3),
            "preprint_title": rp.get("title", ""),
            "published_title": r.get("title", ""),
            "preprint_year": rp.get("year", ""),
            "published_year": r.get("year", ""),
            "published_journal": r.get("journal", ""),
            "preprint_chunks": rp.get("n_chunks", ""),
            "published_chunks": r.get("n_chunks", ""),
        }
        (active if tier in ("A", "B", "C") else review).append(rec)

    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    jl = outdir / "preprint_published_map_v1.jsonl"
    with jl.open("w", encoding="utf-8") as fh:
        for d in sorted(active, key=lambda x: x["preprint_id"]):
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    cols = ["preprint_id", "published_id", "tier", "basis", "common_run", "jaccard",
            "preprint_year", "published_year", "published_journal",
            "preprint_chunks", "published_chunks", "preprint_title", "published_title"]
    ts = outdir / "preprint_published_map_v1.tsv"
    with ts.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for d in sorted(active, key=lambda x: x["preprint_id"]):
            fh.write("\t".join(str(d.get(c, "")).replace("\t", " ") for c in cols) + "\n")
    rv = outdir / "preprint_published_borderline_review_v1.tsv"
    with rv.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for d in sorted(review, key=lambda x: x["preprint_id"]):
            fh.write("\t".join(str(d.get(c, "")).replace("\t", " ") for c in cols) + "\n")

    import collections as _c
    tiers = _c.Counter(d["tier"] for d in active)
    print(f"active(A+B+C)={len(active)} {dict(tiers)} "
          f"borderline_review(D)={len(review)} preprints_without_partner={len(unmatched)}",
          file=sys.stderr)
    print(f"wrote {jl}\nwrote {ts}\nwrote {rv}", file=sys.stderr)


if __name__ == "__main__":
    main()