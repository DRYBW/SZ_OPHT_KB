#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 4 — apply the query-surface fix for defect 2 (the development_stage fall-through).

Every replacement asserts that its anchor occurs exactly once, so a silent no-op or a
double-apply aborts instead of producing a half-edited file. Run from anywhere; the target is
fixed to the repo path.

  python3 c1_apply_stage_fix.py --check     # report what would change, write nothing
  python3 c1_apply_stage_fix.py             # apply
"""
import argparse
import pathlib
import sys

CORE = pathlib.Path("/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py")
SRV = pathlib.Path("/home/ubuntu/EYEKB_REPO/mcp_server/server.py")

# ---------------------------------------------------------------- eyekb_core.py
CONSTANTS = '''# KB2c developmental-stage contract at the query surface (ruling Q1, red line 2).
# The four level names are fetal / adult / developing / unknown. "" means "not specified" and
# resolves to the adult main file; the documented synonyms fold onto a level and say so; every
# other literal -- organoid, organoid_Day30, a misspelling -- resolves to the unknown tier with a
# flag naming it. The builder side has implemented this rule since KB2c
# (scripts/baselines/build_baselines.py:classify_uberon -> "organoid -> unknown + flag", and the
# stage_axis block shipped with every baseline carries the same unknown_rule); the query path used
# to fall through to the adult baseline instead, which is the silent adult assignment the ruling
# forbids.
STAGE_TIERS = ("fetal", "adult", "developing", "unknown")
STAGE_FOLD = {"any": "adult", "postnatal": "developing"}
STAGE_FOLD_RULE = {
    "adult": 'documented synonym: "any" = the main-file caliber (adult-only entries)',
    "developing": "postnatal -> developing (KB2c ruling Q1 mapping)",
}
STAGE_UNRECOGNISED_RULE = ("unrecognised development_stage literal -> the unknown tier (KB2c ruling "
                           "Q1: organoid is neither fetal tissue nor adult; red line 2: no stage is "
                           "ever silently assigned to adult)")
STAGE_ACCEPTED_LITERALS = ("", "fetal", "adult", "developing", "unknown", "postnatal", "any")


def _stage_literal_note(requested, tier, recognised, rule):
    """Disclosure block for a development_stage literal that was not itself a contract tier name.

    It names the caller's literal, whether it is a recognised spelling, the tier it resolved to and
    the accepted spellings, so a caller can see that its input was folded rather than matched. It is
    disclosure only: it changes no row, no interval and no name.
    """
    return {"requested": requested, "recognised_literal": recognised, "tier": tier,
            "flag": "stage_literal_folded" if recognised
                    else "unrecognised_development_stage_literal",
            "accepted_literals": list(STAGE_ACCEPTED_LITERALS), "rule": rule}


'''

OLD_PROLOGUE = '''    want = (development_stage or "").strip().lower()
    if want == "postnatal":
        want = "developing"
    if want in ("fetal", "developing"):
        return _fetal_concept_response(want)
'''

NEW_PROLOGUE = '''    requested = development_stage or ""
    want = requested.strip().lower()
    stage_literal = None        # disclosure block; set only when the literal was not a tier name
    if want in STAGE_FOLD:
        want = STAGE_FOLD[want]
        stage_literal = _stage_literal_note(requested, want, True, STAGE_FOLD_RULE[want])
    elif want and want not in STAGE_TIERS:
        # KB2c red line 2: an unrecognised literal must not reach the adult baseline by falling
        # through -- it resolves to the unknown tier, and says so.
        want = "unknown"
        stage_literal = _stage_literal_note(requested, "unknown", False, STAGE_UNRECOGNISED_RULE)
    if want in ("fetal", "developing"):
        resp = _fetal_concept_response(want)
        if stage_literal:
            resp["stage_literal"] = stage_literal
        return resp
'''

OLD_UNKNOWN = '''    if want == "unknown":
        unk = [c for c in cands if str(c[1].get("organism_stage", "")).startswith("unknown")]
        if not unk:
            return {"mode": "no_unknown_stage_entry", "request_stage": "unknown",
                    "note": (f"this query has no organism_stage=unknown tier entry (species={species!r} "
                             f"tissue={tissue!r}); the unknown-tier source list is in "
                             f"kb/baselines/_STAGE_DISCLOSURE.md"),
                    "disclosure_file": str(BASELINES_DIR / "_STAGE_DISCLOSURE.md")}
        cands = unk
'''

NEW_UNKNOWN = '''    if want == "unknown":
        unk = [c for c in cands if str(c[1].get("organism_stage", "")).startswith("unknown")]
        if not unk:
            resp = {"mode": "no_unknown_stage_entry", "request_stage": "unknown",
                    "note": (f"this query has no organism_stage=unknown tier entry (species={species!r} "
                             f"tissue={tissue!r}); the unknown-tier source list is in "
                             f"kb/baselines/_STAGE_DISCLOSURE.md"),
                    "disclosure_file": str(BASELINES_DIR / "_STAGE_DISCLOSURE.md")}
            if stage_literal:
                resp["stage_literal"] = stage_literal
            return resp
        cands = unk
'''

OLD_TAIL = '''    if (detail or "").strip().lower() in ("answer", "compact", "brief", "short"):
        return _composition_answer_view(resp)
    return resp
'''

NEW_TAIL = '''    if stage_literal:
        resp["stage_literal"] = stage_literal
    if (detail or "").strip().lower() in ("answer", "compact", "brief", "short"):
        return _composition_answer_view(resp)
    return resp
'''

OLD_KEEP = '''    keep = ("entry_id", "title", "species", "tissue", "disease", "organism_stage",
            "development_stage", "rows", "states", "fine_types", "flags", "caveats",
            "source_file", "usage_redline", "usage_scope", "inventory_status", "inventory_note",
            "baseline_status", "distribution_method", "composition_status", "stage_query_note")
'''

NEW_KEEP = '''    keep = ("entry_id", "title", "species", "tissue", "disease", "organism_stage",
            "development_stage", "rows", "states", "fine_types", "flags", "caveats",
            "source_file", "usage_redline", "usage_scope", "inventory_status", "inventory_note",
            "baseline_status", "distribution_method", "composition_status", "stage_query_note",
            "stage_literal")
'''

OLD_CORE_DOC = '''    fetal|developing = returns the transition-state concept entry (borrowing the adult bucket is
    forbidden, PI red line); unknown = only the unknown-tier entries
    (e.g. GSE158629 RPE, a source with no age column). postnatal→developing, organoid→unknown+flag
    (ruling Q1 mapping).
'''

NEW_CORE_DOC = '''    fetal|developing = returns the transition-state concept entry (borrowing the adult bucket is
    forbidden, PI red line); unknown = only the unknown-tier entries
    (e.g. GSE158629 RPE, a source with no age column).
    The literal is resolved, never guessed: "any" and "" reach the adult main file, postnatal folds
    to developing, and every other literal -- organoid, organoid_Day30, a misspelling -- resolves to
    the unknown tier (ruling Q1: organoid→unknown+flag). A folded or unrecognised literal adds a
    stage_literal block naming the literal and the tier it reached, so no stage is ever silently
    assigned to adult (red line 2).
'''

EDITS_CORE = [
    ("stage-literal constants + helper", "def _composition_answer_view(resp):", CONSTANTS + "def _composition_answer_view(resp):"),
    ("prologue + fetal route", OLD_PROLOGUE, NEW_PROLOGUE),
    ("unknown tier early return", OLD_UNKNOWN, NEW_UNKNOWN),
    ("final response", OLD_TAIL, NEW_TAIL),
    ("compact view keeps the disclosure", OLD_KEEP, NEW_KEEP),
    ("core docstring", OLD_CORE_DOC, NEW_CORE_DOC),
]

# ---------------------------------------------------------------- server.py
OLD_SRV_DOC = '''    development_stage: empty = the adult baseline (donors 18y+, non-adult donors removed row by
      row and listed in stage_disclosure / excluded_nonadult_units). "fetal" or "developing"
      returns the developmental transition entry instead -- adult numbers must not answer a
      fetal question, even for the same tissue. "unknown" = only entries whose disclosure files
      carry no age column.
'''

NEW_SRV_DOC = '''    development_stage: empty = the adult baseline (donors 18y+, non-adult donors removed row by
      row and listed in stage_disclosure / excluded_nonadult_units). "fetal" or "developing"
      returns the developmental transition entry instead -- adult numbers must not answer a
      fetal question, even for the same tissue. "unknown" = only entries whose disclosure files
      carry no age column. The literal is resolved, never guessed: "" and "any" reach the adult
      main file, "postnatal" folds to "developing", and any other literal -- "organoid" included --
      resolves to the unknown tier and adds a stage_literal block naming the literal and the tier it
      reached. No literal falls through to the adult baseline.
'''

EDITS_SRV = [("tool docstring", OLD_SRV_DOC, NEW_SRV_DOC)]


def apply(path, edits, check):
    text = path.read_text(encoding="utf-8")
    before = text
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            print(f"ABORT {path.name}: anchor {label!r} occurs {n} times (expected 1)")
            return False
        text = text.replace(old, new)
        print(f"  ok  {path.name}  {label}")
    if text == before:
        print(f"ABORT {path.name}: no change")
        return False
    if not check:
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}  ({len(before)} -> {len(text)} bytes)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ok = apply(CORE, EDITS_CORE, a.check) and apply(SRV, EDITS_SRV, a.check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())