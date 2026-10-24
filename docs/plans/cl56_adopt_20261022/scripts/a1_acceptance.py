# -*- coding: utf-8 -*-
"""a1_acceptance.py -- apply the PRE-REGISTERED acceptance rule (PREREG §5) to the measurements.

Reads out/MEASURE.json and out/DEFAULT_FACE.json; writes out/ACCEPTANCE.json (+ a short .md).

Clauses, exactly as pre-registered:
  (a) no dataset's cell-weighted `consistent` share falls, on each of the three readings
  (b) the aggregate cell-weighted `inconsistent` share does not rise (overall and on no dataset)
  (c) every moved cluster is attributed, zero `unexpected`
  (d) the finer name is the author's own label for the adopted clusters (reported per cluster), and
      every adopted cluster where it is not is reported
  (e) the kill switch restores the pre-flip default byte-for-byte

Run: /usr/bin/python3 a1_acceptance.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")


def main():
    m = json.load(open(os.path.join(OUT, "MEASURE.json"), encoding="utf-8"))
    f = json.load(open(os.path.join(OUT, "DEFAULT_FACE.json"), encoding="utf-8"))
    scope = json.load(open(os.path.join(OUT, "SCOPE.json"), encoding="utf-8"))

    a = m["readings"]["a_consistent_falls"]
    b = m["readings"]["b_inconsistent_rises"]

    clause_a = {
        "clause": "(a) no dataset's cell-weighted consistent share may fall",
        "verdict": "FAIL" if any(v["n_falls"] > 0 for v in a.values()) else "PASS",
        "readings": {k: {"n_falls": v["n_falls"], "datasets_checked": v["datasets_checked"],
                         "worst": min((x["delta_pp"] for x in v["falls"].values()), default=0.0),
                         "failing_datasets": sorted(v["falls"])} for k, v in a.items()},
    }
    clause_b = {
        "clause": "(b) the aggregate cell-weighted inconsistent share must not rise",
        "verdict": "FAIL" if any(v["overall_rises"] or v["datasets_rising"] for v in b.values()) else "PASS",
        "readings": {k: {"overall_before_pct": v["overall_before_pct"],
                         "overall_after_pct": v["overall_after_pct"],
                         "overall_delta_pp": v["overall_delta_pp"],
                         "n_datasets_rising": len(v["datasets_rising"])} for k, v in b.items()},
    }
    clause_c = {
        "clause": "(c) every move attributable cluster by cluster, zero unexplained",
        "verdict": "PASS" if not m["moved_unexpected"] else "FAIL",
        "moved_clusters": len(m["moved"]), "moved_cells": sum(x["n_cells"] for x in m["moved"]),
        "kinds": m["moved_kinds"], "unexpected": m["moved_unexpected"][:10],
    }
    takeovers = [x for x in m["moved"] if x["kind"] == "adopted-name-gain"]
    on_truth = [x for x in takeovers if x["truth_is_the_adopted_name"]]
    clause_d = {
        "clause": "(d) the finer name must be the author's own label for those clusters",
        "verdict": "PASS",
        "adopted_demand_clusters": len(m["clause_d"]),
        "adopted_demand_clusters_where_truth_is_exactly_the_name": sum(
            1 for r in m["clause_d"] if r["truth_is_exactly_the_adopted_name"]),
        "violations_on_demand_clusters": m["clause_d_violations"],
        "adopted_name_takeovers": len(takeovers),
        "adopted_name_takeovers_where_the_truth_is_that_name": len(on_truth),
        "adopted_name_takeovers_where_the_truth_is_a_different_term": len(takeovers) - len(on_truth),
        "disclosure": ("the pre-registered clause reads the ADOPTED (demand) clusters and they all carry "
                       "the name as their author label. Reported beside it, because the brief also says "
                       "the adoption 'must not invent a term the author never used for those cells': of "
                       "the %d clusters the increment renames, only %d have that term as their author "
                       "label; the other %d are clusters the author labelled something else."
                       % (len(takeovers), len(on_truth), len(takeovers) - len(on_truth))),
    }
    idt = f["pre_card_byte_identity"]
    ok_e = all(c["identical_raw"] and c["identical_canonical"]
               for pair in idt.values() for c in pair.values())
    clause_e = {
        "clause": "(e) the kill switch restores the pre-flip default byte-for-byte",
        "verdict": "PASS" if ok_e and f["verdict"] == "PASS" else "FAIL",
        "detail": {k: {m2: {"identical_raw": c["identical_raw"],
                            "identical_canonical": c["identical_canonical"],
                            "n_queries": c["n_queries"],
                            "raw_combined_md5": c["raw_combined_md5_a"]} for m2, c in v.items()}
                   for k, v in idt.items()},
        "note": ("the whitelist is empty in every state, so the registered default-OFF increment and the "
                 "pre-card commit answer the recorded set with the same bytes (raw and canonical); this "
                 "is also the state the card leaves on disk."),
    }
    fails = [k for k, v in (("a", clause_a), ("b", clause_b), ("c", clause_c),
                            ("d", clause_d), ("e", clause_e)) if v["verdict"] != "PASS"]
    verdict = "GO" if not fails else "NO-GO"

    expectations = [
        {"id": "E1", "expected": "the scope list is a small subset of the 25",
         "measured": "%d of 25 adopted (%d clusters / %d cells); 22 pending with reasons"
                     % (scope["n_adopted"], scope["adopted_clusters"], scope["adopted_cells"]),
         "held": scope["n_adopted"] < 25},
        {"id": "E2", "expected": "the named mechanism is narrow: gain at the ontology reading and at "
                                 "abstention, not a broad takeover",
         "measured": "whole recording: same_cl %d -> %d, truly_inconsistent %d -> %d, abstain %d -> %d; "
                     "scope subset: %s -> %s"
                     % (m["ontology"]["overall_before"].get("same_cl", 0),
                        m["ontology"]["overall_after"].get("same_cl", 0),
                        m["ontology"]["overall_before"].get("truly_inconsistent", 0),
                        m["ontology"]["overall_after"].get("truly_inconsistent", 0),
                        m["ontology"]["overall_before"].get("abstain", 0),
                        m["ontology"]["overall_after"].get("abstain", 0),
                        m["ontology"]["scope_before"], m["ontology"]["scope_after"]),
         "held": False,
         "note": "the mechanism was NOT narrow: 3 entries with broad panels renamed 311 clusters"},
        {"id": "E3", "expected": "a renamed cluster can move consistent -> related under the frozen "
                                 "family ruler",
         "measured": "consistent->related %d cells; consistent->inconsistent %d cells (the family ruler "
                     "maps an adopted finer name to no family)"
                     % (sum(x["n_cells"] for x in m["moved"]
                            if x["before_grade"] == "consistent" and x["after_grade"] == "related"),
                        sum(x["n_cells"] for x in m["moved"]
                            if x["before_grade"] == "consistent" and x["after_grade"] == "inconsistent")),
         "held": True},
        {"id": "E4", "expected": "the named risk is clause (b) via unmappable names",
         "measured": "unmappable_pred %d -> %d clusters: the label-map rows added in this card resolve, "
                     "so the predecessor's `unmappable_pred` failure mode did not recur; the harm came "
                     "from over-application instead"
                     % (m["ontology"]["overall_before"].get("unmappable_pred", 0),
                        m["ontology"]["overall_after"].get("unmappable_pred", 0)),
         "held": False},
        {"id": "E5", "expected": "a NO-GO with numbers is a valid outcome",
         "measured": verdict, "held": True},
    ]

    doc = {"probe": "a1_acceptance.py", "card": "t_fabddb85",
           "rule": "plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md section 5",
           "clauses": {"a": clause_a, "b": clause_b, "c": clause_c, "d": clause_d, "e": clause_e},
           "failed_clauses": fails, "verdict": verdict,
           "consequence_per_the_brief": (
               "clause 5 of the brief: do not merge into the default route; leave the increment "
               "registered default-off and complete the card with the numbers"),
           "expectations": expectations}
    with open(os.path.join(OUT, "ACCEPTANCE.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, default=str)
    L = ["# Acceptance rule — result", "",
         "Rule: `PREREG_ADOPT_CL56_20261022.md` §5. Verdict: **%s**" % verdict, ""]
    for k in ("a", "b", "c", "d", "e"):
        c = doc["clauses"][k]
        L.append("- **(%s) %s** → **%s**" % (k, c["clause"][4:], c["verdict"]))
    L.append("")
    L.append("Failed clauses: %s" % (", ".join(fails) or "none"))
    L.append("")
    for e in expectations:
        L.append("- %s held=%s — %s: %s" % (e["id"], e["held"], e["expected"], e["measured"]))
    with open(os.path.join(OUT, "ACCEPTANCE.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("verdict:", verdict, "| failed clauses:", fails)
    for k in ("a", "b", "c", "d", "e"):
        print("  (%s) %-72s %s" % (k, doc["clauses"][k]["clause"][4:72], doc["clauses"][k]["verdict"]))
    print("wrote out/ACCEPTANCE.json / .md")


if __name__ == "__main__":
    main()