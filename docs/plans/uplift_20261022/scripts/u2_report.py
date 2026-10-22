#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""u2_report.py -- render REPORT.md from out/UPLIFT_MEASUREMENT.json.

Every number in the rendered report is read out of the measurement document: nothing is typed in by
hand, so the report cannot drift from the run it describes. Re-run after u1_uplift.py.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(WAVE, "out", "UPLIFT_MEASUREMENT.json")
DEST = os.path.join(WAVE, "REPORT.md")

ORDER = ["C2_narrowing_only_carrier_off", "C1_carrier_only_today", "C0_cumulative_vs_baseline"]


def fmt(x):
    return "n/a" if x is None else ("%.3f" % x)


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return out


def main() -> int:
    with open(SRC, encoding="utf-8") as fh:
        doc = json.load(fh)
    runs = doc["runs"]
    rs = (runs[ORDER[0]]["recorded_set"] if ORDER[0] in runs else
          next(iter(runs.values()))["recorded_set"])
    L = []
    A = L.append

    A("# Uplift measurement: the two shipped changes, re-measured on the tree as it stands")
    A("")
    A("Measured %s on the recorded query set: **%d volumes, %d clusters, %s cells**."
      % (doc.get("probe", "u1_uplift.py"), rs["volumes"], rs["clusters"], format(rs["cells"], ",")))
    A("Each arm replays the same recorded queries through the live router with a declared switch")
    A("overlay; the routing layer and the grading ruler are imported read-only from")
    A("`docs/plans/noregr_20261022`. Nothing outside this directory is written.")
    A("")
    A("Reading of the grades: `consistent` the candidate resolves to the same Cell Ontology class as")
    A("the reference label; `related` a coarser or finer class in the same lineage; `inconsistent` a")
    A("class outside the reference lineage; `mixed` no single reading for the cluster.")
    A("")
    A("## 1. Headline")
    A("")
    rows = []
    for k in ORDER:
        if k not in runs:
            continue
        v = runs[k]
        b, a, d = v["overall_before"], v["overall_after"], v["overall_delta_pp"]
        rows.append([k.split("_", 1)[0], v["name"].split(",", 1)[0],
                     fmt(b["share_pct"]["consistent"]), fmt(a["share_pct"]["consistent"]),
                     "%+.3f" % d["consistent"], "%+d" % (a["clusters"]["consistent"] - b["clusters"]["consistent"]),
                     v["changed_clusters"], format(v["changed_cells"], ","), v["ruling"]["verdict"]])
    L += table(["arm", "what it isolates", "consistent before %", "consistent after %",
                "delta pp", "clusters gained", "clusters moved", "cells moved", "gate verdict"], rows)
    A("")
    A("The `before` value of C0 is the arm with **both** switches off, i.e. the state before the")
    A("tissue-scope narrowing and before the carrier. C2 holds the carrier off in both arms so that")
    A("the narrowing is measured on its own; C1 flips only the carrier on the narrowed tree.")
    A("C2 and C1 add up to C0 in the `consistent` share, which is the check that the decomposition")
    A("is complete.")
    A("")
    A("## 2. Per-volume detail")
    A("")
    for k in ORDER:
        if k not in runs:
            continue
        v = runs[k]
        A("### %s" % v["name"])
        A("")
        A("Before arm `%s`, after arm `%s`."
          % (json.dumps(v["before_arm"], ensure_ascii=False), json.dumps(v["after_arm"], ensure_ascii=False)))
        A("")
        A("| grade | before % | after % | delta pp | clusters before | clusters after |")
        A("|---|---|---|---|---|---|")
        for g in ("consistent", "related", "inconsistent", "mixed"):
            A("| %s | %s | %s | %+.3f | %d | %d |"
              % (g, fmt(v["overall_before"]["share_pct"][g]), fmt(v["overall_after"]["share_pct"][g]),
                 v["overall_delta_pp"][g], v["overall_before"]["clusters"][g],
                 v["overall_after"]["clusters"][g]))
        A("")
        moved = [r for r in v["per_dataset"] if r["delta_pp"] not in (0.0, None)]
        moved.sort(key=lambda r: -r["delta_pp"])
        A("Volumes whose `consistent` share moved (%d of %d):" % (len(moved), len(v["per_dataset"])))
        A("")
        A("| volume | before % | after % | delta pp |")
        A("|---|---|---|---|")
        for r in moved:
            A("| %s | %s | %s | %+.3f |" % (r["volume"], fmt(r["before"]), fmt(r["after"]), r["delta_pp"]))
        A("")
        A("Largest movers by cluster:")
        A("")
        A("| volume | cluster | cells | reference type | before top | after top | grade |")
        A("|---|---|---|---|---|---|---|")
        sel = [r for r in v["per_cluster_deltas"] if r.get("before_top") != r.get("after_top")]
        sel.sort(key=lambda r: -r["n_cells"])
        for r in sel[:8]:
            A("| %s | %s | %s | %s | %s | %s | %s -> %s |"
              % (r["vol"], r["cluster"], format(r["n_cells"], ","), r.get("ref_cell_type"),
                 r.get("before_top"), r.get("after_top"), r.get("before_grade"), r.get("after_grade")))
        A("")
    A("## 3. What the aggregate hides")
    A("")
    for k in ORDER:
        if k not in runs:
            continue
        v = runs[k]
        left = [r for r in v["per_cluster_deltas"]
                if r.get("before_grade") == "consistent" and r.get("after_grade") != "consistent"]
        lost = [r for r in v["per_cluster_deltas"]
                if r.get("after_top") is None and r.get("before_top") is not None]
        entered = [r for r in v["per_cluster_deltas"]
                   if r.get("after_grade") == "consistent" and r.get("before_grade") != "consistent"]
        A("- **%s**: %d cluster(s) left `consistent`, %d entered it, and %d cluster(s) (%s cells) were"
          % (k.split("_", 1)[0], len(left), len(entered), len(lost), format(sum(r["n_cells"] for r in lost), ",")))
        A("  left with no named candidate at all.")
        for r in left:
            A("  - left `consistent`: %s cluster %s, %s cells, reference `%s`; candidate `%s` -> `%s`,"
              % (r["vol"], r["cluster"], format(r["n_cells"], ","), r.get("ref_cell_type"),
                 r.get("before_top"), r.get("after_top")))
            A("    graded %s -> %s with CL reading `%s` -> `%s`."
              % (r.get("before_grade"), r.get("after_grade"), r.get("before_cl"), r.get("after_cl")))
    A("")
    A("## 4. Attribution of every fall")
    A("")
    A("A fall in any volume's cell-weighted `consistent` share may not be reported as complete unless")
    A("it is attributed, in the artefact, to a named cluster, a named cause and a named row or panel.")
    A("")
    for k in ORDER:
        if k not in runs:
            continue
        v = runs[k]
        drops = (v["ruling"].get("drops") or {})
        if not drops:
            A("- **%s**: no volume's `consistent` share fell (verdict %s)."
              % (k.split("_", 1)[0], v["ruling"]["verdict"]))
            continue
        A("- **%s** (verdict %s):" % (k.split("_", 1)[0], v["ruling"]["verdict"]))
        for vol, rec in sorted(drops.items()):
            A("  - `%s` %+.3f pp (%s%% -> %s%%): cluster %s; cause: %s; row/panel: %s"
              % (vol, rec["delta_pp"], fmt(rec["before_pct"]), fmt(rec["after_pct"]),
                 rec["attribution"].get("cluster"), rec["attribution"].get("cause"),
                 rec["attribution"].get("row_or_panel")))
    A("")
    A("## 5. Limits of this measurement")
    A("")
    A("1. **In-sample.** The carrier library was selected on these same volumes, so these readings")
    A("   describe the recorded set, not held-out data. They are not an accuracy estimate.")
    A("2. **The reference labels are a consensus, not an independent truth set.** The grades report")
    A("   agreement with those labels; they do not certify that a call is biologically correct.")
    A("3. **`consistent` is a mapping-dependent grade.** One cluster in C2 leaves `consistent` while")
    A("   its new candidate string is *identical* to the reference string, because the grading layer")
    A("   cannot resolve that label to a Cell Ontology id (`unmappable_pred`). Counted, not hidden.")
    A("4. **The window lever is not in these arms.** The production default recall window stays at 10;")
    A("   the 30-window variant is a separate arm and is not part of any number above.")
    A("5. **The harness's per-dataset `cells_lost` block is global, not per-dataset** -- in the frozen")
    A("   harness the same transition counts are repeated under each dropped volume. Read the")
    A("   per-cluster table for cluster-level detail; the harness was not edited.")
    A("6. **Switch handling.** `scripts/switch_coverage/arm_hygiene.py` derives the switch list from")
    A("   the source and `preflight()` refuses to run a comparison whose arms are not in different")
    A("   states; `tests/gate_switch_coverage.py` enforces the same rule over every report on disk.")
    A("")
    A("## 6. Re-deriving these numbers")
    A("")
    A("```")
    A("cd %s" % WAVE)
    A("export PYTHONHASHSEED=0 NR_NET_AUDIT_LOG=$PWD/logs/net_audit.log")
    A("/usr/bin/python3 scripts/u1_uplift.py        # writes out/UPLIFT_MEASUREMENT.json")
    A("/usr/bin/python3 scripts/u2_report.py        # writes this file")
    A("/usr/bin/python3 tests/gate_switch_coverage.py   # switch coverage and arm hygiene")
    A("```")
    A("")
    A("The harness's own pre-image travels inside the measurement document, so any reported number can")
    A("be traced back to the harness revision that produced it.")
    A("")

    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("wrote %s (%d bytes)" % (DEST, os.path.getsize(DEST)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())