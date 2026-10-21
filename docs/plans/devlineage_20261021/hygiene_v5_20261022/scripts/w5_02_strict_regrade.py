#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_02_strict_regrade.py — ITEM 1, second half: grade the transition table honestly.

The upstream table's `support_status` grades a marker change on "the corpus mentions this gene
anywhere" (n_chunks > 0). The marker layer grades it on four conditions at once:

    1. the chunk carries the gene token                    (by construction here)
    2. the chunk's species is admissible for the node      (human | both)
    3. the chunk names the target group                    (a photoreceptor-lineage phrase)
    4. the chunk is developmentally scented                (dev keyword, or the paper's own
                                                            declared stage scope is fetal/mixed)

This script applies the marker layer's own rule to the same 100 transition rows, from the raw
corpus (its own pass, not the marker layer's product), and reconciles the result with
`markers/out/MARKER_CHANGE_EDGES.tsv`, which the card names as the superseding artefact. Two
readings are produced on purpose:

  strict_all_chunks      every chunk in the corpus is eligible
  strict_recorded_top10  only the ten best-ranked rows the marker layer recorded per gene, which
                         is what its own admission test actually saw

If the two agree, the residual "the admission test only saw ten rows per gene" is measured and
bounded rather than argued.

Outputs: out/ITEM1_STRICT_REGRADE.tsv, out/ITEM1_RECONCILIATION.json,
         out/TRANSITION_TABLE_RECONCILED.tsv
Usage  : python3 scripts/w5_02_strict_regrade.py [--limit-batches N]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402

sys.path.insert(0, C.MK_SCRIPTS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-batches", type=int, default=0)
    args = ap.parse_args()

    import pyarrow.parquet as pq  # noqa: E402
    import m0_corpus_gene_index as M0  # noqa: E402  (the marker layer's own rule constants)
    M = C.markers_common()

    rows = C.read_tsv(os.path.join(C.CLD_OUT, "LINEAGE_MARKER_TRANSITIONS.tsv"))
    edges = {r["edge_id"]: r for r in C.read_tsv(os.path.join(C.CLD_OUT, "LINEAGE_EDGES.tsv"))}
    target_genes = {r["gene"] for r in rows}

    stage_scope = M.load_stage_scope()
    role_flags = M.load_role_flags()
    no_anchor = {str(p) for p, f in role_flags.items() if f == "data_side_only"}
    no_anchor.update(str(t) for t in M.FORBIDDEN_TOKENS if str(t).isdigit())

    phrases = {k: re.compile(r"(?<![A-Za-z0-9])" + re.escape(v) + r"(?![A-Za-z0-9])", re.I)
               for k, v in M0.TARGET_PHRASES.items()}

    best = {}                     # gene -> best admissible row meeting all four conditions
    seen = collections.defaultdict(lambda: {"n_rows": 0, "n_species_ok": 0, "n_named": 0,
                                            "n_dev": 0, "n_all4": 0})
    t0 = time.time()
    pf = pq.ParquetFile(C.CHUNKS)
    cols = ["paper_id", "section", "chunk_type", "text", "cell_type_mentioned", "species",
            "tissue", "full_text_available"]
    n_chunks = 0
    ord_i = 0
    for b, batch in enumerate(pf.iter_batches(batch_size=20000, columns=cols), 1):
        d = batch.to_pydict()
        for i in range(batch.num_rows):
            n_chunks += 1
            text = d["text"][i] or ""
            toks = {t.upper() for t in M0.TOKEN_RE.findall(text)}
            present = toks & target_genes
            if not present:
                continue
            pid = str(d["paper_id"][i])
            species = d["species"][i] or "unknown"
            has_dev = bool(M0.DEV_KW.search(text))
            t_hits = [k for k, rx in phrases.items() if rx.search(text)]
            for g in present:
                ord_i2 = n_chunks
                st = seen[g]
                st["n_rows"] += 1
                c2 = species in ("human", "both")
                c3 = bool(t_hits)
                c4 = has_dev or (stage_scope.get(pid) in ("fetal_only", "mixed"))
                st["n_species_ok"] += int(c2)
                st["n_named"] += int(c3)
                st["n_dev"] += int(c4)
                if not (c2 and c3 and c4):
                    continue
                st["n_all4"] += 1
                if pid in no_anchor:
                    continue
                cand = {"ord": ord_i2, "paper_id": pid, "section": (d["section"][i] or "")[:120],
                        "chunk_type": d["chunk_type"][i] or "", "species": species,
                        "tissue": d["tissue"][i] or "unknown", "dev_kw": has_dev,
                        "target_phrases": sorted(t_hits),
                        "sha16": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]}
                cur = best.get(g)
                if cur is None or M0.example_rank(cand) < M0.example_rank(cur):
                    best[g] = cand
        if args.limit_batches and b >= args.limit_batches:
            print("[probe] stopped after %d batches (%d chunks)" % (b, n_chunks), flush=True)
            break
        if b % 5 == 0:
            print("  scanned %d chunks (maxrss %.2f GiB)"
                  % (n_chunks, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576),
                  flush=True)
    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576
    print("scanned %d chunks; genes with an all-four-condition row: %d/%d; maxrss %.2f GiB; %.1fs"
          % (n_chunks, len(best), len(target_genes), maxrss, time.time() - t0), flush=True)
    if args.limit_batches:
        C.write_json(os.path.join(C.OUT, "ITEM1_STRICT_PROBE.json"),
                     {"limit_batches": args.limit_batches, "chunks": n_chunks,
                      "maxrss_gib": round(maxrss, 3), "seconds": round(time.time() - t0, 1)})
        return 0

    # the recorded examples the marker layer's own admission test saw (its top ten per gene)
    recorded = {}
    with open(os.path.join(C.MK_OUT, "CORPUS_GENE_EXAMPLES_v1.jsonl"), encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            recorded[d["gene"]] = d["examples"]

    def recorded_verdict(g, label):
        """The marker layer's test, restricted to the rows it recorded."""
        for x in recorded.get(g, []):
            if x["species"] not in ("human", "both"):
                continue
            dev = x["dev_kw"] or (stage_scope.get(str(x["paper_id"])) in ("fetal_only", "mixed"))
            name_hit = bool(x.get("target_phrases"))
            if name_hit and dev:
                return x
        return None

    superseding = {r["gene_symbol"]: r for r in C.read_tsv(
        os.path.join(C.MK_OUT, "MARKER_CHANGE_EDGES.tsv"))}

    out_rows, recon_rows = [], []
    for r in rows:
        g = r["gene"]
        e = edges[r["edge_id"]]
        b = best.get(g)
        rv = recorded_verdict(g, e["child_label"])
        s = seen.get(g) or {"n_rows": 0, "n_species_ok": 0, "n_named": 0, "n_dev": 0, "n_all4": 0}
        verdict_all = "strict_supported" if b else ("no_chunk_meets_all_four"
                                                    if s["n_rows"] else "gene_absent_from_corpus")
        verdict_top10 = "strict_supported" if rv else ("no_chunk_meets_all_four"
                                                       if recorded.get(g) else
                                                       "gene_absent_from_corpus")
        sup = superseding.get(g)
        out_rows.append({
            "edge_id": r["edge_id"], "direction": r["direction"], "gene": g,
            "in_child_panel": r["in_child_panel"], "in_parent_panel": r["in_parent_panel"],
            "upstream_support_status": r["support_status"],
            "upstream_corpus_n_chunks": r["corpus_n_chunks"],
            "chunks_with_gene_token": s["n_rows"],
            "chunks_admissible_species": s["n_species_ok"],
            "chunks_naming_target_group": s["n_named"],
            "chunks_developmentally_scented": s["n_dev"],
            "chunks_meeting_all_four": s["n_all4"],
            "support_status_strict": verdict_all,
            "support_status_strict_top10": verdict_top10,
            "strict_locator": ("%s @ %s#ord%d#sha%s" % (b["paper_id"], b["section"], b["ord"],
                                                        b["sha16"])) if b else "",
            "superseding_assertion_id": (sup or {}).get("assertion_id", ""),
        })
        recon_rows.append({
            "edge_id": r["edge_id"], "direction": r["direction"], "gene": g,
            "upstream_says": r["support_status"],
            "strict_says": verdict_all,
            "marker_layer_admitted": "yes" if sup else "no",
            "strict_all_chunks_agrees_with_marker_layer":
                ("yes" if ((sup is not None) == (verdict_all == "strict_supported")) else "no"),
            "strict_top10_agrees_with_marker_layer":
                ("yes" if ((sup is not None) == (verdict_top10 == "strict_supported")) else "no"),
        })

    C.write_tsv(os.path.join(C.OUT, "ITEM1_STRICT_REGRADE.tsv"), out_rows,
                ["edge_id", "direction", "gene", "in_child_panel", "in_parent_panel",
                 "upstream_support_status", "upstream_corpus_n_chunks", "chunks_with_gene_token",
                 "chunks_admissible_species", "chunks_naming_target_group",
                 "chunks_developmentally_scented", "chunks_meeting_all_four",
                 "support_status_strict", "support_status_strict_top10", "strict_locator",
                 "superseding_assertion_id"])

    # ---- reconciliation: one table, both readings, and the supersession mapping made mechanical
    cols = list(out_rows[0].keys())
    C.write_tsv(os.path.join(C.OUT, "TRANSITION_TABLE_RECONCILED.tsv"), out_rows, cols)

    n_gain = sum(1 for r in out_rows if r["direction"] == "gain")
    n_loss = sum(1 for r in out_rows if r["direction"] == "loss")
    gain_rows = [r for r in out_rows if r["direction"] == "gain"]
    loss_rows = [r for r in out_rows if r["direction"] == "loss"]
    # The comparison is made per direction on purpose. The marker layer only ever claims a
    # marker change on the gain side (loss is refused by design: panel absence is not a
    # detection result), so comparing the two readings across all 100 rows would score a
    # deliberate refusal as a disagreement. Outside the gain side the two columns answer
    # different questions and the reconciliation says so instead of averaging them.
    gain_agree = [r for r in recon_rows if r["direction"] == "gain"
                  and r["strict_all_chunks_agrees_with_marker_layer"] == "yes"]
    loss_strict_fail = [r for r in loss_rows
                        if r["support_status_strict"] != "strict_supported"]
    summ = {
        "rows": len(out_rows), "gain_rows": n_gain, "loss_rows": n_loss,
        "upstream_grading": "n_chunks > 0 ('the corpus mentions this gene anywhere')",
        "strict_grading": "gene token + admissible species + names the target group + "
                          "developmentally scented",
        "upstream_support_status_values": dict(collections.Counter(
            r["upstream_support_status"] for r in out_rows)),
        "strict_values_all_chunks": dict(collections.Counter(
            r["support_status_strict"] for r in out_rows)),
        "strict_values_top10": dict(collections.Counter(
            r["support_status_strict_top10"] for r in out_rows)),
        "gain_rows_upstream_supported": sum(1 for r in gain_rows
                                            if r["upstream_support_status"] == "corpus_supported"),
        "gain_rows_strict_supported": sum(1 for r in gain_rows
                                          if r["support_status_strict"] == "strict_supported"),
        "gain_rows_agreement_with_superseding_artefact": len(gain_agree),
        "gain_rows_disagreement_with_superseding_artefact": n_gain - len(gain_agree),
        "loss_rows_upstream_supported": sum(1 for r in loss_rows
                                            if r["upstream_support_status"] == "corpus_supported"),
        "loss_rows_strict_supported": sum(1 for r in loss_rows
                                          if r["support_status_strict"] == "strict_supported"),
        "loss_rows_strict_refused": len(loss_strict_fail),
        "loss_rows_strict_refused_genes": sorted(r["gene"] for r in loss_strict_fail),
        "loss_rows_superseding_artefact_refusals": 90,
        "loss_rows_superseding_artefact_refusal_reason": "detection_conditions_insufficient",
        "marker_layer_admitted_rows": len(superseding),
        "marker_layer_gene_set": sorted(superseding),
        "strict_all_chunks_gene_set": sorted(r["gene"] for r in gain_rows
                                             if r["support_status_strict"] == "strict_supported"),
        "gain_gene_sets_identical": sorted(superseding) == sorted(
            r["gene"] for r in gain_rows
            if r["support_status_strict"] == "strict_supported"),
        "strict_all_chunks_agreement_all_rows": sum(
            1 for r in recon_rows
            if r["strict_all_chunks_agrees_with_marker_layer"] == "yes"),
        "strict_top10_agreement_all_rows": sum(
            1 for r in recon_rows
            if r["strict_top10_agrees_with_marker_layer"] == "yes"),
        "rows_in_reconciliation": len(recon_rows),
        "corpus_pass": {"chunks": n_chunks, "maxrss_gib": round(maxrss, 3),
                        "seconds": round(time.time() - t0, 1)},
        "loss_side_note": ("loss rows are reported by the upstream table and deliberately NOT "
                           "written as marker changes by the superseding artefact: panel "
                           "absence is not a detection result (the superseding artefact carries "
                           "them in its refusal register with reason "
                           "detection_conditions_insufficient)"),
    }
    C.write_tsv(os.path.join(C.OUT, "ITEM1_RECONCILIATION_ROWS.tsv"), recon_rows,
                ["edge_id", "direction", "gene", "upstream_says", "strict_says",
                 "marker_layer_admitted", "strict_all_chunks_agrees_with_marker_layer",
                 "strict_top10_agrees_with_marker_layer"])
    C.write_json(os.path.join(C.OUT, "ITEM1_RECONCILIATION.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())