#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 2 — the recognition probe.

Builds the input a caller would actually supply for a fetal-state cluster and for the corresponding
adult-state cluster (from the frozen stage-resolved table of step 1), drives **the shipped service**
over its real MCP stdio transport, stores every raw response, and derives one observability verdict
per lineage by the rules frozen in PREREG_STAGE_CHANGE_v1.md §2.

Fidelity notes (measured, not assumed):
  * transport: real `mcp_server/server.py` started as a stdio subprocess by the MCP SDK 2.x client;
    the interpreter is the one on this machine that can import `mcp.server.MCPServer` (selected by
    `--interpreter`, default /home/ubuntu/training-venv/bin/python3). No kernel function is imported
    into this process, so the answer recorded is the answer the shipped server sends.
  * the probe's own calls are tagged with EYEKB_MCP_TRACE_TAG so the service's call-tracing layer
    can exclude self-test traffic.
  * the probe never writes inside the repository except under this card's own directory.

Usage:
  <sdk-interpreter> scripts/02_probe_recognition.py --pass 1
  <sdk-interpreter> scripts/02_probe_recognition.py --pass 2
"""
import argparse
import asyncio
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = HERE / "out"
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PLAN_F = OUT / "PROBE_PLAN.json"
RESULTS = OUT / "PROBE_RESULTS.json"
VERDICTS = OUT / "VERDICTS.tsv"
TAG = "devlineage-v3-stage-probe"

K_WINDOWS = (10, 25)          # frozen in the prereg


def load_marker_table():
    rows = list(csv.DictReader(open(OUT / "STAGE_RESOLVED_MARKERS.tsv", encoding="utf-8"), delimiter="\t"))
    return rows


def build_plan():
    """Per (lineage, stage): the ordered gene window a caller would supply.

    Order is the order the source asserts the markers in (dev panel entry order / baseline
    markers_local_lib order), recovered from the source files — the frozen table is used for the
    assertion ids, never for the order."""
    dev = json.loads((REPO / "kb" / "markers" / "markers_v9_dev_retina.json").read_text(encoding="utf-8"))
    base = json.loads((REPO / "kb" / "baselines" / "retina.json").read_text(encoding="utf-8"))
    adult_sets = {r["class"]: list(r["markers_local_lib"]) for r in base["major_classes"]}

    nodes = list(csv.DictReader(open(OUT / "NODE_KEYS.tsv", encoding="utf-8"), delimiter="\t"))
    table = load_marker_table()
    aid = {(r["stage"], r["in_house_entry"], r["gene_symbol"]): r["assertion_id"] for r in table}

    plan = []
    for n in nodes:
        if n["node_kind"] != "fetal_entry":
            continue
        lin = n["lineage_id"]
        entry = n["in_house_entry"]
        fe = list(dev["markers"][entry])
        adult_classes = [c for c in n["adult_counterpart_classes"].split(";") if c]
        plan.append({
            "lineage_id": lin, "side": "fetal", "node_key": n["node_key"],
            "entry_or_class": entry, "stage": "fetal",
            "full_set": fe, "full_set_assertion_ids": [aid.get(("fetal", entry, g), "") for g in fe],
            "adult_counterparts": adult_classes,
            "windows": {str(k): [aid.get(("fetal", entry, g), "") for g in fe[:k]] for k in K_WINDOWS},
            "window_genes": {str(k): fe[:k] for k in K_WINDOWS},
        })
    for n in nodes:
        if n["node_kind"] != "adult_class":
            continue
        cls = n["in_house_entry"]
        lin = n["lineage_id"]
        aset = adult_sets[cls]
        plan.append({
            "lineage_id": lin or f"adult_only::{cls}", "side": "adult", "node_key": n["node_key"],
            "entry_or_class": cls, "stage": "adult",
            "full_set": aset, "full_set_assertion_ids": [aid.get(("adult", cls, g), "") for g in aset],
            "adult_counterparts": [],
            "windows": {str(k): [aid.get(("adult", cls, g), "") for g in aset[:k]] for k in K_WINDOWS},
            "window_genes": {str(k): aset[:k] for k in K_WINDOWS},
        })
    return plan


def calls_for_plan(plan):
    """The call list: the fetal input and the corresponding adult input, default route and the
    explicit developmental route, for both frozen windows."""
    calls = []
    # NOTE: one call id per (lineage, side, adult class, window, route). A lineage can carry two
    # adult counterparts (the glia entry claims MG and Astrocyte); keying only by (lineage, side)
    # would silently drop one of them, so the class is part of the id.
    for p in plan:
        lin = p["lineage_id"]
        tag = p["entry_or_class"] if p["side"] == "adult" else ""
        base = f"{lin}.{p['side']}" + (f".{tag}" if tag else "")
        for k in K_WINDOWS:
            genes = p["window_genes"][str(k)]
            calls.append({"id": f"{base}.K{k}.default", "lineage_id": lin, "side": p["side"],
                          "target": p["entry_or_class"], "window": k, "tool": "query_marker",
                          "args": {"genes": genes}, "route": "default", "n_genes": len(genes),
                          "declared_but_unrunnable": len(genes) < k})
            calls.append({"id": f"{base}.K{k}.devroute", "lineage_id": lin, "side": p["side"],
                          "target": p["entry_or_class"], "window": k, "tool": "query_marker",
                          "args": {"genes": genes, "library": "retina_dev"},
                          "route": "explicit_dev", "n_genes": len(genes),
                          "declared_but_unrunnable": len(genes) < k})
    # composition surface: the only shipped tool that accepts a stage at all
    for literal in ["", "adult", "fetal", "developing", "unknown", "postnatal", "organoid"]:
        calls.append({"id": f"composition.{literal or 'empty'}", "lineage_id": None, "side": None,
                      "window": None, "tool": "get_tissue_composition",
                      "args": {"species": "human", "tissue": "retina", "development_stage": literal},
                      "route": "composition", "n_genes": None, "declared_but_unrunnable": False})
    calls.append({"id": "release_identity", "lineage_id": None, "side": None, "window": None,
                  "tool": "get_release_identity", "args": {}, "route": "identity",
                  "n_genes": None, "declared_but_unrunnable": False})
    return calls


def md5(txt: str) -> str:
    return hashlib.md5(txt.encode()).hexdigest()


async def drive(calls, interpreter):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    srv = str(REPO / "mcp_server" / "server.py")
    env = dict(os.environ)
    env["EYEKB_MCP_TRACE_TAG"] = TAG
    out = {}
    sp = StdioServerParameters(command=interpreter, args=[srv], env=env)
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["_handshake"] = {"server_info": str(getattr(init, "serverInfo", None)),
                                 "protocolVersion": getattr(init, "protocolVersion", None)}
            advertised = sorted(t.name for t in (await s.list_tools()).tools)
            out["_tools"] = advertised
            for c in calls:
                res = await s.call_tool(c["tool"], c["args"])
                parts = [getattr(x, "text", "") or "" for x in (res.content or [])]
                txt = "".join(parts)
                norm = txt.replace(str(REPO), "<REPO>")
                rec = {"id": c["id"], "tool": c["tool"], "args": c["args"], "route": c["route"],
                       "lineage_id": c["lineage_id"], "side": c["side"], "window": c["window"],
                       "n_genes_supplied": c["n_genes"],
                       "declared_but_unrunnable": c["declared_but_unrunnable"],
                       "is_error": bool(getattr(res, "is_error", getattr(res, "isError", False))),
                       "response_text_md5": md5(norm),
                       "response_text_bytes": len(txt.encode()),
                       "response_text": txt}
                try:
                    rec["response"] = json.loads(txt)
                    rec["parsed"] = True
                except Exception:
                    rec["parsed"] = False
                out[c["id"]] = rec
    return out


# ---------------------------------------------------------------- verdicts (prereg §2)
def top1(resp):
    r = (resp or {}).get("celltype_ranking") or []
    return r[0] if r else None


def ranking_genes_top1(resp):
    t = top1(resp)
    return tuple(t.get("shared_genes") or []) if t else tuple()


def dev_best_from(resp, fetal_genes):
    """The dev-panel signal the shipped advisory itself measures: the best overlap between the
    supplied window and any dev-panel entry. Recomputed here from the shipped dev-panel file so the
    verdict does not depend on the advisory firing."""
    ds = DEV_SETS
    g = set(x.upper() for x in fetal_genes)
    best, terms = 0, []
    for e, gs in ds.items():
        n = len(g & gs)
        if n > best:
            best, terms = n, [e]
        elif n == best and n > 0:
            terms.append(e)
    return best, sorted(terms)


DEV_SETS = None


ENTRY_OF = {}


def verdict_for(lin, recs, plan_side, adult_cls_names):
    """One verdict per lineage, by the frozen rules (first match wins).

    The adult side is the lineage's primary adult counterpart (the first class the fetal entry
    claims); a second counterpart, where one exists, is recorded as a supplementary measurement and
    never substitutes for the primary."""
    fet10 = recs.get(f"{lin}.fetal.K10.default")
    fet25 = recs.get(f"{lin}.fetal.K25.default")
    adults = plan_side.get("adult_counterparts") or []
    ad10 = recs.get(f"{lin}.adult.{adults[0]}.K10.default") if adults else None
    ad_alts = [f"{a}:{((recs.get(f'{lin}.adult.{a}.K10.default') or {{}}).get('response') or {})}"
               for a in adults[1:]]
    fet_dev = recs.get(f"{lin}.fetal.K25.devroute") or recs.get(f"{lin}.fetal.K10.devroute")
    m = {"lineage_id": lin}
    if fet10 is None:              # no fetal-stage assertion exists in the corpus
        m.update(verdict="needs_information_this_interface_cannot_observe",
                 reason_code="no_assertion_in_corpus",
                 fetal_top1="", fetal_top1_n_shared="", adult_top1="", adult_top1_n_shared="",
                 dev_best_max=0, advisory_fired="N", rankings_identical="NA",
                 silent_adult_assignment="NA")
        m["detail"] = ("no fetal-stage marker assertion exists for this lineage in the loaded corpus, "
                       "so there is no fetal window a caller could supply")
        return m
    f1 = top1(fet10.get("response")) if fet10.get("parsed") else None
    a1 = top1(ad10.get("response")) if ad10 and ad10.get("parsed") else None
    f10_genes = fet10["args"]["genes"]
    f25_genes = (fet25 or {}).get("args", {}).get("genes", f10_genes)
    devbest10 = dev_best_from(None, f10_genes)[0]
    devbest25 = dev_best_from(None, f25_genes)[0]
    devbest = max(devbest10, devbest25)
    adv = bool((fet10.get("response") or {}).get("off_domain"))
    adv25 = bool((fet25.get("response") or {}).get("off_domain")) if fet25 else False
    r_f = ranking_genes_top1(fet10.get("response"))
    r_a = ranking_genes_top1(ad10.get("response")) if ad10 else None
    ident = ("NA" if r_a is None else ("Y" if r_f == r_a else "N"))
    empty_both = (not (fet10.get("response") or {}).get("celltype_ranking")) and \
                 (ad10 is not None and not (ad10.get("response") or {}).get("celltype_ranking"))
    silent = "N"
    # the ranking can return the same class under a cross-library alias ("retina_interneuron::HC"),
    # so the comparison is made on the bare class name
    if f1 is not None and adult_cls_names and str(f1.get("cell_type", "")).split("::")[-1] in adult_cls_names:
        silent = "Y"
    if empty_both:
        v, code = "no_candidate_either_way", "ranking_empty_both_sides"
    elif adv or adv25:
        v, code = "observable_now", "shipped_off_domain_advisory_fires_on_fetal_input"
    elif devbest >= 1:
        v, code = "needs_wider_query_window", f"dev_signal_present_below_shipped_criterion(dev_best={devbest})"
    else:
        v, code = ("needs_information_this_interface_cannot_observe",
                   "no_discriminating_gene_in_any_loaded_library_and_no_stage_channel")
    sa = (fet10.get("response") or {}).get("state_annotations") or []
    sa_hit = next((x for x in sa if str(x.get("cell_type", "")) == ENTRY_OF.get(lin)), None)
    m.update(verdict=v, reason_code=code,
             state_annotation_hit=(f"{sa_hit['cell_type']} n_shared={sa_hit['n_shared']}" if sa_hit else ""),
             adult_top1_secondary=(";".join(ad_alts)[:160] if ad_alts else ""),
             fetal_top1=(f1 or {}).get("cell_type", ""), fetal_top1_n_shared=(f1 or {}).get("n_shared", ""),
             adult_top1=(a1 or {}).get("cell_type", ""), adult_top1_n_shared=(a1 or {}).get("n_shared", ""),
             dev_best_k10=devbest10, dev_best_k25=devbest25, dev_best_max=devbest,
             advisory_fired="Y" if (adv or adv25) else "N",
             rankings_identical=ident, silent_adult_assignment=silent,
             n_fetal_genes_supplied=len(f10_genes))
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_no", type=int, default=1)
    ap.add_argument("--interpreter", default="/home/ubuntu/training-venv/bin/python3")
    a = ap.parse_args()

    global DEV_SETS
    dev = json.loads((REPO / "kb" / "markers" / "markers_v9_dev_retina.json").read_text(encoding="utf-8"))
    DEV_SETS = {e: set(g.upper() for g in gs) for e, gs in dev["markers"].items()}

    plan = build_plan()
    calls = calls_for_plan(plan)
    PLAN_F.write_text(json.dumps({"interpreter": a.interpreter, "trace_tag": TAG,
                                  "k_windows": list(K_WINDOWS), "plan": plan, "calls": calls},
                                 indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    t0 = time.time()
    rows = asyncio.run(drive(calls, a.interpreter))
    rows["_meta"] = {"pass": a.pass_no, "wall_seconds": round(time.time() - t0, 2),
                     "interpreter": a.interpreter, "server": str(REPO / "mcp_server" / "server.py"),
                     "trace_tag": TAG, "n_calls": len(calls),
                     "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (OUT / f"PROBE_RESULTS_pass{a.pass_no}.json").write_text(
        json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.pass_no == 2:
        RESULTS.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # verdicts (computed from the pass-1 or pass-2 rows; they must agree)
    adult_cls = {n["in_house_entry"] for n in
                 csv.DictReader(open(OUT / "NODE_KEYS.tsv", encoding="utf-8"), delimiter="\t")
                 if n["node_kind"] == "adult_class"}
    lines = sorted({p["lineage_id"] for p in plan if p["side"] == "fetal"})
    vrows = []
    for lin in lines:
        side = next(p for p in plan if p["lineage_id"] == lin and p["side"] == "fetal")
        ENTRY_OF[lin] = side["entry_or_class"]
        vrows.append(verdict_for(lin, rows, side, adult_cls))
    # adult classes nothing points at from the fetal side: an explicit, honest row rather than a
    # silent omission (this is the Microglia case — no precursor entry claims it in the corpus)
    for p in plan:
        if p["side"] == "adult" and p["lineage_id"] not in lines:
            vrows.append({"lineage_id": p["lineage_id"] or f"adult_only::{p['entry_or_class']}",
                          "verdict": "needs_information_this_interface_cannot_observe",
                          "reason_code": "no_precursor_entry_in_corpus",
                          "n_fetal_genes_supplied": 0, "fetal_top1": "", "fetal_top1_n_shared": "",
                          "adult_top1": (top1((rows.get(f"{p['lineage_id']}.adult.{p['entry_or_class']}.K10.default") or {}).get("response")) or {}).get("cell_type", ""),
                          "adult_top1_n_shared": (top1((rows.get(f"{p['lineage_id']}.adult.{p['entry_or_class']}.K10.default") or {}).get("response")) or {}).get("n_shared", ""),
                          "state_annotation_hit": "", "adult_top1_secondary": "",
                          "dev_best_k10": 0, "dev_best_k25": 0, "dev_best_max": 0,
                          "advisory_fired": "N", "rankings_identical": "NA",
                          "silent_adult_assignment": "NA",
                          "detail": ("the adult class exists in the adult vocabulary but no fetal/precursor "
                                     "entry in the loaded corpus claims it, so no fetal window exists to supply")})
    cols = ["lineage_id", "verdict", "reason_code", "n_fetal_genes_supplied", "fetal_top1",
            "fetal_top1_n_shared", "adult_top1", "adult_top1_n_shared", "dev_best_k10", "dev_best_k25",
            "dev_best_max", "advisory_fired", "rankings_identical", "silent_adult_assignment",
            "state_annotation_hit", "adult_top1_secondary", "detail"]
    with open(OUT / f"VERDICTS_pass{a.pass_no}.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n",
                           extrasaction="ignore")
        w.writeheader()
        for r in vrows:
            w.writerow(r)
    if a.pass_no == 2:
        VERDICTS.write_text(open(OUT / "VERDICTS_pass2.tsv", encoding="utf-8").read(), encoding="utf-8")

    print(json.dumps({"pass": a.pass_no, "n_calls": len(calls), "wall_seconds": rows["_meta"]["wall_seconds"],
                      "tools": rows["_tools"], "n_errors": sum(1 for k, v in rows.items()
                                                               if isinstance(v, dict) and v.get("is_error")),
                      "verdict_counts": {v: sum(1 for r in vrows if r["verdict"] == v)
                                         for v in sorted({r["verdict"] for r in vrows})}},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()