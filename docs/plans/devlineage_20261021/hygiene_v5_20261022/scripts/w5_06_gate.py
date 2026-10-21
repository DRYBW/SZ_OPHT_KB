#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_06_gate.py — the wave's gate. It judges, it does not describe.

Every check reads files on disk and recomputes what it needs; nothing is taken from a previous
script's own report except where that report is itself the object under test. The verdict is
written to out/GATE.json and out/GATE_READOUT.md.

Usage: python3 scripts/w5_06_gate.py [--json OUT/GATE.json] [--no-replay]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402


class Gate:
    def __init__(self):
        self.checks = []

    def add(self, code, name, ok, detail, offenders=()):
        off = list(offenders)
        self.checks.append({"code": code, "name": name, "status": "PASS" if ok else "FAIL",
                            "detail": detail, "n_offenders": len(off), "offenders": off[:12]})

    def info(self, code, name, detail):
        """A check the verdict cannot judge here, reported rather than silently passed.

        Used for exactly one case: the clone check runs this gate inside the clone, and that
        same clone check is the step that produces the clone-check record — so this invocation
        cannot judge its own evidence. The author-tree invocation, which a reader runs, judges it
        as a real PASS/FAIL.
        """
        self.checks.append({"code": code, "name": name, "status": "INFO", "detail": detail,
                            "n_offenders": 0, "offenders": []})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(C.OUT, "GATE.json"))
    ap.add_argument("--no-replay", action="store_true")
    ap.add_argument("--inner-clone-check", action="store_true",
                    help="this invocation runs inside the clone check: G12 is reported as INFO "
                         "instead of judged, because this invocation produces its own evidence")
    args = ap.parse_args()
    g = Gate()

    # ---- G1 the upstream table, judged by recomputation ------------------------------------
    table = C.read_tsv(os.path.join(C.CLD_OUT, "LINEAGE_MARKER_TRANSITIONS.tsv"))
    bad = [r for r in table
           if r["in_child_panel"] != ("yes" if r["direction"] == "gain" else "no")]
    b1 = open(C.CLD_B1, encoding="utf-8").read()
    line_fixed = ('"in_child_panel": "yes" if g in child_genes else "no"' in b1)
    gate_b = C.read_json(os.path.join(C.CLD_OUT, "GATE_B.json"))
    g.add("G1", "UPSTREAM_TABLE_HONEST",
          (not bad) and line_fixed and gate_b["verdict"] == "PASS",
          "rows=%d; rows contradicting their own direction=%d; the builder computes the value "
          "(%s); upstream gate B verdict=%s (%d failed)"
          % (len(table), len(bad), line_fixed, gate_b["verdict"], gate_b["n_fail"]),
          ["|".join((r["edge_id"], r["direction"], r["gene"])) for r in bad])

    # ---- G2 the honest grading, judged against the superseding artefact --------------------
    rec = C.read_json(os.path.join(C.OUT, "ITEM1_RECONCILIATION.json"))
    g.add("G2", "STRICT_GRADING_MATCHES_SUPERSEDING_ARTEFACT",
          rec["gain_gene_sets_identical"] and rec["gain_rows_disagreement_with_superseding_artefact"] == 0,
          "gain rows=%d; agreement with MARKER_CHANGE_EDGES.tsv=%d; disagreements=%d; gene sets "
          "identical=%s" % (rec["gain_rows"], rec["gain_rows_agreement_with_superseding_artefact"],
                            rec["gain_rows_disagreement_with_superseding_artefact"],
                            rec["gain_gene_sets_identical"]), [])

    # ---- G3 one reconciled table, both readings, no silent difference ----------------------
    reconciled = C.read_tsv(os.path.join(C.OUT, "TRANSITION_TABLE_RECONCILED.tsv"))
    cols = set(reconciled[0]) if reconciled else set()
    need = {"upstream_support_status", "support_status_strict", "support_status_strict_top10",
            "chunks_meeting_all_four", "superseding_assertion_id"}
    both_readings = need <= cols
    loss_note = rec.get("loss_rows_superseding_artefact_refusal_reason", "")
    g.add("G3", "ONE_RECONCILED_TABLE",
          both_readings and len(reconciled) == rec["rows"] and bool(loss_note),
          "reconciled rows=%d; both gradings carried=%s; the loss side's refusal reason is "
          "recorded (%s)" % (len(reconciled), both_readings, loss_note or "MISSING"))

    # ---- G4 the re-point: everything the scaffold published is accounted for ----------------
    s3 = C.read_json(os.path.join(C.OUT, "ITEM3_SUMMARY.json"))
    adap_n = C.read_tsv(os.path.join(C.OUT, "adapter", "NODES_from_scaffold.tsv"))
    adap_e = C.read_tsv(os.path.join(C.OUT, "adapter", "EDGES_from_scaffold.tsv"))
    scaf_n = C.read_tsv(os.path.join(C.SCAF_OUT, "SCAFFOLD_NODES.tsv"))
    scaf_e = C.read_tsv(os.path.join(C.SCAF_OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    builders_ok = all(r["rc"] == 0 for r in s3["builder_rc"])
    g.add("G4", "REPOINT_ACCOUNTS_FOR_EVERY_SOURCE_ROW",
          builders_ok and len(adap_n) == len(scaf_n) and len(adap_e) == len(scaf_e)
          and s3["adapter_edges_unresolved_endpoints"] == []
          and s3["node_assertions"]["resolution"]["unresolved"] == 0,
          "scaffold rows in=%d/%d nodes, %d/%d edges; adapter rows=%d/%d; builders rc=%s; "
          "endpoints unresolved=%d; assertions unresolved=%d"
          % (len(scaf_n), len(adap_n), len(scaf_e), len(adap_e), len(scaf_n), len(scaf_e),
             [r["rc"] for r in s3["builder_rc"]],
             len(s3["adapter_edges_unresolved_endpoints"]),
             s3["node_assertions"]["resolution"]["unresolved"]))

    # ---- G5 the grade conflict is surfaced and the source grade governs --------------------
    gr = s3["grade_reconciliation"]
    edge_rec = C.read_tsv(os.path.join(C.OUT, "repointed", "EDGES_RECONCILED.tsv"))
    src_grade = {e["edge_id"]: e["evidence_grade"] for e in scaf_e}
    wrong = [r for r in edge_rec if r["evidence_grade"] != src_grade.get(r["edge_id"], "")]
    g.add("G5", "GRADE_CONFLICT_SURFACED_AND_SOURCE_GOVERNS",
          gr["edges_compared"] > 0 and (not wrong) and gr["conflicts"] == gr["edges_compared"]
          and len(edge_rec) == gr["edges_compared"],
          "edges=%d; builder/source agreement=%d; conflicts=%d (all surfaced); reconciled rows "
          "where the source grade governs=%d/%d"
          % (gr["edges_compared"], gr["agreement"], gr["conflicts"], len(edge_rec) - len(wrong),
             len(edge_rec)), wrong[:5])

    # ---- G6 item 2: the byte ledger is complete and nothing under kb/ was written -----------
    led = C.read_tsv(os.path.join(C.OUT, "ITEM2_BYTE_LEDGER.tsv"))
    site_now = {n: C.sha256(os.path.join(C.KB_MARKERS, n))
                for n in sorted(os.listdir(C.KB_MARKERS))
                if os.path.isfile(os.path.join(C.KB_MARKERS, n))}
    repo_now = {n: C.sha256(os.path.join(C.REPO_KB_MARKERS, n))
                for n in sorted(os.listdir(C.REPO_KB_MARKERS))
                if os.path.isfile(os.path.join(C.REPO_KB_MARKERS, n))}
    led_site = {r["file"]: r["sha256_mntD"] for r in led if r["present_in_mntD"] == "yes"}
    led_repo = {r["file"]: r["sha256_repo"] for r in led if r["present_in_repo"] == "yes"}
    unchanged = (site_now == led_site) and (repo_now == led_repo)
    same_claim = all((r["byte_identical"] in ("yes", "n/a")) for r in led)
    sync_script = os.path.join(C.OUT, "ITEM2_SYNC_KB_MARKERS.sh")
    dry_default = os.path.isfile(sync_script) and "APPLY=0" in open(
        sync_script, encoding="utf-8").read()
    g.add("G6", "KB_LEDGER_COMPLETE_AND_NO_KB_WRITE",
          unchanged and same_claim and dry_default and bool(led),
          "files ledgered=%d; data tree unchanged=%s; git tree unchanged=%s; every shared file "
          "either byte-identical or n/a=%s; sync script dry-run by default=%s"
          % (len(led), unchanged, unchanged, same_claim, dry_default))

    # ---- G7 item 4: the counts reconcile and nothing was activated -------------------------
    s4 = C.read_json(os.path.join(C.OUT, "ITEM4_SUMMARY.json"))
    eval_rows = C.read_tsv(os.path.join(C.OUT, "ITEM4_EVAL_BASIS_BY_GENE.tsv"))
    a_panel = sum(int(r["A_refused_eval_only_no_independent_evidence"])
                  for r in C.read_tsv(os.path.join(C.OUT, "ITEM4_EVAL_BASIS_BY_PANEL.tsv")))
    a_rows = sum(1 for r in eval_rows if r["panel_basis_class"] == "panel_basis_eval_only")
    a_genes = len({r["gene"] for r in eval_rows
                   if r["panel_basis_class"] == "panel_basis_eval_only"})
    no_activation = (s4["activation"] == "none" and s4["panel_bodies_changed"] == 0)
    # the per-panel count is a count of distinct genes, the per-gene file is one row per
    # (panel, label, gene), so the two reconcile on the gene count and the row count is reported
    # next to it rather than forced equal (a gene can sit in two labels of the same panel)
    g.add("G7", "EVAL_BASIS_FINDING_RECONCILES",
          a_panel == s4["totals"]["A_refused_eval_only_no_independent_evidence"]
          == a_genes and a_rows >= a_genes and no_activation
          and os.path.isfile(os.path.join(C.OUT, "ITEM4_NONBENCHMARK_FLAG_SPEC.md")),
          "per-panel A total=%d; distinct eval-only genes=%d; per-gene rows=%d (one row per "
          "label the gene sits in); summary A=%d; activation=%s; panel bodies changed=%d"
          % (a_panel, a_genes, a_rows,
             s4["totals"]["A_refused_eval_only_no_independent_evidence"],
             s4["activation"], s4["panel_bodies_changed"]))

    # ---- G8 zero network, proven by the audit hook, not by reading the source ---------------
    net = os.path.join(C.LEDGERS, "net_audit.log")
    events, receipts = 0, 0
    if os.path.isfile(net):
        for line in open(net, encoding="utf-8"):
            if line.startswith("EVENT "):
                events += 1
            elif line.startswith("# hook-installed"):
                receipts += 1
    g.add("G8", "NO_NETWORK",
          events == 0 and receipts > 0,
          "audit-hook receipts=%d (proves the hook was installed); network events=%d"
          % (receipts, events))

    # ---- G9 the default answer is byte-identical: the recorded query set replayed ----------
    golden = {"performed": False}
    if os.path.isfile(C.GOLDEN) and not args.no_replay:
        gp = os.path.join(tempfile.mkdtemp(prefix="w5_golden_"), "golden_now.json")
        t0 = time.time()
        p = subprocess.run([sys.executable, C.GOLDEN, gp], capture_output=True, text=True,
                           cwd=os.path.dirname(C.GOLDEN))
        golden = {"performed": True, "rc": p.returncode, "seconds": round(time.time() - t0, 1),
                  "stdout_tail": (p.stdout or "")[-300:]}
        if p.returncode == 0 and os.path.isfile(gp):
            now, before = C.read_json(gp), C.read_json(C.GOLDEN_RECORDED)
            shutil.copy2(gp, os.path.join(C.LEDGERS, "golden_721_now.json"))
            golden["now"] = now.get("stats")
            golden["recorded"] = before.get("stats")
            same = (now.get("stats", {}).get("off", {}).get("differ") == 0
                    and now.get("stats", {}).get("off", {}).get("n")
                    == before.get("stats", {}).get("off", {}).get("n"))
            g.add("G9", "DEFAULT_BEHAVIOUR_IDENTICAL",
                  same,
                  "recorded production queries replayed in %.1fs: n=%s identical=%s differ=%s "
                  "(recorded n=%s)"
                  % (golden["seconds"], now.get("stats", {}).get("off", {}).get("n"),
                     now.get("stats", {}).get("off", {}).get("identical"),
                     now.get("stats", {}).get("off", {}).get("differ"),
                     before.get("stats", {}).get("off", {}).get("n")))
        else:
            g.add("G9", "DEFAULT_BEHAVIOUR_IDENTICAL", False,
                  "the replay did not produce a comparable result (rc=%s)" % p.returncode,
                  [str(p.stdout)[-200:]])
    else:
        g.add("G9", "DEFAULT_BEHAVIOUR_IDENTICAL", False,
              "the recorded query set was not replayed (--no-replay or the script is missing)")
    # what this card touched outside its own wave, as a positive statement
    diff = subprocess.run(["git", "-C", C.REPO, "diff", "--name-only"], capture_output=True,
                          text=True)
    touched = sorted(x for x in diff.stdout.splitlines() if x)
    g.add("G10", "WHAT_THIS_CARD_TOUCHED_OUTSIDE_ITS_WAVE",
          all(not x.startswith("kb/") for x in touched),
          "the repository working tree's modified paths (this card adds kb/ nothing): %s"
          % ", ".join(touched) if touched else "the repository working tree is clean", [])

    # ---- G11 the wave's own artefacts verify against its manifest --------------------------
    man = os.path.join(C.OUT, "MANIFEST.sha256")
    ok, n = 0, 0
    badman = []
    if os.path.isfile(man):
        for line in open(man, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            h, rel = line.split(None, 1)
            rel = rel.lstrip("*")
            n += 1
            p = os.path.join(C.WAVE, rel)
            if os.path.isfile(p) and C.sha256(p) == h:
                ok += 1
            else:
                badman.append(rel)
    g.add("G11", "MANIFEST_VERIFIES", n > 0 and ok == n,
          "manifest entries=%d, verified=%d, failing=%d" % (n, ok, len(badman)), badman)

    # ---- G12 the clone check ---------------------------------------------------------------
    clone = os.path.join(C.OUT, "CLEAN_CLONE_CHECK.json")
    clone_doc = C.read_json(clone) if os.path.isfile(clone) else {}
    if args.inner_clone_check:
        g.info("G12", "CLEAN_CLONE_GREEN",
               "delegated: this invocation runs inside the clone check, which is the step that "
               "produces this record; the author-tree invocation judges it")
    else:
        g.add("G12", "CLEAN_CLONE_GREEN",
              clone_doc.get("verdict") == "PASS",
              "clean-clone check: %s" % json.dumps(
                  {k: v for k, v in clone_doc.items() if k in ("commit", "clone_root", "gate_rc",
                                                               "gate_verdict", "gate_failed",
                                                               "files_mirrored",
                                                               "files_differing_from_author_tree")},
                  ensure_ascii=False) if clone_doc else "not run")

    fails = [c for c in g.checks if c["status"] == "FAIL"]
    verdict = "PASS" if not fails else "FAIL"
    doc = {"gate": "wave-5 lineage hygiene", "verdict": verdict, "n_checks": len(g.checks),
           "n_fail": len(fails),
           "checks": g.checks, "golden": golden,
           "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if args.inner_clone_check:
        doc["invocation"] = ("inside the clone check: G12 is reported as INFO because this "
                             "invocation produces its own evidence")
    C.write_json(args.json, doc)
    lines = ["# Gate readout — wave-5 lineage hygiene", "",
             "verdict: **%s** (%d checks, %d failed%s)"
             % (verdict, len(g.checks), len(fails),
                "; %d reported as INFO" % sum(1 for c in g.checks if c["status"] == "INFO")
                if any(c["status"] == "INFO" for c in g.checks) else ""),
             "", "| check | name | status | n_offenders | detail |", "|---|---|---|---|---|"]
    for c in g.checks:
        lines.append("| %s | %s | %s | %d | %s |" % (c["code"], c["name"], c["status"],
                                                      c["n_offenders"],
                                                      c["detail"].replace("|", "/")))
    open(os.path.join(C.OUT, "GATE_READOUT.md"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())