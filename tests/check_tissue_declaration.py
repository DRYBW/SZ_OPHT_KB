#!/usr/bin/env python3
"""Checker for the pre-registered tissue-declaration rule.

The rule (docs/TISSUE_DECLARATION_RULE.md) says: the tissue handed to query_marker for a dataset
is derived from that dataset's OWN metadata — before any comparison runs — and is not chosen by
looking at the score. This script makes that checkable.

What it checks, per dataset row of a declaration table
  C1 VOCABULARY   the declared tissue is in this repository's tissue dictionary
                  (enumerated mechanically, the same way pipeline/run_pipeline.py does)
  C2 DERIVATION   the declared tissue equals what the rule derives from the dataset's source
                  labels and the frozen crosswalk (kb/baselines/_tissue_source_label_crosswalk_v1.json):
                  one mapped label -> that tissue; several -> the coarsest dictionary name that
                  covers all of them; none -> MIXED_CONTENT, where no single-tissue declaration is
                  admissible and the dataset has to be scored per source-tissue partition
  C3 PREREG       the row says where the declaration came from and when it was frozen
                  (`declared_from`, `frozen_at`): a declaration that is not traceable to the
                  dataset's own metadata, or that carries no freeze point, is not pre-registered
  C4 NO_POSTHOC   a declaration that disagrees with the rule is only reported, never accepted:
                  the row fails unless the rule's own outcome is MIXED_CONTENT (i.e. unless the
                  dataset is genuinely underdetermined) — so running both declarations and
                  keeping the better number cannot pass this check

Declaration table (TSV, one row per dataset; '#' comment lines allowed)
  dataset_id        stable identifier of the dataset
  source_labels     the tissue labels found in the dataset's OWN metadata, ';'-separated
  declared_tissue   the value handed to query_marker (MIXED_CONTENT when the rule says so)
  declared_from     the metadata field or the pre-registration document the declaration comes from
  frozen_at         when the declaration was frozen (date or commit), i.e. before the comparison

Usage (from the repository root)
  python3 tests/check_tissue_declaration.py --table declarations.tsv
  python3 tests/check_tissue_declaration.py --explain "retina;lens"        # derive, do not judge
  python3 tests/check_tissue_declaration.py --selftest                     # the rule's own cases

Exit codes: 0 = every row admissible and pre-registered
            1 = at least one row fails (each failure names its check and the row)
            2 = usage error / the table is missing
            3 = the rule's inputs are not on disk (crosswalk or dictionary): no judgement is made
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "kb" / "baselines" / "_tissue_source_label_crosswalk_v1.json"
MIXED = "MIXED_CONTENT"


def tissue_dictionary() -> set:
    """This repository's tissue dictionary, enumerated the way the pipeline enumerates it:
    kb/baselines/*.json entries (excluding the private _-prefixed, fetal and retina__ layers)
    plus the tissue fields of kb/priors/{composition,disease}/*.json."""
    tis = set()
    d = ROOT / "kb" / "baselines"
    if not d.is_dir():
        return tis
    for p in d.glob("*.json"):
        if not p.name.startswith(("_", "fetal", "retina__")):
            tis.add(p.stem)
    for sub in ("composition", "disease"):
        d2 = ROOT / "kb" / "priors" / sub
        if d2.is_dir():
            for p in d2.glob("*.json"):
                try:
                    e = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                t = (e.get("tissue") or "").strip().lower()
                if t:
                    tis.add(t)
    return tis


def load_crosswalk():
    return json.loads(CROSSWALK.read_text(encoding="utf-8"))


def derive(labels, xwalk, vocab):
    """The rule, applied. -> (outcome, detail). outcome is a dictionary name or MIXED_CONTENT."""
    rows = xwalk.get("source_labels") or {}
    covers = xwalk.get("covers") or {}
    unmapped = [l for l in labels if l not in rows]
    if unmapped:
        return "UNDERDETERMINED", ("unmapped source label(s): " + ", ".join(sorted(unmapped))
                                   + " (add a reviewed crosswalk row, or report the dataset as "
                                     "underdetermined: the rule never guesses)")
    mapped = sorted({rows[l]["kb_tissue"] for l in labels})
    off_vocab = [t for t in mapped if vocab and t not in vocab]
    if off_vocab:
        return "UNDERDETERMINED", ("crosswalk target(s) not in the tissue dictionary: "
                                   + ", ".join(sorted(off_vocab)))
    if len(mapped) == 1:
        return mapped[0], "one dictionary name for every source label: " + mapped[0]
    holders = [t for t, r in covers.items() if set(mapped) <= set(r.get("covers_dictionary_names") or [])]
    if not holders:
        return MIXED, ("source labels span " + ", ".join(mapped)
                       + ": no dictionary name covers them, so no single-tissue declaration is "
                         "admissible — score the dataset per source-tissue partition, or state "
                         "why it is out of scope for a single number")
    holders.sort(key=lambda t: (len(covers[t].get("covers_dictionary_names") or []), t))
    return holders[0], ("covered by the coarsest dictionary name " + holders[0]
                        + " (of " + ", ".join(holders) + ")")


def read_table(p: Path) -> list:
    lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    if not lines:
        return []
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, ln.split("\t"))) for ln in lines[1:]]


REQUIRED_COLUMNS = ["dataset_id", "source_labels", "declared_tissue", "declared_from", "frozen_at"]


def judge_row(row, xwalk, vocab):
    errs = []
    did = row.get("dataset_id", "?")
    labels = [l.strip() for l in (row.get("source_labels") or "").split(";") if l.strip()]
    declared = (row.get("declared_tissue") or "").strip()
    if not labels:
        return [f"{did}: C2 DERIVATION: no source_labels (the declaration has no input)"]
    outcome, detail = derive(labels, xwalk, vocab)
    if vocab and declared and declared not in vocab and declared != MIXED:
        errs.append(f"{did}: C1 VOCABULARY: declared '{declared}' is not in the tissue dictionary")
    if declared != outcome:
        errs.append(f"{did}: C2 DERIVATION: declared '{declared}' but the rule derives '{outcome}'"
                    f" ({detail})")
    if outcome == MIXED and declared != MIXED:
        errs.append(f"{did}: C4 NO_POSTHOC: a single-tissue declaration for a source-label set no"
                    f" dictionary name covers (the rule's outcome is {MIXED})")
    if not (row.get("declared_from") or "").strip():
        errs.append(f"{did}: C3 PREREG: declared_from is empty (where did the declaration come from?)")
    if not (row.get("frozen_at") or "").strip():
        errs.append(f"{did}: C3 PREREG: frozen_at is empty (a declaration has to be frozen before"
                    " the comparison it is used in)")
    return errs


SELFTEST = [
    ("one label", ["retina"], "retina"),
    ("coarser cover", ["cornea", "conjunctiva"], "ocular_surface"),
    ("whole eye", ["retina", "lens", "iris", "ciliary body"], MIXED),
    ("unmapped", ["eye"], "UNDERDETERMINED"),
    ("organoid", ["retinal organoid"], "retina"),
]


def selftest(xwalk, vocab) -> int:
    bad = 0
    for name, labels, want in SELFTEST:
        got, detail = derive(labels, xwalk, vocab)
        ok = got == want
        bad += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + f"selftest/{name}: {labels} -> {got} (want {want})")
        if not ok:
            print("      ", detail)
    print(f"selftest: {len(SELFTEST) - bad}/{len(SELFTEST)} as specified")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default="")
    ap.add_argument("--crosswalk", default=str(CROSSWALK))
    ap.add_argument("--explain", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    cw = Path(a.crosswalk)
    if not cw.exists():
        print(f"NO JUDGEMENT: the rule's crosswalk is not on disk ({cw}).")
        return 3
    xwalk = json.loads(cw.read_text(encoding="utf-8"))
    vocab = tissue_dictionary()
    if not vocab:
        print("NO JUDGEMENT: the tissue dictionary could not be enumerated from this checkout.")
        return 3

    if a.explain:
        labels = [l.strip() for l in a.explain.split(";") if l.strip()]
        outcome, detail = derive(labels, xwalk, vocab)
        print(f"labels      {labels}")
        print(f"declaration {outcome}")
        print(f"because     {detail}")
        return 0

    if a.selftest:
        return selftest(xwalk, vocab)

    if not a.table:
        print("usage: check_tissue_declaration.py --table declarations.tsv | --explain 'a;b' | --selftest")
        return 2
    t = Path(a.table)
    if not t.exists():
        print(f"FAIL: declaration table not found: {t}")
        return 2
    rows = read_table(t)
    if not rows:
        print(f"FAIL: no data rows in {t}")
        return 2
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing_cols:
        print(f"FAIL: the table's first non-comment line must be its header; missing column(s): "
              f"{', '.join(missing_cols)}")
        print("  expected columns: " + "\t".join(REQUIRED_COLUMNS))
        return 2
    errs = []
    for r in rows:
        errs += judge_row(r, xwalk, vocab)
    print(f"[tissue-declaration] rows={len(rows)} failures={len(errs)}")
    for e in errs:
        print("  FAIL " + e)
    if not errs:
        print("  every row: declared tissue derivable from the dataset's own metadata, and frozen "
              "before the comparison it is used in")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())