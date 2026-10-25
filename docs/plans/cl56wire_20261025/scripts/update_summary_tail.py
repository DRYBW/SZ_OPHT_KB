#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-take the knowledge-entry-level tail of ANNOTATION_EVIDENCE_SUMMARY_v1.md (2026-10-25).

What this touches and what it does not:
  * the per-cluster coverage block (clusters / answered / cells / per-library cluster table) is
    copied BYTE-FOR-BYTE from the pre-image. It cannot move: the library this change wires
    (`cl56_v15`) is registered default-off, so no cluster-level reading changes, and the cluster
    panel that produced the block is a run artefact that is not shipped, so the generator cannot be
    re-run.
  * everything from "## How checkable is a citation" onward is re-taken: the entry-level table is
    regenerated from the shipped registry + shipped full-text index (see
    scripts/recompute_summary_table.py, whose rule reproduces the shipped table's entry columns),
    the index-wiring lines are kept verbatim and labelled as the historical reading they are, and
    the registered-gaps section is re-read against the current circularity audit.

Usage: python3 update_summary_tail.py [--check]
  --check   assert the head is byte-identical to the pre-image and print a diff summary; write nothing
"""
import argparse
import difflib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WAVE = HERE.parent
REPO = Path("/home/ubuntu/EYEKB_REPO")
SUMMARY = REPO / "kb" / "link_registry" / "out" / "ANNOTATION_EVIDENCE_SUMMARY_v1.md"
PRE = WAVE / "pre_images" / "ANNOTATION_EVIDENCE_SUMMARY_v1.md.pre_cl56wire"
MARK = "## How checkable is a citation (knowledge-entry level)"


def head_of(text):
    i = text.index(MARK)
    return text[:i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pre = PRE.read_text(encoding="utf-8")
    cur = SUMMARY.read_text(encoding="utf-8")
    if head_of(cur) != head_of(pre):
        raise SystemExit("REFUSING: the cluster-level block has changed since the pre-image; "
                         "investigate before re-taking the tail")
    table = json.loads((WAVE / "out" / "SUMMARY_TABLE_NEW.json").read_text(encoding="utf-8"))
    circ = subprocess.run(["/home/ubuntu/training-venv/bin/python3",
                           str(REPO / "kb" / "link_registry" / "scripts" /
                               "audit_link_circularity.py")],
                          capture_output=True, text=True, check=True).stdout.strip()
    key_b = "B. reachable excluding the registry's own rendered appendix"
    circ_read = {ln.split(":")[0].strip(): ln.split(":", 1)[1].strip()
                 for ln in circ.splitlines() if ":" in ln}
    circ_txt = "%s marker entries, %s reachable at all, %s reachable excluding this registry's own " \
               "rendered appendix, %s relying on that appendix alone." % (
                   circ_read.get("entries", "?"), circ_read.get("A. reachable at all", "?"),
                   circ_read.get(key_b, "?"),
                   circ_read.get("of which rely only on that appendix", "?"))

    def fill(s, width=100, subsequent_indent=""):
        import textwrap
        return "\n".join(textwrap.wrap(s, width=width, subsequent_indent=subsequent_indent))

    tail = [MARK, "",
            fill("A citation counts as checkable when the cited paper's own full text states at "
                 "least one of the marker genes of the entry. Same rule applied before and after "
                 "the full-text index is wired in."), ""]
    tail += table["table_markdown"]
    tail += ["",
             fill("Table re-taken 2026-10-25 (`plans/consistency_20261024/cl56wire_out/"
                  "scripts/recompute_summary_table.py --registry kb/link_registry/"
                  "LINK_REGISTRY_v1.jsonl`), together with the full-text index it is scored against "
                  "(330 panel genes / 10,550 rows). The version it replaces was recorded early in "
                  "the 2026-10-21 wave and predates that wave's own extended-evidence pass: its "
                  "row-count columns read 2,106 citation rows / 1,241 checkable while the registry "
                  "it was computed from already carried 3,735 / 2,870. Its entry columns and this "
                  "table agree (the 80 entries of the time, 78 of them with a checkable citation). "
                  "Two libraries were added after it: `onfibro_v13` (activated on the default route "
                  "2026-10-22) and `cl56_v15` (registered, default-off, so no cluster-level reading "
                  "moves)."), "",
             fill("Before the index (read at the 2026-10-21 full-text-index wave): 1,489 rows, 624 "
                  "checkable (41.9%), 361 distinct papers, 75/80 entries."),
             fill("After (same wave): 2,106 rows, 1,241 checkable (58.9%), 497 distinct papers, "
                  "78/80 entries."),
             fill("The paper-level detail, with the chunk and section where each marker was found, "
                  "is in `ANNOTATION_EVIDENCE_APPENDIX_v1.md` (machine-readable twin: the `.tsv`)."),
             "",
             "## Registered gaps", "",
             fill("- Two marker entries record **no panel at all** in their source library "
                  "(`face_v6::Fibroblast`, `face_v6::Myofibroblast`), so nothing about them can be "
                  "checked against a paper's text; their 20 citations each stay at the label level.",
                  subsequent_indent="  "),
             fill("- One marker gene of the 330 scanned (MOBP) occurs nowhere in the corpus."),
             fill("- Re-taken 2026-10-25, same change as the table above: the shipped version of "
                  "this section still named `membrane::cDC1` / `membrane::cDC2` as reachable only "
                  "through this registry's generated appendix; both gained a written page at the "
                  "2026-10-21 link-spine close-out, and the current reading of "
                  "`scripts/audit_link_circularity.py` is: " + circ_txt,
                  subsequent_indent="  "),
             "",
             "These are disclosure readings. Nothing here feeds a score, a weighting or a ranking.",
             ""]
    new = head_of(pre) + "\n".join(tail)

    if args.check:
        print("head byte-identical to the pre-image: OK")
        d = list(difflib.unified_diff(pre.splitlines(), new.splitlines(), "shipped", "re-taken",
                                      lineterm="", n=1))
        print(f"diff lines: {len(d)}")
        for ln in d[:60]:
            print(ln)
        return 0

    SUMMARY.write_text(new, encoding="utf-8")
    print("re-taken:", SUMMARY, SUMMARY.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())