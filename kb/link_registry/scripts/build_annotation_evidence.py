#!/usr/bin/env python3
"""Attach the evidence trail to actual annotations: one row per cluster.

Input : a cluster-level result panel (JSON) of this project's form -
        {detail: [{vol, cluster, n, truth, truth_cl, tops: {arm: label}, verdicts: {arm: verdict}}]}
        and, optionally, a second panel giving the same keys' verdicts under the shipped default
        configuration, used to flag rows whose outcome depends on which switches are on.
        The link registry built by kb/link_registry/scripts/build_link_registry.py.

Output: ANNOTATION_EVIDENCE_TABLE_v1.tsv   - one row per cluster, ready to become a report appendix
        ANNOTATION_EVIDENCE_SUMMARY_v1.md  - how much of the annotation is backed by a source

The point of the table: a reader looking at a label in the report can see, on the same row, which
knowledge-base entry supports it, the page that describes it and the papers behind it. Clusters the
system abstained on carry no label and therefore no citation - that is the honest reading of an
abstention, not a gap to be filled.
"""
import argparse
import csv
import json
from pathlib import Path

TEXTBOOK_LIB = "textbook_t4"


def load_registry(path):
    """label -> evidence bundle, from the link registry."""
    by_label = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "error" in r:
            continue
        key = (r.get("cell_type") or "").strip().lower()
        if key and key not in by_label:
            by_label[key] = r
    return by_label


def evidence_for(label, by_label):
    if not label:
        return None
    r = by_label.get(label.strip().lower())
    if r:
        return r
    # fall back to the "<library>::<class>" alias rows, then to a containment match
    for k, v in by_label.items():
        if k.endswith("::" + label.strip().lower()):
            return v
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", required=True, help="cluster-level result panel (JSON)")
    ap.add_argument("--default-config", default="", help="panel with shipped-default verdicts (JSON)")
    ap.add_argument("--registry", required=True, help="LINK_REGISTRY_v1.jsonl")
    ap.add_argument("--arm", default="A0", help="which arm's labels to report")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--top-citations", type=int, default=2)
    args = ap.parse_args()

    panel = json.loads(Path(args.clusters).read_text(encoding="utf-8"))
    detail = panel["detail"]
    by_label = load_registry(args.registry)

    changed = {}
    if args.default_config:
        dc = json.loads(Path(args.default_config).read_text(encoding="utf-8"))
        for arm, verdicts in (dc.get("_verdicts") or {}).items():
            if arm == "base":
                continue
            changed[arm] = verdicts

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for o in detail:
        label = (o.get("tops") or {}).get(args.arm, "")
        verdict = (o.get("verdicts") or {}).get(args.arm, "")
        ev = evidence_for(label, by_label)
        cites = (ev or {}).get("citations") or []
        anchors = (ev or {}).get("book_anchors") or []
        top = "; ".join(
            f"PMID {c['pmid']} ({c.get('journal','')} {c.get('year','')})"
            + (f" [mentions {','.join(c.get('matched_panel_genes') or [])}]" if c.get("gene_match") else "")
            for c in cites[:args.top_citations])
        key = f"{o['vol']}/{o['cluster']}"
        conf_flag = ""
        for arm, verdicts in changed.items():
            if verdicts.get(key) and verdicts.get(key) != verdict:
                conf_flag = f"{verdict} -> {verdicts[key]} under the shipped default"
        rows.append({
            "volume": o["vol"], "cluster": o["cluster"], "n_cells": o["n"],
            "our_label": label, "verdict": verdict,
            "reference_label": o.get("truth", ""), "reference_cl": o.get("truth_cl", ""),
            "evidence_library": (ev or {}).get("library", ""),
            "key_markers": ",".join((ev or {}).get("genes_top", [])[:6]),
            "wiki_page": "; ".join((ev or {}).get("wiki_pages", [])[:1]),
            "textbook_anchor": "; ".join(f"{b} {p}" for b, p in anchors[:1]),
            "n_citations": len(cites), "backing_papers": top,
            "config_dependent": conf_flag,
        })

    fields = list(rows[0].keys())
    tsv = out / "ANNOTATION_EVIDENCE_TABLE_v1.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    labelled = [r for r in rows if r["our_label"]]
    cited = [r for r in labelled if r["n_citations"] > 0]
    textbooked = [r for r in labelled if r["textbook_anchor"]]
    cells = sum(r["n_cells"] for r in rows)
    cells_labelled = sum(r["n_cells"] for r in labelled)
    cells_cited = sum(r["n_cells"] for r in cited)

    lines = ["# Annotation evidence coverage",
             "",
             "How much of this project's annotation carries a source a reader can follow. One row per "
             "cluster; a cluster the system abstained on carries no label, so it carries no citation.",
             "",
             f"- clusters: **{len(rows)}** over **{cells:,} cells**",
             f"- answered (a label was emitted): **{len(labelled)}** clusters / **{cells_labelled:,}** cells",
             f"- answered **and** backed by at least one paper: **{len(cited)}** clusters "
             f"({len(cited)/max(len(labelled),1)*100:.1f}% of answered) / **{cells_cited:,}** cells "
             f"({cells_cited/max(cells_labelled,1)*100:.1f}% of answered cells)",
             f"- answered with a textbook page anchor as well: **{len(textbooked)}**",
             f"- abstained (no label, no citation - by design): **{len(rows)-len(labelled)}** clusters",
             "",
             "| library the supporting entry comes from | clusters |",
             "|---|---|"]
    libs = {}
    for r in labelled:
        libs[r["evidence_library"] or "(none)"] = libs.get(r["evidence_library"] or "(none)", 0) + 1
    for k in sorted(libs, key=lambda x: -libs[x]):
        lines.append(f"| {k} | {libs[k]} |")
    lines += ["", "Rows flagged `config_dependent` change verdict when a knowledge-base switch is "
                  "flipped; their label in this table is the one the panel recorded, not necessarily "
                  "the shipped default.", ""]
    (out / "ANNOTATION_EVIDENCE_SUMMARY_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"clusters={len(rows)} answered={len(labelled)} cited={len(cited)} "
          f"({len(cited)/max(len(labelled),1)*100:.1f}% of answered) "
          f"cells_cited={cells_cited}/{cells_labelled} "
          f"({cells_cited/max(cells_labelled,1)*100:.1f}%)")
    print(f"wrote {tsv} and ANNOTATION_EVIDENCE_SUMMARY_v1.md")


if __name__ == "__main__":
    main()