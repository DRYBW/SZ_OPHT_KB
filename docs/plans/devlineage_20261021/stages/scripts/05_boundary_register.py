#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 5 — the observability boundary register.

One row per lineage x stage cell, with the reason it is or is not observable through the shipped
interface, and the measurement that decides it. The measurements are read from the stored probe
output (out/PROBE_RESULTS.json and out/VERDICTS.tsv) — nothing here re-runs the service, so the
register cannot disagree with what the service actually said.

Observability is defined strictly: a cell is observable when a caller holding the input that exists
for that cell gets back a response that identifies either the lineage or the stage, through a
shipped code path. Three shipped paths count, and the register names which one carried the answer:
  * the named ranking on the default route (an adult class coming back for an adult window);
  * the `off_domain` advisory on the default route (a fetal window recognised as developmental);
  * the explicit `library=retina_dev` route or the additive `state_annotations` key.
"""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = HERE / "out"
STAGES = ["fetal", "developing", "adult", "unknown"]


def main():
    probe = json.loads((OUT / "PROBE_RESULTS.json").read_text(encoding="utf-8"))
    verdicts = {r["lineage_id"]: r for r in
                csv.DictReader(open(OUT / "VERDICTS.tsv", encoding="utf-8"), delimiter="\t")}
    nodes = list(csv.DictReader(open(OUT / "NODE_KEYS.tsv", encoding="utf-8"), delimiter="\t"))
    cov = {r["lineage_id"]: r for r in
           csv.DictReader(open(OUT / "STAGE_COVERAGE.tsv", encoding="utf-8"), delimiter="\t")}
    lab = json.loads((REPO / "kb" / "markers" / "markers_cl_alignment_v2_unified.json")
                     .read_text(encoding="utf-8"))["labels"]

    # every in-house/label-map name that denotes the same ontology record as an adult class
    def names_for_class(cls, cl_id):
        names = {cls}
        for k, v in lab.items():
            if v.get("cl_id") and v.get("cl_id") == cl_id:
                names.add(k)
                names.add(v.get("cl_label") or "")
        return {n for n in names if n}

    def t1_of(rec):
        r = ((rec or {}).get("response") or {}).get("celltype_ranking") or []
        return r[0] if r else {}

    rows = []
    for n in nodes:
        if n["node_kind"] != "fetal_entry":
            continue
        lin, entry = n["lineage_id"], n["in_house_entry"]
        v = verdicts.get(lin, {})
        adults = [c for c in n["adult_counterpart_classes"].split(";") if c]
        n_fetal = int(cov[lin]["n_fetal_markers"])
        fet = probe.get(f"{lin}.fetal.K10.default") or {}
        resp = fet.get("response") or {}
        adv = bool(resp.get("off_domain"))
        dev = probe.get(f"{lin}.fetal.K10.devroute") or {}
        dev_t1 = t1_of(dev)
        sa = resp.get("state_annotations") or []
        sa_hit = next((x for x in sa if str(x.get("cell_type", "")) == entry), None)

        if n_fetal == 0:
            rows.append(dict(lineage_id=lin, cell=f"{entry} @ fetal", stage="fetal",
                             assertion_exists="N", n_markers=0, observable="N", observable_route="",
                             reason_code="no_assertion_in_corpus",
                             measurement=("no per-gene fetal marker assertion exists for this entry in the loaded "
                                          "corpus, so a caller holds no fetal window to supply"),
                             node_key=n["node_key"]))
        else:
            route = ("off_domain advisory (default route)" if adv else
                     ("state_annotations key (entry is concept_kind=state_program)" if sa_hit else
                      ("explicit library=retina_dev named ranking" if dev_t1 else "")))
            rows.append(dict(lineage_id=lin, cell=f"{entry} @ fetal", stage="fetal",
                             assertion_exists="Y", n_markers=n_fetal,
                             observable="Y" if route else "N", observable_route=route,
                             reason_code=("observable_via_shipped_path" if route
                                          else "signal_below_shipped_criterion"),
                             measurement=(f"default route: off_domain={'fired' if adv else 'absent'}, "
                                          f"top1={t1_of(fet).get('cell_type','(empty)')} "
                                          f"n_shared={t1_of(fet).get('n_shared','')}, "
                                          f"state_annotations={'yes' if sa_hit else 'no'}; explicit dev route top1="
                                          f"{dev_t1.get('cell_type','(empty)')} n_shared={dev_t1.get('n_shared','')}; "
                                          f"verdict={v.get('verdict','')}"),
                             node_key=n["node_key"]))

        rows.append(dict(lineage_id=lin, cell=f"{entry} @ developing", stage="developing",
                         assertion_exists="N", n_markers=0, observable="N", observable_route="",
                         reason_code="no_assertion_in_corpus",
                         measurement=("no per-gene developing-stage marker assertion exists in the corpus (the KB3 "
                                      "postnatal layer carries published-label percentages only), and the marker "
                                      "surface accepts no stage argument to reach one"),
                         node_key=n["node_key"]))
        rows.append(dict(lineage_id=lin, cell=f"{entry} @ unknown", stage="unknown",
                         assertion_exists="N", n_markers=0, observable="N", observable_route="",
                         reason_code="no_assertion_in_corpus",
                         measurement=("no per-gene unknown-stage marker assertion exists; organoid material is "
                                      "isolated with the unknown literal upstream and is not used as marker evidence"),
                         node_key=n["node_key"]))
        if adults:
            for cls in adults:
                an = next(x for x in nodes if x["node_kind"] == "adult_class" and x["in_house_entry"] == cls)
                a10 = probe.get(f"{lin}.adult.{cls}.K10.default") or {}
                at1 = t1_of(a10)
                names = names_for_class(cls, an["cl_id"])
                ok = str(at1.get("cell_type", "")).split("::")[-1] in names
                rows.append(dict(lineage_id=lin, cell=f"{cls} @ adult", stage="adult",
                                 assertion_exists="Y", n_markers=len(an["adult_counterpart_classes"].split(";")) and "",
                                 observable="Y" if ok else "N",
                                 observable_route="named ranking (default route)" if ok else "",
                                 reason_code=("observable_via_named_ranking" if ok
                                              else "adult_window_does_not_rank_its_own_class_first"),
                                 measurement=(f"adult-window response, default route: top1={at1.get('cell_type','(empty)')} "
                                              f"n_shared={at1.get('n_shared','')}; accepted names for this ontology "
                                              f"record: {','.join(sorted(names))}"),
                                 node_key=an["node_key"]))
        else:
            rows.append(dict(lineage_id=lin, cell="(no adult counterpart) @ adult", stage="adult",
                             assertion_exists="N", n_markers=0, observable="N", observable_route="",
                             reason_code="no_adult_counterpart_in_vocabulary",
                             measurement=("the entry's own record forbids mapping a developmental concept onto an "
                                          "adult class (separate ontology face), so this cell has no adult side"),
                             node_key=n["node_key"]))

    claimed = {c for n in nodes if n["node_kind"] == "fetal_entry"
               for c in n["adult_counterpart_classes"].split(";") if c}
    for n in nodes:
        if n["node_kind"] == "adult_class" and n["in_house_entry"] not in claimed:
            lin = n["lineage_id"] or "adult_only"
            cls = n["in_house_entry"]
            # the probe id for an adult-only class is named by the plan, not by the node table;
            # resolve it from the stored call ids so a renamed id cannot silently empty a cell
            kids = [k for k in probe if isinstance(probe[k], dict) and probe[k].get("tool") == "query_marker"
                    and k.endswith(f".adult.{cls}.K10.default")]
            a10 = probe.get(kids[0]) if kids else {}
            # the stored call ids rather than reconstructing it, so a renamed id cannot silently
            # turn a measurement into an empty cell
            kids = [k for k in probe if isinstance(probe[k], dict) and probe[k].get("tool") == "query_marker"
                    and k.endswith(f".adult.{cls}.K10.default")]
            a10 = probe.get(kids[0]) if kids else {}
            at1 = t1_of(a10)
            names = names_for_class(cls, n["cl_id"])
            ok = str(at1.get("cell_type", "")).split("::")[-1] in names
            rows.append(dict(lineage_id=lin, cell=f"{cls} @ adult", stage="adult", assertion_exists="Y",
                             n_markers="", observable="Y" if ok else "N",
                             observable_route="named ranking (default route)" if ok else "",
                             reason_code=("observable_via_named_ranking_fetal_side_absent" if ok
                                          else "adult_window_does_not_rank_its_own_class_first"),
                             measurement=(f"top1={at1.get('cell_type','(empty)')} n_shared={at1.get('n_shared','')}; "
                                          "no fetal/precursor entry in the corpus claims this class, so no fetal-side "
                                          "cell exists for it"),
                             node_key=n["node_key"]))
            for st in ("fetal", "developing", "unknown"):
                rows.append(dict(lineage_id=lin, cell=f"{cls} @ {st}", stage=st, assertion_exists="N",
                                 n_markers=0, observable="N", observable_route="",
                                 reason_code="no_precursor_entry_in_corpus",
                                 measurement=("no precursor entry claims this adult class in the loaded corpus, so no "
                                              "precursor window exists to supply"),
                                 node_key=n["node_key"]))

    cols = ["lineage_id", "cell", "stage", "assertion_exists", "n_markers", "observable",
            "observable_route", "reason_code", "measurement", "node_key"]
    with open(OUT / "OBSERVABILITY_BOUNDARY_REGISTER.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    summ = {"rows": len(rows),
            "by_stage": dict(Counter(r["stage"] for r in rows)),
            "observable_by_stage": {s: sum(1 for r in rows if r["stage"] == s and r["observable"] == "Y")
                                    for s in STAGES},
            "by_reason": dict(Counter(r["reason_code"] for r in rows)),
            "unobservable_cells": sum(1 for r in rows if r["observable"] == "N")}
    (OUT / "BOUNDARY_SUMMARY.json").write_text(json.dumps(summ, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
    print(json.dumps(summ, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()