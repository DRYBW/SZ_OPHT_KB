#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit checks for the near_miss column (criterion P6).

Rather than inventing synthetic responses, this re-runs the clusters that actually
produced a near_miss list and cross-checks every entry against the SAME response's
own guard fields. If near_miss ever disagrees with the demotion records it claims to
summarise, one of the two is lying and this fails.

Cases
  U1  a response with an empty score carries no near_miss key
  U2  a response with a ranking carries no near_miss key
  U3  every near_miss entry is traceable to state_annotations or to an
      antseg_guard_demoted row whose reason is below_increment_eligibility
  U4  no near_miss entry names a class listed in tissue_excluded_candidates
      or composite_demoted (PI red line)
  U5  near_miss is capped at 3 entries and sorted by n_shared descending
  U6  the switch OFF arm never carries the key

Run: python3 near_miss_unit.py      (exit 0 = all pass)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
VERIFY = os.path.join(OUT, "NEAR_MISS_VERIFY.json")
ROOT = "/home/ubuntu/EYEKB_REPO"
EVROOT = "/home/ubuntu/eyekb_indep_validation_20261022/ev"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print("  %s  %-58s %s" % ("PASS" if cond else "FAIL", name, detail))


def main():
    if not os.path.exists(VERIFY):
        raise SystemExit("run near_miss_measure.py --verify first")
    v = json.load(open(VERIFY))

    # reconstruct the corpus so we can re-run individual clusters
    corpus = {}
    for d in sorted(os.listdir(EVROOT)):
        p = os.path.join(EVROOT, d, "annotation_evidence_report.json")
        if not os.path.exists(p):
            continue
        rep = json.load(open(p))
        for c in rep.get("clusters", []):
            g = [x for x in (c.get("top_genes") or []) if isinstance(x, str)]
            if g:
                corpus["%s::%s" % (d, c.get("cluster"))] = {
                    "genes": g, "tissue": rep.get("tissue")}

    for k in [k for k in list(os.environ) if k.startswith("EYEKB_")]:
        del os.environ[k]
    os.environ["EYEKB_ABSTAIN_REASON"] = "1"
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    import eyekb_core as core  # noqa: E402

    on = v["ON"]["corpus"]
    with_nm = [k for k, r in on.items() if r.get("near_miss")]
    print("clusters carrying near_miss: %d\n" % len(with_nm))

    resp = {}
    for k in with_nm:
        rec = corpus[k]
        vol, cl = k.split("::")
        resp[k] = core.query_marker(genes=rec["genes"], library="all",
                                    tissue=rec["tissue"],
                                    volume_id="near_miss_unit")

    # U1: empty score -> no key
    empty = [k for k, r in corpus.items()
             if not core.query_marker(genes=["ZZZNOTAGENE1", "ZZZNOTAGENE2"],
                                      library="all", volume_id="nm_unit")
             .get("celltype_ranking")]
    r_empty = core.query_marker(genes=["ZZZNOTAGENE1", "ZZZNOTAGENE2"],
                               library="all", volume_id="nm_unit")
    check("U1 empty score carries no near_miss",
          "near_miss" not in (r_empty.get("abstain_reason") or {}),
          "cause=%s" % (r_empty.get("abstain_reason") or {}).get("cause"))

    # U2: ranking present -> no key
    bad2 = [k for k, r in on.items() if r["n_rank"] > 0 and r.get("near_miss")]
    check("U2 a ranked response carries no near_miss", not bad2, str(bad2[:3]))

    # U3: traceability
    bad3 = []
    for k, r in resp.items():
        states = {s.get("cell_type") for s in (r.get("state_annotations") or [])}
        dem = {d.get("cell_type") for d in (r.get("antseg_guard_demoted") or [])
               if d.get("reason") == "below_increment_eligibility"}
        for e in (r.get("abstain_reason") or {}).get("near_miss") or []:
            ok = (e["why"] == "state_program_only" and e["cell_type"] in states) or \
                 (e["why"] == "increment_guard" and e["cell_type"] in dem)
            if not ok:
                bad3.append((k, e.get("cell_type"), e.get("why")))
    check("U3 every entry traces to its own demotion record", not bad3, str(bad3[:3]))

    # U4: red line
    bad4 = []
    for k, r in resp.items():
        banned = {x.get("cell_type") for x in (r.get("tissue_excluded_candidates") or [])}
        banned |= {x.get("cell_type") for x in (r.get("composite_demoted") or [])}
        banned |= {x.get("cell_type") for x in (r.get("antseg_guard_demoted") or [])
                   if x.get("reason") != "below_increment_eligibility"}
        for e in (r.get("abstain_reason") or {}).get("near_miss") or []:
            if e["cell_type"] in banned:
                bad4.append((k, e["cell_type"]))
    check("U4 no wrong-class demotion leaks", not bad4, str(bad4[:3]))

    # U5: cap and order
    bad5 = []
    for k, r in resp.items():
        nm = (r.get("abstain_reason") or {}).get("near_miss") or []
        if len(nm) > 3:
            bad5.append((k, "len", len(nm)))
        ns = [e.get("n_shared") or 0 for e in nm]
        if ns != sorted(ns, reverse=True):
            bad5.append((k, "order", ns))
    check("U5 capped at 3 and sorted by n_shared desc", not bad5, str(bad5[:3]))

    # U6: OFF arm never carries the key
    bad6 = [k for k, r in v["OFF"]["corpus"].items() if r.get("near_miss")]
    check("U6 switch OFF never carries near_miss", not bad6, str(bad6[:3]))

    # show one worked example for the record
    if resp:
        k = sorted(resp)[0]
        nm = (resp[k].get("abstain_reason") or {}).get("near_miss")
        print("\nworked example  %s" % k)
        print("  ranking: %s" % (resp[k].get("celltype_ranking") or [])[:1])
        print("  near_miss: %s" % json.dumps(nm, ensure_ascii=False)[:400])

    bad = [r for r in results if not r[1]]
    print("\nunit cases: %d, failures: %d" % (len(results), len(bad)))
    if bad:
        sys.exit(1)
    print("UNIT PASS: near_miss is traceable, capped, ordered and rule-clean.")


if __name__ == "__main__":
    main()