#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure the near-miss column: capture the pre-change bytes, verify after the change.

Corpus: the 25 volumes / 764 clusters of the independent-validation wave; genes are the
top_genes of each cluster's evidence report, tissue is the volume's tissue. Route: the
default composite surface (library="all").

Arms
  OFF  EYEKB_ABSTAIN_REASON unset          -> must be byte-identical (P1)
  ON   EYEKB_ABSTAIN_REASON=1              -> pre-existing abstain_reason fields must be
                                              byte-identical; near_miss may be added (P2/P3)

Run:  python3 near_miss_measure.py --capture   (on pre-change bytes)
      python3 near_miss_measure.py --verify    (after the change)
Exit 0 = every criterion passed.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
CAP = os.path.join(OUT, "NEAR_MISS_CAPTURE.json")
ROOT = "/home/ubuntu/EYEKB_REPO"
EVROOT = "/home/ubuntu/eyekb_indep_validation_20261022/ev"

TISSUE = {}


def clean_env():
    for k in [k for k in list(os.environ) if k.startswith("EYEKB_")]:
        del os.environ[k]


def load_corpus():
    """{volume::cluster: {genes, tissue}} straight from the evidence reports."""
    corpus = {}
    for p in sorted(glob.glob(os.path.join(EVROOT, "*",
                                          "annotation_evidence_report.json"))):
        d = json.load(open(p))
        vol = os.path.basename(os.path.dirname(p))
        for c in d.get("clusters", []):
            g = [x for x in (c.get("top_genes") or []) if isinstance(x, str)]
            if not g:
                continue
            corpus["%s::%s" % (vol, c.get("cluster"))] = {
                "genes": g, "tissue": d.get("tissue")}
    return corpus


def md5(resp):
    return hashlib.md5(json.dumps(resp, sort_keys=True, ensure_ascii=False)
                       .encode()).hexdigest()


PRE_FIELDS = ("cause", "causes", "n_query_genes", "n_genes_with_hit",
              "n_scored_classes", "demoted")


def run(arm):
    """arm = 'OFF' | 'ON'; returns per-cluster records."""
    clean_env()
    if arm == "ON":
        os.environ["EYEKB_ABSTAIN_REASON"] = "1"
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    for m in [m for m in list(sys.modules) if m.startswith("eyekb_core")]:
        del sys.modules[m]
    import eyekb_core as core  # noqa: E402

    corpus = load_corpus()
    out = {}
    errs = []
    for key, rec in sorted(corpus.items()):
        vol, cl = key.split("::")
        try:
            r = core.query_marker(genes=rec["genes"], library="all",
                                  tissue=rec.get("tissue"),
                                  volume_id="near_miss_probe")
        except Exception as e:                       # noqa: BLE001
            errs.append("%s: %r" % (key, e))
            continue
        ar = r.get("abstain_reason") or {}
        out[key] = {
            "md5": md5(r),
            "n_rank": len(r.get("celltype_ranking") or []),
            "rank_seq": [x.get("cell_type") for x in (r.get("celltype_ranking") or [])],
            "has_abstain_reason": "abstain_reason" in r,
            "ar_fields": {k: ar.get(k) for k in PRE_FIELDS},
            "near_miss": ar.get("near_miss"),
        }
    return {"arm": arm, "n": len(out), "errs": errs, "corpus": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if not (a.capture or a.verify):
        raise SystemExit("need --capture or --verify")
    os.makedirs(OUT, exist_ok=True)

    if a.capture:
        cap = {arm: run(arm) for arm in ("OFF", "ON")}
        for arm, v in cap.items():
            print("captured %s: %d clusters, %d errors" % (arm, v["n"], len(v["errs"])))
            if v["errs"]:
                print("  ", v["errs"][:3])
        json.dump(cap, open(CAP, "w"), indent=1, ensure_ascii=False)
        print("wrote", CAP)
        return

    if not os.path.exists(CAP):
        raise SystemExit("no capture at %s -- run --capture on pre-change bytes" % CAP)
    cap = json.load(open(CAP))
    fails = []

    def chk(cid, name, ok, detail=""):
        print("  %s  %-52s %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            fails.append("%s/%s" % (cid, name))

    # ---- P1: default bytes unchanged
    now = run("OFF")
    keys = sorted(set(cap["OFF"]["corpus"]) & set(now["corpus"]))
    same = sum(1 for k in keys
               if cap["OFF"]["corpus"][k]["md5"] == now["corpus"][k]["md5"])
    seq = sum(1 for k in keys
              if cap["OFF"]["corpus"][k]["rank_seq"] == now["corpus"][k]["rank_seq"])
    print("== P1 default route, switch OFF ==")
    chk("P1", "responses byte-identical", same == len(keys), "%d/%d" % (same, len(keys)))
    chk("P1", "ranking sequences identical", seq == len(keys), "%d/%d" % (seq, len(keys)))
    chk("P1", "no new errors", not now["errs"], str(now["errs"][:2]))

    # ---- P2 / P3: opt-in arm
    now_on = run("ON")
    keys_on = sorted(set(cap["ON"]["corpus"]) & set(now_on["corpus"]))
    changed_fields, added_key, kept = [], [], 0
    for k in keys_on:
        c, n = cap["ON"]["corpus"][k], now_on["corpus"][k]
        if c["ar_fields"] == n["ar_fields"]:
            kept += 1
        else:
            changed_fields.append(k)
        if (n["near_miss"] is not None) and (c["near_miss"] is None):
            added_key.append(k)
    print("\n== P2/P3 opt-in route, switch ON ==")
    chk("P2/P3", "pre-existing abstain_reason fields unchanged",
        not changed_fields, "%d/%d identical" % (kept, len(keys_on)))
    if changed_fields:
        print("      first offenders:", changed_fields[:3])
    n_abstain_now = sum(1 for k in keys_on if now_on["corpus"][k]["n_rank"] == 0)
    print("      abstaining clusters: %d ; near_miss written on %d"
          % (n_abstain_now, len(added_key)))
    # the key must never appear on a cluster that produced a ranking
    bad = [k for k in keys_on
           if now_on["corpus"][k]["near_miss"] and now_on["corpus"][k]["n_rank"] > 0]
    chk("P3", "near_miss never written alongside a ranking", not bad, str(bad[:3]))

    # ---- P4: red line - no tissue-out-of-scope or composite demotion leaks
    leaks = []
    for k in keys_on:
        nm = now_on["corpus"][k]["near_miss"] or []
        for e in nm:
            if e.get("why") not in ("state_program_only", "increment_guard"):
                leaks.append((k, e.get("cell_type"), e.get("why")))
    print("\n== P4 red line ==")
    chk("P4", "no out-of-scope / composite class in near_miss", not leaks, str(leaks[:3]))

    json.dump({"OFF": now, "ON": now_on},
              open(os.path.join(OUT, "NEAR_MISS_VERIFY.json"), "w"),
              indent=1, ensure_ascii=False)
    print("\ncriterion failures: %d" % len(fails))
    if fails:
        print("MISMATCH:", fails)
        sys.exit(1)
    print("READTHROUGH PASS: default bytes unchanged; near_miss is additive and rule-clean.")


if __name__ == "__main__":
    main()